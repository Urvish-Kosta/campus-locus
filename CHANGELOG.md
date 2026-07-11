# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Added
- Flask backend with an app factory, SQLite storage, and CORS.
- `Venue` and `Event` models with server-computed live / upcoming / ended status.
- Campus wayfinding graph with Dijkstra shortest-path routing.
- REST API: campus geometry, venues, events (with status filter), starting-soon,
  and route endpoints.
- Time-relative seed data for a fictional campus.
- Captive-portal frontend: Leaflet map, live event board, one-tap wayfinding,
  and opt-in on-device notifications with an in-page fallback.
- Service worker and web app manifest (installable PWA).
- Local captive-portal redirect simulation (`portal-sim/`).
- pytest suite covering the API and the wayfinding algorithm.
- GitHub Actions CI across Python 3.10–3.12.
- Documentation: architecture, API reference, captive-portal deployment, privacy.

[Unreleased]: https://github.com/Urvish-Kosta/campus-locus/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Urvish-Kosta/campus-locus/releases/tag/v0.1.0
