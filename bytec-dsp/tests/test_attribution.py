"""Tests for Attribution Service — click tracking and conversion postback."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from services.attribution.main import (
    app, _clicks, _impressions, _conversions,
    make_click_token, parse_click_token,
)

client = TestClient(app, follow_redirects=False)


def setup_function():
    _clicks.clear()
    _impressions.clear()
    _conversions.clear()


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["service"] == "attribution"


class TestClickToken:
    def test_roundtrip(self):
        imp_id, camp_id = "imp-123", "campaign-456"
        token = make_click_token(imp_id, camp_id)
        parsed_imp, parsed_camp, ts = parse_click_token(token)
        assert parsed_imp == imp_id
        assert parsed_camp == camp_id
        assert ts > 0

    def test_invalid_token_raises(self):
        with pytest.raises((ValueError, Exception)):
            parse_click_token("not-a-valid-token!!")


class TestClickTracking:
    def setup_method(self):
        _clicks.clear()
        _impressions.clear()
        _conversions.clear()

    def test_click_redirects(self):
        token = make_click_token("imp-001", "camp-001")
        resp = client.get(f"/click/{token}", params={"redirect_url": "https://example.com"})
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com"

    def test_click_recorded(self):
        token = make_click_token("imp-002", "camp-002")
        client.get(f"/click/{token}", params={"redirect_url": "https://example.com"})
        assert len(_clicks) == 1

    def test_invalid_token_returns_400(self):
        resp = client.get("/click/INVALID_TOKEN", params={"redirect_url": "https://example.com"})
        assert resp.status_code == 400


class TestPostback:
    def setup_method(self):
        _clicks.clear()
        _impressions.clear()
        _conversions.clear()

    def test_attributed_conversion(self):
        """Click → postback within window should be attributed."""
        token = make_click_token("imp-100", "camp-100")
        # Record the click
        client.get(f"/click/{token}", params={"redirect_url": "https://example.com"})

        # Send postback
        resp = client.post("/postback", json={
            "click_token": token,
            "event_type": "install",
            "revenue_usd": 0.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["attributed"] is True
        assert data["campaign_id"] == "camp-100"
        assert data["event_type"] == "install"

    def test_unattributed_no_click(self):
        """Postback with a token that was never clicked → not attributed."""
        token = make_click_token("imp-999", "camp-999")
        # Do NOT call /click — just send postback directly
        resp = client.post("/postback", json={
            "click_token": token,
            "event_type": "install",
        })
        assert resp.status_code == 200
        assert resp.json()["attributed"] is False

    def test_invalid_token_in_postback(self):
        resp = client.post("/postback", json={
            "click_token": "garbage-token",
            "event_type": "install",
        })
        assert resp.status_code == 200
        assert resp.json()["attributed"] is False

    def test_conversion_id_generated(self):
        token = make_click_token("imp-200", "camp-200")
        client.get(f"/click/{token}", params={"redirect_url": "https://example.com"})
        resp = client.post("/postback", json={"click_token": token, "event_type": "purchase"})
        assert "conversion_id" in resp.json()
        assert len(resp.json()["conversion_id"]) == 36  # UUID length
