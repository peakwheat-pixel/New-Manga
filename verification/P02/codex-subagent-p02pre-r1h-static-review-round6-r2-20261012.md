# P02PRE-R1H Round6 独立 Review — attempt 2

日期：2026-10-12（Asia/Shanghai）；非作者Reviewer=`/root/p02_r1h_remediation_review`；Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。实际模型/力度未暴露，记录`UNKNOWN`。

VERDICT=`APPROVED_STATIC_CONTENT`；P0/P1/P2/P3=`0/0/0/0`。本轮冻结候选未发现新的实质问题。此为独立静态Review，不表示AC2/AC4、parser、自检、fixtures、capture或任何Gate/runtime已通过。

## 冻结对象与pre/post核验

有效prompt=`verification/P02/codex-p02pre-r1h-round6-review-dispatch-r3-20261012.prompt.md`；pins=`verification/P02/codex-p02pre-r1h-round6-review-pins-r3-20261012.json`，实测SHA-256=`E9A82F1EC8A0447298A71390E1CEEB24BFAC35E855321CF61480459609270505`。

Reviewed HEAD=`c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`；base/parent=`dd5d2e3bc8e0702da9d059131f6364a997897661`；tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`；branch=`agent/codex/P02PRE-R1H`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`；common-dir=`G:/CODEX/New Manga/.git`。候选branch/HEAD/parent/tree/common-dir前后均实测匹配，controlled porcelain-v2 -z前后为空。

**14项绝对路径input pins：pre=14/14 MATCH；post=14/14 MATCH；mismatch=0。** Main前后仍`main@cddff58469b56e181019a8ddfeade80684bc7eb9`、tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`、index=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，与freeze一致。Task=45192 / `AE85F46FE6497260A8ACD64E93F5D8B5A3F96A638EE43FFA428EBDBDD1D20958`；Plan/STATUS/Index与JSON枚举hash均未变化。

完整base→HEAD diff精确仅：

- `M verification/P02/p02pre-r1h-selfcheck.ps1`：57812 / `6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9`。
- `A verification/P02/p02pre-r1h-round6-handoff-20261012.md`：3551 / `700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658`。

capture=93124 / `0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3`，本轮无diff且pin匹配。

Attempt1的`BLOCKED_BY_MISSING_EVIDENCE`保持历史原值；未沿用为批准。旧attempt2 pins-r2文件实测4 bytes、内容`null`，作为生成故障证据冻结，不作为有效评审输入列表。有效r3 JSON明确14项并全部复算。此次重新读取实际diff/循环/谓词/Task要求，未仅依赖Owner或attempt1意见。

## 独立代码结论

Capture component loop有两处真实索引：**511**的`$parts[$partIndex]`用于取路径组件，**521**的`$indexModes[$relative]`用于stage entry。旧predicate仅接受后者且要求Count=1，会静态确定拒绝该合法循环；这与Round5 failure artifact中的contract总括断言失败相符，而非PowerShell版本/Parser失败。

新selfcheck **383–387**要求`IndexExpressionAst`总数恰好2，并要求这两种精确文本各出现1次。新增第三索引会被384拒绝；未知索引、删除一种或重复同种导致期望种类次数不是1，会被386拒绝。不使用wildcard或任意索引许可。它纠正了已识别false-negative，但静态Review不能保证其它引擎/AST运行条件也通过。

完整实现diff只改此predicate；命令/member/redirection及assignment/control-flow约束保留。`$parts.Count`成员白名单保持精确；helper IsNullOrEmpty/Math.Max的receiver/Static/method/arguments限制未改变。真实13项outer prefix、nested staging/throw guard、object-key字典读取、两种skip的state/flag/break与outer continue前后的调用闭包均未修改。

既有negative fixtures仍是source-only内存变异，覆盖hash/ACL/枚举/target read、state变更、break/continue/flag旁路、component-loop到continue间隙及四种prefix注入；只解析/检查AST，没有执行变异source的代码路径。本轮未新增索引专用fixture，但“总数2且每一种1次”的精确拒绝逻辑可直接静态审查，实际判别力仍需root运行自检留证。

Capture no-follow、未知对象/stage停止、缺失精确frozenGit baseline前置UNPROVABLE fail-stop、CreateNew/失败保留语义保持；没有增加host API、path、executable、权限或产品范围。Handoff的base、范围、原因、pins和only diff-check/未运行声明与当前diff一致；Owner不自审或集成。未发现需要新finding的安全放宽或交付错误。

## 验证与限制

冻结Round5 failure evidence记录PID48356/exit1、Parser errors0、contract failureClass/旧line648，仍是实际FAILED历史结果。该standalone JSON的stderr raw为空，只保存416 bytes/hash及分类，不能声称本Reviewer从它复现了完整原始错误；本轮根因的直接依据是capture两处索引与predicate差异。Round5 engine preflight PASS只证明历史命令/engine能力，不证明Round6自检。493429-byteintegration evidence完成hash核对并读取结构/相关历史指针，本轮未重新审计其完整事件链，不把它扩张为当前宿主安全证明。

当前Round6 parser/selfcheck/fixtures、集成后验证=`NOT_RUN / NOT_VERIFIED`；先前R1H findings静态修复保持，但nil main/scratch status/index仍`UNPROVABLE`。本Review不更新AC2/AC4或Task完成状态；AC5/capture/Build/Cargo/system AC未执行。Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE；Owner waiver不是技术PASS。

## 实际读取/只读命令

- `Get-Content`：有效r3prompt/pins、当前Task Round6合同和冻结治理当前段、manifest、完整base→HEAD两文件diff与完整Handoff、实际capture component loop/停止分支、selfcheck index/continue/prefix/helper及fixtures；Round5 failure/engine evidence相关字段、integration evidence结构、attempt1 blocked report、旧r2prompt和null pins。相同未改部分结合此前逐段读取和本轮pins核对，结论由实际相关代码独立得出。
- `Get-Item`/`Get-FileHash`：JSON枚举14项绝对输入路径前后复算14/14；pins文件SHA匹配；主仓indexhash与main refs符合freeze。
- `git rev-parse HEAD HEAD^{tree} HEAD^ --path-format=absolute --git-common-dir`、`branch --show-current`、`git diff <base>..<head> --`、`diff --name-status <base>..<head>`：exit0，refs及完整两路径如上。
- `git --no-optional-locks status --porcelain=v2 -z --untracked-files=all -- . ':(exclude).tmp.driveupload'`前后为空、未访问排除路径；没有运行全主仓status或其他未知内容查询。
- 唯一写入本报告。未修改14项输入或任何candidate/governance/manifest/evidence，未执行Parser/selfcheck/fixtures、capture/getter/API、Build/Cargo、AC、OSdynamic或Sandbox；未集成/adjudicate。

下一步可转发root：先复核r3同一14项pins与本报告、candidate`c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`；单独adjudicate后按本轮已冻结且可恢复的集成范围安装精确selfcheck bytes，再在固定PS7环境实际重测Parser/selfcheck/fixtures，并保留历史Round5失败及新日志。不得据本静态意见直接运行capture或解除Gate。Reviewer交付后停止，root负责后续集成和执行。

未运行Round6自检或动态验证；批准仅为固定HEAD静态意见，真实重测仍可能揭示其他断言问题，Build Barrier保持。
