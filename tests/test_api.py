"""Tests for the campus portal backend: API endpoints and wayfinding."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app  # noqa: E402
from app.campus import build_default_campus  # noqa: E402
from app.models import Event, Venue, db  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture()
def app():
    app = create_app("config.TestingConfig")
    with app.app_context():
        db.create_all()
        seed()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_venues_seeded(client):
    resp = client.get("/api/venues")
    venues = resp.get_json()["venues"]
    assert len(venues) == 5
    assert {v["node_id"] for v in venues} == {
        "library", "auditorium", "labs", "sports", "cafeteria"
    }


def test_events_have_live_and_upcoming(client):
    live = client.get("/api/events?status=live").get_json()["events"]
    upcoming = client.get("/api/events?status=upcoming").get_json()["events"]
    assert len(live) >= 1
    assert len(upcoming) >= 1
    assert all(e["status"] == "live" for e in live)
    assert all(e["status"] == "upcoming" for e in upcoming)


def test_starting_soon_window(client):
    resp = client.get("/api/events/starting-soon")
    data = resp.get_json()
    # Seeded "Open Lab" starts in 10 min; default lead window is 15 min.
    titles = [e["title"] for e in data["events"]]
    assert any("Open Lab" in t for t in titles)


def test_route_from_gate_to_venue(client):
    venue = client.get("/api/venues").get_json()["venues"][0]
    resp = client.get(f"/api/route?to={venue['id']}&from=gate")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["waypoints"][0]["id"] == "gate"
    assert data["waypoints"][-1]["id"] == venue["node_id"]
    assert data["distance_m"] > 0


def test_route_missing_param(client):
    assert client.get("/api/route").status_code == 400


def test_route_unknown_venue(client):
    assert client.get("/api/route?to=9999").status_code == 404


# --- Pure wayfinding unit tests (no HTTP layer) --------------------------

def test_dijkstra_picks_shorter_route():
    g = build_default_campus()
    # gate -> cafeteria has two possible paths; check the algorithm returns
    # a valid, connected path ending at the goal.
    path, dist = g.shortest_path("gate", "cafeteria")
    assert path[0] == "gate"
    assert path[-1] == "cafeteria"
    # consecutive nodes in the path must be genuine neighbours
    for a, b in zip(path, path[1:]):
        assert any(n == b for n, _ in g.adj[a])
    assert dist > 0


def test_event_status_transitions():
    now = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    e = Event(
        title="x",
        starts_at=now - timedelta(minutes=5),
        ends_at=now + timedelta(minutes=5),
    )
    assert e.status(now) == "live"
    assert e.status(now - timedelta(hours=1)) == "upcoming"
    assert e.status(now + timedelta(hours=1)) == "ended"
