"""Save a GIF of a quantum walk on a finite line with fixed plot axes."""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coin import Coin
from graph import Graph
from walker import Walker


def main():
    num_nodes = 61
    num_steps = 100

    graph = Graph.line(num_nodes)
    hadamard = Coin.hadamard()
    coins = {node: hadamard if graph.degree(node) == 2 else Coin.identity(1)
             for node in graph.nodes}
    walker = Walker(graph, coins)
    walker.localize(num_nodes // 2, np.array([1, 1j]) / np.sqrt(2))

    probabilities = [walker.probabilities()]
    for _ in range(num_steps):
        walker.step()
        probabilities.append(walker.probabilities())

    fig, ax = plt.subplots(figsize=(10, 4.5))
    bars = ax.bar(graph.nodes, probabilities[0], width=0.9, color="steelblue")
    ax.set_xlabel("Posición (nodo)")
    ax.set_ylabel("Probabilidad")
    ax.set_xlim(-0.5, num_nodes - 0.5)
    ax.set_ylim(0, 0.4)
    ax.set_xticks(np.arange(0, num_nodes, 5))
    ax.set_autoscale_on(False)
    title = ax.set_title(f"Quantum walk en una línea de {num_nodes} nodos | T = 0")
    fig.tight_layout()

    def update(t):
        for bar, probability in zip(bars, probabilities[t]):
            bar.set_height(probability)
        title.set_text(f"Quantum walk en una línea de {num_nodes} nodos | T = {t}")

    animation = FuncAnimation(fig, update, frames=num_steps + 1, interval=100)
    output_dir = Path(__file__).resolve().parents[1] / "images"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / "line_walk.gif"
    animation.save(output, writer=PillowWriter(fps=10), dpi=100)
    plt.close(fig)
    print(f"GIF guardado en {output}")


if __name__ == "__main__":
    main()
