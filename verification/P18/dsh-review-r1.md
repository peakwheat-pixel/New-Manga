---
task_id: P18
title: 真实 JA/KO 质量资格方案与最小实验切片
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P18-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 5a18b865ec34534c64bc719db37549f4f4ead27f
declared_delivery_head: 50329bc0ae653bbb9c46875504dcc2baae61eade
reviewed_head: 34d81c96a66fbde17e4eb44bc058ab993483922f
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P18-JA-KO-QUALITY
date: 2026-10-16
mode: 只读审查 + 独立 Git/证据/原始运行产物复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
decision: approved_with_conditions
---

# P18 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 5a18b865..HEAD` | **62 个路径，全部在 `experiments/P18/**`、`verification/P18/**`、Task 与 Handoff 内** |
| **未改产品代码/测试** | 过滤 `^(src\|apps\|packaging\|tests)/` | **空** ✅（符合"生产修复须另 Task"） |
| 越界路径 | 反向过滤授权集合 | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 产物体量 | 逐文件大小 | 62 文件共 **1.78 MB**（最大为 5 组 `library.db` 各 311 KB） |
| 方案结构 | 读 `qualification-plan.md` | §1 AC1 五类缺口、§2 AC2 JA/KO 方案、§3 AC3 terminal 一致性、§4 AC4/AC5 运行安排、§5 结论边界 |
| **逐步 terminal 矩阵** | 读 `terminal-matrix.csv` | 逐 stage（import/detect/ocr/translate/inpaint/render/pipeline_terminal）给出分类与**具体原因 + 证据路径** |
| **原始运行证据** | 读 `raw/ja-r3/probe-summary.json`、`sidecar-exit-code.txt` | 真实 Core sidecar 运行；含输入指纹、运行时与模型信息、设备、endpoint、隔离、请求序列、**raw stdout/stderr SHA-256** |

## 1. AC 逐项结论

| AC | Owner | Reviewer 判定 | 说明 |
|---|---|---|---|
| AC1 五类缺口清单 | PASS | **接受** | 检测 / OCR 真值 / 翻译评测 / 无字页 F4 / 复杂背景修复**逐项**给出既有来源与缺口；**未编造统一通过率**；**未**把 BJ13 `0.90` 当质量分数 ✅ 完全符合 SCOPE_DRAFT 第 65 行 |
| AC2 JA/KO 实验方案 | PARTIAL | **接受（受限）** | JA 与 KO 的样本/真值/指标/记录方案已分别列出；**产品发布门槛仍待用户裁决**——属真实产品取舍，不得由 AI 自定 |
| AC3 逐步 terminal 一致性 | PASS | **接受** | `terminal-matrix.csv` 逐步判定；**明确 `export OK` 不替代 Run/Task/Step terminal** ✅ |
| AC4 素材许可与指纹 | PASS | **接受** | `material-registry.json` 记录 JA/KO 素材 SHA-256 与许可（`private local verification only`，不可再分发）；**未重新获取 Manga109** ✅ |
| **AC5 最小真实实验** | **BLOCKED** | **接受（受限）** | 真实调用 Core sidecar（JA/KO 各一轮，exit 0），但链路在**导入阶段即阻断**；逐步结果诚实标注，**未伪造成功** |
| AC6 不越界 | PASS | **接受** | 无产品代码/测试改动 |
| AC7 可复核性 | PARTIAL | **接受（受限）** | 来源/命令/日志/hash 齐全；但**无人工真值**，故未计算任何质量分数（诚实） |
| AC8 Review + 集成 | PARTIAL | **Review 由本文件闭合；集成由 Coordinator 执行** | — |

## 2. AC5 阻塞的根因（**本 Task 最有价值的发现**）

真实运行暴露了三个**此前未登记的技术缺口**（均为客观事实，有原始日志）：

1. **`ImportPages` = `UNKNOWN_COMMAND`** —— Core IPC **没有导入命令**。
   契约 rev 2.1 中 `ImportPages` 仍是 **PROPOSAL**（P16-C1 只冻结了 Reader/Export）。
   即：P09 交付的是**应用层导入**，**导入侧的 wire 从未冻结、也未实现** → 端到端链路第一步就无法进行。
2. **JA 输入触发像素上限**：`core.detect` 返回 `INVALID_REQUEST`，`2946x4167 = 12,275,982 px > 11,184,810 px`。
   说明检测侧存在像素上限，而真实漫画页可能超过该上限（需分块/降采样策略或上限复核）。
3. **KO 检测权重缺失**：`PROVIDER_NOT_CONFIGURED` —— 隔离数据根下无 pinned detector 权重，runtime 拒绝下载。
   另：`manga_ocr` 与 `paddleocr` 在本环境均不可用。

**这三项都应另立 Task**（生产修复须另 Task，符合本 Task 禁止范围）。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P1（DAG 前置缺口）** | **导入侧 IPC 从未冻结/实现**（`ImportPages` 仍 PROPOSAL）。这不仅是 P18 的阻塞，也是 **P12（书架导入）/P19 的前置缺口** | 建议优先建立**导入 wire 契约 + 实现**的 Task（可仿 P16-C1 → P16 的两段式） |
| **F2** | **P1（用户裁决）** | AC2 的**产品发布门槛**（JA/KO 质量达到何种程度才允许声明支持）是**产品取舍** | 按禁止范围上交 `BLOCKED_WAITING_EXTERNAL_DECISION`：请用户在 P18 方案 §2 的基础上裁决门槛 |
| **F3** | P2（技术） | 检测像素上限（11,184,810 px）会挡住真实漫画页 | 另立 Task：复核上限来源与分块/降采样策略 |
| **F4** | P2（技术） | 隔离数据根缺 pinned detector 权重，且 OCR provider（manga_ocr/paddleocr）不可用 | 另立 Task：模型/权重准备与 provider 可用性（对齐 P10 的凭据/模型管理范围） |
| **F5** | P3（证据卫生） | 5 组 raw 运行产物（含二进制 `library.db`/`catalog.sqlite`，共 1.78 MB）入库 | 可接受（契约允许 `verification/P18/**`）；建议后续只保留最终轮或在 Resource Manifest 标注中间轮性质 |
| **F6** | P3（流程） | `delivery_head` 申报 `50329bc0`（证据提交），实际 HEAD=`34d81c96` | closeout 冻结实际 HEAD |

**无 P0 finding。** 交付的诚实度值得肯定：**exit 0 被明确标注为"不代表阶段成功"**，未制造"实验已跑通"的假象。

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `34d81c96a66fbde17e4eb44bc058ab993483922f`。
- **C2**：P18 以 **`closed_with_limitations`** 收口：AC1/AC3/AC4/AC6 完成；**AC2 待用户门槛裁决**、**AC5 待 F1/F3/F4 解阻**。
- **C3**：**AC2 的产品门槛必须由用户裁决**（F2），Coordinator 不得代定。
- **C4**：F1（导入 IPC）应作为高优先前置登记，因为它同时阻塞 P12 与 P19。
- 方案与证据本身无需返修。

## 5. 能力边界

- 本 Review 覆盖范围合规、五类缺口清单的诚实性、terminal 矩阵与原始运行证据的真实性；**未重跑** Core sidecar。
- 所有 Git / 日志 / JSON 结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
