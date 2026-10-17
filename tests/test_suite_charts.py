"""tools/suite_charts.py compiles: a broken chart tool fails the tests, not only the last step of the suite."""
import os
import py_compile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SuiteChartsCompile(unittest.TestCase):
    def test_compiles(self):
        py_compile.compile(os.path.join(ROOT, 'tools', 'suite_charts.py'), doraise=True)


if __name__ == '__main__':
    unittest.main()
