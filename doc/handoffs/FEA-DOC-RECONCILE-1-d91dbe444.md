---
task_id: FEA-DOC-RECONCILE-1
author: DSH（Lead / Integrator）
recipient: DeepSeek Harness
base_commit: 9b0683822
delivery_head: d91dbe444
status: delivered
---

# Handoff：FEA-DOC-RECONCILE-1（FEA 线文档对账）

## 交付结果

对账 7 项（见 Task 卡 §对账清单），**0 源码 / 0 契约字节 / 0 pin 重算**，全部为文档与卡级状态修正。交付提交 `d91dbe444`（9 files, +175/−23），基线 `9b0683822`。

| 变更路径 | 内容 |
|---|---|
| `doc/STATUS.md` | 当前 Task 指向本卡；「FEA-12 四表 DDL 未冻」→「四表 DDL 已冻（C-15 v7 + FEA-11-PREREQ-1 v8+）」 |
| `doc/REBASELINE_PLAN.md` | `FEA-C11-PREREQ-1` 行翻 `done`（集成 `b7018e19b`）；新增本卡 DAG 行（含 FEA-02-BRIDGE 裁决）；腾预算时把 C-04b 注记并入「完成」行，**r2 已补回 `Owner c04b-impl` 署名** |
| `doc/tasks/FEA-GOV-11.md` | `status: done`；AC1–AC3 `<<MET>>`；Closeout 追加（引 `ADJ-2026-11-01-FEA-DECISIONS.md` 与 4 份冻结记录） |
| `doc/tasks/FEA-D07-UNBLOCK.md` | `status: done`；AC8 `[x] <<MET>>`（原 `[ ]`+`<<MET>>` 矛盾）；Closeout 追加（引 Gate 关闭裁定） |
| `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | append-only「对账补充」：v2 壳 F11 入口 limitation 由 `FEA-07-V2-F11-1` 关闭；status 不变 |
| `doc/tasks/FEA-11-RUN-GRANT-2.md` | append-only「对账注记」：title 中「proposed，待依赖」为历史描述 |
| `doc/TASK_LEDGER.md` | 重生成（GOV-11/D07 退出非终态；本卡入 plan-row） |
| `doc/tasks/FEA-DOC-RECONCILE-1.md` | 新建对账卡（governance v3，AC1–AC8 MET / AC9 PARTIAL 待 Review） |
| `verification/FEA-DOC-RECONCILE-1/gates.log` | 门禁原始输出（check / check -TaskPath / pins / git status） |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC7 | 逐项 diff 对照 Task 卡 §对账清单「事实依据」列 | `d91dbe444` | PASS | Task 卡 §对账清单 |
| AC8 check | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 `d91dbe444` | **PASS（3 warnings）** | `verification/FEA-DOC-RECONCILE-1/gates.log` |
| AC8 check -TaskPath | `... check.ps1 -TaskPath doc/tasks/FEA-DOC-RECONCILE-1.md` | 同上 | PASS（3 warnings） | 同上 |
| AC8 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | **PASS 18/18** | 同上 |
| AC8 ledger | `python tools/governance/task_ledger.py --write` | Python 3.14.6 | PASS（ledger 重生成） | `doc/TASK_LEDGER.md` |
| AC8 预算 | STATUS 2997 B/28 行（≤3200/45）；PLAN 6985 B/63 行（≤7000/64） | 同上 | PASS | gates.log |
| AC9 独立 Review | fresh subagent 只读审查 | 交付 head | NOT_RUN（交付后立即指派） | `doc/reviews/FEA-DOC-RECONCILE-1-r1.md` |

未运行项：真实构建/测试套件（本轮 0 源码改动，不适用）；`FEA-07-AC5-NATIVE-1` 与 `FEA-06-RESIDUAL-1` 未处理（用户动作/残余承接未变，超出对账范围）。

## 接收方式

- 分支 `main`，无 worktree；基线 `9b0683822` → 交付 `d91dbe444`。
- 复核命令：`git show --stat d91dbe444`、`git diff 9b0683822..d91dbe444 -- doc/`、两条门禁命令。
- 关键事实核对点（Review 建议逐项验证）：`FEA-CONTRACT-FROZEN-C15.md:43,50`、`FEA-11-PREREQ-1.md:65`（v8 DDL AC-P1 MET）、`FEA-C11-PREREQ-1.md` Closeout 2026-11-02（`b7018e19b`）、`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md`（R/U-04/U-05a/U-05b）、`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md`（Gate CLOSED）、`doc/tasks/FEA-07-V2-F11-1.md`（done + 2K 复验）。
- 下一接收者需确认：append-only 边界（是否误改历史字节）、STATUS/PLAN 指针唯一性、预算是否可接受。

## 下一任务建议（必填）

- Task ID / 标题：`FEA-07-RESIDUAL-4`（既有 headless 用例真实 AppData 隔离 + FEA-07 后续 residual 收口）的 **scope review**；候选 `2C-RESIDUAL-1`（typed-stop 次序）可并行提名。
- 推荐 Agent / Reviewer：DSH 指派独立上下文 Owner；Reviewer 为非实现会话的独立子 agent 或 ZCode/Codex。
- 推荐原因与前置依赖：DAG/STATUS 已指名的下一候选；scope 未冻结前不得实施。依赖 `FEA-07`（done）与 `FEA-07-RESIDUAL-3`（done）。
- Recovery point：仓库 `G:\CODEX\New Manga`、`main`、固定 base `d91dbe444`；不创建 worktree（待 scope 冻结后由 DSH 决定）。
- 允许修改路径：待 scope review 冻结；预估 `apps/desktop-avalonia/tests/**` 与 `verification/FEA-07-RESIDUAL-4/**`。
- 禁止范围与新增授权条件：不得改契约字节；不得把 `NOT_RUN` 写 PASS；scope 未冻结不得实施。
- 交付物：scope review 报告 `doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`；冻结后建卡并实施。
- 验证命令、环境与完成 Gate：`check.ps1`（默认 + `-TaskPath`）、`verify_pins` 18/18、全量 pytest ≥3395/10、全量 .NET ≥1794/0/107、`generate_api_inventory.py --check`、scope ⊆ allowed_paths。
- 可直接转发给 Agent 的指令：见本 Handoff 末行。

> 可直接转发：`只读 scope review：对 FEA-07-RESIDUAL-4（headless 用例真实 AppData 隔离 + FEA-07 后续 residual）做独立 scope review，冻结 base=d91dbe444。输出 doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md，含 allowed_paths、AC、证据计划、风险与 verdict（READY-TO-FREEZE / NOT_RECOMMENDED）。不改任何生产源码/契约；门禁 check.ps1 + verify_pins 只读复核。`

## 风险与遗留

- **对账范围限于文档**：不推进 S5，不释放 FEA-13/14/15；FEA-02-BRIDGE 裁决为「不独立释放」，若后续发现退出协调缺口需另立卡。
- **未处理项**：`FEA-07-AC5-NATIVE-1`（用户需恢复 4K 分辨率）、`FEA-06-RESIDUAL-1`（残余承接关系未变）、`2C-RESIDUAL-1`/README 对账（候选未建卡）。
- **PLAN 预算**：6985/7000 bytes，接近上限；下次要加 DAG 行必须先腾空间。
- **append-only 解释**：GOV-11/D07 的 AC 勾选与标记为状态转换必要修正（原 AC 文本未改），测试表 `NOT_RUN` 历史记录原样保留并在 Closeout 说明。
- 用户动作：`FEA-07-AC5-NATIVE-1` 记录的系统显示设置未恢复（仅 1 屏 1920×1080），需用户恢复 4K 并核验。

## r2 返修记录（Review r1 = changes_requested，P0=0/P1=1/P2=4/P3=8）

| Finding | 处置 |
|---|---|
| REC-01（P1）AC7 要求 PLAN 载依据 | AC7 改为「PLAN 记结论，依据登记于本卡 §对账清单 #7」；PLAN 预算仅剩 4 B 无法再载依据 |
| REC-02（P2）ledger 分项数字 | 提交后重跑 `task_ledger.py --write` 并随 r2 提交 |
| REC-03（P2）AC3 子句假 | AC3 改为「测试表 `NOT_RUN` 原样保留（append-only，不据此判 PASS）」 |
| REC-04（P2）STATUS 的 L-1 冲突 | 改为「四表 DDL 已冻 = L-1 前置已满足（C-15 schema v7 + C-17 v1.1 schema v8；L-2…L-9 保留）」；AD-003/FEA-C11_IMPL_PREREQS 过期口径登记为卡 §残余 R-1/R-2（不在 allowed_paths） |
| REC-05（P2）BRIDGE 依据 | 改引 `FEA-07.md:298`（AC2 `ExitCoordinator`）与 `FEA-07-RESIDUAL-2.md:50`（AC-R4a-2）；结论改「不独立释放；退出协调由 FEA-07 已交付实现覆盖，残余风险另卡」 |
| REC-06（P3）D07 L-5 口径 | D07 Closeout 追加口径补充（D07 行 7 = 「部分」，由 L-5 认定） |
| REC-07（P3）Owner 署名 | PLAN「完成」行补回 `Owner c04b-impl` |
| REC-08（P3）GOV-11 AC3 主证据 | GOV-11 Closeout 追加证据更正（主证据 `FEA-02-CORE` `135479270`） |
| REC-09（P3）版本记法 | STATUS 改为「C-15 schema v7 + C-17 v1.1 schema v8」；PLAN:12 的 C-17 v1.0 登记为卡 §残余 R-3 |
| REC-10（P3）IMMERSIVE 限定 | 追加「仅指本卡 legacy 壳；v2 壳 2K 已由 `EV-V2F-05` 复验」 |
| REC-11（P3）PLAN 预算 | 登记为卡 §残余 R-4（6994/7000 B，63/64 行） |
| REC-12（P3）handoffs 不在 allowed_paths | allowed_paths 增 `doc/handoffs/FEA-DOC-RECONCILE-1-*.md` |
| REC-13（P3）gates.log 无 EXIT/shell 头 | 新增 `verification/FEA-DOC-RECONCILE-1/gates-2.log`（含 shell 头、逐命令 EXIT、预算实测）；gates.log 保留为 HISTORICAL |

r1 报告保留原字节（`doc/reviews/FEA-DOC-RECONCILE-1-r1.md`），随 head 变化降为历史；当前结论以 rev 后的 r2 报告为准。

## r3 返修记录（第二独立审查者 `FEA-DOC-RECONCILE-1-review.md`，P0=0/P1=2/P2=4/P3=3）

| Finding | 处置 |
|---|---|
| P1-01（P1）GOV-11/D07 翻 done 但 front matter 仍 `pending`/`null` | 两卡 `integration_commit`/`delivery_head` = `b6ada81e8`；`canonical_evidence_status`/`resource_closeout_status` = `complete`；Canonical Evidence 表填实（GOV-11：ADJ + C-01b/C-02/C-03/C-11 + FEA-02-CORE；D07：C-09 FROZEN + Gate 裁定）；GOV-11 `reviewer` 改为独立 Review 指针 |
| P1-02（P1）AC3 自设条件与事实相反 | 已在 r2 改为「测试表 `NOT_RUN` 原样保留（append-only，不据此判 PASS）」 |
| P2-01（P2）ledger 不可复现 | 已在 r2 提交后重跑，现 559 tracked / 0 untracked / 13 non-terminal tracked |
| P2-02（P2）四表名不可追溯 + AD-003 冲突 | 卡 §对账清单 #1 已列四表名（v7：`source_entries`/`page_bindings`；v8：`source_sync_plans`/`source_operations` + `source_binding_publications`/`source_revision_lineage`）；AD-003 过期口径登记为 §残余 R-1 |
| P2-03（P2）AC7 PLAN 载依据 | 已在 r2 改为「PLAN 记结论、依据在卡内」 |
| P2-04（P2）GOV-11 AC3 主证据 | 已在 r2 追加证据更正（`FEA-02-CORE` `135479270`） |
| P3-01/P3-02/P3-03 | 版本记法、D07 L-5 口径已在 r2 修；预算登记 §残余 R-4 |

当前门禁证据：`verification/FEA-DOC-RECONCILE-1/gates-3.log`（r2 的 `gates-2.log` 与 `gates.log` 转为 HISTORICAL）。

## r4 收口记录（2026-11-09）

- 复审结果：r2（head `b6ada81e8`）= **approved**（11 FIXED / 2 PARTIAL / 0 OPEN，PARTIAL 两项随后由 r3 修）；r3（head `c22aea60c`）= **approved**（22 FIXED / 0 OPEN；新增 P3×5 非阻断，已在本轮处置 reviewer 引用、AC8 证据入口、写域、交付指针时点；gates-3 的提交前标注如实保留）。
- 收口提交：`236d5a853`（AC1–AC9 MET、`status: done`、GOV-11/D07 交付指针、台账重生成）与 `e0dc4a74c`（对账卡门禁：evidence class、仓外产物 manifest 登记）。
- 最终门禁：`check.ps1` PASS（3 warnings）、`check.ps1 -TaskPath doc/tasks/FEA-DOC-RECONCILE-1.md` PASS、`verify_pins` 18/18 PASS；STATUS 2985 B/29 行、PLAN 6989 B/63 行（预算内，PLAN 余 11 B/1 行）。
- 交付边界：本轮全部改动限于 `doc/**` 与 `verification/**`；0 源码、0 契约字节、0 pin 重算、未 push。
- 下一接收者：先处理 PLAN 预算结构性风险（§残余 R-4），再对 `FEA-07-RESIDUAL-4` 做 scope review。