import ctypes
import hashlib
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PS1_SOURCE = REPO_ROOT / 'installer' / 'mod_patch.ps1'

GENERIC_READ_WRITE = 0xC0000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@contextmanager
def _exclusive_win_lock(path: Path):
    """Hold a Windows share-exclusive handle so FileShare.None rejects opening."""
    k32 = ctypes.windll.kernel32
    k32.CreateFileW.restype = ctypes.c_void_p
    handle = k32.CreateFileW(str(path), GENERIC_READ_WRITE, 0, None, OPEN_EXISTING, 0, None)
    if handle == INVALID_HANDLE_VALUE or handle is None:
        raise ctypes.WinError()
    try:
        yield
    finally:
        k32.CloseHandle(ctypes.c_void_p(handle))


class ModPatchPs1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt' or shutil.which('powershell') is None:
            raise unittest.SkipTest('Windows PowerShell is required')

    def _run_ps1(self, mod_dir: Path, *args: str) -> subprocess.CompletedProcess:
        cmd = [
            'powershell',
            '-NoProfile',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(mod_dir / 'mod_patch.ps1'),
            *args,
        ]
        return subprocess.run(cmd, cwd=mod_dir, capture_output=True, text=True, check=False)

    def _build_fixture(self, tmp: Path):
        game = tmp / 'game'
        mod_dir = game / 'DT22_Mod'
        param_dir = game / 'Data' / 'ENG' / 'Parameter'
        dungeon_dir = game / 'Data' / 'Dungeon'
        param_dir.mkdir(parents=True)
        dungeon_dir.mkdir(parents=True)
        mod_dir.mkdir(parents=True)
        shutil.copy2(PS1_SOURCE, mod_dir / 'mod_patch.ps1')

        van_a = b'VANILLA_A_00000000'
        van_b = b'VANILLA_B_11111111'
        van_exe = b'MZ' + b'\x00' * 16 + b'OLD_EXE' + b'\x00' * 8
        van_dungeon = b'\xaa' * 12 + b'ORIG' + b'\xbb' * 8

        (param_dir / 'a.pck').write_bytes(van_a)
        (param_dir / 'b.pck').write_bytes(van_b)
        (game / 'Game.exe').write_bytes(van_exe)
        (dungeon_dir / 'd01.dat').write_bytes(van_dungeon)

        v1_a = b'VANILLA_A_' + b'V1_NEW!!'
        v1_b = b'V1_B_MODDED_BYTES!'
        v2_a = b'V2_ONLY_A_BYTES___'

        # Build ops/dat for v1 (includes copy+insert op on a.pck and full insert on b.pck)
        blob_v1 = b'V1_NEW!!' + v1_b
        ops_v1 = (
            struct.pack('<III', 0, 0, len(b'VANILLA_A_'))
            + struct.pack('<III', 1, 0, len(b'V1_NEW!!'))
            + struct.pack('<III', 1, len(b'V1_NEW!!'), len(v1_b))
        )
        (mod_dir / 'v1.ops').write_bytes(ops_v1)
        (mod_dir / 'v1.dat').write_bytes(blob_v1)

        exe_off = van_exe.index(b'OLD_EXE')
        dung_off = van_dungeon.index(b'ORIG')
        manifest_v1 = [
            f'file|Data\\ENG\\Parameter\\a.pck|{_sha256(van_a)}|{_sha256(v1_a)}|{len(v1_a)}|0|2',
            f'file|Data\\ENG\\Parameter\\b.pck|{_sha256(van_b)}|{_sha256(v1_b)}|{len(v1_b)}|2|1',
            f"exe|main|{exe_off:x}|{b'OLD_EXE'.hex()}|{b'NEW_EXE'.hex()}",
            f"poke|Data\\Dungeon\\d01.dat|{dung_off:x}|{b'ORIG'.hex()}|{b'MOD1'.hex()}",
        ]
        (mod_dir / 'v1.txt').write_text('\n'.join(manifest_v1) + '\n', encoding='utf-8')

        # Build ops/dat for v2 (modifies only a.pck; drops b.pck, exe, and poke)
        (mod_dir / 'v2.ops').write_bytes(struct.pack('<III', 1, 0, len(v2_a)))
        (mod_dir / 'v2.dat').write_bytes(v2_a)
        manifest_v2 = [
            f'file|Data\\ENG\\Parameter\\a.pck|{_sha256(van_a)}|{_sha256(v2_a)}|{len(v2_a)}|0|1',
        ]
        (mod_dir / 'v2.txt').write_text('\n'.join(manifest_v2) + '\n', encoding='utf-8')

        return {
            'game': game,
            'mod_dir': mod_dir,
            'a': param_dir / 'a.pck',
            'b': param_dir / 'b.pck',
            'exe': game / 'Game.exe',
            'dungeon': dungeon_dir / 'd01.dat',
            'van': {'a': van_a, 'b': van_b, 'exe': van_exe, 'dungeon': van_dungeon},
            'v1': {
                'a': v1_a,
                'b': v1_b,
                'exe': van_exe.replace(b'OLD_EXE', b'NEW_EXE'),
                'dungeon': van_dungeon.replace(b'ORIG', b'MOD1'),
            },
            'v2': {'a': v2_a},
        }

    def _assert_no_staged_files(self, root: Path):
        leftovers = list(root.rglob('*.dt22new'))
        self.assertEqual([], leftovers, f'Unexpected .dt22new files left behind: {leftovers}')

    def test_install_reinstall_and_uninstall_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            fx = self._build_fixture(Path(td))
            mod_dir = fx['mod_dir']

            res = self._run_ps1(mod_dir, 'install', 'v1')
            self.assertEqual(0, res.returncode, res.stdout + res.stderr)
            self.assertEqual(fx['v1']['a'], fx['a'].read_bytes())
            self.assertEqual(fx['v1']['b'], fx['b'].read_bytes())
            self.assertEqual(fx['v1']['exe'], fx['exe'].read_bytes())
            self.assertEqual(fx['v1']['dungeon'], fx['dungeon'].read_bytes())
            self.assertTrue((mod_dir / 'installed.txt').is_file())
            self.assertTrue((mod_dir / 'pokes.txt').is_file())
            self.assertTrue((mod_dir / 'backup' / 'Game.exe').is_file())
            self._assert_no_staged_files(fx['game'])

            # Idempotent re-install of the same variant
            res2 = self._run_ps1(mod_dir, 'install', 'v1')
            self.assertEqual(0, res2.returncode, res2.stdout + res2.stderr)
            self.assertEqual(fx['v1']['a'], fx['a'].read_bytes())
            self._assert_no_staged_files(fx['game'])

            res_un = self._run_ps1(mod_dir, 'uninstall')
            self.assertEqual(0, res_un.returncode, res_un.stdout + res_un.stderr)
            self.assertEqual(fx['van']['a'], fx['a'].read_bytes())
            self.assertEqual(fx['van']['b'], fx['b'].read_bytes())
            self.assertEqual(fx['van']['exe'], fx['exe'].read_bytes())
            self.assertEqual(fx['van']['dungeon'], fx['dungeon'].read_bytes())
            self.assertFalse((mod_dir / 'backup').exists())
            self.assertFalse((mod_dir / 'installed.txt').exists())
            self.assertFalse((mod_dir / 'pokes.txt').exists())
            self._assert_no_staged_files(fx['game'])

    def test_switch_variant_restores_unlisted_files_exe_and_pokes(self):
        with tempfile.TemporaryDirectory() as td:
            fx = self._build_fixture(Path(td))
            mod_dir = fx['mod_dir']

            res1 = self._run_ps1(mod_dir, 'install', 'v1')
            self.assertEqual(0, res1.returncode, res1.stdout + res1.stderr)

            res2 = self._run_ps1(mod_dir, 'install', 'v2')
            self.assertEqual(0, res2.returncode, res2.stdout + res2.stderr)
            self.assertEqual(fx['v2']['a'], fx['a'].read_bytes())
            self.assertEqual(fx['van']['b'], fx['b'].read_bytes())
            self.assertEqual(fx['van']['exe'], fx['exe'].read_bytes())
            self.assertEqual(fx['van']['dungeon'], fx['dungeon'].read_bytes())
            self.assertFalse((mod_dir / 'pokes.txt').exists())
            self._assert_no_staged_files(fx['game'])

    def test_locked_target_aborts_before_partial_write_on_install_and_uninstall(self):
        with tempfile.TemporaryDirectory() as td:
            fx = self._build_fixture(Path(td))
            mod_dir = fx['mod_dir']

            # Lock b.pck during v1 install -> nothing changes, no backup created
            with _exclusive_win_lock(fx['b']):
                res = self._run_ps1(mod_dir, 'install', 'v1')
            self.assertNotEqual(0, res.returncode)
            self.assertIn('in use', res.stdout)
            self.assertEqual(fx['van']['a'], fx['a'].read_bytes())
            self.assertEqual(fx['van']['b'], fx['b'].read_bytes())
            self.assertEqual(fx['van']['exe'], fx['exe'].read_bytes())
            self.assertFalse((mod_dir / 'backup').exists())
            self._assert_no_staged_files(fx['game'])

            # Install cleanly, then lock dungeon poke target during uninstall -> nothing restored
            self.assertEqual(0, self._run_ps1(mod_dir, 'install', 'v1').returncode)
            with _exclusive_win_lock(fx['dungeon']):
                res_un = self._run_ps1(mod_dir, 'uninstall')
            self.assertNotEqual(0, res_un.returncode)
            self.assertIn('in use', res_un.stdout)
            self.assertEqual(fx['v1']['a'], fx['a'].read_bytes())
            self.assertEqual(fx['v1']['b'], fx['b'].read_bytes())
            self.assertEqual(fx['v1']['dungeon'], fx['dungeon'].read_bytes())
            self._assert_no_staged_files(fx['game'])

            # Lock crossBack file (Game.exe) when switching v1 -> v2 -> aborts cleanly
            with _exclusive_win_lock(fx['exe']):
                res_sw = self._run_ps1(mod_dir, 'install', 'v2')
            self.assertNotEqual(0, res_sw.returncode)
            self.assertIn('in use', res_sw.stdout)
            self.assertEqual(fx['v1']['a'], fx['a'].read_bytes())
            self._assert_no_staged_files(fx['game'])

    def test_external_update_blocks_uninstall(self):
        with tempfile.TemporaryDirectory() as td:
            fx = self._build_fixture(Path(td))
            mod_dir = fx['mod_dir']

            self.assertEqual(0, self._run_ps1(mod_dir, 'install', 'v1').returncode)
            fx['a'].write_bytes(b'PATCHED_BY_STEAM!!')

            res_un = self._run_ps1(mod_dir, 'uninstall')
            self.assertNotEqual(0, res_un.returncode)
            self.assertIn('changed since the mod was installed', res_un.stdout)
            self.assertEqual(b'PATCHED_BY_STEAM!!', fx['a'].read_bytes())
            self._assert_no_staged_files(fx['game'])


if __name__ == '__main__':
    unittest.main()
