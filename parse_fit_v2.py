"""Parse all FIT files using garmin-fit-sdk and extract running session summaries."""
import os
import csv
import sys
from datetime import datetime, timedelta, date
from collections import defaultdict

from garmin_fit_sdk import Decoder, Stream

DATA_DIR = r"c:\Users\ys\Downloads\exportSportData_451872081420763137_20260505"
OUTPUT_CSV = os.path.join(DATA_DIR, "all_runs.csv")

# Garmin epoch starts 1989-12-31
GARMIN_EPOCH = datetime(1989, 12, 31, 0, 0, 0)

def parse_fit(filepath):
    """Parse a single FIT file using garmin-fit-sdk."""
    sessions = []
    try:
        stream = Stream.from_file(filepath)
        decoder = Decoder(stream)
        messages, errors = decoder.read()
        
        if errors:
            pass  # Some non-critical errors may occur
        
        session_msgs = messages.get("session_mesgs", [])
        
        for sess in session_msgs:
            sport = sess.get("sport")
            if sport is None:
                continue
            
            # Map sport enum values
            sport_name = str(sport)
            if "running" in sport_name.lower() or sport_name == "1":
                sport_name = "running"
            elif "trail" in sport_name.lower():
                sport_name = "trail_running"
            elif "walking" in sport_name.lower() or sport_name == "11":
                sport_name = "walking"
            else:
                continue  # Skip non-running activities
            
            start_time = sess.get("start_time")
            if start_time is None:
                continue
            
            # Handle timestamp - could be datetime or int
            if isinstance(start_time, (int, float)):
                start_dt = GARMIN_EPOCH + timedelta(seconds=start_time)
            elif isinstance(start_time, datetime):
                start_dt = start_time
            else:
                continue
            
            total_distance = sess.get("total_distance")  # meters (might need /100)
            total_timer_time = sess.get("total_timer_time")  # seconds (might need /1000)
            total_elapsed_time = sess.get("total_elapsed_time")
            avg_hr = sess.get("avg_heart_rate")
            max_hr = sess.get("max_heart_rate")
            avg_cadence = sess.get("avg_running_cadence") or sess.get("avg_cadence")
            total_ascent = sess.get("total_ascent")
            total_descent = sess.get("total_descent")
            total_calories = sess.get("total_calories")
            avg_speed = sess.get("enhanced_avg_speed") or sess.get("avg_speed")
            
            # Distance in km
            if total_distance is not None:
                # SDK usually returns in meters already
                if total_distance > 100000:  # probably in cm or mm
                    dist_km = total_distance / 100000.0
                else:
                    dist_km = total_distance / 1000.0
            else:
                dist_km = 0
            
            dist_km = round(dist_km, 2)
            
            # Timer time in minutes
            if total_timer_time is not None:
                if total_timer_time > 1000000:  # probably in ms
                    timer_min = total_timer_time / 60000.0
                else:
                    timer_min = total_timer_time / 60.0
            else:
                timer_min = 0
            timer_min = round(timer_min, 2)
            
            # Elapsed time
            if total_elapsed_time is not None:
                if total_elapsed_time > 1000000:
                    elapsed_min = total_elapsed_time / 60000.0
                else:
                    elapsed_min = total_elapsed_time / 60.0
            else:
                elapsed_min = 0
            elapsed_min = round(elapsed_min, 2)
            
            # Average pace
            if avg_speed and avg_speed > 0:
                if avg_speed > 100:  # mm/s
                    avg_speed_ms = avg_speed / 1000.0
                else:
                    avg_speed_ms = avg_speed
                pace_sec_per_km = 1000.0 / avg_speed_ms
                pace_min = int(pace_sec_per_km // 60)
                pace_s = int(pace_sec_per_km % 60)
                avg_pace = f"{pace_min}:{pace_s:02d}"
                avg_pace_seconds = pace_sec_per_km
            elif dist_km > 0 and timer_min > 0:
                avg_pace_seconds = (timer_min * 60) / dist_km
                pace_min = int(avg_pace_seconds // 60)
                pace_s = int(avg_pace_seconds % 60)
                avg_pace = f"{pace_min}:{pace_s:02d}"
            else:
                avg_pace = ""
                avg_pace_seconds = 0
            
            sessions.append({
                "filename": os.path.basename(filepath),
                "date": start_dt.strftime("%Y-%m-%d"),
                "start_time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "sport": sport_name,
                "distance_km": dist_km,
                "timer_time_min": timer_min,
                "elapsed_time_min": elapsed_min,
                "avg_pace": avg_pace,
                "avg_pace_seconds": round(avg_pace_seconds, 1),
                "avg_heart_rate": avg_hr if avg_hr else "",
                "max_heart_rate": max_hr if max_hr else "",
                "avg_cadence": avg_cadence if avg_cadence else "",
                "total_ascent": total_ascent or 0,
                "total_descent": total_descent or 0,
                "total_calories": total_calories or 0,
            })
    except Exception as e:
        print(f"Error parsing {os.path.basename(filepath)}: {e}", file=sys.stderr)
    return sessions


def format_time(timer_min):
    total_sec = timer_min * 60
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    return f"{h}:{m:02d}:{s:02d}"


def main():
    fit_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".fit")])
    print(f"Found {len(fit_files)} FIT files")
    
    all_sessions = []
    error_count = 0
    for i, fname in enumerate(fit_files):
        fpath = os.path.join(DATA_DIR, fname)
        sessions = parse_fit(fpath)
        if not sessions:
            error_count += 1
        all_sessions.extend(sessions)
        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(fit_files)} files, {len(all_sessions)} running sessions so far")
    
    # Sort by date
    all_sessions.sort(key=lambda x: x["start_time"])
    
    # Filter out very short runs (< 1km, likely GPS glitches)
    running_sessions = [s for s in all_sessions if s["distance_km"] >= 1.0]
    
    print(f"\nTotal sessions found: {len(all_sessions)} (filtered running >= 1km: {len(running_sessions)})")
    print(f"Files with errors or no running data: {error_count}")
    
    # Write CSV
    if running_sessions:
        fieldnames = list(running_sessions[0].keys())
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(running_sessions)
        print(f"Wrote CSV to {OUTPUT_CSV}")
    
    all_sessions = running_sessions
    
    if all_sessions:
        dates = [s["date"] for s in all_sessions]
        print(f"\nDate range: {min(dates)} to {max(dates)}")
        total_dist = sum(s["distance_km"] for s in all_sessions)
        print(f"Total distance: {total_dist:.1f} km across {len(all_sessions)} sessions")
        
        # Monthly summary
        monthly = defaultdict(lambda: {"count": 0, "distance": 0})
        for s in all_sessions:
            month = s["date"][:7]
            monthly[month]["count"] += 1
            monthly[month]["distance"] += s["distance_km"]
        
        print("\n=== Monthly Summary ===")
        for month in sorted(monthly.keys()):
            m = monthly[month]
            print(f"  {month}: {m['count']:3d} runs, {m['distance']:7.1f} km")
        
        # Top 20 Longest Runs
        long_runs = sorted(all_sessions, key=lambda x: x["distance_km"], reverse=True)[:20]
        print("\n=== Top 20 Longest Runs ===")
        for r in long_runs:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Top 20 Fastest (>= 5km)
        qualified = [s for s in all_sessions if s["distance_km"] >= 5 and s["avg_pace_seconds"] > 0]
        fast_runs = sorted(qualified, key=lambda x: x["avg_pace_seconds"])[:20]
        print("\n=== Top 20 Fastest Runs (>= 5km) ===")
        for r in fast_runs:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Recent data
        today = date(2026, 5, 5)
        
        last_30 = [s for s in all_sessions if (today - datetime.strptime(s["date"], "%Y-%m-%d").date()).days <= 30]
        print(f"\n=== Last 30 Days ({len(last_30)} runs, {sum(s['distance_km'] for s in last_30):.1f} km) ===")
        for r in last_30:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        last_90 = [s for s in all_sessions if (today - datetime.strptime(s["date"], "%Y-%m-%d").date()).days <= 90]
        print(f"\n=== Last 90 Days: {len(last_90)} runs, {sum(s['distance_km'] for s in last_90):.1f} km ===")
        for r in last_90:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Half Marathon runs (20-22.5km)
        half_marathons = [s for s in all_sessions if 20.0 <= s["distance_km"] <= 22.5]
        print(f"\n=== Half Marathon Distance Runs ({len(half_marathons)}) ===")
        for r in sorted(half_marathons, key=lambda x: x["timer_time_min"]):
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Full Marathon runs (40-44km)
        full_marathons = [s for s in all_sessions if 40.0 <= s["distance_km"] <= 44.0]
        print(f"\n=== Full Marathon Distance Runs ({len(full_marathons)}) ===")
        for r in sorted(full_marathons, key=lambda x: x["timer_time_min"]):
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # 10K runs
        ten_k = [s for s in all_sessions if 9.5 <= s["distance_km"] <= 10.5]
        print(f"\n=== 10K Distance Runs ({len(ten_k)}) - Top 10 fastest ===")
        for r in sorted(ten_k, key=lambda x: x["avg_pace_seconds"])[:10]:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # 5K runs
        five_k = [s for s in all_sessions if 4.5 <= s["distance_km"] <= 5.5]
        print(f"\n=== 5K Distance Runs ({len(five_k)}) - Top 10 fastest ===")
        for r in sorted(five_k, key=lambda x: x["avg_pace_seconds"])[:10]:
            print(f"  {r['date']} | {r['distance_km']:7.2f} km | {format_time(r['timer_time_min'])} | pace {r['avg_pace']} | HR {r['avg_heart_rate']}")
        
        # Peak periods analysis
        print("\n=== Peak Performance Periods (Monthly avg pace for months with > 100km) ===")
        monthly_pace = defaultdict(lambda: {"total_pace_dist": 0, "total_dist": 0, "count": 0, "distance": 0})
        for s in all_sessions:
            if s["avg_pace_seconds"] > 0 and s["distance_km"] >= 3:
                month = s["date"][:7]
                monthly_pace[month]["total_pace_dist"] += s["avg_pace_seconds"] * s["distance_km"]
                monthly_pace[month]["total_dist"] += s["distance_km"]
                monthly_pace[month]["count"] += 1
                monthly_pace[month]["distance"] += s["distance_km"]
        
        for month in sorted(monthly_pace.keys()):
            mp = monthly_pace[month]
            if mp["distance"] >= 100:
                avg_pace_s = mp["total_pace_dist"] / mp["total_dist"]
                p_min = int(avg_pace_s // 60)
                p_s = int(avg_pace_s % 60)
                print(f"  {month}: {mp['distance']:7.1f} km, avg pace {p_min}:{p_s:02d}")


if __name__ == "__main__":
    main()
