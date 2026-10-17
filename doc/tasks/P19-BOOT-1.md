---
id: P19-BOOT-1
title: 修复 Core 自举：catalog 存在但命名空间锁/binding 缺失时首次运行崩溃（exit 101）
kind: bugfix
governance_version: 2
status: ready
approval: coordinator_release_20261017_from_P19_Dplus_first_step
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-CORE-1C]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
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
- [ ] **AC1 可启动（核心）**：在**"catalog 存在 + `derived/` 为空"**状态下，打包 sidecar **不得崩溃**；应用须**成功启动并可达四页 UI**（以真实启动验证，非仅单测）。
- [ ] **AC2 部分状态可恢复或失败关闭**：缺锁/binding 时走**受控首次绑定**（正确写入 binding）**或**返回**类型化错误**（失败关闭）——**不得**抛出裸 `FileNotFoundError`、**不得**崩溃、**不得**以误导性文案掩盖真实原因（现文案 "namespace busy (a managed peer holds a shared lease)" 与实际不符，须修正）。
- [ ] **AC3 损坏锁不致命**：锁文件为**空/非 JSON/绑定不可解析**时，行为须为**可恢复或类型化失败关闭**，**绝不**崩溃。
- [ ] **AC4 并发与租约语义不得放宽**：修复**不得**削弱既有命名空间保护（独占/共享租约、binding 身份校验、reparse point 检查、GC 启动顺序）；同机多实例的互斥语义须保持。
- [ ] **AC5 反例测试（补盲区）**：新增至少两类反例：① **catalog 存在 + `derived/` 为空**；② **锁文件为空/非 JSON**。断言"**可恢复或失败关闭**且**不崩溃**"，并注明与真实打包启动的对应关系。**不得**只测进程内路径而不声明与打包 sidecar 的差距。
- [ ] **AC6 交付**：固定 commit + Handoff + Canonical Evidence（`status: in_review`；`canonical_evidence_status: complete`；**BL-15/17/19/16(RV-P15-04)/18** 同前）。**必须附真实启动证据**（`exit code` + stderr + 应用窗口/UI 可达证明），不得只给单测结果。

## 允许 / 禁止范围
- **允许**：`src/bootstrap/**`、`src/infrastructure/resource_channel/**`、`tests/core/**`、本 Task、`doc/handoffs/P19-BOOT-1-*.md`、`verification/P19-BOOT-1/**`。
- **禁止**：改契约、Schema/迁移/依赖清单、`apps/desktop/**` 产品代码（如需 host 侧配合**先上报**）；**不得**削弱既有租约/绑定/GC 语义；**不得**用"预创建锁文件"之类的**外部脚本**冒充修复（修复须在产物内）；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`。

## 测试与证据
- Core 套件**不得回归**（基线 **508**）；新增 AC5 反例。
- **必做真实启动验证**：`cargo build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` → 启动 `target/debug/m2rc1-desktop.exe` → 记录 **exit code**、stderr、以及"**UI 可达**"证据；若环境受限须**如实声明**。
- 归档日志+退出码到 `verification/P19-BOOT-1/**`。

## 依赖、风险与阻塞
- **前置**：P15-CORE-1C（Core 面已交付）。**被阻塞方**：**P19**（D+ 验收须等本修复）；**P20**（发布）亦受本缺陷影响。
- 风险：把"跳过初始化"当作设计意图而**放宽保护** → AC4 为硬红线。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据 P19 D+ 首步的真实失败与缺陷报告。Handoff/Review/测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1 | verification/P19-BOOT-1/resource-manifest.json | 派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放与关闭时同步。