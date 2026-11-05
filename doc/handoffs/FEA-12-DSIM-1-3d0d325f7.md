---
task_id: FEA-12-DSIM-1
author: dsh-agent-team teammate `fea12-dsim-impl`（Owner；未自审）
recipient: DeepSeek Harness（Lead / Architect / Integrator）
base_commit: 37f84bb895c9ef9b64e3865f3a92b245f2e28a7c
delivery_head: 3d0d325f7
status: in_review
---

# Handoff：FEA-12-DSIM-1（D 流程模拟切片：typed 原文件回收端口 + SimulatedRecycleBin + 隔离/哨兵测试）

## 交付结果

**范围（与冻结范围一致）**：只新增 D 流程模拟切片 —— application 层协议 + 生产 typed 不可用默认实现 + `SimulatedRecycleBin` 测试替身（只写隔离根、零 OS API）+ 隔离/失败注入/静态扫描/运行时哨兵测试 + 证据/Handoff。**不接 Host/UI、不改既有生产文件（`maintenance/__init__.py` 仅 additive 导出）、无 schema/依赖、不 push。**

**实现 commit（我的提交，均在 `main`，commit message 已标注卡号）**：

| commit | 内容 |
|---|---|
| `94a12e93f` | feat：`src/application/maintenance/recycle_gateway.py`（新增）、`src/infrastructure/filesystem/simulated_recycle_bin.py`（新增）、`src/application/maintenance/__init__.py`（additive 导出）、`tests/fea12/{conftest.py,test_recycle_gateway_sim.py}`（新增）——5 files / +1625 |
| `3d0d325f7` | fix：目录条目指纹改 `os.walk(followlinks=False)` 并拒绝 junction/symlink、路径比较 normcase、消失竞态报 `path_not_found`——1 file / +54/−18 |
| 本 Handoff 所在 docs commit | Task 卡（AC 标记/证据/资源清单）+ 本 Handoff + `verification/FEA-12-DSIM-1/**`（证据、日志、扫描/哨兵脚本） |

> 说明：`94a12e93f` 只含 4 个实现/测试文件 + 1 个 additive 导出文件，**不含** `verification/**`；本轮 evidence 与 docs 一起在 docs commit 提交。

**交付文件**（全部在卡 `allowed_paths` 内）：

- `src/application/maintenance/recycle_gateway.py`（新增，application 层，**不 import infrastructure**）：`OriginalFileRecycleGateway` 协议（`move_to_recyclebin(entries, *, journal)`，journal keyword-only 必填 = C-01b SC-34 seam）、逐项 typed 结果（`moved`/`failed`/`not_started` + 封闭 reason 词表，构造期拒绝未知码）、`RecycleAttempt`/`RecycleReceipt` journal 形状、`RecycleSafetyError`（"failed 必须等于原文件仍在"，无法回滚只能抛错）、生产默认 `UnavailableOriginalFileRecycleGateway`（typed 不可用、`operation_id=""`、零文件/journal/DB 操作）。
- `src/infrastructure/filesystem/simulated_recycle_bin.py`（新增，测试替身）：`SimulatedRecycleBin`（根校验拒绝文件系统根/不存在/非目录/`*recycle.bin`；条目路径 4 道包含检查；隔离根内 `os.replace` 逐项原子 + kind/size/SHA-256 复核 + 失败回滚；manifest 可审计；失败注入）、`JsonLinesRecycleJournal`（attempt→receipt，fsync 追加）、`RecycleBinEntry` manifest 视图。
- `src/application/maintenance/__init__.py`：仅 additive 导出（7 个新名字进 `__all__`）。
- `tests/fea12/conftest.py`、`tests/fea12/test_recycle_gateway_sim.py`（新增，13 tests，全部 `tmp_path` 隔离）。
- `doc/tasks/FEA-12-DSIM-1.md`（AC/测试表/证据/资源清单/边界声明）、本 Handoff、`verification/FEA-12-DSIM-1/**`。

**AC 对照**：AC1–AC5 全部 `<<MET>>`；逐项证据见 Task「测试要求」表与 `verification/FEA-12-DSIM-1/AC-MATRIX.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC4（行为） | `C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings --tb=no` | Python 3.14.6；`3d0d325f7` 工作树 | **PASS**：13 passed（EXIT 0） | `verification/FEA-12-DSIM-1/logs/pytest-fea12.log` |
| AC4（静态禁令） | `pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1` | 仓库根 | **PASS**：`src` 256 + `apps` 510 = **766 files / 0** Windows 回收站 API 命中；`tests/fea12` 2 files / **0** 真实路径字面量；2 个 D 模块 876 lines / **0** 删除/DB/进程回退（EXIT 0） | `logs/static-scan.log`、`ISOLATION-EVIDENCE.md` §3 |
| AC4（运行时哨兵） | `C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py` | `tempfile.TemporaryDirectory()` 隔离 scratch | **PASS**：三次运行（成功模拟 / 注入拒绝 / 生产默认）后，隔离根外哨兵树逐文件 SHA-256 不变、`outside changes: []`（EXIT 0） | `logs/sentinel-probe.log`、`ISOLATION-EVIDENCE.md` §4 |
| AC5（pytest 基线） | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no`（实施首日、clean tree `37f84bb89`） | 仓库根 | **PASS**：3073 passed / 10 skipped（EXIT 0） | `logs/baseline-pytest.log` |
| AC5（pytest 交付 head） | 同上（共享工作树 = `3d0d325f7` + 并发已提交 LINEAGE-1 r3 7 tests） | 仓库根 | **PASS**：3093 passed / 10 skipped in 276.43s（EXIT 0；+20 = 本卡 13 + LINEAGE-1 r3 7） | `logs/pytest-full.log` |
| AC5（.NET 首跑） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo` | .NET SDK 10.0.401；共享工作树（本卡未改 .NET） | **FAIL 1** / 670 passed / 7 skipped（`NewManga.App.Tests`）= `FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`；归因：该测试断言运行期间 `git status --porcelain -- verification` 不变，命中并发写入窗口（当时我的全量 pytest 正在写 `verification/FEA-12-DSIM-1/logs/`；另有既有 `WireLogSourceRedactionTests` 重写 `verification/FEA-09` 行为）。其余 7 个 assembly 全绿 | `logs/dotnet-full-1.log` |
| AC5（.NET 二次复跑） | 同上 | 同上 | **FAIL 1** / 670 passed / 7 skipped（同一测试）；断言差异实测：`Expected: "?? verification/FEA-12-DSIM-1/"` vs `Actual: …"? verification/FEA-11-LINEAGE-1/logs/gate…"` —— 并发 teammate（lineage-impl）在运行期间写入 `verification/FEA-11-LINEAGE-1/logs/**`，命中同一 git-status 断言窗口 | `logs/dotnet-full-2.log` |
| AC5（.NET 稳定树复跑） | 同上 | 工作树仅剩本卡 untracked evidence；无并发写入 | **PASS**：失败 0 / 通过 1403 / 跳过 79（8 assemblies，EXIT 0） | `logs/dotnet-full-3.log` |
| AC5（pins） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 仓库根 | **PASS 18/18**（`PIN AUDIT: PASS (all 18)`，EXIT 0） | `logs/verify-pins.log` |
| AC5（governance） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md` | in_review 卡 + 证据 | 见 `logs/check-final.log`（Lead 已先更新 READY/STATUS 指针） | `logs/check-final.log`、`logs/gates.log` |

**恢复记录**：全量 .NET 运行后 tracked 证据 `verification/FEA-09/logs/wire-redacted.ndjson` 被测试重写，已按卡要求 `git checkout -- verification/FEA-09`（EXIT 0，`git status -- verification/FEA-09` 为空）。

## 接收方式

- 分支/工作树：`main` 主工作树 `G:\CODEX\New Manga`；无 push、未新建分支/worktree。
- 复现命令（全部只读或只写 pytest tmp/自清理 temp）：
  ```text
  C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings --tb=no
  pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1
  C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py
  ```
- 无外部依赖/数据/环境变量需求；不需要 `NEWMANGA_*`、AppData、真实回收站。
- 接收者步骤：①独立上下文 fresh subagent Review（实现者 `fea12-dsim-impl` 未自审）；②Review approved 后由 Lead 做集成验证与 STATUS/Plan/Ledger 指针更新；③closeout 时按 Resource Manifest（本卡 NOT_APPLICABLE，无仓外资源）与 Canonical Evidence 收口。

## 下一任务建议（必填）

- **Task ID / 标题**：`FEA-12-DSIM-1` 独立实现 Review（Lead 派 **fresh subagent**，只读 `94a12e93f` + `3d0d325f7` + 本 Handoff/docs commit）。
- **推荐 Agent / Reviewer**：Lead 派独立上下文 fresh subagent（2026-10-31 裁决：上下文独立即可；实现者不自审）。Reviewer 不得参与本卡实现。
- **推荐原因与前置依赖**：D 流程模拟切片的范围/禁令（ADJ-2026-11-05 §D5/§D8）需要独立复核；Review 通过后 D 流程模拟切片可 integrated，`FEA-12-CORE` 仍按自身依赖推进；**真实 D 流程（Windows 回收站桥）需用户另行专门授权**，不在本轮。
- **Recovery point**：仓库 `G:\CODEX\New Manga`（`main`）；实现 commits `94a12e93f`、`3d0d325f7`；docs commit 紧随其后；无 worktree 需恢复。
- **允许修改路径 / 禁止范围**：Review 只写 `doc/reviews/FEA-12-DSIM-1-*.md`；不得改实现、证据、Task 卡、冻结契约字节；不 push。
- **交付物**：`doc/reviews/FEA-12-DSIM-1-impl-*.md`（P0/P1/P2 + verdict + 审查者身份/上下文来源 + reviewed_head）。
- **验证命令与 Gate**：见上「验证证据」表；Review 需独立复跑 fea12 pytest + 静态扫描 + 哨兵探针，并核对 AC-MATRIX/Canonical Evidence 是否支撑 AC1–AC5。
- **可直接转发给 Agent 的指令**：

```text
你是 FEA-12-DSIM-1 的独立实现 Review 者（未参与实现）。仓库 G:\CODEX\New Manga（main）。
只读审查实现 commits 94a12e93f + 3d0d325f7（及其 docs commit），对照
doc/tasks/FEA-12-DSIM-1.md、doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md §D5/§D7/§D8、
doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §3 D 行、doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §3.7、
doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md SC-B05、doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-31/SC-34。
重点：①协议/typed 结果/生产默认 typed 不可用是否真实且零文件操作；②SimulatedRecycleBin 是否只在隔离根内写、
manifest/journal 是否可审计、失败是否保留原文件且永不降级永久删除；③src/**+apps/** 静态扫描 0 Windows 回收站 API、
运行时哨兵是否独立可复跑；④是否越权接 Host/UI、改既有生产文件、改冻结契约/schema/依赖、删测试/放宽断言；
⑤AC1–AC5 证据与 Canonical Evidence 是否支撑，.NET flaky 归因是否诚实分列（首跑/复跑）。
独立复跑：C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings --tb=no；
pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1；
C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py。
输出 doc/reviews/FEA-12-DSIM-1-impl-r1.md：P0/P1/P2 分级 + verdict（approved/changes_requested）+
审查者身份与来源（子 agent 会话/子任务 ID）+ reviewed_head。不得修改任何实现/证据/契约文件；不 push。
```

## 风险与遗留

1. **模拟 ≠ 真实 D 流程（最重要）**：本卡是模拟切片；生产默认实现 typed 不可用（fail-closed）。真实 Windows 回收站 API/真实回收站/真实用户数据/AppData/外部卷**零操作**，真实 OS 行为 **`NOT_RUN`**，需用户另行专门授权；不得据此声称 D 流程完成。
2. **全量 .NET flaky（已按首跑/二次/稳定树复跑分列，不合并）**：`FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言"运行期间 verification git status 不变"，被并发 teammate 写入 `verification/FEA-11-LINEAGE-1/logs/**`（实测 diff 见 `logs/dotnet-full-2.log`）与既有 `WireLogSourceRedactionTests` 重写 `verification/FEA-09` 命中窗口。稳定树复跑 **0 failed / 1403 passed / 79 skipped**。本卡**未改任何 .NET**；建议后续 DSH 全量复跑时保留"首跑+复跑"记录。
3. **pytest 数字含并发改动**：交付 head `3093/10` = 基线 `3073/10` + 本卡 13 + FEA-11-LINEAGE-1 r3 已提交 7；本卡未改任何既有 Python 生产路径。
4. **目录条目 junction/symlink 无 OS 级测试**：代码对选中文件夹内的 junction/symlink 判 `unsupported_entry`（`os.walk(followlinks=False)` + 每级 reparse 拒绝），但测试未创建真实 junction（避免依赖 `mklink`）；真实桥需另行覆盖。
5. **崩溃恢复未实现**：journal/receipt（SC-34）形状仅作为 seam；"崩溃后先核对 OS 事实再决定重发"属真实 Host 桥任务。
6. **check.ps1 预期 2 个 warning（非本卡引入）**：`存在 15 个非终态 Task`、`doc/REBASELINE_PLAN.md 达到预算 80%`（Lead-owned，本卡不改）。
7. **evidence_dir 过程文件（DONE 前处置）**：`logs/gates.log`、`logs/check-final.log` 为过程/汇总文件未列 Canonical Evidence，draft 态只产生 warning；DONE 前由 DSH 移入 workspace agent-output 或补列 SOURCE_PIN（判别力证据 EV-01…EV-18 已全部登记）。
8. **未推送**：本卡全部 commits 在本地 `main`，无 push。

**Review 就绪声明**：实现与证据已提交（`94a12e93f` + `3d0d325f7` + docs commit）；AC1–AC5 全部 `<<MET>>`；门禁实测（pytest fea12 13 passed；全量 pytest 3093/10；全量 .NET 稳定树 1403/0/79；pins 18/18；静态扫描 766 files / 0 Windows API；运行时哨兵 PASS；check 见 `logs/check-final.log`）；**实现者不自审**，请 Lead 派独立上下文 fresh subagent 执行 Review。
