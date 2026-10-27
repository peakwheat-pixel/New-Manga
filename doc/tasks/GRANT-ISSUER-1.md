---
id: GRANT-ISSUER-1
title: Host grant 签发 + shell 动作（7 条真缺口）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_ns_b1_grant
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: ed85c4173
branch: task/GRANT-ISSUER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1
integration_commit: 941de7f5a
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GRANT-ISSUER-1
allowed_paths:
  - doc/tasks/GRANT-ISSUER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/GRANT-ISSUER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1/**
---

# GRANT-ISSUER-1：Host 侧 grant 签发 + shell 动作（7 条真缺口）

## 背景

NS-RECLASSIFY-1 证明 7 条真缺口在 **Host 侧**：
- 5 条 import/export：Core 有 `ImportPages`/`StartExport`/`GetExportSnapshot`/`CancelExport`，但 grant 需 **host_issuer 签发**；冻结 Core 对未签名 ref 回 `REF_MALFORMED`，Avalonia Host 未实现签发。
- 2 条 host-local shell 动作：`library_reveal_export_folder`、`plugins_open_directory`（Core 无等价命令，Host 本地实现）。

## Acceptance Criteria

- [x] **AC1 grant 签发**：实现 host_issuer 签发链路（与 host_bridge `issue`/`resolve` 既有契约对齐），使 `library_import_file`/`library_import_folder`/`library_start_export`/`library_get_export_snapshot`/`library_cancel_export` 可真实执行（用 BOOK-FIXTURE 隔离根）；证据含 bridge issue/resolve 日志与输出。→ **MET**（成功样例=import；export grant 注册成功但 StartExport 仍 typed `EXPORT_INPUT_UNAVAILABLE`，translated 前置如实登记）：C# HOST-ISSUER-1 全链（OpenHostSession/签名 grant/Register/ImportPages/StartExport），8 页真实导入 `imported_files=8` + 8 grant registered；证据 `command-list.json`、`evidence/parity-contract.json`、test evidence `grants/*.json`。 <<MET>>
- [x] **AC2 shell 动作**：2 条 host-local 动作实现（打开资源管理器目录/插件目录），走安全路径白名单（不得接受任意用户路径），真机验证并截图。→ **MET**：`library_reveal_export_folder`（GetExportHistory→output_path→白名单）与 `plugins_open_directory`（data root/plugins）；真机 Explorer 截图 `screens/01-plugins-directory-explorer.png`；越权路径 typed 拒绝。 <<MET>>
- [x] **AC3 安全边界**：签发只对授权资源 id；失败 typed；不得放宽 TileChannel 摘要校验或资源通道授权。→ **MET**：仅 Host 铸造 grant（signing key 进程内随机不落盘）；import 源/export 目标/reparse/身份校验；shell 白名单；TileChannel/资源通道零改动；失败均 typed（`REF_*`/`EXPORT_*`/`PLUGIN_DIRECTORY_UNAVAILABLE`）。 <<MET>>
- [x] **AC4 parity/回归**：`--check` 零漂移；快照 5 条 NOT_SUPPORTED→IMPLEMENTED（2 条 shell 动作按 Host-local 归类并记录）；`scripts/test.ps1` 全绿；vitest 60/567；pytest 3F/2746P/9S 无新增失败。→ **MET**：`--check` PASS（66 命令零漂移）；registry **51→55 IMPLEMENTED / 15→11 NOT_SUPPORTED**（rebase 到 NS-WIRE-B1 后并集；本 Task 新增 4 条：import_file/import_folder/reveal_export_folder/plugins_open_directory；3 条 export 命令已在 RUN-EXPORT E2E IMPLEMENTED，本批补齐 grant 层）；test.ps1 **166/166 passed**；vitest **60/60 文件 567/567**；pytest **3F/2746P/9S**（0 新增）。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（签发边界/白名单）。→ **MET**：check.ps1 PASS；pin 见下；`doc/handoffs/GRANT-ISSUER-1-handoff.md`（Record Decision §3）。 <<MET>>
## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/GRANT-ISSUER-1/**`、workspace。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 host_bridge 冻结契约（如确需扩展 wire 版本，必须先在 Task 中回报 DSH 裁决）、不改旧壳、不 push、不 gc/prune。

## 并发注意

与 `RUN-EXPORT-E2E-1` 有交集（E2E 需要 grant 才能真跑 Export）：优先交付 **grant 签发最小可用链路 + 一个 import/export 成功样例**，让 RUN-EXPORT 可复用；与 `NS-WIRE-B1`/`S4-CMD-BATCH-1` 的 registry 改动冲突时以先落地者为准、后落地者 rebase。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| G1 | AC | verification/GRANT-ISSUER-1/command-list.json | | d5c6d5455b2f724184fbd925be5c3c1f6d78b2a28664f6cccd808402257b9fbe | SOURCE_PIN |
| G2 | AC | verification/GRANT-ISSUER-1/dotnet-all.log | | 377fabfc082955da6ac95708a7274a846fbf009e934813f44bad3db57af7b7ba | SOURCE_PIN |
| G3 | AC | verification/GRANT-ISSUER-1/parity-check.log | | 820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe | SOURCE_PIN |
| G4 | AC | verification/GRANT-ISSUER-1/parity-update.json | | cc54e5790eb278b3436f6e2a4b396a467c7768ac1251641ec5f7b98814a8fe97 | SOURCE_PIN |
| G5 | AC | verification/GRANT-ISSUER-1/pytest-ignore-broken.log | | 57a606877779db1334acdd4cd1c0bdbdb647fecaab2dfea4907adcd17445e329 | SOURCE_PIN |
| G6 | AC | verification/GRANT-ISSUER-1/pytest.log | | d2cc3a3ac31ca0c96fc5462a117110d89f0846d5d495316957e41ae7fc5109a6 | SOURCE_PIN |
| G7 | AC | verification/GRANT-ISSUER-1/REPORT.md | | 157012874e57577a91a0a4d0f07c0516bf4b6dc6352283f2b22ca6fa68612526 | SOURCE_PIN |
| G8 | AC | verification/GRANT-ISSUER-1/vitest-install.log | | ba44f10e2cd386b4fa562f1b662bf46389940c5f8a3b1e129d3d88008dd69883 | SOURCE_PIN |
| G9 | AC | verification/GRANT-ISSUER-1/vitest.log | | 37142b6e5236098d764c8b1086ac723c13c1f18d4bb0b91b5fc9ced73eb6795a | SOURCE_PIN |
| G10 | AC | verification/GRANT-ISSUER-1/evidence/chinese-roundtrip.json | | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | SOURCE_PIN |
| G11 | AC | verification/GRANT-ISSUER-1/evidence/domain-services.json | | e951fe83619b3b9bdf71ad562c69ccf3105ed0af14b3d38963dede32b69b8c5f | SOURCE_PIN |
| G12 | AC | verification/GRANT-ISSUER-1/evidence/integration-results.json | | 13cba3d26ddcc28765ceef4410acaa6f21249f54852aa9204850dd1c49fdd09c | SOURCE_PIN |
| G13 | AC | verification/GRANT-ISSUER-1/evidence/not-supported-typed-errors.json | | 3dc30f7c246eba06411773fbf1e69b602a79ac9dfdb7217c122db973e1f41786 | SOURCE_PIN |
| G14 | AC | verification/GRANT-ISSUER-1/evidence/ns-b1-integration.json | | f946153f1f73f52d36b5665897bd69427e3ccaae8bee050586658634b5452e89 | SOURCE_PIN |
| G15 | AC | verification/GRANT-ISSUER-1/evidence/ns-b1-invalid-arguments.json | | fec4ebcb4378744e7891b4067845cbb12a406b0c83b143c53a39073b37c19209 | SOURCE_PIN |
| G16 | AC | verification/GRANT-ISSUER-1/evidence/parity-contract.json | | 59d195e18f412ea6045a6fa951ee404fdd15f6820d4c2287cef8a9cce9dce130 | SOURCE_PIN |
| G17 | AC | verification/GRANT-ISSUER-1/evidence/s4-region-reader-results.json | | 1ee022d47c6c69f47ea5f6c43d9e035c2c59a8ce1d1e43bc293c29fc8b188b7f | SOURCE_PIN |
| G18 | AC | verification/GRANT-ISSUER-1/evidence/s4-wiring.json | | e93851d237d046baf98d9afe38ab74e0ab2199cdf34b1485f8c4abe9c596f329 | SOURCE_PIN |
| G19 | AC | verification/GRANT-ISSUER-1/evidence/wiring.json | | 1c3050a24274705d1857460168ca728959644ad49a9f39cfa4003a4d19529a01 | SOURCE_PIN |
| G20 | AC | verification/GRANT-ISSUER-1/screens/01-plugins-directory-explorer.png | | 78b014e5fe43909bba4aa909cf9dcb2878dc306b69f39fea74354c0f48739e2e | SOURCE_PIN |
|---|---|---|---|---|---|
| E-GI-REPORT | AC1–AC5 | `verification/GRANT-ISSUER-1/REPORT.md` | `21fd47551` | `157012874e57577a91a0a4d0f07c0516bf4b6dc6352283f2b22ca6fa68612526` | CANONICAL |
| E-GI-LIST | AC1/AC2/AC3 | `verification/GRANT-ISSUER-1/command-list.json` | `21fd47551` | `d5c6d5455b2f724184fbd925be5c3c1f6d78b2a28664f6cccd808402257b9fbe` | CANONICAL |
| E-GI-PARITY | AC4 | `verification/GRANT-ISSUER-1/parity-update.json` | `21fd47551` | `cc54e5790eb278b3436f6e2a4b396a467c7768ac1251641ec5f7b98814a8fe97` | CANONICAL |
| E-GI-CHECK | AC4 | `verification/GRANT-ISSUER-1/parity-check.log` | `21fd47551` | `820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe` | CANONICAL |
| E-GI-CONTRACT | AC1/AC4 | `verification/GRANT-ISSUER-1/evidence/parity-contract.json` | `21fd47551` | `59d195e18f412ea6045a6fa951ee404fdd15f6820d4c2287cef8a9cce9dce130` | CANONICAL |
| E-GI-SHELL | AC2 | `verification/GRANT-ISSUER-1/evidence/real-shell-opened.json` | `21fd47551` | `89a4b411859e23b782b14241aa1f9663ebbf574fc538bef083aae9d9cd179769` | CANONICAL |
| E-GI-SCREEN | AC2 | `verification/GRANT-ISSUER-1/screens/01-plugins-directory-explorer.png` | `21fd47551` | `78b014e5fe43909bba4aa909cf9dcb2878dc306b69f39fea74354c0f48739e2e` | CANONICAL |
| E-GI-B1-UNION | AC4 | `verification/GRANT-ISSUER-1/evidence/ns-b1-integration.json` | `21fd47551` | `f946153f1f73f52d36b5665897bd69427e3ccaae8bee050586658634b5452e89` | CANONICAL |
| E-GI-S4-UNION | AC4 | `verification/GRANT-ISSUER-1/evidence/s4-region-reader-results.json` | `21fd47551` | `1ee022d47c6c69f47ea5f6c43d9e035c2c59a8ce1d1e43bc293c29fc8b188b7f` | CANONICAL |
| E-GI-DOTNET | AC4 | `verification/GRANT-ISSUER-1/dotnet-all.log` | `21fd47551` | `377fabfc082955da6ac95708a7274a846fbf009e934813f44bad3db57af7b7ba` | CANONICAL |
| E-GI-VITEST | AC4 | `verification/GRANT-ISSUER-1/vitest.log` | `21fd47551` | `37142b6e5236098d764c8b1086ac723c13c1f18d4bb0b91b5fc9ced73eb6795a` | CANONICAL |
| E-GI-PYTEST | AC4 | `verification/GRANT-ISSUER-1/pytest.log` | `21fd47551` | `d2cc3a3ac31ca0c96fc5462a117110d89f0846d5d495316957e41ae7fc5109a6` | CANONICAL |
| E-GI-PYTEST-IGNORE | AC4 | `verification/GRANT-ISSUER-1/pytest-ignore-broken.log` | `21fd47551` | `57a606877779db1334acdd4cd1c0bdbdb647fecaab2dfea4907adcd17445e329` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1 | `evidence-private/`（test.ps1 新鲜证据）、`evidence-real-shell/`、`real-shell-root/`（真机 shell 数据根，含 logs/plugins/exports） | 证据副本已复制到 `verification/GRANT-ISSUER-1/`；无真实用户数据；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（二次 rebase 后干净合并）

- rebase 到 d85c4173 后分支 499dd7c98；与 main（含 RUN-BINDING）合并**零冲突**；DSH 复跑 	est.ps1 **177/177**；parity --check 见执行记录（**55 IMPLEMENTED / 11 NOT_SUPPORTED**）；pytest 见执行记录（基线一致、0 新增）。
- grant 链路：OpenHostSession → HostIssuer 签名 grant（import=排序键压缩 JSON HMAC；export=\0 拼接串 HMAC）→ RegisterImportSource/RegisterExportTarget → ImportPages/StartExport；失败回滚 revoke。
- 成功样例：8 PNG 真实导入（imported_files=8、投影 8 页、grant registered=true）；Export grant 注册成功但 StartExport 仍 EXPORT_INPUT_UNAVAILABLE（fixture 无 translated 页，如实 BLOCKED）；越权 export → EXPORT_PATH_UNAVAILABLE。
- shell 动作：library_reveal_export_folder、plugins_open_directory（白名单；越权 C:\Windows → PLUGIN_DIRECTORY_UNAVAILABLE；真机 Explorer 截图）。
- 安全：仅 Host 铸造 grant（signing key 进程内随机不落盘）、路径/reparse/身份校验、export 限 data root/exports；TileChannel/资源通道零改动。
- 集成：941de7f5a。
## Manifest 补充

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| evidence-private | verification/GRANT-ISSUER-1/evidence-private/ | PRESERVE_REFERENCED | 同左 | test.ps1 新鲜证据 | 已核 |
| evidence-real-shell | verification/GRANT-ISSUER-1/evidence/real-shell-opened.json | PRESERVE_REFERENCED | 同左 | 文件 pin 见上表 | 已核 |
| real-shell-root | G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1/real-shell-root/ | PRESERVE_REFERENCED | 同左 | 真机 shell 数据根（logs/plugins/exports） | 已核 |
