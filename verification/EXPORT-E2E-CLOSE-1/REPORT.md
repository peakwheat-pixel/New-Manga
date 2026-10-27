# EXPORT-E2E-CLOSE-1 交付报告：Export 端到端真跑（新 sidecar + translated 产物 + grant）

- Task: `doc/tasks/EXPORT-E2E-CLOSE-1.md`（team task-42）；Owner `route-research`；Reviewer `dsh`
- Branch: `task/EXPORT-E2E-CLOSE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1`
- Base: 卡面 `e30149258`；按 Lead 指示基于当前 HEAD **`e6c2db84f`** 开分支
- Delivery head: `__DELIVERY_HEAD__`（本任务只新增 C# 验证测试 + 验证工具/证据；未改 Python Core 语义、协议、旧壳、packaging）
- 证据目录: `verification/EXPORT-E2E-CLOSE-1/`

## 0. 结论

| AC | 判定 | 一句话 |
|---|---|---|
| AC1 前置复验 | **MET** | RELEASE-REPACK-2 新 sidecar（models `c5531930…`）上，completed Run 的 3 个 translated 产物存在、可定位、哈希与 DB 一致；`GetExportHistory` 导出前为空 |
| AC2 Export 真跑 | **MET** | Host `HostGrantCoordinator` 链（`RegisterExportTarget` host-control → `StartExport`）**真实产出 ZIP 图片包**：7,070,562 B / sha256 `cf9a0719…` / 3 页 + `manifest.json`；每页条目字节哈希 = manifest = 落库 translated revision |
| AC3 get/cancel 成功路径 | **MET** | 成功记录 `GetExportSnapshot` → `completed`（含 output{format,path,sha256}）；取消：`CancelExport` 后记录 `cancelled`、**未发布任何文件**；未知 id 两侧均 typed `EXPORT_NOT_FOUND`（负例） |
| AC4 回归/证据 | **MET** | `test.ps1` **191/191 passed**（新增 2 例真实 E2E；基线 ≥182）；pytest `3F/2764P/9S`（基线同值，0 新增）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |
| AC5 门禁 | **MET** | 真实产物 + 命令面证据入库（`artifacts/`、`evidence/`）；未伪造任何导出产物 |

## 1. AC1 前置复验（新 sidecar 上 translated 产物存在且可定位）

工具：`tools/ac1_precheck.py`（启动 RELEASE-REPACK-2 models sidecar，真实 wire；数据根为 REPACK-2 已完成 Run 的**私有副本**，原任务证据根未被修改）。证据：`evidence/ac1-precheck.json`。

| 项 | 值 |
|---|---|
| sidecar core_service sha256 | `c55319306e3022f325c1879deaa96a476dc105b206fa7135c6ae312a2a5c027b`（RELEASE-REPACK-2 models；对照 base `091a201d…`） |
| completed Run | `run-236e8cfe1b764fdcbc1fc17854b22ebf`，status=`completed`，command=`translate_untranslated`，bindings `{ocr: manga-ocr, translate: identity-translation}` |
| translated 页 | **3 页**（E04P02/E04P03/E04P06），`artifact_type='translated'`，revision/sha/大小见下 |
| 读投影 | `GetReaderProjection(mode=translated)` 3 页 `translated.artifact_revision_id` + `sha256` 非空 |
| 导出历史 | `GetExportHistory` → `{"exports":[]}`（导出前确实没有记录） |

| page | translated revision | sha256 | bytes |
|---|---|---|---|
| f52f…932 / E04P02 | 56d3c442cb8c49d4b692cb44167185c5 | `4ca8a215401a237380cf62562f1b07137f8e3e9e1da126c6e74320d71f285b7d` | 3,104,675 |
| 4f8a…84f / E04P03 | f5cbd019a6824c77903d0248d859ad48 | `69344431e3c221dd7374602670d008f3321583fffffd2b74291b17b6132d7a0c` | 2,802,034 |
| a607…2ca / E04P06 | 5216cf71f59b47008addb2842c40857c | `562a672aee571e9c26f0d4c427d07f71ed5316d933e07c15fb18c6b4746af2f2` | 1,166,522 |

> 说明：translated 产物来自 identity translation（**EXPERIMENTAL 占位**，输入=输出，不是产品质量——见 TRANSLATE-PROVIDER-1）。本卡只验证“导出真实读到了这些已落库的 translated revision”。

## 2. AC2 Export 真跑（Host 命令面 + grant 链 → 真实产物）

实现：新增 `apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs`，经真实 `HostRuntime`（新 sidecar、私有数据根）执行生产路径：

```
HostRuntime.StartAsync → HostGrantCoordinator.StartExportAsync(request, target)
  → HostIssuer.MintExportGrant（Host 进程内签名，不落盘）
  → SendHostControlAsync("RegisterExportTarget")  ← 真实 wire 帧（证据断言存在）
  → SendAsync("StartExport", target_ref=grant.Reference)
  → P16ExportRuntime.start（异步 job）→ 轮询 "library_get_export_snapshot"（Host 命令面）
```

| 项 | 值 |
|---|---|
| export_id | `exp-268d58e2d983` |
| 请求 | BOOK-FIXTURE 书 / chapter `240bdba5…` / 3 个 translated 页（顺序 E04P02→P03→P06） / format=`zip`（compression=standard）/ stale_policy=`abort` |
| 目标路径 | `task-envs/EXPORT-E2E-CLOSE-1/data-root/exports/book-fixture-20261027-134723.zip`（Host 白名单：data root/exports） |
| 产物 | **7,070,562 B**；sha256 **`41d9d5fc8ee9fbed196b9155816a06cd4388b6010662bbd31957957d07d57ef9`**；zip 可打开、4 条目 = `0001/E04P02.jpg`（3,104,675B）+ `0002/E04P03.jpg`（2,802,034B）+ `0003/E04P06.jpg`（1,166,522B）+ `manifest.json`（2,273B） |
| 内容校验 | manifest 3 页 sha = 落库 translated revision sha = 每页条目字节 sha256（独立复算） |
| snapshot 时间线 | `running` @26.6ms → `completed` @210.4ms（Host 从启动到导出完成 786.9ms） |
| history 记录 | `status=completed`、`output_path`/`sha256` 与产物一致、`ordered_page_ids=3` |
| grant 链 | Host wire 帧中确认 `RegisterExportTarget` 与 `StartExport`；无 grant 时 Core 拒绝（GRANT-ISSUER-1 既有证据，本卡未重复） |

产物已入库：`verification/EXPORT-E2E-CLOSE-1/artifacts/book-fixture-20261027-134723.zip`（sha256 与上表一致）。证据：`evidence/export-success.json`、`evidence/ac2-ac3-records.json`（独立复算）。

## 3. AC3 get/cancel 在真实导出记录上验证

工具：C# 测试（Host 命令面）+ `tools/verify_export_records.py`（新 sidecar 重开同一数据根，独立复读）。证据：`evidence/ac2-ac3-records.json`、`evidence/export-cancel.json`。

| 场景 | 记录 | 结果 |
|---|---|---|
| 成功导出取快照 | `exp-268d58e2d983` | `GetExportSnapshot` → `completed`，`output={format:zip, output_path:…, sha256:cf9a0719…}`；`GetExportHistory` 命中同记录，`status=completed`、sha 一致 |
| 取消（一次） | `exp-827c4833b7cf` | `StartExport` 后立即 `library_cancel_export` → 终态 **`cancelled`**（25ms），**目标文件未发布**（`cancelled_target_absent=true`，`artifact_published=false`） |
| 取消后取快照 | `exp-827c4833b7cf` | `GetExportSnapshot` → `cancelled`，`output=null`（无半成品） |
| 取消重放 | `exp-827c4833b7cf` | `CancelExport` 幂等 → `cancelled` |
| 未知 id 负例 | `exp-does-not-exist` / 空白 id | `GetExportSnapshot`、`CancelExport` 均 typed **`EXPORT_NOT_FOUND`** |

观察（非缺陷、未改 Core）：durable `export_history` 表记录的是已发布结果（completed 行）；cancelled 记录由 P16 runtime 的 job store 保存，`GetExportHistory` 会合并两者返回（本卡只记录语义，不做改动——禁止改 Core）。

## 4. AC4 回归 / 证据

| 门 | 命令 | 结果 |
|---|---|---|
| .NET 全量 | `apps/desktop-avalonia/scripts/test.ps1`（挂真实 E2E 环境变量） | **TEST PASS (Debug): 191/191 passed, 0 skipped**（coreclient 61 + host 55 + app 75；新增 ExportE2ETests ×2，基线 ≥182） |
| Python 全量 | `python -m pytest -q` | **3 failed / 2772 passed / 9 skipped**；同树纯净 base `e6c2db84f` 实测 **3F/2772P/9S**（失败集合逐条相同：`test_detection_manga_real` ×2 + `test_workbench_viewmodel` ×1），**0 新增** |
| Export 记录独立复验 | `python verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py --host-evidence <dir>` | 全部断言 true（见 §2/§3） |
| 治理 | `check.ps1 -TaskPath doc/tasks/EXPORT-E2E-CLOSE-1.md` | PASS（见 Task 卡收口） |

日志：`pytest.log`、`pytest-baseline-base.log`（同树纯净 base 对照）、`evidence/test-ps1.log`、`evidence/dotnet/{summary.json,dotnet-test-Debug.log,results-host.trx}`。

> 树/口径说明：交付树已 rebase 到 `6f6e4a678`（CREDENTIAL-PORT-1/CREDENTIAL-UI-1 集成）。上述 **191/191** 与全部 Export E2E 证据均在该树上重跑生成；pytest 结果沿用同一 Python 树（rebase delta 仅 `apps/desktop-avalonia/**`、`doc/**`、`verification/**`，`git diff` 核对未触及 `src/**`、`tests/**`）。

## 5. Record Decision

1. **只加验证，不改产品语义**：本卡代码改动仅为 `apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs`（2 个真实 E2E 用例）与 `verification/EXPORT-E2E-CLOSE-1/**`；Python Core、wire 协议、Host 契约、旧壳、packaging 零改动。
2. **导出成功的判定标准**：不是“StartExport 返回 pending”，而是（a）job 终态 `completed`；（b）磁盘文件存在且 sha256 = snapshot/history 记录；（c）ZIP 可打开且逐页条目字节 sha256 = manifest = 落库 translated revision；（d）history 可检索到同一记录。以上全部由独立进程复算，未使用任何 mock 或预生成文件。
3. **取消成功的判定标准**：终态 `cancelled` **且**目标文件不存在（Core 的 `before_publish` 取消检查保证不发布半成品）。
4. **grant 边界**：导出目标只能落在 Host 数据根白名单（`data root/exports`）；签名密钥仅存于 Host 进程内、不落盘（GRANT-ISSUER-1 实现，本卡只消费）。
5. **质量声明**：导出内容为 identity 翻译产物（输入=输出），仅证明链路可用；不构成翻译/排版质量验收。
6. **格式范围**：本卡验证 `zip`（图片包）。PDF 需要 Qt composer（headless sidecar 无 Qt），cbz/text 未纳入本卡；未验证不等于失败，已在遗留中列明。

## 6. 遗留 / NOT_RUN

1. **PDF/图片单页/CBZ/text 格式**未在本卡验证：PDF 依赖 Qt composer（本 sidecar 无 Qt），其余格式为不同 writer 分支；如需发布前覆盖，另开格式矩阵 Task。
2. **真实翻译质量**：导出内容来自 identity experimental 占位；产品发布前需真实翻译 provider（OpenAI-compatible / Sakura）与排版验收。
3. **大书/多章导出性能**：本卡 3 页 7MB、204ms；更大规模未测。
4. **导出 UI 动作**：`library_reveal_export_folder` shell 动作已在 GRANT-ISSUER-1 覆盖；本卡未重复真机截图。
5. 取消记录仅存在于 runtime job store（DB `export_history` 只存已发布结果）——语义已记录，未改 Core（本卡禁止改）。
6. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。

## 7. 复跑方式

```powershell
# AC1：重置私有数据根并复验 translated 产物（新 sidecar，真实 wire）
python verification/EXPORT-E2E-CLOSE-1/tools/ac1_precheck.py

# AC2/AC3：Host 真实导出 E2E（2 个用例：成功 ZIP + 取消）
$env:NEWMANGA_EXPORT_SIDECAR_DIR = "G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models/app/core-sidecar"
$env:NEWMANGA_EXPORT_DATA_ROOT  = "G:/CODEX/New Manga.workspace/task-envs/EXPORT-E2E-CLOSE-1/data-root"
$env:NEWMANGA_EVIDENCE_DIR      = "G:/CODEX/New Manga.workspace/task-envs/EXPORT-E2E-CLOSE-1/evidence/dotnet"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --filter "FullyQualifiedName~ExportE2ETests"

# AC2/AC3 独立复验（产物 + 记录 + 负例）
python verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py --host-evidence <dotnet-evidence>/export
```
