"""Tests for cross-platform installer/mod_patch.py (Linux/Steam Deck installer)."""
import hashlib
import os
import shutil
import struct
import sys
import tempfile
import unittest

import installer.mod_patch as mp


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


if __name__ == '__main__':
    unittest.main()
