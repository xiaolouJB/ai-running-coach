# AI Running Coach

> 基于 Claude + 高驰 MCP 的智能跑步训练系统，理论驱动 · 数据实时 · 课表动态调整

---

## 这是什么

AI Running Coach 是一个运行在 Claude 上的跑步训练 Skill。它通过高驰（COROS）MCP 实时读取你的手表数据，结合丹尼尔斯、汉森、80/20 三大经典训练理论，为你生成和动态调整专属训练计划。

**核心特点：**
- 无需上传文件——直接从手表读取实时数据
- 无需填写体能测试表——AI 从运动历史自动推算 VDOT
- 每周一句话更新——`更新本周训练数据` 即可完成所有分析
- 随时复盘——单次、本周、近期滚动，三种粒度按需触发
- 理论有据可查——所有建议可追溯到原始理论出处，调整有 changelog

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
├── THEORY_LIBRARY.md     # 训练理论知识库（可用户扩展）
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

*AI Running Coach v1.2.0 · 基于 Claude Skill 协议构建*

---

## 版权说明

© 2026 [xiaolouJB](https://github.com/xiaolouJB)

本项目以 **CC BY 4.0** 协议开放分享：你可以自由使用、修改和再分发，**但必须注明来源**：

> 原项目：[https://github.com/xiaolouJB/ai-running-coach](https://github.com/xiaolouJB/ai-running-coach)
