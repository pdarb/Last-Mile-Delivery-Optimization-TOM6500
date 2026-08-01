"""
Last-Mile Delivery Route Optimizer
-----------------------------------
Supply Chain Digital Twin - AI/Analytics Final Project

This module simulates a regional delivery company's daily route problem:
- A depot (distribution center)
- ~18 customer delivery stops scattered around a metro area
- A "naive" route (dispatched in order received, no optimization)
- An "AI-optimized" route using Nearest-Neighbor construction + 2-opt local
  search (a genuine combinatorial optimization / AI search technique used
  in real-world routing engines)

Output: distances, time, and cost savings between naive vs optimized routes,
plus the coordinate data needed to visualize both routes on a map.
"""

import json
import math
import random

random.seed(42)

# ---------------------------------------------------------------------------
# 1. SYNTHETIC SCENARIO SETUP
#    Company: "MetroSwift Delivery" - regional last-mile courier
#    Region:  Seattle/Redmond metro area (real lat/long bounding box)
# ---------------------------------------------------------------------------

DEPOT = {"name": "MetroSwift Distribution Center", "lat": 47.6740, "lon": -122.1215}

CUSTOMER_NAMES = [
    "Riverside Cafe", "Blue Heron Apartments", "Overlake Med Plaza",
    "Cedar Park Elementary", "Willowbrook Retail", "Northgate Office Park",
    "Lakeview Condos", "Maple Grove Bakery", "Foothills Hardware",
    "Sunset Ridge HOA", "Downtown Legal Group", "Pinecrest Dental",
    "Harborview Storage", "Ridgemont Pharmacy", "Eastside Fitness Club",
    "Juniper Lane Homes", "Techview Startups Inc", "Green Valley Nursery",
]

def generate_customers(n=18):
    """Generate n synthetic customer stops within ~8km of the depot."""
    customers = []
    for i, name in enumerate(CUSTOMER_NAMES[:n]):
        # jitter around depot, roughly a realistic metro service area
        lat = DEPOT["lat"] + random.uniform(-0.045, 0.045)
        lon = DEPOT["lon"] + random.uniform(-0.06, 0.06)
        customers.append({"id": i + 1, "name": name, "lat": round(lat, 5), "lon": round(lon, 5)})
    return customers


def haversine_km(a, b):
    """Great-circle distance in km between two lat/lon points."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [a["lat"], a["lon"], b["lat"], b["lon"]])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def route_distance(route_points):
    """Total distance for an ordered list of points (depot -> stops -> depot)."""
    total = 0.0
    for i in range(len(route_points) - 1):
        total += haversine_km(route_points[i], route_points[i + 1])
    return total


# ---------------------------------------------------------------------------
# 2. NAIVE ROUTE  (dispatcher just sends driver in the order jobs came in)
# ---------------------------------------------------------------------------

def naive_route(depot, customers):
    return [depot] + customers + [depot]


# ---------------------------------------------------------------------------
# 3. AI-OPTIMIZED ROUTE
#    Step A: Nearest-Neighbor construction heuristic (greedy AI search)
#    Step B: 2-opt local search improvement (classic combinatorial
#            optimization metaheuristic - iteratively removes route
#            crossings until no improving swap remains)
# ---------------------------------------------------------------------------

def nearest_neighbor_route(depot, customers):
    unvisited = customers.copy()
    route = [depot]
    current = depot
    while unvisited:
        nxt = min(unvisited, key=lambda c: haversine_km(current, c))
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    route.append(depot)
    return route


def two_opt(route):
    """Iteratively reverse segments to remove crossing paths until no
    improving swap is found. Depot (first/last) stays fixed."""
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue
                new_route = best[:i] + best[i:j][::-1] + best[j:]
                if route_distance(new_route) < route_distance(best) - 1e-9:
                    best = new_route
                    improved = True
    return best


def ai_optimized_route(depot, customers):
    initial = nearest_neighbor_route(depot, customers)
    improved = two_opt(initial)
    return improved


# ---------------------------------------------------------------------------
# 4. BUSINESS METRICS
# ---------------------------------------------------------------------------

AVG_SPEED_KMH = 35          # average urban delivery driving speed
COST_PER_KM = 0.72          # USD - fuel + maintenance + driver time blended rate
FLEET_SIZE = 12             # trucks in the fleet, for annualized savings
WORK_DAYS_PER_YEAR = 260


def summarize(depot, customers):
    naive = naive_route(depot, customers)
    optimized = ai_optimized_route(depot, customers)

    naive_km = route_distance(naive)
    opt_km = route_distance(optimized)

    naive_hr = naive_km / AVG_SPEED_KMH
    opt_hr = opt_km / AVG_SPEED_KMH

    km_saved_per_driver_per_day = naive_km - opt_km
    pct_saved = (km_saved_per_driver_per_day / naive_km) * 100
    minutes_saved_per_driver_per_day = (naive_hr - opt_hr) * 60

    daily_fleet_savings_usd = km_saved_per_driver_per_day * COST_PER_KM * FLEET_SIZE
    annual_fleet_savings_usd = daily_fleet_savings_usd * WORK_DAYS_PER_YEAR

    return {
        "depot": depot,
        "customers": customers,
        "naive_route": naive,
        "optimized_route": optimized,
        "metrics": {
            "naive_distance_km": round(naive_km, 2),
            "optimized_distance_km": round(opt_km, 2),
            "distance_saved_km_per_driver_per_day": round(km_saved_per_driver_per_day, 2),
            "pct_distance_saved": round(pct_saved, 1),
            "naive_time_hr": round(naive_hr, 2),
            "optimized_time_hr": round(opt_hr, 2),
            "minutes_saved_per_driver_per_day": round(minutes_saved_per_driver_per_day, 1),
            "fleet_size": FLEET_SIZE,
            "daily_fleet_savings_usd": round(daily_fleet_savings_usd, 2),
            "annual_fleet_savings_usd": round(annual_fleet_savings_usd, 2),
        },
    }


if __name__ == "__main__":
    customers = generate_customers(18)
    result = summarize(DEPOT, customers)

    print(json.dumps(result["metrics"], indent=2))

    with open("route_data.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nSaved full route data to route_data.json")
