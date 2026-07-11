# Architecture

Campus Locus is a small client–server web application. A single Flask process
serves both the captive-portal landing page and a JSON API; the browser renders
an interactive map and polls the API for live data.

## System overview

```mermaid
flowchart LR
    subgraph Device["User device (browser)"]
        UI["Portal page<br/>Leaflet map + event board"]
        SW["Service worker<br/>(cache + notifications)"]
    end

    subgraph Gateway["Wi-Fi gateway"]
        CP["Captive-portal redirect"]
    end

    subgraph Server["Campus Locus server (Flask)"]
        API["REST API"]
        WF["Wayfinding<br/>(Dijkstra over campus graph)"]
        DB[("SQLite<br/>venues + events")]
    end

    Device -- "joins network" --> CP
    CP -- "302 redirect" --> UI
    UI -- "GET /api/*" --> API
    API --> DB
    API --> WF
    SW -. "showNotification()" .-> UI
```

The captive-portal redirect is a deployment concern handled by the network
gateway (or the local simulation in [`portal-sim/`](../portal-sim)). The
application itself does not depend on it and runs fully from `flask run`.

## Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| App factory | `backend/app/__init__.py` | Wires Flask, database, CORS, and static serving |
| Models | `backend/app/models.py` | `Venue` and `Event`, plus live/upcoming/ended status logic |
| Campus graph | `backend/app/campus.py` | Node/edge graph and Dijkstra shortest-path |
| REST API | `backend/app/api.py` | Endpoints for campus, venues, events, routes |
| Seed | `backend/app/seed.py` | Fictional campus + time-relative demo events |
| Portal UI | `frontend/` | Landing page, Leaflet map, event board, notifications |
| Service worker | `frontend/sw.js` | App-shell cache and notification surface |

## Request lifecycle: "Navigate to a venue"

```mermaid
sequenceDiagram
    participant U as User
    participant P as Portal page
    participant A as REST API
    participant G as Campus graph

    U->>P: Tap "Navigate" on an event
    P->>A: GET /api/route?to={venue}&from=gate
    A->>G: shortest_path(gate, venue_node)
    G-->>A: ordered waypoints + distance
    A-->>P: JSON { waypoints, distance_m }
    P->>P: Draw polyline on the map, fit bounds
    P-->>U: Route shown + distance in toast
```

## Notification flow: "event starting soon"

```mermaid
sequenceDiagram
    participant P as Portal page
    participant A as REST API
    participant SW as Service worker

    loop every 30s
        P->>A: GET /api/events/starting-soon
        A-->>P: events within the lead window (default 15 min)
    end
    alt new event not yet alerted
        P->>SW: showNotification(title, body)
        SW-->>P: on-device notification
        P->>P: in-page toast (fallback)
    end
```

## Data model

```mermaid
erDiagram
    VENUE ||--o{ EVENT : hosts
    VENUE {
        int id PK
        string name
        string category
        string description
        string node_id "maps to campus graph node"
    }
    EVENT {
        int id PK
        string title
        string description
        datetime starts_at
        datetime ends_at
        int venue_id FK
    }
```

`Venue.node_id` is the join between the relational data and the campus graph:
each venue names the graph node it sits on, which is what wayfinding routes to.

## Design decisions

- **One process serves page + API.** Simpler to run and to deploy on a gateway;
  no separate frontend build step or server.
- **Planar coordinates, not GPS.** The campus is a schematic graph in local
  metres rendered with Leaflet's simple CRS. The honest capability is
  map-based wayfinding from the gate to a venue — not satellite or indoor
  positioning.
- **Time-relative seed data.** Demo events are seeded relative to "now" so the
  app always has something live and something upcoming, keeping the demo
  reproducible.
- **Polling, not server push (for now).** Notifications are triggered by
  client-side polling of `/events/starting-soon`. Full server-initiated Web
  Push is on the [roadmap](../README.md#roadmap).
