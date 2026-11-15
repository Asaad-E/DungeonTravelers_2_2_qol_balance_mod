"""Tests for cross-platform installer/mod_patch.py (Linux/Steam Deck installer)."""
from contextlib import contextmanager
import hashlib
import io
import os
import shutil
import stat
import struct
import sys
import tempfile
import unittest

import installer.mod_patch as mp


@contextmanager
def hold_exclusive_lock(path: str):
    """Hold `path` open exclusively (blocking external write/replace) inside a test."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.CreateFileW(path, 0x80000000, 0x00000001, None, 3, 0, None)
        if handle == wintypes.HANDLE(-1).value:
            raise OSError(ctypes.get_last_error(), f"Failed to lock {path}")
        try:
            yield
        finally:
            kernel32.CloseHandle(handle)
    else:
        old_mode = os.stat(path).st_mode
        os.chmod(path, stat.S_IREAD)
        try:
            yield
        finally:
            os.chmod(path, old_mode)


class ModPatchPyTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = os.path.join(self.temp_dir, 'game')
        self.mod_dir = os.path.join(self.root, 'DT22_Mod')
        os.makedirs(os.path.join(self.root, 'Data', 'ENG', 'Parameter'), exist_ok=True)
        os.makedirs(self.mod_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_install_and_uninstall_cycle(self):
        # 1. Create a dummy data file
        orig_data = b"Original Data Content 1234567890"
        rel_data = os.path.join('Data', 'ENG', 'Parameter', 'Dummy.pck')
        target_path = os.path.join(self.root, rel_data)
        with open(target_path, 'wb') as f:
            f.write(orig_data)

        # 2. Create a dummy exe file
        orig_exe = bytearray(b"\x90" * 100 + b"\x0f\x84\x4b\x01\x00\x00" + b"\x90" * 50)
        exe_path = os.path.join(self.root, 'DT22_en.exe')
        with open(exe_path, 'wb') as f:
            f.write(orig_exe)

        # 3. Build replacement data via ops and blob
        # Let's say new data replaces "1234567890" with "MODIFIED!!"
        new_data = b"Original Data Content MODIFIED!!"
        # ops:
        # Op 0: copy 22 bytes from orig ("Original Data Content ")
        # Op 1: take 10 bytes from blob ("MODIFIED!!")
        blob = b"MODIFIED!!"
        ops = struct.pack('<3i', 0, 0, 22) + struct.pack('<3i', 1, 0, 10)

        # Write variant.ops and variant.dat
        variant = 'testvar'
        with open(os.path.join(self.mod_dir, f'{variant}.ops'), 'wb') as f:
            f.write(ops)
        with open(os.path.join(self.mod_dir, f'{variant}.dat'), 'wb') as f:
            f.write(blob)

        # Manifest text:
        # file|path|old_sha|new_sha|size|start_op|count_ops
        # exe|layout|hex_offset|old_hex|new_hex
        orig_sha = hashlib.sha256(orig_data).hexdigest()
        new_sha = hashlib.sha256(new_data).hexdigest()
        manifest_lines = [
            f"file|{rel_data}|{orig_sha}|{new_sha}|{len(new_data)}|0|2",
            "exe|0|64|0f844b010000|909090909090"
        ]
        with open(os.path.join(self.mod_dir, f'{variant}.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(manifest_lines) + '\n')

        # Run install
        orig_argv = sys.argv
        try:
            sys.argv = ['mod_patch.py', 'install', variant]
            mp.main(script_dir=self.mod_dir)
        finally:
            sys.argv = orig_argv

        # Verify data was modified
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), new_data)

        # Verify exe was patched at offset 100 (0x64)
        with open(exe_path, 'rb') as f:
            patched_exe = f.read()
            self.assertEqual(patched_exe[100:106], b"\x90\x90\x90\x90\x90\x90")

        # Verify backups exist
        backup_dir = os.path.join(self.mod_dir, 'backup')
        self.assertTrue(os.path.exists(os.path.join(backup_dir, rel_data)))
        self.assertTrue(os.path.exists(os.path.join(backup_dir, 'DT22_en.exe')))

        # Run uninstall
        try:
            sys.argv = ['mod_patch.py', 'uninstall']
            with self.assertRaises(SystemExit) as cm:
                mp.main(script_dir=self.mod_dir)
            self.assertEqual(cm.exception.code, 0)
        finally:
            sys.argv = orig_argv

        # Verify target restored exactly to original
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), orig_data)
        with open(exe_path, 'rb') as f:
            self.assertEqual(f.read(), bytes(orig_exe))

        # Verify backup cleaned up
        self.assertFalse(os.path.exists(backup_dir))

    def test_poke_and_unpoke(self):
        # Create dummy dungeon pack
        dung_data = bytearray(b"\x00" * 50 + b"\x12\x34" + b"\x00" * 50)
        rel_dung = os.path.join('Data', 'ENG', 'Dungeon', 'st00', 'Shop.pck')
        dung_path = os.path.join(self.root, rel_dung)
        os.makedirs(os.path.dirname(dung_path), exist_ok=True)
        with open(dung_path, 'wb') as f:
            f.write(dung_data)

        # Manifest with poke
        variant = 'poketest'
        with open(os.path.join(self.mod_dir, f'{variant}.ops'), 'wb') as f:
            f.write(b'')
        with open(os.path.join(self.mod_dir, f'{variant}.dat'), 'wb') as f:
            f.write(b'')
        manifest_lines = [
            f"poke|{rel_dung}|32|1234|5678"
        ]
        with open(os.path.join(self.mod_dir, f'{variant}.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(manifest_lines) + '\n')

        orig_argv = sys.argv
        try:
            sys.argv = ['mod_patch.py', 'install', variant]
            mp.main(script_dir=self.mod_dir)
        finally:
            sys.argv = orig_argv

        # Check poked
        with open(dung_path, 'rb') as f:
            self.assertEqual(f.read()[50:52], b"\x56\x78")

        # Uninstall
        try:
            sys.argv = ['mod_patch.py', 'uninstall']
            with self.assertRaises(SystemExit) as cm:
                mp.main(script_dir=self.mod_dir)
            self.assertEqual(cm.exception.code, 0)
        finally:
            sys.argv = orig_argv

        # Check restored
        with open(dung_path, 'rb') as f:
            self.assertEqual(f.read()[50:52], b"\x12\x34")

    def _setup_two_variants(self):
        orig_data = b"Original Data Content 1234567890"
        rel_data = os.path.join('Data', 'ENG', 'Parameter', 'Dummy.pck')
        target_path = os.path.join(self.root, rel_data)
        with open(target_path, 'wb') as f:
            f.write(orig_data)

        orig_exe = bytes(b"\x90" * 100 + b"\x0f\x84\x4b\x01\x00\x00" + b"\x90" * 50)
        exe_path = os.path.join(self.root, 'DT22_en.exe')
        with open(exe_path, 'wb') as f:
            f.write(orig_exe)

        orig_sha = hashlib.sha256(orig_data).hexdigest()

        # Variant A modifies data + exe
        data_a = b"Original Data Content VARIANT_A!"
        sha_a = hashlib.sha256(data_a).hexdigest()
        ops_a = struct.pack('<3i', 0, 0, 22) + struct.pack('<3i', 1, 0, 10)
        with open(os.path.join(self.mod_dir, 'vara.ops'), 'wb') as f:
            f.write(ops_a)
        with open(os.path.join(self.mod_dir, 'vara.dat'), 'wb') as f:
            f.write(b"VARIANT_A!")
        with open(os.path.join(self.mod_dir, 'vara.txt'), 'w', encoding='utf-8') as f:
            f.write(f"file|{rel_data}|{orig_sha}|{sha_a}|{len(data_a)}|0|2\nexe|0|64|0f844b010000|909090909090\n")

        # Variant B modifies only data (leaving exe original)
        data_b = b"Original Data Content VARIANT_B!"
        sha_b = hashlib.sha256(data_b).hexdigest()
        ops_b = struct.pack('<3i', 0, 0, 22) + struct.pack('<3i', 1, 0, 10)
        with open(os.path.join(self.mod_dir, 'varb.ops'), 'wb') as f:
            f.write(ops_b)
        with open(os.path.join(self.mod_dir, 'varb.dat'), 'wb') as f:
            f.write(b"VARIANT_B!")
        with open(os.path.join(self.mod_dir, 'varb.txt'), 'w', encoding='utf-8') as f:
            f.write(f"file|{rel_data}|{orig_sha}|{sha_b}|{len(data_b)}|0|2\n")

        return target_path, exe_path, orig_data, orig_exe, data_a, data_b

    def _run_cli(self, *args):
        orig_argv = sys.argv
        buf = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.argv = ['mod_patch.py', *args]
            sys.stdout = buf
            try:
                mp.main(script_dir=self.mod_dir)
                return 0, buf.getvalue()
            except SystemExit as exc:
                return exc.code, buf.getvalue()
        finally:
            sys.stdout = orig_stdout
            sys.argv = orig_argv

    def _staged_leftovers(self):
        left = []
        for walk_root, _, files in os.walk(self.root):
            for name in files:
                if name.endswith('.dt22new'):
                    left.append(os.path.join(walk_root, name))
        return left

    def test_cross_variant_restores_exe_and_cleans_staging(self):
        target_path, exe_path, _, orig_exe, data_a, data_b = self._setup_two_variants()
        code, _ = self._run_cli('install', 'vara')
        self.assertEqual(code, 0)
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), data_a)

        code, out = self._run_cli('install', 'varb')
        self.assertEqual(code, 0, out)
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), data_b)
        with open(exe_path, 'rb') as f:
            self.assertEqual(f.read(), orig_exe)
        self.assertIn('put back as the original', out)
        self.assertEqual(self._staged_leftovers(), [])

    def test_locked_target_and_cross_back_abort_before_writes(self):
        target_path, exe_path, orig_data, orig_exe, data_a, _ = self._setup_two_variants()

        # Lock primary target during fresh install
        with hold_exclusive_lock(target_path):
            code, out = self._run_cli('install', 'vara')
        self.assertEqual(code, 1)
        self.assertIn('in use', out)
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), orig_data)
        with open(exe_path, 'rb') as f:
            self.assertEqual(f.read(), orig_exe)
        self.assertFalse(os.path.exists(os.path.join(self.mod_dir, 'backup')))
        self.assertEqual(self._staged_leftovers(), [])

        # Install vara, then lock DT22_en.exe (cross-variant restore) during varb install
        self.assertEqual(self._run_cli('install', 'vara')[0], 0)
        with hold_exclusive_lock(exe_path):
            code, out = self._run_cli('install', 'varb')
        self.assertEqual(code, 1)
        self.assertIn('in use', out)
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), data_a)
        with open(exe_path, 'rb') as f:
            self.assertEqual(f.read(), bytes(b"\x90" * 106 + b"\x90" * 50))
        self.assertEqual(self._staged_leftovers(), [])

    def test_uninstall_locked_file_aborts_without_partial_restore(self):
        target_path, exe_path, _, _, data_a, _ = self._setup_two_variants()
        self.assertEqual(self._run_cli('install', 'vara')[0], 0)
        with hold_exclusive_lock(exe_path):
            code, out = self._run_cli('uninstall')
        self.assertEqual(code, 1)
        self.assertIn('in use', out)
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), data_a)
        self.assertTrue(os.path.exists(os.path.join(self.mod_dir, 'backup')))
        self.assertEqual(self._staged_leftovers(), [])


if __name__ == '__main__':
    unittest.main()
