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
        """
        self.graph = graph
        self.nodes = list(graph.nodes)
        self.coins = coins if isinstance(coins, dict) else {node: coins for node in self.nodes}

    def set_state(self, state):
        """
        Set the current state of the walker.
        """
        if not isinstance(state, np.ndarray):
            raise TypeError("state must be a numpy ndarray")
        if state.ndim != 1 or state.shape[0] != self.graph.num_arcs:
            raise ValueError(f"state must be a 1D array of length {self.graph.num_arcs}")
        if not np.issubdtype(state.dtype, np.complexfloating):
            raise TypeError("state must be a complex array")
        
        self.state = state
        self.initial_state = state.copy()
        self.time = 0

    def localize(self, node, amplitudes = None):
        """
        Localize the walker at a specific node with given amplitudes.
        If amplitudes are not provided, the walker is localized at the first arc of the node.
        """
        if node not in self.nodes:
            raise ValueError(f"Node {node} is not in the graph")
        
        arcs = self.graph.get_arcs(node)
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
        new_state = np.zeros_like(self.state)
        
        for node in self.nodes:
            arcs = self.graph.get_arcs(node)
            coin = self.coins[node]
            local_state = self.state[arcs]
            new_state[arcs] = coin.apply(local_state)
        self.state = new_state

    def _shift(self):
        """
        Return amplitudes reordered according to the flip of the graph.
        """
        return self.state[self.graph.flip]

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
        Perform steps time steps of the quantum walk.
        """
        all = []
        all.append(self.state.copy())

        for _ in range(steps):
            self.step()
            all.append(self.state.copy())

        return np.array(all)

    # ---- Utils

    def norm(self):
        """
        Return the norm of the current state of the walker.
        """
        return np.linalg.norm(self.state)

    def reset(self):
        """
        Reset the walker to its initial state and time step.
        """
        self.state = self.initial_state.copy()
        self.time = 0

    
