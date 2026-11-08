"""FEA-07-RESIDUAL-3（R4b）append-only 回填：只改 AC1/AC3/AC4 三行状态与文末追加登记节。

- AC1/AC3/AC4：`- [ ]` -> `- [x]`，并在行尾追加 `<<MET>>` 回填段（不带原因，按 R4a 模式）。
- AC5（唯一 NA 登记）/ AC7 / 历史 Review 链 / Canonical Evidence 表：字节不动。
- 文末追加 `## FEA-07-RESIDUAL-3（R4b）回填登记（2026-11-08，append-only）` 一节。
"""
from __future__ import annotations

import sys
from pathlib import Path

TASK = Path(sys.argv[1])

AC_BACKFILL = {
    "**AC1（A01/A02/A03/A05/§15.5）**": (
        " **R4b 回填（2026-11-08，FEA-07-RESIDUAL-3）**：`<<MET>>` — gated 真实 Host/Core（默认 skip + "
        "reason）：50 次前端往返（= 100 次生产切换事务）前后真实 `library.db` 逐列相同（`regions.text_json` / "
        "`current_revision_id` / `region_locked`+`translation_locked`+`inpaint_locked` / `sfx_policy='manual'` / "
        "`region_revisions` 行数 / 候选存量；读库走既有 .NET 内嵌 Python 先例，**零新增 SQLite 依赖**）；ACK 丢失 + "
        "同 idempotency key 重连经生产 dispatcher（`HostCommandDispatcher` + `CurrentRunIntentCoordinator`）只产生 "
        "**1** 个 run（同 `run_id`）；旧结果仅 candidate。原生 IME 仍 NA（唯一登记在 AC5 行）。<<MET>>"
    ),
    "**AC3（A06）**": (
        " **R4b 回填（2026-11-08，FEA-07-RESIDUAL-3）**：`<<MET>>` — 外部驱动 `verification/"
        "FEA-07-RESIDUAL-3/tools/crash-switch.ps1` 三阶段（park → `Process.Kill(entireProcessTree:true)` → "
        "新进程 recover），真死由心跳冻结证明；终态 journal `RolledBack`、frontend 回到上一已提交、"
        "`appearance.FrontendId` 未被 target 污染、二次恢复零变化；「暂停期保护状态」两断言 = 切换零写保护列"
        "（内嵌 Python 逐列比对）+ 恢复采用暂停期最新状态、不回写旧快照；**无** `Environment.FailFast`、"
        "**无**同进程冒充、**无**生产 backdoor。<<MET>>"
    ),
    "**AC4（A07）**": (
        " **R4b 回填（2026-11-08，FEA-07-RESIDUAL-3）**：`<<MET>>` — 新增最小 `StartupDiagnostics` sink"
        "（`App/Services/StartupDiagnostics.cs`：`<log-dir>/startup.log` + `Trace` 兼容 + 永不抛；"
        "`App.axaml.cs` **2 行**接线）；真实进程 4 组参数（默认 / `--presentation-host=true` / `--shell=legacy` / "
        "坏外观文档）→ `exit_code=0`、无 `fatal.log`、`startup.log` 含对应诊断行；9 类 warning 逐项 fail-safe 到 "
        "Current V2。<<MET>>"
    ),
}

APPEND = """
## FEA-07-RESIDUAL-3（R4b）回填登记（2026-11-08，append-only）

> 来源卡 `doc/tasks/FEA-07-RESIDUAL-3.md`（0 pin、gated/进程级；base `8855baaac`，证据 `verification/FEA-07-RESIDUAL-3/`，scope 依据 `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md` §3/§4/§5.2）。本节只**追加**：不改上方历史字节（含 2026-11-02 的 Residual / Closeout Record 与 R4a 回填节），不覆盖、不重写。

| AC | before | after | 依据与证据 |
|---|---|---|---|
| AC1（A03 真库 + ACK/Intent） | `- [ ]` + `<<PARTIAL: …A03 真库 DB/current/pinned/Lock 矩阵、ACK 重连与真实 Run/Intent 链路不可测，保持 PARTIAL>>` | `- [x] … <<MET>>`（gated 真实 Host/Core；原生 IME 仍 NA，唯一登记在 AC5 行） | `tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs`（`NEWMANGA_FEA07_A03=1`，默认 skip + reason）：50 次往返 = 100 次生产切换事务；`regions.text_json`/`current_revision_id`/三锁/`manual`/`region_revisions` 行数/候选存量逐列相同（内嵌 Python 读库）；ACK 丢失后同 key 重连 → `pipeline_runs` +1、同一 `run_id`、候选零解析 |
| AC3（A06 跨进程崩溃） | `- [ ]` + `<<PARTIAL: …暂停期间保护状态变化与真实跨进程崩溃注入待补>>` | `- [x] … <<MET>>`（跨进程 park/kill/recover；暂停期保护状态两断言） | `tests/NewManga.App.Tests/Fea07Residual3CrashTests.cs`（`NEWMANGA_FEA07_CRASH=1` + phase 门禁）+ `verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1`（exit code 0/10/11/12/2 语义）；`evidence/crash-switch-r4b.json` |
| AC4（A07 真实入口 + 诊断 sink + 矩阵） | `- [ ]` + `<<PARTIAL: …真实 App 初始化入口与坏包/scale 矩阵待补（r4 维持 PARTIAL）>>` | `- [x] … <<MET>>`（`StartupDiagnostics` 落盘 + 4 组真实进程 + 9 类 warning 逐项 fail-safe） | `src/NewManga.App/Services/StartupDiagnostics.cs`（+ `App.axaml.cs` 2 行接线）、`tests/NewManga.App.Tests/StartupDiagnosticsTests.cs`（`NEWMANGA_FEA07_STARTUP_PROCESS=1` 真实进程门禁）、`verification/FEA-07-RESIDUAL-3/tools/startup-matrix.ps1`、`evidence/startup-matrix-r4b.json` |
| AC5 / AC1-IME / AC2-双屏（NA 三条） | AC5 行唯一 `NOT_APPLICABLE` 登记（2026-11-08 R4a） | **未变更**（零字节改动；保留 `NOT_RUN`，不写成 PASS） | 用户 2026-11-08 授权豁免；`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §7.10 |

- 未变更：AC7 保持 `<<MET>>`；上方 r1–r12 Review 链、Canonical Evidence 表与 `verification/FEA-07/**` 字节不动；`doc/plan/**`、`doc/contracts/**`、18 pins 零 diff（0 pin）。
- 口径：本节不写「FEA-07 完全实现 / AC5 达成 / 生产双屏可用」；只写「AC1/AC3/AC4 达成（gated/进程级）；AC5 与原生项 NA（`NOT_RUN`）；AC2/AC6/AC8 见 R4a」。`skip` 与 `NOT_RUN` 都不写成 PASS。
- 证据强度边界（如实登记）：(a) 冻结卡列的 `region_candidates` 表在冻结 schema 中不存在，候选 store = `step_result_candidates[_v5]`（V5 迁移改名），故「旧结果仅 candidate」断言为「候选存量 0 → 0、零解析、陈旧 base 未进入 `current_revision_id`」；(b) AC1 的 50 次往返在 Host 侧驱动生产切换事务（journal + 唯一写者），UI 侧 layout/Loaded/render 门禁由既有 headless 用例覆盖；(c) AC4 真实进程矩阵需要交互桌面会话，无会话时 gated fact skip + reason（本次有会话，实跑 4/4）。
- 测试基线（本卡执行）：Host **302/0/72**（基线 302/0/71，+1 gated skip）、App **828/0/11**（基线 816/0/8，+12 passed、+3 gated skip）、全量 sln **1791/0/107**（基线 1779/0/103，0 failed）、pytest **3395 passed / 0 failed / 10 skipped**（基线 3394/1 既有 flaky/10；本轮既有 flaky 未复现，零 Python diff）；gated 实跑：AC1 1/1、AC3 `crash-switch.ps1` exit 0、AC4 真实进程 4/4 + gated fact 1/1；变异自检 **4** 组 RED → sha256 MATCH → 复绿（明细 `verification/FEA-07-RESIDUAL-3/mutation-selfcheck.md`）。
- **r1 返修（2026-11-08，独立 Review r1 approved P0=0/P1=0，但 DSH 把 P2-01 升格为 P1）**：红线「不得触碰真实用户数据/AppData」——`--shell=legacy` 的 `window-material.log` 曾硬编码真实 `%APPDATA%`（`MainWindow.WriteMaterialDiagnostics`）。DSH 裁决 A（授权扩域该单文件）：改为「显式 `--log-dir` 拥有全部日志文件（含本文件），无 `--log-dir` 保留历史每用户位置」，diff **+5/−1**（3 语义行 + 2 理由注释）。测试/脚本侧再注入隔离 `APPDATA`/`LOCALAPPDATA`/`USERPROFILE` 并回读子进程值；红线断言 = 真实 `%APPDATA%` 行数 **14275 → 14275（delta=0）**（gated fact 14/14 与 `startup-matrix.ps1` 4/4 各一次）。变异 M4/M4b（回退产品契约 / 再回退 env 隔离 = r0 现场）→ 用例 RED 且真实日志 `+1` 行（主动实验所致，不删除，其后基线 14276 且 delta=0）。同批 P2-03（AC3「暂停期采用最新状态」改为真实 `library.db` 的 `current_revision_id` + `inpaint_locked`，不再只改 appearance `Mode`）、P3-01（`sfx_locked` → `region_locked` erratum）、P3-02（本节数字与实际一致）、P3-03（`ResetForTests` 还原 `Trace.AutoFlush`）、P3-05（崩溃证据 JSON 增 `testhostGone=true`）。
"""


def main() -> int:
    text = TASK.read_text(encoding="utf-8")
    lines = text.split("\n")
    flipped = []
    for index, line in enumerate(lines):
        # 幂等：既可以是待翻转的 `- [ ]`，也可以已经是 `- [x]`（重跑不报错）。
        if not (line.startswith("- [ ] ") or line.startswith("- [x] ")):
            continue
        for anchor, addition in AC_BACKFILL.items():
            if anchor not in line:
                continue
            if line.startswith("- [ ] "):
                lines[index] = line.replace("- [ ] ", "- [x] ", 1) + addition
                flipped.append(anchor)
            else:
                flipped.append(anchor)  # already flipped by an earlier run
    missing = [anchor for anchor in AC_BACKFILL if anchor not in flipped]
    if missing:
        print("MISSING AC ANCHORS: " + ", ".join(missing))
        return 1
    updated = "\n".join(lines)
    if "## FEA-07-RESIDUAL-3（R4b）回填登记（2026-11-08，append-only）" not in updated:
        updated = updated.rstrip("\n") + "\n" + APPEND
    TASK.write_text(updated, encoding="utf-8", newline="\n")
    print("satisfied=" + str(len(flipped)) + " appended=" + str(updated != text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
