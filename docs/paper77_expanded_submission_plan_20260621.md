# Paper 77 Expanded Submission Plan

Date: 2026-06-21

Goal: rebuild Paper 77 into a serious 25+ page ICLR-style submission artifact while preserving hostile-review honesty. The paper is already `KILL_ARCHIVE`; v5 may only improve to `STRONG_REVISE` if a redesigned fixture-inference method survives the frozen local gates. It remains `KILL_ARCHIVE` if stronger baselines still beat it.

## Current State

- Current version: v4.
- Current terminal decision: `KILL_ARCHIVE`.
- Current PDF: 5 pages.
- Current decisive split: `combined_fixture_stress`.
- Current proposed success: 0.671 +/- 0.056.
- Current strongest non-oracle baseline: `prototype_system_id` at 0.771 +/- 0.082.
- Current paired success difference: -0.100 +/- 0.086.
- Current failure modes: lower fixture accuracy, worse parameter error, higher force violation, more damage, more repeated failures, and weaker stress robustness.

## Plan-First Freeze

Before interpreting final results, freeze:

- Seeds: 0 through 7.
- Fixture families: free, clamp, hinge, slot, suction, tether.
- Splits: nominal visible fixture, hidden clamp/hinge, slot axis shift, adhesive/tether fixture, combined fixture stress.
- Aggregate hard-regime splits: hidden clamp/hinge, slot axis shift, adhesive/tether fixture, combined fixture stress.
- Gridless continuous probe benchmark with 12 probes per scenario by default.
- Evaluation scenarios per split: 14.
- Ablation scenarios: 10.
- Stress scenarios: 8.
- Fixed-risk scenarios: 8.
- Stress levels: 0.00 through 1.20 in seven steps.
- Risk budgets: 0.08, 0.12, 0.18, 0.25.

## Method Upgrade

Add `latent_fixture_inference_v5` as the only new proposed method.

It may combine:

- structured compliance anisotropy features,
- torque/rotation signatures,
- release and recoil cues,
- hysteresis memory,
- calibrated prototype likelihoods,
- particle refinement,
- fixture-conditional action safety margins,
- ambiguity-aware cautious probing,
- energy/damage-aware action selection.

The method must remain CPU-only and RAM-light: no neural training loops, no large tensors, no GPU assumptions, and no in-memory explosion beyond small NumPy arrays and CSV checkpoints.

## Strong Hostile Baselines

Keep all v4 baselines and add stronger non-oracle competitors:

- `calibrated_prototype_system_id`
- `random_forest_probe_classifier`
- `bayesian_fixture_belief`
- `robust_impedance_planner`
- `adaptive_probe_then_act`
- `ensemble_uncertainty_planner`
- `particle_filter_fixture`
- `prototype_system_id`
- `oracle_fixture`

The gate compares ACD-v5-style fixture inference against the strongest non-oracle baseline, not against weak strawmen.

## Evaluation Gates

The paper can only remain alive if all local gates pass:

- main success margin against the strongest non-oracle baseline on `combined_fixture_stress`;
- paired success lower bound greater than zero;
- fixture-accuracy difference not worse than the strongest baseline;
- parameter-error reduction positive;
- force-violation, damage, and repeated-failure reductions non-negative;
- path-efficiency loss below a predefined threshold;
- aggregate hard-regime success clears the strongest non-oracle baseline;
- fixed-risk success clears the strongest baseline at every risk budget;
- maximum-stress success clears the strongest baseline;
- ablation necessity is shown by full v5 beating every removed-component ablation.

If any required local gate fails, the terminal decision is `KILL_ARCHIVE`.

## Page-Scale Without Filler

Generate a 25+ page manuscript from real artifacts only:

- decision and protocol section,
- fixture benchmark formalization,
- probe-observation theory sketch,
- identifiability limits for ambiguous fixture families,
- method and baseline details,
- main results,
- aggregate hard-regime results,
- fixed-risk tables,
- stress curves,
- ablation tables,
- negative cases,
- per-seed appendix tables,
- bibliography with bright boxed clickable citations.

No invented experiments, no filler paragraphs, and no fake external validation.

## Expected Full v5 Artifacts

Expected row targets may be adjusted only if the frozen method list changes before the first full run.

- Main rollout rows: 8 seeds x 5 splits x 14 scenarios x 13 methods = 7,280.
- Probe observation rows: 8 seeds x 5 splits x 14 scenarios x 12 probes = 6,720.
- Seed metric rows: 8 seeds x 5 splits x 13 methods = 520.
- Aggregate seed rows: 8 seeds x 13 methods = 104 after aggregating the four hard-regime splits.
- Ablation rows: 8 seeds x 10 scenarios x 9 ablations = 720.
- Stress rows: 7 stress levels x 8 seeds x 8 scenarios x 10 methods = 4,480.
- Fixed-risk rows: 4 budgets x 8 seeds x 8 scenarios x 8 methods = 2,048.
- Negative cases: 12.

## Validation Checklist

- `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py`
- Full phase-by-phase run: main, ablation, stress, fixed_risk, finalize.
- Manuscript generation from frozen CSVs.
- LaTeX/BibTeX compile to `paper/main.pdf`.
- Copy only to `C:/Users/wangz/Downloads/77.pdf`.
- Ensure `C:/Users/wangz/Desktop/77.pdf` does not exist.
- Run artifact validator.
- Render visual PDF samples before closure.
- Commit and push public GitHub repo.
- Update root ledgers with final actual decision.
