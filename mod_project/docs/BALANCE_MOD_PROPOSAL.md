# Dungeon Travelers 2-2: Japanese Community Research & Balance Mod Proposal

**Author:** Senior Strategic Game Mechanics & Mod Architect  
**Scope:** Deep-dive analysis of Japanese community meta (2ch/5ch, Atwiki, Gamerch, JP veteran blogs) and concrete, data-grounded balance proposal built on top of the Transparency Mod suite.

---

## Part 1: Japanese Community & Wiki Meta Investigation

Dungeon Travelers 2-2 is widely praised in Japan as one of the most mechanically demanding and deeply rewarding DRPGs ever created. However, exhaustive reviews of 2ch/5ch strategy threads, the dedicated Atwiki (`dungeontravelers2-2.atwiki.jp`), and endgame veteran write-ups highlight several persistent structural pain points and class balance discrepancies in the post-game (The Matrix, the Gods, and EX Dungeons).

### 1. The "Action Speed / Weapon Delay Monopoly" (速度・ディレイ格差)
* **The Problem:** In DT2-2, turn speed and action recovery delay dictate combat survival.
  * Fast weapon types (Daggers, Rapiers, Shortswords, Fans with Rank A+/A) have delay multipliers of $1.0\times$ to $1.2\times$.
  * Heavy weapon types (2-Handed Swords, 2-Handed Axes, Guns with Rank E/F) have delay multipliers of $2.4\times$ to $2.9\times$.
* **Community Consensus:** Because post-game bosses possess massive AGI, high-delay weapon wielders (Berserkers, 2H Dark Lords, Gun Snipers) act almost **three times slower** and forfeit a shield slot. A single high-delay swing can leave a character paralyzed on the turn bar for 2 to 3 boss attack cycles, frequently resulting in death before their next turn.
* **The Result:** Unless babysat by a Diva casting *Swift March* (疾風迅雷マーチ) or an Etoile dancing, heavy weapons are widely regarded as a liability in deep endgame, forcing the meta toward light, high-speed weapons.

### 2. Magic Falloff & Chant Interruption in Postgame (終盤・裏ダンジョンの魔法不遇)
* **The Problem:** Elemental magic dominates the early and mid-game for clearing mob encounters, but hits a severe mechanical wall in postgame bosses.
  * Deep-postgame bosses possess high innate Elemental Resistances ($\ge 100$), reducing magical damage by 50% or more.
  * Top-tier spells (Crimson Flare, Cocytus, Muon Plasma, Gaia Crush, Tempest) have long chant delays. Under the game's **33.3% critical interrupt check**, fast multi-hit boss attacks frequently interrupt chanting spellcasters, wasting their turn and TP completely.
* **Community Consensus:** In contrast, physical burst classes (Dark Lord with *Power Charge* + *Megaton Press*, Samurai with *Hissatsu*, Sniper with *Armor Pierce*) execute their skills **instantly** without chant windows, benefit from physical ATK stacking, and bypass boss defenses. As a result, pure damage mages (Witch, Sage) are frequently dropped or relegated to utility/buff dispensers in deep post-game.

### 3. The "Trap Skill Level" Dilemma (高レベルスキルの燃費悪化)
* **The Problem:** For many techniques and spells, leveling a skill up from Lv1 to Lv10 yields linear power increases (+5% to +10% per level), but scales TP costs and chant/recovery delays steeply.
* **Community Consensus:** JP strategy guides explicitly warn players about "Trap Levels" (罠レベル): keeping skills at Lv1–3 offers vastly superior damage-per-TP efficiency and faster turn cycling. Leveling skills to max Lv10 is often mathematically detrimental unless a dedicated high-tier Maid is continuously battery-feeding TP every round.

### 4. Mandatory Valkyrie Syndrome (ヴァルキリー一強・編成固定化)
* **The Problem:** Valkyrie is so defensively overloaded (*Cover*, *Parry*, *Daedalus Attack*, *Holy Shield*, and the game-defining *Circle Protection* that grants party damage immunity) that high-difficulty postgame without a Valkyrie feels exponentially more brutal.
* **Community Consensus:** While Valkyrie is praised for making tough content beatable, alternative tank archetypes—such as Paladin (pure shield wall) or Dark Lord (*Attract* / *Dark Aura* bruiser)—struggle to compete because they lack *Circle Protection*'s party wipe mitigation and *Parry*'s physical negation.

### 5. Fragility of Soul Summoner Dolls (ドールの即死・維持難度)
* **The Problem:** Soul Summoner dolls provide fantastic utility, but their defensive scaling does not sufficiently keep pace with post-game boss AoE damage. Dolls frequently get one-shot before acting, forcing the summoner into a continuous, turn-wasting re-summoning loop.

---

## Part 2: Concrete, Data-Grounded Balance Mod Proposal

Building directly on top of the Transparency Mod (Pillar A), this proposed Balance Mod (Pillar B) addresses the JP community's pain points using raw binary adjustments in existing data structures, without breaking the game's identity or challenge.

### Proposal 1: Heavy Weapon Delay Curve Compression (`WeaponRankData.pck`)
* **Mechanism:** In `WeaponRankData.pck`, the bottom 5 delay multipliers are excessively punishing:
  * *Vanilla:* `A+ 1.0x, A 1.2x, B+ 1.4x, B 1.6x, C+ 1.8x, C 2.0x, D+ 2.2x, D 2.4x, E+ 2.6x, E 2.7x, F+ 2.8x, F 2.9x`
  * *Proposed Balance:* Soften Rank D to F:
    `A+ 1.0x, A 1.2x, B+ 1.4x, B 1.6x, C+ 1.8x, C 1.9x, D+ 2.0x, D 2.1x, E+ 2.2x, E 2.3x, F+ 2.35x, F 2.4x`
* **Impact:** 2-Handed Swords, 2-Handed Axes, and Guns become viable in high-tier post-game without forcing a mandatory Diva in every team, while light weapons (daggers, rapiers) retain their speed advantage ($1.0\times$ vs $2.4\times$).

### Proposal 2: High-Tier Spell Chant & Power Scaling (`MagicSkillData.pck`)
* **Mechanism:** Adjust top-tier elemental spells (Crimson Flare, Cocytus, Muon Plasma, Tempest, Gaia Crush) in `MagicSkillData.pck`:
  1. Reduce chant delay frames by **15%–20%**, narrowing the vulnerability window against fast bosses.
  2. Increase base magic power at Lv8–10 (e.g., from 1,300 to 1,500) to ensure high-investment magic rewards the player against post-game bosses.
* **Impact:** Mages regain competitive endgame burst damage without invalidating physical DPS.

### Proposal 3: High-Level Skill TP Efficiency Smoothing (`TechniqueSkillData.pck` & `MagicSkillData.pck`)
* **Mechanism:** Cap the steep TP growth curve at skill levels 7–10 by 15%–25% across key active skills.
* **Impact:** Eliminates the "Trap Skill Level" meta; investing SP to reach Level 10 mastery feels rewarding and usable in standard dungeon loops rather than penalizing.

### Proposal 4: Alternative Tank Enhancements (`ClassData.pck` & `PassiveSkillData.pck`)
* **Paladin:** Increase *Holy Shield* proc rate by +10% and bump Paladin base DEF growth from 1.35x to 1.50x. Gives Paladins the unrivaled passive physical reduction wall they are meant to be.
* **Dark Lord:** Reduce turn delay on *Attract* and *Dark Aura* by 20%, allowing DL tanks to draw aggro without losing turns.
* **Impact:** Gives players genuine frontline choices besides the ubiquitous Valkyrie.

### Proposal 5: Soul Summoner Doll Durability Floor (`ClassData.pck`)
* **Mechanism:** Increase doll baseline HP scaling by +25% and magic resistance by +20.
* **Impact:** Dolls survive stray boss AoE hits, allowing Soul Summoners to participate tactically rather than being locked in re-summon loops.

---

## Part 3: Architecture & Togglable Implementation Plan

Following `docs_example/philosophy.md`, this Balance Mod will be built as an **independent, optional layer**:

1. **Configurable Toggle:** A JSON configuration file (`mod_project/config/balance_mod.json`) with individual feature flags:
   ```json
   {
     "enable_balance_mod": true,
     "heavy_weapon_delay_compression": true,
     "magic_chant_and_power_buff": true,
     "skill_tp_efficiency_smoothing": true,
     "tank_diversity_buffs": true,
     "doll_durability_scaling": true
   }
   ```
2. **Non-Destructive Compilation:**
   * If `enable_balance_mod` is `false`, `apply_mod.py` builds the pure 100% vanilla mechanics Transparency Mod.
   * If `true`, the balance adjustments are injected into the parameter tables, and the UI text automatically reflects the newly tuned numbers.
3. **Audit Suite Integration:** `audit_tool.py` will validate both Vanilla and Balanced modes with 0 errors.

---

## Conclusion
This proposal directly honors the player feedback documented across Japanese forums while staying true to the game's core dungeon-crawling challenge. It provides real build diversity and smooths out artificial bottlenecks without making the game trivially easy.
