# New Manga AD-002 重构执行指令 v2（DSH 自治执行）

Status: ACTIVE_EXECUTION_DIRECTIVE · Owner: DSH（Lead/Architect/Integrator）· 依据：[AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md) · 日期：2026-10-26
取代：用户 2026-10-26 提供的指令 v1（本 v2 修正其 8 条 P0、12 条 P1，见文末「修订溯源」）。

---

## 0. 授权、模式与停止条件

- **全权授权**：自行规划/设计/裁决技术方案与实现取舍，不逐项请用户确认。
- **停止条件（仅此三类）**：
  1. 用户明确说「停止」→ 立即停止，输出本轮汇总 + HANDOFF（§11）。
  2. 同一外部阻塞（缺 SDK/证书/硬件/权限/第三方审核 Agent 全部不可用）**连续 3 个 round 无法自行解除** → 写 `BLOCKED` 证据 + HANDOFF，禁止静默空转。
  3. 触及安全红线或不可逆破坏风险且无法降到保守方案 → 暂停并回报。
- **round 定义**：一个 Task 从 `claim` 到 `done/closed`（或被判 BLOCKED）为 1 round。不是"一次工具调用"。
- **不得停工的理由**：不得以"等待用户决定"停工（除非属于上述停止条件）。遇到 AD-002 未决项按 §6 决策规则自行裁决并留痕。
- **预算护栏**：单个 Task 实际耗时超过估时 **150%** → 暂停该 Task，写重估（剩余范围/成本/风险）再决定继续或缩小；连续 3 个 Task 超估时 → 触发一次整体重估并向用户简报。

## 1. 权威事实源（每个 round 开始必读，禁止凭记忆推断）

1. [AD-002 目标架构](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md) —— 架构与边界（唯一架构权威）。
2. [STATUS](../STATUS.md) 当前状态段 —— 唯一 Active Task 与运行状态。
3. [REBASELINE_PLAN](../REBASELINE_PLAN.md) 当前 DAG —— 唯一 DAG 与 READY 节点。
4. 当前 Task 卡 + 最新 Review/adjudication + rolling checkpoint。
5. `git status --porcelain` + `git log -5`：**必须检查是否有他人未提交改动或活跃 Task 占用**（不覆盖、不 stash、不删除）。
6. 需要定位文档分类时才读 [00_INDEX](../00_INDEX.md)；Task 生命周期按 [09_COLLABORATION §4](../09_COLLABORATION.md) 执行。

**事实优先级**：源码 / 测试 / Git > AD-002 > STATUS / PLAN > Task 卡 > 其他文档。文档与代码冲突时以代码为准并在 Task 留证据。

## 2. 「完成重构」的验收口径

前端（Avalonia）与后端（Python Core）两条线同时收口：

| 阶段 | 必达 |
|---|---|
| **S0** `UI-AVALONIA-SPIKE-1` | 11 项门槛：单文件 ≤45MB、冷启动 p50 ≤600ms、真 Mica（Win11）、3 套主题热切 P95 ≤100ms、CoreClient 中文零乱码、4000×60000 分块 p95 ≤16.7ms/内存 ≤1.5GB、竖排 1:1 像素、IME、打包、无控制台窗口、版本决策。**允许 `GO_WITH_LIMITATIONS`**（仅限环境项：Win10 回退、日语 IME、Narrator），其余硬失败=NO-GO→按 AD-002 换备选并留裁决记录 |
| **S1** `HOST-CORECLIENT-1` | C# spawn 两个 sidecar（`host_bridge` wire v1 + `core_service` protocol 2.3）+ JSON-lines 往返 + 错误码透传 + `\uXXXX`；`core.ping` + `list_books` 跑通；中文零乱码；**sidecar 启动失败可诊断且不 panic**（父子令牌完整性比对 + stderr 落盘 + 明确错误面） |
| **S2** `HOST-COMMAND-MIGRATION-1` | 生产命令面 parity 全绿（定义见 §5.4）；双 sidecar 覆盖；6 个 domain service 只是 C# 侧组织方式 |
| **S3** `UI-SHELL-THEME-1` | 主窗/导航/主题中心/书架（参考规格）/设置骨架；换肤 P95 ≤100ms；主题令牌先行（ResourceDictionary + ThemeDictionaries{Light,Dark}） |
| **S4** `UI-WORKBENCH-READER-1` | 工作台画布/区域编辑 + 沉浸式阅读器（含 webtoon_vertical 接线）；阅读器门槛 G2–G4 |
| **S5** `LEGACY-SHELL-REMOVAL-1` | 退役 Tauri/React/WebView2/m2res/CORS/no-store/每请求 SHA-256（**须先过 §5.6 安全 ADR**）；旧壳 archive + 引用迁移，不删除；全量回归绿 |
| **后端瘦身** | 移除 Core 内 PySide6（`QtImageDecoder`→Pillow/pypdfium2，覆盖 PDF/TIFF/WebP/多帧 GIF 回归）；entry exe 去重；新模型优先 ONNX |
| **发布件** | `LICENSE`（GPL-3.0 或含 AGPL 时按 AGPL-3.0）+ `NOTICE` + `THIRD_PARTY_LICENSES.md`；可复现构建脚本；旧版数据升级路径；安装包 ≤150MB（S0 门槛）/主安装包（含基础模型）≤2GB |

**体积口径（P0-4 修正）**：
- 主安装包（含基础模型）**≤2 GB**；
- Core 运行时（**不含模型**）**≤700 MB**，且该门槛**以 `INFER-BASELINE-EP-1` 结论为前提**（torch 365MB 是否移出主包）；未出结论前只记录实测值、不判定失败；
- CUDA 高性能组件作**可选独立包 ≤8GB**，不进主安装包。

## 3. S0/S1 前置件（必须先完成，缺一不得开工相应阶段）

| # | 前置件 | 交付物 | 解锁 |
|---|---|---|---|
| P1 | 许可三件套 | `LICENSE` / `NOTICE` / `THIRD_PARTY_LICENSES.md` + Saber 移植登记模板（源文件+commit+许可头） | 任何分发（S0 后） |
| P2 | Repo Layout & Coexistence ADR | 新壳目录（建议 `apps/desktop-avalonia/`）、安装标识（新壳独立 identifier/beta 通道）、数据根共用策略、**单实例互斥**、新旧并行规则 | S1（Host 落地） |
| P3 | 资源通道安全模型 v2 ADR | 何时可去 `no-store`/每请求 SHA-256；**必须保留的等价测试**：等长原地重写必拒、revoke/expiry 生效、越界/重解析点防护 | S5 |
| P4 | 测试基线记录 | pytest 基线（当前 `tests/**` 192 个 `test_*.py`：passed/skipped 分列+skip 原因）、旧前端 vitest 基线（60 个测试文件）、新壳 dotnet 基线（从 0 建） | S1/S2 回归判定 |
| P5 | 执行指令 v2（本文件）+ AD-002 未决项登记 | 已存在 | 全部 |

## 4. 每个 round 的固定循环

① **读**：§1 全部事实源 + `git status` + 当前活跃 teammate/Task 占用。
② **选/放**：从 READY 选 Task；无 READY 时由 DSH 拆分并正式释放（改 `status: ready`、冻结范围、`allowed_paths` 显式含 `evidence_dir`、`base_commit` 填实、`reviewer` 指定不同人），同步更新 DAG、STATUS、TASK_LEDGER 并跑 `check.ps1`。
③ **实现**：仅改 `allowed_paths`；产品代码 Task 使用独立分支/worktree（证据/研究类可在 main）。
④ **测试**：命令 + 环境 + 结果 + 证据文件；双轨门禁（§5）。
⑤ **独立 Review**：作者 ≠ 审查者。**DSH 可以审 teammate 的实现**（只要不是自己写的）；需要独审时按 ZCode → Antigravity → Codex 回退，全部不可用才计为外部阻塞。
⑥ **集成验证**：DSH 跑一次端到端（启动/关键路径/回归）。
⑦ **状态更新**：Task `status`、AC 标记、Canonical Evidence pin（commit 或 SHA-256）、STATUS 指针、DAG、TASK_LEDGER。
⑧ **rolling checkpoint**：写 `doc/handoffs/<TaskID>-checkpoint.md`（HEAD、完成项、未完成项、风险、下一步）。
⑨ **立即选下一 Task**，不得空转。

**释放 Task 的前置检查单**：`check.ps1` PASS；STATUS/PLAN 预算未超（§5.8）；无并行的写路径冲突；reviewer 已指定且非作者。

## 5. 质量门禁（每个 Task 关闭前必过）

1. **治理**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/<ID>.md` → PASS；TASK_LEDGER 已刷新。
2. **后端**：`python -m pytest` 全绿；与 P4 基线比**无新增失败、无新增 skip**（新增 skip 必须写原因）。
3. **前端双轨**：旧壳 `npx vitest run` 全绿（直到 S5）；新壳 `dotnet build -warnaserror` + `dotnet test` 全绿。测试框架在 S1 内定（xunit/NUnit），UI 测试用 Avalonia.Headless。
4. **命令 parity（P0-1 修正）**：parity 目标 = **运行时 `command_allowlist(false,false)` 的输出快照**（当前 `PRODUCTION_COMMANDS` 66 条；`#[tauri::command]` 严格计数 57 = main.rs 55 + settings_bridge.rs 2；`PROBE_ONLY_COMMANDS` 4 条与 `AC1_TEST_COMMANDS` 3 条为测试专用，不进 parity）。快照含：命令名、参数 schema、返回 schema、错误码清单；C# 侧逐条打勾。
5. **IPC 中文与编码**：固定测试向量——`建书→列书` 往返 `雾港来信・日本語テスト`，并抓**原始 wire 字节**验证 `\uXXXX` 转义；覆盖 settings/profile 中非 ASCII 字段。
6. **安全等价测试（S5 前置）**：等长原地重写 → 必拒；revoke/expiry → 生效；越界/reparse → 拒绝。
7. **无控制台窗口**：启动后用 `Get-Process | Where MainWindowTitle` + 控制台附着检查，侧车与主进程均无控制台。
8. **文档预算**：STATUS ≤3200 bytes/45 行；REBASELINE_PLAN ≤7000 bytes/64 行（当前已 3188/6996，**每次释放 Task 前先压缩再改**）。超预算即 FAIL。
9. **lifecycle v3**：AC 行末带 `<<MET>>`/`<<PARTIAL: 原因>>`/`<<BLOCKED: 原因>>`/`<<NOT_APPLICABLE: 原因>>`；勾选与标记一致；`MET` 必须有 Canonical Evidence pin。
10. **owner ≠ reviewer**；`done` 只能由 DSH 在集成 + 验证 + 资源 closeout 全部通过后设置。

## 6. 决策规则（自行裁决，必须留痕）

- **技术方案**：按 AD-002 与既有冻结契约裁决；写入 Task 的 Decision 段或新 ADR。
- **AD-002 未决项**：
  - D-D 桌宠/悬浮球：**默认不实现**；S4 后评估，若 ≤8 人日且不阻塞关键路径可直接排期并记录。
  - D-E 旧壳处置：S4 完成前保留并行可运行；S5 才 archive。
- **产品取舍**：以「保护用户源文件、人工修改、Lock、current/pinned Revision、任务可恢复性」为最高优先；不可逆动作保守。
- **架构/范围变更**：不得自行改写 AD-002 或扩大产品范围；确需变更 → 新 ADR + 用户书面裁决。
- **发现文档与代码不一致**：以代码/测试/Git 为准，留证据，不靠旧文档推断。

## 7. 安全红线（任何情况不得突破）

1. 不覆盖/清理他人未提交修改，不自动 stash，不强推，不清理他人 worktree。
2. 不删除受保护资源（WORKSPACE-CONSOLIDATION-1 r212 的 18 项、五广域根保护）；**禁止 gc/prune worktree**；删除前逐项核实。
3. 不 push main；只有用户授权的新分支快照 push 才可执行。
4. 不随包商业/系统字体；新依赖先核许可并在 Task 记录；Saber 代码移植必须保留版权声明与许可证。
5. 不丢弃 Python Core 既有 47k 行业务能力；57/66 命令的**语义**与 grant 三件套不变。
6. 迁移期**同一时刻只允许一个 Host 运行**（单实例互斥）；新旧 Host 不得同时写同一数据根；新 Host 在 S2 parity 全绿前对生产数据**只读**；首次运行自动备份。
7. 旧壳退役 = **archive + 引用迁移**（治理要求），不是删除文件。

## 8. 关键路径与并行编排

```
S0 spike ──GO──> S1 CoreClient ──> S2 命令迁移 ──> S3 Shell/主题/书架 ──> S4 工作台/阅读器 ──> S5 删旧壳
   │                    ▲
   └─ S0b UI 规格 ──────┘（已完成）
INFER-BASELINE-EP-1（后端推理基线）可与 S0/S1 并行；结论驱动 S2 的模型清单与体积门禁
```
- 前置件 §3 P1–P4 在 S1 前完成；P3 在 S5 前完成。
- 并行写路径必须不重叠；同一文件只允许一个 Task 写。

## 9. 汇报格式与频率

- **每个 round 关闭后**一条简报：① 本轮完成 ② 证据（commit / 测试输出 / 截图路径）③ 未完成与风险 ④ 下一轮计划。
- **连续 >2 小时未关闭 round**：一条进度简报（当前 Task、卡点、已尝试项）。
- **BLOCKED**：同一现象、已尝试命令、证据路径、需要的外部条件。
- 不虚构进度；失败就写失败。

## 10. 性能与体验门槛（引用既有测量）

| 代号 | 门槛 | 当前实测 |
|---|---|---|
| G1 | 窗口可见 ≤300ms；首屏 p50 ≤1200ms；Core 不阻塞首帧 | 558ms（串行） |
| G2 | 阅读器 fit 横向利用率 ≥90%；支持 1:1/适应宽/适应高 | 39.9% |
| G3 | 4000×60000 长条滚动 p95 ≤20ms，无 >100ms 卡顿 | 未接线（BLOCKED） |
| G4 | DPR2 下 400% 像素锐利（无插值模糊），平移 ≥55fps | 无缩放能力 |
| G5 | 单页冷加载 ≤60ms；哈希占比 ≤10% | 22.9ms@657KB（哈希 20.4%） |
| G8 | 竖排排版禁则违例 0、基线偏差 ≤1px（Core 渲染成图，UI 1:1 像素显示） | Pillow 无禁则 |
| G9 | 四页 keep-alive、转场 150–250ms、reduced-motion 归零 | 卸载式切换 |

## 11. HANDOFF / 停止模板

```
Task: <ID> / status: <status> / HEAD: <sha>
完成：<条列>（含证据路径）
未完成：<条列> + 原因（BLOCKED/PARTIAL）
风险：<条列>
磁盘/工作区：<worktree、task-env 路径、是否 dirty>
推荐下一步：<可直接转发的指令，含 owner 建议>
```

## 12. 修订溯源（相对指令 v1）

| v1 问题 | v2 修正 |
|---|---|
| 「57 命令」基线错误 | §5.4：以运行时 allowlist 快照为准（66 条生产面；57 宏计数；4+3 测试专用） |
| 只跑 dotnet，丢旧壳回归 | §5.3 双轨门禁（vitest 至 S5） |
| S5 当机械清理 | §3 P3 安全 ADR + §5.6 等价测试 |
| 体积门禁不可达/口径不一 | §2 体积口径 + 依赖 INFER-BASELINE-EP-1 |
| 无许可证交付物 | §3 P1 三件套（仓库当前无 LICENSE） |
| 无仓库布局/新旧共存决策 | §3 P2 ADR（目录、标识、数据根、单实例） |
| 无 Core 启动健壮性 | S1 必含失败诊断、不 panic |
| Review 规则自相矛盾 | §4⑤ DSH 可审 teammate；ZCode→Antigravity→Codex 回退 |
| round/汇报无定义 | §0 round 定义、§9 汇报频率 |
| 预算护栏缺失 | §0 150% 重估、§5.8 文档预算 |
| S0「全部 GO」不现实 | §2 允许 GO_WITH_LIMITATIONS（仅环境项） |
| 未覆盖双 sidecar | S1 同时验证 host_bridge + core_service |
| 数据安全缺失 | §7.6 单实例/只读/备份 |
| 退役=删除 | §7.7 archive + 引用迁移 |
| 未引用已有性能门槛 | §10 G1–G9 |
| 未记录测试基线 | §3 P4 |
