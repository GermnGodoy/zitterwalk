"""Get some basic electric fields and potentials for Graph and Walker easier implementation."""

import numpy as np


def _vector(value, name, dimension=None):
    """Convert a value to a 1D numpy array of floats."""
    
    values = np.atleast_1d(np.asarray(value))
    if (values.ndim != 1 or values.size == 0 or values.dtype.kind not in "iuf"
            or not np.all(np.isfinite(values))):
        raise ValueError(f"{name} must contain finite real values")
    
    if dimension is not None and values.size != dimension:
        raise ValueError(f"{name} must have {dimension} component(s)")
    
    return values.astype(float)


def _coordinates(graph):
    """Return a dict {node: coord} with finite coordinates for all nodes in the graph."""
    coords = {}
    dimension = None
    
    for node in graph.nodes:
        coord = graph.node_coord(node)
        if coord is None:
            raise ValueError(f"Missing coordinates for node {node}; use graph.set_coords()")
        coords[node] = _vector(coord, f"Coordinates for node {node}", dimension)
        dimension = coords[node].size
    
    if not coords:
        raise ValueError("The graph must have at least one node")
    return coords


def uniform_field(graph, E0):
    """Return {node: E0}, this represents a uniform electric field in all the graph.
    
    Args:
        graph (Graph): The graph on which the walker moves.
        E0 (float or array-like): The uniform electric field value, can be a scalar
            or a vector with the same dimension as the graph coordinates.
    Returns:
        dict: {node: E0} A dictionary mapping each node to the uniform electric field value.
    """
    
    coords = _coordinates(graph)
    dimension = next(iter(coords.values())).size
    vector = _vector(E0, "E0", dimension)
    
    return {node: float(vector[0]) if dimension == 1 else vector.copy() for node in coords}


def random_field(graph, std=1.0, seed=None):
    """Sample static, independent Gaussian values eta[node] with mean zero and std.
    The resulting field is E[node] = eta[node]. The random number generator is seeded with the given seed.

    Args:
        graph (Graph): The graph on which the walker moves.
        std (float): Standard deviation of the Gaussian distribution.
        seed (int, optional): Seed for the random number generator. If None, the RNG is not seeded.
    Returns:
        dict: {node: eta[node]} A dictionary mapping each node to its sampled Gaussian value
    """
    coords = _coordinates(graph)
    dimension = next(iter(coords.values())).size
    
    std = float(_vector(std, "std", 1)[0])
    if std < 0:
        raise ValueError("std must be non-negative")
    
    values = np.random.default_rng(seed).normal(0, std, size=(len(coords), dimension))
    
    return {node: float(value[0]) if dimension == 1 else value for node, value in zip(coords, values)}


def noisy_field(graph, E0, std=1.0, seed=None):
    """Return a static field E[node] = E0 + eta[node], with Gaussian eta.
    
    Args:
        graph (Graph): The graph on which the walker moves.
        E0 (float or array-like): The uniform electric field value, can be a scalar
            or a vector with the same dimension as the graph coordinates.
        std (float): Standard deviation of the Gaussian noise.
        seed (int, optional): Seed for the random number generator. If None, the RNG is not seeded.
    Returns:
        dict: {node: E[node]} A dictionary mapping each node to its noisy electric field value.
    """
    uniform = uniform_field(graph, E0)
    noise = random_field(graph, std=std, seed=seed)
    return {node: uniform[node] + noise[node] for node in uniform}


def potential_from_field(graph, field, reference=None):
    """Return a potential dict {node: potential[node]} from a given field.
    The potential is calculated as the dot product of the field vector and the position vector relative to the reference node.
    If reference is None, the potential is calculated relative to the origin (0,0,...).

    Args:
        graph (Graph): The graph on which the walker moves.
        field (float, array-like, or dict): The electric field value(s). 
            If a scalar or array-like is provided, it is applied uniformly to all nodes.
            If a dict is provided, it should map nodes to their corresponding field values.
        reference (node, optional): The node to use as the reference point for potential calculation.
    Returns:
        dict: {node: potential[node]} A dictionary mapping each node to its calculated potential value
    """
    
    coords = _coordinates(graph)
    dimension = next(iter(coords.values())).size
    origin = np.zeros(dimension)
    
    if reference is not None:
        if reference not in coords: #reference node must be in the graph
            raise ValueError(f"Reference node {reference} is not in the graph")
        origin = coords[reference]
    
    if isinstance(field, dict):
        for node in field:
            if node not in coords:
                raise ValueError(f"Field node {node} is not in the graph")

    potential = {}
    for node, coord in coords.items():
        if isinstance(field, dict):
            value = field.get(node, np.zeros(dimension))
        elif callable(field):
            value = field(coord.copy())
        else:
            value = field
        
        vector = _vector(value, f"Field for node {node}", dimension)
        potential[node] = float(np.dot(vector, coord - origin))
        if not np.isfinite(potential[node]):
            raise ValueError(f"Potential for node {node} must be finite")
    
    return potential
