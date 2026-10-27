# EXPORT-E2E-CLOSE-1 Handoff（Export 端到端真跑）

- Task: `doc/tasks/EXPORT-E2E-CLOSE-1.md`（team task-42）
- Branch: `task/EXPORT-E2E-CLOSE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1`
- Base: 卡面 `e30149258`；按 Lead 指示基于当前 HEAD `e6c2db84f` 开分支
- Delivery head: `0b24038b2611450e3643d6178f56c4082ff358e4`（新增 C# E2E 测试 + 验证工具/证据；未改 Python Core/协议/Host 契约/旧壳/packaging）
- 未 push；未 gc/prune。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 前置复验 | **MET** | 新 sidecar models `c5531930…` 上 completed run `run-236e8cfe1b764fdcbc1fc17854b22ebf` 的 3 个 translated 产物：reader 投影 revision/sha、`media_artifacts`+`artifact_revisions` 落库行、磁盘文件 sha 三者一致；导出前 `GetExportHistory` 为空。`evidence/ac1-precheck.json` |
| AC2 真实产物 | **MET** | Host grant 链（host session → `RegisterExportTarget` → `StartExport`）导出 ZIP：**7,070,562 B / sha256 `cf9a0719bc7fca57d574e210fd2c82115ded6f3c76839851ac2e005a9092cdd8`**，3 页 + `manifest.json`；逐页条目字节 sha = manifest = 落库 revision；`GetExportSnapshot`→completed、`GetExportHistory` 一致。`evidence/export-success.json`、`evidence/ac2-ac3-records.json`、`artifacts/book-fixture-20261027-132203.zip` |
| AC3 get/cancel | **MET** | 成功记录 `GetExportSnapshot`=completed（output 含 path/sha256）；取消记录 `exp-96acd695ec04` → `cancelled`（23.9ms）且**无产物**，取消后快照 cancelled；未知 id → typed `EXPORT_NOT_FOUND`。`evidence/export-cancel.json`、`evidence/ac2-ac3-records.json` |
| AC4 回归/证据 | **MET** | `test.ps1` **184/184 passed, 0 skipped**（新增 `ExportE2ETests` ×2，真实执行——trx 含两用例；基线 ≥182）；pytest **3F/2772P/9S** vs 同树纯净 base `e6c2db84f` **3F/2772P/9S**（失败集合逐条相同，0 新增）；`check.ps1 -TaskPath` PASS；64-hex pin；本 Handoff |
| AC5 门禁/入库 | **MET** | 真实产物 + 命令面证据入库；未伪造导出产物 |

## 2. 代码/证据清单

| 路径 | 说明 |
|---|---|
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs`（新增） | 2 个真实 E2E：成功 ZIP（含哈希/manifest/条目校验 + wire 证据断言）与取消（终态 cancelled、无产物）；仅当 `NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT` 均提供时执行，普通 test.ps1 运行直接返回不产生副作用 |
| `verification/EXPORT-E2E-CLOSE-1/tools/ac1_precheck.py` | 新 sidecar + 真实 wire 的前置复验（复制 REPACK-2 数据根到本 Task 私有目录，不改原证据根） |
| `verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py` | 独立复验：ZIP 结构/哈希/manifest/条目、`GetExportHistory` 两条记录、两种快照、cancel 重放、未知 id 负例 |
| `verification/EXPORT-E2E-CLOSE-1/artifacts/book-fixture-20261027-132203.zip` | 真实导出产物（7,070,562B，sha256 `cf9a0719…`） |
| `verification/EXPORT-E2E-CLOSE-1/evidence/*` | AC1/AC2/AC3 JSON、test.ps1 日志/摘要/trx；`REPORT.md` 为完整报告 |

## 3. 关键判定与决策（完整见 REPORT §5）

1. **verification-only**：不触碰任何产品语义；Core 的 `StartExport`/`P16ExportRuntime`/`export_history` 行为保持原样。
2. **成功判定**（全部独立复算）：job 终态 completed + 产物 sha256 == snapshot/history 记录 + ZIP 可打开且逐页条目字节 sha == manifest == 落库 translated revision + history 可检索同一记录。
3. **取消判定**：终态 cancelled 且目标文件不存在（Core `before_publish` 取消检查保证不发布半成品）。
4. **grant 边界**：目标只能在 Host 数据根白名单（data root/exports）；签名密钥仅 Host 进程内。
5. **格式范围**：本卡 zip 图片包；PDF 需 Qt composer（headless sidecar 无 Qt），cbz/text 未纳入（遗留）。
6. **质量声明**：导出内容来自 identity translation（EXPERIMENTAL 占位，输入=输出），只证明链路，不构成翻译/排版质量验收。

## 4. 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/EXPORT-E2E-CLOSE-1.md` → PASS（见 Task 卡收口）。
- Canonical Evidence：12 条 64-hex sha256 pin + 3 条 SOURCE_PIN（commit 列留空）；Resource Manifest 指向 task-env 与产物。
- 未 push、未 gc/prune。

## 5. 遗留

1. PDF/CBZ/text 导出格式未验证（PDF 依赖 Qt composer；其余为不同 writer 分支）——建议另开格式矩阵 Task。
2. 真实翻译质量需真实 provider（identity 仅为 EXPERIMENTAL 占位）。
3. 大书/多章导出性能未测（本卡 3 页 7MB / 204ms）。
4. cancelled 记录仅存在于 runtime job store，DB `export_history` 只存已发布结果——语义已记录，未改 Core。
5. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。
