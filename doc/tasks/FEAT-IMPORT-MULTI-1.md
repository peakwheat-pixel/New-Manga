---
id: FEAT-IMPORT-MULTI-1
title: 页面导入支持多选与文件夹导入（用户要求：一次多张 / Ctrl+A 全选 / 直接导文件夹）
kind: feature
governance_version: 2
status: done
approval: user_requirement_20261017_multi_select_and_folder_import
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [FEAT-CREATE-4]
base_commit: f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f
branch: codex/FEAT-IMPORT-MULTI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-IMPORT-MULTI-1
integration_commit: eac2630920b5780e77e1b6303c530aedbe7fb62d
delivery_head: 8b1a1da1774d418ed7e28ac6eb983028cf73b74b
canonical_evidence_status: registered
resource_closeout_status: complete
evidence_dir: verification/FEAT-IMPORT-MULTI-1
---

# FEAT-IMPORT-MULTI-1：多选 + 文件夹导入

## 来源（用户 2026-10-17 明确要求）
> "我要的是一次能选择很多张，甚至可以 alt+a 进行全选然后导入。尤其需要直接导入文件夹。现在的状态是一次只能选一张。"

**代码层核实**：
- `apps/desktop/src-tauri/src/main.rs:873` 使用 **`blocking_pick_file()`（单选）** → 与"一次只能选一张"一致 → **缺口确认**
- `main.rs:895` 使用 `blocking_pick_folder()`；Core 有 `handle_import_pages`，host 有 `library_import_file`/`library_import_folder` → **文件夹导入能力已存在**，需按用户期望完善语义与入口

## Acceptance Criteria
- [x] **AC1 多选文件**：`📄 选择图片 / PDF 文件` 必须允许**多选**（改为 `blocking_pick_files()` 或等价），一次选择**多张**后**逐张导入**并汇总结果；单次操作的**总页数增量 = 所选文件数**（重复内容按既有 `duplicate_policy` 处理并如实回报跳过数）。
- [x] **AC2 全选可用**：系统对话框内 **`Ctrl+A`（或 `Alt+A`）全选**后确认，能导入文件夹内**全部**图片（不得因逐个 `invoke` 导致超时/部分失败；需汇总成功/失败/跳过）。
- [x] **AC3 直接导入文件夹**：`📁 选择图片文件夹` 选中一个文件夹即导入其中全部图片；依冻结规则仅读取直接子项，不递归子目录；结果汇总同上。
- [x] **AC4 结果可见**：导入完成后界面必须显示**成功数 / 跳过数（重复）/ 失败数及原因**（脱敏，遵守 §5.10 与封闭错误投影）。
- [x] **AC5 安全与契约**：不得让前端直接读文件系统或任意路径；必须经既有 host 命令与 Core；不得回显绝对路径/Secret；**不得**下调既有校验。
- [x] **AC6 测试**：前端（多选映射、汇总渲染、失败脱敏）+ host 侧（多文件/文件夹解析与逐项调用）；基线：前端 **285 / 28 files**、Rust source **108 / 0 failed / 1 ignored**（旧 107 + 本 Task 新增 1 个 host 聚合测试）、packaged **12 / 0 failed**、Core **536**；均须保持。
- [x] **AC7 真实 GUI 复验（必做）**：重建产品（`npm run build` → `build_sidecar.ps1 -Force` → `cargo build`，**校验 bundle==resource hash 一致**）+ 隔离 `NEWMANGA_DATA_ROOT`（**不改用户数据**）→ 实测：多选 2 张 → 页数 +2；文件夹导入 → 页数 = 文件夹内图片数。留 UIA/窗口证据与退出码。
- [x] **AC8**：commit + **Handoff（必须）** + Canonical Evidence（`status: done`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`apps/desktop/src-tauri/**`、`apps/desktop/frontend/**`、本 Task、`doc/handoffs/FEAT-IMPORT-MULTI-1-*.md`、`verification/FEAT-IMPORT-MULTI-1/**`。
- 禁止：修改 `src/**` Core；改契约（wire 若需新增字段 → **停下上报**）；Schema/迁移/依赖；改 STATUS/PLAN；触碰主仓既有 dirty（本轮起始 tracked 改动数为 43）或其他 worktree 的未提交文件；**不得**用"循环调用单文件导入"掩盖超时/失败（AC1/AC2 要求汇总与如实回报）。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-4（done）。**被阻塞方**：P19 的 AC2 主流程（多页场景与翻页验证）。
- 风险：逐个 `invoke` 造成长时间阻塞 → 需明确进度/汇总与失败隔离。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据用户明确要求。

## Owner closeout（2026-10-18）

- 本节更新并取代 2026-10-17 checkpoint 的“等待构建/GUI 批准”状态；历史 checkpoint 与 r1 失败产物仍保留。
- **AC1/AC2**：原生多选对话框 Ctrl+A 选中 2/2 个不同 PNG，单次批量导入报告 `2 imported / 0 skipped / 0 failed / 0 pending`，章节页数 `0→2`。
- **AC3**：新隔离根 `%TEMP%\feat-import-multi-r2` 的文件夹含 3 个直接子项 PNG，导入后页数 `2→5`（增量 3）。确认阶梯 trace：level 1 `InvokePattern.Invoke` 未关闭；level 2 UIA 边界框中心真实鼠标点击关闭；level 3/4 因已成功未执行。GUI runner 与 App exit code 均为 0。
- **AC4**：UIA 报告显示多选 `2/0/0/0`、文件夹 `3/0/0/0`（导入/跳过/失败/待处理）；UIA 转储和截图均已入库。
- **AC5**：无 Core、wire、Schema、migration 或 dependency 变更；前端继续经既有 Tauri host grant 与 Core batch import；路径/Secret 与原始错误不回显；既有校验保持。
- **AC6**：Core **536 passed**；前端 **285 passed / 28 files**；Rust source **108 passed / 0 failed / 1 ignored**；packaged **12 passed / 0 failed / 0 ignored**。Rust source 为旧 107 + 本 Task 新增的 1 个 host 聚合测试。唯一 ignored=`perf_chunk_request_digest_cost`，源码将其标为显式性能测量，不属于默认功能套件；packaged 测试另行执行。
- **AC7**：`npm run build`、使用 `%TEMP%\feat-import-multi-pyinstaller` 的 `build_sidecar.ps1 -Force`、`cargo build` 全部 exit 0。Bundle/resource `core_service.exe` SHA-256 均为 `e8f682225b22be879c0722f1d0ef48a987e32ed103a93a389117cd0d68ff26f0`。GUI 使用只读复制的真实 `{catalog,data}` 与空 derived/runtime 根；前后 AppData hash 一致；最终 DB 页数 5；`m2rc1-desktop` 进程数 0。
- **AC8**：delivery commit=`8b1a1da1774d418ed7e28ac6eb983028cf73b74b`；Handoff=`[FEAT-IMPORT-MULTI-1-8b1a1da17](../handoffs/FEAT-IMPORT-MULTI-1-8b1a1da17.md)`；Canonical Evidence 已登记。当前状态 `in_review`，不代表独立 Review、approved 或 done。
- PyInstaller 第一次使用默认 `%LOCALAPPDATA%\pyinstaller` 缓存时，工具清理了可再生缓存并以 exit 1 中断；未尝试恢复或再次清理。随后在 Coordinator 批准的一次性 `%TEMP%\feat-import-multi-pyinstaller` 配置下构建 exit 0。详情见 Handoff 与原始日志。
- 主仓 `G:\CODEX\New Manga` 最终只读复核：HEAD=`a0dba45198eb6cf547809778586535fc67b3f3c4`，tracked dirty=`43`；Tauri 自动生成 schema/permission 路径状态=`0`。主仓未写入；未 push/merge。
- 逐套件命令头、环境、退出码，构建日志、runner trace、UIA 转储/截图与数据保护证据见 [`closeout-r1/`](../../verification/FEAT-IMPORT-MULTI-1/closeout-r1/)。
- 独立 Review 尚未运行；Reviewer=`DeepSeek Harness`。不得把 Owner 的实现与 GUI 复验称为独立复核。
## 实现约束确认
- 文件多选和文件夹导入均由 Tauri 原生选择器取得路径；Host 为每项签发 grant，并在**一次** `ImportPages` 请求内传入 `sources` 数组，由 Core 逐项处理，避免前端循环 invoke 与重复超时。
- 聚合仅输出既有 `ImportSummary` 字段：`imported_files`、`skipped_files`、`rejected_files`、`pending_files`、`cancelled`；不新增 wire/响应字段，也不回传 Core 原始路径或错误详情。
- 文件夹只包含所选目录直接子项，支持既有图片扩展名过滤；不递归子目录。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-IMPORT-UI | AC1/2/4/5 | `apps/desktop/frontend/src/bookshelf/ImportDialog.tsx` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `67692d903cd75c2e9984d6220466dfa2e3ee08779f2df19d2e0d700967bcf715` | CANONICAL |
| EVID-IMPORT-UI-TEST | AC2/4/6 | `apps/desktop/frontend/src/bookshelf/BookshelfPage.test.tsx` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `16da9232110ccc0504791ba1051b720af7bbac3f76034def3aba01ad1364b329` | CANONICAL |
| EVID-IMPORT-TAURI | AC1/2/3/5 | `apps/desktop/src-tauri/src/main.rs` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `b9d74da3f483c9eed8e9e8c2fa8102092fb844834362d407e73c1d121bca6e85` | CANONICAL |
| EVID-IMPORT-BRIDGE | AC1/3/5/6 | `apps/desktop/src-tauri/src/library_bridge.rs` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `3a21e06c0a6890d010832a9cb46e1e7c8912119d5305787f95f114ca6aff04e5` | CANONICAL |
| EVID-IMPORT-GRANT | AC1/3/5/6 | `apps/desktop/src-tauri/src/host_issuer.rs` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `2ad3739dcd4526a1cfc1b3786105c00ad798117857487c58c0ec3469e2ba5a68` | CANONICAL |
| EVID-IMPORT-PACKAGED-TEST | AC6 | `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `babaf8c3d9fe174eecfc49232d012e3fa51ebbe0cb57cfef5e22c949d7caaa1b` | CANONICAL |
| EVID-IMPORT-CORE-TEST | AC6 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/core-pytest.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `7d5435de73c6e5d20acc35eb5dd1545312e6d0319a9214ef6e6ae3238e79550d` | CANONICAL |
| EVID-IMPORT-FRONTEND-TEST | AC6 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/frontend-npm-test.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `17449448956b2d685232eaa345d6c1630bdacf5339711493fe657f3fbbd6d4ac` | CANONICAL |
| EVID-IMPORT-RUST-SOURCE | AC6 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/rust-source-tests.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `8c7e23463208c5873ce0f06f50791cb5661a780b84eb1a026df1cb0d32f622bb` | CANONICAL |
| EVID-IMPORT-RUST-PACKAGED | AC6 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/rust-packaged-tests.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `b461c4c29cf925880373f0f63678e79955b37183420c4314dea7ecf65230f7af` | CANONICAL |
| EVID-IMPORT-FRONTEND-BUILD | AC7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/frontend-npm-build.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `a0fdecc3ae3c874c655189de8071c7fd22de49730b11080afea2ce3c6efea04c` | CANONICAL |
| EVID-IMPORT-SIDECAR-BUILD | AC7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/sidecar-build-attempt-2.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `2553048a5cb178520c2fdb4a07a09f336c09e74fc7415bc26ef728ecde591671` | CANONICAL |
| EVID-IMPORT-CARGO-BUILD | AC7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/cargo-build.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `fada90d4077fb510bc101b37a7478d0b3749387ccfc882e0ca918f37b3f5efeb` | CANONICAL |
| EVID-IMPORT-SIDECAR-HASH | AC7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/sidecar-resource-hash.json` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `dfdec9556bd2426ae3c52a2ae8e2117133001f71be0277998d3fac28ce960fe5` | CANONICAL |
| EVID-IMPORT-CACHE-INCIDENT | Risk | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/sidecar-build.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `bbec44a4bf9a2eab90153c388895a3cead57bd4062ae3a15a81a75b4ebc56987` | CANONICAL |
| EVID-IMPORT-GENERATED-RESTORE | AC5/AC8 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/generated-restore.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `ca705b679f7901902f39a0395d5dcca29a320d85ea87edfb165055155b02d1c6` | CANONICAL |
| EVID-IMPORT-GUI-TRACE | AC1/2/3/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/uia-run.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `708b5c2a5bed33355c07588ec7dd57fa29a5357f06fc4f9253b3a59fab86a5bf` | CANONICAL |
| EVID-IMPORT-GUI-CONSOLE | AC7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/gui-runner-console.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `2697cab4fcf924eae2e7bfa71e84e085dfeb9c244f828381e4e8c2cf346f91d0` | CANONICAL |
| EVID-IMPORT-GUI-MULTI-UIA | AC1/2/4/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/multi-select-result.uia.txt` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `f4fb1c4eea8e8d90182beb11447aabb142788063922ce3b1ea5e4c2d442f041a` | CANONICAL |
| EVID-IMPORT-GUI-MULTI-SCREEN | AC1/2/4/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/multi-select-result.uia.png` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `53821e52fdbb4eb54b862f360ba5f9a7f5b9c2c8137dc04ee7024e98deeac083` | CANONICAL |
| EVID-IMPORT-GUI-FOLDER-UIA | AC3/4/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/folder-result.uia.txt` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `bb21150f252a636082a7055e256c5f1bd69af6a7321a2246f7f28b5621829103` | CANONICAL |
| EVID-IMPORT-GUI-FOLDER-SCREEN | AC3/4/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/folder-result.uia.png` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `78085ed88ae3341a4cc7ac54b73fa6820c4bd72e7ef7fb04f512a0defb0e789c` | CANONICAL |
| EVID-IMPORT-GUI-FIXTURES | AC1/3/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/fixture-hashes.json` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `a7f7ee602404328cb90ff086f5486adef088a80719703a653190a69182be2176` | CANONICAL |
| EVID-IMPORT-GUI-PAGES | AC1/3/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/page-count-final-r2.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `ba46c078c3b0ba5cd57f3fa2e66a0aa891dd6f4a336c3084bacfe707eb2563a7` | CANONICAL |
| EVID-IMPORT-GUI-APPDATA | AC5/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/gui-run-r2/appdata-source-after.json` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `ff9cec08c1c20c0f21f6fe9c3c9797c6a79ae9c07c2eba19f83d75779adb293a` | CANONICAL |
| EVID-IMPORT-APPDATA-VERIFY | AC5/7 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/verify-appdata-unchanged-r2.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `12b931f8dfc0c0d37ae99e1a7839fb9dc130c9d213fb4f9bad118391b7c861e7` | CANONICAL |
| EVID-IMPORT-SAFETY | AC5/8 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/final-safety-r2.log` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `c3e1003e576e68efebed8f499917dc7725a39c7fbc6e399df842814d0d438c91` | CANONICAL |
| EVID-IMPORT-CHECKPOINT | Recovery | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/checkpoint-r2.md` | `8b1a1da1774d418ed7e28ac6eb983028cf73b74b` | `f3c3533df0157afd61b5d3f1d9909c127422c9ae70fb17a4975a33c98a873b31` | CANONICAL |
| EVID-IMPORT-HANDOFF | AC8 | `doc/handoffs/FEAT-IMPORT-MULTI-1-8b1a1da17.md` | `2795f5febe2ff3d7bad1f0f762edaa401cdbc8da` | `51e3385f26f32e64c904f6f3eaa85b58c678f566536335492cd72cd770db5b20` | CANONICAL |

Task 文件自身不列入自身 hash 表，避免自引用。表中 SHA-256 按当前 worktree 磁盘字节计算；`commit` 使用包含对应文件的完整 `git rev-parse HEAD` 值。`CANONICAL` 仅表示本次交付证据，不代表独立 Review 已通过。