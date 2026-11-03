# Plotter

`plotter.py` provides Matplotlib views independent of the walk dynamics. Import with `from plotter import Plotter`. Supply node probabilities from `Walker.probabilities()`, in the same order as `graph.nodes`.

| Mode | Representation |
| --- | --- |
| `bars` | Vertical bars, ordered by node insertion. |
| `graph` | Graph edges with node color indicating probability. |
| `circular` | Radial bars above a common circle, ordered clockwise. |

Use the public Matplotlib `fig` and `ax` attributes to save figures and adjust labels.

---

::: plotter.Plotter
