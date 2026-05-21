# Quantum-Dissipative Market Simulator (QDMS)

**Simulating Financial Liquidity Cascades and Shock Propagation via Open Quantum System Dynamics**

## 💡 The Big Idea

Traditional financial simulators treat markets like a collection of classical particles moving along stochastic paths (e.g., Geometric Brownian Motion). This completely breaks down during systemic financial crises, black swan events, or flash crashes because classical math fails to capture the sudden, explosive, non-linear entanglement of risk and liquidity dissipation across multiple asset classes.

**The Quantum Paradigm:** This project models the stock market as an **Open Quantum System**.
- **Assets and Traders** are modeled as a lattice of interacting quantum states (sub-systems).
- **Market Liquidity and Sentiments** act as the surrounding external reservoir/bath.
- **Flash Crashes and Panic Selling** are simulated as *Quantum Dissipation and Decoherence*—where energy (capital) rapidly leaks out of the system into the bath, causing a structural collapse of system fidelity (market stability).

## 🛠️ Core Architecture & Components

The repository is built to scale by decoupling the quantum mathematical engine from the real-time visualization layer.

```text
Quantum-Dissipative-Market-Simulator/
├── q_engine/                     # Quantum Simulation Core (Qiskit + QuTiP)
│   ├── hamiltonians.py           # Defines Market Interaction Matrices (Ising/Hopfield mappings)
│   ├── Lindblad_solver.py        # Solves Master Equations for capital dissipation
│   └── state_prep.py             # Sparse state preparation subroutines
├── classical_bridge/             # Real-time Telemetry & Data Aggregation
│   ├── app.py                    # FastAPI Gateway
│   └── processing_worker.py      # Translates quantum density matrices into classical OHLCV data
├── dashboard/                    # React 19 Frontend
│   └── src/                      # Real-time state-fidelity charts & cascading stress heatmaps
├── docker-compose.yml            # Spins up the simulation broker and dashboard
└── README.md                     # Mathematical setup and setup instructions
```

## 🔬 How the Simulation Works (The Technical Blueprint)

### 1. The Market Hamiltonian ($H$)

We map market dependency structures using a modified quantum spin-lattice model (like the Transverse-field Ising Model). Each node represents an asset sector or an institutional block. The interaction strength $J_{ij}$ represents the correlation between assets.

### 2. The Dissipation Engine (The Lindblad Equation)

To simulate a market crash or panic propagation, we use the Lindblad Master Equation to introduce non-unitary, open-system time evolution:

$$
\frac{d\rho}{dt} = -i[H, \rho] + \sum_k \left( L_k \rho L_k^\dagger - \frac{1}{2} \{L_k^\dagger L_k, \rho\} \right)
$$

Where:
- $\rho$ is the density matrix of the market state.
- $L_k$ represents the Collapse Operators (e.g., sudden margin calls, algorithmic sell-offs, or central bank interest rate shocks).

By adjusting the coupling strength to the environment, you can simulate how a shock in one sector (like real estate) rapidly decoheres and collapses the fidelity of the entire market portfolio.

### 3. The Hybrid Classical-AI Predictor

The quantum engine generates a probabilistic matrix of state paths. A classical machine learning model (like an LSTM or XGBoost) reads these quantum trajectory outputs to predict real-world regime changes (shifting from a *Stable Bull Market* to an *Elevated/Critical Crash Phase*).

## 🚀 Setup & Execution

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 20+

### Quick Start
To spin up the entire simulation cluster:
```bash
docker-compose up --build
```
This will start the FastAPI gateway, the processing worker, and the React dashboard visualization.

*Built for the 2026 era of hybrid quantum-classical supercomputing applied to enterprise risk.*
