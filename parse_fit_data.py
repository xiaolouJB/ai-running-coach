"""Parse all FIT files and extract running session summaries."""
import os
import csv
import sys
from datetime import datetime, timedelta
from fitparse import FitFile

DATA_DIR = r"c:\Users\ys\Downloads\exportSportData_451872081420763137_20260505"
OUTPUT_CSV = os.path.join(DATA_DIR, "all_runs.csv")

def parse_fit(filepath):
    """Parse a single FIT file and return session summary dict(s)."""
    sessions = []
    try:
        fitfile = FitFile(filepath)
        for record in fitfile.get_messages("session"):
            data = {}
            for field in record:
                data[field.name] = field.value
            
            sport = data.get("sport", "")
            sub_sport = data.get("sub_sport", "")
            
            # We only want running / trail_running activities
            if sport not in ("running", "trail_running", "walking"):
                continue
            
            start_time = data.get("start_time")
            if start_time is None:
                continue
            
            total_distance_m = data.get("total_distance")  # meters
            total_timer_time_s = data.get("total_timer_time")  # seconds
            total_elapsed_time_s = data.get("total_elapsed_time")  # seconds
            avg_heart_rate = data.get("avg_heart_rate")
            max_heart_rate = data.get("max_heart_rate")
            avg_cadence = data.get("avg_running_cadence") or data.get("avg_cadence")
            total_ascent = data.get("total_ascent")
            total_descent = data.get("total_descent")
            total_calories = data.get("total_calories")
            avg_speed = data.get("enhanced_avg_speed") or data.get("avg_speed")  # m/s
            max_speed = data.get("enhanced_max_speed") or data.get("max_speed")
            
            # Convert distance
            dist_km = round(total_distance_m / 1000.0, 2) if total_distance_m else 0
            
            # Convert time
            timer_min = round(total_timer_time_s / 60.0, 2) if total_timer_time_s else 0
            elapsed_min = round(total_elapsed_time_s / 60.0, 2) if total_elapsed_time_s else 0
            
            # Pace (min/km)
            if avg_speed and avg_speed > 0:
                pace_sec_per_km = 1000.0 / avg_speed
                pace_min = int(pace_sec_per_km // 60)
                pace_s = int(pace_sec_per_km % 60)
                avg_pace = f"{pace_min}:{pace_s:02d}"
                avg_pace_seconds = pace_sec_per_km
            else:
                avg_pace = ""
                avg_pace_seconds = 0
            
            sessions.append({
                "filename": os.path.basename(filepath),
                "date": start_time.strftime("%Y-%m-%d") if isinstance(start_time, datetime) else str(start_time),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(start_time, datetime) else str(start_time),
                "sport": sport,
                "sub_sport": sub_sport,
                "distance_km": dist_km,
                "timer_time_min": timer_min,
                "elapsed_time_min": elapsed_min,
                "avg_pace": avg_pace,
                "avg_pace_seconds": round(avg_pace_seconds, 1),
                "avg_heart_rate": avg_heart_rate or "",
                "max_heart_rate": max_heart_rate or "",
                "avg_cadence": avg_cadence or "",
                "total_ascent": total_ascent or 0,
                "total_descent": total_descent or 0,
                "total_calories": total_calories or 0,
            })
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
    return sessions


def main():
    fit_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".fit")])
    print(f"Found {len(fit_files)} FIT files")
    
    all_sessions = []
    for i, fname in enumerate(fit_files):
        fpath = os.path.join(DATA_DIR, fname)
        sessions = parse_fit(fpath)
        all_sessions.extend(sessions)
        if (i + 1) % 50 == 0:
            print(f"  Processed {i+1}/{len(fit_files)} files, {len(all_sessions)} running sessions so far")
    
    # Sort by date
    all_sessions.sort(key=lambda x: x["start_time"])
    
    print(f"\nTotal running sessions found: {len(all_sessions)}")
    
    # Write CSV
    if all_sessions:
        fieldnames = list(all_sessions[0].keys())
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_sessions)
        print(f"Wrote CSV to {OUTPUT_CSV}")
    
    # Print summary stats
    if all_sessions:
        dates = [s["date"] for s in all_sessions]
        print(f"\nDate range: {min(dates)} to {max(dates)}")
        total_dist = sum(s["distance_km"] for s in all_sessions)
        print(f"Total distance: {total_dist:.1f} km across {len(all_sessions)} sessions")
        
        # Monthly summary
        from collections import defaultdict
        monthly = defaultdict(lambda: {"count": 0, "distance": 0})
        for s in all_sessions:
            month = s["date"][:7]  # YYYY-MM
            monthly[month]["count"] += 1
            monthly[month]["distance"] += s["distance_km"]
        
        print("\n=== Monthly Summary ===")
        for month in sorted(monthly.keys()):
            m = monthly[month]
            print(f"  {month}: {m['count']:3d} runs, {m['distance']:7.1f} km")
        
        # Find longest runs (potential races)
        long_runs = sorted(all_sessions, key=lambda x: x["distance_km"], reverse=True)[:20]
        print("\n=== Top 20 Longest Runs ===")
        for r in long_runs:
            # Format time as HH:MM:SS
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Find fastest runs (by pace, min 5km)
        qualified = [s for s in all_sessions if s["distance_km"] >= 5 and s["avg_pace_seconds"] > 0]
        fast_runs = sorted(qualified, key=lambda x: x["avg_pace_seconds"])[:20]
        print("\n=== Top 20 Fastest Runs (>= 5km) ===")
        for r in fast_runs:
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Recent month data (last 30 days)
        from datetime import date
        today = date(2026, 5, 5)
        last_30 = [s for s in all_sessions if (today - datetime.strptime(s["date"], "%Y-%m-%d").date()).days <= 30]
        print(f"\n=== Last 30 Days ({len(last_30)} runs) ===")
        for r in last_30:
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Last 90 days
        last_90 = [s for s in all_sessions if (today - datetime.strptime(s["date"], "%Y-%m-%d").date()).days <= 90]
        total_90 = sum(s["distance_km"] for s in last_90)
        print(f"\n=== Last 90 Days: {len(last_90)} runs, {total_90:.1f} km ===")
        
        # Races / key performances: half marathon distance (20-22km)
        half_marathons = [s for s in all_sessions if 20.0 <= s["distance_km"] <= 22.5]
        print(f"\n=== Half Marathon Distance Runs ({len(half_marathons)}) ===")
        for r in sorted(half_marathons, key=lambda x: x["timer_time_min"]):
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Full marathon distance (40-44km)
        full_marathons = [s for s in all_sessions if 40.0 <= s["distance_km"] <= 44.0]
        print(f"\n=== Full Marathon Distance Runs ({len(full_marathons)}) ===")
        for r in sorted(full_marathons, key=lambda x: x["timer_time_min"]):
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")

        # 10K-ish runs (9.5-10.5km)
        ten_k_runs = [s for s in all_sessions if 9.5 <= s["distance_km"] <= 10.5]
        print(f"\n=== 10K Distance Runs ({len(ten_k_runs)}) - Top 10 fastest ===")
        for r in sorted(ten_k_runs, key=lambda x: x["avg_pace_seconds"])[:10]:
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")

        # 5K-ish runs (4.5-5.5km)
        five_k_runs = [s for s in all_sessions if 4.5 <= s["distance_km"] <= 5.5]
        print(f"\n=== 5K Distance Runs ({len(five_k_runs)}) - Top 10 fastest ===")
        for r in sorted(five_k_runs, key=lambda x: x["avg_pace_seconds"])[:10]:
            total_sec = r["timer_time_min"] * 60
            h = int(total_sec // 3600)
            m = int((total_sec % 3600) // 60)
            s = int(total_sec % 60)
            time_str = f"{h}:{m:02d}:{s:02d}"
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {time_str} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")


if __name__ == "__main__":
    main()
