---
id: DETECT-TILING-1
title: core.detect 分块处理超限页面（含 SEC-FMT-005 超大图安全）
kind: implementation
governance_version: 3
status: proposed
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: Antigravity
owner: null
reviewer: DSH（非作者独立复核；实现/审查分离）
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/DETECT-TILING-1
activation_note: r34 方向批准，尚未释放；本文件为 Task 本体，Plan 状态为 proposed
---

# core.detect 分块处理超限页面

## 来源与依据

**一个改动解两个 AC**：

| 消费者 | 要求 | 当前阻塞 |
|---|---|---|
| `ARCH-DOC-REBASELINE` AC5 的消费链（经 `P18` AC5）| 真实页 `2946×4167` 可检测 | `core.detect` 拒绝：`12,275,982 px > 11,184,810 px` |
| `ARCH-DOC-REBASELINE` AC6 · `SEC-FMT-005` | 超大图（`> 10000×20000`）不得 OOM，需分块或限尺寸 | **从未实现** |

**阈值来源已查明**（`src/bootstrap/core_service.py`）：

```python
MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3
```

`32 × 1024 × 1024 ÷ 3 = 11,184,810.67` → **11,184,810**，精确吻合
「解码后 RGB24 不超过 32 MiB」。**这是内存保护，不是页宽上限。**

注释里的设计假设：「A real 900x1300 page is ~1.2 M px, roughly 9x headroom」。
被拒的真实页 **12.3 M px**，约为该假设的 **10 倍**——**假设对 Webtoon/高分辨率扫描页失效**。

**裁定**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-detect-tiling-r34.md`

## Acceptance Criteria

- [ ] AC1：**有界解码与分块坐标**——对超限页面，选定解码方式的**峰值内存必须有界并实测证明**；
      不得以「裁 tile 后逐块 `convert()`」默认等价于有界解码（Pillow 可能在首次像素访问时
      解码整图）。无法有界解码的输入必须**在大分配之前**按明确上限拒绝并给出清晰错误。
      可处理时，每 tile 解码后 RGB24 ≤ `MAX_DETECT_PIXELS`，结果坐标映射回**整页坐标空间**。
- [ ] AC2：**重叠边界的唯一性与不漏检**——跨 tile 的同一文本块必须唯一且不丢。
      允许采用保守的 tile ownership / overlap 策略，但**不得**把重复 region 留作
      「以后再合并」后仍声称 P18 质量切片可用。必须写明所选策略与理由。
- [ ] AC3：**32 MiB 契约与输入语义不变**——`MAX_DETECT_PAGE_BYTES` / `MAX_DETECT_PIXELS`
      **值不得修改**（分块是解法，调阈值不是）；PNG/JPEG 白名单、base64 校验、
      `width`/`height` 一致性校验的语义**保持不变**。
- [ ] AC4：**真实页与普通页对照**——用被拒的那一页（`2946×4167 = 12,275,982 px`）实测通过，
      产出 region 集与整页坐标；同时用一张**正常页**做对照，证明分块未改变正常页结果。
- [ ] AC5：**`SEC-FMT-005` 超大图安全 + 回归 + 独立审查**——逐字覆盖 `SEC-FMT-005` 的三项要求
      （检查可用物理内存、分块或尺寸限制、清晰内存警告防 OOM），覆盖 `> 10000×20000` 场景；
      既有 `core.detect` 测试全通过；固定 `delivery_head` 由 DSH 独立复审。
      **未覆盖全项只能登记 `PARTIAL`，不得声称 `SEC-FMT-005` 已满足。**

## 允许修改范围（r34 收敛，待释放时冻结）

- `src/bootstrap/core_service.py`（`handle_detect` 及其相邻常量的**注释**，不改常量值）
- 新增分块/解码策略模块
- `tests/**`（新增分块与内存边界测试）
- `verification/DETECT-TILING-1/**`、本 Task、Handoff、Review

## 禁止范围

- 改 `MAX_DETECT_PIXELS` / `MAX_DETECT_PAGE_BYTES` 的**值**
- 改 `ports.detection` 的 provider 契约或 provider 的 byte-count gate
- 在调用方（P16/P17/P18）以缩放页面的方式规避（r34 否决方案 C）
- 修改其它 Task、Plan、STATUS、`tools/**`

## 依赖、风险与阻塞

- **前置**：无（可独立实施）。
- **风险 R1**：**解码峰值内存**——见 AC1。这是本 Task 的核心技术风险。
- **风险 R2**：**跨 tile 重复 region**——见 AC2。
- **风险 R3**：provider 的 `_validate_request` byte gate 是第二道防线，**保持不变**；
  tile 划分、坐标偏移、结果汇总都在 handler / application 层完成。
- **不影响**：KO 链路（`paddleocr` 在 Python 3.14 无 wheel 的问题独立于本 Task）。

## 交付与运行记录

（待实施后填写）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
