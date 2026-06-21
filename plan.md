# Plan

Rebuild paper 77 `latent_fixture_inference` into a real fixture-physics evidence artifact, compile PDF to Downloads only, publish the exact-name public repo, and mark the ICLR-main gate honestly.

## 2026-06-21 v5 Expansion Plan

- Freeze an expanded CPU-only protocol before interpreting results.
- Increase evidence scale to eight seeds, 42 train scenarios per fixture, 14 evaluation scenarios per split, 12 probes, 10 ablation scenarios, 8 stress scenarios, and 8 fixed-risk scenarios.
- Add stronger non-oracle baselines: calibrated prototype ID, random-forest-style probe classifier, Bayesian fixture belief, robust impedance planner, adaptive probe-then-act, ensemble uncertainty planner, and particle filtering.
- Add `latent_fixture_inference_v5` with compliance anisotropy, torque/release cues, hysteresis memory, calibration, particle refinement, and cautious fixture-conditioned action selection.
- Evaluate main splits, aggregate hard regimes, ablations, stress levels through 1.20, and fixed-risk budgets 0.08, 0.12, 0.18, and 0.25.
- Generate a 25+ page ICLR-style manuscript with bright citation boxes and direct reference routing.
- Validate exact row counts, clean final LaTeX log, Downloads-only numbered PDF, Desktop exclusion, SHA, and rendered visual quality.

## 2026-06-21 v5 Expansion Result

The expansion preserved `KILL_ARCHIVE`. `latent_fixture_inference_v5` reaches 0.554 +/- 0.058 success on `combined_fixture_stress`, while the strongest non-oracle baseline `adaptive_probe_then_act` reaches 0.795 +/- 0.067. The paired success difference is -0.241 +/- 0.115. The method also fails aggregate hard-regime, maximum-stress, fixed-risk, diagnostic-safety, and ablation-necessity gates.

The final PDF is `C:/Users/wangz/Downloads/77.pdf`, 40 pages, SHA256 `AF9C2C97CA9143249B33BCBAA11C5D4988A52962379295FCEC069655B80230C2`. No Desktop copy exists.
