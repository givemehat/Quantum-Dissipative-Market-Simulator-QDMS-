import numpy as np
from qutip import basis, tensor, ket2dm, Qobj

def prepare_initial_market_state(num_assets: int, stable: bool = True) -> Qobj:
    """
    Prepares the initial quantum density matrix representing the market state.
    
    Args:
        num_assets: The number of assets/sectors.
        stable: If True, prepares a high-fidelity 'stable' state. 
                If False, prepares a highly entangled 'fragile' state.
                
    Returns:
        The initial density matrix ρ_0 as a QuTiP Qobj.
    """
    if stable:
        # Stable market: all sectors are in the ground state (aligned)
        state_list = [basis(2, 0) for _ in range(num_assets)]
        psi0 = tensor(state_list)
    else:
        # Fragile market: some sectors are in excited/disturbed states
        # For simplicity, we put the first asset in excited state |1> and rest in |0>
        # or we could make a superposition state.
        state_list = [basis(2, 1) if i % 2 == 0 else basis(2, 0) for i in range(num_assets)]
        psi0 = tensor(state_list)
        
    # Convert state vector (ket) to density matrix
    rho_0 = ket2dm(psi0)
    return rho_0
