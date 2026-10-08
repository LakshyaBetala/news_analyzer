"""Tests for the News Credibility Analyzer API."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


GOOD = {
    "title": "Central bank holds rates",
    "content": "According to an official statement, the verified data and published analysis "
               "confirmed the findings of the research report. Experts cited the evidence.",
    "source": "Reuters",
}
BAD = {
    "title": "SHOCKING secret miracle cure!!!",
    "content": "You won't believe this one weird trick doctors hate. Guaranteed, act now!!!",
    "source": "unknown",
}


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_version(client):
    r = client.get("/api/version")
    assert r.status_code == 200
    assert r.json()["service"] == "news-credibility-analyzer"


def test_analyze_credible_scores_higher_than_suspicious(client):
    good = client.post("/api/analyze", json=GOOD).json()
    bad = client.post("/api/analyze", json=BAD).json()
    assert good["credibility_score"] >= 60
    assert bad["credibility_score"] < 40
    assert good["credibility_score"] > bad["credibility_score"]


def test_analyze_response_shape(client):
    data = client.post("/api/analyze", json=GOOD).json()
    for key in ("credibility_score", "risk_factors", "recommendations", "timestamp", "version"):
        assert key in data


def test_analyze_missing_fields_is_422(client):
    assert client.post("/api/analyze", json={}).status_code == 422


def test_dashboard_and_releases_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/releases").status_code == 200


def test_releases_api_reads_local_file(client, tmp_path, monkeypatch):
    f = tmp_path / "releases.json"
    f.write_text(json.dumps([{"version": "1.abc", "status": "PROMOTED"}]))
    monkeypatch.delenv("S3_BUCKET", raising=False)
    monkeypatch.setenv("RELEASES_FILE", str(f))
    r = client.get("/api/releases")
    assert r.status_code == 200
    assert r.json()[0]["version"] == "1.abc"


def test_releases_api_empty_when_nothing_recorded(client, tmp_path, monkeypatch):
    monkeypatch.delenv("S3_BUCKET", raising=False)
    monkeypatch.setenv("RELEASES_FILE", str(tmp_path / "missing.json"))
    assert client.get("/api/releases").json() == []


def test_metrics_exposed(client):
    assert client.get("/metrics").status_code == 200
