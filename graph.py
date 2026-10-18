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
    An undirected graph, with lazy built arc representation

    Attributes:
        arcs (list): A list of arcs (directed) in the graph.
        arc_index (dict): A dictionary mapping node ids to their corresponding arcs.
        flip (array): Where flip[i] is the index of the arc that is the reverse of arc i.
        leaving_node (dict): A dictionary mapping node ids to their corresponding leaving arcs.
    """

    def __init__(self):
        self._nodes = {} # id -> Node
        self._edges = [] # edges
        self._dirty = True # flag to indicate if the graph has been modified
        self._coords = {} # id -> coordinates array
        
        self.arcs = []
        self.arcs_index = {}
        self.flip = []
        self.leaving_node = {}

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

        if id1 == id2: # ciclic edge
            if id1 in self._nodes[id1].neighbors:
                return
            self._nodes[id1].add_neighbor(id1)
            self._dirty = True
            return

        self.add_node(id2)

        if id2 in self._nodes[id1].neighbors:
            return

        self._nodes[id1].add_neighbor(id2)
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
        self.arcs = []
        self.arcs_index = {}
        self.node_arcs = {nid: [] for nid in self._nodes}

        for node_id, node in self._nodes.items():
            for neighbor_id in node.neighbors:
                arc_index = len(self.arcs)

                self.arcs.append((node_id, neighbor_id))
                self.arcs_index[(node_id, neighbor_id)] = arc_index
                self.node_arcs[node_id].append(arc_index)

        self.flip = [arc_index[(neighbor_id, node_id)] for node_id, neighbor_id in self.arcs]

        self._node_pos = {node_id: idx for idx, node_id in enumerate(self.arcs)}

        self._dirty = False

    # ---- Spatial Coordinates
    
        def set_coords(self, coords):
            """Attach spatial coordinates to nodes from a dict {node: coord}.
    
            Args:
                coords: dict mapping node ids to coordinates.
            """
            for node_id, coord in coords.items():
                if node_id not in self._nodes:
                    raise Warning(f"Node with id {node_id} does not exist in the graph.")
                
                self._coords[node_id] = np.atleast_1d(np.asarray(coord, dtype=float))
    
        @property
        def coords(self):
            """Return the coordinates of the nodes as a dict {node: coord}."""
            self._ensure_arcs()
            return self._coords

    # ---- Props

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
        self._ensure_arcs()
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
        """Return the position of the node in the arcs list."""
        self._ensure_arcs()
        return self._node_pos[id]

    def node_coord(self, id):
        """Return the coordinates of the node with the given id."""
        
        if not self.is_node(id):
            raise ValueError(f"Node with id {id} does not exist in the graph.")
        
        return self._coords.get(id, None)

    