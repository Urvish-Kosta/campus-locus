"""Domain models: venues and events.

A *venue* is a fixed place on campus (a building, hall, or ground) that maps
onto a node in the campus wayfinding graph. An *event* happens at a venue
within a start/end time window and drives both the map markers and the
"starting soon" notifications.
"""
from __future__ import annotations

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    category = db.Column(db.String(60), nullable=False, default="building")
    description = db.Column(db.String(500), nullable=False, default="")

    # Identifier of the corresponding node in the campus graph (see campus.py).
    # Kept as a plain string so the graph and the database stay decoupled.
    node_id = db.Column(db.String(60), nullable=False, unique=True)

    events = db.relationship("Event", back_populates="venue", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "node_id": self.node_id,
        }


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(1000), nullable=False, default="")
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    venue = db.relationship("Venue", back_populates="events")

    def status(self, now: datetime | None = None, live_grace_minutes: int = 0) -> str:
        """Return 'upcoming', 'live', or 'ended' relative to *now*."""
        now = now or _utcnow()
        starts = _as_aware(self.starts_at)
        ends = _as_aware(self.ends_at)
        if now < starts:
            return "upcoming"
        grace = ends
        if live_grace_minutes:
            from datetime import timedelta

            grace = ends + timedelta(minutes=live_grace_minutes)
        if now <= grace:
            return "live"
        return "ended"

    def to_dict(self, now: datetime | None = None, live_grace_minutes: int = 0) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "starts_at": _as_aware(self.starts_at).isoformat(),
            "ends_at": _as_aware(self.ends_at).isoformat(),
            "status": self.status(now, live_grace_minutes),
            "venue": self.venue.to_dict() if self.venue else None,
        }


def _as_aware(value: datetime) -> datetime:
    """SQLite drops tzinfo on round-trip; treat naive timestamps as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
