---
id: SEARCHABLE-PDF-CJK-1
title: 可搜索 PDF 的韩文支持与字体体积
kind: implementation
governance_version: 2
status: blocked
approval: blocked_pending_font_license_review_r40
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [PDF-STREAM-FIX-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SEARCHABLE-PDF-CJK-1
allowed_paths: []
---

# SEARCHABLE-PDF-CJK-1：可搜索 PDF 的韩文支持与字体体积

## 来源与目标

**由 `PDF-STREAM-FIX-1` 的真实页验证（`searchable-pdf-real-page-verification.md`）发现。**

**两个独立问题，都在 `_embedded_font` 的字体选择与嵌入方式上**：

### 问题 A：韩文不可用

**`_embedded_font`（`src/infrastructure/export/qt_free.py` L122-138）候选字体**：

```python
candidates = [font_dir / "msyh.ttc", font_dir / "arial.ttf"]
```

**实测**：

| 文本 | 结果 |
|---|---|
| 日文 `こんにちは世界` | embedded（19,583,608 bytes）|
| **韩文 `안녕하세요`** | **`ValueError: no installed embeddable font covers searchable PDF text`** |
| 中文 `你好世界` | embedded |
| ASCII `hello` | embedded |

**fail-closed 行为本身正确**（抛异常而不是产出无文本 PDF）。

**但后果是**：**韩漫（`test_assets/comic_golden_suite/韩漫_KO/`）无法导出可搜索 PDF。**

**这与产品范围冲突**：`P18` 的验收项明确包含 **KO**。

### 本机字体覆盖的实测（2026-10-20）

**用 `_load_ttf` 直接查 cmap，而不是用 `ImageFont.getlength`——
后者对缺失字形返回 fallback 宽度，`hangul_width=200.0` 看起来像成功，实际是假信号。**

| 字体 | 大小 | ja | ko | zh | latin |
|---|---:|---|---|---|---|
| `malgun.ttf` | 13.5 MB | ✅ | **✅** | ❌ | ✅ |
| `malgunbd.ttf` | 12.6 MB | ✅ | **✅** | ❌ | ✅ |
| `msyh.ttc` | 19.6 MB | ✅ | ❌ | ✅ | ✅ |
| `simsun.ttc` | 18.3 MB | ✅ | ❌ | ✅ | ✅ |
| `arial.ttf` | 1.0 MB | ❌ | ❌ | ❌ | ✅ |
| `segoeui.ttf` | 0.96 MB | ❌ | ❌ | ❌ | ✅ |

**没有任何一个本机字体覆盖全部四种文字。**

**所以问题比「候选列表少了韩文字体」更深**：

- **加 `malgun.ttf` 能解决纯韩文**
- **但「中韩混排」或「日中韩混排」在同一页时，没有单一字体能覆盖**
- **而 `_embedded_font` 的契约是「一个页面一个字体」**

**这意味着 AC1 可能无法按「一个字体覆盖全部」的方式达成。**
**实际可行的方案是**：**按页选字体**（每页选一个能覆盖该页全部字符的字体），
**或合并两个字体的 cmap（技术复杂度高）。**

**本 Task 的 AC1 因此必须明确：是「韩文可用」，还是「任意混排可用」。"


### 问题 B：文件体积 56 倍

**实测**（一页 82 KB 的漫画）：

| 格式 | 字节 |
|---|---:|
| 纯图片 PDF | 224,454 |
| **可搜索 PDF** | **12,632,851** |

**原因**：`msyh.ttc` 原始 **19.5 MB**，**整份字体被完整嵌入，没有子集化**。

**r40 改正了本文档初版的一处错误**：初版写「对每一页重新嵌入」，
但代码实际是 `_embedded_font`（L43）与字体流（L56）都在页循环（L73）**之前**——
**每份 PDF 只嵌入一次字体。**

**所以 56 倍不是重复的后果，是「嵌入整份 19.5 MB 字体」的后果。**
**子集化能把用到的几百个字形压到几十 KB，这是唯一能降低体积的路径。

**可观察的交付结果**：韩文文本能导出为可搜索 PDF 且可提取；
可搜索 PDF 的体积增长从「线性于页数」降到「一次嵌入 + 子集化」。

## Acceptance Criteria

- [ ] AC1 韩文可用：`_embedded_font` 能在候选字体里选中含 Hangul 的字体，
  **纯韩文页**的 `page.get_text()` 能原样提取 `안녕하세요`。
  **须显式登记所选字体与来源**（本机 `malgun.ttf` 已实测含 HanGul 且含日文假名）。
  **混排（zh+ko 同页）是否在范围内，须由 Codex 裁定后写进本 AC——
  实测本机无任何单一字体覆盖两端，这不是实现懒惰而是字体事实。**
- [ ] AC2 **纯语种页**：JA / KO / ZH / 拉丁 各一条真实页的端到端导出，
  全部 `page.get_text()` 可原样提取。
  **混排页（zh+ko 同页）不在范围内**；缺字时须 fail-closed（r40 裁定）。
- [ ] AC3 字体体积：**以实测体积 + 说明为验收，3 倍不作硬门槛**（r40 裁定）。
  须给出「纯图片 PDF vs 可搜索 PDF」的实际字节数，并说明是否做了子集化。
- [ ] AC4 多页：N 页可搜索 PDF 的字体部分**不随页数线性增长**（子集化或共享对象）。
- [ ] AC5 不得回归既有行为：`tests/export/test_pdf_stream_integrity.py` 保持绿；
  `PDF-STREAM-FIX-1` 的修复不被破坏。
- [ ] AC6 不得降低安全性：字体文件来自本机系统目录，不得引入外部下载或网络请求。

## 允许修改范围

- `src/infrastructure/export/qt_free.py`（`_embedded_font`、`_compose_pdf` 的字体嵌入部分）
- 新增测试（建议 `tests/export/`）
- 本 Task 的 `evidence_dir`
- **不得**修改 `SEC-FMT` 相关的白名单、`DETECT` 的像素/字节上限、任何 `src/` 之外的契约

## 禁止范围

- 不得引入**需要网络下载**的字体
- 不得改变「无字体时 fail-closed」的行为
- 不得为了让 AC3 通过而降低文本层质量（例如只嵌 ASCII 子集）
- 不得修改 `MAX_DETECT_PAGE_BYTES` / `MAX_DETECT_PIXELS`

## 测试要求

- 真实页（`test_assets/comic_golden_suite/` 内），不是合成纯色图
- 四种语言各一条
- 体积对比须给出**实际字节数**，不是「小了很多」
- 多页测试至少 5 页，验证字体部分不线性增长

## 依赖、风险与阻塞

| # | 风险 |
|---|---|
| **R1** | **本机可能没有含 Hangul 且许可可用于嵌入的字体**——需先盘点 `C:\Windows\Fonts`。若无，须向用户申请或改用能子集化的开源字体（如 Noto Sans CJK，**但引入需许可审查**）|
| **R2** | **字体子集化需要解析 TrueType 表**，`_load_ttf` 已有部分能力，但子集化是更复杂的工作 |
| **R3** | **体积目标（AC3）可能不可达**——若如此，须如实记录而不是降低文本质量来凑 |

## r40 裁定（2026-10-20）

**产出**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-searchable-cjk-r40.md`

| 裁定项 | 结论 |
|---|---|
| **Plan 归属** | **先作为 `blocked` 节点处理**，待字体嵌入许可审查与 AC 范围冻结后释放 |
| **混排范围** | **只管纯语种**；缺字时 fail-closed |
| **AC3 体积** | **改以实测 + 说明为验收，3 倍不作硬门槛** |
| **可搜索路径是否接线** | **已接入导出界面**，默认 `image_only`（不是功能未接线）|
| **字体嵌入次数** | **每份 PDF 只嵌一次**——纠正本文档初版的错误说法 |

**所以本 Task 现在 `blocked`，阻塞条件是「字体嵌入许可审查」。**

## 交付与运行记录

**未开始（`blocked`）。**

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|

## Closeout Record

（未开始）
