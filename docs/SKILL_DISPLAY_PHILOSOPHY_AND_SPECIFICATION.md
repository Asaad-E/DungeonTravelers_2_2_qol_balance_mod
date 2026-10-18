# Skill Display Specification

This specification defines how skill descriptions, tooltips, and level-up boxes are formatted across both the QoL and Balance variants. It applies to `data_tables/qol_skill_text.xlsx`, `data_tables/balance_skill_text.xlsx`, and the automated formatting tools (`tools/generate_qol_skill_text.py`, `tools/text_checks.py`).

---

## 1. Engine & UI Constraints

The *Dungeon Travelers 2-2* PC engine imposes several strict rendering constraints:

1. **Physical Line Limit**: At most **3 lines** per skill description box.
2. **Line Width Limit**: At most **85 characters** per line to fit the in-game dialog window without truncation or broken line wrapping.
3. **Battle Action Bar**: In combat, only **Line 1** is displayed, and the usable width is limited to **70 characters**.
4. **Font Encoding Safety**: **Never use tildes (`~`)**. The game font engine maps tildes to invalid glyphs, causing corrupted characters on screen. Use hyphens (`-`) or arrows (`->`) instead.
5. **Static Strings**: The game engine stores a single static description per skill rather than dynamic per-level templates. Therefore, tooltips must convey progression across skill levels within a single box.

---

## 2. Layout Blueprint

Every skill tooltip is organized into three structured lines:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Line 1] Original description + qualitative damage tier or ailment chance              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Line 2] Primary effect & level progression (e.g., ATK, healing, or defense scaling)   │
│ [Line 3] Turn duration, TP costs per level, and action speed / delay multiplier        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Formatting Standards

### 3.1 Line 1: In-Game Flavor & Summary

Line 1 preserves the original English prose while appending quick reference data for the combat action bar:

* **Damage Tier**: Added directly into the sentence using standard tiers: *Negligible* (<80%), *Minor* (80-249%), *Moderate* (250-399%), *Major* (400-499%), *Severe* (500-699%), or *Tremendous* (700%+).
* **Ailment Chance**: Appended as a concrete percentage:
  * Static chance: `"May stun (25%)"`
  * Slight scaling: `"May stun (30%+)"`
  * Wide scaling: `"May poison (20-50%)"`
* **In-Universe Glossary**: Always use the game's official terminology (e.g., `Enmity`, `resistance`, `Physical accuracy`). Never invent external acronyms or rebrand existing mechanics.

### 3.2 Lines 2 & 3: Level-by-Level Progression

To keep information instantly readable during gameplay, progression uses clean step arrows (`->`):

* **5-Level Skills** (Buffs, Debuffs, Utility):
  All 5 values are written explicitly:
  `ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)`
  `Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13`

* **10-Level Skills** (Attacks, Spells, Masteries):
  * *Standard case*: When numbers fit within 85 characters, write all 10 values:
    `TP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28`
  * *Compact case*: If wide 3-digit values exceed line length, write base, step increment, and cap:
    `ATK: 125% (+8%/Lv) -> 200% (L10 Max) | Hit Rate: +20% (+2%/Lv)`
  * *Prohibited*: Never use fractional averages like `(avg +3.33%/Lv)` that force the player to calculate current values in their head.

---

## 4. Reference Examples

### Fighter: `War Cry` (5-Level Party Buff)
```text
Raise the party's ATK.
ATK: +8% -> +10% -> +12% -> +15% -> +18% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13
```

### Fighter: `Raging Smash` (10-Level Physical Burst)
```text
Short-range skill. Major strike to one enemy.
ATK: 125% -> 134 -> 143 -> 152 -> 161 -> 170 -> 178 -> 186 -> 193 -> 200% (L10)
Accuracy: +20% (+2%/Lv) | TP Cost: 5 (+2-3/Lv) -> 28 | Speed: 0.8x -> 0.9x
```

### Magic User: `Fireball` (10-Level Elemental Spell)
```text
Deal minor fire damage to one enemy.
Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520 (L10)
TP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32 (Max)
```

### Scout: `Evade` (5-Level Evasion Buff)
```text
Increase own physical evasion rate.
EVA: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 4 -> 6 -> 8 -> 10 -> 12
```

### Maid: `First Aid` (Percentage Healing Technique)
```text
Heal one ally's HP.
Heal: 12% Max HP -> 15% -> 18% -> 21% -> 25% (L1-5 Max)
TP Cost: 2 -> 4 -> 6 -> 8 -> 10 | Affected by Maid Mastery
```

### Passive: `Sword Mastery` (10-Level Passive ATK)
```text
Increases equipped sword base ATK.
ATK: +3% (L1) -> +5% -> +7% -> +9% -> +11% -> +12% -> +13% -> +14% -> +15% (L10)
```

---

## 5. Build Verification

The build script (`tools/build_variant.py`) and test suite (`tests/test_text_checks.py`) strictly validate:
1. Every numeric value against the compiled binary data.
2. Every line length against character limits (70 for battle bar, 85 for tooltips).
3. Total line counts per box ($\le 3$ lines).
4. Total absence of illegal characters (such as tildes).
