# Graph

`Graph` manages the walk's topology, it creates and stores [nodes](node.md) and [edges](edge.md), holds optional node coordinates, and builds the directed arcs used by `Walker`. Each ordinary edge produces two opposite arcs, while a self-loop produces one. Import with `from graph import Graph`.

Build the topology through `Graph.add_node()` and `Graph.add_edge()` before constructing a walker. Node and neighbor insertion order determine arc order. Coordinates are optional for a free walk, but field helpers require them for every node.

---

::: graph.Graph
