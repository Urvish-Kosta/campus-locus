"""REST API for the campus portal.

Endpoints
---------
GET /api/health                     liveness probe
GET /api/campus                     full graph (nodes + edges) for map rendering
GET /api/venues                     all venues
GET /api/events?status=live|upcoming|all
GET /api/events/starting-soon       events whose start is within the lead window
GET /api/route?to=<venue_id>&from=<node_id>   shortest walking route
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, request

from .campus import build_default_campus
from .models import Event, Venue, db

api = Blueprint("api", __name__, url_prefix="/api")

# The campus graph is static data, so it is built once per process.
_campus = build_default_campus()


def _now() -> datetime:
    return datetime.now(timezone.utc)


@api.get("/health")
def health():
    return jsonify(status="ok", time=_now().isoformat())


@api.get("/campus")
def campus():
    edges = []
    seen: set[frozenset[str]] = set()
    for node_id, neighbours in _campus.adj.items():
        for neighbour, dist in neighbours:
            key = frozenset((node_id, neighbour))
            if key in seen:
                continue
            seen.add(key)
            edges.append({"a": node_id, "b": neighbour, "distance_m": round(dist, 1)})
    return jsonify(
        nodes=[n.to_dict() for n in _campus.nodes.values()],
        edges=edges,
    )


@api.get("/venues")
def venues():
    items = Venue.query.order_by(Venue.name).all()
    return jsonify(venues=[v.to_dict() for v in items])


@api.get("/events")
def events():
    status = request.args.get("status", "all").lower()
    grace = current_app.config["LIVE_GRACE_MINUTES"]
    now = _now()

    items = Event.query.order_by(Event.starts_at).all()
    payload = [e.to_dict(now, grace) for e in items]
    if status in {"live", "upcoming", "ended"}:
        payload = [e for e in payload if e["status"] == status]
    return jsonify(events=payload)


@api.get("/events/starting-soon")
def starting_soon():
    """Events starting within the configured lead window.

    This is the data source for the on-device "an event is starting" pop-up.
    """
    lead = current_app.config["NOTIFY_LEAD_MINUTES"]
    now = _now()
    window_end = now + timedelta(minutes=lead)
    grace = current_app.config["LIVE_GRACE_MINUTES"]

    soon = []
    for e in Event.query.order_by(Event.starts_at).all():
        starts = e.starts_at
        if starts.tzinfo is None:
            starts = starts.replace(tzinfo=timezone.utc)
        if now <= starts <= window_end:
            soon.append(e.to_dict(now, grace))
    return jsonify(lead_minutes=lead, events=soon)


@api.get("/route")
def route():
    venue_id = request.args.get("to", type=int)
    start_node = request.args.get("from", default="gate", type=str)
    if venue_id is None:
        return jsonify(error="query parameter 'to' (venue id) is required"), 400

    venue = db.session.get(Venue, venue_id)
    if venue is None:
        return jsonify(error=f"venue {venue_id} not found"), 404

    try:
        data = _campus.route_dict(start_node, venue.node_id)
    except KeyError as exc:
        return jsonify(error=str(exc)), 400
    except ValueError as exc:
        return jsonify(error=str(exc)), 422

    data["venue"] = venue.to_dict()
    return jsonify(data)
