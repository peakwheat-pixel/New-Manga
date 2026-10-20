# `SEC-FMT-003` 与 `SEC-FMT-004` 的最终答案

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` 的两项待查
**上一轮留的**：
> 未确认 `src/` 是否有 JPEG 魔数校验
> 未确认是否有主动添加 `\\?\` 前缀的适配器

## 一、`SEC-FMT-003`：满足，但方式不是「显式魔数」

### 1.1 `src/` 里没有任何显式 JPEG 魔数检查

**全文搜索 `xff.{0,4}xd8` / `xffd8` / `JPEG_MAGIC` / `JPEG_SIG` / `SOI` —— 零命中。**

**PDF 有显式检查**（`_PDF_MAGIC = b"%PDF-"` + `startswith`），
**PNG 有显式检查**（`PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"` × 3 处），
**JPEG 没有。**

### 1.2 但 `core.detect` 路径上的防御是另一种机制

`core_service.py` L1396–L1403 的 docstring：

> Request validation (typed INVALID_REQUEST, fail-closed before any provider is touched):
> - `page` must be a base64-encoded PNG/JPEG image
>   (**format whitelist enforced fail-closed after the header sniff**)

**「header sniff」指的是 `Image.open()` 本身。**

**实际代码（L1457）**：

```python
if image.format not in _DETECT_PAGE_FORMATS:   # frozenset({"PNG", "JPEG"})
    raise DetectRequestError(...)
```

**而 `image.format` 是 Pillow 在 `Image.open()` 时从文件头识别出来的。**

### 1.3 所以 `SEC-FMT-003` 在 detect 路径上满足，机制是

| 层 | 谁做 | 内容 |
|---|---|---|
| 1 | **Pillow `Image.open()`** | 读文件头，识别格式；不是图片则抛 `UnidentifiedImageError` |
| 2 | **`_DETECT_PAGE_FORMATS` 白名单** | 只接受 `PNG` / `JPEG`，fail-closed |
| 3 | **`image.convert("RGB")` 之前的像素上限** | 见 `DETECT-TILING-1` |

**这正是 `SEC-FMT-003` 要求的**：

> 文件头魔数嗅探校验，识别非法图片后报错隔离，**不引发解码器崩溃**

**「不引发解码器崩溃」由 Pillow 的 `Image.open` 抛 typed 异常保证，
而 handler 捕获后转成 `DetectRequestError`。**

### 1.4 但这个满足有一个明确的依赖

**它依赖 Pillow 的嗅探行为，而不是本项目自己的代码。**

**后果**：

- ✅ 当前有效
- ⚠️ **若 Pillow 版本升级改变了嗅探行为，本项目不会知道**
- ⚠️ **若将来有另一条路径接受图片但不经过 `Image.open()`，那条路径没有魔数校验**

**所以判定是：`MET`（在 detect 路径上），但机制是「委托给 Pillow + 白名单」，不是自建嗅探。**

**这需要在验收时写清楚，不能写成「本项目实现了魔数嗅探」。**

## 二、`SEC-FMT-004`：**真缺口**

### 2.1 现有代码只「识别」不「添加」

**唯一的 `\\?\` 处理在 `target_refs.py` L233–L237**：

```python
def _normalized_path(path: Path) -> str:
    value = str(path)
    if value.startswith("\\\\?\\"):
        value = value[4:]        # 去掉前缀
    return os.path.normcase(os.path.normpath(value))
```

**这是**去掉**前缀（为了比较路径），不是**添加**。**

### 2.2 全仓搜索「构造 `\\?\` 路径」：零命中

**没有任何代码在路径过长时主动添加 `\\?\` 前缀。**

### 2.3 所以 `SEC-FMT-004` 不满足

**`SEC-FMT-004` 要求**：

> 文件名含极端特殊 Unicode、空格或超长路径（**> 260 字符**）时，
> **路径适配器自动启用 Windows `\\?\` 长路径前缀**，确保文件可被正确读取与转存，地址栏不截断。

**而现状**：

| 要求 | 现状 |
|---|---|
| 超长路径可读取与转存 | **未实现**（无前缀添加）|
| 地址栏不截断 | 未查 |

### 2.4 查过了：**没有 `longPathAware`，所以 `SEC-FMT-004` 确实是缺口**

**上一版把这条留作「下一步必须先查」。查完了。**

**搜索结果**：

| 查什么 | 结果 |
|---|---|
| 全部 `.json` / `.manifest` / `.toml` / `.xml` 里的 `longPathAware` / `long_path_aware` / `LongPathsEnabled` | **零命中** |
| `apps/desktop/src-tauri/tauri.conf.json` | **存在，但没有 `longPathAware`** |
| 代码里主动添加 `\\?\` 前缀 | **零命中**（§2.2）|

**而 `sqlite/connection.py` L3 的注释是**：

> Implements D07 §28 (PRAGMA profile), **§36 (Unicode paths, no MAX_PATH assumption)**

**「no MAX_PATH assumption」= 「不假设有 MAX_PATH 限制」。**

**这是一个**意图声明**，不是实现。**

**它说的不是「已处理长路径」，而是「代码里没有硬编码 260」。**

**两者不是一回事。**

### 2.5 所以 `SEC-FMT-004` 的判定

| 要求 | 现状 |
|---|---|
| 路径适配器自动启用 `\\?\` 长路径前缀 | **不存在** |
| 或进程清单声明 `longPathAware` | **不存在** |
| 超长路径可读取与转存 | **无实现支撑** |

**判定：`NOT_IMPLEMENTED`。**

**这是四项里唯一的真缺口，也是 `SEC-FMT-IMPL-1` 唯一可能需要新写代码的地方。**

### 2.6 但修复它之前要先确认失败是可复现的

**`SEC-FMT-004` 的措辞假设「当前会失败」。**

**而失败需要三个条件同时成立**：

1. 路径总长 > 259 字符
2. 进程未声明 `longPathAware`
3. 走过 `.NET` / Win32 的 ANSI 路径 API

**Python 3.6+ 在 Windows 上已默认使用宽字符 API，且 `pathlib` 在多数操作上能处理长路径。**

**所以「没有 `\\?\` 前缀添加」不等于「长路径一定失败」。**

**正确的下一步是：构造一个 >260 字符的路径，实测产品能否读取与转存。**

**若实测通过**：`SEC-FMT-004` 的实质要求已满足，**缺的是清单声明或显式保护**，
那可能只是一个文档/防御性问题，而不是功能缺口。

**若实测失败**：才是真缺口，需要实现前缀适配器。

**本文件不预设哪一种——这需要一次实测。**

## 三、汇总：四项的最终判定

| ID | 判定 | 机制 | 备注 |
|---|---|---|---|
| `SEC-FMT-001` | **`MET`（适用路径上）** | `zip_parts` 白名单 + 出口路径隔离 | 产品路径不适用（只写不解压）|
| `SEC-FMT-002` | **`MET`（适用路径上）** | 先拒 `<!DOCTYPE`/`<!ENTITY` | 产品路径不适用（只写不解析）|
| `SEC-FMT-003` | **`MET`（detect 路径上）** | Pillow 嗅探 + `image.format` 白名单 | **不自建嗅探，依赖 Pillow** |
| `SEC-FMT-004` | **待定** | 代码无前缀添加 | **可能由清单项满足，需查** |

**所以四项里前三项在各自的适用路径上都有防御，第四项不确定。**

## 四、这对 `SEC-FMT-IMPL-1` 的最终结论

**这个 Task 的真实工作量**：

| 项 | 工作 |
|---|---|
| `SEC-FMT-001` | **补测试**证明 `zip_parts` 挡住六类攻击（工作量小）|
| `SEC-FMT-002` | **补测试**证明 DTD 拒绝有效（工作量小）|
| `SEC-FMT-003` | **补测试**证明非图片被拒；**并记录「依赖 Pillow 嗅探」这个机制** |
| `SEC-FMT-004` | **先查清单项**；若缺失则**这是唯一的实现工作** |
| **AC5 外部阅读器** | 独立问题，可能客观不可完成 |

**所以这个 Task 从「四项安全测试」收敛为「三项补测试 + 一项待查清单 + 一项互操作验证」。**

**而唯一可能的新实现是 `SEC-FMT-004`——而它也可能不需要实现。**

## 五、明确未做

- **未查 `longPathAware` 清单项**（§2.4）——**这是 `SEC-FMT-004` 判定的前置**
- **未写任何测试**
- **未验证 Pillow 的嗅探在各类伪装文件上的行为**
- **未检查 `.rs` 侧是否有魔数校验或长路径处理**
- **未修改 `SEC-FMT-IMPL-1` 的 AC 判定**
