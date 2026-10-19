"""The table of conformity of the engine with the program (data_tables/engine_conformity.json): no item left MISMATCH or
PARTIAL, every address in the program, every engine method still defined (tools/engine_conformity.py)."""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))


class EngineConformity(unittest.TestCase):
    def test_every_item_passes(self):
        import engine_conformity
        data = json.load(open(engine_conformity.TABLE, encoding='utf-8'))
        try:
            failed = engine_conformity.checks(data['items'])
        except (FileNotFoundError, OSError) as e:          # no program file on this machine
            self.skipTest(str(e))
        self.assertEqual([], failed)


if __name__ == '__main__':
    unittest.main()
