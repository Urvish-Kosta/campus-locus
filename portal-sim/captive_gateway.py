#!/usr/bin/env python3
"""Simulated captive-portal gateway.

Imitates the redirect behaviour of a Wi-Fi captive portal without any network
hardware. Operating systems probe well-known URLs to decide whether a network
needs sign-in; a captive portal answers those probes with a redirect to the
portal page, which triggers the familiar "Sign in to network" prompt.

This is a demonstration/testing aid, not a production gateway. Real deployments
enforce the redirect at the router (see docs/captive-portal.md).

Usage::

    python captive_gateway.py --portal http://localhost:5000/ --port 8080
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# URLs that common operating systems request to detect a captive portal.
CONNECTIVITY_CHECKS = {
    "/generate_204",          # Android
    "/gen_204",               # Android (alt)
    "/hotspot-detect.html",   # iOS / macOS
    "/library/test/success.html",  # iOS (alt)
    "/connecttest.txt",       # Windows
    "/ncsi.txt",              # Windows (alt)
    "/canonical.html",        # Ubuntu / NetworkManager
}


def make_handler(portal_url: str):
    class CaptiveHandler(BaseHTTPRequestHandler):
        server_version = "CampusLocusCaptiveSim/1.0"

        def do_GET(self):  # noqa: N802 (http.server naming)
            # Any probe (or indeed any path) is redirected to the portal,
            # which is what a captive gateway does for unauthenticated clients.
            self.send_response(302)
            self.send_header("Location", portal_url)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            probe = " (connectivity check)" if self.path in CONNECTIVITY_CHECKS else ""
            self.wfile.write(
                f"Redirecting to captive portal: {portal_url}\n".encode()
            )
            self.log_message("redirect %s%s -> %s", self.path, probe, portal_url)

        def log_message(self, fmt, *args):
            print("[gateway]", fmt % args)

    return CaptiveHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulated captive-portal gateway")
    parser.add_argument("--portal", default="http://localhost:5000/",
                        help="URL of the portal landing page to redirect to")
    parser.add_argument("--port", type=int, default=8080, help="port to listen on")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(args.portal))
    print(f"Captive-portal gateway on http://localhost:{args.port}")
    print(f"Redirecting all requests to: {args.portal}")
    print("Try:  curl -si http://localhost:%d/generate_204" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping gateway")
        server.shutdown()


if __name__ == "__main__":
    main()
