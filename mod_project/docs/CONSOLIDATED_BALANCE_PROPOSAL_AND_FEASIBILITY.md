# Dungeon Travelers 2-2: Master Consolidated Balance Proposal, Community Foundations, and Technical Feasibility Audit

**Document Status:** Master Consolidated Reference  
**Scope:** Exhaustive compilation of all balance proposals, their Japanese community foundations, exact before/after numerical parameters, in-game script & dialogue modifications, simulation methodology audits, and a rigorous, honest technical data verification.  
**Language:** English  

---

## Executive Preamble & Auditor Honesty Statement

During earlier design and architecture phases, various proposals, mathematical simulations, and rebalance drafts were created across multiple documents (`BALANCE_MOD_PROPOSAL.md`, `DEFINITIVE_BALANCE_PROPOSAL.md`, `PROGRESSION_FLOW_BALANCE_ARCHITECTURE.md`, `MECHANICS_EXPANSION_PLAN.md`). Several simulation reports even discussed mechanics as if they were fully operational in the game.

### 1. Disclosure on Previous "Red Team" Simulations
The earlier document `RED_TEAM_COMBAT_SIMULATION_REPORT.md` concluded with the dramatic claim: *"APPROVED WITH HIGHEST MATHEMATICAL RATING. The combat ecosystem is fully balanced."*  
**Auditor Verification & Reality:** That simulation script (`exhaustive_combat_simulator.py`) was a self-fulfilling model. Out of the entire game, it only read the 12 delay floats from `WeaponRankData.pck`. Everything else—the boss having 180 AGI and 380 DEF, taking 1,200 damage, the Scout having 570 ATK with a 190% skill—was **hardcoded directly in Python by the subagent**. There are no enemy parameter tables available in the PCK files, so those combat numbers did not originate from the game. It was an artificial script approving its own hardcoded assumptions, not proof of live engine balance.

### 2. The 4-Tier Reality of Proposed Modifications
Following binary reverse engineering and systematic cross-system audits, every proposed balance change is classified strictly into four technical categories:

1. **Group 1: Implemented & Verified in Binary Data Tables (Live in Game)**  
   Parameters whose raw binary structs inside the game's `.pck` archives have been directly modified, verified, and tested in engine:
   * Compressed weapon delay multipliers in `WeaponRankData.pck` (A+ 1.00x to F 2.35x vs vanilla 2.90x).
   * Smoothed EXP curve (-35.7% late postgame) and early SP bonuses (+25 SP) in `LvExpSkptData.pck`.
   * Bag storage upgrades (40 slots at Rank 2, 50 slots at Rank 8) and gold bounties in `QuestRankData.pck`.
   * 4 Consumable item floats (`ItemData.pck`): Magical Fruit (50 TP), Fairy Apple (100 TP), Mui Kuha (30% HP), Flashlight (30 steps).
   * `Slave's Torc` training accessory with native Double EXP (enchant ID 275) packed at offset `0x68` of `EquipmentData_0744.bin`.
2. **Group 2: Feasible & Mapped in Known PCK Structs (Ready to Implement, Previously Mocked in Text Only)**  
   Parameters that exist as verified numerical fields in `.pck` tables, but where earlier builds only changed display text or UI strings rather than altering the underlying parameter structs:
   * Skill TP cost integer arrays per level in `TechniqueSkillData.pck` and `MagicSkillData.pck`.
   * Skill physical power and magic power float arrays in `TechniqueSkillData.pck` and `MagicSkillData.pck`.
   * Spell chant frame arrays in `MagicSkillData.pck`.
   * Skill recovery delay floats (*Attract*, *Dark Aura*).
   * *Tinker Squash* turn delay pushback value.
   * *Cook*, *Holy Shield*, *Concentrate* percentage effect parameters.
   * *Killer Floor* instant death rate (float in `TrapData_0011.bin`).
   * *Golden Apple* Full TP (can be set to `999.0`, exactly as the engine's vanilla `Mermaid Meat` item does!).
3. **Group 3: Probably Feasible in PCK Tables, but Structs Unconfirmed / Unmapped**  
   Parameters that likely reside in parameter archives, but whose binary struct layouts require further reverse engineering:
   * Paladin base DEF growth multiplier (1.55x) in `ClassLevelData.pck`.
   * Summon doll base HP and elemental resistances (in minion/summon data structs).
   * Joint Skill costs (Pep and % TP) in `JoinSkillData.pck` headers.
   * Grand Sealbook aura magnitudes (reassigning existing enchant IDs).
4. **Group 4: No Known Data Parameter Found (Unverified / Unknown Storage / Engine Code)**  
   Proposed mechanics where **no corresponding data field, flag, or struct has been identified in any inspected `.pck` table**:
   * *Elemental Resistance Penetration (+50 pierce):* No effect ID or modifier flag exists for magic resistance pierce; only physical Armor Penetration exists.
   * *Defend Command 100% Critical & Interrupt Immunity:* `StringData.pck` only holds the UI text string.
   * *Global Chant Critical Interrupt Rate Shift (33.3% -> 10%):* No parameter table controls this combat rule.
   * *Concentrate 80% Crit Interrupt Resistance:* No separate resistance parameter exists.
   * *Doll Guts (1 HP Survival Trait):* Minions have no passive trait slots for Guts.
   * *Buffet Meal 900-Step Duration & Dispel Immunity:* No step duration or dispel flag exists in `FoodMenuData.pck`.
   * *Tinker Squash Diminishing Returns:* No stateful resistance counter exists for boss entities.
   * *Percentage Forging (+3%/level):* Weapon stat increases per forge rank are calculated by engine formulas.
   * *Level Reset Dynamic Catch-Up EXP Multiplier:* No automatic formula scaling EXP by level gap exists.
   * *"Covered Chant" Stance:* No column-based cover-casting mechanic exists in the data.

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
  Compensation          (+50 Pierce proposal)    Scalings
   │                        │                        │
   ├────────────────────────┼────────────────────────┤
   ▼                        ▼                        ▼
[Mandatory Valkyrie  [Soul Summoner            [Endgame Crown Grind
 & Tank Lock]         Doll Fragility]           & Early Attrition]
   │                        │                        │
   ▼                        ▼                        ▼
• Paladin DEF Boost   • Doll Stat Inheritance  • Smoothed EXP Curve
• Dark Lord Attract     (60% HP/DEF/RES)         (-35.7% at Lv71-99)
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
  * **Compressed Delay Multipliers:** **GROUP 1 (LIVE IN BINARY).** The 12 IEEE 754 floats at offset `0x10` of `WeaponRankData.pck` were directly modified and verified in the game data.
  * **2H Innate Mitigation & Stagger:** **GROUP 4 (NO DATA PARAMETER FOUND).** Weapons in `EquipmentData.pck` do not have native percentage damage reduction flags identified without consuming enchant slots.
  * **Gun Skill Compatibility:** **GROUP 2 (FEASIBLE VIA PCK, NOT DONE).** Requires modifying weapon requirement bitfields in `TechniqueSkillData.pck`. Was only proposed, never written.

---

### System B: Magic Scaling, Chant Frames & Elemental Penetration (`MagicSkillData.pck`)

* **Community Friction:** In deep postgame (*The Matrix Depths*, the Gods, EX Superbosses), bosses feature $\ge 100$ all-element resistances, halving all magic damage. Furthermore, boss multi-hit attacks trigger the engine's flat 33.3% critical interrupt check, canceling spells. Physical burst classes (*Dark Lord*, *Samurai*, *Sniper*) deal instant, un-interruptible burst that pierces defense. Pure mages (*Witch*, *Sage*) collapse into mere utility/buff dispensers.
* **Exact Numerical Parameters:**

| Spell / Mechanic | Target File | Vanilla Parameter | Proposed Balanced Parameter | Status / Reality |
|---|---|---|---|---|
| **Master Spells Chant** | `MagicSkillData_0146..162.bin` | `80 ~ 90 frames` | **`60 frames` (-25% to -33%)** | Group 2 (PCK array edit feasible; text only in mixed build) |
| **Master Spells Power** | `MagicSkillData_0146..162.bin` | Lv 5: `1,100 ~ 1,300` | **Lv 5: `1,450 ~ 1,650` (+30%)** | Group 2 (PCK float edit feasible; text only in mixed build) |
| **Master Spells TP** | `MagicSkillData_0146..162.bin` | `40 -> 84 TP` | **`28 -> 52 TP`** | Group 2 (PCK int edit feasible; text only in mixed build) |
| **Elemental Resistance Pierce** | Master Spell Flag | `0 Res Pierce` | **`50 Res Pierce`** | **Group 4 (No data parameter found in PCK structs)** |
| **Global Chant Crit Interrupt** | Combat Engine Global | Flat `33.3%` per crit hit | **`10.0%` base** | **Group 4 (No data parameter found in PCK structs)** |
| **Concentrate Lv 5 Passive** | `PassiveSkillData.pck` | Spell cast speed boost | **80% Interrupt Resistance** | **Group 4 (No data parameter found in PCK structs)** |
| **Tier 2 Row Spells Chant** | `MagicSkillData.pck` | `35 -> 80 frames` | **`25 -> 52 frames`** | Group 2 (PCK array edit feasible; text only in mixed build) |
| **Tier 3 All Spells Power** | `MagicSkillData.pck` | `80 -> 510 power` | **`120 -> 680 power` (+33%)** | Group 2 (PCK float edit feasible; text only in mixed build) |
| **Heal HP Cap** | `MagicSkillData.pck` | `100 -> 800 HP` | **`150 -> 1,200 HP`** | Group 2 (PCK float edit feasible; text only in mixed build) |
| **Circle Heal HP Cap** | `MagicSkillData.pck` | `80 -> 700 HP` | **`120 -> 1,050 HP`** | Group 2 (PCK float edit feasible; text only in mixed build) |

* **Deep Dive into Elemental Resistance Penetration:**  
  * The user specifically inquired about this: *"incluso si no se puede aplicar como la penetracion"* (even if it cannot be applied like penetration).
  * **Current Status & Known Data:** In our inspection of `MagicSkillData.pck`, no field, offset, or bitmask for elemental resistance penetration has been identified. Physical techniques have known flags for armor pierce, but we have found no equivalent data field for magic penetration.
  * **Workaround:** Modifying raw base spell power (e.g., from 1,300 to ~2,000) is currently the only confirmed, working parameter to increase magical damage against high-resistance bosses.

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
  * **GROUP 2 (FEASIBLE VIA PCK, PREVIOUSLY MOCKED IN TEXT ONLY).**
  * The integer arrays for TP costs (offset `0x5c..0x80`) and float arrays for damage/rates (offset `0x130..0x154`) exist in `TechniqueSkillData.pck` and `MagicSkillData.pck`.
  * **The Reality:** In the previous mixed build, `apply_mod.py` only updated `mod_desc` and `mod_lvup` string records. The actual binary integer values were **never modified**. Characters in game still consume vanilla TP and deal vanilla damage.
  * **Discrepancy Audit:** 125 of 141 skills displayed TP costs in text that differed from the underlying binary; 37 of 39 displayed physical power numbers that differed from binary; 17 of 22 displayed magic power numbers that differed from binary.

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
  * **Paladin DEF Scaling & DL Attract Delay:** **GROUP 2 / GROUP 3 (FEASIBLE IN DATA).** DL delay is mapped in skill arrays; Paladin DEF is in `ClassLevelData.pck`.
  * **Paladin Cover 60% Cut & Holy Shield 45% Proc:** **GROUP 4 / GROUP 2 SPLIT.** *Cover* damage mitigation has no identified data field (Group 4); *Holy Shield* proc rate exists as a float in `PassiveSkillData.pck` (Group 2).
  * **Universal Defend Crit & Interrupt Immunity:** **GROUP 4 (NO DATA PARAMETER FOUND).** `StringData.pck` only holds the UI text string. No data table or configurable parameters governing Defend's mechanical rules (such as crit or interrupt immunity) have been located in the inspected parameter files.

---

### System E: Soul Summoner Doll Durability & Mechanics (`ClassData.pck`, `EnemyAttackData.pck`)

* **Community Friction:** Dolls possess low static HP (~700 at Lv 99) and 0 elemental resistance, dying to turn 1 boss AoE before acting. The Soul Summoner is trapped in a continuous re-summoning loop.
* **Exact Numerical Parameters:**
  * **Doll Base HP:** Increased from `1.0x` (~700 HP) to **`1.8x` (~1,500 HP)**, or formula: $\text{Doll HP} = \text{Base} + 0.60 \times \text{Summoner Max HP}$.
  * **Doll Elemental Resistances:** Increased from `0` to **`50 All Elements`** (25% damage reduction).
  * **Double Puppet Passive:** Grants a **1-hit Guts survival trait** (doll survives lethal damage with 1 HP once per summon).
  * **Soul Seal Passive:** Transfers 100% of equipped monster sealbook DEF/RES to summoned dolls.
* **Technical Feasibility & Implementation Status:**
  * **GROUP 4 (NO DATA PARAMETER FOUND).**
  * The summon doll base stats and traits have no located data table in the inspected archives (`EnemyAttackData.pck` only contains enemy attack moves). No "Guts" trait field or minion stat scaling table has been found in known files.

---

### System F: Progression Pacing, EXP Curve, SP Economy & Level Resets (`LvExpSkptData.pck`, `QuestRankData.pck`)

* **Community Friction:** Grinding from Lv 1 to Lv 99 after a Crown Reset requires a staggering 37.6 million EXP. Bag storage starts at 30 slots, causing chronic inventory exhaustion and constant premature town exits.
* **Exact Numerical Parameters:**
  * **EXP Curve Requirements (`LvExpSkptData.pck`):**
    * Lv 1–9: Identical to vanilla (Preserves early story challenge).
    * Cumulative EXP to Lv 50: **264,055 EXP** (Vanilla: 336,323 EXP; **78.5% of vanilla**).
    * Lv 11–30: **-20%** EXP required.
    * Lv 31–70: **-25%** EXP required.
    * Lv 71–99: Cumulative EXP **1,317,866 EXP** (Vanilla: 2,050,065 EXP; **-35.7% reduction**).
    * Total cumulative EXP to Lv 99: Reduced from ~37.6M to ~27.2M EXP (-27.7% total grind reduction).
    * *Curve Nuance:* The reduction factor per level falls smoothly from 1.00 (Lv 9) to 0.60 (Lv 99). However, the underlying curve preserves vanilla's sudden increment jumps where required EXP doubles (Lv 30->31, 40->41, 50->51, 80->81, 84->85, 90->91, 94->95).
  * **The Negative NEXT EXP Phenomenon:**
    * When loading a pre-mod save file into the modded EXP curve, characters can display a negative `NEXT` EXP on the status screen. For example, a Lv 20 character with 22,501 EXP displays `NEXT: -1,577` because the mod lowered the cumulative threshold for Lv 21 to 20,924. This resolves naturally after winning a single battle.
  * **The Unannounced +25 Skill Point (SP) Bonus (`LvExpSkptData.pck`):**
    * Lv 2–14: +1 bonus SP per level (2 SP/level instead of vanilla 1 SP).
    * Lv 15–26: +1 bonus SP per level (3 SP/level instead of vanilla 2 SP).
    * Total +25 extra SP across character progression. (Note: this was baked into `LvExpSkptData.pck` without being mentioned in earlier release notes or dialogue).
  * **The Matrix Level 70 -> 99 Benchmark Model:**
    * Mathematical benchmark: Matrix Floors 20–30, 6,400 EXP per character per battle, 50 seconds per battle.
    * Equipment synergy: `Slave's Torc` (native Double EXP enchant 275, `x2.0`) + `Grand Sealbook [Dragon Papi]` (enchant 270 +50% Higher-Level Enemy EXP, `x1.5`).
    * Combined multiplier: **x3.0 EXP**.
    * Progression comparison:
      * *Mod + Torc + Papi:* **68.6 battles (~57.2 minutes)**.
      * *Mod + Torc only:* 103.0 battles (~85.8 minutes).
      * *Mod, no gear:* 205.9 battles (~171.6 minutes).
      * *Vanilla, no gear:* 320.3 battles (~266.9 minutes).
    * *Caveats:* 6,400 EXP and 50s are baseline assumptions; Dragon Papi's bonus applies only if enemies are higher level than the character. If Matrix F20-30 enemies fall below character level, time moves toward 85.8 min.
  * **The Level Reset Permanent Stat Formula:**
    * Permanent base attribute bonuses require a level gap: $\text{Level Gap} = \text{Current Level} - \text{Reset Target Level} \ge 59$.
    * Gap $\ge 59$: $+1$ to all base attributes.
    * Gap $\ge 69$: $+2$ to all base attributes.
    * Gap $\ge 79$: $+3$ to all base attributes.
    * Gap $\ge 89$: $+4$ to all base attributes.
    * Gap $\ge 98$ (Lv 99 Reset to Lv 1 gives gap 98, NOT 99): $+5$ to all base attributes + Crown Milestone. (Earlier tutorials mistakenly wrote $\ge 99$, but the maximum possible gap in the game is 98).
  * **Bag Storage & Gold Milestones (`QuestRankData.pck`):**
    * Quest Rank 2: +10 bag slots -> **40 slots** (achieved in Chapter 1).
    * Quest Rank 8: +10 bag slots -> **50 slots** (engine hard cap).
    * Quest Rank 11: Replaces dead +0 bag entry with **50,000 Gold**.
    * Quest Rank 15: Replaces dead +0 bag entry with **100,000 Gold**.
    * Quest Rank 20: Replaces dead +0 bag entry with **500,000 Gold**.
* **Technical Feasibility & Implementation Status:**
  * **EXP Curve & SP Distribution:** **GROUP 1 (LIVE IN BINARY).** 90 of 99 files in `LvExpSkptData.pck` packed with modified integers.
  * **Slave's Torc Double EXP:** **GROUP 1 (LIVE IN BINARY).** Enchant 275 packed at offset `0x68`.
  * **Quest Rank Bag & Gold Milestones:** **GROUP 1 (LIVE IN BINARY).** Binary structs packed in `QuestRankData.pck`.
  * **Level Reset Dynamic Catch-Up Multiplier:** **GROUP 4 (NO DATA PARAMETER FOUND).** No parameter field has been found that automatically multiplies EXP based on level gap.

---

### System G: In-Game Script Modifications, NPC Dialogues & Classroom Lectures

During mod development, text modifications were injected across **6 script archives** (`.adv.bin` files) to teach players mechanics and reflect system changes. A rigorous audit revealed critical implementation flaws, voice breaks, and pricing errors:

#### 1. The Script Patching Match Bug (11 of 47 replacements failed)
* **The Cause:** The script updater (`update_teaching_script` in `apply_mod.py`) searched for the original text string followed by a NUL byte (`orig_bytes + b'\x00'`). In spoken dialogue files, the spoken line ends with a quotation mark (`"`) before the NUL byte. As a result, the pattern never matched, and **11 of 47 dialogue replacements silently failed to apply**:
  * 8 lines in `Lesson.pck` (Euthys classroom lectures).
  * 2 lines in `ShopStore.pck` (Rin-Rin Mart).
  * 1 line in `ShopBar.pck` (Tavern Patron).
* The script still falsely reported success (*"Applied 10 BattleTeacher lecture scripts"*).

#### 2. Rin-Rin Mart Pricing Blunder (`ShopStore.pck`)
* The intended dialogue lines for Rin-Rin quoted items' **sell values** rather than their store buy prices:
  * Proposed line: *"Mag-i-cal Fruit (50 TP for 100 G)"* $\to$ Store buy price is actually **300 G** (100 G is the sell price).
  * Proposed line: *"Fair-y Ap-ples (100 TP for 300 G)"* $\to$ Store buy price is actually **900 G** (300 G is the sell price).
* **Live Dialogue Desync:** Because Rin-Rin's dialogue replacement failed to apply, she still tells players that Fairy Apples *"re-cov-er 50 TP for the low price of 900 gold"* while the item in the binary was modified to restore 100 TP.

#### 3. Character Voice & Persona Integrity Issues
* **Euthys (`Lesson.pck`):**
  * `BattleTeacher_Sp01`: **Broke Fried's famous save joke.** Original: Fried asks what to do against attacks that exceed his max HP; Euthys answers: *"Abandon hope and make peace with your fate."* Fried: *"Seriously?!"* Euthys: *"Well... it's for times like these that you should be saving frequently."* The mod replaced Euthys's line with dry tactical advice, making the subsequent voiced lines completely nonsensical.
  * `BattleTeacher_Sp03`: **Wrong Crown information.** The injected text claimed that resetting with a 59+ level gap awards a Crown. In reality, a 59 gap only awards +1 to base stats; achieving a Crown requires a Level 99 reset back to Lv 1.
* **Wandering Blacksmith (`ShopBlacksmith.pck`):**
  * Vanilla blacksmith speaks in a polite, formal tone (*"I'm afraid I must politely decline your request"*, *"I advise you plan well..."*). Injected mod lines used informal slang (*"'em"*, *"you'll blow my workshop sky-high"*), clashing with neighbouring dialogue.
* **Mary Conductor (`ShopQuest.pck`):**
  * `Talk_Random08` exceeded the engine UI budget by using 4 lines and a 66-character line (original UI boxes never exceed 3 lines / 62 characters).
* **Library Guide (`Teaching.pck`):**
  * Injected developer jargon into in-universe lore: *"heavy delay capped at 2.35x"*, *"hidden combat telemetry"*, *"Covered Chant procs"*, *"sweet spots"*, *"sustainable loops"*, *"DPS"*.
  * Duplicate numbering in `Teaching_21` caused the rule explaining that mercenaries leave after contract expiration to be lost.

---

### System H: Items, Consumables & The Golden Apple Discovery (`ItemData.pck`)

* **Community Friction:** Early TP starvation before unlocking Maid skills; revived party members instantly dying on boss AoE sweeps due to 1 HP revives; food buffs expiring after only 300 steps in 600-step dungeon floors.
* **Exact Numerical Parameters:**
  * **TP Consumables (`ItemData.pck`):**
    * *Magical Fruit* (`ItemData_0019.bin`): Restores **50 TP** (up from 25 TP). Float at `0x28` set to `50.0`.
    * *Fairy Apple* (`ItemData_0020.bin`): Restores **100 TP** (up from 50 TP). Float at `0x28` set to `100.0`.
    * *Golden Apple*: Binary value is 100 TP (unchanged). Text claimed "(Full TP)", but Golden Apple now restores the exact same 100 TP as Fairy Apple.
    * *The Golden Apple Implementation Discovery:* The vanilla engine item `Mermaid Meat` already uses float value **`999.0`** to trigger full recovery! To make Golden Apple restore Full TP in reality, its float at `0x28` simply needs to be set to `999.0` instead of `100.0`.
  * **Revival Items (`ItemData.pck`):**
    * *Mui Kuha Medicine* (`ItemData_0026.bin`): Revives with **30% Max HP** (up from 10%). Float at `0x28` set to `30.0`.
    * *Peggy's Revivifying Tonic*: Float at `0x28` is `1.0` and says "Revive 100% HP". (Demonstrates that float interpretation across item types was inconsistent).
    * *Mandragora Root*: Revives with **60% Max HP** (up from 1 HP / 20%).
  * **Exploration Tools (`ItemData.pck`):**
    * *Flashlight* (`ItemData_0029.bin`): Duration extended to **30.0 steps** (up from 10.0 steps). Float at `0x28` set to `30.0`.
  * **Buffet Meals (`FoodMenuData.pck`):**
    * Step duration extended from 300 steps to **900 steps** (3x duration).
    * Dispel immunity (food buffs persist through Dispel floors / Dispel attacks).
    * Top meals: +15% All Stats, +15 Elemental Resistances, +10% Action Speed.
* **Technical Feasibility & Implementation Status:**
  * **ItemData Float Edits (Magical Fruit, Fairy Apple, Mui Kuha, Flashlight):** **GROUP 1 (LIVE IN BINARY).** The float values at offset `0x28` of these 4 files were packed and verified in `ItemData.pck`.
  * **Golden Apple 999.0 Full Recovery:** **GROUP 2 (CONFIRMED FEASIBLE VIA PCK).**
  * **Buffet Meal 900 Steps & Dispel Immunity:** **GROUP 4 (NO DATA PARAMETER FOUND).** `FoodMenuData.pck` contains meal costs and stat boost IDs, but no field controlling step duration (vanilla 300 steps) or dispel interaction has been found in the parameter tables.

---

### System I: Blacksmith Forging, Enchantment Scaling & Equipment Display (`EnchantData.pck`, `EquipmentData.pck`)

* **Community Friction:** Vanilla forging (+1 to +9) grants flat +2 to +4 ATK (+25 ATK at +9), completely insignificant against 200,000 HP postgame bosses. Players stack 5x of the same enchant (e.g. 5x Speed UP) rather than building diverse setups.
* **Exact Numerical Parameters:**
  * **Percentage Forging:** Each forge level grants **+3% Base Weapon ATK** and **+2% Shield/Armor DEF**. At +9, weapons gain **+27% total base weapon power**.
  * **Enchant Slots:** Unique endgame weapons guaranteed **3 to 4 open slots**.
  * **Duplicate Enchant Diminishing Returns:** 1st = 100%, 2nd = 75%, 3rd = 50%, 4th/5th = 25%.
* **The Enchant ID 157 Mystery ("Max HP UP +10%"):**
  * An investigation was performed regarding where the "+10" value originated on *Max HP UP* enchants.
  * **Sourced from Japanese DT2-2 Atwiki (Page 32):** In `EnchantData_0000.bin`, the entry points to Enchant ID 157. In the engine, ID 157 is an internal effect ID that awards +10% base Max HP with a minimum guarantee of +4 HP. It is stored as an effect ID rather than an arbitrary raw float in the binary table.
* **The In-Game Equipment Text Overdraw Bug:**
  * **Visual Clutter:** On the equipment inspection screen, the game engine natively draws the item's enchantments on lines 2 and 3 of the text box. When the mod added detailed spec sheets to all 551 equipment descriptions, the engine drew the enchantment text directly over lines 2 and 3 of the description, causing unreadable visual overdraw (`Fire Magic +15%` printed over `[Weapon | Range: Short | Delay: E+ (2.05x) | Slots: 0]`).
  * **Slot Calculation Flaw:** The `Slots: N` label was populated from a field that equals the number of innate enchants, so items with 2 enchants showed `Slots: 0`.
  * **Omitted Enchant ID 0:** 86 equipment descriptions omitted enchant ID 0 ("Max HP +10%").
* **Technical Feasibility & Implementation Status:**
  * **Percentage Forging (+3%/level):** **GROUP 4 (NO DATA PARAMETER FOUND).** No data table defining forge stat scaling per level (+3% vs flat) has been located in the parameter archives.
  * **Enchant Slots:** **GROUP 2 (FEASIBLE VIA `EquipmentData.pck`).** Open slot counts exist in weapon records.
  * **Duplicate Enchant Diminishing Returns:** **GROUP 4 (NO DATA PARAMETER FOUND).** No parameter table or diminishing returns fields have been located in the parameter archives.

---

### System J: Anti-Cheese & Boss Mechanics

* **Community Friction:** Papillon's *Tinker Squash* turn-delay pushback allows players to cheese superbosses with infinite delay locks.
* **Exact Numerical Parameters:**
  * *Tinker Squash* turn pushback on Boss entities receives diminishing returns: `100% -> 50% -> 25% -> 3 turns immunity`.
  * Superboss Enrage Charge: Telegraphed 1-turn charge when HP < 25% to allow tactical counterplay (Defend / burst).
* **Technical Feasibility & Implementation Status:**
  * **GROUP 4 (NO DATA PARAMETER FOUND).** No parameter tables or data fields for status diminishing returns or boss telegraphed charge states have been found in existing files.

---

### System K: Dungeon Hazards, Traps & Display Bugs (`TrapData.pck`)

* **Community Friction:** *Killer Floor* instant death check (50% chance) and *Dispel Floor* party-wide buff wipe cause frustrating random wipes.
* **Exact Numerical Parameters:**
  * *Damage Floor / Mine*: Damage reduced from 50% to **25% current HP**.
  * *Killer Floor*: Instant death chance reduced from 50% to **25%** (or 0% if Earth Res $\ge 80 / 100$).
  * *Dispel Floor*: Scope changed from whole party to triggering ally only.
* **Trap Data Discrepancies & Flaws:**
  * **The 25% vs 50% Contradiction:** Labels in `TrapData.pck` and `Teaching_20` stated "Killer Floor (25% KO)", but the underlying binary float was still `0.5` (50% instant death check).
  * **Elemental Affinity Inversions:** Injected labels assigned incorrect resistances: Poison Gas was labeled "Earth Res" (Poison is Water element in DT2-2), Sleep Gas was labeled "Water Res" (Sleep is Wind element in DT2-2), and Paralysis Gas was labeled "Thunder" (engine terminology is Lightning).
  * **String Insertion Bug:** The trap label is dynamically inserted into the combat log: `"You triggered a %name trap!"`. Injecting verbose labels produced awkward game text: `"You triggered a Killer Floor (25% KO / Earth Res) trap!"`.
* **Technical Feasibility & Implementation Status:**
  * **Trap Damage / Instant Death Rates:** **GROUP 2 (FEASIBLE VIA `TrapData.pck`).** 32-byte records contain rate floats; previously only text was updated.
  * **Dispel Scope Modification:** **GROUP 4 (NO DATA PARAMETER FOUND).** No parameter controlling dispel targeting scope has been identified in `TrapData.pck`.

---

## 3. Binary Tooling & Data Table Flaws Uncovered

During the independent verification audits across `mod_project`, several technical issues with archive rebuilding, data parsing, and string offsets were uncovered:

1. **Lost Skill Battle Execution Messages (17 Skills):**  
   In `apply_mod.py`, each technique, spell, and passive entry in binary has four string pointers. The initial writer in `SkillHelper` only wrote three strings and left the fourth pointer pointing past the end of the entry record. As a result, 17 skills lost their in-battle execution messages:
   * *Power Charge*, *Fascinating Waltz*, *Alluring Samba*
   * Minion summons: *Spartan*, *Catalina*, *Perdurabo*, *Musiy*
   * *Arcane Shield*
   * Passives: *Avenger*, *Guts*, *Auto-Guard*, *Pretend*, *Esarhaddon*, *Ecstasy*, *Recycle*, *Magnificent Steps*, *Elegant Dancing*.  
   *(Resolved in `pck_handler.py`).*
2. **Archive Tail Truncation Bug:**  
   Rebuilt `.pck` archives produced by early helper scripts were 8 to 16 bytes shorter than vanilla originals in 22 of 36 cases due to padding alignment oversights. *(Resolved in `pck_handler.py`).*
3. **Enemy Attack Table Text Corruption (2,150 Attacks):**  
   In `enemy_attacks.xlsx` and `EnemyAttackData.pck`:
   * 2,150 attack entries had their original Line 2 description stripped.
   * 724 descriptions started in lowercase without a grammatical subject (`"damage (ATK 125%)."`).
   * 16 comedic `"Take Break"` enemy actions lost their humor.
   * 44 entries stated "Inflicts Slow" when the underlying effect ID was Petrification (ID 120), and 69 stated "Inflicts Charm" when the effect ID was Slow (ID 122).
4. **The User-Approved Skill Display Standard (`SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md`):**  
   To resolve text clutter and preserve game soul:
   * **Line 1:** 100% untouched vanilla localization flavor text.
   * **Line 2:** Mechanical parameters using clean sequential arrows (`10 -> 20 -> 30`) or step bounds (`10 -> 30 (+2/Lv)`). ZERO statistical average (`avg`) formulas, ZERO tildes (`~`), max 85 characters.
   * **Line 3:** Exact resource costs (`TP: 5 -> 14 | Chant: 20 -> 40f`).
   * Maximum 3 lines total.

---

## 4. Master Technical Feasibility & Binary Verification Matrix

Below is the definitive verification audit across every single proposed change:

| Subsystem | Target File | Proposed Change | Implementation Status | Technical Feasibility Verdict |
|---|---|---|---|---|
| **Weapon Delays (Rank D-F)** | `WeaponRankData.pck` | A+ 1.00x to F 2.35x (vs 2.90x) | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **EXP Curve (Lv 11-99)** | `LvExpSkptData.pck` | -20% to -35.7% required EXP | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Early SP Bonus (Lv 2-26)** | `LvExpSkptData.pck` | +1 SP per level (+25 total SP) | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Bag Storage Upgrades** | `QuestRankData.pck` | Rank 2 = 40, Rank 8 = 50 slots | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Guild Gold Bounties** | `QuestRankData.pck` | Ranks 11, 15, 20 = 50k, 100k, 500k G | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Slave's Torc Double EXP** | `EquipmentData_0744.bin` | Packed Enchant 275 at `0x68` | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Magical Fruit (50 TP)** | `ItemData_0019.bin` | Packed float 50.0 at `0x28` | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Fairy Apple (100 TP)** | `ItemData_0020.bin` | Packed float 100.0 at `0x28` | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Mui Kuha Revive (30% HP)** | `ItemData_0026.bin` | Packed float 30.0 at `0x28` | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Flashlight (30 Steps)** | `ItemData_0029.bin` | Packed float 30.0 at `0x28` | **Implemented in Binary** | **Group 1: Real & Live in Game** |
| **Golden Apple (Full TP)** | `ItemData_0021.bin` | Set float to 999.0 (like Mermaid Meat)| Text Only (Binary = 100) | **Group 2: Feasible via PCK Structs** |
| **Skill TP Curves** | `TechniqueSkillData.pck` / `MagicSkillData.pck` | Flattened TP costs at Lv 6-10 | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Spell Power & Chant Frames**| `MagicSkillData.pck` | Higher base power, lower chant frames | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Dark Lord Attract Delay** | `TechniqueSkillData.pck` | Delay float compressed to 1.50x | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Trap Floor Lethality** | `TrapData.pck` | Reduced damage/death floats | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Paladin Base DEF (1.55x)** | `ClassLevelData.pck` | +15% physical DEF growth | Text Only in Mixed Build | **Group 3: Probably Feasible in PCK** |
| **Doll Base HP / Resistances**| Summon Data Structs | 1.8x HP and 50 All Resists | Proposed / Text Only | **Group 3: Probably Feasible in PCK** |
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

## 5. The Path Forward: Two Clean, Honest Variants

To ensure complete transparency and prevent player confusion, the mod project is structured around two distinct variants:

### Variant A: Mechanics Transparency & QoL Mod (Pure Vanilla Math)
* **Goal:** 100% vanilla data tables and formulas. Zero balance modifications.
* **Content:**
  * Exact numeric skill descriptions formatted according to [`SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md`](file:///c:/Users/user/Personal/Physics/DungeonTraveler2-2/mod_project/docs/SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md).
  * Equipment weapon ranges, speed ranks, delays, and slots documented transparently without overdrawing the enchantment list (Line 1 preserved, Line 2 concise).
  * Item recovery amounts, food buff effects, trap formulas, grand seal auras, and joint skill requirements revealed.
  * Dialogue scripts preserve all original humor, jokes, and character personas (Fried's save joke in Sp01 preserved).
  * Every single number in the UI reflects the authentic, unmodified vanilla binaries with 100% precision.

### Variant B: Definitive Balance & Transparency Mod (Targeted Rebalance)
* **Goal:** Implement the feasible, high-value balance adjustments (Group 1 + Group 2 + Group 3) while omitting proposals that lack verified data parameters (Group 4).
* **Included Components:**
  1. **Weapon Speed Recovery:** Keep Group 1 compressed delay multipliers in `WeaponRankData.pck` (A+ 1.00x to F 2.35x).
  2. **Progression Smoothing:** Keep Group 1 smoothed EXP curve (-35.7% late postgame) and early SP bonuses (+25 SP) in `LvExpSkptData.pck`.
  3. **Bag Capacity & Bounties:** Keep Group 1 bag upgrades (40 & 50 slots) and gold bounties in `QuestRankData.pck`.
  4. **Exploration Tools:** Keep Group 1 Flashlight (30 steps) and consumable recovery in `ItemData.pck`.
  5. **Golden Apple Full Recovery (Group 2):** Set float at `0x28` to `999.0` (matching Mermaid Meat's full heal behavior).
  6. **Skill TP & Power Struct Tuning (Group 2):** When implementing skill changes, modify the actual binary structs in `TechniqueSkillData.pck` and `MagicSkillData.pck` (not just display text).
  7. **Script Bug Fixes:** Correct the string replacement bug in `apply_mod.py` so quotes don't prevent dialogue updates, fix Rin-Rin's buy vs sell prices, and remove developer patch-notes jargon.
  8. **Honest Omissions (Group 4):** Do not claim in tooltips or dialogues that unverified mechanics (Elemental Penetration, Defend Crit Immunity, 900-step meals, Doll Guts) are active when no supporting data parameters exist for them. For Master Spells, achieve endgame viability by scaling base power floats directly.
