# Combat Simulation AI Rationale

This document explains why the automated combat simulator (`engine_cs/`, `tools/full_suite.py`) operates with full knowledge of enemy stats and damage formulas.

---

## 1. Differential A/B Benchmarking

The simulator exists to perform rigorous differential regression testing between the base game (Vanilla) and the Balance variant:

$$\Delta = \text{Metric}_{\text{Mod}} - \text{Metric}_{\text{Vanilla}}$$

To isolate the impact of balance changes, both versions are evaluated under identical conditions:
* The exact same party compositions and gear tiers.
* The exact same decision-making policy.
* The exact same random number seeds.

If an optimized meta party finishes a checkpoint with a 100% win rate and nearly identical turn counts in both versions, it confirms that the baseline difficulty curve remains intact. If an underperforming off-meta party jumps from a 5% win rate in Vanilla to 85% in Balance, the improvement is due to resolved mechanical bottlenecks (such as TP starvation or excessive action delays), not inconsistent evaluation.

---

## 2. Preventing Artificial Noise

Introducing artificial ignorance or human-like mistakes (such as misjudging elemental affinities or picking suboptimal skills) introduces high stochastic variance:

* If a party fails because an artificial heuristic randomly cast a basic attack instead of an essential heal, the loss reflects test noise rather than the balance of the encounter.
* By having the AI execute optimal turn planning, **every combat failure is guaranteed to be a structural mechanical issue**: insufficient DPS, unavoidable turn-1 wipes, or unsustainable resource exhaustion.

---

## 3. Human Playability Margin

A fully informed simulation policy provides clear thresholds for in-game viability:

* Archetypes considered viable in the Balance mod achieve 75% to 100% win rates in the test battery with healthy remaining party HP.
* This high ceiling provides a wide safety margin, ensuring that even with normal human hesitation or imperfect tactical choices, the party remains practical and enjoyable during actual playthroughs.
