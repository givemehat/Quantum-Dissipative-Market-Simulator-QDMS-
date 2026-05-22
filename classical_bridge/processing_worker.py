import os
import sys
import numpy as np
import pandas as pd
import xgboost as xgb

from fastapi import FastAPI
from pydantic import BaseModel

# Enable q_engine imports
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from q_engine.hamiltonians import (
    build_market_hamiltonian,
)

from q_engine.state_prep import (
    prepare_initial_market_state,
)

from q_engine.Lindblad_solver import (
    get_collapse_operators,
    solve_lindblad_master_equation,
)

app = FastAPI(
    title="QDMS Processing Worker"
)

# =========================================================
# Request Model
# =========================================================

class WorkerConfig(BaseModel):
    num_assets: int
    shock_intensity: float
    time_steps: int


# =========================================================
# Dummy XGBoost Model
# =========================================================

dummy_X = pd.DataFrame(
    np.random.rand(100, 5),
    columns=[
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
)

dummy_y = np.random.randint(
    0,
    2,
    100,
)

xgb_model = xgb.XGBClassifier(
    use_label_encoder=False,
    eval_metric="logloss",
)

xgb_model.fit(dummy_X, dummy_y)


# =========================================================
# Simulation Endpoint
# =========================================================

@app.post("/process_simulation")
def run_simulation_task(
    config: WorkerConfig
):
    # Coupling Matrix
    J_matrix = np.random.rand(
        config.num_assets,
        config.num_assets,
    )

    J_matrix = (
        J_matrix + J_matrix.T
    ) / 2

    np.fill_diagonal(
        J_matrix,
        0,
    )

    # Quantum Engine
    H = build_market_hamiltonian(
        config.num_assets,
        J_matrix,
    )

    rho_0 = prepare_initial_market_state(
        config.num_assets,
        stable=True,
    )

    c_ops = get_collapse_operators(
        config.num_assets,
        config.shock_intensity,
    )

    # Lindblad Solver
    times = np.linspace(
        0,
        10,
        config.time_steps,
    )

    expectations = (
        solve_lindblad_master_equation(
            H,
            rho_0,
            c_ops,
            times,
        )
    )

    # Classical Bridge
    ohlcv_data = process_quantum_trajectory(
        expectations,
        times,
    )

    # Hybrid ML Prediction
    regime = hybrid_ml_predict(
        ohlcv_data
    )

    return {
        "status": "completed",
        "regime_prediction": regime,
        "ohlcv_data": ohlcv_data,
    }


# =========================================================
# Quantum → OHLCV Conversion
# =========================================================

def process_quantum_trajectory(
    expectations: list,
    times: np.ndarray,
):
    market_fidelity = np.mean(
        expectations,
        axis=0,
    )

    base_price = 100.0
    ohlcv_data = []

    for index, current_time in enumerate(times):

        fidelity = market_fidelity[index]

        noise = np.random.normal(
            0,
            1,
        )

        price = (
            base_price
            * (1 + fidelity * 0.1)
            + noise
        )

        ohlcv_data.append({
            "time": float(current_time),
            "open": float(
                price - np.random.rand()
            ),
            "high": float(
                price + np.random.rand() * 2
            ),
            "low": float(
                price - np.random.rand() * 2
            ),
            "close": float(price),
            "volume": float(
                10000
                + fidelity * 5000
                + np.random.randint(1000)
            ),
        })

    return ohlcv_data


# =========================================================
# Hybrid ML Prediction
# =========================================================

def hybrid_ml_predict(
    ohlcv_data: list
):
    df = pd.DataFrame(ohlcv_data)

    features = df[
        [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ].iloc[-1:]

    prediction = xgb_model.predict(
        features
    )[0]

    return (
        "Elevated Crash Phase Predicted"
        if prediction == 1
        else "Stable Bull Market"
    )