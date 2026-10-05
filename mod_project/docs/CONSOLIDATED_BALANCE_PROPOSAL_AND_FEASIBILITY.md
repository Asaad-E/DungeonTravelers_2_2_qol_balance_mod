# Dungeon Travelers 2-2: Master Balance Proposal, Community Foundations, and Technical Feasibility Reference

**Document Status:** Definitive Technical & Balance Reference  
**Scope:** Consolidated compilation of all proposed balance adjustments, Japanese community origins, verified vanilla baselines, dialogue script adaptations, and technical binary feasibility classification.  
**Language:** English  

---

## 1. Executive Summary & Methodological Foundations

### 1.1 Source-of-Truth Mandate
All vanilla baseline parameters in this document are extracted directly from `vanilla_source_of_truth.xlsx` and raw binary parameter archives (`.bin` / `.pck`). Earlier design drafts occasionally based balance proposals on forum memory or unverified baselines (e.g., assuming *Halving Slice* was 115%–175% when the binary is 80%–110%). Any future balance adjustments must strictly branch from verified source-of-truth baselines.

### 1.2 Note on Theoretical Combat Simulations
Earlier combat simulation models (`exhaustive_combat_simulator.py`) evaluated theoretical turn-economy pacing using hardcoded enemy stat baselines (e.g., 180 AGI, 380 DEF), as enemy attribute tables are not stored in player parameter archives. They serve as mathematical trend indicators rather than live engine battle telemetry.

### 1.3 Technical Feasibility Classification
Proposed modifications are categorized into four technical classifications:

* **Group 1: Verified in Binary Data Tables (Technically Functional in PCKs)**  
  Parameters with mapped, confirmed binary structs that have been successfully injected and tested:
  * Weapon delay multipliers in `WeaponRankData.pck`.
  * EXP curve and early SP bonuses in `LvExpSkptData.pck`.
  * Quest Rank bag capacities and gold bounties in `QuestRankData.pck`.
  * Consumable recovery values in `ItemData.pck`.
  * `Slave's Torc` training accessory with native Double EXP (Enchant ID 275).  
  *(Note: The active workspace branch currently runs the pure QoL variant with 100% vanilla parameters).*

* **Group 2: Feasible & Confirmed in Known PCK Structs (Ready to Implement)**  
  Fields verified in `.pck` binary records, where earlier builds updated display text but left binary values untouched:
  * Skill TP cost integer arrays and power float arrays (`TechniqueSkillData.pck`, `MagicSkillData.pck`).
  * Spell chant speed multipliers in `MagicSkillData.pck`.
  * Action recovery delay floats (*Attract*, *Dark Aura*).
  * *Tinker Squash* turn delay pushback float array (25% → 43%).
  * *Cover* interception mitigation per-level parameter (0.7 → 0.4).
  * Passive proc rates (*Holy Shield*, *Concentrate*).
  * Trap damage and instant-death rate floats in `TrapData.pck`.
  * *Golden Apple* Full TP recovery (set float to `999.0`, matching vanilla `Mermaid Meat`).

* **Group 3: Probably Feasible in PCK Tables (Unconfirmed Structs)**  
  Parameters believed to reside in existing parameter files whose exact offsets require final mapping:
  * Paladin base DEF growth multiplier in `ClassLevelData.pck`.
  * Summon doll attribute scaling and duration parameters in minion skill records.
  * Joint Skill Pep and TP cost headers in `JoinSkillData.pck`.
  * Grand Sealbook aura assignments in `SealScrollData.pck`.

* **Group 4: No Known Data Parameter Found (Unverified / Unknown Storage / Engine Code)**  
  Mechanics where no corresponding parameter field, flag, or struct exists in inspected data tables:
  * *Elemental Resistance Penetration (+50 pierce):* No magic penetration flag exists in `MagicSkillData.pck`.
  * *Universal Defend Command Immunity:* Crit/interrupt immunity is not parameter-driven in `StringData.pck`.
  * *Global Chant Crit Interrupt Rule (33.3%):* Hardcoded combat rule with no parameter table.
  * *Summon Doll Guts (1 HP Survival):* Minion entities lack passive trait slots for Guts.
  * *Buffet Meal 900-Step Duration & Dispel Immunity:* No step counter or dispel flag exists in `FoodMenuData.pck`.
  * *Boss Diminishing Returns:* No stateful resistance counter exists in enemy data.
  * *Percentage Forging (+3%/level):* Weapon stat increases per forge level are hardcoded formulas.
  * *Level Reset Dynamic Catch-Up Formula:* No engine formula dynamically multiplies EXP by level gap.

---

## 2. Japanese Community Foundations & Grievance Mapping

All proposed adjustments originated from documented friction in Japanese community archives (2ch/5ch strategy threads, the DT2-2 Atwiki, and high-difficulty postgame logs):

```
┌────────────────────────────────────────────────────────┐
│             COMMUNITY GRIEVANCES (ATWIKI / 2CH)        │
└──────────────────────────┬─────────────────────────────┘
                           │
   ┌───────────────────────┼────────────────────────┐
   ▼                       ▼                        ▼
[Action Speed       [Postgame Magic          ["Trap Skill Level"
 Hegemony]           Collapse & 33.3%]        TP Inversion]
   │                       │                        │
   ▼                       ▼                        ▼
• Compressed Delay   • Master Spell Chant/    • Flattened TP Curves
  Multipliers (D-F)    Power Adjustments        at Levels 6-10
• 2H Weapon Viability• Spell Power Scaling    • Preserved Damage/Proc
                       (Penetration proxy)      Scalings
   │                       │                        │
   ├───────────────────────┼────────────────────────┤
   ▼                       ▼                        ▼
[Mandatory Valkyrie [Soul Summoner           [Endgame Crown Grind
 & Frontline Lock]   Doll Fragility]          & Early Attrition]
   │                       │                        │
   ▼                       ▼                        ▼
• Paladin DEF Boost  • Doll Per-Level Scaling • Smoothed EXP Curve
• Dark Lord Attract    (Duration & Stats)       (-35.7% at Lv71-99)
• Defend Command     • Summon Survivability   • Bag Storage Milestones
  Stance Utility                                (40 & 50 slots)
```

### Community Perception vs. Binary Reality
* **TP Inversion Complaint:** Accurate for certain physical techniques (e.g., *Halving Slice* TP nearly doubles from 38 to 74 while damage only scales from 80% to 110%). Inaccurate for elemental spells (*Fireball* base power scales strongly from 175 to 520 between Lv 4 and Lv 10; spell collapse was driven by boss resistances and chant interruptions).
* **Berserk Defense Complaint:** Japanese forum claims that *Berserk* "reduces DEF to 0" are false; binary data proves DEF is reduced by -11% to -25%.
* **Gun Weapon Restriction:** Certain techniques in `TechniqueSkillData.pck` support Bow/Gun, though the majority remain bow-exclusive.

---

## 3. Comprehensive Balance Catalog & Baseline Verification

### System A: Action Economy & Weapon Speed Recovery (`WeaponRankData.pck`)
* **Community Friction:** Heavy weapons (2H Greatswords, 2H Axes, Firearms) have high recovery delay multipliers ($2.30\times \sim 2.90\times$, Ranks D to F) and forfeit the off-hand shield slot. Endgame bosses with 150+ AGI lap heavy weapon users 2 to 3 times, creating high mortality before a second action.
* **Exact Multipliers:**

| Delay Rank | Weapon Types | Vanilla Multiplier | Proposed Balanced Multiplier | Relative Turn Recovery Gain |
|:---:|:---|:---:|:---:|:---:|
| **Rank A+** | Daggers, Shortswords, Fans | `1.00x` | **`1.00x`** | Baseline benchmark |
| **Rank A** | Rapiers, Light Katanas | `1.20x` | **`1.15x`** | +4.2% faster |
| **Rank B+** | Standard 1H Swords, Short Bows | `1.40x` | **`1.30x`** | +7.1% faster |
| **Rank B** | Spears, Whips, Cards | `1.60x` | **`1.45x`** | +9.4% faster |
| **Rank C+** | Heavy Katanas, Great Spears | `1.80x` | **`1.60x`** | +11.1% faster |
| **Rank C** | Flails, War Hammers | `2.00x` | **`1.75x`** | +12.5% faster |
| **Rank D+** | Heavy Bows, Greatbows | `2.15x` | **`1.85x`** | +14.0% faster |
| **Rank D** | 2H Greatswords | `2.30x` | **`1.95x`** | **+15.2% faster** |
| **Rank E+** | Heavy 2H Greatswords | `2.45x` | **`2.05x`** | **+16.3% faster** |
| **Rank E** | 2H Battleaxes, Heavy Guns | `2.60x` | **`2.15x`** | **+17.3% faster** |
| **Rank F+** | Heavy Artillery Guns | `2.75x` | **`2.25x`** | **+18.2% faster** |
| **Rank F** | Anti-Materiel Rifles / Colossal Axes | `2.90x` | **`2.35x`** | **+19.0% faster** |

* **Status:** **Group 1 (Verified in Data).** The 12 IEEE 754 floats at offset `0x10` of `WeaponRankData.pck` are verified and functional. Theoretical 2H passive damage mitigation traits fall into **Group 4 (No Data Parameter Found)**.

---

### System B: Magic Scaling, Chant Delays & Spell Tuning (`MagicSkillData.pck`)
* **Community Friction:** Endgame bosses feature $\ge 100$ all-element resistances, cutting magic damage by $\ge 50\%$. Multi-hit attacks frequently trigger chant critical interrupts (flat 33.3%). Physical burst classes (*Dark Lord*, *Samurai*, *Sniper*) deal immediate defense-piercing burst damage, relegating pure casters (*Witch*, *Sage*) to utility roles.
* **Exact Parameters & Baselines:**

| Spell / Mechanic | Target File | Real Vanilla Baseline | Proposed Parameter | Status / Technical Classification |
|---|---|---|---|---|
| **Master Spells Chant** | `MagicSkillData_0146..162.bin` | Stored as Multipliers (e.g. `1.25x`) | **-25% to -33% Multiplier** | Group 2 (Float edit feasible; stored as multipliers, not raw frames) |
| **Master Spells Power** | `MagicSkillData_0146..162.bin` | Lv 5: `1,300` | **Lv 5: `1,650` (+27%)** | Group 2 (Float edit feasible) |
| **Master Spells TP** | `MagicSkillData_0146..162.bin` | `40 -> 84 TP` | **`28 -> 52 TP`** | Group 2 (Int array edit feasible) |
| **Tier 3 All Spells Power** | `MagicSkillData.pck` | **`300 -> 750 power`** | **`380 -> 850 power`** | Group 2 (Float edit feasible) |
| **Circle Heal HP Cap** | `MagicSkillData.pck` | **`80 -> 600 HP`** | **`120 -> 900 HP`** | Group 2 (Float edit feasible) |
| **Heal HP Cap** | `MagicSkillData.pck` | `100 -> 800 HP` | **`150 -> 1,200 HP`** | Group 2 (Float edit feasible) |
| **Elemental Resistance Pierce** | Master Spell Flag | `0 Res Pierce` | **`50 Res Pierce`** | **Group 4 (No data parameter found in PCK structs)** |
| **Global Chant Crit Interrupt** | Combat Engine Global | Flat `33.3%` per crit hit | **`10.0%` base** | **Group 4 (No data parameter found in PCK structs)** |
| **Concentrate Lv 5 Passive** | `PassiveSkillData.pck` | Cast speed multiplier | **80% Interrupt Resistance** | **Group 4 (No data parameter found in PCK structs)** |

* **Note on Elemental Resistance Penetration:** No field, offset, or bitmask exists for magic penetration in `MagicSkillData.pck` (unlike physical Armor Penetration). Directly tuning base spell power floats (e.g., from 1,300 to ~1,800–2,000) provides the effective operational proxy for higher endgame magic damage.

---

### System C: Active Skill TP Scaling & "Trap Skill Level" Fix
* **Community Friction:** Active skills scale TP costs steeply while scaling damage output linearly. Leveling an active skill from Lv 1 to Lv 10 cuts its damage-per-TP efficiency by up to 71%, causing veteran guides to advise leaving skills at Lv 1–3.
* **Ground-Truth Baseline vs. Initial Drafts:**

| Skill | Class | Real Vanilla Baseline (`vanilla_source_of_truth.xlsx`) | Flawed Baseline in Earlier Drafts | Proposed Parameter (Recalculated) |
|---|---|---|---|---|
| **Halving Slice** | SA | **`80 -> 110% ATK, 10 -> 20% Death, TP 38 -> 74`** | `115 -> 175% ATK, 10-25% Death` | `100 -> 145% ATK, TP 28 -> 50` |
| **Armor Penetration** | SA / DL | **`84 -> 120% ATK, DEF -16 -> -25%, TP 14 -> 32`** | `120 -> 180% ATK, DEF -15 -> -30%` | `100 -> 150% ATK, TP 12 -> 26` |
| **Shield Bash** | PL / VL | **`85 -> 102% ATK, 30 -> 38% Stun, TP 6 -> 14`** | `110 -> 150% ATK, 20 -> 40% Stun` | `95 -> 130% ATK, TP 5 -> 10` |
| **Berserk** | BE | **`ATK +20 -> +50%, DEF -11 -> -25%, TP 8 -> 16`** | `ATK +25 -> +65%, DEF -15 -> -35%` | `ATK +25 -> +65%, TP 6 -> 14` |
| **Tinker Squash** | PA | **`Delay pushback 25 -> 43%, TP 12 -> 40`** | `Delay pushback 10 -> 35%` (Mislabeled "Slash") | `Delay pushback 25 -> 43%, TP 10 -> 30` |
| **Raging Smash** | FI / BE | `125 -> 200% ATK, TP 5 -> 28` | `125 -> 200% ATK, TP 5 -> 28` | `130 -> 225% ATK, TP 4 -> 18` |
| **Fireball** | MU / WI | `70 -> 520 Power, TP 5 -> 32` | `70 -> 520 Power, TP 5 -> 32` | `80 -> 580 Power, TP 4 -> 18` |
| **Eagle Arrow** | AR / SN | `2 hits, 75 -> 115%/hit, TP 8 -> 26` | Mislabeled as "Falcon Arrow" | `2 hits, 85 -> 135%/hit, TP 6 -> 21` |
| **Trump Card** | JO | `Colossal burst, self DEF -50%, TP 25 -> 48` | `Colossal burst, self DEF -50%` | `Colossal burst, self DEF -25%, TP 18 -> 35` |

* **Status:** **Group 2 (Feasible via PCK Structs).** TP cost integer arrays (offset `0x5c..0x80`) and power float arrays (offset `0x130..0x154`) exist in `TechniqueSkillData.pck` and `MagicSkillData.pck`.

---

### System D: Tank Parity & Frontline Balance
* **Community Friction:** Valkyrie dominates defensive slots through *Circle Protection* (full-party damage immunity), *Cover*, *Parry*, and *Holy Shield*. Paladins and Dark Lords lack party-wide wipe prevention.
* **Exact Parameters:**
  * **Paladin DEF Scaling:** Base DEF growth in `ClassLevelData.pck` proposed to increase from `1.35x` to **`1.55x`**. *(Group 3: Probably feasible in PCK).*
  * **Paladin Cover Interception:** Per-level effect scaling parameter exists in binary (`0.7 -> 0.4` across levels). *(Group 2: Feasible via PCK Structs).*
  * **Paladin Holy Shield:** Proc rate in `PassiveSkillData.pck` (`30%` vanilla, proposed `35% ~ 45%`). *(Group 2: Feasible via PCK Structs).*
  * **Dark Lord Attract / Dark Aura:** Recovery delay floats compressed from Rank E (`2.60x`) to Rank B (`1.50x`). Aggro baseline: 150 (Attract), 250 (Provoke). *(Group 2: Feasible via PCK Structs).*
  * **Universal Defend Command Immunity & Covered Chant:** Proposed 100% crit/interrupt immunity for Defend. *(Group 4: No Data Parameter Found; `StringData.pck` only holds display strings).*

---

### System E: Soul Summoner Doll Durability
* **Community Friction:** Dolls possess low static HP (~700 at Lv 99) and 0 elemental resistance, often falling to turn 1 boss AoE sweeps.
* **Exact Parameters:**
  * **Doll Per-Level Parameters:** Minion summon skills in `TechniqueSkillData.pck` contain per-level parameters governing duration and stat factors. *(Group 3: Probably feasible in PCK).*
  * **Proposed HP/RES Scaling:** Proposed formula $\text{Doll HP} = \text{Base} + 0.60 \times \text{Summoner Max HP}$ and 50 All Elemental Resistances.
  * **Double Puppet Guts (1 HP Survival):** Proposed 1 HP lethal damage survival trait. *(Group 4: No Data Parameter Found; minion entities lack passive trait slots).*

---

### System F: Progression Pacing, EXP Curve, SP Economy & Quest Ranks
* **Community Friction:** Resetting from Lv 99 to Lv 1 requires 37.6 million cumulative EXP. Bag storage begins at 30 slots, creating frequent inventory bottlenecks.
* **Exact Parameters:**
  * **EXP Curve (`LvExpSkptData.pck`):**
    * Lv 1–9: Identical to vanilla.
    * Lv 11–30: -20% EXP requirement.
    * Lv 31–70: -25% EXP requirement.
    * Lv 71–99: Cumulative requirement reduced from 2,050,065 to **1,317,866 EXP (-35.7%)**.
    * Total cumulative EXP to Lv 99: Reduced from ~37.6M to ~27.2M EXP (-27.7% overall grind reduction).
    * Preserves vanilla tier jumps at Lv 30->31, 40->41, 50->51, 80->81, 84->85, 90->91, 94->95.
  * **Negative NEXT EXP Behavior:** Loading a vanilla save file into a reduced EXP curve can temporarily show a negative `NEXT` EXP (e.g., Lv 20 character showing `NEXT: -1,577`), which clears after winning one battle.
  * **SP Bonus (`LvExpSkptData.pck`):**
    * Lv 2–14: 2 SP/level (vanilla: 1 SP).
    * Lv 15–26: 3 SP/level (vanilla: 2 SP).
    * Yields +25 total bonus SP across character progression.
  * **Level Reset Milestone Stat Formula:**
    * $\text{Level Gap} = \text{Current Level} - \text{Reset Target Level}$.
    * Gap $\ge 59$: $+1$ to all base attributes.
    * Gap $\ge 69$: $+2$ to all base attributes.
    * Gap $\ge 79$: $+3$ to all base attributes.
    * Gap $\ge 89$: $+4$ to all base attributes.
    * Gap $\ge 98$ (Lv 99 Reset to Lv 1 yields gap 98, the engine maximum): $+5$ to all base attributes + Crown Milestone.
  * **The Matrix Level 70 -> 99 Benchmark & Dragon Papi:**
    * `Slave's Torc` provides native Double EXP (Enchant ID 275, `x2.0`).
    * `Grand Sealbook [Dragon Papi]` carries Enchant 270: **+15% EXP against higher-level enemies** (Atwiki JP ground truth, not +50%).
    * Combined multiplier with Torc + Papi is **x2.30**, resulting in ~74.6 to ~85.8 minutes for Lv 70->99 in The Matrix.
  * **Quest Rank Bag & Gold Milestones (`QuestRankData.pck`):**
    * Rank 2: +10 slots -> **40 slots**.
    * Rank 8: +10 slots -> **50 slots** (engine maximum).
    * Rank 11: 50,000 Gold bounty.
    * Rank 15: 100,000 Gold bounty.
    * Rank 20: 500,000 Gold bounty.
* **Status:** **Group 1 (Verified in Data).** Binary records in `LvExpSkptData.pck` and `QuestRankData.pck` are verified. Automatic level-gap catch-up scaling falls into **Group 4 (No Data Parameter Found)**.

---

### System G: In-Game Script Modifications & Dialogue Refinements
During mod development, script dialogues across 6 `.adv.bin` archives were updated to communicate mechanics. Key technical resolutions include:
* **Trailing Quote String Matching:** Spoken dialogue lines ending in `"` failed to match string-replacement patterns that looked for a trailing null byte (`\x00`), causing 11 lines to be skipped in earlier builds. Resolved by matching the exact quote-terminated string.
* **Rin-Rin Mart Prices (`ShopStore.pck`):** Dialogue was corrected to cite store buy prices (Magical Fruit 300 G, Fairy Apple 900 G) rather than their sell prices (100 G / 300 G).
* **Persona & In-Universe Integrity:**
  * Preserved Fried and Euthys's save joke in lecture `BattleTeacher_Sp01` (*"Abandon hope and make peace with your fate"*).
  * Corrected Crown requirements in `BattleTeacher_Sp03` (clarifying that a gap of 59 grants +1 stats, while a Crown requires resetting from Lv 99 to Lv 1).
  * Maintained Blacksmith's formal tone and Mary Conductor's dialogue constraints (max 3 lines / ~62 characters per box).
  * Removed developer patch jargon ("capped at", "telemetry", "DPS") in favor of in-universe phrasing.

---

### System H: Items, Consumables & Exploration Tools (`ItemData.pck`)
* **TP Consumables:**
  * *Magical Fruit* (`ItemData_0019.bin`): Restores **50 TP** (vanilla: 25 TP). Buy: 300 G, Sell: 100 G.
  * *Fairy Apple* (`ItemData_0020.bin`): Restores **100 TP** (vanilla: 50 TP). Buy: 900 G, Sell: 300 G.
  * *Golden Apple* (`ItemData_0021.bin`): Vanilla binary is 100 TP. Setting float at `0x28` to **`999.0`** provides true Full TP recovery (matching vanilla `Mermaid Meat` behavior).
* **Revival Consumables:**
  * *Mui Kuha Medicine* (`ItemData_0026.bin`): Restores **30% Max HP** (vanilla: 10% Max HP).
  * *Peggy's Revivifying Tonic* (`ItemData_0052.bin`): Float is `1.0` (**1% HP revive** in engine and Japanese wiki).
  * *Mandragora Root*: Restores **60% Max HP** (vanilla: 1 HP / 20%).
* **Exploration Tools:**
  * *Flashlight* (`ItemData_0029.bin`): Binary float is `10.0`. In-engine step mechanics use a factor-of-5 multiplier (**vanilla 10.0 = 50 steps**). Setting float to 30.0 yields **150 steps**.
* **Buffet Meals (`FoodMenuData.pck`):**
  * Proposed 900-step duration and Dispel immunity fall into **Group 4 (No Data Parameter Found)**; `FoodMenuData.pck` contains meal costs and buff IDs, but step duration is not stored in parameter tables.
* **Status:** Float edits for Magical Fruit, Fairy Apple, Mui Kuha, and Flashlight are **Group 1 (Verified in Data)**. Golden Apple 999.0 is **Group 2 (Feasible via PCK Structs)**. Buffet step/dispel mechanics are **Group 4**.

---

### System I: Equipment, Enchantments & Forging (`EquipmentData.pck`, `EnchantData.pck`)
* **Blacksmith Forging & Affixes:**
  * Percentage forging (+3% weapon ATK / +2% armor DEF per rank) and duplicate affix penalties are engine formulas, falling into **Group 4 (No Data Parameter Found)**.
  * Guaranteed 3–4 open enchant slots on endgame gear are **Group 2 (Feasible via PCK Structs)**.
* **Enchantment Flag 157:** Internal behavior category flag shared across several enchantments; does not encode raw magnitude.
* **Equipment UI Display Standard:**
  * The game engine renders enchantments on lines 2 and 3 of the equipment text box. Adding detailed stat specs on lines 2 and 3 causes visual overdraw.
  * The approved QoL standard preserves **100% of vanilla flavor text on Line 1 with lines 2 and 3 empty**, completely preventing overdraw.

---

### System J: Anti-Cheese & Boss Mechanics
* **Tinker Squash Diminishing Returns:** Proposed diminishing returns on boss turn pushback (`100% -> 50% -> 25% -> immunity`).
* **Boss Enrage Charge:** Proposed 1-turn telegraphed charge at < 25% HP.
* **Status:** **Group 4 (No Data Parameter Found).** No stateful counters or charge flags exist in data tables.

---

### System K: Dungeon Hazards & Traps (`TrapData.pck`)
* **Trap Values:**
  * *Damage Floor / Mine*: Stored float is `0.5` (50% HP damage); proposed reduction to `0.25` (25% HP).
  * *Killer Floor*: Stored float is `0.5` (50% instant death check); proposed reduction to `0.25` (25%).
  * Elemental gas trap affinities: Poison = Water, Sleep = Wind, Paralysis = Lightning.
* **Status:** Modifying rate floats in 32-byte records of `TrapData.pck` is **Group 2 (Feasible via PCK Structs)**. Dispel floor single-target scope change is **Group 4 (No Data Parameter Found)**.

---

## 4. Master Technical Feasibility Matrix

| Subsystem | Target File | Proposed Change | Implementation Status | Technical Feasibility Classification |
|---|---|---|---|---|
| **Weapon Delays (Rank D-F)** | `WeaponRankData.pck` | A+ 1.00x to F 2.35x (vs 2.90x) | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **EXP Curve (Lv 11-99)** | `LvExpSkptData.pck` | -20% to -35.7% required EXP | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Early SP Bonus (Lv 2-26)** | `LvExpSkptData.pck` | +1 SP per level (+25 total SP) | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Bag Storage Upgrades** | `QuestRankData.pck` | Rank 2 = 40, Rank 8 = 50 slots | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Guild Gold Bounties** | `QuestRankData.pck` | Ranks 11, 15, 20 = 50k, 100k, 500k G | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Slave's Torc Double EXP** | `EquipmentData_0744.bin` | Packed Enchant 275 at `0x68` | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Magical Fruit (50 TP)** | `ItemData_0019.bin` | Packed float 50.0 at `0x28` | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Fairy Apple (100 TP)** | `ItemData_0020.bin` | Packed float 100.0 at `0x28` | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Mui Kuha Revive (30% HP)** | `ItemData_0026.bin` | Packed float 30.0 at `0x28` | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Flashlight (150 Steps)** | `ItemData_0029.bin` | Packed float 30.0 (factor 5 = 150) | Tested in Binary (Branch on QoL) | **Group 1: Verified in Data** |
| **Golden Apple (Full TP)** | `ItemData_0021.bin` | Set float to 999.0 (like Mermaid Meat)| Text Only (Binary = 100) | **Group 2: Feasible via PCK Structs** |
| **Skill TP Curves** | `TechniqueSkillData.pck` / `MagicSkillData.pck` | Flattened TP costs at Lv 6-10 | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Spell Power & Chant Speed** | `MagicSkillData.pck` | Higher base power, lower chant speed | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Cover Interception Scaling**| `TechniqueSkillData.pck` | Modify per-level rate (0.7 -> 0.4) | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Dark Lord Attract Delay** | `TechniqueSkillData.pck` | Delay float compressed to 1.50x | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Trap Floor Lethality** | `TrapData.pck` | Reduced damage/death floats | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Paladin Base DEF (1.55x)** | `ClassLevelData.pck` | +15% physical DEF growth | Text Only in Mixed Build | **Group 3: Probably Feasible in PCK** |
| **Doll Base HP / Duration** | Summon Skill Structs | Scaled minion params per level | Proposed / Text Only | **Group 3: Probably Feasible in PCK** |
| **Joint Skill Costs** | `JoinSkillData.pck` | Lower Pep / % TP in header | Proposed / Text Only | **Group 3: Probably Feasible in PCK** |
| **Grand Sealbook Auras** | `SealScrollData.pck` | Reassigning enchant IDs | Text Only in Mixed Build | **Group 3: Probably Feasible in PCK** |
| **Elemental Resistance Pierce**| Master Spell Mechanic | 50 Resistance Penetration | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Global Chant Crit Interrupt**| Combat Engine Global | 33.3% reduced to 10% | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Defend Stance Immunity** | Combat Engine Global | 100% Crit & Interrupt Immunity | Text Only in UI Strings | **Group 4: No Data Parameter Found** |
| **Buffet Meal 900 Steps** | `FoodMenuData.pck` | 300 to 900 step duration | Text Only in Food Menu | **Group 4: No Data Parameter Found** |
| **Buffet Dispel Immunity** | Combat Engine Global | Food buffs survive Dispel | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Doll Guts (1 HP Survival)** | Minion Engine Global | Dolls survive 1 lethal hit | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Tinker Squash Diminishing** | Combat Engine Global | Boss delay diminishing returns | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Percentage Forging (+3%/Lv)**| Blacksmith Engine Global| Weapon ATK +3% per forge level | Proposed / Text Only | **Group 4: No Data Parameter Found** |
| **Duplicate Enchant Penalty** | Equipment Engine Global| Diminishing returns on affixes | Proposed / Text Only | **Group 4: No Data Parameter Found** |

---

## 5. Architectural Roadmap: Two Clean Variants

To maintain technical integrity and avoid misleading players, the project is structured into two clean variants:

### Variant A: Mechanics Transparency & QoL Mod (Pure Vanilla Math)
* **Design Goal:** Complete mechanical transparency with zero balance alterations.
* **Features:**
  * Exact numerical skill data displayed cleanly (Line 1 vanilla lore, Line 2 sequential values, Line 3 resource costs; max 3 lines).
  * Equipment descriptions keep **Line 1 vanilla text untouched with lines 2 and 3 blank**, preventing the equipment enchantment overdraw bug.
  * Exact recovery values, trap rates, grand seal auras, and joint skill requirements displayed.
  * In-game dialogue preserves all original humor and character tone (e.g., Fried's save joke in `Sp01`).
  * 100% precision match between UI text and underlying vanilla game binaries.

### Variant B: Definitive Balance & Transparency Mod (Targeted Rebalance)
* **Design Goal:** Implement high-impact, verified balance adjustments (Groups 1, 2, and 3) while omitting unmapped mechanics (Group 4).
* **Execution Requirements:**
  1. **Source of Truth Rule:** All modifications must be calculated directly from `vanilla_source_of_truth.xlsx` baselines.
  2. **Weapon Recovery:** Apply Group 1 compressed delay multipliers in `WeaponRankData.pck` (A+ 1.00x to F 2.35x).
  3. **Progression Smoothing:** Apply Group 1 smoothed EXP curve (-35.7% late postgame) and early SP bonuses (+25 SP) in `LvExpSkptData.pck`.
  4. **Bag & Economy Milestones:** Apply Group 1 bag upgrades (40 & 50 slots) and gold bounties in `QuestRankData.pck`.
  5. **Exploration & Recovery:** Apply Group 1 Flashlight (150 steps via factor 5) and consumable adjustments in `ItemData.pck`. Set *Golden Apple* float to `999.0` for authentic Full TP recovery.
  6. **Skill Struct Updates:** Modify the actual binary structs in `TechniqueSkillData.pck` and `MagicSkillData.pck` (not just UI strings). For Master Spells, scale base power floats directly as the viable proxy for elemental penetration.
  7. **Dialogue Patching:** Apply clean string replacement without trailing quote mismatch, reflect accurate store buy prices, and preserve in-universe character voices.
  8. **Honest Omissions:** Do not advertise or display mechanics in Group 4 (Resistance Penetration, Defend Crit Immunity, 900-step meals, Doll Guts) where no underlying data parameters exist.
