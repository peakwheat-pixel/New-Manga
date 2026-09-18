---
id: TASK-049
title: 生产区域输入面（§11 P-2：detect handler 注册 + detection→Region 路径；不接 QML）
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-008, TASK-019, TASK-048]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-049-region-input
worktree: G:/CODEX/New Manga.worktrees/TASK-049-zcode
integration_commit: e94d5af
---

# TASK-049：生产区域输入面（§11 P-2，P0）

**READY（2026-09-19，ZCode 全权窗口 W2）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-048 已集成**（端到端可跑是本切片 AC 的前提）。开工先 `git merge master`。

## 来源与目标

来源＝§11 第 2 项（P0）与复核证据：

- `RegionEditingService.create_region` 只存在于 `src/application/editing/service.py:247`，**`src/ui/**` 无任何调用点**；`build_production_handlers` 只注册 8 个 step 类型（`ocr/color/term_extract/translate/segment/mask_refine/inpaint/render`），**没有 `detect`**；
- 实测（复核探针）：页级 `ocr` 单元在真实运行里 `region=None` → `handle_ocr` 第一行 `_require_region` 抛 `INVALID_INPUT "step 'ocr' requires a Region target"`，run 以 `completed_with_failures` 结束；
- 先造出 Region 再跑 `OCR_REGION` 时，运行期失败变为 `PROVIDER_NOT_CONFIGURED` ⇒ **墙序 P-1 → P-2 → P-3**。

**目标**：让"区域类步骤的输入"在生产路径上**存在且可诊断**——detection 的输出能经应用服务落成 Region（含首 revision），`detect` 步骤在生产 handler 表里已注册；**没有可用检测器时 typed fail-closed**，不得发明检测器、不得静默跳过。

## Acceptance Criteria

- [x] **AC ①（detect 已注册且可诊断）**：`build_production_handlers` 注册 `detect` 步骤；未配置检测能力时返回**typed** 失败（错误码可诊断），不得静默成功。
- [x] **AC ②（detection→Region 生产路径）**：新增/接通一条应用层路径：检测结果（既有 `ports/detection` 的 `DetectionResult` 语义）→ 落成 Region（复用 `RegionEditingService`/仓库纪律，含首 revision 与 reading_order），**不另造第二套 Region 写入**。
- [x] **AC ③（端到端）**：页级 `ocr` 不再因"无 Region"失败：给出修前/修后对照（修前＝`INVALID_INPUT requires a Region target`；修后＝在"无检测器/无绑定"处 typed 失败），并说明 Region 产生后区域类命令的前进程度。
- [x] **AC ④（不接 QML）**：QML 不改（`src/ui/qml/**` 零改动）；VM 侧可暴露 `createRegion` 槽但**不接线**，并在 Task 内说明"QML 入口待 TASK-047 设计门之后另开实现切片"。
- [x] **AC ⑤（判别力 + 不回归）**：新增用例对修前代码失败；`tests/providers/**`、`tests/core/**` 既有断言逐条不变；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [x] **AC ⑥** Handoff + `verification/TASK-049/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/infrastructure/providers/**`（handler 注册与 detect 步骤）
- `src/application/editing/**`、`src/application/tasks/**`（区域落库路径与规划衔接）
- `src/ui/viewmodels/workbench/**`（仅 VM 槽，**不接 QML**）
- `src/bootstrap/app.py`（装配）
- `tests/providers/**`、`tests/core/**`、`tests/workbench/**`、`tests/editing/**`
- 本 Task、Handoff、`verification/TASK-049/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得引入新的检测器依赖、模型权重或真实 endpoint（`requirements.txt` 零改动）；不得改 Schema/migration（确需 → BLOCKED 转下一项）。
- 不得改 `src/ui/qml/**`；不得放宽既有断言或新增 skip/xfail；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ③ 修前对照 | `python verification/TASK-049/region_probe_pre.py` | venv + 真 SQLite | 修前×2：无 detect、ocr=INVALID_INPUT、MISSING=1；修后×2：detect=PROVIDER_NOT_CONFIGURED、MISSING=0 | region-{pre,post}-fix-run{1,2}.txt |
| AC ①② 单测 | `pytest tests/providers tests/editing tests/core tests/workbench tests/storage -q -rs` | 同上 | 326 passed（含 5 新用例全绿） | targeted-providers-editing-core-workbench-storage.log |
| AC ⑤ 全仓 | `pytest -q -rs` ×5 | 不设 `QT_QPA_PLATFORM` | 859 passed, 0 skipped, exit 0 ×5 | full-suite-post-fix-run{1..5}.log |

## 依赖、风险与阻塞

- 硬依赖：TASK-048（端到端可跑）、TASK-008（Region 编辑/Revision/人工保护语义）、TASK-019（provider 集成层）。
- 风险：detection 端口与生产 provider 绑定是否兼容；若必须新增检测器实现才能"可跑"，则**只做 typed fail-closed + 端口接通**，把真实检测器留给后续切片。
- 风险：Region 落库涉及既有触发器/约束 → 参考 TASK-044 的 FK/TRIGGER 枚举纪律。

## 交付与运行记录

- Handoff：`doc/handoffs/TASK-049-a57617f.md`。Review：独立子对话（进行中，报告将落 `doc/reviews/TASK-049-a57617f.md`）。实际测试：见上方测试要求表与 `verification/TASK-049/**`。
- **最近状态（当前，唯一）**：2026-09-19 ZCode 于窗口 W2 实现并取证完毕（实现提交 `a57617f`）：detect handler 注册 + 页级 plan 前置 + region_creator 装配（复用 create_region）+ 回填；5 新用例、定向 326、全仓 859×5 全绿；判别力双级（import 级 collection error + 行为级双树探针）。独立子对话 Review `approved_subagent`（doc/reviews/TASK-049-a57617f.md，无 P0/P1，R-001 P2 已修正）；integration=`e94d5af`，集成后 master 全仓 878 passed / 0 skipped exit 0。T1 后由 Codex + DSH + Qoder post-hoc 复审（可推翻）。
