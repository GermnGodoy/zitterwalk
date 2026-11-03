# Walker

`walker.py` evolves a complex state on the graph's directed arcs. Import with `from walker import Walker`.

Each step applies the coin, reverses the arcs (the flip-flop shift), then multiplies each node's outgoing amplitudes by its electrostatic phase. In units with $\hbar=1$,

$$
\ket{\psi_{t+1}}=\hat{D} \hat{S} \hat{C}\,\ket{\psi_t}, \qquad
D_{aa}=\exp\!\left(-i q V_{\operatorname{}(a)}\,\Delta t\right)
$$

The graph topology, charge, step duration and potential phase are fixed for a simulation. Create a new walker to change them. Initialize with `localize()` or `set_state()` before evolving or reading probabilities.

---

::: walker.Walker
