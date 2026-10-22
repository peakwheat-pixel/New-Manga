# P02PRE-R1H-H2-COLLECTOR — R4 Review adjudication

## 裁决

**`CHANGES_REQUESTED`；R4 delivery head `b2cea30d05fd66b731bf8caf18358912eb66ebe6` 不获批准。** Task 回到 `in_progress`，由 Antigravity 在同一专用 worktree 完成 R5；Reviewer 仍为 DeepSeek Harness。H2-RUN 继续 `proposed`，没有授权 live collector。

DSH 的 exact-head report 为 [dsh-source-review-r4.md](dsh-source-review-r4.md)，exit 0。Codex 对 DSH manifest 的 8 项输入逐项做 post-review SHA-256 与 byte count 核验，8/8 均匹配；两个代码文件的 Git blob、HEAD blob 和 worktree blob 也匹配。核验记录：[source-review-r4-input-verification.json](source-review-r4-input-verification.json)。

## Finding 裁决与 R5 验收

1. **P2-1：判别力测试未完成，阻塞。** R4 collector 的错误分类本身正确，但 selftest 只检查源码字串、shape 工厂及复制的结果映射，没有驱动生产代码中的分类和 check-result 分支。R5 应将最小纯分类/映射逻辑提取为 collector 与 selftest 共用的函数，并覆盖真缺失、非缺失属性异常、真实存在三例；断言 absence/error shape 与 `PASS`/`NOT_VERIFIED` 结果。负例必须能在分类或映射反转时失败。

2. **P3-1：selftest 探测系统路径，需修复。** 删除对 Git、Whoami、PowerShell 安装路径和仓库 Task 文件的实时文件系统探测。用源码/AST 断言验证这些路径进入 `$chainPaths`；不得以系统路径作为动态 fixture。

3. **P3-2：启动器路径链失败后仍继续执行，按安全边界提升为 P2，需修复。** `path-chain-fixed-paths` 当前只记录 FAIL，脚本还会读取 H1 Task 并执行 launcher。R5 必须在产生链 observation 后立即 fail closed，保证任何 snapshot 读取或 `git`/`whoami`/PowerShell 启动发生前先确认所有固定执行/读取路径为 ordinary、non-reparse。selftest 以受控逻辑/静态顺序断言验证硬停位置，不探测系统路径。

4. **P3-3：runtime exclusion selftest 重写了生产逻辑，需修复。** 将 `$PSHOME` 派生路径的纯字符串 exclusion guard 做成生产与测试共用的最小 helper；测试用 `.tmp.driveupload` 下的虚构路径触发 guard，不访问该路径。保留 `GetterInput` 早于 getter body 和任何 filesystem API 的验证。

5. **P3-4：Owner Handoff byte 数错误，需修复。** Codex 复算 R4 固定代码文件：collector 107,299 bytes，selftest 57,555 bytes；SHA-256 和 Git blob 均与 manifest/`b2cea` 一致。R4 Handoff 中 107,386 / 58,641 两个数字错误。R5 Handoff 应统一写入复算的实际 byte count，并由 Codex 再次独立核验新 delivery head 的 SHA-256、byte count 与 Git blob。

6. **P3-5：记录保真度小项，当前非阻塞。** 可在同一 allowlist 补充属性查询错误的 `HResult`、`LinkTarget` 读取异常字段，并加强 reparse 分支 selftest 的结构提取；若 R5 不处理，Handoff 与 Task 必须明确列为保留的非阻塞限制，不能声称已覆盖。

R2-01..04、P4 与 R3-CX-02/03 的既有源码修复在 R4 复审中通过；R3-CX-01 的生产代码分类通过，但相应行为验收缺少有效测试；R3-CX-04 的路径集合正确，使用前硬停与禁止系统路径探测要求未满足。R4 不产生 live-run 许可。

## 禁止范围与重新审查

R5 仅限既有两份 PowerShell 脚本、Owner Task/Handoff 与 Task-local Parser/selftest 日志。不得运行 live collector、registry/ACL/profile 查询、executor、Build/Cargo、AC 或 Sandbox；不得读取或改写 `.tmp.driveupload` 子树；不得修改根仓库 `.git/index`。完成后固定新的 code commit、文档 commit、源文件 SHA/bytes/blob，运行 Parser 和纯 selftest，由 Codex 在精确 head 独立复测，再提交 DSH exact-head 非作者 Review。R4 verdict 不转移到 R5。

## 状态

Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`；历史 H1 v2 `PRE_RUN_PASS` 及 P2-1 `OPEN` 原值不变。H2-RUN 仍为 `proposed`。
