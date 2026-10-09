请作为 P05 的非作者 Reviewer 进行只读 exact-head Review。不要修改或创建任何文件，不要 checkout/切换分支，不要提交，不要运行产品构建或产品测试。可运行只读 Git 命令与路线校验脚本。

## 固定审查对象

- Task base：`c7a41f52aec961b30ad5e3c7e7569bac042bb847`
- 必须审查的 delivery head：`a2569f38c46b7a7003cf5f729f65e3644344390f`
- 预期 tree：`83d082807765c3f685550573e484d0df3a03c16b`
- Task author：Codex；reviewer：Antigravity（因 DSH 首轮 exact-head Review=`BLOCKED` 而接任）。

先实测固定 commit、tree、parent 和 `git diff --name-only c7a41f52..a2569f38`；审查完整 Task base 到 delivery head 的差异。若工作区 HEAD 在 delivery head 之后，不能把后续 HEAD 当成被审对象；使用 `git show <fixed-head>:<path>`、固定 commit diff 等只读方式核对。若 commit/tree/hash/差异无法验证，结论写 `BLOCKED`。

另分别核对两个局部差异，方便归因：实现 `f52095eb..5288db42`，finding 修复 `b5e44d60..a2569f38`。注意 DSH 对 `5288db42` 的报告是 `BLOCKED`，不能视为通过；其静态意见已促成 RC-4 文案修复。

## 冻结范围与审查项

Task 允许路径：

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：仅 §5 `RerenderPage` 行与 §8 命令级观察注记。
- `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`：仅 `rerender_page` 行的反向链接。
- `doc/tasks/P05.md`、`doc/handoffs/P05-*.md`、`verification/P05/**`。
- `verification/PROJECT-ROADMAP-20261008/verify_plan.py`：仅 live Plan/Task 状态校验变更。
- `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`：仅 Codex 状态、导航和恢复链接。

逐条核对 P05 AC1–AC4：

1. §8 新增内容明确为命令级现状观察、非全局规范；ErrorEnvelope schema、taxonomy 与 `PROPOSAL` 等级没有改变。
2. 准确记录三组当前实现组合：`rerender_page / MISSING_REQUIRED_INPUT / unavailable / false`；`rerender_page / ARTIFACT_WRITE_FAILED / internal / false`；`resolve_page_resource / ARTIFACT_WRITE_FAILED / internal / true`。
3. 明确 `category="unavailable"` 不推出 `retryable=true`，不把同 code 的单命令现状推广为全局映射。
4. 宿主 `CORE_UNAVAILABLE` 与 Core `ErrorEnvelope` 区分，没有添加未经冻结的 envelope mapping。
5. §5 `RerenderPage`、§8 注记、RC-4 `rerender_page` 行的交叉链接双向闭合且目标存在；DSH 提出的中英混排 P3 已修复；不再有重复 Start checkpoint 记录。
6. full Task diff 只涉及允许路径；不改变协议字段、错误码/语义、Revision history、Schema、依赖、代码、测试、用户已有 ROADMAP 内容。
7. 复核 `verify_plan.py` 变更确实只切分固定日期 audit graph 与 live Plan/Task 状态验证；可运行 `python verification/PROJECT-ROADMAP-20261008/verify_plan.py`，并说明它实际读取的是哪个 HEAD/工作区。

## 输出格式

用简体中文给出：实测 reviewed commit/tree/parent；结论 `APPROVED`、`APPROVED_WITH_CONDITIONS`、`CHANGES_REQUESTED` 或 `BLOCKED`；AC1–AC4 逐项结论；P0/P1/P2/P3 finding 清单（文件/位置、依据、影响、最小修复）。无 findings 时明确零 finding。区分你实际运行的只读命令与静态阅读；不得声称执行了未运行的验证。若不能核验固定对象，必须保持 `BLOCKED`，不要根据文件内容推定 commit/tree 正确。
