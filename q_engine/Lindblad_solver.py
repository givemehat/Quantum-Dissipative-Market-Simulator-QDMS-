import numpy as np
from qutip import mesolve, sigmam, tensor, qeye, sigmaz, Qobj

def get_collapse_operators(num_assets: int, shock_intensity: float) -> list:
    """
    Creates collapse operators for the Lindblad Master Equation.
    A collapse operator usually represents a shock or dissipation in an asset.
    We use the relaxation operator sigmam() (sigma_minus) which forces 
    the state from |1> (excited/high value) to |0> (ground/crashed).
    """
    c_ops = []
    for i in range(num_assets):
        op_list = [qeye(2)] * num_assets
        op_list[i] = sigmam() # Energy dissipation (crash)
        # Multiply by sqrt of rate (shock_intensity)
        c_ops.append(np.sqrt(shock_intensity) * tensor(op_list))
    return c_ops

def solve_lindblad_master_equation(H: Qobj, initial_state: Qobj, collapse_operators: list, times: np.ndarray) -> list:
    """
    Solves the Lindblad Master Equation to simulate market crash/panic propagation.
    
    dρ/dt = -i[H, ρ] + \sum_k (L_k ρ L_k^† - 1/2 {L_k^† L_k, ρ})
    
    Args:
        H: The Market Hamiltonian (QuTiP Qobj).
        initial_state: Density matrix representing the initial market state (ρ_0) (QuTiP Qobj).
        collapse_operators: List of L_k operators representing shocks.
        times: Array of time steps for the simulation.
        
    Returns:
        A list of expectation values of sigma_z for each asset over time.
    """
    num_assets = len(H.dims[0])
    
    # We want to measure the "fidelity" or "magnetization" (sigma_z) of each asset over time
    e_ops = []
    for i in range(num_assets):
        op_list = [qeye(2)] * num_assets
        op_list[i] = sigmaz()
        e_ops.append(tensor(op_list))
        
    print(f"Running open quantum system simulation over {len(times)} time steps...")
    
    # mesolve solves the master equation
    result = mesolve(H, initial_state, times, collapse_operators, e_ops)
    
    # result.expect is a list of arrays. result.expect[i] is the expectation value of e_ops[i] over time
    return result.expect
