"""Matplotlib views of node probabilities, independent of the walk dynamics."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle
from matplotlib.text import Text


_BACKGROUND = "#FCFCFA"
_COLOR = "#0D8A75"
_TEXT = "#24332D"
_MUTED = "#6D7972"
_GRID = "#E5EBE7"
_FONTS = {font.name for font in font_manager.fontManager.ttflist}
_FONT = next((font for font in ("Inter", "Helvetica Neue", "Avenir Next", "DejaVu Sans")
              if font in _FONTS), "DejaVu Sans")

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
        vmax (float): The probability mapped to the darkest teal in graph mode.
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
        if node_size is None:
            node_size = 36 if count > 30 else 95
        indices = np.arange(count)
        ticks = np.unique(np.linspace(0, count - 1, min(count, 7), dtype=int))
        angles = 2 * np.pi * indices / count
        
        subplot_kw = {"projection": "polar"} if mode == "circular" else {}
        self.fig, self.ax = plt.subplots(
            figsize=(7.2, 7.2) if mode == "circular" else (10.5, 5.2),
            subplot_kw=subplot_kw, dpi=120, facecolor=_BACKGROUND,
        )
        self.ax.set_facecolor(_BACKGROUND)
        self.ax.set_axisbelow(True)
        self.ax.grid(False)
        self.ax.tick_params(axis="both", which="both", length=0, pad=9,
                            labelsize=10, colors=_MUTED)
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        if mode == "graph":
            # Draw edges and nodes, with loops for self-edges
            positions = self._positions(layout, angles)
            node_index = {node: i for i, node in enumerate(self.nodes)}
            segments = [positions[[node_index[edge.node1.id], node_index[edge.node2.id]]] for edge in graph.edges if edge.node1.id != edge.node2.id]
            
            self.ax.add_collection(LineCollection(segments, colors="#CFDAD4",
                                                   linewidths=1.1, zorder=1))
            loop_radius = (0.2 * np.median([np.linalg.norm(b - a) for a, b in segments]) if segments else 0.15)
            
            for edge in graph.edges:
                if edge.node1.id == edge.node2.id:
                    x, y = positions[node_index[edge.node1.id]]
                    self.ax.add_patch(Circle((x, y + loop_radius), loop_radius,
                                             fill=False, edgecolor="#CFDAD4", linewidth=1.1))
            
            cmap = LinearSegmentedColormap.from_list(
                "probability", ["#F1F7F3", "#A9D8C7", _COLOR, "#075B4C"],
            )
            
            self._points = self.ax.scatter(
                positions[:, 0], positions[:, 1], c=np.zeros(count),
                cmap=cmap, vmin=0, vmax=vmax, s=node_size,
                edgecolors="#91AAA0", linewidths=0.7, zorder=2,
            )
            
            label_ticks = ticks
            span = np.ptp(positions, axis=0)
            if count > 7 and np.linalg.norm(positions[0] - positions[-1]) < 0.2 * max(span):
                label_ticks = ticks[:-1]
            center = positions.mean(axis=0)
            for i in label_ticks:
                direction = positions[i] - center
                distance = np.linalg.norm(direction)
                offset = (16 * direction / distance if span[1] > 0 and distance > 0
                          else np.array([0, -16]))
                self.ax.annotate(str(self.nodes[i]), positions[i], xytext=offset,
                                 textcoords="offset points", ha="center", va="center",
                                 fontsize=9, color=_MUTED)
            
            self.ax.set_aspect("equal")
            
            bounds = self.ax.dataLim
            padding = 0.15 * max(bounds.width, bounds.height, 1)
            
            self.ax.set_xlim(bounds.x0 - padding, bounds.x1 + padding)
            self.ax.set_ylim(bounds.y0 - padding, bounds.y1 + padding)
            self.ax.set_axis_off()
            colorbar = self.fig.colorbar(self._points, ax=self.ax, shrink=colorbar_shrink,
                                         fraction=0.035, pad=0.06, aspect=28)
            colorbar.set_label("Probabilidad", size=10, color=_MUTED, labelpad=12)
            colorbar.set_ticks([0, vmax / 2, vmax])
            colorbar.ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
            colorbar.ax.tick_params(length=0, pad=7, labelsize=9, colors=_MUTED)
            colorbar.outline.set_visible(False)
        
        elif mode == "circular":
            # Draw bars in a circular layout
            inner_radius = 1.35 * ymax
            self._bars = self.ax.bar(angles, np.zeros(count), bottom=inner_radius,
                                     width=0.82 * 2 * np.pi / count, color=_COLOR,
                                     edgecolor="none", zorder=3)
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            
            self.ax.set_xticks([])
            self.ax.set_yticks([inner_radius + ymax], [f"{ymax:g}"])
            self.ax.set_rlabel_position(30)
            self.ax.grid(False)
            
            self.ax.set_ylim(0, inner_radius + 1.08 * ymax)
            circle = np.linspace(0, 2 * np.pi, 200)
            for level in (0, ymax / 2, ymax):
                self.ax.plot(circle, np.full_like(circle, inner_radius + level),
                             color="#C9D7CF" if level == 0 else _GRID,
                             linewidth=1 if level == 0 else 0.8, zorder=1)
            self.ax.text(0.5, 0.53, str(count), transform=self.ax.transAxes,
                         ha="center", va="center", fontsize=28, weight="medium", color=_TEXT)
            self.ax.text(0.5, 0.46, "nodo" if count == 1 else "nodos", transform=self.ax.transAxes,
                         ha="center", va="center", fontsize=11, color=_MUTED)
        
        else:
            # Draw bars in a linear layout
            self._bars = self.ax.bar(indices, np.zeros(count), width=0.78,
                                     color=_COLOR, edgecolor="none", zorder=3)
            self.ax.set_xticks(ticks, [str(self.nodes[i]) for i in ticks])
            
            self.ax.set_xlabel("Posición (nodo)", fontsize=11, color=_MUTED, labelpad=14)
            self.ax.set_ylabel("Probabilidad", fontsize=11, color=_MUTED, labelpad=14)
            self.ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
            self.ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
            self.ax.grid(axis="y", color=_GRID, linewidth=0.8)
            self.ax.axhline(0, color="#C9D7CF", linewidth=1, zorder=2)
            
            self.ax.set_xlim(-0.5, count - 0.5)
            self.ax.set_ylim(0, ymax)

        self.ax.set_autoscale_on(False)
        self._title_artist = self.ax.set_title(title, loc="left", fontsize=16,
                                               weight="medium", color=_TEXT, pad=28)
        self._time_artist = self.ax.annotate(
            "", xy=(1, 1), xycoords="axes fraction", xytext=(0, 28),
            textcoords="offset points", ha="right", va="baseline", annotation_clip=False,
            fontsize=10, color=_COLOR, weight="medium", visible=False,
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "#E8F3ED", "edgecolor": "none"},
        )
        for text in self.fig.findobj(Text):
            text.set_fontfamily(_FONT)
        self.fig.tight_layout(pad=1.8)

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
        
        self._title_artist.set_text(self._title)
        self._time_artist.set_visible(time is not None)
        self._time_artist.set_text("" if time is None else f"Paso {time}")
        return (*artists, self._title_artist, self._time_artist)

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
