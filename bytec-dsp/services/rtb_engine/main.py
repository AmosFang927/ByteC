"""
RTB Engine — OpenRTB 2.5 bid processor.

Responsibilities:
  - Receive BidRequests from SSP
  - Check campaign eligibility (targeting, budget)
  - Call ML Serving for CTR/CVR predictions
  - Calculate bid price: predicted_cvr * goal_cpa
  - Return BidResponse within tmax (default 100ms)

Phase 0: skeleton with health check and stubbed bid endpoint.
Phase 1: real targeting filter + Budget Pacer call.
Phase 2: ML Serving integration.
"""

import os
import uuid
import time
import logging

import httpx
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from shared.openrtb.schema import (
    BidRequest,
    BidResponse,
    BidResponseBid,
    BidResponseSeatBid,
    NoBidReasonCode,
)

logger = logging.getLogger("rtb_engine")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC RTB Engine", version="0.1.0")

ML_SERVING_URL = os.getenv("ML_SERVING_URL", "http://localhost:8003")
BUDGET_PACER_URL = os.getenv("BUDGET_PACER_URL", "http://localhost:8004")
SEAT_ID = "bytec"

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "rtb_engine"}


# ---------------------------------------------------------------------------
# Bid endpoint  POST /bid
# ---------------------------------------------------------------------------

@app.post("/bid", response_model=BidResponse)
async def bid(request: BidRequest) -> BidResponse:
    """
    Main bid handler.  SSP posts an OpenRTB BidRequest here.
    Returns a BidResponse (possibly empty / no-bid).
    """
    start = time.monotonic()

    if not request.imp:
        return BidResponse.no_bid(request.id, NoBidReasonCode.INVALID_REQUEST)

    imp = request.imp[0]  # Phase 0-1: process first impression only

    # --- Phase 1 placeholder: get active campaigns for this impression ---
    # campaign = await _select_campaign(request, imp)
    # For Phase 0 we use a hardcoded stub campaign
    stub_campaign = _stub_campaign()

    # --- Budget check (Phase 1 will call Budget Pacer service) ---
    # has_budget = await _check_budget(stub_campaign["id"], stub_campaign["daily_budget"])
    has_budget = True  # Phase 0 stub

    if not has_budget:
        return BidResponse.no_bid(request.id, NoBidReasonCode.UNKNOWN_ERROR)

    # --- ML prediction (Phase 2 will call ML Serving) ---
    predicted_ctr, predicted_cvr = _stub_ml_prediction()

    # --- Bid price calculation ---
    goal_cpa = stub_campaign["goal_cpa_usd"]
    bid_price_cpm = predicted_cvr * goal_cpa * 1000  # convert CPA → CPM

    # Respect bid floor
    if bid_price_cpm < imp.bidfloor:
        return BidResponse.no_bid(request.id, NoBidReasonCode.UNKNOWN_ERROR)

    bid_id = str(uuid.uuid4())
    elapsed_ms = (time.monotonic() - start) * 1000
    logger.info(
        "bid request_id=%s bid_price=%.4f cpm predicted_ctr=%.4f predicted_cvr=%.4f elapsed=%.1fms",
        request.id, bid_price_cpm, predicted_ctr, predicted_cvr, elapsed_ms,
    )

    return BidResponse(
        id=request.id,
        bidid=bid_id,
        cur="USD",
        seatbid=[
            BidResponseSeatBid(
                seat=SEAT_ID,
                bid=[
                    BidResponseBid(
                        id=bid_id,
                        impid=imp.id,
                        price=round(bid_price_cpm, 6),
                        cid=stub_campaign["id"],
                        crid=stub_campaign["creative_id"],
                        adomain=["example-advertiser.com"],
                        nurl=f"{ML_SERVING_URL}/win?bid_id={bid_id}&price=${{AUCTION_PRICE}}",
                        ext={
                            "predicted_ctr": predicted_ctr,
                            "predicted_cvr": predicted_cvr,
                        },
                    )
                ],
            )
        ],
    )


# ---------------------------------------------------------------------------
# Stubs (replaced in Phase 1 / Phase 2)
# ---------------------------------------------------------------------------

def _stub_campaign() -> dict:
    """Hardcoded demo campaign. Replaced by DB lookup in Phase 1."""
    return {
        "id": "demo-campaign-001",
        "creative_id": "demo-creative-001",
        "goal_cpa_usd": 2.0,      # $2.00 target cost-per-install
        "daily_budget": 100.0,    # $100/day
    }


def _stub_ml_prediction() -> tuple[float, float]:
    """
    Fixed-value stub for CTR and CVR.
    Phase 2 replaces this with a real HTTP call to ml_serving.

    Returns:
        (predicted_ctr, predicted_cvr)
    """
    return 0.05, 0.02  # 5% CTR, 2% CVR → bid = 0.02 * $2.00 * 1000 = $40 CPM
