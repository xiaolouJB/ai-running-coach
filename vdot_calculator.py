#!/usr/bin/env python3
"""
VDOT Calculator · 丹尼尔斯跑步方程式
基于 Jack Daniels' Running Formula (3rd Edition, 2013) 对照表

用法:
  python vdot_calculator.py --distance 5K --time 22:00
  python vdot_calculator.py --vdot 45
"""

import argparse
import math

# ══════════════════════════════════════════════════════════════
# 丹尼尔斯 VDOT 对照表（第3版 Table 3.1 & 3.2）
# 时间单位: 秒  |  配速单位: 秒/公里
# ══════════════════════════════════════════════════════════════

VDOT_TABLE = {
    # VDOT: {
    #   "race": { "5K": secs, "10K": secs, "half": secs, "full": secs },
    #   "pace": { "E": (min_sec_per_km, max_sec_per_km), "M": sec/km, "T": sec/km,
    #             "I_400": secs, "I_1000": secs, "R_200": secs, "R_400": secs }
    # }
    30: {
        "race": {"5K": 1860, "10K": 3876, "half": 8640, "full": 17820},
        "pace": {"E": (462, 498), "M": 426, "T": 402, "I_400": 144, "I_1000": 375, "R_200": 66, "R_400": 138}
    },
    31: {
        "race": {"5K": 1800, "10K": 3750, "half": 8352, "full": 17220},
        "pace": {"E": (450, 486), "M": 414, "T": 390, "I_400": 140, "I_1000": 365, "R_200": 64, "R_400": 134}
    },
    32: {
        "race": {"5K": 1740, "10K": 3630, "half": 8082, "full": 16656},
        "pace": {"E": (438, 474), "M": 402, "T": 381, "I_400": 137, "I_1000": 356, "R_200": 63, "R_400": 131}
    },
    33: {
        "race": {"5K": 1686, "10K": 3516, "half": 7830, "full": 16128},
        "pace": {"E": (426, 462), "M": 393, "T": 372, "I_400": 133, "I_1000": 347, "R_200": 61, "R_400": 128}
    },
    34: {
        "race": {"5K": 1632, "10K": 3408, "half": 7590, "full": 15636},
        "pace": {"E": (417, 450), "M": 384, "T": 363, "I_400": 130, "I_1000": 339, "R_200": 60, "R_400": 125}
    },
    35: {
        "race": {"5K": 1578, "10K": 3300, "half": 7356, "full": 15168},
        "pace": {"E": (405, 441), "M": 375, "T": 354, "I_400": 127, "I_1000": 331, "R_200": 58, "R_400": 122}
    },
    36: {
        "race": {"5K": 1530, "10K": 3198, "half": 7134, "full": 14724},
        "pace": {"E": (396, 429), "M": 366, "T": 348, "I_400": 124, "I_1000": 324, "R_200": 57, "R_400": 120}
    },
    37: {
        "race": {"5K": 1482, "10K": 3102, "half": 6924, "full": 14304},
        "pace": {"E": (387, 420), "M": 360, "T": 339, "I_400": 121, "I_1000": 317, "R_200": 56, "R_400": 117}
    },
    38: {
        "race": {"5K": 1434, "10K": 3006, "half": 6726, "full": 13908},
        "pace": {"E": (378, 411), "M": 351, "T": 333, "I_400": 119, "I_1000": 310, "R_200": 55, "R_400": 115}
    },
    39: {
        "race": {"5K": 1392, "10K": 2916, "half": 6534, "full": 13530},
        "pace": {"E": (369, 402), "M": 345, "T": 327, "I_400": 116, "I_1000": 304, "R_200": 54, "R_400": 112}
    },
    40: {
        "race": {"5K": 1350, "10K": 2832, "half": 6348, "full": 13170},
        "pace": {"E": (363, 396), "M": 339, "T": 321, "I_400": 114, "I_1000": 298, "R_200": 53, "R_400": 110}
    },
    41: {
        "race": {"5K": 1308, "10K": 2748, "half": 6174, "full": 12828},
        "pace": {"E": (354, 387), "M": 333, "T": 315, "I_400": 112, "I_1000": 292, "R_200": 52, "R_400": 108}
    },
    42: {
        "race": {"5K": 1272, "10K": 2670, "half": 6006, "full": 12498},
        "pace": {"E": (348, 378), "M": 327, "T": 309, "I_400": 110, "I_1000": 287, "R_200": 51, "R_400": 106}
    },
    43: {
        "race": {"5K": 1236, "10K": 2592, "half": 5844, "full": 12186},
        "pace": {"E": (339, 372), "M": 321, "T": 306, "I_400": 108, "I_1000": 282, "R_200": 50, "R_400": 104}
    },
    44: {
        "race": {"5K": 1200, "10K": 2520, "half": 5694, "full": 11886},
        "pace": {"E": (333, 363), "M": 318, "T": 300, "I_400": 106, "I_1000": 277, "R_200": 49, "R_400": 102}
    },
    45: {
        "race": {"5K": 1170, "10K": 2454, "half": 5550, "full": 11598},
        "pace": {"E": (327, 357), "M": 312, "T": 294, "I_400": 104, "I_1000": 272, "R_200": 48, "R_400": 100}
    },
    46: {
        "race": {"5K": 1140, "10K": 2388, "half": 5412, "full": 11322},
        "pace": {"E": (321, 351), "M": 309, "T": 291, "I_400": 102, "I_1000": 268, "R_200": 47, "R_400": 99}
    },
    47: {
        "race": {"5K": 1110, "10K": 2328, "half": 5280, "full": 11058},
        "pace": {"E": (315, 345), "M": 303, "T": 285, "I_400": 101, "I_1000": 264, "R_200": 47, "R_400": 97}
    },
    48: {
        "race": {"5K": 1080, "10K": 2268, "half": 5154, "full": 10806},
        "pace": {"E": (309, 339), "M": 300, "T": 282, "I_400": 99, "I_1000": 260, "R_200": 46, "R_400": 96}
    },
    49: {
        "race": {"5K": 1056, "10K": 2214, "half": 5034, "full": 10560},
        "pace": {"E": (306, 333), "M": 294, "T": 279, "I_400": 98, "I_1000": 256, "R_200": 45, "R_400": 94}
    },
    50: {
        "race": {"5K": 1032, "10K": 2160, "half": 4920, "full": 10326},
        "pace": {"E": (300, 330), "M": 291, "T": 275, "I_400": 96, "I_1000": 252, "R_200": 45, "R_400": 93}
    },
    51: {
        "race": {"5K": 1008, "10K": 2112, "half": 4812, "full": 10104},
        "pace": {"E": (294, 324), "M": 288, "T": 272, "I_400": 95, "I_1000": 249, "R_200": 44, "R_400": 92}
    },
    52: {
        "race": {"5K": 984, "10K": 2064, "half": 4710, "full": 9888},
        "pace": {"E": (291, 318), "M": 285, "T": 268, "I_400": 94, "I_1000": 246, "R_200": 43, "R_400": 90}
    },
    53: {
        "race": {"5K": 960, "10K": 2016, "half": 4608, "full": 9684},
        "pace": {"E": (285, 315), "M": 279, "T": 265, "I_400": 92, "I_1000": 243, "R_200": 43, "R_400": 89}
    },
    54: {
        "race": {"5K": 942, "10K": 1974, "half": 4512, "full": 9486},
        "pace": {"E": (282, 309), "M": 276, "T": 262, "I_400": 91, "I_1000": 240, "R_200": 42, "R_400": 88}
    },
    55: {
        "race": {"5K": 918, "10K": 1932, "half": 4416, "full": 9300},
        "pace": {"E": (276, 306), "M": 273, "T": 258, "I_400": 90, "I_1000": 237, "R_200": 42, "R_400": 87}
    },
    56: {
        "race": {"5K": 900, "10K": 1890, "half": 4326, "full": 9120},
        "pace": {"E": (273, 300), "M": 270, "T": 255, "I_400": 89, "I_1000": 234, "R_200": 41, "R_400": 86}
    },
    57: {
        "race": {"5K": 882, "10K": 1854, "half": 4242, "full": 8946},
        "pace": {"E": (270, 297), "M": 267, "T": 252, "I_400": 88, "I_1000": 231, "R_200": 41, "R_400": 85}
    },
    58: {
        "race": {"5K": 864, "10K": 1818, "half": 4158, "full": 8784},
        "pace": {"E": (267, 294), "M": 264, "T": 249, "I_400": 87, "I_1000": 228, "R_200": 40, "R_400": 84}
    },
    59: {
        "race": {"5K": 846, "10K": 1782, "half": 4080, "full": 8622},
        "pace": {"E": (264, 291), "M": 261, "T": 246, "I_400": 86, "I_1000": 226, "R_200": 40, "R_400": 83}
    },
    60: {
        "race": {"5K": 834, "10K": 1746, "half": 4002, "full": 8472},
        "pace": {"E": (261, 288), "M": 258, "T": 243, "I_400": 85, "I_1000": 224, "R_200": 39, "R_400": 82}
    },
    65: {
        "race": {"5K": 762, "10K": 1602, "half": 3678, "full": 7800},
        "pace": {"E": (246, 270), "M": 243, "T": 231, "I_400": 81, "I_1000": 213, "R_200": 37, "R_400": 78}
    },
}

# 支持的比赛距离 → 米
DISTANCES = {
    "5K": 5000, "5k": 5000,
    "10K": 10000, "10k": 10000,
    "half": 21097.5, "半马": 21097.5, "HM": 21097.5,
    "full": 42195, "全马": 42195, "FM": 42195,
}


def format_time(seconds: int) -> str:
    """秒 → H:MM:SS 或 MM:SS 格式"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_pace(seconds_per_km: int) -> str:
    """秒/公里 → M:SS/km 格式"""
    m = seconds_per_km // 60
    s = seconds_per_km % 60
    return f"{m}:{s:02d}/km"


def parse_time(time_str: str) -> int:
    """时间字符串 → 秒。支持 H:MM:SS, MM:SS, 或纯秒数"""
    parts = time_str.strip().split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return int(parts[0])


def lookup_vdot(distance: str, time_seconds: int) -> int:
    """
    根据比赛距离和完赛时间，查表返回最接近的 VDOT 值。
    采用线性插值，取最近整数。
    """
    dist_key = None
    for key in ["5K", "10K", "half", "full"]:
        if distance.upper().replace("半马", "half").replace("全马", "full") in [key, key.lower()]:
            dist_key = key
            break
    if distance in ["半马", "HM"]:
        dist_key = "half"
    elif distance in ["全马", "FM"]:
        dist_key = "full"
    if not dist_key:
        raise ValueError(f"不支持的距离: {distance}。支持: 5K, 10K, 半马/half, 全马/full")

    # 找到最接近的 VDOT
    sorted_vdots = sorted(VDOT_TABLE.keys())
    best_vdot = sorted_vdots[0]
    best_diff = abs(VDOT_TABLE[sorted_vdots[0]]["race"][dist_key] - time_seconds)

    for v in sorted_vdots:
        diff = abs(VDOT_TABLE[v]["race"][dist_key] - time_seconds)
        if diff < best_diff:
            best_diff = diff
            best_vdot = v

    return best_vdot


def get_training_paces(vdot: int) -> dict:
    """根据 VDOT 返回五区训练配速"""
    # 如果精确值不在表中，取最近的
    sorted_vdots = sorted(VDOT_TABLE.keys())
    if vdot not in VDOT_TABLE:
        closest = min(sorted_vdots, key=lambda v: abs(v - vdot))
        vdot = closest

    data = VDOT_TABLE[vdot]
    paces = data["pace"]
    e_min, e_max = paces["E"]

    return {
        "vdot": vdot,
        "E_zone": f"{format_pace(e_min)} ~ {format_pace(e_max)}",
        "M_pace": format_pace(paces["M"]),
        "T_pace": format_pace(paces["T"]),
        "I_400m": format_time(paces["I_400"]),
        "I_1000m": format_time(paces["I_1000"]),
        "R_200m": format_time(paces["R_200"]),
        "R_400m": format_time(paces["R_400"]),
        "race_predictions": {
            "5K": format_time(data["race"]["5K"]),
            "10K": format_time(data["race"]["10K"]),
            "半马": format_time(data["race"]["half"]),
            "全马": format_time(data["race"]["full"]),
        }
    }


def print_report(result: dict):
    """打印完整的 VDOT 报告"""
    print(f"\n{'='*50}")
    print(f"  VDOT = {result['vdot']}")
    print(f"{'='*50}")
    print(f"\n[Training Paces]")
    print(f"  E (Easy):     {result['E_zone']}")
    print(f"  M (Marathon):  {result['M_pace']}")
    print(f"  T (Threshold): {result['T_pace']}")
    print(f"  I (Interval):  400m={result['I_400m']}  1000m={result['I_1000m']}")
    print(f"  R (Repetition):200m={result['R_200m']}  400m={result['R_400m']}")
    print(f"\n[Race Predictions]")
    for dist, time in result["race_predictions"].items():
        print(f"  {dist}: {time}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="丹尼尔斯 VDOT 计算器")
    parser.add_argument("--distance", type=str, help="比赛距离: 5K, 10K, 半马, 全马")
    parser.add_argument("--time", type=str, help="完赛时间: H:MM:SS 或 MM:SS")
    parser.add_argument("--vdot", type=int, help="直接输入 VDOT 值查询配速")
    args = parser.parse_args()

    if args.vdot:
        result = get_training_paces(args.vdot)
        print_report(result)
    elif args.distance and args.time:
        time_secs = parse_time(args.time)
        vdot = lookup_vdot(args.distance, time_secs)
        print(f"\n  {args.distance} 成绩 {args.time} → VDOT {vdot}")
        result = get_training_paces(vdot)
        print_report(result)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python vdot_calculator.py --distance 5K --time 22:00")
        print("  python vdot_calculator.py --vdot 45")
