# Dungeon Travelers 2-2: Master Consolidated Balance Proposal, Community Foundations, and Technical Feasibility Audit

**Document Status:** Master Consolidated Reference  
**Scope:** Exhaustive compilation of all balance proposals, their Japanese community foundations, exact before/after numerical parameters, and a rigorous, brutally honest technical feasibility audit.  
**Language:** English  

---

## Executive Preamble & Auditor Honesty Statement

During earlier design and architecture phases, various proposals, mathematical simulations, and rebalance drafts were created across multiple documents (`BALANCE_MOD_PROPOSAL.md`, `DEFINITIVE_BALANCE_PROPOSAL.md`, `PROGRESSION_FLOW_BALANCE_ARCHITECTURE.md`, `MECHANICS_EXPANSION_PLAN.md`). Several simulation reports even discussed mechanics as if they were fully operational in the game engine.

**This document provides absolute, unvarnished honesty and transparency.** Every proposed change is cataloged here alongside its real-world implementation status. System changes fall strictly into three technical tiers:

1. **Tier 1: Implemented & Verified in Binary Data Tables (Live in PCKs)**  
   Parameters whose raw binary structs inside the game's `.pck` archives have been directly modified and tested.
2. **Tier 2: Feasible via Binary Data Tables (Previously Mocked in Text Only)**  
   Parameters that exist as editable arrays or structs in the `.pck` files (such as skill TP costs and base damage floats), but where earlier builds only changed display text or UI strings rather than altering the underlying parameter structs.
3. **Tier 3: Technically Infeasible via Data Tables Alone (Hardcoded in Engine Executable `DT2-2.exe`)**  
   Proposed mechanics (such as *Elemental Resistance Penetration*, *Defend Command Interrupt Immunity*, *Buffet Meal 900-Step Duration*, *Global Chant Interrupt Rate Shift*, and *Summon Doll Guts Traits*) that **do not exist as configurable fields in any parameter archive**. These calculations are hardcoded directly into the compiled machine code of the executable engine and cannot be modified without binary executable reverse engineering (assembly patching).

---

## 1. Japanese Community Foundations & Grievance Mapping

Every proposed balance modification originated as an attempt to solve documented pain points from Japanese community archives (2ch/5ch strategy threads, the dedicated DT2-2 Atwiki, Amazon JP reviews, and veteran postgame clearance logs).

Below is the mapping between player grievances and the balance systems designed to address them:

```
┌─────────────────────────────────────────────────────────┐
│              COMMUNITY GRIEVANCES (ATWIKI / 2CH)        │
└───────────────────────────┬─────────────────────────────┘
                            │
   ┌────────────────────────┼────────────────────────┐
   ▼                        ▼                        ▼
[Action Speed        [Postgame Magic           ["Trap Skill Level"
 Hegemony]            Collapse & 33.3%]         TP Inversion]
   │                        │                        │
   ▼                        ▼                        ▼
• Compressed Weapon   • Master Spell Chant/    • Flattened TP Curves
  Delays (Rank D-F)     Power Scaling            at Levels 6-10
• 2H Stagger/Def     • Elemental Penetration  • Preserved Damage/Proc
  Compensation          (+50 Pierce)             Scalings
   │                        │                        │
   ├────────────────────────┼────────────────────────┤
   ▼                        ▼                        ▼
[Mandatory Valkyrie  [Soul Summoner            [Endgame Crown Grind
 & Tank Lock]         Doll Fragility]           & Early Attrition]
   │                        │                        │
   ▼                        ▼                        ▼
• Paladin DEF Boost   • Doll Stat Inheritance  • Smoothed EXP Curve
• Dark Lord Attract     (60% HP/DEF/RES)         (-35% at Lv71-99)
• Universal Defend    • Double Puppet Guts     • Bag Storage Milestones
  Stance Immunity       (1 HP Survival)          (40 & 50 slots)
```

### Community Perception vs. Binary Reality
As documented in the project's verification audits, public forum discussions often combine genuine mechanical friction with anecdotal hyperbole:
* **The "TP doubles while damage only increases 25%" Complaint:**  
  * *Accurate* for certain physical techniques: e.g., *Halving Slice* almost doubles in TP (38 to 74 TP) while damage only scales from 80% to 110%.
  * *False* for elemental spells: *Fireball* scales dramatically from 175 to 520 base power between Lv 4 and Lv 10. The actual issue with spells was chant frame inflation and high boss elemental resistance, not lack of base power.
* **The "Berserk reduces DEF to 0" Complaint:**  
  * *False*: Engine binaries verify that *Berserk* reduces DEF by 11% to 25%, not 100%.
* **The "Guns cannot use any techniques" Complaint:**  
  * *Partially False*: Specific physical skills are explicitly flagged in `TechniqueSkillData.pck` as Bow/Gun compatible, though the vast majority of scout techniques remain bow-only.

---

## 2. Exhaustive Catalog of All Proposed Balance Changes

### System A: Action Economy & Weapon Speed Recovery (`WeaponRankData.pck`)

* **Community Friction:** Heavy weapons (2H Greatswords, 2H Axes, Firearms) have brutal recovery delay multipliers ($2.30\times \sim 2.90\times$, Ranks D to F) and sacrifice the off-hand shield slot. Deep-postgame bosses with 150+ AGI lap heavy weapon users 2 to 3 times, causing bruisers to be focused down before getting a second turn. This forced a mandatory Diva casting *Swift March* into every high-difficulty party.
* **Exact Numerical Parameters:**

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

* **Proposed Weapon Compensation (Theoretical):**
  * All 2H Swords and 2H Axes gain innate **+15% Physical Damage Mitigation** and **+20 Parry Rate** to offset shield loss.
  * Guns enable archery techniques and gain native **20% Armor Shred**.
* **Technical Feasibility & Implementation Status:**
  * **Compressed Delay Multipliers:** **TIER 1 (LIVE IN BINARY).** The 12 IEEE 754 floats at offset `0x10` of `WeaponRankData.pck` were directly modified and verified in the game data.
  * **2H Innate Mitigation & Stagger:** **TIER 3 (HARDCODED IN EXE).** Weapons in `EquipmentData.pck` do not have native percentage damage reduction flags without consuming enchant slots.
  * **Gun Skill Compatibility:** **TIER 2 (FEASIBLE VIA PCK, NOT DONE).** Requires modifying weapon requirement bitfields in `TechniqueSkillData.pck`. Was only proposed, never written.

---

### System B: Magic Scaling, Chant Frames & Elemental Penetration (`MagicSkillData.pck`)

* **Community Friction:** In deep postgame (*The Matrix Depths*, the Gods, EX Superbosses), bosses feature $\ge 100$ all-element resistances, halving all magic damage. Furthermore, boss multi-hit attacks trigger the engine's flat 33.3% critical interrupt check, canceling spells. Physical burst classes (*Dark Lord*, *Samurai*, *Sniper*) deal instant, un-interruptible burst that pierces defense. Pure mages (*Witch*, *Sage*) collapse into mere utility/buff dispensers.
* **Exact Numerical Parameters:**

| Spell / Mechanic | Target File | Vanilla Parameter | Proposed Balanced Parameter | Status / Reality |
|---|---|---|---|---|
| **Master Spells Chant** | `MagicSkillData_0146..162.bin` | `80 ~ 90 frames` | **`60 frames` (-25% to -33%)** | Tier 2 (PCK array edit feasible; text only in mixed build) |
| **Master Spells Power** | `MagicSkillData_0146..162.bin` | Lv 5: `1,100 ~ 1,300` | **Lv 5: `1,450 ~ 1,650` (+30%)** | Tier 2 (PCK float edit feasible; text only in mixed build) |
| **Master Spells TP** | `MagicSkillData_0146..162.bin` | `40 -> 84 TP` | **`28 -> 52 TP`** | Tier 2 (PCK int edit feasible; text only in mixed build) |
| **Elemental Resistance Pierce** | Master Spell Flag | `0 Res Pierce` | **`50 Res Pierce`** | **TIER 3 (ENGINE HARDCODED — IMPOSSIBLE IN DATA)** |
| **Global Chant Crit Interrupt** | Combat Engine Global | Flat `33.3%` per crit hit | **`10.0%` base** | **TIER 3 (ENGINE HARDCODED — IMPOSSIBLE IN DATA)** |
| **Concentrate Lv 5 Passive** | `PassiveSkillData.pck` | Spell cast speed boost | **80% Interrupt Resistance** | **TIER 3 (ENGINE HARDCODED — IMPOSSIBLE IN DATA)** |
| **Tier 2 Row Spells Chant** | `MagicSkillData.pck` | `35 -> 80 frames` | **`25 -> 52 frames`** | Tier 2 (PCK array edit feasible; text only in mixed build) |
| **Tier 3 All Spells Power** | `MagicSkillData.pck` | `80 -> 510 power` | **`120 -> 680 power` (+33%)** | Tier 2 (PCK float edit feasible; text only in mixed build) |
| **Heal HP Cap** | `MagicSkillData.pck` | `100 -> 800 HP` | **`150 -> 1,200 HP`** | Tier 2 (PCK float edit feasible; text only in mixed build) |
| **Circle Heal HP Cap** | `MagicSkillData.pck` | `80 -> 700 HP` | **`120 -> 1,050 HP`** | Tier 2 (PCK float edit feasible; text only in mixed build) |

* **Deep Dive into Elemental Resistance Penetration:**  
  * The user specifically inquired about this: *"incluso si no se puede aplicar como la penetracion"* (even if it cannot be applied like penetration).
  * **Why it cannot be applied:** In `DT2-2.exe`, the physical damage calculation checks for the `Ignore DEF` (Armor Pierce) bitflag on skills/weapons. However, the elemental magic formula calculates damage purely as `Damage * max(0, 200 - Target_Res) / 200`. There is **no variable, struct offset, or bitmask in `MagicSkillData.pck` for elemental penetration**.
  * **Workaround:** The only way to achieve equivalent damage parity in data tables without modifying the executable is to increase the raw base magic power of Master Spells (e.g., from 1,300 to ~2,000).

---

### System C: Active Skill TP Scaling & The "Trap Skill Level" Fix

* **Community Friction:** Active skills scale TP costs steeply while scaling damage output linearly. Leveling an active skill from Lv 1 to Lv 10 cuts its damage-per-TP efficiency by up to 71%. Veteran strategy guides actively instruct players to leave skills at Lv 1–3 ("Trap Levels").
* **Exact Numerical Parameters:**

| Skill | Class | Vanilla TP (Lv 1 -> 10) | Proposed TP (Lv 1 -> 10) | Vanilla Effect | Proposed Effect |
|---|---|---|---|---|---|
| **Raging Smash** | FI / BE | `5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28` | **`4 -> 5 -> 6 -> 7 -> 9 -> 11 -> 13 -> 15 -> 16 -> 18`** | 125% -> 200% ATK | **130% -> 225% ATK** |
| **Halving Slice** | SA | `38 -> 42 -> 46 -> 50 -> 54 -> 58 -> 62 -> 66 -> 70 -> 74` | **`18 -> 20 -> 22 -> 25 -> 28 -> 31 -> 34 -> 37 -> 40 -> 44`** | 115% -> 175% ATK, 10-25% Death | **130% -> 210% ATK, 15-35% Death** |
| **Fireball** | MU / WI | `5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32` | **`4 -> 5 -> 6 -> 7 -> 8 -> 10 -> 12 -> 14 -> 16 -> 18`** | 70 -> 520 Power | **80 -> 580 Power** |
| **Armor Penetration** | SA / DL | `14 -> 16 -> 18 -> 20 -> 22 -> 24 -> 26 -> 28 -> 30 -> 32` | **`10 -> 12 -> 14 -> 16 -> 18 -> 20 -> 22 -> 24 -> 26 -> 28`** | 120-180% ATK, -15-30% DEF | **130-200% ATK, -20-40% DEF** |
| **Falcon Arrow** | AR / SN | `8 -> 10 -> 12 -> 14 -> 16 -> 18 -> 20 -> 22 -> 24 -> 26` | **`6 -> 7 -> 8 -> 9 -> 11 -> 13 -> 15 -> 17 -> 19 -> 21`** | 2 hits, 75-115%/hit | **2 hits, 85-135%/hit** |
| **Tinker Slash** | PA | `12 -> 15 -> 18 -> 21 -> 24 -> 27 -> 30 -> 33 -> 36 -> 40` | **`8 -> 10 -> 12 -> 14 -> 16 -> 18 -> 20 -> 22 -> 24 -> 28`** | Delay pushback 10-35% | **Delay pushback 15-40%** |
| **Berserk** | BE | `8 -> 10 -> 12 -> 14 -> 16` (Lv 1-5) | **`6 -> 8 -> 10 -> 12 -> 14`** | ATK +25-65%, DEF -11-25% | **ATK +30-75%, DEF -10-20%** |
| **Shield Bash** | PL / VL | `6 -> 8 -> 10 -> 12 -> 14` (Lv 1-5) | **`5 -> 6 -> 7 -> 8 -> 10`** | 110-150% ATK, 20-40% Stun | **120-180% ATK, 30-60% Stun** |
| **Trump Card** | JO | `25 -> 30 -> 35 -> 40 -> 48` (Lv 1-5) | **`18 -> 22 -> 26 -> 30 -> 35`** | Heavy burst, self DEF -50% | **Heavy burst, self DEF -25%** |

* **Technical Feasibility & Implementation Status:**
  * **TIER 2 (FEASIBLE VIA PCK, PREVIOUSLY MOCKED IN TEXT ONLY).**
  * The integer arrays for TP costs (offset `0x5c..0x80`) and float arrays for damage/rates (offset `0x130..0x154`) exist in `TechniqueSkillData.pck` and `MagicSkillData.pck`.
  * **The Reality:** In the previous mixed build, `apply_mod.py` only updated `mod_desc` and `mod_lvup` string records. The actual binary integer values were **never modified**. Characters in game still consume vanilla TP and deal vanilla damage.

---

### System D: Tank Parity & Frontline Balance (Dethroning Mandatory Valkyrie)

* **Community Friction:** Valkyrie is defensively overloaded (*Circle Protection* granting total party damage immunity, *Cover*, *Parry*, *Holy Shield*). Teams without a Valkyrie struggle immensely in endgame content. Paladins and Dark Lords lack tools to protect the team from party-wide boss wipes.
* **Exact Numerical Parameters:**
  * **Paladin DEF Scaling:** Base DEF growth in `ClassLevelData.pck` increased from `1.35x` to **`1.55x`** (+15% physical damage resistance).
  * **Paladin Cover:** Intercepted physical damage mitigated by **60%** on the Paladin.
  * **Paladin Holy Shield:** Proc rate increased from `30%` to **`35% ~ 45%`** (absorbing 75% incoming damage).
  * **Dark Lord Attract & Dark Aura:** Action recovery delay compressed from Rank E (`2.60x`) to Rank B (`1.50x`), allowing DL to taunt without forfeiting 2 turn cycles.
  * **Universal Defend Command (`StringData_0199..204.bin`):** Defend provides 50% damage reduction, 0.67x delay, and **100% Critical Hit & Chant Interrupt Immunity**. Frontline allies executing Defend grant backline casters in the same column "Covered Chant" (interrupt immunity).
* **Technical Feasibility & Implementation Status:**
  * **Paladin DEF Scaling & DL Attract Delay:** **TIER 2 (FEASIBLE VIA PCK TABLES).**
  * **Paladin Cover 60% Cut & Holy Shield 45% Proc:** **TIER 3 / TIER 2 SPLIT.** *Cover* damage calculation is an engine routine (Tier 3); *Holy Shield* proc rate may exist as a float in `PassiveSkillData.pck` (Tier 2).
  * **Universal Defend Crit & Interrupt Immunity:** **TIER 3 (HARDCODED IN EXE).** `StringData.pck` only holds the UI text string. Changing the tooltip does not alter the combat engine's Defend calculation.

---

### System E: Soul Summoner Doll Durability & Mechanics (`ClassData.pck`, `EnemyAttackData.pck`)

* **Community Friction:** Dolls possess low static HP (~700 at Lv 99) and 0 elemental resistance, dying to turn 1 boss AoE before acting. The Soul Summoner is trapped in a continuous re-summoning loop.
* **Exact Numerical Parameters:**
  * **Doll Base HP:** Increased from `1.0x` (~700 HP) to **`1.8x` (~1,500 HP)**, or formula: $\text{Doll HP} = \text{Base} + 0.60 \times \text{Summoner Max HP}$.
  * **Doll Elemental Resistances:** Increased from `0` to **`50 All Elements`** (25% damage reduction).
  * **Double Puppet Passive:** Grants a **1-hit Guts survival trait** (doll survives lethal damage with 1 HP once per summon).
  * **Soul Seal Passive:** Transfers 100% of equipped monster sealbook DEF/RES to summoned dolls.
* **Technical Feasibility & Implementation Status:**
  * **TIER 3 (HARDCODED IN EXE).**
  * Doll stat calculation is an engine algorithm triggered upon casting the summon skill. `EnemyAttackData.pck` only contains attack definitions, not the dolls' base attribute growth tables. The "Guts 1 HP" trait does not exist as an engine flag for summoned minions.

---

### System F: Progression Pacing, EXP Catch-Up & Bag Storage (`LvExpSkptData.pck`, `QuestRankData.pck`)

* **Community Friction:** Grinding from Lv 1 to Lv 99 after a Crown Reset requires a staggering 37.6 million EXP. Bag storage starts at 30 slots, causing chronic inventory exhaustion and constant premature town exits.
* **Exact Numerical Parameters:**
  * **EXP Curve Requirements (`LvExpSkptData.pck`):**
    * Lv 1–9: Identical to vanilla (Preserves early story challenge).
    * Lv 11–30: **-20%** EXP required.
    * Lv 31–70: **-25%** EXP required.
    * Lv 71–99: **-35.7%** EXP required (Lv 71–99 cumulative EXP reduced from 2,050,065 to 1,317,866).
    * Total EXP to Lv 99: Reduced from ~37.6M to ~27.2M EXP (-27.7% grind reduction).
  * **Early Skill Point (SP) Distribution (`LvExpSkptData.pck`):**
    * Lv 2–14: +1 bonus SP per level (2 SP/level instead of 1).
    * Lv 15–26: +1 bonus SP per level (3 SP/level instead of 2).
    * Total +25 extra SP across leveling.
  * **Training Gear Synergy:**
    * `Slave's Torc` (`EquipmentData_0744.bin`): Native Double EXP enchant (`Enchant ID 275`) packed at offset `0x68`.
    * `Grand Sealbook [Dragon Papi]` (`SealScrollData.pck`): +50% Higher-Level Enemy EXP aura.
    * Theoretical Catch-Up EXP: +100% to +150% EXP multiplier when current level < peak level - 10.
  * **Bag Storage & Gold Milestones (`QuestRankData.pck`):**
    * Quest Rank 2: +10 bag slots -> **40 slots** (achieved in Chapter 1).
    * Quest Rank 8: +10 bag slots -> **50 slots** (engine hard cap).
    * Quest Rank 11: Replaces dead +0 bag entry with **50,000 Gold**.
    * Quest Rank 15: Replaces dead +0 bag entry with **100,000 Gold**.
    * Quest Rank 20: Replaces dead +0 bag entry with **500,000 Gold**.
* **Technical Feasibility & Implementation Status:**
  * **EXP Curve & SP Distribution:** **TIER 1 (LIVE IN BINARY).** 90 of 99 files in `LvExpSkptData.pck` packed with modified integers.
  * **Slave's Torc Double EXP:** **TIER 1 (LIVE IN BINARY).** Enchant 275 packed at offset `0x68`.
  * **Quest Rank Bag & Gold Milestones:** **TIER 1 (LIVE IN BINARY).** Binary structs packed in `QuestRankData.pck`.
  * **Level Reset Catch-Up EXP Multiplier:** **TIER 3 (HARDCODED IN EXE).** The engine does not have an automatic dynamic catch-up multiplier based on level gap.

---

### System G: Items, Consumables & Buffet Meals (`ItemData.pck`, `FoodMenuData.pck`)

* **Community Friction:** Early TP starvation before unlocking Maid skills; revived party members instantly dying on boss AoE sweeps due to 1 HP revives; food buffs expiring after only 300 steps in 600-step dungeon floors.
* **Exact Numerical Parameters:**
  * **TP Consumables (`ItemData.pck`):**
    * *Magical Fruit* (`ItemData_0019.bin`): Restores **50 TP** (up from 25 TP).
    * *Fairy Apple* (`ItemData_0020.bin`): Restores **100 TP** (up from 50 TP).
    * *Golden Apple*: Restores **100% Full TP** (up from 100 flat TP).
  * **Revival Items (`ItemData.pck`):**
    * *Mui Kuha Medicine* (`ItemData_0026.bin`): Revives with **30% Max HP** (up from 10%).
    * *Mandragora Root*: Revives with **60% Max HP** (up from 1 HP / 20%).
  * **Exploration Tools (`ItemData.pck`):**
    * *Flashlight* (`ItemData_0029.bin`): Duration extended to **30.0 steps** (up from 10.0 steps).
  * **Buffet Meals (`FoodMenuData.pck`):**
    * Step duration extended from 300 steps to **900 steps** (3x duration).
    * Dispel immunity (food buffs persist through Dispel floors / Dispel attacks).
    * Top meals: +15% All Stats, +15 Elemental Resistances, +10% Action Speed.
* **Technical Feasibility & Implementation Status:**
  * **ItemData Float Edits (Magical Fruit, Fairy Apple, Mui Kuha, Flashlight):** **TIER 1 (LIVE IN BINARY).** The float values at offset `0x28` of these 4 files were packed and verified in `ItemData.pck`.
  * **Buffet Meal 900 Steps & Dispel Immunity:** **TIER 3 (HARDCODED IN EXE).** Step duration countdown and dispel interaction are engine code routines; `FoodMenuData.pck` only holds stat IDs and gold costs.

---

### System H: Blacksmith Forging & Enchantment Scaling (`EnchantData.pck`, `EquipmentData.pck`)

* **Community Friction:** Vanilla forging (+1 to +9) grants flat +2 to +4 ATK (+25 ATK at +9), completely insignificant against 200,000 HP postgame bosses. Players stack 5x of the same enchant (e.g. 5x Speed UP) rather than building diverse setups.
* **Exact Numerical Parameters:**
  * **Percentage Forging:** Each forge level grants **+3% Base Weapon ATK** and **+2% Shield/Armor DEF**. At +9, weapons gain **+27% total base weapon power**.
  * **Enchant Slots:** Unique endgame weapons guaranteed **3 to 4 open slots**.
  * **Duplicate Enchant Diminishing Returns:** 1st = 100%, 2nd = 75%, 3rd = 50%, 4th/5th = 25%.
* **Technical Feasibility & Implementation Status:**
  * **Percentage Forging (+3%/level):** **TIER 3 (HARDCODED IN EXE).** Weapon stat increases per forge rank are calculated by engine formulas.
  * **Enchant Slots:** **TIER 2 (FEASIBLE VIA `EquipmentData.pck`).** Open slot counts exist in weapon records.
  * **Duplicate Enchant Diminishing Returns:** **TIER 3 (HARDCODED IN EXE).** Enchant stacking logic is hardcoded in engine stat summation.

---

### System I: Anti-Cheese & Boss Mechanics

* **Community Friction:** Papillon's *Tinker Squash* turn-delay pushback allows players to cheese superbosses with infinite delay locks.
* **Exact Numerical Parameters:**
  * *Tinker Squash* turn pushback on Boss entities receives diminishing returns: `100% -> 50% -> 25% -> 3 turns immunity`.
  * Superboss Enrage Charge: Telegraphed 1-turn charge when HP < 25% to allow tactical counterplay (Defend / burst).
* **Technical Feasibility & Implementation Status:**
  * **TIER 3 (HARDCODED IN EXE).** Status diminishing returns and boss AI charge states are hardcoded in engine logic.

---

### System J: Dungeon Hazards & Traps (`TrapData.pck`)

* **Community Friction:** *Killer Floor* instant death check (50% chance) and *Dispel Floor* party-wide buff wipe cause frustrating random wipes.
* **Exact Numerical Parameters:**
  * *Damage Floor / Mine*: Damage reduced from 50% to **25% current HP**.
  * *Killer Floor*: Instant death chance reduced from 50% to **25%** (or 0% if Earth Res $\ge 80 / 100$).
  * *Dispel Floor*: Scope changed from whole party to triggering ally only.
* **Technical Feasibility & Implementation Status:**
  * **Trap Damage / Instant Death Rates:** **TIER 2 (FEASIBLE VIA `TrapData.pck`).** 32-byte records contain rate floats; previously only text was updated.
  * **Dispel Scope Modification:** **TIER 3 (HARDCODED IN EXE).**

---

## 3. Master Technical Feasibility & Binary Verification Matrix

Below is the definitive verification audit across every single proposed change:

| Subsystem | Target File | Proposed Change | Implementation Status | Technical Feasibility Verdict |
|---|---|---|---|---|
| **Weapon Delays (Rank D-F)** | `WeaponRankData.pck` | A+ 1.00x to F 2.35x (vs 2.90x) | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **EXP Curve (Lv 11-99)** | `LvExpSkptData.pck` | -20% to -35.7% required EXP | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Early SP Bonus (Lv 2-26)** | `LvExpSkptData.pck` | +1 SP per level (+25 total SP) | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Bag Storage Upgrades** | `QuestRankData.pck` | Rank 2 = 40, Rank 8 = 50 slots | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Guild Gold Bounties** | `QuestRankData.pck` | Ranks 11, 15, 20 = 50k, 100k, 500k G | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Slave's Torc Double EXP** | `EquipmentData_0744.bin` | Packed Enchant 275 at `0x68` | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Magical Fruit (50 TP)** | `ItemData_0019.bin` | Packed float 50.0 at `0x28` | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Fairy Apple (100 TP)** | `ItemData_0020.bin` | Packed float 100.0 at `0x28` | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Mui Kuha Revive (30% HP)** | `ItemData_0026.bin` | Packed float 30.0 at `0x28` | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Flashlight (30 Steps)** | `ItemData_0029.bin` | Packed float 30.0 at `0x28` | **Implemented in Binary** | **TIER 1: Real & Live in Game** |
| **Skill TP Curves** | `TechniqueSkillData.pck` / `MagicSkillData.pck` | Flattened TP costs at Lv 6-10 | Text Only in Mixed Build | **TIER 2: Feasible via PCK Structs** |
| **Spell Power & Chant Frames**| `MagicSkillData.pck` | Higher base power, lower chant frames | Text Only in Mixed Build | **TIER 2: Feasible via PCK Structs** |
| **Paladin Base DEF (1.55x)** | `ClassLevelData.pck` | +15% physical DEF growth | Text Only in Mixed Build | **TIER 2: Feasible via PCK Structs** |
| **Dark Lord Attract Delay** | `TechniqueSkillData.pck` | Delay float compressed to 1.50x | Text Only in Mixed Build | **TIER 2: Feasible via PCK Structs** |
| **Trap Floor Lethality** | `TrapData.pck` | Reduced damage/death floats | Text Only in Mixed Build | **TIER 2: Feasible via PCK Structs** |
| **Elemental Resistance Pierce**| Master Spell Mechanic | 50 Resistance Penetration | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Global Chant Crit Interrupt**| Combat Engine Global | 33.3% reduced to 10% | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Defend Stance Immunity** | Combat Engine Global | 100% Crit & Interrupt Immunity | Text Only in UI Strings | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Buffet Meal 900 Steps** | `FoodMenuData.pck` | 300 to 900 step duration | Text Only in Food Menu | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Buffet Dispel Immunity** | Combat Engine Global | Food buffs survive Dispel | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Doll Guts (1 HP Survival)** | Minion Engine Global | Dolls survive 1 lethal hit | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Tinker Squash Diminishing** | Combat Engine Global | Boss delay diminishing returns | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Percentage Forging (+3%/Lv)**| Blacksmith Engine Global| Weapon ATK +3% per forge level | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |
| **Duplicate Enchant Penalty** | Equipment Engine Global| Diminishing returns on affixes | Proposed / Text Only | **TIER 3: INFEASIBLE (Hardcoded in EXE)** |

---

## 4. The Path Forward: Two Clean, Honest Variants

To ensure complete transparency and prevent player confusion, the mod project is structured around two distinct variants:

### Variant A: Mechanics Transparency & QoL Mod (Pure Vanilla Math)
* **Goal:** 100% vanilla data tables and formulas. Zero balance modifications.
* **Content:**
  * Exact numeric skill descriptions formatted according to [`SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md`](file:///c:/Users/user/Personal/Physics/DungeonTraveler2-2/mod_project/docs/SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md).
  * Equipment weapon ranges, speed ranks, delays, and slots documented transparently.
  * Item recovery amounts, food buff effects, trap formulas, grand seal auras, and joint skill requirements revealed.
  * Every single number in the UI reflects the authentic, unmodified vanilla binaries with 100% precision.

### Variant B: Definitive Balance & Transparency Mod (Targeted Rebalance)
* **Goal:** Implement the feasible, high-value balance adjustments (Tier 1 + Tier 2) while discarding impossible engine fantasies (Tier 3).
* **Included Components:**
  1. **Weapon Speed Recovery:** Keep Tier 1 compressed delay multipliers in `WeaponRankData.pck` (A+ 1.00x to F 2.35x).
  2. **Progression Smoothing:** Keep Tier 1 smoothed EXP curve (-35% late postgame) and early SP bonuses in `LvExpSkptData.pck`.
  3. **Bag Capacity & Bounties:** Keep Tier 1 bag upgrades (40 & 50 slots) and gold bounties in `QuestRankData.pck`.
  4. **Exploration Tools:** Keep Tier 1 Flashlight (30 steps) and consumable recovery in `ItemData.pck`.
  5. **Skill TP & Power Struct Tuning (Tier 2):** When implementing skill changes, modify the actual binary structs in `TechniqueSkillData.pck` and `MagicSkillData.pck` (not just display text).
  6. **Honest Omissions (Tier 3):** Remove false claims from dialogue and tooltips regarding Elemental Penetration, Defend Crit Immunity, Buffet 900 steps, and Doll Guts traits. For Master Spells, achieve endgame viability by scaling base power floats directly.
