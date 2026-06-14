# Reproducibility Checklist

- Code entry point: `python -m src.run_experiment`.
- Main phase: set `PAPER77_PHASE=main`.
- Ablation phase: set `PAPER77_PHASE=ablation`.
- Stress phase: set `PAPER77_PHASE=stress`.
- Finalization phase: set `PAPER77_PHASE=finalize`.
- Resume support: set `PAPER77_RESUME=1`.
- Seed chunking support: set `PAPER77_ONLY_SEEDS=0`.
- Stress-level chunking support: set `PAPER77_STRESS_LEVELS=0.40`.
- Raw outputs: `results/rollouts.csv`, `results/probe_observations.csv`, `results/ablation_rollouts.csv`, `results/stress_sweep_raw.csv`.
- Summary outputs: `results/metrics.csv`, `results/pairwise_stats.csv`, `results/ablation_metrics.csv`, `results/stress_sweep.csv`, `results/summary.txt`.
- Figures: `figures/latent_fixture_success.png`, `figures/latent_fixture_accuracy.png`, `figures/latent_fixture_ablation_success.png`, `figures/latent_fixture_stress_sweep.png`.
