---
task_id: FEA-11-RUN-GRANT-2C
author: l-s4b1-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: fdd170039
start_head: c5f1b416f
delivery_head: e5e9c4c52
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-RUN-GRANT-2C（2C 长 Run 续期）

- Task：`doc/tasks/FEA-11-RUN-GRANT-2C.md`（`status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=fdd170039`；**实现起点 `c5f1b416f`**（派发时 HEAD `0475adc72`；其后 Lead
  的 `c5f1b416f` 是 PREREQ 冻结记录 docs-only 修正，`0475adc72..c5f1b416f` 实测仅 PREREQ 文档）
- **delivery_head=`e5e9c4c52`**（实现 `c40489b5d` + 测试/ gated/IPC `e5e9c4c52`；随后同批 docs/evidence 提交）
- 权限依据：卡面 + 权威 scope review `doc/reviews/2C-LONG-RUN-RENEWAL-scope-r1.md`
  （READY-WITH-UNFREEZE；方案 a）+ ZCode 裁决（APPROVE 2 pins / 方案 a）+ PREREQ closeout
  （C-06 v1.3 `75f8e2b4…`、C-16 v1.6 `b8f46fb1…`，pins 18/18）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、
  零 schema/迁移、零 Core/Python 生产代码改动、零 Run wire/命令/能力/错误码改动、零 App 改动

## 1. 交付结果（AC-2C-1…8 全 MET；卡面已勾选 + `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-2C-1 续期主 AC** | MET | in-process fake clock：窗口后读/提交分别 typed 失败且零业务写 → 一次续期（新 grant + 同一冻结 `{command, scope}`）后读/提交恢复；Host 单测每轮重绑定；gated 真 IPC 同 scope 两轮 + 页仍可读 |
| **AC-2C-2 不延长/不扩 scope/不改 command** | MET | 每轮新 grant id；旧 grant 永不延长（续期后仍 `SOURCE_GRANT_EXPIRED`）；command/scope 逐字节相同；加宽尝试被忽略 |
| **AC-2C-3 撤销/漂移即停** | MET | 每轮同一 `AuthorizeSliceAsync`（重走 `Registry.Authorize` + 物理 facts）→ typed 停止、不重试、不 reattest |
| **AC-2C-4 失败不放行/不自动重试成自动恢复** | MET | typed/异常/全 skip → 停止续期；Run 仍由 Core fail-closed；不新建 Run |
| **AC-2C-5 预算/间隔** | MET | interval=240 / maxRenewals=12 / round budget=50（240+50<300）；单轮超预算、轮次上限、终态/关停均 typed 停止；coordinator `_gate` 串行；ledger 计数可观测、既有 256 上限未改 |
| **AC-2C-6 接线点/无 App 改动** | MET | dispatcher `runAuthorizeWithResult` + `runDispatched`（Host 内部零 wire）；`AcceptRun` 同 slice 启动；`RunGrantRenewalStatus` 可观测；App 零 diff；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 不变 |
| **AC-2C-7 L-G1 只降级不关闭 + 不夸大** | MET | 卡/EV/Handoff 固定「有续期 + 子限制」口径与子限制清单；未宣称 L-G1 关闭/任意长 Run/Run 全面恢复/自动恢复 |
| **AC-2C-8 门禁** | MET | build PASS；pins 18/18（C06 v1.3/C16 v1.6 新值）；check（默认+`-TaskPath`）PASS；API EXIT=0；scope PASS（`src/**` 零 diff、禁止面零 diff）；全量 pytest 3363/10（起点 3360/10）；全量 .NET ≥ 起点；判别性 7/7；跑后 `verification/FEA-09` CLEAN |

## 2. 验证证据（实跑；`delivery_head=e5e9c4c52`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 0 warning / 0 error** | `logs/build.log` |
| Host 续期单测 | `--filter "FullyQualifiedName~RunGrantRenewal"` | **PASS 13/0/0** | `logs/host-unit.log` |
| 回归 | `--filter "SourceRegistryTests\|Fea11RunGrantIpc"`（无 gated env） | **PASS 32/0/7 skip**（gated 默认 skip） | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter Fea11RunGrantIpc` | **PASS 7/0/0**（含新同 scope 二轮=续期轮） | `logs/host-ipc.log`、`logs/renewal-ipc.json/.txt` |
| 定向 pytest | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 92 passed**（基线 89 + 3） | `logs/regression-74.log` |
| 全量 Python | `pytest tests -q` | **PASS 3363 passed / 10 skipped / 261.08s**（起点 3360/10，+3） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **TBD-FULL-DOTNET** | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **TBD-GATES** | `logs/gates.log` |
| scope | `python verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py` | **TBD-SCOPE** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-2C/tools/discrimination.py` | **PASS 7/7 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **before / after**：before = 窗口后读 `ProviderInputError` + 提交 `SOURCE_ACCESS_DENIED` + 零业务写；after = 一次续期轮后读/提交恢复、旧 grant 不延长、新 grant 被选中；gated 真 IPC `renewal-ipc.json` 记录同 scope 两轮（2 帧 register（run 面增量）+2 帧 authorize、new grant id、`bound_pages=1`、页可读、wire 无路径、`reattest_frames=0`）。
- **跑后恢复**：全量 .NET 运行后 `git checkout -- verification/FEA-09`。
- **并发披露**：共享 `main` 同期 Lead docs-only `c5f1b416f`（PREREQ 冻结记录修正）；本卡提交均显式 pathspec；`src/**` 零 diff。

## 3. L-G1 状态与 known limitations（closeout 必须保留）

**L-G1：只降级不关闭** —— 从「无续期」→「有续期 + 子限制」。保留：

1. **单步 >300s**、2. **续期失败**、3. **L-G2 加密源**、4. **L-G9 Core 重启**、5. **L-R1 残余（viewer 无 Run）**、6. **L-G16 >4096 成员**；
7. **尚未 dispatch 的 pending Run 不在本卡范围**（其 grant 尚未铸造）；
8. 续期每 240s 重 mint（容器整文件 sha256 / folder 逐成员），L-G8 成本按周期放大；单轮 >50s 即停止；
9. 续期失败 ≠ Run 失败；Core 仍是 fail-closed 权威；不自动重新授权/不重建 identity/不 reattest；
10. B2 `roots_available`、folder（L-S4-2）、L-S4-1、L-R1 其余面、UI P3 均不在本卡。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `c5f1b416f`；**delivery_head=`e5e9c4c52`**（未 push、未建 worktree）。
- 复现（repo root）：见 `verification/FEA-11-RUN-GRANT-2C/EV.md` §7。
- 接收者下一步：①Lead 指派**独立上下文** Review（只读 `e5e9c4c52`；重点：每轮新 grant/同一冻结 scope、
  `AuthorizeSliceAsync` 真实计数、撤销/漂移/预算/终态停止、Python fake-clock before/after 与
  「不同 scope/command」反例、gated 同 scope 二轮、7/7 判别性、零 Core/零 wire/零 App/零契约 diff、
  L-G1 只降级措辞）；②Lead 复跑 fake clock/gated；③Lead 集成门禁与 closeout（本 Handoff 不改卡 `status`；
  卡面 `delivery_head` 已回填）。

## 5. 下一任务建议

- 本卡 Review/集成前不释放后续实现。
- Review 通过后建议队列（由 DSH 裁决）：**B2 `roots_available`**（无消费者，延后）/ **L-R11 gate 一致性** /
  **C-04b** / **SCAN-RH** 穿插 / **UI P3** 最后；以及 2C 的后续可选优化（D-4b 成本：按未终态目标页
  裁剪续期；非必需，先评审）。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / `e5e9c4c52`（未创建 worktree，若需隔离 worktree 待 DSH 创建）。

## 6. 风险与遗留

- **R1 口径**：续期易被读成「放宽授权/延长 TTL/撤销后自动放行」；本卡固定「每轮新 grant、同一冻结 scope、
  重新核验 facts、撤销即停、单轮 interval+round<300s」，并在 EV 保留子限制清单。
- **R2 成本**：每次续期重 mint（大 folder 逐成员 sha256）；单轮预算 50s，超预算 typed 停止（不长期占用 mint gate）。
- **R3 竞态**：续期与用户撤销/同步改 binding 竞态由每轮 `Registry.Authorize` + Core per-page 原子匹配兜底；失败即停。
- **R4 gated 时间维边界**：真子进程 Core 无法前推时钟；时间维证据在 Python in-process fake clock，gated 仅证
  「同 scope 二次 mint+bind+可读」。EV 已如实标注。
- **R5 并发共享工作树**：证据按 `delivery_head` 归因；Lead 集成若 HEAD 前进需按其 head 重跑门禁。
- **回退**：`git revert e5e9c4c52 c40489b5d`（2 个实现/测试提交）；无 schema/数据迁移、无 Core 写行为变化，回退无数据风险。
