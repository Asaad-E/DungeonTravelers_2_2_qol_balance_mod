"""
The choices of the model, read from data_tables/sim_setup.xlsx (see its sheet About). Nothing here holds a value.
"""
import os

import openpyxl

from sim.data import PROJECT_DIR

SETUP = os.path.join(PROJECT_DIR, 'data_tables', 'sim_setup.xlsx')


def _rows(wb, name):
    it = wb[name].iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it if any(v is not None for v in r)]


class Setup:
    def __init__(self, path=SETUP):
        wb = openpyxl.load_workbook(path, read_only=True)
        self.settings = {r['Key']: r['Value'] for r in _rows(wb, 'Settings')}
        self.policies = _rows(wb, 'Policies')
        self.roles = {r['Role']: r for r in _rows(wb, 'Roles')}
        self.composition = [r['Role'] for r in sorted(_rows(wb, 'Composition'), key=lambda r: r['Order'])]
        self.checkpoints = _rows(wb, 'Checkpoints')
        self.joins = [(r['Chapter'], [n.strip() for n in str(r['Characters who join in it']).split(';')])
                      for r in _rows(wb, 'Joins')]
        self.assumptions = _rows(wb, 'Assumptions')
        self.calibration = _rows(wb, 'Calibration')

    def checkpoint(self, cid):
        return next(c for c in self.checkpoints if c['ID'] == cid)


_cache = {}


def load(path=SETUP):
    stamp = os.path.getmtime(path)
    if _cache.get('stamp') != stamp:
        _cache['setup'], _cache['stamp'] = Setup(path), stamp
    return _cache['setup']
