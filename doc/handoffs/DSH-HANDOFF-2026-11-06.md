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
