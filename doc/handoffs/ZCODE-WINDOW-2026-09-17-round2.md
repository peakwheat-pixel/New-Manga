---
kind: window-round2-brief
recipient: ZCode
from: Codex（Lead/Integrator）
issued: 2026-09-18（窗口 T1=08:50 之前）
base: 047164ea080651741b38b20a36470115d4830a0d
status: active
---

# ZCode 窗口第二轮指令包（2026-09-18，T1=08:50 前）

> 第一轮 W1–W4 + 插队项 TASK-023 已全部 `done`，Codex 已核验（见 [STATUS](../STATUS.md) 2026-09-18 台账行）。**窗口规则完全不变**（Review 只能 `approved_subagent`；不得新增 `skip`/`xfail`；不得放宽/删除断言；08:20 后不得开新切片；08:50 冻结）。

## 队列与时间门

| # | 切片 | 类型 | 门 |
|---|---|---|---|
| **W5** | [TASK-038](TASK-038.md) 生产装配收口（reader/export/文档导入） | **最高优先，必做** | 立即开始 |
| **W6** | [TASK-039](TASK-039.md) planner `_clean_available` 继承缺陷（P2） | 必做 | W5 集成后立即开始 |
| **W7** | [TASK-021](TASK-021.md) 备份恢复/回收站/清理/诊断 | **条件** | **仅当 W5+W6 于 06:30 前集成**；只交付**一个自洽子集**并 08:20 前集成 |
| — | MOBI 依赖、超大 webtoon 像素解码 | **不要动** | 待用户裁决（已登记） |

**时间门**：06:30 W7 启动门 → 08:20 停止启动新切片 → 08:50 冻结 + 授权失效。

## 起点与流程

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
cd 'G:\CODEX\New Manga.worktrees\TASK-038-zcode'   # 依次 038 → 039 → 021
git merge master                                    # 每个切片开工前先合入 master
```

- worktree/分支已由 Codex 建好（见各 Task 顶部元数据）；**不要**在主工作区 `G:/CODEX/New Manga` 直接改文件。
- 每个切片：置 `in_progress` → 实施 → 取证 → 子 agent Review（Review 模板、passed/skipped 分列）→ 修订 → `merge --no-ff` 集成 → Task/STATUS 收口。

## W5（TASK-038）要点

1. **这是接线切片，价值最高**：`src/bootstrap/app.py::assemble_engine` 目前只注册 `navigationViewModel`/`bookshelfViewModel`/`workbenchViewModel`；reader 与 export 的 ViewModel **从未注册** → 生产阅读器是惰性空态页，TASK-020 的分块阅读与 TASK-023 的文档导入在生产**都不可达**。
2. AC ① 要求**更新而非删除** `tests/reading_export/test_qml_contract.py:224` 那条以"生产装配尚未注入 readerViewModel"为前提的用例——前提变了，用例跟着变，并在 Handoff 说明。
3. export 有两条交付路径（reader 发起经 `readerViewModel.exportController`；独立导出窗口另注入）→ **注册名与对应关系必须在 Handoff 写清**并用测试锁定，避免"注册了但用不到"。
4. AC ⑤ 补**装配契约测试**（断言生产 engine 注册了全部所需 context property；现有 `tests/core/test_bootstrap.py:299` 只断言了 `workbenchViewModel`）。
5. 接上 reader 后若暴露白名单外缺陷 → **留证 + 回抛 Codex**，不得自行扩范围。

## W6（TASK-039）要点

- 承接 TASK-033 的 **R-001（P2）**：`_clean_available` 看的是**无人写入的 `clean` stage**，导致 render-only 命令跨 run 仍 `BLOCKED(missing_clean_artifact)`。
- **AC ③ 的对照矩阵必做**：该函数同时服务 `REINPAINT_*` 等命令族，改动不得外溢。
- 完成后在 TASK-033 Handoff 或 STATUS 记录"R-001 已关闭"。

## W7（TASK-021）要点（条件启动）

- 4 个 AC 覆盖面很大：**只选一个自洽子集**（建议从"软删除 + 同 batch 恢复"开始），**完整做完并集成**，不要留多个半成品。
- **Schema/migration 变更属窗口排除项 → 必须先回抛**。
- 窗口结束时未开始的子集原样留在 Task 中；未完成的子集在窗口报告里如实登记 `frozen`。

## 证据纪律（本轮新增）

- **同一 shell + 同一 venv**（建议 PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`），并在证据里写明所用 shell。上一轮报告把 PowerShell 的 `737/6` 与另一 shell 的 `764/0`（该 shell 下 openssl 可用）并排当作基线增量，容易被误读成"skip 被消除"——不要重复。
- 每条命令记退出码 + passed/skipped 分列；失败一律 `-rf` 记用例名。
- 基线（PowerShell 实测，`047164e`）：全仓 **764 passed / 6 skipped**。

## 收尾

T1（08:50）前更新 [窗口报告](../verification/ZCODE-WINDOW-2026-09-17/window-report.md)：追加第二轮各切片状态、`integration_commit`、`approved_subagent` 清单（供 Codex/DSH post-hoc 复审）、未完成项与冻结原因、环境变化。**08:50 后不得再实施或集成。**
