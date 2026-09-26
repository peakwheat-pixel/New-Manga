# M2-S1 范围登记核验

日期：2026-09-26（Asia/Shanghai）。执行者：Codex Scheduler。用户授权的是上一轮建议的**范围冻结与任务登记**，并未授权立即派发 DeepSeek Harness 实验或产品实现。

## 固定恢复点

| 检查 | 实际值 / 结果 |
|---|---|
| 真实项目 Git common-dir | `G:/CODEX/New Manga/.git` |
| 登记工作区 | `G:/CODEX/New Manga.worktrees/M2-S1-scope-registration` |
| 登记分支 | `codex/M2-S1-scope-registration` |
| 起始 `master` / 研究候选 base | `0c2e202c6aded5326bec9a5460b5142155db0240` |
| 起始 `git status --porcelain=v1` | 空；未触碰 `G:/CODEX/New Manga` 的既存 dirty checkout |
| `doc/tasks/M2-S1.md` / `verification/M2-S1/**` | 登记前均不存在，新建且不覆盖历史文件 |

## 依赖与来源

- M2-C1 Task 在起始 master 为 `done`，Integration Gate=`PASSED`；`git merge-base --is-ancestor c1765aa2fb861c1512aa633ad10960ac90673310 0c2e202c6aded5326bec9a5460b5142155db0240` exit 0。
- `git rev-parse 0c2e202:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`。Contract §10/§11 明确大媒体不走普通 JSON/Base64，通道选择与容量/权限/生命周期/清理/恢复待独立 Spike；§7.2 的事件交付性质仍未冻结。AD-001 §Migration constraints 4/6 明确二进制边界与 Python Core/SQLite 权威。
- 本登记仅为研究 Task 的来源、AC、Owner/Reviewer 建议、允许/禁止路径及验证计划。M2-R1 的 Qt 可行性实验不证明跨进程图片/tile 传输；没有把它记为 S1 PASS。

## 授权与 Gate

M2-S1=`proposed / NOT_RELEASED`；研究 Owner 仅建议 DeepSeek Harness，实际 `owner/branch/worktree` 为 `null`。Reviewer 建议 Codex，须保持非作者。正式研究执行前 Codex 必须在最新 master 重新核对依赖和范围，创建独立 Owner 工作区，固定 base/允许路径，登记 STATUS，并取得单独执行释放。若候选需要改共享 Contract、Schema、依赖、生产接口或用户可见行为，先另行冻结范围/产品决定。

本次没有研究探针、产品测试、GUI 或 IPC runtime 运行；全部为 `NOT_RUN`。登记提交前检查：`git diff --cached --name-status` 仅五份 Codex 导航文档、本 Task 与本核验文件；`git diff --cached --check` 无输出、exit 0。新登记涉及的 15 个 Markdown 相对链接路径逐一解析，缺失 0。上述检查仅验证登记文档，不把 planned 产品测试写成 PASS。
