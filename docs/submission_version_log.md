# Submission Version Log

## v1 - Generated Draft

- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening

- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with synthetic seven-seed diagnostics.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive

- Applied stricter ICLR-main standard.
- Determined that synthetic/template evidence was fatal.
- Terminal decision: KILL_ARCHIVE.

## v4 - Real Fixture-Physics Rebuild

- Replaced the synthetic scaffold with a local fixture-physics benchmark.
- Added probe observations, implemented baselines, oracle, paired stats, ablations, stress sweeps, figures, and a rewritten manuscript.
- `latent_fixture_inference` loses to `prototype_system_id` on the decisive split.
- Terminal decision: KILL_ARCHIVE.

## 2026-06-15 Continuation Audit

- Rechecked code, CSV, ablation, stress, BibTeX/PDF, artifact-location, public-GitHub, and stale-documentation gates.
- Rebuilt the PDF after adding bibliography authors and replacing fragile `[h]` float specifiers.
- Confirmed the negative result: the proposed method loses to `prototype_system_id` on success, fixture accuracy, safety, repeated failures, and stress robustness.
- Terminal decision remains: KILL_ARCHIVE.

## v5 - Hostile-Review Expansion, 2026-06-21

- Froze and executed the expanded CPU-only protocol before interpreting results.
- Added stronger non-oracle baselines, aggregate hard-regime tests, fixed-risk budgets, larger stress sweeps, ablation seed metrics, and a dedicated validator.
- Generated a 40-page ICLR-style archive manuscript with bright citation boxes and a clean final LaTeX log.
- Validated exact evidence counts, Downloads-only `77.pdf`, no Desktop PDF, SHA256, and rendered visual quality.
- `latent_fixture_inference_v5` loses to `adaptive_probe_then_act` on `combined_fixture_stress` and fails every fixed-risk gate.
- Terminal decision remains: KILL_ARCHIVE.
