"""Tests for Campaign Management Service."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from services.campaign_mgmt.main import app, _advertisers, _campaigns, _creatives

client = TestClient(app)


def setup_function():
    """Reset in-memory stores before each test function."""
    _advertisers.clear()
    _campaigns.clear()
    _creatives.clear()


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["service"] == "campaign_mgmt"


class TestAdvertisers:
    def test_create_advertiser(self):
        resp = client.post("/advertisers", json={"name": "Acme Corp", "email": "acme@example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Acme Corp"
        assert "id" in data

    def test_get_advertiser(self):
        create_resp = client.post("/advertisers", json={"name": "Acme", "email": "a@b.com"})
        adv_id = create_resp.json()["id"]
        resp = client.get(f"/advertisers/{adv_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == adv_id

    def test_get_nonexistent_advertiser(self):
        resp = client.get("/advertisers/nonexistent-id")
        assert resp.status_code == 404


class TestCampaigns:
    def _create_advertiser(self) -> str:
        resp = client.post("/advertisers", json={"name": "TestCo", "email": "test@co.com"})
        return resp.json()["id"]

    def _campaign_payload(self, adv_id: str) -> dict:
        return {
            "advertiser_id": adv_id,
            "name": "Summer Install Campaign",
            "goal_type": "CPI",
            "goal_value": 2.0,
            "daily_budget": 100.0,
            "start_date": "2026-04-01",
            "targeting": {
                "geo_countries": ["US", "CA"],
                "device_types": ["phone"],
            },
        }

    def test_create_campaign(self):
        adv_id = self._create_advertiser()
        resp = client.post("/campaigns", json=self._campaign_payload(adv_id))
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Summer Install Campaign"
        assert data["status"] == "PAUSED"
        assert data["goal_value"] == 2.0

    def test_campaign_targeting_saved(self):
        adv_id = self._create_advertiser()
        resp = client.post("/campaigns", json=self._campaign_payload(adv_id))
        targeting = resp.json()["targeting"]
        assert "US" in targeting["geo_countries"]
        assert targeting["device_types"] == ["phone"]

    def test_get_campaign(self):
        adv_id = self._create_advertiser()
        c = client.post("/campaigns", json=self._campaign_payload(adv_id)).json()
        resp = client.get(f"/campaigns/{c['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == c["id"]

    def test_patch_campaign_status(self):
        adv_id = self._create_advertiser()
        c = client.post("/campaigns", json=self._campaign_payload(adv_id)).json()
        resp = client.patch(f"/campaigns/{c['id']}", json={"status": "ACTIVE"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "ACTIVE"

    def test_delete_campaign(self):
        adv_id = self._create_advertiser()
        c = client.post("/campaigns", json=self._campaign_payload(adv_id)).json()
        resp = client.delete(f"/campaigns/{c['id']}")
        assert resp.status_code == 204
        assert client.get(f"/campaigns/{c['id']}").status_code == 404

    def test_list_campaigns_by_advertiser(self):
        adv_id = self._create_advertiser()
        client.post("/campaigns", json=self._campaign_payload(adv_id))
        client.post("/campaigns", json={**self._campaign_payload(adv_id), "name": "Campaign 2"})
        resp = client.get("/campaigns", params={"advertiser_id": adv_id})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_create_campaign_unknown_advertiser(self):
        resp = client.post("/campaigns", json={
            "advertiser_id": "does-not-exist",
            "name": "X",
            "goal_type": "CPI",
            "goal_value": 1.0,
            "daily_budget": 50.0,
            "start_date": "2026-04-01",
        })
        assert resp.status_code == 404


class TestCreatives:
    def _setup(self):
        adv = client.post("/advertisers", json={"name": "A", "email": "a@a.com"}).json()
        campaign = client.post("/campaigns", json={
            "advertiser_id": adv["id"],
            "name": "C",
            "goal_type": "CPI",
            "goal_value": 1.0,
            "daily_budget": 50.0,
            "start_date": "2026-04-01",
        }).json()
        return campaign["id"]

    def test_create_creative(self):
        campaign_id = self._setup()
        resp = client.post(f"/campaigns/{campaign_id}/creatives", json={
            "format": "banner",
            "width": 320,
            "height": 50,
            "asset_url": "https://cdn.example.com/ad.png",
            "click_url": "https://example.com/landing",
        })
        assert resp.status_code == 201
        assert resp.json()["format"] == "banner"

    def test_list_creatives(self):
        campaign_id = self._setup()
        for _ in range(3):
            client.post(f"/campaigns/{campaign_id}/creatives", json={
                "format": "banner",
                "asset_url": "https://cdn.example.com/ad.png",
                "click_url": "https://example.com/lp",
            })
        resp = client.get(f"/campaigns/{campaign_id}/creatives")
        assert resp.status_code == 200
        assert len(resp.json()) == 3
