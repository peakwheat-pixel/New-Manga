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

## 9. 续接补充（2026-11-07 深夜轮次：RUN-GRANT-2A / 2B）

> 本轮完成 2A + 2B 两卡并 push；下一会话只读本文件 + STATUS/PLAN/LEDGER 即可恢复。

- **FEA-11-RUN-GRANT-2B-PREREQ-1 `done`**（`d8dcfc07a`）：**C-16 v1.4 UNFREEZE**（容器源 entries 1..N；逐项校验/整 grant typed 零部分接受/超预算 `SOURCE_BUDGET_EXCEEDED`；1/18 pin 重签，其余 17 不变）；独立 byte-level r1 changes → **r2 approved（P0/P1/P2=0）**；pins 18/18（C16 `ad25fb3c…`）；记录修正 `29365bf3c`/`44965532f`。
- **FEA-11-RUN-GRANT-2A `done`**（`a0bafc89e`）：**Host 生产版本通道**（`SourceIdentityCache` 取 Core `ScanSourceSync` 权威 version + entries；冷缓存有界 on-demand；禁 `"1"` 回退；R3-02）；独立 r1 **approved（P0=0/P1=0/P2=2/P3=6）**；AC-G1…G8 MET；L-G15 修复；L-G16 登记（>4096 成员 folder 不入缓存）。
- **FEA-11-RUN-GRANT-2 `done`**（`018008989`；docs `3dc822b77`/`8e1883655`）：**2B 容器成员 entry 授权通道**（Core `_parse_scope` 1..N + `_scope_covers_entry`；Host 铸 N 项；3 成员 zip/cbz 真实 IPC；66 成员单 grant 末成员可授权；8/8 判别性）；独立 r1 **approved（P0=0/P1=0/P2=0/P3=4）**；AC-J1…J4 MET；P3-01/02/03 处置，P3-04 同名成员子集 follow-up。
- **基线（2B 交付实测）**：全量 pytest **3305 / 10**；全量 .NET **1562 / 0 / 91**；定向 python 74；SourceRegistry 32；真实 IPC 5；pins 18/18；check PASS(3w)；API PASS；scope changed=7 全 ALLOWED。
- **当前状态**：无活动 Task；`FEA-11-L-S1-REGISTRY-RESILIENCE-1` **proposed**（需 scope review）；排队：2C 长 Run 授权续期（L-G1，另卡）、L-S4 死代码、L-R11 gate 统一、C-04b 文档 residual、SCAN-2 RH-1…RH-5、UI P3/L3/L4。
- **limitations 不变**：L-R1 未全修；L-G12② 仅「缓存可用（≤4096 成员）容器源」面闭环；L-G16/L-G1/L-G2/L-G8/L-G9/L-G10/L-G11/L-G13/L-G14 保留；P3-04 可选加固。
- **push**：本轮 `git push origin main` → `61b7eb249..416b1692a`（PRE_HEAD `416b1692a`、PRE_ORIGIN `61b7eb249`、AHEAD 7→0、PUSH_EXIT=0、POST_ORIGIN `416b1692a`）；origin 同步（AHEAD=0）。

## 10. 续接补充（2026-11-07 第 2 轮：C-15 v1.5 / L-S1 A / L-S4 A）

> 本轮完成 1 张契约卡 + 2 张实现卡并 push；下一会话只读本文件 + STATUS/PLAN/LEDGER 即可恢复。

- **FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1 `done`**（`ae8c2de07`）：**C-15 v1.5 UNFREEZE**（Registry 文件级损坏与「根身份当前不可用」分离；1/18 pin 重签；C-16/C-17 零字节；错误码零新增）；独立 byte-level r1 changes → **r2 approved（P0/P1/P2=0）**；pins 18/18（C15 `f9e376a0…`）。
- **FEA-11-L-S1-REGISTRY-RESILIENCE-1（A）`done`**（`b56c5a0e6`）：`SourceAccessRegistry.Load` 只做文件级校验；`Authorize` 逐请求重核验请求路径所属根 identity（不可用 → typed `SOURCE_REGISTRY_UNAVAILABLE` 零写；缺失根≠无授权；不自动重建/重授权/恢复）；`List` 全部条目；文件级损坏路径一字未改；混合 registry 单测 + gated 真机 IPC + 5/5 判别性。独立 r1 **approved（P0=0/P1=0/P2=0/P3=7）**；AC-L1…L8 MET。
- **FEA-11-L-S4-LOCATION-AUTH-REFRESH-1（A）`done`**（`0ebb234bf`）：`refresh_source_location_auth` 单点原地刷新（合并死代码 + 替换内联 UPDATE）；接线 import 复用/页单元 + sync apply（含 D-2 整源 skip 一次条件刷新）；撤销/identity 不符零写；重注册→刷新→枚举闭环；7/7 判别性。独立 r1 **approved（P0=0/P1=0/P2=0/P3=7）**；AC-LS4-1…8 MET。
- **基线（本轮实测）**：全量 pytest **3317 / 10**；全量 .NET **1570 / 0 / 92**（Lead combined 全量 .NET 曾命中已知 flaky `FluentResidual2VisualEvidenceTests`，隔离复跑 1 passed）；pins **18/18**（C15 v1.5）；check PASS(3w)；API PASS。
- **当前状态**：无活动 Task；`FEA-11-L-S1-B-RECOVERY-REAUTH-1` **proposed**（恢复/重授权入口；需 C-16 v1.5 UNFREEZE + scope review）；排队：L-S4-B（零交互自动恢复枚举，需 C-16 v1.5）、2C 长 Run 续期（L-G1）、L-R11 gate 统一、C-04b residual、SCAN-RH、UI P3。
- **limitations 保留**：L-S1 B（恢复/重授权入口不存在）、C（`.corrupt-*` 无界复制）、`SOURCE_REGISTRY_UNAVAILABLE` 码义收窄、D-6 调度器投影；**L-S4-1**（缺触发器，零交互恢复需 B）、**L-S4-2**（folder 身份键）；**L-R1 未全修**；A 卡只兑现「单根不可用不再整库不可读/刷新事实」，**不宣称恢复已可用**。
- **push**：本轮 `git push origin main` → `d782c52a4..db12dc5e5`（PREREQ 线）与 `db12dc5e5..e3f1ff99a`（L-S1/L-S4 closeout）；PRE_HEAD `e3f1ff99a`、POST_ORIGIN `e3f1ff99a`、AHEAD=0、PUSH_EXIT=0。

## 11. 续接补充（2026-11-07 第 3 轮：L-S1-B1）

> 本轮完成 1 张实现卡（3 轮 Review 收敛）并 push；下一会话只读本文件 + STATUS/PLAN/LEDGER 即可恢复。

- **FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1）`done`**（delivery `80d2799de`；docs `8a249538a`）：**App 显式恢复/重授权入口**（App-only 零契约 0/18 pins）——只读 `source_list_roots` 探针分流（文件级→重置 / 根级→重授权 / 其它码→无动作）；撤销全部同路径 stale 条目→按登记 `roots[0]` 再注册→重跑预览；**单源归因**（多选歧义 → `MultipleSources` + 单选提示、零 wire/零撤销）；注册失败 fail-closed「已撤销、未重新授权」不回滚；不扩 `IHostController`（命令数 111）、`quarantine_path` 不展示、wire 77 帧根路径 0 命中/`[REDACTED]` 7。
- **Review 链**：r1 approved（P2×2：多选过宽、IPC 空转断言）→ 返修 `e9e1132a5` → r2 approved（P2×1：歧义提示不可达）→ 返修 `80d2799de` → **r3 approved（P0=0/P1=0/P2=0/P3=3 非阻断；P3 证据记数残留登记接受）**；AC-LSB-1…10 全 MET；判别性 6/6。
- **基线（本轮实测）**：全量 pytest **3317 / 10**；全量 .NET **1617 / 0 / 93**（+47 本卡）；定向 App `SourceRecovery` **47/0/0**；gated 真实 IPC **1/0/0**；pins **18/18**；check PASS(3w)；API PASS；scope changed=29 全 ALLOWED。
- **当前状态**：无活动 Task；`FEA-11-L-S4-B-AUTO-RECOVERY-1` **proposed**（零交互自动恢复枚举 + B2 roots 投影；**C-16 v1.5 批量载体**，1 pin；需 scope review）；排队：2C 长 Run 续期、L-R11 gate 统一、C-04b residual、SCAN-RH、UI P3。
- **limitations 保留**：B2/B3 未做；L-S4-1（零交互恢复）/L-S4-2（folder 身份键）；C-17 journal 撤销撕裂（仅登记）；`quarantine_path` 不展示；重复恢复累积 revoked 行（active 恒 1）；revoke ACK 计数口径；只承诺 file-source 同路径恢复；L-R1 未全修；不宣称自动恢复。
- **push**：`ac528828b..47a5b5167`（PUSH_EXIT=0；PRE_HEAD/POST_ORIGIN `47a5b5167`，AHEAD=0）。

## 12. 续接补充（2026-11-07 第 4 轮：C-16 v1.5 / L-S4-B）

- **FEA-11-L-S4-B-PREREQ-1 `done`**（`3a475b5b9`）：**C-16 v1.5 UNFREEZE**（`source.reattest/1` + §2.5 `ReattestSourceLocation` 条件单行 re-attest + §1 `roots_available` additive；只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值；Host 前置义务分离；拒绝/无匹配零写；幂等/单调；1/18 pins 重签，其余 17 零改动）。独立 byte-level 复核 r1–r7 `changes_requested`（记录/字节逐轮收敛）→ **r8 `approved`（P0=0/P1=0/P2=0/P3=0）**；另有 r9 独立字节复核 **approved**（仅判 C-16 字节）；pins **18/18**（C16 `a7f57ebd…`）。
- **FEA-11-L-S4-B-AUTO-RECOVERY-1** `ready`（base `c6ca1aa3c`）：实现中，Owner=`l-s4b-impl`；交付后需独立 Review → 集成门禁（pytest 3317/10、.NET 1617/0/93 基线）→ closeout → push。
- **当前状态**：HEAD `2c5d0a9d9`（origin 同步，AHEAD=0）；check PASS(3w)；pins 18/18。
- **limitations 保留**：B2 字段冻结、实现延后（无消费者）；L-S4-1（零交互恢复仅指 B1 显式动作之后）；L-S4-2（folder 身份键）；「零交互」不得写成自动恢复；C-15 零字节解释条件性（D-6）；L-R1 未全修。
- **push**：`59ba5189f..c6ca1aa3c`（UNFREEZE + closeout + base）、`c6ca1aa3c..2c5d0a9d9`（r8/r9 报告）；PUSH_EXIT=0，AHEAD=0。

## 13. 续接补充（2026-11-07 第 5 轮：L-S4-B 完成）

- **FEA-11-L-S4-B-AUTO-RECOVERY-1 `done`**（delivery `30bdeb4ce`；docs `9dda04b75`）：B1 显式重授权后的**枚举恢复**——Core `ReattestSourceLocation`（C-16 v1.5 §2.5：恰 2 键、host-only→shape→grant live/scope→四键身份→条件写 `registry_id/authorization_generation` 两列、`last_verified_at` 原值、拒绝零写、幂等/单调）+ Host 能力探测/`SourceRootReattestPlanner`/枚举 pre-pass（每轮每源一次、成功后重枚举一次）+ App B1 成功分支触发既有 refresh；gated 真实 IPC 闭环（B1→reattest→枚举恢复）4/0/0。
- 独立 r1 **approved（P0=0/P1=0/P2=0/P3=5 非阻断）**；AC-LS4B-1…10 全 MET；扩域仅 DSH 批准的 2 文件 3 行能力断言；.NET 预批未消耗。
- **基线（本轮实测）**：全量 pytest **3360/10**；全量 .NET **1644/0/94**；pins 18/18（C16 `a7f57ebd…`）；check PASS(3w)；API PASS；scope 35 文件全 ALLOWED。
- **L-S4-B-1 保留（重要）**：枚举恢复成立，但**扫描执行面仍被既有 `ResolveRegistryEntry` 同路径 revoked 旧条目 fail-closed 拦住（tick typed error）**；本卡只承诺枚举恢复，**不得**写「扫描恢复/自愈/自动恢复」。已登记后续卡 `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`（proposed，需 scope review / C-17 判定）。
- 当前：HEAD `69913d892`（origin 同步，AHEAD=0）；无活动 Task。下一队列：L-S4-B-1（proposed）、B2（proposed，roots 可用性实现延后）、2C 长 Run 续期、L-R11、C-04b、SCAN-RH、UI P3。
- 其他 limitation：B2 延后、folder（L-S4-2）、`source_reset_registry` 后无旧条目、L-S4-1、L-R1 未全修。
- **push**：`4e9ab8d90..69913d892`（L-S4-B 交付 + closeout + proposed 登记）；PUSH_EXIT=0，AHEAD=0。

## 14. 续接补充（2026-11-07 第 6 轮：L-S4-B-1 完成）

- **FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1 `done`**（delivery `bcc88e4a2`；docs `0c1390b2a`）：**枚举 target 扫描执行面恢复**——`VerifyEnumeratedTarget(target, out entry)` 复用同一次 `Registry.List()` 快照中已核验的 live `(registry_id, generation)`，`ScanAsync` 枚举分支直接铸 grant（消除二次 path 解析/TOCTOU）；非枚举 `ResolveRegistryEntry` 零改动；fail-closed 矩阵不变；gated 真 IPC tick 由 `error` → `ok`（`scan_frames=1`）。**零契约 0/18 pins**。
- 独立 r1 **approved（P0=0/P1=0/P2=0/P3=9 非阻断）**；AC-SER-1…6 全 MET；判别性 6/6。
- **基线（本轮实测）**：全量 pytest **3360/10**；全量 .NET **1652/0/94**；pins 18/18；check PASS(3w)；API PASS；scope 24 文件全 ALLOWED。
- **Run 面保留**：`HostRuntime.RunSourceRange` 仍按路径解析（零 diff）→ 已登记后续卡 `FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1`（proposed，需 scope review）。
- 当前：HEAD `28163f27d`（origin 同步，AHEAD=0）；无活动 Task。下一队列：L-S4-B-2（proposed）、B2（proposed，延后）、2C 长 Run、L-R11、C-04b、SCAN-RH、UI P3。
- 其他 limitation：B2、folder（L-S4-2）、L-S4-1、L-R1；backoff 口径「下一个未被既有 backoff 抑制的 tick」；不宣称自动恢复/自愈/自动重新授权/Run 面恢复。
- **push**：`b3143b7ca..28163f27d`（L-S4-B-1 交付 + closeout + proposed）；PUSH_EXIT=0，AHEAD=0。

## 15. 续接补充（2026-11-07 第 7 轮：L-S4-B-2 完成）

- **FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1 `done`**（delivery `fad1ec776`；docs `ca929aade`）：**Run 源范围解析恢复**——`HostRuntime.RunSourceRange.Resolve` 对枚举 target 复用 `SourceScanScheduler.SelectEnumeratedEntry` 选自身 live `(registry_id, generation)`；非枚举保持 `ResolveRegistryEntry` 字节不变；解析失败降级 `Unresolved`（不抛）；枚举 live 但 Core version 冷 → `ColdSources`（恢复 bounded on-demand 分类）；gated 真 IPC before `Unresolved=1`/页读拒绝 → after `Targets=1`/`bound_pages=1`/resolve OK。**零契约 0/18 pins**。
- 独立 r1 **approved（P0=0/P1=0/P2=0/P3=7 非阻断）**；AC-RUN-1…8 全 MET；判别性 5/5。
- **基线（本轮实测）**：全量 pytest **3360/10 EXIT=0**；全量 .NET **1660/1/95 EXIT=1**——唯一失败为既有 flaky `FluentR2ReworkTests.R3001_…`（App UI 时序），隔离复跑 5×9/0/0 + App.Tests 全量 770/0/7 PASS → 非本卡回归；pins 18/18；check PASS(3w)；API PASS；scope 24 文件全 ALLOWED。
- **L-S4-B 线收尾**：B（枚举恢复）→ B-1（扫描执行恢复）→ B-2（Run 范围解析）三卡 done；Run 面只承诺「预授权/冷源分类恢复」≠「Run 全面恢复」（managed-only Run 无需 source 授权；mint 仍 best-effort typed skip）。
- 当前：HEAD `313f88905`（origin 同步，AHEAD=0）；无活动 Task。下一候选：B2 `roots_available`（proposed，**延后至 roots UI/消费者立项**）、2C 长 Run 续期（L-G1）、L-R11 gate 统一、C-04b residual、SCAN-RH、UI P3。
- 其他 limitation：folder（L-S4-2）、L-S4-1、L-R1、多根 first-root；gated Core 行由测试侧 `AlignRegistryAsync` 对齐（本卡不发 reattest）。
- **push**：`7be65026e..313f88905`（L-S4-B-2 交付 + closeout + B2 proposed）；PUSH_EXIT=0，AHEAD=0。

## 16. 续接补充（2026-11-07 第 8 轮：2C 续期实现返修中，收尾交接）

> **新会话从这里读起**：本文件 + `doc/STATUS.md` + `doc/REBASELINE_PLAN.md` + `doc/TASK_LEDGER.md` 即可恢复。

### 当前恢复点
- 仓库 `G:\CODEX\New Manga`，main，**HEAD `6bc9dc449`（origin 同步，AHEAD=0）**；check PASS(3 warnings)；pins **18/18**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`）。
- **工作树含 Owner `l-s4b1-impl` 的未提交返修**（`HostOptions.cs`/`HostRuntime.cs`/`RunGrantRenewal.cs`/`RunGrantRenewalTests.cs` + `verification/FEA-11-RUN-GRANT-2C/logs/*`）——属返修中间态，**不得丢弃/强推**；未提交内容归原作者所有。

### 已完成（本轮）
- C-16 v1.5 批量 UNFREEZE（L-S4-B 线）：`3a475b5b9`（r8/r9 approved）。
- L-S4-B 线三卡 done：B `30bdeb4ce`、B-1 `bcc88e4a2`、B-2 `fad1ec776`。
- 2C 契约前置 done：`FEA-11-RUN-GRANT-2C-PREREQ-1`（C-06 v1.3 + C-16 v1.6，2 pins；`7317837d5`；r6 approved P0/P1/P2=0；closeout `fdd170039`）。
- 2C 实现已交付：delivery `e5e9c4c52`（`c40489b5d` 引擎+接线 → `e5e9c4c52` 测试 → `7c979f18d` evidence；**已在 main/已 push**）。
- 独立 Review r1：**changes_requested（P0=0/P1=1/P2=1/P3=5）**，报告 `doc/reviews/FEA-11-RUN-GRANT-2C-r1.md`：
  - **P1-01**：HostRuntime 续期接线无测试（Probe-C：`_runGrantRenewal=null` 后全量 Host 277/0/65、gated 7/0/0 全绿）→ 需 HostRuntime/dispatcher 级判别用例；
  - **P2-01**：`RoundBudget` 事后检查，单轮可含 8×30s on-demand 扫描 + mint → 可能越 300s 窗口/长占 `_gate` → 需单轮前预算约束；
  - P3×5：EV/Handoff `TBD-*`、manifest pyc/孤儿 head、LedgerStatus 死代码、预算停止吞 typed code/少计等。
- 已退回 Owner 返修（含 P3 同批修）；Owner 正在改，尚未重新交付。

### 下一步（新会话按序）
1. 等待/确认 `l-s4b1-impl` 返修交付（新 delivery_head）；若 Owner 不可用，Lead 可按 r1 报告自行完成 P1/P2/P3 修复（实现者与审查者需不同上下文）。
2. Lead 复跑门禁：全量 pytest/.NET（**当前新基线 3363/10、1674/0/96**；既有 flaky `FluentR2ReworkTests.R3001_*` 隔离）、Host 续期 13、gated IPC、fake clock、pins 18/18、check、API、scope（29 文件、`src/**` 零 diff）。
3. 派**独立 r2 Review**（复跑 Probe-C 判别 + 预算用例 + fake clock/gated）→ approved 后 closeout（卡 done/EV/Manifest/Closeout）→ STATUS/PLAN/LEDGER → push（记录 PRE/POST/AHEAD）。
4. 队列：L-R11、C-04b、SCAN-RH、UI P3；B2 `roots_available` 延后（无消费者）。

### 保留 limitation（不得夸大）
- **L-G1 只降级不关闭**：单步 >300s／续期失败（typed 停止、不重试、不 reattest、不自动重新授权）／L-G2 加密源／L-G9 Core 重启／L-R1 viewer 残余／L-G16 >4096 成员／未 dispatch 的 pending Run 不在范围／240s 重 mint 的 L-G8 成本放大（单轮 >50s 即停）。
- 2C 只承诺「有续期 + 子限制」，**不得**写任意长 Run 可用/L-G1 关闭/Run 全面恢复/自动恢复/自愈/自动重新授权/撤销后放行。
- B2 无消费者延后；folder（L-S4-2）、L-S4-1、L-R1、多根 first-root 保留。

## 17. 续接补充（2026-11-07 第 9 轮：2C 返修已交付，待 r2 + closeout）

- **状态更新（覆盖 §16 的「返修中」）**：Owner `l-s4b1-impl` 已完成 r1 返修并交付，**未 push**：
  - `7c95bb3c4` fix（P1-01 Host 接线判别 + P2-01 轮前预算 + P3）×
  - `03361fec6` docs/evidence（EV/Handoff/卡）
  - **delivery_head=`7c95bb3c4`**；`HEAD=03361fec6`；`origin=f1c4598e8`；**AHEAD=3（不可 reset/强推）**。
- **返修内容**：
  - P1-01：新增 `StartRunGrantRenewal()` 唯一安装行 + Host seam + 3 个 `HostWiring_*` 用例（生产 dispatch→Track→真实 Tick→renew）；**Probe-C 现为 RED（Host 281/2/65，2 failed 正是新接线用例）**，恢复后复绿；判别性 D8。
  - P2-01：roundBudget 进入单轮前传入 mint 路径（on-demand scan timeout=min(30s,剩余预算)），超预算 `SkippedBudget` typed skip + 计数（保留跟踪）；判别性 D9；用例断言单轮 <1.5s。
  - P3：预算停止记录 minted/code、`LedgerStatus` 接真实日志、EV/Handoff 去 TBD 与字面 `\n`、manifest 去 pyc/head 更新（21 evidence + 12 code sha 复核）。
- **Owner 报告门禁**：Host 续期 **19/0/0**；回归 32/0/7；gated 7/0/0；fake clock 3；定向 pytest 92；全量 pytest **3363/10**；全量 .NET **1680/0/96**；pins 18/18；check PASS×2；API 61；scope 32 文件全 ALLOWED、`src/**` 零 diff；判别性 **9/9**；Probe-C 复现/复原 sha MATCH。
- **下一步（新会话按序）**：
  1. Lead 复跑门禁（全量 pytest/.NET、Host `--filter HostWiring|RunGrantRenewal`、gated、fake clock、Probe-C apply/restore、pins/check/API/scope；跑后 `git checkout -- verification/FEA-09`）。
  2. 派**独立 r2 Review**（只读 `7c95bb3c4`；复跑 Probe-C 期望 281/2/65、HostWiring、预算用例；核对 `src/**` 零 diff 与 L-G1 措辞）。
  3. r2 approved → closeout（卡 done/EV/Manifest/Closeout→STATUS/PLAN/LEDGER）→ **push**（PRE/POST/AHEAD 记录；把 `7c95bb3c4`、`03361fec6` 与 closeout 一并推）。
  4. 队列：L-R11、C-04b、SCAN-RH、UI P3；B2 延后。
- **注意**：当前 AHEAD=3 的未 push 提交包含实现与证据；**不得 git reset --hard / push --force**；若中途发现需回退，先记录并交 DSH 裁决。
- **L-G1 口径不变**：只降级不关闭（单步 >300s／续期失败／L-G2／L-G9／L-R1／L-G16／未 dispatch pending Run／L-G8 成本放大）；不得写任意长 Run/自动恢复/自动重新授权。

## 18. 续接补充（2026-11-07 第 10 轮：2C closeout + push + L-R11 冻结释放）

- **FEA-11-RUN-GRANT-2C done**（integration/delivery **7c95bb3c4**；卡面 closeout + Canonical Evidence 22 项 + Resource Manifest 内联）。r1 changes_requested（P1-01/P2-01/P3×5）→ 返修 7c95bb3c4 → **r2 approved（P0=0/P1=0/P2=1/P3=7）**（fresh subagent session a4410d0a…）；R2-01（P2：3 条 HostWiring 未穿过 StartInternalAsync/dispatcher runDispatched/AcceptRun 调用点）→ 登记 **L-2C-01** limitation + follow-up（r2 附加删点探针全量 Host 仍 283/0/65 绿；当前代码正确）；R2-02…R2-08 P3 保留（R2-05 文档口径已清理）。
- **Lead 门禁实跑（2026-11-07）**：build 0/0；Host 定向 19/0/0；**Probe-C 281/2/65 → sha256 bae563e1… MATCH → 复绿 19/0/0**；gated 7/0/0；fake clock 3；全量 pytest **3363/10 EXIT=0**；全量 .NET **1680/0/96 EXIT=0**；pins 18/18；check（默认+TaskPath）PASS(3w)；API EXIT=0；scope PASS（changed=32 全 ALLOWED、src/** 零 diff）；跑后 git checkout -- verification/FEA-09（工作树 clean）。
- **L-R11 线启动**：独立 scope review doc/reviews/L-R11-GATE-UNIFY-scope-r1.md（session 5aa2c0cf…，verdict **recommended**；方案 C：Core 单谓词 + 全链检测；**1/18 pin UNFREEZE C-16 v1.7**；新发现两跳链两面均放行、dded 缺行不可检测）；**DSH 裁决（2026-11-07）**：采纳，先 PREREQ 后实现。已建/释放：FEA-11-L-R11-GATE-UNIFY-PREREQ-1 **ready**（C-16 v1.7 §2.4 :90/:93，1 pin，owner=dsh；独立 byte-level 复核待派）+ FEA-11-L-R11-GATE-UNIFY-1 **proposed**（Core-only，0 pin，depends PREREQ+2C）；PLAN READY 节点 = PREREQ；STATUS 指针 = PREREQ。
- **push**：1c4598e8..07a7d746a（PUSH_EXIT=0；PRE_HEAD 07a7d746a、PRE_ORIGIN f1c4598e8、AHEAD 4→0、POST_ORIGIN 07a7d746a）；含 7c95bb3c4 / 03361fec6 / 3945e1f5c / 07a7d746a（closeout + L-R11 释放）。
- **下一轮**：实施 PREREQ（C-16 v1.7）→ 派独立 byte-level 复核（fresh subagent，未参与起草）→ 重冻/矩阵/pins 18/18 → 释放实现卡 → 实现（建议 ZCode 或 DSH + fresh Review）→ 门禁 → closeout → push；队列：C-04b residual（文档卡）、SCAN-RH（RH-1…RH-5）、UI P3（FEA-12-UI-RESIDUAL-1 已 done，需确认残余）；B2 延后。

## 19. 续接补充（2026-11-07 第 11 轮：2C 门禁复核 + L-R11 PREREQ C-16 v1.7 UNFREEZE + 实现卡释放）

- **2C 独立 r2 approved**（doc/reviews/FEA-11-RUN-GRANT-2C-r2.md；P0=0/P1=0/P2=1/P3=7）→ 2C **done**（integration 7c95bb3c4；R2-01 P2 limitation **L-2C-01**；R2-02…08 P3 保留）→ closeout + **push** 1c4598e8..07a7d746a（AHEAD 4→0）。
- **L-R11 scope review r1**（doc/reviews/L-R11-GATE-UNIFY-scope-r1.md，session 5aa2c0cf…，recommended，方案 C 单谓词+全链，**1/18 pin UNFREEZE**；新发现两跳链两面均放行、dded 缺行不可检测）→ **DSH 裁决**：采纳，先 PREREQ 后实现。
- **FEA-11-L-R11-GATE-UNIFY-PREREQ-1 done**（integration/delivery **2175238ab**）：**C-16 v1.7 UNFREEZE**——§2.4 :90 口径改「旧 v7 legacy 无行 open / 新同步链缺行 fail-closed（C-17 §3.3），不得当 legacy 放行」；:93 改「两读面判定由 L-R11 统一为同一谓词」；C-17/C-06/C-15/C-07/M2-C1 与其余 17 pins **零字节**；pins **18/18**（C16 67286eec…）；check PASS×2；独立 byte-level **r1 approved（P0=0/P1=0/P2=0/P3=7 非阻断；session 9bc4c117-…；reviewed_head  7a7d746a）**；P3 处置：提交隔离/EV 措辞/卡面元数据/载体限定已落地，P3-03/P3-04 留后续 UNFREEZE。载体 doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md。
- **FEA-11-L-R11-GATE-UNIFY-1 已释放**（
eady，Owner **l-r11-impl**，base 2175238ab；Core-only 0 pin；allowed：source_sync.py/core_assembly.py/core_service.py + 新 	ests/fea11/test_source_gate_unify.py；AC-1…AC-6；Out 含 dded 缺行/写面/章级面）。实现进行中，交付后需 **fresh subagent 独立 Review** → 门禁 → closeout → push。
- **C-04b residual scope review r1**（doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md，session  fc94b7f…，**recommended**）：8 项分 docs-only 1 / 契约措辞 6 / 代码+契约 1；**建议 1 张 docs-only 卡（0 pin）**，不建议现在 UNFREEZE（若全改：C-04b 1/18 pin + M2-C1 仅记录型冻结契约，不是 2/18）；优先级 **P3 最低**，排在 L-R11 实现之后 → 待冻结 FEA-12-CORE-C04B-RESIDUAL-1。
- **push**： 7a7d746a..8584f412f（PUSH_EXIT=0；PRE_HEAD 8584f412f、PRE_ORIGIN  7a7d746a、AHEAD 2→0、POST_ORIGIN 8584f412f；含 C-16 v1.7 UNFREEZE + PREREQ closeout + 实现卡释放）。
- **UI P3 队列项已闭环**：FEA-12-UI-RESIDUAL-1 已 done（8e3bd03d6），后续 UI 残余仅为 L3 真机 NOT_RUN 等 limitation，不再单独建 P3 卡。
- **下一轮**：确认 l-r11-impl 交付（delivery_head/证据）→ 派 fresh subagent Review（复跑判别性 + legacy/一跳/两跳 + 门禁）→ approved → closeout → push；并行可冻结 C-04b docs-only 卡；SCAN-RH（RH-1…RH-5）随后。

## 20. 续接补充（2026-11-07 第 12 轮：C-04b residual 收口 + SCAN-RH scope review + L-R11 实现中）

- **`FEA-12-CORE-C04B-RESIDUAL-1` `done`**（docs-only，0 pin；integration/delivery **`698ac9524`**；后续 docs 修正 `423efa200`/`3c4f62dbf`）：冻结记录 §4A 一行 residual 扩为 `R-1…R-8` 表 + 新增 **L-3**（R-1 artifact 成员谓词代码偏差，未修）；新增 **§1C**（r1–r7 报告完整 sha256，闭合 **R-6**）；§4B「五轮」→「r1–r6 CHANGES + r7 APPROVE」；载体追加 **§5F** errata（R-2/R-3/R-4/R-5/R-7/R-8 现行权威读法）。**C-04b `acc8f0e0…` 与 M2-C1 `701093b5…` 契约字节零 diff**，pins 18/18；独立 docs-only **r1 approved（P0=0/P1=0/P2=0；P3 共 8：open=6 / fixed=1 / mitigated=1）**（session `c66cd50f-…`）。**口径：8 项中仅 R-6 完全闭合；R-1/R-2/R-5/R-7/R-8 规范修复待 UNFREEZE（另卡未建）；L-3 未修**。
- **C-04b residual scope review r1**（`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`，session `0fc94b7f…`，recommended）：8 项分类 docs-only 1 / 契约措辞 6 / 代码+契约 1；**精确 pin 口径 = C-04b 1/18 + M2-C1 仅记录型（非 2/18）**；不建议现在 UNFREEZE。
- **SCAN-RH scope review r1**（`doc/reviews/FEA-11-SCAN-RH-scope-r1.md`，session `c50bc2b0…`，**recommended**）：RH-1 真行为+半句假注释（`SourceScanScheduler.cs:914` vs 注释 `:846-849`；refresh 在途时第二次 Refresh 最坏等一个 tick 900s，不丢只延迟）；RH-2 真实生命周期缺口（`HostRuntime.cs:231` 用 `CancellationToken.None`；停机时在飞 refresh 不取消不 join，`Release()` 可能抛 `ObjectDisposedException` 记 WARN）；建议**一张 Host-only 小卡（implementation，0 pin）**修 RH-1/RH-2 + RH-4 文档订正，RH-3/RH-5 仅登记 limitation，**不做** targets 主动清理与 fake-Core seam；优先级排 L-R11 之后。
- **L-R11 实现进行中**：Owner `l-r11-impl`（card `FEA-11-L-R11-GATE-UNIFY-1`，base `2175238ab`）。落点已确认：单谓词下沉 `src/infrastructure/sqlite/source_sync.py`（模块级 `_publication_gate_verdict` 返回 open/pending/unavailable/corrupt_chain；`page_is_sync_managed` 复用同一链 walk），`core_assembly.read_gate` 与 `core_service._assert_source_sync_gate` 委托（corrupt_chain→unavailable，保持 legacy 零漂移）。已改 `source_sync.py`/`core_assembly.py`/`core_service.py`（未提交）；预计再 2–2.5h 交付。
- **push**：`28a2826af..3c4f62dbf`（PUSH_EXIT=0；PRE_HEAD `3c4f62dbf`、PRE_ORIGIN `28a2826af`、AHEAD 4→0、POST_ORIGIN `3c4f62dbf`；含 C-04b residual 收口 4 提交）。
- **下一轮**：① 等 `l-r11-impl` 交付 → 派 fresh subagent 独立 Review（legacy/一跳/两跳/判别性/门禁）→ approved → closeout → push；② 冻结 `FEA-11-SCAN-RH-1`（Host-only 0 pin；待 L-R11 落地后释放）；③ C-04b UNFREEZE 后续卡（R-1/R-2/R-5/R-7/R-8）按 DSH 裁决决定是否建立；B2 延后。

## 21. 续接补充（2026-11-08 第 13 轮：C-04b 收口终态 + SCAN-RH 卡冻结 + L-R11 实现中）

- **C-04b residual 终态**：`FEA-12-CORE-C04B-RESIDUAL-1` done（integration `698ac9524`；closeout `63b95abda`；EV/报告终版 `87e270a93`；Canonical Evidence 指向 `87e270a93`/sha `3e22c333…`）。**P3 口径统一为保守计法 open=6（8 项：fixed=1/mitigated=1/open=6；P3-8 已按 closeout 提交链处理但按提交时点计 open）**。C-04b/M2-C1 契约字节零 diff、pins 18/18。
- **`FEA-11-SCAN-RH-1` 已冻结**（`status: proposed`，`base_commit=a969f405f`，0 pin；DSH 裁决 D-1…D-4 全采纳）：RH-1 pending 重放 + RH-2 lifetime/停机 join（implementation）+ RH-4 表集口径订正（documentation）+ RH-3/RH-5 仅登记 limitation；`allowed_paths` 仅 `SourceScanScheduler.cs`/`HostRuntime.cs`（token 传递）/`SourceScanSchedulerTests.cs`/卡/评审/证据 + `FEA-11-SCAN-2.md` append-only 一行。**待 L-R11 收口后释放**。
- **SCAN-RH scope review r1**（`doc/reviews/FEA-11-SCAN-RH-scope-r1.md`，session `c50bc2b0…`，recommended）已入库（含终版精修 + 实跑：`--filter SourceScan` 68/0/0、`SourceWatcher` 19/0/0、`pytest -k "scan or scheduler"` 14 passed）。
- **L-R11 实现进行中**（Owner `l-r11-impl`）：工作树已有 `src/infrastructure/sqlite/source_sync.py`（动词 +152/−25 级）、`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py` 改动 + 新增 `tests/fea11/test_source_gate_unify.py`（**未提交**，不得触碰）。落点：单谓词 `_publication_gate_verdict`（open/pending/unavailable/corrupt_chain）+ `SourceSyncStore.publication_gate_of_page` 唯一入口；`read_gate`/`_assert_source_sync_gate` 委托；legacy 零漂移。
- **push**：`a4cc8a9b7..821aac0da`（含 C-04b 终态与 SCAN-RH 冻结；PUSH_EXIT=0）。当前 HEAD `821aac0da`（+ STATUS/handoff 本次 docs 提交），AHEAD→0。
- **下一轮**：等 L-R11 交付 → 派 fresh subagent 独立 Review（legacy/一跳/两跳/判别性/全量 pytest/check/pins/scope）→ approved → closeout（卡 done/EV/Manifest/Closeout）→ push；随后释放 `FEA-11-SCAN-RH-1`（或按 DSH 裁决）。

## 22. 续接补充（2026-11-08 第 14 轮：L-R11 gate 统一 done + SCAN-RH-1 释放）

- **`FEA-11-L-R11-GATE-UNIFY-1` `done`**（integration/delivery **`86cd1d124`**；feat `1c1c9ca2f` → test `86cd1d124` → docs/evidence `1e339f30a` → closeout `ffcfab050`）：**Core 单谓词 `_publication_gate_verdict` + `SourceSyncStore.publication_gate_of_page` + 全链 walk `_binding_chain_ids`**；`core_assembly.read_gate` 委托（corrupt_chain→unavailable）；`core_service._assert_source_sync_gate(+复数)` 委托并**删除旧一跳 previous_binding_id 启发式**；`read_gate` docstring 修正。**legacy 零回归**（previous NULL 与「previous 非空但全链无 publication」均 open）；**新同步链缺行（一跳 + 两跳）全链 fail-closed**，各面映射既有 family（Run `TARGET_NOT_FOUND`、provider `INVALID_INPUT` 0 次 prepare/read、resolve/reader `SOURCE_ACCESS_DENIED`、Authorize typed 零映射），无新码。
- **Review**：独立 fresh subagent **r1 `approved`（P0=0/P1=0/P2=0/P3=5 非阻断；reviewed_head `86cd1d124`）**（报告 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-r1.md`）；reviewer 独立复跑 3 个破坏点（无行即 corrupt / 全链改回一跳 / resolve 面恢复旧启发式）**3/3 RED + 复原 sha MATCH + 复绿**；manifest 33/33 sha MATCH。
- **Lead 集成门禁**：全量 pytest **3369/10 EXIT=0**（起点 3363/10，+6）；pins **18/18**；check（默认 + `-TaskPath`）PASS；API EXIT=0；scope 实现+测试仅 4 文件、`doc/plan`/`doc/contracts`/`schema.py`/`apps/**` 零 diff；`git diff --check` 0。
- **P3 保留**：manifest src changed-file sha 为工作树 CRLF（commit blob LF，文本一致，**EOL 口径**）；无 publication 链全链 walk 每代 2 查询 + reader 逐页潜在 N+1；谓词多语句无显式只读快照（残余 TOCTOU，修复前已有）；resolve 面对「非 healthy + pending」message 文本变化（码/类别不变）；docstring「only judgement in Core」宜限定 read-face。
- **limitation 保留**：**L-R11-a**（`relation='added'` 缺行不可检测 / plan receipt 未实现）、**L-R11-b**（写面/章级面仍 pending-only）、**L-R11-c**（无专用诊断码）、**L-R11-d**（不自动修复损坏行）、**L-R11-e**（legacy 真实 v7→v8）。**未声称** C-17 §3.3 完全实现 / L-R11 全部关闭。
- **`FEA-11-SCAN-RH-1` 已释放**（`ready`，Owner **`scan-rh-impl`**，base `a969f405f`，Host-only 0 pin）：RH-1 pending 重放 + RH-2 lifetime/停机 join（implementation）+ RH-4 表集口径订正 + RH-3/RH-5 仅登记。实现进行中。
- **push**：`2e4d6128e..ffcfab050`（PUSH_EXIT=0；含 L-R11 交付/closeout + SCAN-RH-1 释放）。当前 HEAD `ffcfab050`（+ 本 §22 提交），AHEAD→0。
- **下一轮**：等 `scan-rh-impl` 交付 → 派 fresh subagent 独立 Review（复跑判别性 + 全量 .NET/pytest/pins/scope）→ approved → closeout → push；C-04b UNFREEZE 后续（R-1/R-2/R-5/R-7/R-8，1/18 pin + M2-C1 记录型 rev）待 DSH 裁决是否建卡；B2 `roots_available` 延后（无消费者）。

## 23. 续接补充（2026-11-08 第 15 轮：SCAN-RH-1 done → 可推进队列耗尽）

- **`FEA-11-SCAN-RH-1` `done`**（integration/delivery **`fb74b4ef7`**；feat `938d598ac` → test `fb74b4ef7` → docs `1a769c9cc` → 门禁/scope `86c5b053a`/`327b299e6`/`33c1dd66f` → closeout `d5e2ec4ed`）：**RH-1** 抽出 `RefreshTargetsPassAsync`（非重放）+ `ReplayPendingRefreshAsync`，pass 完成枚举并释放闸门后按 `_refreshPending` **重放一次**（取消/已 disposed 不重放；有界不递归；`TickAsync` refresh→hint 顺序不变；注释改 "coalesced and replayed after the in-flight pass"）；**RH-2** 新增 `_lifetimeCts` + `_activeRefreshes`/`_refreshIdle`，枚举 token = caller ∪ lifetime（linked），`DisposeAsync` = disposed→Stop→cancel lifetime→join loop→**refresh join ≤2s**→hint join ≤2s→`_tickGate.Dispose()`（主路径 ODE 零逃逸）；**RH-4** 文档订正（Core 14 / Host 15 / C-17 16 基线；并集 17；缺 3 多 4）+ `FEA-11-SCAN-2.md` **append-only 一行（`1 0`）**；**RH-3/RH-5 仅登记不实现**。`HostRuntime.cs` 零 diff。
- **Review**：独立 fresh subagent **r1 `approved`（P0=0/P1=0/P2=0/P3=8 非阻断；reviewed_head `fb74b4ef7`；session `e14e3d88-…`）**；reviewer 独立复跑 M1（删重放）2 用例 RED → 复原 sha `6b77d9ca…` MATCH → touch mtime → 复绿 → 71 passed；并核对单飞/风暴/死锁、Dispose 顺序、SCAN-2 append-only、三套表集。
- **Lead 集成门禁**：build 0/0；定向 `~SourceScan` **71/0/0**、`~SourceWatcher` **19/0/0**；全量 .NET **1683/0/96 EXIT=0**（起点 1680/0/96）；全量 pytest **3369/10 EXIT=0**；pins **18/18**；check（默认 + `-TaskPath`）PASS；API EXIT=0；scope ⊆ allowed_paths、`HostRuntime.cs`/`src/**`/`doc/contracts`/schema/依赖零 diff；跑后 `verification/FEA-09` 已恢复。
- **P3 保留（8 项）**：**P3-1** `CreateLinkedTokenSource` 在内层 try 之外（极窄 ODE 窗口，需线程挂起 ≥2×2s；**未加固**——P0/P1=0、调用方恒传 `None`；登记 follow-up，**不得**据此宣称 AC-RH-2 100% 闭合）；P3-2 重放 pass 被取消时合并请求丢失；P3-3 join 半边判别竞态；P3-4 EV sha 为工作树 CRLF 口径；P3-5 scope 日志残留旧文件名/停在 `1a769c9cc`；P3-6 卡面 pytest 基线 3363 vs 3369（时点）；P3-7 loop join 无界（既有）；P3-8 hint pass 用 `CancellationToken.None`（既有）。
- **可推进队列耗尽（DSH 裁决）**：① **C-04b UNFREEZE 后续**（R-1 artifact 成员谓词 / R-2 §2.0 / R-5 首确认来源 / R-7 M2-C1 banner / R-8 单条 manifest；需 C-04b **1/18 pin** + M2-C1 记录型 rev）→ **裁决不推进**：scope review 明确「不建议现在 UNFREEZE」，正常数据无运行时/安全影响，成本>收益；作为 **contract debt** 记录在 `FEA-CONTRACT-FROZEN-C04b.md` §4A `R-1…R-8`，未来若因审计/实现需要再立卡。② **B2 `roots_available`**：延后（无消费者）。③ 其余 `TASK_LEDGER` 非终态卡均为历史/旧架构/Rust 线（不属 FEA 线当前 DAG）。
- **push**：`d09e91d1d..d5e2ec4ed`（PUSH_EXIT=0；含 SCAN-RH-1 交付/closeout）。HEAD `d5e2ec4ed`（+ 本 §23 与 STATUS 指针提交），AHEAD→0。
- **结论**：FEA 线当前可推进队列（2C → L-R11 → C-04b → SCAN-RH → UI P3）**已全部收口**；无 active/ready 可执行卡。恢复入口：本文件 + `doc/STATUS.md` + `doc/REBASELINE_PLAN.md` + `doc/TASK_LEDGER.md`。

## 24. 续接补充（2026-11-08 第 16 轮：C-04b v1.2 UNFREEZE done + RESIDUAL-3 释放）

- **`FEA-12-CORE-C04B-RESIDUAL-2` `done`**（integration **`26aa0ca4a`**；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`）：**C-04b v1.2**（`4b304c0c…`）+ **M2-C1 rev 2.15**（`a82a7fc1…`，0/18 机械 pin，记录登记）——R-1 artifact 谓词补 `media_artifacts.book_id = 本书`；R-2 §2.0 措辞；R-3 删 `separate/detached` + 写死 representative；R-4 §1 表行号→节名；R-5 请求 `book_ids` + 单条 `inventoryDigests[bookId]`；R-8 单条 manifest 取值。**仅措辞与谓词文字；规则/字段/错误码/能力/`PROTOCOL_MINOR`/wire minor 零改动**；pins **18/18**（其余 17 blob 与 HEAD 全同）。
- **Review 链（三轮，两个 P1 由 reviewer 探针发现）**：r1 `changes_requested`（P0=0/P1=2/P2=1/P3=4）——representative 误改为 region 字典序、M2-C1 `:972` 缺谓词；r2 `changes_requested`（P0=0/P1=1/P2=2/P3=2）——**artifact fallback 取 pointer 首项而非排序数组首项**（探针：DTO `["aaa","zzz"]` → `"zzz"`）；r3 **`approved`（P0=0/P1=0/P2=3/P3=4；session `98692074-…`）**，三案探针确认与 `core_service.py:1907-1930` + `library.py:1158-1190` 逐要素等价。
- **过程事故（未进入提交，已修复）**：批量 `Replace` 曾把 FROZEN-C04b 内所有 `R` 写成 `-`（如 `UNF-EEZE`、`--1…--8`）。提交前用编码/词元扫描发现 → `git checkout -- doc/plan/FEA-CONTRACT-FROZEN-C04b.md` 恢复 HEAD 版本 → **改用 edit 工具（UTF-8 安全）重做 6 处改动**；最终校验 bad `--N`=0、UNFREEZE=33、R-1…R-8 齐全、pins/check PASS。**教训：含中文的批量文本替换改用 edit 或 Python 显式 UTF-8，勿用 PowerShell `Replace` 后 `Set-Content`。**
- **`FEA-12-CORE-C04B-RESIDUAL-3` 已释放**（`ready`，Owner **`c04b-impl`**，base `26aa0ca4a`，0 pin）：R-1 **artifact 成员谓词代码**修复（`library.py:1178-1190` page/chapter join → `media_artifacts.book_id = 本书`）+ 跨书损坏行判别用例；**不改 representative 语义**（已定案 pointer 首项，勿改字典序）。
- **limitation 保留**：R-1 代码**未改** → 契约与实现当前不一致、**L-3 仍有效**（归 RESIDUAL-3）；R-6 已闭合；R-7 已由 rev 2.15 落地；P3-1（M2-C1 `:140` 仍写「文档 rev 2.14」）**保留不改**（历史段落，改字节需新一轮独立复核）。**不得**写「8 项 residual 全部关闭 / R-1 已修复」。
- **push**：`d91d9b6cc..857354751`（PUSH_EXIT=0；含 UNFREEZE 提交 `26aa0ca4a` 与 closeout `857354751`）。HEAD=origin=`857354751`，AHEAD=0。
- **下一轮**：`FEA-12-CORE-C04B-RESIDUAL-3` 实现（R-1 代码 + 判别测试）→ 独立 Review → 门禁（pytest 3369/10 不降、pins 18/18、check、API、scope）→ closeout（并更新 L-3 为「已修」）→ push；之后时间/契约债务队列见 `REBASELINE_PLAN`。

## 25. 续接补充（2026-11-08 第 17 轮：RESIDUAL-3 R-1 代码修复 done）

- **`FEA-12-CORE-C04B-RESIDUAL-3` `done`**（integration **`25dc1523c`**；docs/evidence `6e20d5d28`+`2babb0c78`）：`library.py` 的 `list_book_artifact_current_pointers` 成员谓词 `WHERE c.book_id = ?` → **`WHERE ma.book_id = ?`**（保留 `current_revision_id IS NOT NULL`、不过滤可见性），pages/chapters 改 **`LEFT JOIN`**（仅阅读序排序 + `page_id` 投影），阅读序 7 键逐项保留；与删除面 `DELETE FROM media_artifacts WHERE book_id = ?`、`list_book_artifact_revision_ids` 同源；`core_service.py`/representative/删除事务 **零改动**。**R-1 代码与 C-04b v1.2 谓词现已一致，L-3 关闭（保留为历史）**。
- **Review**：fresh subagent **r1 `approved`（P0=0/P1=0/P2=2/P3=4；session `a4b5d82e-…`）**；reviewer 独立复跑判别性（回退谓词 → 3 failed → 复原 `da07ccdb…` MATCH + touch → 3 passed）、pins 18/18、check×2、API、manifest 15/15 MATCH。
- **Lead 集成门禁**：全量 pytest **3372 passed / 10 skipped**（起点 3369/10 → +3）；定向 **59 passed**（起点 56）；pins **18/18**（契约零改动）；check（默认 + `-TaskPath`）PASS；API EXIT=0；实现 diff 仅 `library.py` + 测试 2 文件，契约/schema/apps/依赖零 diff。
- **P2/P3 处置**：R3-001（卡面 AC-3 方向笔误「A 不含/B 含」应为「A 含/B 不含」）→ **closeout 已更正**（实现与测试自始按正确方向落地并双向覆盖）；**R3-002**（`media_artifacts.book_id` 无索引 → `SCAN ma`；60k artifacts 实测 0.26→5.32 ms/书）→ 登记冻结记录 §4A **L-4**（建议后续独立 schema 卡加 `idx_media_artifacts_book(book_id)`；本卡 AC-4 要求 schema 零 diff 故未改）；**R3-003**（损坏数据下 `currentRevisionId` 展示值可能随成员/排序键变化；规则未改、不进 digest）→ closeout limitation 已含；**R3-004**（`preview_lifecycle` 清理枚举按 page 归属，损坏行可能漏清；pre-existing）→ 登记 **L-5**；**R3-005**（`reviewed_head=25dc1523c` vs evidence HEAD=`2babb0c78`、20 文件）→ closeout 已写明；**R3-006**（静态断言 `inspect.getsource` 白空格脆性）→ follow-up 登记。
- **口径**：R-1～R-8 均已处置（R-6 闭合、R-7 由 rev 2.15 落地、R-1/R-2/R-3/R-4/R-5/R-8 契约文字由 RESIDUAL-2 修正、**R-1 代码由本卡修复并与契约一致**）；但 **L-1/L-2/L-4/L-5 运行限制仍在**；**不得**写「8 项 residual 全部关闭」。
- **push**：`4c42e11b8..a88b1780a`（PUSH_EXIT=0；含 RESIDUAL-3 交付/closeout）。HEAD=origin=`a88b1780a`，AHEAD=0。
- **队列状态**：`READY 节点：无`；`STATUS：无活动 Task`（指针指向 proposed B2 以满足 checker）。**下一候选**：`media_artifacts.book_id` 索引入卡（L-4 / R3-002）——**需先 scope review 判定**：`schema.py` 加索引是否触及 C-15 冻结 DDL（若需 UNFREEZE 则 1 pin），以及 migration 形状/兼容/回滚；B2 延后（无消费者）；RH-3 根治（C-17 additive）成本更高，排后。

## 26. 续接补充（2026-11-08 第 18 轮：INDEX-L4-1 done（v9 索引）+ 可推进项判定）

- **`FEA-12-CORE-C04B-INDEX-L4-1` `done`**（integration **`e593cc9d7`**；docs/evidence `9618056f2`；closeout **`ffa243905`**）：`schema.py` **+22/−0**——`SCHEMA_VERSION_V9=9`、`MIGRATION_V9_NAME="v9__media_artifacts_book_index"`、单条**裸** `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`、+1 元组项；**v1–v8 迁移字节零改**（新测试 checksum 硬校验 + reviewer 8/8 逐字节比对）。**0 pin、无 UNFREEZE**（scope review 判定 C-15 冻结字节是 v7 规范 DDL、不含 `media_artifacts`；18 pin 不含 `schema.py`）。
- **效果**：`EXPLAIN` 由 `SCAN ma` → **`SEARCH ma USING INDEX idx_media_artifacts_book`**；COUNT/DELETE 走覆盖索引；60k 厚数据集 8.90→**4.36 ms/书**（旧谓词实测 2.85，仍 **1.53×**，如实登记）；preview/删除面结果逐值等价。
- **Review**：fresh subagent **r1 `approved`（P0=0/P1=0/P2=0/P3=6；session `231cd1fe-…`）**；判别性（v9 SQL 改 `SELECT 1;` → 13 failed → 复原 `5fe87b69…` MATCH → 33 passed）；风险探针：同名索引已存在 → `OperationalError`、停 v8、DROP 后重试到 9（fail-closed）。
- **DSH 扩域裁决**：实现中发现册外派生断言 `tests/storage/test_upgrade_schema_data.py`（`MIGRATIONS[:-1]` 派生 + `assert new_tables`，v9 纯索引迁移必然 `new_tables=[]`）→ 授权扩 allowed_paths，做**不放宽方向**最小修复（新增表**或**新增索引 + v8 起点显式断言索引出现）。
- **Lead 集成门禁**：build 0/0；定向 **109 passed**；全量 pytest **3390/10 EXIT=0**（起点 3372/10 → +18）；全量 .NET **1683/0/96 EXIT=0**（不降）；pins **18/18**；check×2 PASS；API EXIT=0；scope 29 文件全 ⊆ allowed_paths；跑后 `verification/FEA-09` 恢复。
- **P3 处置**：R4-001（limitation「5.81」→ 实测 **2.85**）已更正；R4-006（「5 处」→ **6 处**：test_v7 ×4 + test_source_gate_unify ×1 + C# ×1）已更正；R4-005 已在 closeout 补正 manifest `tmp/` 措辞；**R4-003**（`ipc_seed.py` docstring 过时）**不改**（连锁改 sha/manifest，成本>收益）、**R4-002**（storage `or` 断言兜底 v1–v7「新增表」方向）、**R4-004**（唯一 .NET 断言在 opt-in skipped 测试）均登记 P3。
- **L-4 关闭**（冻结记录 §4A 更新为「已修（本卡）」）。
- **push**：`d7823a0e0..ffa243905`（PUSH_EXIT=0）。HEAD=origin=`ffa243905`，AHEAD=0。
- **可推进项判定（DSH 裁决，依据 AUTORUN §2）**：
  - (a) 用户可见价值且无需解冻：**无**（剩余均为内部质量/诊断）；
  - (b) 契约债务清偿：**已清**（`R-1…R-8` 全处置：R-6 闭合、R-7 由 rev 2.15 落地、6 项文字由 RESIDUAL-2 修正、R-1 代码由 RESIDUAL-3 修复；`L-4` 由本卡修复）；
  - (c) 需改核心协议才有运行时收益：**RH-3 根治**（需 C-17 additive UNFREEZE + Host 删除 API）——SCAN-RH scope review 与历史裁决均判「不值得」，且「软删源」当前无生产者 → **不立项**，保持 `FEA-11-SCAN-2.md:252` + SCAN-RH 卡 limitation 登记；
  - (d) B2 `roots_available`：无消费者 → **不做**（STATUS/PLAN 已记延后）；
  - (e) UI L3 真机：仅真机可验 → **不做**（`FEA-12-UI` 卡已记 NOT_RUN limitation）；
  - 其余已登记 P3（SCAN-RH P3-1/P3-3、2C R2-02…08、L-R11 P3、C-04b R4-002/003/004/005、RESIDUAL-1 P3）均**非阻塞、已留痕**，不再逐项开卡。
  - **结论：可推进项耗尽（停止条件①）**；后续仅在出现新需求/新证据（如 roots UI 立项、真机环境、RH-3 有真实生产者）时再开卡。

## 27. 续接补充（2026-11-08 第 19 轮：**推翻 §26「耗尽」结论** + FEA-12-UI-RESIDUAL-2 done）

- **⚠ 上轮结论被推翻（如实记录）**：§26 判「可推进项耗尽（停止条件①）」**是错的**。本轮按「先核实，不要相信叙述」重做候选面：并行派两个独立只读审计（用户可见价值面 / 工程契约债务面），两者均 HAS_CANDIDATE；DSH 逐行复核确认两条**未登记**的用户可见缺陷（①回收站恢复成功后书架不刷新；②回收站假空态 + 「加载更多」不可达）。**教训**：卡面 label（如「登记 follow-up」）与 P3 清单**不能**当作穷尽证据，必须回到真实代码链 + 独立上下文复核（本轮 4 个独立只读子代理：2 审计 + 2 scope review + 1 Review）。
- **门禁一手复跑（HEAD 54e5d69db）**：build 0/0；全量 .NET **1683/0/96**；全量 pytest **3390/10**；pins 18/18；check PASS(3w)；跑后 git checkout -- verification/FEA-09。→ 基线从「叙述」变为一手事实（同时发现 STATUS/AUTORUN 的 3369 漂移，见下）。
- **FEA-12-UI-RESIDUAL-2 done**（integration/delivery **85356c22a**；冻结卡 7c63bc50；closeout **5f3431dfd**）：App-only 三条修复 ——
  - **A（AC-R1/R2）**：TrashViewModel 构造增可选 Func<Task>? onBooksRestored，RestoreSelectedAsync 在 SucceededIds.Count>0 时 wait 该回调；LibraryViewModel 装配 () => RefreshAsync()（orceHostRead:true）。覆盖 RecycleBinView.axaml:120 绑定的唯一活动入口；部分成功刷新、全失败不刷新不伪报；**不用 event**（async void 竞态）。
  - **B（AC-R3/R4）**：IsEmpty 增 && _nextCursor is null；ShowList 改 (Items.Count > 0 || HasMore)；恢复与彻底删除两条路径同构覆盖；不改 XAML、不自动重载。
  - **A′（AC-R6，第二轮独立评审发现）**：IsRecycleBinView setter 补 
ameof(BookCountText)、
ameof(ListStatusText)，修「进入回收站 bar 仍显示 N/M 作品」「返回后残留『回收站』」。
  - 零 XAML/契约/wire/schema/依赖变更；**0 pin、无 UNFREEZE**；死代码 RecycleRestoreCommand 按裁决保留（L-3）。
- **Review 链**：冻结前两轮独立 scope review（402ec34a-…、986a9e4c-…）均 **READY-TO-FREEZE**（第二轮独立发现 A′ 并指出「只断 RefreshCalls/Snapshot.Books 会假绿」）；实现后独立 Review r1 **approved（P0=0/P1=0/P2=1/P3=5；session 897f3928-…）**；**7 组变异实测：M1/M2/M3/M4/M5/M6b 共 15 RED**，逐字节复原 sha256 MATCH 后 74 全绿；**M6a 0 RED → 登记 L-4（ShowList 能力/probe 短路子句仅结构性保护、无变异判别）**。
- **Lead 集成门禁（亲自实跑）**：build 0/0；定向 **74/0/0**；全量 .NET **1691/0/96**（+8 新用例、0 failed）；全量 pytest **3390/10**（不降）；pins **18/18**；check（默认 + -TaskPath）PASS(3w)×2；generate_api_inventory.py --check EXIT=0；scope 5 文件 ⊆ allowed_paths、禁止面零 diff；跑后 FEA-09 已恢复。
- **AC/证据**：AC-R1…AC-R6 全 MET（AC-R3 的 ShowList 短路子句按 **L-4** 降级表述）；erification/FEA-12-UI-RESIDUAL-2/ EV-01…EV-26（含 reviewer 变异日志逐字节归档、Lead 门禁日志、changed-files、Resource Manifest）；closeout_counts = deleted/moved/migrated/archived = 0/0/0。
- **limitation（保留，不得夸大）**：**L-2**（恢复后 RefreshAsync 按既有语义自动选中 Books[0]，接受不修）、**L-3**（RecycleRestoreCommand 死代码另卡）、**L-4**（ShowList 短路子句无判别测试，P3-01）、**L-5**（回调异常面 + RefreshAsync 无重入闸，既有结构）、**L-6**（T2 等待谓词不判别）、**L-7**（T7 一处空断言；ListStatusText 无 UI 消费者）、**L-8**（证据级别 VM headless；真实 IPC 与 L3/L4 真机 **NOT_RUN**）。FEA-12-UI 的 L1/L2/L3/L8 原样保留。
- **口径红线**：**不得**写「回收站已完全修复 / UI L1–L10 已关闭 / AC-R3 回归栅栏已被变异钉住」。
- **文档对账（本轮）**：STATUS 测试基线 3369→**3390/10**（.NET 1691/0/96）；DSH-AUTORUN-PROMPT → **v1.1**（基线同步、§7 队列快照刷新并标注 §26 结论被推翻）；STATUS push 指针改为引用 §27（不再写死过期 sha）。**README 漂移已登记未改**（.NET 258/258、pytest 2773、managed copy 与 AD-003/实际基线冲突）→ 下一轮 docs 卡候选②。
- **下一候选（需先 scope review）**：① **2C typed-stop / 预算守卫次序残项**（Host-only：RunGrantRenewal.cs:371-390 事后预算守卫先于 !outcome.KeepsTracking ⇒ typed 停止被改写成 budget skip，违背 AC-2C-4「typed→Stop 不重试」；登记 FEA-11-RUN-GRANT-2C-r2.md:159 R2-03，同族 R2-02/R2-04；0 pin）；② **README 基线/AD-003 对账**（docs，0 pin）；③ L-4 的补测试（补「已加载行 + 能力翻转 + RefreshAsync」用例）。
- **push**：PRE_HEAD=85356c22a、PRE_ORIGIN=54e5d69db、AHEAD_BEFORE=2 → **push1 54e5d69db..5f3431dfd（PUSH1_EXIT=0）**；本节提交 **73462ac33** → **push2 5f3431dfd..73462ac33（PUSH2_EXIT=0）**；POST_ORIGIN=73462ac33、POST_AHEAD=0；最终 HEAD=origin，工作树 clean。

## 28. 续接补充（2026-11-08 第 20 轮：残余收口方案 + 专用 AUTORUN 提示词）

- **本轮性质**：用户要求「把 4 个 closed_with_limitations 彻底解决」，本轮只产出**方案与提示词**（未开实现卡，未改节点状态）。
- **产出 1**：[RESIDUAL-CLOSEOUT-PLAN-2026-11-08](../plan/RESIDUAL-CLOSEOUT-PLAN-2026-11-08.md)：把 4 节点残余分为 C1 工程可闭环 / C2 契约对齐 / C3 设计选择·范围外 / C4 硬件，逐项给关闭路径；定义「彻底解决」= done 或 done+waiver（C3/C4 标 NOT_APPLICABLE: 原因），禁止伪造硬件 PASS。
  - 关键判断：**只有 R1（FEA-11-HOST-AUTH-2）能不依赖 waiver 直接翻 done**；FEA-06-RESIDUAL-2 的 6 个 BLOCKED 格中 **5 格依赖已 done**（FEA-09/10/12）可补做；FEA-11 与 FEA-07 各有 C3/C4 项必须走裁决。
  - 卡片序列：R0 RESIDUAL-WAIVER-1（治理，10 项裁决）→ R1 FEA-11-HOST-AUTH-2 → R2 FEA-06-RESIDUAL-3 → R3 FEA-11-RESIDUAL-4A → R4 FEA-07-RESIDUAL-2；每卡完成即翻对应节点（append-only），预计 6–8 轮。
- **产出 2**：[DSH-AUTORUN-PROMPT-RESIDUAL-CLOSEOUT](DSH-AUTORUN-PROMPT-RESIDUAL-CLOSEOUT.md)：可直接粘贴的专用持续推进提示词（队列/流水线/门禁/红线/停止条件/已知坑）。
- **指针**：STATUS 增「残余收口 PLAN」行；DSH-AUTORUN-PROMPT §7 增独立程序指引。
- **未做**：未创建任何 R0–R4 卡文件（按流程，立项前必须先派独立 scope review）；未改任何节点 closed_with_limitations 状态；未改契约/pins。

## 29. 续接补充（2026-11-08 第 21 轮：残余收口 R0 裁决 v2 + R1 冻结）

- **固定核实**：HEAD=origin=`4070f0043`，AHEAD=0，工作树 clean；check PASS(3w)；pins 18/18；PLAN `READY 节点：无`。
- **R0（`RESIDUAL-WAIVER-1`）**：独立 scope review **`NOT_RECOMMENDED`**（session `4092531d-…`）→ **DSH 采纳并改写为 v2**：
  - 4 项被误判为「不可工程闭环」（FEA-07 AC1 的 A03/ACK/Run、AC2 的单写 owner、FEA-06-RESIDUAL-2 的 Tab 遍历/a11y 属性）→ **改判 C1，进实现卡**；
  - 2 项契约依据被推翻（PDF 插页在 C-15 §3.2 `:230` 覆盖内有 matcher 消费者；folder relink 在 C-17 `:278` 允许「能证明同一」）→ **不再 NA**；
  - 「无硬件」事实错误（本机实测 **2 个活动显示器** + 仓库记录 3 个虚拟适配器）→ 改口径为「**原生交互矩阵未执行**」；
  - 基线漂移（STATUS `:20` 写 1683，实际 1691）→ **本轮已修正**；
  - 治理冲突（翻 done 需改写 17 条历史 AC 行 vs `09_COLLABORATION:79` 与 HOST-AUTH-1 Codex 终裁）→ **以用户 2026-11-08 指令为新授权**，按节点逐个翻转 + 逐条 before/after 登记 + 不改 Review/证据字节（`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §3）。
  - 产出：`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md`（v2，12 项裁决表 + 翻转矩阵 + 边界）、`doc/reviews/RESIDUAL-WAIVER-1-scope-r1.md`（评审原文落盘）、PLAN 追加 §11 v2 修订。
- **R1（`FEA-11-HOST-AUTH-2`）**：独立 scope review **`READY-TO-FREEZE`**（session `bd32e3f6-…`）→ **DSH 冻结**（base `4070f0043`，0 pin）：
  - 契约：C-17 `:161`/`:169` 经独立复核确属**冻结字节**（pin `aefa0fa5…` 实测一致、v1.0 逐行比对未变）→ 遵守型修复，**无需 UNFREEZE**；
  - 缺陷确认：ACK/recovery 均以 journal 原 authorization 发送（`SourceOperationCoordinator.cs:172-174`、`:232-233`），无 Registry 重验、无 fresh mint；
  - 卡面 AC-F1…AC-F5 + 实现口径（Prepare seam、先落盘、锁内 state 守卫、拒绝码复用）+ **窄口径 done**：limitation {1,2,5,P2-7} 关闭、**{3,4,6,7,8,9} re-home**（3/4 属 C-17 UNFREEZE 类）。
  - 评审原文：`doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md`；卡：`doc/tasks/FEA-11-HOST-AUTH-2.md`。
- **指针**：PLAN `READY 节点：FEA-11-HOST-AUTH-2`（未加行）；STATUS 当前 Task 指向本卡；`task_ledger.py --write` 已重跑。
- **下一轮**：R1 实现（fresh 授权 + 拒绝矩阵 + gated e2e + 崩溃点）→ 独立 Review → 集成门禁 → `FEA-11-HOST-AUTH-1` append-only 翻 done → push。
- **未做**：未开 R2/R3/R4 卡（按流程先 scope review）；未改任何节点终态；未改契约/pins。
