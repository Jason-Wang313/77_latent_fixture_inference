# Final Audit

Paper: 77 latent_fixture_inference

Version: v5

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local fixture-physics manipulation benchmark.
- Hidden fixture families: free, clamp, hinge, slot, suction, tether.
- Eight seeds: 0 through 7.
- Five evaluation splits.
- Aggregate hard-regime evaluation over hidden clamp/hinge, slot-axis shift, adhesive/tether, and combined fixture stress.
- Fixed-risk budgets: 0.08, 0.12, 0.18, 0.25.
- Stress levels: 0.00 through 1.20.
- 7,280 main rollout rows.
- 6,720 probe observation rows.
- 520 seed-level metric rows.
- 104 aggregate hard-regime seed rows.
- 720 ablation rollout rows.
- 4,480 stress-sweep raw rows.
- 2,048 fixed-risk raw rows.
- 256 fixed-risk seed rows.
- 12 negative cases.

## Gate Result

The proposed v5 method fails the decisive gate.

- `latent_fixture_inference_v5`: 0.554 +/- 0.058 combined-fixture-stress success.
- `adaptive_probe_then_act`: 0.795 +/- 0.067 combined-fixture-stress success.
- Paired success difference: -0.241 +/- 0.115.
- Fixture-accuracy difference: -0.179.
- Parameter-error reduction: -0.055, meaning worse parameter error.
- Damage reduction: -0.179, meaning more damage.
- Repeated-failure reduction: -0.241, meaning more repeated failures.
- Path-efficiency difference: -0.206.

## Expanded Gate Failures

- Aggregate hard-regime paired success difference versus `adaptive_probe_then_act`: -0.176 +/- 0.039.
- Maximum stress level 1.20: `latent_fixture_inference_v5` reaches 0.406 success while the strongest non-oracle `calibrated_prototype_system_id` reaches 0.641.
- Fixed-risk budget 0.08: v5 0.266 versus best non-oracle 0.703.
- Fixed-risk budget 0.12: v5 0.266 versus best non-oracle 0.719.
- Fixed-risk budget 0.18: v5 0.266 versus best non-oracle 0.641.
- Fixed-risk budget 0.25: v5 0.172 versus best non-oracle 0.672.
- Ablation necessity fails because `latent_fixture_v5_no_adaptive_probe` and `latent_fixture_v5_no_calibration` outperform the full v5 variant.

## Artifact Audit

- `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py` passed.
- `python scripts/validate_submission_artifacts.py` passed.
- Final PDF: `C:/Users/wangz/Downloads/77.pdf`.
- PDF pages: 40.
- PDF SHA256: `AF9C2C97CA9143249B33BCBAA11C5D4988A52962379295FCEC069655B80230C2`.
- `C:/Users/wangz/Desktop/77.pdf` does not exist.
- Visual QA passed after Poppler rendering and inspection of title/citations, main results, stress/fixed-risk figures, appendix tables, and references.

## Audit Conclusion

The repo is now a larger, more rigorous negative-result artifact. It should not be submitted to ICLR main. The archive is useful because it shows the method fails under stronger baselines and predefined hostile stress tests rather than under weak strawmen.
