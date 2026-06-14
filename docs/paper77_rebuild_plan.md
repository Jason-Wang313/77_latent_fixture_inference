# Paper 77 Rebuild Plan: Latent Fixture Inference

Date: 2026-06-14

## Goal

Rebuild Paper 77 into a real ICLR-main-target robotics artifact, or terminate it honestly as `STRONG_REVISE` / `KILL_ARCHIVE` if the evidence does not justify submission. The central question is whether robots can infer unseen fixtures and environmental supports from action-resistance patterns, then use that latent fixture belief to choose safer and more successful manipulation actions.

## Core Claim To Test

Objects and tools often behave strangely because they are latently constrained by clamps, hinges, slots, suction pads, friction fixtures, or tethers. These fixtures may not be visible, but physical probes reveal them through compliance anisotropy, torque response, hysteresis, release cues, and force/displacement mismatch. A fixture-aware planner should beat observed-only, endpoint-force, generic uncertainty, and system-identification baselines on downstream manipulation.

## Benchmark

Implement a local continuous 2D manipulation benchmark with:

- Hidden fixture families: free object, clamp, hinge, slot/rail, suction/friction pad, tether.
- Probe actions: pulls/pushes from multiple contact points and directions.
- Observations: force vector, contact point, displacement, rotation, resistance, slip, release cue, hysteresis/recoil, and noise.
- Downstream actions: direct translate, release-and-pull, rotate about pivot, follow slot axis, peel-and-translate, unwind/release tether, or abstain.
- Stress conditions: fixture occlusion, parameter shift, noisy force observations, ambiguous probes, high stiffness, and dynamic slip.

Evaluation splits:

- `nominal_visible_fixture`: easy fixtures and low noise.
- `hidden_clamp_hinge`: unseen clamps and hinges with ambiguous visual state.
- `slot_axis_shift`: hidden slots/rails with shifted axes and contact points.
- `adhesive_tether_fixture`: suction, friction pad, and tether constraints.
- `combined_fixture_stress`: mixed hidden fixtures, high stiffness, force noise, ambiguous probes, and dynamic slip.

## Methods

- `visible_only_policy`: assumes the object is free and plans direct translation.
- `force_threshold_heuristic`: reacts to high resistance with a generic cautious pull/peel rule.
- `prototype_system_id`: nearest-prototype fixture classifier trained on simulated probe traces.
- `ensemble_uncertainty_planner`: bootstrap-style prototype ensemble with conservative action choice under disagreement.
- `particle_filter_fixture`: Bayesian fixture-type filter from probe likelihoods.
- `latent_fixture_inference`: proposed physics-structured inference using compliance anisotropy, torque signatures, release cues, and hysteresis.
- `oracle_fixture`: upper bound with true fixture family and parameters.

## Metrics

- Closed-loop manipulation success.
- Force violation and damage rate.
- Fixture-type accuracy.
- Fixture-parameter error.
- Repeated failed-action rate.
- Action efficiency / energy.
- Calibration of predicted success.
- Stress-sweep robustness.

## Rigor

- Seven seeds.
- Multiple scenarios per split.
- Strong non-oracle baselines.
- Paired seed-level comparisons.
- Ablations: no torque features, no compliance anisotropy, no release cues, no hysteresis memory, no particle refinement, no safety margin.
- Stress sweeps over fixture ambiguity/noise/stiffness/occlusion.
- Raw probe logs, rollout rows, seed metrics, summary metrics, pairwise stats, ablations, stress sweeps, negative cases, figures, and training summary.

## Submission Gate

The paper can only move above archive if `latent_fixture_inference` beats the strongest non-oracle baseline on `combined_fixture_stress` success with a meaningful paired effect, reduces force/damage or repeated failures, improves fixture identification/parameter metrics, and does not win merely by abstaining or over-conservatism. Even if it passes locally, it remains `STRONG_REVISE` unless hardware or external benchmark validation exists.

## Deliverables

- Replace the synthetic scaffold with a reproducible local fixture-physics benchmark runner.
- Generate raw probe/rollout CSVs, metrics, pairwise stats, ablations, stress sweeps, negative cases, figures, and `training_summary.csv`.
- Rewrite README, claims, novelty boundary, hostile response, reproducibility checklist, final audit, and readiness decision.
- Rewrite `paper/main.tex` around the actual evidence.
- Compile `paper/main.pdf`, copy exactly to `C:/Users/wangz/Downloads/77.pdf`, and do not copy any PDF to Desktop.
- Commit and push the final Paper77 repo, then update shared root reports before moving to Paper78.
