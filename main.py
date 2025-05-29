import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd 

# Import our core logic functions
from tokenomics_simulator import run_simulation
from risk_analysis import get_llm_analysis

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Tokenomics Lab API",
    description="API for simulating tokenomics and providing AI-powered risk analysis.",
    version="0.1.0"
)

# --- CORS Configuration ---
origins = ["*"] # Be more restrictive in production environments

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for Simulation Parameters ---
class SimulationParameters(BaseModel):
    total_supply: int
    initial_circulating_supply: int
    simulation_duration_months: int
    team_allocation_pct: float
    private_sale_pct: float
    public_sale_pct: float
    treasury_pct: float
    community_rewards_pct: float
    liquidity_mining_pct: float
    team_cliff_months: int
    team_vesting_linear_months: int
    private_sale_cliff_months: int
    private_sale_vesting_linear_months: int
    monthly_emission_tokens: int
    transaction_fee_burn_pct: float
    monthly_simulated_transactions: int

# --- Pydantic Model for LLM Analysis Request ---
class LLMAnalysisRequest(BaseModel):
    simulation_data: list[dict]

# --- Pydantic Model for Report Generation Request (Placeholder) ---
class ReportRequest(BaseModel):
    simulation_params: dict
    simulation_results: list[dict]
    llm_analysis_text: str

# --- API Endpoints ---

@app.post("/simulate")
async def simulate_tokenomics(params: SimulationParameters):
    """
    Runs the tokenomics simulation and returns the results.
    """
    try:
        simulation_params_dict = params.dict()
        results_df = run_simulation(simulation_params_dict)
        return results_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")

@app.post("/analyze_tokenomics")
async def analyze_tokenomics(request: LLMAnalysisRequest):
    """
    Analyzes simulation data using the LLM and returns the risk assessment.
    """
    try:
        simulation_data_json = json.dumps(request.simulation_data)
        analysis_text = get_llm_analysis(simulation_data_json)
        return {"analysis": analysis_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {e}")

@app.post("/generate_report")
async def generate_report_placeholder(request: ReportRequest):
    """
    Placeholder for generating a PDF report.
    """
    return {"message": "Report generation request received. Functionality to be implemented."}

@app.get("/")
async def read_root():
    """
    Simple root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Tokenomics Lab API!"}
