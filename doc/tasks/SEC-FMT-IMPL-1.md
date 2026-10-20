---
id: SEC-FMT-IMPL-1
title: SEC-FMT-001..004 的实现与外部阅读器互操作验证
kind: implementation
governance_version: 3
status: proposed
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: DSH
owner: null
reviewer: null
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SEC-FMT-IMPL-1
activation_note: r37 判定这是 ARCH-DOC-REBASELINE 的 AC6 Gate 责任缺口；本文件为承接 Task 本体
---

# SEC-FMT-001..004 的实现与外部阅读器互操作验证

## 来源与依据

**`ARCH-DOC-REBASELINE` 的 AC6** 要求「必须通过 `SEC-FMT-001` 到 `SEC-FMT-005` 的全部安全测试」。

**`DETECT-TILING-1` 与 `DETECT-MEMORY-GUARD-1` 覆盖了 `SEC-FMT-005` 的第 ② 与 ① 项。**

**剩余四项从未有活动承接者。** r37 原文：

> **AC6 的格式追踪和安全要求已定义，但 `SEC-FMT-001..004` 与外部阅读器验证
> 没有当前活动的实现/验收 Task。AC6 的要求有文字，不等于责任已实际分派。**

**且明确警告**：

> 不能仅凭 P16/P17 曾被列作消费者，就断言其已接受这项未完成工作；
> 两 Task 已 `done`，且 r33 已……

**裁定**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-archdoc-closeout-r37.md`

## 四项要求（原文见 `ac6-p08-fmt-traceability.md` L37–L40）

| ID | 攻击面 | 要求的防御 | 覆盖格式 |
|---|---|---|---|
| `SEC-FMT-001` | Zip Slip（`../../Windows/System32`）| 识别非法相对路径，丢弃条目并记日志，限制在托管沙箱 | ZIP / CBZ |
| `SEC-FMT-002` | 畸形超深嵌套实体的 XML（Billion Laughs / XXE）| XML 解析器禁用外部实体解析（DTD/Entity Expansion 禁用）| CBZ |
| `SEC-FMT-003` | 伪装成图像的无效二进制（文本/可执行改名为 `.png`）| 文件头魔数嗅探校验，识别非法图片后报错隔离，不引发解码器崩溃 | PNG / JPG / WEBP |
| `SEC-FMT-004` | 文件名含极端特殊 Unicode、空格或超长路径（> 260 字符）| 路径适配器自动启用 Windows `\\?\` 长路径前缀 | 全部格式 |

## Acceptance Criteria

- [ ] **AC1 Zip Slip 防御** <<PARTIAL: 待实施>>
  - 构造含 `../../` 的恶意 ZIP/CBZ，断言条目被拒绝并记日志，且不写托管沙箱之外。
  - **必须覆盖**：绝对路径条目、多级 `../`、Windows 驱动器前缀（`C:\`）、UNC 路径。
- [ ] **AC2 XXE / Billion Laughs 防御** <<PARTIAL: 待实施>>
  - 构造含外部实体和实体扩展炸弹的 XML，断言解析器**不解析外部实体**且**不耗尽内存/CPU**。
  - **须说明**：本项目是否真的解析 XML（CBZ 的 `ComicInfo.xml`）？若不解析，本项记为 `NOT_APPLICABLE` 并给出代码证据。
- [ ] **AC3 魔数嗅探** <<PARTIAL: 待实施>>
  - 把文本文件、可执行文件、截断图片改名为 `.png`/`.jpg`，断言得到 typed 错误、**不崩溃、不进入解码器**。
  - 注意：`core.detect` 已有 Pillow 格式白名单（fail-closed），但**那是 detect 面，不是导入面**。
- [ ] **AC4 长路径** <<PARTIAL: 待实施>>
  - 超过 260 字符的路径必须可读取与转存，**无截断**。
  - 须说明 Windows 长路径前缀是自动启用还是需清单项（`longPathAware`）。
- [ ] **AC5 外部阅读器互操作验证** <<PARTIAL: 待实施>>
  - `DETECT-TILING-1` 的 L1/L5 已记录：**结构验证不能替代真实阅读器验证**（r33 裁定）。
  - 至少用**一个**外部阅读器打开导出的 CBZ 与 PDF，记录结果。
  - **若本环境无法安装外部阅读器，必须如实登记为 limitation，不得以结构验证充当**。
- [ ] **AC6 回归与独立审查** <<PARTIAL: 待实施>>
  - 既有导入/导出测试全通过；
  - 固定 `delivery_head`，由**非作者**独立复审。

## 允许修改范围（待释放时冻结）

- `src/**` 的导入/导出路径（具体文件待实施时定位）
- `tests/**`
- `verification/SEC-FMT-IMPL-1/**`、本 Task、Handoff

## 禁止范围

- 修改 `DETECT-TILING-1` / `DETECT-MEMORY-GUARD-1` 的任何结论或限制
- 修改 `ARCH-DOC-REBASELINE` 的 AC 判定
- 修改其它 Task、Plan、STATUS、`tools/**`
- **以结构验证充当外部阅读器验证**（r33 已明确禁止）

## 依赖、风险与阻塞

- **前置**：无（可独立实施）。
- **风险 R1**：**AC2 可能不适用**。若本项目不解析 XML，本项应为 `NOT_APPLICABLE`，
  但**必须给代码证据**，不能只因「没听说过」就跳过。
- **风险 R2**：**AC5 可能客观不可完成**。若无法安装外部阅读器，
  **这是真限制，必须登记**——而这会让 `ARCH-DOC-REBASELINE` 的 AC6 永久带 limitation。
- **风险 R3**：**scope 可能过大**。四项安全测试 + 互操作验证是一个 Task 还是两个？
  **实施前应先评估**；若过大，拆成 `SEC-FMT-IMPL-1`（001–004）与 `READER-INTEROP-1`（AC5）。

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
