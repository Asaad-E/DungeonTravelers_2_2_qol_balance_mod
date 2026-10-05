# Dungeon Travelers 2-2: Skill Display Specification & Design Philosophy

**Document Status:** Official Project Standard & Design Directive  
**Target Platform:** Dungeon Travelers 2-2 (PC / Steam EN)  
**Applicability:** Data tables (`skills.xlsx`, `qol_skill_text.xlsx`), injection scripts (`pck_handler.py`, `apply_mod.py`), and multi-agent development pipelines.

---

## 1. User Feedback, Core Complaints & Design Mandates

This standard was forged directly through iterative playtesting feedback, player critiques, and explicit directives provided by the user. Any future modification or automated generation script **must strictly comply** with these user-defined mandates:

### Mandate A: Elimination of "Spreadsheet Friction" & Verbose Formulas
* **The User's Complaint (Step 186):**
  > *"I don't like it, it's way too verbose. Why are you showing me confusing ranges? I just want to know what it does, what damage it deals, and what cost it has right now and next level. You have the numbers in the game, why make it harder?"*
* **The Design Rule:**
  * **Strictly Prohibited:** Statistical formulas such as `(avg +3.33%/Lv)`, aggregated summaries, or mathematical jargon.
  * **Required:** Players in the middle of a dungeon crawl must not be forced to do mental algebra or play with a calculator. Information must be readable **at a glance in under 0.5 seconds**.

---

### Mandate B: Pure In-Universe Nomenclature (Line 1 Untouched)
* **The User's Directive (Step 197):**
  > *"When I say in-game, I don't mean a generic RPG style. Use the exact nomenclature and descriptions that the game uses normally. Nothing outside."*
* **The Design Rule:**
  * **Line 1 belongs 100% to Aquaplus/Sting.** The original English flavor text and descriptive prose must never be replaced, rewritten with modder jargon, or trimmed.
  * Mechanical data must be neatly categorized on Lines 2 and 3 without interfering with Line 1.

---

### Mandate C: Solving the Engine's Static String Limitation
* **The Technical Dilemma (Steps 208–210):**
  * The *Dungeon Travelers 2-2* engine reads a **single static string** per skill entry. It cannot dynamically render separate text based on the character's current skill level.
  * If a tooltip only showed Level 1, a player at Level 8 would have no clue what their skill does. If it only showed Max Level, a rookie player would have no idea what they currently possess.
* **The Approved Solution:**
  * Direct sequential progression using arrows (`->`). The player immediately sees their current level's value, the next level's value, and the final cap.

---

### Mandate D: Rejection of Automated "Average" Compression
* **The User's Complaint on Automated Scripts (`qol_skill_text.xlsx`):**
  > Automated scripts attempting to adhere to character limits took shortcuts by reintroducing compressed statistical formulas: e.g. `ATK: 80% -> 110% (avg +3.33%/Lv, L1-10)`.
* **The Directive:**
  * The user explicitly rejected this format. If a 10-level skill cannot fit all 10 numbers due to wide values, it must use clean, explicit step progression (e.g., `ATK: 125% (+8%/Lv) -> 200% (L10 Max)`), **never** fractional averages like `(avg +3.33%/Lv)`.

---

## 2. Hard Engine Constraints (Non-Negotiable)

1. **Physical Line Limit:** **Maximum 3 lines** per skill box.
   * Line 1: Original Vanilla Description.
   * Line 2: Primary Effect, Scaling & Values across levels.
   * Line 3: Costs (TP), Durations (Turns), and Action Delay / Speed.
2. **Character Width Limit:** **Maximum 85 characters per line** (calibrated to the English UI dialog box width to prevent text overflow or word-wrapping).
3. **Font Encoding Safety:** **ZERO tildes (`~`)**.
   * The DT2-2 English font engine uses reserved bytes for special symbols; literal tildes cause severe font corruption and broken glyphs. Use arrows (`->`) or hyphens (`-`).
4. **Absolute Binary Grounding (Anti-Placebo):**
   * Every number must originate from verified bytes in the game binary (`TechniqueSkillData.pck`, `MagicSkillData.pck`, `PassiveSkillData.pck`). Never invent mechanics that the engine does not support (e.g. fake "elemental resistance penetration" or "Defend crit immunity").

---

## 3. Concrete Line-by-Line Formatting Specification

### Layout Blueprint

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Line 1] Original Vanilla Description (Untouched from game binary)                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Line 2] Effect: [L1 Value] -> [L2 Value] -> [L3 Value] -> ... -> [Max Value]          │
│ [Line 3] Turns: [L1] -> [Max] | TP Cost: [L1] -> [L2] -> ... | Speed: [Value]          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Progression Formatting Rules

#### 1. Five-Level Skills (Buffs, Debuffs, Utility Techniques)
Since 5 levels fit comfortably within 85 characters, **all 5 values must be written explicitly**:
* `ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)`
* `Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13`

#### 2. Ten-Level Skills (Primary Physical Techniques & Magic Spells)
* **Standard Case (All 10 values fit within 85 chars):** Write all 10 values explicitly:
  * `TP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28`
  * `Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520 (L10)`
* **Tight Case (Large 3-digit values that exceed 85 chars):** Write starting base, exact step, and max cap:
  * **CORRECT:** `ATK: 125% (+8%/Lv) -> 200% (L10 Max) | Hit Rate: +20% (+2%/Lv)`
  * **STRICTLY PROHIBITED:** `ATK: 125% -> 200% (avg +8.33%/Lv)`

---

## 4. Approved Reference Archetypes (The Approved Mockups)

These mockups were rendered on real game screenshots and formally approved by the user in Step 231:

### 1. ⚔️ Fighter: `War Cry` (5-Level Party Buff)
```text
Raise the party's ATK.
ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13
```
* **At a glance:** Level 1 gives +8% ATK for 4 turns at 5 TP. Level 2 gives +10% ATK for 5 turns at 7 TP. Clear, instant, zero cognitive load.

### 2. ⚔️ Fighter: `Raging Smash` (10-Level Physical Burst)
```text
Short-range skill. Powerful strike to one enemy.
ATK: 125% -> 133 -> 141 -> 150 -> 158 -> 166 -> 175 -> 183 -> 191 -> 200%
TP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28 | Speed: 0.8x -> 0.9x
```
* **At a glance:** Every level's exact damage multiplier and TP cost is immediately visible.

### 3. 🔮 Magic User: `Fireball` (10-Level Elemental Spell)
```text
Deal fire damage to one enemy.
Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520 (L10)
TP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32 (Max)
```
* **At a glance:** Real spell power straight from the binary structs, showing exact non-linear scaling.

### 4. 🏹 Scout: `Evade` (5-Level Evasion Buff)
```text
Increase own physical evasion rate.
EVA: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 4 -> 6 -> 8 -> 10 -> 12
```

### 5. ☕ Maid: `First Aid` (Percentage Healing Technique)
```text
Heal one ally's HP.
Heal: 12% Max HP -> 15% -> 18% -> 21% -> 25% (L1-5 Max)
TP Cost: 2 -> 4 -> 6 -> 8 -> 10 | Affected by Maid Mastery
```

### 6. 🎲 Spieler: `Coffee Break` (Self-Sustain & Fast Recovery)
```text
Take a break to heal own HP and raise Pep. Fast turn recovery.
Heal: 20% Max HP -> 25% -> 30% -> 35% -> 40% (L1-5 Max)
TP Cost: 6 -> 7 -> 8 -> 9 -> 10 | Action delay: 1.50x
```

### 7. 🔵 Passive Skill: `Sword Mastery` (10-Level Passive ATK)
```text
Increases equipped sword base ATK.
ATK: +3% (L1) -> +5% -> +7% -> +9% -> +11% -> +12% -> +13% -> +14% -> +15% (L10)
```

---

## 5. Direct Comparison: User-Approved Standard vs. Script-Generated Text

| Dimension | User-Approved Standard (This Document) | Automated Script Format (`qol_skill_text.xlsx`) |
| :--- | :--- | :--- |
| **Non-Linear Values** | Sequential progression: `70 -> 105 -> 140...` | Statistical compression: `avg +3.33%/Lv` |
| **Cognitive Load** | Zero. Player looks and knows immediately. | High. Player has to calculate what each level does. |
| **Line 1 Handling** | Untouched vanilla text. | Untouched vanilla text. |
| **Line Separators** | Clean arrow transitions (`->`) with breathing room. | Dense vertical pipes (`\|`) squeezed together. |
| **Screen Limits** | Strictly verified $\le 85$ characters. | Strictly verified $\le 85$ characters. |
| **Encoding Safety** | Zero tildes (`~`). | Zero tildes (`~`). |
| **Player Verdict** | **Approved.** | **Rejected (violates Step 186 directive).** |

---

## 6. Implementation Mandate for Future Modding

1. **For QoL / Transparency Builds:**
   * Numbers must be extracted directly from the verified vanilla binary (`vanilla_source_of_truth.xlsx`).
   * Tooltip text formatting must follow **only the approved sequential arrow standard** defined in this document.
2. **For Balance Builds:**
   * Binary parameters (struct arrays for TP, power, chant delay) must be modified in the `.pck` files first.
   * Tooltip descriptions must then be generated to reflect the exact newly patched binary numbers.
   * No mechanical claims may ever be published without matching executable/binary code backing them up.

---

## 7. Amendment of 2026-10-04: line 1 in battle

Decided by the user after seeing the battle bar, which shows line 1 alone and without the skill level. It replaces "Line 1 untouched" for techniques and spells; everything else in this document stands.

1. Line 1 keeps the game's sentence and gains only the main points:
   * **Damage as one word**, placed inside the sentence ("Deal minor bash damage to one enemy"): Negligible (only below 80%), Minor, Moderate, Major, Severe. The word is chosen by the average of the real values over the levels. Magic uses the same words. A value beyond the scale is an exception and gets its own word (the game's "tremendous").
   * **Ailment chance as a figure**: the value itself when it never changes ("May stun (25%)"), the starting value and a plus when it changes little ("May stun (30%+)"), first and last level when it changes more ("May poison (20-50%)"). The tilde of "~30%+" is not available in the game font.
2. No other figure goes in line 1: the level is not visible in battle, so a per-level list cannot be read there.
3. When the exact value is shown, the vague word next to it is removed ("(medium) (+250 HP)" is wrong; "(+250)" is right).
4. The words of the game are kept (Enmity, resistance); no concept is renamed.
5. Everything a screen shows must give the precise data, without removing the jokes or the in-game prose.

Bounds of the scale and the rules of placement: `tools/magnitude_words.py` and section 6.2 of `dungeontravelers2-2.md`.

---

## 8. Amendment of 2026-10-04, second round

Answers of the user to the open questions of the roadmap. They extend section 7.

1. **A value that does not change with the level is always shown** in the box ("Speed decrease: 10%").
2. **Line 1 says the value for every skill**, not only damage and ailments: buffs, heals and passives too ("Raise the party's ATK (8%+)."). Same three forms: the value when it never changes, the starting value and a plus when it changes little, first and last level when it changes more. The level-by-level list stays in the box.
3. **A chance of 100% is written as 100%.**
4. **When a text and the data disagree, the data wins.** The sentence is kept as it is and only the wrong figure or word is replaced.
5. **Items: the original text plus the data in parentheses** ("Eat, Skill, Love. (SP +3)").
6. The bounds of the magic scale are confirmed: below 80 negligible, 80-249 minor, 250-399 moderate, 400-499 major, 500-699 severe, above that the exception word.
