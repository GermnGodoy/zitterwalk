"""Matplotlib views of node probabilities, independent of the walk dynamics."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle

# ---------------------------------------------
# Plotter
# TODO: Think if it is better to have a separate class for each mode, and new plot types
class Plotter:
    """Draw or animate probabilities for a Graph.

    Attributes:
        graph (Graph): The graph to plot.
        mode (str): The plotting mode, one of ``bars``, ``graph``, or ``circular``.
        layout (str): The graph layout, one of ``auto``, ``line``, or ``circle``.
        ymax (float): The maximum y-value for bar plots.
        vmax (float): The probability mapped to full turquoise in graph mode.
        node_size (float or None): Node marker area in points squared; None uses an automatic size.
        colorbar_shrink (float): Size of the colorbar relative to the graph axes.
        title (str): The title of the plot.
    """

    def __init__(self, graph, mode="bars", *, layout="auto", ymax=1.0, title="Quantum walk",
                 vmax=1.0, node_size=None, colorbar_shrink=1.0):
        
        if mode not in ("bars", "graph", "circular"):
            raise ValueError("mode must be 'bars', 'graph', or 'circular'")
        if layout not in ("auto", "line", "circle"):
            raise ValueError("layout must be 'auto', 'line', or 'circle'")
        if not graph.nodes:
            raise ValueError("Cannot plot an empty graph")
        if not np.isfinite(ymax) or ymax <= 0:
            raise ValueError("ymax must be finite and positive")
        if not np.isfinite(vmax) or vmax <= 0:
            raise ValueError("vmax must be finite and positive")
        if node_size is not None and (not np.isfinite(node_size) or node_size <= 0):
            raise ValueError("node_size must be finite and positive")
        if not np.isfinite(colorbar_shrink) or colorbar_shrink <= 0:
            raise ValueError("colorbar_shrink must be finite and positive")

        self.graph = graph
        self.nodes = graph.nodes
        self.mode = mode
        self._title = title
        
        count = len(self.nodes)
        color = "turquoise"
        if node_size is None:
            node_size = 30 if count > 30 else 80
        indices = np.arange(count)
        ticks = indices[::max(1, int(np.ceil(count / 20)))]
        angles = 2 * np.pi * indices / count
        
        subplot_kw = {"projection": "polar"} if mode == "circular" else {}
        self.fig, self.ax = plt.subplots(
            figsize=(7, 7) if mode == "circular" else (10, 4.5),
            subplot_kw=subplot_kw,
        )

        if mode == "graph":
            # Draw edges and nodes, with loops for self-edges
            positions = self._positions(layout, angles)
            node_index = {node: i for i, node in enumerate(self.nodes)}
            segments = [positions[[node_index[edge.node1.id], node_index[edge.node2.id]]] for edge in graph.edges if edge.node1.id != edge.node2.id]
            
            self.ax.add_collection(LineCollection(segments, colors="0.65", zorder=1))
            loop_radius = (0.2 * np.median([np.linalg.norm(b - a) for a, b in segments]) if segments else 0.15)
            
            for edge in graph.edges:
                if edge.node1.id == edge.node2.id:
                    x, y = positions[node_index[edge.node1.id]]
                    self.ax.add_patch(Circle((x, y + loop_radius), loop_radius,
                                             fill=False, edgecolor="0.65"))
            
            cmap = LinearSegmentedColormap.from_list("probability", ["white", color])
            
            self._points = self.ax.scatter(
                positions[:, 0], positions[:, 1], c=np.zeros(count),
                cmap=cmap, vmin=0, vmax=vmax, s=node_size,
                edgecolors="0.3", zorder=2,
            )
            
            for i in ticks:
                self.ax.annotate(str(self.nodes[i]), positions[i], xytext=(0, -14),
                                 textcoords="offset points", ha="center", fontsize=8)
            
            self.ax.set_aspect("equal")
            
            bounds = self.ax.dataLim
            padding = 0.15 * max(bounds.width, bounds.height, 1)
            
            self.ax.set_xlim(bounds.x0 - padding, bounds.x1 + padding)
            self.ax.set_ylim(bounds.y0 - padding, bounds.y1 + padding)
            self.ax.set_axis_off()
            self.fig.colorbar(self._points, ax=self.ax, label="Probabilidad",
                              shrink=colorbar_shrink)
        
        elif mode == "circular":
            # Draw bars in a circular layout
            self._bars = self.ax.bar(angles, np.zeros(count), bottom=1,
                                     width=0.9 * 2 * np.pi / count, color=color)
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            
            self.ax.set_xticks(angles[ticks], [str(self.nodes[i]) for i in ticks])
            levels = np.linspace(0, ymax, 5)
            self.ax.set_yticks(1 + levels, [f"{p:g}" for p in levels])
            
            self.ax.set_ylim(0, 1 + ymax)
            circle = np.linspace(0, 2 * np.pi, 200)
            self.ax.plot(circle, np.ones_like(circle), color="0.4", linewidth=1)
            self.ax.set_ylabel("Probabilidad", labelpad=35)
        
        else:
            # Draw bars in a linear layout
            self._bars = self.ax.bar(indices, np.zeros(count), width=0.9,
                                     color=color)
            self.ax.set_xticks(ticks, [str(self.nodes[i]) for i in ticks])
            
            self.ax.set_xlabel("Posición (nodo)")
            self.ax.set_ylabel("Probabilidad")
            
            self.ax.set_xlim(-0.5, count - 0.5)
            self.ax.set_ylim(0, ymax)

        self.ax.set_autoscale_on(False)
        self._title_artist = self.ax.set_title(title)
        self.fig.tight_layout()

    def _positions(self, layout, angles):
        """Return the positions of nodes for plotting, based on the layout"""

        if layout == "auto":
            coords = [self.graph.node_coord(node) for node in self.nodes]
            
            if all(coord is not None for coord in coords):
                positions = []
                for coord in coords:
                    
                    if coord.ndim != 1 or coord.size not in (1, 2) or not np.all(np.isfinite(coord)):
                        raise ValueError("Graph coordinates must be finite 1D or 2D vectors")
                    positions.append([coord[0], coord[1] if coord.size == 2 else 0])
                
                return np.asarray(positions)
            
            edges = {frozenset((edge.node1.id, edge.node2.id)) for edge in self.graph.edges if edge.node1.id != edge.node2.id}
            line_edges = {frozenset(pair) for pair in zip(self.nodes, self.nodes[1:])} # frozenset to ignore order
            
            layout = "line" if edges == line_edges else "circle"
        
        if layout == "line":
            return np.column_stack((np.arange(len(self.nodes)), np.zeros(len(self.nodes))))
        
        return np.column_stack((np.sin(angles), np.cos(angles)))

    def _probabilities(self, probabilities):
        """Validate and convert probabilities to a numpy array"""

        values = np.asarray(probabilities, dtype=float)
        if (not np.all(np.isfinite(values)) or
                np.any(values < -1e-10) or np.any(values > 1 + 1e-10)):
            raise ValueError("Probabilities must be finite values between 0 and 1")
        
        return np.clip(values, 0, 1)

    def update(self, probabilities, time=None):
        """Update existing artists, and checks that probabilities are valid"""

        values = self._probabilities(probabilities)
        
        if values.shape != (len(self.nodes),):
            raise ValueError(f"Expected one probability per node ({len(self.nodes)})")
        
        if self.mode == "graph":
            self._points.set_array(values)
            artists = (self._points,)
        
        else:
            for bar, value in zip(self._bars, values):
                bar.set_height(value)
            artists = tuple(self._bars)
        
        self._title_artist.set_text(self._title if time is None else f"{self._title} | T = {time}")
        return (*artists, self._title_artist)

    def animate(self, probabilities, *, interval=100, start_time=0):
        """Return a FuncAnimation from a history shaped (frames, nodes).

        If the animation is alive, it will be shown. Can be saved to a file using save() method
        """
        history = self._probabilities(probabilities)
        if history.ndim != 2 or history.shape[0] == 0 or history.shape[1] != len(self.nodes):
            raise ValueError("Expected a non-empty probability history shaped (frames, nodes)")
        
        self.update(history[0], time=start_time)
        
        return FuncAnimation(
            self.fig, lambda t: self.update(history[t], time=start_time + t),
            frames=len(history), interval=interval,
        )
