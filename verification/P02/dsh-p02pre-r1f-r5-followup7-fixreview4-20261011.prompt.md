# DeepSeek Harness 独立 Review — P02PRE-R1F R1F-R7 cohort #5 / fixreview4

## 派发与冻结来源

- Task：`P02PRE-R1F`，路径 `doc/tasks/P02PRE-R1F.md`。
- Owner/Author/Integrator/Adjudicator：Codex `/root`；本轮 Reviewer：DeepSeek Harness（非作者）。
- 固定仓库/HEAD：`G:/CODEX/New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 本轮只审文档与 Review 治理证据。不得写仓库、运行 host getter、capture、Build/Cargo、AC1–AC7、系统 API、Git mutation 或测试命令；不读取 `.tmp.driveupload` 用户暂存内容。
- Codex 已于 dispatch 前以两个独立 `git status --porcelain=v1 -z --untracked-files=all -- . :(exclude).tmp.driveupload` 查询冻结 pre-prompt 快照：`760 NUL records / 48780 bytes / SHA-256 EA78E197FF1D50155921FA1AA8963DF0B44B75B47EDB5E249A70A03B3435A8FA`，stderr 空，repeat 相同。该快照发生在本 prompt 创建前；prompt 自身会使 status 增加一条记录。不要把 pre-prompt digest 描述成创建后的当前 digest。
- 不需要验证或重算 source hashes 才可继续审查；若无法核验请写 `UNVERIFIED` 并继续可读内容 Review。Codex 在宿主机独立维护精确 bytes/SHA 记录。

## 审查问题

请独立检查下列冻结来源和最新 cohort #4 DSH report/adjudication，判断本轮文档修订是否完整、前后一致、没有新的 P0–P3 阻塞：

1. Task / manifest / Plan / STATUS / index / Task README / P02 navigation / checkpoint 对唯一 Active Task、唯一 DAG、cohort #1–#5 序号、当前 READY 下一步是否一致；cohort #4 是否标成已返回并已 adjudicate，cohort #5 是否仍为待执行/READY。
2. Task test/result 表：follow-up #6=`APPROVED (0/0/0/0)`、Codex adjudication=`REVIEW_ACCEPTED_FOR_R8_ONLY`；R8 应如实为 Windows PowerShell `5.1.26100.9549` 的 parse-only `PARSE_OK / PASS_WITH_EVIDENCE`，`captureScriptInvoked=false`；Capture 仍 `BLOCKED / NOT_RUN`。不要把 parse-only 写成 capture 或 Gate PASS。
3. cohort #4 的 F1–F4 是否已准确落实：修正 Task 行 106–108 的过期状态；统一 governance cohort 编号（与 R5 follow-up 编号分开）；更新当前 dispatch/review/adjudication 状态；修正对 cohort #3 P3-1 raw report 的转述。对于 P3-1，请直接比较 exact fixreview2 prompt/tool result、raw report 与 Codex adjudication；不要重复旧误归属。
4. PowerShell 术语是否一致：外层编排为 PowerShell `7.6.6`；冻结 R1F parser/capture target 为 Windows PowerShell `5.1.26100.9549`。文档没有证据证明 PS7 不兼容；不要提出没有依据的兼容性断言。
5. 所有文档与 adjudication 是否原样保留授权与 Gate：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。该 owner waiver 不等于技术 PASS，也不解除 Build Barrier。
6. 检查 current Plan 的中文 Mermaid DAG 与实际状态相符；不能从 R8、Review、Owner waiver 推断 Build Gate 或 AC 放行。

## 已接受的上一轮 finding 与预期修订

cohort #4=`CHANGES_REQUESTED (P0=0/P1=0/P2=1/P3=3)`，Codex adjudication 接受四项：

- F1 P2：Task 测试表状态陈旧；已更正 follow-up #6、R8 与仍阻塞的 capture 状态。
- F2 P3：三轮 Review 的治理 cohort ordinal 混乱；现统一为 #1 followup7、#2 fixreview、#3 fixreview2、#4 fixreview3、#5 fixreview4，和历史 R5 follow-up 序号分开。
- F3 P3：dispatch 状态滞后；现 cohort #4 标记为已 Review/adjudicate，下一 READY 是 cohort #5。
- F4 P3：此前 Codex 对 P3-1 的复述不精确。raw report 实际声称 prompt 输入表把“修复轮 exit artifact”列为 `2 bytes / 9A271F…`，与 manifest/adjudication 的 `3 bytes / 13BF7B…` 冲突；但 exact fixreview2 prompt 和 DSH tool result 并没有那条 exit artifact 行，所以此前 `REJECTED_AS_MISATTRIBUTED` 裁定保持。当前只修正转述，不改变旧 Review verdict。

请只报告真实发现。每项必须有严重级别、确切文件与行号、当前证据、用户影响和最小修正建议；区分事实错误、文本不清和已由 adjudication 关闭的旧 finding。若没有新的阻塞，给出 `APPROVED`；否则给出 `CHANGES_REQUESTED`，不要因为 sandbox 无法执行 hash/Git 命令就把可读的文档 Review 判为失败。报告中注明 hash/Git 检查是否实际运行；不得声称执行了未运行的命令。

## 输出

请以简体中文给出结论、分级 findings、证据和是否存在未关闭的文档阻塞。保持只读。

## 精确输入 pins

| Path | Bytes | SHA-256 |
|---|---:|---|
| `AGENTS.md` | 4503 | `46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501` |
| `doc/09_COLLABORATION.md` | 19131 | `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D` |
| `doc/REBASELINE_PLAN.md` | 276875 | `3A6D19A036F7CE1E4000F991A87D950BFA0A4805E3234C5E19A41B9094DC0264` |
| `doc/STATUS.md` | 285580 | `F938B51409F99352D0061BB0FBB6B36DD6BFB929BDCCC8005961AD2DE1062C68` |
| `doc/00_INDEX.md` | 57173 | `A630503D2C8BCAD4EBFE84452A5B1F1AB6C55F8E72E2D39D5FAFF45CD51085F8` |
| `doc/tasks/README.md` | 36698 | `B860F9FB5EA8D26C64D27C17FA68BBC59DE2359AE001112DE0FEFD3DBACB49E6` |
| `doc/tasks/P02.md` | 222292 | `53D9E7B38533C1B7C3D8F3DE3B1279B0C7B6368957DCF297D1B320BC60DE8434` |
| `doc/tasks/P02PRE-R1F.md` | 26125 | `B88D9B9149F8C05F4946022672320F1BC6061DD390FF858E5EEB61125DFF54E2` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 36990 | `5313D977AA82CC5AA78757364B8FA34BC1E3D384F6CD09F4E79AA505027F2405` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 23216 | `22B6A89C35BCBD7A7E385508876C69B67442048AD7F1C612E4A4B506F5CAC927` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview3-adjudication-20261011.md` | 5149 | `B640F31D0690C606BCF234E46E4B3E5D276AD2F924EFE30ED1E77B4F24CDCEBF` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.prompt.md` | 7030 | `7F10D7708AD3305384B1BF8B2F231EDAF5170ECB52C6368DD9CDC6D89CC5A2D3` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.stdout.md` | 252709 | `682F2794C6A43A57E054CF014A8B4289D7334604AEBE23CCAC880513C00FFFAA` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview2-adjudication-20261011.md` | 3401 | `4D74A2AAB9661244DFFF9AEAD04248D427D3215A7C5FA293FB2AE54E498508C0` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.prompt.md` | 5726 | `50E73237B7441DE2B3A4EBE9FC7B800FB511E930B18600880041BC95C83AEBA5` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.stdout.md` | 100209 | `F646928900746BB7E2F99E179734015FA317E6D232E50283CB2423A0382421FA` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
