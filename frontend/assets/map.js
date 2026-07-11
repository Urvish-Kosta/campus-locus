/* map.js — campus map rendering with Leaflet on a simple (non-geographic) CRS.
 *
 * The backend serves campus geometry in a local planar coordinate system
 * (metres). We render it with L.CRS.Simple, so there is no pretence of real
 * GPS positioning — this is a schematic campus map with map-based wayfinding.
 */

const CampusMap = (() => {
  let map;
  let nodeLatLng = {};        // node_id -> [lat, lng] in CRS.Simple space
  let markerLayer, edgeLayer, routeLayer;
  let onVenueClick = () => {};

  // Convert backend (x, y) metres to CRS.Simple [lat, lng].
  // In CRS.Simple, y grows downward, so we negate y to keep "up" as up.
  const toLatLng = (x, y) => [-y, x];

  function init(campus, handlers = {}) {
    onVenueClick = handlers.onVenueClick || onVenueClick;

    const xs = campus.nodes.map((n) => n.x);
    const ys = campus.nodes.map((n) => n.y);
    const pad = 80;
    const bounds = [
      toLatLng(Math.min(...xs) - pad, Math.max(...ys) + pad),
      toLatLng(Math.max(...xs) + pad, Math.min(...ys) - pad),
    ];

    map = L.map("map", {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 2,
      zoomControl: true,
      attributionControl: false,
    });
    map.fitBounds(bounds);

    edgeLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    markerLayer = L.layerGroup().addTo(map);

    nodeLatLng = {};
    campus.nodes.forEach((n) => {
      nodeLatLng[n.id] = toLatLng(n.x, n.y);
    });

    drawEdges(campus.edges);
    return map;
  }

  function drawEdges(edges) {
    edges.forEach((e) => {
      L.polyline([nodeLatLng[e.a], nodeLatLng[e.b]], {
        color: "#33456b",
        weight: 3,
        opacity: 0.9,
      }).addTo(edgeLayer);
    });
  }

  // Build a Leaflet divIcon for a node given its role.
  function icon(kind, label) {
    return L.divIcon({
      className: "",
      html: `<div class="marker marker--${kind}">
               <div class="marker__dot"></div>
               ${label ? `<div class="marker__label">${label}</div>` : ""}
             </div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    });
  }

  /* Render markers. `venues` maps node_id -> {venue, status}. Gate is always
   * shown; venues get a status-coloured marker and a click handler. */
  function renderMarkers(campus, venueStatus) {
    markerLayer.clearLayers();
    campus.nodes.forEach((n) => {
      if (n.kind === "gate") {
        L.marker(nodeLatLng[n.id], { icon: icon("gate", "Gate") }).addTo(markerLayer);
        return;
      }
      if (n.kind !== "venue") return;

      const info = venueStatus[n.id];
      const kind = info ? info.status : "idle";
      const marker = L.marker(nodeLatLng[n.id], {
        icon: icon(kind === "live" ? "live" : kind === "upcoming" ? "soon" : "idle", n.name),
      }).addTo(markerLayer);

      if (info) {
        marker.on("click", () => onVenueClick(info.venue));
      }
    });
  }

  // Draw a route as an ordered list of waypoint objects ({x, y, ...}).
  function drawRoute(waypoints) {
    routeLayer.clearLayers();
    const line = waypoints.map((w) => toLatLng(w.x, w.y));
    L.polyline(line, {
      color: "#2e7cf6",
      weight: 5,
      opacity: 0.95,
      dashArray: "1 9",
      lineCap: "round",
    }).addTo(routeLayer);
    // A crisp underlay so the dashed route reads clearly on the dark map.
    L.polyline(line, { color: "#0e1b31", weight: 8, opacity: 0.5 }).addTo(routeLayer).bringToBack();
    map.fitBounds(L.polyline(line).getBounds(), { padding: [40, 40] });
  }

  function clearRoute() {
    routeLayer.clearLayers();
  }

  return { init, renderMarkers, drawRoute, clearRoute };
})();
