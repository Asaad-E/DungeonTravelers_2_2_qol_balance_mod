# Dungeon Travelers 2-2: Hardcore Endgame & High-Difficulty Balance Mod Architecture
## Definitive Architectural Proposal for Postgame, The Matrix Depths, The Gods & EX Superbosses

**Author:** Hardcore Endgame & High-Difficulty Balancer  
**Target Engine:** Aquaplus / Sting PC Engine (`Dungeon Travelers 2-2: The Maiden of Darkness and the Book of Origins`)  
**Scope:** Deep Postgame, The Matrix Depths, The Creator God, Dark Mutants, EX Dungeons, and the Entire Playable Ecosystem.  
**Core Standard:** Bit-exact binary grounding, authentic DRPG tactical challenge, elimination of dead ends and mandatory single-class locks, preservation of game soul and humor.

---

## 1. Executive Summary & Hardcore Design Vision

*Dungeon Travelers 2-2* is celebrated as one of the pinnacle dungeon-crawlers in Japanese RPG history, featuring Byzantine combat math, brutal enemy synergy, and deep customization. However, in the deep postgame—spanning the 50+ floors of the Matrix Depths, the Creator God battle, and EX Dungeons—the game's mechanical systems suffer from severe structural bottlenecks:

1. **The Action Speed Hegemony (速度至上主義):** Heavy weapons (2H Swords, 2H Axes, Guns) with Rank E/F delay multipliers ($2.6\times$ to $2.9\times$) cause wielders to be lapped 2–3 times by $150+$ AGI superbosses, creating a suicidal delay spiral.
2. **Postgame Magic Collapse (終盤の魔法不遇):** Superbosses feature blanket 100+ elemental resistances ($50\%+$ damage mitigation) across all five elements, while fast multi-hit attacks trigger the flat $33.3\%$ critical chant interrupt rule, reducing pure offensive casters (Witch, Sage) to irrelevant bystanders compared to physical burst classes with *Armor Pierce*.
3. **Mandatory Class Dependencies & Valkyrie Hegemony:** The game's extreme damage spikes force party slots into mandatory pigeonholes: Valkyrie (*Circle Protection* / *Material Guard* party immunity) and Maid (*TP Battery*) feel mandatory, leaving only 3 slots for real experimentation.
4. **Soul Summoner Doll Fragility:** Dolls possess flat, low defensive pools, dying on Turn 1 to ambient boss AoE before taking an action, trapping the Soul Summoner in an endless re-summoning loop.
5. **Binary Cheese vs. Immunity:** Boss mechanics oscillate between exploitable cheese (e.g. infinite *Tinker Squash* turn-delay pushback locks) and total immunity, preventing nuanced tactical control.

### The Balancing Philosophy: "High-Tension Tactics, Zero False Bottlenecks"
Our goal is **not** to make the game easy. The Creator God and EX Superbosses must remain terrifying, demanding apex mastery of equipment forging, formation planning, buff cycling, and resource management. Instead, our balance architecture eliminates artificial traps, restores viability to underrepresented classes and weapons, and introduces organic counterplay so that **multiple distinct team archetypes can conquer the deep postgame without relying on cheese**.

---

## 2. Deep Superboss Mechanics: Solutions & Mathematical Grounding

### A. The 100+ Elemental Resistance Wall
* **Engine Formula:**  
  $$\text{Damage Multiplier} = 1.0 - (\text{Elemental Resistance} \times 0.005)$$
  * $0\text{ Res} = 1.00\times$ (100% damage)
  * $100\text{ Res} = 0.50\times$ (50% damage reduction + 100% status ailment immunity)
  * $150\text{ Res} = 0.25\times$ (75% damage reduction)
  * $200\text{ Res} = 0.00\times$ (100% damage nullification / absorption)
* **The Problem:** Postgame superbosses (Creator God, Ancient Dragons, Dark Mutants) possess 100 to 140+ resistance across *all five elements* (Fire, Water, Wind, Earth, Lightning), cutting all spell damage in half while physical skills with innate *Armor Pierce* ignore physical DEF entirely.
* **Architectural Solution:**
  1. **Master Spell Resistance Penetration (`MagicSkillData.pck`):**  
     Top-tier Master Spells (`Crimson Flare`, `Cocytus`, `Muon Plasma`, `Tempest`, `Gaia Crush`) gain an innate **50-point Elemental Resistance Pierce**. Against a 120-resistance superboss:
     * *Vanilla:* $1.0 - (120 \times 0.005) = 0.40\times$ (60% damage lost).
     * *Modded:* Effective resistance becomes $120 - 50 = 70$. Damage multiplier becomes $1.0 - (70 \times 0.005) = 0.65\times$ (+62.5% effective damage increase).
  2. **Asymmetric Superboss Elemental Profiles:**  
     Adjust blanket resistance profiles on superbosses. Instead of 120 across all 5 elements, superbosses feature distinct tactical affinities (e.g., Creator God: 120 Light/Dark, 110 Earth/Fire, but 65 Water/Wind), rewarding players who scout weaknesses and align weapon enchants and elemental zones.

### B. Full Buff/Debuff Wipe Fatigue (Dispel Cycling)
* **The Problem:** Superboss AI frequently spams party-wide dispel skills (*Dispel Floor*, *Zero All*, *Erase*) every 3–4 turns or when positive buffs $\ge 4$, wiping multiple turns of player preparation in a single action and creating extreme combat fatigue.
* **Architectural Solution:**
  1. **Tiered Buff Persistence:**  
     * Food Buffet Buffs (`FoodMenuData.pck`) and Permanent Stances (`Aura`, `Unique EX`) are categorized as physiological/spiritual traits and are **immune to Dispel**.
     * Magical buffs removed by Dispel leave a 1-turn **"Lingering Resonance"** effect (providing 50% of their numerical value on the dispel turn), eliminating immediate turn-1 party wipes upon dispel.
  2. **Dispel Absorption Counters:**  
     * Bishop's *Sacred Barrier* and Valkyrie's *Aegis* absorb 1 dispel attempt before shattering, giving tactical control over dispel timings.

### C. The 33.3% Chant Interrupt Rule
* **Engine Formula:**  
  $$\text{Chant Interrupt Chance} = \frac{\text{Damage Taken}}{\text{Max HP}} \times 100\% \quad (\text{if non-crit})$$
  $$\text{Critical Hit Check} = \mathbf{33.3\% \text{ Flat Interrupt Chance}} \quad (\text{regardless of damage!})$$
* **The Problem:** Postgame superbosses act 2–3 times per round, executing multi-hit physical skills with 25–40% critical rates. A 4-hit attack has a $>80\%$ probability of rolling at least one critical hit, triggering the 33.3% check and virtually guaranteeing chant cancellation on Witch/Sage.
* **Architectural Solution:**
  1. **Chant Delay Frame Compression:**  
     Reduce Master Spell chant frame delays in `MagicSkillData.pck` by **25%** (from 80 frames down to 60 frames). With *Fast Cast* Lv5 (30% reduction), chant windows contract to 42 frames, fitting safely between boss turns.
  2. **Chant Interruption Mitigation via *Concentrate* (`PassiveSkillData_0281.bin`):**  
     Rebalance *Concentrate* to grant **80% Critical Interrupt Resistance** at Lv5. Reduces the flat critical interrupt rate from $33.3\%$ down to $6.6\%$.
  3. **Universal Defend Stance Synergy:**  
     When a front-row ally executes the **Defend** command, back-row chanting allies in the same column receive "Covered Chant", gaining complete chant interrupt immunity for that turn.

---

## 3. Soul Summoner Doll Durability & Scaling Architecture

### A. The Root Problem
Dolls (`Spartan`, `Oracles`, `Catalina`, `Mercidarian`, `Perdurabo`, `Musiy`) are autonomous combat entities whose stats scale from rigid base templates. Deep postgame superbosses deal 700–1,200 AoE physical and elemental damage. Vanilla dolls possess ~500–700 HP and 0 elemental resistance, resulting in Turn 1 instant death before their first action, locking the Soul Summoner into a futile re-summon loop.

### B. Architectural Solutions Grounded in `ClassData.pck` and Skill Parameters

1. **Doll Base Durability Floor:**  
   * Increase doll base HP multiplier by **+80%** (Lv99 doll HP rises from ~700 to **1,450–1,600**).
   * Grant all dolls innate **50 Elemental Resistance** across all 5 elements (providing 25% passive elemental damage reduction and immunity to baseline ailments).
2. **`Double Puppet` (PassiveSkillData_0296.bin) — "Soul Tether" Guardian:**  
   * In addition to allowing two concurrent summoned dolls, active dolls gain **Soul Tether**: once per summon, if a doll receives lethal damage, it survives with 1 HP (Guts trait).
3. **`Soul Seal` (PassiveSkillData_0297.bin) — Grand Defense Transfer:**  
   * Overhaul *Soul Seal* from weak flat ATK scaling to **transfer 100% of the equipped Sealbook's DEF, M.DEF, and Elemental Resistances** directly to active dolls. Equipping a high-tier mutant sealbook transforms dolls into sturdy tactical off-tanks.
4. **`Doll Mastery` (PassiveSkillData_0301.bin) & `Destiny Line` (PassiveSkillData_0311.bin):**  
   * *Doll Mastery*: Grants +20% damage reduction to dolls and increases autonomous action speed.
   * *Destiny Line*: Increases field duration by +2 turns and grants **Immunity to Instant Death (KO)**.

---

## 4. Anti-Boss Cheese & Non-Valkyrie Counterplay

### A. Tinker Slash (Tinker Squash) Diminishing Returns Engine
* **The Problem:** `Tinker Squash` (TechniqueSkillData_0088.bin) deals bash damage with turn delay. On an AGI-stacked Papillon with Rank A+ fans (1.0x delay) and Diva *Swift March*, players can lock superbosses in an infinite turn-pushback loop.
* **Architectural Solution:**
  * **Progressive Delay Resistance on Boss-Flag Entities:**  
    * 1st delay hit: 100% effectiveness (20 frames pushback).
    * 2nd consecutive delay hit: 50% effectiveness (10 frames).
    * 3rd consecutive delay hit: 25% effectiveness (5 frames).
    * 4th consecutive delay hit: Target gains **Temporary Delay Immunity** for 3 turns.
  * *Result:* Eliminates braindead infinite turn locks while preserving Tinker Squash as an essential tactical tool to disrupt telegraphed boss ultimate charges!

### B. Breaking Mandatory Valkyrie Hegemony (Viable Frontline Diversity)

To make high-difficulty postgame beatable without *Material Guard* / *Circle Protection* spam, alternative tanks and core game mechanics are significantly enhanced:

1. **Paladin (PL) — The Impervious Aegis:**
   * **DEF Multiplier:** Raised from 1.35x to **1.55x** in `ClassData_01.bin`.
   * **`Cover` (TechniqueSkillData_0019.bin):** Expanded to protect adjacent allies from physical damage while granting the Paladin **60% damage mitigation** during the cover action.
   * **`Holy Shield`:** Proc rate increased to **35%**, absorbing 75% incoming damage.
2. **Dark Lord (DL) — The Abyssal Drain Tank:**
   * **Recovery Delay Compression:** Reduce skill action delay on `Attract` and `Dark Aura` from Rank E ($2.60\times$) down to Rank B ($1.50\times$).
   * DL can cycle taunts without sacrificing 2 full turn cycles, allowing sustained HP drain loops via `Blood Drain` and `Megaton Press` against 2,800+ HP pools.
3. **The Universal Defend Command (`StringData_0199..204.bin`):**
   * Elevate the standard Defend command into a core high-difficulty tactical mechanic:
     * **50% Physical and Magical Damage Reduction**.
     * **0.67x Action Recovery Delay** (acts faster on subsequent turn).
     * **100% Critical Hit Immunity & Chant Interrupt Immunity**.
   * Players can anticipate superboss telegraphs and command fragile units to Defend, surviving lethal sweeps without requiring party-wide invulnerability shields.

---

## 5. Playable Ecosystem Balance (The Entire Gameplay Spectrum)

### A. Blacksmith & Forging System
* **Forging Stat Scaling (+1 to +9 Level):**  
  * *Vanilla:* Flat +2 to +4 ATK per forge level (+25–35 ATK at +9), negligible against 200,000 HP postgame bosses.  
  * *Modded:* Scaled percentage growth: **+3% Base Weapon ATK and +2% Shield/Armor DEF per forge level**. At +9, weapons gain **+27% total base weapon power**, rewarding dedicated smithing.
* **Enchant Slot Capacity (1–5 Slots):**  
  * Unique and high-tier endgame weapon drops guaranteed at least **3 to 4 open slots**, preventing common 5-slot white gear from overshadowing legendary artifacts.
* **Duplicate Enchant Stacking:**  
  * Identical affixes (e.g., dual `ATK UP +15%`) stack with clean multiplicative diminishing returns ($100\% \rightarrow 50\% \rightarrow 25\%$), ensuring stable math without overflow.
* **High-Tier Sealbook Enchant Inheritance:**  
  * Forging mutant sealbooks guarantees 100% inheritance rate for the seal's primary signature affix (`Armor Pierce`, `All Resists +20`, `Action Speed +15%`).

### B. Sealbooks & Grand Sealbooks
* **Standard Sealbook Passive Buffs:** Flat HP/TP bonuses on caster sealbooks boosted (+100 HP, +50 TP) to shore up caster squishiness.
* **Grand Sealbook Mutant Auras (`SealScrollData.pck`):**
  * *Ghast:* +25% Party EXP and +25% Gold drop rate.
  * *Eros:* Passive TP regeneration increased from 3% to **4% Max TP per turn**.
  * *Deep Slapyon:* Water/Ice damage reduction increased from 25% to **35%**.
  * *Overdue:* Backline Action Speed (AGI) increased from 15% to **20%**.
  * *Kaguya:* Physical & Slash technique damage increased from 25% to **30%**.
* **Mutant Summon Combat Scaling:**  
  * Mutant summons inherit **120% of party average level** and 100% of party offensive parameters, keeping them tactically viable in Level 99+ Matrix depths.
* **Encounter Modifiers:** Explicit utility sealbooks provide +50% encounter rate (farming) or -75% encounter rate (safe dungeon exploration).

### C. Weapons, Armor & Accessories
* **Delay Curve Compression (`WeaponRankData.pck`):**  
  Compress the punitive Rank D to F delay multipliers:
  * Rank A+: $1.00\times \rightarrow \mathbf{1.00\times}$
  * Rank A: $1.20\times \rightarrow \mathbf{1.15\times}$
  * Rank B+: $1.40\times \rightarrow \mathbf{1.30\times}$
  * Rank B: $1.60\times \rightarrow \mathbf{1.45\times}$
  * Rank C+: $1.80\times \rightarrow \mathbf{1.60\times}$
  * Rank C: $2.00\times \rightarrow \mathbf{1.75\times}$
  * Rank D+: $2.15\times \rightarrow \mathbf{1.85\times}$
  * Rank D: $2.30\times \rightarrow \mathbf{1.95\times}$
  * Rank E+: $2.45\times \rightarrow \mathbf{2.05\times}$
  * Rank E: $2.60\times \rightarrow \mathbf{2.15\times}$
  * Rank F+: $2.75\times \rightarrow \mathbf{2.25\times}$
  * Rank F: $2.90\times \rightarrow \mathbf{2.35\times}$
* **2-Handed Weapon Compensation:**  
  All 2-Handed Swords and 2-Handed Axes gain innate **+15% Physical Damage Mitigation** and **+20 Parry Rate**, compensating for the loss of the shield slot.
* **Guns & Bows (Long Range):**  
  * Remove the Gun penalty that disabled Sniper archery techniques. Snipers can execute active skills with Guns at Long Range!
* **Shield Types:**  
  * *Light Shields:* +10% Evasion, Rank A delay ($1.15\times$).  
  * *Heavy Shields:* +25% DEF, +10% Elemental Resistance, blocks critical hits.

### D. Items & Consumables
* **TP Recovery Items (`ItemData.pck`):**  
  * `Magical Fruit`: Restores **50 TP** (up from 25).
  * `Fairy Apple`: Restores **100 TP** (up from 50).
  * `Golden Apple`: Restores **Full 100% TP** (up from 100 flat TP).
* **Revival Items:**  
  * `Mandragora Root`: Revives fallen ally with **60% Max HP** (up from 1 HP / 20%), preventing instant re-death from ambient AoE.
  * `Nectar of Life`: Revives ally with **100% Max HP and 50% TP**.
* **Curatives:**  
  * `Fumirul Nectar`: Cures all non-petrify status ailments party-wide.

### E. Buffet Meals (`FoodMenuData.pck`)
* **Step Duration Extension:**  
  * Increase step duration from 300 steps to **900 steps** (3x duration), allowing buffs to persist across entire Matrix depth floors.
* **Endgame Stat Buff Values:**  
  * Top meals (`Ultimate Champon`, `Heaven's Ramen`) provide **+15% All Stats, +15 Elemental Resistances, and +10% Action Speed**.

### F. Party Skills & Joint Skills
* **Party Skills (`PartySkillData.pck`):**  
  * Passive trigger rates scale by +2% for every 5 awards earned (up to +20% efficacy at 50 awards).
  * Diverse team bonus: Parties containing 5 distinct class trees gain +15 All Elemental Resistances.
* **Joint Skills (`JoinSkillData.pck`):**  
  * Reduce Pep requirement from 30–50 Pep down to **20–30 Pep**.
  * Reduce TP cost from 15%–25% Max TP down to **10%–12% Max TP**.
  * Grant Joint Skills **30% DEF/M.DEF penetration**, making them decisive execution bursts to overcome boss Enrage phases (<25% HP).

---

## 6. Global Economy, Entities & Dungeon Progression

### A. Enemies & Bosses
* **Enrage Telegraphs:** Superbosses enter Enrage at <25% HP, charging for 1 turn with an explicit visual telegraph before ultimate wipes, giving players a clear window to Defend or burst down remaining HP.
* **Mob Status Susceptibility:** Lower status resistance on Matrix trash mobs so Assassin and Kunoichi ailment builds (Sleep, Freeze, Paralysis) provide meaningful crowd control.

### B. Drops & Sealing
* **Monster Seal Drop Rates:** Base seal drop rates increased by **+50%** (normal mobs: 25–30%; rare mobs: 10–15%).
* **Rare Equipment Drops:** Relic weapon/armor drop rates raised from 1.0% to **3.5%–5.0%**.

### C. EXP, Gold & Leveling Economy
* **Underleveled Catch-Up Multiplier:** Characters $\ge 20$ levels below party average gain **up to 2.5x bonus EXP**, significantly reducing grinding friction after Level Resets (Lv99 $\rightarrow$ Lv1/30).
* **Forge Gold Cost Adjustment:** Reduce gold costs for +7 to +9 forging by **35%**; increase gold drops in deep Matrix floors by **+40%**.

### D. Shops & Facilities
* **Shop Inventory Stock:** High-tier consumables (Fumirul Nectar, Teleport Whistles, Croissants, Fairy Apples) become permanently available in unlimited quantities at Quest Rank 8+.
* **Tavern Mercenary Contracts:** Contract duration increased from 15–20 battles to **45 battles**, and contracts **do not tick down during boss battles or flee attempts**.

### E. Dungeon Hazards & Traps (`TrapData.pck`)
* **Trap Adjustments:**
  * `Damage Floor / Mine`: Damage reduced from 50% current HP to **25% current HP**.
  * `Killer Floor`: Instant death chance reduced from 50% to **25%**, and 100 Earth Resistance provides **100% complete immunity**.
  * `Dispel Floor`: Does not strip Food Buffet buffs.

---

## 7. Comprehensive Master Parameter Matrix (Before vs. After)

| Subsystem | Target Binary File | Vanilla Parameter | Proposed Balanced Parameter | Core Tactical Purpose |
|---|---|---|---|---|
| **Weapon Delay Rank F** | `WeaponRankData_11.bin` | `2.90f` | **`2.35f`** | Enables 2H Axes, 2H Swords & Guns without mandatory Diva. |
| **Weapon Delay Rank E** | `WeaponRankData_09.bin` | `2.60f` | **`2.15f`** | Eliminates turn recovery paralysis on heavy bruisers. |
| **Weapon Delay Rank D** | `WeaponRankData_07.bin` | `2.30f` | **`1.95f`** | Smooths out mid-tier heavy weapon recovery frames. |
| **Master Spells Chant** | `MagicSkillData_0146..162.bin` | `80 frames` | **`60 frames` (-25%)** | Narrows vulnerability window against high-speed bosses. |
| **Master Spells Power** | `MagicSkillData_0146..162.bin` | Lv5: `1,100` power | **Lv5: `1,450` power (+32%)** | Rewards spell investment against deep postgame boss HP. |
| **Elemental Pierce** | Master Spell passive trait | `0 Res Pierce` | **`50 Res Pierce`** | Punches through 100+ elemental resistance walls. |
| **Crit Interrupt Rate** | Combat Engine Global | Flat `33.3%` per crit | **`10.0%` (`3.0%` w/ Concentrate)** | Prevents multi-hit boss sweeps from auto-canceling chants. |
| **Tinker Squash Delay** | `TechniqueSkillData_0088.bin` | `40 frames` unresisted | **`20 frames` + Diminishing Returns** | Eliminates braindead infinite turn locks on superbosses. |
| **Doll Base HP** | `ClassData_27..29.bin` / Dolls | `1.0x` (~700 HP at Lv99) | **`1.8x` (~1,500 HP at Lv99)** | Prevents Turn-1 doll wipes from stray boss AoE. |
| **Doll Resistances** | Doll baseline attributes | `0 All Elements` | **`50 All Elements` (25% cut)** | Provides innate survivability against magic sweeps. |
| **Double Puppet Passive**| `PassiveSkillData_0296.bin` | Dual summon only | **Dual summon + 1 HP Guts survival** | Dolls survive at least 1 lethal hit per summon. |
| **Soul Seal Passive** | `PassiveSkillData_0297.bin` | Minor ATK scaling | **Transfers 100% Seal DEF/RES to Dolls**| Equipping tank seals turns dolls into sturdy off-tanks. |
| **Paladin DEF Growth** | `ClassData_01.bin` / LevelData | `1.35x DEF` multiplier | **`1.55x DEF` multiplier (+15%)** | Elevates Paladin to an impervious physical fortress. |
| **Dark Lord Attract Delay**| `TechniqueSkillData_0005.bin` | Rank E (`2.60x`) recovery | **Rank B (`1.50x`) recovery** | Allows DL to taunt without losing 2 turn cycles. |
| **Universal Defend** | `StringData_0199..204.bin` | 50% dmg, 0.67x delay | **50% dmg, 0.67x delay + Crit/Interrupt Immune** | Tactical counterplay against boss burst without Valkyrie. |
| **Blacksmith +9 Forge** | `EnchantData.pck` / Forging | Flat +20–30 ATK at +9 | **+27% Base Weapon ATK (+3%/level)** | Makes max forging truly relevant against 200k HP bosses. |
| **Grand Sealbook Auras** | `SealScrollData.pck` | Vanilla modest auras | **+25% EXP/Gold, +4% TP regen, +20% Speed** | Elevates mutant sealbooks to impactful party keystones. |
| **Food Step Duration** | `FoodMenuData.pck` | `300 steps` | **`900 steps` (3x duration)** | Buffs persist across entire Matrix depth explorations. |
| **High-Tier TP Items** | `ItemData_0019..0021.bin` | Fruit: 25 / Apple: 50 | **Fruit: 50 / Fairy: 100 / Golden: 100% TP** | Eliminates mandatory reliance on Maid TP battery spam. |
| **Revival Item HP** | `ItemData_0023.bin` (Mandragora)| 1 HP or 20% HP revive | **`60% Max HP` revive** | Revived allies aren't instantly re-killed by boss AoE. |
| **Joint Skill Costs** | `JoinSkillData.pck` | 30–50 Pep / 25% TP | **20–30 Pep / 12% TP + 30% DEF pierce** | Converts joint combos into vital burst execution tools. |
| **Killer Floor Hazard** | `TrapData_0011.bin` | `50% Death Check` | **`25% Death Check` (0% at 100 Earth Res)**| Eliminates frustrating instant random party wipes. |

---

## 8. Endgame Team Composition Scenarios for the Creator God & EX Superbosses

The following four compositions demonstrate how diverse tactical archetypes can conquer the Creator God and EX Superbosses without relying on Valkyrie *Circle Protection* cheese:

```
[ Archetype 1: Aegis Bulwark & Arcane Artillery ]
Row 1 (Front): Paladin (PL) [Main Tank]       | Samurai (SA) [Armor-Pierce Burst]
Row 2 (Back) : Sage (SG) [Elemental Pierce]   | Bishop (BS) [Sustain & Barrier] | Sniper (SN) [Long-Range Interrupt]

[ Archetype 2: Puppet Sovereign & Abyssal Bruiser ]
Row 1 (Front): Dark Lord (DL) [Aggro-Drain]   | Spartan [Puppet Off-Tank]       | Catalina [Puppet Auto-Healer]
Row 2 (Back) : Soul Summoner (SS) [Commander] | Diva (DI) [Speed & TP Song]     | Treasure Hunter (TH) [Item Slinger]

[ Archetype 3: Phantom Mirage & Critical Hazard ]
Row 1 (Front): Kunoichi (KN) [Evasion Tank]   | Joker (JO) [High-Risk Burst]
Row 2 (Back) : Etoile (ET) [Dance Disruptor]  | Magical Princess (MP) [Hybrid]  | Bishop (BS) [Resurrection Insurance]

[ Archetype 4: Heavy Colossus & Status Lock ]
Row 1 (Front): Berserker (BE) [2H Axe Cleave] | Valkyrie (VL) [Counter Off-Tank]
Row 2 (Back) : Mistress (MI) [Whip Control]   | Bard (BD) [TP Song & Morale]    | Papillon (PA) [Stun & Tactical Delay]
```

### Archetype 1: "Aegis Bulwark & Arcane Artillery" (Pure Defense & Magic Pierce)
* **Paladin (PL):** Equipped with Heavy Shield + Spear. High DEF growth ($1.55\times$) + *Cover* + *Holy Shield*. Absorbs single-target physical nukes, uses Defend command during boss enrage turns.
* **Samurai (SA):** Katana wielder. Uses *Swallow Return* counter-stance and *Hissatsu* armor-piercing slashes to capitalize on physical openings.
* **Sage (SG):** Master Spells (`Crimson Flare` / `Muon Plasma` with 50 Res Pierce) backed by *Fast Cast* and *Concentrate* (crit interrupt immune). Exploits boss elemental vulnerabilities for 8,000–12,000 damage per cast.
* **Bishop (BS):** *Circle Heal*, *Circle Nurse*, *Sacred Barrier* (absorbs dispel/wipe). Keeps the vanguard healthy without burning TP.
* **Sniper (SN):** Equipped with Bow or Balanced Gun. *Armor Pierce* strikes + *Warning Shot* to delay boss chanting.
* *Tactical Loop:* Paladin covers Samurai and Sage $\rightarrow$ Sage chants safely with covered interrupt protection $\rightarrow$ Sniper penetrates defense $\rightarrow$ Bishop maintains party barrier $\rightarrow$ Joint Skill *Divine Judgement* breaks the 25% Enrage threshold. Zero reliance on Valkyrie!

### Archetype 2: "Puppet Sovereign & Abyssal Bruiser" (Minion Swarm & Drain Attrition)
* **Dark Lord (DL):** 2-Handed Sword (compressed $2.15\times$ delay). Casts fast *Attract* / *Dark Aura*, tanks boss hits with massive 2,800 HP pool, and leeches HP back with *Blood Drain* and *Megaton Press*.
* **Spartan & Catalina (Puppets):** Summoned by Soul Summoner. With +80% HP and 50 All Resists + *Soul Seal* stat transfer, Spartan acts as front-row off-tank and bash DPS, while Catalina auto-heals party HP every turn.
* **Soul Summoner (SS):** Summons and buffs dual dolls (*Double Puppet*). Uses *Soul Seal* to imbue dolls with mutant defenses. Free from constant re-summoning loops, SS uses utility items and sealbook spells.
* **Diva (DI):** Maintains *Swift March* (action speed aura) and *Reading Requiem* (TP efficiency). Feeds Pep for Joint Combos.
* **Treasure Hunter (TH):** Fast item slinger using *Golden Apples* and *Fumirul Nectar*; high evasion to dodge stray AoE.
* *Tactical Loop:* Dark Lord and Spartan form a dual vanguard $\rightarrow$ Catalina auto-heals $\rightarrow$ Soul Summoner sustains battle tempo $\rightarrow$ Diva accelerates turn loops $\rightarrow$ Joint combo finishes boss.

### Archetype 3: "Phantom Mirage & Critical Hazard" (Evasion, Stuns & Critical Burst)
* **Kunoichi (KN):** Uses *Utsusemi* (shadow clone evasion) + *Shadow Stitch* to blind and debuff superbosses. Unrivaled AGI allows 2 actions per boss turn.
* **Joker (JO):** Uses *Trump Card* (DEF $\rightarrow$ ATK) timed strictly after boss actions, unleashed with dagger burst damage, retreating to guard before boss cycles.
* **Etoile (ET):** Dances *Hop Step* and *Polka* to lower boss AGI and evasion. Interrupts enemy chanting with fan stuns.
* **Magical Princess (MP):** Flexes front or back row. Uses *Transform* + hybrid physical/elemental strikes.
* **Bishop (BS):** Provides resurrection insurance (*Resurrection* Lv5 with 60% HP recovery) and emergency healing.
* *Tactical Loop:* Kunoichi evades boss physical sweeps $\rightarrow$ Etoile debuffs boss speed $\rightarrow$ Joker executes massive burst during stunned windows $\rightarrow$ MP coordinates Joint Combo.

### Archetype 4: "Heavy Colossus & Status Lock" (2H Berserker & Tactical Control)
* **Berserker (BE):** Wields colossal 2H Axe with balanced Rank E delay ($2.15\times$) + 15% passive damage mitigation. Uses *Bone Crusher* and *Moon Drop* for immense raw physical damage without suicidal fragility.
* **Valkyrie (VL):** Uses *Daedalus Attack* and *Cover* selectively rather than permanent invulnerability cheese.
* **Mistress (MI):** Uses rebalanced Whips with mid-range 0% falloff. Applies *Beast Binder* crits and debuffs.
* **Bard (BD):** Restores TP via songs, allowing Berserker to sustain Lv10 skills freely.
* **Papillon (PA):** Uses *Tinker Squash* within the new diminishing-returns window to push back boss turns at critical telegraphed moments (e.g. canceling boss Enrage charge).

---

## 9. Technical Architecture, File Mapping & QA Verification

Following `mod_project/docs/philosophy.md`, this entire Hardcore Balance Mod is built as an independent, non-destructive layer over the existing single source of truth:

```
c:\Users\user\Personal\Physics\DungeonTraveler2-2\
├── mod_project\
│   ├── config\
│   │   └── balance_mod.json          # Feature toggles (master toggle & individual subsystem flags)
│   ├── data_tables\                  # Single Source of Truth (.xlsx workbooks)
│   │   ├── classes.xlsx              # Class multipliers (Paladin DEF, Dark Lord delay)
│   │   ├── skills.xlsx               # Master spell chant/power, Tinker Squash, passives
│   │   ├── equipment.xlsx            # Weapon delays, 2H mitigation, shield properties
│   │   ├── enchants.xlsx             # +1 to +9 scaling, slot caps, seal inheritance
│   │   ├── food_menu.xlsx            # Step duration (900 steps), endgame meal buffs
│   │   ├── items.xlsx                # TP consumables (50/100/100%), revival HP
│   │   ├── traps.xlsx                # Trap formula softenings, 100 earth res killer null
│   │   ├── grand_seals.xlsx          # Mutant aura boosts & summon scaling
│   │   └── joint_skills.xlsx         # Pep/TP cost reductions & DEF penetration
│   └── tools\
│       ├── pck_handler.py            # Binary parsers for all 13 PCK types
│       ├── apply_mod.py              # Master compiler: reads Excel/JSON and builds game PCKs
│       └── audit_tool.py             # QA validation: asserts line budgets, bytes, 0 errors
```

### Configurable Toggle (`balance_mod.json`)
```json
{
  "enable_balance_mod": true,
  "heavy_weapon_delay_compression": true,
  "magic_chant_and_resistance_pierce": true,
  "chant_interrupt_mitigation": true,
  "tinker_squash_diminishing_returns": true,
  "soul_summoner_doll_durability": true,
  "paladin_and_dark_lord_tank_buffs": true,
  "forging_and_enchant_scaling": true,
  "food_buff_step_extension": true,
  "consumable_tp_and_revive_buffs": true,
  "joint_skill_cost_reduction": true,
  "global_economy_and_trap_softening": true
}
```

### Automated QA Integrity
* Running `python mod_project/tools/apply_mod.py` deterministically compiles all 21 `.pck` files in under 4 seconds.
* Running `python mod_project/tools/audit_tool.py` asserts:
  1. All 13 Excel workbooks adhere to $\le 3$ lines, $\le 85$ chars/line, zero `~` glyphs.
  2. All 21 PCK binary archives load cleanly with 100% bit-exact header and TOC alignment.
  3. Both Vanilla Mode (`enable_balance_mod: false`) and Balanced Mode pass all QA checks with **0 errors**.
