---
id: SEARCHABLE-PDF-CJK-1
title: 可搜索 PDF 的韩文支持与字体体积
kind: implementation
governance_version: 2
status: closed_with_limitations
approval: unblocked_r41_pending_ready_fields
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [PDF-STREAM-FIX-1]
base_commit: null
branch: null
worktree: null
integration_commit: 2a6a35726
delivery_head: 8593f81c6
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 韩文可用** <<MET>>
- [x] **AC2 纯语种页可提取** <<MET>>
- [ ] **AC3 字体体积与子集化** <<PARTIAL: 体积实测与未子集化理由已给出；「不做子集化」是判断而非事实，待 Review 裁定>>
- [x] **AC4 字体开销不随页数增长** <<MET>>
- [x] **AC5 不回归既有行为** <<MET>>
- [x] **AC6 不引入外部字体下载** <<MET>>

### AC 证据索引

| AC | 证据 |
|---|---|
| AC1 | `verification/SEARCHABLE-PDF-CJK-1/font-embedding-license-review.md`；真实韩漫页 600×18401 导出后 `text='안녕하세요 세계'` 可提取 |
| AC2 | ja/zh/ko/拉丁 四语各一条；`tests/export/test_searchable_cjk_font.py`（5 测试）|
| AC3 | `ac4-font-cost-scaling.md`（体积）+ `ac3-subsetting-feasibility.md`（未做理由与原型数据）|
| AC4 | `ac4-font-cost-scaling.md`：开销 12,408,210 / 12,408,385 / 12,408,543，极差 333 字节 |
| AC5 | `tests/export` 11 passed；`test_pdf_stream_integrity.py` 4 项仍绿 |
| AC6 | 候选字体仅 `Path(WINDIR)/Fonts` 下四文件；无网络调用 |
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

## r41 裁定（2026-10-20）

**产出**：`verification/SEARCHABLE-PDF-CJK-1/codex-confirm-unblock-r41.md`

| 裁定项 | 结论 |
|---|---|
| **许可审查** | **完成**，r40 的阻塞条件解除 |
| **解除目标状态** | **`proposed`（不是 `ready`）** |
| **`ready` 门槛** | 须补齐 Owner / Reviewer / `base_commit` / branch / worktree / 完整 `allowed_paths`，并登记到 `STATUS` |
| **AC3** | 按 §2 定稿（已应用）|
| **实施顺序** | 先纯韩文，再单独评估子集化；可分阶段交付 |
| **字体清单 JSON** | **须脱敏**——去掉本机绝对路径，标注为一次性观测 |

**本 Task 现为 `proposed`：阻塞已解除，但释放字段未齐。**

## 交付与运行记录

**未开始（`blocked`）。**

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-CJK-FIX | AC1 | `src/infrastructure/export/qt_free.py` | 590118987 | `53af6735067367de0ab2b5b0f3d45fabdebcff0f01e32307c56df42e57b5a88c` | CANONICAL |
| EV-CJK-LIC | AC1 | `verification/SEARCHABLE-PDF-CJK-1/font-embedding-license-review.md` | c5e87d2ce | `44473510781cc465c9ff043e2adac56985860d0b8413e4219b27b0c92f61679a` | CANONICAL |
| EV-CJK-FONT | AC1 | `tests/export/test_searchable_cjk_font.py` | 590118987 | `25d0a34c0eb38c153fa22ec30832b8f00b17a32dc195eff5da88203f3f1ad33d` | CANONICAL |
| EV-CJK-KO-E2E | AC2 | `tests/export/test_searchable_korean_e2e.py` | 2a6a35726 | `99b8bf44cf2d7b61ce044858ef39264503742b8a0e25ac863cc0dc7e6d9e54f8` | CANONICAL |
| EV-CJK-AC3 | AC3 | `verification/SEARCHABLE-PDF-CJK-1/ac3-subsetting-feasibility.md` | 8593f81c6 | `5ddf012ddbb7cfec905ad9221204558d755eaa521fa44b7e0518f5eadd1ed43e` | CANONICAL |
| EV-CJK-AC4 | AC4 | `verification/SEARCHABLE-PDF-CJK-1/ac4-font-cost-scaling.md` | dfed15eef | `74285e44ad8f23c4bc9b2748c8ee7caf11a34d668b2cdda6d31e8efe61bfcaed` | CANONICAL |
| EV-CJK-COST | AC4 | `tests/export/test_searchable_font_cost.py` | dfed15eef | `62785369650e6690a0979739d0c3756a809c4435ebf5776ef3b105f156abeefe` | CANONICAL |
| EV-CJK-RV | AC5 | `verification/SEARCHABLE-PDF-CJK-1/dsh-zcode-review.md` | 2a6a35726 | `86ad0749cc38cbfb5784805af9a845ed2ede48a2e14c539fd9df5c276a22e4bd` | CANONICAL |

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| **（无）** | — | **NOT_APPLICABLE** | — | — | 只改 `src/infrastructure/export/qt_free.py` 一处候选列表，并新增测试与证据；未移动或删除任何被引用资源 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

- **Closeout date / Reviewers**：2026-10-20（ZCode `approve_with_conditions` → 条件已闭）
- **canonical_evidence_status**：`complete`
- **resource_closeout_status**：`complete`
- **删除、迁移、归档数量/字节数**：**0**

### 逐 AC 终态

| AC | 终态 | 证据 |
|---|---|---|
| AC1 韩文可用 | **MET** | `malgun.ttf` 加入候选；真实韩文页文本可提取 |
| AC2 纯语种页可提取 | **MET** | 四语覆盖 + ja/ko 各一条真实页端到端 |
| **AC3 字体体积与子集化** | **`PARTIAL`** | 体积实测 + 未子集化理由；「不做」是判断待审 |
| AC4 开销不随页数增长 | **MET** | 1/3/5 页开销 12,408,210 / …385 / …543 |
| AC5 不回归 | **MET** | `tests/export` 15 passed |
| AC6 无外部字体下载 | **MET** | 仅读 `%WINDIR%\Fonts` |

### ZCode Review 的处置

`approve_with_conditions`，两项 P2 条件全部闭合：

| 项 | 处置 |
|---|---|
| **F-1** AC4 测试只测 1/3 页，文档说 5 页 | **已修**（改为 1/3/5）|
| **F-2** AC1 证据是一句话而非工件 | **已修**（补 `test_searchable_korean_e2e.py`）|
| **F-3** `>15_000_000` 是大小代理 | **未做**（后续建议）|
| **F-4** `importorskip` 会静默吞掉守护 | **未做**（CI 依赖问题）|
| **F-5** 「10–50 KB」口径错 | **已修**（改为按字符数缩放）|
| **N-6** frontmatter 与 AC 表矛盾 | **已修** |
| **N-5** 临时 PDF 写进资产树 | **未做**（可选）|

### 限制清单

| # | 限制 |
|---|---|
| **L1** | **未做子集化**——体积开销约 12.4 MB/份，实测字形数据只占 0.01%，收益巨大但需独立 Task |
| **L2** | **无桌面阅读器验证**——仍是独立实现（PyMuPDF） |
| **L3** | **混排页（zh+ko）fail-closed**——本机无单一字体覆盖两端，r40 裁定不在范围 |
| **L4** | **硬编码候选字体名**——只覆盖装 `msyh.ttc` 或 `malgun.ttf` 的 Windows |
| **L5** | **错误消息不可操作**——`ValueError` 不指明缺哪种文字，用户看不出该装什么字体 |
| **L6** | **AC3 的「不做子集化」是判断**，不是事实；已标 PARTIAL 待后续 Review |

### L5 值得单独说

**当前错误是**：

```
ValueError: no installed embeddable font covers searchable PDF text
```

**它不说明缺的是韩文、不说明哪些字符、不说明用户能做什么。**

**作为内部异常足够；作为用户可见错误不可操作。**

**这属于导出错误呈现的集成层，不在本 Task 范围。**

### 后续建议（不属本 Task）

1. **字体子集化独立立项**——按 distinct 字符数估算，整章约 0.2–0.9 MB
2. **错误消息可操作化**——指明缺哪种文字、建议装什么、或降级为纯图片导出
3. **字体探测而非硬编码**——扫描 `%WINDIR%\Fonts` 覆盖 Noto/Dotum 等非微软字体
4. **CI 固定字体清单**——否则韩文测试在无 `malgun` 的 runner 上预期红

