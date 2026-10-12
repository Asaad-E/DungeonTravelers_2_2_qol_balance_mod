"""E8. Is a run of the simulator the same in two processes? One cell, same seeds, printed as a fingerprint.
Run it under different values of PYTHONHASHSEED and compare."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_lib as A
data, setup, variant = A.state()
for cid, pname in (('C36', 'Mage-Heavy'), ('C32', 'Anti-Meta')):
    r = A.play_cell(variant, setup, A.B.PARTIES[pname]['roles'], cid, 20)
    print(os.environ.get('PYTHONHASHSEED'), cid, pname, r['wins'], round(r['time'], 6), round(r['enemy_actions'], 3))
