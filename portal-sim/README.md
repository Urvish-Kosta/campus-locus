# Captive-portal simulation

A real captive portal works at the network layer: the gateway intercepts a new
client's first HTTP request and redirects it to the portal page. You don't need
that hardware to run Campus Locus — the app serves its own landing page — but
this folder shows *how the redirect behaves*, so the captive-portal flow can be
demonstrated and tested locally.

`captive_gateway.py` is a tiny standalone HTTP server that imitates the gateway:

- It answers the OS connectivity-check URLs that phones and laptops probe when
  they join a network (e.g. Apple's `/hotspot-detect.html`, Android's
  `/generate_204`, Windows' `/connecttest.txt`).
- Instead of returning "you're online", it returns a redirect to the portal,
  which is exactly what makes the OS pop up the "Sign in to network" sheet.

## Run

```bash
# 1. Start the main app (serves the portal at :5000)
cd ../backend && flask --app wsgi run

# 2. In another terminal, start the simulated gateway
python captive_gateway.py --portal http://localhost:5000/
```

Then request a connectivity-check URL and watch it redirect:

```bash
curl -si http://localhost:8080/generate_204 | head -n 5
curl -si http://localhost:8080/hotspot-detect.html | head -n 5
```

For real deployment on OpenWRT / pfSense / CoovaChilli, see
[`../docs/captive-portal.md`](../docs/captive-portal.md).
