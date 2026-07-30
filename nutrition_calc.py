"""
nutrition_calc.py — 运动营养与补给纯函数计算（仅标准库，零第三方依赖）

确定性算术计算器：
1. sweat_rate_ml_h: 个性化出汗率计算 (ml/h)
2. hydration_plan: 补水/补盐方案计算 (含胃排空上限 800ml/h 封顶)
3. fueling_plan: 长跑补给方案计算 (能量胶支数、补给时点、碳水与水合)

依据 ACSM Position Stand: Nutrition and Athletic Performance (2016)。
"""

import sys
import math
import json
import argparse

STANDARD_RANGE = (400, 800)
MAX_INTAKE_ML_H = 800
HOT_TEMP_C = 28


def sweat_rate_ml_h(
    pre_weight_kg: float,
    post_weight_kg: float,
    duration_min: float,
    fluid_ml: float = 0,
    urine_ml: float = 0,
) -> int:
    """每小时出汗量(ml) = [(跑前−跑后)kg×1000 + 饮水ml − 排尿ml] ÷ (时长min/60)。

    时长 <= 0 抛 ValueError。
    """
    hours = (duration_min or 0) / 60.0
    if hours <= 0:
        raise ValueError("训练时长必须大于 0")
    loss_g = (float(pre_weight_kg) - float(post_weight_kg)) * 1000.0
    return round((loss_g + (fluid_ml or 0) - (urine_ml or 0)) / hours)


def hydration_plan(
    sweat_rate: float | None = None,
    *,
    race_hours: float | None = None,
    loss_kg: float | None = None,
    temp_c: float | None = None,
    feels_like_c: float | None = None,
) -> dict:
    """根据出汗率计算补水/补盐建议（确定性算术）。"""
    eff_c = feels_like_c if feels_like_c is not None else temp_c
    hot = eff_c is not None and eff_c >= HOT_TEMP_C
    sodium = (300, 600)
    out: dict = {
        "personalized": sweat_rate is not None,
        "sodium_mg_h": sodium,
        "sodium_pick": sodium[1] if hot else sodium[0],
        "carb_g_h": (30, 60),
        "hot": hot,
    }
    if sweat_rate is None:
        out["intake_ml_h"] = STANDARD_RANGE
    else:
        target = round(min(sweat_rate, MAX_INTAKE_ML_H))
        out["sweat_rate_ml_h"] = round(sweat_rate)
        out["intake_ml_h"] = target
        out["capped"] = sweat_rate > MAX_INTAKE_ML_H
        if race_hours and race_hours > 0:
            out["total_intake_ml"] = round(target * race_hours)

    if loss_kg is not None and loss_kg > 0:
        out["post_run_rehydrate_l"] = round(1.5 * loss_kg, 2)

    return out


def fueling_plan(
    duration_min: float,
    sweat_rate_ml_h: int | None = None,
    temp_c: float | None = None,
) -> dict:
    """长跑补给方案（能量胶支数、补给时点、碳水与水合目标）。"""
    dur = float(duration_min or 0)
    if dur < 90:
        return {"carb_needed": False, "note": "90min 内无需额外补碳"}

    hot = temp_c is not None and temp_c >= HOT_TEMP_C
    if dur <= 150:
        carb_g_h = (30, 60)
    else:
        carb_g_h = (60, 90)

    # 胶点：第 30min 起，每 40min 1 支
    gel_count = max(1, math.ceil((dur - 30) / 40)) if dur > 30 else 1
    gels = [{"at_min": 30 + i * 40} for i in range(gel_count)]
    total_carb_g = round(carb_g_h[0] * dur / 60, 0)

    sodium_mg_h = (300, 600)
    sodium_pick = sodium_mg_h[1] if hot else sodium_mg_h[0]

    # 饮水
    if sweat_rate_ml_h and sweat_rate_ml_h > 0:
        intake_ml_h = round(sweat_rate_ml_h * 0.8)
        water_per_gel = round(intake_ml_h * 40 / 60)
        water = {"intake_ml_h": intake_ml_h, "per_gel_ml": water_per_gel, "personalized": True}
    else:
        water = {"intake_ml_h": STANDARD_RANGE, "per_gel_ml": None, "personalized": False}

    return {
        "carb_needed": True,
        "carb_g_h": carb_g_h,
        "total_carb_g": total_carb_g,
        "gels": gels,
        "gel_count": gel_count,
        "sodium_mg_h": sodium_mg_h,
        "sodium_pick": sodium_pick,
        "hot": hot,
        "water": water,
        "duration_min": dur,
    }


def main():
    parser = argparse.ArgumentParser(description="跑者营养与水合算术工具")
    subparsers = parser.add_subparsers(dest="command")

    # sweat
    sweat_parser = subparsers.add_parser("sweat", help="计算出汗率")
    sweat_parser.add_argument("--pre", type=float, required=True, help="跑前体重 (kg)")
    sweat_parser.add_argument("--post", type=float, required=True, help="跑后体重 (kg)")
    sweat_parser.add_argument("--dur", type=float, required=True, help="训练时长 (分钟)")
    sweat_parser.add_argument("--fluid", type=float, default=0, help="途中饮水量 (ml)")
    sweat_parser.add_argument("--urine", type=float, default=0, help="途中排尿量 (ml)")

    # fuel
    fuel_parser = subparsers.add_parser("fuel", help="长跑补给方案")
    fuel_parser.add_argument("--dur", type=float, required=True, help="预计长跑时长 (分钟)")
    fuel_parser.add_argument("--sweat-rate", type=int, default=None, help="实测出汗率 (ml/h)")
    fuel_parser.add_argument("--temp", type=float, default=None, help="体感或气温 (℃)")

    args = parser.parse_args()

    if args.command == "sweat":
        rate = sweat_rate_ml_h(args.pre, args.post, args.dur, args.fluid, args.urine)
        plan = hydration_plan(rate)
        res = {"sweat_rate_ml_h": rate, "hydration_plan": plan}
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.command == "fuel":
        res = fueling_plan(args.dur, args.sweat_rate, args.temp)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
