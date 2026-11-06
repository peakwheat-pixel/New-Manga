"""Generate verification/FEA-11-RUN-GRANT-1/EV.md (per-file sha256 + AC matrix).

Review r1 rework edition (2026-11-07).

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-1"
BASE = "a94052ba7"
DELIVERY_HEAD = "3ffabeb8134b355076a9e964305de895e7c5b9d1"
HANDOFF = "doc/handoffs/FEA-11-RUN-GRANT-1-3ffabeb81.md"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    ).stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row(path: str, note: str) -> str:
    return f"| {note} | `{path}` | `{_sha256(REPO / path)}` |"


def main() -> int:
    chain = _git("log", "--oneline", f"{BASE}..{DELIVERY_HEAD}").splitlines()
    changed = _git("diff", "--name-only", f"{BASE}..{DELIVERY_HEAD}").splitlines()
    delivery_rows = [
        _row(path, "实现/测试")
        for path in changed
        if path.startswith(("src/", "tests/", "apps/"))
    ]
    evidence_files = sorted(
        path for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "EV.md"
    )
    evidence_rows = [
        _row(str(path.relative_to(REPO)).replace("\\", "/"), "证据")
        for path in evidence_files
    ]
    doc_rows = [
        _row("doc/tasks/FEA-11-RUN-GRANT-1.md", "卡面（AC/处置记录）"),
        _row(HANDOFF, "Handoff（Review r1 返修）"),
    ]
    manifest = json.loads((EVIDENCE / "RESOURCE-MANIFEST.json").read_text(encoding="utf-8"))
    workspace_files = next(
        item["file_count"] for item in manifest["resources"]
        if item["resource_type"] == "temp"
    )
    lines = [
        "# FEA-11-RUN-GRANT-1 Canonical Evidence（Run-scoped source-read 授权；Review r1 返修版）",
        "",
        "> 结论先行：本卡交付 **C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`**（Core host-control 授权建立命令，"
        "第三 `_bindings` 生产者）与 **Host 铸造/绑定/接线**。Review r1（`changes_requested` P0=0/P1=1/P2=3/P3=7）后已完成"
        "**R1-01…R1-11 全部处置**：Host 预授权改为 **best-effort**（能力缺失/无相关源/mint I/O 失败 → 跳过并继续 dispatch；"
        "只有 Core 对目标页的 typed 拒绝才阻断，R-5 不变）；补齐 AC-R4 的 pause/stop、能力缺失、AcceptRun prepared-slice、"
        "源范围过滤判别性测试；L-G12 扩写为「version 通道 + 容器成员 entry 身份通道」并把可用边界收窄为 "
        "**image/folder 单 entry 源 + 归档首成员**。**不宣称**「referenced Run 全场景可用」或「L-R1 全修」；"
        "仍受 L-G1（300s）、L-G2（加密源）、L-G8（mint I/O 成本）、L-G9（Core 重启）、L-G10（两读面 gate 差异）、"
        "L-G11（Host 不提供 page→binding）、**L-G12（见上）**、L-G14（AcceptRun prepared-slice 行为）限制。"
        "独立 **r2 窄面复审由 Lead 指派**，本 EV 不替代复审。",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| task | `FEA-11-RUN-GRANT-1`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-1.md`；`status` 未改） |",
        "| Owner | `run-grant-impl`（DSH Agent Teams teammate；Lead `lead`） |",
        f"| base | 卡 `base_commit=2067789ea`；实现起点 `{BASE}` |",
        "| r1 delivery head | `7ff49f1cc`（Review r1 reviewed_head；证据 r1 版 `b28133392`） |",
        f"| 本次 delivery_head | `{DELIVERY_HEAD}`（Review r1 返修；证据/卡/Handoff 为同批文档提交） |",
        "| 分支/工作树 | `main` / `G:\\CODEX\\New Manga`（未创建 linked worktree、未 push） |",
        "| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 10.0.26300 |",
        "| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**` 全空 diff；pins 18/18） |",
        "| 依赖 | **零新增** |",
        "| R-12 扩域 | `tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`（仅 capabilities 精确期望 additive +1；Lead 提交 `218775bca` 批准） |",
        "",
        "## 1. 交付 commit 链（base `" + BASE + "` → delivery_head `" + DELIVERY_HEAD[:9] + "`）",
        "",
        "```text",
        *chain,
        "```",
        "",
        "## 2. 门禁实测（Review r1 返修后；`" + DELIVERY_HEAD[:9] + "`）",
        "",
        "| Gate | 命令 | 结果 | 日志 |",
        "|---|---|---|---|",
        "| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed**（36 + 14） | `logs/feature.log` |",
        "| Host 单测（AC-R4/R5/R1-01/R1-02/R1-04） | `dotnet test ... --filter \"FullyQualifiedName~SourceRegistry\"` | **PASS 17 passed**（r1 5 + 12） | `logs/host-unit.log` |",
        "| 真实 IPC（AC-R4/R1-01/R1-03） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter \"FullyQualifiedName~Fea11RunGrant\"` | **PASS 2 passed**（不设 env 时 2 skipped） | `logs/host-ipc.log` |",
        "| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped**（r1 基线 3280/10，+1） | `logs/full-pytest.log` |",
        "| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1547 / 0 / 88**（r1 基线 1535/0/88，+12 单测；2 个 IPC opt-in 未设 env 时 skipped） | `logs/full-dotnet.log` |",
        "| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |",
        "| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS**（changed 文件全 ALLOWED；禁止面全空；minor=3） | `scope-validation.log`、`changed-files.txt` |",
        "| 判别性（6 点） | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **6/6 破坏点 RED_AS_EXPECTED + 6/6 字节级 RESTORED + rebuild OK** | `logs/discrimination.log` |",
        "",
        "**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；均执行 "
        "`git checkout -- verification/FEA-09`。**已知 flaky/环境交互**：全量 .NET 首次运行时若 `verification/` 目录正在被写入"
        "（或 FEA-09 tracked 字节未恢复），`NewManga.App.Tests.FluentResidual2VisualEvidenceTests` 会因 `git status --porcelain -- "
        "verification` 前后快照不一致而失败；clean tree 隔离复跑 **1547/0/88 全绿**（非产品缺陷）。skip 说明：pytest 10 skipped "
        "与 .NET 88 skipped 均为既有环境门控（无 provider 权重/GPU、sidecar/UI 集成 opt-in、本卡 2 个 `NEWMANGA_FEA11_IPC` "
        "未设时跳过），本卡未新增 skip 条件。",
        "",
        "## 3. 判别性验证（6 破坏点，删掉实现必须变红）",
        "",
        "`logs/discrimination.log`（脚本 `tools/discrimination.py`，`repo_head=" + DELIVERY_HEAD[:9] + "`）逐个破坏一条已提交的"
        "生产分支后运行**一个**目标用例，必须变红（exit≠0），随后按**原字节**恢复并复核 sha256，最后重新 build 恢复二进制：",
        "",
        "| Case | 破坏点 | 目标用例 | 实测 |",
        "|---|---|---|---|",
        "| B1 | 删除 `authorize_run_bindings` 的映射写入 | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard` | **RED_AS_EXPECTED + RESTORED** |",
        "| B2 | 删除容器源 facts 与 `source_locations` 的核验 | `test_scope_and_facts_mismatch_is_refused` | **RED_AS_EXPECTED + RESTORED** |",
        "| B3 | 删除「有 refused 页即整体失败」的原子性 | `test_authorization_is_entry_granular_and_refuses_other_pages` | **RED_AS_EXPECTED + RESTORED** |",
        "| B4 | 删除 `command` 在 `COMMAND_CATALOG` 的取值域校验 | `test_forged_shape_requests_are_invalid_requests` | **RED_AS_EXPECTED + RESTORED** |",
        "| B5 | 删除 Host dispatcher 的 Run 前置授权钩子 | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns` | **RED_AS_EXPECTED + RESTORED** |",
        "| **B6（R1-01 新增）** | 删除 Host 预授权 best-effort 跳过（mint 失败重新阻断） | `SourceRegistryTests.RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot` | **RED_AS_EXPECTED + RESTORED**（final_rebuild exit 0） |",
        "",
        "## 4. AC 矩阵（测试 → 证据映射；Review r1 修订后）",
        "",
        "| AC | 判定 | 判别性测试 | 证据 |",
        "|---|---|---|---|",
        "| AC-R1 协议面 | MET | `tests/core/test_host_control.py`（host-only/session + **逐表快照零写（R1-08）**/closed shape/§6 typed/能力公告，13 用例）+ `test_forged_shape_requests_are_invalid_requests`、`test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（幂等） | `logs/feature.log` |",
        "| AC-R2 真实装配 Run 端到端 | MET | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（真实 `assemble_core_services`：target/provider/commit guard）；`test_real_run_commit_writes_expected_rows_after_authorization`（**RENDITION-1 同构 harness**：in-memory migrations + `build_run_harness`，非 assemble —— R1-09 修正）；`test_real_run_without_authorization_writes_nothing`；判别 B1/B2/B3 | `logs/discrimination.log`、`logs/feature.log` |",
        "| AC-R3 fail-closed 6 例 | MET | `test_missing_grant_*`、`test_expired_*`、`test_revoked_*`、`test_scope_and_facts_mismatch_is_refused`、`test_pending_publication_gate_blocks_the_authorization`、`test_binding_switched_mid_run_*`；`test_authorization_never_leases_or_reads_the_source`（**`source_lease` + `read_entry_bytes` 双 spy 0**，R1-07）；`test_per_page_gate_refusal_uses_the_shared_gate_predicate`（mixed binding per-page gate，R1-07） | `logs/feature.log` |",
        "| AC-R4 Host 接线/生命周期/IPC | MET | `SourceRegistryTests`（**17 例**：dispatcher 4 命令钩子/只读不触发、`RunCommandPolicy` pause/stop/abandon 不触发（R1-02①）、能力缺失跳过（R1-02②）、`PreparedRunSlices` + AcceptRun seam（R1-02③）、`RunSourceRange` book 过滤/known=0/unresolved（R1-02④）、best-effort/Core 阻断判别、剪枝上界）；`Fea11RunGrantIpcTests`（2 实跑：首成员成功/多成员 fail-closed/mint 失败 best-effort/partial/wire 无路径） | `logs/host-unit.log`、`logs/host-ipc.log` |",
        "| AC-R5 managed 零回归（修订口径） | MET | Core 面：`test_managed_targets_are_skipped_not_refused`（`bound_pages=0`、零映射、零 DB 写、metadata 6 键）；**Host best-effort**：`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`（mint 失败→到达 dispatch；Core 拒绝→不 dispatch）、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`；IPC 层 mint 失败/partial | `logs/feature.log`、`logs/host-unit.log`、`logs/host-ipc.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |",
        "| AC-R6 零漂移与门禁 | MET | `scope_validation.py`（changed 全 ALLOWED、禁止面全空、minor=3）+ pins/check/API inventory + 全量 pytest/.NET | `scope-validation.log`、`changed-files.txt`、`logs/gates-governance.log` |",
        "| AC-R7 证据/Handoff/不夸大 | **PARTIAL（待 r2）** | 本 EV 逐文件 sha256；`RESOURCE-MANIFEST.json`；Handoff §3 limitations（L-G1/2/8/9/10/11/**12 扩写**/13/**14**）与未宣称项；卡面未写「全场景可用/L-R1 全修」；**独立 r1 changes_requested → findings 已处置 → 独立 r2 窄面复审待 Lead 指派** | 本文件、`RESOURCE-MANIFEST.json`、Handoff |",
        "",
        "### 4.1 Review r1 findings 处置映射",
        "",
        "| Finding | 状态 | 判别性证据（本 EV 对应测试） |",
        "|---|---|---|",
        "| R1-01（P1）Host best-effort | FIXED | `RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、IPC mint/partial；判别 B6 |",
        "| R1-02（P2）AC-R4 覆盖 4/4 | FIXED | `RunCommandPolicy`/`RunAuthorizerControlActionsPauseStopDoNotAuthorize`、能力缺失、`PreparedRunSlices`/Accept seam、`RunSourceRange` |",
        "| R1-03（P2）L-G12 扩写/口径 | FIXED | 卡 L-G12、Handoff §3、IPC 首成员/多成员语义、`test_authorization_is_entry_granular_*` docstring |",
        "| R1-04（P2）错误面 | FIXED | `RunSourceAuthorizerMapsMintIoFailuresToFrozenCodes`、`RunSourceRange...`、IPC mint/partial |",
        "| R1-05/R1-06（P3） | FIXED | 卡 I-1 响应形态 + `grant_ids` 封闭形状行/测试注释 |",
        "| R1-07（P3） | FIXED | `test_authorization_never_leases_or_reads_the_source`、`test_per_page_gate_refusal_uses_the_shared_gate_predicate` |",
        "| R1-08（P3） | FIXED | `test_authorize_source_read_for_run_is_host_only_and_session_gated`（total_changes + 逐表快照） |",
        "| R1-09/R1-10（P3） | FIXED | 本节 AC-R2 措辞（harness）、能力缺失单测 |",
        "| R1-11（P3） | FIXED（登记） | Handoff §3 L-G14：`AcceptRunAsync` 需同进程 `PrepareRunAsync`，否则 `RUN_STALE_PREVIEW` |",
        "",
        "## 5. 逐文件 sha256",
        "",
        "### 5.1 交付文件（实现 + 测试，`" + DELIVERY_HEAD[:9] + "`）",
        "",
        "| 类别 | path | sha256 |",
        "|---|---|---|",
        *delivery_rows,
        "",
        "### 5.2 证据文件（本目录，`EV.md` 除外）",
        "",
        "| 类别 | path | sha256 |",
        "|---|---|---|",
        *evidence_rows,
        "",
        "### 5.3 文档（同批文档提交）",
        "",
        "| 类别 | path | sha256 |",
        "|---|---|---|",
        *doc_rows,
        "",
        "> `RESOURCE-MANIFEST.json` 的仓外隔离根聚合 sha256 覆盖工作区/日志/夹具全部文件（"
        + str(workspace_files)
        + " 个），逐文件详情见该 JSON 的 ``children``。",
        "",
        "## 6. 复现命令",
        "",
        "```powershell",
        "# 1) 定向",
        "C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q",
        "# 2) Host 单测 / 真实 IPC",
        "dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter \"FullyQualifiedName~SourceRegistry\"",
        "$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter \"FullyQualifiedName~Fea11RunGrant\"",
        "# 3) 全量（跑后恢复 FEA-09 tracked 字节）",
        "C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09",
        "dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09",
        "# 4) 治理",
        "pwsh -NoProfile -File tools/governance/verify_pins.ps1",
        "pwsh -NoProfile -File tools/governance/check.ps1",
        "pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md",
        "C:/Python314/python.exe tools/generate_api_inventory.py --check",
        "# 5) 范围 + 判别性",
        "C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py",
        "C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/discrimination.py",
        "```",
        "",
        "## 7. limitations / 未宣称（closeout 必须保留）",
        "",
        "- **L-G1**：单 grant ≤300s；窗口后的提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑 follow-up。",
        "- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）。",
        "- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希），大库未标定。",
        "- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail）。",
        "- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up。",
        "- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。",
        "- **L-G12（Review r1 R1-03 扩写）Host→Core 源身份通道缺失**：①**version 通道**（枚举 DTO 无 version、寒启动 "
        "version 固定 `\"1\"`）→ 生产 Host 容器 grant 的 `scope.version` 通常与 `binding.accepted_source_version` "
        "不匹配 → typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）；②**容器成员 entry 身份通道**（Host 单容器 "
        "entry、locator=容器名/ordinal=0 vs Core 成员 `source_entries` 匹配）→ 多成员归档只有首成员可被授权，其余 "
        "fail-closed 拒绝。可用边界 = **image/folder 单 entry 源 + 归档首成员**；follow-up 候选 "
        "`FEA-11-RUN-GRANT-2`（proposed）。",
        "- **L-G14（Review r1 R1-11）**：`HostRuntime.AcceptRunAsync` 需同进程先 `PrepareRunAsync`（冻结 slice），"
        "缺失/过期 → `RUN_STALE_PREVIEW`；仓内 App 无 Prepare/Accept 调用点。",
        "- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；只交付「窗口内可用 + image/folder 单 entry 源与"
        "归档首成员（L-G12 边界）」；FEA-11 AC11-5/AC11-9 未回填；独立 r2 窄面复审由 Lead 指派。",
        "",
        "## 8. 生成信息",
        "",
        f"- generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- delivery_head={DELIVERY_HEAD}",
        "- generator=`verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py`（sha256 由本地文件实时计算）",
        "",
    ]
    (EVIDENCE / "EV.md").write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"WROTE {EVIDENCE / 'EV.md'} rows={len(delivery_rows) + len(evidence_rows) + len(doc_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
