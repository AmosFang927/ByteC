"""
ML Serving Service — real-time CTR/CVR prediction API.

Endpoints:
  POST /predict       — batch predict CTR + CVR for a bid context
  GET  /models        — list loaded models and versions
  POST /models/reload — hot-reload models from registry (called hourly)
  GET  /health

Phase 0: skeleton returning synthetic predictions (no real model).
Phase 2: load PyTorch / ONNX models, real feature assembly.
"""

import os
import time
import logging
import random
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("ml_serving")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC ML Serving", version="0.1.0")

# ---------------------------------------------------------------------------
# Feature and prediction schemas
# ---------------------------------------------------------------------------

class BidFeatures(BaseModel):
    """
    Feature vector assembled from BidRequest fields.
    Phase 2 will add many more features (user history, app embedding, etc.)
    """
    # Device
    device_type: Optional[int] = None        # DeviceType enum value
    os: Optional[str] = None                 # "iOS", "Android", "Windows"
    # Geography
    country: Optional[str] = None            # ISO 3166-1 alpha-2
    # App / Publisher
    app_bundle: Optional[str] = None         # "com.example.app"
    app_categories: Optional[list[str]] = None
    # Impression
    imp_bidfloor: float = 0.0
    imp_is_interstitial: int = 0
    # Campaign
    campaign_id: Optional[str] = None
    campaign_goal_type: Optional[str] = None  # CPI | CPA | ROAS


class PredictRequest(BaseModel):
    request_id: str
    features: BidFeatures


class PredictResponse(BaseModel):
    request_id: str
    predicted_ctr: float
    predicted_cvr: float
    model_version: str
    latency_ms: float


class ModelInfo(BaseModel):
    name: str
    version: str
    loaded_at: str
    status: str


# ---------------------------------------------------------------------------
# In-memory model registry stub
# ---------------------------------------------------------------------------

_LOADED_MODELS: dict[str, ModelInfo] = {
    "ctr_model": ModelInfo(
        name="ctr_model",
        version="stub-v0.1",
        loaded_at="2026-03-22T00:00:00Z",
        status="loaded",
    ),
    "cvr_model": ModelInfo(
        name="cvr_model",
        version="stub-v0.1",
        loaded_at="2026-03-22T00:00:00Z",
        status="loaded",
    ),
}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml_serving", "models_loaded": len(_LOADED_MODELS)}


# ---------------------------------------------------------------------------
# Predict
# ---------------------------------------------------------------------------

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    """
    Predict CTR and CVR for a single bid opportunity.

    Phase 0: returns synthetic values with light noise to simulate model output.
    Phase 2: loads PyTorch DNN, assembles feature tensor, runs inference.
    """
    start = time.monotonic()

    ctr, cvr = _stub_predict(req.features)

    latency_ms = (time.monotonic() - start) * 1000
    logger.debug(
        "predict request_id=%s ctr=%.4f cvr=%.4f latency=%.2fms",
        req.request_id, ctr, cvr, latency_ms,
    )

    return PredictResponse(
        request_id=req.request_id,
        predicted_ctr=ctr,
        predicted_cvr=cvr,
        model_version=_LOADED_MODELS["ctr_model"].version,
        latency_ms=latency_ms,
    )


# ---------------------------------------------------------------------------
# Model management
# ---------------------------------------------------------------------------

@app.get("/models", response_model=list[ModelInfo])
async def list_models():
    return list(_LOADED_MODELS.values())


@app.post("/models/reload", status_code=202)
async def reload_models():
    """
    Hot-reload models from MLflow registry.
    Phase 0: no-op acknowledgement.
    Phase 2: downloads latest checkpoint, swaps in-memory model objects.
    """
    logger.info("model reload requested (no-op in Phase 0)")
    return {"status": "accepted", "message": "Model reload scheduled (Phase 0 stub)"}


# ---------------------------------------------------------------------------
# Stub predictor (Phase 0)
# ---------------------------------------------------------------------------

def _stub_predict(features: BidFeatures) -> tuple[float, float]:
    """
    Synthetic CTR/CVR with slight deterministic variation by country and device.
    Keeps downstream services testable before real models are wired in.

    Phase 2 replacement: load ONNX / PyTorch model, assemble feature vector,
    run inference, calibrate outputs with Platt scaling.
    """
    base_ctr = 0.04
    base_cvr = 0.02

    # Light country-based multipliers (simulates geo performance variance)
    geo_multiplier = {
        "US": 1.5, "JP": 1.3, "KR": 1.2, "DE": 1.1,
        "IN": 0.8, "BR": 0.9,
    }.get(features.country or "", 1.0)

    # Interstitials typically have higher CTR
    fmt_multiplier = 1.3 if features.imp_is_interstitial else 1.0

    ctr = min(base_ctr * geo_multiplier * fmt_multiplier, 0.99)
    cvr = min(base_cvr * geo_multiplier, 0.99)

    return round(ctr, 6), round(cvr, 6)
