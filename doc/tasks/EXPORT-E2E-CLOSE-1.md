---
id: EXPORT-E2E-CLOSE-1
title: Export 端到端真跑（新 sidecar + translated 产物 + grant）
kind: verification
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: route-research
reviewer: dsh
depends_on: []
base_commit: e30149258
branch: task/EXPORT-E2E-CLOSE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1
integration_commit: 3f73c92a1
delivery_head: 6ba640d9984fb647d97233883fe55bef6eba1e32
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/EXPORT-E2E-CLOSE-1
allowed_paths:
  - doc/tasks/EXPORT-E2E-CLOSE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/EXPORT-E2E-CLOSE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/EXPORT-E2E-CLOSE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1/**
---

# EXPORT-E2E-CLOSE-1：Export 端到端真跑

## 背景

RELEASE-REPACK-2 新 sidecar（models `c5531930…` / base `091a201d…`）上 Run 已 **terminal=completed**（translate/render 22/22），translated 产物已具备；GRANT-ISSUER-1 已实现 host_issuer grant（`RegisterExportTarget`）。此前 `StartExport` 卡 `EXPORT_INPUT_UNAVAILABLE` 的前置条件解除。本卡为 **verification** 性质：只加真实 E2E 测试与验证工具/证据，不改产品语义。

分支基于当前 HEAD `e6c2db84f`（Lead 指示；卡面 base 为 `e30149258`）。Handoff：`doc/handoffs/EXPORT-E2E-CLOSE-1-handoff.md`。

## Acceptance Criteria

- [x] **AC1 前置复验**：RELEASE-REPACK-2 新 sidecar 上，completed Run 的 3 个 translated 产物存在且可定位（`GetReaderProjection(mode=translated)` 的 revision/sha、`media_artifacts`/`artifact_revisions` 落库行、磁盘文件 sha 三者一致）；导出前 `GetExportHistory` 为空。证据：`evidence/ac1-precheck.json`。<<MET>>
- [x] **AC2 真实产物**：Host 命令面 + grant 链（`HostGrantCoordinator.StartExportAsync` → `RegisterExportTarget`(host-control) → `StartExport`）对 BOOK-FIXTURE 书导出 ZIP 图片包：**7,070,562 B / sha256 `cf9a0719…` / 3 页 + manifest.json**；ZIP 可打开、逐页条目字节 sha256 = manifest = 落库 translated revision；`GetExportSnapshot`/`GetExportHistory` 记录一致。证据：`evidence/export-success.json`、`evidence/ac2-ac3-records.json`、`artifacts/book-fixture-20261027-134723.zip`。<<MET>>
- [x] **AC3 get/cancel 成功路径**：成功记录 `GetExportSnapshot` → `completed`（output 含 format/path/sha256）；另一记录 `CancelExport` → `cancelled` 且**未发布文件**（25ms），取消后快照 `cancelled`；未知 id 两侧均 typed `EXPORT_NOT_FOUND`。证据：`evidence/ac2-ac3-records.json`、`evidence/export-cancel.json`。<<MET>>
- [x] **AC4 回归/证据**：`test.ps1` **191/191 passed, 0 skipped**（新增 `ExportE2ETests` ×2，基线 ≥182；本次运行真实挂载新 sidecar 与数据根，trx 含两用例）；pytest 本树 **3F/2772P/9S** vs 同树纯净 base `e6c2db84f` **3F/2772P/9S**（失败集合逐条相同，0 新增）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。<<MET>>
- [x] **AC5 门禁/入库**：真实产物 + 命令面证据入库（`artifacts/`、`evidence/`）；未伪造导出产物。<<MET>>

## Record Decision（摘要；完整见 REPORT §5）

1. **verification-only**：代码改动仅为新增 C# E2E 测试 `ExportE2ETests`（2 例）+ `verification/EXPORT-E2E-CLOSE-1/**`；Python Core 语义、wire 协议、Host 契约、旧壳、packaging 零改动。
2. **成功判定**：job 终态 `completed` + 磁盘产物 sha256 = snapshot/history 记录 + ZIP 可打开且逐页条目字节哈希 = manifest = 落库 revision + history 可检索同一记录；全部由独立进程复算。
3. **取消判定**：终态 `cancelled` 且目标文件不存在（`before_publish` 取消检查保证不发布半成品）。
4. **grant 边界**：导出目标限 Host 数据根白名单（data root/exports），签名密钥仅 Host 进程内、不落盘（GRANT-ISSUER-1）。
5. **范围**：本卡验证 `zip` 图片包；PDF（需 Qt composer）、cbz、text 未纳入（列入遗留）。
6. **质量声明**：导出内容为 identity translation（EXPERIMENTAL 占位，输入=输出），只证明链路可用，不构成翻译/排版质量验收。

## 实际测试记录

| 套件 | 命令 | 结果 |
|---|---|---|
| .NET 全量 | `apps/desktop-avalonia/scripts/test.ps1`（挂真实 E2E env） | **TEST PASS 191/191，0 skipped**（coreclient 61 + host 55 + app 75） |
| Export E2E 单跑 | `dotnet test ...Host.Tests --filter FullyQualifiedName~ExportE2ETests` | 2/2 passed（成功 ZIP + 取消） |
| Python 全量 | `python -m pytest -q` | **3F/2772P/9S**（同树纯净 base 3F/2772P/9S，失败集合相同、0 新增） |
| 产物/记录独立复验 | `python verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py ...` | 全部断言 true（见 REPORT §2/§3） |
| AC1 前置 | `python verification/EXPORT-E2E-CLOSE-1/tools/ac1_precheck.py` | 3 translated 页，sha 与 DB/磁盘一致 |

## 允许修改范围

`apps/desktop-avalonia/**`（仅验证脚本/测试）、本卡、STATUS/PLAN/LEDGER、`verification/EXPORT-E2E-CLOSE-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/旧壳、不 push、不 gc/prune；**不得伪造导出产物**；若仍 BLOCKED 需给可判定证据与前置缺口。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1 | AC1 | verification/EXPORT-E2E-CLOSE-1/evidence/ac1-precheck.json | - | b8fc8c3a7fa10a9681fcfcc1665896356358981b786b7aa7d35db1e23e614576 | CANONICAL |
| E2 | AC2/AC3 | verification/EXPORT-E2E-CLOSE-1/evidence/ac2-ac3-records.json | - | 58e2d274ef0f16f987a5a00fe8ea274afa326bfac0cbaded8cb3eed62b794990 | CANONICAL |
| E3 | AC2 | verification/EXPORT-E2E-CLOSE-1/evidence/export-success.json | - | e03394c903e3ae9de1293207abbbdc9b29c4aa580712b264815a8c59e2a9ede7 | CANONICAL |
| E4 | AC3 | verification/EXPORT-E2E-CLOSE-1/evidence/export-cancel.json | - | 7cd1b21bb4cbebdde9f719e23149534b7084c2edb384c5183fa1e743f7236364 | CANONICAL |
| E5 | AC2 | verification/EXPORT-E2E-CLOSE-1/artifacts/book-fixture-20261027-134723.zip | - | 41d9d5fc8ee9fbed196b9155816a06cd4388b6010662bbd31957957d07d57ef9 | CANONICAL |
| E6 | AC4 | verification/EXPORT-E2E-CLOSE-1/evidence/test-ps1.log | - | 3d1ec22fdd152f1ac11a21c0dbdc6cf9f0b6581b35fc982a96544eb292e1f115 | CANONICAL |
| E7 | AC4 | verification/EXPORT-E2E-CLOSE-1/evidence/dotnet/summary.json | - | 214e96ec7c57f6b88f5ae925cf6d97bffe778124ec0fd4cec16ac24d94b0877d | CANONICAL |
| E8 | AC4 | verification/EXPORT-E2E-CLOSE-1/evidence/dotnet/results-host.trx | - | 0ff5d6854dac4897d3a620c1f44b82b73bbd925a5c5b3df171fbd942b92f8276 | CANONICAL |
| E9 | AC4 | verification/EXPORT-E2E-CLOSE-1/evidence/dotnet/dotnet-test-Debug.log | - | eaf3f7df226a94d743545c316d628c6d2c9530cfda86830661cf7357f8376ddf | CANONICAL |
| E10 | AC4 | verification/EXPORT-E2E-CLOSE-1/pytest.log | - | fded90f2b21c751d48f06574e88f6ce57444d39fe3d6e030df0882018a0c358b | CANONICAL |
| E11 | AC4 | verification/EXPORT-E2E-CLOSE-1/pytest-baseline-base.log | - | 7876aea0a8ca92479c39cd884b4896c75b118d25ec4da0d346ab3f8dbe1a8ec2 | CANONICAL |
| E12 | AC1–AC5 | verification/EXPORT-E2E-CLOSE-1/REPORT.md | - | b76bfa9470afdf0180f67f42a5b9aa5b7747dafbbc8879bfd31fd2816053ce20 | CANONICAL |
| E13 | 复跑工具 | verification/EXPORT-E2E-CLOSE-1/tools/ac1_precheck.py | - | c35a5c09b6b770811cdcd928c5b5d66fb83763494b139ac2460431691cf394fe | SOURCE_PIN |
| E14 | 复跑工具 | verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py | - | 38d2bcde8a31893c308f4da3a0817659c83f15e9365bad1c355ac5b37d1a4b8f | SOURCE_PIN |
| E15 | AC4 | apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs | - | 6cc06bb6c9e19f24d0dbb70f4b7638a2bdac11d67b652fe0b8fa7b59482dd993 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/EXPORT-E2E-CLOSE-1 | PRESERVE_REFERENCED | 原路径 | `data-root`（REPACK-2 completed-run 的私有副本）+ `evidence/` + `dotnet-full-evidence/` + 日志 | 保留：真实数据根、dotnet 证据、AC1/AC2/AC3 JSON；`baseline-worktree`（纯净 base 对照）交付后清理。关闭时复核引用。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2 | PRESERVE_REFERENCED | 原路径 | sidecar models core_service sha `c5531930…`；数据根被**只读复制** | 本卡未修改其证据根；归属 RELEASE-REPACK-2。 |
| artifact | verification/EXPORT-E2E-CLOSE-1/artifacts/book-fixture-20261027-134723.zip | PRESERVE | 同路径 | sha256 `cf9a0719…` | 真实导出产物入库（7,070,562B）；引用见 E5。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（12 条 sha256 pin + 3 条 SOURCE_PIN）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写（交付后清理 `baseline-worktree`）。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

## Review（DSH 集成复核，2026-10-27）— PASS

- AC1：REPACK-2 新 sidecar 上 3 个 translated 页 revision/sha 与 DB/磁盘三方一致；导出前 GetExportHistory 为空。
- AC2：grant 链真实导出 **ZIP 7,070,562B**，DSH 独立复算 sha256 `41d9d5fc…d57ef9`（与实现方一致，已用 Get-FileHash 复验）；3 页 + manifest，逐页字节 sha = manifest = 落库 translated revision；快照 running@26.6ms→completed@210.4ms。
- AC3：GetExportSnapshot completed（path/sha256）；CancelExport→cancelled（25ms）无产物；未知 id 两侧 typed EXPORT_NOT_FOUND。
- AC4：DSH 复跑 test.ps1 **191/191**（含 2 条真实 ExportE2ETests）；pytest 3F/2772P/9S（与纯净 base 逐条相同，0 新增）。
- 遗留：PDF（需 Qt composer）/cbz/text 未覆盖；identity 翻译为 experimental 占位（不构成翻译质量验收）；大书性能未测。
- 集成：3f73c92a1。

