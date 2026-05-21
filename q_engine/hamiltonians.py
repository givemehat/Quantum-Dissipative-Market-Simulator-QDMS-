import numpy as np
from qutip import sigmax, sigmaz, tensor, qeye, Qobj

def build_market_hamiltonian(num_assets: int, coupling_matrix: np.ndarray) -> Qobj:
    """
    Constructs the Market Hamiltonian based on a modified Transverse-field Ising Model.
    Each 'spin' represents an asset sector.
    
    H = - \sum_{<i,j>} J_{ij} Z_i Z_j - \sum_i h_i X_i
    
    Args:
        num_assets: Number of assets/sectors in the simulation.
        coupling_matrix: A 2D matrix (J_ij) representing correlations.
        
    Returns:
        The Hamiltonian matrix as a QuTiP Qobj.
    """
    H = 0
    # Construct operators for each asset
    # sigmax(), sigmaz(), qeye(2)
    # The transverse field (market volatility / external noise)
    h_field = 1.0  

    for i in range(num_assets):
        # Transverse field term: -h_i X_i
        op_list = [qeye(2)] * num_assets
        op_list[i] = sigmax()
        H -= h_field * tensor(op_list)

        for j in range(num_assets):
            if i != j and coupling_matrix[i, j] != 0:
                # Interaction term: -J_{ij} Z_i Z_j
                op_list_ij = [qeye(2)] * num_assets
                op_list_ij[i] = sigmaz()
                op_list_ij[j] = sigmaz()
                # Divide by 2 because the loop double counts pairs
                H -= (coupling_matrix[i, j] / 2.0) * tensor(op_list_ij)

    return H
