from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
TINY = r"\tiny"

METHOD_ALIASES = {
    "visible_only_policy": "visible",
    "force_threshold_heuristic": "threshold",
    "prototype_system_id": "proto-ID",
    "calibrated_prototype_system_id": "calib-proto",
    "random_forest_probe_classifier": "rf-probe",
    "bayesian_fixture_belief": "bayes",
    "robust_impedance_planner": "robust-imp",
    "adaptive_probe_then_act": "adaptive-probe",
    "ensemble_uncertainty_planner": "ensemble",
    "particle_filter_fixture": "particle",
    "latent_fixture_inference": "LFI-v4",
    "latent_fixture_inference_v5": "LFI-v5",
    "oracle_fixture": "oracle",
    "latent_fixture_v5_full": "full-v5",
    "latent_fixture_v5_no_torque_features": "no-torque",
    "latent_fixture_v5_no_compliance_anisotropy": "no-aniso",
    "latent_fixture_v5_no_release_cues": "no-release",
    "latent_fixture_v5_no_hysteresis_memory": "no-hysteresis",
    "latent_fixture_v5_no_particle_refinement": "no-particle",
    "latent_fixture_v5_no_safety_margin": "no-margin",
    "latent_fixture_v5_no_calibration": "no-calib",
    "latent_fixture_v5_no_adaptive_probe": "no-adapt",
}

SPLIT_ALIASES = {
    "nominal_visible_fixture": "nominal",
    "hidden_clamp_hinge": "clamp-hinge",
    "slot_axis_shift": "slot-shift",
    "adhesive_tether_fixture": "adhesive-tether",
    "combined_fixture_stress": "combined",
    "aggregate_hard_regime": "hard-agg",
}


def read_csv(name: str) -> List[Dict[str, str]]:
    path = RESULTS / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def method_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(METHOD_ALIASES.get(name, name)) + "}"


def split_tex(name: str) -> str:
    return r"\texttt{" + tex_escape(SPLIT_ALIASES.get(name, name)) + "}"


def f(value: str | float, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return tex_escape(value)


def pm(row: Dict[str, str], mean_key: str, ci_key: str, digits: int = 3) -> str:
    return f"${f(row.get(mean_key, '0'), digits)} \\pm {f(row.get(ci_key, '0'), digits)}$"


def summary_fields() -> Dict[str, str]:
    text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    fields = {"summary_text": text}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    return fields


def row_lookup(rows: Sequence[Dict[str, str]], **kwargs: str) -> Dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in kwargs.items()):
            return row
    return {}


def sorted_float(rows: Iterable[Dict[str, str]], key: str, reverse: bool = True) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda row: float(row.get(key, "0") or "0"), reverse=reverse)


def figure(path: str, caption: str, width: str = "0.92") -> str:
    if not (FIGURES / path).exists():
        return ""
    return "\n".join(
        [
            r"\begin{center}",
            rf"\includegraphics[width={width}\linewidth]{{../figures/{path}}}",
            r"\captionof{figure}{" + caption + r"}",
            r"\end{center}",
        ]
    )


def chunked_table(
    caption: str,
    headers: Sequence[str],
    align: str,
    rows: Sequence[Sequence[str]],
    chunk_size: int = 34,
    size: str = r"\scriptsize",
) -> str:
    if not rows:
        return ""
    out: List[str] = [size, r"\setlength{\tabcolsep}{2pt}"]
    table_no = 1
    for chunk_idx in range(0, len(rows), chunk_size):
        chunk = rows[chunk_idx : chunk_idx + chunk_size]
        label = tex_escape(caption if chunk_idx == 0 else f"{caption} continued")
        out.append(r"\begin{center}")
        out.append(r"\textbf{Table: " + label + r"}\\[0.4ex]")
        out.append(r"\resizebox{\linewidth}{!}{%")
        out.append(r"\begin{tabular}{" + align + "}")
        out.append(r"\toprule")
        out.append(" & ".join(headers) + r" \\")
        out.append(r"\midrule")
        for row in chunk:
            out.append(" & ".join(row) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}%")
        out.append(r"}")
        out.append(r"\end{center}")
        table_no += 1
    out.append(r"\normalsize")
    return "\n".join(out)


def write_references() -> None:
    refs = r"""@book{mason2001mechanics,
  title={Mechanics of Robotic Manipulation},
  author={Mason, Matthew T.},
  publisher={MIT Press},
  year={2001},
  url={https://manipulation.csail.mit.edu/}
}

@book{lynch2017modern,
  title={Modern Robotics: Mechanics, Planning, and Control},
  author={Lynch, Kevin M. and Park, Frank C.},
  publisher={Cambridge University Press},
  year={2017},
  url={https://modernrobotics.northwestern.edu/}
}

@book{lavalle2006planning,
  title={Planning Algorithms},
  author={LaValle, Steven M.},
  publisher={Cambridge University Press},
  year={2006},
  url={https://lavalle.pl/planning/}
}

@article{khatib1986potential,
  title={Real-time obstacle avoidance for manipulators and mobile robots},
  author={Khatib, Oussama},
  journal={The International Journal of Robotics Research},
  volume={5},
  number={1},
  pages={90--98},
  year={1986},
  doi={10.1177/027836498600500106}
}

@article{ames2017cbf,
  title={Control Barrier Function Based Quadratic Programs for Safety Critical Systems},
  author={Ames, Aaron D. and Xu, Xiangru and Grizzle, Jessy W. and Tabuada, Paulo},
  journal={IEEE Transactions on Automatic Control},
  volume={62},
  number={8},
  pages={3861--3876},
  year={2017},
  doi={10.1109/TAC.2016.2638961}
}

@article{breiman2001rf,
  title={Random Forests},
  author={Breiman, Leo},
  journal={Machine Learning},
  volume={45},
  pages={5--32},
  year={2001},
  doi={10.1023/A:1010933404324}
}

@book{rawlings2017mpc,
  title={Model Predictive Control: Theory, Computation, and Design},
  author={Rawlings, James B. and Mayne, David Q. and Diehl, Moritz M.},
  edition={2},
  publisher={Nob Hill Publishing},
  year={2017},
  url={https://sites.engineering.ucsb.edu/~jbraw/mpc/}
}
"""
    (PAPER / "references.bib").write_text(refs, encoding="utf-8")


def manuscript() -> str:
    fields = summary_fields()
    metrics = read_csv("metrics.csv")
    seed_metrics = read_csv("raw_seed_metrics.csv")
    pairwise = read_csv("pairwise_stats.csv")
    aggregate = read_csv("aggregate_metrics.csv")
    aggregate_seed = read_csv("aggregate_seed_metrics.csv")
    aggregate_pairwise = read_csv("aggregate_pairwise_stats.csv")
    ablations = read_csv("ablation_metrics.csv")
    ablation_seed = read_csv("ablation_seed_metrics.csv")
    stress = read_csv("stress_sweep.csv")
    fixed = read_csv("fixed_risk_metrics.csv")
    fixed_seed = read_csv("fixed_risk_seed_metrics.csv")
    fixed_pairwise = read_csv("fixed_risk_pairwise.csv")
    negatives = read_csv("negative_cases.csv")

    combined = [row for row in metrics if row.get("split") == "combined_fixture_stress"]
    v5 = row_lookup(combined, method="latent_fixture_inference_v5")
    non_oracle = [row for row in combined if row.get("method") not in {"latent_fixture_inference", "latent_fixture_inference_v5", "oracle_fixture"}]
    best = sorted_float(non_oracle, "mean_success")[0]
    main_pair = row_lookup(pairwise, split="combined_fixture_stress", comparison=best.get("method", ""))
    oracle = row_lookup(combined, method="oracle_fixture")
    agg_v5 = row_lookup(aggregate, method="latent_fixture_inference_v5", split="aggregate_hard_regime")
    agg_best = sorted_float(
        [row for row in aggregate if row.get("method") not in {"latent_fixture_inference", "latent_fixture_inference_v5", "oracle_fixture"}],
        "mean_success",
    )[0]
    agg_pair = row_lookup(aggregate_pairwise, split="aggregate_hard_regime", comparison=agg_best.get("method", ""))
    max_stress = max((float(row["stress_level"]) for row in stress), default=0.0)
    stress_max = [row for row in stress if abs(float(row.get("stress_level", "0")) - max_stress) < 1e-9]
    stress_v5 = row_lookup(stress_max, method="latent_fixture_inference_v5")
    stress_best = sorted_float([row for row in stress_max if row.get("method") not in {"latent_fixture_inference_v5", "oracle_fixture"}], "mean_success")[0]

    def metric_rows(rows: Sequence[Dict[str, str]]) -> List[List[str]]:
        return [
            [
                method_tex(row["method"]),
                split_tex(row["split"]),
                pm(row, "mean_success", "ci95_success"),
                pm(row, "mean_fixture_correct", "ci95_fixture_correct"),
                pm(row, "mean_parameter_error", "ci95_parameter_error"),
                pm(row, "mean_damage", "ci95_damage"),
                pm(row, "mean_repeated_failure", "ci95_repeated_failure"),
            ]
            for row in sorted(rows, key=lambda r: (r["split"], -float(r["mean_success"])))
        ]

    main_rows = metric_rows(metrics)
    combined_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_fixture_correct", "ci95_fixture_correct"),
            pm(row, "mean_parameter_error", "ci95_parameter_error"),
            pm(row, "mean_force_violation", "ci95_force_violation"),
            pm(row, "mean_damage", "ci95_damage"),
            pm(row, "mean_repeated_failure", "ci95_repeated_failure"),
        ]
        for row in sorted_float(combined, "mean_success")
    ]
    pair_rows = [
        [
            split_tex(row["split"]),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_fixture_accuracy_diff"]),
            f(row["paired_parameter_error_reduction"]),
            f(row["paired_damage_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(pairwise, key=lambda r: (r["split"], r["comparison"]))
    ]
    aggregate_rows = metric_rows(aggregate)
    aggregate_pair_rows = [
        [
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_fixture_accuracy_diff"]),
            f(row["paired_parameter_error_reduction"]),
            f(row["paired_damage_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(aggregate_pairwise, key=lambda r: r["comparison"])
    ]
    fixed_rows = [
        [
            method_tex(row["method"]),
            f(row["risk_budget"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_fixture_correct", "ci95_fixture_correct"),
            pm(row, "mean_damage", "ci95_damage"),
            pm(row, "mean_repeated_failure", "ci95_repeated_failure"),
            pm(row, "mean_path_efficiency", "ci95_path_efficiency"),
        ]
        for row in sorted(fixed, key=lambda r: (float(r["risk_budget"]), -float(r["mean_success"])))
    ]
    fixed_pair_rows = [
        [
            f(row["risk_budget"], 2),
            method_tex(row["comparison"]),
            f(row["paired_success_diff"]),
            f(row["ci95_success_diff"]),
            f(row["paired_fixture_accuracy_diff"]),
            f(row["paired_damage_reduction"]),
            tex_escape(row["reference_better_seeds"] + "/" + row["seeds"]),
        ]
        for row in sorted(fixed_pairwise, key=lambda r: (float(r["risk_budget"]), r["comparison"]))
    ]
    ablation_rows = [
        [
            method_tex(row["method"]),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_fixture_correct", "ci95_fixture_correct"),
            pm(row, "mean_parameter_error", "ci95_parameter_error"),
            pm(row, "mean_damage", "ci95_damage"),
            pm(row, "mean_repeated_failure", "ci95_repeated_failure"),
        ]
        for row in sorted_float(ablations, "mean_success")
    ]
    stress_rows = [
        [
            method_tex(row["method"]),
            f(row["stress_level"], 2),
            pm(row, "mean_success", "ci95_success"),
            pm(row, "mean_fixture_correct", "ci95_fixture_correct"),
            pm(row, "mean_damage", "ci95_damage"),
            pm(row, "mean_repeated_failure", "ci95_repeated_failure"),
        ]
        for row in sorted(stress, key=lambda r: (float(r["stress_level"]), r["method"]))
    ]
    negative_rows = [
        [
            tex_escape(row.get("seed", "")),
            tex_escape(row.get("scenario", "")),
            tex_escape(row.get("fixture_type", "")),
            tex_escape(row.get("estimated_fixture", "")),
            tex_escape(row.get("action", "")),
            tex_escape(row.get("force_violation", "")),
            tex_escape(row.get("damage", "")),
            f(row.get("parameter_error", "0")),
        ]
        for row in negatives
    ]
    seed_rows = [
        [
            method_tex(row["method"]),
            split_tex(row["split"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["fixture_correct"]),
            f(row["parameter_error"]),
            f(row["damage"]),
            f(row["repeated_failure"]),
        ]
        for row in sorted(seed_metrics, key=lambda r: (r["split"], r["method"], int(r["seed"])))
    ]
    aggregate_seed_rows = [
        [
            method_tex(row["method"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["fixture_correct"]),
            f(row["parameter_error"]),
            f(row["damage"]),
            f(row["repeated_failure"]),
        ]
        for row in sorted(aggregate_seed, key=lambda r: (r["method"], int(r["seed"])))
    ]
    ablation_seed_rows = [
        [
            method_tex(row["method"]),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["fixture_correct"]),
            f(row["parameter_error"]),
            f(row["damage"]),
            f(row["repeated_failure"]),
        ]
        for row in sorted(ablation_seed, key=lambda r: (r["method"], int(r["seed"])))
    ]
    fixed_seed_rows = [
        [
            method_tex(row["method"]),
            f(row["risk_budget"], 2),
            tex_escape(row["seed"]),
            tex_escape(row["episodes"]),
            f(row["success"]),
            f(row["fixture_correct"]),
            f(row["damage"]),
            f(row["repeated_failure"]),
        ]
        for row in sorted(fixed_seed, key=lambda r: (float(r["risk_budget"]), r["method"], int(r["seed"])))
    ]

    verdict = fields.get("terminal_recommendation", "UNKNOWN")
    reason = fields.get("reason", "")

    return rf"""\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{caption}}
\usepackage[colorlinks=false,pdfborder={{0 0 1.6}},citebordercolor={{0 1 0}},linkbordercolor={{1 0.55 0}},urlbordercolor={{0 0.45 1}}]{{hyperref}}
\usepackage{{url}}
\sloppy
\emergencystretch=3em
\title{{Latent Fixture Inference Under Hostile System-Identification Baselines}}
\author{{Anonymous Authors}}
\begin{{document}}
\maketitle

\begin{{abstract}}
Robots often discover hidden fixtures only after probing an object: clamps resist translation, hinges rotate about hidden anchors, slots allow anisotropic motion, suction pads release only under peel, and tethers recoil.  Paper 77 tests whether structured latent fixture inference improves downstream manipulation over system identification baselines.  The expanded v5 rebuild uses eight seeds, six fixture families, force/displacement/torque/release/recoil observations, hostile baselines, ablations, aggregate hard-regime tests, fixed-risk budgets, stress sweeps, and negative cases.  The frozen terminal decision is \textbf{{{tex_escape(verdict)}}}.  On the decisive split, \texttt{{LFI-v5}} reaches {pm(v5, "mean_success", "ci95_success")} success versus {pm(best, "mean_success", "ci95_success")} for the strongest non-oracle baseline, \texttt{{{tex_escape(METHOD_ALIASES.get(best.get("method", ""), best.get("method", "")))}}}.  We report the result honestly rather than optimizing for a pretty story.
\end{{abstract}}

\section{{Decision And Protocol}}
This manuscript is generated only from frozen CSV artifacts.  The terminal recommendation is \textbf{{{tex_escape(verdict)}}}.  The summary reason is: \emph{{{tex_escape(reason)}}}

The protocol asks a hostile question: can structured latent fixture inference beat prototype, calibrated prototype, random-subspace probe classification, Bayesian belief, robust impedance, adaptive probing, ensemble, and particle baselines while also improving damage and repeated failures?  If not, the paper remains an archive result.

\section{{Benchmark}}
Each scenario samples one hidden fixture family from free, clamp, hinge, slot, suction, and tether.  The simulator emits probe observations: force vector, contact point, displacement, rotation, resistance, slip, release cue, recoil, and torque.  The downstream controller chooses among direct translation, clamp release, hinge pivot, slot following, suction peel, tether unwind, or cautious probing.  The benchmark follows mechanics and planning concerns from manipulation and planning literature \citep{{mason2001mechanics,lynch2017modern,lavalle2006planning}}.

\section{{Methods}}
Baselines include weak visual and threshold policies, prototype system identification, calibrated prototype ID, random-subspace probe classification inspired by random forests \citep{{breiman2001rf}}, Bayesian fixture belief, robust impedance planning, adaptive probe-then-act, ensemble uncertainty planning, particle filtering, the old LFI-v4 method, LFI-v5, and an oracle.  Safety-motivated baselines are interpreted in relation to robust control and barrier ideas \citep{{khatib1986potential,ames2017cbf,rawlings2017mpc}}.

\section{{Theory Sketch}}
Let $z_1,\ldots,z_K$ be probe observations and $y$ be a hidden fixture family with continuous parameters $\theta$.  Prototype ID estimates $p(y\mid z)$ from class centroids.  Structured LFI tries to factor the evidence into compliance anisotropy, torque/rotation coupling, release cues, recoil hysteresis, and fixture-conditioned action constraints.  Identifiability fails when two fixture families induce overlapping probe statistics under the available force directions.  The v5 protocol therefore requires not only success, but also fixture accuracy, parameter error, damage, repeated-failure, fixed-risk, and ablation-necessity evidence.

\section{{Main Results}}
{chunked_table("Combined-fixture-stress main results", ["Method", "Success", "Fixture", "Param", "Force", "Damage", "Repeat"], "lcccccc", combined_rows, chunk_size=18)}

The oracle reaches {pm(oracle, "mean_success", "ci95_success")} success.  Against the strongest hostile non-oracle baseline, the paired success difference is ${f(main_pair.get("paired_success_diff", "0"))}\pm {f(main_pair.get("ci95_success_diff", "0"))}$.

{figure("latent_fixture_success.png", "Closed-loop success on the decisive combined-fixture-stress split.")}
{figure("latent_fixture_accuracy.png", "Fixture-family accuracy on the decisive split.")}

\section{{Aggregate Hard Regimes}}
{chunked_table("Aggregate hard-regime metrics", ["Method", "Split", "Success", "Fixture", "Param", "Damage", "Repeat"], "llccccc", aggregate_rows, chunk_size=18)}

The aggregate paired difference against the strongest aggregate baseline is ${f(agg_pair.get("paired_success_diff", "0"))}\pm {f(agg_pair.get("ci95_success_diff", "0"))}$.  This gate prevents cherry-picking a favorable fixture family.

{chunked_table("Aggregate paired comparisons", ["Comparison", "Succ diff", "CI", "Fixture", "Param red", "Damage red", "Wins"], "lcccccc", aggregate_pair_rows, chunk_size=28)}

\section{{Ablations}}
{chunked_table("LFI-v5 ablations", ["Variant", "Success", "Fixture", "Param", "Damage", "Repeat"], "lccccc", ablation_rows, chunk_size=18)}

{figure("latent_fixture_ablation_success.png", "Ablation success. Full v5 must beat component removals to support the mechanism.")}

\section{{Stress Sweep}}
{chunked_table("Stress sweep", ["Method", "Stress", "Success", "Fixture", "Damage", "Repeat"], "llcccc", stress_rows, chunk_size=34)}

At maximum stress {f(max_stress, 2)}, LFI-v5 reaches {pm(stress_v5, "mean_success", "ci95_success")} success while the strongest non-oracle stress baseline reaches {pm(stress_best, "mean_success", "ci95_success")}.  This gate is reported even when unfavorable.

{figure("latent_fixture_stress_sweep.png", "Success under increasing fixture ambiguity, stiffness shift, noise, and slip.")}

\section{{Fixed-Risk Budgets}}
{chunked_table("Fixed-risk budget metrics", ["Method", "Budget", "Success", "Fixture", "Damage", "Repeat", "Efficiency"], "llccccc", fixed_rows, chunk_size=34)}

{chunked_table("Fixed-risk paired comparisons", ["Budget", "Comparison", "Succ diff", "CI", "Fixture", "Damage", "Wins"], "llccccc", fixed_pair_rows, chunk_size=34)}

{figure("latent_fixture_fixed_risk.png", "Fixed-risk success across predefined force/damage budgets.")}

\section{{Negative Cases}}
{chunked_table("Curated combined-stress negative cases", ["Seed", "Scenario", "True", "Estimate", "Action", "Force", "Damage", "Param"], "llllllll", negative_rows, chunk_size=18)}

\section{{Limitations}}
The benchmark is local and diagnostic.  It has no real robot validation, accepted external benchmark evaluation, videos, released neural policy checkpoint, or full manual related-work synthesis.  These limitations would prevent a ready-to-submit claim even if the local gates passed.  If the local gates fail, they justify an archive decision.

\section{{Conclusion}}
Latent fixture inference is an interesting representation, but the v5 protocol demands survival against strong system-ID and robust manipulation baselines.  The correct terminal decision is the one printed above.

\appendix
\section{{Protocol Checklist}}
\begin{{itemize}}
\item CPU-only and RAM-light execution.
\item Frozen reference: \texttt{{LFI-v5}}.
\item Frozen decisive split: \texttt{{combined\_fixture\_stress}}.
\item Frozen risk budgets: {tex_escape(fields.get("risk_budgets", ""))}.
\item Bright boxed citation links.
\item Numbered PDF copied only to Downloads.
\end{{itemize}}

\section{{All Main Metrics}}
{chunked_table("All split-by-method metrics", ["Method", "Split", "Success", "Fixture", "Param", "Damage", "Repeat"], "llccccc", main_rows, chunk_size=34)}

\section{{All Main Pairwise Comparisons}}
{chunked_table("All paired comparisons versus LFI-v5", ["Split", "Comparison", "Succ diff", "CI", "Fixture", "Param red", "Damage red", "Wins"], "llcccccc", pair_rows, chunk_size=34)}

\section{{Seed-Level Main Metrics}}
{chunked_table("Seed-level main metrics", ["Method", "Split", "Seed", "Episodes", "Success", "Fixture", "Param", "Damage", "Repeat"], "llllccccc", seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Aggregate Metrics}}
{chunked_table("Seed-level aggregate metrics", ["Method", "Seed", "Episodes", "Success", "Fixture", "Param", "Damage", "Repeat"], "lllccccc", aggregate_seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Ablation Metrics}}
{chunked_table("Seed-level ablation metrics", ["Variant", "Seed", "Episodes", "Success", "Fixture", "Param", "Damage", "Repeat"], "lllccccc", ablation_seed_rows, chunk_size=38, size=TINY)}

\section{{Seed-Level Fixed-Risk Metrics}}
{chunked_table("Seed-level fixed-risk metrics", ["Method", "Budget", "Seed", "Episodes", "Success", "Fixture", "Damage", "Repeat"], "llllcccc", fixed_seed_rows, chunk_size=38, size=TINY)}

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}

\end{{document}}
"""


def main() -> None:
    PAPER.mkdir(exist_ok=True)
    write_references()
    (PAPER / "main.tex").write_text(manuscript(), encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'}")


if __name__ == "__main__":
    main()
