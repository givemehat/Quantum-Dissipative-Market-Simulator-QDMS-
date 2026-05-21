import time
import numpy as np
import xgboost as xgb
import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import sys
import os

# Ensure q_engine can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from q_engine.hamiltonians import build_market_hamiltonian
from q_engine.state_prep import prepare_initial_market_state
from q_engine.Lindblad_solver import get_collapse_operators, solve_lindblad_master_equation

app = FastAPI(title="QDMS Processing Worker")

class WorkerConfig(BaseModel):
    num_assets: int
    shock_intensity: float
    time_steps: int

# We pre-train a dummy XGBoost model for demonstration
# In reality, this would be trained on historical quantum trajectory mappings
dummy_X = pd.DataFrame(np.random.rand(100, 5), columns=['open', 'high', 'low', 'close', 'volume'])
dummy_y = np.random.randint(0, 2, 100)
xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
xgb_model.fit(dummy_X, dummy_y)

@app.post("/process_simulation")
def run_simulation_task(config: WorkerConfig):
    # 1. Setup Quantum Engine Parameters
    # Define a random coupling matrix for assets
    J_matrix = np.random.rand(config.num_assets, config.num_assets)
    J_matrix = (J_matrix + J_matrix.T) / 2.0 # Make symmetric
    np.fill_diagonal(J_matrix, 0)
    
    # 2. Build Market Hamiltonian
    H = build_market_hamiltonian(config.num_assets, J_matrix)
    
    # 3. Prepare Initial State
    rho_0 = prepare_initial_market_state(config.num_assets, stable=True)
    
    # 4. Get Collapse Operators
    c_ops = get_collapse_operators(config.num_assets, config.shock_intensity)
    
    # 5. Run Lindblad Solver
    times = np.linspace(0, 10, config.time_steps)
    expectations = solve_lindblad_master_equation(H, rho_0, c_ops, times)
    
    # 6. Translate to OHLCV (Classical Bridge)
    ohlcv_data = process_quantum_trajectory(expectations, times)
    
    # 7. Hybrid ML Prediction
    regime = hybrid_ml_predict(ohlcv_data)
    
    return {
        "status": "completed",
        "regime_prediction": regime,
        "ohlcv_data": ohlcv_data
    }

def process_quantum_trajectory(expectations: list, times: np.ndarray):
    """
    Translates quantum expectation values into classical OHLCV data.
    `expectations` is a list of arrays (one array of length `times` per asset).
    """
    # We aggregate the expectations to form a "Market Index" fidelity score
    market_fidelity = np.mean(expectations, axis=0) # shape (time_steps,)
    
    ohlcv_data = []
    base_price = 100.0
    for i, t in enumerate(times):
        # Introduce some volatility
        noise = np.random.normal(0, 1)
        
        # Quantum expectation values [-1, 1]. We map this to a price multiplier.
        # If fidelity goes down, price drops.
        fidelity = market_fidelity[i]
        price = base_price * (1 + fidelity * 0.1) + noise
        
        ohlcv = {
            "time": float(t),
            "open": float(price - np.random.rand()),
            "high": float(price + np.random.rand() * 2),
            "low": float(price - np.random.rand() * 2),
            "close": float(price),
            "volume": float(10000 + fidelity * 5000 + np.random.randint(1000))
        }
        ohlcv_data.append(ohlcv)
    return ohlcv_data

def hybrid_ml_predict(ohlcv_data: list):
    """
    Passes the classical OHLCV data to XGBoost model to predict regime changes.
    """
    df = pd.DataFrame(ohlcv_data)
    # Use the last row for prediction
    features = df[['open', 'high', 'low', 'close', 'volume']].iloc[-1:]
    
    prediction = xgb_model.predict(features)[0]
    
    if prediction == 1:
        return "Elevated Crash Phase Predicted"
    else:
        return "Stable Bull Market"
