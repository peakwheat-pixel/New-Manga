# P02PRE-R1H-R6-ZCODE-H1 — H1 独立静态 Review 报告

- **Verdict: `CHANGES_REQUESTED`**
- **Finding counts: P0=0 / P1=0 / P2=1 / P3=6**
- 审查类型：只读静态审查（未运行任何脚本、未做动态验证、未计算或声称任何 byte-hash）
- 审查输入：题面 13 项 pin 全部可读（读取深度见"Review limitations"）

---

## 一、总体判定（对应 Review 问题 1、5）

v2 的 `PRE_RUN_PASS` **没有被任何 pinned 原始输出直接证伪**，其 24 项 checks 计数自洽（23 PASS + 1 `NOT_VERIFIED`，`j-driveupload-scope` 未被转写成 PASS），`.exit`=`0`、`.stderr` 0 字节、`.json`/`.stdout`/`.stderr` 三者时间戳与内容互相吻合，且 v2 `.stdout.log` 是**完整文档**（1150 行，第 1144/1150 行有 `--- end root status verbatim ---`、`--- end of log ---` 收尾标记），与 attempt1 那份 3704 字节、无收尾标记的截断日志形成对照，说明 attempt1 的 partial-write 故障模式在**产物层面**未复现。

但 v2 作为"可审计证据包"不满足 H1 自身 AC3 的"每一项均有原始证据"要求：**23 项 PASS 中有 15 项的 `evidence` 指针在 13 项 pinned 输入内无法解析**（见 P2-1）。因此不能以"证据充分"结案。

---

## 二、Findings

### P2-1｜15 项 PASS 的 evidence 指针在 pinned 输入内不可解析，AC3"每项均有原始证据"无法成立

- **位置**：`verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.json` → `checks[].evidence`：第 172、180、188、196、204 行 = `"collection A"`（`tools`、`a-identity`、`b-registry-wer-localdumps`、`b-profile-moniker`、`c-temp-paths`，5 项）；第 244、252、260、268、276、284、292、300 行 = `"collection B"`（`e-root-refs`、`e-owner-refs`、`e-agy-refs`、`e-root-status`、`e-owner-status`、`e-agy-status`、`e-root-index-hash`、`f-protected-file-pin`，8 项）；第 324 行 = `"v2 precheck"`（`h-targets-initial`）；第 348 行 = `"write script guard"`（`h-targets-final-prewrite`）。共 **15/23** PASS 项。
- **具体证据**：对仓库 `*.md` 与 `verification/P02/*.json` 全文检索，`collection A` / `collection B` **只在 v2 JSON 自身出现，全仓库无任何定义**；v2 `.stdout.log` 无 attempt1 那样的 `--- helper: … ---` 分节（v2 全文仅 4 行 header/key-values + 1137 条 status verbatim + 3 条 agy verbatim，第 1–6、1144–1150 行）。唯一可能定义这些标签的产物是 `.json` `harnessNote`（第 153 行）自述的 `%TEMP%` 暂存文件与 write script——**在仓库之外、且不在 13 项 pin 内**；按 AGENTS.md"聊天记录不是项目事实来源"，作者会话内的原始输出不构成版本化证据。
- **为什么重要**：这 15 项里包含**全部 4 项 pre-write 前置条件中的 2 项**（`h-targets-initial`、`h-targets-final-prewrite`）——正是 attempt1 翻车的那一环；也包含 `b-profile-moniker`、`c-temp-paths`（在 v2 stdout、attempt1 stdout、H1 中均无任何原始对应物）。H1 第 83 行 AC3 明确要求"只读 final pre-run 的每一项均有原始证据"，因此在这些指针可解析化之前，`PRE_RUN_PASS` 只能算"值已记录、来源不可追溯"。
- **减轻情节（故不升为 P1）**：check 的 `observed` 字段确实记录了数值，v2 `.stdout.log` 第 4 行是机器生成的 key-values 汇总（含 git 版本、四仓 refs、index、protected hash、check-ignore、WER、`.tmp.driveupload` 声明）；且 H1 Task 第 166–172 行对 index/refs/pins/protected/git 版本做了独立现场复测，与 v2 记录一致，executor 源码亦可静态复核。故这是**证据来源/标注缺陷，不是伪造或错误 PASS 的证据**。

### P3-1｜写入原子性描述在两份 pinned 文件里互相冲突

- `...-v2-...json` `harnessNote`（第 153 行）与 `checks[h-targets-final-prewrite].observed`（第 346 行）称 "writes form one atomic try block" / "writes executed as one atomic try block"；同批 pinned 的 `...-v2-....stderr.log` 第 3 行称 "flat-statement scripts with final guards; **no multi-line try blocks**"。write script 本身未 pin，两种描述无法调和；这正是 attempt1 失效的机制所在。结果层面无矛盾（四产物完整），但机制陈述不可核。

### P3-2｜v2 对 "+4 records vs attempt1" 的归因与 porcelain 记录算术不符

- `v2 JSON` 第 96 行（`statusSnapshots[0].note`）与第 266 行（`e-root-status.observed`）把 1133→1137 的 +4 归因于"coordinator takeover section written into H1 Task doc between attempts"。但 H1 Task doc 在 v2 快照中已是 `?? doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md`（v2 `.stdout.log` 第 40 行），对**已 untracked** 文件的修改不产生任何 porcelain 记录（最多在该 doc 本身新建时 +1）；而 v2 自己的 verbatim 第 302–305 行恰好列出 4 个 attempt1 证据文件为 `??`。缺少逐路径基线（pin 边界内不可得），归因应记为"未确定"而非"consistent with"。checks 的 PASS 判据（exit 0 / stderr 0 / 末尾 pathspec）不受影响。

### P3-3｜`.exit` 记录对 PASS/BLOCKED 无区分力

- 题面 pin 表与 `H1` 第 126、171 行：attempt1（`PRE_RUN_BLOCKED`）与 v2（`PRE_RUN_PASS`）的 `.exit` 均为 2 字节、内容 `0`、SHA-256 同为 `9A271F2A…`（本次静态阅读确认两文件正文均为 `0`）。protocol §3 的 disposition/process-exit 区分被正确遵守，但"PASS 由 exit record 支持"这一表述不能依赖 `.exit`——区分力全部来自 `.json`/`.stderr`/`.stdout`。

### P3-4｜H1 Task 当前态文本未随 attempt1/v2 完成而更新

- `doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md` 第 110 行测试表仍写 `实际结果 NOT_RUN`、"四个 final-pre-run 输出目标待创建"，第 120 行写"H1 final pre-run 尚未运行"，与第 25、145、147、171 行（v2 已完成、`PRE_RUN_PASS`）直接矛盾；同因，第 56–61 行 author 写入 allowlist 仍只列 attempt1 四个 basename，v2 四个目标仅在后期分节（第 128–133 行）授权，读者可能误判 v2 写超 allowlist。

### P3-5｜pre-run 自身的 status argv 与 executor 冻结的 S0 argv 不可比，不能作 X6 基线

- v2 `.stdout.log` 第 22/30/33 行为 `--porcelain=v1 -z -- :(exclude).tmp.driveupload`（无 `--untracked-files=all`、`--no-renames`、`--ignore-submodules=none`，无前导 `.`），而 executor 第 390 行冻结为 `--porcelain=v2 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload`。因此 v2 的 1137 条记录把未跟踪目录折叠为单条（如 verbatim 第 1139 行 `?? verification/P22/`），与 executor S0 的多重集**不同口径**，只能作为"当时点快照"，不可当作 X6 的 delta 基线。

### P3-6｜"执行器 639 行"与实际行数不符（未解）

- `...-attempt6-exec-handoff-20261012.md` 第 47 行称"执行器总行数仍为 639 行"，`doc/tasks/P02PRE-R1H-R6-EXEC-A6.md` 第 140 行记 `639 - 10 = 629`；本次对 pinned executor（43527B / `1C8D6220…`）逐段读取时，行号终点为 **638**。可能是行尾/末空行计数约定差异，不涉及任何 pin，但作为事实陈述未闭合。

---

## 三、已独立确认的项（Review 问题 2、3、4、6）

- **证据链（Q2）**：`v2 JSON` 第 6–32 行 `previous_attempt.evidence_files` 恰为 attempt1 四文件，size/SHA 与题面 pin 表逐字节一致（12984/`D698E5FB…`、3704/`61A3DD58…`、1237/`990FAAF1…`、2/`9A271F2A…`）；`verdict=PRE_RUN_BLOCKED` + `blockedReasons[0]`（`OUTPUT_TARGET_ALREADY_EXISTS_DEFECTIVE`）保留。attempt1 `.stdout.log` 内容确为部分落盘（无结束标记、多处空值），`.stderr` 第 3 行完整记录 INCIDENT（`return[pscustomobject]`×14、`Get-History` 别名冲突）。v2 使用独立 `-v2-` basename，未覆盖/改名/重标 attempt1；attempt1 四文件本次仍可正常读取，内容与 `PRE_RUN_BLOCKED` 一致。
- **受保护文件与 Git 版本（Q3）**：v2 `protected_files_pre_post_hash` 两次读取均 57648 / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`，`unchanged=true`（10:51:07Z → 11:04:51.4885731Z）；与 executor 第 22 行 `$OldHash`、第 436 行 `AssertPin … 57648 $OldHash`（`attributes -ceq 'Archive'`、`aclSddl -ceq $ExpectedSddl`）静态一致，H1 第 147/171 行独立记录同值。`git_version_note`（第 152 行）准确：实测 `2.52.0.windows.1`、Handoff 第 67 行确称 `2.48.1`、protocol 全文未冻结 Git 版本一致性（仅冻结 pwsh 7.6.6）——未声称 protocol equality。
- **范围一致性（Q4）**：H1 第 25/54/63/172 行明确不调用 executor（executor/Replace/ProcessObserver/capture/Build/Cargo/AC1–AC7 = 未运行）；protocol §2 的 7 个输出名与 executor 第 13–19 行逐个一致、全部含唯一 `attempt6`，`CreateNew` 保留（executor 第 463/493 行 `[IO.FileMode]::CreateNew` + `FileShare::None`，第 490–491 行首次 CreateNew 前重检 absent；Handoff 第 39 行声明保留）。v2 `childContract` 声明的静态抽取经独立静态核对成立：executor 第 8–9 行固定 exe、第 277–297 行 `UseShellExecute=false`/`ArgumentList`/GIT context fail-stop/`GIT_OPTIONAL_LOCKS=0`+`GIT_TERMINAL_PROMPT=0`、第 346 行 git argv 前缀、第 390 行 status argv（末尾独立 pathspec）、第 487 行 `check-ignore --no-index --quiet --`（允许 exit 1）、第 574/584 行 `-NoLogo -NoProfile -NonInteractive -File/-Command`。`dynamic_process_closure=REQUIRES_ACTIVE_TEST / NOT_RUN` 在 v2 JSON 第 133 行、v2 stderr 第 4 行与 H1 第 83、171、176 行一致，并显式延后到独立 X6 one-shot Task。
- **Root status 差异（Q5）**：H1 第 167–168 行 live `1218 NUL / 83897 bytes / 1A2B7975…`（11:20:37.951Z）对 v2 `1137 / 79291 / 0DB72CDA…` 差 `+81 / +4606`，对 1133/78983 差 `+85 / +4914`，算术全部核对无误；H1 将其记为 `UNKNOWN / NOT_VERIFIED`、不推断原因、不归咎 Agent，这是在没有逐路径基线时唯一诚实的处理。该差异**不削弱 pre-run checks**（每项 check 只断言其自身时刻的判据，无任何 pinned 文本声称工作区在 pre-run 后被冻结），但结论是：v2 快照仅为时点记录，且如 P3-5 所述口径与 executor S0 不同，必须显式保留为限制，不得转成 X6 的期望基线。
- **Gate（Q6）**：六个 Gate 值在 H1 第 91–102 行、protocol §6 第 97–105 行、A6 Task 第 88 行、Handoff 第 141–151 行、executor 第 41–46 行均为原值（仅 protocol/Handoff 用 `X = Y` 空格写法，取值完全一致）：`private_registry_absence=UNPROVABLE`；`Technical Gate=NOT_SATISFIED`；`Owner Risk Acceptance=APPROVED`；`Gate Disposition=WAIVED_BY_OWNER`；`Build Authorization=AUTHORIZED_WITH_EXCEPTION`；residual=`technical condition unmet; user explicitly accepted residual risk`；`Build Gate=BLOCKED`；`Hard Build Barrier=EFFECTIVE`；`Build/Cargo=NOT_RUN`；`AC1–AC7=BLOCKED / NOT_RUN`。无任何 pinned 文件把 waiver 或 Parser 结果写成技术 PASS。

---

## 四、Review limitations

1. **13 项 pin 全部可读**，无"无法读取"项；但读取深度不同：v2 `.stdout.log`（1150 行）读取了第 1–120、1136–1150 行并对全文做内容检索（第 7–1143 行为 1137 条 status verbatim）；executor（638 行）读取了第 1–60、265–309、335–400、425–454、478–507、565–604 行并对全文做内容检索，其余为同源机械重复代码，未逐行通读。
2. **未做任何 hash/字节长度独立验证**（按边界要求，pre/post input-pin verification 由 Codex 负责）；本报告所有 hash/字节数均为**引用题面 pin 表与 pinned 文件自身文本**，不构成独立复算。
3. **未运行任何命令/脚本**：未执行 executor、未 dot-source、未运行 ProcessObserver/ProcessSnapshot/Toolhelp/File.Replace/Build/Cargo/capture/AC1–AC7/profile·registry·ACL 写入/Windows Sandbox；动态进程闭包仍为 `REQUIRES_ACTIVE_TEST / NOT_RUN`，本报告不是其通过条件，也未得出任何动态结论。尝试使用 shell 做只读辅助核对时被环境拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite`），此后仅使用只读文件读取，未以其他方式重试。
4. **未读取 13 项 pin 之外的产物**：`.json` `harnessNote` 披露的 `%TEMP%` 暂存模板（6914B / `0D225C27…`）与 v2 write script 均未读取，故 P2-1 中这些指针"在 pin 内不可解析"的判断是**在冻结审查范围内**成立，而非断言其内容不存在。
5. **未访问被排除路径** `.tmp.driveupload`（其 scope 保持 `NOT_VERIFIED`），未据此推断工作区内容；`g-acl-p02-dir` 的"equals A5 record"因 A5 记录不在 13 项 pin 内而未独立比对。
6. 未验证 attempt1 的 1133/78983 逐路径清单（该 baseline 仅以 hash+计数形式存在于 attempt1 JSON），故 P3-2 只判定"归因与算术不符"，不判定真实原因。

---

## 五、建议的下一步（非本 Review 判定的一部分）

在 `PRE_RUN_PASS` 的**事实层**无 P0/P1 的前提下，闭合 P2-1 的最短路径是**不重跑 pre-run、不调用 executor** 的标注性修复：由 Codex /root 将 15 项 check 的 `evidence` 指针改写为可解析引用（或把已有的原始采集产物/暂存模板 pin 进版本化证据层），并在 `codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md` 中逐项记录该映射与限制；同时修正 P3-1/P3-2/P3-4 的陈述。完成后按 H1 第 142 行 PASS 分支继续（Codex pre/post pin verification → 非作者 adjudication → 才可登记独立 X6 one-shot Task）。此前：`Build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`，dynamic process closure 维持 `REQUIRES_ACTIVE_TEST / NOT_RUN`。

**未解决 P0/P1/P2 声明**：无未解决 P0、无未解决 P1；**存在 1 项未解决 P2（P2-1）**，另有 6 项 P3。据此本 Review 判定为 `CHANGES_REQUESTED`。
