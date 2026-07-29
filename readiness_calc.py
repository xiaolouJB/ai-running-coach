"""
readiness_calc.py — 今日身体准备度判定（纯标准库，零依赖）

多信号红旗否决制：
- 每个指标入参可缺 (None) → 不参与、不计红旗、放入 skipped 列表。
- 硬红旗条件：
  - HRV 跌幅 >= 20% (hrv_drop_pct >= 20.0)
  - 静息心率突升 >= 7bpm (rhr_spike_bpm >= 7.0)
  - 睡眠分 < 60 (sleep_score < 60)
- 判定逻辑：
  - 0 面红旗 → ok
  - 1 面红旗 → caution
  - >=2 面红旗 → hard_caution
"""
import sys
import json
import argparse

SLEEP_SCORE_LOW = 60


def compute_readiness(
    hrv_drop_pct: float | None = None,
    rhr_spike_bpm: float | None = None,
    sleep_score: int | None = None,
    hrv_threshold: float = 20.0,
    rhr_threshold: float = 7.0,
    sleep_threshold: int = SLEEP_SCORE_LOW,
) -> dict:
    """多信号红旗否决，确定性返回判定。

    返回:
      {
        "verdict": "ok" | "caution" | "hard_caution",
        "red_flags": ["hrv" | "rhr" | "sleep", ...],
        "flag_count": int,
        "skipped": ["hrv" | "rhr" | "sleep", ...]
      }
    """
    red_flags = []
    skipped = []

    if hrv_drop_pct is None:
        skipped.append("hrv")
    elif hrv_drop_pct >= hrv_threshold:
        red_flags.append("hrv")

    if rhr_spike_bpm is None:
        skipped.append("rhr")
    elif rhr_spike_bpm >= rhr_threshold:
        red_flags.append("rhr")

    if sleep_score is None:
        skipped.append("sleep")
    elif sleep_score < sleep_threshold:
        red_flags.append("sleep")

    n = len(red_flags)
    if n == 0:
        verdict = "ok"
    elif n == 1:
        verdict = "caution"
    else:
        verdict = "hard_caution"

    return {
        "verdict": verdict,
        "red_flags": red_flags,
        "flag_count": n,
        "skipped": skipped,
    }


def main():
    parser = argparse.ArgumentParser(description="计算今日身体准备度 (Readiness)")
    parser.add_argument("--hrv-drop", type=float, default=None, help="HRV 较 7 日均值跌幅百分比（如 20.0 表示跌 20%%）")
    parser.add_argument("--rhr-spike", type=float, default=None, help="静息心率较基线升高 bpm（如 7.0 表示升 7bpm）")
    parser.add_argument("--sleep-score", type=int, default=None, help="睡眠分 (0-100)")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    result = compute_readiness(
        hrv_drop_pct=args.hrv_drop,
        rhr_spike_bpm=args.rhr_spike,
        sleep_score=args.sleep_score,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Readiness Verdict: {result['verdict']}")
        print(f"Red Flags ({result['flag_count']}): {', '.join(result['red_flags']) if result['red_flags'] else 'None'}")
        print(f"Skipped Inputs: {', '.join(result['skipped']) if result['skipped'] else 'None'}")

    sys.exit(0)


if __name__ == "__main__":
    main()
