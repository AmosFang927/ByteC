"""
Attribution Service — conversion tracking and last-touch attribution.

Responsibilities:
  - Click tracking pixel endpoint (GET /click/{click_token})
  - Install / conversion postback endpoint (POST /postback)
  - Attribution matching: click → install (last-touch, 7-day window)
  - Emit attributed events to Kafka topic "attributed_conversions"

Endpoints:
  GET  /click/{click_token}   — redirect + record click (called by ad creative)
  POST /postback              — receive install/conversion from MMP or app SDK
  GET  /health

Click token format (base64-encoded, using bytec.py utilities):
  {impression_id}:{campaign_id}:{timestamp}

Phase 0: skeleton with in-memory stores; no Kafka.
Phase 1: PostgreSQL persistence + Kafka emit.
Phase 2: view-through attribution, MMP webhook integration.
"""

import base64
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Re-use bytec.py encoding utilities from repo root
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
try:
    from bytec import encode, decode, to_hex
except ImportError:
    # Fallback if bytec not on path
    def encode(text: str, encoding: str = "utf-8") -> bytes:
        return text.encode(encoding)
    def decode(data: bytes, encoding: str = "utf-8") -> str:
        return data.decode(encoding)
    def to_hex(data: bytes) -> str:
        return data.hex()

logger = logging.getLogger("attribution")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC Attribution", version="0.1.0")

ATTRIBUTION_WINDOW_DAYS = 7

# ---------------------------------------------------------------------------
# In-memory stores (Phase 0)
# ---------------------------------------------------------------------------

_clicks: dict[str, dict] = {}          # click_id → click record
_impressions: dict[str, dict] = {}     # impression_id → click_id
_conversions: list[dict] = []


# ---------------------------------------------------------------------------
# Click token helpers
# ---------------------------------------------------------------------------

def make_click_token(impression_id: str, campaign_id: str) -> str:
    """Encode impression metadata into a URL-safe click token."""
    payload = f"{impression_id}|{campaign_id}|{int(time.time())}"
    raw = encode(payload)
    return base64.urlsafe_b64encode(raw).decode("ascii")


def parse_click_token(token: str) -> tuple[str, str, int]:
    """Decode click token → (impression_id, campaign_id, timestamp)."""
    raw = base64.urlsafe_b64decode(token.encode("ascii") + b"==")
    payload = decode(raw)
    parts = payload.split("|")
    if len(parts) != 3:
        raise ValueError(f"Invalid click token: {token}")
    impression_id, campaign_id, ts = parts
    return impression_id, campaign_id, int(ts)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class PostbackRequest(BaseModel):
    """
    Conversion postback from MMP (Adjust, AppsFlyer) or app SDK.
    Identifies which click led to this install/event.
    """
    click_token: str                      # same token sent in ad click URL
    event_type: str = "install"           # install | purchase | registration | ...
    revenue_usd: float = 0.0
    idfa: Optional[str] = None
    gaid: Optional[str] = None
    app_bundle: Optional[str] = None
    event_time: Optional[datetime] = None


class PostbackResponse(BaseModel):
    conversion_id: str
    attributed: bool
    campaign_id: Optional[str]
    click_id: Optional[str]
    event_type: str


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "attribution",
        "clicks_tracked": len(_clicks),
        "conversions_tracked": len(_conversions),
    }


# ---------------------------------------------------------------------------
# Click tracking
# ---------------------------------------------------------------------------

@app.get("/click/{click_token}")
async def track_click(
    click_token: str,
    redirect_url: str = Query(..., description="Landing page URL to redirect user to"),
):
    """
    Record click, then redirect user to advertiser landing page.
    Called by click_url embedded in ad creative.
    """
    try:
        impression_id, campaign_id, ts = parse_click_token(click_token)
    except (ValueError, Exception) as e:
        logger.warning("invalid click token %s: %s", click_token, e)
        raise HTTPException(status_code=400, detail="Invalid click token")

    click_id = str(uuid.uuid4())
    click_record = {
        "id": click_id,
        "click_token": click_token,
        "impression_id": impression_id,
        "campaign_id": campaign_id,
        "ts": datetime.now(timezone.utc),
        "token_ts": ts,
    }
    _clicks[click_id] = click_record
    _impressions[impression_id] = click_id

    # Log click token hex fingerprint for auditing (uses bytec.py)
    token_hex = to_hex(encode(click_token))[:16]
    logger.info(
        "click id=%s campaign=%s token_hex=%s",
        click_id, campaign_id, token_hex,
    )

    return RedirectResponse(url=redirect_url, status_code=302)


# ---------------------------------------------------------------------------
# Conversion postback
# ---------------------------------------------------------------------------

@app.post("/postback", response_model=PostbackResponse)
async def receive_postback(req: PostbackRequest) -> PostbackResponse:
    """
    Match incoming conversion to the last click within attribution window.
    Phase 0: last-touch click-to-install only.
    Phase 2: view-through, multi-touch, MMP webhook passthrough.
    """
    conversion_id = str(uuid.uuid4())

    try:
        impression_id, campaign_id, token_ts = parse_click_token(req.click_token)
    except (ValueError, Exception) as e:
        logger.warning("postback with invalid click token: %s", e)
        conversion = {
            "id": conversion_id,
            "attributed": False,
            "campaign_id": None,
            "click_id": None,
            "event_type": req.event_type,
            "revenue_usd": req.revenue_usd,
            "ts": datetime.now(timezone.utc),
        }
        _conversions.append(conversion)
        return PostbackResponse(
            conversion_id=conversion_id,
            attributed=False,
            campaign_id=None,
            click_id=None,
            event_type=req.event_type,
        )

    click_id = _impressions.get(impression_id)
    attributed = False

    if click_id:
        click = _clicks.get(click_id)
        if click:
            # Check attribution window
            event_ts = req.event_time or datetime.now(timezone.utc)
            click_ts = click["ts"]
            if event_ts - click_ts <= timedelta(days=ATTRIBUTION_WINDOW_DAYS):
                attributed = True

    conversion = {
        "id": conversion_id,
        "attributed": attributed,
        "campaign_id": campaign_id if attributed else None,
        "click_id": click_id if attributed else None,
        "event_type": req.event_type,
        "revenue_usd": req.revenue_usd,
        "ts": datetime.now(timezone.utc),
    }
    _conversions.append(conversion)

    logger.info(
        "conversion id=%s attributed=%s campaign=%s event=%s",
        conversion_id, attributed, campaign_id, req.event_type,
    )

    # Phase 1: emit to Kafka topic "attributed_conversions"

    return PostbackResponse(
        conversion_id=conversion_id,
        attributed=attributed,
        campaign_id=campaign_id if attributed else None,
        click_id=click_id if attributed else None,
        event_type=req.event_type,
    )
