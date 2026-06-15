# Paper 77 Terminal Audit

Date: 2026-06-15 07:32:58 +0100
Paper: 77 - `latent_fixture_inference`
Decision: `KILL_ARCHIVE`

## Verification Performed

- Compiled `src/run_experiment.py`.
- Verified required CSV artifacts and schemas.
- Confirmed evidence scale: 2,450 main rollout rows, 3,500 probe observation rows, 245 seed metric rows, 35 aggregate metric rows, 30 pairwise rows, 343 ablation rollout rows, 30 stress-sweep aggregate rows, 1,470 stress-sweep raw rows, and 12 negative cases.
- Confirmed seven seeds: 0 through 6.
- Confirmed required baselines: `prototype_system_id`, `ensemble_uncertainty_planner`, `particle_filter_fixture`, `force_threshold_heuristic`, `visible_only_policy`, and `oracle_fixture`.
- Rebuilt the LaTeX/BibTeX PDF after fixing bibliography author warnings and fragile float placement warnings.
- Copied only `77.pdf` to Downloads.
- Confirmed no `C:/Users/wangz/Desktop/77.pdf` exists.

## Decisive Evidence

On `combined_fixture_stress`:

- `latent_fixture_inference`: 0.671 +/- 0.056 success, 0.671 fixture accuracy, 0.297 parameter error, 0.214 force violation, 0.171 damage, 0.329 repeated failure, 0.527 path efficiency.
- `prototype_system_id`: 0.771 +/- 0.082 success, 0.957 fixture accuracy, 0.274 parameter error, 0.086 force violation, 0.086 damage, 0.229 repeated failure, 0.605 path efficiency.
- `ensemble_uncertainty_planner`: 0.700 +/- 0.096 success, 0.957 fixture accuracy, 0.086 damage.
- `oracle_fixture`: 0.900 +/- 0.096 success.

Paired proposed-minus-prototype evidence:

- Success difference: -0.100 +/- 0.086.
- Fixture-accuracy difference: -0.286.
- Parameter-error reduction: -0.023.
- Force-violation reduction: -0.129.
- Damage reduction: -0.086.
- Repeated-failure reduction: -0.100.
- Path-efficiency difference: -0.078.
- Better seeds: 0/7.

The proposed structured latent fixture representation does not beat a simpler prototype system-identification baseline and is less safe.

## Ablation Gate

The ablation evidence shows internal component sensitivity, but not submission viability.

- `latent_fixture_full`: 0.571 +/- 0.086 success.
- `latent_fixture_no_hysteresis_memory`: 0.490 +/- 0.057 success.
- `latent_fixture_no_particle_refinement`: 0.224 +/- 0.103 success.
- `latent_fixture_no_release_cues`: 0.490 +/- 0.083 success.
- `latent_fixture_no_safety_margin`: 0.449 +/- 0.073 success.
- `latent_fixture_no_torque_features`: 0.327 +/- 0.101 success.

Components matter inside the proposed system, but the system still loses to stronger baselines.

## Stress Gate

The stress sweep falsifies robustness. At maximum stress level 1.00:

- `latent_fixture_inference`: 0.469 success, 0.490 fixture accuracy, 0.449 force violation, 0.265 damage, 0.531 repeated failure.
- `prototype_system_id`: 0.694 success, 0.878 fixture accuracy, 0.265 force violation, 0.143 damage, 0.306 repeated failure.
- `oracle_fixture`: 0.837 success.

The proposed method is below the best non-oracle method at every stress level.

## Artifact Result

- PDF: `C:/Users/wangz/Downloads/77.pdf`
- SHA256: `BED33DDA6E10D2BCF25D1BA25C0D1336B14B32F22BCFF31D3ADF1A72B327D43A`
- Public GitHub: `https://github.com/Jason-Wang313/77_latent_fixture_inference`

## Final Recommendation

Keep `KILL_ARCHIVE`. A future revival would require new experiments where latent fixture inference beats prototype system identification on success, fixture accuracy, safety, and stress robustness.
