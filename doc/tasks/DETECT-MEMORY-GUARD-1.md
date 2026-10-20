---
id: DETECT-MEMORY-GUARD-1
title: core.detect 的可用物理内存检查（补 SEC-FMT-005 第①项）
kind: implementation
governance_version: 3
status: in_review
language: zh-CN
parent: ARCH-DOC-REBASELINE
blocked_by: null
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 2c569457c
branch: agent/dsh/DETECT-MEMORY-GUARD-1
worktree: null
integration_commit: null
delivery_head: fa8615dc5
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/DETECT-MEMORY-GUARD-1
activation_note: r36 建议新立；本文件为 Task 本体，Plan 状态待登记
---

# core.detect 的可用物理内存检查

## 来源与依据

**`SEC-FMT-005` 原文**（`verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md` L41）：

> 单图尺寸超过 10000x20000 的极端 Webtoon 图像文件 |
> **内存管理器检查可用物理内存**，分块处理或适当限制最大处理尺寸，
> 提供清晰内存警告，防止程序 OOM | WEBP / PNG

**`DETECT-TILING-1`（已 `closed_with_limitations`）完成了四项中的第 ② 项**
（「适当限制最大处理尺寸」），
**并逐项映射出第 ① 项完全不存在**：

> 在 `src/**` 全文搜索 `GlobalMemoryStatus` / `available_memory` /
> `psutil.virtual_memory` / `MEMORYSTATUSEX` / `free_memory` —— **零命中**。

**现行阈值的性质**：

```python
MAX_DETECT_PAGE_BYTES = 32 * 1024 * 1024
MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3   # = 11,184,810
```

**它是一个固定常量，与「当前机器有多少可用内存」完全无关。**
**8 GB 机器与 64 GB 机器的行为完全相同。**

**裁定**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-tiling-closeout-r36.md`
（r36 建议另立本 Task）

## 目标

让 `core.detect` 在处理页面之前，**依据当前机器的可用物理内存**做出准入决定，
而不是仅依赖固定像素上限。**这不改变第 ② 项**（现有固定上限保留为下限保护）。

## Acceptance Criteria

- [x] **AC1 可用内存探测** <<MET>>
- [x] **AC2 准入判定的设计** <<MET>>
- [x] **AC3 与既有上限的关系** <<MET>>
- [x] **AC4 清晰的内存警告** <<MET>>
- [x] **AC5 回归与独立审查** <<MET>>

## 允许修改范围（待释放时冻结）

- `src/bootstrap/core_service.py` 的 `handle_detect`（准入判定部分）
- 新增的内存探测模块（如 `src/application/detection/memory.py`）
- `tests/**`
- `verification/DETECT-MEMORY-GUARD-1/**`、本 Task、Handoff

## 禁止范围

- 改 `MAX_DETECT_PIXELS` / `MAX_DETECT_PAGE_BYTES` 的**值**
- 改 `ports.detection` 的 provider 契约
- 修改其它 Task、Plan、STATUS、`tools/**`
- 引入重型依赖（如 `psutil` 需先评估是否已在冻结闭包内）

## 依赖、风险与阻塞

- **前置**：无（`DETECT-TILING-1` 已收口，其拒绝路径是基础）。
- **风险 R1**：**平台耦合**。Windows 上 `GlobalMemoryStatusEx` 可用，
  但「可用物理内存」在容器/低权限环境下含义不同，需记录假设。
- **风险 R2**：**误拒**。若可用内存判据过严，小内存机器会拒绝正常页。
  AC2 的「不得成为唯一判据」就是防这一条。
- **风险 R3**：**依赖**。若需 `psutil`，必须先确认它是否已在冻结闭包内
  （`DETECT-TILING-1` 的经验：Pillow 在闭包内，但那是既有依赖）。
- **不影响**：`SEC-FMT-005` 的 ② 已由 `DETECT-TILING-1` 完成；本 Task 只补 ①③。

## 交付与运行记录

（待实施后填写）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-MG-S1 | AC1 | `verification/DETECT-MEMORY-GUARD-1/stage1-memory-api.md` | 2c569457c | 68ab3f227b8c5219b641c401dfd301355d51c54a2d339022fd8880aaf6be6e7e | CANONICAL |
| EV-MG-S1J | AC1 | `verification/DETECT-MEMORY-GUARD-1/stage1-memory-api.json` | 2c569457c | de7b84a9be163f64c2e0d9f9840719d7ea1b49c3f4aeda0eeec89d1eec628927 | CANONICAL |
| EV-MG-S2 | AC2 | `verification/DETECT-MEMORY-GUARD-1/stage2-admission-rule.md` | fa8615dc5 | 441cb906ed64cc46844fcda01687f4fd546892d9fb02dfcf1da27a0bac339d7a | CANONICAL |
| EV-MG-RV | AC5 | `verification/DETECT-MEMORY-GUARD-1/dsh-zcode-review.md` | 953a10eda | 614c842882f9f027723f6c0ca42bd63d5a686d81d3e125fe5e792334054d916b | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | — | — | — | 本 Task 不涉及资源操作 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
