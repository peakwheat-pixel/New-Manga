---
task: FEA-11-RUN-GRANT-1
title: FEA-11-RUN-GRANT-1 独立实现 Review r1（Run-scoped source-read 授权：Core 命令 + Host 铸造/绑定/接线）
reviewer: fresh subagent（独立上下文；未参与实现/返修；只读）
session: 62c6bf16-7f51-4d3b-92b7-774173cc3ff6
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
worktree: clean（本报告写入前；写入后仅本报告为 untracked）
reviewed_head: 7ff49f1cc21346be0b4867304499ee17f7ffb84e
verdict: changes_requested
---

# FEA-11-RUN-GRANT-1 独立实现 Review r1

> **结论先行：`changes_requested`。P0=0 / P1=1 / P2=3 / P3=7。**
>
> - **Core 机制实现质量高**：C-16 v1.3 §2.4 的 closed shape、校验顺序、同 Run scope 展开器、per-page 同一 gate、
>   per-page facts/entry 匹配、整体 typed 失败零映射、零 DB 写、幂等、能力公告、错误闭集全部逐项落地；
>   我独立实跑定向 `36 passed + 13 passed`，并独立复现 2 个破坏点（映射写入删除、容器 facts 核验删除）均变红、字节恢复 sha 复核一致。
> - **门禁数字全部为真**：我独立跑全量 `pytest tests` = **3280 passed / 10 skipped**、全量 `dotnet test NewManga.sln -c Release`
>   = **1535 passed / 0 failed / 88 skipped（exit 0）**、pins **18/18**、check **PASS(3 warnings)**、API inventory **EXIT=0**；
>   EV.md **27/27 sha256 全匹配**，changed-files / scope-validation / discrimination 与实测一致。
> - **不能 approve 的原因**：frozen AC 有两项只到 PARTIAL，且 L-G12 的登记不完整。
>   ① **AC-R5（managed 零回归）** 的「managed-only Run **不调用新命令**」在 Host 层不成立：只要 Host 有任一已知源，
>   `library_*` Run 命令在 dispatch 前总会 mint + 调 `AuthorizeSourceReadForRun`（managed 页在 Core 侧 `bound_pages=0`
>   只是 Core 层语义），并可能因无关源的铸造失败而**阻断一个 managed-only Run**——这与卡 I-2「不得改变既有非
>   referenced Run 行为」相抵触（**P1**）。
> ② **AC-R4** 的 AcceptRun 前置授权、能力缺失跳过、真实 `HostRuntime` 钩子（含 pause/stop 不触发）**没有判别性测试**；
>   .NET IPC 直接调用 `SourceReadCoordinator`，绕过了生产 Host 编排（**P2**）。
> ③ **L-G12 只登记了 version 通道**；但 Host 为 zip/cbz/pdf 铸造的是「容器单 entry」grant（locator=容器名、ordinal=0），
>   Core 对成员页按 `source_entries` 匹配——**多成员归档只有 ordinal=0 的那一页**能被授权（.NET IPC 的 p1 成功 / p2
>   typed 拒绝正是这个事实）。因此「Host 已知源携带正确 version 时可用」对多成员容器不成立；该 production limitation
>   未登记（**P2**，L-G12 需扩写或另立 follow-up）。
>
> **这不是对实现者能力的否定**：Core 命令、真实装配测试、判别性、证据链都扎实；需要处置的是 frozen AC 的口径/证据覆盖、
> Host managed 路径的行为耦合、以及 L-G12 的完整性与 follow-up 边界。

---

## 0. 复核对象、方法与边界

- 仓库 `G:\CODEX\New Manga`，`main`；复核开始时 `HEAD=b28133392df0d9c0d5a7605278205fc47766ea8b`（docs/evidence），
  实现+测试 delivery head = `7ff49f1cc21346be0b4867304499ee17f7ffb84e`（`git rev-parse` 实测），工作树 clean。
- 只读事实以 `7ff49f1cc` 的实现/测试字节与当前工作树为准；卡面 / Handoff / EV / scope review 的叙述只作索引，不替代字节。
- 本复核**未参与**该卡的实现、返修或证据生成；未 `git add`/`commit`/`push`；未删除/移动任何文件；唯一写入为本报告。
- 破坏性复跑（2 个自选破坏点）均先备份字节、跑目标用例、再按原字节恢复并 sha256 复核（见 §4）。
- 全量 .NET 运行重写了 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；已 `git checkout --` 恢复并 sha 复核
  （side-effect `5E50A98E…` → `548DE629D163D80B9CD8D1E62251DE2016782E46A0C48A48575749D2A059D593`，5004 bytes，与运行前一致）。
- 全量 pytest / 定向测试 / .NET IPC 在仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/fixtures/` 下新增了测试夹具目录；
  这是测试运行的预期副作用，仓内 tracked 字节零变化。

### 0.1 本 Review 实跑命令与结果（全部实测）

| # | 命令 | 实测结果 |
|---|---|---|
| 1 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py -q` | **36 passed** in 5.87s |
| 2 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_run_grant.py -q` | **13 passed** in 1.62s |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"` | **5 passed / 0 failed / 0 skipped** |
| 4 | `$env:NEWMANGA_FEA11_IPC=1; dotnet test … --no-build --filter "FullyQualifiedName~Fea11RunGrant"` | **2 passed / 0 failed / 0 skipped** |
| 5 | `C:/Python314/python.exe -m pytest tests -q` | **3280 passed / 10 skipped / 10 warnings** in 247.33s（与 `logs/full-pytest.log` 相同） |
| 6 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1535 passed / 0 failed / 88 skipped**（8 assemblies，exit 0；与 `logs/full-dotnet.log` 聚合一致） |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`（C16 `7c355ccb8f82`） |
| 8 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` |
| 9 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`，EXIT=0 |
| 10 | `git diff --name-status 218775bca..7ff49f1cc` | 11 文件，全部 ⊆ 卡 `allowed_paths`（含 R-12 两文件）；禁止面零 diff |
| 11 | EV.md 27 个 sha256 逐文件复算 | **OK=27 / MISMATCH=0 / MISSING=0** |
| 12 | `git diff --name-status a94052ba7..7ff49f1cc` vs `changed-files.txt` | 12 行逐行一致（含卡面） |
| 13 | 破坏性复跑 2 点 | **2/2 变红 + 2/2 字节级 RESTORED + sha 一致**（§4） |

> 未独立重跑 `verification/FEA-11-RUN-GRANT-1/tools/discrimination.py`：该脚本会重写仓库内
> `logs/discrimination.log`（属被审证据字节，本 Review 不得改写）。我改为独立复现 B1/B2 两个破坏点，
> 并对 B3–B5 的破坏定义与目标用例做逐行核对（脚本 `tools/discrimination.py:29-89`）。

---

## 1. 结论与判定摘要

| 项 | 判定 |
|---|---|
| P0 | **0** |
| P1 | **1**（AC-R5 Host 层 managed 零回归字面未满足 / 行为耦合） |
| P2 | **3**（AC-R4 证据覆盖、L-G12 完整性、Host 预授权 typed 错误面） |
| P3 | **7**（卡/EV/Handoff 精度、grant_ids 去重解释、spy/快照范围、prepared slice 行为等） |
| AC-R1 | **MET** |
| AC-R2 | **MET（有保留）**：Core 真实装配端到端成立；提交行数由 RENDITION-1 同构 harness 断言，且 grant 形状非生产 Host-mintable |
| AC-R3 | **MET（有保留）**：6 类 typed + 零业务写成立；⑥ 为 provider/guard 面而非真在跑 Run，`read_entry_bytes` spy 缺失 |
| AC-R4 | **PARTIAL**：dispatcher 钩子/剪枝/IPC 成立；AcceptRun、能力缺失跳过、真实 `HostRuntime` 钩子无判别性测试 |
| AC-R5 | **PARTIAL**：Core 授权面对 managed 页跳过成立；Host 层「不调用新命令 / 零回归」不成立（见 R1-01） |
| AC-R6 | **MET** |
| AC-R7 | **PARTIAL**：门禁数字全真、27/27 sha 全真；但 L-G12 不完整、Handoff 有「单测」表述不实 |

---

## 2. A–H 逐项核验

### A. AC-R1 协议面 —— **PASS**

- 独立实跑 `tests/core/test_host_control.py` → **36 passed**；新增用例覆盖：
  - 普通 application 面 → `HOST_ONLY_REQUIRED`（`tests/core/test_host_control.py:640-691` 的 5 例 host-only/session 参数化，
    以及既有 host-only 参数化集合加入 `AuthorizeSourceReadForRun`）；错误 JSON 无 fixture 路径/credential
    （`test_host_control.py:768-782`）。
  - closed shape：缺键/未知键/空/65 项/重复/非字符串 id/非字符串 command/非对象 scope → `INVALID_REQUEST`
    （`test_host_control.py:693-730`）。
  - 缺失/过期/撤销 → `SOURCE_ACCESS_DENIED` / `SOURCE_GRANT_EXPIRED` / `SOURCE_GRANT_REVOKED`，且 category=authorization
    （`test_host_control.py:732-787`）；过期用注入 clock（`:755-760`）。
  - 能力公告：`core.ping` 含 `source.read.run/1` 且既有能力/minor=3 保持（`test_host_control.py:614-638`）。
- 代码面复核：`_HOST_CONTROL_COMMANDS` 注册 + 分发分支
  （`src/bootstrap/core_service.py:356-364`、`:1498-1513`）；普通面 host-only 拒绝在 `core_service.py:6253-6262`；
  `_source_import_error_envelope` 只输出固定 message + 计数（`core_service.py:4871-4881`、`:1060-1070`）。
- **保留（P3，R1-08）**：host-only/session 用例用 `core.conn.total_changes` 而非 AC-R1 所写的「业务表逐表快照相等」；
  shape/grant 用例确实用了逐表快照（`test_host_control.py:592-611`）。

### B. AC-R2/R3/R5 真实装配 —— **PASS（测试真实性成立）**

- 独立实跑 `tests/fea11/test_source_run_grant.py` → **13 passed**。
- 真实装配证据：
  - `real_core` fixture 走 `assemble_core_services`（真实 v8 migrations、真实 `SourceSyncStore`、真实 zip/PNG；
    `tests/fea11/test_source_run_grant.py:113-205,429-445`）。
  - 绑定后 `create_run(page-scope)` target 展开、`source_commit_guard` 打开、provider `page_frame` 尺寸 = 当前 binding
    的 B 图（12×7，而不是 managed 旧图 30×20），managed 页仍读 Managed Copy
    （`test_source_run_grant.py:452-511`）；未用 `_StubImages`（复用 `_ManagedPageImageSource`，
    `tests/fea11/test_source_rendition_source.py:144-151`）。
  - commit 行数用例使用真实 handler 授权 + 真实 store + RENDITION-1 同构 production pipeline
    （`test_source_run_grant.py:539-605`）；`test_real_run_without_authorization_writes_nothing` 证明无授权时 typed 失败、
    region/revision/lineage 0、detector 0（`:608-661`）。
  - fail-closed 6 类：无 grant/过期/撤销/scope+facts 不符/pending gate/中途 binding 切换，全部 typed、零业务写
    （`test_source_run_grant.py:675-826`）；授权面 `source_lease` spy 0（`:828-846`）。
  - managed：Core 授权面对 managed 页 `bound_pages=0`、零映射、零 DB 写（`:854-883`）。
- 判别性：我独立复现 B1/B2 破坏点，目标用例变红（§4），与 `logs/discrimination.log` 的 B1/B2 完全对应。
- **保留**：AC-R2 使用的「真实 grant」是测试侧按 Core 成员 entry 形状签名的 grant（`test_source_run_grant.py:269-322`；
  `build_rendition_site` 用 `entries=[(archive_path, "002-current.png", 1)]`），不是生产 Host `IssueAsync` 的容器 grant 形状；
  提交行数用例不是 `assemble_core_services`，而是 harness（见 R1-03/R1-09）。这影响「生产可用」口径，不影响 Core 机制证明。

### C. AC-R4 Host 接线 —— **PASS（功能），P2 覆盖缺口**

- 独立实跑 `SourceRegistry` 过滤 → **5 passed**；`NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` → **2 passed**（真实 Python Core）。
- 代码事实：
  - dispatcher 前置钩子在 **4 个会触发步骤执行的 Host 命令**上执行：`library_start_run`、`library_control_run`、
    `library_resume_blocked_run`、`library_retry_failed_targets`（`HostCommandDispatcher.cs:76-84`、`:146-160`）；
    只读命令不在集合内；授权异常经 `ProjectRunError` 保留原 code、category 降级为 unknown（`:180-188`），符合 R-5。
  - `library_control_run` 仅 `continue`/`restart` 触发，`pause`/`stop`/`abandon` 直接返回
    （`HostRuntime.cs:1511-1529`）。
  - `AcceptRun` 走 PrepareRun 记录的冻结 `{command, scope}` 前置授权（`HostRuntime.cs:60-137`）。
  - 能力探测只 `core.ping`（`SourceReadCoordinator.cs:91-106`）；缺失 → 不铸造、不绑定、按现状 dispatch
    （`HostRuntime.cs:1480-1494`）。
  - 源范围：book scope 按 project 过滤，否则全部已知源；known 为 0 / filtered 为 0 时跳过（`HostRuntime.cs:1617-1674`）；
    计数日志不落路径（`:1600-1607`）。
  - 记账有界：`MaxTrackedPayloads=256`、过期/撤销/绑定后剪枝（`SourceReadCoordinator.cs:40,114-207`）；
    单测断言 256 上界与过期清零（`SourceRegistryTests.cs:19-45`）。
  - 真实 IPC：Host 铸造 → 绑定 → `resolve_page_resource` 成功；另一 entry typed 拒绝；撤销后 typed；
    wire/stderr 无 fixture 路径（`Fea11RunGrantIpcTests.cs:66-148`）。
- **P2 覆盖缺口（R1-02）**：
  1. `AcceptRunAsync` 前置授权无任何单测/IPC 覆盖（代码在，无证据）；
  2. 能力缺失 → 跳过授权的分支无判别性测试；
  3. 真实 `HostRuntime.RunAuthorizeAsync`/`RunSourceTargets` 无测试；`SourceRegistryTests` 只测 dispatcher 注入的 fake delegate
     （`SourceRegistryTests.cs:48-121`），.NET IPC 直接调 `SourceReadCoordinator`（`Fea11RunGrantIpcTests.cs:73-85`），
     生产 Host 编排未被端到端验证；
  4. `library_control_run` pause/stop 不触发的分支无测试。
- 这些是「证据不足」而非「代码错误」；但 AC 段头要求「每条须有判别性测试」，故 AC-R4 判 PARTIAL。

### D. AC-R6 零漂移 —— **PASS**

- `git diff --name-status 218775bca..7ff49f1cc` 实测 11 文件，全部 ⊆ `allowed_paths`（含 R-12 的
  `tests/core/test_core_service.py` 与 `tests/fea09/test_referenced_wire.py`）。
- `git diff --name-only 2067789ea..7ff49f1cc`：`doc/plan/**`、`doc/contracts/**`、`schema.py`、`core_assembly.py`、
  `apps/**/NewManga.App/**`、依赖文件 **零 diff**。
- `CORE_PROTOCOL_MINOR = 3`（`src/bootstrap/core_service.py:320`）；`core_service.py` 相对 `218775bca` 仅 4 个 additive hunk
  （`:356`、`:1495`、`:1605`、`:4937`），`StartRun`/`PrepareRun`/`AcceptRun` 行零改动。
- 证据侧：pins 18/18、check PASS、API inventory EXIT=0 均独立实测；`scope-validation.log` 的 12 文件/禁止面全空与实测一致。
- 全量门禁独立实跑：pytest 3280/10、.NET 1535/0/88，均不降于卡基线（3249/10、1532/0/86）。

### E. AC-R7 证据真实性 —— **PASS（字节），PARTIAL（口径）**

- EV.md 27 个条目（11 实现/测试 + 14 证据 + 2 文档）逐文件 sha256 复算 **27/27 OK**；EV 排除自身，无循环。
- `changed-files.txt` 与 `git diff --name-status a94052ba7..7ff49f1cc` 逐行一致（12 行）。
- `RESOURCE-MANIFEST.json`：仓外隔离根存在；抽查 `baseline/dotnet-baseline.exit`、`discrimination/B1/B4/B5`、
  `check_ev.py`、`patch_*.py` 的 sha256 与 manifest 一致；`file_count=500` 是 2026-11-06T16:49:54 交付时快照
  （本次复核运行后目录文件数增加，属预期，不更改 manifest 快照）。
- 门禁数字与 logs 对照：`feature.log` 49 = 36+13；`host-unit.log` 5；`host-ipc.log` 2；`full-pytest.log` 3280/10；
  `full-dotnet.log` 聚合 1535/0/88；`gates-governance.log` 18/18 + PASS + EXIT=0。全部与独立实测一致。
- `logs/discrimination.log`：B1/B2 我独立复现（同测试、同失败面）；B3–B5 的破坏定义/目标用例见
  `tools/discrimination.py:56-88`，与目标测试语义一致（B3 去掉整体失败；B4 去掉 command 域校验；B5 去掉 dispatcher 钩子）。
- **PARTIAL 原因（R1-03/R1-09/R1-10）**：L-G12 不完整；EV 把 commit 行数用例描述为 `assemble_core_services` 真实装配
  （实际是 `build_run_harness`）；Handoff 称能力缺失跳过有「单测」（实际无）。
- **未发现**「手改证据后回填哈希」：27/27 字节与 EV 一致，且测试日志数字可由独立实跑复现。

### F. 契约一致性 —— **PASS（无违反级），有登记偏差**

按 C-16 v1.3 §2.4 逐条（契约 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:73-90`）：

| 条款 | 实现位置 | 判定 |
|---|---|---|
| closed shape `{grant_ids, command, scope}`；1..64；去重；非空 string | `core_service.py:4960-4990`；`source_read_refs.py:447-469` | **PASS**（重复采用 `INVALID_REQUEST`，见 R1-06） |
| 校验顺序 ① host-only ② shape ③ grant live（§6 优先级）④ 同 scope 展开器 | `core_service.py:1498-1513`（host/session）→ `:4949-4990`（shape）→ `:4992`（liveness）→ `:4994-5009`（expand） | **PASS**（另加 registry/catalog 可用性前置检查，生产恒成立） |
| command 域 = COMMAND_CATALOG + 同 Run scope 校验 | `core_service.py:4980-5002`；`_validate_command_scope` 复用 | **PASS** |
| per-page：managed 跳过；非 healthy / gate 非 open 拒绝；source_id/version + entry（key/locator/ordinal）+ facts | `source_read_refs.py:472-543,545-631` | **PASS**（容器 ordinal 语义见 R1-03） |
| 同一 gate 谓词 | `core_service.py:5011-5035` 用 `catalog.source_gate_reader`；assembly `core_assembly.py:1240-1261,1750` | **PASS** |
| 任一 refused → 整体 `SOURCE_ACCESS_DENIED`、`details={"refused_pages": n}`、零映射 | `source_read_refs.py:500-516` | **PASS**（details 以 M2-C1 envelope 的 `list[dict]` 包装，与既有先例一致） |
| 成功 → `{"bound_pages": n}`、与 `bind_imported_entry` 同构映射 | `source_read_refs.py:519-541`；`core_service.py:5044-5045` | **PASS**（卡 I-1 写成 `{bound_pages, refused}`，与契约冲突，见 R1-05） |
| 零 DB 写 / 不建 plan/journal / 不发布 / 不延 TTL / 不撤销 | handler 仅 SELECT + 进程内写；测试逐表快照 | **PASS** |
| 幂等（集合语义） | 同请求重复返回相同 bound_pages 与映射（`test_source_run_grant.py:501-511`） | **PASS** |
| 能力 `source.read.run/1` additive | `core_service.py:1605-1613`；两个既有精确期望 additive +1 | **PASS** |
| 错误码 §6 闭集、无新码、details 只计数/ID | `_source_import_error_envelope`；无新码 | **PASS** |
| 不改 Run wire / minor / schema / 依赖 | diff 与全量门禁 | **PASS** |

- **未发现「实现比契约更松」的授权放宽**；「更严」仅见 grant_ids 重复拒绝（R1-06）与 registry 可用性前置（P3）。
- **实现未引入第二套 target/page 解析**：直接 `_parse_run_scope` + `catalog.expand`，复用 Run 路径。
- **容器 per-entry 语义**见 R1-03：实现忠实于 §2.4 字面规则，但生产 Host 的容器 grant 无法为成员页提供 entry 身份；
  这是契约/Host 形状缺口，不是实现绕过契约。

### G. L-G12 诚实性与严重度 —— **FAIL（limitation 真实但登记不完整，口径需收窄）**

- **① limitation 真实**：`SourceScanScheduler.cs:1894-1895` 冷启动枚举把 `SourceScanTarget.Version` 固定为 `"1"`；
  `source_list_scan_targets` DTO 只有 `{source_id, registry_id, generation, source_kind, identity_digest, project_ids}`
  （`src/application/sources/scanner.py:165-176`；C-17 §5.2），无 `version_id`；`RegisterSourceScanTarget` 在生产 App
  无调用点（仅测试 `Fea11WatchHostRuntimeTests.cs:40`），且其默认 version 也是 `"1"`（`HostRuntime.cs:186-196`）。
  `RunSourceTargets` 把 `target.Version` 直接写入 `RunSourceScope`（`HostRuntime.cs:1661-1663`），因此生产 Host 铸造的
  grant 的 `scope.version` 与 Core `binding.accepted_source_version`（`sv-…`）通常不匹配 → `SOURCE_ACCESS_DENIED`、
  不 dispatch。该 limitation 在卡 `:142`、EV `:139`、Handoff `:66` 均已登记，**不是隐藏缺陷**。
- **② 登记不完整 / 口径过大**：生产 Host `IssueLockedAsync` 对非 folder 源只签 **一个 entry**，`locator = Path.GetFileName(member)`、
  `ordinal = 0`（`SourceReadCoordinator.cs:259-275`）；Core 对容器源的 per-entry 匹配是
  `entry_key == binding.entry_id` 或 `locator == source_entries.locator` 或 `ordinal == source_entries.ordinal`
  （`source_read_refs.py:598-610`）。容器 grant 的 locator 是容器文件名、ordinal 恒为 0，因此对 zip/cbz/pdf
  **只有 Core 侧 `source_entries.ordinal == 0` 的那一页**能命中；多成员归档的其余页永远 refused。
  .NET IPC 实测正是 p1（ordinal 0）`bound_pages=1`、p2（ordinal 1）`SOURCE_ACCESS_DENIED`
  （`Fea11RunGrantIpcTests.cs:77-109`）——测试注释把它解释为「entry granularity」，实际包含的是「容器 grant 只覆盖首成员」的
  功能限制。Python AC-R2 的 grant 使用成员 locator/ordinal（`test_source_run_grant.py:269-322`、
  `build_rendition_site` 的 `entries=[(archive_path, "002-current.png", 1)]`），该形状**不是生产 Host 对 zip 能铸出的**。
  因此 Handoff/EV 的「Host 接线在 Host 已知源携带正确 version 时可用」只对 image/folder 单 entry 源与归档首成员成立；
  **生产多页 zip Run 即使补上 version 通道仍不可用**。
- **③ 判定**：
  - 本卡**没有**写成「referenced Run 全场景可用 / L-R1 全修」（卡/EV/Handoff 均明确否定），R-11 的「不夸大」未被违反；
  - 但 **AC-R5 判 PARTIAL**（Host 层 managed 语义，见 R1-01），**AC-R4 判 PARTIAL**（证据覆盖，见 R1-02）；
  - **应扩写 L-G12**（或另立 follow-up `Host→Core source entry identity channel（archive member locators）`），并把
    「version 已知时可用」收窄为「image/folder 单 entry 源 + 归档首成员」；不建议把本卡判为「Core 机制不可用」——
    Core 命令本身在真实装配下完整成立，问题在 Host 数据通道与 limitation 边界。
  - **不建议**升级为 P0/P1 安全缺陷：Host 的容器 grant 本身是对整个容器的授权（facts 校验容器身份），
    当前表现为欠授权（只覆盖首成员）而非越权；`.NET IPC` 的 p2 拒绝是 fail-closed，不是静默放行。

### H. 其他 —— **PASS**

- **既有断言零弱化**：`git diff 218775bca..7ff49f1cc -- tests/` 全部为 **0 deletion**（`git diff --numstat` 实测），
  未删除/弱化任何断言；R-12 两文件仅 capabilities 精确期望 additive +1（`tests/core/test_core_service.py` 两处、
  `tests/fea09/test_referenced_wire.py` 一处），无新增 skip。
- **新增 skip 仅 2 个 opt-in IPC**（`NEWMANGA_FEA11_IPC=1`），与卡 AC-R4 的 opt-in 设计一致；全量 .NET（未设 env）中
  这 2 例 skipped，置 env 后过滤实跑 2 passed（两者均实测）。
- **`SourceRegistryTests` 增补是真断言**：`RunGrantLedgerIsBoundedAndPrunesExpiredGrants` 断言 256 上界与过期清零
  （`SourceRegistryTests.cs:19-45`）；`RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns` 断言拒绝码、
  只读命令 0 调用、4 个触发命令各调用一次（`:48-99`）；`RunAuthorizationHookWithoutARefusal…` 断言放行后到达真实 dispatch
  （`:101-121`）。
- **R-12 两处 capabilities 期望**：`git diff` 显示仅 + 注释 + 字符串，无删改；全量 pytest 通过。
- **`TargetSnapshot.metadata` 6 键**：与 RENDITION-1 既有断言一致（`tests/fea11/test_source_rendition_run.py:334-372`），
  本卡未新增键；测试断言见 `test_source_run_grant.py:488,882`。

---

## 3. AC-R1…R7 逐条判定

| AC | 判定 | 理由 |
|---|---|---|
| **AC-R1** | **MET** | 36 passed；host-only/session/closed shape/§6 typed/零 DB 写/幂等/能力公告均有测试；错误 JSON 无路径泄漏。P3：host-only 用例零写用 `total_changes` 而非逐表快照。 |
| **AC-R2** | **MET（有保留）** | 真实 `assemble_core_services` + 真实 zip/PNG + 真实签名 grant；绑定后 provider 像素 = 当前 binding（12×7，非 managed 30×20）、commit guard 打开；真实 handler 授权后 Run 提交写出 region/revision/lineage。保留：grant 形状为测试侧成员 entry（非 Host-mintable）；提交行数用 harness 而非 assembly；判别 B1/B2 我独立复现。 |
| **AC-R3** | **MET（有保留）** | 6 类 fail-closed typed、零业务写、不崩溃；授权面 lease spy 0。保留：⑥「Run 中途」用 provider/guard 面验证而非真在跑 Run；无 `read_entry_bytes` spy；pending gate 的 refused_pages 分支对 pure referenced 页被 `catalog.expand` 先拒，未直接覆盖 per-page gate 分支。 |
| **AC-R4** | **PARTIAL** | dispatcher 4 命令钩子、失败不 dispatch、只读不触发、剪枝上界、真实 IPC 均成立；但 AcceptRun 前置授权、能力缺失跳过、真实 `HostRuntime` 钩子（含 pause/stop 不触发）无判别性测试。 |
| **AC-R5** | **PARTIAL** | Core 授权面对 managed 页 `bound_pages=0`、零映射、零 DB 写、managed provider 仍读 Managed Copy、metadata 6 键不变、全量套件不降——这些成立。但「managed-only Run 不调用新命令 / 不触碰 grant registry」在 Host 层不成立：存在已知源时任何 Run 命令都会 mint + 调用命令；无关源铸造失败可阻断 managed Run（R1-01）。 |
| **AC-R6** | **MET** | scope diff ⊆ allowed_paths；禁止面全空；minor=3；Run wire 零改动；pins 18/18、check PASS、API inventory PASS；全量 pytest 3280/10、.NET 1535/0/88 独立复现。 |
| **AC-R7** | **PARTIAL** | EV 27/27 sha 全真、changed-files/scope-validation 全真、门禁数字全真、卡/EV/Handoff 未写「全场景可用」；但 L-G12 不完整（R1-03）、Handoff「能力缺失跳过有单测」不实（R1-10）、EV 对 commit 用例的装配描述不精确（R1-09）。 |

---

## 4. 破坏性复跑记录（备份 / 变红 / 恢复 / sha）

> 规则：破坏前 `Copy-Item` 备份到 `%TEMP%`，记录原始 sha256；只改目标分支；跑目标用例必须 exit≠0；
> `finally` 式恢复后重算 sha256 与原始值逐字节比较；`git status --porcelain -- <file>` 必须为空。

| # | 文件 | 原始 sha256 | 破坏内容 | 目标用例与结果 | 恢复 sha256 | 结论 |
|---|---|---|---|---|---|---|
| R-D1 | `src/infrastructure/resource_channel/source_read_refs.py` | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` | 把 `authorize_run_bindings` 的映射写入循环改为空迭代（成功路径不再写 `_bindings`） | `pytest tests/fea11/test_source_run_grant.py -q` → **3 failed / 10 passed**（`test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`、`test_real_run_commit_writes_expected_rows_after_authorization`、`test_binding_switched_mid_run_is_typed_and_writes_nothing`），首个失败在 `test_source_run_grant.py:474`（`_bindings` 为空） | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` | **RED + RESTORED（sha 一致）** |
| R-D2 | 同上 | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` | 删除容器源 `_location_matches` facts 核验（只保留 `facts is None`） | `pytest tests/fea11/test_source_run_grant.py::test_scope_and_facts_mismatch_is_refused -q` → **1 failed**（期望 `SOURCE_ACCESS_DENIED`，实际 `{"bound_pages": 1}`，`test_source_run_grant.py:670`） | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` | **RED + RESTORED（sha 一致）** |

- 两次破坏的 mutated sha 分别为 `a70987c2aaec80695eac83d251663e2aacd51810a4f71bf928fa5d00762baf76`（R-D1）与
  `4770c35c50d9cdae50ff38fbff3ca3738f424d965ec523359589e1267738f934`（R-D2）；恢复后 `git status --porcelain -- <file>` 均为空。
- 与证据对应：R-D1 = `logs/discrimination.log` B1（`test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`）；
  R-D2 = B2（`test_scope_and_facts_mismatch_is_refused`）。两者独立复现的证据一致。
- B3（去掉整体失败原子性）/ B4（去掉 command 域校验）/ B5（去掉 dispatcher 钩子）我未重跑（避免改写证据日志），
  但逐行核对 `tools/discrimination.py:56-88` 的破坏文本与目标测试语义：B3 目标用例断言 p1 被拒整体失败
  （`test_source_run_grant.py:522-536`）、B4 目标用例断言越域 command → `INVALID_REQUEST`（`:885-926`）、
  B5 目标用例断言钩子拒绝时不 dispatch（`SourceRegistryTests.cs:48-99`）；破坏定义与目标一致，`discrimination.log` 的
  `exit_code=1 verdict=RED_AS_EXPECTED` 与 sha 恢复记录可信。

---

## 5. Findings

| ID | 严重度 | 事实 | 最小修复 | 是否阻断 |
|---|---|---|---|---|
| **R1-01** | **P1** | **AC-R5 Host 层不成立 / 违反 I-2「不得改变既有非 referenced Run 行为」**：`RunAuthorizeAsync` 在 `ReferencedImportEnabled` 且 `RunSourceTargets` 非空时，对**任何** Run 命令（start/control continue\|restart/resume/retry，以及 AcceptRun 的 `AuthorizeRunSliceAsync`）都会 mint + 调用 `AuthorizeSourceReadForRun`，与 Run 是否含 referenced 页无关（`HostRuntime.cs:1480-1530,1574-1615`）。managed 页只是在 Core 授权面被跳过（`bound_pages=0`）；Host 已 mint 并触碰了 grant registry。若任一已知源铸造失败（registry 不可用/文件缺失/路径不可解析），managed-only Run 会被 typed 拒绝而不 dispatch。AC-R5 的「不调用新命令」只有「Host 无已知源」时才成立，且无测试覆盖 Host 层。 | 需 DSH 裁决：①把 AC-R5 明确为「Core 授权面对 managed 页跳过」并登记 Host 预授权成本/失败耦合；或 ②在 Host 侧增加可判定性（例如先通过只读 snapshot/projection 判断 Run 是否有 referenced target，无法判定时按 fail-open 跳过授权）；③无论哪种，补 Host 层 managed-only Run 不失败/不越权的判别性测试。 | **是**（frozen AC 未满足） |
| **R1-02** | P2 | **AC-R4 证据覆盖不足**：AcceptRun 前置授权、能力缺失跳过、真实 `HostRuntime.RunAuthorizeAsync`/`RunSourceTargets`、`library_control_run` pause/stop 不触发均无判别性测试；`SourceRegistryTests` 用注入 fake delegate（`SourceRegistryTests.cs:48-121`），.NET IPC 绕过 HostRuntime 直接调 coordinator（`Fea11RunGrantIpcTests.cs:73-85`）。 | 补 4 个测试：①dispatcher 钩子对 `library_control_run` pause/stop 不调用；②能力缺失时 `RunAuthorizeAsync` 不 mint 且 dispatch；③`AcceptRun` 从 `_preparedSlices` 取 command/scope 并调用授权；④`RunSourceTargets` 的 book 过滤/known=0/unresolved typed 分支。 | 否（补证据/或 DSH 降级 AC） |
| **R1-03** | P2 | **L-G12 登记不完整 / 生产口径过大**：Host 非 folder 源 grant 的 entry 是容器自身（locator=文件名、ordinal=0，`SourceReadCoordinator.cs:259-275`），Core 按成员 `source_entries` 匹配（`source_read_refs.py:598-610`），多成员 zip/cbz/pdf 只有 Core ordinal=0 的页可被授权；.NET IPC 的 p1 成功/p2 typed 拒绝（`Fea11RunGrantIpcTests.cs:77-109`）已实证该限制，但 L-G12 只写 version 通道；Handoff/EV 的「Host 已知源携带正确 version 时可用」对多成员容器不成立。Python AC-R2 的 grant 是测试侧成员 locator 形状，不是生产 Host mint 形状。 | 扩写 L-G12（或另立 follow-up）为「Host→Core source entry identity 通道缺失（容器成员 locator/ordinal）」，把可用边界收窄为 image/folder 单 entry 源 + 归档首成员；修正 .NET IPC 注释/测试语义与 Handoff/EV 措辞。 | 否（limitation/口径，但须 DSH 确认） |
| **R1-04** | P2 | **Host 预授权 typed 错误面不完整**：`RunSourceTargets` 在部分源可解析、部分 unresolved 时静默继续（`HostRuntime.cs:1669-1673`），与 R-7「无法解析 → typed（不静默放行）」存在解释冲突；`IssueLockedAsync` 的 `FileStream`/哈希 I/O 异常（`SourceReadCoordinator.cs:259-264`）不是 `SourceAccessException`，`AuthorizeRunSliceAsync` 只 catch `SourceAccessException`（`HostRuntime.cs:1598-1610`），可能以未类型化异常阻断 Run。 | 统一把 mint I/O 异常映射为 `SOURCE_ENTRY_MISSING`/`FILE_IDENTITY_CHANGED` 等 §6 typed；对 partial unresolved 明确「typed 拒绝或按 R-7 跳过」并测试。 | 否（健壮性） |
| **R1-05** | P3 | 卡 I-1 写响应 `{bound_pages, refused}`（`doc/tasks/FEA-11-RUN-GRANT-1.md:83`），与 C-16 v1.3 §2.4「成功不采用 refused 形态、成功仅 `{bound_pages}`」冲突；实现按契约（`core_service.py:5044-5045`）。 | closeout 修卡面措辞（不改契约）。 | 否 |
| **R1-06** | P3 | 契约写 `grant_ids`「1..64 个、去重、非空 string」；实现把重复 id 判 `INVALID_REQUEST`（`core_service.py:4969-4974`），Handoff/测试也按「重复非法」写（`test_host_control.py:707-708`）。若「去重」意为 Core 去重而非请求非法，则实现偏严。 | 在卡/契约解释记录「重复 → INVALID_REQUEST」并保持测试；或按契约改为去重接受。 | 否 |
| **R1-07** | P3 | AC-R3 要求 `read_entry_bytes`/`source_lease` spy 0；实测只有 `source_lease` spy（`test_source_run_grant.py:828-846`），无 `read_entry_bytes` spy；pending gate 用例走 `catalog.expand` 的 `TARGET_NOT_FOUND`，`authorize_run_bindings` 的 `gate != open` refused 分支对 pure referenced 页不可达（`source_read_refs.py:487-492`、`core_service.py:5011-5035`）。 | 补 `read_entry_bytes` spy 或说明 lease 已覆盖；为 per-page gate 分支加 mixed/legacy binding 用例。 | 否 |
| **R1-08** | P3 | AC-R1 写「全部零 DB 写（业务表逐表快照相等）」；host-only/session 参数化只用 `core.conn.total_changes`（`test_host_control.py:640-691`），shape/grant 用例才用逐表快照。 | host-only/session 也加逐表快照，或把 AC 口径改为「total_changes + 关键表」。 | 否 |
| **R1-09** | P3 | EV 把 `test_real_run_commit_writes_expected_rows_after_authorization` 描述为 `assemble_core_services` 真实装配（`EV.md:56-57,129`），实际是 in-memory migrations + `build_run_harness`（`test_source_run_grant.py:539-605`）；Handoff 的「RENDITION-1 同构真实 pipeline + 真实 store」更准确。 | 修 EV 措辞（不改变门禁数字）。 | 否 |
| **R1-10** | P3 | Handoff 写「能力缺失 → 跳过授权按现状 dispatch（代码路径 + 单测）」（`doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md:38`），实际无对应单测；代码路径存在（`HostRuntime.cs:1493-1497`）。 | 补 1 个单测或删「单测」二字。 | 否 |
| **R1-11** | P3 | `AcceptRunAsync` 行为变化：现在要求同 Host 进程内先 `PrepareRunAsync` 留下 slice，否则抛 `RUN_STALE_PREVIEW`（`HostRuntime.cs:69-137`）；仓内 App 无 UI 调用点（scope review §3.3），未登记该 API 行为变化。 | 在 Handoff limitations 登记，或为缺失 slice 保留旧直通行为（若 DSH 认为需要）。 | 否 |

---

## 6. L-G12 判定（对应任务 G）

| 问题 | 判定 | 依据 |
|---|---|---|
| ① limitation 是否真实、是否准确登记 | **真实，登记存在但不完整** | version 通道：`SourceScanScheduler.cs:1894-1895` 固定 `"1"`、C-17 §5.2 DTO 无 version、`RegisterSourceScanTarget` 无生产调用点；卡 `:142`、EV `:139`、Handoff `:66` 均已登记。**未登记**的是容器成员 entry 身份通道：`SourceReadCoordinator.cs:259-275` 单容器 entry vs `source_read_refs.py:598-610` 成员匹配；.NET IPC p1 成功/p2 拒绝已实证。 |
| ② 是否把「Core 机制可用」与「生产端到端可用」混写（R-11） | **未写成「全场景可用」，但「version 已知时可用」口径过大** | 卡/EV/Handoff 均明确否定「references Run 全场景可用 / L-R1 全修」；但「Host 已知源携带正确 version 时可用」对多成员 zip 不成立（首成员除外），且生产不存在提供正确 version 的路径。 |
| ③ 是否应判 AC 部分 MET / 加更重 limitation / 另立 follow-up | **AC-R4/R5 判 PARTIAL；应扩写 L-G12 并另立 follow-up；不建议升级为 P0/P1 安全缺陷** | AC-R5 的 Host 层 managed 语义未满足（R1-01/P1）；AC-R4 证据覆盖不足（R1-02/P2）；L-G12 扩写 + `Host→Core source entry identity channel` follow-up（R1-03/P2）。容器 grant 是整容器授权 + facts 校验，当前是欠授权而非越权，故不判安全 P0。 |

---

## 7. 与卡面/Handoff 自述的交叉核对

| 自述 | 实测 | 判定 |
|---|---|---|
| `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → 49 passed | 36 + 13 = **49 passed**（分开跑） | 真 |
| 全量 pytest 3280/10 | **3280/10**（独立跑，247.33s） | 真 |
| 全量 .NET 1535/0/88 | **1535/0/88**（独立跑，exit 0；聚合 21+38+253+117+31+188+167+720） | 真 |
| 真实 IPC 2 passed（不设 env 2 skipped） | **2 passed**（env=1 过滤实跑）；全量 .NET 未设 env 时这 2 例 skipped | 真 |
| SourceRegistry 5 passed | **5 passed** | 真 |
| pins 18/18 / check PASS / API inventory EXIT=0 | 独立实测一致 | 真 |
| 判别性 5/5 + 字节恢复 | B1/B2 独立复现；B3–B5 破坏定义/目标逐行核对 | 真（B1/B2 强证据，B3–B5 为脚本+日志证据） |
| EV 27 文件 sha256 | 27/27 全匹配 | 真 |
| changed-files 12 文件、禁止面零 diff、minor=3 | 与 `git diff` 一致 | 真 |
| 「能力缺失 → 跳过授权按现状 dispatch（代码路径 + 单测）」 | 有代码路径，**无单测** | **不实（R1-10）** |
| 「Host 接线在 Host 已知源携带正确 version 时可用」 | 对 image/folder 单 entry 源可成立；对多成员 zip 仅首成员 | **口径过大（R1-03）** |
| 「Core 级机制完整可用」 | 真实装配 + 真实 grant 下成立 | 真（但 grant 为测试侧成员形状，见 R1-03） |

---

## 8. 最终 verdict

**`changes_requested`。**

- **不阻断的事实**：实现主体、测试真实性、判别性、门禁数字、证据链均通过；没有 P0；没有数据破坏/越权/静默放行。
- **必须处置后才能 closeout**：
  1. **R1-01（P1）**：AC-R5 的 Host 层 managed 语义——由 DSH 明确「managed-only Run 预授权成本/失败耦合」的口径，并补 Host 层测试；
     若 DSH 认定 AC-R5 仅为 Core 授权面语义，则须以裁决形式修订 AC 并把 Host 预授权行为登记为 limitation（不得保持现状自述「零回归」）。
  2. **R1-02（P2）**：补 AC-R4 的 AcceptRun / 能力缺失 / 真实 HostRuntime 钩子 / pause-stop 不触发测试，
     或由 DSH 明确接受当前覆盖并降级 AC-R4。
  3. **R1-03（P2）**：扩写 L-G12 或另立 `Host→Core source entry identity` follow-up；收窄「version 已知时可用」表述，
     修正 .NET IPC 注释/断言语义（p1 = 首成员 ordinal 命中，不是通用 entry 粒度）。
  4. **R1-04（P2）**：Host mint I/O 异常 typed 化；partial unresolved 的 R-7 语义明确。
  5. P3（R1-05…R1-11）可在 closeout 文档批一并处置。
- **建议**：修完后由独立上下文做 r2 窄面复核；本 r1 不批准集成。

---

## 9. 真实性声明

- 本报告是 fresh 上下文独立只读 Review：未参与 `FEA-11-RUN-GRANT-1`（或 PREREQ-1）的实现、返修、证据生成或 Handoff 编写；
  未在同一会话中实现该变更。
- 唯一写入是 `doc/reviews/FEA-11-RUN-GRANT-1-r1.md`（本文件）。未修改实现、测试、证据、卡、契约、STATUS/PLAN/LEDGER；
  未 `git add`/`commit`/`push`；未删除/移动/归档任何文件。
- 破坏性复跑记录见 §4：两次修改均先备份、后恢复，恢复后 sha256 与原始值逐字节一致（`c2680a09…`），
  `git status --porcelain -- <file>` 为空。
- 全量 .NET 运行的 tracked 副作用已恢复：`verification/FEA-09/logs/wire-redacted.ndjson` 从 side-effect sha
  `5E50A98E…` 恢复为 `548DE629D163D80B9CD8D1E62251DE2016782E46A0C48A48575749D2A059D593`（5004 bytes，与运行前一致）。
- 定向/全量 pytest、.NET IPC 与全量 .NET 在仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/fixtures/`
  生成的测试夹具目录未删除（属测试运行产物，不在仓库内）；仓库工作树在本报告写入前为 clean。
- 本报告所有「实测」均有对应命令与结果记录；未执行项（如 `tools/discrimination.py` 全脚本复跑、全量 .NET 的逐用例
  二次隔离复跑）已明确标注理由或替代验证方式，未以静态判断冒充实测。
