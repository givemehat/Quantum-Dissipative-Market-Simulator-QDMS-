from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="QDMS Classical Bridge", description="Gateway for the Quantum-Dissipative Market Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKER_URL = os.getenv("WORKER_URL", "http://localhost:8001")

class SimulationConfig(BaseModel):
    num_assets: int = 4
    shock_intensity: float = 0.5
    time_steps: int = 50

@app.post("/simulate")
async def run_simulation(config: SimulationConfig):
    """
    Triggers a new market collapse simulation run using the quantum engine 
    via the processing worker.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{WORKER_URL}/process_simulation", json=config.model_dump())
            response.raise_for_status()
            result = response.json()
            return {
                "status": "Simulation completed",
                "config": config.model_dump(),
                "result": result
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Worker request failed: {str(e)}")

@app.get("/status")
async def get_status():
    """
    Checks if the gateway is alive.
    """
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
