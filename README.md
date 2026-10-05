# Surface-code Fig. 4 study

In this project, I study Fig. 4 in Fowler et al., *Surface codes: Towards
practical large-scale quantum computation* (arXiv:1208.0928v2). I generate a
statistical estimate related to panel (b) and run a modern circuit-level
surface-code memory experiment related to the threshold behavior in panel (a).

## What the two scripts calculate

In `panel_b_model.py`, I plot the paper's data-error-only statistical estimate
from Eq. (12) for distances 3, 7, 11, 25, and 55:

```text
P_L = d * binomial(d, (d + 1) / 2) * (8p)^((d + 1) / 2)
```

Here `p` is the per-step physical error probability and `8p` approximates the
per-cycle data error probability. This estimate does not include all the
circuit faults used in panel (a). The older
`outputs/fig4b_statistical_model.png` uses the empirical Eq. (11), which fixes
`p_th = 0.57%` and therefore forces its curves to meet there. I retain that
older image for comparison; the current script produces
`outputs/fig4b_eq12_estimate.png`.

In `reproduce_threshold.py`, I sample Stim's `surface_code:rotated_memory_x`
circuit and decode with PyMatching. I use this as a modern baseline. Fowler et
al. instead used their planar layout, the eight-step syndrome-extraction
schedule in Fig. 1, and the five error channels described before Fig. 4. The
paper counts logical X errors per complete cycle. My CSV records the fraction
of memory experiments decoded incorrectly and a derived per-round estimate.
For `r` rounds, I calculate the latter as
`[1 - (1 - 2 * P_experiment)^(1/r)] / 2`. This conversion assumes independent,
identical logical flips per round and is not the paper's counting convention.
Consequently, I do not identify any crossing of my curves with the paper's
reported `p_th = 0.57%`.

## Set up and run on Windows PowerShell

I tested this project with Python 3.13.12, NumPy 2.5.3, Matplotlib 3.11.2,
Stim 1.16.0, and PyMatching 2.4.0. I pin these tested direct dependencies in
`requirements.txt`; changing versions can give different Monte Carlo samples.
From this project directory, I create the environment and install dependencies
with:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

I then generate the statistical estimate and run the small threshold scan:

```powershell
.\.venv\Scripts\python.exe panel_b_model.py
.\.venv\Scripts\python.exe reproduce_threshold.py --distances 3 5 --error-rates 0.003 0.006 0.01 --min-failures 20 --max-shots 50000
```

For a larger initial scan, I run:

```powershell
.\.venv\Scripts\python.exe reproduce_threshold.py
```

The Monte Carlo script uses base seed `12345` by default and assigns the next
seed to each `(distance, p)` point. I can change it with `--seed` and select an
output directory with `--output-dir`. The CSV records the seed used for each
point. A fixed seed makes repeated runs comparable with the same Stim version,
machine, batch size, and sampling calls; it does not guarantee identical
samples across different versions or machines.

New runs create `outputs/threshold_results.csv` and
`outputs/threshold_scan.png` if these names are free. Otherwise they use the
next available `_run2`, `_run3`, and so on suffix, preserving earlier data and
images. The original six-point run remains in
`outputs/threshold_results.csv` and `outputs/threshold_crossing.png`; the
second filename is historical and does not imply an observed crossing.

## Interpreting the threshold scan

The horizontal axis is the physical error probability `p` passed to Stim's
noise parameters. The vertical axis is the derived logical failure estimate
per syndrome round. Each distance `d` has its own curve. In the original
six-point CSV, the d=5 estimate is lower than d=3 at all three sampled error
rates (0.003, 0.006, and 0.01). I therefore have **not observed a threshold
crossing** in that small test. A credible threshold estimate needs more
distances, denser sampling near a crossing, and uncertainty estimates.

At low error rates and high distances, I may observe zero failures before the
shot limit. I treat such a point as statistically unresolved and omit it from
the log-scale plot instead of presenting it as a true zero error rate.

My next research step is to implement the paper's exact layout, eight-step
circuit, and noise channels, then align the detector model and per-cycle
logical X error count with its Fig. 4(a) simulation.
