---
id: DISPLAY-PERF-DECISION-1
title: 显示效果与运行效率基线 + 三路线裁决（仅证据/设计，不改产品代码）
kind: research
governance_version: 3
status: in_review
approval: user_authorized_2026-10-26_display_perf_decision
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on: []
base_commit: c0251b9e7
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/DISPLAY-PERF-DECISION-1
allowed_paths:
  - doc/tasks/DISPLAY-PERF-DECISION-1.md
  - doc/design/DISPLAY_PERF_DECISION_1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/DISPLAY-PERF-DECISION-1-*.md
  - verification/DISPLAY-PERF-DECISION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/**
---

# DISPLAY-PERF-DECISION-1：显示效果与运行效率基线 + 三路线裁决

## 来源与目标

**来源（用户 2026-10-26 直接指令）**：用户对当前软件「显示效果不满意、底层运行效率也不行」，判断「目前的技术栈不太行」，指定先出**证据级方案**再决定是否换栈。用户确认四个显示面全部纳入（外观材质/阅读器画面/成品页排版/工作台画布），并点名效率痛点为「Core 和软件不是一起启动」；路线选择为「先出证据级基线 + 三档路线对比，再由用户裁决」。

**性质**：研究 + 设计 + 真机测量。**未写任何产品代码、未改配置/依赖/契约**。

**交付结论**：见 [DISPLAY_PERF_DECISION_1](../../doc/design/DISPLAY_PERF_DECISION_1.md)。核心：实测无一项"必须换 UI 栈"；A 现栈深化 35–60 人日为主线，B 混合原生 GPU 层 60–110 人日为条件升级，C 换栈 180–320 人日不推荐。

## Acceptance Criteria

- [x] **AC1 启动与 Core 生命周期基线**（3 次冷启动中位：Core spawn 40ms → Core ready 513ms → 窗口可见 558ms；严格先 Core 后窗口，最坏 30s）<<MET>>
- [x] **AC2 图片通道成本分解**（真实 657KB 页端到端 22.9ms：resolve 3.40 / issue 3.20 / 取块 6.00（含整文件 SHA-256 4.65）/ Blob 0.50 / 解码 9.75；Host 哈希比同字节 WebCrypto 慢 11–13×，opt-level=1 代理证据）<<MET>>
- [x] **AC3 阅读器画质与流畅基线**（DPR2：1200×1660 → 渲染 471×652，线性缩放 0.3928、横向利用率 39.9%；缩放控件 0、可滚容器 0、长条未接线；翻页上屏 49.60ms；rAF 59.95fps）<<MET>>
- [x] **AC4 四页视觉差距清单**（43 条编号：欠账 27 / 严格栈限制 2 / 有原生替代 2 / 设计源冲突 5 / 待验证 2 / 合规 4）<<MET>>
- [x] **AC5 排版渲染能力评估**（Pillow 四缺陷实测：无 kerning/ligature、日文字体回退到微软雅黑、cell 35px vs 1em 26px、无禁则；Chromium 侧 DOM 量化 BLOCKED、对照样本无效，已如实登记）<<MET>>
- [x] **AC6 三路线对比**（A 35–60 / B 60–110 / C 180–320 人日；各含差距映射、风险、验收门槛、不可解决项，附一手资料 URL）<<MET>>
- [x] **AC7 裁决建议与决策点**（推荐 A + 排版子线；D1–D10 共 10 个待裁决点，含 2 处设计源冲突与 B 触发条件）<<MET>>
- [x] **AC8 证据与范围自检**（全部数字可复核；产品代码/配置/依赖零改动；测量全程隔离 env，未触用户数据；`git status` 仅本 Task 新增路径）<<MET>>
- [x] **AC9 Core 非管理员启动 RCA**（已复现：非提权 3 次/提权对照 2 次；根因链闭合到 Low 完整性令牌 → sidecar 无法写 `%APPDATA%\com.newmanga.desktop\{derived,catalog}` → Core 秒退 → supervisor 3 次失败 → t≈20s panic 退出；候选机器策略待干净机复核）<<MET>>
- [x] **AC10 非 Web 前端技术栈选型证据**（用户追加需求；实测 Avalonia 单文件 34.24MB、运行时换肤机制对比、WinUI3 单文件/RequestedTheme 限制、GPL 红线；给出主选/备选/不推荐与 11 项 spike 验收）<<MET>>

## 允许修改范围

- 本 Task 卡、`doc/design/DISPLAY_PERF_DECISION_1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/handoffs/DISPLAY-PERF-DECISION-1-*.md`。
- `verification/DISPLAY-PERF-DECISION-1/**`（全部证据）。
- `G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/**`（隔离运行环境）。
- 只读引用：`apps/**`、`src/**`、`doc/**`、`verification/**`、`test_assets/**`。

## 禁止范围

- 不得修改任何产品源码、配置、依赖清单、契约、Schema、`AGENTS.md`、`AD-001`（本 Task 全部执行完毕，未触碰）。
- 不得修改用户真实 `%APPDATA%` / 媒体库（全部启动使用隔离 env）。
- 不得 `push`、`merge`、`reset`、`stash`、删除既有文件。
- 不得把「换栈」写成既成事实（C 仅为候选，待用户裁决）。
- 不得以 mock 代替真机测量；未跑项如实标 NOT_RUN/BLOCKED。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 隔离 env 启动基线 exe 3 次，黑盒时间线（进程创建/窗口可见/Core 日志/标题线程） | packaged 模式 + 隔离 task-env | PASS（中位 558ms，min 540/max 582） | `verification/DISPLAY-PERF-DECISION-1/baseline/REPORT.md` §2 + `ac1/` |
| AC2 | 真实 30 页导入后同路径重放，越界 chunk 隔离哈希；仓外最小工程测 SHA-256 代理 | acceptance 构建（CDP，差异仅 browser args） | PASS（22.9ms 端到端，哈希占比 20.4%） | 同上 §3 + `ac2/ac2-stages.json` |
| AC3 | DPR2 截图 + DOM 量化 + 内置 rAF 采样（≥10s） | 同上 | PASS（39.9% 横向利用率、0 缩放、翻页 49.6ms、59.95fps）；长条 FPS BLOCKED（产品未接线） | 同上 §4 + `ac3/` |
| AC4 | 现状 DPR2 截图 vs 设计基线 vs Figma v2（只读） | Figma MCP 可用，无设置页画板（已降级说明） | PASS（43 条编号 + 判定依据） | `visual/GAP_REPORT.md` + `visual/figma-ref/` |
| AC5 | Pillow 真实适配器链渲染 + shaping/几何探针 + Edge 截图对照 | Pillow 12.3.0（无 raqm）；msedge launcher 限制 | PARTIAL（Pillow 侧 PASS；Chromium DOM 量化 BLOCKED、对照样本塌缩无效，已如实登记） | `routes/TYPESETTING_COMPARISON.md` + `routes/metrics.json` |
| AC6/AC7 | 证据汇总 + 外部资料核查 + 路线矩阵 | 一手资料 web 核查 | PASS（三路线 + 10 决策点 + URL/未核实标注） | `routes/ROUTES.md`、`doc/design/DISPLAY_PERF_DECISION_1.md` |
| AC9 | 非提权 vs 提权启动对照 + 令牌/ACL/stderr/事件日志取证 | packaged exe + 隔离 env，本机有沙箱痕迹 | PASS（根因链闭合：Low IL 令牌 → sidecar 写 denied）；PARTIAL：「谁降到 Low」需干净机复核 | `verification/DISPLAY-PERF-DECISION-1/nonadmin/RCA.md` + `nonadmin/evidence/`（24 文件） |
| AC10 | 各栈一手资料核查 + Avalonia 真实 publish 实测 | .NET 9 SDK、NuGet、官方文档 | PASS（Avalonia 34.24MB 单文件实测；WinUI3/QML/Flutter 限制逐条有据） | `verification/DISPLAY-PERF-DECISION-1/ui-stack/STACK_COMPARISON.md` + `_spike/` |

## 依赖、风险与阻塞

- 依赖：`target/release/new-manga.exe`（基线 `1136BB0A…3226`）+ 自带 sidecar；工作树 HEAD `c0251b9e7`。
- 已解决阻塞：冻结 release exe 无法开 WebView2 CDP（wry 覆盖 env 变量）→ 经 Lead 批准做一次仓外配置增量构建（18.9s），差异仅 browser args，溯源 `BUILD-PROVENANCE.json`。
- 保留限制：AC5 的 Chromium 侧 DOM 量化 BLOCKED（本机 msedge launcher 交接）；长条滚动 FPS BLOCKED（产品能力缺失）；物理 DPR2 屏 NOT_RUN。
- 审查：本 Task 不自我批准；用户裁决 D1–D10 后，如需技术复核再指派未参与实现的 ZCode/Antigravity/Codex。
- **用户 2026-10-26 追加裁决**：前端改用 **WinUI 3**（非 Web、主题中心）；架构替换 AD-001 的 React+Tauri 冻结目标，需落 AD-002 并由用户书面确认。选型证据同时给出 Avalonia 更利于「运行时深度换肤」的反向证据（`ui-stack/STACK_COMPARISON.md` §4），WinUI3 需在 spike 中证明换肤/打包两条硬约束。
- **RCA 机器特异性待复核**：本机存在沙箱 ACE 痕迹（`HOME-MY\CodexSandboxUsers`），「谁把 sidecar 降到 Low IL」未最终定位；需在无沙箱痕迹的干净 Windows 上重跑 `child-token-probe.ps1`（RCA §排除表末段），以判定是机器策略还是产品/打包问题。

## 交付与运行记录

- Handoff：本卡 + `doc/design/DISPLAY_PERF_DECISION_1.md`（替代独立 Handoff）。
- Review：待用户裁决（D1–D10）。
- 实际测试：2026-10-26，隔离 task-env，ac1/ac2/ac3 见上表；证据 43 文件 5.5MB。
- 遗留：P3 排版方案需 spike；B 需 3–5 人日 spike 才能确认 airspace/输入/DPI。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-AC1-3 | AC1/AC2/AC3 | verification/DISPLAY-PERF-DECISION-1/baseline/REPORT.md | | fd8d49c3f4f1401b87a70ca56f067553a1449769c2037ac31fd4dc3e894e3fa0 | CANONICAL |
| E-AC4 | AC4 | verification/DISPLAY-PERF-DECISION-1/visual/GAP_REPORT.md | | 49e8372fd910892b967b1c864457810073023ee4f927b5dd6ce54458cfa73957 | CANONICAL |
| E-AC5M | AC5 | verification/DISPLAY-PERF-DECISION-1/routes/metrics.json | | e6fa6986b8c2f72a7bc113d42fba11454f81d3d4fd284c5acc981cb43191d39a | CANONICAL |
| E-AC5T | AC5 | verification/DISPLAY-PERF-DECISION-1/routes/TYPESETTING_COMPARISON.md | | 9db2e1fc9c9a1f3d3c0f25190f4ad4e07edbb91cd317aef1f1fb0821b87ee1e9 | CANONICAL |
| E-AC6 | AC6 | verification/DISPLAY-PERF-DECISION-1/routes/ROUTES.md | | 02205b32f77be3382a9b6d3087f7dee8a824a1558b4af4befce32f30e48c73ee | CANONICAL |
| E-AC7 | AC7 | doc/design/DISPLAY_PERF_DECISION_1.md | | 9d9687d7f6bd44e302b24556a7e204fab6cbd1bc28c3e159ab16f8b9db840643 | CANONICAL |
| E-AC9 | AC9 | verification/DISPLAY-PERF-DECISION-1/nonadmin/RCA.md | | df33ab8c999edda61715736f784744a3869b7b8f3bb34e0f841be624791a1734 | CANONICAL |
| E-AC10 | AC10 | verification/DISPLAY-PERF-DECISION-1/ui-stack/STACK_COMPARISON.md | | 9e9786fc6bfc1ff4aec370ad68de693b61201d3628681303bc334e36db06774c | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1 | 目录级（ac1/ac2/ac3/session 日志 + pinned-baseline exe 副本 1136BB0A…3226） | 已核实目录存在；残留进程已清零；不删除（证据引用） |
| build-artifact | apps/desktop/src-tauri/target/release/new-manga.exe | PRESERVE_REFERENCED | apps/desktop/src-tauri/target/release/new-manga.exe | acceptance 版 SHA-256 见 BUILD-PROVENANCE.json（基线副本在 task-env） | 产品后续构建会覆盖；基线已另存，不影响复核 |

## Closeout Record

- Closeout date / DSH：待用户裁决后关闭。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`pending`（task-env 与基线副本待关闭时统一处置）。
- 删除、迁移、归档数量/字节数：0（本 Task 不删除任何资源）。
- 未关闭项及保留原因：AC5 Chromium DOM 量化 BLOCKED；长条 FPS BLOCKED（实现待 P1）。
- 当前指针清理：STATUS / Plan / Task 导航已更新（本卡释放与交付时）。
