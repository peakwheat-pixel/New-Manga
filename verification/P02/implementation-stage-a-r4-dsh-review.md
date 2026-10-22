# P02 Stage A r4 正式 Review（DSH，非作者）

**对象**：base `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`；reviewed_head `cc1bd7505f3fc48079db7ea2719040e77a8c58dd`；expected tree `d2569f6c4854c05e18cf22fa363397525962eec8`；parent r3 `5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`；branch `agent/antigravity/P02-real-webview-harness`。**Stage A only；P02 仍 `in_progress`；`integration_commit: null`。**

**decision: `changes_requested` ｜ P0/P1/P2/P3 = 0/0/3/8（open 11）**

**我能核验**：`refs/heads/agent/antigravity/P02-real-webview-harness`=`cc1bd750`✔；worktree reflog `5fa8a41f→cc1bd750`（parent= r3、单提交）✔；`refs/heads/main`=`5de8d44c`=base✔；运行期 porcelain 14×`M`+2×`??` 全在 allowlist✔；11 项 WCAG 数值逐项复算✔；源码枚举/overlay/relabel/wire 契约对照✔；TS 类型推断（TS2556 报错列 41 与 `...effectiveFg` 位置逐字吻合）。
**我不能核验**：`pwsh` 不可用（`SetNamedSecurityInfoW Win32 5 grantWrite …`）⇒ tree `d2569f6c`/`f27d12a7`、scope SHA-256、报告内全部 SHA-256、`git status/diff` 均未复核；**未执行** tsc、PowerShell、Python、探针/harness/runner、Vitest、任何 build/GUI/真实 WebView。Codex 已独立确认 Owner worktree clean 与 HEAD/tree/branch/common-dir，并有 exact replay 日志（`verification/P02/r4-clean-commit-validation.md`，仅存根工作区、不在被审 HEAD 内）——**那是 Codex 的执行，非 DSH 运行结果**。

| ID | 级 | 路径/行 | 触发·影响 | 最小修复 |
|---|---|---|---|---|
| R4-01 | P2 | `apps/desktop/frontend/e2e/workbench_driver_protocol.ts:162,164` | `effectiveFg` 被推断为 `[n,n,n]｜number[]`（else 分支字面量无元组标注），`:164` 展开到三参函数 ⇒ TS2556；`tsconfig:19` 只 `include ["src"]`，常规构建不查 | 显式元组标注；为 `e2e/**` 建可执行类型检查 |
| R4-02 | P2 | `harness/workbench_cdp_harness.py:259,260,275,281` | 白名单 `skip｜translate｜ignore`、`user｜machine｜legacy` 与 `src/region/types.ts:33,37`（`…｜manual`、`…｜imported｜restored`）不符：**接受非法** ignore/legacy，**拒绝合法** manual/imported/restored（restore 场景涉 restored） | 按源码闭集白名单，或同时派生 SfxPolicy/RegionOrigin |
| R4-03 | P2 | `harness:695-706` vs `:752-780`；`run-webview.ps1:126-128` | Full 日志在 harness（Step3）**运行中**被哈希，而本轮内容由 runner `finally` 在 harness 退出后才落盘 ⇒ 记录值只能是上一轮遗留文件；TXT 亦在写入前被哈希（仅因内容运行内不变而可能巧合相符）。反证：probeonly 日志定稿后再哈希，其值与 Codex 复跑逐字相同 | 两阶段：先定稿日志/TXT，再由独立收尾步骤计算并落盘哈希 |
| R4-04 | P3 | `harness:477-481` | 新鲜度只比 head/tree：**同一 HEAD 但输入 dirty**（正是本片 pre-commit 作业方式）时旧报告被判「新鲜」；`exit_code` 缺失时以 `0 if PASS else 1` 合成，非观察值 | 绑定输入哈希/run id；缺 exit_code 记 NOT_VERIFIABLE |
| R4-05 | P3 | `harness:368-380,512` | PRE-02 自检在函数内重写比较逻辑，未走真实读取/失败路径；`report_freshness_verified` 恒为字面 `True`（本次碰巧为真） | 注入真实消费函数的自检；字段改实算值+分支标记 |
| R4-06 | P3 | `run-webview.ps1:121-128`（对照 `:81-86`） | 异常路径只 append `[UNHANDLED_EXCEPTION]`，**不记录**失败 command/output/子 EXIT；「异常也落盘 exact command/EXIT」仅对非零退出成立。另 catch 内 `exit` 是否触发外层 `finally`（PS 5.1）我无法执行验证 | catch 内补 Command/EXIT，或先 Flush 再 exit |
| R4-07 | P3 | `harness:101-110` | 源缺失/正则不匹配即静默回退硬编码六值，details 仍宣称「权威枚举」 | 解析失败即 raise，或标注 fallback |
| R4-08 | P3 | `harness:328,339,450`；`json:83` | mutation 1/2 受守卫可静默跳过，报告仍无条件称「4 组均被拒绝」 | 计数实际执行组数并记 skipped |
| R4-09 | P3 | `ts:214`；`fixture:233` | `large_text` 与 `ui_component` 同得 3.0 ⇒ 协议层给「文本」开了 Task 未授权的 3.0 档（AC6：文本≥4.5、仅禁用文字/非文本 3.0）；fixture `large_text_min_ratio` 从未被消费。**当前无产出使用该 role**，故为潜在违规 | `large_text` 归 4.5，或删除该 role |
| R4-10 | P3 | `run-webview.ps1:26,31-45,95-128` | `try` 之前失败（`Get-Command python`，EAP=Stop 终止）或强杀时不写盘，旧「EXIT=0」日志留存；「杜绝残留旧 PASS 日志」过强；所述本地微探针无归档 | 开头写入并截断/标记 RUN_STARTED；归档微探针证据 |
| R4-11 | P3 | `harness:213,263-266` | `page_count` 强制 int，而 `library/types.ts:23` 允许 `null`；`bbox` 元素类型与 `polygon` 从不校验（夹具 3 处 polygon 存在） | 放宽为 int\|None；补 polygon/元素类型断言 |

上述 6 项专项已独立裁决为：TS2556→R4-01；枚举白名单→R4-02；artifact_hashes→R4-03；PRE-02 消费路径（同 HEAD dirty／缺 EXIT 回退／stale/malformed）→R4-04+R4-05；`large_text`→R4-09；异常路径→R4-06。均无需降级，也未见 evidence 支持排除。

**r3/Codex-r3 处置**：C1 closed（`harness:539-548,576,612`；`json` 的 `min_required` 4.5/3.0 与判定一致）；C2 closed（全量遍历+FK+4 mutation）但暴露 R4-02/07/08/11；C3 closed（探针写 head/tree/exit，不新鲜重跑取真实 `returncode`，非零或非 PASS 即 FAIL 并 `exit 1`），残余 R4-04/05；C4 closed（`:81-86` 先 Flush 再 exit、改用 `Write-Host`、`:30` 无 BOM UTF8），残余 R4-06/10；**C5 open**（=R4-01）。H-01 closed（编号回归 r2 口径、全文无 `#30363d`、改为 `#2a3038`、「彻底闭合」改为逐项状态+残余）；H-02 closed（=C3）；**H-03 partial**（region_type 已派生，sfx_policy/origin 仍错+静默回退）；H-04 closed（pill 自身文字令牌 `#7eb287`/`#fbbf24`，来源 `RegionOverlay.tsx:48/46`，5.83/7.97）；H-05 closed（`assumed_global_config`+`sfx_policy_is_config_dependent`）；H-06 closed（`P02.md:102-103` 标 `[历史快照]`）；H-07 closed（snake_case、移除惰性字段）。r2 G-03 closed（Codex r4 replay 归档 `git diff --check 5de8d44c cc1bd750` EXIT=0；交付内仍无该 artifact，属补充证据）；G-04 closed（两模式独立日志并分别链接 `P02.md:78/79`、`RESUME:19/20`）；G-05 closed（容器/边框 `NOT_VERIFIABLE`+原因；含 `ink_2/ink_3/#8a94a2` 的普通文本升 4.5）；**F-05 closed（输入侧）**——运行期 head/tree、`is_clean_worktree`、7 源哈希、6 执行输入哈希、`PRE_COMMIT_LOCAL_EVIDENCE`、`replay PENDING`、无自引用，且 6 项输入哈希与 Codex replay 逐字一致，唯 artifact_hashes 见 R4-03；F-01..04、F-06..12、G-01/02/06/07 抽查无回退，closed。

**Architecture**：通过。变更 ⊆ allowlist（14M+2??，无删除）；零产品源码/依赖/共享契约/P03 runner/设计 token 改动；`frontend/dist`、`cargo-target` 不存在；仅标准库；夹具全 synthetic；无 `shell=True`/网络/删除；写限于 `verification/P02/`。frontmatter、AC1–AC7、允许/禁止范围与 r1–r3 逐字相同。

**Verification**：PRE-01/02/03 为**静态前置**（3 PASS），机制与数值已复核；**AC1–AC6 未执行**，全部 `BLOCKED`、`exit_code: null`；未运行真实 WebView2/GUI/Vitest/build。R4-03/R4-06 结论基于代码顺序与 PS 5.1 语义推断，非执行结果（见上「不能核验」）。

**Final verdict**：`changes_requested`（Stage A only）。r4 真实闭合了 C1–C4、H-01/02/04/05/06/07、G-03/04/05 与 F-05 输入侧，但仍有 3 项 P2（TS2556 未修、枚举白名单违背冻结 wire 契约、`artifact_hashes` 不绑定交付字节）⇒ **不可交 Codex 集成**。建议 Owner 在现有 allowlist 内提交 r5 修正 R4-01/02/03 及 8 项 P3，再由 DSH 复审；Codex 对新 head 做 clean detached exact replay 并归档逐 artifact 实测哈希。**P02 保持 `in_progress`、`integration_commit: null`；AC1–AC6 维持 `BLOCKED`；本 Review 不代表 P02 完成。**
