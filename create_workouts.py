"""
Create FIT workout files for COROS import testing.

NOTE: COROS does NOT support importing FIT workout files for scheduled training.
FIT import is only for completed activity history.

For COROS, the options are:
1. Create workouts manually in COROS App → Workout Library
2. Sync via TrainingPeaks / Final Surge integration
3. Use COROS Training Hub (training.coros.com)

This script creates standard FIT workout files that can be used with Garmin devices
or imported into platforms like TrainingPeaks which then sync to COROS.
"""

import os
import struct
from datetime import datetime, timedelta
from garmin_fit_sdk import Encoder, Profile

OUTPUT_DIR = r"c:\Users\ys\Downloads\exportSportData_451872081420763137_20260505\workouts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# FIT constants
MESG_NUM_FILE_ID = 0
MESG_NUM_WORKOUT = 26
MESG_NUM_WORKOUT_STEP = 27

# Sport
SPORT_RUNNING = 1

# File type
FILE_TYPE_WORKOUT = 5

# Intensity
INTENSITY_ACTIVE = 0
INTENSITY_REST = 1
INTENSITY_WARMUP = 2
INTENSITY_COOLDOWN = 3
INTENSITY_RECOVERY = 4
INTENSITY_INTERVAL = 5

# Duration type
DURATION_TIME = 0        # duration_value in ms (1000 = 1 second)
DURATION_DISTANCE = 1    # duration_value in 100*m (100 = 1 meter)
DURATION_OPEN = 5        # manual lap press
DURATION_REPEAT = 6      # repeat_until_steps_cmplt

# Target type
TARGET_SPEED = 0        # custom_target_value in 1000*m/s
TARGET_HEART_RATE = 1   # custom_target_value in bpm (offset by 100 if absolute)
TARGET_OPEN = 2         # no target
TARGET_CADENCE = 3

# Garmin epoch offset
GARMIN_EPOCH = datetime(1989, 12, 31, 0, 0, 0)


def pace_to_speed_ms(pace_str):
    """Convert pace string like '5:30' (min:sec per km) to m/s."""
    parts = pace_str.split(':')
    total_sec = int(parts[0]) * 60 + int(parts[1])
    return 1000.0 / total_sec


def speed_to_fit(speed_ms):
    """Convert speed in m/s to FIT format (1000 * m/s)."""
    return int(speed_ms * 1000)


def distance_to_fit(distance_km):
    """Convert distance in km to FIT format (100 * meters)."""
    return int(distance_km * 1000 * 100)


def time_to_fit(minutes):
    """Convert time in minutes to FIT format (milliseconds)."""
    return int(minutes * 60 * 1000)


def create_workout_fit(filename, workout_name, steps):
    """
    Create a FIT workout file.
    
    steps: list of dicts with keys:
        - type: 'warmup', 'active', 'rest', 'cooldown', 'interval', 'recovery', 'repeat'
        - duration_type: 'time', 'distance', 'open'
        - duration_value: minutes (for time) or km (for distance)
        - target_type: 'speed', 'heart_rate', 'open'
        - target_low: pace string like '5:30' or HR in bpm
        - target_high: pace string like '5:00' or HR in bpm
        - repeat_from: step index for repeat
        - repeat_count: number of repeats
        - notes: optional text
    """
    encoder = Encoder()
    
    # Timestamp
    now = datetime(2026, 5, 6, 6, 0, 0)  # fixed time for testing
    timestamp = int((now - GARMIN_EPOCH).total_seconds())
    
    # 1. File ID
    file_id = {
        'mesg_num': MESG_NUM_FILE_ID,
        'type': FILE_TYPE_WORKOUT,
        'manufacturer': 1,  # Garmin
        'product': 1,
        'serial_number': 12345,
        'time_created': timestamp,
    }
    encoder.write_mesg(file_id)
    
    # Count valid steps
    num_steps = len(steps)
    
    # 2. Workout message
    workout = {
        'mesg_num': MESG_NUM_WORKOUT,
        'sport': SPORT_RUNNING,
        'num_valid_steps': num_steps,
        'wkt_name': workout_name,
    }
    encoder.write_mesg(workout)
    
    # 3. Workout steps
    for i, step in enumerate(steps):
        step_mesg = {
            'mesg_num': MESG_NUM_WORKOUT_STEP,
            'message_index': i,
        }
        
        # Intensity
        intensity_map = {
            'warmup': INTENSITY_WARMUP,
            'active': INTENSITY_ACTIVE,
            'rest': INTENSITY_REST,
            'cooldown': INTENSITY_COOLDOWN,
            'recovery': INTENSITY_RECOVERY,
            'interval': INTENSITY_INTERVAL,
        }
        
        if step.get('type') == 'repeat':
            # Repeat step
            step_mesg['duration_type'] = DURATION_REPEAT
            step_mesg['duration_value'] = step['repeat_from']  # step index to repeat from
            step_mesg['target_type'] = TARGET_OPEN
            step_mesg['target_value'] = step['repeat_count']  # number of repeats
            step_mesg['intensity'] = INTENSITY_ACTIVE
        else:
            step_mesg['intensity'] = intensity_map.get(step.get('type', 'active'), INTENSITY_ACTIVE)
            
            # Duration
            dur_type = step.get('duration_type', 'open')
            if dur_type == 'time':
                step_mesg['duration_type'] = DURATION_TIME
                step_mesg['duration_value'] = time_to_fit(step['duration_value'])
            elif dur_type == 'distance':
                step_mesg['duration_type'] = DURATION_DISTANCE
                step_mesg['duration_value'] = distance_to_fit(step['duration_value'])
            else:
                step_mesg['duration_type'] = DURATION_OPEN
                step_mesg['duration_value'] = 0
            
            # Target
            tgt_type = step.get('target_type', 'open')
            if tgt_type == 'speed':
                step_mesg['target_type'] = TARGET_SPEED
                step_mesg['target_value'] = 0  # custom
                # Speed: FIT uses m/s * 1000
                # Note: for speed target, "low" means slower pace (lower speed), "high" means faster pace (higher speed)
                low_speed = pace_to_speed_ms(step['target_low'])   # slower pace = lower speed value
                high_speed = pace_to_speed_ms(step['target_high']) # faster pace = higher speed value
                step_mesg['custom_target_value_low'] = speed_to_fit(min(low_speed, high_speed))
                step_mesg['custom_target_value_high'] = speed_to_fit(max(low_speed, high_speed))
            elif tgt_type == 'heart_rate':
                step_mesg['target_type'] = TARGET_HEART_RATE
                step_mesg['target_value'] = 0  # custom
                # HR: offset by 100 for absolute BPM
                step_mesg['custom_target_value_low'] = int(step['target_low']) + 100
                step_mesg['custom_target_value_high'] = int(step['target_high']) + 100
            else:
                step_mesg['target_type'] = TARGET_OPEN
                step_mesg['target_value'] = 0
                step_mesg['custom_target_value_low'] = 0
                step_mesg['custom_target_value_high'] = 0
        
        if step.get('notes'):
            step_mesg['notes'] = step['notes']
        
        encoder.write_mesg(step_mesg)
    
    # Close and write file
    fit_data = encoder.close()
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(fit_data)
    print(f"Created: {filepath} ({len(fit_data)} bytes)")
    return filepath


def create_day1_easy_run():
    """Day 1 (Tuesday): Easy Run 8-10km @ 5:40-6:00"""
    steps = [
        {
            'type': 'warmup',
            'duration_type': 'distance',
            'duration_value': 1.0,  # 1km warmup
            'target_type': 'speed',
            'target_low': '6:30',   # slow end
            'target_high': '6:00',  # fast end
            'notes': '热身慢跑',
        },
        {
            'type': 'active',
            'duration_type': 'distance',
            'duration_value': 7.0,  # 7km main
            'target_type': 'speed',
            'target_low': '6:00',
            'target_high': '5:40',
            'notes': '轻松跑主体 配速5:40-6:00',
        },
        {
            'type': 'cooldown',
            'duration_type': 'distance',
            'duration_value': 1.0,  # 1km cooldown
            'target_type': 'speed',
            'target_low': '6:30',
            'target_high': '6:00',
            'notes': '收操慢跑',
        },
    ]
    return create_workout_fit(
        'Week01_D1_EasyRun_9km.fit',
        'W1D1 轻松跑 9km',
        steps
    )


def create_day2_speed_with_strides():
    """Day 2 (Thursday): Easy Run 8km + 4x strides"""
    steps = [
        {
            'type': 'warmup',
            'duration_type': 'distance',
            'duration_value': 2.0,
            'target_type': 'speed',
            'target_low': '6:30',
            'target_high': '6:00',
            'notes': '热身慢跑 2km',
        },
        {
            'type': 'active',
            'duration_type': 'distance',
            'duration_value': 4.0,
            'target_type': 'speed',
            'target_low': '5:50',
            'target_high': '5:30',
            'notes': '轻松跑主体 4km',
        },
        # Strides block: 4 x (200m fast + 200m recovery)
        {
            'type': 'interval',
            'duration_type': 'distance',
            'duration_value': 0.2,  # 200m
            'target_type': 'speed',
            'target_low': '5:00',
            'target_high': '4:30',
            'notes': '加速跑 200m',
        },
        {
            'type': 'recovery',
            'duration_type': 'distance',
            'duration_value': 0.2,  # 200m recovery
            'target_type': 'open',
            'notes': '慢跑恢复 200m',
        },
        {
            'type': 'repeat',
            'repeat_from': 2,  # repeat from step index 2 (the interval)
            'repeat_count': 4, # 4 repeats total
        },
        {
            'type': 'cooldown',
            'duration_type': 'distance',
            'duration_value': 1.5,
            'target_type': 'speed',
            'target_low': '6:30',
            'target_high': '6:00',
            'notes': '收操慢跑 1.5km',
        },
    ]
    return create_workout_fit(
        'Week01_D2_EasyStrides_9km.fit',
        'W1D2 轻松跑+加速 9km',
        steps
    )


def create_day3_long_run():
    """Day 3 (Sunday): Long Run 13-15km @ 5:30-5:50"""
    steps = [
        {
            'type': 'warmup',
            'duration_type': 'distance',
            'duration_value': 2.0,
            'target_type': 'speed',
            'target_low': '6:00',
            'target_high': '5:50',
            'notes': '热身跑 2km',
        },
        {
            'type': 'active',
            'duration_type': 'distance',
            'duration_value': 11.0,
            'target_type': 'speed',
            'target_low': '5:50',
            'target_high': '5:20',
            'notes': '长距离跑主体 11km 配速5:20-5:50',
        },
        {
            'type': 'cooldown',
            'duration_type': 'distance',
            'duration_value': 2.0,
            'target_type': 'speed',
            'target_low': '6:30',
            'target_high': '6:00',
            'notes': '收操慢跑 2km',
        },
    ]
    return create_workout_fit(
        'Week01_D3_LongRun_15km.fit',
        'W1D3 长距离跑 15km',
        steps
    )


def verify_workout(filepath):
    """Read back and verify a workout FIT file."""
    from garmin_fit_sdk import Decoder, Stream
    
    stream = Stream.from_file(filepath)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    
    if errors:
        print(f"  Errors: {errors}")
    
    file_ids = messages.get('file_id_mesgs', [])
    workouts = messages.get('workout_mesgs', [])
    workout_steps = messages.get('workout_step_mesgs', [])
    
    print(f"\n  Verifying: {os.path.basename(filepath)}")
    
    if file_ids:
        fid = file_ids[0]
        print(f"  File Type: {fid.get('type')}")
    
    if workouts:
        wkt = workouts[0]
        print(f"  Workout: {wkt.get('wkt_name')}")
        print(f"  Sport: {wkt.get('sport')}")
        print(f"  Steps: {wkt.get('num_valid_steps')}")
    
    if workout_steps:
        for i, step in enumerate(workout_steps):
            dur_type = step.get('duration_type', '')
            dur_val = step.get('duration_value', 0)
            intensity = step.get('intensity', '')
            target_type = step.get('target_type', '')
            
            # Format duration
            if 'time' in str(dur_type):
                dur_str = f"{dur_val/60000:.1f} min"
            elif 'distance' in str(dur_type):
                dur_str = f"{dur_val/100000:.1f} km"
            elif 'repeat' in str(dur_type):
                dur_str = f"repeat from step {dur_val}"
            else:
                dur_str = f"{dur_type}={dur_val}"
            
            # Format target
            low = step.get('custom_target_value_low', 0) 
            high = step.get('custom_target_value_high', 0)
            if 'speed' in str(target_type) and high and high > 0:
                # Convert back to pace
                low_pace_s = 1000 / (low / 1000) if low > 0 else 0
                high_pace_s = 1000 / (high / 1000) if high > 0 else 0
                low_p = f"{int(high_pace_s//60)}:{int(high_pace_s%60):02d}"  # higher speed = faster pace
                high_p = f"{int(low_pace_s//60)}:{int(low_pace_s%60):02d}"   # lower speed = slower pace
                target_str = f"pace {low_p}-{high_p}"
            elif 'heart_rate' in str(target_type):
                target_str = f"HR {low-100}-{high-100}"
            else:
                target_str = str(target_type)
            
            print(f"  Step {i}: {intensity} | {dur_str} | {target_str}")


if __name__ == "__main__":
    print("=" * 60)
    print("Creating FIT Workout Files")
    print("=" * 60)
    
    f1 = create_day1_easy_run()
    f2 = create_day2_speed_with_strides()
    f3 = create_day3_long_run()
    
    print("\n" + "=" * 60)
    print("Verifying created files")
    print("=" * 60)
    
    verify_workout(f1)
    verify_workout(f2)
    verify_workout(f3)
    
    print("\n" + "=" * 60)
    print("IMPORTANT: COROS Import Notes")
    print("=" * 60)
    print("""
⚠️  COROS 不支持直接导入 FIT 训练计划文件！
    
FIT 文件导入功能仅用于上传"已完成的历史运动记录"。

要将训练课表导入 COROS，推荐以下方式：

1. 【推荐】COROS App 手动创建
   → 个人资料 → 训练课程 → 新建训练
   → 按照上面的配速区间手动编辑

2. 【推荐】通过 TrainingPeaks 同步
   → 在 TrainingPeaks 创建训练计划
   → COROS App → 设置 → 第三方应用 → TrainingPeaks
   → 自动同步未来 7 天课表到手表

3. COROS Training Hub (training.coros.com)
   → 网页端创建/管理训练计划

这些 FIT 文件可以：
✅ 导入 Garmin Connect → 放入手表 NewFiles 文件夹
✅ 上传到 TrainingPeaks → 通过 TP 同步到 COROS
✅ 作为训练参考，在 COROS App 中手动创建对应课程
""")
