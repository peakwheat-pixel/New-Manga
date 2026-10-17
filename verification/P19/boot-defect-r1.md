# P19 验收阻断缺陷 R1：干净/部分状态首次运行无法启动（exit 101）

| 项 | 值 |
|---|---|
| 发现者 | dsh（P19 D+ 真实 WebView2 + CDP 验收第 1 步：启动应用即失败） |
| 发现日期 | 2026-10-17 |
| 严重度 | **阻断（release blocker）**：**打包应用在该状态下完全无法启动**，四页 UI 不可达 |
| 被测产物 | `apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe`（15.4MB，sha256 `aa32baa1eae9499d45f5a2a73540d05de80c60069599d06f6d20479694bb5027`），由 `157e00f67` 构建（`cargo build --locked`，22.95s，exit 0） |
| 状态 | **未修复**；P19 的 D+ 验收在此修复前无法继续 |

## 1. 现象与复现（可重放）

```powershell
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS='--remote-debugging-port=9222'
Start-Process apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe -PassThru
# 结果：进程立即退出，exitCode = 101
```

**stderr（原文，见 [`boot-defect-stderr-run1.log`](boot-defect-stderr-run1.log) / [`boot-defect-stderr-run2.log`](boot-defect-stderr-run2.log)）**：

```text
[core.derived_gc] skipped: namespace busy (a managed peer holds a shared lease)
Traceback (most recent call last):
  File "entry_core_service.py", line 10, in <module>
  File "bootstrap\core_service.py", line 3239, in main
  File "infrastructure\resource_channel\handle_resolver.py", line 734, in acquire_shared_lease
  File "infrastructure\resource_channel\handle_resolver.py", line 647, in _open_lock_handle
FileNotFoundError: C:\Users\49745\AppData\Roaming\com.newmanga.m2rc1.desktop\derived\.preview-lifecycle.lock
[PYI-22224:ERROR] Failed to execute script 'entry_core_service' due to unhandled exception!

thread 'main' panicked at src\main.rs:1168:10:
production core library sidecar failed to start (startup ping): LibraryError { code: "CORE_UNAVAILABLE", ... }
```

**两次独立启动（run1/run2）结果一致：exit 101** ✓ 可复现。

## 2. 现场状态（关键）

`%APPDATA%\com.newmanga.m2rc1.desktop\`：

| 路径 | 状态 |
|---|---|
| `catalog\catalog.sqlite` | **存在**（12288B） |
| `data\library.db` | **存在**（311296B） |
| `data\managed\temp` | 存在（空） |
| **`derived\`** | **存在但为空** → **`.preview-lifecycle.lock` 缺失** |
| `managed\` | 存在（空） |

→ 即"**catalog 已存在、命名空间未绑定**"的**部分初始化**状态。

## 3. 根因（代码级，已定位到行）

```python
# src/bootstrap/core_service.py
L3337:  if not catalog_db.exists():
L3338:      initialize_namespace(catalog_db, derived_root)   # ← 仅在 catalog 缺失时初始化
L3339:  catalog_identity = resolve_namespace_identity(catalog_db)[1]
L3340:  exclusive = try_acquire_exclusive_lease(derived_root, expected_catalog_identity=catalog_identity)
        # 「try」变体吞掉缺锁 → L3363 打印 "[core.derived_gc] skipped: namespace busy …"（误导性文案）
L3368:  shared_lease = acquire_shared_lease(derived_root, ...)  # ← 缺锁 → FileNotFoundError 未被捕获
```

```python
# src/infrastructure/resource_channel/handle_resolver.py
L640:  disposition = CREATE_NEW if create_new else OPEN_EXISTING
L644-647:  # 文件缺失（ERROR_FILE_NOT_FOUND）→ raise FileNotFoundError
L734:  acquire_shared_lease(...) → _open_lock_handle(derived_str, exclusive=False)   # create_new=False
L769-777:  open_exclusive_lock_for_initialize(...)  # 唯一 CREATE_NEW 路径（首次绑定用），仅由 initialize_namespace 调用
```

**缺陷**：自举用"**`catalog.sqlite` 是否存在**"作为"命名空间是否已初始化"的判据，但二者**可以不一致**（catalog 存在而锁/binding 缺失）。此时：
1. `initialize_namespace` 被**跳过**（唯一会创建锁与 binding 的路径未执行）；
2. `try_acquire_exclusive_lease` 因是"try"而**静默降级**，并输出**误导性**的 "namespace busy (a managed peer holds a shared lease)"；
3. `acquire_shared_lease` **无保护地**抛出 `FileNotFoundError` → sidecar 进程退出 → host `main.rs:1168` panic → **应用无法启动**。

**旁证（第二实验）**：手动创建一个**空**锁文件后重跑（[`boot-defect-stderr-run3.log`](boot-defect-stderr-run3.log)），失败点变为

```text
File "infrastructure\resource_channel\handle_resolver.py", line 681, in _read_lock_binding
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

→ 证明该锁文件**不是单纯互斥物**，而是承载 **JSON `NamespaceBinding`** 的绑定载体；仅创建文件**不足以**修复，必须走**正确的首次绑定**流程（`open_exclusive_lock_for_initialize` → 写入 binding）。
（该实验产物已被移除，`derived\` 已恢复为空，未留残留。）

## 4. 影响

- **用户可见**：处于该状态（catalog 有、锁无；例如中断的首次初始化、或安装/升级后命名空间未绑定）的机器上，**应用启动即崩溃**，四页全部不可达 → **P20 发布的硬阻断**。
- **P19**：D+ 验收第 1 步（启动应用）即失败，**无法继续**直到本缺陷修复。

## 5. 测试盲区（为什么 CI 没抓到）

- Core 套件（508 passed）在**进程内**运行，且 fixture 会**预先绑定** fresh derived root（如 `tests/core/test_derived_gc.py:32` 注释所述"fresh derived root through the frozen narrow initializer"）→ **"catalog 存在 + 锁缺失"这一组合从未被构造**。
- 既有 `packaged_sidecar_tests`（12 passed）针对 sidecar 的**其他**启动面向，未覆盖本组合。
- **只有真实启动打包应用**（本 Task 的 D+ 路径）才暴露。

## 6. 修复方向（**供 Owner 决策，不由本报告定案**）

以下为可选方向，**具体修复方案与语义取舍属实现/契约责任**：
1. **判据改为命名空间绑定**：把"是否需要初始化"从 `catalog_db.exists()` 改为"**锁/binding 是否存在**"（可用 `read_lock_binding_if_any`），或在 catalog 存在但 binding 缺失时补齐绑定；
2. **启动链不得抛裸 `FileNotFoundError`**：`acquire_shared_lease` 在缺锁时应走**受控初始化**或**失败关闭为类型化错误**（并修正误导性的 "namespace busy" 文案）；
3. **补测试**：新增"**catalog 存在 + `derived/` 为空**"与"**锁文件非 JSON/空**"两类反例，断言**可恢复或失败关闭**且**绝不崩溃**。

## 7. 证据清单（本目录）

| 文件 | 内容 |
|---|---|
| [`boot-defect-stderr-run1.log`](boot-defect-stderr-run1.log) | 首次启动原始 stderr（含完整 traceback） |
| [`boot-defect-stderr-run2.log`](boot-defect-stderr-run2.log) | 第二次独立复现原始 stderr |
| [`boot-defect-stderr-run3.log`](boot-defect-stderr-run3.log) | 预创建空锁后的失败（证明 binding 必需） |
