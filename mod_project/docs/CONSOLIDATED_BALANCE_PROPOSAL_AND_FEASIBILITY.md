# Dungeon Travelers 2-2: Master Balance Proposal, Community Foundations, and Technical Feasibility Reference

**Document Status:** Definitive Technical & Balance Reference  
**Scope:** Consolidated compilation of all proposed balance adjustments, Japanese community origins, verified vanilla baselines from `vanilla_source_of_truth.xlsx`, dialogue script requirements, and technical binary feasibility classification.  
**Language:** English  

---

## 1. Executive Summary & Methodological Foundations

### 1.1 Source-of-Truth Mandate & `CommandData.pck`
All vanilla baseline parameters in this document are extracted directly from `vanilla_source_of_truth.xlsx` and raw binary parameter archives (`.bin` / `.pck`). 

A vital architectural discovery is **`CommandData.pck`** (containing 364 binary records, naming 317 in-game effects). `CommandData.pck` provides the engine's canonical internal names for skill commands, trap effects, and status conditions (e.g., Effect 0: `"Physical Attack"`, Effect 26: `"Weapon Attack"`, Effect 48: `"Trump Card"`, Effect 54: `"Turn Delay"`, Effect 170: `"Taunt"`, Effect 171: `"Cover"`, Effect 264: `"Magic Interruption Modifier"`). It serves as the primary tool for determining which mechanics possess editable parameter fields in `.pck` records.

Any future balance pass must programmatically generate its baseline figures from `vanilla_source_of_truth.xlsx` to avoid manual copy errors (such as previous misstatements of *Tinker Squash* or *Trump Card*).

### 1.2 Note on Theoretical Combat Simulations
Earlier combat simulation models (`exhaustive_combat_simulator.py`) evaluated theoretical turn-economy pacing using hardcoded enemy stat baselines (e.g., 180 AGI, 380 DEF), as enemy attribute tables are not stored in player parameter archives. They serve as mathematical trend indicators rather than live engine battle telemetry.

### 1.3 Technical Feasibility Classification
"Verified" indicates that the binary struct, offsets, and data types have been mapped and confirmed in the `.pck` files; it does not imply comprehensive in-game balance telemetry has been playtested. Proposed modifications are categorized into four technical classifications:

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
  * Spell chant speed multipliers in `MagicSkillData.pck` (stored as multipliers like 1.25x).
  * Skill speed multipliers (*Attract*, *Provoke*).
  * *Tinker Squash* turn delay pushback float array (25% → 43%, Effect 54 / "Turn Delay") and TP cost (10 → 32).
  * *Trump Card* DEF-to-ATK conversion bonus (60% → 150%, Effect 48 / "Trump Card") and TP cost (38 → 50).
  * *Concentrate* chant interruption reduction parameter (10% → 50% reduction in `PassiveSkillData_0281.bin`, Effect 264 / "Magic Interruption Modifier").
  * Trap damage and instant-death rate floats in `TrapData.pck`.
  * *Golden Apple* Full TP recovery (set float to `999.0`, matching vanilla `Mermaid Meat`).

* **Group 3: Probably Feasible in PCK Tables (Unconfirmed Structs / Mechanics)**  
  Parameters believed to reside in existing parameter files whose exact scaling formula or structure requires further mapping:
  * *Cover* Effect 171 per-level parameter (`0.7 -> 0.4` in `TechniqueSkillData_0019.bin`). The parameter exists, but the exact mechanic it scales (damage transfer percentage, mitigation factor, or duration) is unverified in engine code.
  * Paladin base DEF growth multiplier in `ClassLevelData.pck`.
  * Summon doll attribute scaling and duration parameters in minion skill records.
  * Joint Skill Pep and TP cost headers in `JoinSkillData.pck`.
  * Grand Sealbook aura assignments in `SealScrollData.pck`.

* **Group 4: No Known Data Parameter Found (Unverified / Unknown Storage / Engine Code)**  
  Mechanics where no corresponding parameter field, flag, or struct exists in inspected data tables:
  * *Elemental Resistance Penetration (+50 pierce):* No magic penetration flag exists in `MagicSkillData.pck`.
  * *Universal Defend Command Immunity:* Crit/interrupt immunity is not parameter-driven in `StringData.pck`.
  * *Global Chant Crit Interrupt Rule (33.3%):* Hardcoded combat rule with no parameter table (the 33.3% figure itself is a community-derived estimate).
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
 Hegemony]           Collapse & Interrupts]   TP Inversion]
   │                       │                        │
   ▼                       ▼                        ▼
• Compressed Delay   • Master Spell Chant/    • Flattened TP Curves
  Multipliers (D-F)    Power Adjustments        at Levels 6-10
• Heavy Weapon Flow  • Spell Power Scaling    • Preserved Damage/Proc
                       (Penetration proxy)      Scalings
   │                       │                        │
   ├───────────────────────┼────────────────────────┤
   ▼                       ▼                        ▼
[Mandatory Valkyrie [Soul Summoner           [Endgame Crown Grind
 & Frontline Lock]   Doll Fragility]          & Early Attrition]
   │                       │                        │
   ▼                       ▼                        ▼
• Paladin DEF Boost  • Doll Per-Level Scaling • Smoothed EXP Curve
• Attract Speed/Aggro  (Duration & Stats)       (-35.7% at Lv71-99)
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
* **Community Friction:** Heavy weapons (2H Greatswords, 2H Axes, Firearms) have high recovery delay multipliers ($2.30\times \sim 2.90\times$, Ranks D to F) and forfeit the off-hand shield slot. Endgame bosses with high AGI lap heavy weapon users multiple times, creating high mortality before a second action.
* **Proposal & Flat Speed Boost:** In addition to compressing the delay spread on heavy weapons, a **flat +4% baseline speed / recovery improvement** is applied across all delay ranks to raise the overall combat action tempo for all weapon types.
* **Exact Multipliers:**

| Delay Rank | In-Game Weapon Examples (`Equipment`) | Vanilla Multiplier | Proposed Balanced Multiplier (Includes +4% Flat Boost) | Relative Turn Recovery Gain |
|:---:|:---|:---:|:---:|:---:|
| **Rank A+** | Daggers (`Edge of Tartarus`) | `1.00x` | **`0.96x`** | **+4.0% faster** |
| **Rank A** | Daggers, Knives (`Pluto Knife`, `Assassin's Dagger`, `Shamrock`) | `1.20x` | **`1.11x`** | **+7.5% faster** |
| **Rank B+** | 1H Swords, Batons (`Phantom Menace`, `Spiritstaff Tulsa`) | `1.40x` | **`1.25x`** | **+10.7% faster** |
| **Rank B** | Spears, Flutes, Stilettos (`Heaven's Voice`, `Stunning Stiletto`) | `1.60x` | **`1.39x`** | **+13.1% faster** |
| **Rank C+** | Katanas, Spikes (`Bamboo Spike`, `Bashousen`) | `1.80x` | **`1.54x`** | **+14.4% faster** |
| **Rank C** | Staves, Whips, Hammers (`Tentacle Whip`, `Westward Staff`) | `2.00x` | **`1.68x`** | **+16.0% faster** |
| **Rank D+** | Heavy Spears, Drills, Forks (`Battle Fork`, `Dreadspear Pisear`, `Miracle Drill`) | `2.15x` | **`1.78x`** | **+17.2% faster** |
| **Rank D** | Heavy Katanas, Swords (`Samidare`, `Hacchozashi`, `Walawichani`) | `2.30x` | **`1.87x`** | **+18.7% faster** |
| **Rank E+** | Lances, Arbalests (`Heavy Lance`, `Kanesada`, `Arbalest`) | `2.45x` | **`1.97x`** | **+19.6% faster** |
| **Rank E** | Hammers, Harkens (`Kotetsu`, `Titan Hammer`, `Double Harken`) | `2.60x` | **`2.06x`** | **+20.8% faster** |
| **Rank F+** | Great Tachis, War Axes (`Taro Tachi`, `Valhalla Axe`, `Ayamur Magna`) | `2.75x` | **`2.16x`** | **+21.5% faster** |
| **Rank F** | Colossal Axes, Cleavers (`Heavy Axe`, `Asterios`, `Kuchinawa's Cleaver`) | `2.90x` | **`2.26x`** | **+22.1% faster** |

* **Status:** **Group 1 (Verified in Data).** The 12 IEEE 754 floats at offset `0x10` of `WeaponRankData.pck` are verified and functional. Theoretical passive damage reduction traits for 2H weapons fall into **Group 4 (No Data Parameter Found)**.

---

### System B: Magic Scaling, Chant Delays & Spell Tuning (`MagicSkillData.pck`, `PassiveSkillData.pck`)
* **Community Friction:** Endgame bosses feature $\ge 100$ all-element resistances, cutting magic damage by $\ge 50\%$. Multi-hit attacks frequently trigger chant interrupts. Physical burst classes (*Dark Lord*, *Samurai*, *Sniper*) deal immediate burst damage, relegating pure casters (*Witch*, *Sage*) to utility roles.
* **Proposed Balance Modifications (Subject to Combat Evaluation):**
  1. **Chant Time Reduction for All Spells:** Propose reducing spell chant multipliers across Tier 2, Tier 3, and Master Spells (shortening chant time by 25%–35%) so that spells execute earlier in the turn timeline, drastically narrowing the vulnerable window where casters can be interrupted by boss sweeps.
  2. **Reduction of Boss Elemental Resistances:** Propose lowering endgame superboss elemental resistances (scaling down the $\ge 100$ resistance wall down to ~50–70) so that exploiting elemental affinities yields authentic burst damage instead of being nullified.
  3. **Evaluation Mandate:** *All of these magic adjustments must be rigorously evaluated in playtesting to measure the exact shift in boss lethality and caster DPS, ensuring bosses retain tactical tension without forcing casters into irrelevance.*
* **Exact Parameters & Baselines:**

| Spell / Mechanic | Target File | Real Vanilla Baseline (`vanilla_source_of_truth.xlsx`) | Proposed Parameter | Technical Classification |
|---|---|---|---|---|
| Spell / Mechanic | Target File | Real Vanilla Baseline (`vanilla_source_of_truth.xlsx`) | Proposed Parameter | Technical Classification |
|---|---|---|---|---|
| **Master Spells Chant** | `MagicSkillData_0146..162.bin` | Stored as Multipliers: `0.75 -> 0.70x` (vs `1.25x` Circle Heal, `2.00x` Heal) | **-25% to -35% Multiplier** | Group 2 (Float edit feasible; stored as multipliers, not raw frames) |
| **Master Spells Power** | `MagicSkillData_0146..162.bin` | Lv 5: `1,300` | **Lv 5: `1,650` (+27%)** | Group 2 (Float edit feasible) |
| **Master Spells TP** | `MagicSkillData_0146..162.bin` | `40, 50, 60, 72, 84 TP` (5 levels) | **`28 -> 52 TP`** | Group 2 (Int array edit feasible) |
| **Tier 3 All Spells Power** | `MagicSkillData.pck` | **`300 -> 750 power`** (Inferno, etc.) | **`380 -> 850 power`** | Group 2 (Float edit feasible) |
| **Circle Heal HP Cap** | `MagicSkillData.pck` | **`80 -> 600 HP`** | **`120 -> 900 HP`** | Group 2 (Float edit feasible) |
| **Heal HP Cap** | `MagicSkillData.pck` | `100 -> 800 HP` | **`150 -> 1,200 HP`** | Group 2 (Float edit feasible) |
| **Concentrate Passive** | `PassiveSkillData_0281.bin` | **-10% to -50% Interrupt Rate** (Effect 264: `0.1 -> 0.5`) | **-20% to -70% Interrupt Rate** | **Group 2: Feasible via PCK Structs** (Already an interrupt reduction stat!) |
| **Boss Elemental Resistances**| Enemy Parameter Data | 100+ All Elements (Superbosses) | **Reduced to 50–70 (Subject to Evaluation)** | **Group 3 / 4 (Requires locating enemy stat tables)** |
| **Elemental Resistance Pierce** | Master Spell Flag | `0 Res Pierce` | **`50 Res Pierce`** | **Group 4 (No data parameter found in PCK structs)** |
| **Global Chant Crit Interrupt** | Combat Engine Global | Flat interrupt check (community estimates 33.3%) | **`10.0%` base** | **Group 4 (No data parameter found in PCK structs)** |

* **Note on Elemental Resistance Penetration:** No field, offset, or bitmask exists for magic penetration in `MagicSkillData.pck`. Directly tuning base spell power floats (e.g., from 1,300 to ~1,800–2,000) alongside chant speed reductions provides the confirmed, operational path to make casters viable.

---

### System C: Active Skill TP Scaling & "Trap Skill Level" Fix [CRITICAL META REVIEW REQUIRED]
* **Metagame Warning & Review Mandate:** **This system must be thoroughly reviewed and retuned as active skills are currently severely underperforming in the high-difficulty meta.** Because active techniques consume heavy TP and scale recovery delays while basic attacks and passive procs consume 0 TP, high-level players almost entirely abandon active skill rotations in favor of basic-attack/proc setups.
* **Community Friction:** Active skills scale TP costs steeply while scaling damage output linearly. Leveling an active skill from Lv 1 to Lv 10 cuts damage-per-TP efficiency significantly (e.g. *Tinker Squash* damage/TP ratio drops by 47% from Lv 1 to Lv 10; *Halving Slice* ratio drops by 30%), causing veteran guides to advise leaving skills at Lv 1–3.
* **Ground-Truth Baseline vs. Flawed Initial Proposals:**  
  *(Note on Damage Notation: All physical attack percentages below represent Total ATK Damage = Base 100% + Effect 26 "Weapon Attack" modifier).*

| Skill | Class | Real Vanilla Baseline (`vanilla_source_of_truth.xlsx`) | Flawed Baseline in Earlier Drafts | Proposed Parameter (Recalculated) |
|---|---|---|---|---|
| **Halving Slice** | SA | **`80 -> 110% Total ATK (-20% -> +10%), 10 -> 20% Death, TP 38 -> 74`** | `115 -> 175% ATK, 10-25% Death` | `100 -> 145% Total ATK, TP 28 -> 50` |
| **Armor Penetration** | SA / DL | **`84 -> 120% Total ATK (-16% -> +20%), DEF -16 -> -25%, TP 14 -> 32`** | `120 -> 180% ATK, DEF -15 -> -30%` | `100 -> 150% Total ATK, TP 12 -> 26` |
| **Shield Bash** | PL / VL | **`85 -> 102% Total ATK (-15% -> +2%), 30 -> 38% Stun, TP 6 -> 14`** | `110 -> 150% ATK, 20 -> 40% Stun` | `95 -> 130% Total ATK, TP 5 -> 10` |
| **Berserk** | BE | **`ATK +20 -> +50%, DEF -11 -> -25%, TP 8 -> 16`** | `ATK +25 -> +65%, DEF -15 -> -35%` | `ATK +25 -> +65%, TP 6 -> 14` |
| **Tinker Squash** | PA | **`Delay pushback 25 -> 43%, TP 10 -> 32, ATK +50% -> +156%`** | `Delay pushback 10 -> 35%, TP 12 -> 40` (Mislabeled "Slash") | `Delay pushback 25 -> 43%, TP 8 -> 26` |
| **Trump Card** | JO | **`DEF converted to ATK bonus 60 -> 150% (DEF = 0), TP 38 -> 50`** | `Colossal burst damage, self DEF -50%` | `DEF conversion 80 -> 180%, TP 28 -> 40` |
| **Raging Smash** | FI / BE | **`125 -> 200% Total ATK (+25% -> +100%), Crit +20 -> +38%, TP 5 -> 28`** | `125 -> 200% ATK, TP 5 -> 28` | `130 -> 225% Total ATK, TP 4 -> 18` |
| **Fireball** | MU / WI | `70 -> 520 Power, TP 5 -> 32` | `70 -> 520 Power, TP 5 -> 32` | `80 -> 580 Power, TP 4 -> 18` |

* **Note on Non-Existent Skills:** "Eagle Arrow" / "Falcon Arrow" does not exist in DT2-2. Bow skills in the engine are *Spiral Arrow* (Technique 43), *Freeze Shot* (45), *Paralysis Shot* (46), *Gravity Shot* (47), *Arrow Rain* (48), *Star Dust Arrow* (49), and *Divine Cannon* (50).
* **Status:** **Group 2 (Feasible via PCK Structs).** TP cost integer arrays (offset `0x5c..0x80`) and power float arrays (offset `0x130..0x154`) exist in `TechniqueSkillData.pck` and `MagicSkillData.pck`.

---

### System D: Tank Parity & Frontline Balance
* **Community Friction:** Valkyrie dominates defensive slots through *Circle Protection* (full-party damage immunity), *Cover*, *Parry*, and defense passives. Paladins and Dark Lords lack tools to prevent party wipes.
* **Exact Parameters & Data Status:**
  * **Paladin DEF Scaling:** Base DEF growth in `ClassLevelData.pck` proposed to increase from `1.35x` to **`1.55x`**. *(Group 3: Probably feasible in PCK).*
  * **Paladin Cover Parameter:** `TechniqueSkillData_0019.bin` (ID 19) contains Effect 171 per-level parameter (`0.7 -> 0.4` across skill levels). *(Group 3: Parameter exists, but exact mechanic/scaling it governs is unverified in engine code).*
  * **Paladin Defense Passives:** Real Paladin passives are `Auto-Guard` (`PassiveSkillData_0266.bin`, proc to Defend automatically) and `Imperial Guard` (`PassiveSkillData_0277.bin`, back row damage cut when front row uses a shield). `Divine Shield` (`MagicSkillData_0201.bin`) is an active Priest/Bishop magic buff, not a Paladin passive.
  * **Dark Lord Attract & Provoke:** Skills have their own speed multipliers and do not use weapon delay ranks. *Attract* (`TechniqueSkillData_0001.bin`, ID 1) has speed multiplier `1.25 -> 1.77` and generates Aggro 150 (Effect 170 / "Taunt"). *Provoke* (`TechniqueSkillData_0000.bin`, ID 0) has speed `1.50 -> 2.00` and generates Aggro 250 (Effect 170 / "Taunt"). *Dark Aura* (`PassiveSkillData_0279.bin`, Effect 262) is a passive with values 1 to 6.
  * **Universal Defend Command Immunity & Covered Chant:** Proposed 100% crit/interrupt immunity for Defend. *(Group 4: No Data Parameter Found; `StringData.pck` only holds display strings).*

---

### System E: Soul Summoner Doll Durability
* **Community Friction:** Dolls possess low static HP (community reports ~700 at Lv 99) and 0 elemental resistance, often falling to turn 1 boss AoE sweeps.
* **Exact Parameters:**
  * **Doll Per-Level Parameters:** Minion summon skills in `TechniqueSkillData.pck` contain per-level parameters governing duration and stat factors. *(Group 3: Probably feasible in PCK).*
  * **Proposed HP/RES Scaling:** Proposed formula $\text{Doll HP} = \text{Base} + 0.60 \times \text{Summoner Max HP}$ and 50 All Elemental Resistances.
  * **Double Puppet Guts (1 HP Survival):** Proposed 1 HP lethal damage survival trait. *(Group 4: No Data Parameter Found; minion entities lack passive trait slots).*

---

### System F: Progression Pacing, EXP Curve, SP Economy & Quest Ranks [HIGH PRIORITY / PRIORITARIO]
* **High-Priority Architectural Status:** **System F represents the single most impactful, verified, and rewarding pillar in the entire mod.** It directly eliminates the game's two most severe progression bottlenecks—the post-Crown 37.6 million EXP grind and early inventory exhaustion—using 100% verified Group 1 binary records.
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
  * **The Complete EXP & Leveling Gear Ecosystem:**
    * **Enchant 275 (Double EXP, `x2.0`):**
      * *Vanilla Distribution:* Exists exclusively on postgame equipment: *Lord Mashiro's Fan* (`EquipmentData_0475.bin`, Fan weapon) and *Therion's Crown* (`EquipmentData_0627.bin`, Helm).
      * *Mod Training Gear Implementation:* Packed into *Slave's Torc* (`EquipmentData_0744.bin`, Accessory) at offset `0x68`. This transforms an early-accessible accessory (which in vanilla only possessed AGI DOWN and damage reduction) into dedicated training gear for catch-up and Crown resets.
    * **Enchant 270 (Higher-Level Enemy EXP, `+15%`):**
      * *Single Monster Sealbooks:* *Sealbook [Grimoire]* (ID 308) and *Sealbook [Great-Fruit]* (ID 515).
      * *Grand Sealbook Aura:* *Grand Sealbook [Dragon Papi]* (ID 896), projecting Enchant 270 party-wide.
      * *Real Ground-Truth Multiplier:* Japanese Atwiki confirms Enchant 270 provides **+15% EXP against higher-level enemies** (not +50%). Stacking *Slave's Torc* (`x2.0`) with *Dragon Papi* yields a real combined multiplier of **`x2.30`** (~74.6 to ~85.8 minutes for Lv 70->99 in The Matrix).
    * **Active Party EXP Buff (Bard Hymn):**
      * *Experience Paean* (`MagicSkillData_0214.bin`, Effect 218): Bard active hymn that boosts party-wide EXP earned while the song remains active, scaling up with skill level.
    * **Direct Skill Point (SP) Consumables:**
      * *Magical Skill Garnish* (`ItemData_0031.bin`): Permanent consumable item granting **+3 SP**.
      * *Dazzling Skill Garnish* (`ItemData_0032.bin`): Permanent consumable item granting **+9 SP**.
    * **Engine Combat EXP Division & Solo/Duo Power-Leveling Synergy:**
      * *Engine Division Rule (`Teaching.pck`):* Total battle EXP is divided equally among surviving party members:
        $$\text{EXP per Member} = \frac{\text{Total Encounter EXP}}{\text{Surviving Party Members}}$$
      * *Catch-Up Synergy:* When a high-level carry escorts a single underleveled trainee equipped with *Slave's Torc* (`x2.0`), the trainee receives $50\%$ of the encounter EXP (instead of $20\%$ in a 5-person party). Combined with Double EXP, this concentrates **$5.0\times$ the effective progression rate** onto the trainee, allowing a reset character to catch up from Lv 1 to Lv 50 in only a few high-level encounters.
  * **Quest Rank Bag & Gold Milestones (`QuestRankData.pck`):**
    * Rank 2: +10 slots -> **40 slots**.
    * Rank 8: +10 slots -> **50 slots** (engine maximum).
    * Rank 11: 50,000 Gold bounty.
    * Rank 15: 100,000 Gold bounty.
    * Rank 20: 500,000 Gold bounty.
* **Status:** **Group 1 (Verified in Data).** Binary records in `LvExpSkptData.pck` and `QuestRankData.pck` are verified. Automatic level-gap catch-up scaling falls into **Group 4 (No Data Parameter Found)**.

---

### System G: In-Game Tutorials, Classroom Lectures & NPC Dialogue Expansion
*(Note: The active workspace currently runs 100% original vanilla scripts. The detailed expansions below represent the pedagogical roadmap designed to teach players complex hidden systems in-game while rigorously preserving character personas and humor).*

#### 1. Library In-Game Encyclopedia (`Teaching.pck` — 22 Expanded Tutorials)
The Royal Library tutorials in `Teaching.pck` serve as the game's comprehensive in-universe reference manual:
* **Weapon Delay Multipliers (`Teaching_01` & `Teaching_09`):** Teaches the exact delay recovery multipliers across all weapon ranks (Rank A+ 1.00x up to Rank F 2.90x vanilla / 2.26x modded), explaining turn lag and recovery ticks in accessible in-universe terms.
* **Dungeon Hazards & Trap Formulas (`Teaching_13` & `Teaching_20`):** Explains all 12 trap mechanisms, correctly stating 50% damage floor / mine damage, 50% killer floor instant death checks, and exact elemental affinities (Poison = Water, Sleep = Wind, Freeze = Water, Paralysis = Lightning, Silence = Wind, Petrification = Earth, Slow = Earth).
* **Combat Rules & Dual-Scaling (`Teaching_15`):** Teaches the dual nature of elemental resistance: 100 elemental resistance grants 100% immunity to associated status ailments and a 50% flat reduction to incoming elemental spell damage.
* **Chant Vulnerability & Interrupts (`Teaching_17`):** Explains that spells and hymns are subject to disruption when struck during casting, teaching tactical positioning and defensive coverage.
* **EXP Division & Power-Leveling (`Teaching_19`):** Explicitly teaches the engine rule that battle EXP is divided among surviving allies, explaining the mechanics of solo/duo power-leveling.
* **Mercenary Contract Duration (`Teaching_21`):** Teaches contract rules, hire costs, and party synergies so players understand mercenary departure timings.
* **Mutant Enrage States (`Teaching_24`):** Warns adventurers of mutant enrage triggers at low HP thresholds.

#### 2. Euthys's Classroom Lectures (`Lesson.pck` — Special Lectures & Curricula)
Classroom lectures delivered by Euthys at the Academy combine advanced tactical guidance with authentic character dynamics:
* **Superboss Wipe Survival (`BattleTeacher_Sp01`):** Teaches strategies for handling colossal attacks that exceed max HP (Cover, Defend, party buffs). **Crucial Voice & Humor Rule:** Must preserve Fried's iconic save joke intact:
  * *Fried:* "What should we do against attacks that deal more damage than our max HP?!"
  * *Euthys:* "Abandon hope and make peace with your fate."
  * *Fried:* "Seriously?!"
  * *Euthys:* "Well... it's for times like these that you should be saving frequently, Fried."
* **Crown Reset Milestones (`BattleTeacher_Sp03`):** Clarifies level reset bonuses with mathematical precision: explains that a reset gap of $\ge 59$ grants $+1$ permanent stats, while achieving a Crown requires a Level 99 reset back to Lv 1 (gap 98).
* **Core Advanced Topics:** Classroom lectures cover 2H weapon tradeoffs, weapon ranges (Short/Mid/Long), 100 resistance walls, bag storage milestones (Rank 2 and 8), Party Skill activation thresholds (+1% stat per 5 awards, +10% max at 50 trophies), and buffet meal mechanics.

#### 3. Facility Attendant Wisdom & In-Town Advice Dialogues
Town attendants offer mechanical guidance tailored to their distinct personalities:
* **Mary Conductor (`ShopQuest.pck`):** Speaks out loud only in dots (`"....................."`), with all true thoughts in parentheses `(...)`. Informs Fried of bag capacity expansions (+10 at Rank 2 = 40 slots; +10 at Rank 8 = 50 slots) and *The Matrix* postgame unlock at Rank 16 (620 Trust Points), strictly formatted within 3-line dialogue boxes.
* **Wandering Blacksmith (`ShopBlacksmith.pck`):** Maintains his formal, polite craftsman demeanor (*"I advise you plan well..."*). Explains forging limits (+9 cap) versus preserving open enchantment slots.
* **Tavern Patron (`ShopBar.pck`):** Seasoned veteran adventurer offering pragmatic combat advice over a drink regarding mercenary contract duration and frontline tank archetypes.
* **Rin-Rin Mart (`ShopStore.pck`):** Android shopkeeper speaking with characteristic syllable breaks (`wel-come`, `Flash-lights`). Dialogue accurately cites store buy prices (Magical Fruit for 300 G, Fairy Apple for 900 G) rather than misleading sell prices.

#### 4. Technical Script Implementation Requirements
* **Trailing Quotation Bug Fix:** Refactor `apply_mod.py` regex/byte search logic to match quote-terminated lines (`orig_bytes + b'"\x00'`) so that the 11 dialogue replacements that previously failed apply cleanly.
* **Strict Layout Budget:** Ensure every injected line strictly adheres to engine UI constraints: maximum 3 lines per dialogue box and maximum 62 characters per line.
* **Elimination of Patch Jargon:** Completely purge modern developer patch jargon ("capped at", "telemetry", "DPS") in favor of immersive in-universe terminology.

---

### System H: Items, Consumables & Exploration Tools (`ItemData.pck`)
* **TP Consumables:**
  * *Magical Fruit* (`ItemData_0019.bin`): Restores **50 TP** (vanilla: 25 TP). Buy: 300 G, Sell: 100 G.
  * *Fairy Apple* (`ItemData_0020.bin`): Restores **100 TP** (vanilla: 50 TP). Buy: 900 G, Sell: 300 G.
  * *Golden Apple* (`ItemData_0021.bin`): Vanilla binary is 100 TP. Setting float at `0x28` to **`999.0`** provides true Full TP recovery (matching vanilla `Mermaid Meat` behavior).
* **Revival & Cleansing Consumables:**
  * *Mui Kuha Medicine* (`ItemData_0026.bin`): Restores **30% Max HP** (vanilla: 10% Max HP, Effect Type 8: Revival, value 10.0). Buy: 1200 G, Sell: 400 G.
  * *Peggy's Revivifying Tonic* (`ItemData_0052.bin`): Stored float is `1.0` (**1% Max HP revive** in engine and Japanese wiki, Effect Type 8, value 1.0). Buy: 600 G, Sell: 200 G.
  * *Resurrection Stone* (`ItemData_0514.bin`): Restores **15% Max HP** (Effect Type 8: Revival, value 15.0; not Type 15 freeze). Buy: 5000 G, Sell: 1000 G.
  * *Mandra Root* (`ItemData_0835.bin`): Usable cleansing item (Effect Type 7: Status recovery, value 1.0) that cures all status ailments and stat debuffs. (Not an inert cooking ingredient).
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
  * Gas trap status IDs (from `Traps` and `CommandData.pck`): Status 113 (Poison), Status 114 (Freeze), Status 115 (Paralysis), Status 116 (Sleep), Status 117 (Silence), Status 120 (Petrification), Status 122 (Slow).
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
| **Concentrate Interruption Rate**| `PassiveSkillData_0281.bin`| Scale interrupt reduction (-10% to -50% vanilla)| Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Dark Lord Attract / Provoke** | `TechniqueSkillData.pck` | Speed multiplier & Aggro scaling | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Trap Floor Lethality** | `TrapData.pck` | Reduced damage/death floats | Text Only in Mixed Build | **Group 2: Feasible via PCK Structs** |
| **Cover Parameter Scaling** | `TechniqueSkillData_0019.bin`| Modify Effect 171 per-level rate (0.7 -> 0.4)| Unverified in Engine Code | **Group 3: Probably Feasible in PCK** |
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
  * Exact numerical skill data displayed cleanly (integrating damage keywords and numeric values directly, preserving/shortening original flavor text within 1–3 lines).
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
  7. **Dialogue Patching Refactor:** Refactor `apply_mod.py` string matching to support quote-terminated strings (`"`), reflect accurate store buy prices, and preserve in-universe character voices.
  8. **Honest Omissions:** Do not advertise or display mechanics in Group 4 (Resistance Penetration, Defend Crit Immunity, 900-step meals, Doll Guts) where no underlying data parameters exist.

---

## 6. Unverified High-Value Balance Proposals from Japanese Meta Analysis

The following suggestions originate directly from Japanese community discussions (2ch/5ch strategy threads, the DT2-2 Atwiki class evaluations, and veteran logs in `COMMUNITY_BALANCE_COMPLAINTS.md`). While **not yet verified in raw engine executable code** (categorized as Group 3 or Group 4), they represent compelling, logically coherent solutions to the game's most persistent balance pain points:

### 6.1 Gun Viability for Snipers (Addressing the "Dead Gun" Dilemma / 死に武器種)
* **Japanese Community Problem:** Equipping a Gun disables bow skills (*Spiral Arrow*, *Star Dust Arrow*, etc.), leaving Snipers with only basic attacks. Guns also suffer from crushing Rank F recovery delay ($2.90\times$), rendering the entire weapon category dead content.
* **Data Grounding:** In `vanilla_source_of_truth.xlsx` and `TechniqueSkillData.pck`, physical techniques feature weapon compatibility flags. Furthermore, gun items in `EquipmentData.pck` possess unique stat profiles (high DEX/Hit, innate criticals).
* **Unverified Proposal:** If executable reverse-engineering confirms the weapon compatibility bitmask for Sniper archery skills, enabling the Gun flag would unlock an entirely new ranged sniper archetype. Alternatively, within Group 2 parameters, boosting Gun innate critical rates and slot counts in `EquipmentData.pck` would provide compensation for basic-attack gun builds without requiring code hacks.

### 6.2 Whip Tree Mechanical Identity for Mistress (Addressing Subpar Range & DPS)
* **Japanese Community Problem:** The Mistress class (Maid tree) is widely regarded on 2ch/5ch as inferior to Diva and Etoile because Whips have awkward range and subpar skill multipliers compared to Daggers or Fans.
* **Data Grounding:** Whips in `EquipmentData.pck` are flagged as Middle Range weapons. Mistress whip techniques in `TechniqueSkillData.pck` feature per-level status infliction rates.
* **Unverified Proposal:** In `TechniqueSkillData.pck` (Group 2), increase the status ailment proc rates (Charm, Paralyze) and speed multipliers on Whip skills so the Mistress functions as a reliable frontline crowd-control specialist rather than a weak DPS hybrid.

### 6.3 Progressive Delay Resistance on Bosses (Resolving the Infinite Tinker Squash Stunlock)
* **Japanese Community Problem:** 2ch/5ch threads document the deep polarization over Papillon's *Tinker Squash* (empowered by Diva's *Swift March*): it can push back superboss turns indefinitely, turning the Creator God into a punching bag.
* **Data Grounding:** Enemy AI scripts and status resistance routines reside in the game executable and enemy attack parameters.
* **Unverified Proposal (Group 4):** Implement an engine-level diminishing returns counter on turn-delay pushback (`100% -> 50% -> 25% -> temporary immunity for 3 turns`). This preserves Tinker Squash as a clutch tactical tool to disrupt telegraphed boss enrage charges while eliminating degenerate infinite stunlocks.

### 6.4 Defensive Compensation Traits for 2-Handed Weapons (両手武器絶望論)
* **Japanese Community Problem:** Documented in Japanese wiki battle logs, wielding a 2H weapon (Rank E/F delay) forfeits the shield slot, DEF, and elemental resistances, leading to superbosses lapping and killing Berserkers before their next action.
* **Data Grounding:** `EnchantData.pck` contains passive enchants for Physical Damage Reduction (Enchant 66) and Parry Rate.
* **Unverified Proposal:** While universal hardcoded traits are Group 4, an elegant data-driven approach within **Group 1 / 2** is to inject innate defensive enchants (e.g., innate +10% Phys Damage Cut or +15% Parry) directly into 2H Greatswords, 2H Axes, and Polearms in `EquipmentData.pck`, compensating for the missing shield slot without touching executable code.

### 6.5 Dynamic Level-Reset Catch-Up EXP Multiplier (Lv99リセットの苦行)
* **Japanese Community Problem:** Resetting to Lv 1 to achieve Crown status requires enduring the full EXP curve again across 18 characters, described on Atwiki as an exhausting chore that discourages build experimentation.
* **Data Grounding:** The engine currently supports static EXP bonuses via equipment (Enchant 275 Double EXP) and sealbooks (Enchant 270 +15% against higher-level enemies).
* **Unverified Proposal (Group 4):** A proposed dynamic engine hook that grants `+100%` bonus EXP whenever $\text{Current Level} \le (\text{Peak Level} - 10)$. Until executable hooks can be developed, the verified solution remains the **Slave's Torc training gear (Enchant 275) + Dragon Papi synergy**, which safely achieves a $5.0\times$ catch-up rate in duo party compositions.

---

## 7. Methodological Evaluation Frameworks for Balance Tuning

To evaluate and tune proposed balance adjustments rigorously—without hallucinated mechanics, speculative stats, or spreadsheet bloat—the following prompt frameworks are established for analytical agents and human testers. Each framework is grounded strictly in game design theory, psychological flow, and verified binary parameters.

### 7.1 Adversarial Combat Simulation Framework (Turn Economy & Survival Math)
* **Design Lens:** Sid Meier's *Interesting Decisions* & Mathematical Parity.
* **Target Objective:** Stress-test whether weapon delay compression (System A) and skill TP/power adjustments (System C) create degenerate dominant strategies or trivialize difficulty.
* **Actionable Evaluation Prompt:**
  ```text
  You are an Adversarial Combat Balance Analyst for Dungeon Travelers 2-2.
  Using ONLY verified data from `vanilla_source_of_truth.xlsx` (WeaponRanks, Skills, SkillLevels):
  1. Turn Economy Ratio: Calculate the action frequency ratio over 100 combat ticks between:
     - Rank A+ (0.96x mod vs 1.00x vanilla)
     - Rank B (1.39x mod vs 1.60x vanilla)
     - Rank F (2.26x mod vs 2.90x vanilla)
  2. Survivability & Window of Vulnerability: Determine if a 2.26x recovery multiplier allows 
     a 2H weapon user to take a defensive action before a fast enemy (1.3x–1.5x speed) acts twice.
  3. Active Skill Damage-per-TP Efficiency: Calculate the exact damage/TP ratio of Lv 1 vs Lv 5 vs Lv 10 
     for Halving Slice (TP 28->50, ATK 100->145%) and Tinker Squash (TP 8->26, ATK +50->+156%).
  4. Boundary Check: Confirm that no physical technique exceeds single-target magic burst (Tier 3 / Master),
     and that basic-attack procs do not render active skills obsolete.
  Deliver a concise mathematical verdict stating whether the changes preserve challenge without frustration.
  ```

### 7.2 Game Flow & Visceral Friction Framework (Eliminating Calculator Overhead)
* **Design Lens:** Mihaly Csikszentmihalyi's *Flow* & Steve Swink's *Game Feel*.
* **Target Objective:** Ensure that mechanical transparency and balance changes streamline player decision-making during dungeon crawls rather than imposing mental arithmetic fatigue ("playing with a calculator").
* **Actionable Evaluation Prompt:**
  ```text
  You are a Game Flow & UX Systems Evaluator for Dungeon Travelers 2-2.
  Evaluate the cognitive load and tactile rhythm of combat and exploration:
  1. Combat Readability: Verify that skill descriptions convey utility at a glance (e.g., total ATK %,
     status chance, TP cost) without requiring manual math during turn selection.
  2. Attrition Rhythm: Evaluate how early TP consumables (Magical Fruit 50 TP, Fairy Apple 100 TP)
     and early SP pacing (+25 SP across Lv 2-26) affect dungeon exploration rhythm.
     Do they remove boring basic-attack slogs while preserving resource tension across floors?
  3. Inventory Friction: Evaluate the 40-slot (Rank 2) and 50-slot (Rank 8) bag upgrades. Does it 
     allow completing standard floor loops without inventory exhaustion while maintaining town return value?
  4. Flow State Verdict: Confirm whether the player stays immersed in dungeon exploration without
     hitting artificial progression walls or spreadsheet fatigue.
  ```

### 7.3 Difficulty Curve & Progression Pacing Framework
* **Design Lens:** Jesse Schell's *The Art of Game Design* & Raph Koster's *A Theory of Fun*.
* **Target Objective:** Validate that the smoothed EXP curve (-35.7% late postgame) maintains authentic hardcore DRPG tension while removing masochistic repetition.
* **Actionable Evaluation Prompt:**
  ```text
  You are a Progression Pacing & Difficulty Curve Auditor for Dungeon Travelers 2-2.
  Inspect `vanilla_source_of_truth.xlsx` ('ExpCurve' sheet) and `LvExpSkptData.pck`:
  1. Campaign Pacing (Lv 1–50): Verify that Lv 1–9 is strictly vanilla, and Lv 11–50 maintains 
     boss encounter difficulty without accidental over-leveling during standard story exploration.
  2. Late & Postgame Curve (Lv 71–99): Verify the 1,317,866 EXP threshold (-35.7% reduction).
     Confirm that cumulative requirements strictly increase monotonically with zero inversions.
  3. Catch-Up Loop: Evaluate the progression rate of a reset character (Lv 1) in a high-level party
     using Slave's Torc (Enchant 275 Double EXP) under the engine's EXP division rule.
     Does it reach mid-game viability within a healthy 15–30 minute session without breaking level progression?
  Deliver a concise verdict verifying that endgame prestige (Crown) remains an earned achievement.
  ```


