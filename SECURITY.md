# Security Policy

## Supported versions

This is a demonstration project. Security fixes are applied to the `main` branch.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, report
them privately by emailing **kostaurvish@gmail.com** with:

- a description of the issue and its impact, and
- steps to reproduce it.

You can expect an acknowledgement within a few days.

## Notes for deployers

- Serve the app over HTTPS behind a reverse proxy. On-device notifications and
  the service worker require a secure context (except on `localhost`).
- Run behind a production WSGI server (e.g. gunicorn), not the Flask
  development server.
- The app stores no personal data by default (see `docs/privacy.md`). If you add
  features that do, review them against your deployment's data-protection
  obligations.
- Restrict who can write to the events database; the current build has no
  authentication layer for content management.
