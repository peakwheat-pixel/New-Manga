P02PRE-R1H 独立静态 Review 派发

角色：你是独立 Reviewer，未参与此 Owner 实施。Owner=/root/p02_r1h_codex_owner；Integrator=/root。请审查候选的完整变更并单独提交 Review 报告，不要修改实现文件，不得审核自己的实现。

冻结对象：
- 仓库：G:\CODEX\New Manga
- Owner worktree：C:\Users\49745\.codex\worktrees\p02pre-r1h-codex
- Branch：agent/codex/P02PRE-R1H
- 冻结 Task base：946938bd0696dfddd01f87d61fe6723c63ecdc86
- remediation parent：256e3ea622cba7a658020ddcf015b18894d88b38
- delivery HEAD：4a02811d6edf9ab423d299a36c51f103e62dd5f3
- tree：95eb4b2977bded814e667b392e46ce5f76015c9f
- Pins：verification/P02/codex-p02pre-r1h-remediation-review-input-pins-20261012.json
- Pins SHA-256：66CCFB05CD3E05FF12D4C1D4C85469AA864E0A0C5CCAC2149E8AD554D9A09CA3
- 唯一允许写入：verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-20261012.md
- Review 范围：从 frozen Task base 到 delivery HEAD 的完整 diff，且仅三条路径：
  1. verification/P02/p02pre-r1h-capture.ps1
  2. verification/P02/p02pre-r1h-selfcheck.ps1
  3. verification/P02/p02pre-r1h-handoff-20261012.md

验收：
1. 独立审查实际代码与 frozen Task/manifest 的一致性，提供 VERDICT、P0/P1/P2/P3 计数、每项 finding 的稳定 ID、严重度、精确文件与行号、触发条件、影响和最小修复。确认只检查三个授权文件。
2. R1H-001：精确 frozen main/scratch status/index 预期值缺失时，代码必须在任何相关仓库查询、inventory、target 触碰前 fail-stop 为 UNPROVABLE；不能把 status 查询成功、本轮 index 前后相同或新读值当成 frozen equality。非 reparse symlink skip 不得在无法证明冻结基线时放行。
3. R1H-002：index parser 保留 stage，并对任何 nonzero/unmerged stage、重复/冲突/格式异常 fail-stop；不得只保留 mode 后丢弃 stage。
4. R1H-003：skip 仅能针对可明确证明的普通文件 leaf；Device、provider/属性未知对象必须 stop；不可追加目标内容读取、ACL、枚举或新的 API/path。
5. R1H-004：静态 self-check 必须绑定实际 AST/control-flow 分支，覆盖 skip 状态写入、break、外层 continue、hash/ACL/枚举/目标读取的顺序与禁用操作，并有足以杀死这些回归的 negative cases。不要把字符串匹配或复制纯函数夸大为实现证明。
6. 检查异常路径、错误处理、Handoff 声明是否有代码证据；不得扩展原 Task 的路径/API/子进程或执行范围。

Review 限制：
- 仅静态阅读、diff 和必要的只读 Git 元数据。
- 不运行 PowerShell parser、self-check、preflight、capture、getter、任何测试、Build/Cargo、AC1–AC7、OS 动态验证或 Sandbox。
- 不修改候选、Task、Plan、STATUS 或其他报告。
- Review 与 Gate/Integration/运行证据分开。即使实现符合 Task，也只给 Review verdict，不宣称 Gate/P02PRE/Build/AC PASS。
- 若证据不足，明确 UNKNOWN / NOT_VERIFIED。可参考先前报告的 R1H-001..004，但必须独立基于此次冻结完整 diff adjudicate，避免照抄或沿用旧结论。

交付报告应引用 Pins、实际 HEAD 和文件行号，记录实际读取/命令及其结果，并说明限制。