# 7th Dragon 2020 (PSP): what was done, how, and how to continue

Reference for agents working on this game or on its sequels. Read `philosophy.md` first for the reasoning.
Confidence tags: **[verified]** read from the binary or run, **[inferred]** deduced from code/data, **[untested]** not run in an emulator.

## 1. Deliverables
| Output | Built by | Content |
|---|---|---|
| `7th Dragon 2020 (Skill Mod).iso` | `build_iso.bat` | All text changes (skills, items, town, UI, NPC, enemies). Never touched by QoL builds. |
| `field_qol/7th Dragon 2020 (Skill Mod + Field QoL).iso` | `build_field_qol.bat` | Skill Mod + QoL driven by `field_qol/field_qol.json`. |
| `data/text_mods.xlsx` | edited by hand | Single source of truth for every modded string (Original / New columns). |
| `data/game_binary.xlsx` | `src/08_export_binary_excel.py` | Decoded binaries (skills, effects, classes, enemies, items, texts). Fact base. |

Base game: PSP, English fan translation v0.91 (modified font; space is the glyph `U+FF9C`, ASCII is stored fullwidth).
Language of chat with the user: Spanish. Everything in the repo: English. Commits: one line `type: description`, enforced by
`hooks/commit-msg` (types feat/fix/perf/test/docs/build/ci/chore/refactor, lowercase, <=72 chars, no trailing period, no ids), no attribution lines.

## 2. Repository map
* `src/01-02` parse the GameFAQs pages in `data/*.mhtml` into `json/skills_database.json` (FAQ is only a last-resort source).
* `src/03` validate skill text (44 / 26 chars) -> `json/modded_texts.json`. `src/07` QoL text databases. `src/04` patch binaries in `modified_init/`.
  `src/05` repack `init.tpk` (exactly 717744 bytes). `src/06` inject into the ISO. `src/08` export `game_binary.xlsx`.
  `src/common.py` paths, limits and text encoder. `src/text_excel.py` workbook loader. `src/power_tiers.py` damage tier words.
* `extracted_init/` original binaries, `modified_init/` patched ones. `tests/` unittest/pytest (51 tests). `scratch/` ignored one-shot scripts.
* `tools/` standalone analysis tools, standard library only: `cpk.py` (CPK/TPK reader: `list`, `extract`), `eboot.py` (EBOOT disassembler per word, callers, data references,
  relocation entries, function bounds), `lua_bytecode.py` (call sites and constant arguments in the `.lub` scripts). Tested by `tests/test_tools.py`.
* `field_qol/` QoL builder: `build_field_qol.py`, `field_qol.json`, `field_qol_test.json` (extreme test values), `encounter_enemies.py`.
* Build: `build_iso.bat` (steps 03,07,04,05,06 + tests), `src/build_all.py` (everything), `build_field_qol.bat [json]`.
  Close `text_mods.xlsx` in Excel before building (the file is locked otherwise).

**Dependencies.** Game tools, builders and tests use only the Python standard library, plus `openpyxl` for the Excel workbooks (text pipeline and `game_binary.xlsx`).
No external disassembler is needed (`tools/eboot.py`); `pytest` is optional (`unittest` works). Nothing depends on files outside the repository.

## 3. Data layout (container and binaries)
ISO -> `PSP_GAME/INSDIR/GAME.DNS` (CPK container, LBA 155, @UTF table TOC, ~12000 files) -> files such as `init/init.tpk`,
`Field/SceneSet/*.tpk`, `event/*.lub` (compiled Lua 5.1). `EBOOT.BIN` is a plain relocatable MIPS ELF (LBA 750055, 3141409 bytes;
`BOOT.BIN` is an unused duplicate). `init.tpk` offset in the ISO = `317440 + 2048 + 129987072`.
TPK: magic `0x0004841C`, count, entries of (offset, name[28]). Text BINs: `count`, (id, offset) pairs, NUL-terminated strings.

Key tables **[verified]** unless noted:
* `SKILL.BIN`: 4-byte count, 48-byte records (12 x u32). f0 skill id (companions = parent+1..8, enemy skills 10010+); f1 level | SP<<16;
  f2 description text id; f3 bytes (group, auto rate code 3/5/7 = 35/15/12 %, category[inferred], target scope[inferred]);
  f4 MANA<<16 | flags | element; f5 power | hits<<16 | priority<<24; f6 EX gain x100 in the high half; f7 speed | accuracy<<16; f8-f11 ADDEFF ids.
* `ADDEFF.ADB`: 40-byte records (id, type, rate, duration, flags, 3 values). Type 86 = cannot miss.
* Class DBs (5 x 99 x 84 B): w1 HP, w2 MANA, w3 low half = level, w9 cumulative EXP.
* `ENEMYDB.BIN` (4 B header, 168 x 84 B): w1 HP, w3 low = level, **w9 = EXP, w10 = SP**. `ENEMYLIST.BIN` (4 B, 168 x 108 B): w0 id, name at bytes 8-56,
  **w14 = money, w17/w18 = drop items (0xFFFFFFFF none), w20 = two u16 drop chances in %**.
* `BTLPARAMSETTING.BIN` (812 B, u32): +0x14/+0x18 random-encounter countdown min/max (28900/30600); +0x08 normal attack EX gain (200); +0x54..+0x60 EX gained when
  hit (<25/50/75/100 % HP: 100/250/500/1000); +0x74 = 85, +0x78 = 100 (Casual factors); +0x314 enemy HP % (85), +0x318/+0x31c EXP/SP % (105),
  +0x320/+0x324/+0x328 level-gap EXP tiers (150/300/500).
* `ITEMDATA.BIN` records: 32-byte name, a **96-byte text area (31 characters + NUL)** (80 in Samples, 100 in Key_Items), then data words. The first data word is an
  `ADDEFF.ADB` effect id for consumables and weapons (weapon status = type/rate/duration there, e.g. effect 1801 = Poison 25 %, 3 turns; Nano Aid = effect 14720, type 147,
  value 30). Writing past the text area destroys this data (revive and cure items stopped working once: the patch zero-filled 108 bytes). Sections: Consumables 0-41,
  Weapons 200-307, Armors 400-430, Accessories 500-548, Samples 700-746, Key_Items 1000-1053. Decoded in the `Items` sheet of `game_binary.xlsx`.
* `FIELDSETTINGPARAM.ALT`: floats at +0x08 (0.24) and +0x0C (0.12) are the player's per-frame step (full / half stick).
* `Field/SceneSet/*.tpk` contain `*.BEB` encounter tables: +0x10 step value (0 = no random encounters), 8 groups of 0x40 B at +0x14
  (weight, formation id, enemy ids x5, -1 empty).
* `QUEST.QDB` (4 B, 55 x 132 B): word 28 is money for 9 quests; item/count words 18-32 not decoded **[inferred]**.

## 4. Text system and limits
* Encoding: ASCII -> fullwidth (`chr(c + 0xFEE0)`), space -> `U+FF9C`, dashes -> fullwidth hyphen. `common.to_game_text/from_game_text`.
* UI limits: skill description **44** chars, NEXT LEVEL **26** chars (the old constant 54 was wrong). Item description capacity: 96 bytes of text (31 characters) in consumables, weapons, armors and
  accessories, 80 in samples, 100 in key items (the on-screen box shows 32 characters). Enemy names 48 B. NPC pool (`09001200.tpk`) 3260 B exactly. Combined pool
  `B_BATTLE1 + CUSTOMMENUTEXT + TOWNTEXT + UICOMMONTEXT` must equal **142880** bytes (identical strings are deduplicated to stay inside the budget).
* Workbook sheets: Skills (120), SkillLevels (559), Items (331), Town (30), Common (198), UI (8), Field (17), NPC (6), Enemies (122).
  Only "New" columns are consumed; empty New = unchanged. Excel turns CR into `_x000D_` and drops CRs of LF CR LF: `text_excel._clean` restores them.
* The base translation contains corrupted bytes in many names and descriptions; the mod sanitizes every item, enemy and speaker name.

## 5. Skill text style guide (decided with the user)
* Tags without parentheses: `Battou:`, `Iai:`, `Auto:`, `EX Skill:`, `D-Depth 2:`. Use `Auto at end:` only for auto skills that act at turn end.
* Do not put a second `:` in a description; use `/` or reorder. Include a probability only if constant. MANA and SP costs are shown by the UI, so never write them.
* Keep original flavour words; add data. Damage words come from real power (`power_tiers.py`): average of Lv1 and max power (multi-hit = total),
  thresholds Moderate 225, Major 475, Severe 600, Extreme 850, AoE skills one tier higher. Fitted to 13 of 19 original tier words (the other 6 were inconsistent).
* NEXT LEVEL says what the upgrade adds, using binary values (`325% dmg, 40% Crit`, `Dmg -27%`, `Learn (35% rate, Hack 75%)`).
* Auto activation % is NOT in the binary (only code 3/5/7); 35/15/12 come from the FAQ and the code grouping **[inferred]**. Say so when unsure.

Examples (Original -> New):
| Skill | Original | New |
|---|---|---|
| Surprise Hunt | (Auto) Low chance for a preemptive attack. | Auto: More preemptive hits; blocks ambush. |
| Battering Gale | (Battou) Major damage + bleeding to one enemy. | Battou: Major damage + 50%+ Bleed (4t). |
| Double Hook | (D-Depth 2) Damage and lower enemy's attack. | D-Depth 2: Damage + enemy ATK down (3t). |
| Shutdown | For 2 turns, put enemies to sleep, 100% if Hacked. | Sleep enemies 2 turns, 55%+ (100% if Hacked) |
| Ifritbane | Deals major magic fire damage to one or all foes. | Moderate magic fire dmg to one or all foes. |
| Resurrection | Revive an ally. | Revive a fallen ally with some LIFE. |
| NEXT LEVEL: Microburst Lv2 | Stronger, MANA 9+1 | 400%, 80% Bleed |
| NEXT LEVEL: Payback Lv3 | Attack/debuff up | 475% dmg, +30% Vuln |
| Item 415 | (corrupted) | DEF+50 MDF+25. [SAM/TRK/DES] |
| Item 24 | (corrupted) | Panacea: Cure Blind (Restores accuracy) |
| Town 89 | Workspace for the development team. | [Cost: 4 Dz] Murasame Workshop Lv 5. Reward: Tier 5 Weapon & Armor Crafting |
| Field 231 | Enemies will have a hard time finding you for a while. | Reduces encounter rate to 20% for 200 steps. |
| Enemy 20 / 1000 | (corrupted) | Slime / Damselfly |
| COMMON1 12/13 | Standard / Easy difficulty text | Standard 100% damage dealt and taken / Casual 85% (0.85x) |
Divergences of binary vs FAQ found: Rush Shot Lv1 135% (FAQ 130), Zero at the Bone counter 175-235%, A-Skill Caller priority 0, Recover speed 100%,
Plasma Jolt element Air. NPC `09001200` was turned into a combat tutorial (formulas, ailments, guard rings); mechanics there partly come from the FAQ **[inferred]**.

## 6. Tests (what each guards)
`test_text_encoder` (round trip, space glyph), `test_character_limits` (44/26, 120 skills, no Japanese), `test_qol_limits` (byte budgets, semantic checks of items/manuals/names),
`test_tpk_integrity` (header, entries, 142880 pool), `test_iso_integrity` (original untouched, size, strings extracted back from the ISO), `test_power_tiers`
(tier words match the binary), `test_field_qol` (reward maths, frame patch, level-gap code run in `tests/mips_mini.py`, config loading).
Run: `python -m pytest tests -q` or `python -m unittest discover -s tests -p "test_*.py"`.

## 7. Field and battle QoL (field_qol.json)
Build: copies the Skill Mod ISO, rebuilds `init.tpk` (data patches) and patches `EBOOT.BIN` (code), asserting original bytes first. Keys:
| Key | Mechanism | Notes |
|---|---|---|
| `move_speed_boost` | ALT +0x08/+0x0C x (1+b) | Walk animation does not scale. [verified in emulator by user at x2] |
| `encounters.reduction` | countdown min/max x 1/(1-r), divided by speed boost when `compensate_speed_boost` | Walking: a counter drains per moving frame; at <=0 a battle starts (function 0x1428ec, re-roll 0x143484). Per-scene drain 45-100 in the BEB `+0x10`. |
| `encounters.countdown_override` | absolute [min, max] | Original min/max differ only 3 %, so raising only the minimum does nothing; scale both. |
| `map_reveal` | `radius`: table at va 0x23A290 (9 signed byte pairs, shift 2 -> 0 at 0x56790/0x56798); `all`: rewrite loop 0x56788-0x567C0, bound 0x5682C | Cells are 16 px. [`all` verified by user; `radius` untested] |
| `game_speed` | main loop frame end calls `sceDisplayWaitVblankStartMultiCB(2)` at 0x1A9888 (30 fps logic, fixed 1/30 s step) | `field_vblanks`/`battle_vblanks` 2 = original, 1 = x2. Music unaffected. Battle detection = CBtlTask singleton pointer at 0x23C5B8 != 0. Uses a 13-word cave at the dead function 0x1CD73C. **[untested]** |
| `rewards` | EXP = ENEMYDB w9, SP = w10, money = ENEMYLIST w14, drop % = w20 | `match_encounter_rate=true`: factor = (1+boost) * mean(new countdown) / mean(original); floor per enemy, only the 57 enemies of random-encounter tables (`encounter_enemies.py`). Visible/boss enemies untouched. |
| `exhaust_gain` | SKILL f6 high half (player skills) + BTL +0x08, +0x54..+0x60 | Per battle, so not compensated. |
| `battle_tuning` | BTL +0x314/+0x318/+0x31c, level-gap tiers | See Casual note below. |
| `level_gap_bonus` | rewrites the tier code at 0x104234-0x104294 in `0x103eec` | Per character: gap = avg enemy level - character level (effective level from CBtlObjAlly +0x108 struct, offset 8). percent = min(max, 100 + extra*(gap // every)); EXP always, SP if `also_sp`. Defaults 5 / +100 / 1000 / true. Original tiers: 150/300/500 at gap 5/10/20. Not gated by difficulty. **[untested]** |

**Casual vs Standard (corrected).** The new-game difficulty menu (code near 0x830B0) writes word 3 of the progress struct (0x39490): Standard = 1, Casual = 0
**[inferred from code]**. Only when it is 0 does the game apply enemy HP 85 %, EXP/SP +5 %, the 85 % factor in 0xEF97C and 100 % in 0xEF2BC. Earlier notes claiming
these are "always on" or tied to the clear flag were wrong. Consequence: `battle_tuning.enemy_hp_percent/exp_percent/sp_percent` have no effect in Standard unless
the gate branches (0xE4558, 0x10408C) are patched (not done yet).

**Result screen.** EXP, SP and money count down 1 per frame (0x104D90); pressing the button applies everything at once (0x1052C8, handles multi-level gains).
Large reward multipliers lengthen the animation. Possible future work: count several per frame.

## 8. Code-patching rules learned (EBOOT)
* `EBOOT.BIN` file offset = module va + 0xA0 (code segment), data segment va 0x25E150 -> file 0x25E200. Disassemble **per 4-byte word** (capstone stops at the first VFPU opcode otherwise).
* It is relocatable: every `jal/j` (type 4), `lui` (HI16, 5) and `lw/addiu/...` (LO16, 6) with an absolute address needs an entry in the PSP relocation table
  (file offset 0x260988, 8-byte entries r_offset/r_info, 71668 entries). A new absolute reference without an entry crashes on a real load. Reuse entries of dead code by changing `r_offset`
  (keep HI16 immediately followed by its LO16; park displaced entries on dead words of the same instruction type). Branches (`b`, `beqz`) and register/immediate code need none.
* Dead code check: no `jal/j`, no branch from outside, no pointer word in the file (except the relocation table itself), no `lui+addiu` materialisation.
* Stubs: library headers at 0x20E270-0x20E43C; sceDisplay stubs 0x20DCA4+8*idx (idx 2 = WaitVblankStartMultiCB). Main loop 0x1A92E8, frame end 0x1A9848.
* Lua event scripts are Lua 5.1 bytecode with **4-byte float numbers**. They only call `add_party_sp` 6 times (100-1000 SP); every `money_add_*` is a payment; item gains use variables.
* Verification pattern: diff the final image against the base (only expected regions), simulate relocation to see final addresses, run patched words in `tests/mips_mini.py`.

## 9. Mistakes made and corrected (do not repeat)
FAQ numbers over binary; 54 vs 44 limit; Excel CR corruption; disassembly truncated at 0x198CFC; random encounters confused with visible dragons; the first
field-QoL scripts used wrong ALT indexes and a wrong ELC patch; reward multiplier applied to bosses; `also_sp`/level-gap range overflow guard added; difficulty flag mis-described (see 7).

## 10. Not done / ideas
Dialogue text speed (no variable found); menu animation speed (battle menu motion files hold only 5-8 frame durations, so they are not the cause); faster result-screen count;
drops of items outside enemy tables and quest item rewards (QUEST.QDB words undecoded); applying `battle_tuning` in Standard; emulator validation of `game_speed`, `radius` reveal and `level_gap_bonus`.

## 11. For the sequels and other games
Check the old tools on the new files first: container (CPK/TPK), text pools (`id,offset` tables), record sizes (48-byte skills, 84-byte class/enemy), `BTLPARAMSETTING`-like parameter file, `ALT`
field settings. Reuse the process: workbook export -> style guide with the user -> limit tests -> JSON knobs -> extreme test build -> moderate defaults -> documentation of what is unverified.
