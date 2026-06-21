from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOWNLOADS = Path.home() / "Downloads"
DESKTOP = Path.home() / "Desktop"
PDF = DOWNLOADS / "77.pdf"

EXPECTED_COUNTS = {
    "rollouts.csv": 7280,
    "probe_observations.csv": 6720,
    "raw_seed_metrics.csv": 520,
    "metrics.csv": 65,
    "pairwise_stats.csv": 60,
    "aggregate_seed_metrics.csv": 104,
    "aggregate_metrics.csv": 13,
    "aggregate_pairwise_stats.csv": 12,
    "ablation_rollouts.csv": 720,
    "ablation_seed_metrics.csv": 72,
    "ablation_metrics.csv": 9,
    "stress_sweep_raw.csv": 4480,
    "stress_sweep.csv": 70,
    "fixed_risk_raw.csv": 2048,
    "fixed_risk_seed_metrics.csv": 256,
    "fixed_risk_metrics.csv": 32,
    "fixed_risk_pairwise.csv": 28,
    "training_summary.csv": 1,
}

HARD_LOG_PATTERNS = [
    "Overfull",
    "Citation",
    "undefined references",
    "undefined citation",
    "Rerun to get",
    "Package natbib Warning",
    "LaTeX Warning",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pdf_page_count(path: Path) -> int:
    try:
        from pypdf import PdfReader  # type: ignore

        return len(PdfReader(str(path)).pages)
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore

            return len(PdfReader(str(path)).pages)
        except Exception:
            result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())
            raise RuntimeError("could not determine PDF page count")


def main() -> None:
    for name, expected in EXPECTED_COUNTS.items():
        path = RESULTS / name
        require(path.exists(), f"missing {path}")
        rows = read_rows(path)
        require(len(rows) == expected, f"{name} has {len(rows)} rows, expected {expected}")

    negative_cases = read_rows(RESULTS / "negative_cases.csv")
    require(1 <= len(negative_cases) <= 12, f"negative_cases.csv has unexpected row count {len(negative_cases)}")

    summary = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    require("Terminal recommendation:" in summary, "summary lacks terminal recommendation")
    require("Main rollout rows: 7280" in summary, "summary lacks final rollout count")
    require("Probe observation rows: 6720" in summary, "summary lacks final probe count")
    require("Fixed-risk rows: 2048" in summary, "summary lacks fixed-risk row count")
    require("Stress rows: 4480" in summary, "summary lacks stress row count")

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    require("citebordercolor={0 1 0}" in tex, "bright citation boxes are not configured")
    require("pdfborder={0 0 1.6}" in tex, "PDF border width is not configured")
    require("latent_fixture_inference_v5" in tex or "LFI-v5" in tex, "v5 method is absent from manuscript")

    log = (PAPER / "main.log").read_text(encoding="utf-8", errors="ignore")
    hard_hits = [pattern for pattern in HARD_LOG_PATTERNS if pattern in log]
    require(not hard_hits, f"hard LaTeX log patterns found: {hard_hits}")

    require(PDF.exists(), f"missing Downloads PDF {PDF}")
    require(not (DESKTOP / "77.pdf").exists(), "Desktop copy of 77.pdf exists")
    pages = pdf_page_count(PDF)
    require(pages >= 25, f"PDF has {pages} pages, expected at least 25")

    digest = hashlib.sha256(PDF.read_bytes()).hexdigest().upper()
    print(f"validated Paper 77 artifacts: pages={pages}, sha256={digest}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise
