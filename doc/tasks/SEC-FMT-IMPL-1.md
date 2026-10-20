---
id: SEC-FMT-IMPL-1
title: SEC-FMT-001..004 的实现与外部阅读器互操作验证
kind: implementation
governance_version: 3
status: ready
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: DSH
owner: DSH
reviewer: ZCode
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

- [ ] **AC1 Zip Slip：证明 `zip_parts` 挡住六类攻击** <<PARTIAL: 待实施>>
  - 六类：`../` 穿越、绝对路径、Windows 驱动器前缀、反斜杠、NUL 字节、`.`/空段。
  - 断言 `zip_parts` 对每一类**抛 `ValueError`**，合法条目正常返回。
  - **对照臂**：`images/<title>/001.jpg` 必须被接受（否则「拒绝一切」也能过前六条）。
  - 依据：`guard-on-attack-path.md` §1.2。
- [ ] **AC2 XXE：证明 DTD/ENTITY 拒绝有效** <<PARTIAL: 待实施>>
  - 外部实体（`<!DOCTYPE ... SYSTEM "file:///...">`）、Billion Laughs（嵌套 `<!ENTITY>`）均被拒。
  - **对照臂**：合法 `ComicInfo.xml` 仍能解析。
  - 依据：`r1-xml-parsing-scope.md` §7.2。
- [ ] **AC3 魔数：证明非图片被拒，并记录机制** <<PARTIAL: 待实施>>
  - 把文本/可执行/截断图片改名为 `.png`/`.jpg`，断言得到 typed 错误、不崩溃。
  - **必须记录**：本项目的嗅探是**委托 Pillow `Image.open()`** + `image.format` 白名单，
    不是自建魔数检查。**文档不得写成「本项目实现了魔数嗅探」。**
  - 依据：`final-two-items.md` §一。
- [ ] **AC4 长路径：把探针转成回归测试** <<PARTIAL: 待实施>>
  - `probe-sfx004-lifecycle.py` 已验证 434 字符路径 7/7 通过；**需转成 pytest 用例**。
  - 断言 `write_temp`/`publish`/读回/`remove_managed` 在 >300 字符根目录下均成功。
  - 依据：`sfx004-long-path-repro.md` §三。
- [ ] **AC5 外部阅读器互操作验证** <<PARTIAL: 待实施>>
  - 至少用**一个**外部阅读器打开导出的 CBZ 与 PDF。
  - **若本环境无法安装，必须如实登记为 limitation，不得以结构验证充当**（r33 已禁止）。
- [ ] **AC6 回归与独立审查** <<PARTIAL: 待实施>>
  - 既有测试全通过；固定 `delivery_head`，由**非作者**独立复审。

### 2026-10-20 释放记录（范围经四轮证据收敛）

**Owner = DSH，Reviewer = ZCode**（与 `DETECT-MEMORY-GUARD-1` 同一对，两端均已实证）。

**范围收敛过程**（每一轮的初始判断都不对）：

| 轮 | 原以为 | 实际 |
|---|---|---|
| 143 | `SEC-FMT-002` 不适用 | 已实现（`assets.py` DTD 拒绝）|
| 144 | 四项都要实现 | 四项都已存在 |
| 145 | 都有守卫 | 001/002 在「产品不用」的路径上 |
| 146 | `SEC-FMT-004` 是真缺口 | 缺口可能无害 |
| **147** | **004 需要实现** | **实测 7/7 通过，规范的技术细节过时** |

**所以本 Task 没有「从零实现」的工作，全部是「落证据为测试」。**

**唯一可能的新实现是 UI 层地址栏不截断（未测），但那可能属于另一个 Task。**

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
