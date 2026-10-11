"""
Kept for the scripts that import it. The battery is tools/party_battery.py; the parties and the bosses are the sheet
BatteryParties and Settings battery_checkpoints of data_tables/sim_setup.xlsx, and a party is built by
sim/scenario.py party_of_roles (full whenever five characters have joined, one bag for the party).

    python mod_project/tools/party_battery.py all | report
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sim import scenario                                 # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
import party_battery                                     # noqa: E402

_SETUP = setup_mod.load()
CHECKPOINTS = party_battery.checkpoints(_SETUP)
PARTIES = {name: {'roles': roles, 'desc': archetype, 'opt': archetype} for name, (archetype, roles) in _SETUP.battery.items()}


def build_party_complete(data_source, setup, role_names, cid):
    return scenario.party_of_roles(data_source, setup, cid, role_names)


if __name__ == '__main__':
    print(__doc__)
