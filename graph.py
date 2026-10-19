"""
Implementation of Basic Graph Structure to make quantum walks on
"""

import numpy as np

# ---------------------------------------------
# Node

class Node: 
    """
    Node class to represent a node in the graph, it has its own id, and its
    neighbors ids.

    Attributes:
        id (int): The unique identifier of the node.
        neighbors (list): A list of neighboring nodes in insertion order.
    """

    __slots__ = ('id', 'neighbors') # reduce memory usage

    def __init__(self, id):
        self.id = id
        self.neighbors = []

    def add_neighbor(self, neighbor_id):
        self.neighbors.append(neighbor_id)

    @property
    def degree(self):
        """Number of neighbors of the node"""
        return len(self.neighbors)

    def __repr__(self):
        return f"Node({self.id})"


# ---------------------------------------------
# Edge

class Edge:
    """
    An edge to represent an undirected connection between two

    Attributes:
        node1 (Node): The first node of the edge.
        node2 (Node): The second node of the edge.
    """

    __slots__ = ('node1', 'node2') # reduce memory usage

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

    def endpoints(self):
        """Return the endpoints of the edge as a tuple"""
        return (self.node1, self.node2)

    def __repr__(self):
        return f"Edge({self.node1.id}, {self.node2.id})"

# ---------------------------------------------
# Graph

class Graph:
    """
    An undirected graph, with a lazily built arc representation.

    A self-loop contributes one neighbor and one arc, which is its own reverse.

    Attributes:
        arcs (list): A list of arcs (directed) in the graph.
        arcs_index (dict): A dictionary mapping directed node pairs to arc indices.
        flip (list): Where flip[i] is the index of the reverse of arc i.
        leaving_node (dict): A dictionary mapping node ids to outgoing arc indices.
        node_arcs (dict): An alias for leaving_node.
    """

    def __init__(self):
        self._nodes = {} # id -> Node
        self._edges = [] # edges
        self._dirty = True # flag to indicate if the graph has been modified
        self._coords = {} # id -> coordinates array
        
        self._arcs = []
        self._arcs_index = {}
        self._flip = []
        self._leaving_node = {}
        self._node_pos = {}

    # ---- Construction
    
    def add_node(self, id):
        """Add a node to the graph with the given id. Returns the node object."""
        if id not in self._nodes:
            self._nodes[id] = Node(id)
            self._dirty = True
        return self._nodes[id]

    def add_edge(self, id1, id2):
        """Add an undirected edge between two nodes with the given ids."""

        self.add_node(id1)
        self.add_node(id2)

        if id2 in self._nodes[id1].neighbors:
            return

        self._nodes[id1].add_neighbor(id2)
        if id1 != id2:
            self._nodes[id2].add_neighbor(id1)
        self._edges.append(Edge(self._nodes[id1], self._nodes[id2]))
        self._dirty = True

    def add_self_loops(self, nodes=None):
        """Add self-loops to the specified nodes. If no nodes are specified, add self-loops to all nodes."""
        
        if nodes is None:
            nodes = list(self._nodes.keys())
        
        for node_id in nodes:
            self.add_edge(node_id, node_id)

    # ---- Internal Methods

    def _ensure_arcs(self):
        """Ensure that the arcs representation is up-to-date."""
        if self._dirty: # we only rebuild if needed
            self._build_arcs() 

    def _build_arcs(self):
        """Build the arcs representation of the graph."""

        # TODO: maybe will be interesting to add changes pool instead of full rebuild
        self._arcs = []
        self._arcs_index = {}
        self._leaving_node = {nid: [] for nid in self._nodes}

        for node_id, node in self._nodes.items():
            for neighbor_id in node.neighbors:
                arc_index = len(self._arcs)

                self._arcs.append((node_id, neighbor_id))
                self._arcs_index[(node_id, neighbor_id)] = arc_index
                self._leaving_node[node_id].append(arc_index)

        self._flip = [self._arcs_index[(neighbor_id, node_id)]
                      for node_id, neighbor_id in self._arcs]

        self._node_pos = {node_id: idx for idx, node_id in enumerate(self._nodes)}

        self._dirty = False

    # ---- Spatial Coordinates
    
    def set_coords(self, coords):
        """Attach spatial coordinates to existing nodes from a dict {node: coord}."""
        converted = {}
        for node_id, coord in coords.items():
            if node_id not in self._nodes:
                raise ValueError(f"Node with id {node_id} does not exist in the graph.")

            converted[node_id] = np.atleast_1d(np.asarray(coord, dtype=float))

        self._coords.update(converted)

    @property
    def coords(self):
        """Return the coordinates of the nodes as a dict {node: coord}."""
        return self._coords

    # ---- Props

    @property
    def arcs(self):
        self._ensure_arcs()
        return self._arcs

    @property
    def arcs_index(self):
        self._ensure_arcs()
        return self._arcs_index

    @property
    def flip(self):
        self._ensure_arcs()
        return self._flip

    @property
    def leaving_node(self):
        self._ensure_arcs()
        return self._leaving_node

    @property
    def node_arcs(self):
        return self.leaving_node

    @property
    def nodes(self):
        """Return a list of all nodes ids in the graph."""
        return list(self._nodes.keys())

    @property
    def edges(self):
        """Return a list of all edges in the graph."""
        return list(self._edges)

    @property
    def num_nodes(self):
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    @property
    def num_arcs(self):
        """Return the number of arcs in the graph."""
        return len(self.arcs)

    # ---- Node Props

    def is_node(self, id):
        """Check if a node with the given id exists in the graph."""
        return True if id in self._nodes else False

    def node(self, id):
        """Return the node object with the given id."""
        if not self.is_node(id):
            raise ValueError(f"Node with id {id} does not exist in the graph.")
        
        node = self._nodes.get(id, None)

        return node

    def neighbors(self, id):
        """Return a list of neighbor ids for the node with the given id."""
        
        node = self.node(id)
        return list(node.neighbors)

    def degree(self, id):
        """Return the degree of the node with the given id."""
        
        node = self.node(id)
        return node.degree

    def node_position(self, id):
        """Return the index of the node in insertion order, as listed by nodes."""
        if not self.is_node(id):
            raise ValueError(f"Node with id {id} does not exist in the graph.")
        self._ensure_arcs()
        return self._node_pos[id]

    def node_coord(self, id):
        """Return the coordinates of the node with the given id."""
        
        if not self.is_node(id):
            raise ValueError(f"Node with id {id} does not exist in the graph.")
        
        return self._coords.get(id, None)

    # ----------------------------------------
    # Example Graphs

    @classmethod
    def line(cls, n):
        """Create a line graph with n nodes."""
        if n < 0:
            raise ValueError("A line graph cannot have a negative number of nodes.")
        g = cls()
        for i in range(n):
            g.add_node(i)
        for i in range(n - 1):
            g.add_edge(i, i + 1)

        return g

    @classmethod
    def cycle(cls, n):
        """Create a simple cycle graph with n nodes, where n is at least three."""
        if n < 3:
            raise ValueError("A simple cycle graph requires at least three nodes.")
        g = cls.line(n)
        g.add_edge(n - 1, 0)

        return g
