"""Tests for ML Serving prediction API."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from services.ml_serving.main import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["models_loaded"] == 2   # ctr_model + cvr_model


class TestPredict:
    def _features(self, country: str = "US", device_type: int = 4) -> dict:
        return {
            "request_id": "test-req-001",
            "features": {
                "device_type": device_type,
                "os": "Android",
                "country": country,
                "app_bundle": "com.example.game",
                "app_categories": ["IAB9"],
                "imp_bidfloor": 0.5,
                "imp_is_interstitial": 0,
                "campaign_id": "campaign-001",
                "campaign_goal_type": "CPI",
            },
        }

    def test_predict_returns_valid_response(self):
        resp = client.post("/predict", json=self._features())
        assert resp.status_code == 200
        data = resp.json()
        assert "predicted_ctr" in data
        assert "predicted_cvr" in data
        assert data["request_id"] == "test-req-001"

    def test_ctr_in_valid_range(self):
        resp = client.post("/predict", json=self._features())
        ctr = resp.json()["predicted_ctr"]
        assert 0.0 <= ctr <= 1.0

    def test_cvr_in_valid_range(self):
        resp = client.post("/predict", json=self._features())
        cvr = resp.json()["predicted_cvr"]
        assert 0.0 <= cvr <= 1.0

    def test_latency_reported(self):
        resp = client.post("/predict", json=self._features())
        assert resp.json()["latency_ms"] >= 0

    def test_model_version_in_response(self):
        resp = client.post("/predict", json=self._features())
        assert "model_version" in resp.json()

    def test_us_higher_than_low_value_country(self):
        """US should have higher predicted CTR than BR (stub geo multipliers)."""
        us_ctr = client.post("/predict", json=self._features("US")).json()["predicted_ctr"]
        br_ctr = client.post("/predict", json=self._features("BR")).json()["predicted_ctr"]
        assert us_ctr > br_ctr

    def test_interstitial_higher_ctr(self):
        features_non_inst = self._features()
        features_inst = self._features()
        features_inst["features"]["imp_is_interstitial"] = 1
        non_inst_ctr = client.post("/predict", json=features_non_inst).json()["predicted_ctr"]
        inst_ctr = client.post("/predict", json=features_inst).json()["predicted_ctr"]
        assert inst_ctr > non_inst_ctr


class TestModels:
    def test_list_models(self):
        resp = client.get("/models")
        assert resp.status_code == 200
        models = resp.json()
        names = [m["name"] for m in models]
        assert "ctr_model" in names
        assert "cvr_model" in names

    def test_reload_models(self):
        resp = client.post("/models/reload")
        assert resp.status_code == 202
