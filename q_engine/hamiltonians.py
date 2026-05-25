import numpy as np

from qutip import (
    Qobj,
    qeye,
    sigmax,
    sigmaz,
    tensor,
)

# =========================================================
# Market Hamiltonian Builder
# =========================================================

def build_market_hamiltonian(
    num_assets: int,
    coupling_matrix: np.ndarray,
) -> Qobj:
    """
    Modified Transverse-field Ising Model

    H = -Σ Jᵢⱼ ZᵢZⱼ - Σ hᵢXᵢ
    """

    H = 0
    h_field = 1.0

    for i in range(num_assets):

        # Transverse Field Term
        x_ops = [qeye(2)] * num_assets
        x_ops[i] = sigmax()

        H -= h_field * tensor(x_ops)

        # Interaction Terms
        for j in range(num_assets):

            if i == j or coupling_matrix[i, j] == 0:
                continue

            z_ops = [qeye(2)] * num_assets

            z_ops[i] = sigmaz()
            z_ops[j] = sigmaz()

            H -= (
                coupling_matrix[i, j] / 2
            ) * tensor(z_ops)

    return H