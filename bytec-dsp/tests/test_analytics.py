"""Tests for Analytics reporting service."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from services.analytics.main import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["service"] == "analytics"


class TestCampaignReport:
    def test_report_returns_valid_structure(self):
        resp = client.get("/report/campaign/campaign-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["campaign_id"] == "campaign-001"
        assert "impressions" in data
        assert "clicks" in data
        assert "conversions" in data
        assert "spend_usd" in data
        assert "ctr" in data
        assert "cvr" in data
        assert "cpi_usd" in data
        assert "roas" in data

    def test_metrics_in_valid_ranges(self):
        resp = client.get("/report/campaign/campaign-001")
        data = resp.json()
        assert data["impressions"] > 0
        assert 0.0 <= data["ctr"] <= 1.0
        assert 0.0 <= data["cvr"] <= 1.0
        assert data["spend_usd"] >= 0.0

    def test_deterministic_for_same_campaign(self):
        """Same campaign_id should return identical metrics."""
        r1 = client.get("/report/campaign/campaign-abc").json()
        r2 = client.get("/report/campaign/campaign-abc").json()
        assert r1["impressions"] == r2["impressions"]
        assert r1["spend_usd"] == r2["spend_usd"]

    def test_different_campaigns_differ(self):
        r1 = client.get("/report/campaign/campaign-111").json()
        r2 = client.get("/report/campaign/campaign-222").json()
        # Different seeds → different impressions counts
        assert r1["impressions"] != r2["impressions"]

    def test_date_range_accepted(self):
        resp = client.get("/report/campaign/campaign-001", params={
            "date_from": "2026-03-01",
            "date_to": "2026-03-22",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["date_from"] == "2026-03-01"
        assert data["date_to"] == "2026-03-22"


class TestMultiCampaignReport:
    def test_multi_campaign(self):
        resp = client.get("/report/campaigns", params={
            "campaign_ids": ["campaign-001", "campaign-002", "campaign-003"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        ids = [d["campaign_id"] for d in data]
        assert "campaign-001" in ids
        assert "campaign-002" in ids
