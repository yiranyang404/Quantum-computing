# Surface-code Fig. 4 reproduction

In this project, I reproduce selected features of Fig. 4 in Fowler et al.,
*Surface codes: Towards practical large-scale quantum computation*
(arXiv:1208.0928v2).

## What is included

1. In `panel_b_model.py`, I reproduce the qualitative curves in panel (b) from
   the paper's empirical Eq. (11).
2. In `reproduce_threshold.py`, I run a circuit-level Monte Carlo experiment
   with Stim and decode the detection events with PyMatching's minimum-weight
   perfect matching decoder.

## Important scientific limitation

I use the Monte Carlo script as a **modern reproduction of the threshold
phenomenon**, not as an exact historical reproduction of panel (a). My current
implementation uses Stim's rotated surface-code memory circuit, whereas the
paper used its own planar surface-code layout, an eight-step
syndrome-extraction schedule, and the five error channels listed immediately
before Fig. 4. I therefore do not claim that the crossing point produced here
exactly reproduces the paper's reported `p_th = 0.57%`.

As my next research step, I plan to encode the paper's exact circuit schedule
and noise model, then compare its detector error model and logical-error
counting convention with this modern baseline.

## Setup on Windows PowerShell

I use Python 3.11 or 3.12 and create the virtual environment with:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, I call the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the statistical model first

```powershell
python panel_b_model.py
```

Output: `outputs/fig4b_statistical_model.png`

## Run a fast smoke test

```powershell
python reproduce_threshold.py --distances 3 5 --error-rates 0.003 0.006 0.01 --min-failures 20 --max-shots 50000
```

## Run the initial experiment

```powershell
python reproduce_threshold.py
```

Outputs:

- `outputs/threshold_results.csv`
- `outputs/threshold_crossing.png`

At low error rates and high distances, I may observe zero failures before the
default shot limit. I treat such a point as statistically unresolved and omit
it from the log-scale plot instead of presenting it as a true zero error rate.

## How the experiment maps to Fig. 4

- I use the physical error probability `p` on the horizontal axis.
- I plot the estimated logical failure probability per syndrome round on the
  vertical axis.
- I draw one curve for each code distance `d`.
- I use a common crossing region to estimate the threshold.
- Below threshold, I expect increasing `d` to suppress the logical error rate.
