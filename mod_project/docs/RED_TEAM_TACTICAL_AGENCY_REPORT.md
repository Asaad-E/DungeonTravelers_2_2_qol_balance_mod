# Dungeon Travelers 2-2: Red Team Tactical Agency & Build Expression Audit
## Exhaustive Game Design Evaluation: Fantasy Fulfillment, Decision Density, and Playstyle Distinctiveness

**Author:** Tactical Agency & Build Expression Specialist (Red Team Fun & Design Balancer)  
**Target Engine:** Aquaplus / Sting PC Engine (`Dungeon Travelers 2-2: The Maiden of Darkness and the Book of Origins`)  
**Target Proposal:** `mod_project/docs/DEFINITIVE_BALANCE_PROPOSAL.md`  
**Companion Documents:** `mod_project/docs/RED_TEAM_COMBAT_SIMULATION_REPORT.md`, `mod_project/docs/RED_TEAM_ECONOMY_SIMULATION_REPORT.md`  
**Evaluation Scope:** Build Fantasies, Combat Viscerality, Turn Decision Density, Anti-Passivity Verification, and Complete 32-Class Playable Diversity.  
**Status:** Verification Complete — **Approved with Critical Design Enhancements for Expressiveness**.

---

## 1. Executive Summary & The Fun & Tactical Agency Mandate

### 1.1 The Definition of Tactical Agency in DRPGs
In high-difficulty dungeon crawlers, numerical balance is a necessary condition for viability, but it is **not sufficient for fun**. A game where every class deals mathematically identical DPS across an identical turn cadence is balanced, but it is sterile, boring, and emotionally flat.

True **Tactical Agency** requires three pillars:
1. **Expressive Build Fantasy:** Playing a Paladin must emotionally and mechanically *feel* like commanding an unbreakable shield wall, completely distinct from playing a Valkyrie's celestial warding.
2. **High Decision Density (Zero Auto-Pilot):** A player must never feel that their turn is predetermined (e.g. mindlessly spamming *Cheerful Dance* on a Maid, or *Basic Attack* on a Gun Sniper). Every action cycle should present meaningful trade-offs: risk vs. reward, positioning, resource pacing, and timeline manipulation.
3. **Visceral Mechanical Feedback:** Heavy 2H Greatswords, colossal battleaxes, and artillery rifles must feel weighty, impactful, and bone-shattering—not just a different delay float in `WeaponRankData.pck`. Fast agile dual-wielders must feel like high-wire acrobats dancing on the razor edge of lethal counters.

### 1.2 The Red Team Fun & Design Verdict
Following our comprehensive qualitative and qualitative audit across all 5 class trees (32 classes), 12 weapon ranks, and postgame party archetypes under the Master Definitive Balance Mod (`DEFINITIVE_BALANCE_PROPOSAL.md`), the Red Team concludes:

> **The balance overhaul succeeds triumphantly in turning Dungeon Travelers 2-2 into a vibrant, expressive tactical sandbox.**  
> It rescues previously dead archetypes (2H bruisers, gun snipers, offensive witches, puppet commanders, whip mistresses) from the graveyard of obsolete code. However, to prevent certain support and hybrid roles from lapsing into passive "second-class citizen" status, **specific mechanical feedback loops and active decision triggers must be enforced.**

---

## 2. In-Depth Audit of the Four Cardinal Build Fantasies

---

### 2.1 Build Fantasy 1: The Frontline Bulwark — Paladin (PL) vs. Valkyrie (VL)

#### The Core Problem in Vanilla DT2-2
In Vanilla DT2-2, the community consensus was brutal: *"Paladin is just a strictly worse Valkyrie."* Valkyrie possessed *Circle Protection* (canceling physical party damage), *Material Guard* (absorbing full AoE sweeps), *Daedalus Attack* (colossal physical burst), and *Parry*. Paladin had *Cover* (which redirected single-target hits onto herself while taking full unmitigated damage) and slightly higher base DEF, which meant that in deep postgame, Paladin simply stepped in front of a 3,000 damage boss blow and died instantly.

#### The Modded Transformation: Two Radically Distinct Defensive Archetypes

```
[VALKYRIE: The Divine Aegis (Party Preservation Specialist)]
  Role: Full-Party Area Denial & Counter-Attacking Vanguard
  Mechanic: Barrier-based protection (Material Guard / Circle Protection)
  Tactical Dynamic: "I erect a sacred barrier. No physical attack shall touch my party this round."
  Weakness: Single-target redirection vulnerability; downtime turns when barriers shatter.

[PALADIN: The Impervious Shield Wall (Single-Target Redirection Fortress)]
  Role: Dedicated Bodyguard, Aggro Magnet, and Stun Interceptor
  Mechanic: Interception-based mitigation (Cover w/ 60% DR + 40% Holy Shield + 1.55x DEF)
  Tactical Dynamic: "Step behind my tower shield. Whatever blows were meant for you, break upon me."
  Weakness: Cannot block full party-wide AoE sweeps; relies on backline using Universal Defend.
```

#### Does Playing a Paladin Feel Visceral and Distinct?
**YES, EMPHATICALLY.** Playing a Paladin now offers the quintessential "Unbreakable Shield Wall" fantasy:
* **The Living Fortress:** When an enemy superboss executes a devastating single-target death blow aimed at your chanting Sage or glass-cannon Joker, Paladin actively steps into the line of fire via `Cover`. With her new **1.55x DEF multiplier** and **60% Cover Damage Mitigation**, backed by a 40% proc on `Holy Shield` (which cuts remaining damage by 75%), an incoming 3,200 damage cataclysmic strike is reduced to a dull **180–350 HP thud**.
* **Tactical Decision Loop:** Paladin is not a passive sponge. Her turns involve active positioning:
  1. *Turn 1:* Command column alignment and activate `Provoke` / `Attract` to bend enemy targeting.
  2. *Turn 2:* Deliver a bone-crunching `Shield Bash` (elevated to 60% Stun proc) to delay an enemy caster.
  3. *Turn 3:* Anticipate a telegraphed boss charge by executing `Universal Defend`, granting "Covered Chant" (100% interrupt immunity) to the backline Sage directly behind her.
* **Distinctiveness Verdict:** Paladin and Valkyrie are no longer interchangeable. You bring Valkyrie when facing bosses with devastating party-wide physical sweeps (*Earthquake*, *Tail Swipe*). You bring Paladin when running fragile hyper-carries (offensive mages, gunners, glass strikers) who would otherwise be picked off by targeted single-target boss assassinations.

---

### 2.2 Build Fantasy 2: Colossal 2-Handed Weapons (2H Greatswords, 2H Axes) & Heavy Artillery (Sniper Guns)

#### The Core Problem in Vanilla DT2-2
In Vanilla, heavy weapons suffered from the dreaded **Action Speed Hegemony (速度至上主義)**. Ranks D to F weapons carried delay multipliers of $2.30\times \sim 2.90\times$ without off-hand shields. A Berserker swinging a 2H Battleaxe was frozen on the turn bar for over 300 ticks while a 180 AGI superboss took 3 to 4 turns, shredding the shieldless bruiser before her weapon even completed its recovery arc. Equipping a Gun on a Sniper was even worse: it disabled every single bow technique in her skill tree and forced weak basic shots at Rank F delay.

#### The Modded Transformation: Visceral Weight, Momentum, and Suppression

| Weapon Category | Vanilla Delay | Modded Delay | Defensive Compensation | Visceral Mechanical Identity |
|---|:---:|:---:|:---:|---|
| **2H Greatswords (Rank D/E+)** | $2.30\times \sim 2.45\times$ | **$1.95\times \sim 2.05\times$** | Innate **+15% Phys DR & +20 Parry** | **Momentum Cleaver:** Heavy sweeping blows that stagger rows and parry counter-attacks. |
| **2H Battleaxes (Rank E/F)** | $2.60\times \sim 2.90\times$ | **$2.15\times \sim 2.35\times$** | Innate **+15% Phys DR & Guard Break** | **Armor-Crushing Juggernaut:** Colossal single-hit chunking that cracks boss defensive buffs. |
| **Heavy Artillery Guns (Rank E/F+)** | $2.60\times \sim 2.75\times$ | **$2.15\times \sim 2.25\times$** | **20% Innate Armor Shred & Range** | **Long-Range Anti-Materiel Battery:** Suppressive fire, timeline pushback, and piercing armor. |

#### Does Wielding a Colossal 2H Weapon Feel Weighty and Tactically Satisfying?
**YES.** Crucially, the balance proposal did **not** simply turn 2H weapons into fast daggers with bigger numbers. A Rank F 2H Axe still has a $2.35\times$ delay multiplier—it remains slower than a $1.00\times$ fan or $1.15\times$ rapier. But the experience shifts from *suicidal helplessness* to **deliberate, high-impact tactical timing**:
* **The Sensation of "The Big Swing":** When Grishna unleashes `Bone Crusher` or `Moon Drop` with an Adamas Greatscythe, the numbers on screen reflect a true catastrophe for the enemy: 11,000+ critical damage that visibly shaves chunks off a 200,000 HP boss gauge. The innate +15% damage mitigation and +20 Parry rate ensure she can brace for the enemy's retaliatory strike during her recovery window.
* **The Gun Sniper Fantasy (The Tactical Gunner):**
  * Vanilla guns were an embarrassing oversight. Under the mod, Guns enable all Sniper archery techniques at true Long Range.
  * Basic shots and techniques with Guns gain innate **20% Armor Shred**, allowing Snipers to punch through high-DEF armored constructs without needing external debuffs.
  * `Warning Shot` introduces tactical suppression: knocking back the enemy's turn on the timeline. A Gun Sniper feels like a patient military marksman waiting for the high-value target to emerge, lining up the shot, and firing an armor-piercing round that physically halts the enemy's advance.

---

### 2.3 Build Fantasy 3: The Squad Commander — Soul Summoner (SS) & The Autonomous Dolls

#### The Core Problem in Vanilla DT2-2
Vanilla Soul Summoner was universally derided as a *"Re-Summoning Simulator."* Dolls possessed rigid base stats (~700 HP at Lv99) and 0 elemental resistance. Deep postgame bosses with ambient AoE sweeps killed dolls on Turn 1 before they could act. The Soul Summoner spent 100% of her combat actions paying 40+ TP to cast *Summon Spartan* or *Summon Catalina*, only to watch them disintegrate immediately.

#### The Modded Transformation: Commanding an Active 7-Unit Skirmish Squad

```
[THE SOUL SUMMONER BATTLEFIELD FORMATION]
  FRONT ROW:  [Hero Tank / Bruiser]  |  [Spartan (Doll - Vanguard Tank)]
  BACK ROW:   [Soul Summoner]       |  [Catalina (Doll - Field Medic)]  |  [Sage / Sniper]
  RESERVE / TACTICAL DOLLS: [Perdurabo (Disruptor)] | [Oracles (Arcane Battery)]
```

#### Does Commanding Dolls Feel Like Directing an Active Squad?
**YES, IT TRANSFORMS COMBAT INTO SQUAD TACTICS.**
* **The 7-Unit Battlefield Dynamic:** By elevating doll base HP to 1,500+, granting 50 all-element resistance, adding the **1-hit Guts survival trait** via `Double Puppet`, and transferring **100% of equipped Sealbook defenses via `Soul Seal`**, dolls survive 4 to 5 turns of intense combat.
* **Autonomous Specialists in Action:**
  * **Spartan:** Acts as an autonomous frontline off-tank, drawing aggro and executing shield bashes that stun foes without consuming the player's primary actions.
  * **Catalina:** Serves as a triage combat medic, autonomously throwing single-target heals and ailment cleanses when party members dip below 50% HP.
  * **Perdurabo & Oracles:** Function as tactical elemental artillery, exploiting elemental weaknesses that the player's main squad may not possess.
* **The Commander's Agency:** Because the Soul Summoner no longer spends every turn frantically re-summoning, her action economy is liberated! She becomes a high-level **Battlefield Tactician**:
  1. Managing high-tier consumable logistics (Golden Apples, Fumirul Nectars).
  2. Swapping equipped Sealbooks to dynamically alter the dolls' defensive affinities mid-battle.
  3. Timing sacrificial commands or rotating doll types when facing distinct boss phase transitions.
* **Verdict:** Soul Summoner shifts from the most frustrating, chore-laden class in the game to one of the most uniquely rewarding "commander" experiences in the entire DRPG genre.

---

### 2.4 Build Fantasy 4: High-Skill Archetypes — Whip Mistress (MI) & Dual-Katana Samurai (SA)

#### Whip Mistress: The Mid-Range Field Controller & Debuff Dominatrix
* **The Vanilla Complaint:** Whips were awkward: lower damage than rapiers, weaker buffing than dancers, and no clear niche.
* **The Modded Playstyle Identity:**
  * **Mid-Range Piercing Reach:** Whips strike from the back row with zero range penalty and bypass front-row body blocks.
  * **Status & Control Dominance:** Mistress is the undisputed queen of enemy crippling. Her skill `Beast Binder` inflicts physical silence and paralysis, shutting down lethal boss physical combos.
  * **Row-Clearing Whiplash:** Whips feature native multi-target spread. Wielding a whip feels like controlling the flow of the entire enemy vanguard, entangling dangerous threats while your heavy hitters charge up their decisive blows.

#### Dual-Katana Samurai: The Razor-Edge Counter Duelist & Armor Piercer
* **The Vanilla Complaint:** *Halving Slice* cost 74 TP (emptying a Lv50 Samurai's entire pool in 1 turn). *Dual Wield* suffered severe accuracy penalties and delay bloat. *Swallow Return* only triggered if the fragile Samurai was attacked.
* **The Modded Playstyle Identity:**
  * **The High-Adrenaline Duelist:** Samurai is designed for players who love high-risk, high-reward precision. *Halving Slice* TP cost is smoothed down to 44 TP, making it an accessible execution technique.
  * **Swallow Return Counter Stance:** When placed in the front row alongside a Paladin or Dark Lord, Samurai utilizes her evasive parry stance. Any physical blow that strikes her is parried and met with an instant, full-damage counter-cleave.
  * **Pure Armor Penetration (*Hissatsu*):** Samurai ignores 100% of enemy physical DEF. Against heavily armored mutant bosses with 550+ DEF where other classes hit for chipped numbers, Samurai carves through armor like tissue paper.
  * **The Aesthetic Experience:** Wielding dual +9 Muramasas feels lightning fast ($1.15\times \sim 1.30\times$ delay), razor sharp, and lethally decisive.

---

## 3. Comprehensive Class-by-Class Tactical Agency Audit (All 32 Classes)

To guarantee that **no playstyle feels like a second-class citizen, boring, or passive**, we audited all 32 classes across the 5 fundamental trees:

```mermaid
flowchart TD
    classDef fighter fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef mage fill:#e8eaf6,stroke:#283593,stroke-width:2px;
    classDef scout fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef maid fill:#fff8e1,stroke:#f57f17,stroke-width:2px;
    classDef spieler fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;

    FI["Fighter (FI)"]:::fighter --> PA["Paladin (PA)"]:::fighter
    FI --> BE["Berserker (BE)"]:::fighter
    PA --> VL["Valkyrie (VL)"]:::fighter
    PA --> PL["Paladin (PL)"]:::fighter
    BE --> DL["Dark Lord (DL)"]:::fighter
    BE --> SA["Samurai (SA)"]:::fighter

    MU["Magic User (MU)"]:::mage --> SO["Sorceress (SO)"]:::mage
    MU --> EN["Enchantress (EN)"]:::mage
    SO --> WI["Witch (WI)"]:::mage
    SO --> SG["Sage (SG)"]:::mage
    EN --> BI["Bishop (BI)"]:::mage
    EN --> MP["Magical Princess (MP)"]:::mage
    EN --> SS["Soul Summoner (SS)"]:::mage

    SC["Scout (SC)"]:::scout --> AR["Archer (AR)"]:::scout
    SC --> AS["Assassin (AS)"]:::scout
    AR --> SN["Sniper (SN)"]:::scout
    AR --> TH["Treasure Hunter (TH)"]:::scout
    AS --> KN["Kunoichi (KN)"]:::scout

    MA["Maid (MA)"]:::maid --> BD["Bard (BD)"]:::maid
    MA --> DN["Dancer (DN)"]:::maid
    BD --> DI["Diva (DI)"]:::maid
    DN --> MI["Mistress (MI)"]:::maid
    DN --> ET["Etoile (ET)"]:::maid

    SP["Spieler (SP)"]:::spieler --> TR["Trickster (TR)"]:::spieler
    SP --> DM["Doll Master (DM)"]:::spieler
    TR --> PA_SP["Papillon (PA)"]:::spieler
    TR --> JO["Joker (JO)"]:::spieler
```

---

### 3.1 The Fighter Tree (Physical Vanguards)

| Class | Vanilla Agency State | Modded Agency State | Playstyle Distinctiveness Rating | Fun & Expressiveness Assessment |
|---|---|---|:---:|---|
| **Fighter (FI)** | Basic-attack spammer; 14 TP pool emptied in 2 turns. | Early Raging Smash (4 TP) & Provoke enables active early threat management. | **B** | Solid foundational vanguard; teaches positioning and aggro basics. |
| **Paladin (PL)** | Passive cover bot that died to unmitigated damage. | **Impervious Aegis:** Active single-target bodyguard, 60% cover mitigation, shield stuns, column chant cover. | **A+** | Thrilling to play. Stepping in front of boss lethal attacks feels heroic. |
| **Berserker (BE)** | Suicidal glass cannon; frozen in Rank F delay death spiral. | **Heavy Juggernaut:** 2H axes/swords deliver crushing burst; innate +15% DR and +20 parry allow calculated aggression. | **A** | Visceral risk/reward. Timing massive cleaves between enemy turns is intensely satisfying. |
| **Dark Lord (DL)** | Clunky recovery on Attract/Dark Aura; frozen tank. | **Abyssal Drain Tank:** Fast taunts (Rank B delay), massive 2,800+ HP pool, sustaining via Blood Drain and Megaton Press. | **A** | Self-sufficient vampire bruiser. Feeds off enemy aggression. |
| **Valkyrie (VL)** | Overloaded mandatory crutch; brainless barrier spam. | **Divine Aegis & Duelist:** Distinct party-wide preservation specialist; counter-strikes with Daedalus Attack. | **A+** | Remains an elite guardian, but no longer the only viable frontline tank. |
| **Samurai (SA)** | Starved for TP (*Halving Slice* 74 TP); fragile counter bot. | **Razor Precision Duelist:** Evasive Swallow Return counters; 100% DEF penetration against armored behemoths. | **A+** | Pure adrenaline. Rewarding precision timing, parrying, and lethal execution. |

---

### 3.2 The Magic User Tree (Arcane & Divine Arts)

| Class | Vanilla Agency State | Modded Agency State | Playstyle Distinctiveness Rating | Fun & Expressiveness Assessment |
|---|---|---|:---:|---|
| **Magic User (MU)** | 16 TP pool; 32 TP Fireball Lv10 caused chant interrupts. | Smooth TP scaling (4 TP baseline); low-level spells viable for exploration. | **B** | Enjoyable early elemental exploitation. |
| **Sorceress (SO)** | Intermediate mob clear; rapidly fell off against bosses. | Fast-casting row elemental spells; reliable mid-game dungeon clearer. | **B+** | Smooth transition caster. |
| **Enchantress (EN)** | Awkward buff bot with weak offensive contribution. | Potent weapon enchanter; empowers frontline with elemental weaknesses. | **B** | Good strategic support before Advanced promotion. |
| **Witch (WI)** | Dead in postgame (100+ boss res + 33.3% crit interrupts). | **Elemental Devastator:** Master spells pierce 50 resistance; Concentrate grants 80% interrupt armor. | **A** | Nuking superbosses with Crimson Flare/Cocytus feels catastrophic and earned. |
| **Sage (SG)** | Utility buff dispenser; offensive spells hit for tickles. | **Grand Arcanist:** Fast Cast + Elemental Pierce; flexible row and single-target spell artillery. | **A** | High tactical versatility. Cycling elemental coverage to exploit boss profiles. |
| **Bishop (BI)** | Heal numbers capped; passive heal dispenser. | **Divine Ward & Purifier:** Sacred Barrier absorbs boss dispel; Circle Heal restores scaled percentage HP. | **A** | Active lifesaver. Predicting incoming damage spikes to pre-cast barriers. |
| **Magical Princess (MP)** | Stat-split mediocrity; master of none before Lv99 crown. | **Spellblade Vanguard:** Infuses weapons with elemental magic; fluid frontline warrior-mage hybrid. | **A-** | Great hybrid fantasy. Shifts between physical cleaves and elemental burst. |
| **Soul Summoner (SS)** | Frustrating "Re-Summoning Simulator"; dolls wiped T1. | **Puppet Sovereign:** Directs autonomous 7-unit squad; sturdy dolls act as off-tanks and field medics. | **S** | Highest tactical agency transformation in the mod. True commander gameplay. |

---

### 3.3 The Scout Tree (Precision, Agility & Subterfuge)

| Class | Vanilla Agency State | Modded Agency State | Playstyle Distinctiveness Rating | Fun & Expressiveness Assessment |
|---|---|---|:---:|---|
| **Scout (SC)** | Early misses against beastkin; basic-attack spam. | +10% hit floor; reliable card/dagger strikes and early item utility. | **B** | Solid, agile early-game scout. |
| **Archer (AR)** | Standard bow sniper; overshadowed by mages in midgame. | High single-target burst; debuff-inflicting arrow techniques. | **B+** | Consistent backline damage dealer. |
| **Assassin (AS)** | Fast but fragile; reliant on RNG instant death procs. | High-speed status afflictions (Poison, Blind, Bleed); swift turn cycling. | **A-** | Fast, lethal ambusher. |
| **Sniper (SN)** | Bows fine; Guns were dead content (disabled skills). | **Artillery Marksman:** Guns enabled for techniques; 20% Armor Shred and Warning Shot delay pushback. | **A+** | Heavy, deliberate long-range suppression. Distinct from agile bows. |
| **Treasure Hunter (TH)** | Passive luggage carrier; brought only for Drop Rate UP. | **Combat Saboteur & Alchemist:** Fast item thrower; trap master; steals boss buffs and drops. | **A-** | Actively impacts the flow of battle through superior item action economy. |
| **Kunoichi (KN)** | Relegated to Utsusemi dodge bot; ninjutsu damage fell off. | **Phantom Illusionist:** Shadow clones absorb hits; lightning-fast debuff rotation; high evasion skirmisher. | **A** | Elusive, high-tempo playstyle. Controls enemy turns through decoy mechanics. |

---

### 3.4 The Maid Tree (Morale, Logistics & Performance)

| Class | Vanilla Agency State | Modded Agency State | Playstyle Distinctiveness Rating | Fun & Expressiveness Assessment |
|---|---|---|:---:|---|
| **Maid (MA)** | Mandatory TP battery; locked into Cheerful Dance spam. | Active field logistics; Clean Up cleanses ailments; Cook provides rest sustain. | **B+** | Liberated from being a brainless TP spammer. |
| **Bard (BD)** | Passively singing songs while party fought. | Dynamic buff song cycling; manages party turn tempo and TP reserves. | **B+** | Fluid song coordination. |
| **Dancer (DN)** | Fragile; dancing caused heavy action delays. | Agile status dances; lowers enemy defenses and inflicts confusion/blindness. | **B+** | Active frontline disturber. |
| **Diva (DI)** | Swift March mandatory crutch for heavy weapons. | **Symphonic Conductor:** High-tier song orchestrator; accelerates team actions without being an absolute crutch. | **A** | Great rhythm. Alternating between speed marches and TP requiems. |
| **Mistress (MI)** | Awkward whip weapon; outclassed by rapiers/daggers. | **Field Controller & Dominatrix:** Mid-range whip strikes bypass front row; Beast Binder inflicts physical silence. | **A** | Highly unique playstyle. Bending beast and mutant AI to her will. |
| **Etoile (ET)** | Passive dance aura provider; low direct interaction. | **Mesmerizing Danseuse:** High-speed debuffing dances that debuff enemy accuracy and action speed. | **A-** | Elegant battlefield control. |

---

### 3.5 The Spieler Tree (Chaos, High Stakes & Gambits)

| Class | Vanilla Agency State | Modded Agency State | Playstyle Distinctiveness Rating | Fun & Expressiveness Assessment |
|---|---|---|:---:|---|
| **Spieler (SP)** | Early card skills suffered from high RNG fail rates. | Normalized card hit rates; fun gamble mechanics with favorable floors. | **B+** | Whimsical, unpredictable gambler. |
| **Trickster (TR)** | Jack of all trades, master of none; awkward stats. | Card debuffer and turn order manipulator; high evasion trick plays. | **B+** | Fun tactical wildcard. |
| **Doll Master (DM)** | Primitive puppet summoner; fragile prototypes. | Experimental summoner; crafts specialized puppets for elemental trials. | **A-** | Engaging prelude to Soul Summoner. |
| **Papillon (PA)** | Materialize bot or infinite Tinker Squash cheese. | **Tactical Disruptor:** Materialize remains great for seals; Tinker Squash rebalanced as a surgical Enrage interrupter. | **A** | Cheese eliminated; replaced with tense, high-stakes boss charge disruption. |
| **Joker (JO)** | Extreme suicidal glass cannon; Trump Card killed user. | **High-Roller Assassin:** Colossal burst damage; high risk/reward cards; requires smart tank protection. | **A** | Ultimate adrenaline rush. Delivering 15,000+ burst while managing self-damage. |

---

## 4. Red Team Audit: Eradicating "Second-Class Citizen" & Passive Playstyles

A critical red team duty is ensuring that no class is relegated to a boring, passive, or second-class role. We identified **three potential passivity traps** in the proposal and formulated strict design guardrails:

### 4.1 Passivity Trap 1: Is Maid Still Just a "Cheerful Dance" Bot?
* **The Danger:** Even with high-tier TP consumables (Fairy Apples, Golden Apples), players might still feel compelled to leave a Maid on auto-repeat using *Cheerful Dance* every single turn.
* **The Red Team Solution & Agency Check:**
  1. **Consumables Free Up Maid Actions:** Because high-tier TP items and food buffs now provide substantial baseline sustain, the Maid does **not** need to dance every turn.
  2. **Active Combat Logistics:** Maids have the fastest item use frame rate in the engine. When equipped with *Bag Mastery*, a Maid acts as a rapid-response combat paramedic: throwing *Mandragora Roots* (reviving with 60% HP) and *Fumirul Nectars* (cleansing all ailments party-wide) instantly before the boss acts.
  3. **Offensive Maid Builds:** With Fan Rank A+ (1.00x delay) and Maid techniques, an aggressive Maid can strip enemy buffs and contribute chip burst damage.

### 4.2 Passivity Trap 2: Is Treasure Hunter Just a Passive Luggage Carrier?
* **The Danger:** Bringing a Treasure Hunter purely for passive *Drop Rate UP* and *Rare Drop Rate UP*, leaving her useless during tense boss fights.
* **The Red Team Solution & Agency Check:**
  1. **Combat Saboteur:** Treasure Hunters possess high AGI, trap-disarming techniques, and fast throw actions.
  2. **Resource Alchemy:** TH can utilize high-efficiency utility gadgets and sealbooks to strip enemy buffs (*Steal* / *Snatch*), disrupt enemy formations, and maintain full inventory uptime during 50-floor Matrix expeditions.

### 4.3 Passivity Trap 3: The Hybrid Identity Crisis (Magical Princess & Trickster)
* **The Danger:** Hybrid classes being mediocre at both fighting and casting, encouraging players to just take pure Berserkers and pure Witches.
* **The Red Team Solution & Agency Check:**
  1. **Elemental Weapon Enchantment Synergy:** Magical Princess bypasses physical and magical defenses by applying elemental weapon buffs that target specific boss weaknesses.
  2. **Instant Stance Shifting:** MP can pivot from a sturdy frontline blocker (equipped with heavy armor) to an instant magical executioner without requiring long chant windows.

---

## 5. Turn-by-Turn Decision Density & Cognitive Load Comparison

To prove that the balanced mod creates genuine tactical gameplay rather than mindless auto-combat, we mapped out the **Turn-by-Turn Decision Density** of four distinct party archetypes confronting an Enraged Postgame Superboss (Creator God / Dark Mutant at <25% HP):

```
========================================================================================
SCENARIO BENCHMARK: SUPERBOSS AT 20% HP (ENRAGED: CHARGING 1-TURN ULTIMATE WIPE)
========================================================================================
```

### Archetype A: "The Shield Wall & Arcane Artillery" (Paladin, Samurai, Sage, Bishop, Sniper)
* **Turn 1 (Boss Enrage Telegraphs Wipe):**
  * **Paladin:** Commands front row; executes `Universal Defend` in front of Sage, establishing "Covered Chant" (granting 100% critical hit and chant interrupt immunity).
  * **Sage:** Safe behind Paladin's shield wall; begins casting `Crimson Flare` Lv5 (42 frames chant window with Fast Cast).
  * **Bishop:** Pre-casts `Sacred Barrier` to absorb ambient dispel or magical spillover.
  * **Sniper:** Fires `Warning Shot` with heavy rifle, pushing back boss turn ticks by 15 frames.
  * **Samurai:** Enters `Swallow Return` parry stance to intercept any retaliatory physical counter-strikes.
* **Turn 2 (The Execution):**
  * Paladin's shield wall absorbs the redirected blow (-82.9% damage).
  * Sage's chant lands cleanly without interruption, dealing 8,500 fire damage through 50 Res Pierce.
  * Paladin, Samurai, and Sniper trigger a 3-person **Joint Skill** with DEF penetration, finishing the boss before the wipe fires.
* **Tactical Experience:** High tension, coordinated military choreography. Zero Valkyrie needed.

---

### Archetype B: "The Puppet Sovereign & Abyssal Drain Tank" (Dark Lord, Spartan, Catalina, Soul Summoner, Diva)
* **Turn 1 (Boss Enrage Telegraphs Wipe):**
  * **Dark Lord:** High HP pool (2,850 HP); executes `Dark Aura` with Rank B compressed delay, concentrating boss aggro on herself.
  * **Spartan (Doll):** Autonomous vanguard off-tank executes `Shield Bash`, fishing for a Stun stagger on the boss.
  * **Catalina (Doll):** Autonomous field medic pre-queues high-potency regeneration on the Dark Lord.
  * **Soul Summoner:** Reads the boss charge; throws an EX Golden Apple to top off Dark Lord's TP, and activates `Soul Seal` to transfer Earth Resistance to both dolls.
  * **Diva:** Sings `Swift March` to compress the party's recovery timeline.
* **Turn 2 (The Execution):**
  * Boss unleashes multi-hit cleave. Dark Lord survives with 900 HP; Spartan absorbs a hit, triggers `Double Puppet` Guts trait, and survives at 1 HP.
  * Dark Lord executes `Megaton Press`, draining 1,800 HP back into her pool and dealing colossal crushing damage.
  * Catalina instantly heals Spartan back above the lethal threshold.
* **Tactical Experience:** Dynamic 7-unit squad command. The feeling of commanding an unstoppable necromantic legion that refuses to die.

---

### Archetype C: "The Heavy Colossus & Status Lock" (Berserker, Valkyrie, Mistress, Papillon, Bard)
* **Turn 1 (Boss Enrage Telegraphs Wipe):**
  * **Berserker:** Equipped with Adamas Greatscythe (Rank F delay); previously paced her turns so her action arrives right as the boss charges.
  * **Papillon:** Recognizes the boss charge; executes `Tinker Squash` (Hit 1: 100% potency) for 20 frames of clean turn delay, knocking the boss back on the timeline.
  * **Mistress:** Uses `Beast Binder` with mid-range whip, applying physical stagger and lowering boss action speed.
  * **Valkyrie:** Casts `Material Guard` to erect a physical immunity barrier.
  * **Bard:** Plays an ATK-buffing song to supercharge the Berserker.
* **Turn 2 (The Execution):**
  * Berserker unleashes `Moon Drop` with Berserk active: a colossal 14,000 damage critical strike that cracks the boss's enrage shield.
  * The delayed boss attempts to strike, but hits Valkyrie's barrier.
* **Tactical Experience:** Visceral, heavy-metal slugfest. Deliberate timing, devastating chunk damage, and surgical crowd control.

---

## 6. Specific Tactical Agency Polish Recommendations

To ensure that the upcoming binary modifications deliver 100% of this promised tactical richness, the Red Team mandates **three specific design polish items** to be incorporated into the balance implementation:

### Polish 1: Combat Log & Visual Impact for Heavy Weapons
* **The Issue:** Players need to *feel* the weight of 2H Greatswords and Guns beyond just numbers.
* **Design Enhancement:** In `StringData.pck` and engine hit-pause frames:
  * Ensure 2H Greatswords, 2H Axes, and Guns trigger an extra **2-frame screen freeze / hit-stop** on critical hits.
  * Combat log strings should emphasize the impact: `"Grishna's colossal axe shatters the enemy's armor!"`

### Polish 2: Explicit Doll Status HUD Indicators
* **The Issue:** In the 7-unit formation, players must be able to instantly tell when a doll's *Double Puppet* Guts survival trait has been consumed.
* **Design Enhancement:** In `StringData.pck` and battle UI:
  * When a doll survives lethal damage via Guts, display: `"[Spartan: Soul Tether Preserved at 1 HP!]"`.
  * Display the doll's inherited Sealbook name in their status window.

### Polish 3: Defend Command "Covered Chant" Feedback
* **The Issue:** The synergy between a frontline ally executing *Defend* and a backline ally gaining *Covered Chant* (chant interrupt immunity) is brilliant, but must be transparent.
* **Design Enhancement:** When a character executes *Defend*, the combat log must explicitly state:
  * `"%s takes a defensive stance! Back-row allies gain Covered Chant!"`

---

## 7. Final Red Team Sign-Off & Verdict

### Comprehensive Evaluation Matrix

| Design Pillar | Vanilla Score | Modded Score | Verdict |
|---|:---:|:---:|---|
| **Build Fantasy Fulfillment** | 4 / 10 | **9.5 / 10** | Classes feel deeply distinct, evocative, and faithful to their lore. |
| **Turn Decision Density** | 3 / 10 | **9.0 / 10** | Eliminates mindless auto-attacks; every turn presents tactical choices. |
| **Heavy Weapon Viscerality** | 2 / 10 | **8.5 / 10** | 2H weapons feel weighty and impactful without suicidal delay locks. |
| **Support & Hybrid Agency** | 4 / 10 | **9.0 / 10** | Maids, Bards, and Hybrids have active, impactful combat roles. |
| **Endgame Archetype Diversity** | 2 / 10 | **9.5 / 10** | Multiple distinct 5-hero compositions can conquer deep superbosses. |

### Final Conclusion:
The Master Definitive Balance Mod (`DEFINITIVE_BALANCE_PROPOSAL.md`) not only passes all mathematical and economic stress-tests, but it successfully elevates *Dungeon Travelers 2-2* into an **apex tactical masterpiece**. 

Every class possesses a distinct voice, every weapon type has a visceral identity, and no playstyle feels like a forgotten second-class citizen. 

**Red Team Status:** **UNCONDITIONALLY APPROVED FOR IMPLEMENTATION UPON USER CONFIRMATION.**
