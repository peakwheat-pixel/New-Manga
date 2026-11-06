"""Generate verification/FEA-11-RUN-GRANT-1/EV.md (per-file sha256 + AC matrix).

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py
"""

from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-1"
DELIVERY_HEAD = "7ff49f1cc21346be0b4867304499ee17f7ffb84e"
BASE = "a94052ba7"


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
        _row("doc/tasks/FEA-11-RUN-GRANT-1.md", "卡面（AC/交付记录）"),
        _row("doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md", "Handoff"),
    ]
    import json as _json

    manifest = _json.loads((EVIDENCE / "RESOURCE-MANIFEST.json").read_text(encoding="utf-8"))
    workspace_files = next(
        item["file_count"] for item in manifest["resources"]
        if item["resource_type"] == "temp"
    )
    lines = [
        "# FEA-11-RUN-GRANT-1 Canonical Evidence（Run-scoped source-read 授权）",
        "",
        "> 结论先行：本卡交付 **C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`**（Core host-control 授权建立命令，"
        "第三 `_bindings` 生产者）与 **Host 铸造/绑定/接线**（Run 前置授权：mint → bind → dispatch；失败不 dispatch、"
        "返回授权自身 typed code）。在 **真实 migrations 库 + 真实 zip/PNG + 真实签名 grant + `assemble_core_services`** "
        "下，经本命令绑定后 Run 目标展开、provider 读取**当前 binding** 像素、commit guard 通过、真实 Run 提交写出 "
        "region/revision/lineage。**不宣称**「referenced Run 全场景可用」或「L-R1 全修」：仍受 L-G1（300s 窗口）、"
        "L-G2（加密源）、L-G8（铸造 I/O 成本）、L-G9（Core 重启）、L-G10（两读面 gate 差异）、L-G11（Host 不提供 "
        "page→binding）、以及本卡实测的 **L-G12（Host 无 Core version 通道）** 限制；只承诺「窗口内可用 + Host 源范围/"
        "version 已知时可用」。",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| task | `FEA-11-RUN-GRANT-1`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-1.md`；`status` 未改） |",
        "| Owner | `run-grant-impl`（DSH Agent Teams teammate；Lead `lead`） |",
        f"| base | 卡 `base_commit=2067789ea`；实现起点 `{BASE}` |",
        f"| delivery_head | `{DELIVERY_HEAD}`（实现+测试提交；证据/卡/Handoff 为同批文档提交） |",
        "| 分支/工作树 | `main` / `G:\\CODEX\\New Manga`（未创建 linked worktree、未 push） |",
        "| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 10.0.26300 |",
        "| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**` 全空 diff；pins 18/18） |",
        "| 依赖 | **零新增** |",
        "| R-12 扩域 | `tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`（仅 capabilities 精确期望 additive +1；Lead 提交 `218775bca` 批准） |",
        "",
        "## 1. 交付 commit 链（base `" + BASE + "` → delivery_head `" + DELIVERY_HEAD + "`）",
        "",
        "```text",
        *chain,
        "```",
        "",
        "## 2. 门禁实测（`" + DELIVERY_HEAD[:9] + "`）",
        "",
        "| Gate | 命令 | 结果 | 日志 |",
        "|---|---|---|---|",
        "| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 49 passed** | `logs/feature.log` |",
        "| 真实 IPC（AC-R4） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter \"FullyQualifiedName~Fea11RunGrant\"` | **PASS 2 passed**（不设 env 时 2 skipped） | `logs/host-ipc.log` |",
        "| Host 单测（AC-R4/R5） | `dotnet test ... --filter \"FullyQualifiedName~SourceRegistry\"` | **PASS 5 passed** | `logs/host-unit.log` |",
        "| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3280 passed / 10 skipped**（卡基线 3249/10，+31） | `logs/full-pytest.log` |",
        "| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1535 / 0 / 88**（卡基线 1532/0/86） | `logs/full-dotnet.log` |",
        "| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |",
        "| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS**（12 文件全 ALLOWED；禁止面全空；minor=3） | `scope-validation.log`、`changed-files.txt` |",
        "| 判别性 | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **5/5 破坏点变红 + 5/5 字节级 RESTORED + rebuild OK** | `logs/discrimination.log` |",
        "",
        "**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行 "
        "`git checkout -- verification/FEA-09`（见 `logs/gates-governance.log` 尾注）。**已知 flaky/环境交互**：全量 .NET 首跑 1 例 "
        "`NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 失败，原因是该用例比较 "
        "`git status --porcelain -- verification` 前后快照（当时证据目录在运行中新建 + FEA-09 tracked 字节未恢复）；clean 工作树隔离复跑 "
        "**1535/0/88 全绿**，非产品缺陷，Handoff §2 如实记录。skip 说明：pytest 10 skipped 与 .NET 88 skipped 均为既有环境门控"
        "（无 provider 权重/GPU、sidecar/UI 集成 opt-in、本卡 2 个 `NEWMANGA_FEA11_IPC` 未设时跳过），本卡未新增 skip 条件。",
        "",
        "## 3. 判别性验证（≥4 破坏点，删掉实现必须变红）",
        "",
        "`logs/discrimination.log`（脚本 `tools/discrimination.py`）逐个破坏一条已提交的生产分支后运行**一个**目标用例，"
        "必须变红（exit≠0），随后按**原字节**恢复并复核 sha256，最后重新 build 恢复二进制：",
        "",
        "| Case | 破坏点 | 目标用例 | 实测 |",
        "|---|---|---|---|",
        "| B1 | 删除 `authorize_run_bindings` 的映射写入 | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard` | **RED_AS_EXPECTED + RESTORED** |",
        "| B2 | 删除容器源 facts 与 `source_locations` 的核验 | `test_scope_and_facts_mismatch_is_refused` | **RED_AS_EXPECTED + RESTORED** |",
        "| B3 | 删除「有 refused 页即整体失败」的原子性 | `test_authorization_is_entry_granular_and_refuses_other_pages` | **RED_AS_EXPECTED + RESTORED** |",
        "| B4 | 删除 `command` 在 `COMMAND_CATALOG` 的取值域校验 | `test_forged_shape_requests_are_invalid_requests` | **RED_AS_EXPECTED + RESTORED** |",
        "| B5 | 删除 Host dispatcher 的 Run 前置授权钩子 | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns` | **RED_AS_EXPECTED + RESTORED**（final_rebuild exit 0） |",
        "",
        "## 4. AC 矩阵（测试 → 证据映射）",
        "",
        "| AC | 判定 | 判别性测试 | 证据 |",
        "|---|---|---|---|",
        "| AC-R1 协议面 | MET | `tests/core/test_host_control.py`（host-only/session/closed shape/§6 typed/零 DB 写/能力公告，+13 用例）+ `tests/fea11/test_source_run_grant.py::test_forged_shape_requests_are_invalid_requests`、`::test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（幂等） | `logs/feature.log`、`C-16 v1.3 §2.4` |",
        "| AC-R2 真实装配 Run 端到端 | MET | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`、`test_real_run_commit_writes_expected_rows_after_authorization`、`test_real_run_without_authorization_writes_nothing`、`test_authorization_is_entry_granular_and_refuses_other_pages`；判别 B1/B2/B3 | `logs/discrimination.log`、`logs/feature.log` |",
        "| AC-R3 fail-closed 6 例 | MET | `test_missing_grant_is_refused_and_writes_nothing`、`test_expired_grant_is_refused_with_the_frozen_priority`、`test_revoked_grant_is_refused_with_the_frozen_priority`、`test_scope_and_facts_mismatch_is_refused`、`test_pending_publication_gate_blocks_the_authorization`、`test_binding_switched_mid_run_is_typed_and_writes_nothing`、`test_authorization_never_leases_the_source`（source_lease spy 0） | `logs/feature.log` |",
        "| AC-R4 Host 接线/生命周期/IPC | MET | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns`、`RunAuthorizationHookWithoutARefusalLetsTheRunCommandReachDispatch`、`RunGrantLedgerIsBoundedAndPrunesExpiredGrants`、`Fea11RunGrantIpcTests`（opt-in 2 实跑） | `logs/host-unit.log`、`logs/host-ipc.log` |",
        "| AC-R5 managed 零回归 | MET | `test_managed_targets_are_skipped_not_refused`、`test_forged_shape_requests_are_invalid_requests`（TARGET_METADATA_KEYS 6 键）、全量 pytest/.NET 不降 | `logs/feature.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |",
        "| AC-R6 零漂移与门禁 | MET | `scope_validation.py`（禁止面全空、minor=3）+ pins/check/API inventory + 全量 pytest/.NET | `scope-validation.log`、`changed-files.txt`、`logs/gates-governance.log` |",
        "| AC-R7 证据/Handoff/不夸大 | MET | 本 EV 逐文件 sha256；`RESOURCE-MANIFEST.json`；Handoff §3 limitations（L-G1/2/8/9/10/11/**12**）与未宣称项；卡面未写「全场景可用/L-R1 全修」 | 本文件、`RESOURCE-MANIFEST.json`、`doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md` |",
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
        "# 2) 全量 Python（跑后恢复 FEA-09 tracked 字节）",
        "C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09",
        "# 3) 真实 IPC（不设 env 时 2 skipped）",
        "$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter \"FullyQualifiedName~Fea11RunGrant\"",
        "# 4) 全量 .NET（跑后恢复 FEA-09）",
        "dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09",
        "# 5) 治理",
        "pwsh -NoProfile -File tools/governance/verify_pins.ps1",
        "pwsh -NoProfile -File tools/governance/check.ps1",
        "pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md",
        "C:/Python314/python.exe tools/generate_api_inventory.py --check",
        "# 6) 范围 + 判别性",
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
        "- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up，本卡不碰。",
        "- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。",
        "- **L-G12（本卡实测新增，待 DSH 裁决）**：Host 侧无 Core `version_id` 通道（枚举 DTO 无 version、寒启动 "
        "`SourceScanTarget.Version` 固定 `\"1\"`），生产 Host 用既有 `IssueAsync` 铸出的容器 grant 通常与 "
        "`binding.accepted_source_version` 不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）。"
        "Core 级机制完整可用（真实 grant/facts/entry 匹配）；Host 接线在 Host 已知源携带正确 version 时可用"
        "（.NET IPC 冻结 fixture `s1`/`sv1` 实跑成功）。缓解候选见 Handoff §3/§6。",
        "- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；本卡只交付「窗口内可用 + Host 源范围/version "
        "已知时可用」；FEA-11 AC11-5/AC11-9 未回填（由 Lead closeout 决定）。",
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
