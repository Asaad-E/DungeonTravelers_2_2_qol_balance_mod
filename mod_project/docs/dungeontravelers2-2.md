# Dungeon Travelers 2-2: Mechanics, Binary Architecture & Source of Truth

Reference for agents and modders working on *Dungeon Travelers 2-2: The Maiden of Darkness and the Book of Origins* (PC / Aquaplus-Sting Engine).  
Confidence tags: **[verified]** confirmed by bit-exact binary roundtrip, audit tool, or in-engine test; **[inferred]** deduced from reverse-engineered structures; **[untested]** not directly tested in execution.

---

## 1. Deliverables & Mod Components

| Component / Artifact | Built By | Target File / Destination | Content & Purpose |
|---|---|---|---|
| **Combat Skills** | `apply_mod.py` | `Data/ENG/Parameter/*SkillData.pck` | 218 skills (Tech, Magic, Passive, Unique with Crown EX) with exact Lv1–10 scaling, chants, and recovery. |
| **Consumable Items** | `apply_mod.py` | `Data/ENG/Parameter/ItemData.pck` | 388 items preserving 100% original humor/flavor + concise `(+data)` (HP/TP, status cures, SP). |
| **Equipment Catalog** | `apply_mod.py` | `Data/ENG/Parameter/EquipmentData.pck` | 551 weapons, armors, and accessories with Range (`Short`/`Mid`/`Long`), Delay Multiplier ($A+$ to $F$), Slots, and native enchants. |
| **Grand Sealbooks** | `apply_mod.py` | `Data/ENG/Parameter/SealScrollData.pck` | 374 mutant sealbooks displaying party auras, drop rate bonuses, and summon scaling formulas. |
| **Joint Skills** | `apply_mod.py` | `Data/ENG/Parameter/JoinSkillData.pck` | 52 multi-turn combos with initiator/participant classes, TP/Pep costs, and damage formulas. |
| **Enchantments** | `apply_mod.py` | `Data/ENG/Parameter/EnchantData.pck` | 247 forge affixes with exact stat boosts, elemental resistances, and forge limits. |
| **Party Skills** | `apply_mod.py` | `Data/ENG/Parameter/PartySkillData.pck` | 20 party compositions with exact passive stats, trigger rates, and award scaling. |
| **Buffet Meals** | `apply_mod.py` | `Data/ENG/Parameter/FoodMenuData.pck` | 16 cafeteria meals with exact step durations and stat boosts (flavor strings 100% preserved). |
| **Enemy/Summon Attacks** | `apply_mod.py` | `Data/ENG/Parameter/EnemyAttackData.pck` | 2,375 attack techniques with elemental attributes, status infliction rates, and damage types. |
| **Player Classes** | `apply_mod.py` | `Data/ENG/Parameter/ClassData.pck` | 32 classes with stat multipliers, proficiencies, combat archetypes, and promotion thresholds. |
| **Combat UI Commands** | `apply_mod.py` | `Data/ENG/Parameter/StringData.pck` | IDs 199–204 (Defend 50% dmg/0.67x delay/crit & interrupt immune, Escape AGI checks, Joint Combos, etc.). |
| **Dungeon Traps** | `apply_mod.py` | `Data/ENG/Parameter/TrapData.pck` | 12 traps displaying lethality and elemental resistance nullification (e.g. Killer Floor 50% KO, 100 Earth Res Null). |
| **Trophies & Milestones** | `apply_mod.py` | `Data/ENG/Parameter/TrophyData.pck` | 50 trophies preserving original jokes + exact numeric goals `(Escape 100 battles)` for Party Skill boosts. |
| **In-Game Encyclopedia** | `apply_mod.py` | `Data/ENG/Script/Teaching.pck` | 25 ADV tutorial chapters overhauled with exact math: delay formulas, trap formulas, chant interrupts, elemental scaling. |
| **Special Lessons** | `apply_mod.py` | `Data/ENG/Script/Lesson.pck` | Guild lectures detailing superboss survival, Valkyrie Circle Protection, Crown thresholds, and award scaling. |
| **Facility Advice** | `apply_mod.py` | `Data/ENG/Script/Shop*.pck` | Strategic guidance in Quest Desk (ShopQuest), Blacksmith forge +9 vs 5 slots (ShopBlacksmith), Tavern merc roles (ShopBar). |
| **Single Source of Truth** | Hand / Scripts | `mod_project/data_tables/*.xlsx` | 13 Excel workbooks serving as the sole source of truth for all modded game content. |
| **QA Verification Suite** | `audit_tool.py` | Terminal Output | Validates 21 PCK archives and 13 Excel tables against engine line budgets, byte budgets, and encoding limits. |

---

## 2. Repository Architecture & Workflow Map

```
c:\Users\user\Personal\Physics\DungeonTraveler2-2\
├── DungeonTravelers2-2_EN\Data\ENG\
│   ├── Parameter\          # Live game parameter PCK archives (16 archives modified/verified)
│   └── Script\             # Live game ADV script PCK archives (5 archives modified/verified)
├── mod_project\
│   ├── backups\            # Untouched vanilla backup copies of all PCKs
│   ├── data_tables\        # 13 Excel workbooks (The Single Source of Truth)
│   ├── docs\               # Architecture, philosophy, and balance proposals
│   └── tools\
│       ├── pck_handler.py  # Binary parser/rebuilder helpers (PckArchive, helpers for all 13 types)
│       ├── apply_mod.py    # Master compiler: reads Excel tables and writes live game PCKs
│       └── audit_tool.py   # Comprehensive QA test suite: asserts 100% format and byte integrity
└── docs_example\           # Design philosophy and reference architecture (7th Dragon 2020)
```

**Build Command:** `python mod_project/tools/apply_mod.py` (compiles all 21 PCKs from Excel in ~4 seconds).  
**Test Command:** `python mod_project/tools/audit_tool.py` (validates all 21 PCKs and 13 tables in ~5 seconds).  
**Dependencies:** Python standard library (`os`, `struct`, `re`, `shutil`) + `openpyxl`. Zero external binary tools needed.

---

## 3. Binary Architecture & Container Formats

### A. The PCK Archive Container **[verified]**
All parameter and script packages in DT2-2 are packed in `.pck` archives:
* **Header (16 bytes):**
  * `0x00:0x04`: Magic header `0x00010000` (little-endian: `00 00 01 00`).
  * `0x04:0x08`: File count `N` (`uint32`).
  * `0x08:0x10`: Reserved / padding (`00 00 00 00 00 00 00 00`).
* **Table of Contents (TOC):** `N` entries of 48 bytes each:
  * `0x00:0x20`: Filename (32 bytes, null-terminated ASCII, e.g. `EquipmentData_0000.bin\0`).
  * `0x20:0x28`: Absolute byte offset in archive (`uint64`).
  * `0x28:0x30`: File byte length (`uint64`).
* **Data Payload:** Follows immediately after the TOC. Entries are stored consecutively with natural padding.

### B. Record Formats Across Subsystems **[verified]**

#### 1. `EquipmentData.pck` (551 Entries | Weapons, Armors, Shields, Accessories)
* **Header Size:** Exactly 128 bytes (`0x80`).
* **String Pointers (32-bit):**
  * `0x08`: `p0` $\rightarrow$ Item Name.
  * `0x10`: `p1` $\rightarrow$ Item Description (up to 3 lines, $\le 85$ chars/line).
  * `0x18`: `p2` $\rightarrow$ Unidentified Item Name (`? Sword`, etc.).
  * `0x70`: `p70` $\rightarrow$ Duplicate Name Pointer.
* **Mechanical Parameter Offsets:**
  * `0x40:0x44`: Weapon Range flags (`0x42/0x82/0x102` = Short, `0x85/0x95/0x104` = Mid, `0x89/0x99/0x219` = Long; `0x0` = Non-weapon).
  * `0x4c:0x50`: Delay Speed Rank (`0` = A+ 1.0x, `1` = A 1.2x, ..., `11` = F 2.9x). Direct index into `WeaponRankData.pck`.
  * `0x60, 0x64, 0x68, 0x6C`: Four 32-bit integer IDs for innate passive enchantments mapping to `EnchantData.pck` (`-1` = empty).
* **Alignment Rule:** Must be **8-byte aligned at file end** (`(8 - (len % 8)) % 8`), NOT 16-byte aligned.

#### 2. `ItemData.pck` (576 Entries | Consumables, Food, Tools, Valuables)
* **Header Size:** Exactly 112 bytes (`0x70`).
* **String Pointers (64-bit):**
  * `0x08`: `p0` $\rightarrow$ Item Name.
  * `0x10`: `p1` $\rightarrow$ Item Description.
  * `0x60`: `p60` $\rightarrow$ Secondary / Unidentified Name.
* **Alignment Rule:** 8-byte aligned strings and file end.

#### 3. `SkillData.pck` (Technique, Magic, Passive, Unique)
* **Header Size:** `0x28` to `0x38` depending on category.
* **Structure:** Contains string pointers for Skill Name, Description, and Level-Up Progression text, followed by raw skill attributes (TP curve index, target scope, element flag, chant frame delay).

#### 4. `TrapData.pck` (12 Entries | In-Dungeon Hazard Formulas)
* **Header Size:** Exactly 32 bytes (`0x20`).
  * `0x00`: Trap ID (`0` to `11`).
  * `0x08`: `p_name` pointer (always `0x20`).
  * `0x10`: Status ID (`-1` none; `113` Poison, `114` Freeze, `115` Paralysis, `116` Sleep, `117` Silence, `120` Petrify, `122` Slow).
  * `0x14`: Float32 Activation Check (`0.50f` for Damage/Mine/Killer/Petrify; `0.33f` for elemental gas; `0.25f` for Slow; `1.00f` for Dispel/Alarm).
  * `0x18`: SFX Anim Index.
  * `0x1C`: Target Scope (`1` = single triggering ally; `2` = entire party; `4` = alert battle).
* **Name String:** Starts at `0x20`, null-terminated, 8-byte aligned. Inserts directly into `StringData_0378.bin` (`"You triggered a %name trap!"`).

#### 5. `TrophyData.pck` (50 Entries | In-Game Awards & Milestones)
* **Header Size:** Exactly 24 bytes (`0x18`).
  * `0x00`: Trophy ID (`0` to `49`).
  * `0x04`: Sort order.
  * `0x08`: `p_title` (always `0x18`).
  * `0x10`: `p_desc` pointer (calculated dynamically: `0x18 + len(title_padded)`).
* **Alignment Rule:** Title and description are 8-byte aligned.

#### 6. ADV Script Archives (`Teaching.pck`, `Lesson.pck`, `Shop*.pck`)
* **Format:** Bytecode sequence with null-terminated ASCII strings. Strings can be patched in-place or dynamically resized without crashing opcode flow, provided null terminators are preserved.

#### 7. Untouched Pure Binary Archives **[verified]**
* **`WeaponRankData.pck` (12 entries | 856 bytes):** Lookup table of 12 IEEE 754 32-bit floats defining action recovery delays:
  `[1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.7, 2.8, 2.9]`.
* **`ClassLevelData.pck` (38 entries | 122,352 bytes):** 32-byte growth records for levels 1–99 (HP, TP, 6 core attributes). Contains 0 strings.
* **`LvExpSkptData.pck`:** EXP curve and SP accumulation tables per level.

---

## 4. Text Rules, UI Budget & The Hybrid Integrity Policy

### A. The Engine Display Constraints
* **Line Count:** $\le 3$ lines in items, equipment, and skills; $\le 2$ lines in trophies.
* **Line Length:** $\le 85$ characters per line maximum.
* **Prohibited Characters:** The tilde character (`~`) is NOT supported by the Aquaplus-Sting font glyph table and causes severe in-game rendering glitched boxes. Always use `->` or `-` instead.
* **Separators:** Standardize on `' | '` with clean spacing.

### B. The Non-Destructive Hybrid Policy ("Game Soul Protection")
A core rule of the mod is: **It is a data transparency mod, not a mod that destroys the spirit or humor of the game.**
1. **Never erase lore or humor:** Vanilla flavor text, witty Japanese-RPG banter, pop culture references, and puns must remain intact.
2. **Format Rule:**
   * **Single-Line Items:** `OG text (concise data).`  
     *Example:* `"Even more umami than MSG. Taste the skill points (+9 SP)."`
   * **Multi-Line Items:** If `OG + (data)` would exceed 85 characters, keep the complete OG text on Line 1 and place `(concise data)` cleanly on Line 2.  
     *Example:*  
     Line 1: `"A Souffle special. Goes off with a bang that makes you jump."`  
     Line 2: `"(Explosive bomb damage, 75% Blind)"`
3. **No Redundant Filler:** Omit repetitive boilerplate like `"to an ally"` or `"Restore HP"`. Only the concise mechanical value matters: `(+60 HP)`, `(Full HP/TP)`, `(+20% ATK)`.

---

## 5. QA Verification Suite (`audit_tool.py`)

The automated audit suite acts as an unyielding gatekeeper asserting:
1. `skills.xlsx`: Line count $\le 3$, length $\le 85$, no `~`.
2. `items.xlsx`: 388 active items, line count $\le 3$, length $\le 85$, no `~`.
3. `equipment.xlsx`: 551 active items, line count $\le 3$, length $\le 85$, no `~`.
4. `grand_seals.xlsx`: 374 active seals.
5. `joint_skills.xlsx`: 52 active combos.
6. `enchants.xlsx`: 280 affixes.
7. `party_skills.xlsx`: 20 party compositions.
8. `food_menu.xlsx`: 16 buffet meals.
9. `enemy_attacks.xlsx`: 2,375 enemy techniques.
10. `classes.xlsx`: 32 player classes.
11. `ui_strings.xlsx`: 14 core combat command tooltips.
12. `traps.xlsx`: 12 trap definitions.
13. `trophies.xlsx`: 50 hybrid trophy milestones.
14. **Binary PCK Integrity:** Loads all 21 live `.pck` files in `DungeonTravelers2-2_EN/Data/ENG/` with `PckArchive`, asserting zero byte corruptions or TOC mismatches.

---

## 6. Mistakes Made and Corrected (Do Not Repeat)

1. **Equipment End Alignment:** Initially attempted 16-byte end padding on `EquipmentData.bin`, causing 8-byte file length mismatches on ~50% of items. Tested and proved that DT2-2 engine uses strictly **8-byte end alignment** (`pad = (8 - (len % 8)) % 8`), restoring 100% byte-exact identity across all 551 files.
2. **Flat Text Overwrites (The Humor Loss):** In early sessions, `items.xlsx` and `trophies.xlsx` replaced charming flavor text (MSG umami joke, "Eat, Skill, Love", Souffle pipe bomb ticking noise) with dry mechanical descriptions. Detected and corrected in Commits `be90446` and `45efe13` with the hybrid `OG + (data)` architecture.
3. **ADV Bytecode Script Offsets:** Early attempts to patch `.adv.bin` scripts by rebuilding bytecode headers caused dialogue freezes. Solved by in-place sequential text substitution (`update_teaching_script`), which the Sting engine parses safely without opcode table corruption.
