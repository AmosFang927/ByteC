"""
Analytics Service — campaign performance reporting.

Endpoints:
  GET /report/campaign/{campaign_id}   — summary metrics for a campaign
  GET /report/campaigns                — multi-campaign summary
  GET /health

Phase 0: query from in-memory stores (imports from sibling services' state).
Phase 1: query PostgreSQL bid_logs, impressions, clicks, conversions tables.
Phase 2: streaming ClickHouse queries for sub-minute refresh.
"""

import os
import logging
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

logger = logging.getLogger("analytics")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC Analytics", version="0.1.0")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CampaignMetrics(BaseModel):
    campaign_id: str
    date_from: str
    date_to: str
    impressions: int
    clicks: int
    conversions: int
    spend_usd: float
    ctr: float            # clicks / impressions
    cvr: float            # conversions / clicks
    cpi_usd: float        # spend / conversions (cost-per-install)
    roas: float           # revenue / spend (0 if no revenue data)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics"}


# ---------------------------------------------------------------------------
# Campaign report
# ---------------------------------------------------------------------------

@app.get("/report/campaign/{campaign_id}", response_model=CampaignMetrics)
async def campaign_report(
    campaign_id: str,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
) -> CampaignMetrics:
    """
    Return aggregated performance metrics for a single campaign.

    Phase 0: returns synthetic stub data to validate schema and wiring.
    Phase 1: replace with PostgreSQL query against bid_logs + conversions.
    Phase 2: ClickHouse query for real-time data.
    """
    if date_from is None:
        date_from = date.today()
    if date_to is None:
        date_to = date.today()

    # Phase 0 stub: synthetic numbers per campaign_id
    stub = _stub_metrics(campaign_id, date_from, date_to)
    return stub


@app.get("/report/campaigns", response_model=list[CampaignMetrics])
async def campaigns_report(
    campaign_ids: list[str] = Query(...),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
) -> list[CampaignMetrics]:
    """Multi-campaign batch report."""
    if date_from is None:
        date_from = date.today()
    if date_to is None:
        date_to = date.today()
    return [_stub_metrics(cid, date_from, date_to) for cid in campaign_ids]


# ---------------------------------------------------------------------------
# Stub data generator (Phase 0)
# ---------------------------------------------------------------------------

def _stub_metrics(campaign_id: str, date_from: date, date_to: date) -> CampaignMetrics:
    """
    Synthetic but self-consistent metrics.
    Seed based on campaign_id so repeated calls return same values.
    """
    # Use a simple hash of campaign_id as a deterministic seed
    seed = sum(ord(c) for c in campaign_id) % 1000

    impressions = 10000 + seed * 50
    clicks = int(impressions * 0.04)      # 4% CTR
    conversions = int(clicks * 0.10)      # 10% CVR → 0.4% overall
    spend = conversions * 2.10            # ~$2.10 CPI
    revenue = conversions * 5.00          # $5 LTV per install (stub)

    ctr = clicks / impressions if impressions > 0 else 0.0
    cvr = conversions / clicks if clicks > 0 else 0.0
    cpi = spend / conversions if conversions > 0 else 0.0
    roas = revenue / spend if spend > 0 else 0.0

    return CampaignMetrics(
        campaign_id=campaign_id,
        date_from=date_from.isoformat(),
        date_to=date_to.isoformat(),
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        spend_usd=round(spend, 4),
        ctr=round(ctr, 6),
        cvr=round(cvr, 6),
        cpi_usd=round(cpi, 4),
        roas=round(roas, 4),
    )
