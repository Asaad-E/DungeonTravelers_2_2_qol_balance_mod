# Night worksheet, 2026-10-19 (working note of this machine, not in git)

Read this whole file after any reset of context before doing anything. It holds every requirement of the user's
message of 2026-10-19 (autonomous night: the user is away and will not confirm), his answers to three questions, the
order of work, and the state of each step. Update the column "State" and the notes under each step as work goes.

## A. What the user asked, in full (do not drop any point)

1. **Review the last contributions of the engine audit** (docs/result_engine_audit*.md, 99 items, 33 MISMATCH + 3
   PARTIAL). Verify in the binary the claims not yet verified before fixing.
2. **Correct the engine with the new data until everything is perfect, and verify it works** (dtcli golden, dotnet test,
   traces of the corrected cases).
3. **Make the audit permanent in the project**: a form where anyone can see that the engine is 1:1 with the binary
   (mechanic, address in the program, place in the engine, verdict, evidence), kept as a generated, checked document.
   **Delete everything else that makes noise** (the raw result files of the agents, AUDIT_AGENT_B_STATUS.md, agent scratch
   files, stale documents, the checklist of the old simulator).
4. **The Python simulator must cease to exist completely**: it only gives noise to agents. C# is final. Nothing that refers
   to it as alive may remain (tools/sim_coverage.py reads a coverage copied from it; docs that describe sim/ as current).
   Python stays only for readers of the binary and of the game files, building and installing the mod, and tests.
5. **FORMULAS.md and code comments were full of claims taken for granted that proved false in the assembly**: correct
   FORMULAS.md everywhere the audit showed it wrong; correct engine comments that cite addresses wrongly.
6. **Statistics of the measures (audit phase 14 critique)**: scans of 20 battles with thresholds of 3% length and 8% wins
   are inside Monte Carlo noise (binomial SE ~11% at N = 20); contested at 30 runs without confirmation; saturated
   reference parties (100% wins) make verdicts on noise. Fix: enough runs, confirmation passes, minimum wins to read a
   length, thresholds above the noise of each measure, no verdict from a saturated cell.
7. **Run all the simulations and obtain the new data** of everything that rested on the engine's results.
8. **If values change a little, follow the user's history of decisions and the philosophy of the project** to reach the
   desired state, which is similar to what the mod has now (now measured with an outdated engine). Balance changes are
   allowed tonight; nothing drastic, nothing that changes an identity; first try inside the current limits of the mod.
9. **Review the complaints (sheet Criticisms) and whether they are well closed**; propose and apply changes where needed,
   inside the scope of the project and inside the identities. Four rows are open (F89, S04, S16, F27; memory
   dt22-register-reopened) and category-3 rows must be re-confirmed on the corrected engine.
10. **Summons and mercenaries must fulfil their niche**: write an identity document for each summon and each mercenary,
    like docs/CLASS_IDENTITY.md for classes, so that tuning a niche never loses an identity. Not only stats: also their
    skills a little (ANSWER: no change of their attack lists; only stats and script weights). **Check that the AI plays
    well with them** (the party policy around them, and their own scripts). Added later by the user: **read all the
    in-game dialogue about each summon and mercenary** and put her personality and traits in her identity; it weighs
    little in the final decision.
11. **Effects of the grand sealbooks**: check that each effect makes sense and acts where it should (in the model and in
    the game); if an effect is weak, raise it without breaking the game. (Memory dt22-grand-sealbooks: Ghast dominates,
    Death Cataphract the worst battle book; exploration books judged by their summon only.)
12. **Places accepted as easier than vanilla**: evaluate them and bring them back into a range similar to vanilla, using
    the five battery parties as reference, for bosses and random battles. If a party does very badly, review the AI: it
    must not be perfect, but act like a moderately informed human, no stupid actions. Accepted easier only when it is not
    possible, when it would change a lot, or when the original is simply unfair or badly designed. **Anti-Meta-Plus is
    easier in the mod by design** (it uses classes that are very low in the original) **but must not be a win button.**
13. **Model the story bosses still missing** with specific strategies or concrete preparations from the Japanese guide
    (atwiki dt2-2) or the GameFAQs guide. Story only; postgame is separate. This closes the main part of the mod.
14. **Quest gold**: the raise was too big; a lighter raise (ANSWER: half of the current raise over vanilla).
15. **Mass run for broken combinations**, and not only by simulation (the AI cannot find a broken strategy): analyse
    every skill, class, character, book, mercenary, item and think of broken strategies, then test them. If a break
    exists in the original it may stay when fixing it would break the whole game; if it is trivial or easy it must be
    fixed. Not only against bosses: also breaking the economy, trivialising random encounters, gold, items, shop, forge
    (weak according to the criticisms) and the rest. Something that needs an immense grind does not matter much; something
    super easy that breaks the game does.
16. **At the end: update every report and chart and add them to the README if missing.** Send the user a summary of the
    changes made (to approve or iterate) and a summary of the project, saying what is left to review.
17. **Then a general review** that everything is well closed and nothing escaped; use the history of decisions and git
    to know what kind of mod this is.
18. **Gemini 3.8 Flash on high through the Antigravity CLI (agy)** may be used freely (no token worry) for repetitive
    work, texts, searching the binary, auditing for stale files and rubbish, global cleanup reviews, with super clear
    instructions because it hallucinates; do not depend on it much; verify what it returns.
19. **Organise the order so that work is not repeated**, since many changes act backwards (difficulty near the end;
    balance of classes / mercenaries / summons early).

## B. The user's answers (before starting)

* Mercenaries and summons: **stats and script weights only; their attack lists are not changed.**
* The executable **may be patched tonight** when the reading is certain and both program files are verified byte by byte.
* Quest gold: **half of the current raise over vanilla.**

## C. Rules that hold all night

* CLAUDE.md rules: nothing hardcoded (values in workbooks), binary first then JP guides, commits by explicit path, no push,
  neutral wording in tracked files, no game file in git, Python never writes regex/backslashes through a heredoc.
* The machine has 15 GB RAM and **must never page to disk**: every heavy run with the memory guard (kill above 7 GB),
  recorder runs in small batches.
* Balance changes: record each in balance_changes.xlsx with its reason and measure; list them for the final summary.
* Never claim a measure that was not run; report counts.

## D. Order of work and state

| # | Step (requirement numbers of A) | Done when | State |
|---|---|---|---|
| 0 | Housekeeping (3, 4): agent files and old-simulator pieces out | no reference to sim/ as current; raw audit files merged then removed | done except sim_coverage.py removal (after suite) |
| 1 | Review audit findings (1) | every MISMATCH/PARTIAL verified or reasoned | done |
| 2 | Fix the engine (2, 5) | each MISMATCH fixed or justified MODEL-LIMIT; golden recorded; tests pass; traces of corrected cases | done 43ec275 |
| 3 | Permanent conformity (3, 5) | docs/ENGINE_CONFORMITY.md generated + checked; FORMULAS.md corrected; raw files gone | data + tool + FORMULAS done; commit pending |
| 4 | Statistics of the measures (6) | measure_config and measures fixed; verdicts above noise | code done (Noise helper); suite running |
| 5 | Full suite = new baseline (7) | suite passes; what moved listed | |
| 6 | Roster identity docs (10) | docs/ROSTER_IDENTITY.md (every summon, every mercenary) | written (dialogue read) |
| 7 | Mercenaries and summons niches, AI around them (8, 10) | every mercenary in band; summons by niche; policy checked | |
| 8 | Grand sealbook effects (11) | weak battle enchantments raised; exploration ones checked | |
| 9 | Exploits (15) | report: each finding fixed or kept with reason | |
| 10 | Story bosses modelled (13) | every story boss with its guide preparation/strategy or a reason | |
| 11 | Difficulty back toward vanilla (12, 8) | curve and party battery in band; Anti-Meta-Plus not a win button; AI sane | |
| 12 | Quest gold (14) | rows at half the raise | done dbeffb5 (x1.20) |
| 13 | Register (9) | 0 open; category-3 rows re-confirmed | |
| 14 | Reports, charts, README, summaries (16) | all regenerated; summary sent | |
| 15 | General review (17) | nothing left loose | |

## E. Notes as work goes

* Audit: 99/99 items, 33 MISMATCH, 3 PARTIAL (checker 0 failing).
* Verified in the binary tonight: silence blocks spells (bit 2 of the attack flags, slot 0xc0 of the unit class), freeze
  blocks techniques (bit 1, slot 0xb4), shadow sew always (slot 0xd0); P4.1/P4.2/P4.6 read by the agent with lines.
  The after-hit answers (0x423cd0: Dark Aura, Slow Target, Reprisal) are skipped whole when the attacker is a doll, the
  summon or a guest (0x423d0e - 0x423d38): agent B's open note on Reprisal was wrong.
* Engine fixes done so far: AI (Ai.cs) P4.1, P4.2, P4.3, P4.4, P4.6, P4.7, P4.8 (+ export of the technique flag and the
  stop tail); targets P5.2, P5.5, P9.3 (105/106 candidates include the fallen); after-hit P7.2, P7.3 (Counter Whip),
  P7.5. Kept as model limits: P5.1 (no petrification stages in the engine), P5.3 (same distribution).
* Engine conformity: data_tables/engine_conformity.json (99 items: MATCH 62, FIXED 29+3 P14, MODEL-LIMIT 5) and
  tools/engine_conformity.py (checks addresses and engine methods). Raw audit files and 110 agent scratch files deleted.
* Statistics: Noise helper (Common.cs): paired SE, bar = max(threshold, z*SE), length only with min_wins both-won;
  applied to skill/mercenary/sealbook/unique batteries (Judge), contested (100 runs), support battery (100 runs),
  win-rates (independent shares), mercenaries, unique-skills. skill_battery scan 40, confirm cells 5.
* First mercenary profile on the corrected engine (points = wins + shorter): Estelle 3.6 (below 4), Euthys 10.2 (above
  8), Peggy & Beard 2.6 on 6 cells; the rest in band.
* Dialogue for roster identity: profiles in NPC.pck (UTF-8 lines), ShopBar.pck advice, dungeon packs stNN for
  mutant scenes. Scratch dump script in the session scratchpad (dump_text.py).
* Full suite on the corrected engine (2026-10-19 00:10, 1336 s, 9 of 9): skill battery 54 good / 170 niche / 23 dead
  (was 127 / 107 / 8): of 16 newly dead, 6 by the engine (Armor Penetration, Bash Guard, Stab Guard, Ether Strike, Heal
  Mastery, Life Bringer), 8 by the honest statistics (their old best cells were noise or about 3%). Confirm runs 400 now.
  Unique battery 2 good / 15 niche / 1 dead (Tranquil Song). Curve 36/44 (7 easier: C14 C15 C29 C32 C37 P08 P24, 1 harder
  C08 pressure). Party battery 78/85. Guide curve: story all within but C29 (read: policy gap); 6 postgame unread.
* Mercenaries tuned (balance_changes rows N050-N059, N091-N092, N130-N134): Euthys ATK/INT x0.78, Estelle AGI x1.25,
  Peggy & Beard INT x1.1 ATK x1.05 (trials: 7.5-8.2, 4.7, 4.9 points).
* C29 Calliope: Policy condition enemy_named (Policy.cs, not built yet while the battery runs); rules '*' 2-4 in sheet
  Policies: silence, paralysis, slow on Calliope (atwiki page 227).
* STOP 2026-10-19 (usage limit), commit db97660. Next, in order: (1) the enchantment 296 (not found by push+0xf0) and 272
  (0x44ee3d) still to read and model; 265 read at 0x48d1e0 (recovery every 5 ticks, 2 with it, when context +0x40 is 0:
  likely the map) to confirm and list under sealbook_outside_battle. (2) Sealbook battery again (enchantments now act),
  then settle Ghast/Eros (ATK x0.85 rows F004-F008 under trial) and Death Cataphract (P092 second enchantment 219).
  (3) Full suite (skill battery with "unclear" + settle 1600 runs), commit the reports. (4) Steps 9 exploits, 11
  difficulty toward vanilla (easier: C14 C15 C32 C37 P08 P24), 13 register (F89 S04 S16 F27; unique-gear-trial for S16),
  6 postgame curve rows unread, 14 reports/README/summary, 15 review. Rows F/P092 and Euthys/Estelle not yet in a build
  installed in the game.
* END OF NIGHT (final pass committed): steps 0-14 done; open for the user: 14 dead skills (5 not fixable by value:
  Backward Swing, Ether Strike, Halving Slice, Life Bringer, Warm-Up), 38 confirmed drops of Maid-less parties at C30/C34/
  C38, Etoile and Witch "too fast" in class balance, Euthys cut deep, nothing installed in the game yet.
