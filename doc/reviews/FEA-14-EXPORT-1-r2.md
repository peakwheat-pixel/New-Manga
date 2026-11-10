---
task_id: FEA-14-EXPORT-1
reviewer: fresh 独立上下文子 agent（续接 r1；未参与本卡实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 863d1b4f5
reviewed_head: 22683068e
decision: approved
---

# Review：FEA-14-EXPORT-1（r1 处置后复核，r2）

## 0. 审查对象、环境与范围

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `22683068e15d1c61218b463bf157acd064c83be8`**。审查开始 `2026-11-10T11:09:55+08:00`、结束（本报告写入前）`11:20+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`863d1b4f5..22683068e`，**10 文件**（`ImportExportPanels.cs`、`ImportExportUiTests.cs`、`service.py`、`test_export.py`、卡面、README、3 份日志、r1 报告入库）；全部 ⊆ 卡面 allowed_paths（OUT=0）；无 `IHostController.cs`/`schema.py`/契约改动。
- r1 报告：`doc/reviews/FEA-14-EXPORT-1-r1.md`（本审查者上一轮，未被实现者改动）。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。r1 探针与 r2 日志在仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r2\`。

## 1. 结论

**`approved`（带 P2/P3 残余；AC4 按 r1 处置后的新口径为 PARTIAL，需 DSH 接受或另立卡）。**

| 计数 | 值 |
|---|---|
| P0 | **0** |
| P1 | **0**（R-001 已由仓外探针 + 新增 runner 测试证明修复） |
| P2 | **2**（R2-001 `target_context` 跳过导致 AUTO_RENAME 路径的 reparse/父句柄校验缺失；R2-002 AC4 新口径与 Scope §4/标题/测试不一致） |
| P3 | **5**（`_publish_to` exists→replace TOCTOU；R-002 源码顺序测试脆弱；R-005/R-008 无测试；证据 provenance；E2E/NOT_RUN） |

核心通过：**r1 P1 的 runner 覆盖缺陷已修复**。以 r1 完全相同的探针场景（默认 AUTO_RENAME + mint 时 target 存在 + `ResolvedExportTarget(replace_existing=True)` + `P16ExportRuntime.start`）重跑：旧 target 字节保持 `OLD-USER-FILE`、`book (1).zip` 生成、snapshot `completed`、history output_path=`book (1).zip`、job 不卡 publishing。全量/定向门禁全绿（§5）。

## 2. r1 findings 关闭判定

| r1 ID | r1 级别 | r2 判定 | 依据 |
|---|---|---|---|
| R-001 | P1 | **CLOSED** | `service.py:326-344` 仅在解析路径≠`request.output_path` 时跳过 mint target-context；`:1021` 改为 `_publish_to(final_path,temp,target)`（`:768-784`：同父目录 + final 不存在 + `os.replace`；final==target 时仍 `target.publish`）。新增 `tests/reading_export/test_export.py:333-373` 用 mint 时 target 存在 + `replace_existing=True` 断言 old bytes、`runtime (1).zip`、snapshot/history completed。仓外探针 `probe_runner_autorename.py`（r2）实测：`status: completed`、target bytes=`OLD-USER-FILE`、renamed exists=True、history output=`book (1).zip`。门禁定向 pytest 177/0 |
| R-002 | P2 | **CLOSED（P3 残余）** | `ImportExportUiTests.cs:634+` 新增 `HostStartExportResolvesTheNameBeforeMintingTheTargetRef`：断言源码中 policy 调用位置早于 mint 调用（若移动顺序则失败）；`ExportPathPolicyTests` 4 项覆盖自由/已存在/二次冲突/目录。E2E 仍 NOT_RUN（README 已声明）。残余：源码文本断言依赖精确字符串/无运行时行为测试（R2-004） |
| R-003 | P2 | **PARTIAL（P2）** | AC4 判据改为「不产生/不破坏 + typed cancelled」（卡 `:96`、README `:15`），`test_cancel_before_replace_publishes_nothing` 覆盖旧 bytes/无新文件/history cancelled；但 **卡面 Scope §4（`:65`）与标题（`:3`）仍写「取消保留成功文件/typed 报告完成数量」**，与新 AC4 矛盾；新 AC4 声称的 mtime 与 snapshot cancelled 未被该测试断言（未做 runtime cancel 测试）→ 口径/证据未完全一致（R2-002） |
| R-004 | P2 | **CLOSED（新 P2 残余）** | 探针证明 `replace_existing=true` 时不再覆盖（发布落点由 `_resolve_target` 决定）；README `:27` 说明一致。**但** AUTO_RENAME 时跳过 mint target-context 后，`_publish_to` 只做字符串父目录 + final 不存在检查，未保留 `ResolvedExportTarget.hold_parent` 的 reparse/父句柄/发布后校验（R2-001），属路径安全回归 |
| R-005 | P3 | **CLOSED（P3 残余）** | `ImportExportPanels.cs:505-510` 在 `requested==0 && !currentKnown` 时提示「当前页未定位；已回退为整章导出」；无对应 UI 测试（R2-005） |
| R-006 | P2 | **CLOSED（P3 provenance）** | README `:26` 记录 pytest 首轮失败→修复、m2 显式 OVERWRITE 说明；`pytest-full.log` 保留首轮 1 failed（`:317-318,364`）与 final 3477/0/10（`:618,664`）；卡面/README 一致 |
| R-007 | P3 | **CLOSED（P3 残余）** | README `:4` 修正 Base/实现提交；logs 注明 HEAD 为生成时/提交前（README `:27`）；仍待 closeout：卡面 `delivery_head:null`、Canonical Evidence commit 列 `-`（R2-006） |
| R-008 | P3 | **CLOSED（P3 残余）** | `ImportExportPanels.cs:767-775` 仅在 `_status.Text` 不含 OutputPath 时追加；无测试断言完成态文本不重复（R2-005） |
| R-009 | P3 | **CLOSED** | `test_default_policy_never_replaces_an_existing_target` 增加 mtime 断言；runner 边界测试（mint target 存在 + `replace_existing=true`）覆盖；case/symlink 未测（非 r1 要求） |

## 3. R2 Findings（新发现，均不改变 approved 门槛）

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R2-001 | **P2** | `src/application/export/service.py:326-333`（AUTO_RENAME 跳过 target-context）、`:768-784`（`_publish_to`）；对照 `src/infrastructure/export/target_refs.py:45-84,192-204` | **AUTO_RENAME 路径失去了 mint target-context 的路径安全校验**：原 `ResolvedExportTarget.hold_parent` 会 resolve 父目录、拒绝 reparse/junction、持有不允许删除共享的父句柄，并在发布后校验；改为 `_publish_to` 后只剩「父目录字符串相同 + final 不存在 + `os.replace`」。若授权父目录在 resolve→publish 间被替换为 junction/symlink，发布可写到授权目录之外；这是相对既有 `target_refs` 安全不变量的回归。常规产品路径（Host 预改名）不触发，但修复引入了该缺口。 | 为重命名 sibling 也取得授权父目录的 handle/reparse 校验（可复用 `hold_parent` 的父目录部分或新增 `hold_parent_for(final_path)`），再 `os.replace`；补 reparse/父目录替换负例 |
| R2-002 | **P2** | 卡 `:3`（title）、`:65`（Scope §4）、`:72`（r1 处置记录）、`:96`（AC4）；README `:15`；`tests/reading_export/test_export.py:315-330` | **AC4 口径收窄未同步冻结 Scope/标题，且测试未覆盖新 AC4 的 mtime/snapshot**：Scope §4 仍要求「取消时已完成页/已成功文件保留（typed 报告完成数量，不静默删除）」，卡标题仍「取消保留成功文件」，而 AC4/README 改为「不产生/不破坏 + typed cancelled（无部分成功文件）」。若这是 DSH 的产品/范围口径修正，应在 Scope §4/标题记录并给出裁决；否则属于未经冻结范围记录的缩减。测试只断言旧 bytes/无新文件/history cancelled，未断言 mtime 或 `P16ExportRuntime` 的 cancelled snapshot。 | DSH 明确：更新 Scope §4/标题并在 r1 处置记录引用裁决，或恢复「报告完成数」实现/测试；补 cancel runner 的 snapshot/mtime 断言 |
| R2-003 | P3 | `src/application/export/service.py:782-784` | `_publish_to` 的 `final_path.exists()` 与 `os.replace` 之间仍有 TOCTOU：窗口内出现的同名文件会被 `os.replace` 覆盖（`os.replace` 不拒绝已存在目标）。原 `target.publish` 是同类模式，但新路径没有额外保护。 | 用独占创建/link+rename 或再校验；至少注明该窗口并补压力/负例（README 已声明未压测） |
| R2-004 | P3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs:634+` | R-002 的源码顺序测试依赖精确字符串 `ExportPathPolicy.NextFreeExportPath` 与 `grants.StartExportAsync(request, effectiveTarget`；格式化/换行/注释出现同名串即可造成假阴/假阳；它验证「源码顺序」而非运行时行为（真实 HostController 行为测试仍无，E2E NOT_RUN）。 | 改为行为测试（可注入 grants/记录 target）或在源码测试中限定代码区/使用 Roslyn；保持 E2E NOT_RUN 声明 |
| R2-005 | P3 | `ImportExportPanels.cs:505-510`（R-005）、`:767-775`（R-008）；`ImportExportUiTests.cs` | R-005 当前页未定位提示与 R-008 输出路径去重均无测试；代码简单但回归无保护。 | 各补一条 headless UI 断言（未定位提示文本；完成态 OutputPath 只出现一次） |
| R2-006 | P3 | `verification/FEA-14-EXPORT-1/logs/*`；卡 `:17,128-134` | 证据 provenance：r2 新增 run 记录 HEAD=`863d1b4f5`（r2 修复提交前 base；代码字节等同修复后但无法直接证明 commit 内容）；`gates-check.log` 的 STATUS/PLAN 字节数为生成时值（README 已注）；卡面 `delivery_head:null`、Canonical Evidence commit 列 `-` 未填；`pytest-full.log` 首轮失败已在 README 说明。 | 交付 head 上重生成 logs（或记录父 HEAD+diff hash）；closeout 时填 delivery_head/Canonical commit；README 继续保留首轮失败说明 |
| R2-007 | P3 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs:147`；README `:49-53` | 真实 Host+Core E2E 仍 NOT_RUN（env 实测为空），且 `ExportE2ETests` 直接 `runtime.Grants.StartExportAsync`，即使提供 env 也不会覆盖 HostController 的 policy→mint 接线；AC2 端到端层仍无证据。 | 保持 NOT_RUN；如要验证 HostController 接线，另加可注入 grants 的 Host 测试 |

## 4. AC 逐项（r1 处置后）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认不覆盖 | **MET** | 默认 AUTO_RENAME/`_next_free_name`；direct 测试 + **runner 测试 + 仓外探针**均证明旧 target 不变、新 `(1)` 生成、snapshot/history completed；mtime 已在 direct 测试断言 |
| AC2 Host 冲突计划 | **MET（E2E NOT_RUN）** | Host 源码顺序 test + 4 项 `ExportPathPolicyTests`；真实 Host+C E2E 仍 NOT_RUN（README/卡面记录） |
| AC3 scope 三档与顺序预览 | **MET（带 limitation）** | UI 3 项测试通过；当前页/已选页/整章与预览；当前页未定位提示代码已加（无测试，R2-005） |
| AC4 取消保护 | **PARTIAL** | 新 AC4 的「不发布/不破坏/history cancelled」有测试；**mtime 与 snapshot cancelled 未断言；Scope §4/标题仍是旧口径**（R2-002） |
| AC5 零 wire/零 DDL/旧签名 | **MET** | 无 `IHostController.cs`/`schema.py`；`--check` 1/54/6=61 EXIT 0；pins 18/18 |
| AC6 门禁与证据 | **MET（P3 provenance）** | check 默认/TaskPath PASS、pins 18/18、API EXIT 0、定向 27/0、App 865/0/11、pytest 3477/0/10；NOT_RUN 如实；日志 provenance 见 R2-006 |

## 5. 门禁实测（命令 + 时点 + EXIT）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `dotnet test .../NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests\|~PdfExportUiTests\|~ExportStalePolicyTests\|~ExportPathPolicyTests"` | 11:10:36 → 11:10:48 | **27 通过 / 0 失败** | **0** |
| 2 | `python -m pytest tests/reading_export tests/core/test_p16_reader_export.py tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -q` | 11:10:49 → 11:11:20 | **177 passed** | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 11:11:27 → 11:11:29 | PASS（3 warnings：11 非终态 / STATUS 3181 B·31 L / PLAN 6857 B·64 L） | **0** |
| 3b | `... check.ps1 -TaskPath doc/tasks/FEA-14-EXPORT-1.md` | 11:11:27 → 11:11:29 | PASS（同上） | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 11:11:30 | **PIN AUDIT: PASS (all 18)** | **0** |
| 5 | `python tools/generate_api_inventory.py --check` | 11:11:30 | `OK: rendered counts match`；1/54/6 = 61 | **0** |
| 6 | `dotnet test .../NewManga.App.Tests.csproj`（全量） | 11:12:39 → 11:18:33（5 m 50 s） | **865 通过 / 0 失败 / 11 跳过 / 876 总计** | **0** |
| 7 | `python -m pytest -q`（全量） | 11:12:39 → 11:17:52（5 m 6 s） | **3477 passed / 10 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 11:09:55 / 11:20+ | 两次均 **clean**；HEAD 均 `22683068e…` | — |
| 9 | 仓外探针 `python ...\probe_runner_autorename.py`（R-001） | 11:11:37 | `status: completed`；target=`OLD-USER-FILE`；`book (1).zip` exists=True；history output=`book (1).zip` | 0 |

探针日志：`G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r2\probe-runner-autorename.log`。探针与新增 runner 测试使用同一形态（mint target 存在 + `ResolvedExportTarget(replace_existing=True)` + 默认 AUTO_RENAME）。

## 6. 范围与证据复核

- 增量 10 文件全部匹配卡面 allowed_paths（**OUT=0**）；无 `IHostController.cs`/`schema.py`/契约/DDL 改动；pins 18/18、API 61 不变。
- 卡面 Canonical Evidence **7 个 sha256 全部与当前文件匹配**（实测）；`dotnet-app-tests.log` 新增 r2 865/0/11、`dotnet-export-tests.log` 27/0、`pytest-full.log` final 3477/0/10（日志含首轮 1 failed，README 已说明）；`gates-check.log`/`gates-pins.log` 为生成时旧字节数（README 已注）。
- NOT_RUN：真实 Host+Core E2E（env 为空、ExportE2ETests bypass HostController 且 skip）、真实 UI 截图、阅读器多选、并发压力 — 均如实声明，未冒充 PASS。

## 7. 处置建议（P2/P3，不阻塞本次 approved 但应在 closeout 或后续卡处理）

1. **R2-001（P2）**：为 AUTO_RENAME sibling 恢复父目录 handle/reparse 校验（或使 `_publish_to` 复用 `hold_parent` 的父目录保护）；补 reparse 负例。
2. **R2-002（P2）**：DSH 明确 AC4 口径——更新卡面 Scope §4/标题并记录裁决，或恢复「报告完成数」；补 mtime/snapshot cancel 断言。
3. **R2-003/R2-004/R2-005（P3）**：`_publish_to` 独占落盘/TOCTOU 说明；源码顺序测试改行为测试或加限定；R-005/R-008 补 UI 测试。
4. **R2-006（P3）**：交付 head 重生成日志或记录父 HEAD+diff hash；closeout 填 `delivery_head`/Canonical commit。
5. E2E 保持 NOT_RUN；如需 AC2 端到端证据，另建可注入 grants 的 Host 测试。

## 8. 审查者声明

本报告由未参与 FEA-14-EXPORT-1 实现/返修的独立上下文子 agent 出具（与 r1 同一审查上下文续接；r1 报告为本审查者上一轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测或逐行静态核对，未实测项已在 §6 记 NOT_RUN；R-001 的仓外探针不当作产品 E2E PASS。
