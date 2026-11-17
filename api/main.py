"""Experience Analysis Studio - FastAPI service."""
from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from basis.experience import analyse_experience, load_experience_dataset

app = FastAPI(title="Experience Analysis Studio", version="1.0.0",
    docs_url="/api/docs", openapi_url="/api/openapi.json",
    description="Actual-versus-expected mortality analysis with credibility.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
router = APIRouter(prefix="/api")


@router.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "basis-experience"}


class ExperienceRequest(BaseModel):
    by: list[Literal["age_band", "sex", "smoker_status"]] = Field(default_factory=lambda: ["smoker_status"])


@router.post("/experience/analyse", tags=["pricing"])
def experience(req: ExperienceRequest) -> dict:
    df = load_experience_dataset().copy()
    by = list(req.by)
    if "age_band" in by:
        df["age_band"] = (df["age"] // 10 * 10).astype(int).astype(str) + "s"
    return asdict(analyse_experience(df, by=by))


@router.get("/experience/dataset", tags=["admin"])
def experience_dataset() -> dict:
    df = load_experience_dataset()
    return {"cells": len(df), "life_years": round(float(df["exposure"].sum()), 0),
            "deaths": int(df["actual_deaths"].sum()),
            "ages": [int(df["age"].min()), int(df["age"].max())],
            "expected_basis": "2015 VBT ultimate"}

app.include_router(router)
