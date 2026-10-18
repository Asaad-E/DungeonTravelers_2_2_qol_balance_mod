# Project Documentation Index

This directory contains technical references, specifications, and architecture notes for the *Dungeon Travelers 2-2* mod project.

To install the mod, refer to the main [README.md](../README.md).

---

## Core Documentation

| Document | Description |
|---|---|
| [philosophy.md](philosophy.md) | Core design principles, variant separation, and engineering standards. |
| [FORMULAS.md](FORMULAS.md) | Reverse-engineered combat formulas with decompiled executable offsets. |
| [CLASS_IDENTITY.md](CLASS_IDENTITY.md) | Intended class roles, niches, and skill toolkits across all progression tiers. |
| [SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md](SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md) | Tooltip layout guidelines, screen width limits, and formatting standards. |
| [SIMULATOR_AI_BENCHMARK_PHILOSOPHY.md](SIMULATOR_AI_BENCHMARK_PHILOSOPHY.md) | Rationale behind the simulation engine's optimal AI policy for A/B testing. |
| [dungeontravelers2-2.md](dungeontravelers2-2.md) | Technical reference for binary container formats, memory layouts, and struct offsets. |
| [QOL_ROADMAP.md](QOL_ROADMAP.md) | Verification checklist and package breakdown for the QoL variant. |
| [BALANCE_PLAN.md](BALANCE_PLAN.md) | Balance methodology, complaint triage, and progression milestones. |
| [CREDITS.md](CREDITS.md) | Data sources, community references, and external walkthrough citations. |
| [generated/](generated/) | Automated benchmark reports, coverage audits, and balance test results. |

---

## Directory Overview

```text
data_tables/       Spreadsheets defining all gameplay parameters, rules, and text strings
tools/             Python utilities for extraction, binary rebuilding, and text validation
engine_cs/         High-performance C# combat simulator and benchmark test harness
gamedata/          Data readers and binary layout definitions used by build scripts
installer/         Release package assets, batch scripts, and user documentation
measures/          Scripts and datasets supporting specific balance adjustments
tests/             Automated test suite (binary round-trips, layout bounds, text verification)
docs/              Technical specifications and design documentation
backups/           Local unmodified game files used as build references (not tracked in git)
build/, dist/      Generated binary outputs and packaged release archives (not tracked in git)
```

---

## Primary Spreadsheets (`data_tables/`)

All gameplay adjustments, text revisions, and rule definitions are maintained in spreadsheets:

* `vanilla_source_of_truth.xlsx`: Decoded baseline game parameters.
* `balance_changes.xlsx`: Register of all balance modifications, specifying modified fields, baseline values, new values, and design rationale.
* `balance_criteria.xlsx`: Community feedback logs, risk categories, executable patches, and effect mechanics.
* `qol_rules.xlsx`: Text templates, magnitude descriptors, and layout boundaries.
* `qol_*_text.xlsx`: Sourced text definitions for skills, items, enchants, attacks, and meals.
* `balance_*_text.xlsx`: Specialized text overrides for rebalanced skills and items.

---

## Common Development Commands

```bash
# Build and apply a variant locally
python tools/apply_mod.py balance
python tools/apply_mod.py qol

# Run the Python test suite
python -m unittest discover -s tests -p "test_*.py"

# Run full balance benchmark battery and generate charts
python tools/full_suite.py

# Package release archives to dist/
python tools/package_all.py
```
