---
task_id: FEA-11-RUN-GRANT-1
author: run-grant-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2067789ea
delivery_head: a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853
status: in_review
supersedes_handoff: doc/handoffs/FEA-11-RUN-GRANT-1-3ffabeb81.md（r1 返修交付；§2 门禁数字已被本文件取代）
---

# Handoff — FEA-11-RUN-GRANT-1（Review r2 findings 返修；Run-scoped source-read 授权）

- Task：`doc/tasks/FEA-11-RUN-GRANT-1.md`（Owner=`run-grant-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=2067789ea`；r1 reviewed_head `7ff49f1cc`；r2 reviewed_head `3ffabeb81`；本次返修自 `b8a4b2092`（r2 报告入库）之后
- 交付实现 commit：`9e1861ee0`（folder kind 检测 + AcceptRun 接线 seam）、`a11ded0d3`（判别性测试；**`delivery_head`**）；证据/卡/本 Handoff 为同批文档提交
- 环境：Windows 11 10.0.26300 / PowerShell 7 / CPython 3.14.6 / .NET（net9.0）；无新依赖、无 schema/migration/契约/wire 改动
- 依据：r2 `doc/reviews/FEA-11-RUN-GRANT-1-r2.md`（changes_requested P0=0/P1=0/P2=2/P3=2）+ 卡「Review r1 处置」+ 本次卡「Review r2 处置记录」

## 1. 返修结果（R2-01…R2-04）

| Finding | 状态 | 处置摘要 |
|---|---|---|
| **R2-01（P2）** L-G12 folder 边界不实 | **FIXED** | `RunSourceRange.KindOfSource`：枚举声明 `SourceKind` 优先 → `Directory.Exists` → folder → 最后按扩展名（旧实现把目录当 `image`，`FileStream` 打开目录失败 → 整源跳过）。新增**真实目录源 IPC 证据**：真实 Core 上 folder grant mint 成功 → Core `AuthorizeSourceReadForRun` 绑定成员 entry（`bound_pages=1`）→ `resolve_page_resource` 成功；新增 kind 判别单测。L-G12/Handoff/EV 边界修正为「**image 单 entry 源 + folder 源（逐成员 entry 匹配）+ zip/cbz/pdf 归档首成员（ordinal=0）**」。 |
| **R2-02（P2）** 能力缺失测试不判别 | **FIXED** | 用例改为 known 源非空 + entries 非空 + 计数 authorize（经 `AuthorizeSliceAsync`），probe=false 断言 0 次 mint；另加 dispatcher 级「能力缺失仍到达 dispatch」断言；**删除能力门 → 用例变红（判别点 B7）**。 |
| **R2-03（P3）** AcceptRun 生产接线未测 | **FIXED** | 生产 `AcceptRunAsync` 委托到新的可测 seam `HostRuntime.AuthorizePreparedRunForAcceptAsync`（取 `PreparedRunSlices` 的冻结 `{command, scope}` → best-effort authorizer）；新增接线用例（正常路径调用授权；缺失/过期 slice → `RUN_STALE_PREVIEW`；无 authorizer 仍先取 slice）；**删除接线调用 → 用例变红（判别点 B8）**。 |
| **R2-04（P3）** 卡 I-2 / Manifest 旧口径 | **FIXED** | 卡 I-2「铸造」「源范围」改为 best-effort 权威口径（跳过并继续 dispatch；unresolved 跳过，由 Core 对目标页 fail-closed）；`RESOURCE-MANIFEST.json` 新增动态 `delivery_head` 字段，worktree `source_path` 指向新 delivery head。 |

## 2. 验证证据（返修后实跑；clean tree）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed** | `logs/feature.log` |
| Host 单测（AC-R4/R5/R1-01/R1-02/R1-04/R2-02/R2-03） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 21 passed**（r1 17 + 4） | `logs/host-unit.log` |
| 真实 IPC（AC-R4/R1-01/R1-03/R2-01） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 3 passed**（首成员/多成员 fail-closed/mint 部分失败/**真实 folder 源 mint→绑定→resolve**；wire 无路径） | `logs/host-ipc.log` |
| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped** | `logs/full-pytest.log` |
| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1551 / 0 / 89**（r2 基线 1547/0/88，+4 单测；3 个 IPC opt-in 未设 env 时 skipped） | `logs/full-dotnet.log` |
| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS（changed=31 全 ALLOWED；禁止面全空；minor=3）** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **PASS 9/9 破坏点 RED_AS_EXPECTED + 9/9 字节级 RESTORED + rebuild OK**（新增 B7 能力门 / B8 AcceptRun 接线 / B9 folder 检测） | `logs/discrimination.log` |

- 未运行项：无（上述门禁全部实跑）。已知 flaky/环境交互：全量 .NET 若在 `verification/` 正在写入时运行，`FluentResidual2VisualEvidenceTests` 会因 `git status --porcelain -- verification` 快照变化失败；clean tree 隔离复跑全绿 1551/0/89。全量 pytest/.NET 后均 `git checkout -- verification/FEA-09`。

## 3. 已知 limitation（closeout 必须保留）

- **L-G1**：单 grant ≤300s；窗口后提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑 follow-up。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希），大库未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail）。
- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up。
- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G12（Review r1 扩写 / r2 修正）Host→Core 源身份通道缺失**：①**version 通道**（枚举 DTO 无 version、寒启动 version 固定 `"1"`）→ 生产 Host 容器 grant 的 `scope.version` 通常与 `binding.accepted_source_version` 不匹配 → typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）；②**容器成员 entry 身份通道**（Host 单容器 entry、locator=容器名/ordinal=0 vs Core 成员 `source_entries` 匹配）→ 多成员归档只有首成员可被授权，其余 fail-closed 拒绝。**当前可用边界 = image 单 entry 源 + folder 源（逐成员 entry 匹配，r2 已用真实目录源 IPC 证明）+ zip/cbz/pdf 归档首成员**；多成员容器其余页与 version 通道缺口仍不可用。follow-up 候选 `FEA-11-RUN-GRANT-2`（proposed，不释放）。
- **L-G13**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑。
- **L-G14（R1-11 行为变化）**：`HostRuntime.AcceptRunAsync` 需同进程先 `PrepareRunAsync`（冻结 slice），缺失/过期 → `RUN_STALE_PREVIEW`；仓内 App 无 Prepare/Accept 调用点。
- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；只交付「窗口内可用 + image 单 entry 源 + folder 源 + 归档首成员（L-G12 边界）」；FEA-11 AC11-5/AC11-9 未回填；独立 r3 窄面复审由 Lead 指派（本 Handoff 不自审）。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `a94052ba7`；r1 head `7ff49f1cc`；r2 head `3ffabeb81`；**本次 delivery_head=`a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`**（未 push、未建 worktree）。
- 复现：
  1. `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **50 passed**
  2. `C:/Python314/python.exe -m pytest tests -q` → **3281 passed / 10 skipped**（跑后 `git checkout -- verification/FEA-09`）
  3. `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` → **21 passed**；`$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` → **3 passed**
  4. `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` → **1551 / 0 / 89**（跑后 `git checkout -- verification/FEA-09`）
  5. pins/check/API inventory/scope/discrimination 同 EV §2。
- 接收者下一步：①独立 r3 窄面复审（R2-01 folder 证据、R2-02 判别性、R2-03 接线 seam、R2-04 文档）；②核对 EV 每文件 sha256；③Lead closeout（本卡 `status` 未改）。

## 5. 下一任务建议

- **无释放**（本卡 r3 复审/集成前不释放后续实现卡）；候选 follow-up `FEA-11-RUN-GRANT-2`（Host→Core source identity 通道：version + 归档成员 locator/ordinal；或 L-G1 定期重铸）由 Lead 决定。
- Reviewer：由 DSH 指派**独立上下文**（非本实现会话；fresh subagent 或未参与实现的 ZCode/Codex）。
