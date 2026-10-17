---
id: P19-UI-FIX-1
title: 修复两处 P1 用户可见缺陷：未开放分区可操作 + 导入作品无反应
kind: bugfix
governance_version: 2
status: done
approval: coordinator_release_20261017_from_P19_D_acceptance_findings
suggested_owner: Codex
owner: codex
reviewer: DeepSeek Harness
depends_on: [P15, P12]
base_commit: fe4e8662f293105615eb82a28c7091b0800fec15
branch: codex/P19-UI-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1
integration_commit: 8a0afacea
delivery_head: f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P19-UI-FIX-1
---

# P19-UI-FIX-1：两处 P1 用户可见缺陷

## 来源（P19 D 验收的真实产出）
1. **AC4 缺陷**（Codex R2 判 FAIL）：设置页 9 个「未开放」分区实测 `enabled=True`、可 Invoke、点击后页面变化 → **不满足"可见但不可操作"**。证据：`verification/P19/d-run-v2/uia/04-settings.uia.txt`、`trace.log`、`codex-review-r2.md`。
2. **导入缺陷**（本轮实测）：书架 `导入作品` 点击后 **10 次采样无任何选择器/无错误/无反馈** → 用户无法导入。证据：`verification/P19/import-no-response-r4.md`。

## Acceptance Criteria
- [x] **AC1 未开放分区真禁用**：9 个分类按钮使用原生 `disabled`、`aria-disabled` 和 guarded click；键盘分类导航跳过未开放项。9 项保留可见性与原因文案。真实 UIA 均 `IsEnabled=False`、`IsOffscreen=False`、Invoke blocked；见 `04-settings.uia.txt`、`uia-run.log`。
- [x] **AC2 导入必须可用或明确反馈**：`导入作品` 打开现有导入面板；空书架显示明确「未开放」原因，两个无目标的 picker 按钮按现有流程禁用。有效目标章节的 file/folder IPC 选择器路径由既有组件/client 测试覆盖；取消与失败状态可见，未隐藏导入入口。真实 GUI 的空书架反馈见 `import-open.uia.txt`。
- [x] **AC3 反例/回归测试**：增加设置页不可交互/键盘导航和空书架导入反馈测试，并覆盖导入错误反馈；前端 `npm test` **28 files / 277 passed / exit 0**，基线为 28 files / 274 passed。
- [x] **AC4 真实 GUI 复验**：强制重建 frozen sidecar，Cargo 刷新资源且 5 个 sidecar 可执行文件哈希一致；在隔离数据副本启动应用并采集 UIA。9 项 `IsEnabled=False`；点击导入后出现 5 个可见 UIA 元素，其中包含未开放原因；应用退出码 0。用户源数据四个文件前后哈希一致。
- [x] **AC5 交付**：实现提交与 Handoff 已固定，独立 Review 待 DeepSeek Harness；Task/Handoff 状态 `in_review`，`canonical_evidence_status: complete`，`resource_closeout_status: complete`。Evidence class 仅 `CANONICAL` / `SOURCE_PIN`；按磁盘字节计算 SHA256 并验证每个 commit:path 存在。

## 允许 / 禁止范围
- **允许**：`apps/desktop/frontend/**`（组件与测试）、`verification/P19-UI-FIX-1/**`、本 Task、`doc/handoffs/P19-UI-FIX-1-*.md`。
- **禁止**：改契约、Schema/依赖；改 `src/**`（若确需 Core/host 配合**先上报另立**）；**不得**用"去掉未开放分区"或"隐藏导入按钮"来规避缺陷（必须保留可见性）；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty。

## 测试与证据

| 场景/AC | 实际命令或步骤 | 前提/环境与被测 commit | 实际结果 | 证据 |
|---|---|---|---|---|
| AC3 前端套件 | `npm test`（`apps/desktop/frontend`） | Windows，`f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0` | PASS：28 files / 277 passed / exit 0；相较基线 274 passed 增加 3 项 | `verification/P19-UI-FIX-1/frontend-npm-test-final.log` |
| AC3 前端构建 | `npm run build`（`apps/desktop/frontend`） | 同上 | PASS：exit 0 | `verification/P19-UI-FIX-1/frontend-npm-build-final.log` |
| AC4 sidecar | `packaging/m2ac5/build_sidecar.ps1 -Force` | build log 绑定 HEAD `f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0` | PASS：exit 0 | `verification/P19-UI-FIX-1/sidecar-build-final.log` |
| AC4 frozen Tauri resources | `cargo build`（`apps/desktop/src-tauri`） | 同上 | PASS：exit 0；5/5 sidecar exe 与 frozen resource SHA256 相同 | `cargo-build-final.log`、`sidecar-resource-hash-comparison-final.json` |
| AC4 真实 GUI/UIA | `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File verification/P19-UI-FIX-1/run-uia.ps1` | debug exe；隔离 `target/p19-ui-fix-1-isolation-20261017`，设置 `NEWMANGA_DATA_ROOT` 与隔离 catalog/derived/managed roots | PASS：9/9 设置断言；导入反馈 5 个 UIA 元素；应用 exit 0 | `04-settings.uia.txt`、`import-open.uia.txt`、`uia-run.log`、`uia-run-wrapper.log` |
| 数据源保护 | GUI 前后对 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data,derived}` 做长度和 SHA256 对比 | 原始用户数据只读；仅启动克隆副本 | PASS：4/4 文件 unchanged | `appdata-source-before-with-derived.json`、`appdata-source-after.json`、`appdata-source-preservation-check.json` |

修复前后 UIA 对照见 [`uia-before-after-comparison.md`](../../verification/P19-UI-FIX-1/uia-before-after-comparison.md)。完整日志和已归档的失败诊断见 `verification/P19-UI-FIX-1/**`。

## 依赖、风险与阻塞
- **前置**：P15（设置页）、P12（书架导入面）。**被阻塞方**：P19 的 AC4/AC2。
- 风险：把"隐藏/删除"当修复 → AC1 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。
- 实现 commits：`528c6289c1ee8bb0c076056fb5cb47c9eba6c364`、`f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0`；固定 `delivery_head` 为后者。
- Evidence commit：`5dd4b2af0a0c1da00d49d7267ddac11d718cd94c`。Handoff：[P19-UI-FIX-1-f19275a](../handoffs/P19-UI-FIX-1-f19275a.md)，提交 `e6b35a2f6265d0c17fc12b462e1b390c3e79522d`。
- 状态：`in_review`；独立 Review 待 DeepSeek Harness，不代表已接受或集成。

## Canonical Evidence

本表 `sha256` 按对应路径的当前磁盘字节计算；对每条记录执行 `git cat-file -e <commit>:<path>` 确认路径存在。source pins 来自主仓 `fe4e8662f293105615eb82a28c7091b0800fec15` 的只读验收证据；SHA256 为磁盘字节，文本文件由 `core.autocrlf` 做正常化。`codex-review-r2.md` 在主仓观察时为既有 dirty 文件，因此仅作为原始报告链接引用，不作为 source pin；修复前事实由 UIA 转储和 trace 直接 pin。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| P19UI-TEST | AC3 | `verification/P19-UI-FIX-1/frontend-npm-test-final.log` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `2f6bd61d4acd94e6204278f276084b2261a57192cb129bec41cde9446088eba8` | CANONICAL |
| P19UI-FRONTEND-BUILD | AC3 | `verification/P19-UI-FIX-1/frontend-npm-build-final.log` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `80c9e7ebc60daf5c45635a57346f4114111248be10ebcd57749e3c628619fad6` | CANONICAL |
| P19UI-SIDECAR-BUILD | AC4 | `verification/P19-UI-FIX-1/sidecar-build-final.log` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `43481c84a651406eb2f17188ea66ef6bfa777c0fe58935c92ed5b6d3bf3d6ed6` | CANONICAL |
| P19UI-CARGO-BUILD | AC4 | `verification/P19-UI-FIX-1/cargo-build-final.log` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `a1be79b3172400a7f29f78b1e5117ac053a79063e3c10d1fe70242a0ec408e29` | CANONICAL |
| P19UI-SIDECAR-HASHES | AC4 | `verification/P19-UI-FIX-1/sidecar-resource-hash-comparison-final.json` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `dcfdc28fff13a3f5edfb0e5426a8cf3f3ecc47c5b9a4069e2f235256ab1fb27c` | CANONICAL |
| P19UI-SETTINGS-UIA | AC1, AC4 | `verification/P19-UI-FIX-1/04-settings.uia.txt` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `5c6401373059870d11f378a2a8d4161f405eb0c6605fba3a675d9b30b14c1e89` | CANONICAL |
| P19UI-IMPORT-UIA | AC2, AC4 | `verification/P19-UI-FIX-1/import-open.uia.txt` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `db3ebf3146eb8aae9f49513c7a53fd00be88a3155e68d63eca4e048814f4ac68` | CANONICAL |
| P19UI-UIA-TRACE | AC1, AC2, AC4 | `verification/P19-UI-FIX-1/uia-run.log` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `66bf6413c3981e2228734c1429ba44f9e2b50cf3f938b46e297423b8e7e9bde5` | CANONICAL |
| P19UI-DATA-PRESERVATION | AC4 | `verification/P19-UI-FIX-1/appdata-source-preservation-check.json` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `43f817472f8daf97694620b90bc33a7edf623d2c9271ee3f940f3ea4da84f623` | CANONICAL |
| P19UI-UIA-COMPARISON | AC1, AC2, AC4 | `verification/P19-UI-FIX-1/uia-before-after-comparison.md` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `50a115681b9e45ca500fe167e0fcd29583298c7da2269075c3a7b6c9d6d5309e` | CANONICAL |
| P19UI-RUNNER | AC4 | `verification/P19-UI-FIX-1/run-uia.ps1` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `908564083bd05b7ebe374e353a8d5784767bc23b92e1ff5e17e52ed030c4a092` | CANONICAL |
| P19UI-ISOLATION-REBIND | AC4 | `verification/P19-UI-FIX-1/rebind-isolated-namespace.py` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `389dae0374c3801412ad971b5c54285308cfde878cb7e0c0874a52f1a9ff8a70` | CANONICAL |
| P19UI-RESOURCE-MANIFEST | AC5 | `verification/P19-UI-FIX-1/resource-manifest.json` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `d40280e1653e75ccdff74979a4a58dffe7feae8de4402a06abac194241e61110` | CANONICAL |
| P19UI-HANDOFF | AC5 | `doc/handoffs/P19-UI-FIX-1-f19275a.md` | `e6b35a2f6265d0c17fc12b462e1b390c3e79522d` | `8c8c741f6ae8f95279dd4caaa8362737ae454eb0ce6b2038463ccdaac92a38f4` | CANONICAL |
| P19UI-BEFORE-SETTINGS | AC1, AC4 | `verification/P19/d-run-v2/uia/04-settings.uia.txt` | `fe4e8662f293105615eb82a28c7091b0800fec15` | `d11954c503ac7f526b0edf07f77a1d057871a6c688782df4946c23f167e505a1` | SOURCE_PIN |
| P19UI-BEFORE-TRACE | AC1, AC4 | `verification/P19/d-run-v2/trace.log` | `fe4e8662f293105615eb82a28c7091b0800fec15` | `6ce28ef237c08b93017d394c50e93fad2cc898f27c5ce6269ad1abfd540e12c9` | SOURCE_PIN |
| P19UI-BEFORE-IMPORT | AC2 | `verification/P19/import-no-response-r4.md` | `fe4e8662f293105615eb82a28c7091b0800fec15` | `05cb83b7bcbe8e5ae339e933cef4d98c4d47fe3b931aca602ec0f2c903a3a83f` | SOURCE_PIN |

## Resource Manifest

见 [`resource-manifest.json`](../../verification/P19-UI-FIX-1/resource-manifest.json)。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖；`build_sidecar.ps1 -Force` 清理的外部 PyInstaller 缓存已在资源清单与 Handoff 风险中明确登记。

## Closeout Record

- 关闭：2026-10-17（dsh）。Reviewer=dsh（批准，erification/P19-UI-FIX-1/dsh-review-r1.md）。
- 交付 done；合并 8a0afacea（--no-ff，无冲突）。
- 复核要点：未开放分区 IsEnabled=False+Invoke=blocked 且可见性与原因保留；导入改显式可见反馈（非静默）；前端 274 采信 Owner 日志（我本人 -4058 未复现，已登记）。
- 遗留：P19 主流程验收须记录「空书架无法导入」这一产品约束；前端套件需 R3 独立复跑。
