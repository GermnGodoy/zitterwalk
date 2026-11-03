# zitterwalk.

zitterwalk is a Python library for simulating discrete-time quantum walks on graphs. Define a graph and its coin operators, evolve a walker, and inspect the probability at each node. Static local potentials can be included in the evolution.

## Installation

Clone the repository and install the required dependencies

```sh
git clone https://github.com/GermnGodoy/zitterwalk.git
cd zitterwalk
python3 -m pip install numpy matplotlib pillow
```

Run Python from the repository root, as the modules are imported directly from the checkout. See [Getting Started](getting-started.md) for a virtual environment setup.

## Quick Start

```python
from coin import Coin
from graph import Graph
from walker import Walker

graph = Graph.line(41)

coins = {n: Coin.hadamard() if graph.degree(n) == 2 else Coin.identity(1) for n in graph.nodes}

walker = Walker(graph, coins)
walker.localize(20)
walker.steps(15)

print(walker.probabilities())
```

The coin dimension must match the number of outgoing arcs at each node, in this case, two in the interior and one at each endpoint.

## Explore

- [Examples](examples/line.md): walks on a line, on a circle, and with a constant electric field.
- [API Reference](api/coin.md): signatures, parameters and methods.
- [GitHub repository](https://github.com/GermnGodoy/zitterwalk): source code and existing scripts.

Developed as part of a Collaboration Grant with the Department of Theoretical Physics at the University of Valencia.
