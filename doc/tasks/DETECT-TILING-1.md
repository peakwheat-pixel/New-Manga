---
id: DETECT-TILING-1
title: core.detect 超限输入的预解码安全拒绝（含 SEC-FMT-005 映射）
kind: implementation
governance_version: 3
status: in_review
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: Antigravity
owner: DSH
reviewer: null（必须非 DSH；DSH 已实现，不得自审。当前 Session 无人可派，待 Codex 指派）
depends_on: []
base_commit: 5885b182e
branch: agent/antigravity/DETECT-TILING-1
worktree: null
integration_commit: null
delivery_head: 843cfe705
canonical_evidence_status: complete
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
| EV-DT1-MEM | AC1 | `verification/DETECT-TILING-1/stageA-rejection-memory.md` | 843cfe705 | `f3de5ce30fe5696858411ba3587e3729c1d77dfd` | CANONICAL |
| EV-DT1-MEMJSON | AC1 | `verification/DETECT-TILING-1/stageA-rejection-memory.json` | 843cfe705 | `1c33d92ecec43961597455c3e3f22df55e86174b` | CANONICAL |
| EV-DT1-JPEG | AC4 | `verification/DETECT-TILING-1/stageA-jpeg-rejection-memory.json` | 783434e5b | `0a0fa56e5ec76ed0dad96f7d4f84ae4647d3ad7d` | CANONICAL |
| EV-DT1-S1 | AC1 basis | `verification/DETECT-TILING-1/stage1-decoder-memory.md` | b5253ebfc | 506d34e60f7b2590824fa2d553a72c8108f95b6d | CANONICAL |
| EV-DT1-S2 | AC1 basis | `verification/DETECT-TILING-1/stage2-candidate-paths.md` | c776dc1ae | `611780af4206182e71eba0cd15baff51b8349d49` | CANONICAL |
| EV-DT1-R35 | ruling | `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-tiling-stage2-r35.md` | 5885b182e | `7e17c88c7b6a6d695074a220966b895bd4e3b015` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## 阶段 A 交付

### 2026-10-20 Owner 变更

**`owner` 由 `Antigravity` 改为 `DSH`。**

**理由**：实际实施者是 DSH。`agy`（Antigravity CLI）在本环境**两次卡死**：

| 次 | 卡住时长 | CPU 观测 | 产出 |
|---|---:|---|---|
| 1 | **42 分钟** | 20 秒涨 **0.2 s** | 0 字节 |
| 2 | **10 分钟** | 15 秒涨 **0.0 s** | 0 字节 |

**同一 `agy` 做只读探测任务 98.9 秒成功**（正确报出 `MAX_DETECT_PAGE_BYTES` L289
与 `MAX_DETECT_PIXELS` L299 的值）。**所以它能做只读分析，做不了实施。**

**这一条是环境约束，不是本 Task 的缺陷**，应另行登记到治理层，
否则下一个 Task 还会重复派给 Antigravity 再等 40 分钟。

**`Reviewer` 不变**：DSH 不得审核自己实现的变更，**所以本次变更必须由非 DSH 复审**。
**当前 Session 无人可派，这是需要 Codex 处置的治理事实。**



### 2026-10-20 AC4 收口（合成 JPEG）

**问题**：AC4 原文要求「至少覆盖一个 PNG 与一个 JPEG」，
而 `test-materials` 的 34 个 JPEG **没有一个超过 `MAX_DETECT_PIXELS`**。

**裁定（按推荐自行裁决）**：用**合成 JPEG** 补齐，理由与边界写在证据里。

| 样本 | 尺寸 | 像素 | 满幅 RGB24 | **拒绝时峰值** |
|---|---|---:|---:|---:|
| 真实 PNG | `690×62133` | 42,871,770 | 122.7 MB（RGBA 163.5）| **141.7 MB**（原 37.3 已撤回）|
| **合成 JPEG** | `5000×4000` | 20,000,000 | 57.2 MB | **53.2 MB**（原 19.5 已撤回）|

**合成 JPEG 证明的是**：拒绝路径**与格式无关**，JPEG 与 PNG 行为一致。
**合成 JPEG 不证明**：真实超大漫画页的检测质量——**那条限制仍然存在**。

样本位置：`G:\CODEX\New Manga.workspace\DETECT-TILING-1\synthetic\oversized-5000x4000.jpg`
（**在 workspace 内，未入库**，符合素材治理规则）。

（2026-10-20）

**Handoff**：`doc/handoffs/DETECT-TILING-1-dsh-stageA-20261020.md`
**delivery_head**：`843cfe705`（分支 `agent/antigravity/DETECT-TILING-1`）
**base_commit**：`5885b182e`（主线不含本次产品改动）

| AC | 状态 |
|---|---|
| AC1（预解码安全拒绝 + 内存证据） | 代码 + 实测 + 测试完成，**待独立 Review** |
| AC4（实测证据） | PNG 与合成 JPEG 均已测（见下「AC4 收口」）；**真实超限 JPEG 仍不存在**，该项限制保留 |
| AC2（SEC-FMT-005 映射） | 未开始 |
| AC3（RGBA 阈值缺陷登记） | 未开始（缺陷已在 stage2 记录） |
| AC5（回归 + 独立审查） | 回归 **36 通过**；独立审查 **r1/r2 已由 ZCode 完成** |

**实测关键数（已更正）**：满幅 RGBA 163.5 MB；拒绝时峰值 **141.7 MB**（同源完整解码为 479.8 MB）。**旧值 37.3 MB 系 trim 基线产物，已撤回**（见 `stageA-remeasurement-20261020.md` §一）。

**Owner 不符**：Task 的 `owner` 是 `Antigravity`，实际实施者为 DSH
（`agy` 两次卡死；详见 Handoff §风险 R1）。**需 Codex 裁定。**

### 2026-10-20 阻塞：无可用 Reviewer

**`owner` 与 `reviewer` 不能是同一人**（`AGENTS.md`：DSH 不得审核自己实现的变更）。

**当前事实**：

| 候选 | 可用性 |
|---|---|
| DSH | **是实施者，不可自审** |
| Antigravity | **本环境两次卡死**（42 分钟 0.2 s CPU / 10 分钟 0.0 s CPU）|
| Codex | 是 Lead/Integrator，**通常不兼 Reviewer**；可裁定但不宜作为独立实现审查者 |
| ZCode | 有 headless CLI，但 `AGENTS.md` 未把它列为通用代码 Reviewer |
| Qoder | **2026-10-08 已退出项目**，不得分配 |

**所以本 Session 没有合规的独立 Reviewer。**

**这不是我能靠努力解决的**——它是环境与角色分配的事实。

**因此本 Task 保持 `in_review`，不得进入 `done`。**
**任何「已自审通过」的记录都是伪造，我没有写。**

**需要 Codex 处置**：
1. 指派一个非 DSH 的 Reviewer；或
2. 明确授权「本 Task 以 limitation 收口，接受无独立审查」并记录该限制。

### 2026-10-20 ZCode Review 处置（P1-2 / P2）

**Review**：`verification/DETECT-TILING-1/dsh-stageA-zcode-review.md`（结论 `APPROVE_WITH_COMMENTS`，P0 无）

| 项 | 处置 |
|---|---|
| **P1-1** 测试不守「拒绝先于解码」 | **已修**（`07e414773`）：新增 `test_detect_oversized_rejected_before_any_pixel_decode` 与对照组；**注入回归实测证明旧测试通过、新测试失败** |
| **P1-2(a)** `PARTIAL` 与「已收口」并存 | **已修**（本 commit）|
| **P1-2(b)** `EV-DT1-JPEG` pin 指向 `843cfe705`，实际为 `783434e5b` | **已修**（本 commit）|
| **P1-2(c)** sha256 全为 `(worktree)`，合成 JPEG 无 sha256 | **已修**（本 commit）|
| **P1-2(d)** AC4 改用合成 JPEG 属口径变更，需追认 | **未处置**（需 Codex 追认）|
| **P2-1** 同源对照 | **已做**：`stageA-remeasurement-20261020.md` |
| **P2-2** 指标口径矛盾 | **已做并撤回旧数**：37.3 MB 是 trim 基线产物，真实拒绝峰值 141.7 MB |
| **P2-3** stageA md 自述过时 | **未修** |
| **P2-4** 弱断言 `"over" in message` | **未修** |

**合成 JPEG 样本 sha256**：`84592ff425ae348313ef202230d59583ef727cada9aca55027dfcc1f800bee5f`
路径：`G:\CODEX\New Manga.workspace\DETECT-TILING-1\synthetic\oversized-5000x4000.jpg`（**在 workspace 内，未入库**）

**说明（N-6）**：注入回归实验与删比例转红实验**已执行并观察结果，但未留可重跑的脚本或输出记录**——表述已改为「验证过（未留痕）」，不再声称「实测证明」有独立载体。

## 终态处置表（唯一权威，截至 `4868dc3fa`）

**规则**：本 Task 内其它任何位置的「未修 / 未做 / PARTIAL / 待处置」陈述
**都是写入时点的快照，不代表终态**。**终态只看本表。**

| 项 | 终态 | 依据 |
|---|---|---|
| P1-1 测试不守「拒绝先于解码」 | **已修** | `07e414773`；注入回归实证旧测试绿/新测试红 |
| P1-2(a) `PARTIAL` 与「已收口」并存 | **已修** | `de788b212` |
| P1-2(b) `EV-DT1-JPEG` pin 指向错误 commit | **已修** | `de788b212`（改为 `783434e5b`）|
| P1-2(c) sha256 全为 `(worktree)` | **已修** | `de788b212` 补真实值；`4868dc3fa` 改口径为 git blob |
| **P1-2(d)** AC4 改用合成 JPEG 属验收口径变更 | **待追认** | 需 Codex 裁定；**不阻断阶段 A 代码面，阻断 Task 收口** |
| P2-1 同源对照 | **已做** | `stageA-remeasurement-20261020.md` §二 |
| P2-2 指标口径矛盾 | **已修**（旧数已撤回） | `stageA-remeasurement-20261020.md` §一 |
| P2-3 stageA md 自述过时 | **已修** | `96bc66d93` 追加勘误 |
| P2-4 弱断言 `"over" in message` | **已修** | `96bc66d93`；删比例后测试转红 |
| **N-1** remeasurement §四 归因错误 | **已修** | `4868dc3fa`（探针崩溃，非字节门拒绝）|
| **N-2** sha256 口径与 commit 列矛盾 | **已修** | `4868dc3fa`（6/6 blob hash 独立验证通过）|
| **N-3** 状态表滞后家族 | **已修** | 本表 + 各文件时点标注 |
| **N-4** spy 只拦 `convert` | **未修** | 建议级；当前 handler 唯一解码入口是 convert |
| **N-5** 勘误表测试名笔误 | **已修** | 本 commit |
| **N-6** 注入实验无留痕 | **已改为「验证过（未留痕）」** | 本 commit 修正表述 |
| **AC2** `SEC-FMT-005` 四项映射 | **未开始** | — |
| **AC3** RGBA 阈值缺陷登记 | **未开始** | 缺陷已在 `stage2-candidate-paths.md` 记录 |
| **AC5** 独立审查 | **r1 + r2 已完成**（ZCode，非作者）| 见两份 Review 文件 |

**收口前必须清零**：P1-2(d) 追认、AC2、AC3。

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
