"""Contains all the logic of the walk itself"""

import numpy as np
from coin import Coin

class Walker:
    """
    Walker class to represent the quantum walker.

    Attributes:
        graph (Graph): The graph on which the walker moves.
        nodes (list): The list of nodes in the graph.
        coins (dict): A dictionary mapping nodes to their corresponding coin operators.
        state (np.ndarray complex): The current state of the walker (length of graph.num_arcs).
        initial_state (np.ndarray complex): The initial state of the walker (length of graph.num_arcs).
        time (int): The current time step of the walker.
        
        _flip (np.ndarray): Copy of the flip from the graph.
        _node_arcs (dict): Mapping of nodes to their corresponding arcs in the graph.
    """

    def __init__(self, graph, coins):
        """
        Initialize the Walker with a graph and coin operators.
        The graph topology must remain fixed during the simulation.
        """
        self.graph = graph
        self.nodes = list(graph.nodes)
        self.coins = coins.copy() if isinstance(coins, dict) else {node: coins for node in self.nodes}
        
        self._flip = np.array(graph.flip, dtype=int)
        self._node_arcs = {node: arcs.copy() for node, arcs in graph.leaving_node.items()}
        
        self._neighbors = {node: graph.neighbors(node) for node in self.nodes}
        self.state = None
        self.initial_state = None
        self.time = 0

        for node in self.nodes:
            degree = len(self._node_arcs[node])
            if degree == 0:
                continue
            if node not in self.coins:
                raise ValueError(f"Missing coin for node {node}")
            if not isinstance(self.coins[node], Coin):
                raise TypeError(f"Coin for node {node} must be a Coin instance")
            if self.coins[node].dimension != degree:
                raise ValueError(f"Coin for node {node} must have dimension {degree}")

    def _check_ready(self, require_state=True):
        """Check that the topology is unchanged and a state is available."""
        
        if (self.graph.nodes != self.nodes or
                any(self.graph.neighbors(node) != self._neighbors[node] for node in self.nodes)):
            raise RuntimeError("Graph topology has changed; create a new Walker")
        
        if require_state and self.state is None:
            raise RuntimeError("Initialize the state with set_state() or localize() first")

    def set_state(self, state):
        """
        Set the current state of the walker.
        """
        self._check_ready(require_state=False)
        if not isinstance(state, np.ndarray):
            raise TypeError("state must be a numpy ndarray")
        if state.ndim != 1 or state.shape[0] != self.graph.num_arcs:
            raise ValueError(f"state must be a 1D array of length {self.graph.num_arcs}")
        if not np.issubdtype(state.dtype, np.complexfloating):
            raise TypeError("state must be a complex array")
        if not np.all(np.isfinite(state)):
            raise ValueError("state must contain only finite values")
        if not np.isclose(np.linalg.norm(state), 1, rtol=0, atol=1e-10):
            raise ValueError("state must be normalized")
        
        self.state = state.copy()
        self.initial_state = state.copy()
        self.time = 0

    def localize(self, node, amplitudes = None):
        """
        Localize the walker at a specific node with given amplitudes.
        If amplitudes are not provided, use a uniform superposition of outgoing arcs.
        """
        self._check_ready(require_state=False)
        if node not in self.nodes:
            raise ValueError(f"Node {node} is not in the graph")
        
        arcs = self._node_arcs[node]
        if not arcs:
            raise ValueError(f"Node {node} has no outgoing arcs")
        if amplitudes is None: # Initialize uniform amplitudes
            amplitudes = np.ones(len(arcs), dtype=np.complex128) / np.sqrt(len(arcs))
        else:
            amplitudes = np.array(amplitudes, dtype=np.complex128)
            if amplitudes.ndim != 1 or amplitudes.shape[0] != len(arcs):
                raise ValueError(f"amplitudes must be a 1D array of length {len(arcs)}")
        
        state = np.zeros(self.graph.num_arcs, dtype=np.complex128)
        for i, arc in enumerate(arcs):
            state[arc] = amplitudes[i]
        
        self.set_state(state)

    # ---- Time Evolution

    def apply_coin(self):
        """
        Apply the coin operator to the current state of the walker.
        """
        self._check_ready()
        new_state = np.zeros_like(self.state)
        
        for node in self.nodes:
            arcs = self._node_arcs[node]
            if not arcs:
                continue
            coin = self.coins[node]
            local_state = self.state[arcs]
            new_state[arcs] = coin.apply(local_state)
        self.state = new_state

    def _shift(self):
        """
        Return amplitudes reordered according to the flip of the graph.
        """
        self._check_ready()
        return self.state[self._flip]

    def step(self):
        """
        Perform a single time step of the quantum walk.
        This involves applying the coin operator followed by the shift operation.
        """
        self.apply_coin()
        self.state = self._shift()
        self.time += 1

    def steps(self, steps):
        """
        Return the current arc state and the states after each requested step.
        """
        
        self._check_ready()
        
        if isinstance(steps, (bool, np.bool_)) or not isinstance(steps, (int, np.integer)):
            raise TypeError("steps must be an integer")
        if steps < 0:
            raise ValueError("steps must be non-negative")
        
        all = []
        all.append(self.state.copy())

        for _ in range(steps):
            self.step()
            all.append(self.state.copy())

        return np.array(all)

    # ---- Utils

    def probabilities(self):
        """Return node probabilities in the order of self.nodes, without changing the state."""
        self._check_ready()
        return np.array([np.sum(np.abs(self.state[self._node_arcs[node]]) ** 2)
                         for node in self.nodes])

    def norm(self):
        """
        Return the norm of the current state of the walker.
        """
        self._check_ready()
        return np.linalg.norm(self.state)

    def reset(self):
        """
        Reset the walker to its initial state and time step.
        """
        self._check_ready()
        self.state = self.initial_state.copy()
        self.time = 0

    
