# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Reason: The v5 hostile-review rebuild provides real local fixture-physics evidence at larger scale, but the evidence refutes the main claim. `latent_fixture_inference_v5` loses to `adaptive_probe_then_act` on the decisive `combined_fixture_stress` split: 0.554 +/- 0.058 versus 0.795 +/- 0.067 success, paired difference -0.241 +/- 0.115. It is also worse on fixture accuracy, parameter error, force violations, damage, repeated failures, path efficiency, aggregate hard-regime success, maximum-stress success, every fixed-risk budget, and ablation necessity.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: a substantially different fixture-inference method that beats strong system-ID, adaptive probing, and robust-control baselines on downstream manipulation, fixed-risk safety, stress robustness, and external or hardware validation.
