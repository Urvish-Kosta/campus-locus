"""Seed the database with the fictional campus venues and demo events.

Events are seeded *relative to the current time* so that a freshly seeded
database always has one live event, one starting soon, and one later today.
This keeps the demo reproducible without hand-editing timestamps.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .campus import build_default_campus
from .models import Event, Venue, db


def _venues_from_graph() -> list[Venue]:
    graph = build_default_campus()
    descriptions = {
        "library": ("Central Library", "library", "Study spaces, archives, and the digital resource centre."),
        "auditorium": ("Auditorium", "hall", "Main 600-seat auditorium for talks and ceremonies."),
        "labs": ("Engineering Labs", "academic", "Electronics, embedded systems, and prototyping labs."),
        "sports": ("Sports Complex", "recreation", "Indoor courts, gym, and the athletics ground."),
        "cafeteria": ("Cafeteria", "amenity", "Central food court and seating."),
    }
    venues = []
    for node in graph.nodes.values():
        if node.kind != "venue":
            continue
        name, category, desc = descriptions[node.id]
        venues.append(Venue(name=name, category=category, description=desc, node_id=node.id))
    return venues


def seed(clear: bool = True) -> dict:
    if clear:
        Event.query.delete()
        Venue.query.delete()
        db.session.commit()

    venues = _venues_from_graph()
    db.session.add_all(venues)
    db.session.commit()

    by_node = {v.node_id: v for v in venues}
    now = datetime.now(timezone.utc)

    demo_events = [
        # (venue_node, title, start_offset_min, duration_min, description)
        ("auditorium", "Keynote: Semiconductors & Edge AI", -20, 90,
         "Guest lecture on AI accelerators and edge computing."),
        ("labs", "Embedded Systems Open Lab", 10, 120,
         "Walk-in demos of student FPGA and IoT projects."),
        ("sports", "Inter-Department Football Final", 150, 100,
         "Championship match on the main ground."),
        ("library", "Research Writing Workshop", 300, 60,
         "Hands-on session on structuring a technical paper."),
    ]

    events = []
    for node_id, title, start_off, dur, desc in demo_events:
        starts = now + timedelta(minutes=start_off)
        events.append(
            Event(
                title=title,
                description=desc,
                starts_at=starts,
                ends_at=starts + timedelta(minutes=dur),
                venue=by_node[node_id],
            )
        )
    db.session.add_all(events)
    db.session.commit()

    return {"venues": len(venues), "events": len(events)}


def main() -> None:
    from . import create_app

    app = create_app()
    with app.app_context():
        result = seed()
        print(f"Seeded {result['venues']} venues and {result['events']} events.")


if __name__ == "__main__":
    main()
