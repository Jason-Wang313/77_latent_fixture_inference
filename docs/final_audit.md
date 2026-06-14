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
