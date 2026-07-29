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
    ┌─────────────────────────────────┐
    │  GET_SPORT_RECORDS              │
    │  GET_ACTIVITY_DETAIL            │
    │  GET_ACTIVITY_LAP_DATA          │
    │  GET_FIT_DOWNLOAD_URLS          │
    │  DOWNLOAD_FIT_FILES             │
    │  GET_HRV                        │
    │  GET_SLEEP_DATA                 │
    │  GET_RESTING_HR                 │
    │  GET_STRESS_LEVEL               │
    │  GET_FITNESS_OVERVIEW           │
    │  GET_TRAINING_LOAD              │
    │  GET_RECOVERY_STATUS            │
    │  GET_USER_INFO                  │
    │  GET_MENSTRUATION_CYCLES        │
    │  ... (其余辅助接口)              │
    └─────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
 COROS       Garmin
 适配器      适配器（占位，未实现）
```

---

## 一、高驰（COROS）适配器

**状态**：✅ 正式支持  
**MCP 端点**：`https://mcpcn.coros.com/mcp`  
**认证方式**：OAuth 2.0（authorization_code flow）  
**安装方式**：见 USER_GUIDE.md 第二章

### 1.1 全量工具映射表（22 个 COROS MCP 工具）

> 状态标注说明：
> - `✅ 已验证（产品在用）`：已在生产环境中调通并稳定运行。
> - `◻️ 官方提供 · 未在产品验证`：COROS 官方 `tools/list` 提供的有效只读接口，产品暂未集成。

#### 1. 活动与分段（Activity & Lap Data）

| 抽象接口 | COROS MCP 工具名 | 关键参数 | 状态 | 说明 |
|---|---|---|---|---|
| `GET_SPORT_RECORDS` | `querySportRecords` | `startDate`, `endDate`, `sportTypeCodes`, `limit`, `timezone` | ✅ 已验证（产品在用） | 活动列表。返回格式化文本而非 JSON，格式如 `LabelId: <id> \| SportType: 100` |
| `GET_ACTIVITY_DETAIL` | `getActivityDetail` | `labelId`, `sportType` | ✅ 已验证（产品在用） | 单次详情，含 Training Load、Aerobic/Anaerobic TE、Training Focus、**Perceived Effort（主观 RPE）** |
| `GET_ACTIVITY_LAP_DATA` | `queryActivityLapData` | `labelId`, `sportType` | ✅ 已验证（产品在用） | 逐圈数据：配速/心率/功率/触地时间/步频/步幅/调整配速及 lapGroups |
| `GET_CUSTOM_ACTIVITY_LAP_DATA` | `queryCustomActivityLapData` | `labelId`, `sportType`, `startTimestamp`, `endTimestamp` | ◻️ 官方提供 · 未在产品验证 | 自定义时间窗口逐圈数据 |
| `GET_FIT_DOWNLOAD_URLS` | `queryActivityFitFileDownloadUrls` | `labelId`, `sportType` | ✅ 已验证（产品在用） | OSS FIT 直链（含 GPS + 逐秒流），**限 50 文件/日** |
| `DOWNLOAD_FIT_FILES` | `downloadActivityFitFiles` | `labelId`, `sportType` | ✅ 已验证（产品在用） | 直接下载二进制 FIT 文件 |
| `ANALYZE_ACTIVITY` | `analyzeActivityDetail` | `labelId`, `sportType` | ◻️ 官方提供 · 未在产品验证 | COROS 官方生成的文字分析摘要 |

#### 2. 日健康（Daily Health Metrics）

| 抽象接口 | COROS MCP 工具名 | 关键参数 | 状态 | 说明 |
|---|---|---|---|---|
| `GET_HRV` | `querySleepHrv` | `days`, `timezone` | ✅ 已验证（产品在用） | HRV 日均 + normal range + baseline + 时序。**（旧工具 queryHrvAssessment 已被 COROS 官方删除，现统一调此接口）** |
| `GET_SLEEP_DATA` | `querySleepData` | `days`, `timezone` | ✅ 已验证（产品在用） | 睡眠分及深睡/浅睡/REM/清醒时长 |
| `GET_RESTING_HR` | `queryRestingHeartRate` | `days`, `timezone` | ✅ 已验证（产品在用） | 静息心率趋势 |
| `GET_STRESS_LEVEL` | `queryStressLevel` | `days`, `timezone` | ✅ 已验证（产品在用） | 每日平均压力水平 |
| `GET_DAILY_HEALTH_DATA` | `queryDailyHealthData` | `days`, `timezone` | ◻️ 官方提供 · 未在产品验证 | 每日综合健康数据 |
| `GET_AVG_HR` | `queryAvgHeartRate` | `days`, `timezone` | ◻️ 官方提供 · 未在产品验证 | 全天平均心率 |
| `GET_HEALTH_CHECK_SERIES` | `queryHealthCheckTimeSeries` | `days`, `timezone` | ◻️ 官方提供 · 未在产品验证 | 一键体检健康检测时序数据 |
| `GET_STRESS_SERIES` | `queryStressTimeSeries` | `days`, `timezone` | ◻️ 官方提供 · 未在产品验证 | 日内高频压力时序 |

#### 3. 评估与账户（Assessment & Account）

| 抽象接口 | COROS MCP 工具名 | 关键参数 | 状态 | 说明 |
|---|---|---|---|---|
| `GET_FITNESS_OVERVIEW` | `queryFitnessAssessmentOverview` | — | ✅ 已验证（产品在用） | VO2max / 跑力 / 阈值配速 / 5K~全马预测成绩 |
| `GET_TRAINING_LOAD` | `queryTrainingLoadAssessment` | `days` | ✅ 已验证（产品在用） | 每日短期(ATL)/长期(CTL)负荷 + **Load Ratio（现成 ACWR）** + 评语 |
| `GET_RECOVERY_STATUS` | `queryRecoveryStatus` | `timezone` | ✅ 已验证（产品在用） | 恢复% / 恢复 level / 预计完全恢复小时数 |
| `GET_USER_INFO` | `queryUserInfo` | — | ✅ 已验证（产品在用） | 身高 / 体重 / 生日 / 性别 |
| `GET_TRAINING_SCHEDULE` | `queryTrainingSchedule` | `startDate`, `endDate` | ◻️ 官方提供 · 未在产品验证 | 高驰 App 内已有计划 |
| `GET_DEVICES` | `queryDevices` | — | ◻️ 官方提供 · 未在产品验证 | 已绑定硬件设备列表 |
| `GET_MENSTRUATION_CYCLES` | `queryMenstruationCycles` | `timezone` | ✅ 已验证（产品在用） | 女性月经周期相位及下次经期预测 |

---

### 1.2 使用注意（已知坑）

1. **`querySportRecords` 高频 404 flaky**：连续新建 MCP 会话时，该工具约有 40%-50% 概率偶发 404 错误。主数据同步代码必须带退避重试（retry_on_404）。
2. **`queryActivityFitFileDownloadUrls` 额度限制**：COROS 对 FIT 直链生成接口实行**每日最多 50 文件**的配额限制，请勿大批量频繁拉取全量历史 FIT。
3. **Token 有效期与一次性轮换**：OAuth `access_token` 有效期约为 30 天；`refresh_token` 在使用后会**一次性轮换**，新 token 生成后旧 token 立即失效。

---

### 1.3 数据可用范围与能力边界

| 数据类型 | 开放深度与能力 | 备注 / 注意事项 |
|---|---|---|
| 运动记录 | 支持分段（lap）逐圈数据 (`queryActivityLapData`) | 包含逐圈配速、心率、触地时间、步频、步幅、调整配速及分段分组 |
| FIT 文件 | 支持 FIT 直链及二进制下载 (`queryActivityFitFileDownloadUrls` / `downloadActivityFitFiles`) | 包含 GPS + 逐秒轨迹流（受每日 50 文件配额限制）|
| 训练负荷 | 提供官方 Load Ratio 负荷比 (`queryTrainingLoadAssessment`) | 官方现成 ACWR，无需自行手动计算 ATL/CTL 比例 |
| 工具可枚举 | 具备 `tools/list` 功能 | 已通过 live 探测确认 22 个可调用工具 |
| 主观 RPE | 包含主观评分 (`getActivityDetail` 之 `perceived_effort`) | AI 优先读取设备字段，缺失时再询问用户 |

#### ⚠️ 已确认不开放：写工具

COROS MCP 目前**全为只读接口**。调用以下写入/修改类工具：
- `updateTrainingPlan`
- `queryTrainingPlanDetail`
- `createTrainingPlan`
- `deleteTrainingPlan`

均返回 `-32602 Unknown tool`。因此**将课表自动回写至高驰 App/手表目前无法实现**。AI 只能生成 Markdown 课表或打卡图供用户查阅。

---

## 二、佳明（Garmin）适配器

**状态**：🚧 占位，未实现  
**说明**：当前版本尚未实现 Garmin MCP 接入。

### 2.1 规划接口（占位）

| 抽象接口 | 预计 Garmin 工具 | 状态 |
|---|---|---|
| `GET_SPORT_RECORDS` | `mcp__garmin__getActivities` | 🚧 占位未实现 |
| `GET_ACTIVITY_DETAIL` | `mcp__garmin__getActivityDetail` | 🚧 占位未实现 |
| `GET_SLEEP_DATA` | `mcp__garmin__getSleepData` | 🚧 占位未实现 |
| `GET_HRV` | `mcp__garmin__getHRVStatus` | 🚧 占位未实现 |

---

## 三、无 MCP 手动模式

对于无 COROS 手表或使用不支持 MCP 运行环境的用户，可使用项目内置的 `parse_fit.py` 脚本：

```bash
# 解析单个 .fit 文件或整个目录，生成 runs.csv 供 AI 识别
python parse_fit.py --input <FIT文件或目录> [--out runs.csv] [--summary]
```

生成 `runs.csv` 后，用户可将其粘贴发给 AI，AI 仍可完整进行 VDOT 计算、课表生成与周复盘。

---

*本文件由 AI Running Coach v2.2.0 维护 · 契约变更请同步更新 SKILL.md 与 USER_GUIDE.md*
