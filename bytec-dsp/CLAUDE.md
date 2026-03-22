# ByteC DSP — Claude Development Guide

## Project Overview

A Moloco-comparable ML-first Demand-Side Platform (DSP). Core capability: real-time bidding
driven by deep neural network predictions (CTR, CVR, pacing) to maximize advertiser ROAS.

## Architecture

```
services/rtb_engine/     — OpenRTB 2.x bidding core (FastAPI)
services/campaign_mgmt/  — Advertiser/Campaign CRUD (FastAPI)
services/ml_serving/     — PyTorch inference API (FastAPI)
services/budget_pacer/   — Redis-based spend controller (FastAPI)
services/attribution/    — Conversion tracking (FastAPI)
services/analytics/      — Reporting queries (FastAPI)
shared/openrtb/          — OpenRTB 2.x Pydantic schemas
shared/bytec.py          — Byte encoding utilities (symlinked from repo root)
ml/models/               — PyTorch model definitions
ml/training/             — Training pipelines
infra/docker-compose.yml — Local dev environment
```

## Local Development

```bash
# Start infrastructure
cd infra && docker compose up -d

# Run all tests
pytest tests/ -v

# Run a single service
cd services/rtb_engine && uvicorn main:app --reload --port 8001
```

## Service Ports

| Service | Port |
|---|---|
| rtb_engine | 8001 |
| campaign_mgmt | 8002 |
| ml_serving | 8003 |
| budget_pacer | 8004 |
| attribution | 8005 |
| analytics | 8006 |

## gstack Workflow Gates

| Gate | When | Skill |
|---|---|---|
| Architecture review | Before building any service | `/plan-eng-review` |
| Brainstorm | Before complex design decisions | `/office-hours` |
| Code review | After service feature complete | `/review` |
| QA | Integration testing | `/qa` |
| Safety | Before Redis/Kafka/DB destructive ops | `/careful` |
| Release | End of each Phase | `/ship` |
| Debug | Any unexplained bug | `/investigate` |
| Retro | End of each Phase | `/retro` |

## Environment Variables

```
POSTGRES_URL=postgresql://bytec:bytec@localhost:5432/bytec_dsp
REDIS_URL=redis://localhost:6379
KAFKA_BOOTSTRAP=localhost:9092
ML_SERVING_URL=http://localhost:8003
BUDGET_PACER_URL=http://localhost:8004
```

## Key Design Decisions

1. **Bid price formula**: `bid_price = predicted_cvr * campaign_goal_cpa`
2. **Budget enforcement**: Redis atomic DECRBY on each bid; block when < 0
3. **ML model refresh**: Hourly retrain on last 24h events, hot-reload via MLflow registry
4. **OpenRTB version**: 2.5 (widely supported by SSPs)
