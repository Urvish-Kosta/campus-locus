"""Campus map model and wayfinding.

The campus is represented as an undirected weighted graph in a local planar
coordinate system (metres), rendered on the client with Leaflet's simple
(non-geographic) CRS. This deliberately avoids real GPS coordinates: the
system provides map-based wayfinding from a known entry point to a chosen
venue, not satellite or indoor positioning.

Edge weights are the straight-line distance between the two nodes, so the
shortest path returned by Dijkstra's algorithm is the shortest walkable
route along the defined footpaths.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    x: float  # metres, local grid
    y: float  # metres, local grid
    kind: str = "waypoint"  # gate | junction | venue

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "x": self.x, "y": self.y, "kind": self.kind}


@dataclass
class CampusGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    # adjacency: node_id -> list of (neighbour_id, distance)
    adj: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node
        self.adj.setdefault(node.id, [])

    def add_edge(self, a: str, b: str) -> None:
        if a not in self.nodes or b not in self.nodes:
            raise KeyError(f"cannot connect unknown nodes: {a!r}, {b!r}")
        dist = self._distance(a, b)
        self.adj[a].append((b, dist))
        self.adj[b].append((a, dist))

    def _distance(self, a: str, b: str) -> float:
        na, nb = self.nodes[a], self.nodes[b]
        return math.hypot(na.x - nb.x, na.y - nb.y)

    def shortest_path(self, start: str, goal: str) -> tuple[list[str], float]:
        """Return (ordered node ids, total distance) via Dijkstra's algorithm.

        Raises KeyError for unknown endpoints and ValueError if no route
        exists between them.
        """
        if start not in self.nodes:
            raise KeyError(f"unknown start node: {start!r}")
        if goal not in self.nodes:
            raise KeyError(f"unknown goal node: {goal!r}")

        dist: dict[str, float] = {start: 0.0}
        prev: dict[str, str] = {}
        pq: list[tuple[float, str]] = [(0.0, start)]
        visited: set[str] = set()

        while pq:
            d, node = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            if node == goal:
                break
            for neighbour, weight in self.adj[node]:
                if neighbour in visited:
                    continue
                nd = d + weight
                if nd < dist.get(neighbour, math.inf):
                    dist[neighbour] = nd
                    prev[neighbour] = node
                    heapq.heappush(pq, (nd, neighbour))

        if goal not in dist:
            raise ValueError(f"no route between {start!r} and {goal!r}")

        path = [goal]
        while path[-1] != start:
            path.append(prev[path[-1]])
        path.reverse()
        return path, dist[goal]

    def route_dict(self, start: str, goal: str) -> dict:
        path, total = self.shortest_path(start, goal)
        return {
            "from": start,
            "to": goal,
            "distance_m": round(total, 1),
            "waypoints": [self.nodes[nid].to_dict() for nid in path],
        }


def build_default_campus() -> CampusGraph:
    """A small fictional campus used for the demo and tests.

    Layout (not to scale)::

        GATE ── PLAZA ──── LIBRARY
                  │           │
               AUDITORIUM   LABS
                  │           │
                SPORTS ──── CAFETERIA

    The layout is invented; it is not a map of any real institution.
    """
    g = CampusGraph()
    nodes = [
        Node("gate", "Main Gate", 0, 0, kind="gate"),
        Node("plaza", "Central Plaza", 120, 0, kind="junction"),
        Node("library", "Central Library", 300, 20, kind="venue"),
        Node("auditorium", "Auditorium", 130, -120, kind="venue"),
        Node("labs", "Engineering Labs", 310, -110, kind="venue"),
        Node("sports", "Sports Complex", 140, -240, kind="venue"),
        Node("cafeteria", "Cafeteria", 320, -240, kind="venue"),
    ]
    for n in nodes:
        g.add_node(n)

    edges = [
        ("gate", "plaza"),
        ("plaza", "library"),
        ("plaza", "auditorium"),
        ("library", "labs"),
        ("auditorium", "sports"),
        ("labs", "cafeteria"),
        ("sports", "cafeteria"),
    ]
    for a, b in edges:
        g.add_edge(a, b)
    return g
