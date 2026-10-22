# P02PRE-R1H Round6 独立静态 Review

日期：2026-10-12（Asia/Shanghai）。Reviewer=`/root/p02_r1h_remediation_review`，非作者；Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。实际模型/力度未暴露，记录`UNKNOWN`。

VERDICT=`BLOCKED_BY_MISSING_EVIDENCE / INPUT_PIN_MISMATCH`；P0/P1/P2/P3=`0/0/0/0`（候选代码findings，不代表批准）。静态阅读未发现新的候选实质问题，但审后Task pin已变化，冻结输入不再一致；本报告不批准该交付，等待Integrator重新冻结或独立对账。

## 固定对象与 pins

Task=`P02PRE-R1H`；base/parent=`dd5d2e3bc8e0702da9d059131f6364a997897661`；reviewed HEAD=`c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`；tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`；branch=`agent/codex/P02PRE-R1H`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`；common-dir=`G:/CODEX/New Manga/.git`。上述refs均只读实测匹配，受控status前后为空。

Frozen prompt=`verification/P02/codex-p02pre-r1h-round6-review-dispatch-20261012.prompt.md`；pins=`verification/P02/codex-p02pre-r1h-round6-review-pins-20261012.json`（SHA-256=`2FC64501F65DB60F04B3778B63B6BB66F6E3CF8965F060EDD812FCC9344FE8AA`）。**Pre referencePins=5/5 MATCH、scopePins=3/3 MATCH，合计8/8；post referencePins=4/5 MATCH、scopePins=3/3 MATCH，合计7/8**。完整base→HEAD diff精确为：修改selfcheck，新增Round6 Handoff；capture无变更。Candidate pins：

- selfcheck：57812 / `6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9`。
- Round6 Handoff：3551 / `700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658`。
- capture：93124 / `0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3`，与原冻结内容相同。

唯一审后不匹配项：`G:/CODEX/New Manga/doc/tasks/P02PRE-R1H.md`，冻结值43604 bytes / `E613FFED6968A93AA76F652A17434D45B684F2E17D9CFEA9824AF71F2F8302F3`；实测当前43654 / `2A27B01C770D6A2FE2829FD6FC0F723E2ABAAD4AD703AC3040AF8DD0C0F93D06`。本Reviewer没有修改Task；变化原因/具体内容本次未继续调查。发现后立即通知root停止沿用批准，并停止实质Review；不更新pins。以下是漂移发现前的静态观察，不能作为新的批准或Task条件不变凭证。

## 根因与修复的独立对照

Round5证据记录PS7.6.6/Core、PID48356、directParser两脚本errors=0、selfcheck exit=1，并标`AST_CHECK_FAILED_REAL_COMPONENT_LOOP_CONTRACT`/旧line648；engine capability另有PASS，不能抵销自检失败。独立failure JSON的stderr raw为空，仅保存bytes/hash及failureLocation分类，本Review不冒称从它复现了原始stderr全文；具体拒绝原因由当前源码与parent diff直接核对。

Capture实际component loop中：

- **511**：`$part = $parts[$partIndex]`，一处`IndexExpressionAst`。
- **521**：`$indexEntry = if (...) { $indexModes[$relative] } ...`，另一处。

旧selfcheck要求Body中恰好一处索引且为`$indexModes[$relative]`，与这两处实际合法索引冲突，因而可静态确定其拒绝原因。新selfcheck **383–387** 明确要求总数2，并对两段精确文本分别要求出现1次；没有允许任意索引、通配receiver或只检查数量：添加第三处会在384停止，改成未知索引、删掉一种或重复同一种会在386停止。这关闭已识别的静态false-negative，不等于新候选全部自检已成功。

两处索引与原approved路径组件拆分/Git index查询配套，不增加文件内容、link target、ACL、registry或枚举访问。完整base→HEAD selfcheck仅该谓词修订，Handoff明确原因、三文件pins、only diff-check、未执行项目以及Owner不自审/集成，与delivery范围一致。

## 覆盖与回归核对

真实component loop的命令/member/assignment/control-flow白名单、精确`$parts.Count`仍保留；helper的Static/receiver/method/argument窄规则保持。13条outer prefix、staging nested guard、object-key字典读取、state/flag/break和outer continue约束没有修改。既有内存source mutation fixtures仍覆盖skip前hash、skip内ACL/枚举/内容/状态、break/continue/flag旁路、loop间隙，以及四种prefix注入；source只供解析/AST contract检查，没有执行变异内容的代码路径。本轮没有新增fixture，但新“2项且各1次”谓词对未知/额外索引的拒绝可从静态结构直接看见；实际判别力仍需后续运行。

Capture字节未变，no-follow skip、ordinary-file/type/stage限制、nil冻结Git基线的UNPROVABLE fail-stop和证据CreateNew/失败保留语义未回归。没有新增API/path/executable或产品范围。此前R1H-001..007静态处置保持；Git基线缺失仍UNPROVABLE，不以自检修复解除capture barrier。

Task当前Round6合同与两文件范围一致；历史Round5 FAILED保留。当前Round6 AC2/AC4=`NOT_VERIFIED / NOT_RUN`；AC5/capture/Build/Cargo/系统AC未运行；Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE。Round5 preflight及integration证据只作历史环境/字节背景，不延用为Round6运行PASS。本Review不更新AC/Gate。

## 实际读取、命令与限制

- 读取frozen prompt/pins、Task当前Round6段、manifest、完整Round6 Handoff、完整base→HEAD selfcheck diff，当前selfcheck相关helpers/prefix/index/control-flow/fixtures及capture实际component loop。相同capture既有逐段阅读结合本轮hash未变，不采信Owner摘要代替相关代码。
- 读取Round5 failedselfcheck JSON、enginepreflight JSON相关result/checks、integrationexecution JSON结构与其冻结hash；未重新审计integration全493429-byte事件链，不把它扩张为本轮宿主安全证明。
- `Get-Item`/`Get-FileHash`对8项冻结输入前后核对，pre8/8、post7/8，定向复核确认Task bytes/hash变化；`git rev-parse HEAD HEAD^{tree} HEAD^ --path-format=absolute --git-common-dir`、`branch --show-current`匹配pins；`git diff <base>..<head> -- selfcheck-path`、`diff --name-status <base>..<head>`仅两授权路径，exit=0。
- `git --no-optional-locks status --porcelain=v2 -z --untracked-files=all -- . ':(exclude).tmp.driveupload'`前后为空；没有访问该排除路径。
- 仅写本报告。没有运行Parser/selfcheck/fixtures、preflight、capture、getters/APIs、tests、Build/Cargo、AC1–AC7、OSdynamic或Sandbox；未改任何candidate/governance/pins/evidence，未集成或adjudicate。

下一步可直接交root：先查明Task审中修改原因，以实际变更重新冻结输入或派独立source reconciliation；候选保持`agent/codex/P02PRE-R1H@c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`。本报告不能批准集成57812-byte selfcheck，必须先消除INPUT_PIN_MISMATCH并形成有效Review/adjudication；随后才按新冻结范围安排集成/真实重测。不要覆盖或删除旧Round5 FAIL。Reviewer交付后停止，不集成、不改pins。

未运行Round6自检/fixtures或动态验证；Task审后pin漂移使本次Review阻塞，不能沿用静态批准，其他运行问题仍未验证。
