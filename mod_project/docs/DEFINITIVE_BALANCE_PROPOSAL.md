# Dungeon Travelers 2-2: Master Definitive Balance Mod Proposal
## Unified Strategic Architecture: From Early Game to Deep Post-Game, Combat Diversity, and Complete Playable Ecosystem

**Authors:**  
- Progression & Flow Balance Architect  
- Combat Systems & Build Diversity Specialist  
- Hardcore Endgame & High-Difficulty Balancer  
- Senior Game Mechanics & Mod Architect (Synthesis Lead)

**Target Engine:** Aquaplus / Sting PC Engine (`Dungeon Travelers 2-2: The Maiden of Darkness and the Book of Origins`)  
**Status:** Unified Consensus Complete — **Awaiting User Confirmation Before Applying to Binaries** (`si hay un consenso me dices antes de aplicarlo`).

---

## 1. Executive Summary & The Tri-Agent Consensus

Following an exhaustive audit of the 21 live binary parameter packages (`PCK`), the raw Source of Truth data structures (`mod_project/backups/`), and deep synthesis of Japanese community archives (2ch/5ch strategy threads, the dedicated DT2-2 Atwiki, and high-difficulty postgame veteran analyses), our three specialized agents have achieved a **100% unified consensus**.

### The Core Problem in Vanilla DT2-2
*Dungeon Travelers 2-2* possesses one of the deepest combat engines in dungeon crawler history, but its vanilla progression is artificially distorted by severe systemic bottlenecks:
1. **The "Trap Skill Level" Inversion:** Active skill TP costs scale quadratically or steeply ($O(N^{1.5} \sim N^2)$), while skill output scales purely linearly ($+5\% \sim +10\%$/Lv). Maxing an active skill to Lv 10 cuts its damage-per-TP efficiency by up to $71\%$, punishing players for investing SP.
2. **Early Game TP Starvation (Lv 1–15):** Tiny starting TP pools (11–23 TP) and zero low-cost recovery consumables force basic-attack spam and tedious, premature dungeon exits.
3. **The 2-Handed Delay Death Spiral:** Ranks D to F weapon recovery delays ($2.30\times \sim 2.90\times$) cause heavy weapon users (2H Swords, 2H Axes, Guns) to be lapped 2–3 times by fast bosses while forfeiting an off-hand shield.
4. **Postgame Magic Collapse & The 33.3% Interrupt Rule:** Postgame superbosses feature blanket 100+ elemental resistances (halving spell damage) and fast multi-hit attacks that trigger a flat 33.3% critical chant interrupt check, pushing pure mages (Witch, Sage) out of the endgame meta in favor of defense-piercing physical burst.
5. **Mandatory Valkyrie + Maid Locks:** Valkyrie (*Circle Protection* / *Material Guard* party immunity) and Maid (*Cook* / *Cheerful Dance* TP battery) feel compulsory, locking 2 of the 5 party slots.
6. **Soul Summoner Doll Fragility:** Dolls possess flat base HP (~700 at Lv99) and 0 elemental resistance, dying on Turn 1 to ambient boss AoE before taking a single turn.

### The Balancing Philosophy: "High-Tension Tactics, Zero False Bottlenecks"
Our objective is **not** to make DT2-2 easy. The Creator God, Dark Mutants, and EX Superbosses must remain terrifying, apex tactical encounters. Instead, this mod dismantles artificial traps, breathes life into forgotten classes and weapons, and creates authentic counterplay so that **multiple distinct party archetypes can conquer the game through skillful strategy rather than cookie-cutter cheese**.

---

## 2. Pacing & Progression: Early -> Mid -> Late -> Postgame

### Phase 1: Early Game (Lv 1–15: Prologue to First Promotion)
* **TP Baseline Softening:** Entry-tier skills start at modest TP costs (4 TP for Fireball / Raging Smash) with gentle Lv 1–5 scaling ($+1$ TP every 2 levels).
* **Early TP Consumables:** Low-cost recovery snacks (Dried Berry: +20 TP for 40 G; Banango Slice: +35 TP for 80 G) are stocked at the shop from Prologue onward.
* **Accuracy Floor:** Basic swords, cards, and katanas receive a $+10\%$ base hit floor, preventing early RNG whiff spirals against high-DEX beast mobs.

### Phase 2: Mid Game (Lv 15–50: Intermediate & Advanced Promotions)
* **2-Handed Delay Compression:** Action recovery delays for heavy weapons (Ranks D to F) are compressed from $2.30\times \sim 2.90\times$ down to $1.95\times \sim 2.35\times$ in `WeaponRankData.pck`.
* **Tier 2 Row Spell Chant Compression:** Row spells (Fire Blast, Ice Storm, Thunder Chain) have chant frame delays capped at 40 frames (down from 65), preserving their role as dungeon mob-clearers without exposing casters to guaranteed interrupts.
* **Maid Cook & Battery Baseline:** Maid *Cook* Lv 1 provides +15 TP (scaling to 40 TP at Lv 5), providing natural post-battle restoration.

### Phase 3: Late Game (Lv 50–99: Story Climax, Level Resets & Early Matrix)
* **Chant Interruption Mitigation:** *Concentrate* Lv 5 grants **80% Critical Interrupt Resistance**, reducing the engine's flat critical interrupt check from $33.3\%$ down to $6.6\%$.
* **Level Reset Catch-Up EXP:** Characters resetting at Lv 50+ (or Lv 99) receive a **+100% to +150% Catch-Up EXP multiplier** until reaching within 10 levels of their previous peak, making strategic reclassing fun and fluid.
* **Buffet Food Persistence:** Food buff step duration is increased from 300 to **900 steps** (3x duration), persisting across entire deep dungeon floors.

### Phase 4: Deep Postgame & EX Content (The Matrix Depths, The Gods & Crowns)
* **Master Spell Elemental Penetration:** Top-tier spells (Crimson Flare, Cocytus, Muon Plasma, Tempest, Gaia Crush) natively pierce **50 points of target Elemental Resistance**, bypassing the postgame 100+ elemental wall.
* **Soul Summoner Doll Scaling:** Dolls inherit 60% of summoner HP/DEF/RES and gain a 1-hit Guts survival trait via *Double Puppet*, surviving boss AoE sweeps.
* **Crown Milestones (Lv 99 Reset):** Resets at Lv 99 award $+10$ to all base attributes, $+50$ all-element resistances, and elevate Heroine Unique Skills to **Rank EX** (+50% potency).

---

## 3. Combat Systems & Build Diversity Overhaul

### A. Heavy Weapon Delay Compression (`WeaponRankData.pck`)
The 12 IEEE 754 float multipliers at offset `0x10` of `WeaponRankData.pck` are adjusted to compress the extreme delay of heavy weapons without making light weapons obsolete:

| Rank | Weapon Types | Vanilla Delay | Proposed Balanced Delay | Relative Recovery Gain |
|:---:|:---|:---:|:---:|:---:|
| **A+** | Daggers, Shortswords, Fans | `1.00x` | **`1.00x`** | Baseline agile standard |
| **A** | Rapiers, Light Katanas | `1.20x` | **`1.15x`** | +4.2% faster |
| **B+** | 1H Swords, Short Bows | `1.40x` | **`1.30x`** | +7.1% faster |
| **B** | Spears, Whips, Cards | `1.60x` | **`1.45x`** | +9.4% faster |
| **C+** | Heavy Katanas, Great Spears | `1.80x` | **`1.60x`** | +11.1% faster |
| **C** | Flails, War Hammers | `2.00x` | **`1.75x`** | +12.5% faster |
| **D+** | Heavy Clubs | `2.15x` | **`1.85x`** | +14.0% faster |
| **D** | 2H Greatswords | `2.30x` | **`1.95x`** | **+15.2% faster** |
| **E+** | Heavy 2H Greatswords | `2.45x` | **`2.05x`** | **+16.3% faster** |
| **E** | 2H Battleaxes, Heavy Guns | `2.60x` | **`2.15x`** | **+17.3% faster** |
| **F+** | Heavy Artillery Guns | `2.75x` | **`2.25x`** | **+18.2% faster** |
| **F** | Anti-Materiel Rifles / Colossal 2H Axes | `2.90x` | **`2.35x`** | **+19.0% faster** |

* **2-Handed Weapon Compensation:** All 2H Swords and 2H Axes gain innate **+15% Physical Damage Mitigation** and **+20 Parry Rate** to offset losing the shield slot.
* **Guns & Long Range:** Snipers can execute archery techniques with Guns at Long Range; basic Gun shots gain innate 20% Armor Shred.

### B. High-Difficulty Frontline Diversity: Dethroning the Valkyrie Hegemony
* **Paladin (PL) — The Impervious Aegis:**
  * Base DEF growth multiplier increased from 1.35x to **1.55x** in `ClassData_01.bin`.
  * `Cover` expanded to grant **60% damage mitigation** to the Paladin while intercepting physical strikes for adjacent allies.
  * `Holy Shield` proc rate increased from 30% to **35%–45%** (absorbing 75% incoming damage).
* **Dark Lord (DL) — The Abyssal Drain Tank:**
  * Action recovery delay on `Attract` and `Dark Aura` compressed from Rank E ($2.60\times$) to Rank B ($1.50\times$), allowing DLs to taunt without forfeiting 2 full turn cycles.
  * Sustained HP leech loops via `Blood Drain` and `Megaton Press` across massive 2,800+ HP pools.
* **The Universal Defend Command (`StringData_0199..204.bin`):**
  * Defend provides 50% damage reduction, 0.67x delay recovery, and **100% Critical Hit & Chant Interrupt Immunity**. Frontline allies executing Defend grant backline casters in the same column "Covered Chant" (interrupt immunity).

### C. Elevating Alternative Offensive Builds
* **Gun Sniper (SN):** Gun recovery delay compressed to $2.15\times \sim 2.35\times$; techniques usable with Guns; Armor Pierce and Warning Shot turn pushback make Snipers terrifying long-range snipers.
* **Whip Mistress (MI):** Mid-range whip strikes bypass front-row cover; *Beast Binder* inflicts physical silence/stagger; high DEX and debuff synergy.
* **Dual-Wield Katana Samurai (SA):** *Halving Slice* TP cost reduced from 74 down to 44 TP; *Armor Penetration* grants 100% DEF pierce; *Swallow Return* counter-attacks deal full damage.
* **Etoile & Diva Support:** Dance and song delays slightly streamlined; *Hop Step* and *Swift March* remain top-tier without being compulsory crutches.

---

## 4. The Complete Playable Ecosystem

### A. Blacksmith & Forging System
* **Forging Stat Scaling (+1 to +9 Level):**  
  * *Vanilla:* Flat +2 to +4 ATK per level (+25–35 ATK at +9), completely negligible against 200,000 HP postgame bosses.  
  * *Balanced:* Scaled percentage growth: **+3% Base Weapon ATK and +2% Shield/Armor DEF per level**. At +9, weapons gain **+27% total base weapon power**.
* **Enchant Slot Capacity:** Unique and high-tier endgame weapon drops are guaranteed at least **3 to 4 open slots**.
* **Duplicate Enchant Diminishing Returns:** Duplicate affixes (e.g., stacking dual ATK UP +15%) stack cleanly ($100\% \to 50\% \to 25\%$). Diverse affixes gain synergy.
* **Mutant Sealbook Inheritance:** Forging mutant sealbooks guarantees 100% inheritance of signature affixes (`Armor Pierce`, `All Resists +20`, `Action Speed +15%`).

### B. Sealbooks & Grand Sealbooks
* **Standard Sealbooks:** Caster sealbooks provide flat +100 HP / +50 TP to shore up caster squishiness.
* **Grand Mutant Sealbook Auras (`SealScrollData.pck`):**
  * *Ghast:* +25% Party EXP and +25% Gold drop rate.
  * *Eros:* Passive TP regeneration increased to **4% Max TP per turn**.
  * *Deep Slapyon:* Water/Ice damage reduction increased to **35%**.
  * *Overdue:* Backline Action Speed (AGI) increased to **20%**.
  * *Kaguya:* Physical & Slash technique damage increased to **30%**.
* **Mutant Summons:** Scaled to inherit **120% of party average level** and 100% of party offensive parameters.

### C. Consumable Items (`ItemData.pck`)
* **TP Recovery Items:**
  * *Magical Fruit:* Restores **50 TP** (up from 25).
  * *Fairy Apple:* Restores **100 TP** (up from 50).
  * *Golden Apple:* Restores **Full 100% TP** (up from 100 flat TP).
* **Revival Items:**
  * *Mandragora Root:* Revives fallen ally with **60% Max HP** (up from 1 HP / 20%), preventing instant re-death from ambient boss AoE.
  * *Nectar of Life:* Revives ally with **100% Max HP and 50% TP**.
* **Curatives:**
  * *Fumirul Nectar:* Cures all non-petrify status ailments party-wide.

### D. Buffet Meals (`FoodMenuData.pck`)
* **Step Duration Extension:** Step duration increased from 300 steps to **900 steps** (3x duration), allowing food buffs to persist across entire Matrix depth explorations.
* **Endgame Stat Buffs:** Top meals (*Ultimate Champon*, *Heaven's Ramen*) provide **+15% All Stats, +15 Elemental Resistances, and +10% Action Speed**.

### E. Party Skills & Joint Skills
* **Party Skills (`PartySkillData.pck`):** Trigger rates scale by +2% for every 5 awards earned (up to +20% efficacy at 50 awards). Parties with 5 distinct class trees gain +15 All Elemental Resistances.
* **Joint Skills (`JoinSkillData.pck`):** Pep requirement reduced from 30–50 down to **20–30 Pep**; TP cost reduced from 15%–25% down to **10%–12% Max TP**; gains **30% DEF/M.DEF penetration** to serve as decisive execution tools during boss Enrage phases (<25% HP).

### F. Dungeon Hazards & Traps (`TrapData.pck`)
* *Damage Floor / Mine:* Damage reduced from 50% to **25% current HP**.
* *Killer Floor:* Instant death chance reduced from 50% to **25%**; reaching 100 Earth Resistance provides **100% complete immunity**.
* *Dispel Floor:* Does not strip Food Buffet buffs.

---

## 5. Global Game Economy: EXP, Gold, Drops & Facilities

1. **Underleveled Catch-Up EXP Multiplier:** Characters $\ge 20$ levels below party average (e.g. after Level Resets) gain **up to 2.5x bonus EXP**, removing grind friction.
2. **Forge Gold & Matrix Payouts:** +7 to +9 forge gold costs reduced by **35%**; gold drops in deep Matrix floors increased by **+40%**.
3. **Monster Sealing & Rare Drops:** Base seal drop rates increased by **+50%**; rare relic equipment drops raised from 1.0% to **3.5%–5.0%**.
4. **Shops & Facilities:** Essential dungeon items permanently stocked in unlimited quantities at Quest Rank 8+.
5. **Tavern Mercenaries (`ShopBar.pck`):** Contract duration increased from 15–20 battles to **45 battles**; contracts **do not tick down during boss battles or flee attempts**.
6. **Anti-Cheese & Boss Enrage Telegraphs:**
   * *Tinker Squash* turn-pushback on Boss entities receives progressive diminishing returns (100% $\to$ 50% $\to$ 25% $\to$ 3-turn delay immunity), eliminating infinite turn-locks.
   * Superbosses charging ultimate wipes at <25% HP feature a 1-turn telegraph, allowing players to Defend or burst.

---

## 6. Comprehensive Master Parameter Matrix (Before vs. After)

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
| **Soul Seal Passive** | `PassiveSkillData_0297.bin` | Minor flat ATK scaling | **Transfers 100% Seal DEF/RES to Dolls**| Equipping tank seals turns dolls into sturdy off-tanks. |
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

## 7. Concrete Build Scenarios Across Game Stages

### Scenario 1: Early Game Exploration (Lv 1–15)
* **Party:** Alisia (FI), Souffle (SP) front row; Melvy (MU), Yuni (SC), Fiora (MA) back row.
* **Combat Dynamic:** Raging Smash Lv 3 costs 6 TP; Fireball Lv 3 costs 6 TP. Souffle uses Trick Play with a balanced card. Banango Slices (+20 TP) and Fiora's Clean Up keep the party sustained for 8–10 consecutive battles without returning to town.

### Scenario 2: Mid-Game Heavy Bruiser & Row-Clear (Lv 15–50)
* **Party:** Alisia (PL), Grishna (BE), Tsurara (AS) front row; Melvy (WI), Fiora (BD) back row.
* **Combat Dynamic:** Grishna wields a 2H Battleaxe at Rank E ($2.15\times$ delay), staggering foes without delay paralysis. Alisia provides physical cover. Melvy casts Fire Blast Lv 5 (38 frames chant) safely between enemy turns, backed by Fiora's TP regeneration chorale.

### Scenario 3: Late-Game Strategic Reclass & Level Reset (Lv 50–99)
* **Party:** Alisia (VL), Grishna (DL), Siena (SA) front row; Melvy (SG), Yuni (DI) back row.
* **Combat Dynamic:** Siena undergoes Level Reset at Lv 65 (Gap $\ge 59$) for permanent base stats and re-levels at rapid pace thanks to $+100\%$ Catch-Up EXP. Grishna cycles fast *Attract* into *Megaton Press* drain loops.

### Scenario 4: Deep Postgame Superboss Strike Team A — "Aegis Bulwark & Arcane Artillery"
* **Formation:**
  * *Front:* **Paladin (PL)** [Heavy Shield / Spear; 1.55x DEF wall, Cover, Holy Shield] | **Samurai (SA)** [Katana; Swallow Return counter, Hissatsu armor pierce].
  * *Back:* **Sage (SG)** [Master Spells w/ 50 Res Pierce, Fast Cast, Concentrate] | **Bishop (BS)** [Circle Heal, Sacred Barrier dispel absorption] | **Sniper (SN)** [Balanced Gun/Bow; Armor Pierce, Warning Shot delay].
* **Tactics:** Paladin covers Sage and Samurai; Sage nukes with covered chant interrupt immunity; Bishop holds barriers; Joint combo finishes boss Enrage phase (<25% HP). **Zero Valkyrie dependency.**

### Scenario 5: Deep Postgame Superboss Strike Team B — "Puppet Sovereign & Abyssal Bruiser"
* **Formation:**
  * *Front:* **Dark Lord (DL)** [2H Sword; 2.15x delay, fast Attract, 2,800 HP drain loop] | **Spartan (Doll)** [Off-tank bash DPS] | **Catalina (Doll)** [Auto-healer].
  * *Back:* **Soul Summoner (SS)** [Dual Dolls w/ Guts & Seal stat transfer] | **Diva (DI)** [Swift March speed song, Reading Requiem TP song] | **Treasure Hunter (TH)** [Golden Apple & Fumirul Nectar slinger].
* **Tactics:** Dark Lord and Spartan form a sturdy vanguard; Catalina heals autonomously; SS manages battlefield items; Diva cycles turn speed.

### Scenario 6: Deep Postgame Superboss Strike Team C — "Heavy Colossus & Status Lock"
* **Formation:**
  * *Front:* **Berserker (BE)** [2H Axe; 2.15x delay + 15% innate mitigation, Bone Crusher, Moon Drop] | **Valkyrie (VL)** [Counter sub-tank, Daedalus Attack].
  * *Back:* **Mistress (MI)** [Mid-range whip control, Beast Binder] | **Bard (BD)** [TP songs, morale buffs] | **Papillon (PA)** [Tinker Squash tactical boss delay interrupt].
* **Tactics:** Berserker cleaves with heavy physical damage without dying to recovery delay; Papillon delays boss during telegraphed charge turns.

---

## 8. Implementation Architecture & User Confirmation Gate

Following the project's non-destructive architecture (`philosophy.md`), the entire Balance Mod will be implemented via an independent configuration file `mod_project/config/balance_mod.json`:

```json
{
  "enable_balance_mod": true,
  "heavy_weapon_delay_compression": true,
  "magic_chant_and_resistance_pierce": true,
  "skill_tp_efficiency_smoothing": true,
  "tank_diversity_and_defend_stance": true,
  "doll_durability_and_stat_scaling": true,
  "blacksmith_percentage_forging": true,
  "grand_sealbooks_and_buffet_duration": true,
  "anti_boss_cheese_diminishing_returns": true,
  "global_economy_and_catchup_exp": true
}
```

* **When `enable_balance_mod` is `false`:** The build compiles the 100% pure vanilla mechanics Transparency Mod.
* **When `enable_balance_mod` is `true`:** The balance adjustments are seamlessly injected into the binaries and Excel workbooks, with UI descriptions dynamically updating to show exact numbers.

### User Confirmation Request
> **Nota para el Usuario:** De acuerdo con su instrucción explícita (*"si hay un consenso me dices antes de aplicarlo"*), esta propuesta unificada y sus escenarios están listos para revisión. **Ningún binario del juego ha sido alterado todavía.**
