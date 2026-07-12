# AI Running Coach

> An AI running coach built on classic training science — reads your COROS watch data, estimates your fitness, and generates marathon plans that adapt week by week. Runs as a skill on Claude (or any capable LLM in manual mode).
>
> 基于 Claude + 高驰 MCP 的智能跑步训练系统，理论驱动 · 数据实时 · 课表动态调整（[中文文档见下半部分](#ai-running-coach-中文)）

---

## What is this?

This repo is the **open methodology layer** behind [Pacer](https://pacer.xiaolou.space/en), a hosted AI running coach. Everything the coach "believes" about training lives here in auditable form: the workflow rules, the pace/load math conventions, and a structured knowledge-card library covering injury rehab, strength work, and race nutrition.

You can run it yourself as a **Claude skill**: it reads your training history from a COROS watch via COROS's official MCP server (read-only), estimates your VDOT from real runs (no time-trial needed), and generates a race training plan built on three classic methodologies — then re-scores and adjusts it every week based on what you actually ran.

**Core ideas:**

- ⌚ **No file uploads** — activity and physiological data come straight from the watch via MCP.
- 🧠 **Structured knowledge cards** — injury triage (Level 0–2 grading), strength sessions, and race-day nutrition are routed from in-repo cards, not hallucinated.
- 🏃 **VDOT from history** — fitness is estimated from your real runs; no all-out test required.
- 📅 **One-line weekly update** — one prompt scores last week's execution, checks fatigue, and adjusts next week.
- 🛡️ **Safety over compliance** — resting-HR / HRV red flags and the 10% mileage rule are enforced, not suggested.
- 🌍 **Fully redistributable** — no copyrighted source material included; clone it and run your own coach.

## Quick start (English)

1. **Model**: use a strong model for plan generation (Claude Opus/Sonnet class). Weaker models are fine for day-to-day analysis.
2. **Install the COROS MCP** (~3 min) — in Claude Code / Claude Desktop, add the MCP server `https://mcpcn.coros.com/mcp`, then confirm `coros` shows up under `/mcp`. No COROS watch? Manual mode works: paste your training data instead.
3. **Generate your plan** — send:

```
Initialize the AI running coach. Read my last 6 weeks of COROS training data and build my plan.

About me:
- Goal race: [half marathon / marathon]
- Target time: [e.g. 1:45:00]
- Training days per week: [e.g. 4]
- Race date: [e.g. 2026-11-15]
```

4. **Each week** — just say: `Update this week's training data`.

## Training theory

| Theory | Source | What it contributes |
|--------|--------|---------------------|
| VDOT system | Jack Daniels, *Daniels' Running Formula* (2013) | Precise five-zone pace prescription |
| Cumulative fatigue | Luke Humphrey, *Hansons Marathon Method* (2012) | Sane long-run ceilings |
| 80/20 intensity split | Matt Fitzgerald, *80/20 Running* (2014) | Keeps you out of the gray zone |
| 10% progression rule | Hal Higdon, *Marathon* (2011) | Safe ramp-up and taper |

## This repo vs. Pacer (the hosted app)

- **This repo** = the methodology, as a self-hostable skill. Bring your own LLM; your data stays in your own Claude/COROS accounts.
- **[Pacer](https://pacer.xiaolou.space/en)** = the same logic productized: one-tap COROS sign-in (official OAuth, read-only), deterministic pace/load math in code (the LLM never does arithmetic), weekly auto-review, weather- and readiness-aware daily advice. Free while early.

> **Language note**: the detailed docs below are currently in Chinese (an English pass is in progress). The skill itself works fine in English conversations — the coach replies in whatever language you use.

---

<a name="ai-running-coach-中文"></a>

# AI Running Coach（中文）

## 这是什么

AI Running Coach 是一个运行在 Claude 上的跑步训练 Skill。它通过高驰（COROS）MCP 实时读取你的手表数据，结合丹尼尔斯、汉森、80/20 三大经典训练理论，**并通过独创的分层知识卡片库涵盖了伤病康复、力量体能和运动营养**，为你生成和动态调整专属训练计划。

**核心特点：**
- ⌚ **无需上传文件**——直接通过 MCP 从手表读取实时运动记录和生理数据。
- 🧠 **内置专业知识卡片（v2.1 新特性）**——自带涵盖伤病诊断、力量动作、赛事营养的结构化知识卡片。无需笨重的外挂数据库，AI 即可在对话中精准路由并调用。
- 🏃 **免去繁琐测试**——AI 从运动历史自动推算 VDOT，无需单独安排全力测试跑。
- 📅 **每周一句话更新**——`更新本周训练数据` 即可完成课表执行度打分、疲劳判断和下周计划自动调整。
- 🛡️ **伤病与疲劳保护机制**——实时监控静息心率与 HRV，结合专业的伤病分级模型（Level 0-2），察觉过载立刻干预。
- 📊 **一键生成周打卡图**——`生成本周打卡图` 输出 1080×1440 小红书规格分享图，含课表实录、AI 复盘、下周预览，支持导出 PNG。
- 🌍 **全量合规开源**——去除了训练理论原始版权材料的依赖，彻底清除了分发障碍，任何人都可以一键克隆并部署自己的专属教练。

---

## 推荐运行环境与模型

> AI 会在生成课表前自动检查模型能力。**如果当前模型不足以生成完整训练计划，AI 会直接告知并给出替代建议，不降低课表质量。**

### 环境支持（MCP 自动同步）

MCP 是手表数据自动同步的关键协议，目前支持范围如下：

| 运行环境 | MCP 自动拉取 | 推荐度 |
|---------|------------|------|
| **Claude Code 桌面版 / CLI** | ✅ 完整支持 | ⭐⭐⭐ 首选 |
| **Claude 桌面应用（Desktop App）** | ✅ 完整支持 | ⭐⭐⭐ 首选 |
| **Claude 网页版（claude.ai）** | ⚠️ 需手动配置 | ⭐⭐ |
| **Cursor / Windsurf 等 IDE** | ✅ 支持 MCP 插件 | ⭐⭐ 适合开发者 |
| **Gemini / DeepSeek / Kimi 等** | ❌ 暂不支持 MCP | ⭐ 手动模式可用 |

> **无 MCP 时**：手动粘贴训练数据，AI 仍可完整分析和生成课表，但无法每周自动同步。

### 主流模型适配一览

MCP 列表示能否自动同步手表数据；❌ 表示需手动粘贴训练数据。

| 模型 | 提供方 | MCP | 课表生成 | 日常分析 | 中文 |
|------|--------|:---:|:-------:|:-------:|:----:|
| **claude-opus-4-7** 【推荐】 | Anthropic | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **claude-sonnet-4-6** 【推荐】 | Anthropic | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| claude-haiku-4-5 | Anthropic | ✅ | ⭐ | ⭐⭐ | ⭐⭐ |
| **Gemini 2.5 Pro** 【推荐】 | Google | ❌ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Gemini 2.5 Flash | Google | ❌ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **DeepSeek V3** 【推荐】 | 深度求索 | ❌ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| DeepSeek R1 | 深度求索 | ❌ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Kimi k2 | 月之暗面 | ❌ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Qwen3（通义千问）| 阿里云 | ❌ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| GPT-4o | OpenAI | ❌ | ⭐⭐ | ⭐⭐ | ⭐⭐ |

### 最佳配置

```
# 完整功能（推荐）
环境：Claude Code 桌面版
生成课表：Claude Opus 4.7      ← 推荐
日常更新：Claude Sonnet 4.6    ← 推荐

# 手动模式（无 MCP，自行粘贴数据）
国际用户：Gemini 2.5 Pro       ← 推荐
国内用户：DeepSeek V3          ← 推荐
```

---

## 支持设备

| 设备 | 状态 | 说明 |
|------|------|------|
| 高驰（COROS）全系列 | ✅ 正式支持 | 通过官方 MCP 实时拉取数据 |
| 佳明（Garmin）| 🚧 开发中 | v2.0 计划支持 |
| 苹果 Watch | 🔮 规划中 | 待评估 |

---

## 快速开始

### 第一步：确认模型

生成完整课表前，请先切换到 **Claude Opus 4.7** 或 **Claude Sonnet 4.6**。

### 第二步：安装高驰 MCP（约 3 分钟）

在 Claude Code 中输入：

```
帮我安装高驰 COROS MCP，地址是 https://mcpcn.coros.com/mcp
```

重启后输入 `/mcp` 确认 `coros` 出现在列表中。

### 第三步：生成你的训练计划

复制以下内容，填写你的信息后发给 Claude：

```
请帮我初始化 AI 跑步教练系统，读取我高驰手表最近6周的训练数据，为我生成专属课表。

我的信息：
- 目标比赛：[半程马拉松 / 全程马拉松]
- 目标完赛时间：[例如 1小时30分]
- 每周可训练天数：[例如 4天]
- 目标比赛日期：[例如 2026年11月15日]
```

### 第四步：每周更新

每周训练结束后，对 Claude 说：

```
更新本周训练数据
```

---

## 文件结构

```
ai-running-coach/
├── README.md             # 本文件：项目介绍与快速开始
├── USER_GUIDE.md         # 用户操作手册（所有用户必读）
├── 快捷指令.md            # 四大场景快捷模板（复制即用）
├── SKILL.md              # AI 教练核心规范（AI 自动读取）
├── THEORY_LIBRARY.md     # 训练理论知识库大纲（v2.1+）
├── knowledge_cards/      # 分层知识卡片库（伤病/力量/营养，AI 按需路由调用）
├── rebuild_vectordb.py   # 本地高级用户重构向量库脚本
├── ADAPTERS.md           # 设备适配器配置（开发者参考）
├── CONTRIBUTING.md       # 贡献指南（开发者）
├── 赘肉.md               # 归档内容（AI 不读取）
├── schedules/
│   ├── example_schedule.md        # 示例课表（了解格式）
│   └── [你的昵称]_schedule.md    # 你的专属课表（AI 自动生成）
└── 训练数据/              # 本地 .fit 文件（MCP 优先，此为备用）
```

---

## 训练理论依据

| 理论 | 出处 | 核心贡献 |
|------|------|---------|
| VDOT 体系 | Jack Daniels, *Daniels' Running Formula* (2013) | 五区配速精确划定 |
| 累积疲劳原则 | Luke Humphrey, *Hansons Marathon Method* (2012) | 消除超长跑迷信 |
| 80/20 强度分配 | Matt Fitzgerald, *80/20 Running* (2014) | 避免"灰色地带"训练 |
| 10% 递增法则 | Hal Higdon, *Marathon* (2011) | 安全增量与赛前减量 |

---

## 分享给朋友

把整个 `ai-running-coach` 文件夹分享给朋友，让他们按照 USER_GUIDE.md 连接自己的高驰账号即可——课表数据各自独立生成，不会互相影响。

---

## 贡献

欢迎为本项目贡献：
- 新设备适配器（参考 ADAPTERS.md 格式）
- 训练理论补充（THEORY_LIBRARY.md 第四章）
- 用户反馈与建议

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*AI Running Coach v2.1.0 · 基于 Claude Skill 协议构建*
