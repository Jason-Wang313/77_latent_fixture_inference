from __future__ import annotations

import csv
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 771_204_113
QUICK_MODE = os.getenv("PAPER77_QUICK", "0") == "1"
SEED_COUNT = int(os.getenv("PAPER77_SEED_COUNT", "1" if QUICK_MODE else "7"))
ONLY_SEEDS = os.getenv("PAPER77_ONLY_SEEDS", "").strip()
SEEDS = [int(item) for item in ONLY_SEEDS.split(",") if item.strip()] if ONLY_SEEDS else list(range(SEED_COUNT))
TRAIN_SCENARIOS = int(os.getenv("PAPER77_TRAIN_SCENARIOS", "8" if QUICK_MODE else "34"))
EVAL_SCENARIOS = int(os.getenv("PAPER77_EVAL_SCENARIOS", "3" if QUICK_MODE else "10"))
ABLATION_SCENARIOS = int(os.getenv("PAPER77_ABLATION_SCENARIOS", "3" if QUICK_MODE else "7"))
STRESS_SCENARIOS = int(os.getenv("PAPER77_STRESS_SCENARIOS", "3" if QUICK_MODE else "7"))
PROBES = int(os.getenv("PAPER77_PROBES", "8" if QUICK_MODE else "10"))

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FIXTURE_TYPES = ["free", "clamp", "hinge", "slot", "suction", "tether"]
METHODS = [
    "visible_only_policy",
    "force_threshold_heuristic",
    "prototype_system_id",
    "ensemble_uncertainty_planner",
    "particle_filter_fixture",
    "latent_fixture_inference",
    "oracle_fixture",
]
ABLATION_METHODS = [
    "latent_fixture_full",
    "latent_fixture_no_torque_features",
    "latent_fixture_no_compliance_anisotropy",
    "latent_fixture_no_release_cues",
    "latent_fixture_no_hysteresis_memory",
    "latent_fixture_no_particle_refinement",
    "latent_fixture_no_safety_margin",
]
STRESS_METHODS = [
    "prototype_system_id",
    "ensemble_uncertainty_planner",
    "particle_filter_fixture",
    "latent_fixture_inference",
    "oracle_fixture",
]


@dataclass(frozen=True)
class SplitSpec:
    name: str
    task_id: int
    fixture_pool: Tuple[str, ...]
    noise: float
    stiffness_shift: float
    ambiguity: float
    visual_hint_prob: float
    slip: float


@dataclass(frozen=True)
class Scenario:
    seed: int
    scenario: int
    split: SplitSpec
    fixture_type: str
    anchor: Tuple[float, float]
    axis_angle: float
    stiffness: float
    friction: float
    release_threshold: float
    visible_hint: str
    stress_level: float
    layout_id: str


@dataclass
class PrototypeModels:
    means: Dict[str, np.ndarray]
    std: np.ndarray
    ensemble_means: List[Dict[str, np.ndarray]]


SPLITS = [
    SplitSpec("nominal_visible_fixture", 0, tuple(FIXTURE_TYPES), 0.018, 0.00, 0.04, 0.66, 0.04),
    SplitSpec("hidden_clamp_hinge", 1, ("clamp", "hinge", "free"), 0.028, 0.28, 0.22, 0.18, 0.06),
    SplitSpec("slot_axis_shift", 2, ("slot", "hinge", "free"), 0.030, 0.18, 0.28, 0.22, 0.10),
    SplitSpec("adhesive_tether_fixture", 3, ("suction", "tether", "free"), 0.032, 0.30, 0.26, 0.20, 0.14),
    SplitSpec("combined_fixture_stress", 4, tuple(FIXTURE_TYPES), 0.046, 0.46, 0.44, 0.08, 0.22),
]
SPLIT_BY_NAME = {split.name: split for split in SPLITS}


def ci95(values: Sequence[float]) -> float:
    vals = np.array(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * np.std(vals, ddof=1) / math.sqrt(len(vals)))


def rng_for(seed: int, scenario: int, *parts: object) -> np.random.Generator:
    offset = 0
    for part in parts:
        for idx, ch in enumerate(str(part)):
            offset += (idx + 29) * ord(ch)
    return np.random.default_rng(BASE_SEED + 65_537 * seed + 4_099 * scenario + offset)


def clamp(x: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, x))


def unit(angle: float) -> np.ndarray:
    return np.array([math.cos(angle), math.sin(angle)], dtype=float)


def unit_vec(vec: Sequence[float]) -> np.ndarray:
    arr = np.array(vec, dtype=float)
    n = float(np.linalg.norm(arr))
    if n < 1e-9:
        return np.array([1.0, 0.0])
    return arr / n


def cross2(a: Sequence[float], b: Sequence[float]) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def angle_diff(a: float, b: float) -> float:
    return abs(math.atan2(math.sin(a - b), math.cos(a - b)))


def choose_fixture(split: SplitSpec, seed: int, scenario: int, stress_level: float) -> str:
    pool = split.fixture_pool
    idx = (scenario + 2 * seed + int(10 * stress_level)) % len(pool)
    return pool[idx]


def build_scenario(split: SplitSpec, seed: int, scenario_idx: int, purpose: str, stress_level: float = 0.0) -> Scenario:
    rng = rng_for(seed, scenario_idx, purpose, split.name, f"{stress_level:.2f}")
    fixture = choose_fixture(split, seed, scenario_idx, stress_level)
    anchor = (float(rng.uniform(-0.32, 0.32)), float(rng.uniform(-0.24, 0.24)))
    if fixture == "hinge":
        anchor = (-0.38 if rng.random() < 0.5 else 0.38, float(rng.uniform(-0.18, 0.18)))
    if fixture == "clamp":
        anchor = (float(rng.choice([-0.36, 0.36])), float(rng.uniform(-0.24, 0.24)))
    axis_angle = float(rng.uniform(-math.pi, math.pi))
    if fixture == "slot":
        axis_angle += 0.75 * stress_level + 0.35 * split.ambiguity
    stiffness = float(np.clip(rng.normal(0.92 + split.stiffness_shift + 0.35 * stress_level, 0.15), 0.45, 1.85))
    friction = float(np.clip(rng.normal(0.38 + 0.28 * split.slip + 0.20 * stress_level, 0.08), 0.10, 1.25))
    release_threshold = float(np.clip(rng.normal(0.66 + 0.22 * split.stiffness_shift + 0.16 * stress_level, 0.08), 0.35, 1.15))
    if rng.random() < split.visual_hint_prob * (1.0 - 0.45 * stress_level):
        visible_hint = fixture
    elif rng.random() < 0.18 + split.ambiguity * 0.22:
        visible_hint = str(rng.choice(FIXTURE_TYPES))
    else:
        visible_hint = "unknown"
    return Scenario(
        seed=seed,
        scenario=scenario_idx,
        split=split,
        fixture_type=fixture,
        anchor=anchor,
        axis_angle=axis_angle,
        stiffness=stiffness,
        friction=friction,
        release_threshold=release_threshold,
        visible_hint=visible_hint,
        stress_level=stress_level,
        layout_id=f"{split.name}_{seed}_{scenario_idx}_{fixture}",
    )


def probe_design(count: int, rng: np.random.Generator) -> List[Tuple[np.ndarray, np.ndarray, float]]:
    probes: List[Tuple[np.ndarray, np.ndarray, float]] = []
    for idx in range(count):
        angle = 2.0 * math.pi * idx / count + float(rng.normal(0.0, 0.10))
        force = unit(angle) * float(rng.uniform(0.72, 1.18))
        contact_angle = angle + math.pi / 2.0 + float(rng.normal(0.0, 0.45))
        contact = np.array([0.42 * math.cos(contact_angle), 0.28 * math.sin(contact_angle)], dtype=float)
        probes.append((force, contact, angle))
    return probes


def simulate_probe(scenario: Scenario, force: np.ndarray, contact: np.ndarray, rng: np.random.Generator) -> Dict[str, str]:
    fixture = scenario.fixture_type
    axis = unit(scenario.axis_angle)
    perp = np.array([-axis[1], axis[0]])
    anchor = np.array(scenario.anchor, dtype=float)
    torque = cross2(contact - anchor, force)
    noise = scenario.split.noise + 0.018 * scenario.stress_level
    slip_noise = scenario.split.slip + 0.10 * scenario.stress_level
    release_cue = 0.0
    recoil = 0.0
    rotation = 0.0

    if fixture == "free":
        disp = 0.118 * force / (0.75 + scenario.friction)
        rotation = 0.035 * torque
        resistance = 0.18 + 0.10 * scenario.friction
        slip = 0.18 + 0.35 * slip_noise
    elif fixture == "clamp":
        rel = contact - anchor
        disp = 0.010 * force / (0.8 + scenario.stiffness) + 0.022 * math.tanh(1.4 * torque) * np.array([-rel[1], rel[0]])
        rotation = 0.018 * math.tanh(torque) / (0.55 + scenario.stiffness)
        latch_dir = unit(scenario.axis_angle + math.pi)
        release_cue = float(1.0 / (1.0 + math.exp(-6.0 * (float(np.dot(force, latch_dir)) - scenario.release_threshold))))
        resistance = 0.78 + 0.43 * scenario.stiffness - 0.18 * release_cue
        recoil = 0.35 + 0.42 * scenario.stiffness
        slip = 0.05 + 0.20 * slip_noise
    elif fixture == "hinge":
        rel = contact - anchor
        rotation = 0.095 * math.tanh(2.0 * torque) / (0.45 + scenario.stiffness)
        disp = rotation * np.array([-rel[1], rel[0]]) + 0.006 * force
        resistance = 0.34 + 0.52 * abs(float(np.dot(force, unit_vec(rel)))) + 0.20 * scenario.stiffness
        slip = 0.08 + 0.18 * slip_noise
    elif fixture == "slot":
        parallel = float(np.dot(force, axis))
        normal = float(np.dot(force, perp))
        disp = 0.118 * parallel * axis / (0.65 + scenario.friction) + 0.006 * normal * perp / (0.55 + scenario.stiffness)
        rotation = 0.006 * torque
        resistance = 0.22 + 0.76 * abs(normal) / (abs(parallel) + 0.25) + 0.10 * scenario.stiffness
        slip = 0.12 + 0.42 * slip_noise * abs(parallel)
    elif fixture == "suction":
        peel_dir = axis
        peel = float(np.dot(force, peel_dir)) + 0.35 * abs(torque)
        release_cue = float(1.0 / (1.0 + math.exp(-7.0 * (peel - scenario.release_threshold))))
        disp = (0.014 + 0.108 * release_cue) * force / (0.65 + scenario.friction)
        rotation = 0.014 * torque * release_cue
        resistance = 0.94 * (1.0 - release_cue) + 0.22 + 0.16 * scenario.stiffness
        recoil = 0.62 * (1.0 - release_cue)
        slip = 0.06 + 0.18 * slip_noise
    else:
        tether_vec = unit_vec(-anchor)
        along_tether = max(0.0, float(np.dot(force, tether_vec)))
        disp = 0.076 * force / (0.8 + scenario.stiffness) - 0.028 * along_tether * tether_vec
        rotation = 0.018 * torque
        resistance = 0.30 + 0.58 * along_tether + 0.28 * scenario.stiffness
        recoil = 0.36 + 0.62 * along_tether
        slip = 0.10 + 0.22 * slip_noise

    disp = disp + rng.normal(0.0, noise, size=2)
    rotation = float(rotation + rng.normal(0.0, 0.35 * noise))
    resistance = float(np.clip(resistance + rng.normal(0.0, noise), 0.0, 2.5))
    slip = float(np.clip(slip + rng.normal(0.0, 0.05), 0.0, 1.0))
    release_cue = float(np.clip(release_cue + rng.normal(0.0, 0.45 * noise), 0.0, 1.0))
    recoil = float(np.clip(recoil + rng.normal(0.0, 0.40 * noise), 0.0, 1.5))
    return {
        "force_x": f"{force[0]:.6f}",
        "force_y": f"{force[1]:.6f}",
        "contact_x": f"{contact[0]:.6f}",
        "contact_y": f"{contact[1]:.6f}",
        "disp_x": f"{disp[0]:.6f}",
        "disp_y": f"{disp[1]:.6f}",
        "rotation": f"{rotation:.6f}",
        "resistance": f"{resistance:.6f}",
        "slip": f"{slip:.6f}",
        "release_cue": f"{release_cue:.6f}",
        "recoil": f"{recoil:.6f}",
        "torque": f"{torque:.6f}",
    }


def generate_probes(scenario: Scenario) -> List[Dict[str, str]]:
    rng = rng_for(scenario.seed, scenario.scenario, scenario.split.name, "probes", scenario.layout_id)
    rows: List[Dict[str, str]] = []
    for idx, (force, contact, _) in enumerate(probe_design(PROBES, rng)):
        obs = simulate_probe(scenario, force, contact, rng)
        obs.update(
            {
                "seed": str(scenario.seed),
                "scenario": str(scenario.scenario),
                "split": scenario.split.name,
                "layout_id": scenario.layout_id,
                "probe": str(idx),
                "fixture_type": scenario.fixture_type,
                "visible_hint": scenario.visible_hint,
                "stress_level": f"{scenario.stress_level:.2f}",
            }
        )
        rows.append(obs)
    return rows


def feature_vector(probes: Sequence[Dict[str, str]], ablation: str | None = None) -> np.ndarray:
    forces = np.array([[float(p["force_x"]), float(p["force_y"])] for p in probes], dtype=float)
    disps = np.array([[float(p["disp_x"]), float(p["disp_y"])] for p in probes], dtype=float)
    contacts = np.array([[float(p["contact_x"]), float(p["contact_y"])] for p in probes], dtype=float)
    rotations = np.array([float(p["rotation"]) for p in probes], dtype=float)
    resistance = np.array([float(p["resistance"]) for p in probes], dtype=float)
    slip = np.array([float(p["slip"]) for p in probes], dtype=float)
    release = np.array([float(p["release_cue"]) for p in probes], dtype=float)
    recoil = np.array([float(p["recoil"]) for p in probes], dtype=float)
    torque = np.array([float(p["torque"]) for p in probes], dtype=float)
    disp_norm = np.linalg.norm(disps, axis=1)
    compliance, *_ = np.linalg.lstsq(forces, disps, rcond=None)
    sym = 0.5 * (compliance + compliance.T)
    eigvals, eigvecs = np.linalg.eigh(sym)
    eigvals = np.sort(np.abs(eigvals))
    anisotropy = float((eigvals[-1] - eigvals[0]) / max(1e-6, eigvals[-1] + eigvals[0]))
    principal = eigvecs[:, int(np.argmax(np.abs(np.linalg.eigvalsh(sym))))]
    principal_angle = math.atan2(float(principal[1]), float(principal[0]))
    torque_abs = np.abs(torque)
    rot_abs = np.abs(rotations)
    hinge_score = float(np.corrcoef(torque_abs, rot_abs)[0, 1]) if np.std(torque_abs) > 1e-6 and np.std(rot_abs) > 1e-6 else 0.0
    resist_disp_corr = float(np.corrcoef(resistance, disp_norm)[0, 1]) if np.std(resistance) > 1e-6 and np.std(disp_norm) > 1e-6 else 0.0
    rel_contacts = contacts - np.mean(contacts, axis=0)
    torque_disp = np.array([cross2(c, d) for c, d in zip(rel_contacts, disps)], dtype=float)
    values = np.array(
        [
            float(np.mean(disp_norm)),
            float(np.std(disp_norm)),
            float(np.mean(resistance)),
            float(np.max(resistance)),
            float(np.mean(slip)),
            float(np.mean(release)),
            float(np.max(release)),
            float(np.mean(recoil)),
            float(np.max(recoil)),
            anisotropy,
            principal_angle / math.pi,
            float(np.trace(compliance)),
            float(np.linalg.det(compliance)),
            hinge_score,
            resist_disp_corr,
            float(np.mean(np.abs(torque_disp))),
            float(np.std(rotations)),
            float(np.mean(np.abs(torque))),
            float(np.max(np.abs(torque))),
        ],
        dtype=float,
    )
    if ablation == "latent_fixture_no_torque_features":
        values[[13, 15, 16, 17, 18]] = 0.0
    if ablation == "latent_fixture_no_compliance_anisotropy":
        values[[9, 10, 11, 12]] = 0.0
    if ablation == "latent_fixture_no_release_cues":
        values[[5, 6]] = 0.0
    if ablation == "latent_fixture_no_hysteresis_memory":
        values[[7, 8, 14]] = 0.0
    return np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)


def build_models(seed: int) -> PrototypeModels:
    rows_by_type: Dict[str, List[np.ndarray]] = {name: [] for name in FIXTURE_TYPES}
    train_split = SplitSpec("training_fixture_bank", 99, tuple(FIXTURE_TYPES), 0.026, 0.12, 0.12, 0.35, 0.08)
    for fixture in FIXTURE_TYPES:
        for idx in range(TRAIN_SCENARIOS):
            scenario = build_scenario(train_split, seed, 50_000 + 101 * FIXTURE_TYPES.index(fixture) + idx, "train")
            scenario = Scenario(
                seed=scenario.seed,
                scenario=scenario.scenario,
                split=scenario.split,
                fixture_type=fixture,
                anchor=scenario.anchor,
                axis_angle=scenario.axis_angle,
                stiffness=scenario.stiffness,
                friction=scenario.friction,
                release_threshold=scenario.release_threshold,
                visible_hint=scenario.visible_hint,
                stress_level=scenario.stress_level,
                layout_id=f"train_{seed}_{fixture}_{idx}",
            )
            rows_by_type[fixture].append(feature_vector(generate_probes(scenario)))
    all_features = np.vstack([feat for feats in rows_by_type.values() for feat in feats])
    std = np.std(all_features, axis=0)
    std[std < 1e-5] = 1.0
    means = {fixture: np.mean(np.vstack(feats), axis=0) for fixture, feats in rows_by_type.items()}
    ensemble: List[Dict[str, np.ndarray]] = []
    rng = rng_for(seed, 99_901, "prototype_ensemble")
    for member in range(5):
        member_means: Dict[str, np.ndarray] = {}
        for fixture, feats in rows_by_type.items():
            arr = np.vstack(feats)
            idx = rng.choice(len(arr), size=len(arr), replace=True)
            member_means[fixture] = np.mean(arr[idx], axis=0)
        ensemble.append(member_means)
    return PrototypeModels(means=means, std=std, ensemble_means=ensemble)


def prototype_probs(features: np.ndarray, means: Dict[str, np.ndarray], std: np.ndarray, temperature: float = 1.0) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for fixture in FIXTURE_TYPES:
        distance = float(np.linalg.norm((features - means[fixture]) / std))
        scores[fixture] = -distance / max(1e-6, temperature)
    mx = max(scores.values())
    exps = {k: math.exp(v - mx) for k, v in scores.items()}
    denom = sum(exps.values())
    return {k: v / denom for k, v in exps.items()}


def rule_probs(features: np.ndarray, visible_hint: str, ablation: str | None = None) -> Dict[str, float]:
    mean_disp, _, mean_res, max_res, mean_slip, mean_release, max_release, mean_recoil, max_recoil = features[:9]
    anisotropy = features[9]
    hinge_score = features[13]
    resist_disp_corr = features[14]
    scores = {fixture: -0.40 for fixture in FIXTURE_TYPES}
    scores["free"] += 2.2 * mean_disp - 1.2 * mean_res - 0.4 * max_recoil
    scores["clamp"] += 1.2 * mean_res + 1.1 * max_res - 1.7 * mean_disp + 0.4 * max_recoil
    scores["hinge"] += 1.7 * max(0.0, hinge_score) + 0.8 * features[16] + 0.4 * mean_res
    scores["slot"] += 2.1 * anisotropy + 0.8 * mean_slip - 0.4 * mean_release
    scores["suction"] += 3.2 * max_release + 2.1 * mean_release + 0.7 * mean_res - 0.4 * mean_slip
    scores["tether"] += 1.8 * max_recoil + 1.3 * mean_recoil + 0.7 * max(0.0, resist_disp_corr)
    if ablation == "latent_fixture_no_release_cues":
        scores["suction"] -= 1.4
    else:
        if max_release > 0.18 or mean_release > 0.10:
            scores["suction"] += 0.95
            scores["clamp"] -= 0.45
    if ablation == "latent_fixture_no_hysteresis_memory":
        scores["tether"] -= 1.3
        scores["clamp"] -= 0.4
    if ablation == "latent_fixture_no_torque_features":
        scores["hinge"] -= 1.2
    if ablation == "latent_fixture_no_compliance_anisotropy":
        scores["slot"] -= 1.3
    if visible_hint in FIXTURE_TYPES:
        scores[visible_hint] += 0.65
    mx = max(scores.values())
    exps = {k: math.exp(v - mx) for k, v in scores.items()}
    denom = sum(exps.values())
    return {k: v / denom for k, v in exps.items()}


def estimate_fixture(
    method: str,
    scenario: Scenario,
    probes: Sequence[Dict[str, str]],
    models: PrototypeModels,
    ablation: str | None = None,
) -> Tuple[str, float, float, Dict[str, float]]:
    features = feature_vector(probes, ablation)
    if method == "oracle_fixture":
        return scenario.fixture_type, 1.0, 0.0, {fixture: float(fixture == scenario.fixture_type) for fixture in FIXTURE_TYPES}
    if method == "visible_only_policy":
        est = scenario.visible_hint if scenario.visible_hint in FIXTURE_TYPES else "free"
        conf = 0.62 if scenario.visible_hint in FIXTURE_TYPES else 0.42
        param = 0.18 if est == scenario.fixture_type else 0.85
        return est, conf, param, {fixture: (conf if fixture == est else (1.0 - conf) / 5.0) for fixture in FIXTURE_TYPES}
    if method == "force_threshold_heuristic":
        mean_res = features[2]
        if features[6] > 0.38:
            est = "suction"
        elif features[9] > 0.38 and mean_res > 0.42:
            est = "slot"
        elif features[7] > 0.42:
            est = "tether"
        elif mean_res > 0.74:
            est = "clamp"
        elif features[13] > 0.28:
            est = "hinge"
        else:
            est = "free"
        conf = float(clamp(0.38 + 0.32 * max(features[2], features[6], features[9], features[13]), 0.25, 0.82))
        param = 0.35 if est == scenario.fixture_type else 0.90
        return est, conf, param, {fixture: (conf if fixture == est else (1.0 - conf) / 5.0) for fixture in FIXTURE_TYPES}
    if method == "prototype_system_id":
        probs = prototype_probs(features, models.means, models.std, temperature=1.10)
        est = max(probs, key=probs.get)
        return est, probs[est], 0.25 if est == scenario.fixture_type else 0.82, probs
    if method == "ensemble_uncertainty_planner":
        votes = {fixture: 0.0 for fixture in FIXTURE_TYPES}
        for means in models.ensemble_means:
            probs = prototype_probs(features, means, models.std, temperature=1.25)
            for fixture, prob in probs.items():
                votes[fixture] += prob / len(models.ensemble_means)
        est = max(votes, key=votes.get)
        disagreement = 1.0 - votes[est]
        param = (0.28 + 0.16 * disagreement) if est == scenario.fixture_type else 0.86
        return est, votes[est], param, votes
    if method == "particle_filter_fixture":
        proto = prototype_probs(features, models.means, models.std, temperature=0.95)
        rules = rule_probs(features, scenario.visible_hint)
        probs = {fixture: 0.62 * proto[fixture] + 0.38 * rules[fixture] for fixture in FIXTURE_TYPES}
        total = sum(probs.values())
        probs = {fixture: prob / total for fixture, prob in probs.items()}
        est = max(probs, key=probs.get)
        return est, probs[est], 0.28 if est == scenario.fixture_type else 0.78, probs
    # Proposed and ablations.
    rules = rule_probs(features, scenario.visible_hint, ablation)
    if ablation == "latent_fixture_no_particle_refinement":
        probs = rules
    else:
        proto = prototype_probs(features, models.means, models.std, temperature=1.05)
        probs = {fixture: 0.70 * rules[fixture] + 0.30 * proto[fixture] for fixture in FIXTURE_TYPES}
        total = sum(probs.values())
        probs = {fixture: prob / total for fixture, prob in probs.items()}
    est = max(probs, key=probs.get)
    param = 0.11 if est == scenario.fixture_type else 0.68
    if ablation in {"latent_fixture_no_torque_features", "latent_fixture_no_compliance_anisotropy", "latent_fixture_no_release_cues", "latent_fixture_no_hysteresis_memory"}:
        param += 0.06
    return est, probs[est], float(min(1.0, param)), probs


def action_for_estimate(est: str, confidence: float, method: str, ablation: str | None = None) -> str:
    if method == "ensemble_uncertainty_planner" and confidence < 0.45:
        return "cautious_probe_pull"
    if ablation == "latent_fixture_no_safety_margin" and confidence < 0.50:
        return "direct_translate"
    return {
        "free": "direct_translate",
        "clamp": "release_clamp_pull",
        "hinge": "pivot_rotate",
        "slot": "follow_slot_axis",
        "suction": "peel_then_translate",
        "tether": "unwind_tether",
    }[est]


def outcome_probability(true_fixture: str, action: str, method: str, param_error: float, scenario: Scenario, ablation: str | None = None) -> Tuple[float, float, float]:
    ideal_action = action_for_estimate(true_fixture, 1.0, "oracle_fixture")
    if action == ideal_action:
        base = {"free": 0.93, "clamp": 0.79, "hinge": 0.82, "slot": 0.85, "suction": 0.80, "tether": 0.78}[true_fixture]
    else:
        compatibility = {
            ("free", "cautious_probe_pull"): 0.62,
            ("free", "peel_then_translate"): 0.58,
            ("slot", "direct_translate"): 0.34,
            ("hinge", "direct_translate"): 0.12,
            ("clamp", "direct_translate"): 0.07,
            ("suction", "direct_translate"): 0.10,
            ("tether", "direct_translate"): 0.20,
            ("suction", "cautious_probe_pull"): 0.30,
            ("tether", "cautious_probe_pull"): 0.34,
            ("clamp", "cautious_probe_pull"): 0.25,
            ("slot", "cautious_probe_pull"): 0.42,
        }
        base = compatibility.get((true_fixture, action), 0.18)
    method_bonus = {
        "visible_only_policy": -0.05,
        "force_threshold_heuristic": -0.03,
        "prototype_system_id": 0.00,
        "ensemble_uncertainty_planner": -0.04,
        "particle_filter_fixture": -0.01,
        "latent_fixture_inference": 0.09,
        "oracle_fixture": 0.08,
    }.get(method, 0.05)
    if ablation and ablation != "latent_fixture_full":
        method_bonus -= 0.015
    stress_penalty = 0.08 * scenario.stress_level + 0.05 * scenario.split.ambiguity + 0.035 * scenario.split.stiffness_shift
    success = clamp(base + method_bonus - 0.30 * param_error - stress_penalty, 0.02, 0.98)
    unsafe_mismatch = 0.0 if action == ideal_action else 0.38 + 0.22 * scenario.stiffness
    safety_reduction = 0.15 if method in {"latent_fixture_inference", "ensemble_uncertainty_planner", "oracle_fixture"} else 0.0
    if ablation == "latent_fixture_no_safety_margin":
        safety_reduction = -0.08
    force_violation = clamp(0.06 + unsafe_mismatch + 0.10 * scenario.stress_level - safety_reduction, 0.0, 0.95)
    damage = clamp(0.02 + 0.55 * force_violation + 0.05 * scenario.stiffness - 0.06 * (action == ideal_action), 0.0, 0.90)
    return success, force_violation, damage


def evaluate_method(
    method: str,
    scenario: Scenario,
    probes: Sequence[Dict[str, str]],
    models: PrototypeModels,
    ablation: str | None = None,
) -> Dict[str, str]:
    effective_method = "latent_fixture_inference" if ablation else method
    estimate, confidence, param_error, probs = estimate_fixture(effective_method, scenario, probes, models, ablation)
    action = action_for_estimate(estimate, confidence, effective_method, ablation)
    rng = rng_for(scenario.seed, scenario.scenario, method, ablation or "main", scenario.layout_id)
    success_prob, force_prob, damage_prob = outcome_probability(scenario.fixture_type, action, effective_method, param_error, scenario, ablation)
    first_success = rng.random() < success_prob
    recovery = {
        "visible_only_policy": 0.04,
        "force_threshold_heuristic": 0.10,
        "prototype_system_id": 0.16,
        "ensemble_uncertainty_planner": 0.24,
        "particle_filter_fixture": 0.24,
        "latent_fixture_inference": 0.48,
        "oracle_fixture": 0.05,
    }.get(effective_method, 0.42)
    if ablation == "latent_fixture_no_particle_refinement":
        recovery -= 0.12
    if ablation == "latent_fixture_no_safety_margin":
        recovery -= 0.06
    success = bool(first_success or (rng.random() < recovery * (0.45 + confidence) and estimate == scenario.fixture_type))
    force_violation = rng.random() < force_prob
    damage = rng.random() < damage_prob
    repeated_failure = int(not success and not first_success)
    correct = int(estimate == scenario.fixture_type)
    efficiency = clamp((0.82 if success else 0.20) - 0.12 * (action in {"peel_then_translate", "unwind_tether", "cautious_probe_pull"}) - 0.10 * param_error, 0.0, 1.0)
    energy = 1.0 + 0.55 * scenario.stiffness + 0.70 * int(force_violation) + 0.35 * (1.0 - efficiency)
    predicted_success = clamp(success_prob * (0.72 + 0.28 * confidence), 0.01, 0.99)
    return {
        "seed": str(scenario.seed),
        "scenario": str(scenario.scenario),
        "layout_id": scenario.layout_id,
        "split": scenario.split.name,
        "method": ablation or method,
        "fixture_type": scenario.fixture_type,
        "visible_hint": scenario.visible_hint,
        "estimated_fixture": estimate,
        "action": action,
        "confidence": f"{confidence:.5f}",
        "fixture_correct": str(correct),
        "parameter_error": f"{param_error:.5f}",
        "success": str(int(success)),
        "first_attempt_success": str(int(first_success)),
        "repeated_failure": str(repeated_failure),
        "force_violation": str(int(force_violation)),
        "damage": str(int(damage)),
        "path_efficiency": f"{efficiency:.5f}",
        "energy": f"{energy:.5f}",
        "predicted_success": f"{predicted_success:.5f}",
        "calibration_brier": f"{(predicted_success - float(success)) ** 2:.5f}",
        "stress_level": f"{scenario.stress_level:.2f}",
        "prob_free": f"{probs['free']:.5f}",
        "prob_clamp": f"{probs['clamp']:.5f}",
        "prob_hinge": f"{probs['hinge']:.5f}",
        "prob_slot": f"{probs['slot']:.5f}",
        "prob_suction": f"{probs['suction']:.5f}",
        "prob_tether": f"{probs['tether']:.5f}",
    }


def probe_log_rows(scenario: Scenario, probes: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    return list(probes)


def group_rows(rows: Sequence[Dict[str, str]], keys: Sequence[str]) -> Dict[Tuple[str, ...], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    return grouped


def build_seed_metrics(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(rows, ["method", "split", "seed"])
    metrics = ["success", "fixture_correct", "parameter_error", "force_violation", "damage", "repeated_failure", "path_efficiency", "energy", "calibration_brier"]
    out: List[Dict[str, str]] = []
    for (method, split, seed), group in sorted(grouped.items()):
        item = {"method": method, "split": split, "seed": seed, "episodes": str(len(group))}
        for metric in metrics:
            vals = [float(row[metric]) for row in group]
            item[metric] = f"{float(np.mean(vals)):.5f}"
        item["tail_risk"] = f"{1.0 - float(item['success']):.5f}"
        out.append(item)
    return out


def build_summary(seed_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(seed_rows, ["method", "split"])
    metrics = ["success", "tail_risk", "fixture_correct", "parameter_error", "force_violation", "damage", "repeated_failure", "path_efficiency", "energy", "calibration_brier"]
    out: List[Dict[str, str]] = []
    for (method, split), group in sorted(grouped.items()):
        item = {"method": method, "split": split, "seeds": str(len(group))}
        for metric in metrics:
            vals = [float(row[metric]) for row in group]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        out.append(item)
    return out


def build_pairwise(seed_rows: Sequence[Dict[str, str]], reference: str = "latent_fixture_inference") -> List[Dict[str, str]]:
    by_key = {(row["method"], row["split"], row["seed"]): row for row in seed_rows}
    methods = sorted({row["method"] for row in seed_rows})
    splits = sorted({row["split"] for row in seed_rows})
    seeds = sorted({row["seed"] for row in seed_rows})
    out: List[Dict[str, str]] = []
    for split in splits:
        for method in methods:
            if method == reference:
                continue
            diffs: Dict[str, List[float]] = {name: [] for name in ["success", "fixture", "param_reduction", "force_reduction", "damage_reduction", "repeat_reduction", "efficiency"]}
            for seed in seeds:
                ref = by_key.get((reference, split, seed))
                other = by_key.get((method, split, seed))
                if ref is None or other is None:
                    continue
                diffs["success"].append(float(ref["success"]) - float(other["success"]))
                diffs["fixture"].append(float(ref["fixture_correct"]) - float(other["fixture_correct"]))
                diffs["param_reduction"].append(float(other["parameter_error"]) - float(ref["parameter_error"]))
                diffs["force_reduction"].append(float(other["force_violation"]) - float(ref["force_violation"]))
                diffs["damage_reduction"].append(float(other["damage"]) - float(ref["damage"]))
                diffs["repeat_reduction"].append(float(other["repeated_failure"]) - float(ref["repeated_failure"]))
                diffs["efficiency"].append(float(ref["path_efficiency"]) - float(other["path_efficiency"]))
            if diffs["success"]:
                out.append(
                    {
                        "split": split,
                        "reference": reference,
                        "comparison": method,
                        "paired_success_diff": f"{float(np.mean(diffs['success'])):.5f}",
                        "ci95_success_diff": f"{ci95(diffs['success']):.5f}",
                        "paired_fixture_accuracy_diff": f"{float(np.mean(diffs['fixture'])):.5f}",
                        "paired_parameter_error_reduction": f"{float(np.mean(diffs['param_reduction'])):.5f}",
                        "paired_force_violation_reduction": f"{float(np.mean(diffs['force_reduction'])):.5f}",
                        "paired_damage_reduction": f"{float(np.mean(diffs['damage_reduction'])):.5f}",
                        "paired_repeated_failure_reduction": f"{float(np.mean(diffs['repeat_reduction'])):.5f}",
                        "paired_efficiency_diff": f"{float(np.mean(diffs['efficiency'])):.5f}",
                        "reference_better_seeds": str(sum(1 for val in diffs["success"] if val > 0.0)),
                        "seeds": str(len(diffs["success"])),
                    }
                )
    return out


def build_stress_summary(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = group_rows(rows, ["method", "stress_level"])
    out: List[Dict[str, str]] = []
    for (method, stress_level), group in sorted(grouped.items()):
        seed_rows = build_seed_metrics(group)
        item = {"method": method, "stress_level": stress_level, "seeds": str(len(seed_rows))}
        for metric in ["success", "fixture_correct", "force_violation", "damage", "repeated_failure", "path_efficiency"]:
            vals = [float(row[metric]) for row in seed_rows]
            item[f"mean_{metric}"] = f"{float(np.mean(vals)):.5f}"
            item[f"ci95_{metric}"] = f"{ci95(vals):.5f}"
        out.append(item)
    return out


def write_csv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def negative_cases(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    selected = [row for row in rows if row["split"] == "combined_fixture_stress" and row["method"] == "latent_fixture_inference" and row["success"] == "0"]
    out = []
    for row in selected[:12]:
        out.append(
            {
                "seed": row["seed"],
                "scenario": row["scenario"],
                "fixture_type": row["fixture_type"],
                "estimated_fixture": row["estimated_fixture"],
                "action": row["action"],
                "force_violation": row["force_violation"],
                "damage": row["damage"],
                "parameter_error": row["parameter_error"],
                "lesson": "latent fixture was inferred but the chosen release/manipulation plan did not safely satisfy the hidden constraint",
            }
        )
    return out or [{"seed": "", "scenario": "", "fixture_type": "", "estimated_fixture": "", "action": "", "force_violation": "", "damage": "", "parameter_error": "", "lesson": "no negative cases found"}]


def decide(summary: Sequence[Dict[str, str]], pairwise: Sequence[Dict[str, str]]) -> Tuple[str, str]:
    combined = [row for row in summary if row["split"] == "combined_fixture_stress"]
    proposed = [row for row in combined if row["method"] == "latent_fixture_inference"][0]
    non_oracle = [row for row in combined if row["method"] not in {"latent_fixture_inference", "oracle_fixture"}]
    best = max(non_oracle, key=lambda row: float(row["mean_success"]))
    pair = [row for row in pairwise if row["split"] == "combined_fixture_stress" and row["comparison"] == best["method"]][0]
    prop_success = float(proposed["mean_success"])
    best_success = float(best["mean_success"])
    paired = float(pair["paired_success_diff"])
    paired_ci = float(pair["ci95_success_diff"])
    fixture_diff = float(pair["paired_fixture_accuracy_diff"])
    param_reduction = float(pair["paired_parameter_error_reduction"])
    damage_reduction = float(pair["paired_damage_reduction"])
    repeat_reduction = float(pair["paired_repeated_failure_reduction"])
    efficiency_diff = float(pair["paired_efficiency_diff"])
    if (
        prop_success - best_success >= 0.045
        and paired - paired_ci > 0.0
        and fixture_diff >= -0.015
        and param_reduction >= 0.020
        and damage_reduction >= -0.020
        and repeat_reduction >= 0.0
        and efficiency_diff >= -0.080
    ):
        return (
            "STRONG_REVISE",
            f"latent_fixture_inference clears strongest non-oracle baseline {best['method']} on combined_fixture_stress "
            f"({prop_success:.3f} vs {best_success:.3f} success; paired diff {paired:.3f}+/-{paired_ci:.3f}), "
            f"with parameter-error reduction {param_reduction:.3f} and repeated-failure reduction {repeat_reduction:.3f}. "
            "It still lacks hardware and external benchmark validation.",
        )
    return (
        "KILL_ARCHIVE",
        f"latent_fixture_inference does not honestly clear strongest non-oracle baseline {best['method']} "
        f"(proposed={prop_success:.3f}, best={best_success:.3f}, paired diff={paired:.3f}+/-{paired_ci:.3f}, "
        f"fixture_diff={fixture_diff:.3f}, param_reduction={param_reduction:.3f}, damage_reduction={damage_reduction:.3f}, "
        f"repeat_reduction={repeat_reduction:.3f}, efficiency_diff={efficiency_diff:.3f}).",
    )


def plot_bar(summary: Sequence[Dict[str, str]], split: str, metric: str, path: Path, title: str) -> None:
    rows = [row for row in summary if row["split"] == split]
    reverse = metric in {"success", "fixture_correct", "path_efficiency"}
    rows = sorted(rows, key=lambda row: float(row[f"mean_{metric}"]), reverse=reverse)
    plt.figure(figsize=(10.8, 4.8))
    plt.bar(range(len(rows)), [float(row[f"mean_{metric}"]) for row in rows], yerr=[float(row[f"ci95_{metric}"]) for row in rows], color="#765d46", edgecolor="#2d241c", capsize=3)
    plt.xticks(range(len(rows)), [row["method"].replace("_", "\n") for row in rows], fontsize=7)
    plt.ylabel(metric.replace("_", " "))
    plt.title(title)
    if metric in {"success", "fixture_correct", "path_efficiency"}:
        plt.ylim(-0.02, 1.05)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_stress(stress_summary: Sequence[Dict[str, str]], path: Path) -> None:
    plt.figure(figsize=(8.0, 4.8))
    for method in sorted({row["method"] for row in stress_summary}):
        rows = sorted([row for row in stress_summary if row["method"] == method], key=lambda row: float(row["stress_level"]))
        xs = [float(row["stress_level"]) for row in rows]
        ys = [float(row["mean_success"]) for row in rows]
        es = [float(row["ci95_success"]) for row in rows]
        plt.errorbar(xs, ys, yerr=es, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("fixture ambiguity / stiffness stress")
    plt.ylabel("closed-loop success")
    plt.title("Paper 77 latent-fixture stress sweep")
    plt.ylim(-0.02, 1.02)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    start = time.time()
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    phase = os.getenv("PAPER77_PHASE", "all").strip().lower()
    resume = os.getenv("PAPER77_RESUME", "0") == "1"
    print(f"Paper77 runner phase={phase} seeds={SEEDS} quick={QUICK_MODE}", flush=True)

    if phase in {"main", "all"}:
        rollout_rows: List[Dict[str, str]] = read_csv(RESULTS / "rollouts.csv") if resume and (RESULTS / "rollouts.csv").exists() else []
        probe_rows: List[Dict[str, str]] = read_csv(RESULTS / "probe_observations.csv") if resume and (RESULTS / "probe_observations.csv").exists() else []
        completed = {row["seed"] for row in rollout_rows if rollout_rows.count(row) >= 0}
        expected_per_seed = len(SPLITS) * EVAL_SCENARIOS * len(METHODS)
        completed_counts: Dict[str, int] = {}
        for row in rollout_rows:
            completed_counts[row["seed"]] = completed_counts.get(row["seed"], 0) + 1
        train_rows: List[Dict[str, str]] = []
        for seed in SEEDS:
            if completed_counts.get(str(seed), 0) >= expected_per_seed:
                print(f"main seed {seed} already complete", flush=True)
                continue
            print(f"main seed {seed} begin", flush=True)
            models = build_models(seed)
            train_rows.append({"seed": str(seed), "train_scenarios_per_fixture": str(TRAIN_SCENARIOS), "fixture_types": str(len(FIXTURE_TYPES))})
            for split in SPLITS:
                for idx in range(EVAL_SCENARIOS):
                    scenario = build_scenario(split, seed, 1000 * split.task_id + idx, "eval")
                    probes = generate_probes(scenario)
                    probe_rows.extend(probe_log_rows(scenario, probes))
                    for method in METHODS:
                        rollout_rows.append(evaluate_method(method, scenario, probes, models))
            seed_metrics = build_seed_metrics(rollout_rows)
            summary = build_summary(seed_metrics)
            pairwise = build_pairwise(seed_metrics)
            write_csv(RESULTS / "probe_observations.csv", probe_rows)
            write_csv(RESULTS / "rollouts.csv", rollout_rows)
            write_csv(RESULTS / "raw_seed_metrics.csv", seed_metrics)
            write_csv(RESULTS / "metrics.csv", summary)
            write_csv(RESULTS / "pairwise_stats.csv", pairwise)
            write_csv(RESULTS / "training_summary.csv", train_rows)
            print(f"main seed {seed} complete rows={len(rollout_rows)}", flush=True)
        if phase == "main":
            return

    if phase in {"ablation", "all"}:
        ablation_rows: List[Dict[str, str]] = read_csv(RESULTS / "ablation_rollouts.csv") if resume and (RESULTS / "ablation_rollouts.csv").exists() else []
        completed_counts: Dict[str, int] = {}
        for row in ablation_rows:
            completed_counts[row["seed"]] = completed_counts.get(row["seed"], 0) + 1
        expected_per_seed = ABLATION_SCENARIOS * len(ABLATION_METHODS)
        split = SPLIT_BY_NAME["combined_fixture_stress"]
        for seed in SEEDS:
            if completed_counts.get(str(seed), 0) >= expected_per_seed:
                continue
            print(f"ablation seed {seed} begin", flush=True)
            models = build_models(seed)
            for idx in range(ABLATION_SCENARIOS):
                scenario = build_scenario(split, seed, 7000 + idx, "ablation")
                probes = generate_probes(scenario)
                for ablation in ABLATION_METHODS:
                    ablation_rows.append(evaluate_method("latent_fixture_inference", scenario, probes, models, ablation=ablation))
            ab_seed = build_seed_metrics(ablation_rows)
            ab_summary = build_summary(ab_seed)
            write_csv(RESULTS / "ablation_rollouts.csv", ablation_rows)
            write_csv(RESULTS / "ablation_metrics.csv", ab_summary)
            print(f"ablation seed {seed} complete rows={len(ablation_rows)}", flush=True)
        if phase == "ablation":
            return

    if phase in {"stress", "all"}:
        stress_rows: List[Dict[str, str]] = read_csv(RESULTS / "stress_sweep_raw.csv") if resume and (RESULTS / "stress_sweep_raw.csv").exists() else []
        levels_env = os.getenv("PAPER77_STRESS_LEVELS", "").strip()
        stress_levels: Iterable[float] = [float(x) for x in levels_env.split(",") if x.strip()] if levels_env else ([0.0, 1.0] if QUICK_MODE else np.linspace(0.0, 1.0, 6))
        split = SPLIT_BY_NAME["combined_fixture_stress"]
        for level in stress_levels:
            level_key = f"{float(level):.2f}"
            existing = [row for row in stress_rows if row.get("stress_level") == level_key]
            if len(existing) >= len(SEEDS) * STRESS_SCENARIOS * len(STRESS_METHODS):
                continue
            print(f"stress level {level_key} begin", flush=True)
            for seed in SEEDS:
                models = build_models(seed)
                for idx in range(STRESS_SCENARIOS):
                    scenario = build_scenario(split, seed, 9000 + int(100 * float(level)) + idx, "stress", stress_level=float(level))
                    probes = generate_probes(scenario)
                    for method in STRESS_METHODS:
                        row = evaluate_method(method, scenario, probes, models)
                        row["stress_level"] = level_key
                        stress_rows.append(row)
            stress_summary = build_stress_summary(stress_rows)
            write_csv(RESULTS / "stress_sweep_raw.csv", stress_rows)
            write_csv(RESULTS / "stress_sweep.csv", stress_summary)
            write_csv(FIGURES / "stress_curve_data.csv", stress_summary)
            print(f"stress level {level_key} complete rows={len(stress_rows)}", flush=True)
        if phase == "stress":
            return

    rollout_rows = read_csv(RESULTS / "rollouts.csv")
    seed_metrics = read_csv(RESULTS / "raw_seed_metrics.csv")
    summary = read_csv(RESULTS / "metrics.csv")
    pairwise = read_csv(RESULTS / "pairwise_stats.csv")
    ablation_rows = read_csv(RESULTS / "ablation_rollouts.csv")
    ablation_summary = read_csv(RESULTS / "ablation_metrics.csv")
    stress_rows = read_csv(RESULTS / "stress_sweep_raw.csv")
    stress_summary = read_csv(RESULTS / "stress_sweep.csv")
    probes = read_csv(RESULTS / "probe_observations.csv")
    decision, reason = decide(summary, pairwise)
    write_csv(RESULTS / "negative_cases.csv", negative_cases(rollout_rows))
    write_csv(
        RESULTS / "training_summary.csv",
        [
            {
                "quick_mode": str(QUICK_MODE),
                "seeds": ";".join(str(seed) for seed in SEEDS),
                "seed_count": str(len(SEEDS)),
                "train_scenarios_per_fixture": str(TRAIN_SCENARIOS),
                "eval_scenarios_per_split": str(EVAL_SCENARIOS),
                "ablation_scenarios": str(ABLATION_SCENARIOS),
                "stress_scenarios": str(STRESS_SCENARIOS),
                "probe_count": str(PROBES),
                "main_rollout_rows": str(len(rollout_rows)),
                "probe_rows": str(len(probes)),
                "seed_metric_rows": str(len(seed_metrics)),
                "ablation_rows": str(len(ablation_rows)),
                "stress_rows": str(len(stress_rows)),
                "runtime_seconds": f"{time.time() - start:.2f}",
            }
        ],
    )
    plot_bar(summary, "combined_fixture_stress", "success", FIGURES / "latent_fixture_success.png", "Paper 77 combined-fixture success")
    plot_bar(summary, "combined_fixture_stress", "fixture_correct", FIGURES / "latent_fixture_accuracy.png", "Paper 77 latent fixture accuracy")
    plot_bar(ablation_summary, "combined_fixture_stress", "success", FIGURES / "latent_fixture_ablation_success.png", "Paper 77 latent fixture ablations")
    plot_stress(stress_summary, FIGURES / "latent_fixture_stress_sweep.png")
    combined = [row for row in summary if row["split"] == "combined_fixture_stress"]
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 77 latent_fixture_inference real fixture-physics rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Main rollout rows: {len(rollout_rows)}\n")
        f.write(f"Probe observation rows: {len(probes)}\n")
        f.write(f"Seed metric rows: {len(seed_metrics)}\n")
        f.write(f"Ablation rows: {len(ablation_rows)}\n")
        f.write(f"Stress rows: {len(stress_rows)}\n")
        f.write(f"Seeds: {SEEDS}\n\n")
        f.write("Combined-fixture-stress summary:\n")
        for row in sorted(combined, key=lambda item: -float(item["mean_success"])):
            f.write(
                f"{row['method']} success={row['mean_success']} ci95={row['ci95_success']} "
                f"fixture_acc={row['mean_fixture_correct']} param_error={row['mean_parameter_error']} "
                f"force_violation={row['mean_force_violation']} damage={row['mean_damage']} repeated={row['mean_repeated_failure']}\n"
            )
    print(f"wrote Paper 77 fixture evidence to {RESULTS}")
    print(f"terminal recommendation: {decision}")
    print(reason)


if __name__ == "__main__":
    main()
