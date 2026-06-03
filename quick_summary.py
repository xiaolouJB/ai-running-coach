import csv
from collections import defaultdict

with open("all_runs.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total sessions: {len(rows)}")

monthly = defaultdict(lambda: {"count": 0, "distance": 0})
for s in rows:
    month = s["date"][:7]
    monthly[month]["count"] += 1
    monthly[month]["distance"] += float(s["distance_km"])

print("\n=== Complete Monthly Summary ===")
for month in sorted(monthly.keys()):
    m = monthly[month]
    print(f"  {month}: {m['count']:3d} runs, {m['distance']:7.1f} km")

yearly = defaultdict(lambda: {"count": 0, "distance": 0})
for s in rows:
    year = s["date"][:4]
    yearly[year]["count"] += 1
    yearly[year]["distance"] += float(s["distance_km"])
print("\n=== Yearly Summary ===")
for year in sorted(yearly.keys()):
    y = yearly[year]
    print(f"  {year}: {y['count']:3d} runs, {y['distance']:7.1f} km")
