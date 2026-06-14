# 77 Latent Fixture Inference

Submission-hardening version: v4

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository now contains a real Paper 77 rebuild: a local continuous fixture-physics benchmark with hidden clamps, hinges, slots, suction/friction pads, and tethers; force/resistance probes; implemented baselines; seven-seed evaluation; paired statistics; ablations; stress sweeps; negative cases; figures; and a rewritten archive manuscript.

The evidence does not support ICLR-main submission. On the decisive `combined_fixture_stress` split, `latent_fixture_inference` reaches 0.671 +/- 0.056 closed-loop success. The strongest non-oracle baseline, `prototype_system_id`, reaches 0.771 +/- 0.082. The paired success difference is -0.100 +/- 0.086. The proposed method has worse fixture accuracy, worse parameter error, higher force violation, higher damage, and more repeated failures than the prototype baseline.

## Main Result

Full run:

- Main rollout rows: 2,450.
- Probe observation rows: 3,500.
- Seed-level metric rows: 245.
- Ablation rollout rows: 343.
- Stress-sweep raw rows: 1,470.
- Seeds: 0 through 6.
- Fixture families: free, clamp, hinge, slot, suction, tether.
- Probe count per scenario: 10.

Combined-fixture-stress summary:

- `oracle_fixture`: 0.900 +/- 0.096 success, fixture accuracy 1.000, damage 0.029.
- `prototype_system_id`: 0.771 +/- 0.082 success, fixture accuracy 0.957, damage 0.086.
- `ensemble_uncertainty_planner`: 0.700 +/- 0.096 success, fixture accuracy 0.957, damage 0.086.
- `latent_fixture_inference`: 0.671 +/- 0.056 success, fixture accuracy 0.671, damage 0.171.
- `particle_filter_fixture`: 0.614 +/- 0.108 success.
- `force_threshold_heuristic`: 0.343 +/- 0.084 success.
- `visible_only_policy`: 0.200 +/- 0.086 success.

The paper is retained as a reproducible negative-result archive.

## Reproduce

```powershell
$env:PAPER77_PHASE = "main"; python -m src.run_experiment
$env:PAPER77_PHASE = "ablation"; python -m src.run_experiment
$env:PAPER77_PHASE = "stress"; python -m src.run_experiment
$env:PAPER77_PHASE = "finalize"; python -m src.run_experiment
```

Optional chunking:

```powershell
$env:PAPER77_RESUME = "1"
$env:PAPER77_ONLY_SEEDS = "0,1"
$env:PAPER77_STRESS_LEVELS = "0.40"
```

Outputs are written under `results/` and `figures/`.

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/77.pdf`

No PDF is copied to the visible Desktop.
