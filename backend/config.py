"""Application configuration.

Configuration is environment-driven so the same codebase runs unchanged in
local development, CI, and a deployed captive-portal gateway.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration shared by all environments."""

    # How soon before an event's start time a "starting soon" notification
    # should be surfaced to a connected device, in minutes.
    NOTIFY_LEAD_MINUTES = int(os.environ.get("NOTIFY_LEAD_MINUTES", "15"))

    # An event is considered "live" from its start until this many minutes
    # after it ends, so late arrivals still see it on the map.
    LIVE_GRACE_MINUTES = int(os.environ.get("LIVE_GRACE_MINUTES", "0"))

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'campus_locus.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


class TestingConfig(Config):
    """In-memory database for fast, isolated tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
