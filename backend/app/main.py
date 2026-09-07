from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.repository import load_data_file
from app.schemas import (
    LenderSearchResponse,
    ModelCardResponse,
    Persona,
    ScoreRequest,
    ScoreResponse,
)
from app.services.lenders import search_lenders
from app.services.scoring import calculate_score

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description=(
        "Stateless, synthetic-data-only prototype API. It provides decision support, not credit underwriting, approval, or fraud determination."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    model = load_data_file("model.json")
    registry = load_data_file("registry.json")
    return {
        "status": "ok",
        "api_version": settings.api_version,
        "model_version": model["model_version"],
        "registry_snapshot_id": registry["provenance"]["snapshot_id"],
    }


@app.get("/api/personas", response_model=list[Persona])
def list_personas() -> list[Persona]:
    personas = load_data_file("personas.json")["personas"]
    return [Persona(**persona) for persona in personas]


@app.post("/api/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    if not request.consent_acknowledged:
        raise HTTPException(
            status_code=422,
            detail="Consent acknowledgement is required before calculating a prototype score.",
        )
    return calculate_score(request.features, request.intended_use)


@app.get("/api/lenders/search", response_model=LenderSearchResponse)
def lender_search(q: str = Query(min_length=2, max_length=120)) -> LenderSearchResponse:
    return search_lenders(q)


@app.get("/api/model-card", response_model=ModelCardResponse)
def model_card() -> ModelCardResponse:
    model = load_data_file("model.json")
    registry = load_data_file("registry.json")
    return ModelCardResponse(
        model_version=model["model_version"],
        feature_schema_version=model["feature_schema_version"],
        scoring_approach=model["scoring_approach"],
        baseline_score=model["baseline_score"],
        features=model["features"],
        exclusions=model["exclusions"],
        limitations=model["limitations"],
        test_summary=model["test_summary"],
        registry_provenance=registry["provenance"],
    )
