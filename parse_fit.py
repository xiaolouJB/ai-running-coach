"""Parse FIT files and extract running session summaries."""
import os
import sys
import csv
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

SDK_TYPE = None

try:
    from garmin_fit_sdk import Decoder, Stream
    SDK_TYPE = "garmin_fit_sdk"
except ImportError:
    try:
        from fitparse import FitFile
        SDK_TYPE = "fitparse"
    except ImportError:
        SDK_TYPE = None

GARMIN_EPOCH = datetime(1989, 12, 31, 0, 0, 0)
CSV_HEADER = [
    "date",
    "sport",
    "distance_km",
    "duration_min",
    "avg_pace_min_km",
    "avg_hr",
    "max_hr",
    "cadence",
    "calories"
]


def format_pace(pace_sec):
    if pace_sec is None or pace_sec <= 0:
        return ""
    pace_min = int(pace_sec // 60)
    pace_s = int(round(pace_sec % 60))
    if pace_s == 60:
        pace_min += 1
        pace_s = 0
    return f"{pace_min}:{pace_s:02d}"


def parse_fit_garmin_sdk(filepath):
    stream = Stream.from_file(filepath)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    session_msgs = messages.get("session_mesgs", [])
    sessions = []

    for sess in session_msgs:
        sport = sess.get("sport")
        if sport is None:
            continue

        sport_name = str(sport)
        if "running" in sport_name.lower() or sport_name == "1":
            sport_name = "running"
        elif "trail" in sport_name.lower():
            sport_name = "trail_running"
        elif "walking" in sport_name.lower() or sport_name == "11":
            sport_name = "walking"
        else:
            sport_name = str(sport).lower()

        start_time = sess.get("start_time")
        if start_time is None:
            continue

        if isinstance(start_time, (int, float)):
            start_dt = GARMIN_EPOCH + timedelta(seconds=start_time)
        elif isinstance(start_time, datetime):
            start_dt = start_time
        else:
            continue

        total_distance = sess.get("total_distance")
        total_timer_time = sess.get("total_timer_time")
        avg_hr = sess.get("avg_heart_rate")
        max_hr = sess.get("max_heart_rate")
        avg_cadence = sess.get("avg_running_cadence") or sess.get("avg_cadence")
        total_calories = sess.get("total_calories")
        avg_speed = sess.get("enhanced_avg_speed") or sess.get("avg_speed")

        dist_km = None
        if total_distance is not None:
            if total_distance > 100000:
                dist_km = round(total_distance / 100000.0, 2)
            else:
                dist_km = round(total_distance / 1000.0, 2)

        timer_min = None
        if total_timer_time is not None:
            if total_timer_time > 1000000:
                timer_min = round(total_timer_time / 60000.0, 2)
            else:
                timer_min = round(total_timer_time / 60.0, 2)

        pace_sec = None
        if avg_speed and avg_speed > 0:
            avg_speed_ms = avg_speed / 1000.0 if avg_speed > 100 else avg_speed
            if avg_speed_ms > 0:
                pace_sec = 1000.0 / avg_speed_ms
        elif dist_km and timer_min and dist_km > 0 and timer_min > 0:
            pace_sec = (timer_min * 60.0) / dist_km

        sessions.append({
            "date": start_dt.strftime("%Y-%m-%d"),
            "sport": sport_name,
            "distance_km": f"{dist_km:.2f}" if dist_km is not None else "",
            "duration_min": f"{timer_min:.2f}" if timer_min is not None else "",
            "avg_pace_min_km": format_pace(pace_sec),
            "avg_hr": int(avg_hr) if avg_hr is not None else "",
            "max_hr": int(max_hr) if max_hr is not None else "",
            "cadence": int(avg_cadence) if avg_cadence is not None else "",
            "calories": int(total_calories) if total_calories is not None else "",
            "_raw_date": start_dt,
            "_dist_num": dist_km or 0.0,
            "_dur_num": timer_min or 0.0,
            "_pace_sec": pace_sec or 0.0,
        })
    return sessions


def parse_fit_fitparse(filepath):
    fitfile = FitFile(filepath)
    sessions = []
    for record in fitfile.get_messages("session"):
        data = {field.name: field.value for field in record}
        sport = data.get("sport")
        if not sport:
            continue
        sport_name = str(sport).lower()

        start_time = data.get("start_time")
        if not start_time:
            continue

        if isinstance(start_time, datetime):
            start_dt = start_time
        elif isinstance(start_time, (int, float)):
            start_dt = GARMIN_EPOCH + timedelta(seconds=start_time)
        else:
            continue

        total_distance = data.get("total_distance")
        total_timer_time = data.get("total_timer_time")
        avg_hr = data.get("avg_heart_rate")
        max_hr = data.get("max_heart_rate")
        avg_cadence = data.get("avg_running_cadence") or data.get("avg_cadence")
        total_calories = data.get("total_calories")
        avg_speed = data.get("enhanced_avg_speed") or data.get("avg_speed")

        dist_km = round(total_distance / 1000.0, 2) if total_distance is not None else None
        timer_min = round(total_timer_time / 60.0, 2) if total_timer_time is not None else None

        pace_sec = None
        if avg_speed and avg_speed > 0:
            pace_sec = 1000.0 / avg_speed
        elif dist_km and timer_min and dist_km > 0 and timer_min > 0:
            pace_sec = (timer_min * 60.0) / dist_km

        sessions.append({
            "date": start_dt.strftime("%Y-%m-%d"),
            "sport": sport_name,
            "distance_km": f"{dist_km:.2f}" if dist_km is not None else "",
            "duration_min": f"{timer_min:.2f}" if timer_min is not None else "",
            "avg_pace_min_km": format_pace(pace_sec),
            "avg_hr": int(avg_hr) if avg_hr is not None else "",
            "max_hr": int(max_hr) if max_hr is not None else "",
            "cadence": int(avg_cadence) if avg_cadence is not None else "",
            "calories": int(total_calories) if total_calories is not None else "",
            "_raw_date": start_dt,
            "_dist_num": dist_km or 0.0,
            "_dur_num": timer_min or 0.0,
            "_pace_sec": pace_sec or 0.0,
        })
    return sessions


def parse_single_file(filepath):
    if SDK_TYPE == "garmin_fit_sdk":
        return parse_fit_garmin_sdk(filepath)
    elif SDK_TYPE == "fitparse":
        return parse_fit_fitparse(filepath)
    else:
        raise RuntimeError("No FIT parsing library installed.")


def print_monthly_summary(sessions):
    if not sessions:
        return
    monthly = defaultdict(lambda: {"count": 0, "distance": 0.0, "duration": 0.0})
    for s in sessions:
        month = s["date"][:7]
        monthly[month]["count"] += 1
        monthly[month]["distance"] += s["_dist_num"]
        monthly[month]["duration"] += s["_dur_num"]

    print("\n=== Monthly Summary ===")
    for month in sorted(monthly.keys()):
        m = monthly[month]
        total_dist = m["distance"]
        total_dur = m["duration"]
        if total_dist > 0 and total_dur > 0:
            avg_pace_sec = (total_dur * 60.0) / total_dist
            pace_str = format_pace(avg_pace_sec)
        else:
            pace_str = "N/A"
        print(f"  {month}: {m['count']:3d} runs, {total_dist:7.1f} km, avg pace {pace_str}")


class _Parser(argparse.ArgumentParser):
    """参数错误退出码用 1（argparse 默认是 2，本脚本 2 专用于「缺依赖」）。"""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"错误：{message}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = _Parser(description="解析 FIT 文件，导出跑步记录摘要 CSV。")
    parser.add_argument("--input", required=True, help="单个 .fit 文件，或包含 .fit 的目录（递归）")
    parser.add_argument("--out", default="runs.csv", help="CSV 输出路径（默认 ./runs.csv）")
    parser.add_argument("--summary", action="store_true", help="额外打印按月汇总")

    # 先解析参数：--help 在缺依赖时也必须可用（陌生人 clone 后的第一个动作）
    args = parser.parse_args()

    if SDK_TYPE is None:
        print("错误：未安装 FIT 解析库（garmin-fit-sdk 或 fitparse）。", file=sys.stderr)
        print("请先安装：pip install garmin-fit-sdk", file=sys.stderr)
        sys.exit(2)

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"错误：输入路径不存在：'{input_path}'", file=sys.stderr)
        sys.exit(1)

    fit_files = []
    if os.path.isfile(input_path):
        if input_path.lower().endswith(".fit"):
            fit_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(".fit"):
                    fit_files.append(os.path.join(root, file))

    if not fit_files:
        print(f"错误：在 '{input_path}' 未找到 .fit 文件。", file=sys.stderr)
        sys.exit(1)

    all_sessions = []
    failed_files = 0

    for filepath in sorted(fit_files):
        try:
            all_sessions.extend(parse_single_file(filepath))
        except Exception as e:
            failed_files += 1
            print(f"解析失败（已跳过）{os.path.basename(filepath)}: {e}", file=sys.stderr)

    if failed_files == len(fit_files):
        print(f"错误：全部 {len(fit_files)} 个 FIT 文件解析失败。", file=sys.stderr)
        sys.exit(1)

    if not all_sessions:
        print("错误：未能从 FIT 文件中提取到任何有效运动记录。", file=sys.stderr)
        sys.exit(1)

    # Sort by raw date
    all_sessions.sort(key=lambda s: s["_raw_date"])

    # Write CSV
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_sessions)

    print(f"成功解析 {len(fit_files) - failed_files}/{len(fit_files)} 个文件。")
    print(f"已写入 {len(all_sessions)} 条记录到 {args.out}")

    if args.summary:
        print_monthly_summary(all_sessions)

    sys.exit(0)


if __name__ == "__main__":
    main()
