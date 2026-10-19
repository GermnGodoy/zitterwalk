"""Coin class for hte quantum walk"""

import numpy as np

class Coin:
    """
    Coin class to represent the coin operator in a quantum walk.

    Attributes:
        matrix (np.ndarray): The coin operator matrix.
    """

    def __init__(self, matrix):

        # Checks
        if not isinstance(matrix, np.ndarray):
            raise TypeError("matrix must be a numpy ndarray")

        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("matrix must be a square matrix")

        if not np.allclose(
            matrix.conj().T @ matrix,
            np.eye(matrix.shape[0]),
            rtol=0,
            atol=1e-10,
        ):
            raise ValueError("matrix must be unitary")

        # Complex type check and conversion
        if not np.issubdtype(matrix.dtype, np.complexfloating):
            matrix = matrix.astype(np.complex128)

        self.matrix = matrix

    # ---- Utils

    @property
    def dimension(self):
        """Return the dimension of the coin operator"""
        return self.matrix.shape[0]
    

    def apply(self, state):
        """Apply the coin operator to a given state"""
        return np.dot(self.matrix, state)

    def __repr__(self):
        return f"Coin(matrix={self.matrix})"

    # ---- Class Methods

    @classmethod
    def hadamard(cls):
        """Return the Hadamard coin operator"""
        def __repr__(self):
            return f"HadamardCoin(matrix={self.matrix})"
        
        return cls(np.array([[1, 1], [1, -1]]) / np.sqrt(2))

    @classmethod
    def identity(cls, dimension):
        """Return the identity coin operator of given dimension"""
        def __repr__(self):
            return f"IdentityCoin(matrix={self.matrix})"
        
        return cls(np.eye(dimension))

    @classmethod
    def grover(cls):
        """Return the Grover coin operator"""
        def __repr__(self):
            return f"GroverCoin(matrix={self.matrix})"
        
        return cls(np.array([[0, 1], [1, 0]]))
