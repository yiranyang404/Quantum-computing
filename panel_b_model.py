"""Plot the data-error-only statistical estimate in Fowler et al. Eq. (12).

This is the estimate plotted in Fig. 4(b), not the circuit simulation in (a).
For odd d, P_L = d * comb(d, (d + 1) / 2) * (8p) ** ((d + 1) / 2).
"""

from math import comb
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DISTANCES = [3, 7, 11, 25, 55]
OUTPUT_DIR = Path("outputs")


def logical_error_rate(p: np.ndarray, distance: int) -> np.ndarray:
    error_dimension = (distance + 1) // 2
    return distance * comb(distance, error_dimension) * (8 * p) ** error_dimension


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    physical_error_rates = np.logspace(-4, -2, 300)

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    for distance in DISTANCES:
        logical_rates = logical_error_rate(physical_error_rates, distance)
        ax.loglog(physical_error_rates, logical_rates, label=f"d={distance}")

    ax.set_xlim(1e-4, 1e-2)
    ax.set_ylim(1e-15, 1)
    ax.set_xlabel(r"Per-step physical error rate $p$")
    ax.set_ylabel(r"Logical $X$ error rate per cycle $P_L$")
    ax.set_title("Fowler et al. Fig. 4(b): Eq. (12) estimate")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    output_path = OUTPUT_DIR / "fig4b_eq12_estimate.png"
    fig.savefig(output_path, dpi=220)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
