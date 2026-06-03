# 🔌 设备适配器配置

> **说明**：本文件定义各设备 MCP 工具与 AI 教练抽象接口的映射关系。  
> AI 读取本文件后，会自动选择与用户手表匹配的适配器。  
> 新增设备支持时，只需在本文件追加适配器配置，无需修改 SKILL.md 核心逻辑。

---

## 适配器架构说明

```
AI 教练核心逻辑（SKILL.md）
         │
         ▼
  抽象工具接口层（本文件定义）
    ┌─────────────────┐
    │  GET_SPORT_RECORDS      │
    │  GET_HEALTH_METRICS     │
    │  GET_RECOVERY_STATUS    │
    │  GET_FITNESS_OVERVIEW   │
    │  GET_SLEEP_DATA         │
    │  GET_HRV               │
    │  GET_STRESS_LEVEL       │
    │  GET_DEVICES            │
    │  GET_USER_INFO          │
    │  ANALYZE_ACTIVITY       │
    └─────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
 COROS       Garmin
 适配器      适配器（开发中）
```

---

## 一、高驰（COROS）适配器

**状态**：✅ 正式支持  
**MCP 端点**：`https://mcpcn.coros.com/mcp`  
**认证方式**：OAuth 2.0（authorization_code flow）  
**安装方式**：见 USER_GUIDE.md 第二章

### 1.1 工具映射表

| 抽象接口 | COROS MCP 工具 | 关键参数 | 说明 |
|---------|--------------|---------|------|
| `GET_SPORT_RECORDS` | `mcp__coros__querySportRecords` | `startDate`, `endDate`, `sportType` | 拉取运动记录列表 |
| `GET_ACTIVITY_DETAIL` | `mcp__coros__getActivityDetail` | `activityId` | 获取单次训练详情 |
| `ANALYZE_ACTIVITY` | `mcp__coros__analyzeActivityDetail` | `activityId` | AI 分析单次训练 |
| `GET_HEALTH_METRICS` | `mcp__coros__queryDailyHealthData` | `startDate`, `endDate` | 每日健康数据 |
| `GET_RESTING_HR` | `mcp__coros__queryRestingHeartRate` | `startDate`, `endDate` | 静息心率趋势 |
| `GET_AVG_HR` | `mcp__coros__queryAvgHeartRate` | `startDate`, `endDate` | 平均心率数据 |
| `GET_RECOVERY_STATUS` | `mcp__coros__queryRecoveryStatus` | `startDate`, `endDate` | 恢复状态评分 |
| `GET_SLEEP_DATA` | `mcp__coros__querySleepData` | `startDate`, `endDate` | 睡眠质量数据 |
| `GET_HRV` | `mcp__coros__queryHrvAssessment` | `startDate`, `endDate` | HRV 心率变异性 |
| `GET_STRESS_LEVEL` | `mcp__coros__queryStressLevel` | `startDate`, `endDate` | 压力水平评分 |
| `GET_FITNESS_OVERVIEW` | `mcp__coros__queryFitnessAssessmentOverview` | `startDate`, `endDate` | 综合体能评估（含 VO2max）|
| `GET_TRAINING_LOAD` | `mcp__coros__queryTrainingLoadAssessment` | `startDate`, `endDate` | 训练负荷评估（ATL/CTL）|
| `GET_TRAINING_SCHEDULE` | `mcp__coros__queryTrainingSchedule` | `startDate`, `endDate` | 高驰 App 内训练计划 |
| `GET_DEVICES` | `mcp__coros__queryDevices` | — | 已绑定设备列表 |
| `GET_USER_INFO` | `mcp__coros__queryUserInfo` | — | 用户基本信息 |

### 1.2 数据字段说明

**运动记录（GET_SPORT_RECORDS）**

| 字段 | 含义 | 单位 |
|------|------|------|
| `sportType` | 运动类型（100=跑步，101=室内跑步，以此类推） | 枚举值 |
| `totalDistance` | 总距离 | 米 |
| `totalTime` | 总时长 | 秒 |
| `avgPace` | 平均配速 | 秒/公里 |
| `avgHeartRate` | 平均心率 | bpm |
| `maxHeartRate` | 最大心率 | bpm |
| `totalCalories` | 总消耗卡路里 | kcal |
| `avgCadence` | 平均步频 | 步/分钟 |
| `trainingLoad` | 单次训练负荷 | 无量纲 |

**体能评估（GET_FITNESS_OVERVIEW）**

| 字段 | 含义 | 说明 |
|------|------|------|
| `vo2max` | 最大摄氧量估算值 | VDOT 推算的交叉验证来源 |
| `fitnessLevel` | 体能等级 | 高驰内部评分 |
| `aerobicTrainingEffect` | 有氧训练效果 | 1-5 分 |
| `anaerobicTrainingEffect` | 无氧训练效果 | 1-5 分 |

**训练负荷（GET_TRAINING_LOAD）**

| 字段 | 含义 | AI 使用规则 |
|------|------|-----------|
| `atl` | 急性训练负荷（短期，约7天） | ATL/CTL > 1.3 → 插入恢复日 |
| `ctl` | 慢性训练负荷（长期，约42天） | CTL 稳定上升 → 训练效果良好 |
| `tsb` | 训练压力平衡（TSB = CTL - ATL） | TSB < -20 → 疲劳预警 |

### 1.3 数据可用范围

| 数据类型 | 最大回溯范围 | 备注 |
|---------|------------|------|
| 运动记录 | 账号注册以来所有数据 | 受设备同步状态影响 |
| 每日健康 | 约 3-6 个月 | 取决于 App 保留策略 |
| 睡眠 / HRV | 约 3-6 个月 | 同上 |
| 体能评估 | 约 3-6 个月 | 同上 |
| 训练负荷 | 约 3-6 个月 | 同上 |

---

## 二、佳明（Garmin）适配器

**状态**：🚧 开发中  
**预计支持版本**：v2.0  
**MCP 端点**：待定（预计使用 Garmin Connect API）  
**认证方式**：OAuth 2.0

### 2.1 工具映射表（规划）

| 抽象接口 | 预计 Garmin MCP 工具 | 状态 |
|---------|-------------------|------|
| `GET_SPORT_RECORDS` | `mcp__garmin__getActivities` | 🚧 规划中 |
| `GET_ACTIVITY_DETAIL` | `mcp__garmin__getActivityDetail` | 🚧 规划中 |
| `GET_HEALTH_METRICS` | `mcp__garmin__getDailyStats` | 🚧 规划中 |
| `GET_RESTING_HR` | `mcp__garmin__getRestingHeartRate` | 🚧 规划中 |
| `GET_RECOVERY_STATUS` | `mcp__garmin__getBodyBattery` | 🚧 规划中 |
| `GET_SLEEP_DATA` | `mcp__garmin__getSleepData` | 🚧 规划中 |
| `GET_HRV` | `mcp__garmin__getHRVStatus` | 🚧 规划中 |
| `GET_FITNESS_OVERVIEW` | `mcp__garmin__getVO2MaxStatus` | 🚧 规划中 |
| `GET_TRAINING_LOAD` | `mcp__garmin__getTrainingLoad` | 🚧 规划中 |
| `GET_USER_INFO` | `mcp__garmin__getUserProfile` | 🚧 规划中 |

### 2.2 对应关系说明

Garmin 与 COROS 的核心指标对应关系：

| COROS 指标 | Garmin 对应指标 | 注意事项 |
|-----------|--------------|---------|
| 恢复状态评分 | Body Battery | 算法不同，数值不可直接对比 |
| VO2max | VO2 Max 状态 | 估算方法略有差异 |
| 训练负荷 ATL/CTL | Training Load Focus | 字段命名不同，需归一化处理 |
| 平均步频 | Average Cadence | 单位相同（步/分钟） |

---

## 三、新增适配器指南

如果你想为其他设备（苹果 Watch、Polar、Suunto 等）贡献适配器，请参考 CONTRIBUTING.md 中的"适配器贡献规范"章节，并按照以下模板追加：

```markdown
## N、[设备名称]适配器

**状态**：🚧 开发中 / ✅ 正式支持
**MCP 端点**：[填写端点URL]
**认证方式**：[填写认证方式]

### N.1 工具映射表

| 抽象接口 | [设备] MCP 工具 | 关键参数 | 说明 |
|---------|--------------|---------|------|
| `GET_SPORT_RECORDS` | [对应工具名] | [参数] | [说明] |
...
```

---

*本文件由 AI Running Coach v1.1.0 维护 · 如有设备适配贡献，请参阅 CONTRIBUTING.md*
