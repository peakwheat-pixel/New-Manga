请对项目仓库中的 P05 实现提交作只读、非作者 Review。不得修改文件、切换分支、提交、运行产品构建或运行产品测试。

## 固定审查对象

- Task base：`c7a41f52aec961b30ad5e3c7e7569bac042bb847`
- 实现差异起点：`f52095ebf2a46f41905edede199c77f4668b8a09`
- 必须审查的 delivery head：`5288db42352d265aeb9f4f5e8c430f042e6fd279`
- 预期 tree：`ff9847ce1b5b68f24b41d215189c2cd860fc0a79`

先用 Git 读取并验证上述固定对象的真实 commit/tree；审查 `f52095eb..5288db42` 差异。当前 checkout 的 HEAD 可能在 delivery head 之后；不要把当前 HEAD 当作审查对象，也不要 checkout。若固定对象或 tree 不匹配，结论写 `BLOCKED` 并说明证据。

## 冻结范围

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：仅 §5 `RerenderPage` 行与 §8 命令级注记。
- `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`：仅 `rerender_page` 命令行反向引用。
- `doc/tasks/P05.md`：仅 AC1–AC3 完成状态记录。
- 其余路径不得因实现提交而改变。

## 必查验收

1. §8 注记明确是当前命令级实现观察、非全局规范；ErrorEnvelope schema、taxonomy 和 `PROPOSAL` 等级没有被修改。
2. 三组 command/code/category/retryable 值准确：
   - `rerender_page` / `MISSING_REQUIRED_INPUT` / `unavailable` / `false`
   - `rerender_page` / `ARTIFACT_WRITE_FAILED` / `internal` / `false`
   - `resolve_page_resource` / `ARTIFACT_WRITE_FAILED` / `internal` / `true`
3. 明确 `category="unavailable"` 不推出 `retryable=true`，且不把单命令观察推广成同一 code 的全局映射。
4. 宿主 `CORE_UNAVAILABLE` 与 Core `ErrorEnvelope` 区分，没有新增 category/retryable 映射。
5. §5 `RerenderPage`、§8 注记、RC-4 `rerender_page` 命令之间的交叉链接完整且目标存在。
6. 检查 implementation delta 是否只有 Task 冻结的上述三个路径；无产品代码、测试、Schema、依赖、Revision history 或 wire 语义改动。

## 输出格式

用简体中文给出：实际 reviewed commit 与 tree；结论 `APPROVED`、`APPROVED_WITH_CONDITIONS` 或 `CHANGES_REQUESTED`；AC1–AC4 逐项结论；按 P0/P1/P2/P3 列出每项 finding 的文件/位置、依据、影响和最小修复。没有 findings 时明确写零 finding。区分静态审查与实际运行的检查；不得声称运行过未执行的测试。若批准有条件，写明条件是否阻断 P05 `done`。
