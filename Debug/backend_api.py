from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI(title="Reddit Insight Engine")

# Allow frontend (Vite / React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Request schema -------- #

class AnalyzeRequest(BaseModel):
    query: str


# -------- API -------- #

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Full pipeline:
    1. Convert user query → research plan (query_planner_agent)
    2. Run reddit ingestion
    3. Run analysis agent
    4. Return insights
    """

    # ---------------- Step 1: Query → Research Plan ---------------- #

    subprocess.run(
        ["python", "query_planner_agent.py", req.query],
        check=True
    )
    # This generates: ex.json

    # ---------------- Step 2: Reddit Ingestion ---------------- #

    subprocess.run(
        ["python", "main.py", "ex.json"],
        check=True
    )
    # This generates: ingestion_output.json

    # ---------------- Step 3: Analysis Agent ---------------- #

    result = subprocess.run(
        ["python", "reddit_analysis_agent.py", "ingestion_output.json"],
        capture_output=True,
        text=True,
        check=True
    )

    # ---------------- Step 4: Return JSON ---------------- #

    return json.loads(result.stdout)
