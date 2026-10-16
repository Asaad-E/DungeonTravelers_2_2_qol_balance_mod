"""One-off: data_tables/measure_config.json, the configuration of the measures of the C# suite (parties, places, cases,
thresholds, the rules a measure gives a skill, the wording of the audit), taken once from the constants of the Python
measure scripts, which were their only home. From now on the JSON is the source (tools/engine_export.py reads it); the
Python scripts keep their own copy as the historical reference."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'measures')]

import boss_rows_check                                       # noqa: E402
import curve_ablation                                        # noqa: E402
import dance_trial                                           # noqa: E402
import def_debuff_trial                                      # noqa: E402
import design_rows                                           # noqa: E402
import etoile_dances                                         # noqa: E402
import etoile_trial                                          # noqa: E402
import lize_ideas                                            # noqa: E402
import magic_wall                                            # noqa: E402
import measure_open_rows                                     # noqa: E402
import mercenaries                                           # noqa: E402
import party_skills                                          # noqa: E402
import postgame_compare                                      # noqa: E402
import provoke_trial                                         # noqa: E402
import random_battles                                        # noqa: E402
import regression_r04                                        # noqa: E402
import sage_buffs_trial                                      # noqa: E402
import sim_audit                                             # noqa: E402
import skill_value_contested                                 # noqa: E402
import tp_items_trial                                        # noqa: E402
import unique_skills                                         # noqa: E402
import win_rates                                             # noqa: E402
from sim.battle import HANDLED                               # noqa: E402


def lists(table):
    return {k: list(v) for k, v in table.items()}


HEALS = [103, 9, 104, 128, 130, 131, 132, 133]
config = {
    'about': 'The configuration of the measures of the C# suite (engine_cs/src/DtEngine/Suite), read by tools/engine_export.py into '
             'the snapshot. Taken on 2026-10-16 from the constants of the Python scripts of measures/ and tools/ (kept there as the '
             'historical reference); change it here.',
    'win_rates': {'parties': {k: [v[0], v[1], v[2]] for k, v in win_rates.PARTIES.items()}, 'flag': win_rates.FLAG, 'low_below': 0.5},
    'sim_audit': {'tiers': [list(t) for t in sim_audit.TIERS], 'late': list(sim_audit.LATE), 'seeds': sim_audit.SEEDS,
                  'enemy': sim_audit.ACTIVES_ENEMY, 'tries': sim_audit.ACTIVE_TRIES, 'fallback': sim_audit.ACTIVES_FALLBACK,
                  'outside': sorted(e for e, where in HANDLED.items() if where.startswith('outside battle')),
                  'damage_effects': [8, 12, 138, 140, 141, 142, 434, 435],
                  'situational': [{'effects': [104, 105], 'why': 'situational: a revive'},
                                  {'effects': [103, 9, 128, 130, 131, 132, 133],
                                   'why': 'situational: a heal (another heal or the songs come first)'},
                                  {'effects': [106, 235], 'why': 'situational: a cure'},
                                  {'effects': [129, 426], 'why': 'situational: TP'},
                                  {'effects': [74], 'why': 'situational: a dispel'}]},
    'skill_value': {'rules': [{'effects': [105], 'condition': 'ally_down', 'action': 'revive'},
                              {'effects': [106, 235], 'condition': 'ally_ailing', 'action': 'cure'},
                              {'effects': HEALS, 'condition': 'ally_hp_below:0.7', 'action': 'heal:0.7'},
                              {'effects': [129, 426], 'condition': 'ally_tp_below:0.5', 'action': 'tp:0.5'}],
                    'attacking': [0, 1, 8, 12, 138, 140, 141, 142, 434, 435], 'chain_seed': 7},
    'support_chains': {'chain_seed': 7},
    'class_stages_report': {'hard_below': 0.5},
    'mercenaries': {'places': list(mercenaries.PLACES)},
    'party_skills': {'places': list(party_skills.PLACES), 'resist': dict(party_skills.RESIST),
                     'skills': {k: [v[0], dict(v[1])] for k, v in party_skills.SKILLS.items()}},
    'postgame_compare': {'steps': list(postgame_compare.STEPS), 'flag': 0.15},
    'unique_skills': {'roles': dict(unique_skills.ROLES), 'places': [list(p) for p in unique_skills.PLACES], 'pep': dict(unique_skills.PEP)},
    'skill_value_contested': {'contested': list(skill_value_contested.CONTESTED), 'not_battle': dict(skill_value_contested.NOT_BATTLE),
                              'wins': skill_value_contested.WINS, 'length': skill_value_contested.LENGTH, 'hp': skill_value_contested.HP},
    'random_battles': {'chain': random_battles.CHAIN, 'ahead': random_battles.AHEAD},
    'regression_r04': {'substitutes': {k: list(v) for k, v in regression_r04.SUBSTITUTES.items()}},
    # Eccentrics: AGI +20 since row P091 (effect 366), edited in the JSON on 2026-10-16
    'boss_rows_check': {'fields': list(boss_rows_check.FIELDS), 'keys': list(boss_rows_check.KEYS)},
    'design_rows': {'swaps': dict(design_rows.SWAPS), 'no_magic': design_rows.NO_MAGIC, 'down': list(design_rows.DOWN),
                    'steps_a_turn': design_rows.STEPS_A_TURN},
    'trials': {
        'dance_trial': {'parties': lists(dance_trial.PARTIES), 'cases': dict(dance_trial.CASES), 'dances': dict(dance_trial.DANCES)},
        'def_debuff_trial': {'parties': lists(def_debuff_trial.PARTIES), 'cases': list(def_debuff_trial.CASES), 'samba': def_debuff_trial.SAMBA,
                             'pierce': def_debuff_trial.PIERCE, 'def_down': def_debuff_trial.DEF_DOWN,
                             'usual': ['status:195', 'status:199']},   # her two dances since 2026-10-15 (Waltz, Salsa)
        'samba_trial': {'second': ['status:199', 'status:201']},
        'etoile_dances': {'dances': dict(etoile_dances.DANCES), 'pairs': [list(p) for p in etoile_dances.PAIRS]},
        'etoile_trial': {'dances': dict(etoile_trial.DANCES), 'factors': list(etoile_trial.FACTORS)},
        'lize_ideas': {'girl': lize_ideas.GIRL, 'ideas': [[label, list(idea) if isinstance(idea, tuple) else idea] for label, idea in lize_ideas.IDEAS]},
        'magic_wall': {'elements': list(magic_wall.ELEMENTS)},
        'measure_open_rows': {'weapon': dict(measure_open_rows.WEAPON), 'role': dict(measure_open_rows.ROLE), 'stage': dict(measure_open_rows.STAGE)},
        'provoke_trial': {'provoke': list(provoke_trial.PROVOKE), 'enmity': provoke_trial.ENMITY, 'vanilla': list(provoke_trial.VANILLA)},
        'sage_buffs_trial': {'chanted': list(sage_buffs_trial.CHANTED), 'sized': dict(sage_buffs_trial.SIZED), 'extra_rules': list(sage_buffs_trial.EXTRA_RULES)},
        'tp_items_trial': {'fruit': tp_items_trial.FRUIT, 'trials': lists(tp_items_trial.TRIALS)},
        'curve_ablation': {'places': list(curve_ablation.PLACES), 'cases': list(curve_ablation.CASES)},
    },
}
with open(os.path.join(ROOT, 'data_tables', 'measure_config.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')
