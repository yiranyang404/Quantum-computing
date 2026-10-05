"""Small-scale circuit-level surface-code threshold experiment.

This studies the threshold phenomenon using Stim's rotated surface-code memory
circuit and PyMatching. Fowler et al. instead use a specific eight-step planar
circuit and count logical X errors per cycle; see README.md for the main
differences.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pymatching
import stim


OUTPUT_DIR = Path("outputs")


@dataclass
class Result:
    distance: int
    physical_error_rate: float
    rounds: int
    seed: int
    shots: int
    failures: int
    logical_error_per_experiment: float
    logical_error_per_round: float


def build_circuit(distance: int, rounds: int, p: float) -> stim.Circuit:
    """Create a noisy rotated surface-code logical-X memory experiment."""
    return stim.Circuit.generated(
        "surface_code:rotated_memory_x",
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=p,
        after_reset_flip_probability=p,
        before_measure_flip_probability=p,
        before_round_data_depolarization=p,
    )


def experiment_error_to_round_error(experiment_error: float, rounds: int) -> float:
    """Convert odd-parity failure probability over many rounds to per-round rate."""
    capped = min(max(experiment_error, 0.0), 0.5 - 1e-15)
    return 0.5 * (1.0 - (1.0 - 2.0 * capped) ** (1.0 / rounds))


def sample_point(
    distance: int,
    p: float,
    rounds: int,
    seed: int,
    batch_shots: int,
    min_failures: int,
    max_shots: int,
) -> Result:
    circuit = build_circuit(distance, rounds, p)
    detector_sampler = circuit.compile_detector_sampler(seed=seed)
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matching = pymatching.Matching.from_detector_error_model(detector_error_model)

    shots = 0
    failures = 0
    while shots < max_shots and failures < min_failures:
        current_batch = min(batch_shots, max_shots - shots)
        detection_events, actual_observables = detector_sampler.sample(
            shots=current_batch,
            separate_observables=True,
        )
        predicted_observables = matching.decode_batch(detection_events)
        failures += int(np.count_nonzero(
            np.any(predicted_observables != actual_observables, axis=1)
        ))
        shots += current_batch

    experiment_rate = failures / shots
    return Result(
        distance=distance,
        physical_error_rate=p,
        rounds=rounds,
        seed=seed,
        shots=shots,
        failures=failures,
        logical_error_per_experiment=experiment_rate,
        logical_error_per_round=experiment_error_to_round_error(experiment_rate, rounds),
    )


def save_csv(results: list[Result], path: Path) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Result.__annotations__))
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def plot_results(results: list[Result], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    distances = sorted({result.distance for result in results})
    for distance in distances:
        rows = sorted(
            (result for result in results if result.distance == distance),
            key=lambda result: result.physical_error_rate,
        )
        x = [row.physical_error_rate for row in rows]
        y = [row.logical_error_per_round for row in rows]
        # A zero means the run did not observe a failure, not that the true rate is zero.
        y_for_plot = [value if value > 0 else np.nan for value in y]
        ax.loglog(x, y_for_plot, marker="o", label=f"d={distance}")

    ax.set_xlabel(r"Physical error probability $p$")
    ax.set_ylabel("Estimated logical failure rate per round (parity model)")
    ax.set_title("Rotated surface-code memory: logical-error scan")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def available_output_paths(output_dir: Path) -> tuple[Path, Path]:
    """Keep earlier results by choosing a fresh pair of filenames."""
    run_number = 1
    while True:
        suffix = "" if run_number == 1 else f"_run{run_number}"
        csv_path = output_dir / f"threshold_results{suffix}.csv"
        figure_path = output_dir / f"threshold_scan{suffix}.png"
        if not csv_path.exists() and not figure_path.exists():
            return csv_path, figure_path
        run_number += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7, 9, 11])
    parser.add_argument(
        "--error-rates",
        type=float,
        nargs="+",
        default=[0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008, 0.01],
    )
    parser.add_argument("--rounds", type=int, default=0,
                        help="Rounds per experiment; 0 means rounds=distance.")
    parser.add_argument("--batch-shots", type=int, default=10_000)
    parser.add_argument("--min-failures", type=int, default=200)
    parser.add_argument("--max-shots", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=12345,
                        help="Base Stim seed; each (distance, p) point gets the next seed.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed < 0 or args.seed + len(args.distances) * len(args.error_rates) > 2**64:
        raise ValueError("The seed for every point must be in [0, 2**64).")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []

    for distance in args.distances:
        rounds = args.rounds or distance
        for p in args.error_rates:
            result = sample_point(
                distance=distance,
                p=p,
                rounds=rounds,
                seed=args.seed + len(results),
                batch_shots=args.batch_shots,
                min_failures=args.min_failures,
                max_shots=args.max_shots,
            )
            results.append(result)
            print(
                f"d={distance:2d} p={p:.4g} shots={result.shots:8d} "
                f"failures={result.failures:5d} "
                f"P_L/round={result.logical_error_per_round:.3e}"
            )

    csv_path, figure_path = available_output_paths(args.output_dir)
    save_csv(results, csv_path)
    plot_results(results, figure_path)
    print(f"Saved {csv_path}")
    print(f"Saved {figure_path}")


if __name__ == "__main__":
    main()
