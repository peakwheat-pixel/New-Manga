---
task_id: TASK-003
reviewer: Codex
author: DeepSeek Harness
base_commit: 9472df5c44a1bad24cda639201b0824a9ea5eecc
reviewed_head: 6caefe1201428ad9cf0636173567c8cc0b7aba80
decision: changes_requested
---

# Review：TASK-003 复审（6caefe1）

审查日期：2026-09-14（Asia/Shanghai）。本报告固定审查 `9472df5..6caefe1`。后续 Handoff/元数据提交 `7aacac1`、`05eb18f` 仅用于核对交付，不改变被审内容。

## 范围与依据

- 需求与规则：`doc/tasks/TASK-003.md`、D07、D08、D13、TASK-002 最小契约、`doc/09_COLLABORATION.md`。
- 首次 Review：`doc/reviews/TASK-003-588383f.md` 的 R-001～R-010。
- 固定差异：9 个路径，均位于 TASK-003 `allowed_paths`；D08、AGENTS、STATUS 与其他 Task 未修改。
- 审查轴：Spec、Architecture/Standards、Verification。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-011 | P1 | `doc/fixtures/MANIFEST.md:22-28`；`verification/TASK-003/verify.ps1:138-139` | Task AC2 要求未取得素材标为 `missing`，但 Manifest 同时把 `planned` 定义为“尚未执行/仍属未取得”，并声称未取得时“只能是 missing”；验证脚本又允许 `planned`。状态边界自相矛盾，R-007 的防线仍可被 `planned` 绕过。 | 把任一未取得行从 `missing` 改为 `planned`，现有状态/Hash 检查仍接受。 | 删除库存行可用的 `planned` 状态，或给出与“未取得必须 missing”互斥且可验证的定义；脚本必须拒绝未取得库存行使用 `planned`。 | open |
| R-012 | P2 | `doc/fixtures/MANIFEST.md:37-43`；`verification/TASK-003/verify.ps1:141-145` | Manifest 声明 `available` 必须同时满足许可、SHA256、可复现生成方式，但脚本只验证前两项；空白或占位“生成方式”仍可能通过。 | `available` 分支只读取 `$fxSource/$fxHash/$fxState`，未断言生成方式单元格。 | 对 `available` 行验证生成方式非空、非占位，并符合 generated/acquired 对应口径。 | open |
| R-013 | P2 | `verification/TASK-003/verify.ps1:83-88` | 脚本只固定总数、7 个 global ID 与 `ACG-EXT-*` 数量，没有固定 10 个主题 ID和7个扩展 ID的完整集合；同步替换错误 ID 后两表仍可能 PASS。 | 当前内容的 24 个 ID 正确，但脚本未把完整预期集合与两表比较。 | 固定并比较完整 24-ID 集合。 | open |
| R-014 | P2 | `doc/verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md:186`；`doc/13_ACCEPTANCE_TRACEABILITY.md:231` | 两处称 D08 §73 最终 Checklist 有 18 项，权威 D08 实际只有 17 个勾选项，派生摘要不一致。 | 独立统计 `# 73` 至 `# 74` 之间的 `^[ ]` 项得到 17。 | 改为 17 项，或不复制数量、只回链 D08 §73。 | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定对象与祖先关系 | `git rev-parse`；`git merge-base --is-ancestor 9472df5 6caefe1` | Git 2.52 / `6caefe1` detached | PASS | base/head 可解析，祖先检查 exit 0，diff 非空 |
| 作者验证脚本复跑 | `pwsh -NoProfile -File ./verification/TASK-003/verify.ps1` | Windows / `6caefe1` detached | PASS，exit 0 | 12 条 PASS；只代表作者护栏运行成功 |
| 空白检查 | `git diff --check 9472df5 6caefe1 --` | 同上 | PASS，exit 0 | 无输出 |
| 185 AC 保留 | 脚本与独立 D08 diff 检查 | 同上 | PASS | D08 相对基线无变化，185 个标题保持 |
| R-001～R-010 内容处置 | 阅读 `c55ec27..6caefe1` 完整 diff，并对照首次报告 | 同上 | PASS | 权威边界、ACG-SYNC、性能协议、Smoke、容量路由、F-08 与隐私语义已修订 |
| F-08 | `git diff --unified=0 9472df5 6caefe1 -- D02 D04 D11` | 同上 | PASS | 三文件各新增一条 `Blocked → Cancelled`，0 删除 |
| Fixture 生命周期护栏 | 人工阅读 Manifest 与脚本状态分支 | 同上 | FAIL | 见 R-011/R-012 |
| ACG ID 与 Release Checklist 派生准确性 | 对照规范、D13 与 D08 | 同上 | FAIL | 当前 ID 正确；护栏和条目数量见 R-013/R-014 |
| Mermaid 渲染 | 未执行 | 同上 | NOT_RUN | 仅完成围栏与链接检查 |
| 产品、模型、性能、SQL、打包 | 本 Review 不执行 | 同上 | N/A / NOT_RUN / BLOCKED | 仓库无产品实现；素材和阈值未就绪 |

### Standards

所有变更路径符合 Task 白名单，未发现生产代码、Schema、依赖或其他 Task 越界。后置 Handoff 符合“内容 head 之后追加”的仓库约定，不要求它存在于 `6caefe1`。R-011 是明确规则冲突；`planned`/`missing` 也构成命名边界不清。

### Spec

R-001～R-010 的正文处置基本成立，185 AC、F-08、性能协议与权威边界符合要求。R-011 仍违反 AC2，故不能批准；R-012～R-014 为需同步处理的护栏与派生摘要问题。未发现新功能或产品范围扩张。

### Verification

固定 head 上作者脚本和 `git diff --check` 均通过，但脚本没有捕获 R-011～R-014，不能以该 PASS 替代内容审查。

## 结论与复审

`decision = changes_requested`。`6caefe1` 不可集成。Owner 仅需处理 R-011～R-014，生成新内容 head 与对应 Handoff；复审继续绑定 `base_commit=9472df5` 和新 `reviewed_head`。TASK-004 不受本结论影响。
