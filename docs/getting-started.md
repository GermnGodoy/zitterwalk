# Getting Started

This example creates a finite line, starts a walker at its center, and plots the node probabilities after 25 steps.

## Install and run

Clone the repository, create a **virtual environment**, and install the runtime dependencies

```sh
git clone https://github.com/GermnGodoy/zitterwalk.git
cd zitterwalk

python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy matplotlib pillow
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. Run the code below from the repository root, either in a Python session or in a script saved there. The project currently uses top level modules rather than an installable package.

## Create, initialize, evolve and plot

```python
import matplotlib.pyplot as plt
import numpy as np

from coin import Coin
from graph import Graph
from plotter import Plotter
from walker import Walker

# Create a graph with nodes 0 through 60
graph = Graph.line(61)

# Match each coin's dimension to the node degree
coins = {
    node: Coin.hadamard() if graph.degree(node) == 2 else Coin.identity(1) for node in graph.nodes
}

# Initialize a normalized state on the center node's two outgoing arcs
walker = Walker(graph, coins)
walker.localize(30, np.array([1, 1j]) / np.sqrt(2))

# Evolve by 25 discrete steps
walker.steps(25)

# Plot probabilities in graph.nodes order
plotter = Plotter(graph, mode="bars", ymax=0.2, title="Line walk: 25 steps")
plotter.update(walker.probabilities())

plotter.ax.set(xlabel="Node", ylabel="Probability")
plotter.fig.savefig("walk.png", dpi=120, bbox_inches="tight")
plt.show()
```

![Node probabilities after 25 steps on a 61-node line, showing two spreading peaks.](../assets/line.png)

`Graph.line(61)` has reflecting endpoints, each endpoint has one outgoing arc and uses `Coin.identity(1)`. Interior nodes use `Coin.hadamard()`. Finish building the graph before constructing the walker.

`localize()` sets both the current state and the initial state used by `reset()`. Its optional amplitudes follow the node's neighbor insertion order and must be normalized. Omitting them creates a uniform superposition of outgoing arcs.

`steps(25)` advances the walker and returns 26 states, including the state before the first step. `probabilities()` returns one probability per node, in `graph.nodes` order, these sum to one up to floating-point error. `walker.time` counts steps, with physical time given by `walker.time * walker.dt`.

The figure opens in Matplotlib and is also saved as `walk.png`. For a circular view or a static potential, continue to the [circle](examples/circle.md) and [electric-field](examples/electric-field.md) examples.
