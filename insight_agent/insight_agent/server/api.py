from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ..engine import InsightAgentEngine
from ..schemas import InsightAgentRequest, InsightAgentResponse

app = FastAPI(
    title="InsightAgent Engine",
    version="0.1.0",
    description="Agentic marketing analytics microservice.",
)

engine = InsightAgentEngine()


@app.post("/analyze", response_model=InsightAgentResponse)
async def analyze(request: InsightAgentRequest) -> InsightAgentResponse:
    try:
        return engine.analyze(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
