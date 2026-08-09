from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import httpx
import os
import time

app = FastAPI(
    title="QDMS Classical Bridge",
    description="Gateway for Quantum-Dissipative Market Simulator",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKER_URL = os.getenv("WORKER_URL", "http://localhost:8001")


class SimulationConfig(BaseModel):
    num_assets: int = Field(default=4, gt=0, le=100, description="Number of assets")

    shock_intensity: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Shock intensity"
    )

    time_steps: int = Field(
        default=50, gt=1, le=10000, description="Simulation time steps"
    )


# =========================================================
# 🛡️ GLOBAL ERROR HANDLING MIDDLEWARES
# =========================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic validation failures globally and returns
    structured JSON layout instead of collapsing raw streams.
    """
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_type": "ValidationError",
            "message": "The request payload parameters are invalid or out of bounds.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def universal_generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all safety wrapper for unexpected internal architecture faults.
    """
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_type": "InternalServerError",
            "message": "An unhandled runtime error occurred inside the gateway layer.",
            "details": str(exc),
        },
    )


# =========================================================
# 🔍 HEALTH CHECK ENDPOINT (#4)
# =========================================================


@app.get("/health")
async def health_check():
    """
    Monitors overall service accessibility by running live diagnostic pings
    downstream to the execution worker nodes.
    """
    worker_status = "disconnected"
    simulation_engine = "stopped"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{WORKER_URL}/status")
            if response.status_code == 200:
                worker_data = response.json()
                # If worker returns alive status, map parameters safely
                if worker_data.get("status") == "alive":
                    worker_status = "connected"
                    simulation_engine = "running"
    except (httpx.HTTPError, Exception):
        # Gracefully fall back to disconnected metric instead of breaking endpoint structure
        pass

    return {
        "status": "healthy",
        "simulation_engine": simulation_engine,
        "worker": worker_status,
        "timestamp": float(time.time()),
    }


# =========================================================
# Simulation Endpoint
# =========================================================


@app.post("/simulate")
async def run_simulation(config: SimulationConfig):
    try:
        async with httpx.AsyncClient(timeout=60) as client:

            response = await client.post(
                f"{WORKER_URL}/process_simulation", json=config.model_dump()
            )

            response.raise_for_status()

        # 🛡️ Safeguard: Safely extract parsed JSON from the worker
        worker_result = response.json()

        return {
            "status": "Simulation completed",
            "config": config.model_dump(),
            "result": worker_result,
        }

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail={
                "status": "error",
                "message": f"Execution worker rejected simulation schema parameters.",
                "worker_error": error.response.text,
            },
        )
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": f"Unable to reach the core background execution cluster.",
                "details": str(error),
            },
        )


@app.get("/status")
async def get_status():
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
