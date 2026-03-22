"""Tests for RTB Engine bid endpoint."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from services.rtb_engine.main import app
from shared.openrtb.schema import BidRequest, Imp, Banner, App, Device, Geo


client = TestClient(app)


def _bid_request_payload(request_id: str = "req-test-001", bid_floor: float = 0.5) -> dict:
    return {
        "id": request_id,
        "imp": [
            {
                "id": "imp-001",
                "bidfloor": bid_floor,
                "bidfloorcur": "USD",
                "banner": {"w": 320, "h": 50},
            }
        ],
        "app": {"id": "app-001", "bundle": "com.example.game", "cat": ["IAB9"]},
        "device": {"devicetype": 4, "os": "Android", "geo": {"country": "US"}},
    }


class TestRTBEngineHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert resp.json()["service"] == "rtb_engine"


class TestBidEndpoint:
    def test_returns_bid_for_valid_request(self):
        resp = client.post("/bid", json=_bid_request_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "req-test-001"
        assert data["seatbid"] is not None
        assert len(data["seatbid"]) == 1
        assert len(data["seatbid"][0]["bid"]) == 1

    def test_bid_price_positive(self):
        resp = client.post("/bid", json=_bid_request_payload())
        bid_price = resp.json()["seatbid"][0]["bid"][0]["price"]
        assert bid_price > 0

    def test_bid_impid_matches_request(self):
        resp = client.post("/bid", json=_bid_request_payload())
        impid = resp.json()["seatbid"][0]["bid"][0]["impid"]
        assert impid == "imp-001"

    def test_no_bid_when_floor_too_high(self):
        """When bid floor is above our max bid price, expect no-bid."""
        # Stub predicts CVR=0.02, goal_cpa=$2 → bid = $40 CPM
        # Set floor to $999 CPM → should no-bid
        payload = _bid_request_payload(bid_floor=999.0)
        resp = client.post("/bid", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # No seatbid means no-bid response
        assert data.get("seatbid") is None or data.get("nbr") is not None

    def test_no_bid_when_no_impressions(self):
        payload = {
            "id": "req-empty",
            "imp": [],
        }
        resp = client.post("/bid", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("nbr") is not None

    def test_bid_price_formula(self):
        """bid_price_cpm should equal predicted_cvr * goal_cpa * 1000."""
        resp = client.post("/bid", json=_bid_request_payload())
        bid = resp.json()["seatbid"][0]["bid"][0]
        ext = bid.get("ext", {})
        predicted_cvr = ext.get("predicted_cvr", 0)
        # Stub: CVR=0.02, goal_cpa=2.0 → expected CPM = 40.0
        assert abs(bid["price"] - 40.0) < 0.01

    def test_response_currency(self):
        resp = client.post("/bid", json=_bid_request_payload())
        assert resp.json()["cur"] == "USD"
