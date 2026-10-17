---
id: P19-BOOT-1
title: 修复 Core 自举：catalog 存在但命名空间锁/binding 缺失时首次运行崩溃（exit 101）
kind: bugfix
governance_version: 2
status: in_review
approval: coordinator_release_20261017_from_P19_Dplus_first_step
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P15-CORE-1C]
base_commit: 04d7beedc4a390ff67130eab0baa5b5ee78140cc
branch: codex/P19-BOOT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1
integration_commit: null
delivery_head: c44b47dd9852121e18496502870f4e4cbaf5c737
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/P19-BOOT-1
---

# P19-BOOT-1：修复 Core 自举的部分初始化崩溃

## 来源（**为什么需要**）
**P19 的 D+（真实 WebView2 + CDP）验收第 1 步**（启动打包应用）即失败：`m2rc1-desktop.exe` **立即退出 exit 101**。完整复现、代码定位与证据见 **[verification/P19/boot-defect-r1.md](../verification/P19/boot-defect-r1.md)**（发现者 dsh，2026-10-17）。

**根因（已定位到行）**：`src/bootstrap/core_service.py` **L3337** 以"`catalog.sqlite` 是否存在"判定"命名空间是否已初始化"，但二者可**不一致**：

```python
L3337: if not catalog_db.exists():
L3338:     initialize_namespace(catalog_db, derived_root)      # 唯一会创建锁+binding 的路径 → 被跳过
L3340: exclusive = try_acquire_exclusive_lease(...)           # "try" → 缺锁静默降级，打印误导性 namespace busy
L3368: shared_lease = acquire_shared_lease(...)               # 缺锁 → FileNotFoundError 未捕获 → 崩溃
```

`handle_resolver.py` **L640** `disposition = CREATE_NEW if create_new else OPEN_EXISTING`；**L644-647** 缺文件即 `raise FileNotFoundError`；唯一 `CREATE_NEW` 路径 `open_exclusive_lock_for_initialize`（**L769-777**）仅由被跳过的 `initialize_namespace` 调用。
第二实验：预创建**空**锁后失败点变为 `_read_lock_binding` 的 `JSONDecodeError` → 证明锁是**承载 JSON NamespaceBinding 的绑定载体**，**仅创建文件不足以修复**。

## Acceptance Criteria
- [x] **AC1 可启动（核心）**：真实 Cargo debug host 在**"catalog 存在 + `derived/` 为空"**状态下启动成功，Python Core source sidecar 未崩溃；WebView2 实际到达四页，见真实窗口截图。冻结 sidecar/安装包的验证边界见执行记录。
- [x] **AC2 部分状态可恢复或失败关闭**：缺锁时受控首次绑定并写入 binding；共享租约入口将竞态下缺锁转为 `TypedResourceChannelError`。真实 stderr 无裸 `FileNotFoundError` 或旧的误导性 busy 文案。
- [x] **AC3 损坏锁不致命**：空、非 JSON、绑定不可解析锁从已验证的 catalog binding 恢复；身份不匹配时以类型化错误失败关闭且不覆盖损坏锁。
- [x] **AC4 并发与租约语义不得放宽**：恢复继续使用独占锁句柄、canonical schema/row 检查、路径与 volume/file identity 校验；现有 reparse point 检查、共享/独占 share mode、GC 启动顺序未放宽。
- [x] **AC5 反例测试（补盲区）**：覆盖 catalog 存在且 `derived/` 为空、缺锁类型化失败、空/非 JSON/不可解析锁、binding identity mismatch；进程内测试与真实 Tauri debug host/source sidecar 启动的差距已在 Handoff 和证据中说明。
- [x] **AC6 交付**：固定实现 head、Handoff 与 Canonical Evidence 已归档；真实运行记录 exit code、stderr、UIA WebView 标题和四页窗口截图。

## 允许 / 禁止范围
- **允许**：`src/bootstrap/**`、`src/infrastructure/resource_channel/**`、`tests/core/**`、本 Task、`doc/handoffs/P19-BOOT-1-*.md`、`verification/P19-BOOT-1/**`。
- **禁止**：改契约、Schema/迁移/依赖清单、`apps/desktop/**` 产品代码（如需 host 侧配合**先上报**）；**不得**削弱既有租约/绑定/GC 语义；**不得**用"预创建锁文件"之类的**外部脚本**冒充修复（修复须在产物内）；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`。

## 测试与证据
- Core 套件**不得回归**（基线 **508**）；新增 AC5 反例。
- **必做真实启动验证**：`cargo build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` → 启动 `target/debug/m2rc1-desktop.exe` → 记录 **exit code**、stderr、以及"**UI 可达**"证据；若环境受限须**如实声明**。
- 归档日志+退出码到 `verification/P19-BOOT-1/**`。

## 执行记录

- Owner：Codex；Reviewer：DeepSeek Harness（待独立审查）。基线 `04d7beedc4a390ff67130eab0baa5b5ee78140cc`；分支 `codex/P19-BOOT-1`；worktree 为本任务 worktree。
- 实现 commits：`daabedccd101b1993bbaf33f78d4dd1092fbb670`（修复自举恢复）、`607595165e722425030f031e56bec15c60bf51d4`（共享租约缺锁转类型化错误）及 `c44b47dd9852121e18496502870f4e4cbaf5c737`（长损坏锁截断反例）；固定 `delivery_head=c44b47dd9852121e18496502870f4e4cbaf5c737`。
- Core 套件：`G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe -m pytest tests/core -q -p no:cacheprovider`，`515 passed, 0 skipped, 1 warning`，exit `0`；基线 `508`，净增 7 个测试通过。唯一 warning 是既有 Pillow `Image.Image.getdata` deprecation。
- Cargo 必需构建及嵌入前端的 `tauri/custom-protocol` 构建均 exit `0`；`npm run build` exit `0`。
- 真实启动：运行 `target/debug/m2rc1-desktop.exe`，隔离 `APPDATA` 在 `verification/P19-BOOT-1/runtime-final6`；进程 exit `0`，stderr 有 GC 完成记录且无 `FileNotFoundError`、`JSONDecodeError`、误导性 busy 文案；UIA 标题确认 React/WebView 已交互，四页截图齐全。启动后 lock JSON 与唯一 catalog binding row 及两条文件身份完全匹配。
- 真实运行形态：Cargo debug host + 通过 `M2RC1_SRC_ROOT` 加载的本 worktree Python Core source sidecar。未验证冻结 PyInstaller sidecar/安装包。既有 `target/core-sidecar` junction 指向共享主仓库 target；删除该 junction 的操作被自动审批策略拒绝，未改动 junction 或主仓库。详见 [真实启动证据](../../verification/P19-BOOT-1/real-startup-evidence.md)。
- 测试命令、构造状态、完整 stderr、截图和 SHA-256 目录见 [Canonical Evidence Manifest](../../verification/P19-BOOT-1/evidence-manifest.json)。

## 依赖、风险与阻塞
- **前置**：P15-CORE-1C（Core 面已交付）。**被阻塞方**：**P19**（D+ 验收须等本修复）；**P20**（发布）亦受本缺陷影响。
- 风险：把"跳过初始化"当作设计意图而**放宽保护** → AC4 为硬红线。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据 P19 D+ 首步的真实失败与缺陷报告。`in_review` 交付 head 固定为 `c44b47dd9852121e18496502870f4e4cbaf5c737`。
- Handoff：[P19-BOOT-1-c44b47dd](../handoffs/P19-BOOT-1-c44b47dd.md)。Review：等待 DeepSeek Harness 对固定 delivery head 独立审查。
- 当前为 in_review；尚未集成，不能标记为 `done`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| core-suite | AC2–AC5 / Gate | verification/P19-BOOT-1/core-suite.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 0f4186fa8408caa8cdbb3bd5a9bde01f0b18a784f18fe5334c8c36e4fa6e77be | CANONICAL |
| cargo-build | AC1 / Gate | verification/P19-BOOT-1/cargo-build.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 0473d6b5106ed4b83e33a31a2eb6c78424da36909abf3e7d30e2a4badc1fd3fd | CANONICAL |
| cargo-build-custom-protocol | AC1 / Gate | verification/P19-BOOT-1/cargo-build-custom-protocol.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 4346f72f751e7107e18a25b7a88ac4562945a2d39dcddc12630d89d92c8785cc | CANONICAL |
| frontend-build | AC1 / Gate | verification/P19-BOOT-1/frontend-build.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | b067992b1a1ea3f0be33c9d17ed3c83c5ccfe8be1b4b4bae8febdcab6738ebbb | CANONICAL |
| partial-state-fixture | AC1, AC5 | verification/P19-BOOT-1/partial-state-runtime-final6.json | c44b47dd9852121e18496502870f4e4cbaf5c737 | 4e808a696575d832ceab115f9ed55200516842b224eefe586abcea789deaf209 | CANONICAL |
| partial-state-setup-log | AC1, AC5 | verification/P19-BOOT-1/partial-state-runtime-final6-run.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 6b08563180d13205b27980a695098e197f1031c80ef48aea7d05725777001941 | CANONICAL |
| real-startup-launch | AC1, AC6 | verification/P19-BOOT-1/real-startup-launch-final.json | c44b47dd9852121e18496502870f4e4cbaf5c737 | fab6551fde639b5e71bd66986548244f11bb8025eec8cf6a59070dbacb8524fe | CANONICAL |
| real-startup-result | AC1, AC6 | verification/P19-BOOT-1/real-startup-final.json | c44b47dd9852121e18496502870f4e4cbaf5c737 | 2661c53d8d14e2689ae061e4fac5bb1d009c4bc076fc9f7586e3eb653486df43 | CANONICAL |
| real-startup-log | AC1, AC6 | verification/P19-BOOT-1/real-startup-final-run.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 30a0873d5c57f4932a57cda06d73afad4a72612c4157a703accc80e6397c14de | CANONICAL |
| real-startup-stderr | AC1, AC2, AC6 | verification/P19-BOOT-1/final-app.stderr.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | 90a6f1b65e49bb38103b344c95493581fd6221136fffe9d7b77954080b4fad34 | CANONICAL |
| runtime-binding | AC2, AC3 | verification/P19-BOOT-1/runtime-binding-final.json | c44b47dd9852121e18496502870f4e4cbaf5c737 | 8f909b1ada972f3577aaa205b437d556b157f37f98927b0f0d8e0dc677440b4d | CANONICAL |
| runtime-binding-log | AC2, AC3 | verification/P19-BOOT-1/runtime-binding-final-run.log | c44b47dd9852121e18496502870f4e4cbaf5c737 | d8fe3e2fb834fafac77c73dbc66dc12f49ab508d80153f33a0f76be7ae2b12ed | CANONICAL |
| ui-bookshelf | AC1, AC6 | verification/P19-BOOT-1/ui-bookshelf-real-window.png | c44b47dd9852121e18496502870f4e4cbaf5c737 | cb373d919c2e8651b76d23c5afdc6830d74a2b2594b4e0c73dc578d6247a4848 | CANONICAL |
| ui-workbench | AC1, AC6 | verification/P19-BOOT-1/ui-workbench-real-window.png | c44b47dd9852121e18496502870f4e4cbaf5c737 | 73d63aa14eff087372959e1b5669d93b25e36a8744a6d2dd20bc6799779e9c44 | CANONICAL |
| ui-reader | AC1, AC6 | verification/P19-BOOT-1/ui-reader-real-window.png | c44b47dd9852121e18496502870f4e4cbaf5c737 | 4de460a24e1a94d31c25dec927dd878b86be074b7ce950c00aeffcd7fd5b6773 | CANONICAL |
| ui-settings | AC1, AC6 | verification/P19-BOOT-1/ui-settings-real-window.png | c44b47dd9852121e18496502870f4e4cbaf5c737 | 6406b3766df95f0d3ac7d9dee81dd78248f14d402f2462d73588d193e8b0c455 | CANONICAL |
| startup-evidence-narrative | AC1, AC6 | verification/P19-BOOT-1/real-startup-evidence.md | c44b47dd9852121e18496502870f4e4cbaf5c737 | 236f64c1012f796295e07c362ce3797f46fa8757e2799e6258dc11eaa52f621e | CANONICAL |
| partial-state-setup-script | AC1, AC5 | verification/P19-BOOT-1/prepare_partial_state.py | c44b47dd9852121e18496502870f4e4cbaf5c737 | b8ae573afcd8de80c8460f2199a4a3faaa4af9148004972158e694aab3ec9129 | CANONICAL |
| real-window-capture-script | AC1, AC6 | verification/P19-BOOT-1/capture_real_startup.ps1 | c44b47dd9852121e18496502870f4e4cbaf5c737 | 656a6e07f3ac22729f47afa6821e79db9e22d9adb95fd6f601a028a6004b5f7b | CANONICAL |
| binding-check-script | AC2, AC3 | verification/P19-BOOT-1/verify_runtime_binding.py | c44b47dd9852121e18496502870f4e4cbaf5c737 | 1e02419f59343b8f8cd97e679eaf85f06d9a7b4ba7c7bde8eee1750a80385c0b | CANONICAL |
| evidence-manifest | AC6 | verification/P19-BOOT-1/evidence-manifest.json | c44b47dd9852121e18496502870f4e4cbaf5c737 | a7c269b7145b098d41aef3923b6b2a9f71adda6520ca55192e9e9cf2605d5619 | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1 | verification/P19-BOOT-1/resource-manifest.json | 派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`complete`。resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：独立 Review、Codex 集成与集成后验证尚未完成；当前状态 `in_review`。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放与关闭时同步。
