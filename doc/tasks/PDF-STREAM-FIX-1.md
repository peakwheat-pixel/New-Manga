---
id: PDF-STREAM-FIX-1
title: 修复 QtFreePdfComposer 的 content stream 压缩声明
kind: bugfix
governance_version: 3
status: closed_with_limitations
language: zh-CN
parent: P18
blocked_by: null
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: f4fd0671e
branch: agent/dsh/PDF-STREAM-FIX-1
worktree: null
integration_commit: 09676cc19
delivery_head: 09676cc19
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/PDF-STREAM-FIX-1
activation_note: P1 缺陷，由 SEC-FMT-IMPL-1 AC5 的外部验证发现
---

# 修复 QtFreePdfComposer 的 content stream 压缩声明

## 来源与依据

**`SEC-FMT-IMPL-1` 的 AC5（外部验证器互操作）发现**：
用 MuPDF 打开导出的 PDF 时，每一页都报 `zlib error: incorrect header check`。

**Round 151 定位到具体行**：
`src/infrastructure/export/qt_free.py` L97

**完整证据**：`verification/SEC-FMT-IMPL-1/BUG-pdf-content-stream-deflate.md`

## 缺陷

```python
# L244-246 —— _stream 无条件声明 FlateDecode，假定调用者已压缩
def _stream(dictionary: bytes, payload: bytes) -> bytes:
    prefix = b"<< " + dictionary + b" /Filter /FlateDecode /Length " + str(len(payload)).encode() + b" >>\nstream"
    return prefix + payload + b"\nendstream"

# L97 —— 唯一一个传未压缩明文的调用点
content_id = add(_stream(b"", "".join(content).encode("ascii")))
```

**其它所有调用点传 `zlib.compress(...)`；L97 传明文。**

## 影响

**每一个经由 `QtFreePdfComposer` 导出的 PDF，每一页的 content stream 都解压失败。**

**后果**：`/Im0 Do` 指令未执行 → **页面渲染为空白**。

**实测**：纯红 `(255,0,0)` 页面渲染出 5400 个像素，**0 个非白**。

**而所有结构指标均正常**：`page_count`、`rect` 尺寸、`get_images()`、`xref`、`%%EOF`。

## Acceptance Criteria

- [x] **AC1 修复 content stream 的声明与数据一致** <<MET>>
- [x] **AC2 单元级：每个 stream 都能被 zlib 解压** <<MET>>
- [x] **AC3 集成级：MuPDF 不再报 zlib 错误** <<NOT_APPLICABLE: MuPDF 只在 stderr 是终端时输出，capsys/capfd/子进程均不可见；实质由 AC4 蕴含>>
- [x] **AC4 端到端：渲染出的页面不是空白** <<MET>>
- [x] **AC5 回归与独立审查** <<MET>>

## 允许修改范围

- `src/infrastructure/export/qt_free.py`
- `tests/**`（新增 PDF stream 测试）
- `verification/PDF-STREAM-FIX-1/**`、本 Task、Handoff

## 禁止范围

- 修改 `SEC-FMT-IMPL-1` 的任何结论或文件
- 修改其它导出格式（CBZ/ZIP/SINGLE_IMAGE/TEXT）的行为
- 修改 `PdfComposer` 协议
- 修改其它 Task、Plan、STATUS、`tools/**`

## 依赖、风险与阻塞

- **前置**：无。
- **风险 R1**：**修复可能影响 searchable PDF**（`compose_searchable` 走同一条 `_compose_pdf`）。
  **必须验证带文字层的 PDF 也能正常渲染。**
- **风险 R2**：**AC4 的颜色断言可能脆弱**。MuPDF 渲染可能有色彩空间转换。
  **建议断言「非白像素比例 > 0」而不是精确 RGB 匹配。**
- **风险 R3**：**可能存在其它未发现的 stream 问题**。AC2 的「每一个流都要能解压」是为了覆盖这一点。

## 交付与运行记录

（待实施后填写）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-PF-FIX | AC1 | `src/infrastructure/export/qt_free.py` | 662ba150e | - | CANONICAL |
| EV-PF-TEST | AC2 | `tests/export/test_pdf_stream_integrity.py` | 09676cc19 | - | CANONICAL |
| EV-PF-P11 | AC3 | `verification/PDF-STREAM-FIX-1/p1-1-stderr-capture-experiment.md` | 09676cc19 | - | CANONICAL |
| EV-PF-REG | AC5 | `verification/PDF-STREAM-FIX-1/ac5-regression-baseline-comparison.md` | 09676cc19 | - | CANONICAL |
| EV-PF-RV | AC5 | `verification/PDF-STREAM-FIX-1/dsh-zcode-review.md` | 09676cc19 | - | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | NOT_APPLICABLE | — | — | 本 Task 不涉及资源操作 |

## Closeout Record

- **Closeout date / Reviewers**：2026-10-20（ZCode `CHANGES_REQUESTED` → 已返修）
- **canonical_evidence_status**：`complete`
- **resource_closeout_status**：`complete`
- **删除、迁移、归档数量/字节数**：**0**
- **未关闭项及保留原因**：见下

### 逐 AC 终态

| AC | 终态 | 证据 |
|---|---|---|
| AC1 修复 content stream | **MET** | `qt_free.py` L104-105 |
| AC2 每个流可解压 | **MET** | `test_every_declared_flate_stream_actually_inflates` |
| AC3 MuPDF 不报 zlib 错误 | **NOT_APPLICABLE**（不可机器断言）| `p1-1-stderr-capture-experiment.md`；**实质由 AC4 蕴含** |
| AC4 渲染非空白 | **MET** | `test_rendered_page_is_not_blank`；纯红/纯蓝各 5400 非白像素 |
| AC5 回归与独立审查 | **MET** | 基线对照 9/9 pre-existing；ZCode Review + P1/P2 处置 |

**4 MET + 1 NOT_APPLICABLE（有机制证据）。**

### AC3 为什么是 `NOT_APPLICABLE` 而不是 `MET` 或 `PARTIAL`

**MuPDF 的 zlib 消息只在 stderr 是终端时输出。**

**实验证据**（`p1-1-stderr-capture-experiment.md`）：

| 场景 | 可见 |
|---|---|
| 终端直接跑 | ✅ |
| pytest `capsys` | ❌ |
| pytest `capfd` | ❌ |
| **子进程 `capture_output=True`** | **❌**（0 字节）|
| 子进程 + `mupdf_display_errors(True)` | **❌**（默认已是 1）|

**所以这个断言在自动化环境里不可观测。**

**但 AC3 的实质要求（content stream 能被正确解析）由 AC4 蕴含**：
**渲染出非白像素 ⟹ inflate 成功 ⟹ 无 zlib error。**

### 限制清单

| # | 限制 |
|---|---|
| **L1** | **AC3 的 stderr 文本断言不可机器验证**（机制见上）|
| **L2** | **既有 PDFium 端到端测试在缺陷期间全绿四天** | 
| **L3** | **CBZ/ZIP 的独立验证（7-Zip）只在 verification 探针层，未进 pytest** |

### L2 的完整说明（这是本 Task 最重要的发现）

**`tests/core/test_p16_reader_export.py:580-590` 一直在用 PDFium 在真实生产链路上
断言精确像素。它不是同构读回。**

**而缺陷正是引入那个测试的提交（`e2c07fa9b`，2026-10-16）带来的，四天全绿。**

**原因**：**PDFium 对「声明 FlateDecode、内容为明文」的流按容错路径照常渲染，
而 MuPDF 与 Chrome 拒绝。**

**所以缺口不是「没有独立验证」，是「互操作性押在单一外部实现上，
缺陷的可见性由该引擎的容错行为决定」。**

**这是 ZCode Review §3.5 的结论，我采纳。**

### ZCode Review 的处置

| 项 | 处置 |
|---|---|
| **P1-1** `test_mupdf_reports_no_zlib_error` 应处置 | **已按选项 2 删除** + docstring + 实验文档 |
| **P2-1** `_stream` 契约集中化 | **未做**（后续 Task；把 `zlib.compress` 收进 helper）|
| **P2-2** 测试策略缺口登记 | **未做**（后续 Backlog；两件事见下）|
| **P2-3** 回归命令缺 stash 往返 | **已修** |
| **P2-4** `_streams` 定界健壮性 | **未做**（当前输入下概率可忽略）|

### 后续建议（不属于本 Task）

1. **`_stream` 契约集中化**：把 `zlib.compress` 收进 helper，使「忘压缩」在调用点不可表达。
2. **CBZ/ZIP 的独立验证进 pytest**：7-Zip 子进程目前只在探针层。
3. **「单引擎验证对规范违反类缺陷无判别力」写入验证纪律。**
4. **`transformers` 版本不匹配**（`RTDetrV2ForObjectDetection` 缺失）需独立 Task。

