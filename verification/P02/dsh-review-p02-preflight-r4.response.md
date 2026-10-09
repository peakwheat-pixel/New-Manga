# P02 Codex-only Isolation Smoke 授权与预检候选 — 独立 exact-head Review 最终报告

- 审查方：DeepSeek Harness（非作者 Reviewer）
- 审查性质：只读、独立、固定点 exact-head Review
- 结论：**APPROVED_WITH_CONDITIONS**（阻断缺陷 P0/P1/P2 = **0 / 0 / 0**；非阻断记录项 P3 = **6**，NOTE = 1）

---

## 一、审查对象与实际核验方法

| 项目 | 值 |
|---|---|
| reviewed HEAD | `083d2b47f7051c2dedd0d9ae4346ae1affab6c1b` |
| reviewed tree | `27a8051b95df3c2cf40be90737d09b324592a78e` |
| base / parent | `ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`（`docs: close out P05 integration`） |
| commit | `docs(P02): authorize isolation smoke preflight`，`2026-10-10T02:54:53+08:00` |
| 范围 | `base..HEAD` = 1 commit、5 paths、`+514 / −0`（4 A + 1 M，全部 `verification/P02/**`） |
| checkout | `git status --porcelain=v1` 为空（审查前后一致；未写任何文件） |

候选文件与核验方式：

1. `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`（仅 r9 extension，`:125-153`）— 读取固定 blob，与 base 逐 hunk 对比。
2. `verification/P02/codex-scratch-build-preflight-r2.md`（20 行）— 全文读取。
3. `verification/P02/codex-scratch-build-preflight-observations-r2.json`（439 行）— 全文读取；worktree 与 committed blob 一致（`git hash-object` = `git rev-parse HEAD:…` = `02dc6178…`）。
4. `verification/P02/codex-checkpoint-p02-preflight-r4-start.md`（12 行）— 全文读取。
5. `verification/P02/codex-preflight-r4-validation.md`（13 行）— 全文读取。

交叉上下文：`doc/tasks/P02.md:58-62,69,75-89`、`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:5`、`doc/00_INDEX.md:3`、`codex-scratch-build-process-isolation-proposal-r1.md:30-69`、`codex-scratch-build-preflight-hostfolders-r1.tsv`、`codex-scratch-build-preflight-observations-r1.json`、`dsh-review-p02-preflight-r3.response.md`、`dsh-review-process-isolation-r6.followup.response.md`。

实际执行的核验（全部只读，无文件写入、无 clone、无 Sandbox 启动、无构建）：

- `git rev-parse / cat-file -p / show --format=%T,%P,%cI / status / diff --check / --numstat / rev-list / merge-base --is-ancestor`：HEAD/tree/base 与声明一致；`diff --check` **EXIT=0**；range 内仅 1 commit；`7ce3c40c…`（clone 来源）是 HEAD 祖先 **EXIT=0**；被引用的 `c36435ae`、`7d8951c2`、`2be02783`、`2394dc98`、`561f4105` 均为 reviewed HEAD 祖先（各 EXIT=0），`2be02783` 的 parent = `c36435ae`。
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`：**EXIT=0**，7 项 PASS（196 unique nodes / 105 集成祖先 / Task-Plan 状态一致 / 21 planned nodes 无环 / 导航链接 / governance whitespace），打印 `live HEAD=083d2b47…`、`Product tests/build/GUI: NOT_RUN (planning-only)`。
- r3 Smoke config 复算：CRLF→LF 归一后 **2609 字符、CR=0、LF=22**；工作区 raw = 2631 bytes（22 CR）；结构 = **11 mappings（1 RW / 10 RO）、无 `LogonCommand`**。SHA-256 未在本受限 shell 重算，但值与前序多轮独立复算一致。
- 固定输入抽样实算 6 项：`Python312\python.exe` `15b41a48…`、`node.exe` `3331e1ff…`、`Git\cmd\git.exe` `3cbd024d…`、`m2ac5-build\Scripts\python.exe` `864530d7…`、`rc.exe` `65db0d7b…`、`wsb.exe` `247e092b…`(156160 B) — 与 observations 记录逐项一致。
- 链接解析：r9 相关 3 个 Markdown 共 **5 条**相对链接全部解析成功，0 missing。
- `G:\CODEX\P02-scratch-build-source` 实测不存在（与记录 `ABSENT` 一致）。
- 复现 `Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM`：**EXIT=1，"请求的操作需要提升"**，与候选记录一致。
- Microsoft Learn `Win32_OptionalFeature`：`InstallState` = Enabled(1)/Disabled(2)/Absent(3)/Unknown(4)，与候选引用**逐字一致**。

**未运行 / 无法独立复现（如实标注，不作为缺陷）**：`Get-CimInstance Win32_OptionalFeature` 与 `Get-AppxPackage` 在本 DSH 受限 shell 返回"拒绝访问"（环境 ACL，非命令失败）→ InstallState=1 与 WSB 包身份标记 **NOT_RUN**；`wsb --version`、`wsb list --raw` 未运行（触碰 WSB 服务）；live root `G:/CODEX/New Manga` 现场清单 203/203 与 digest `3a54fa97…` 未独立复算（本 worktree 无该 repo 读权限），采信记录；Sandbox 启动、clone 创建、递归 HostFolder manifest、guest 探针、网络判别、截图绑定、Build/产品测试全部未运行。

---

## 二、最终判定

**APPROVED_WITH_CONDITIONS。**

- 阻断缺陷（P0/P1/P2）：**0**。
- 非阻断记录项（P3）：**6**；NOTE：1。
- 判定理由：r9 授权边界、Gate 分离（Review → Smoke admission → Build Gate）、预检证据的"未实测即 NOT_RUN"记账方式全部成立；无任何"未实测却宣称隔离或 clone 检出成功"的表述；无数据安全、用户数据、产品代码/契约/依赖路径改动。6 项 P3 均为**记录精度/可核验性**问题，按项目口径不阻断 Smoke 准入，但须在 Codex 记录 `Smoke admission=ADMITTED` 前逐条 disposition。

---

## 三、Findings（按对下一步风险排序）

### C-01（P3，非阻断）— `expected_size_bytes` 为空却 `size_match=true`
- 文件:行：`verification/P02/codex-scratch-build-preflight-observations-r2.json:205,216,359,370,381,392`（`size_match` 分别在 `:209,220,363,374,385,396`）；相关措辞 `verification/P02/codex-scratch-build-preflight-r2.md:13`
- 触发：6 条 pin 的 `expected_size_bytes=""`（空字符串）时仍置 `size_match=true`；其中 `pyvenv.cfg`、`distutils-precedence.pth`、`config.json`、`preprocessor_config.json` 可直接看出未做数值比较（`actual_size_bytes` 为 325/151/2320/470）。
- 独立裁定：**真实存在，但仅为记录项（P3），不是阻断缺陷。** 内容完整性由 `expected_sha256 == actual_sha256` 独立覆盖（我抽样 6/20 实算哈希全部匹配），因此**不构成隔离或 pin 完备性风险**；问题在于 `preflight-r2.md:13` "20/20 尺寸/哈希匹配"对其中 6 条尺寸口径略强于实测。
- 最小修复：将该 6 条 `size_match` 改为 `null` 并新增说明（如 `size_check: "not_registered"`），或在 `preflight-r2.md:13` 注明"20/20 哈希匹配；其中 6 条未登记期望尺寸，仅按哈希核验"。

### C-02（P3，非阻断）— checkpoint 写入范围未点名精确路径
- 文件:行：`verification/P02/codex-checkpoint-p02-preflight-r4-start.md:5`；`verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:142-144`
- 触发：start checkpoint 写"only the fixed r9 P02 evidence paths are being written"却只点名 observations R2 与 report R2（`:7-8`）；r9"Exact r9 write scope"只以类名描述"a Task-local checkpoint, validation, dispatch, and independent Review packet"。5 个精确路径仅出现在 `codex-preflight-r4-validation.md:5`。
- 独立裁定：**真实存在，但仅为可核验性记录项（P3），不是阻断缺陷。** 实测候选仅 5 路径且全部在授权范围内（`git diff --name-status` = 4 A + 1 M），无越界。
- 最小修复：在 start checkpoint 或 scope delta 的 r9 写入范围段显式列出 5 个候选路径名（`codex-scratch-build-preflight-r2.md`、`codex-scratch-build-preflight-observations-r2.json`、`codex-checkpoint-p02-preflight-r4-start.md`、`codex-preflight-r4-validation.md`、`codex-scratch-build-process-isolation-scope-delta-r1.md`）。

### C-03（P3，非阻断）— r2 observations 的 `mapping_domain=null`
- 文件:行：`verification/P02/codex-scratch-build-preflight-observations-r2.json` 的 12 条 `hostfolder_roots` 记录（每条 `"mapping_domain": null`）
- 触发：同一交付的 `codex-scratch-build-preflight-hostfolders-r1.tsv:1-13` 已具权威分类列 `mapping_domain`（1 Scratch RW + 9 Smoke RO + 2 Build-only RO，共 12 行），JSON 未承接。
- 独立裁定：**真实存在，但仅为一处一致性问题（P3），不是阻断缺陷；也不影响 12 根 vs 11 mappings 的口径。** 我解析 r3 config 得 11 条 `<MappedFolder>`（1 RW + 1 clone 内 canary RO + 9 输入 RO，不含 2 个 Git root），与 TSV 的 12 行换算自洽。
- 最小修复：二选一即可——(a) 填充该字段与 TSV 一致；或 (b) 在 `preflight-r2.md` 注明"`mapping_domain` 以 `hostfolders-r1.tsv` 为权威，JSON 该字段未承接"。

### C-04（P3，非阻断）— 用户授权缺少 commit 内锚点
- 文件:行：`verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:127`
- 触发：仅散文式"the user renewed the persistent PROJECT_ORCHESTRATION_AUTHORIZATION and explicitly directed…"，未指向同一授权在仓库内的既有登记。
- 独立裁定：**真实存在，但仅为审计可追溯性记录项（P3），不是阻断缺陷，也不是"越权授权"。** 同源授权已在 `:85`（r7 extension）与 `doc/tasks/P02.md:87-88` 登记，链条可闭合。
- 最小修复：在 `:127` 增补一句锚点引用（"授权依据见本文 r7 extension 的 authorization basis 条目 / `doc/tasks/P02.md` 对应 checkpoint"）。

### C-05（P3，非阻断）— Smoke admission checklist 两项前置未在同一清单显式化
- 文件:行：`verification/P02/codex-scratch-build-preflight-r2.md:14`；`verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:134,136`
- 触发：(a) `wsb list`/Sandbox UI 窗口身份与本次 session 的绑定要求只在 `proposal:62,68`，r9 未重述；(b) "Smoke 须由本机非提权交互式 host shell 启动"（`proposal:68`）在 r9 只体现为非提权 CIM 查询；observations 记录的 shell 为 pwsh 7.6.6。
- 独立裁定：**实施细则已存在，缺的是准入清单里的显式项（P3，非阻断）。**
- 最小修复：在 Smoke admission checkpoint 的 checklist 中逐条列出"绑定 `wsb list` 输出/UI 窗口身份到本次 session"与"从非提权交互式 host shell 启动"。

### C-06（P3，非阻断）— SHARED 文档与本轮实测的已知差异未登记
- 文件:行：`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:5`、`doc/00_INDEX.md:3`、`doc/tasks/P02.md:88`
- 触发：上述文档在本 HEAD 仍写 `Windows Sandbox Feature 未查询且=UNKNOWN` / `完整 preflight=BLOCKED / INCOMPLETE`，而 r9 已实测 `InstallState=1 (Enabled)` / `PRESTART_STAGE_1_PASS`。
- 独立裁定：**候选刻意未改 SHARED 文档**（r9 写入范围把 `STATUS/Plan/Index/Task` 推迟到 Review 之后，`:145`），因此**不是越界改动、不是阻断缺陷**；但候选自身未登记这条"已知差异"，恢复/审计时可能被误读为矛盾。
- 最小修复：在 r9 scope delta 或 start checkpoint 增加一句"SHARED 文档仍记 UNKNOWN/BLOCKED，系刻意未改，待 exact-head Review 通过后按授权更新"。

### NOTE-01（非严重，仅供参考）
source commit pins 的期望尺寸/哈希取自既有登记（r9 `acceptance` 第 2 条已如实声明 `source checkout pins and recursive manifests remain pending until the clone is created`），我无法独立核对 pin 源表。若后续需要端到端可复算，建议在 Smoke admission 时把 pin 源表引用写进 observations。

---

## 四、此前过程讨论四项的独立裁定汇总

| 过程草案标签 | 独立裁定 | 真实严重性 | 阻断下一步 Sandbox Smoke？ |
|---|---|---|---|
| P0-01 授权溯源 | 部分成立：授权确已在 `:85` 与 `doc/tasks/P02.md:87-88` 登记，缺的只是 `:127` 的自引用锚点 | P3 记录项 | 否 |
| P0-02 `expected_size_bytes=""` 却 `size_match=true` | 成立（6 条）；哈希匹配独立成立，尺寸口径略强 | P3 记录项 | 否 |
| P0-03 checkpoint 写入路径范围不精确 | 成立（未点名 5 路径）；实测无越界 | P3 记录项 | 否 |
| P0-04 `mapping_domain=null` | 成立（12 条）；TSV 已具权威分类，口径自洽 | P3 记录项 | 否 |

结论：四项**均不应标为 P0**，全部属于非阻断的记录/可核验性问题；不存在需要打回重做的授权越权或技术 Gate 失效。

---

## 五、是否存在其他会阻止下一步 Sandbox Smoke 的缺陷

**未发现阻断缺陷。** 逐项核查如下：

- 授权边界：r9 仅授权非提权只读 CIM 查询、一次固定路径 clone、一次 r3 config Smoke；elevation、feature mutation、产品 build、产品验收、AC 完成、barrier release 均保持独立（`:133,:137,:138`）——**成立**。
- r3 Smoke config 身份：`2609 bytes / 9af44513…` 与已审查值一致，我复核 canonical 长度与 CR 数吻合，无未审查的配置漂移——**成立**。
- 前置阈值：available RAM 16,854 MiB ≥ 4096 MiB、total 31.647 GiB、C:/G: 330.108/1,299.434 GiB、16 物理核、固件虚拟化 True——**达标**。
- 路径与 pin：固定 clone 路径实测不存在（`ABSENT` 匹配）、12 roots、20 pins（我抽样 6/20 尺寸+哈希全匹配）——**成立**。
- 失败即停语义：`:133`"A query that cannot return a known state blocks execution"、`:153`"If any pre-start check fails or is unknown, do not run wsb start"、`preflight-r2.md:18`"If any check is unknown or fails, stop and preserve the state"——**fail-closed 语义完整**。
- 未实测项记录：checkout、递归 manifest、reparse 遍历、no-link、guest 探针、网络 fail-closed、截图绑定、post-run 比对全部 `NOT_RUN`，未转写为 PASS——**成立**。

因此，6 项 P3 属"记录精度条件"，不构成技术阻断。

---

## 六、各阶段状态（分别陈述）

1. **方案审查（process-isolation design）**：已完成并通过。R4 exact-head = `APPROVED`(0/0/0/3)；R5 = `APPROVED_WITH_CONDITIONS`(0/0/0/2) 的 N-04/N-05 已闭合；R6 follow-up（`2394dc98`）确认 **N-06 CLOSED**、新 findings `0/0/0/0`。设计线无未闭合阻断项。
2. **Smoke 准入（admission）**：**当前 = NOT_ADMITTED（条件性可准入）**。前置预检 = `PRESTART_STAGE_1_PASS`；本 Review 判定 APPROVED_WITH_CONDITIONS 且无 P0/P1/P2；待 6 项 P3 disposition 后，Codex 方可另立 checkpoint 记录 `Smoke admission=ADMITTED`。Smoke 运行状态 = `NOT_AUTHORIZED / NOT_RUN`。
3. **Build Gate**：**BLOCKED**（独立于 Smoke，需自身 exact-head Review 与 Codex Gate）。build = `NOT_AUTHORIZED / NOT_RUN`。
4. **产品验收**：**未开始**。AC1–AC7 = `BLOCKED / NOT_RUN`；产品 build/runner/Vitest/GUI/WebView 全部 NOT_RUN；Hard Build Barrier 继续有效。

---

## 七、精确可执行的条件清单（Smoke admission 前置）

按顺序执行，全部为**纯文档/证据修订**，不得改 r3 WSB XML 或 canonical hash（`2609 / 9af44513…`）、产品代码/测试、Schema/IPC/依赖、Owner allowlist、用户数据：

1. **C-01**：修改 `verification/P02/codex-scratch-build-preflight-observations-r2.json` 第 205/216/359/370/381/392 行的 `expected_size_bytes` 处理口径（对应 `size_match` 行 209/220/363/374/385/396 改 `null` 或加 `size_check` 字段）；同步修正 `codex-scratch-build-preflight-r2.md:13` 的"20/20 尺寸/哈希匹配"措辞或在报告中披露 6 条未登记尺寸。
2. **C-02**：在 `codex-checkpoint-p02-preflight-r4-start.md:5` 或 scope delta `:142-144` 显式列出 5 个 r9 候选路径名。
3. **C-03**：填充 observations JSON 12 条 `hostfolder_roots` 的 `mapping_domain`，或在报告中注明以 `codex-scratch-build-preflight-hostfolders-r1.tsv` 为权威。
4. **C-04**：在 scope delta `:127` 增补授权锚点引用（指向 `:85` 的 authorization basis 与 `doc/tasks/P02.md` 对应 checkpoint）。
5. **C-05**：在 Smoke admission checkpoint 的 checklist 增加两条：`wsb list`/UI 窗口身份与本次 session 绑定；从非提权交互式 host shell 启动。
6. **C-06**：登记 SHARED 文档（`STATUS:3`/`REBASELINE_PLAN:5`/`00_INDEX:3`/`P02.md:88`）"Feature 未查询=UNKNOWN"与本轮实测 Enabled 的已知差异，并声明将在 Review 通过后按 r9 `:145` 更新为实测状态。
7. 条件闭合后：重跑 `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`（期望 EXIT=0）、Markdown 链接检查、`git diff --check`（期望 EXIT=0），固定新 commit 并递送 DeepSeek Harness 做**条件闭合 exact-head 复核**（只读、固定 HEAD/Tree）。
8. 复核通过后，Codex 方可另立 `Smoke admission=ADMITTED` checkpoint 并创建固定 clone；任何前置检查缺失/未知即停止，保持 `Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。

---

## 八、推荐下一步

由 Codex 按第七节 1–6 项完成纯文档 disposition 并固定新 commit，随后在本会话续派 DeepSeek Harness 做条件闭合 exact-head 复核；复核通过后 Codex 才可记录 `Smoke admission=ADMITTED` 并创建 `G:\CODEX\P02-scratch-build-source` clone。Build Gate 与产品验收保持独立阻断，无需其他 Agent 介入。
