"""
Budget Pacer Service — real-time spend control.

Responsibilities:
  - Track per-campaign daily spend via Redis atomic operations
  - Check budget availability before each bid
  - Enforce daily budget caps (overspend protection)
  - Provide hourly pacing signal (uniform in Phase 1, ML-driven in Phase 3)

Endpoints:
  POST /budget/check           — check if campaign has remaining budget
  POST /budget/spend           — deduct spend after win notification
  GET  /budget/{campaign_id}   — get current spend state
  POST /budget/reset           — reset daily counters (called at midnight)
  GET  /health

Redis key design:
  budget:daily:{campaign_id}:{YYYY-MM-DD}  →  spent (cents, integer)
  budget:limit:{campaign_id}:{YYYY-MM-DD}  →  daily_limit_cents (set once per day)
"""

import os
import logging
from datetime import date
from typing import Optional

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("budget_pacer")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC Budget Pacer", version="0.1.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_redis: Optional[aioredis.Redis] = None


@app.on_event("startup")
async def startup():
    global _redis
    _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    logger.info("connected to Redis at %s", REDIS_URL)


@app.on_event("shutdown")
async def shutdown():
    if _redis:
        await _redis.aclose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _spend_key(campaign_id: str, day: date) -> str:
    return f"budget:daily:{campaign_id}:{day.isoformat()}"


def _limit_key(campaign_id: str, day: date) -> str:
    return f"budget:limit:{campaign_id}:{day.isoformat()}"


def _to_cents(usd: float) -> int:
    """Convert USD float to integer cents (avoid float rounding in Redis)."""
    return int(round(usd * 100))


def _from_cents(cents: int) -> float:
    return cents / 100.0


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class BudgetCheckRequest(BaseModel):
    campaign_id: str
    bid_price_usd: float           # CPM bid; will be divided by 1000 on win
    daily_budget_usd: float        # authoritative daily limit (from Campaign Mgmt)


class BudgetCheckResponse(BaseModel):
    campaign_id: str
    allowed: bool
    spent_usd: float
    remaining_usd: float
    daily_budget_usd: float
    pacing_factor: float           # 0.0–1.0, used to throttle bid rate


class BudgetSpendRequest(BaseModel):
    campaign_id: str
    actual_spend_usd: float        # clear price / 1000 on a win


class BudgetSpendResponse(BaseModel):
    campaign_id: str
    spent_usd: float
    remaining_usd: float


class BudgetStateResponse(BaseModel):
    campaign_id: str
    date: str
    spent_usd: float
    daily_budget_usd: float
    remaining_usd: float
    utilization_pct: float


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    try:
        await _redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {"status": "ok" if redis_ok else "degraded", "service": "budget_pacer", "redis": redis_ok}


# ---------------------------------------------------------------------------
# Budget check (called by RTB Engine before each bid)
# ---------------------------------------------------------------------------

@app.post("/budget/check", response_model=BudgetCheckResponse)
async def check_budget(req: BudgetCheckRequest) -> BudgetCheckResponse:
    today = date.today()
    spend_key = _spend_key(req.campaign_id, today)
    limit_key = _limit_key(req.campaign_id, today)

    # Ensure limit is set (idempotent SETNX)
    limit_cents = _to_cents(req.daily_budget_usd)
    await _redis.setnx(limit_key, limit_cents)
    await _redis.expire(limit_key, 86400 * 2)  # TTL 2 days for safety

    spent_str = await _redis.get(spend_key)
    spent_cents = int(spent_str) if spent_str else 0
    remaining_cents = limit_cents - spent_cents

    allowed = remaining_cents > 0
    pacing_factor = _compute_pacing_factor(spent_cents, limit_cents)

    return BudgetCheckResponse(
        campaign_id=req.campaign_id,
        allowed=allowed,
        spent_usd=_from_cents(spent_cents),
        remaining_usd=max(_from_cents(remaining_cents), 0.0),
        daily_budget_usd=req.daily_budget_usd,
        pacing_factor=pacing_factor,
    )


# ---------------------------------------------------------------------------
# Record spend after a win notification
# ---------------------------------------------------------------------------

@app.post("/budget/spend", response_model=BudgetSpendResponse)
async def record_spend(req: BudgetSpendRequest) -> BudgetSpendResponse:
    today = date.today()
    spend_key = _spend_key(req.campaign_id, today)

    spend_cents = _to_cents(req.actual_spend_usd)
    new_spent_cents = await _redis.incrby(spend_key, spend_cents)
    await _redis.expire(spend_key, 86400 * 2)

    # Retrieve limit for remaining calc
    limit_key = _limit_key(req.campaign_id, today)
    limit_str = await _redis.get(limit_key)
    limit_cents = int(limit_str) if limit_str else 0

    remaining = max(_from_cents(limit_cents - new_spent_cents), 0.0)

    logger.info(
        "spend campaign=%s spend=%.4f total_spent=%.4f remaining=%.4f",
        req.campaign_id,
        req.actual_spend_usd,
        _from_cents(new_spent_cents),
        remaining,
    )

    return BudgetSpendResponse(
        campaign_id=req.campaign_id,
        spent_usd=_from_cents(new_spent_cents),
        remaining_usd=remaining,
    )


# ---------------------------------------------------------------------------
# Current budget state (for monitoring / analytics)
# ---------------------------------------------------------------------------

@app.get("/budget/{campaign_id}", response_model=BudgetStateResponse)
async def get_budget_state(campaign_id: str) -> BudgetStateResponse:
    today = date.today()
    spend_key = _spend_key(campaign_id, today)
    limit_key = _limit_key(campaign_id, today)

    spent_str = await _redis.get(spend_key)
    limit_str = await _redis.get(limit_key)

    spent_cents = int(spent_str) if spent_str else 0
    limit_cents = int(limit_str) if limit_str else 0

    remaining_cents = max(limit_cents - spent_cents, 0)
    utilization = (spent_cents / limit_cents * 100) if limit_cents > 0 else 0.0

    return BudgetStateResponse(
        campaign_id=campaign_id,
        date=today.isoformat(),
        spent_usd=_from_cents(spent_cents),
        daily_budget_usd=_from_cents(limit_cents),
        remaining_usd=_from_cents(remaining_cents),
        utilization_pct=round(utilization, 2),
    )


# ---------------------------------------------------------------------------
# Daily reset (called at midnight by cron / scheduler)
# ---------------------------------------------------------------------------

@app.post("/budget/reset", status_code=202)
async def reset_daily_budgets(campaign_ids: list[str]):
    """
    Expire today's spend keys for listed campaigns.
    Keys for the new day will be created lazily on first check_budget call.
    """
    today = date.today()
    for cid in campaign_ids:
        key = _spend_key(cid, today)
        await _redis.delete(key)
        logger.info("reset daily budget for campaign=%s", cid)
    return {"reset_count": len(campaign_ids)}


# ---------------------------------------------------------------------------
# Pacing factor (Phase 1: uniform; Phase 3: ML-driven)
# ---------------------------------------------------------------------------

def _compute_pacing_factor(spent_cents: int, limit_cents: int) -> float:
    """
    Simple uniform pacing: expected utilization based on hour of day.
    Returns a factor in [0, 1] that RTB Engine can use to throttle bid rate.

    Phase 3: replace with ML-predicted hourly spend distribution.
    """
    from datetime import datetime
    hour = datetime.now().hour  # 0-23
    # Expected fraction of daily budget by end of current hour
    expected_fraction = (hour + 1) / 24.0
    if limit_cents == 0:
        return 0.0
    actual_fraction = spent_cents / limit_cents
    # If we're ahead of pace, return factor < 1 to throttle
    if actual_fraction > expected_fraction:
        return max(0.0, 1.0 - (actual_fraction - expected_fraction))
    return 1.0
