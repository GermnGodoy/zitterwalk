# Edge

`Edge` represents an undirected connection between two [nodes](node.md). It stores the endpoint objects as `node1` and `node2`, and both can refer to the same node for a self-loop. Import with `from graph import Edge`.

Create connections with [Graph.add_edge()](graph.md#graph.Graph.add_edge) and retrieve their `Edge` objects through `Graph.edges`. Constructing `Edge` directly only stores its endpoints, it does not connect the nodes or register the edge in a graph.

---

::: graph.Edge
