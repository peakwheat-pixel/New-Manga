<!-- Reviewer session: sess_88acf941-2220-4c42-a4bf-ca95923a8cfe; turn: turn_70d174e1-beee-43d5-907b-408b29cba54a; CLI EXIT 0. Response preserved verbatim below. -->

全部核验完成。以下为正式 Review 报告。

---

# FEA-15-ACCEPT-1 独立 Review 报告

- **Reviewer**：ZCode 独立新会话（本会话未参与本 Task 的实现、返修或先前裁决；全程只读，未编辑/提交/删除/push）
- **Reviewed head**：`e55a23dc9b7c701e31360a9e41b9fc4a88d0bf30`（main，工作区 clean）
- **审查范围**：`164ebabcfa90b92fc46c07238280960fc01f7423..e55a23dc9`，共 5 个提交（d63d735a7 → 8cad6d68c → b7344445e → 6ad10aacf → e55a23dc9），全部为治理/证据提交，无生产代码、测试或契约字节改动
- **实质交付 head**：`delivery_head = 6ad10aacf886a3c2b98ff3434070edf6b31dbf36`（Task frontmatter 已固定）；`e55a23dc9` 相对它仅改 4 个治理文件（in_review 翻转 + reviewer 任命 + 24 条 SOURCE_PIN 登记），已逐 hunk 核验无夹带
- **审查方式**：直接读取全部 29 个证据文件中的 22 个 + Git 对象级核验（blob hash、diff、commit 存在性、autocrlf/.gitattributes 链）+ 源码核对；未复跑任何测试/构建/门禁（见「未验证项」）

## 结论：**approved**（附 P2×2 + P3×4 处置条件；无 P0/P1）

验收卡的核心义务——**如实披露、不伪造、失败不虚标 PASS、NOT_RUN 如实登记**——全部核验通过。所有 README/Handoff/Task 卡的数字声称与原始日志逐项一致；A5 全量基线未满足被诚实登记为 AC1 PARTIAL 而非隐藏；两个 P2 是证据表述与 pin 可复现性口径问题，不改变验收实质结论。

## Findings

### P0 / P1

无。

### P2

**P2-1 证据 pin 的 sha256 为「本机 CRLF 工作区」口径，26/29 跨环境不可复现**
- 位置：`doc/tasks/FEA-15-ACCEPT-1.md:90-119`（EV-01..05 + SRC-01..24 共 29 条 pin）
- 证据：按 `git show <commit>:<path> | sha256sum`（blob 口径）复算，29 条中 **26 条不匹配**（仅 EV-04/SRC-01/SRC-02 匹配，其 blob 本身含 CRLF）；29 条 pin 值与**当前工作区文件**全部一致。根因已定位：仓库根 `.gitattributes` 对 `verification/FEA-15-ACCEPT-1/**` **没有任何 eol 规则**，`core.autocrlf=true` 来自**系统级** Git 配置（`C:\Program Files\Git\etc\gitconfig`；仓库级与全局均未设置）；`git ls-files --eol` 显示多数日志 `i/lf w/crlf`、三个 zcode-*.log 为 `w/mixed`。即 CRLF 检出形态是本地配置偶然，不是仓库规则强制。
- 为什么是问题：仓库自己的 `.gitattributes` 已两次把同类状态定性为必须修复的陷阱——P19-UI-MANIFEST-VIEW-1 注释「Without an eol rule, core.autocrlf=true rewrites them to CRLF on checkout and **every pin fails on a fresh clone**」；FEA-08 注释明确选择「pins are SHA-256 of the Git blob (LF)」并为此加 `eol=lf` 规则。本卡 26 条 pin 在 autocrlf=false / Linux fresh clone / `git cat-file` 口径下全部无法复现。
- 减轻因素：§4.1 对仓内文件的字面义务是「路径 + 含该文件的 commit」（已满足），sha256 是额外自加的；且内容除行尾外与提交逐字一致，无真实性疑问。
- 处置建议：由裁决方授权为 `verification/FEA-15-ACCEPT-1/**` 增加 eol 规则并按选定口径（建议 FEA-08 的 blob/LF 口径）重算登记 pin。注意 `.gitattributes` 不在本卡 `allowed_paths`，需另行授权；不改证据文件本身字节。

**P2-2 README 将归因推断写成日志事实：「App 4 项失败堆栈指向 `Directory.Exists(.git)`」**
- 位置：`verification/FEA-15-ACCEPT-1/README.md:9`
- 证据：`dotnet-full.log` 中 `Directory.Exists` 与 `.git` 字样 **0 次命中**（两个独立核验均确认）；4 个 App 失败的实际错误全部是 `Assert.NotNull() Failure: Value is null`，堆栈最深帧为 `at NewManga.App.Tests.NoDbOsAccessTests.get_RepoRoot()`（dotnet-full.log 行 339-345、890-905、913-930、931-946）。「.git 为文件导致定位失败」是**源码审查 + 对照实验的推断**：`apps/desktop-avalonia/tests/NewManga.App.Tests/NoDbOsAccessTests.cs:39-52` 的 `RepoRoot` 确以 `Directory.Exists(Path.Combine(directory.FullName, ".git"))` 逐级向上找根、找不到即 `Assert.NotNull` 失败；对照实验 `dotnet-repo-root-control.log`（构造空 `.git` 目录后同样 4 项 4/4 PASS、EXIT 0）支持该归因。
- 影响：归因实质成立、A5 分类（ZCode 裁决三分类之①「环境形态」）不受影响，但「堆栈指向」是对日志证据的超范围表述，按项目先例（M2-RG1 r2 P1-1「改文字为实」）应纠正。
- 处置建议：收口时把该句改为「堆栈终止于 `get_RepoRoot()` 的 NotNull 失败；`.git` 文件形态归因由源码与对照实验支持」，或在裁决记录中明确澄清。

### P3

- **P3-1** `doc/tasks/FEA-15-ACCEPT-1.md:95-96`：SRC-01..24 表块与 EV 表之间断开且**无自己的表头行**，markdown 渲染为无头表；建议补 `| id | class | path | commit | sha256 | class |` 头。
- **P3-2** 裁决日志命名与时序相反：`zcode-evidence-decision.log`（SRC-22，observed 23:48）实为**第三份/最终**裁决，早于它的 `zcode-second-decision-raw.log`（SRC-23，observed 23:39）才是第二份。三份同属 `sess_2a802094`，演进链（中期处置 II → 串行化补充（撤回并行诊断卡、方案 A 废弃）→ 最终收口路径裁决）完整自洽，但文件名误导后来者按字面排序阅读。
- **P3-3** 证据计划（Task 卡 L64）约定 `logs/` 子目录，实际 29 个文件平铺在 evidence_dir 根（无子目录）；NOT_RUN 登记与复现命令由 README + 各日志首行 `command=` 承担。功能等价，结构偏离计划文字。
- **P3-4** Handoff 的「提交列表/变更路径」以概括句代替逐列（`doc/handoffs/FEA-15-ACCEPT-1-b7344445e.md:3`「二者相对执行基线仅包含任务文档与证据」）；本 Review 已用 `git diff --name-status` 证实该概括属实（见下），但建议未来 Handoff 直接列 diff 清单或其 pin。

## 核验明细（全部通过项）

| 核验点 | 结果 |
|---|---|
| 提交范围与夹带 | 5 commits 全为治理/证据；diff 34 文件 **全部 ⊆ allowed_paths**（8 个允许路径逐一对照，无越界；`doc/reviews/FEA-15-ACCEPT-1-*.md` 预留位未使用——本 Review 是第一份） |
| 治理登记一致 | STATUS:7 / REBASELINE_PLAN:51,56 / TASK_LEDGER:40 / Task 卡 status 四处均 `in_review`，计数表同步（in_review=3） |
| A1 构建 | `build.log`：`preexisting_bin_obj=0`、0 警告/0 错误、EXIT 0、HEAD=d63d735a7 ✓ |
| A5 pytest | `pytest-full-retry.log` 末行 `16 failed, 3515 passed, 12 skipped` + `EXIT=1` ✓；16 失败=3×p16 export hook（:762/:780）+1×fea11 v7 fixture +12×plugin sandbox；12 skip 逐条原因在案（黄金资产 2/docTR 2/transformers 1/openssl 6/registry 1）；首跑隔离失败 `No module named pytest EXIT=1` 保留 ✓ |
| A5 .NET | `dotnet-full.log` 八项目：App 884/4/11、Appearance 21、ApplicationCore 31、CoreClient 164/0/27、DesignSystem 117、Host 198/123/74、Presentation 72、ThemeEngine 253，2 项目失败 EXIT 1 ✓；Host 123 失败=96×UnauthorizedAccess（`SourceSecurity.PrivateDirectory→SetSecurityInfo`）+27×repo not found——README「不能归因于同一原因」属实 |
| 主树定向复跑 | `pytest-main-targeted.log` 4 passed/15 failed EXIT 1，失败集与隔离树同构 → worktree 形态致因被排除，如实登记 ✓ |
| 对照实验 | `dotnet-repo-root-control.log` 4/4 PASS EXIT 0（构造空 .git 目录）；`dotnet-host-control.log` 1 passed/1 failed EXIT 1（ACL 样例仍 UnauthorizedAccessException）——「支持但不充分」的边界如实写明 ✓ |
| 插件对照 | `plugin-control.log` 6 passed/10 failed EXIT 1（专用 venv+固定源码仍复现）→「不能单独判定根因」如实 ✓ |
| v7/v14 探针 | `v7-repro.log`（原始失败+事后 post-run 说明，原字节保留）/`v7-repro-2.log`（干净复现 `no such column: custom_rank` EXIT 1）/`v7-v14-probe.log`（in-memory、no user database、v14 列存在、absent→None、EXIT 0）——README:7「不证明真实用户库迁移/完整性/回退」的限定与日志 `command` 行吻合 ✓ |
| A2 安装旧包 | 旧包实存（71.9MB），本 Review 独立复算 sha256=**486a2275…d3ba10 与登记完全匹配**；登记为「历史参考，不能证明当前 HEAD 安装」+当前 HEAD 安装 NOT_RUN + FEA-15-PACKAGE-GAP-1 缺口承接——AC2 走 NOT_RUN+缺口登记路径，符合 scope 冻结第 2 条 ✓ |
| A3 隐藏 UI 层级 | `ui-process-smoke.log`：两入口 hidden 启动、2s 存活、exit_code=0、真实 data/theme 目录元数据指纹前后一致、fatal/unhandled 0 匹配，**末行自标 `scope=process_only; visible_window_and_page_interaction=NOT_RUN`**——L1/L2/L3 三级判据（ZCode 最终裁决「禁止以 L1 冒充通过」）被严格遵守 ✓ |
| A4 | v14 真实用户库升级与 pre_restore 回退 NOT_RUN 如实登记（README:23、矩阵 A4 行、Handoff:6），历史替代证据入口在矩阵 §6/§67 列明并限定「早于当前 v14，不构成当前版本 PASS」✓ |
| 门禁 | gates.log（23:23，default+task+pins+api 全 PASS，API 1/79/6=86 与 appointment.md 一致）、gates-post.log、gates-control.log 三份均 `Governance check: PASS (3 warnings)` + `PIN AUDIT: PASS (all 18)` EXIT 0 ✓；3 warnings 为治理侧（11 个非终态 Task、STATUS/PLAN 预算 80%），非本卡缺陷 |
| AC 标记（v3） | AC1 `[ ]`+PARTIAL、AC2/3/4/6 `[x]`+MET、AC5 `[ ]`+PARTIAL——符合 §4.3 一致表；PARTIAL 理由（A5 未全绿、门禁待固定 head 复核）与事实一致 ✓ |
| 三份 ZCode 裁决 | `sess_2a802094` 演进链自洽，最终裁决的 AC 定稿与卡面一致（卡面 AC5 比裁决更保守，AC1 未点名 DIAG 卡由 out_of_scope 承接）；与本 Review 无会话重叠 ✓ |
| FEA-11 共享 fixtures / ACL / profile | `fixture-observation.log`：62 候选仅按时间窗枚举、`ownership not proven; no cleanup` ✓；`python-acl-observation.log`：python.exe 48/目录 24 AppContainer ACE、`no-pre-run-snapshot`、观测本身零写入 ✓；Resource Manifest 三行 PRESERVE_UNKNOWN 与裁决 closeout 处置一致，`resource_closeout_status: pending` 如实 ✓ |
| Handoff 引用 | 基线 164ebabc、执行基线 d63d735a7、证据提交 8cad6d68c/b7344445e 全部存在且时间线自洽（23:13→23:40→23:50→23:52→23:53）；文件名 `<short-head>=b7344445e` 符合 §5 命名；不包含自身 commit hash ✓ |
| 唯一 Active | checkpoint 记录的串行执行与 STATUS「唯一 Active Task」语义一致（并行诊断卡建议已由补充裁决撤回）✓ |

## 未验证项（本 Review 未执行，须后续完成）

1. **固定交付 head 上的最终门禁复跑**：三次 gates 日志最后一次 HEAD=8cad6d68c（gates-control.log:1，23:43），早于 delivery_head 6ad10aacf（23:52）。AC5 PARTIAL 已如实声明此缺口；`doc/STATUS.md` 等 doc-only 差异对门禁敏感性极低，但 §4.2 要求 done 前以 `-TaskPath` 复跑并留证——**收口前必须补**。
2. 本 Review 为只读审查，未复跑任何测试/构建/门禁/探针；结论基于日志与 Git 对象核验。
3. A2/A3 真实层（当前 HEAD 安装、可见窗口、四页交互）与 A4 真实用户库升级/回退：维持 NOT_RUN，须由 FEA-15-PACKAGE-GAP-1 与后续卡承接。
4. resource closeout：62 个 fixture 候选、`C:\Python314` ACL、AppContainer profile 的最终处置待裁决（当前 PRESERVE 处置正确）。
5. sandbox 15 项 + Host ACL 96 项 + export_hook 根因：按 ZCode 三分类挂 FEA-15-DIAG-ACL-1 诊断范围，本卡不修（符合 out_of_scope）。

## 必要处置（approve 条件）

1. **（P2-1）** 裁决方授权修复 pin 口径：`verification/FEA-15-ACCEPT-1/**` eol 规则 + 按 blob/LF 口径重算 26 条 pin 值（`.gitattributes` 改动需新授权；建议并入 FEA-15-DIAG-ACL-1 或独立 GOV 卡）。
2. **（P2-2）** 收口时修正 README:9 措辞（或由裁决记录澄清）。
3. **（收口前置）** 在 6ad10aacf/e55a23dc9 上复跑 `check.ps1` 默认 + `-TaskPath` + `verify_pins` 并留日志，闭合 AC5。
4. **（P3-1..4）** 随下一轮治理文档提交顺手处理（SRC 表头、裁决日志时序注记、handoff diff 列举习惯）。

---

**推荐下一步**（可直接转发）：

> **致 DSH / ZCode 裁决会话（`sess_2a802094`）**：FEA-15-ACCEPT-1 独立 Review 已完成，结论 **approved**（0×P0/P1，2×P2 + 4×P3，见报告处置清单）。建议按序执行：① 在固定 head 复跑双门禁 + pins 留证，闭合 AC5；② 裁决 P2-1 pin 口径修复授权（.gitattributes + 26 条 pin 重算，建议并入 FEA-15-DIAG-ACL-1 承接）；③ 按既定顺序释放 `FEA-15-DIAG-ACL-1`（Owner 建议 Codex，诊断 sandbox 15 项 + Host ACL 96 项根因 + P2-2 文字修正）；④ 完成后按 closeout 处置 resource manifest（62 fixtures / Python ACL / profile）。本报告请按调度约定逐字保存至 `doc/reviews/FEA-15-ACCEPT-1-r1.md` 并记录本会话 ID。
