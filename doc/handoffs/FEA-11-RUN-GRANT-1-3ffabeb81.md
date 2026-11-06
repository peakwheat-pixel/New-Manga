---
task_id: FEA-11-RUN-GRANT-1
author: run-grant-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2067789ea
delivery_head: 3ffabeb8134b355076a9e964305de895e7c5b9d1
status: in_review
supersedes_handoff: doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md（r1 交付；§2 门禁数字已被本文件取代）
---

# Handoff — FEA-11-RUN-GRANT-1（Review r1 findings 返修；Run-scoped source-read 授权）

- Task：`doc/tasks/FEA-11-RUN-GRANT-1.md`（Owner=`run-grant-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=2067789ea`；r1 交付 head `7ff49f1cc`（reviewed_head）；本次返修自 `cddfc8fad`/`15ecafca3`（Lead 处置提交）之后
- 交付实现 commit：`04317256c`（Host best-effort 编排/错误面）、`3ffabeb81`（判别性测试；**`delivery_head`**）；证据/卡/本 Handoff 为同批文档提交
- 环境：Windows 11 10.0.26300 / PowerShell 7 / CPython 3.14.6 / .NET（net9.0）；无新依赖、无 schema/migration/契约/wire 改动
- 依据：Review r1 `doc/reviews/FEA-11-RUN-GRANT-1-r1.md`（changes_requested P0=0/P1=1/P2=3/P3=7）+ 卡「Review r1 处置（DSH，2026-11-07）」+ DSH R-12 扩域批准

## 1. 返修结果（R1-01…R1-11 映射）

| Finding | 状态 | 处置摘要 |
|---|---|---|
| **R1-01（P1）** Host best-effort | **FIXED** | 抽出 `RunSourceAuthorizer`（生产同一编排、可单测）：能力缺失/探测失败/无相关源/registry 不可读/mint I/O 失败（含部分源）→ **跳过并继续 dispatch**；只有 Core 对目标页 typed 拒绝 → 阻断（R-5 不变）。`AuthorizeRunAsync` 逐源 best-effort，全源失败不发命令；IPC 与单测双证据。 |
| **R1-02（P2）** AC-R4 证据 | **FIXED（4/4）** | ①pause/stop/abandon 不触发（`RunCommandPolicy`）；②能力缺失→不 mint 且不抛；③`AcceptRun` 经 `PreparedRunSlices` 取冻结 slice 后调用授权，缺失/过期→`RUN_STALE_PREVIEW`；④`RunSourceRange` book 过滤/known=0/filtered=0/unresolved 全测。 |
| **R1-03（P2）** L-G12/口径 | **FIXED** | L-G12 扩写为「version 通道 + 容器成员 entry 身份通道」；可用边界收窄为 image/folder 单 entry 源 + 归档首成员；IPC 注释/断言语义修正；follow-up 候选 `FEA-11-RUN-GRANT-2`（proposed，不释放）。 |
| **R1-04（P2）** 错误面 | **FIXED** | `MapMintFailure`：file/access→`SOURCE_ENTRY_MISSING`、读写中 IO→`FILE_IDENTITY_CHANGED`、参数/路径→`SOURCE_ACCESS_DENIED`；partial unresolved = 跳过该源，由 Core 对目标页 fail-closed。 |
| **R1-05/R1-06（P3）** | **FIXED** | 卡 I-1 响应形态已按契约；新增 I-1 `grant_ids` 封闭形状行（1..64 唯一；重复→`INVALID_REQUEST`）+ 测试注释。 |
| **R1-07（P3）** | **FIXED** | `read_entry_bytes` + `source_lease` 双 spy 零断言；per-page `gate != open` 用 mixed binding 用例覆盖。 |
| **R1-08（P3）** | **FIXED** | host-only/session 零写证据 = `total_changes` + 业务表逐表快照。 |
| **R1-09（P3）** | **FIXED** | EV 明确 commit 行数用例为 RENDITION-1 同构 harness（非 `assemble_core_services`）。 |
| **R1-10（P3）** | **FIXED** | 能力缺失跳过有单测；Handoff 表述以实测为准。 |
| **R1-11（P3）** | **FIXED（登记）** | `AcceptRunAsync` 需同进程先 `PrepareRunAsync`，否则 `RUN_STALE_PREVIEW`（仓内 App 无调用点）——见 §3。 |

## 2. 验证证据（返修后实跑；clean tree）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed**（36 + 14） | `logs/feature.log` |
| Host 单测（AC-R4/R5/R1-01/R1-02/R1-04） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 17 passed**（原 5 + 12） | `logs/host-unit.log` |
| 真实 IPC（AC-R4/R1-01/R1-03） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 2 passed**（p1 首成员成功；p2 多成员 fail-closed；mint 失败 best-effort；partial minted=1/bound=1/skipped=1；wire 无路径） | `logs/host-ipc.log` |
| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped**（r1 基线 3280/10，+1） | `logs/full-pytest.log` |
| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1547 / 0 / 88**（r1 基线 1535/0/88，+12 单测；2 个 IPC opt-in 未设 env 时 skipped） | `logs/full-dotnet.log` |
| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS**（changed 文件全 ALLOWED；禁止面全空；minor=3） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **6/6 破坏点 RED_AS_EXPECTED + 6/6 字节级 RESTORED + rebuild OK**（B1 写绑定/B2 facts/B3 原子性/B4 command 域/B5 dispatcher 钩子/**B6 best-effort 跳过**） | `logs/discrimination.log` |

- 未运行项：无（上述门禁全部实跑）。已知 flaky/环境交互：全量 .NET 首跑 `FluentResidual2VisualEvidenceTests` 会因运行中新建 `verification/` 目录或 FEA-09 tracked 字节未恢复而失败（该用例比较 `git status --porcelain -- verification` 前后快照）；clean tree 隔离复跑全绿，非产品缺陷。全量 pytest/.NET 后均 `git checkout -- verification/FEA-09`。

## 3. 已知 limitation（closeout 必须保留）

- **L-G1**：单 grant ≤300s；窗口后提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑未实现（follow-up）。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希），大库未标定；best-effort 逐源跳过不改变成本上界。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail）。
- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up。
- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G12（扩写，按 Review r1 R1-03）Host→Core 源身份通道缺失**：①**version 通道**：枚举 DTO 无 `version_id`、寒启动 `SourceScanTarget.Version` 固定 `"1"`，生产 Host 铸出的容器 grant 通常与 `binding.accepted_source_version` 不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）；②**容器成员 entry 身份通道**：Host 对 zip/cbz/pdf 只铸容器单 entry（locator=容器名、ordinal=0），Core 按成员 `source_entries` 匹配 → 多成员归档只有 `ordinal=0` 首成员可被授权，其余 fail-closed 拒绝（.NET IPC p1/p2 实证）。因此可用边界 = **image/folder 单 entry 源 + 归档首成员**；「version 已知时可用」对多成员容器不成立。缓解候选（另卡 `FEA-11-RUN-GRANT-2`，proposed）：①App/枚举传 Core version；②Host 缓存 `ScanSourceSync` 的 `source.version_id`；③容器成员 locator/ordinal 通道；④契约层 facts-only 匹配（需 UNFREEZE）。
- **L-G13**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑。
- **L-G14（R1-11 行为变化）**：`HostRuntime.AcceptRunAsync` 现在要求**同一 Host 进程内**先 `PrepareRunAsync`（Host 用冻结的 `{command, scope}` 做 Run 前置授权）；缺失/过期 prepared slice → typed `RUN_STALE_PREVIEW`。仓内 `NewManga.App` 无 `PrepareRun/AcceptRun` 调用点（scope review §3.3），故不构成生产 UI 回归；若未来接线需在同一 Host 进程内 Prepare→Accept。
- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；只交付「窗口内可用 + image/folder 单 entry 源与归档首成员（L-G12 边界）」；FEA-11 AC11-5/AC11-9 未回填；独立 r2 窄面复审由 Lead 指派（本 Handoff 不自审）。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；基准 `a94052ba7`；r1 delivery head `7ff49f1cc`；**本次 delivery_head=`3ffabeb8134b355076a9e964305de895e7c5b9d1`**（未 push、未建 worktree）。
- 复现：
  1. `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **50 passed**
  2. `C:/Python314/python.exe -m pytest tests -q` → **3281 passed / 10 skipped**（跑后 `git checkout -- verification/FEA-09`）
  3. `$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"` → **2 passed**
  4. `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` → **1547 / 0 / 88**（跑后 `git checkout -- verification/FEA-09`）
  5. pins/check/API inventory/scope/discrimination 同 EV §2。
- 接收者下一步：①独立 r2 窄面复审（R1-01/R1-02/R1-04 的 fixed 判定 + 新测试判别性）；②核对 EV 每文件 sha256；③确认 L-G12 边界与 R1-11 登记；④Lead closeout（本卡 `status` 未改）。

## 5. 下一任务建议

- **无释放**（本卡未 r2 复审/集成前不释放后续实现卡）；候选 follow-up `FEA-11-RUN-GRANT-2`（Host→Core source identity 通道：version + 归档成员 locator/ordinal；或 L-G1 定期重铸）由 Lead 决定。
- Reviewer：由 DSH 指派**独立上下文**（非本实现会话；fresh subagent 或未参与实现的 ZCode/Codex）。
