# Zitterwalk

**Discrete-time quantum walks on graphs, with local potentials and clear visualizations.**

Developed as part of a Collaboration Grant with the Department of Theoretical Physics at the University of Valencia.

![A quantum walk shown as a probability distribution, a graph, and circular bars](images/line_walk.gif)

*A 61 nodes free quantum walk (bouncing at line ends)*

## Installation

Run the project directly from the repository root. The dependencies are NumPy, Matplotlib, and Pillow:

```sh
python3 -m pip install numpy matplotlib pillow
```

## Quick start

Create a line, initialize the walker at its center, and plot the distribution after 25 steps:

```python
import numpy as np

from coin import Coin
from graph import Graph
from plotter import Plotter
from walker import Walker

graph = Graph.line(61) #Graph
coins = {
    node: Coin.hadamard() if graph.degree(node) == 2 else Coin.identity(1)
    for node in graph.nodes
} # We define the coin for each node

walker = Walker(graph, coins)
walker.localize(30, np.array([1, 1j]) / np.sqrt(2)) # Starting position
walker.steps(25)

plotter = Plotter(graph, mode="bars", ymax=0.2, title="Quantum walk on a line")
plotter.update(walker.probabilities(), time=walker.time)
plotter.fig.savefig("walk.png", dpi=200, bbox_inches="tight")
```

The endpoints use one-dimensional identity coins, while interior nodes use the Hadamard coin.

## Visualization

`Plotter` reads node probabilities in `graph.nodes` order, and display the state independently of the walk dynamics.

| Mode | Representation |
| --- | --- |
| `bars` | Probability at each node as a vertical bar. |
| `graph` | Graph connectivity, with node color representing probability. |
| `circular` | Probability as bar height above a common circle (for circular walks). |

### Animation and export

We can also store multiple states and animate them as a *gif* for easier visualization:

```python
walker.reset()
history = [walker.probabilities()]

for _ in range(100):
    walker.step()
    history.append(walker.probabilities())

plotter = Plotter(graph, mode="bars", ymax=1)
animation = plotter.animate(history)
animation.save("walk.gif", writer="pillow", fps=10)
```
