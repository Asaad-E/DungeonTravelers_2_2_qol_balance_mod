import io
import sys
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')

from sim.data import game_data, Skill
from sim import setup as setup_mod, scenario
from sim.variant import balance_data
from sim.battle import Battle, Action
from sim.units import Unit, PARTY, ENEMIES, build_enemy
import sim.formulas as f
from tools.parallel_party_battery import PARTIES, CHECKPOINTS, build_party_complete

data = game_data()
setup = setup_mod.load()
mod = balance_data(data)

print("="*80)
print("TEST DE IMPACTO ESPECÍFICO 1: FACTOR DE RAZA (ADITIVO VS MULTIPLICATIVO)")
print("="*80)
# We test a hit with effect 88 (e.g. +100% to undead) + 1x race UP (0.15) or 1x race Mega (0.60)
for race_id, race_name in [(5, 'Undead'), (7, 'Demon'), (8, 'Beast')]:
    for ench_share, tier_name in [(0.15, 'UP (0.15)'), (0.30, 'Grand (0.30)'), (0.60, 'Mega (0.60)')]:
        # Multiplicative (Old code bug): (1.0 + 1.0) * (1.0 + ench_share)
        old_factor = (1.0 + 1.0) * (1.0 + ench_share)
        # Additive (Binary reality x86): 1.0 + 1.0 + ench_share
        new_factor = 1.0 + 1.0 + ench_share
        diff_pct = (old_factor - new_factor) / new_factor * 100
        print(f"  Raza {race_name:<7} | Tier {tier_name:<13} | Vanilla/Bug: {old_factor:.2f}x | Binario/Fix: {new_factor:.2f}x | Inflación corregida: -{diff_pct:.1f}%")

print("\n" + "="*80)
print("TEST DE IMPACTO ESPECÍFICO 2: TOPE DE 50 EN PRECISIÓN MÁGICA (ENCHANTS 39/40)")
print("="*80)
# Check all party builds across all checkpoints: how many pieces of 39 and 40 do they have?
max_39_40 = 0
max_info = ""
for cid in CHECKPOINTS:
    for pname, pinfo in PARTIES.items():
        party = build_party_complete(mod, setup, pinfo['roles'], cid)
        for u in party:
            p39 = u.pieces(39)
            p40 = u.pieces(40)
            pts = 3 * p39 + 2 * p40
            if pts > max_39_40:
                max_39_40 = pts
                max_info = f"{u.name} en {pname} ({cid}): {p39}x UP (+{3*p39}), {p40}x MiniUP (+{2*p40}) -> {pts} pts"

print(f"  Máximo valor de precisión mágica por encantamientos encontrado en todas las parties:")
print(f"  {max_info if max_info else '0 puntos (ningún equipo equipó encantamientos 39/40)'}")
print(f"  ¿Supera el tope de 50?: {'SÍ (afectado por el cap)' if max_39_40 > 50 else 'NO (0 impacto práctico en la curva de historia)'}")

print("\n" + "="*80)
print("TEST DE IMPACTO ESPECÍFICO 3: HABILIDADES CON PRECISIÓN FIJA (EFECTO 55 Y 72)")
print("="*80)
skills_with_55_72 = []
for sid, sk in data.skills.items():
    for eid, _, vals in sk.effects:
        if eid in (55, 72):
            skills_with_55_72.append((sk.name, eid, vals))

print(f"  Habilidades con efecto 55 (Precisión Fija) o 72 (Valor Directo): {len(skills_with_55_72)}")
for sname, eid, vals in skills_with_55_72:
    min_val = min(vals) if vals else 0
    print(f"    - {sname:<25} | Efecto {eid} | Valores: {vals} | Menor valor: {min_val*100:.1f}%")

print("\n" + "="*80)
print("TEST DE IMPACTO ESPECÍFICO 4: INMUNIDADES Y RESISTENCIAS A ESTADOS ALTERADOS EN JEFES")
print("="*80)
# Check how many story bosses have bit 12 (turn delay immunity) and their ailment resistances
c_bosses = []
for cid in ('C10', 'C13', 'C17', 'C19', 'C24', 'C26', 'C28', 'C29', 'C30', 'C32', 'C34', 'C36', 'C38', 'C40'):
    cp = setup.checkpoint(cid)

    _, grps = scenario.checkpoint_fight(mod, setup, cid)
    for g in grps:
        for e in g:
            td_immune = 'turn delay' in e.immune
            c_bosses.append((cid, e.name, td_immune, e.immune))

print(f"  Jefes con inmunidad a Turn Delay (bit 12) añadida por el Mod:")
for cid, bname, td, imm in c_bosses[:14]:
    print(f"    - {cid:<4} | {bname:<22} | Inmune a Turn Delay: {'SÍ' if td else 'NO'} | Inmunidades: {len(imm)}")
