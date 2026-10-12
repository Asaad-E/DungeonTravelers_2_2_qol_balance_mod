"""One-off edit of 2026-10-12 for the publication: the documents that stay are brought up to date where they named a
document that left, a state that is over, or a tool that no longer exists. Kept as the record of what was changed."""
import io
import os

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'docs')
NL = chr(10)


def read(name):
    return io.open(os.path.join(DOCS, name), encoding='utf-8').read()


def write(name, text):
    io.open(os.path.join(DOCS, name), 'w', encoding='utf-8', newline=NL).write(text)


def swap(text, pairs, name):
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit(f'{name}: {text.count(old)} matches of {old[:70]!r}')
        text = text.replace(old, new)
    return text


def between(text, start, end, new, name):
    """The text from the line that starts with `start` up to the line that starts with `end` (kept), replaced."""
    a = text.index(NL + start) + 1
    b = text.index(NL + end, a) + 1 if end else len(text)
    return text[:a] + new + text[b:]


# --- BALANCE_PLAN.md: the documents it names that left ---------------------------------------------------------
t = read('BALANCE_PLAN.md')
t = swap(t, [
    ("It replaces nothing yet: `COMMUNITY_BALANCE_COMPLAINTS.md` stays as the survey of what players feel, "
     "`CONSOLIDATED_BALANCE_PROPOSAL_AND_FEASIBILITY.md` stays as a list of ideas (its author marks it provisional, and "
     "section 1 below corrects three of its premises).",
     "Two earlier documents it started from, a survey of complaints and a first proposal of changes, left the repository "
     "on 2026-10-12: every complaint is now a row of the register with its source, and every change a row of "
     "`balance_changes.xlsx` (section 1 below corrects three premises of that first proposal)."),
    ("| Japanese community (`COMMUNITY_BALANCE_COMPLAINTS.md`) | What players feel. Each complaint is a row of the register |",
     "| Japanese community (the atwiki of the game; `docs/CREDITS.md`) | What players feel. Each complaint is a row of the register, with its page |"),
    ("| The earlier proposal (`CONSOLIDATED_BALANCE_PROPOSAL_AND_FEASIBILITY.md`) | Ideas to test.",
     "| The earlier proposal (a document of 2026-10-04, since removed) | Ideas to test."),
    ("and the table for the user is" + NL + "   `docs/THEME_TABLES.md`.",
     "and the table for the user was" + NL + "   `docs/THEME_TABLES.md` (removed on 2026-10-12, every theme decided)."),
    ("all still open for the user's decision; the tables are in `docs/THEME_TABLES.md`.",
     "all still open for the user's decision at that date; the tables were in `docs/THEME_TABLES.md`."),
], 'BALANCE_PLAN.md')
write('BALANCE_PLAN.md', t)

# --- philosophy.md ---------------------------------------------------------------------------------------------
t = read('philosophy.md')
t = swap(t, [
    ("Address the biggest complaints of Japanese players about the game, as collected in `COMMUNITY_BALANCE_COMPLAINTS.md`.",
     "Address the complaints of the Japanese players and the criticisms of the English guide, each one a row of the "
     "register (`data_tables/balance_criteria.xlsx`, sheet `Criticisms`) with the page it comes from."),
    ("It must address a complaint documented in `COMMUNITY_BALANCE_COMPLAINTS.md`",
     "It must address a row of the register of complaints (sheet `Criticisms`)"),
    ("   - That document records what players perceive, not what the engine does.",
     "   - The register records what players perceive, not what the engine does."),
    ("**Order of work.** QoL first, until it is right. Balance afterwards.",
     "**Order of work.** QoL first, until it is right (closed on 2026-10-04). Balance afterwards (`BALANCE_PLAN.md`)."),
], 'philosophy.md')
write('philosophy.md', t)

# --- SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md -------------------------------------------------------------
t = read('SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md')
t = swap(t, [
    ("**Applicability:** Data tables (`skills.xlsx`, `qol_skill_text.xlsx`), injection scripts (`pck_handler.py`, `apply_mod.py`), and multi-agent development pipelines.",
     "**Applicability:** the skill text of both variants: `data_tables/qol_skill_text.xlsx`, `data_tables/balance_skill_text.xlsx`, "
     "the labels of `data_tables/qol_rules.xlsx`, and the tools that write and check them (`tools/generate_qol_skill_text.py`, "
     "`tools/text_checks.py`, `tools/build_variant.py`)."),
], 'SKILL_DISPLAY')
write('SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md', t)

# --- QOL_ROADMAP.md: its last section ----------------------------------------------------------------------------
t = read('QOL_ROADMAP.md')
a = t.index(NL + 'Still open, needs the user: the play-through.') + 1
t = t[:a] + '''The QoL variant is closed. A text is still corrected, in both variants, when a reading of the program shows it wrong
(on 2026-10-12: the labels of four unique skills, and the box of Concentrate, which goes back to the sentence of the
game because the program gives the passive no effect; `FORMULAS.md` 2.5).

## The conditions of side events: looked at and dropped

Reopened on 2026-10-07 for one point, row S25 of the Balance register ("side events with conditions nobody can
guess"): whether the condition of each side event could be read from the data and shown somewhere in the game without
changing the program. Dropped by the user on 2026-10-12 before anything was built.
'''
write('QOL_ROADMAP.md', t)

# --- dungeontravelers2-2.md: the technical reference ---------------------------------------------------------------
t = read('dungeontravelers2-2.md')
t = swap(t, [
    ("# Dungeon Travelers 2-2 (PC): what was done, how, and how to continue",
     "# Dungeon Travelers 2-2 (PC): the technical reference"),
    ("Reference for agents and modders working on *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, Aquaplus / Sting engine). Read `philosophy.md` first for the reasoning, and `docs_example/` for the method this project copies.",
     "Reference for modders working on *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, Aquaplus / Sting engine): the file formats, the text system and its limits, and the rules the text of the mod follows. Read `philosophy.md` first for the reasoning." + NL + NL +
     "Sections 3 to 7 and 9 were written while the QoL variant was built (2026-10-04) and hold for both variants; the counts they give are those of that day. Where the work stands is in `QOL_ROADMAP.md` (QoL, closed) and `BALANCE_PLAN.md` section 7 (Balance). The battle formulas are in `FORMULAS.md`."),
    ("Language of chat with the user: Spanish. Everything in the repository: English." + NL, "Everything in the repository is in English." + NL),
], 'dungeontravelers2-2.md')
t = between(t, '## 1. Deliverables', '## 3. Data layout', '''## 1. Deliverables

The mod ships as **two variants that are built separately**, from the same tools and the same text template.

| Variant | Goal | May change game values | State |
|---|---|---|---|
| **QoL** | Everything the player needs to make an informed decision is in the game, clean, understandable and easy to read. | No. Every figure shown is the original one. | Closed (`QOL_ROADMAP.md`). |
| **Balance** | Answer the complaints of the Japanese players and the criticisms of the English guide (the register: `data_tables/balance_criteria.xlsx`, sheet `Criticisms`), and show the figures of the changed game. | Yes: each change is a row of `data_tables/balance_changes.xlsx`. It also patches the program (sheet `ExePatches`). | Built and installed; in its final checks (`BALANCE_PLAN.md` section 7). |

`tools/build_variant.py <variant>` builds a variant into `build/<variant>/` and verifies it; `tools/install_variant.py`
puts it into the game, saving what it replaces; `tools/apply_mod.py` runs the whole chain (the README of the
repository tells it step by step).

---

## 2. Repository map

The layout, the workbooks and the tools are listed in `mod_project/README.md`. No file of the game is in the
repository: `backups/` is made by `tools/setup_backups.py` from a copy of the game.

---

''', 'dungeontravelers2-2.md')
t = between(t, '## 8. The earlier mixed build', '## 9. Mistakes made and corrected', '''## 8. The earlier mixed build

Before 2026-10-04 the project was one build that mixed text and value changes. An audit of it found figures in the
text that did not match the data, mechanics announced with nothing behind them, replacements that failed in silence
and boxes drawn over one another. It was removed with its tools and workbooks, and its lessons are the rules of
section 9 and of `philosophy.md`: a text is generated from the data of the variant it ships with, the build proves
every figure, and a step that cannot do its job stops the build.

---

''', 'dungeontravelers2-2.md')
t = between(t, '## 10. Not done / next', None, '''## 10. What is left

Nothing is listed here any more: what the QoL variant shows and leaves unshown, pack by pack and with the reason, is
`QOL_ROADMAP.md`; the state of the Balance variant and its known limits are `BALANCE_PLAN.md` section 7.
''', 'dungeontravelers2-2.md')
t = t.replace("its tools (`apply_mod.py`, `audit_tool.py`, `package_release.py`,", "its tools (an `apply_mod.py` of that time, which the present `tools/apply_mod.py` only shares its name with, `audit_tool.py`, `package_release.py`,")
write('dungeontravelers2-2.md', t)
print('documents updated')
