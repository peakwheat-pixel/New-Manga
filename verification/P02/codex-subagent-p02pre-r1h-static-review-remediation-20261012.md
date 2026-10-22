# P02PRE-R1H remediation 独立静态 Review

Reviewer：`/root/p02_r1h_remediation_review`；Owner：`/root/p02_r1h_codex_owner`；Integrator：`/root`。Reviewer 未参与实现，未修改候选。

VERDICT：`CHANGES_REQUESTED`。P0/P1/P2/P3 = `0/0/2/0`。这是静态 Review verdict，不是 Gate、运行或集成批准。

固定 base：`946938bd0696dfddd01f87d61fe6723c63ecdc86`；完整 reviewed HEAD：`4a02811d6edf9ab423d299a36c51f103e62dd5f3`；tree：`95eb4b2977bded814e667b392e46ce5f76015c9f`；branch：`agent/codex/P02PRE-R1H`；worktree：`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`；common directory：`G:/CODEX/New Manga/.git`。

派发文件 `verification/P02/codex-p02pre-r1h-remediation-review-dispatch-20261012.prompt.md` SHA-256=`79786443FE374E25989AE049A81A5B3949A45578B3E20B3150FE61BEB30799DB`；pins 文件 `verification/P02/codex-p02pre-r1h-remediation-review-input-pins-20261012.json` SHA-256=`66CCFB05CD3E05FF12D4C1D4C85469AA864E0A0C5CCAC2149E8AD554D9A09CA3`。实测两项相符，5 项 source 与 3 项 candidate 的 bytes/SHA-256 全部 `8/8 MATCH`。Pins 中 reviewer 名为旧 fallback，实际本轮独立 Reviewer 是上述新身份，不能据此声称旧 Agent 执行了本轮审查。

完整 base..HEAD diff 只新增三条授权路径：capture（1287 行）、selfcheck（331 行）、Handoff（62 行），共 1680 行。只审查这三个候选文件，治理和冻结输入仅作需求/事实参照。

## Findings

### R1H-005 — P2：helper AST 禁令拒绝候选现有的纯内存方法

位置：`verification/P02/p02pre-r1h-selfcheck.ps1:278`（判断在 280，throw 在 281）；对应 `verification/P02/p02pre-r1h-capture.ps1:144` 与 `:398`。

触发：self-check 走到 helper 检查，按 `FindAll` 查找 `Get-LinkTypeEvidence` 和 `Set-RepositoryStop` 内任意 `InvokeMemberExpressionAst`，发现一个即 throw。实际前者调用 `[string]::IsNullOrEmpty`，后者调用 `[Math]::Max`；两者都属于被禁止的成员调用节点。因此即使前面所有断言通过，当前合法候选仍会被拒绝，无法满足 AC2/AC4 的 self-check 条件。此结论来自静态代码结构；未运行 self-check，也未伪记测试失败。

最小修复：对这两个既有、纯内存调用进行精确接收者、方法、参数及所在 helper 的白名单校验，继续拒绝其它命令/成员调用；增加一个合法 helper 正例及外部操作注入负例。不得通过删除整个 helper 安全检查放宽范围。

Disposition：`OPEN`。

### R1H-006 — P2：AST 检查缺少真实控制流的负例，仍能漏掉 skip 前后的目标访问

位置：`verification/P02/p02pre-r1h-selfcheck.ps1:263`、`:272`、`:284`、`:298`；复制的纯函数断言位于 `:21`、`:107`–`:232`。真实候选组件循环及 continue/hash 位于 capture `:510`–`:550`。

触发与影响：现有禁止操作检测只覆盖 skip 分支内部和 continue 分支内部。外层顺序仅证明组件循环、continue 和一个 `Get-FileHash` 的文本 offset 顺序，没有检查组件循环中 skip 之前的额外 target/hash/ACL/枚举调用，也没有检查组件循环结束至 continue 之间的操作。例如在 capture 的组件循环结束（547）与 `if ($linkSkipped) { continue }`（548）之间加入 `Get-Acl -LiteralPath $full`，既不改变被检查的 skip block，也不改变 hash 数量、continue 的父循环和 offset 关系；现有 AST 条件仍接收这个会访问已 skip 项的回归（在 R1H-005 修正后）。相应 AST/control-flow 变异负例在 self-check 中不存在；stage/Device/mismatch 负例调用的是自行复制的函数，并不能证明实际候选函数或控制流发生回归时会被拒绝。

最小修复：将实际组件循环内 skip 前后的允许操作及循环结束至 continue 的区间纳入 AST 校验，绑定实际 state 写入、flag、break、continue 的直接所在 block 和顺序；在内存中对真实候选 AST/source 做最小变异负例，覆盖增加 hash/ACL/枚举/target 读取、改变 state、删除或绕过 break/continue，逐例断言拒绝。仅运行解析/纯内存检查，不执行候选或 getter，不扩大路径/API。

Disposition：`OPEN`；旧 R1H-004 尚未充分解决。

## 旧 findings 的本轮独立处置

| ID | 本轮静态证据与处置 |
|---|---|
| R1H-001 | `FIXED_BY_FAIL_STOP_STATIC`：capture 178–181 将两仓 frozen status/index 明确保持 null，401–407 在任何该函数中的路径/Git/inventory 查询前返回；795–823 将 main 条件分类为 UNPROVABLE 并设置 stopReason，后续 scratch 和其它阶段由 stopReason 阻断。没有用 live 读值充当冻结值。安全放行条件仍 `UNPROVABLE`，未完成双仓动态基线核验；Handoff 明确这一限制。 |
| R1H-002 | `FIXED_STATIC`：capture 249–270 保存 mode/stage，拒绝非零 stage、重复/大小写冲突与未知 mode；inventory 521–524 再检查 stage 0。运行验证 `NOT_RUN`。 |
| R1H-003 | `FIXED_STATIC`：capture 161–167 只接受精确 FileInfo 与显式属性位，517–525 在分类前拒绝未知类型/属性。非-reparse skip 内没有内容 hash、ACL、枚举或 target 解析。运行验证 `NOT_RUN`。 |
| R1H-004 | `OPEN`：本轮 R1H-005 与 R1H-006。新增 AST 校验确有进展，但合法输入必被拒绝，且缺少控制流回归的实际负例。 |

Architecture：变更仍为原执行契约下的安全停止与窄分类，未见新增 executable、输出、registry/ACL 写入或产品架构改动。当前冻结 null 值使 inventory/skip 路径不可达；不得把该不可达性当作未来补全基线后的 skip 安全证明。`Test-FrozenGitBaselineMatch` 只在纯函数断言使用，真实仓库路径没有进行完整 frozen equality；Handoff 已明确后续须独立冻结输入及双仓预检，不能仅填入 null 后直接放行。

Verification：只做静态读取与必要 Git 元数据。Parser/self-check/preflight/final pre-run/capture、getters、Build/Cargo、AC1–AC7 和 OS 动态验证全部 `NOT_RUN / NOT_VERIFIED`。未查询、安装、启用或启动 Windows Sandbox。

## 实际读取/命令与结果

- `Get-Content -LiteralPath ...`：读取派发、pins、Task、manifest、协作协议、Plan/STATUS/索引当前段、checkpoint 当前段、Ponytail skill、三份候选及按行号分段内容；exit=0。个别大块显示截断后使用针对分段补读；未执行所读脚本。
- `Get-FileHash -Algorithm SHA256 -LiteralPath ...` 与 `Get-Item`：仅核对上述派发/pins 和已枚举的 8 项 Review 输入 bytes/hash；exit=0，全部相符。
- `git -C <owner-worktree> rev-parse HEAD`、`rev-parse HEAD^{tree}`、`branch --show-current`、`rev-parse --path-format=absolute --git-common-dir`：exit=0，结果如冻结对象。
- `git -C <owner-worktree> diff --stat <base>..<head>`、`diff --name-only <base>..<head>`、完整 capture diff 与 remediation parent..HEAD capture diff：exit=0，范围仅三文件；逐行审查候选 self-check/Handoff。没有运行 git status，因此没有访问 excluded staging path。
- 本报告是唯一写入。候选、Task、manifest、Plan、STATUS 均保持未修改。

## 下一步

由 `/root` adjudicate 后将 R1H-005/R1H-006 转发 `/root/p02_r1h_codex_owner`；恢复点是上述 worktree/branch，base/head=`4a02811d6edf9ab423d299a36c51f103e62dd5f3`。Owner 仅修复三条已有授权路径并提交新的 Handoff/head，静态 Review 前仍只可运行 Task 允许的 `git diff --check`；禁止 parser/self-check/capture/getters/Build/Cargo/AC。新 commit 须由非作者再审，不沿用旧批准。R1H 完成或关闭与后续释放由 Codex 管理，本 Reviewer 不释放任务或解除 Gate。

未运行任何 parser、测试或动态验证；上述运行行为仍 NOT_VERIFIED。风险：self-check 尚不能作为 skip 控制流的可靠证明，Build Barrier 必须保持。
