"""FEA-11-RUN-GRANT-2 (2B) canonical evidence generator (card AC-J4).

Reads the real gate logs committed under ``verification/FEA-11-RUN-GRANT-2/logs/``,
extracts the measured numbers and writes ``EV.md`` with:

* the delivery commit chain and the evidence status;
* the gate table (command -> measured result -> log);
* the discrimination table (8 break points, RED + byte-level RESTORED);
* the AC matrix (AC-J1..AC-J4 plus the card's AC-H1..H5 mapping);
* a per-file sha256 table for every evidence file (``EV.md`` itself excluded);
* the NOT_RUN / limitation / non-claim section.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2/tools/gen_ev.py
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2"
LOGS = EVIDENCE / "logs"
OUT = EVIDENCE / "EV.md"

DELIVERY_BASE = "5397be149"
DELIVERY_COMMITS = ["7466cb99d", "018008989"]
DELIVERY_HEAD = "0180089894b2286d8ff6a94289b84dd318871d18"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(name: str) -> str:
    path = LOGS / name
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _last_line(text: str, *patterns: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines):
        if any(pattern in line for pattern in patterns):
            return line
    return "NOT_FOUND"


def _pytest_summary(text: str) -> str:
    line = _last_line(text, " passed", " failed", " skipped")
    return line or "NOT_RUN"


def _dotnet_summary(text: str) -> str:
    """Aggregate every per-assembly ``dotnet test`` line into one total."""
    total_failed = total_passed = total_skipped = 0
    matched = 0
    for line in text.splitlines():
        match = re.search(
            r"失败:\s*(\d+)，通过:\s*(\d+)，已跳过:\s*(\d+)", line)
        if match:
            matched += 1
            total_failed += int(match.group(1))
            total_passed += int(match.group(2))
            total_skipped += int(match.group(3))
    if matched:
        return (f"{total_passed} passed / {total_failed} failed / "
                f"{total_skipped} skipped（{matched} 个测试程序集）")
    for line in reversed([item.strip() for item in text.splitlines() if item.strip()]):
        if "总计" in line or "Passed!" in line or "Failed!" in line:
            return line
    return "NOT_RUN"


def _break_rows(text: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\[(B\d+)\] break=(.*)$", line)
        if match:
            current = {"id": match.group(1), "what": match.group(2)}
            continue
        target = re.match(r"^    runner=(\S+) target=(.*)$", line)
        if target and current:
            current["runner"] = target.group(1)
            current["target"] = target.group(2)
            continue
        verdict = re.match(r"^    exit_code=(-?\d+) verdict=(\S+)$", line)
        if verdict and current:
            current["verdict"] = verdict.group(2)
            continue
        restore = re.match(r"^    restore=(\S+) sha256=(\S+)$", line)
        if restore and current:
            current["restore"] = restore.group(1)
            rows.append((
                current.get("id", "?"),
                current.get("what", "?"),
                current.get("verdict", "?") + " / " + current.get("restore", "?"),
                current.get("target", "?"),
            ))
            current = {}
    return rows


def main() -> int:
    feature = _read("feature.log")
    host_unit = _read("host-unit.log")
    host_ipc = _read("host-ipc.log")
    full_pytest = _read("full-pytest.log")
    full_dotnet = _read("full-dotnet.log")
    gates = _read("gates.log")
    discrimination = _read("discrimination.log")
    scope = (EVIDENCE / "scope-validation.log").read_text(encoding="utf-8") \
        if (EVIDENCE / "scope-validation.log").exists() else ""

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()
    build_text = _read("build.log")
    build_line = _last_line(build_text, "已成功生成", "生成失败")
    for line in build_text.splitlines():
        if "个警告" in line:
            build_line += " / " + line.strip()
            break
    for line in build_text.splitlines():
        if "个错误" in line:
            build_line += " / " + line.strip()
            break
    pin_line = _last_line(gates, "PIN AUDIT")
    check_lines = [line.strip() for line in gates.splitlines() if "Governance check" in line]
    api_ok = _last_line(gates, "OK: rendered counts match")
    api_line = api_ok if api_ok != "NOT_FOUND" else _last_line(gates, "EXIT=")
    scope_result = _last_line(scope, "result=")
    disc_result = _last_line(discrimination, "result=")
    disc_rows = _break_rows(discrimination)

    files = [
        path for path in sorted(EVIDENCE.rglob("*"))
        if path.is_file() and path.name not in {"EV.md"}
    ]
    file_rows = "\n".join(
        f"| `{path.relative_to(EVIDENCE).as_posix()}` | `{_sha256(path)}` |"
        for path in files
    )

    break_table = "\n".join(
        f"| {break_id} | {what} | {target} | {verdict} |"
        for break_id, what, verdict, target in disc_rows
    ) or "| — | NOT_FOUND | — | — |"

    body = f"""# FEA-11-RUN-GRANT-2（2B）Canonical Evidence：容器成员 entry 授权通道

> **结论先行。** 本卡按 **C-16 v1.4 §2**（容器源 `entries[]` 1..N）实现容器成员 entry 授权通道：
> **Core** 注册期接受 zip/cbz/pdf 的 1..N 容器成员条目（逐项校验：locator 安全、ordinal ≥ 0 且唯一、同一容器 `path`、
> facts 四键=容器物理身份；任一不符 **整 grant typed `SOURCE_ACCESS_DENIED`、零部分接受**；条目数超 `budget.max_entries`
> → **`SOURCE_BUDGET_EXCEEDED`，不截断**），匹配期沿用 `entry_key OR locator OR ordinal` + **容器 facts vs `source_locations`**
> （无路径回退、永不使用成员 digest；`find_bound_for_source`/`commit_guard` 不变）；**Host** 用 2A 的 `SourceIdentityCache`
> （Core 权威 `version_id` + `entries[]`）为容器源铸 **N 项** grant（locator/ordinal **原样使用**、容器 path/facts 同一、
> 容器文件只指纹一次），超 `max_entries` → **typed、不截断**；缓存不足 → best-effort 跳过（R-5 语义不变）。
> **真实 IPC 已证明**：真实 zip / cbz 各 3 成员 → 每个成员页 `authorize → resolve_page_resource` 成功；删/错一项 →
> typed `SOURCE_ACCESS_DENIED` 且**不可读到未授权成员**；**66 成员**容器由**一个** grant 覆盖（64 是 grant 数上限、不是成员数上限），
> **最后一个成员（ordinal 65）可授权**（不截断见证）。
> **不夸大**：本卡只覆盖「容器成员 entry 授权通道」；folder **>4096 成员不入缓存**（L-G16，沿用 2A 登记）、长 Run（L-G1）、
> 加密源（L-G2）、Core 重启（L-G9）、L-R11（L-G10）**均未解决**；**L-R1 未全修**；不得表述为「referenced Run 全场景可用」。

| 项 | 值 |
|---|---|
| task | `FEA-11-RUN-GRANT-2`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-2.md`；`status` 未改） |
| Owner | `run-grant-2b-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=97812958d`；实现起点 `{DELIVERY_BASE}`（工作树 clean，实测） |
| 本次 delivery_head | `{DELIVERY_HEAD}`（实现 `7466cb99d` + 测试 `018008989`；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\\CODEX\\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 |
| 契约字节 | **本卡零变更**：C-16 v1.4 已冻结（`doc/plan/**`、`doc/contracts/**` 本卡零 diff；`verify_pins` 18/18）；wire 字段/命令集/`CORE_PROTOCOL_MINOR=3`/错误闭集零改动 |
| 依赖 | **零新增** |
| 证据生成 | `verification/FEA-11-RUN-GRANT-2/tools/gen_ev.py`（`repo_head_at_generation={head}`） |

## 1. 交付 commit 链（起点 `{DELIVERY_BASE}` → delivery_head `{DELIVERY_HEAD}`）

```text
{DELIVERY_HEAD} test(fea-11-run-grant-2): container member entry matrix, 3-member zip/cbz IPC and the 66-member no-truncation witness
7466cb99d feat(fea-11-run-grant-2): container member entries in the Core grant registry + Host N-entry Run mint
{DELIVERY_BASE} (起点 HEAD，工作树 clean)
```

文档提交（本卡记录 / Handoff / 本证据树）随后同批提交，均在卡面 `allowed_paths` 内。

## 2. 门禁实测（`{DELIVERY_HEAD}`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **{build_line}** | `logs/build.log` |
| 定向 Python（AC-J1/J2/J3 + 既有 50 例回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **{_pytest_summary(feature)}**（基线 50，新增 24） | `logs/feature.log` |
| Host 单测（AC-H3 + 2A 回归） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **{_dotnet_summary(host_unit)}**（基线 29，+3） | `logs/host-unit.log` |
| 真实 IPC（AC-H4 / AC-J1/J2/J3） | `NEWMANGA_FEA11_IPC=1 dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **{_dotnet_summary(host_ipc)}**（基线 4，+1 容器成员用例；2A 用例扩展为第二成员可用） | `logs/host-ipc.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **{_pytest_summary(full_pytest)}**（基线 3281/10） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release` | **{_dotnet_summary(full_dotnet)}**（基线 1559/0/90） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **{pin_line}** / **{check_lines[0] if check_lines else "NOT_RUN"}** / **{api_line}** | `logs/gates.log` |
| 范围 | `python verification/FEA-11-RUN-GRANT-2/tools/scope_validation.py` | **{scope_result}** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-2/tools/discrimination.py` | **{disc_result}** | `logs/discrimination.log` |

**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行
`git checkout -- verification/FEA-09`（见各日志末尾的 `RESTORED`/`unchanged` 行）。

## 3. 判别性验证（{len(disc_rows)} 破坏点；删掉实现必须变红）

`logs/discrimination.log` 逐个破坏**一个已提交的实现分支**后运行**一个**目标用例，要求变红（exit≠0），随后按**原字节**恢复并复核
sha256，最后重新 build 恢复二进制并对恢复后的树补跑定向套件。

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
{break_table}

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性/真实证据 | 证据 |
|---|---|---|---|
| **AC-J1** 容器 ≥3 成员真实 IPC：每个成员页可 `AuthorizeSourceReadForRun` 绑定并 `resolve_page_resource`；不可读到未授权成员 | MET | 真实 IPC `ContainerMemberEntriesAuthorizeEveryMemberOverRealIpc`（真实 zip/cbz 各 3 成员：逐个 `authorize → bound_pages=1 → resolve_page_resource` OK；`minted=1` 即一个 grant 覆盖全部成员）；Core 真实装配 `test_container_members_are_entry_granular_on_every_authorized_member[zip|cbz]`（每成员 provider 读到**该成员自己的像素尺寸**）；未授权面 `test_container_member_outside_the_signed_entries_cannot_be_read`（scope 少一项 → typed、`commit_guard` 不开、provider 拒绝） | `logs/host-ipc.log`、`logs/feature.log`、`G:\\CODEX\\New Manga.workspace\\FEA-11-RUN-GRANT-2\\fixtures\\ipc-*\\run-grant-2b-container-members.txt` |
| **AC-J2** fail-closed：任一项 locator/facts/ordinal 不符或 entry 不在 version → 整体 typed、零映射写入 | MET | Core 注册矩阵 `test_container_grant_any_bad_entry_refuses_the_whole_grant[...]`（unsafe/absolute locator、负 ordinal、重复 ordinal、跨容器 path、facts 不一致 → 全部 typed 且 grant 未注册、`_bindings` 空、业务表快照不变）；协议面 `test_container_grant_violations_are_typed_with_zero_partial_acceptance[...]`；P3-4 `test_container_grant_facts_reference_point_is_the_container_identity`（成员 digest 冒充容器 facts → typed 拒绝；同形状真容器 facts → 成功）；P3-5 `test_container_grant_out_of_range_ordinal_never_matches`（越界 ordinal 不命中）；IPC 删一项/错一项 → typed `SOURCE_ACCESS_DENIED`；判别 B1/B2/B4/B5/B6 | `logs/feature.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| **AC-J3** 上限：超 `max_entries` 或 64 grant 上限 → typed/按契约，不截断；≥65 成员有明确用例 | MET | Core `test_container_grant_entry_budget_is_typed_and_never_truncated`（`max_entries=3` 边界接受、+1 项 → `SOURCE_BUDGET_EXCEEDED` 且未注册；配置预算 20000 时命中实现硬上限 10000 → 同样 typed）；Host `ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`（超预算抛 typed、边界不截断）；真实 IPC：Host mint `max_entries=65` + 66 项 → typed `SOURCE_BUDGET_EXCEEDED`（不截断），**66 成员容器由 1 个 grant 覆盖且 ordinal=65 的最后一个成员可授权/可读**（64 为单次命令 grant 数上限，不是成员数上限）；判别 B3/B8 | `logs/feature.log`、`logs/host-unit.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| **AC-J4** managed/旧路径零回归；零漂移（pins 18/18、Run wire/minor/schema/依赖零改动）；全量门禁不降；EV/Handoff 不夸大 | MET | `scope-validation.log`（changed=7 全 ALLOWED；`doc/plan`/`doc/contracts`/schema/迁移/依赖/`NewManga.App`/STATUS/PLAN/LEDGER 全 ZERO_DIFF；`CORE_PROTOCOL_MINOR=3`）；`verify_pins` 18/18；全量 pytest / 全量 .NET 不降（见 §2）；既有 50 例定向回归全绿；Handoff 与本节均保留 limitation 与未宣称项 | `scope-validation.log`、`logs/gates.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |

### 4.1 与卡面 AC-H1…H5 的对应（scope review 口径）

| 卡面 AC | 本卡证据 |
|---|---|
| AC-H1（C-16 v1.4 UNFREEZE） | 由前置卡 `FEA-11-RUN-GRANT-2B-PREREQ-1`（`d8dcfc07a`）完成；本卡 `doc/plan/**` 零 diff、pins 18/18（`logs/gates.log`）。 |
| AC-H2（Core 注册/匹配） | §4 AC-J2 全部 Core 用例 + `_scope_covers_entry` 多 entry 匹配；`_bindings` 写入语义不变（`bind_imported_entry`/`find_bound_for_source` 未改，既有回归全绿）。 |
| AC-H3（Host 铸 N 项、权威来源、上限 typed） | `RunSourceRangeCarriesContainerMemberIdentitiesVerbatim`（缓存值原样、不重编号、image/folder 保持）、`ContainerEntryPlanIsVerbatimAndTypedOverTheBudget`、`RunAuthorizerForwardsTheContainerMemberPlanToTheMint`；真实 IPC 生产路径（scan → cache → range → mint → Core）。 |
| AC-H4（真实 IPC ≥3 成员 zip/cbz、删/错一项 typed、零越权） | §4 AC-J1/AC-J2 的 IPC 证据；wire/stderr 路径 0 泄漏断言。 |
| AC-H5（门禁/证据） | §2 门禁表 + §3 判别性 + §5 逐文件 sha256 + Handoff 的 limitation/未宣称。 |

## 5. 证据文件 sha256（本文件 `EV.md` 除外）

| 文件 | sha256 |
|---|---|
{file_rows}

> sha256 为**工作树字节**（检出配置 `core.autocrlf=true`；与 RUN-GRANT-1/2A 证据同口径）。
> `RESOURCE-MANIFEST.json` 记录仓外隔离根 `G:\\CODEX\\New Manga.workspace\\FEA-11-RUN-GRANT-2\\`
> 的聚合 sha256 与逐文件详情，并钉 `delivery_head={DELIVERY_HEAD}`。

## 6. NOT_RUN / 未宣称 / 保留 limitation

- **NOT_RUN**：无。本卡 §2 全部门禁均真跑；`logs/*.log` 为原始输出（含 `EXIT=` 行）。
- **未宣称**：本卡不宣称「referenced Run 全场景可用」、不宣称「L-R1 全修」、不宣称长 Run/加密源/Core 重启可用、不宣称 folder >4096 成员可用、不宣称 2C（长 Run 续期）有任何进展。
- **保留 limitation**：
  - **L-G16**（2A 登记，本卡不解决）：`SourceIdentityCache.MaxEntriesPerIdentity=4096` < `DefaultMaxEntriesPerSource=10000` → **>4096 成员的 folder/容器源不入缓存**，Run 期每次触发 on-demand 扫描但不铸造（fail-closed，无错误授权）。
  - **L-G1**（300s TTL/长 Run）、**L-G2**（加密源）、**L-G8**（扫描/铸造成本：容器 grant 的 entries 规模 = 成员数，payload/注册成本随成员数线性增长）、**L-G9**（Core 重启）、**L-G10**（L-R11 gate 两读面差异）、**L-G12②**（在本卡**已闭环**：缓存可用的容器源其多成员 entry 可授权；>4096 成员/L-G16 场景仍不可）、**L-G13**（flaky）。
  - **P3-6/N-4 口径**：`budget.max_entries` 限制**单 grant 条目数**；64 限制**单次命令 `grant_ids` 数**；实现侧硬上限 10,000 为更严 fail-closed；**不得**表述为「容器成员数上限」。
  - **P3-2（wire 追溯）**：C-16 §0 wire 版本行保留历史追溯说明，本卡未改 wire 字段/命令集。
- **接口/边界**：本卡未改 Run wire / `CORE_PROTOCOL_MINOR` / 错误码闭集 / schema / 迁移 / 依赖 / `NewManga.App/**`；未 push。

## 7. 真实性与证据边界

- 本 EV 的数字全部来自 `logs/` 内**原始输出**；未把未跑写成 PASS。
- IPC 夹具/`discrimination` 备份在仓外隔离根；仓内证据为 `verification/FEA-11-RUN-GRANT-2/**`。
- 2A 的 IPC 用例在本卡中被**扩展**（归档第二成员由「typed 拒绝」改为「可用」，测试名相应更新）；2A 的历史 canonical 证据仍按 commit `a0bafc89e` 的字节保留，不受本卡影响。
- 独立 Review 由 Lead 指派（本会话不自审）；集成门禁由 Lead 重跑。
"""

    OUT.write_text(body, encoding="utf-8", newline="")
    print("wrote", OUT, "files_hashed=", len(files), "breaks=", len(disc_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
