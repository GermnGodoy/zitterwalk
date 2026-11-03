# Node

`Node` represents a single vertex. It stores a hashable identifier (`id`) and an ordered list of neighbor identifiers (`neighbors`). Its `degree` counts these neighbors, including a self loop once. Import with `from graph import Node`.

Create nodes with [Graph.add_node()](graph.md#graph.Graph.add_node) and retrieve them with `Graph.node()`. Add connections through `Graph.add_edge()` to keep neighbor lists and directed arcs consistent. Node coordinates are stored by `Graph`.

---

::: graph.Node
