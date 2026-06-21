# 77 Latent Fixture Inference

Submission-hardening version: v5

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository contains the expanded Paper 77 hostile-review rebuild: a CPU-only local fixture-physics benchmark with hidden clamps, hinges, slots, suction/friction pads, and tethers; continuous force/displacement/torque/release observations; strong non-oracle baselines; eight-seed evaluation; paired statistics; ablations; aggregate hard-regime tests; stress sweeps; fixed-risk budgets; curated negative cases; figures; and a 40-page ICLR-style archive manuscript.

The evidence does not support ICLR-main submission. On the decisive `combined_fixture_stress` split, `latent_fixture_inference_v5` reaches 0.554 +/- 0.058 closed-loop success. The strongest non-oracle baseline, `adaptive_probe_then_act`, reaches 0.795 +/- 0.067. The paired success difference is -0.241 +/- 0.115. The proposed method is also worse on fixture accuracy, parameter error, force violations, damage, repeated failures, path efficiency, aggregate hard-regime performance, maximum-stress performance, fixed-risk budgets, and ablation necessity.

## Main Result

Full v5 run:

- Main rollout rows: 7,280.
- Probe observation rows: 6,720.
- Seed-level metric rows: 520.
- Aggregate hard-regime seed rows: 104.
- Ablation rollout rows: 720.
- Stress-sweep raw rows: 4,480.
- Fixed-risk raw rows: 2,048.
- Fixed-risk seed rows: 256.
- Negative cases: 12.
- Seeds: 0 through 7.
- Fixture families: free, clamp, hinge, slot, suction, tether.
- Probe count per scenario: 12.
- Risk budgets: 0.08, 0.12, 0.18, 0.25.

Combined-fixture-stress summary:

- `oracle_fixture`: 0.902 +/- 0.070 success, fixture accuracy 1.000, damage 0.036.
- `adaptive_probe_then_act`: 0.795 +/- 0.067 success, fixture accuracy 0.955, damage 0.054.
- `calibrated_prototype_system_id`: 0.786 +/- 0.099 success, fixture accuracy 0.973, damage 0.071.
- `robust_impedance_planner`: 0.777 +/- 0.077 success.
- `random_forest_probe_classifier`: 0.759 +/- 0.088 success.
- `prototype_system_id`: 0.750 +/- 0.088 success.
- `latent_fixture_inference`: 0.634 +/- 0.049 success.
- `latent_fixture_inference_v5`: 0.554 +/- 0.058 success, fixture accuracy 0.777, damage 0.232.

Hard-gate failures:

- Main success margin against the strongest non-oracle baseline.
- Paired success lower bound.
- Diagnostic safety and efficiency.
- Aggregate hard-regime success.
- Maximum-stress success.
- Fixed-risk success at every risk budget.
- Ablation necessity, because stronger ablations beat the v5 full method.

The paper is retained as a reproducible negative-result archive.

## Reproduce

```powershell
$env:PAPER77_PHASE = "all"
python -m src.run_experiment
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Optional chunking:

```powershell
$env:PAPER77_RESUME = "1"
$env:PAPER77_ONLY_SEEDS = "0,1"
$env:PAPER77_STRESS_LEVELS = "0.40"
```

Outputs are written under `results/`, `figures/`, and `paper/`.

## Rebuild PDF

Canonical local PDF: `C:/Users/wangz/Downloads/77.pdf`

Validated PDF:

- Pages: 40.
- SHA256: `AF9C2C97CA9143249B33BCBAA11C5D4988A52962379295FCEC069655B80230C2`.
- Visual QA: passed after rendering all pages with Poppler and spot-checking title/citations, figures, fixed-risk plot, appendix tables, and references.
- Desktop exclusion: `C:/Users/wangz/Desktop/77.pdf` does not exist.

No PDF is copied to the visible Desktop.
