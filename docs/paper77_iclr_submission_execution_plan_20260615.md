# Paper 77 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15
Paper: 77 - `latent_fixture_inference`
Target venue posture: ICLR main only if the latent fixture mechanism beats strong fixture-identification baselines
Current terminal label entering audit: `KILL_ARCHIVE`

## Goal

Audit Paper 77 as a real submission candidate rather than a polished negative template. The audit must decide whether latent fixture inference can honestly support a main-conference robotics claim, or whether the stronger prototype system-identification baseline falsifies the idea.

## Decision Rule

Upgrade from `KILL_ARCHIVE` only if all of the following are true:

1. `latent_fixture_inference` decisively beats the strongest non-oracle baseline, especially `prototype_system_id`, on `combined_fixture_stress` success.
2. Fixture accuracy and parameter-error improvements translate into downstream success.
3. The method reduces force violation, damage, and repeated failures rather than increasing them.
4. Ablations show the proposed structured fixture components are necessary.
5. Stress-sweep evidence remains favorable at high stress.
6. The evidence is reproducible from checked-in code, raw CSVs, a clean PDF, and a public GitHub repository.

If any decisive gate fails, preserve `KILL_ARCHIVE` and document the exact failure mode.

## Evidence Gates

Run these checks before changing the decision:

1. Code integrity: compile `src/run_experiment.py`.
2. Result integrity: verify all required CSVs exist, are nonempty, finite, and schema-valid.
3. Scale check: confirm 2,450 main rollout rows, 3,500 probe observation rows, 245 seed metric rows, 343 ablation rollout rows, and 1,470 stress-sweep raw rows.
4. Baseline check: confirm `prototype_system_id`, `ensemble_uncertainty_planner`, `particle_filter_fixture`, `force_threshold_heuristic`, `visible_only_policy`, and `oracle_fixture` are present.
5. Central comparison check: verify `combined_fixture_stress` success, fixture accuracy, parameter error, force violation, damage, and repeated failures.
6. Ablation check: confirm whether full latent fixture inference beats removed-component variants.
7. Stress check: verify high-stress behavior against the strongest non-oracle baselines.
8. Documentation consistency check: correct stale counts or wording if direct artifacts disagree.
9. Paper build: run LaTeX/BibTeX to produce a clean PDF and copy only `77.pdf` to Downloads.
10. Artifact hygiene: confirm no numbered PDF is copied to the visible Desktop.
11. GitHub hygiene: confirm the matching public GitHub repository exists and the local commit is pushed.
12. Root-report hygiene: update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

## Expected Risk

The existing summary reports a decisive negative result: `latent_fixture_inference` reaches 0.671 +/- 0.056 success while `prototype_system_id` reaches 0.771 +/- 0.082, with paired success difference -0.100 +/- 0.086. It also reports worse fixture accuracy, parameter error, damage, and repeated failures. Unless direct verification contradicts that result, Paper 77 remains a reproducible negative-result archive.

## Execution Order

1. Re-check repository cleanliness and result inventory.
2. Run code and CSV integrity gates.
3. Extract central, pairwise, ablation, and stress evidence.
4. Rebuild the paper PDF and repair recoverable build warnings.
5. Update child status and audit docs with exact verified evidence.
6. Update root reports through Paper 77.
7. Commit and push the Paper 77 repository.
8. Verify `Downloads/77.pdf`, no Desktop copy, public GitHub visibility, clean git state, and root report consistency.
