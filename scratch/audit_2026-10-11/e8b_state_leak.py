"""E8b. Does a run change what the next run of the same process gives? The same measures repeated in one process."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_lib as A
data, setup, variant = A.state()
level = A.scenario.reference_levels(data, setup)['C40'][0]


def exp(source, roles):
    r = A.measures.expedition(source, setup, 'St15_1150', level, 'C40', roles=roles, battles=8, runs=12)
    return r['won']


def boss():
    r = A.play_cell(variant, setup, A.B.PARTIES['Mage-Heavy']['roles'], 'C36', 12)
    return r['wins'], round(r['time'], 5)


print('boss cell           ', boss())
print('expedition reference', exp(data, None), exp(data, None), '(the same call twice)')
print('expedition Dual     ', exp(data, A.B.PARTIES['Dual-Support']['roles']))
print('expedition reference', exp(data, None), '(after another party)')
print('expedition variant  ', exp(variant, None))
print('expedition reference', exp(data, None), '(after the variant)')
print('boss cell           ', boss())
