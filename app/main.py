"""FastAPI service exposing the NEWS2 early-warning score.

Endpoints:
    GET  /health  - liveness probe used by the CD deployment health check.
    POST /score    - compute the NEWS2 score for a set of observations.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.news2 import Consciousness, Observation, calculate_news2

app = FastAPI(
    title="NEWS2 Early-Warning Score API",
    description=(
        "Computes the National Early Warning Score 2 (Royal College of "
        "Physicians, 2017) from patient vital signs."
    ),
    version="1.0.0",
)


class ObservationRequest(BaseModel):
    respiratory_rate: int = Field(..., ge=0, le=80, examples=[18])
    spo2: int = Field(..., ge=50, le=100, examples=[97])
    on_supplemental_oxygen: bool = Field(..., examples=[False])
    systolic_bp: int = Field(..., ge=40, le=300, examples=[120])
    pulse: int = Field(..., ge=20, le=250, examples=[72])
    consciousness: Consciousness = Field(..., examples=["A"])
    temperature: float = Field(..., ge=25.0, le=45.0, examples=[36.8])


class ScoreResponse(BaseModel):
    total_score: int
    parameter_scores: dict[str, int]
    has_red_score: bool
    risk_band: str
    clinical_response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(request: ObservationRequest) -> ScoreResponse:
    observation = Observation(
        respiratory_rate=request.respiratory_rate,
        spo2=request.spo2,
        on_supplemental_oxygen=request.on_supplemental_oxygen,
        systolic_bp=request.systolic_bp,
        pulse=request.pulse,
        consciousness=request.consciousness,
        temperature=request.temperature,
    )
    result = calculate_news2(observation)
    return ScoreResponse(
        total_score=result.total_score,
        parameter_scores=result.parameter_scores,
        has_red_score=result.has_red_score,
        risk_band=result.risk_band.value,
        clinical_response=result.clinical_response,
    )
