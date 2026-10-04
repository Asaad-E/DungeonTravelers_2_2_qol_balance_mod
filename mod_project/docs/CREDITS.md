# Dungeon Travelers 2-2: Definitive Edition & Mechanics Transparency Suite
## Special Thanks & Community Credits (謝辞・クレジット)

> *"This project exists thanks to the passionate research, mathematical rigor, and tireless dedication of the Japanese Dungeon Travelers community."*

---

### 1. The Japanese Strategy & Theorycrafting Community (日本攻略コミュニティ)

This definitive balance and mechanics transparency overhaul would not have been possible without the exhaustive reverse-engineering, damage formula breakdowns, and combat logs documented by the Japanese DRPG playerbase across years of post-game dedication.

#### 1.1 2ch / 5ch Strategy & Discussion Threads (5ちゃんねる 攻略・本スレ)
* **【DT2-2】ダンジョントラベラーズ2-2 本スレ (Parts 1–65)**:
  * For cataloging every boss attack pattern, turn order quirk, and class promotion dilemma.
  * For the legendary debates on post-game superboss viability (*"ヴァルキリー＋メイド抜きのパーティ構築"*), which inspired our tank parity and support independence overhauls.
  * For exposing the extreme action delay penalties on 2-handed weapons (*"両手武器絶望論"*), directly driving our delay compression curve in `WeaponRankData.pck`.
* **【DT2-2】装備強化・エンチャント厳選スレ (Equipment & Forging Research)**:
  * For documenting the flat $+2 \sim +4$ forging limitation and demonstrating why percentage-based scaling was essential for deep Matrix relevancy.
  * For analyzing duplicate affix stacking mechanics and proposing diverse affix synergy rules.
* **【DT2-2】質問・初心者救済スレ (Q&A and Newcomer Help)**:
  * For identifying the chronic early-game TP starvation and the widespread "Trap Skill Level" pitfalls (罠スキル) that punished players for investing skill points.

#### 1.2 The Official DT2-2 Japanese Strategy Wiki (攻略・検証 Wiki)
* **Atwiki Editors & Contributors (`dungeontravelers2-2.atwiki.jp`)**:
  * For maintaining the definitive database of monster parameters, drop rates, weapon speed ranks, skill frame data, and grand sealbook auras.
  * For reverse-engineering the exact mathematical formulas behind:
    * The $33.3\%$ critical hit chant interruption check.
    * Elemental resistance scaling ($1.0 - \text{Resist} \times 0.005$).
    * Trap damage calculations and evasion thresholds.
    * The Level Reset stat gap thresholds ($\text{Gap} \ge 59$).

#### 1.3 Veteran DRPG Bloggers & Post-Game Clear Researchers (先人たちのブログ・記録)
* **DRPG深層考察 (DRPG Deep Mechanics Analysis)**:
  * For the definitive mathematical proof of why chanting spellcasters collapsed in post-game superboss battles, which directly inspired our 50-point elemental penetration and chant frame compression.
* **マトリックス深層踏破録 (The Matrix Depths Clearance Journals)**:
  * For recording the step counts of 50-floor Matrix explorations and demonstrating why 300-step food buffs felt frustratingly brief, leading to our 900-step persistence extension.
* **Soul Summoner Research Labs**:
  * For analyzing doll durability curves and advocating for Guts traits and stat inheritance from equipped sealbooks.

---

### 2. Core Development & Mod Suite Principles

* **AQUAPLUS & Sting Engine Architects**:
  * For creating one of the most mechanically sophisticated, challenging, and beloved dungeon crawlers in gaming history.
* **The Localization & Modding Community**:
  * For preserving 100% of the game's original soul, charm, character banter, and comedy (umami MSG, Souffle's ticking pipe bomb, and Euthys's lectures) while illuminating every hidden mechanic for players worldwide.

---

*“To every traveler who ever dared to venture into the depths of the Matrix—thank you.”*
