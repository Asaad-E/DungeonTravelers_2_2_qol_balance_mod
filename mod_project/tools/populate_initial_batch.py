import os
import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')

SKILL_UPDATES = {
    "Provoke": {
        "desc": "Attract single-target attacks to user with high speed turn recovery.",
        "lvup": "Turns: 3 (L1) -> 4 (L2) -> 5 (L3) -> 6 (L4) -> 7 (L5 Max).\nSpeed: +50% -> +63% -> +76% -> +89% -> +100%. TP: 1 -> 2 -> 3 -> 4 -> 5.",
        "notes": "Fast turn recovery (+50% to +100% action delay)."
    },
    "War Cry": {
        "desc": "Raise party physical ATK & replace debuffs. Usable out of battle.",
        "lvup": "ATK: +8% (L1) -> +10% (L2) -> +12% (L3) -> +14% (L4) -> +18% (L5 Max).\nTurns: 4 -> 5 -> 6 -> 7 -> 8. TP Cost: 5 -> 7 -> 9 -> 11 -> 13.",
        "notes": "Best party physical buff. Replaces active ATK debuffs."
    },
    "Raging Smash": {
        "desc": "Short-range skill. Strike one enemy for 125% ATK (+8%/Lv, Max 200%).",
        "lvup": "Hit Rate: +20% (+2%/Lv, Max +38%). Action delay: 0.80x~0.90x.\nTP Cost: 5 (Lv1) -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28 (Max).",
        "notes": "Short weapon only. Solid accuracy scaling."
    },
    "Sword Mastery": {
        "desc": "Increases equipped sword base ATK.",
        "lvup": "ATK: +3% (L1) -> +5% (L2) -> +7% (L3) -> +9% (L4) -> +10% (L5)... +15% (L10 Max).\nGrowth: +2%/Lv for Lv1-4, then +1%/Lv for Lv5-10.",
        "notes": "Scales off base weapon ATK, not total character ATK."
    },
    "Axe Mastery": {
        "desc": "Increases equipped axe base ATK.",
        "lvup": "ATK: +3% (L1) -> +5% (L2) -> +7% (L3) -> +9% (L4) -> +10% (L5)... +15% (L10 Max).\nGrowth: +2%/Lv for Lv1-4, then +1%/Lv for Lv5-10.",
        "notes": "Scales off base weapon ATK."
    },
    "Lance Mastery": {
        "desc": "Increases equipped lance base ATK.",
        "lvup": "ATK: +3% (L1) -> +5% (L2) -> +7% (L3) -> +9% (L4) -> +10% (L5)... +15% (L10 Max).\nGrowth: +2%/Lv for Lv1-4, then +1%/Lv for Lv5-10.",
        "notes": "Scales off base weapon ATK."
    },
    "Avenger": {
        "desc": "Counterattack short/medium physical hits with equipped weapon.",
        "lvup": "Counter: 6% (L1) -> 9% (L2) -> 12% (L3) -> 15% (L4) -> 18% (L5 Max).\nCaution: short-range retaliations will trigger enemy Dark Aura.",
        "notes": "Counter range matches weapon reach. Beware Dark Aura."
    },
    "Double Attack": {
        "desc": "Chance to attack twice when using normal attacks.",
        "lvup": "Trigger: 9% (L1) -> 12% (L2) -> 15% (L3) -> 18% (L4) -> 21% (L5 Max).\nCan stack with Triple Attack (up to 5 strikes total).",
        "notes": "High synergy with Luco unique skill."
    },
    "Defender": {
        "desc": "Increase own DEF at the cost of ATK (ATK debuff can be cleansed).",
        "lvup": "DEF: +20% (L1) -> +27% (L2) -> +35% (L3) -> +42% (L4) -> +50% (L5 Max).\nATK: -11% -> -14% -> -18% -> -21% -> -25%. TP Cost: 8 -> 10 -> 12 -> 14 -> 16.",
        "notes": "Lasts 4~8 turns. 1.25x~1.77x speed. ATK debuff is removable."
    },
    "Cover": {
        "desc": "Step forward to intercept physical attacks aimed at allies.",
        "lvup": "Turns: 4 (L1) -> 5 -> 6 -> 7 -> 8 (L5 Max). TP Cost: 10 -> 13 -> 16 -> 20 -> 24.\nGuard chance: 30%~60% on hit. Requires 1H weapon & shield.",
        "notes": "Can evade while covering. May attract counters."
    },
    "Parry": {
        "desc": "Short-range skill. Block physical attacks with equipped weapon.",
        "lvup": "Turns: 3 (L1) -> 4 -> 5 -> 6 -> 7 (L5 Max). TP Cost: 10 -> 13 -> 16 -> 19 -> 22.\nMay break on consecutive blocks. Fast recovery (1.30x speed).",
        "notes": "Blocks single/AoE physical damage toward user."
    }
}

ITEM_UPDATES = {
    "Croissant": "A fresh, flaky crescent pastry. Restores 60 HP to one ally.",
    "Danish": "A sweet fruit-topped bakery treat. Restores 250 HP to one ally.",
    "Bagel Sandwich": "A hearty and satisfying bagel meal. Restores 500 HP to one ally.",
    "Pain Aux Raisins": "A luxurious bakery treat. Fully restores an ally's HP (9,999 HP).",
    "Gateau Au Chocolat": "Rich chocolate cake baked to share. Restores 100 HP to all allies.",
    "Maharaja Curry": "Super spicy curry. Restores 200 HP and boosts physical ATK for 3 turns.",
    "Refreshing Eye Drop": "A soothing herbal tincture. Clears overworked vision, curing Blindness."
}

def populate_skills():
    excel_path = os.path.join(TABLES_DIR, 'skills.xlsx')
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Skills"]
    
    updated = 0
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=4).value
        if name in SKILL_UPDATES:
            u = SKILL_UPDATES[name]
            ws.cell(row=row, column=9).value = u["desc"]
            ws.cell(row=row, column=10).value = u["lvup"]
            ws.cell(row=row, column=11).value = "Approved"
            ws.cell(row=row, column=12).value = u["notes"]
            updated += 1
            
    wb.save(excel_path)
    print(f"Updated {updated} skills in {excel_path}")

def populate_items():
    excel_path = os.path.join(TABLES_DIR, 'items.xlsx')
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Items"]
    
    updated = 0
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=3).value
        if name in ITEM_UPDATES:
            ws.cell(row=row, column=6).value = ITEM_UPDATES[name]
            ws.cell(row=row, column=7).value = "Approved"
            updated += 1
            
    wb.save(excel_path)
    print(f"Updated {updated} items in {excel_path}")

if __name__ == "__main__":
    populate_skills()
    populate_items()
