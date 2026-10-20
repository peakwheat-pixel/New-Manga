---
id: PDF-STREAM-FIX-1
title: 修复 QtFreePdfComposer 的 content stream 压缩声明
kind: bugfix
governance_version: 3
status: ready
language: zh-CN
parent: P18
blocked_by: null
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: f4fd0671e
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 修复 content stream 的声明与数据一致** <<PARTIAL: 待实施>>
  - `_stream` 的契约是「调用者给压缩数据，我加 `/Filter /FlateDecode` 声明」。
  - **L97 必须遵守这个契约**（传压缩数据），或 `_stream` 增加不压缩的分支。
  - **不得改变其它调用点的行为**——它们的输入已经是压缩的。
- [ ] **AC2 单元级：每个 stream 都能被 zlib 解压** <<PARTIAL: 待实施>>
  - 解析 `_compose_pdf` 的输出，对**每一个** `/Filter /FlateDecode` 流调用 `zlib.decompress`。
  - **全部必须成功。**
  - 同时断言每个流的 `/Length` 声明值与实际字节数一致。
- [ ] **AC3 集成级：MuPDF 不再报 zlib 错误** <<PARTIAL: 待实施>>
  - **注意**：MuPDF 的 zlib 错误走 **stderr**，不抛异常。
  - 所以测试必须**捕获 stderr**（`capsys` 或 `contextlib.redirect_stderr`），断言其中没有 `zlib error`。
  - **只用 `try/except` 包 `fitz.open` 抓不到这个缺陷。**
- [ ] **AC4 端到端：渲染出的页面不是空白** <<PARTIAL: 待实施>>
  - 生成一个**纯色**页面的 PDF（例如纯红），用 MuPDF 渲染成位图。
  - **断言至少有一个非白像素，且其中包含预期的颜色。**
  - **这一条是唯一能证明「修好了」的测试**——AC2/AC3 都可能因其它原因通过。
- [ ] **AC5 回归与独立审查** <<PARTIAL: 待实施>>
  - 既有导出测试全通过；既有 PDF 相关测试全通过。
  - 固定 `delivery_head`，由**非作者**独立复审。

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

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | NOT_APPLICABLE | — | — | 本 Task 不涉及资源操作 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。

## 释放记录（2026-10-20）

**Owner = DSH，Reviewer = ZCode**（已验证的组合）。

**为什么直接释放为 `ready`**：
- 缺陷已定位到具体行（L97），修复方案明确（三选一，推荐 A）
- 影响已实测（页面空白）
- AC 已设计到「能证明修好」的程度（AC4 的渲染断言）
- 无外部依赖

**这不是「先做再想」——Round 150/151 已经完成定位与影响评估。**
