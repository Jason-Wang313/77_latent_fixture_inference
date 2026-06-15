# Final Audit

Paper: 77 latent_fixture_inference

Version: v4

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local fixture-physics manipulation benchmark.
- Hidden fixture families: free, clamp, hinge, slot, suction, tether.
- Seven seeds: 0 through 6.
- Five evaluation splits.
- 2,450 main rollout rows.
- 3,500 probe observation rows.
- 245 seed-level metric rows.
- 343 ablation rollout rows.
- 1,470 stress-sweep raw rows.
- 12 negative cases.

## Gate Result

The proposed method fails the decisive gate.

- `latent_fixture_inference`: 0.671 +/- 0.056 combined-fixture-stress success.
- `prototype_system_id`: 0.771 +/- 0.082 combined-fixture-stress success.
- Paired success difference: -0.100 +/- 0.086.
- Fixture-accuracy difference: -0.286.
- Parameter-error reduction: -0.023, meaning worse parameter error.
- Damage reduction: -0.086, meaning more damage.
- Repeated-failure reduction: -0.100, meaning more repeated failures.

## Audit Conclusion

The repo is now a real negative-result artifact. It should not be submitted to ICLR main.

## Continuation Audit 2026-06-15

Rechecked gates:

- `python -m py_compile src/run_experiment.py` passed.
- CSV integrity passed with the expected evidence scale: 2,450 main rollout rows, 3,500 probe observation rows, 245 seed-level metric rows, 35 aggregate metric rows, 30 pairwise rows, 343 ablation rollout rows, 30 stress-sweep aggregate rows, 1,470 stress-sweep raw rows, and 12 negative cases.
- Required baselines were present: `prototype_system_id`, `ensemble_uncertainty_planner`, `particle_filter_fixture`, `force_threshold_heuristic`, `visible_only_policy`, and `oracle_fixture`.
- LaTeX/BibTeX rebuilt a 5-page PDF after repairing missing bibliography authors and fragile float placement warnings.
- `C:/Users/wangz/Downloads/77.pdf` SHA256 is `BED33DDA6E10D2BCF25D1BA25C0D1336B14B32F22BCFF31D3ADF1A72B327D43A`.
- `C:/Users/wangz/Desktop/77.pdf` does not exist.

The decisive negative result was reproduced. On `combined_fixture_stress`, `latent_fixture_inference` scores 0.671 +/- 0.056 success, while `prototype_system_id` scores 0.771 +/- 0.082. The paired proposed-minus-prototype success difference is -0.100 +/- 0.086, with 0/7 better seeds for the proposed method.

The mechanism-specific diagnostics are also unfavorable:

- Fixture accuracy is 0.671 for `latent_fixture_inference` versus 0.957 for `prototype_system_id`.
- Parameter-error reduction versus `prototype_system_id` is -0.023, meaning worse parameter error.
- Force-violation reduction is -0.129, damage reduction is -0.086, and repeated-failure reduction is -0.100.
- Path-efficiency difference is -0.078.

Ablations do not rescue the paper. The full ablation variant reaches only 0.571 +/- 0.086 success, and removing components generally makes it worse, but the full method still fails the strongest baseline. Component necessity inside a losing system is insufficient for ICLR-main readiness.

Stress evidence is also unfavorable. At maximum stress level 1.00, `latent_fixture_inference` reaches 0.469 success, while `prototype_system_id` reaches 0.694. The proposed method is below the best non-oracle method at every stress level.

Continuation decision: keep `KILL_ARCHIVE`. Revival would require new evidence where structured latent fixture inference beats prototype system identification on success, fixture accuracy, safety, and stress robustness.
