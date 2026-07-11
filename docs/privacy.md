# Privacy &amp; data handling

Location plus notifications is a privacy-sensitive combination, so the design
takes a deliberately conservative stance. This document states what the system
does and does not do with user data.

## What the system collects

**Nothing personal.** In its current form Campus Locus stores only campus data
(venues and events). It does not have user accounts, does not store device
identifiers, and does not log who requested a route or viewed an event.

## Location

- The app does **not** read the device's GPS or physical location.
- Wayfinding routes are computed from a **fixed, known start point** (the campus
  gate) to a venue the user chooses. The user's real position is never sensed,
  transmitted, or stored.
- The "location-aware" property comes from *context* — the user is on the campus
  guest network — not from tracking an individual.

## Notifications

- On-device notifications are **opt-in**. The browser only shows them after the
  user taps "Notify me" and grants permission, which can be revoked at any time
  in browser settings.
- Notification triggers are computed from public event schedules, not from any
  per-user data. Every connected device that opts in sees the same campus-wide
  alerts.

## Data retention

- Event and venue data lives in a local SQLite database controlled by the
  operator. There is no per-user data to retain.

## Principles carried into any future work

If features that touch personal data are added (for example saved favourites or
true device location), they should preserve these properties:

- **Opt-in, not opt-out** for anything involving the device or a person.
- **Data minimisation** — collect only what a feature genuinely needs.
- **No silent tracking** — no analytics that identify individuals across visits
  without clear, revocable consent.
- **Transparency** — document what is collected and why, in plain language.

> This document describes the design intent of this repository. It is not legal
> advice; any real deployment on a campus network should be reviewed against the
> institution's own data-protection obligations (e.g. GDPR where applicable).
