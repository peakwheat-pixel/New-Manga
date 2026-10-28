# IMPORT-TRIAGE-1 交付报告：REPACK-5 导入 BLOCKED 诊断

> **结论：不是 HEAD 代码回归，也不是数据根/catalog 缺陷。** 全新空数据根 + 全新 fixture + REPACK-5 安装包，真实 UI 导入成功（`RegisterImportSource` → **`ImportPages`**，16–18ms；DB pages 8→9）。用**与烟测完全相同的输入文件**（`ui-import-2.png`，sha256 `e1b6787b…`，134 B）重跑也成功。烟测 BLOCKED 属烟测脚本/安装环境产物，无需修复产品代码。

- Task: `doc/tasks/IMPORT-TRIAGE-1.md`（team task-58）；Owner `route-research`；Reviewer `dsh`
- Branch: `task/IMPORT-TRIAGE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/IMPORT-TRIAGE-1`；Base `441b7b57a`
- 结论：diagnosis；未改产品源码；未 push。

## AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 干净根复测 | **MET** | `task-envs/IMPORT-TRIAGE-1/ac1-root`（`new-test-book.ps1` 全新生成，8 页） + REPACK-5 `out/...-models/app` 真机 UI 导入：① 重复文件 → `RegisterImportSource`@01:16:58.608 + `ImportPages`@01:16:58.626，UI「已导入 0 个文件，跳过 1 个重复」；② **烟测同文件** `triage-tiny-134.png`（sha `e1b6787b…`，134 B）→ Register@01:21:10.930 + `ImportPages`@01:21:10.946，UI「已导入 1 个文件」，pages **8→9**（新页 `triage-tiny-134.png`）。 |
| AC2 判定 | **MET（干净根成功）** | 同一 REPACK-5 包、全新空数据根真实 UI 导入成功 ⇒ **非 HEAD 回归**；且非数据根/catalog 状态导致（根是全新生成，非 REPACK-4 副本）。烟测 BLOCKED 未复现。 |
| AC3 二分 | **N/A** | 仅回归时执行；本卡 AC2 已判定非回归。 |
| AC4 修复/隔离 | **N/A（无回归，无需修复）** | 未改产品代码；给出烟测脚本硬化建议（见 §4）。 |
| AC5 门禁 | **N/A（无代码改动）** | 仅新增 verification 证据与文档；`check.ps1 -TaskPath` PASS；64-hex pin。 |

## 1. AC1 现场与 wire

- 数据根：`G:/CODEX/New Manga.workspace/task-envs/IMPORT-TRIAGE-1/ac1-root`（`new-test-book.ps1` 全新创建，BOOK-FIXTURE 8 页；证据 `evidence/ac1-fixture.json`）。
- 包：`task-envs/RELEASE-REPACK-5/out/NewManga-0.1.0-win-x64-models/app`（`NewManga.App.exe` sha256 `b81ce6ef15871f1c6a3484e8db17c4b5098bba14efdb1b346b1d1956e7c3cdcf`），sidecar 指向该包 `app/core-sidecar`，`--parity`，私有 `--log-dir`。
- 真实 UI：书架 →「导入文件」→ 系统选择器（新 fixture 路径）→ 面板（目标书/章/重复策略默认已选）→「开始导入」→ 结果行。
- wire（`evidence/logs/core-service.wire.ndjson`，复制自该次会话）：
  - `hostctl-14 RegisterImportSource @01:16:58.608` → `req-15 ImportPages @01:16:58.626`（+18 ms）→ 重复跳过；
  - `hostctl-23 RegisterImportSource @01:21:10.930` → `req-24 ImportPages @01:21:10.946`（+16 ms）→ 导入 1；
  - 两次均无 Revoke，grant 证据落 `evidence/grants/import-*.json`。
- 截图：`evidence/screens/01-bookshelf.png`（8 页）、`03-import-panel.png`（面板三选择器可用）、`04-import-result.png`（跳过 1 重复）、`06-tiny-result.png`（已导入 1，书架 9 页）。

## 2. 与烟测证据对照（Lead 解析的 `import-wire-tail.ndjson`）

烟测 wire：`RegisterImportSource` 携带 `source_path=…\IMPORT-EXPORT-UI-1\import-src\ui-import-2.png`、`size=134`、`sha256=e1b6787b…`、`expires_at=1793149393`（注册后 **299 s**，未过期）；**同一秒即 `RevokeImportSource`**，随后 34 s 无命令。说明：grant 有效、未过期；客户端在 `ImportPages` 之前主动 revoke → 烟测 UI 自动化流程中途放弃/确认步骤未真正完成，而非 Core 拒绝或产品回归。本次用同 sha 输入在干净根实测成功，直接否定了「输入文件/数据根/HEAD 回归」三种假设。

## 3. 为什么不是回归

- 产品导入代码（`ImportExportPanels` / `HostController` / `HostGrantCoordinator`）与 REPACK-4 无 diff（卡面已记录），且本次同一 REPACK-5 二进制真实导入成功；
- 干净根、全新 fixture、烟测同文件全部成功；
- 烟测失败签名（Register 后立即 Revoke、无 `ImportPages`、`REF_MALFORMED` 记录）在本地无法复现；REPACK-5 的 `install` 目录已被清理，安装包二进制混装无法再核验（证据不足，不作结论）。

## 4. 建议（不属本卡修复范围）

1. 烟测导入自动化：打开面板后显式断言 `ImportBookSelector`/`ImportChapterSelector`/`ImportPolicySelector` 存在且可用，点击 `ImportStartButton` 后断言行文本（`已导入 N 个文件`）与 DB pages 增量；不要只等待/截图。
2. 失败时保留 `grants/import-error-*.json` + wire tail（本次烟测只留下错误码，没有调用上下文）。
3. 烟测前校验安装目录 `app`/`app/core-sidecar` 哈希与 `out/` 包一致，避免混装旧包。

## 5. Record Decision

- 采用「干净根 + 真机 UI + wire 帧」作为判定依据；结论 **非回归、无需产品修复**。
- 不执行 `f1b89c5e5`→HEAD 二分（AC2 已成功，二分无必要）。
- 不改任何产品源码；仅入库复现证据与烟测硬化建议。
- AC5 条件（「修好时」）不适用；`check.ps1 -TaskPath` PASS，证据 64-hex pin。

## 6. 证据

见 Task 卡 Canonical Evidence 表；核心三份：`evidence/evidence.json`、`evidence/logs/core-service.wire.ndjson`、`evidence/screens/06-tiny-result.png`。
