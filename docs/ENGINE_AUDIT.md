# Engine audit: method, roadmap and rules

This document tells an agent how to check, piece by piece, that the battle engine of this project (`engine_cs/`) does what
the game's program does. It is meant to be followed literally, from the first phase to the last. The agent writes
everything it finds into `docs/result_engine_audit.md`, in the format of section 8, and two people review that file
afterwards. **The agent changes nothing**: no engine code, no data, no workbook, no document other than the result file.

Read the whole document before starting. Then read, in this order: `CLAUDE.md` (if present), `engine_cs/README.md`,
`docs/FORMULAS.md` (all of it), `docs/philosophy.md`, and the sheet `Assumptions` of
`data_tables/sim_setup.xlsx`.

---

## 1. Why this audit exists

The engine was ported from a Python simulator and proven equal to it, trace line by trace line. That proof says the
port is faithful to the simulator. It does not say the simulator was faithful to the game. On 2026-10-18 four defects
were found in one afternoon, each invisible to every test the project had, because the tests compare the engine with
itself or with the old simulator, never with the program:

| Class of defect | What happened | Where it was |
|---|---|---|
| **Lifetime of a state** | A target set by command 1 of an AI script was kept for the whole battle and applied every time the skill came back. The program empties the sixteen target lists at the start of every choice (`0x430f8c - 0x430fa6`), so it holds for one turn only. | `Ai.cs`, `unit.AiTargets` |
| **Fallback branch** | A one-ally action (scope 5 or 7) with no target fell back on the acting unit itself. The program rolls evenly among the candidates (`0x43f7ba`); with a target that is no longer a candidate it takes the lowest HP ratio, the last of them on a tie (`0x43f668 - 0x43f6e9`). | `Battle.Targets`, now `OwnSidePick` |
| **Membership of a list** | Own-side actions (whole party, one ally, random ally) could reach the summon, the dolls and a hired guest. The program builds the candidates of every scope with `0x43e6d0`, which keeps only units numbered below 2000: dolls (2000+n), the summon (3000) and a guest (3001) are never among them. Moved 7,003 of 12,731 recorded traces. | `Battle.Targets`, `friends` |
| **Bias of a measure** | A profile of the mercenaries averaged the length of every fight, lost ones included: a healer that kept a losing party alive longer read as "makes fights longer". Then the length of the won fights was compared on bosses with two or three wins out of 400, which is noise. | `Suite/SkillBattery.cs`, `ProfileOf` |

Two more lessons from the same day:

* **`docs/FORMULAS.md` is a reading, not the program.** Section 9.1 said "a pick on the unit's own side is an even roll
  among the candidates". That is true when no target is given, and false when a target was given but is no longer a
  candidate. A sentence of FORMULAS can be right for the case its author looked at and silent or wrong for its
  neighbours. The binary is the only source of truth (`CLAUDE.md`: "Sources, in order: the game binary, then the Japanese
  player guides").
* **A comment in the engine that cites an address is a claim, not a proof.** Several comments say "as 0x...". Check that
  the address says it.

The audit hunts for these classes everywhere. Section 6 lists the phases; section 7 lists concrete leads already known.

---

## 2. Ground rules (read twice)

These rules exist because an agent can produce a confident sentence that nothing supports. A finding without evidence
is worth less than "not read".

1. **Evidence or nothing.** Every verdict cites, verbatim:
   * the program: the address range, and the disassembly lines that decide the question, copied from the output of a
     tool (section 4), not retyped from memory;
   * the engine: the file and line numbers, and the lines of C# that implement it, copied;
   * when a trace was used: the job JSON and the trace lines (section 5).
   A sentence like "the program checks X" with no quoted lines is not allowed.
2. **"UNREAD" is a valid verdict.** If the code could not be followed to a conclusion, write UNREAD, what was read, and
   where it stopped. Never fill a gap with what "games usually do", with what a function name suggests, or with what
   the engine does.
3. **Do not reason from names.** Debug strings and class names (`Battle::CBattleAI2::Task_s::...`) help to find code;
   they do not say what the code does. Read the instructions.
4. **Follow every branch of a decision.** For each rule, list the cases (target given / not given / given but dead;
   unit is member / doll / summon / guest; side party / enemies; chanting / not; first turn / later turns) and settle
   each one. The 2026-10-18 defects were all in a branch nobody had followed.
5. **Follow the lifetime of every state.** For each piece of state the engine keeps on a unit or on the battle, find
   where the program creates it, where it reads it, and where it clears it (per action, per turn, per choice, per
   battle, never).
6. **Follow the membership of every list.** For each list of units the engine builds (allies, foes, candidates,
   targetable, alive, rows), find the list the program builds in the same place and compare who is in it.
7. **Write down the command of every tool run**, so the reviewers can run it again. Paste its relevant output.
8. **Change nothing.** No edit to `engine_cs/`, `tools/`, `gamedata/`, `data_tables/`, `docs/FORMULAS.md` or any other
   file except `docs/result_engine_audit.md`. A proposed fix is written in the result file, as text, and is not applied.
   Do not commit. Do not push.
9. **Respect the machine.** It has 15 GB of RAM and must never use the disk as memory (a battery with the recorder once
   froze it). Allowed: `dtcli trace` and `dtcli run` on small job files (at most 20 runs a job, at most 20 jobs a file),
   the `exe_*` readers, reading files. Not allowed: `tools/full_suite.py`, `dtcli suite`, any battery
   (`skill-battery`, `mercenary-battery`, `class-search`, ...), any measure of the suite. If a question seems to need a
   measure, write the question in the result file instead.
10. **One item at a time, written as you go.** Append each item to the result file as soon as it is settled, so that
    nothing is lost if the session ends. Do not batch twenty items in memory.
11. **No Python simulator exists.** Battles are played only by `dtcli` (C#). The Python files under `tools/` that the
    audit uses are readers of the binary and of the game files; they play no battle.
12. **When the engine and FORMULAS disagree, read the program.** When FORMULAS and the program disagree, the program
    wins and the item reports that FORMULAS must be corrected (as a proposal).

---

## 3. Map of the code

### 3.1 The engine (`engine_cs/src/DtEngine`)

| File | Lines (2026-10-18) | What it holds |
|---|---|---|
| `Battle.cs` | 2,619 | The battle: units, turn order, actions, targets, hits, damage, statuses, heals, songs, dolls, items, end |
| `Policy.cs` | 1,012 | What a party member does on her turn: the **player model** (not the game; see phase 13) |
| `Scenario.cs` | 993 | Building a party and its enemies for a checkpoint, the runs of a job |
| `Units.cs` | 660 | `Unit`, `Status`, `UnitFactory` (members, enemies, summons, guests, dolls) |
| `Loader.cs` | 534 | Reading the snapshot into `GameData` |
| `Jobs.cs` | 478 | Job JSON, runner, results, traces |
| `Data.cs` | 370 | Records (`Skill`, `EnemyAttack`, `NpcRec`, `DollRec`, ...), constants `T` (target codes) |
| `Formulas.cs` | 366 | The formulas of FORMULAS sections 2 - 6 (`F.` methods) |
| `Action.cs` | 306 | An action: kind, skill or attack, values of its effects, target code, reach |
| `Ai.cs` | 297 | Enemy, summon and guest scripts (FORMULAS 9) |
| `Measures.cs`, `Recipe.cs`, `Probe.cs`, `Analysis.cs` | | Measures around a battle, party recipes, probes |
| `Recorder.cs`, `Trace.cs` | | What a battle records; the trace format |
| `PyRandom.cs`, `PyMath.cs` | | CPython's generator and rounding, kept for parity |
| `Suite/` | 31 files | Every measure of the project (phase 14) |

Methods of `Battle.cs` by line (find them again with `grep -n "MethodName(" Battle.cs`; lines move):
`Refresh 240, Build 247, SideArray 258, TargetableArray 269, Over 310, Wait 323, Start 364, Ambush 380, Run 400,
Turn 474, BeforeAction 522, Deny 586, LostTurn 592, NextAction 606, ChantOf 636, Pay 643, EndOfTurn 659, Tick 700,
Perform 780, OwnSidePick 921, Targets 935, PickOpponent 1040, Behind 1048, Targetable 1075, WeightedPick 1105,
NumberOfHits 1134, Resolve 1185, Redirect 1207, Voided 1229, Hits 1295, CriticalRateOf 1365, Critical 1377,
Damage 1392, PhysicalDamageValue 1457, MagicValue 1543, HitChance 1612, SpecialDamage 1774, RaceFactor 1807,
ElementFactor 1830, ZoneFactor 1842, TakeDamage 1858, Interrupt 1907, LoseHp 1927, Fall 1939, Restore 1967,
AfterHit 1977, PerformSong 2175, ApplyAilment 2219, Stun 2262, EndPerformances 2270, Delay 2306, Dispel 2333,
Heal 2347, Counter 2409, MakeDoll 2421, MakeGuestDoll 2463, RemoveDoll 2484, DollAction 2503, RandomMove 2538,
UseItem 2567, Roll 2614`.

Constants of the engine that are not data (each must be traced to the program or declared a model limit; phase 12):
`Battle.cs`: `MaxTime = 400.0`, `MaxActions = 3000`, `POISON_SHARE = 0.05`, `TRANQUIL_TURNS = 4`,
`DARK_AURA_TURNS = 4`, `ECSTASY_TURNS = 3`, `SLOW_TARGET_RECOVERY = 5`, `SLOW_TARGET_TURNS = 5`,
`SUGAR_COMA_RECOVERY = 5`, `SUGAR_COMA_TURNS = 3`, `SPECIAL_SLEEP_VALUE = 10.0`, `DOLL_MAGIC_SCALE = 500.0`,
`START_GAUGE = 500`, `RANDOM_ORDER = 20`; `Ai.cs`: `MAX_SWITCHES = 8`; every literal in `Formulas.cs`. Find all with
`grep -nE "const (int|double)|= [0-9]+(\.[0-9]+)?;" engine_cs/src/DtEngine/*.cs`.

Unit kinds (`Units.cs`): `Kind.Member`, `Kind.Enemy`, `Kind.Summon` (the summon of the grand sealbook **and** a hired
guest ally: both are built with this kind; tell them apart by name or by how they were built), `Kind.Doll`, `Kind.Npc`.
Program numbers: members and enemies below 2000, dolls 2000+n, summon 3000, guest 3001.

### 3.2 What the engine reads

`build/engine_snapshot.json`, written by `tools/engine_export.py` from the game files (`backups/`, through readers
such as `tools/enemy_data.py`, `tools/npc_data.py`, `tools/summon_data.py`, `tools/doll_data.py`, `tools/enemy_ai.py`)
and from the workbooks. Two sides: `vanilla` and `variant` (the variant applies the rows of
`data_tables/balance_changes.xlsx` through `gamedata/variant.py`; the game build writes the same rows through
`tools/balance_values.py`). Record layouts: `data_tables/record_layouts.json`.

### 3.3 The program

Two files in the game folder (`tools/mod_config.py` says where): `DT22_en.exe` (DRM wrapped) and
`DT22_en_unwrapped.exe`. The readers use the unwrapped one through `tools/exe_reader.py`. Code from `0x401000` to
about `0x640000`. The battle code is around `0x410000 - 0x510000`; FORMULAS gives the address of every rule it read.

### 3.4 Documents that help

* `docs/FORMULAS.md`: every rule read so far, with addresses and a tag **[code]**, **[message]**, **[read in part]**.
* `docs/generated/EXE_FORMULA_STRINGS.md`: the developers' debug messages that print each step of a formula, with the
  functions that print them.
* `docs/generated/EFFECT_COVERAGE.md`, `docs/generated/EFFECT_CONTEXT.md`: for every effect id, where the program asks
  for it and what follows.
* `data_tables/engine_coverage.json`: `handled` (280 effect ids with the engine method that acts on each), `ai`
  (commands, sources and target kinds the engine has a branch for).
* `data_tables/sim_setup.xlsx`, sheet `Assumptions`: rules the model uses, with what is not read yet.

---

## 4. Tools to read the program

All run from the repository root. On this machine (Windows, Git Bash) set the encoding and strip carriage returns, or
`grep` finds nothing:

    PYTHONIOENCODING=utf-8 python tools/exe_dis.py 0x43f450 0x43f900 | tr -d '\r' > scratch/dis_43f450.txt
    grep -an "call\|cmp" scratch/dis_43f450.txt

| Tool | Use |
|---|---|
| `python tools/exe_dis.py START END [START END ...]` | Disassemble a range; constants read are noted beside their line. Main tool. |
| `python tools/exe_around.py ADDR [BEFORE AFTER]` | Disassemble around an address, aligned so the instruction holding it decodes. |
| `python tools/exe_who_calls.py ADDR` | The start of the function holding ADDR and its direct callers. Calls through tables are not seen. |
| `python tools/exe_find_const.py HEX` | Where a 32-bit constant (an address of a table, an effect id) appears in the code. |
| `python tools/exe_digest.py START END` | A reading aid: effect lookups, rolls, stat reads, constants, messages in a range. Not the code. |
| `python tools/exe_effects.py` / `exe_effect_context.py` | Regenerate the effect coverage documents (they write files: **do not run**; read the generated ones). |

How to read what you see:

* `call 0x490790` with a count pushed: the even roll "a number below n" (`push ebx; call 0x490790`); the result is an
  index into a list.
* An effect lookup: `mov edx, N` or `push N` followed by a call to one of the finder functions (listed in
  `tools/exe_effects.py`, `FINDERS`): "is effect N on this unit / in this action".
* `[unit + 0x78]` is the side flag of a unit (1: the party side), `[unit + 0x79]` the row flag (front), `[unit + 4]`
  its number (below 2000 / 2000+n / 3000 / 3001). Confirm each time; do not assume another offset means the same.
* A jump table: `jmp dword ptr [eax*4 + TABLE]`; read the table's entries with `exe_dis` on a range that holds code
  addresses, or find the cases by disassembling each target.
* Floats: `movss xmm0, dword ptr [0x6d....]` with the value noted by the tool.
* Parameters: `ebp + 8` is the first argument of a function with a frame; arguments are pushed last-first.

If a range decodes as nonsense (`lcall`, `into`, `adc al, 0x89`), the start is misaligned or it is data: try
`exe_around` or start at the function's `push ebp`.

---

## 5. Tools to see what the engine does

Build once: `dotnet build engine_cs/src/DtEngine.Cli -c Release`. The program: `dotnet
engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll` (below: `dtcli`). Export the snapshot if it is missing:
`python tools/engine_export.py`.

A trace of a battle: write a job file in `scratch/`, then

    dtcli trace --snapshot build/engine_snapshot.json --job scratch/audit_job.json --out scratch/audit_trace.txt [--level 2]

A job (fields in `engine_cs/README.md`, section Jobs):

    [{"id": "a", "side": "variant",
      "party": {"cid": "C34", "roles": null, "level": null, "crown": 0, "guest": "Chloe"},
      "enemies": {"kind": "checkpoint"}, "runs": 1, "seed": 7}]

`guest`: omit for the party as built (members and the summon), `"none"` for the members only, or a mercenary's name.
`enemies.kind`: `checkpoint` (its fixed battles), `enemies` (battles written by hand: `"groups": [[[enemy id, front],
...]]`), `formation`, `zone`, `fixed`. Hand-written enemies let you build the exact case a rule needs.

Reading a trace:

* `U n name|kind|side|front|L..|hp..|tp..|st ATK,DEF,INT,RES,DEX,AGI|rs (8 resistances)|w weight|...|pv passives|...|at
  attack ids` : one line per unit before the battle.
* `T k time aN A<n>:<kind>:<name>:L<level>;<events> | <state of every unit> | w<words drawn>` : one line per turn.
  Events: `H a>b=1` a hit of a on b landed (`=0` missed); `L b-n` b lost n HP; `D a>b=n` damage a dealt to b;
  `R b+n` b recovered n HP. Unit state: `hp/tp/alive/next time`.
* `E ...` the end of a battle: won, lost, time, actions, ...; `C ...` the recorder tables after it.
* `--level 2` adds every draw of the generator.

Two quick checks the 2026-10-18 audit used and that are good models:

* "Who receives this heal?": trace a guest with a heal and grep its lines: `grep -o "A6:enemy:Honey[^|]*" trace.txt |
  sort | uniq -c`.
* "Does this change matter?": `dtcli golden check --root .` before and after (it plays 12,731 recorded jobs in about
  11 s and says how many traces move). Only to size a proposed fix in a scratch copy is it needed; this audit changes
  nothing, so it is used only at phase 0.

---

## 6. The phases

Each phase lists its items with an ID. Every item ends in the result file with a verdict (section 8). The item list is
the checklist: at the end, every ID appears in the result file exactly once. Add items you discover with the next free
ID of the phase (`P5.14`, ...) and say why you added them.

For every item the procedure is the same (section 6.0); the items say what to look at.

### 6.0 The procedure for one item

1. **State the rule** in one sentence as FORMULAS gives it (quote the section) or, if FORMULAS is silent, as the
   engine implements it.
2. **List the cases** (rule 4): who acts, who is aimed at, what kind each unit is, what state it is in, what was set
   before.
3. **Find the program's code**: the address from FORMULAS, or from a debug string (`EXE_FORMULA_STRINGS.md`), or an
   effect lookup (`EFFECT_CONTEXT.md`), or `exe_find_const` on an id, then `exe_who_calls` up to the caller that
   decides. Disassemble the whole function, not a window.
4. **Settle each case** in the program; quote the lines.
5. **Find the engine's code** for each case (grep the method; follow the calls); quote the lines.
6. **Compare** case by case. For state, compare lifetimes (rule 5); for lists, compare members (rule 6); for numbers,
   compare constants and their rounding (int cut, float precision).
7. **If they differ**: write the smallest trace that shows the engine's behaviour (section 5), and estimate how often
   the case occurs (which data uses it: count enemies, skills, guests that carry the effect or the scope; the snapshot
   is JSON and can be counted).
8. **Write the item** (section 8) and go to the next.

### Phase 0. Baseline

| ID | Item |
|---|---|
| P0.1 | Record the commit (`git log --oneline -1`), the date, `git status --short` (expected: clean). |
| P0.2 | `dotnet build engine_cs/src/DtEngine.Cli -c Release`: 0 errors. |
| P0.3 | `dtcli golden check --root .`: every trace as recorded (paste the line). |
| P0.4 | `dotnet test engine_cs`: all pass (paste the count). |
| P0.5 | Read the sheet `Assumptions` (31 rows) and copy into the result file the ID, rule and state of each; phase 12 settles them. |

### Phase 1. Data the engine reads

The engine can be right and still read a wrong field. For each record kind, check that the field the engine uses is the
field the program uses for the same purpose.

| ID | Item |
|---|---|
| P1.1 | `EnemyStatusData`: stats, resistances (order of the 8), weight at 0x44 (the turn formula), swing, level, flags word 0x3C (immunity bits; FORMULAS 5c), passives. Compare `tools/enemy_data.py` and `record_layouts.json` with the program's readers of each field. |
| P1.2 | `EnemyAttackData` (FORMULAS 9.2): target code 0x2C, attribute 0x30, chant speed 0x34, accuracy 0x38, power 0x3C, turns 0x40 (float to int), speed 0x44, five effect slots from 0x4C (id, value, kind). Check how the engine maps the target code (0x2C) to its `T` constants (`Data.cs`, `Loader.cs`): every code 0 - 15, especially 5 - 12 (own side) and 14 - 15. |
| P1.3 | `EnemyAIData` / `NPCAIData` (FORMULAS 9): the decoder `tools/enemy_ai.py` (commands, argument kinds, result words, once and stop tails) against the parser at `0x430cd7` and the interpreter. |
| P1.4 | `NPCData` (guest allies): id, level, rank 0x1C (the weight; FORMULAS 5 says summons and mercenaries return the delay of that weapon rank, `0x4feeb0`, `0x5001d0`), stats 0x20, attacks 0x38/0x3C, passives 0x94/0x98, cost 0xAC, contract 0xB0, unlock flag 0xB4. Confirm the passive at 0x98 is applied as the engine applies it (`UnitFactory.BuildGuest`: only attacks flagged passive). |
| P1.5 | Summon forms (`SealScrollData`, `tools/summon_data.py`): stat factors, level, rank, attacks, script; FORMULAS 11. |
| P1.6 | Dolls (`tools/doll_data.py`): FORMULAS 11.1, 16.5 (a copy of the owner, HP 9,999). |
| P1.7 | Skills of the player (`SKILL_LAYOUTS` in `tools/extract_vanilla.py`): per level TP, speed, chant speed, effect values and kinds, target code, reach, weapon codes. |
| P1.8 | Items, equipment, enchantments, unique skills, party skills: the fields the engine reads (grep `Loader.cs`). |
| P1.9 | The variant: for every table of `balance_changes.xlsx` that the engine models, `gamedata/variant.py` must change the same field that `tools/balance_values.py` writes in the game file. List the tables and fields of each, side by side. Any field written in the game but not applied in the model (or the reverse) is a MISMATCH. |
| P1.10 | Spot check: pick 3 enemies, 3 attacks, 3 guests, 3 skills at random (write the seed or the choice) and compare the snapshot values with the bytes of the game file read by the readers. |

### Phase 2. Building the battle

| ID | Item |
|---|---|
| P2.1 | Stats of a member (FORMULAS 10, 10.1, 10.4, 12.17): growth row, class modifiers, equipment, crown, the weapon rank weight. |
| P2.2 | The summon of the grand sealbook (FORMULAS 11): stats from the owner and factors, HP (A06), level, rank, script, passive; built at `0x449771`, number 3000. |
| P2.3 | A hired guest (FORMULAS 16.5): built at `0x449839` from the character object `[0x71fc24]+0x1424` (`0x449879 call 0x435890`), number 3001 (`0x449892`). Which stage the bar offers (`0x58adb0 - 0x58b060`; sheet `MercenaryUnlocks`). The engine gives her `hp 9999` and `Kind.Summon`: list everything the engine does with that HP (damage taken, refills, death checks, heal targets, HP ratio in AI sources) and what the program does (she has no HP: `0xAC` is the hire gold). |
| P2.4 | Dolls at creation (FORMULAS 11.1): stats, HP, number, what they inherit (enchantments, passives). |
| P2.5 | Rows and formation: who is front and back, for the party and for enemies; the share table of 9.1. |
| P2.6 | Start of battle (FORMULAS 5 and 16.5, `0x449130`, `0x449194`): member and enemy gauges `((a number below 500) + 1) / 1000`, summon and guest "at the value of a plain action", one battle in five random order `(n < 93)/100`, ambush, effect 300. Engine: `Battle.Start`. Check every kind gets the program's rule, and the order of the draws if it matters. |

### Phase 3. Order of turns

| ID | Item |
|---|---|
| P3.1 | The formula of FORMULAS 5 (`0x4499d0`): base, weight term, F1, F2, slow, the random r, the 0.92 cap. Engine: `Battle.Wait`, `F.TurnValue`. Every constant and its rounding. |
| P3.2 | The stat used: AGI; INT or RES while chanting (by a flag of the skill, `0x449b4c`). |
| P3.3 | Buffs and enchantments of speed: the lists of FORMULAS 5 (168, 217, 221, 261 under 40% HP, 201, 340, 276, 277, 316; chanting 214, 265, 281; enchantments 51 - 56 and their caps at ±0.5); effect 298. |
| P3.4 | Defend (×1.15) and escape (×1.20); which actions count as a plain action. |
| P3.5 | The weight of a summon and a guest (their rank) and of an enemy (float at 0x44). |
| P3.6 | Who acts when two units are due at the same time (ties): the program's order and the engine's (`NextAction`). |
| P3.7 | Turn denial: petrify, sleep, paralysis 30/100, Warning Shot, Magnificent Steps (FORMULAS 16.5, `0x436c40 - 0x436d4c`); `Deny`, `LostTurn`. |

### Phase 4. Choice of action: enemies, summons, guests (FORMULAS 9)

| ID | Item |
|---|---|
| P4.1 | The choice loop (`0x430f10`): set 0 at the start of every turn; weights copied back; commands before the first set run in order until one decides; roll in the weights of the current set; commands of the set; a set switch marks the set done and rolls again. Engine: `Ai.Choose`, `Ai.Run`. Is there a limit on switches in the program? The engine has `MAX_SWITCHES = 8`: find the program's equivalent or classify it. |
| P4.2 | Every command 1 - 15 (table in FORMULAS 9): condition and arguments, against the engine's `Passes`/`FinalResult` branches. `engine_coverage.json` `ai.commands` lists those with a branch. |
| P4.3 | Every source 0 - 11 (jump table `0x432fa0`): who is "an ally", "an opponent" for the source (candidates below 2000? the unit itself? the guest's own HP ratio, always full?). Engine: the sources in `Ai.cs`. |
| P4.4 | Every target kind 0 - 15 of command 1 (jump table `0x434754`, function `0x433350`): the candidate list the program builds (`0x43af10` / `0x43b1d0`), the order, ties (first or last?), what happens when none qualifies. Engine: `Ai.PickByKind` (uses `battle.AlliesArray`, which **includes** summons, dolls and guests, and `MinBy` keeps the **first** on ties). |
| P4.5 | Lifetime of a command 1 target: per choice (fixed 2026-10-18). Verify the fix covers every path (silence, freeze, shadow bind replacing the choice; a unit with no script; a unit with no attacks). |
| P4.6 | "Once" commands (first byte of the tail) and "stop after a switch" (second byte): lifetime of the once flag (per battle?). Engine: `unit.OnceDone`. |
| P4.7 | Silence, freeze and shadow bind replace the choice with slot 0 (`Ai.Choose` checks statuses 117, 114, 123): check the ids and that the program does the same for a summon and a guest. |
| P4.8 | Attacks chosen by id (`0x8000 + id`) versus by slot (`0x4000 + n`): both paths. |
| P4.9 | Double and Triple Action of enemies (FORMULAS 12.14): after an action, roll for two actions, failing that for three. |

### Phase 5. Targets (FORMULAS 9.1, 12.12)

| ID | Item |
|---|---|
| P5.1 | The candidate builder `0x43e6d0`: number below 2000, side flag, row mode (0x79), the extra check through `[vtable+0xe8]` and the flag that enables it, the optional sort/shuffle `0x440d10`. List every caller and the arguments each passes. |
| P5.2 | Every scope 0 - 15 in `0x43f450` (two jump tables `0x43fde8`/`0x43fdf4` and `0x43fe04`): single, random (per hit), row, pierce, all; ally, random ally, ally row, allies, self, no target, 12, 14 everyone, 15 anyone. For each: target given and valid / given and invalid / not given; party side / enemy side. Engine: `Battle.Targets`, `OwnSidePick`, `PickOpponent`, `WeightedPick`. |
| P5.3 | The weighted pick of an enemy on the party (`0x43f7e9`, `0x505ad0`): weights by position (table `0x6517a0`), provoke (170), enchantments 49/50, minimum 10. Which units are candidates (dolls and summons never). |
| P5.4 | Piercing (`0x43fa64`, lists at `0x43def0`) and rows. |
| P5.5 | Cover (171) and redirections: who can cover whom; does a guest or a summon ever cover or get covered? |
| P5.6 | A target that dies between the choice and the hit; a multi-hit action whose target dies mid-action. |
| P5.7 | Effects that list targets themselves (EXTRA_TARGETS, the random moves, songs and dances that hit the whole party): which units they reach (members only?). |
| P5.8 | `T.ALLY_MOST_TP_LOST` (code 12) in the engine: is it a code of the program or an engine invention? |

### Phase 6. Hit and damage

| ID | Item |
|---|---|
| P6.1 | Physical hit chance (FORMULAS 2.1). |
| P6.2 | Physical attack value, defence value, damage (2.2 - 2.4), with every modifier's id and where it adds. |
| P6.3 | Magic attack (3, 16.5): attack B, attack C, element boosts, hit terms, defence modifiers, doll spells. |
| P6.4 | Critical hits (4): rate, factor, effect 70, effect 110, Critical Magic (301). |
| P6.5 | Number of hits (12.2, `0x417cd0`), Double and Triple Attack (16.5). |
| P6.6 | Special damage (12.3): fixed, share of HP, the cap 296. |
| P6.7 | Race, element and zone factors (2.5 zones, `0x44fbb0`); full HP bonus. |
| P6.8 | The enemy formula as used by a summon and a guest: their attacks are `EnemyAttackData`; check that the attacker side of the formula is the same function the program calls for units 3000/3001, and what "weapon" or "swing" they have (the engine gives them `swing 0`). |
| P6.9 | Rounding: where the program cuts to an integer, in which precision (single) and order. |
| P6.10 | Chant interruption (2.5): rate, Concentrate (264), the X14 patch of the variant. |

### Phase 7. After a hit, counters, follow-ups

| ID | Item |
|---|---|
| P7.1 | Counter (250, `0x422553`): the hit is void and the target counters. Engine: `Voided`/`Counter`. |
| P7.2 | Reprisal (249, `0x424689`): FORMULAS 12.13 says "counter **when the action ends**"; the engine calls `Counter` **at once** inside `AfterHit` (Battle.cs, `if (target.Has(249) ... Counter(target, unit)`). Settle the timing: the flag `[esi+0x45]` set at `0x424711` and where it is consumed (`_SetupCounter 0x425930` builds the counter aimed at the attacker, `0x425a34`). A multi-hit action can be answered once per hit or once per action: which? |
| P7.3 | Counter Whip (0x4203b1), Support Shot (0x424c42), Absolute Attack (307). |
| P7.4 | A counter aimed at a summon or a guest (they cannot be picked, but a counter is aimed at the attacker): what the program does with the hit (does it land? does it deal damage? to what HP?). In the engine the guest takes the damage and, in traces, recovers exactly the same amount right after (`H7>6=1;L6-536;D7>6=536;R6+536`): find the code that restores it, and check it against the program. |
| P7.5 | Dark Aura (262), Ecstasy (312), slow on hit (293), the effects of 12.9: each one's condition, target and duration; which of them can apply to a guest, a summon or a doll. |
| P7.6 | Damage received (12.7, 16.6): waking, ending chants, songs, dances and dolls; stun (16.5). |

### Phase 8. Statuses

| ID | Item |
|---|---|
| P8.1 | Application of a status (kind 5): duration from the action (float to int), who is the source. |
| P8.2 | Stacking (12.18, `0x4f9b72`): a status of the same effect replaces the old one even if weaker; petrification below its third stage is the exception. Engine: `SetStatus`. Check every path that adds a status uses the same rule. |
| P8.3 | Ticks (12.15, `0x4363bc`, states at `0x439820`): when a status loses a turn, which statuses tick at the bearer's turn and which at the source's, the ones that end at a sleeping bearer's tick (slot 0x8c), base method `0x48bc50`. |
| P8.4 | Ailments against resistance (5b): the formula, the element of each ailment, immunity bits (5c), blocked when already present. |
| P8.5 | Recovery from an ailment (16.5): starts at the turns figure of the action, +10 per failed check. |
| P8.6 | Poison (16.4, 12.5): the share, the cap 296, ticks. Engine constant `POISON_SHARE = 0.05`. |
| P8.7 | Stun, sleep, paralysis, petrify stages, freeze, silence, slow, shadow sew, turn delay (5c). |
| P8.8 | Dispel and strip buffs (74; `Dispellable`, `Dispel`): what counts as a buff. |
| P8.9 | Statuses that change stats (12.6, `0x4fbdd0`). |

### Phase 9. Healing and recovery

| ID | Item |
|---|---|
| P9.1 | Heal (6b, `0x48d730`, cap `0x48c5c0`): RES formula, the random table, passives 245 and 317, the cap 295. |
| P9.2 | Fixed healing (9), full heal (104), share heals (128, 131, 132), TP recovery (129, 426). |
| P9.3 | Revive (105, 16.5): who can be revived (members only?), HP given, when the revived unit acts next. |
| P9.4 | Who receives a heal of a guest, a summon, a doll, an enemy (rule 6 and the 2026-10-18 fix). |

### Phase 10. Songs, dances, dolls, chants

| ID | Item |
|---|---|
| P10.1 | Songs and dances (12.8, `0x48bf90`): slots, Solo Duet / On Stage / Double Puppet, what ends them (16.6). |
| P10.2 | Chants: start, speed (F2), interruption, what a stun or sleep does to them. |
| P10.3 | Dolls (11.1): creation, actions (`DollAction` picks a random hidden action and aims ally skills at the member with the lowest HP ratio: check against the program), magic scale (`DOLL_MAGIC_SCALE = 500`), removal (`RemoveDoll`, effect 350). |
| P10.4 | Guest dolls (`MakeGuestDoll`): Marion and Paracas use Catalina, Spartan, Oracles, Musiy (effects 146, 147, 228 - 230). What the program creates for a guest that uses these (a doll of the guest? numbered how?), and what the engine creates. |

### Phase 11. Other mechanics

| ID | Item |
|---|---|
| P11.1 | Items in battle (15, `0x50c596`): who can use them, targets, effects. |
| P11.2 | Random moves (12.10). |
| P11.3 | Steal (12.16). |
| P11.4 | Unique skills (12.19, 16.3). |
| P11.5 | Passives outside the damage formulas (12.11). |
| P11.6 | Sealbooks (16.1) and zones that forbid magic (16.2). |
| P11.7 | End of a battle (`Over`): when it is won or lost (members only? a party with only a summon and a guest alive?), escape. The engine's caps `MaxTime = 400` and `MaxActions = 3000`: model limits, say how often they end a battle (count `E` lines of a few long traces). |
| P11.8 | Effects with turns counted in actions of the source versus the bearer. |

### Phase 12. Assumptions and engine constants

| ID | Item |
|---|---|
| P12.1 | Every row of the sheet `Assumptions` (P0.5): read its address, settle it, verdict. |
| P12.2 | Every constant of section 3.1: its source in the program (address and quoted instruction) or MODEL-LIMIT with a reason. |
| P12.3 | Every literal in `Formulas.cs`: the same. |

### Phase 13. The player model (`Policy.cs`, sheet `Policies`)

This is not the game: it is how the project models a smart player. Check it is coherent, not that it matches a
program.

| ID | Item |
|---|---|
| P13.1 | Every rule of the sheet `Policies`: its condition and action are implemented as written (`Policy.cs`). |
| P13.2 | Targets the policy chooses for ally skills: always a member? never a summon, a doll or a guest (they are not candidates in the game, so a policy that aims at them is aiming at nothing)? |
| P13.3 | The policy and a guest: does any rule of the policy read the guest or the summon (HP ratios, buffs present) and act on them? A buff present on a guest must not stop a member from casting it on herself. |
| P13.4 | Buffs that would replace a stronger one (P8.2): does the policy avoid casting a weaker buff over a stronger one, and does it recast when a guest's weaker buff replaced a member's stronger one? |

### Phase 14. The measures (`Suite/`)

A measure turns battles into a claim ("this skill serves", "this mercenary adds 5 points"). Check each claim is
computed so that it says what it claims. Read each measure's code; do not run it.

| ID | Item |
|---|---|
| P14.1 | The paired comparisons (with / without, vanilla / variant): same seeds, same parties, same enemies on both sides. |
| P14.2 | Length metrics: computed on **won** fights only, and only when both sides have enough wins to read (the 2026-10-18 fix in the mercenary profile used `mercenary_profile_min_wins`). List every measure that compares lengths and how it handles few or no wins. |
| P14.3 | Thresholds and verdicts (`skill_battery` of `measure_config.json`: wins 0.08, length 0.03, hp 0.03, tp, alive, `good_share`): what a verdict means, and whether a saturated reference (a party that always wins) can make every candidate "good". |
| P14.4 | Rounding in reports: a figure printed as "4" that is 3.6, components rounded separately then added (the mercenary table did this). |
| P14.5 | The recorder: who a damage, a heal, an action is credited to (a doll's damage to the doll, to its owner, to "members"?). |
| P14.6 | Noise: for each measure, the number of runs and the size of the effects it reports; flag any claim smaller than its noise. |

---

## 7. Leads already known (start with these)

Settle these first, inside their phase, and mark them "lead" in the result file.

1. **P7.2 Reprisal timing**: engine counters at once; FORMULAS says when the action ends.
2. **P7.4 Damage to a guest or summon and its refill**: where `R6+536` comes from; whether the program deals damage to
   units 3000/3001 at all.
3. **P4.4 Target kinds of command 1** use `AlliesArray` (with summons, dolls and guests) and keep the first on ties;
   the program builds its own list (`0x433350` calls `0x43af10` or `0x43b1d0`). The same three questions as the
   2026-10-18 fix: membership, ties, empty list.
4. **P4.3 Sources of AI conditions** ("lowest HP ratio among allies", "an ally with an ailment", ...): same membership
   question; a guest whose own HP ratio is always 1.0.
5. **P5.2 Scope 6 (random ally) with a target given**: the program uses the given target (`0x43f5c2`); the engine
   ignores it.
6. **P13.2 / P13.3** policy and guests.
7. **P2.3** every use of the 9,999 HP of a guest or summon.
8. **`Battle.cs` effect 350** removes every doll **and summon** of the opposing side: check the program's list for
   that effect (does it remove the summon? a guest?).
9. **P10.4** guest dolls.
10. **P11.7** a battle where every member is down but the summon or a guest is "alive".

---

## 8. The result file: `docs/result_engine_audit.md`

Create it at the start with the header, then append items as they are settled.

### 8.1 Header

    # Engine audit: results
    Commit: <hash>   Date: <date>   Auditor: <agent and model>
    Baseline: build <ok/fail>, golden <line>, tests <count>

    ## Summary
    | Phase | Items | MATCH | MISMATCH | PARTIAL | MODEL-LIMIT | UNREAD | N/A |
    |---|---|---|---|---|---|---|---|
    (one row per phase, filled at the end; a final row of totals)

    ## Mismatches by severity
    (filled at the end: every MISMATCH and PARTIAL, S1 first, one line each with its ID)

### 8.2 One item

    ### P5.2 Scope 6 (random ally) with a target given   [lead]

    **Rule.** <one sentence; FORMULAS section quoted or "FORMULAS is silent">

    **Cases.**
    1. target given and a candidate
    2. target given and not a candidate
    3. no target
    ...

    **Program.** <function and range>. Command: `python tools/exe_dis.py 0x43f450 0x43f900`
    ```
    <the decisive lines, copied from the output>
    ```
    Case 1: <what these lines do, line by line>. Case 2: ... Case 3: ...

    **Engine.** `engine_cs/src/DtEngine/Battle.cs:986`
    ```
    <the lines, copied>
    ```
    Case 1: ... Case 2: ... Case 3: ...

    **Trace** (if one was made). Job: `<json>`. Lines: `<copied>`

    **Verdict.** MATCH | MISMATCH | PARTIAL | MODEL-LIMIT | UNREAD | N/A
    **Severity** (MISMATCH, PARTIAL). S1 | S2 | S3, and why.
    **Reach.** <which data uses this case: counts from the snapshot, with the command used>
    **Proposed fix** (not applied). <the change, in words and in a sketch of code>
    **FORMULAS.** <unchanged | must be corrected: the sentence and the correction>
    **Open questions.** <what is left, if anything>

### 8.3 Verdicts

| Verdict | Meaning |
|---|---|
| MATCH | Every case read in the program and in the engine, and they agree. |
| MISMATCH | At least one case differs. |
| PARTIAL | Some cases agree, some could not be read. Say which. |
| MODEL-LIMIT | The engine deliberately does something the program does not, for a stated reason (a cap that stops endless battles, a mean in place of a roll in an expectation). Cite where the reason is written, or write it. |
| UNREAD | The program's code could not be followed to a conclusion. Say where it stopped. |
| N/A | The mechanic is not in the battles the project models (out of battle, DLC). Say why. |

### 8.4 Severity

| Severity | Meaning |
|---|---|
| S1 | Changes results broadly: many battles, many units, or a rule every battle uses (turn order, targets, damage). |
| S2 | Changes a class of battles or units (a family of enemies, the guests, dolls, a status). |
| S3 | Rare or small: a corner case, a rounding that moves no result. |

---

## 9. Order of work and stopping

* Phase 0, then the leads of section 7, then phases 1 - 14 in order. Within a phase, items in order.
* After each phase, update the summary table in the result file.
* If an item takes very long, write PARTIAL or UNREAD with where it stopped, and go on. Come back to it at the end if
  there is time.
* At the end: the summary filled, the list of mismatches by severity, and a count that every ID of section 6 (plus
  the ones added) appears once. Write that count as the last line: `Items: N listed, N written.`

## 10. What not to do (seen before)

* Do not write "verified" for something only searched. Searching an address is not reading it.
* Do not trust a range that decodes as `lcall` or `into`: it is misaligned or data.
* Do not take the behaviour of the engine as evidence of the game.
* Do not take a sentence of FORMULAS as evidence of the game when the item is about a case that sentence does not name.
* Do not run batteries or the suite to "see if it matters"; size an effect by counting the data that uses the case.
* Do not edit anything but the result file. Do not commit.
