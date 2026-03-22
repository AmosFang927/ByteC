"""
Campaign Management Service — advertiser/campaign CRUD.

Endpoints:
  POST   /advertisers
  GET    /advertisers/{id}
  POST   /campaigns
  GET    /campaigns/{id}
  PATCH  /campaigns/{id}
  DELETE /campaigns/{id}
  GET    /campaigns             (list by advertiser)
  POST   /campaigns/{id}/creatives
  GET    /campaigns/{id}/creatives

Phase 0: skeleton with in-memory store.
Phase 1: swap to PostgreSQL via asyncpg.
"""

import uuid
import os
import logging
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr

logger = logging.getLogger("campaign_mgmt")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ByteC Campaign Management", version="0.1.0")

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AdvertiserCreate(BaseModel):
    name: str
    email: str  # use str to avoid email-validator dep in Phase 0


class AdvertiserOut(BaseModel):
    id: str
    name: str
    email: str


class TargetingIn(BaseModel):
    geo_countries: Optional[list[str]] = None
    device_types: Optional[list[str]] = None
    app_categories: Optional[list[str]] = None


class CampaignCreate(BaseModel):
    advertiser_id: str
    name: str
    goal_type: str = "CPI"          # CPI | CPA | ROAS | CPM
    goal_value: float               # e.g. $2.00 target CPI
    daily_budget: float
    lifetime_budget: Optional[float] = None
    start_date: date
    end_date: Optional[date] = None
    targeting: Optional[TargetingIn] = None


class CampaignPatch(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    goal_value: Optional[float] = None
    daily_budget: Optional[float] = None
    end_date: Optional[date] = None


class CampaignOut(BaseModel):
    id: str
    advertiser_id: str
    name: str
    status: str
    goal_type: str
    goal_value: float
    daily_budget: float
    lifetime_budget: Optional[float]
    start_date: date
    end_date: Optional[date]
    targeting: Optional[TargetingIn]


class CreativeCreate(BaseModel):
    format: str          # banner | video | native
    width: Optional[int] = None
    height: Optional[int] = None
    asset_url: str
    click_url: str


class CreativeOut(BaseModel):
    id: str
    ad_group_id: str
    format: str
    width: Optional[int]
    height: Optional[int]
    asset_url: str
    click_url: str
    status: str


# ---------------------------------------------------------------------------
# In-memory store (Phase 0 — replaced by PostgreSQL in Phase 1)
# ---------------------------------------------------------------------------

_advertisers: dict[str, dict] = {}
_campaigns: dict[str, dict] = {}
_creatives: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "campaign_mgmt"}


# ---------------------------------------------------------------------------
# Advertisers
# ---------------------------------------------------------------------------

@app.post("/advertisers", response_model=AdvertiserOut, status_code=201)
async def create_advertiser(body: AdvertiserCreate):
    adv_id = str(uuid.uuid4())
    _advertisers[adv_id] = {"id": adv_id, "name": body.name, "email": body.email}
    return _advertisers[adv_id]


@app.get("/advertisers/{adv_id}", response_model=AdvertiserOut)
async def get_advertiser(adv_id: str):
    if adv_id not in _advertisers:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    return _advertisers[adv_id]


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

@app.post("/campaigns", response_model=CampaignOut, status_code=201)
async def create_campaign(body: CampaignCreate):
    if body.advertiser_id not in _advertisers:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    campaign_id = str(uuid.uuid4())
    record = {
        "id": campaign_id,
        "advertiser_id": body.advertiser_id,
        "name": body.name,
        "status": "PAUSED",
        "goal_type": body.goal_type,
        "goal_value": body.goal_value,
        "daily_budget": body.daily_budget,
        "lifetime_budget": body.lifetime_budget,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "targeting": body.targeting.model_dump() if body.targeting else None,
    }
    _campaigns[campaign_id] = record
    logger.info("created campaign id=%s name=%s", campaign_id, body.name)
    return record


@app.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: str):
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _campaigns[campaign_id]


@app.patch("/campaigns/{campaign_id}", response_model=CampaignOut)
async def patch_campaign(campaign_id: str, body: CampaignPatch):
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    record = _campaigns[campaign_id]
    for field, value in body.model_dump(exclude_none=True).items():
        record[field] = value
    return record


@app.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: str):
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    del _campaigns[campaign_id]


@app.get("/campaigns", response_model=list[CampaignOut])
async def list_campaigns(advertiser_id: str = Query(...)):
    return [c for c in _campaigns.values() if c["advertiser_id"] == advertiser_id]


# ---------------------------------------------------------------------------
# Creatives (attached to campaign, no ad-group layer in Phase 0)
# ---------------------------------------------------------------------------

@app.post("/campaigns/{campaign_id}/creatives", response_model=CreativeOut, status_code=201)
async def create_creative(campaign_id: str, body: CreativeCreate):
    if campaign_id not in _campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    cid = str(uuid.uuid4())
    record = {
        "id": cid,
        "ad_group_id": campaign_id,  # Phase 0: campaign_id doubles as ad_group_id
        "format": body.format,
        "width": body.width,
        "height": body.height,
        "asset_url": body.asset_url,
        "click_url": body.click_url,
        "status": "ACTIVE",
    }
    _creatives[cid] = record
    return record


@app.get("/campaigns/{campaign_id}/creatives", response_model=list[CreativeOut])
async def list_creatives(campaign_id: str):
    return [c for c in _creatives.values() if c["ad_group_id"] == campaign_id]
