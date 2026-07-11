/* app.js — portal application logic.
 *
 * Responsibilities:
 *   - load campus geometry + events from the API
 *   - render the live/upcoming event board
 *   - draw wayfinding routes when a user picks "Navigate"
 *   - poll for "starting soon" events and raise an on-device notification
 *
 * No build step: plain ES modules-free browser JS, so the repo runs by
 * simply opening the served page.
 */

const API = "/api";
const POLL_MS = 30000;          // how often to check for starting-soon events
const notified = new Set();     // event ids we've already alerted for

const els = {
  list: document.getElementById("event-list"),
  clearRoute: document.getElementById("clear-route"),
  notifyToggle: document.getElementById("notify-toggle"),
  toast: document.getElementById("toast"),
  toastTitle: document.getElementById("toast-title"),
  toastText: document.getElementById("toast-text"),
  toastClose: document.getElementById("toast-close"),
};

let campus = null;
let activeVenueId = null;

async function getJSON(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* Map current events to per-venue status for the map markers.
   A venue showing a live event outranks one that is merely upcoming. */
function venueStatusFromEvents(events) {
  const rank = { live: 2, upcoming: 1 };
  const byNode = {};
  events.forEach((e) => {
    if (!e.venue || e.status === "ended") return;
    const node = e.venue.node_id;
    const current = byNode[node];
    if (!current || (rank[e.status] || 0) > (rank[current.status] || 0)) {
      byNode[node] = { venue: e.venue, status: e.status };
    }
  });
  return byNode;
}

function renderEvents(events) {
  const shown = events.filter((e) => e.status !== "ended");
  if (shown.length === 0) {
    els.list.innerHTML = `<li class="event-empty">No live or upcoming events right now.</li>`;
    return;
  }

  els.list.innerHTML = "";
  shown.forEach((e) => {
    const li = document.createElement("li");
    li.className = `event event--${e.status}`;
    const tagClass = e.status === "live" ? "tag--live" : "tag--upcoming";
    const tagText = e.status === "live" ? "Live" : "Upcoming";

    li.innerHTML = `
      <span class="event__rail" aria-hidden="true"></span>
      <div class="event__main">
        <p class="event__title">${escapeHtml(e.title)}</p>
        <div class="event__meta">
          <span class="tag ${tagClass}">${tagText}</span>
          <span class="event__venue">${escapeHtml(e.venue ? e.venue.name : "—")}</span>
          <span class="event__time">${fmtTime(e.starts_at)}–${fmtTime(e.ends_at)}</span>
        </div>
      </div>
      <button class="nav-btn" type="button" data-venue="${e.venue ? e.venue.id : ""}">
        Navigate
      </button>`;
    els.list.appendChild(li);
  });

  els.list.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => navigateTo(Number(btn.dataset.venue)));
  });
}

async function navigateTo(venueId) {
  if (!venueId) return;
  try {
    const route = await getJSON(`/route?to=${venueId}&from=gate`);
    CampusMap.drawRoute(route.waypoints);
    activeVenueId = venueId;
    els.clearRoute.hidden = false;
    highlightActive();
    showToast("Route ready", `${route.venue.name} · ${route.distance_m} m from the Main Gate.`);
  } catch (err) {
    showToast("Couldn't build route", "Please try again in a moment.");
  }
}

function highlightActive() {
  els.list.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.dataset.active = String(Number(btn.dataset.venue) === activeVenueId);
  });
}

function clearActiveRoute() {
  CampusMap.clearRoute();
  activeVenueId = null;
  els.clearRoute.hidden = true;
  highlightActive();
}

/* --- On-device notifications ------------------------------------------- */

async function enableNotifications() {
  if (!("Notification" in window)) {
    showToast("Not supported", "This browser can't show device notifications.");
    return;
  }
  const permission = await Notification.requestPermission();
  if (permission === "granted") {
    els.notifyToggle.dataset.state = "on";
    els.notifyToggle.textContent = "Notifications on";
    showToast("Notifications on", "We'll alert you when an event is about to start.");
  } else {
    showToast("Notifications blocked", "Enable them in your browser settings to get alerts.");
  }
}

async function checkStartingSoon() {
  try {
    const data = await getJSON("/events/starting-soon");
    data.events.forEach((e) => {
      if (notified.has(e.id)) return;
      notified.add(e.id);
      raiseAlert(e);
    });
  } catch (_) {
    /* transient network errors are non-fatal for polling */
  }
}

function raiseAlert(event) {
  const title = "Starting soon on campus";
  const body = `${event.title} · ${event.venue ? event.venue.name : ""} at ${fmtTime(event.starts_at)}`;

  // Prefer a real device notification via the Service Worker if allowed.
  if ("Notification" in window && Notification.permission === "granted") {
    navigator.serviceWorker?.ready
      .then((reg) => reg.showNotification(title, {
        body,
        tag: `event-${event.id}`,
        icon: "/icons/icon-192.png",
        badge: "/icons/icon-192.png",
      }))
      .catch(() => new Notification(title, { body }));
  }
  // Always show the in-page toast so the alert is visible in captive-portal
  // browsers that restrict notifications.
  showToast(title, body);
}

/* --- Toast ------------------------------------------------------------- */

let toastTimer = null;
function showToast(title, text) {
  els.toastTitle.textContent = title;
  els.toastText.textContent = text;
  els.toast.hidden = false;
  requestAnimationFrame(() => (els.toast.dataset.show = "true"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(hideToast, 6000);
}
function hideToast() {
  els.toast.dataset.show = "false";
  setTimeout(() => (els.toast.hidden = true), 220);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* --- Boot -------------------------------------------------------------- */

async function refreshEvents() {
  const { events } = await getJSON("/events?status=all");
  renderEvents(events);
  CampusMap.renderMarkers(campus, venueStatusFromEvents(events));
  highlightActive();
}

async function boot() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }

  els.clearRoute.addEventListener("click", clearActiveRoute);
  els.notifyToggle.addEventListener("click", enableNotifications);
  els.toastClose.addEventListener("click", hideToast);

  try {
    campus = await getJSON("/campus");
    CampusMap.init(campus, { onVenueClick: (venue) => navigateTo(venue.id) });
    await refreshEvents();
    await checkStartingSoon();
  } catch (err) {
    els.list.innerHTML = `<li class="event-empty">Couldn't reach the campus service. Is the backend running?</li>`;
    return;
  }

  // Keep the board and notifications current.
  setInterval(refreshEvents, POLL_MS);
  setInterval(checkStartingSoon, POLL_MS);
}

document.addEventListener("DOMContentLoaded", boot);
