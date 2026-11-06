# DSH → 下一会话交接（New Manga，2026-11-06）

> 用途：新开 DSH 对话时，先读本文件，再继续自动推进；用户已授权「自动推进、全部授权、裁决交给 Codex 或 DSH、无需用户介入」。
> 事实以 Git/文件为准；本文件是恢复入口，不是第二套事实。

## 0. 用户最新授权（2026-11-06，逐字要点）

- 「自动推进，全部授权，裁决交给 codex 或者 dsh，不需要用户介入。」
- 解释：新会话可自主释放/实施/复审/集成/closeout；**裁决（架构/契约/方案/争议）交 Codex 或 DSH 判定**（Codex 不可用时由 ZCode 备选，且不把 Codex 额度放关键路径）。
- **推送**：过去长期规则是「不 push 除非明确授权」；本轮「全部授权」视为覆盖该限制——新会话可在门禁（check/pins/测试）全过后 `git push origin main`，并在推送前后记录 hash；若判断不合适可保持不 push 并记录原因。
- 不可越界：不碰真实用户数据 / AppData / 外部卷 / 回收站；不新建依赖；不修改 18 份冻结契约字节（除正式 UNFREEZE 流程）；实现者不得自审；`verification/FEA-09/**` 测试重写后必须 `git checkout` 恢复。

## 1. 仓库与基线（交接时快照）

- 仓库：`G:\CODEX\New Manga`，main；HEAD **`3127932b3`**；工作树 **clean**。
- 本地领先 origin/main **988** 个提交（`git rev-list --count origin/main..HEAD`）；origin/main ref 为本地跟踪引用，未 fetch。
- 门禁：`check.ps1` **PASS（3 warnings：非终态计数/STATUS 80%/PLAN 80%）**；`verify_pins.ps1` **18/18 PASS**。
- 测试基线：全量 pytest **3212 passed / 10 skipped**；全量 .NET **1527 passed / 0 failed / 86 skipped**（RUN1/RUN2 可能命中已知 FEA-09 写竞争 flaky，隔离复跑/重跑即可）。
- `doc/STATUS.md`：当前 **无活动 Task**；PLAN `READY 节点：无`。
- `doc/TASK_LEDGER.md`：非终态 9 个，均为历史/旧架构/前提未冻结项（Rust ready、GIT-CLEAN-*、FEA-D07/FEA-GOV、NEW-MANGA-V1-FULL-AUDIT blocked 等）——**不得**作为可执行任务自动恢复；当前 FEA 线无 ready 卡。

## 2. 已闭环（可直接信赖的交付）

| Task | 终态 | delivery / 说明 |
|---|---|---|
| FEA-11-SCAN-2 | done | `555f57b8d`；B1 冷启动枚举；AC-S2-1…9 MET；r1 CHANGES→r2 APPROVE |
| FEA-11-SCAN-2-PREREQ-1 | done | `7451bfaaa`；**C-17 v1.1** UNFREEZE（`source_list_scan_targets` + ScanTarget/ScanTargets + `source.sync.enumerate/1`）；独立 byte-level APPROVE；pins 18 |
| FEA-11-WATCH-1 | done | `00083a977`（实现链 e60105cf9→19a2af7f3→00083a977）；r3 APPROVE；AC-W1…W5 MET；C-01b SC-25 watcher hint 已兑现 |
| FEA-11-SCAN-1 | done | `7080167e1`；Host 周期扫描方案 A |
| FEA-11-MATCH-1 | done | `869b6d5d5`；AC11-3 MET（带 L-M1/L-M4 limitation） |
| FEA-11-AC4-GAPS-1 | done | `2d9a4a219`；AC11-4 MET |
| FEA-12-CORE | done | `51e139eff`；UNFREEZE `fc9833479`（C-04b v1.1 + M2-C1 rev 2.14） |
| FEA-12-UI | done | `a46d4d5c7`；AC1–AC10 MET；L3 真机 NOT_RUN |
| FEA-12-PREREQ-1 / FEA-12-DSIM-1 / FEA-11-LINEAGE-1 | done | `3e37c595b` / `beee351bb` / `90a8c8218` |
| FEA-11-HOST-AUTH-1 | closed_with_limitations | `cbd561b4`；Codex 裁决 A |

## 3. 下一步队列（推荐顺序，Codex/ZCode 已排序）

1. **FEA-11-RENDITION-1（proposed 占位卡 `doc/tasks/FEA-11-RENDITION-1.md`）**——承接 LINEAGE-1 L10：Run/provider 消费当前 binding 的真实 referenced rendition（旧 managed original 仅兼容）。**必须先独立 scope review**（核实 C-17 v1.1 §7.2/§7.3 与 C-15 是否足够；是否需 UNFREEZE），再冻结/释放/实施/fresh Review/closeout。
2. **FEA-12-UI-RESIDUAL-1（未建卡）**——UI 残余 P3：delete-time capability 防御边、preview `BOOK_NOT_FOUND` 自动刷新、AC6 第二次 cleanup retry 测试、只读/能力缺失文案。先建卡 + scope review。
3. **AC11-1 终态裁决**（DSH/Codex）：WATCH-1 已完成 watcher 半边；争议点是「启动/访问前检查」= 读取时强验证 vs 启动全量扫描。若采纳前者，AC11-1 可判 MET（带 limitation）；否则保持 PARTIAL 或另立启动扫描卡。
4. 其他小项（不占主线）：L-S1 registry resilience（file-root 缺失整库 `SOURCE_REGISTRY_UNAVAILABLE`，另立缺陷卡）、L-S4 `refresh_source_location_auth` 死代码、FEA-12-UI P3s、C-04b 8 项文档 residual、SCAN-2 RH-1…RH-5。

## 4. 必须遵守的作业流程

- **释放前**：独立 scope review（fresh subagent，记录 session）→ DSH 裁决 → 卡面冻结（kind/status/base_commit/owner/reviewer/allowed_paths/AC/Out）→ PLAN `READY 节点` + STATUS 指针 + TASK_LEDGER。
- **实施**：Agent Teams teammate（`spawn_teammate` 上限 8；必要时复用 inactive teammate 用 `send_message` 唤醒）；只写卡 allowed_paths；不 `git add -A`；提交用显式 pathspec；不 push 除非门禁全过并记录。
- **复审**：独立上下文 fresh subagent（作者/实现者不得自审）；报告含 frontmatter（reviewed_head/decision/reviewer session）；DSH 处置 findings；返修后窄面复审。
- **集成门禁**：`check.ps1 -TaskPath` + `check.ps1`、`verify_pins.ps1`（18/18）、`pytest tests`、全量 .NET（跑后 `git checkout -- verification/FEA-09`）、`generate_api_inventory.py --check`、scope diff（契约/schema/依赖零漂移）、证据 sha 复算、资源清单。
- **closeout**：卡 status done + delivery_head/integration_commit + Canonical Evidence（每文件 sha256）+ Resource Manifest（真实存在的路径）+ closeout record（含 limitation）；更新 STATUS/PLAN/LEDGER；重跑 check/pins。
- **冻结契约**：18 pins（`doc/plan/FEA-CONTRACT-FROZEN-*.md` + matrix）；任何字节修改必须 UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-<DATE>-*.md` + 独立 byte-level 复核 + 重冻 + pins 重算；pin 行只允许一个 sha 行。
- **真实性纪律**：不得在卡/报告/commit message 写未落地的「已修」；残修登记 limitation 或 follow-up，不得静默改口径（WATCH-1 的 RootLost 误述即先例）。

## 5. 关键路径与命令

```powershell
Set-Location 'G:\CODEX\New Manga'
git log --oneline -5; git status --short
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:/Python314/python.exe tools/governance/task_ledger.py --write
C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no   # 基线 3212/10
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build # 基线 1527/0/86
git checkout -- verification/FEA-09   # .NET 全量后必须恢复
```

- 契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.1，sha `aefa0fa5…`）、`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（v1.1）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（rev 2.14）、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`、`doc/plan/FEA-CONTRACT_FROZEN_C04b.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`。
- 状态：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`；卡：`doc/tasks/*.md`；复审：`doc/reviews/*.md`；证据：`verification/FEA-*/*`。
- 工作区：`G:\CODEX\New Manga.workspace\`（temp/agent-output/archive/scope-review 等；资源处置按 `doc/WORKSPACE_GOVERNANCE.md`，删除前核对引用/独有文件）。
- 决策输入：`G:\CODEX\New Manga.workspace\FEA-12\codex-next-task.md`、`codex-next-task-2.md`、`G:\CODEX\New Manga.workspace\FEA-11\scope-review\*`。

## 6. 已知 limitation（如实保留，不得宣称已解决）

- **AC11-1 仍 PARTIAL**（watcher 已兑现，启动/访问前解释歧义未裁决）；**L10 不解决**（referenced 图源/rendition）。
- SCAN-2：L-S1 registry resilience（file-root 缺失整库 typed fail-closed）、RH-1…RH-5（refresh pending 延迟/不绑停机 token/targets 只增不减/14-15 表口径/HostRuntime 证据强度）、大库冷启动成本未标定。
- WATCH-1：漏事件依赖周期兜底；folder 事件=source due；hint pass 重扫 ≤budget−1；跨 tick 延迟由 900s 周期决定；无 fake-Core seam。
- SCAN-1：L-A/L-G（首次 ok 前 missing fail-closed）；MATCH-1：L-M1…L-M7（PDF 无 profile、旧证据重算未实现等）；UI：L1–L10（L3 真机 NOT_RUN、能力/只读边等 P3）；CORE：C-04b 8 项文档精度 residual；HOST-AUTH-1：AC3 PARTIAL + 10 limitation；LINEAGE-1：L4–L11。

## 7. 新会话启动清单（按序执行）

1. `git log --oneline -5`、`git status`、`check.ps1`、`verify_pins.ps1`；确认 HEAD 与 clean。
2. 读 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 与本手交文件。
3. 若继续主线：对 `FEA-11-RENDITION-1` 派独立 scope review（指令见 §3/下轮候选）；处置后冻结/释放/实施/复审/closeout。
4. 若裁决 AC11-1：先读 `doc/tasks/FEA-11.md` AC11-1 原文与 WATCH-1/SCAN-1/SCAN-2 证据，交 Codex 或 DSH 判定，再回填（或登记 limitation）。
5. 任何新卡先 scope review，不直接开工；不 push 未经门禁；不改冻结字节未经 UNFREEZE。

## 8. 续接补充（2026-11-06 深夜 / 2026-11-07 凌晨轮次）

> 本轮完成两卡并 push；下一会话只读本文件 + STATUS/PLAN/LEDGER 即可恢复。

- **FEA-11-RUN-GRANT-1-PREREQ-1 `done`**（`116a711ba`）：**C-06 v1.2 + C-16 v1.3 UNFREEZE**（新增 host-control `AuthorizeSourceReadForRun` + `source.read.run/1`；Run wire/minor/schema/依赖/16 项 pins 零改动）；独立 byte-level 复核 r1 changes → r2 changes → **r3 approved P0=0/P1=0**；pins **18/18**（C06 `99831a20…`、C16 `7c355ccb…`）；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md`。
- **FEA-11-RUN-GRANT-1 `done`**（delivery/integration `a11ded0d3`；实现链 `85eace738`→`7ff49f1cc`→`04317256c`→`3ffabeb81`→`9e1861ee0`→`a11ded0d3`）：Core 授权建立命令 + Host best-effort 铸造/绑定/接线；**独立 Review r1 changes（P1×1/P2×3/P3×7）→ r2 changes（P2×2/P3×2）→ r3 approved（P0=0/P1=0/P2=0/P3=2 非阻断）**；AC-R1…R7 全 MET。**L-G12 边界（如实保留）**：可用=窗口内 + image 单 entry + folder（逐成员，已真实 IPC 证明）+ zip/cbz/pdf 归档首成员；**多成员容器其余页与 version 通道缺口不可用**；L-G1/L-G2/L-G8/L-G9/L-G10/L-G11/L-G14 一并保留；**L-R1 未全修**。
- **基线（本轮末实测）**：pytest **3281 passed / 10 skipped**；全量 .NET **1551 / 0 / 89**；pins **18/18**；check PASS(3w)；API inventory PASS；scope diff ⊆ allowed_paths（31 文件，禁止面零 diff）。
- **当前状态**：无活动 Task；`doc/tasks/FEA-11-RUN-GRANT-2.md` **proposed 占位**（Host→Core source version/容器成员 locator 通道 + 长 Run 续期 + R3-02 委托行覆盖；**须先独立 scope review，未释放**）。
- **下一候选顺序建议**：①`FEA-11-RUN-GRANT-2`（scope review → 冻结/释放；若需 UNFREEZE 走正式载体）；②其他小项（L-S1 registry resilience、L-S4 死代码、L-R11 gate 统一、C-04b 文档 residual、SCAN-2 RH-1…RH-5、UI P3）——均须先建卡 + scope review。
- **push**：本轮已 `git push origin main` → `2067789ea..d7374ce34`（PRE_HEAD `d7374ce34`、PRE_ORIGIN `2067789ea`、AHEAD 17→0、PUSH_EXIT=0、POST_ORIGIN `d7374ce34`；含 PREREQ-1/RUN-GRANT-1 closeout 与 handoff）；origin/main 与本地同步（AHEAD=0）。
- **工作区资源**：`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\`（500+ 测试夹具/日志/判别备份）→ `PRESERVE_REFERENCED`；`FEA-11-RUN-GRANT-1-PREREQ-1\tmp` 保留；未删除任何仓内文件。
