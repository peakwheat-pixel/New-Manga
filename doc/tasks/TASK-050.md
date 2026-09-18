---
id: TASK-050
title: 生产 Pipeline 的设置与 provider 绑定注入（§11 P-3 非 UI 部分）
kind: implementation
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-009, TASK-019, TASK-048, TASK-049]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-050-settings-bindings
worktree: G:/CODEX/New Manga.worktrees/TASK-050-zcode
integration_commit: null
---

# TASK-050：设置与 provider 绑定注入（§11 P-3 非 UI，P1）

**READY（2026-09-19，ZCode 全权窗口 W3）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-048、TASK-049 已集成**。开工先 `git merge master`。

## 来源与目标

来源＝§11 第 3 项（P1）：`src/infrastructure/pipeline/assembly.py:19-28` 暴露 `settings` / `provider_bindings` / `constraint_snapshot_ref` / `context_policy` / `limits` 五个可选注入，而 `src/bootstrap/app.py:529-531` **只传 `handlers=` 与 `clean_probe=`** ⇒ 全部取默认 `None`；实测（复核探针）：越过区域墙后 `handlers.py:817-825` 的 `_chain` 抛 `PROVIDER_NOT_CONFIGURED`（`no provider binding configured for step 'ocr'`）。

**目标**：让"设置 + provider 绑定"能**从持久化设置面注入生产 Pipeline**（读面 + 写入面 API），从而"配置好 provider 即可推进"，并把真实端点排除在外（仍 NOT_RUN）。

## Acceptance Criteria

- [ ] **AC ①（读面注入）**：`build_production_pipeline(...)` 在生产装配处收到由**设置存储**解析出的 `settings` 与 `provider_bindings`（不复用"第二套"解析；与既有 settings/constraint/context 语义一致）；无配置时行为与现状**逐字节一致**（仍 typed fail-closed）。
- [ ] **AC ②（写面 API）**：提供保存/读取 provider 绑定与相关设置的**应用层 API**（含校验与 typed 错误），并有用例；**不做设置页 UI**（属 TASK-022，见其设计门）。
- [ ] **AC ③（端到端前进）**：配置一个**确定性/本地**（测试内自建，不引入依赖、不配真实端点）provider 后，命令能越过 `PROVIDER_NOT_CONFIGURED` 前进到更后段；给出修前/修后对照与"真实端点仍 NOT_RUN"的声明。
- [ ] **AC ④（凭据边界）**：不得读写真实凭据/密钥文件；凭据路径遵循既有 D03/settings 边界（若需要凭据注入，必须是**接口**而非值）。
- [ ] **AC ⑤（判别力 + 不回归）**：新用例对修前失败；`tests/providers/**`、`tests/core/**`、`tests/pipeline/**` 既有断言逐条不变；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑥** Handoff + `verification/TASK-050/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/infrastructure/pipeline/**`（注入点消费）
- `src/application/**`（settings / provider 绑定的应用层读写信道）
- `src/bootstrap/app.py`（装配注入）
- `tests/pipeline/**`、`tests/providers/**`、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-050/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- **不得配置真实 endpoint / 密钥 / 模型权重**；不得改 `requirements.txt`；不得改 Schema/migration（确需 → BLOCKED 转下一项）。
- 不得改 `src/ui/qml/**`（设置页 UI 属 TASK-022）；不得放宽既有断言/新增 skip；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ③ 前后对照 | `python verification/TASK-050/bindings_probe.py`（planned） | venv + 真 SQLite | NOT_RUN | 无 |
| AC ①② 用例 | `pytest tests/pipeline tests/core -q`（planned） | 同上 | NOT_RUN | 无 |
| AC ⑤ 全仓 | `pytest -q -rs` ×5（planned） | 不设 `QT_QPA_PLATFORM` | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 硬依赖：TASK-048/049（端到端与区域输入）；TASK-009（Provider 配置/网络策略/凭据边界）。
- 风险：settings 的既有存储位置与形状（`_load_pipeline_settings(conn)` 已存在，见 `app.py:335`）→ 优先复用它，不另造。
- 风险：绑定快照语义与规划期 `_provider_available` 的交互（`binding is None → True`）→ 需覆盖"绑定存在但不可用"的既有语义不被破坏。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`，前置 TASK-048/049）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 依 §11 复核结论开立为 `ready`（窗口 W3）。**实施尚未开始。**
