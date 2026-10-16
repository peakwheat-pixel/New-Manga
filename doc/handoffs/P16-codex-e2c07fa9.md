---
task_id: P16
author: Codex (Owner)
recipient: Codex / DeepSeek Harness
base_commit: 093430c75a46d28ed759ec646039bf2f55e3d429
delivery_head: e2c07fa9b172c7a585653e376f309e3e39abd026
status: in_review
---

# Handoff：P16 Codex Owner 交付

## 交付结果

实现 head `e2c07fa9b172c7a585653e376f309e3e39abd026`，分支 `codex/P16-reader-export-core`，worktree `G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE`。用户指定的实际 base 为 `093430c75a46d28ed759ec646039bf2f55e3d429`。`de4f1fc56f8d3c37449b8be8fc578089043fb701` 补入范围审计和资源 manifest；随后 Task 元数据与本 Handoff 由文档提交归档。实现 head 作为 Review/集成的固定代码对象，Task 仍为 `in_review`。

- Reader：实现 projection、原图/译图资源投影、独立模式进度、RTL/LTR/Webtoon 单长图 Page、源像素 `scroll_offset_y` 持久化和重开恢复。
- Export：实现 `StartExport`、snapshot/history/cancel、PNG/ZIP/CBZ/PDF/文本格式、顺序/hash/lineage、stale 策略、取消清理和发布前持久快照事件。
- 安全：Core 通过 host-only 注入 seam 获取 grant；在写任何目标前验证并原子消费 `ExportTargetRef`。公开 JSONL 不提供 grant 注册命令；路径本身不授权写入。
- PDF：新增无 Qt 的 PDF composer；`pdf_qt.py` 未修改。
- 协议：envelope major 2/minor 1；既有 resource channel 未修改。

变更仅在 P16 allowlist。具体 AC 对照和 6 类拒绝判别见 `verification/P16/ac-matrix.md`、`ac3-target-ref-matrix.md`；host issuer 遗留见 `host-issuer-todo.md`。canonical evidence 表与哈希在 `doc/tasks/P16.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC5 聚焦 | `python -m pytest tests/core/test_p16_reader_export.py -q` | task-env Python 3.12；`e2c07fa9b172c7a585653e376f309e3e39abd026` | 12 passed，exit 0 | `verification/P16/pytest-p16.log` |
| AC3 六类拒绝与原子消费 | 聚焦命令中的 6 个参数拒绝、12 线程竞争、成功后重放 | 同上 | 六类目标零写；1 次竞争消费成功 / 11 次 replay 拒绝；导出后 replay 拒绝且输出不变 | `verification/P16/ac3-target-ref-matrix.md`、聚焦日志 |
| AC2 五格式 | 聚焦测试覆盖 PNG、ZIP 三压缩选项、CBZ、PDF 两种内容层、文本 JSON/TXT/Markdown | 同上 | PASS；断言顺序、文件 hash、逐页 lineage/revision/hash、PDF 文本 | `verification/P16/ac-matrix.md`、聚焦日志 |
| AC6/AC8 Core 回归 | `python -m pytest tests/core -q` | task-env Python 3.12；固定实现 head | 352 passed、0 failed、1 Pillow `Image.getdata` deprecation warning，exit 0 | `verification/P16/pytest-tests-core.log` |
| Python 编译 | `python -m compileall -q src/application/reading src/application/export src/infrastructure/export src/bootstrap/core_service.py src/bootstrap/core_assembly.py tests/core/test_p16_reader_export.py` | task-env Python 3.12 | exit 0 | `verification/P16/py-compile.log` |
| AC7 范围 / resources | `git diff --name-only 093430c75a46d28ed759ec646039bf2f55e3d429..HEAD`；main status 比对 | 本 worktree + 只读主仓 | allowlist 内；主仓既有 19 条 tracked dirty 未改 | `verification/P16/scope-audit.md`、`resource-manifest.json`；最终命令输出由接收者复核 |
| AC9 Review / 集成 | 未运行 | — | `NOT_RUN`：Owner 不自审；Coordinator 未集成 | Task 与本 Handoff |

所有 pytest 日志包含 PowerShell shell、指定解释器路径、工作目录、原命令、完整输出和 exit code。只有上述 1 条既存 Pillow 弃用告警；没有 skip。

## 接收方式

- 固定审查范围：base `093430c75a46d28ed759ec646039bf2f55e3d429` → implementation head `e2c07fa9b172c7a585653e376f309e3e39abd026`。
- 分支/worktree：`codex/P16-reader-export-core` / `G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE`。
- 复现：在该目录使用 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q`。不得安装依赖。
- host issuer 不属于该固定代码；未来 host Task 需新增 Tauri host-only 签发与注入 adapter，详见 `verification/P16/host-issuer-todo.md`。

## 下一任务建议（必填）

- **Task ID / 标题**：P16 — 非作者独立 Review（当前 `in_review` Task 的下一 Gate）；Review 通过后由 Coordinator 执行串行集成。
- **推荐 Agent / Reviewer**：DeepSeek Harness，作为非作者 Reviewer。Codex Owner 不审核自己的实现；Coordinator 由 Codex 按协作协议承担。
- **推荐原因与前置依赖**：实现与 AC 证据已固定，聚焦/全量 Core 测试均通过；Task AC9 明确要求独立 Review 与 Coordinator 集成。Review 前置依赖为本 Handoff、Task 及 `verification/P16/**` 证据。
- **Recovery point**：仓库 `G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE`；branch `codex/P16-reader-export-core`；固定 base `093430c75a46d28ed759ec646039bf2f55e3d429`；固定实现 head `e2c07fa9b172c7a585653e376f309e3e39abd026`。实现代码位于该 head；后续文档提交不改变代码 head。
- **允许修改路径**：Review 只读仓库代码/契约/测试；Review 结果写入 `verification/P16/review.md`。如提出修复，停止只读 Review，交 Codex Coordinator 在另行确认范围后处理。禁止 Reviewer 改实现、契约、`pdf_qt.py`、`tests/reading_export/**` 或主仓。
- **交付物**：以 Standards 与 Spec 两轴记录 Review 覆盖、P0/P1 findings、复现、建议及未覆盖风险；无发现也要记录。结论未批准或存在未闭合 P0/P1 时不得集成。
- **验证命令、环境与完成 Gate**：核对固定 `base..head` diff、Task allowlist、AC3 六拒绝/零目标写与并发/重放证据、五格式/事件/取消证据、`pytest tests/core -q` 原始日志；若 Review 后有代码修改，重跑受影响 Gate 并重新审查。完成 Gate 为 Review 无未闭合 P0/P1，Coordinator 集成检查通过并更新 Task/STATUS；不得把 `NOT_RUN` 记为 PASS。
- **可直接转发给 Agent 的指令**：

  > 请作为 P16 非作者 Reviewer，只读审查仓库 `G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE` 的 branch `codex/P16-reader-export-core`，固定 base `093430c75a46d28ed759ec646039bf2f55e3d429`、implementation head `e2c07fa9b172c7a585653e376f309e3e39abd026`。按项目 `doc/templates/REVIEW.md` 的 Standards 与 Spec 两轴检查 P16 Task/契约 rev 2.1、真实实现及测试，优先复核 AC3：六类 `ExportTargetRef` 拒绝、零目标写断言、并发原子消费与成功后重放；另核五格式、事件持久化后发送、stale、取消清理及 allowlist。引用可复核文件/行号并写明触发条件、影响、复现和建议；无发现也记录覆盖和遗留风险。Review 报告写入 `verification/P16/review.md`，不得修改代码、冻结契约、`pdf_qt.py`、`tests/reading_export/**` 或主仓。独立 Review 完成后由 Coordinator 决定集成；不得自行合并或把未跑项标 PASS。

后续产品工作：Tauri host issuer 是单独 host Task，当前 `in_review` 与本 Review 不授权实现；授权范围和待办见 `verification/P16/host-issuer-todo.md`。

## 风险与遗留

- host issuer 尚未实现；Core 私有 `_register_export_target` / `_revoke_export_target` seam 需在后续 Tauri Task 通过 host-only adapter 接入。此 seam 不在公开 JSONL 命令面。
- Webtoon display↔source coordinate 转换由 Reader view 执行；本 Task Core 端保存并恢复 §6.3 定义的原图像素坐标，后续 UI/host 需完成显示坐标映射。
- PDF searchable dual-layer 依赖 Windows 可用字体覆盖所需 glyph；缺少覆盖时应按导出失败处理，不静默输出损坏文本。
- Review、Coordinator 集成和集成后的回归仍未执行。取消已发布文件不回滚已完成的原子发布，遵循契约终态语义。
- 回退方式：在独立分支保留 `e2c07fa9...` 供审查；若需修订，新增修复提交与新 Handoff/head，不覆盖或重写固定交付历史。
