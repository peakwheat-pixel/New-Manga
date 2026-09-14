# TASK-003 集成验证证据

- 被测主线：`e3c8de7ebdf47e38d2f9b298bb1a938948b442bf`
- reviewed head：`9c6a73b8f87248d65e9b3865ef4d087b2c2fb21f`
- integration commit：`db269e98aa6783151f86ed922691840f52930afc`
- 环境：Windows 11 Pro `10.0.26200` AMD64；PowerShell `7.6.6`；Git `2.52.0.windows.1`
- 执行日期：2026-09-14（Asia/Shanghai）

| 检查 | 实际命令 | 结果 |
|---|---|---|
| 固定 head 护栏 | 在一次性 detached worktree `9c6a73b` 执行 `pwsh -NoProfile -File ./verification/TASK-003/verify.ps1` | PASS；退出码 0；12 条 PASS；worktree 已清理 |
| 固定范围空白检查 | `git diff --check 9472df5 9c6a73b --` | PASS；退出码 0 |
| reviewed head 已集成 | `git merge-base --is-ancestor 9c6a73b db269e9` | PASS；退出码 0 |
| 被审实质内容未被合并改写 | `git diff --exit-code 9c6a73b db269e9 -- doc/02_TECHNICAL_ARCHITECTURE_.md doc/04_USER_FLOW.md doc/11_ARCHITECTURE_MAPS.md doc/13_ACCEPTANCE_TRACEABILITY.md doc/fixtures/MANIFEST.md doc/verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md verification/TASK-003/verify.ps1` | PASS；退出码 0 |
| merge 拓扑 | `git rev-list --parents -n 1 db269e9` | PASS；一个提交及两个 parent |
| 集成范围空白检查 | `git diff --check 84795fb e3c8de7 --` | PASS；退出码 0 |
| 冻结边界 | `git diff --name-only 84795fb...e3c8de7 -- doc/tasks/TASK-005.md doc/tasks/TASK-006.md doc/tasks/TASK-007.md doc/tasks/TASK-008.md doc/tasks/TASK-009.md doc/tasks/TASK-010.md doc/tasks/TASK-011.md doc/tasks/TASK-012.md doc/tasks/TASK-013.md doc/tasks/TASK-014.md doc/tasks/TASK-015.md doc/tasks/TASK-016.md doc/tasks/TASK-017.md doc/tasks/TASK-018.md doc/tasks/TASK-019.md doc/tasks/TASK-020.md doc/tasks/TASK-021.md doc/tasks/TASK-022.md doc/tasks/TASK-023.md doc/tasks/TASK-024.md doc/tasks/TASK-025.md doc/tasks/TASK-026.md doc/tasks/TASK-027.md` | PASS；无输出；23 个 Task 仍为 `proposed` |

固定 head 脚本会按 `base_commit=9472df5` 检查 allowed paths；主线包含该 base 之后、TASK-003 内容交付之前的 TASK-004 并行授权元数据，因此该脚本只在固定 reviewed head 上运行。主线集成由 ancestry、merge topology、被审路径树一致性、冻结边界和全量文档检查共同验证。

产品、SQL、模型与性能测试：`NOT_RUN / N/A`，原因是 TASK-003 仅交付验收与 Fixture 规范，仓库仍无生产应用实现。
