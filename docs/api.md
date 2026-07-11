# API reference

Base URL (local): `http://localhost:5000/api`

All responses are JSON. Times are ISO 8601 with UTC offset.

---

### `GET /api/health`

Liveness probe.

```json
{ "status": "ok", "time": "2025-05-01T09:30:00+00:00" }
```

---

### `GET /api/campus`

Campus geometry for map rendering: nodes (in local metres) and the footpath
edges between them.

```json
{
  "nodes": [
    { "id": "gate", "name": "Main Gate", "x": 0, "y": 0, "kind": "gate" },
    { "id": "library", "name": "Central Library", "x": 300, "y": 20, "kind": "venue" }
  ],
  "edges": [
    { "a": "gate", "b": "plaza", "distance_m": 120.0 }
  ]
}
```

`kind` is one of `gate`, `junction`, `venue`.

---

### `GET /api/venues`

All venues, ordered by name.

```json
{
  "venues": [
    {
      "id": 1,
      "name": "Auditorium",
      "category": "hall",
      "description": "Main 600-seat auditorium for talks and ceremonies.",
      "node_id": "auditorium"
    }
  ]
}
```

---

### `GET /api/events`

Query parameters:

| Param | Values | Default | Meaning |
|-------|--------|---------|---------|
| `status` | `live`, `upcoming`, `ended`, `all` | `all` | Filter by computed status |

```json
{
  "events": [
    {
      "id": 2,
      "title": "Embedded Systems Open Lab",
      "description": "Walk-in demos of student FPGA and IoT projects.",
      "starts_at": "2025-05-01T10:00:00+00:00",
      "ends_at": "2025-05-01T12:00:00+00:00",
      "status": "upcoming",
      "venue": { "id": 3, "name": "Engineering Labs", "node_id": "labs", "...": "" }
    }
  ]
}
```

Status is computed server-side from `starts_at` / `ends_at` against the current
time.

---

### `GET /api/events/starting-soon`

Events whose start falls within the notification lead window
(`NOTIFY_LEAD_MINUTES`, default 15). This is the data source for the on-device
"event starting" alert.

```json
{
  "lead_minutes": 15,
  "events": [ { "id": 2, "title": "Embedded Systems Open Lab", "...": "" } ]
}
```

---

### `GET /api/route`

Shortest walking route from a start node to a venue, via Dijkstra's algorithm
over the campus graph.

Query parameters:

| Param | Type | Default | Meaning |
|-------|------|---------|---------|
| `to` | int (venue id) | — (required) | Destination venue |
| `from` | string (node id) | `gate` | Start node |

```json
{
  "from": "gate",
  "to": "labs",
  "distance_m": 420.6,
  "waypoints": [
    { "id": "gate", "name": "Main Gate", "x": 0, "y": 0, "kind": "gate" },
    { "id": "plaza", "name": "Central Plaza", "x": 120, "y": 0, "kind": "junction" },
    { "id": "library", "name": "Central Library", "x": 300, "y": 20, "kind": "venue" },
    { "id": "labs", "name": "Engineering Labs", "x": 310, "y": -110, "kind": "venue" }
  ],
  "venue": { "id": 3, "name": "Engineering Labs", "node_id": "labs", "...": "" }
}
```

Errors: `400` if `to` is missing or a node is unknown, `404` if the venue does
not exist, `422` if no route connects the endpoints.
