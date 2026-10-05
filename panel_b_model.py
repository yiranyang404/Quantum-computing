"""Reproduce the qualitative statistical-model curves in Fowler et al. Fig. 4(b).

This is not the full circuit-level simulation in panel (a). It uses Eq. (11):
    P_L ~= 0.03 * (p / p_th) ** ceil(d / 2)
for odd code distances d.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


P_THRESHOLD = 0.0057
DISTANCES = [3, 7, 11, 25, 55]
OUTPUT_DIR = Path("outputs")


def logical_error_rate(p: np.ndarray, distance: int) -> np.ndarray:
    error_dimension = (distance + 1) // 2
    return 0.03 * (p / P_THRESHOLD) ** error_dimension


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    physical_error_rates = np.logspace(-4, -2, 300)

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    for distance in DISTANCES:
        logical_rates = logical_error_rate(physical_error_rates, distance)
        ax.loglog(physical_error_rates, logical_rates, label=f"d={distance}")

    ax.axvline(P_THRESHOLD, color="black", linestyle="--", label=r"$p_{th}=0.57\%$")
    ax.set_xlim(1e-4, 1e-2)
    ax.set_ylim(1e-15, 1)
    ax.set_xlabel(r"Per-step physical error rate $p$")
    ax.set_ylabel(r"Logical $X$ error rate per cycle $P_L$")
    ax.set_title("Fowler et al. Fig. 4(b): Eq. (11) model")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    output_path = OUTPUT_DIR / "fig4b_statistical_model.png"
    fig.savefig(output_path, dpi=220)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()

