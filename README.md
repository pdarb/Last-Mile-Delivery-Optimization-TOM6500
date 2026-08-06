# TOM 6500 Final Project
### AI-Powered Last-Mile Delivery Route Optimizer — Supply Chain Digital Twin

A proof-of-concept that shows how classical AI search algorithms (nearest-neighbor + 2-opt),
a vehicle routing heuristic (sweep clustering), and an LLM reasoning layer (Claude) can
optimize a delivery fleet's daily routes — with a live, interactive dashboard to demonstrate it.

## What's in this repo

```
metroswift-route-optimizer/
├── dashboard/
│   ├── fleet_dashboard.html        ← main deliverable: interactive multi-driver dashboard
│   └── single_driver_dashboard.html  ← earlier single-driver version
├── python/
│   └── route_optimizer.py         ← standalone Python implementation (single-driver)
├── data/
│   └── route_data.json            ← sample generated route data (from the Python script)
└── README.md
```

## Quick start

**Dashboard (no install needed):**
Just open `dashboard/fleet_dashboard.html` in any modern browser. Everything runs client-side.

> Note: the "AI Dispatch Console" feature calls the Anthropic API directly from the browser
> (`https://api.anthropic.com/v1/messages`). Outside of Claude.ai's artifact environment,
> this call will need your own Anthropic API key wired in, or it can be removed/stubbed out
> for a purely static demo.

**Python script:**
```bash
cd python
python3 route_optimizer.py
```
This generates synthetic delivery stops, runs the optimizer, prints the resulting metrics,
and writes `route_data.json`.

## Architecture

**No backend.** This is a fully client-side, single-file web app (HTML + CSS + vanilla JS).
No server, no database, no build step. Everything — data, algorithms, rendering, and state —
runs in the browser.

- **Frontend:** Vanilla JavaScript + native SVG (no React/Vue/D3/Tailwind). A single `render()`
  function recomputes routes and redraws the SVG map on every state change (add/remove a stop,
  change driver count, adjust cost assumptions).
- **Styling:** Plain CSS with custom properties. Fonts: Space Grotesk (display), Inter (body),
  IBM Plex Mono (data/labels), via Google Fonts.

## Algorithms used

| Component | Technique | Category |
|---|---|---|
| Distance calculation | Haversine formula | Geospatial math |
| Route construction | Nearest-neighbor heuristic | Classical AI / greedy search |
| Route improvement | 2-opt local search | Combinatorial optimization / metaheuristic |
| Fleet assignment (multi-driver) | Sweep (angle-based) clustering | VRP heuristic — cluster-first, route-second |
| Constraint interpretation & explanation | Gemini (LLM) via Gemini Studio API | Generative AI / natural language reasoning |

**Important distinction:** the routing/optimization layer is classical operations-research
search (no training data, no model weights, no neural network) — legitimately "AI" in the
search/optimization sense, but not machine learning. The one place a trained model is actually
involved is the AI Dispatch Console, which calls Gemini to interpret
natural-language questions/constraints and explain the current plan in plain English. It does
**not** re-run the optimizer — it reasons qualitatively about the live route data passed to it
as context.

## How the fleet split works

1. **Naive baseline ("Before"):** the stop list is divided into N equal-sized contiguous chunks
   in whatever order they were entered — no geographic or routing logic. Approximates an
   unassisted dispatcher manually dividing a job list.
2. **AI-optimized ("After"):** stops are sorted by compass angle from the depot and split into
   N contiguous "pie slice" zones (one per driver) — the sweep heuristic. Each driver's zone is
   then routed independently using nearest-neighbor construction followed by 2-opt improvement.

## Data

All delivery stops are **synthetic** — randomly generated coordinates within a realistic radius
of a simulated distribution center in the Seattle/Redmond metro area, with placeholder business
names. This is a proof-of-concept design choice (no real customer or company data), not a data
quality limitation — real GPS/order data could be substituted directly since the algorithms are
data-shape agnostic.

## Assumptions used in cost/time calculations

- Average urban delivery driving speed: 35 km/h
- Blended cost per km (fuel + maintenance + driver time): $0.72
- Working days per year: 260
- All adjustable live in the dashboard's Fleet Parameters panel.

## Limitations & possible extensions

- Sweep clustering doesn't balance workload by *distance*, only by stop count — a driver whose
  zone is geographically larger can end up with a longer route than others.
- No real-time traffic, time windows, vehicle capacity, or delivery priority constraints are
  modeled in the optimizer itself (the LLM layer can *discuss* these qualitatively but doesn't
  feed them back into the algorithm).
- A production version would likely use a proper VRP solver (e.g., Google OR-Tools) with hard
  constraints, real road-network distances (not straight-line/Haversine), and live traffic data.

## License

Class project — MIT License, free to reuse/adapt.
