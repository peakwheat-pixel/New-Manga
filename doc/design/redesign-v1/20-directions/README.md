# 三套全新 UI/UX 设计方案 · 总览

> 阶段 2 交付物。三套方案均从零设计，**不继承旧界面的布局、导航、流程、组件、配色与令牌**。
> 共同遵守：`10-ux/00_DESIGN_BRIEF.md`（设计任务书）、`10-ux/10_UX_FOUNDATION.md`（业务骨架）、`10-ux/12_USER_JOURNEYS.md`（10 条旅程）、`10-ux/13_STATE_MODELS.md`、`10-ux/14_INPUT_SPEC.md`。

---

## 如何查看

每套方案目录下的 `index.html` 双击即可打开（纯静态、离线、零依赖）：

| 方案 | 入口 | 规范页 |
|---|---|---|
| A · 暗房 | `A-darkroom/index.html` | `A-darkroom/spec.html` |
| B · 校阅台 | `B-parlor/index.html` | `B-parlor/spec.html` |
| C · 工坊 | `C-atelier/index.html` | `C-atelier/spec.html` |

原型支持 URL 参数直接定位到特定状态（便于对比）：

```
A: index.html?space=studio|library|console&theme=dark|light&state=<状态名>
B: index.html?view=proof|canvas|final&theme=light|dark&state=<状态名>
C: index.html?stage=detect|ocr|verify|inpaint|render|queue&theme=dark|light&state=<状态名>
```

---

## 差异矩阵

| 维度 | **A · 暗房** | **B · 校阅台** | **C · 工坊** |
|---|---|---|---|
| 一句话 | 以画布为中心的专业图像工位，界面几乎消失 | 以文本行为主角的双语工作稿 | 以批次与阶段为中心的可观测生产线 |
| 主导航 | 单空间 + 三视图瞬切（Library/Studio/Console） | 三段式文档框架（工程树/工作稿/边注） | 阶段轨道 + 资源树 |
| 主工作对象 | 画布上的 Region | 文本行条目 | Page×Stage 状态单元 |
| 默认主视图 | 全屏画布 | 账本式对照表 | 状态矩阵 |
| 主操作入口 | 选中 Region 的 HUD 环 + 快捷键 | 行光标 + 内联编辑 | 批量动作条 |
| 默认主题 | 深色 | 浅色 | 深色 |
| 信息密度 | 高 | 中 | 极高 |
| 批量能力 | 弱–中 | 中 | 强 |
| 校对效率 | 中 | 最强 | 中 |
| 图像精修 | 最强 | 弱–中 | 中 |
| 学习曲线 | 高 | 低 | 中–高 |
| 最适合 | 个人高端 / 重图像编辑 | 个人日常 / 校对为主 | 工作室 / 批量生产 |

三套的**主导航范式、主工作对象、默认主视图、主操作入口全部不同**，不构成"同一布局三种配色"。

---

## 方案 A · 暗房（Darkroom）

**主张**：用户看到的是页面，其余一切（页列表、检查器、任务、命令）都是环绕画布的可收纳浮带。

**核心流程**：导入 → 自动流水线 → `J/K` 在 Region 间移动、`Enter` 确认、`Shift+Enter` 重渲染 → 胶片条换页 → 导出。

**优势**
- 空间利用率最高，图像编辑路径最短，专业感与专注度最强
- 暗色长时间工作舒适；键鼠效率极高（Region 级全键盘操作）
- 四轨（原图/文本/修复/排版）在画布上叠加表达最自然

**劣势**
- 发现性差：HUD 环与快捷键需要学习，新手首日容易迷路
- 批量管理弱：胶片条适合单章流转，不适合跨章/跨作品批量作业
- 校对链路不如 B 顺；浅色主题属于"适配"而非"母语"

**风险**：最容易做成"花哨的编辑器皮肤"，需要极克的细节控制。

---

## 方案 B · 校阅台（Parlor）

**主张**：产品的核心产出是译文，界面应以文本为主体、图像为佐证；像一份可逐行校对的双语工作稿。

**核心流程**：打开章节即进入对照稿 → `J/K` 移动行 → `Enter` 编辑 / `Ctrl+Enter` 确认并下一条 → `O` 改原文 / `V` 切画布核对 → 批量确认 → 导出。

**优势**
- 校对效率最高；学习成本最低（像熟悉的表格/编辑软件）
- 术语一致性最易发现与管理；CJK 排版友好，长时间阅读舒适
- 原文/译文/机器译/人工译的四级差异可在行内表达

**劣势**
- 图像几何编辑弱：画框/多边形不在主路径
- 批量生产能力中等；画布需切视图，精细修图不如 A
- 容易滑向"普通表格软件"，气质依赖排版细节

**风险**：画布呈现若设计不佳，会破坏整体纸稿一致性。

---

## 方案 C · 工坊（Atelier）

**主张**：真正的瓶颈是流水线上哪里卡住了；界面以阶段与批次状态为中心，一次批量动作能否把失败单元推进。

**核心流程**：导入 → 自动创建批次 → 阶段轨道推进 → 概览胶囊筛选失败 → 框选 → 批量重试/换 Provider → 阶段门禁通过 → 批次导出。

**优势**
- 批量与异常处置最强；状态最透明（矩阵本身就是状态真相）
- 阶段门禁避免半成品流出；可观测性极强，适合工作室规模化
- 240 页的异常分布可以一眼看完

**劣势**
- 单条精细校对不如 B；画面感与艺术感较弱
- 对个人单章作业偏"重"；矩阵需要图例教学

**风险**：容易做成"监控大屏"，必须保证矩阵可直接操作而非只读展示。

---

## 选择建议（供参考，最终由用户裁决）

| 如果最看重 | 建议 |
|---|---|
| 图像编辑的精准与效率、专业修图感 | A |
| 译文校对速度、低学习成本、每天长时间改稿 | B |
| 多章批量生产、异常治理、团队协作与可观测性 | C |
| 混合诉求（如"个人用但每周批量"） | B 或 C，取决于批量占比 |

**Lead 的观察**（不作为裁决）：
- 三套中 **B 的落地风险最低、用户接受度最高**（迁移成本小、可渐进增强）。
- **A 的差异化最强、上限最高**，但对设计执行力要求最高（细节一松就显廉价）。
- **C 解决的是当前真实痛点**（旧 UI 的失败页定位与批处理极其薄弱，见 `00-facts/03_LEGACY_UI_ASSESSMENT.md` 中 21 条 P0），但需要用户接受更高信息密度。

---

## 目录结构

```
doc/design/redesign-v1/
├─ 00-facts/            事实盘点（能力清单、数据模型、旧 UI 评估、技术约束）
├─ 10-ux/               共享 UX 基础（任务书、业务骨架、旅程、状态、键鼠）
├─ 20-directions/
│  ├─ 00_DIRECTION_SPEC.md   三套方向冻结规格
│  ├─ A-darkroom/       A 方案（index/spec/styles/app/tokens + 文档 + 截图）
│  ├─ B-parlor/         B 方案
│  └─ C-atelier/        C 方案
└─ 30-prototype/
   └─ 00_SAMPLE_DATA.md 三套共用的统一假数据
```

---

## 交付清单（阶段 1 + 阶段 2）

### 共享基础（阶段 1）
| 文件 | 内容 |
|---|---|
| `10-ux/00_DESIGN_BRIEF.md` | 设计任务书：最高原则、8 条禁止项、质量门槛、反 AI 塑料感清单、L4 判据 |
| `10-ux/10_UX_FOUNDATION.md` | 业务骨架：对象层级、作用域×动作矩阵、内容四轨、状态模型、Lock、审阅闭环、错误恢复、长任务、12 状态真相 |
| `10-ux/12_USER_JOURNEYS.md` | 10 条以任务为中心的用户旅程（J1–J10），含决策点、失败分支、完成判据 |
| `10-ux/13_STATE_MODELS.md` | 状态基元、阶段矩阵、十二状态实现要求、转换可见性、加载与错误呈现规则 |
| `10-ux/14_INPUT_SPEC.md` | 桌面键鼠规范：L0–L3 分层、IME 红线、画布手势、危险操作、可访问性与高 DPI |
| `30-prototype/00_SAMPLE_DATA.md` | 三套原型共用的统一假数据（作品/页/Region/错误码/术语/版本） |

### 事实盘点（只读分析，非设计依据）
| 文件 | 内容 |
|---|---|
| `00-facts/01_CAPABILITY_INVENTORY.md` | 193 条能力清单（23 业务域，含 file:line 证据；已实现 141 / 部分 40 / 未实现 10 / UNVERIFIED 2） |
| `00-facts/02_DATA_MODEL_AND_STATES.md` | 领域实体、字段约束、状态机、并发语义、用户数据兼容边界 |
| `00-facts/03_LEGACY_UI_ASSESSMENT.md` | 旧 UI 界面清单、67 条缺陷（P0 21 / P1 34 / P2 12）、20 条不可沿用交互假设 |
| `00-facts/04_LEGACY_TOKENS_AND_CONSTRAINTS.md` | 旧令牌现状、技术约束（710 处内联样式 / 0 CSS 文件 / CSP 限制 / 资源通道限制） |
| `00-facts/05_GAP_LIST.md` | 37 条缺口：A 类文档有代码无 14 / B 类代码有 UI 无 13 / C 类仅测试通道 10 |

### 三套方案（阶段 2）
每套包含：`index.html`（可交互动原型）+ `app.js` + `styles.css` + `tokens.json` + `DIRECTION_CARD.md` + `SCREENSHOTS/`。

| 方案 | 入口 | 核心截图 |
|---|---|---|
| A · 暗房 | `A-darkroom/index.html` | `30-prototype/cmp-A-studio.png`、`cmp-A-library.png`、`cmp-A-blocked.png`、`cmp-A-light.png` |
| B · 校阅台 | `B-parlor/index.html` | `30-prototype/cmp-B-proof.png`、`cmp-B-canvas.png` |
| C · 工坊 | `C-atelier/index.html` | `30-prototype/cmp-C-detect.png`、`cmp-C-verify.png` |

原型支持 URL 参数直接定位：`?space=`/`?view=`/`?stage=`、`?theme=dark|light`、`?state=<状态>`、`?page=`。

## 当前验证状态

- 三套原型均已在 Chrome 156 headless 1600×1000 下实测渲染，无白屏、无 JS 阻断、中文与日文正常渲染。
- 每套内置「状态演示面板」，可逐一切换 12 个状态真相（空态 / 导入 / 无页 / 无 Region / 运行 / 暂停 / 完成有失败 / 阻塞 / 中断 / partial / stale）。
- 独立复核（uiux-verify 角色、只读、未参与实现）报告见 `40-review/VERIFY_REPORT.md`。
- **未执行**：`uiux-engine finalize` 的 G0–G6 正式 Gate 链（需要契约化 request 输入与完整 evidence manifest）。该 Gate 链应在用户选定方向、进入阶段 4 实施时按 Task 冻结范围执行；本轮为方向探索，不签发 TaskResult。
