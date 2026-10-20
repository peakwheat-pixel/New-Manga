---
id: DETECT-TILING-1
title: core.detect 超限输入的预解码安全拒绝（含 SEC-FMT-005 映射）
kind: implementation
governance_version: 3
status: ready
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: Antigravity
owner: Antigravity
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
- [ ] AC1：**超限输入的预解码安全拒绝与内存证据**——对 PNG/JPEG 请求，必须在**任何触发
      像素解码或建立整页像素缓冲的操作之前**完成格式、尺寸与资源策略判定。超过明确最大处理尺寸
      或内存策略的页面必须**安全拒绝**，错误须说明**实际尺寸、适用上限及用户可采取的处理方式**。
      不得通过 `crop()` / `reduce()` / `draft()` 或其它 Pillow 访问路径绕过上限。
      **须实测记录拒绝前后的峰值内存**，证明拒绝路径**未触发整图像素分配**。
      若某格式的头部/元数据解析本身会触发像素分配，必须相应调整判定路径，
      或明确拒绝声称满足本 AC。
      ——**改写依据**：`codex-adjudicate-tiling-stage2-r35.md` §2。
      阶段 1/2 已实测证明「裁 tile 后逐块 `convert()`」**不是**有界解码
      （见 `verification/DETECT-TILING-1/stage1-decoder-memory.md`
      与 `stage2-candidate-paths.md`）。
- [ ] AC2：**`SEC-FMT-005` 的逐项映射**——`SEC-FMT-005` 原文要求「检查可用物理内存、
      **分块或适当限制最大处理尺寸**、提供清晰内存警告防止 OOM」。
      **「限制」是被明文允许的**，所以本 Task 走拒绝路线不违反它。
      但**当前代码的像素上限与通用错误尚不能单独证明其全部满足**，
      必须把四项逐一映射并给证据：①可用物理内存检查/明确上限
      ②超限前拒绝 ③用户可读警告 ④OOM 防护。
      **未覆盖全项只能登记 `PARTIAL`，不得声称 `SEC-FMT-005` 已满足。**
- [ ] AC3：**阈值口径缺陷单独立项，本 Task 不改常量**——
      `MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3` 按 **RGB24** 计算，
      而实测样本 `mode` 可为 **RGBA**（4 B/px）。
      32 MiB ÷ 4 = **8,388,608 px** 才是 RGBA 平面的对应上限；
      现行 11,184,810 px 的 RGBA 满幅为 **42.7 MB**，超过 32 MiB 的设计意图。
      **该缺陷成立，但本 Task 明确禁止改常量值**（改它是收紧，会拒绝更多页）。
      **须在证据中登记该缺陷并给出建议口径**，实际修正在**另立 Task** 中进行。
- [ ] AC4：**实测证据**——用 `test-materials` 中已存在的超限样本实测拒绝行为，
      记录：输入尺寸、现有错误文本、拒绝是否发生在像素解码前、拒绝前后峰值内存。
      样本引用方式为路径 + `sha256`，**不得复制入仓库**（依据 `data-registry` policy
      `unknown rights mean no redistribution`）。至少覆盖一个 PNG 与一个 JPEG。
- [ ] AC5：**回归与独立审查**——既有 `core.detect` 测试全通过；
      PNG/JPEG 白名单、base64 校验、`width`/`height` 一致性校验的语义**不变**；
      正常页（未超限）的检测行为与结果**不得改变**；
      固定 `delivery_head` 由 DSH 独立复审。

**已删除的 AC**：原 AC2（跨 tile 边界去重）——**不再产生 tile，无验收对象**
（依据 r35 §3）。

### 2026-10-20 r35 重写

原目标是「分块处理超限页面」。阶段 1/2 实测证明 **Pillow 无法对该类 PNG 做有界分块解码**（裁 1×1 像素即 324.4 MB；PNG 是单一 zlib 流，只有一个整图 tile）。

**Codex r35 裁定改为「预解码安全拒绝」**：不承诺超限页可检测，改为在像素解码前准确拒绝、给可操作错误、并用实测证明拒绝路径不触发整图分配。

**关键事实**：现有 `handle_detect` **已经在 `Image.open` 后、`convert()` 前校验像素数并拒绝**——所以这不是新增机制，而是**把已有拒绝做准确、做可证明**。

**AC 从 5 条重排**：分块目标与跨 tile 去重（原 AC2）删除；`SEC-FMT-005` 映射与阈值口径缺陷登记成为新 AC2 / AC3。

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
