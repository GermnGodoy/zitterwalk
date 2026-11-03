# Fields

`fields.py` creates static field profiles and converts them to node potentials. Import functions directly from `fields`. Every node must have finite coordinates of a common dimension, set with `Graph.set_coords()`.

You can also get a potential (used for the evolution) with `potential_from_field()` that internally performs

$$
V_n=F_n\cdot(r_n-r_{\mathrm{ref}}).
$$

This is the implemented convention, including for a dictionary or callable profile. For a constant physical electric field $E=-\nabla V$, supply $F=-E$. For a spatially varying profile, the helper evaluates this product at each node, and does not integrate the field. See the [constant-field example](../examples/electric-field.md) for more information.

---

::: fields.uniform_field

::: fields.random_field

::: fields.noisy_field

::: fields.potential_from_field
