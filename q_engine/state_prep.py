import numpy as np

from qutip import (
    Qobj,
    basis,
    ket2dm,
    tensor,
)

# =========================================================
# Initial Market State Preparation
# =========================================================

def prepare_initial_market_state(
    num_assets: int,
    stable: bool = True,
) -> Qobj:
    """
    Prepares the initial quantum market state.
    """

    if stable:
        # Ground State
        states = [
            basis(2, 0)
            for _ in range(num_assets)
        ]

    else:
        # Disturbed / Fragile State
        states = [
            basis(2, 1)
            if index % 2 == 0
            else basis(2, 0)
            for index in range(num_assets)
        ]

    psi0 = tensor(states)

    return ket2dm(psi0)