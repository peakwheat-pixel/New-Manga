# GOV-RESIDUAL-RUNTIME-IDENTITY-1 交付与下一 Gate

Owner dsh（Coordinator epoch 10，lease `37230d7822a141fcae8f46acd7841890`）；Reviewer zcode（独立，未参与本 Task 任何实现）。
canonical 仓库 `G:/CODEX/New Manga`；分支 `main`；base `43a7d73c850f669cc2595343a1747a661c277f2e`；common dir `G:/CODEX/New Manga/.git`。
本 Task 只读研究，未新建 branch/worktree，未修改任何历史原件或解析器。

## 1. 交付摘要

- 生产审计复现：`2627 declarations / 1926 protected roots / 7 errors / 276 warnings`，EXIT=2。7 项身份与既有记录逐字一致。
- 逐项矩阵：`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md`，含完整身份、原文、归属、引用、实际路径、现存资源、保护缺口、技术可解性与裁决归属。
- 历史环境取证：`historical-env-evidence.json`。`%TEMP%` 与 `%APPDATA%` 的历史展开值均由**其他 Task 的 tracked 明文记录 + 当前字节 SHA-256 交叉校验**证明，未用当前环境变量直接推断。
- 只读保护评估：`probe-protected.py` → `raw/protection-evaluation.json`。

## 2. 七项结论（速览）

| # | 身份 | 现存真实资源 | 保护缺口 | 技术可解 | 需用户裁决 |
|---|---|---|---|---|---|
| E1 | `worktrees/P19-AC3-1`（P19.md） | 无 | 无 | 是 | 否 |
| E2 | `%TEMP%/p19-ac2-r1`（P19.md） | 无 | 无 | 是 | 否 |
| E3 | `%TEMP%/p19-ac2-main-1`（P19.md） | 无 | 无 | 是 | 否 |
| E4 | `%TEMP%/.tmp*` + `CLEANED_BY_OWNER`（ENV-BUNDLE-1-FU1） | 无 | 无 | 是 | 否 |
| E5 | destination prose `Same ignored target/dist locations…`（P19-UI-FIX-1） | 有（构建产物，已被覆盖） | 无 | 是 | 否 |
| E6 | `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}` #1 | **有（用户数据）** | **有（hits=0）** | 是 | 否 |
| E7 | 同上 #2 | **有（用户数据）** | **有（hits=0）** | 是 | 否 |

关键结论：**七项中只有 E6/E7 存在真实安全影响** —— 真实用户数据目录 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（含 `catalog/catalog.sqlite` 24,576 B、`data/library.db` 311,296 B、`derived/`）当前不受任何声明保护；其余五项无现存资源、无保护缺口。
**没有任何一项需要用户裁决。** 七项差异均可由「精确历史运行身份解释层」技术方案解决，且既有 `tools/governance/historical-evidence-interpretation.json` 已提供同类机制与已独审先例。

## 3. 额外事实登记（不处置）

1. 当前系统 Temp 下存在 11 个 `p19*` 测试隔离根（合计约 1.9 MiB，非用户数据），不被这 7 项声明或清理工具的四受管根覆盖。属清理禁令与用户数据边界事项，本 Task 仅登记，不删除、不提议删除；如需清理须另行授权。
2. 解析器 JSON 声明的错误 locator 精度缺陷：E6/E7 的 locator 被记为 `$.resources[2].disposition` / `$.resources[3].disposition`，实际拒绝原因是 `source_path`。仅影响可追溯性，不影响安全性；本 Task 记录但未修改。
3. `resource-manifest.schema.json` 允许 `source_path` 原样保留 `%VARS%`/globs 且「永不展开」、允许 `destination_path` 为 prose；声明审计要求可枚举身份。两者服务目的不同，不构成矛盾，但缺少「记录 → 可枚举身份」的桥接，这正是实施 Task 的目标。

## 4. 下一 Gate

独立 Reviewer（ZCode）对固定 head 做只读审查；approved 后由 dsh 正常集成并复验，才可 done。
Review 范围：`matrix.md` 的七项结论、`historical-env-evidence.json` 的 FACT/UNKNOWN 划分与 SHA 交叉校验、`probe-protected.py` 只读性与结果、Task 的 AC1–AC6 与实际日志一致性。不得以本 Task 结论自动解除任何 fatal 或保护。

## 5. 恢复点与可转发指令

固定恢复点：`G:/CODEX/New Manga`，`main`，base `43a7d73c850f669cc2595343a1747a661c277f2e`（交付 commit 见 Task Canonical Evidence 与 STATUS）。
本 Task 未创建 branch/worktree；证据提交与交付 head 在同一 `main` 上。

可直接转发给下一实施 Task 的 Lead：

“从 `G:/CODEX/New Manga` 当前 `main` 先读 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、本 Handoff 与 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md`，核对 HEAD 与 epoch 10 租约。GOV-RESIDUAL-RUNTIME-IDENTITY-1 取证已给出七项结论：只有 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（E6/E7）存在真实保护缺口且为真实用户数据，其余五项无现存资源或无缺口。请冻结 `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1`（Owner dsh，Reviewer 由 route 独立选择，不得为 Owner），先固定 base/head 再建任务 branch/linked worktree（统一 `G:/CODEX/New Manga.workspace/worktrees/`）。范围限：扩展现有历史证据解释层（`tools/governance/historical-evidence-interpretation.json` 及其加载校验、精确数量断言、新 policy 摘要常量、对应测试），为七项逐项建立字节绑定的精确身份解释：E6/E7 必须新增对上述用户数据目录及其 catalog/data/derived 的保护根（只增不减），E1/E2/E3 绑定 workspace-relative 根与历史 `%TEMP%` 展开值并记 `ALREADY_ABSENT` 语义，E4 绑定为等价 `ALREADY_ABSENT`，E5 绑定为非身份 prose 或三个已存在目标路径。禁止：修改 `doc/tasks/P19.md`、两份 `resource-manifest.json` 或任何历史原件字节；全局忽略任何错误码；按变量名整体展开 `%TEMP%`/`%APPDATA%`；实施任何真实删除/迁移/归档/GC/prune/push/reset/stash；缩小既有保护集合或解除 r212。必须保留全部 7 项完整身份可审计、保留 1926 既有保护根为真子集、提供区分力负例（非绑定错误必须仍 fatal）、跑 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `git diff --check` 并记录真实 EXIT，固定 head 交独立审查，集成复验后才 done。”

## 6. 交付后自查返修（2026-10-22，dsh）

首次交付（证据提交 ``bb04c78d4``、状态提交 ``56260c145``）的 Task Resource Manifest 含两行被声明审计拒绝的写法，使全仓错误数由 7 变 9：

- `| branch | refs/heads/main | ... |` → DECL_RELATIVE_UNRESOLVED；改为 NOT_APPLICABLE（本 Task 未新建分支）。
- `| temp（系统 Temp） | C:/Users/49745/AppData/Local/Temp/p19*（…） | ... |` → DECL_GLOB；改为 NOT_APPLICABLE（历史遗留观察，非本 Task 产生的资源）。

修复后复跑 `python -B tools/governance/clean_workspace.py --audit-declarations`：**7 errors**，与取证结论一致。

**计数时效说明**：matrix.md 中的 `2627 declarations / 1926 protected roots / 276 warnings` 是交付提交前的实测；本 Task 自身文档与证据入库后，同一时刻的实测为 `2636 / 1934 / 281`（新增声明来自本 Task 文件与证据引用）。**七项错误身份与逐项结论不变**，保护集合只增不减。此前"1926"若被后续实施 Task 引用，应以实施时的实时基线为准。

此返修未改动任何历史原件、七项身份或证据字节（EV-01..EV-07 仍 pin 到 `bb04c78d4`）。
