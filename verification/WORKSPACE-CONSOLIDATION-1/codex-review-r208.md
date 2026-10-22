---
task_id: WORKSPACE-CONSOLIDATION-1
reviewer: Codex
author: dsh
base_commit: b4560ae8ab2ff9c6c4db50f9d57b50fe1e8393df
reviewed_head: 3947d63447457fe3ef8d3587942e632724ab3d72
decision: changes_requested
review_mode: read_only
---

# WORKSPACE-CONSOLIDATION-1：Codex 独立复核 r208

## 结论

**changes_requested。不可据当前记录批准收口，也不适用 approve_with_conditions。**

76 个分支 bundle 的提交集合与归档基线吻合，这是已独立验证的成果。但保护项枚举遗漏仍未查全、ignored 内容没有删除前清册，另有一个 detached worktree 的两个独有提交没有进入任何已验证 bundle。治理 PASS 不能代替这些数据保护门槛。

本报告明确回答四项：

1. **越界删除重算为 18 个具体受保护资源路径，涉及 15 个实际删除根目录。** 单纯字符串相等求交是 14 个根目录；加上父子目录覆盖才得到完整影响范围。原「13」只覆盖六个 worktree 加七个不同的 temp 资源；其「8 temp」把同一个 capture 路径在父 Task / Review Task 的两行重复计数。新发现另外 **5 个**：P09 四个 review-scratch 资源，以及 P06 保留根下的 old-runtime/worktree。
2. **不能将「8 个 temp 夹具永久不可恢复」作为事实接受。** 去重为七个路径，其中一个是另外三个的父目录。X6 capture 的两份原始字节仍有现存、哈希相同的副本；两轮 selftest 的三个固定内容文件也可在内存精确重建并匹配原 pin。其余内容没有足够备份搜索证据，记「原位置缺失 / 恢复能力未证实」，不能仅凭 rmtree 推断全盘永久不可恢复。
3. **六个重建 worktree 均满足原九位 HEAD 前缀，属于部分重建，形态已改变，不是原样复原。** 原分支检出变成 detached；原 ignored 内容、目录元数据和运行环境没有被该操作恢复。六个原目录的记录体积合计 12,911,515,002 B，目前六处均没有列出的 ignored 内容。
4. **执行者未提到的主要问题**：P09/P06 新增保护资源受损；P03 两个独有提交未归档且当前无 ref；仍有 19 条未合并本地分支；1,223 是分支计数合计而非去重提交数（去重 320）；workspace/worktrees 实际删过七处；3.6 GiB task-envs 中检测环境仅占约 0.129 GiB；五个治理脚本不在冻结 allowed_paths；权威摘要、AC 与实际证据仍不一致。详见 Findings 与 Q1–Q8。

## 固定范围、方法与环境

- 审查固定上述 reviewed_head；Task 中 delivery_head 仍为 811fc2ea4，早于工具、清理清单和事故披露提交，不能把该旧字段当作本次审查对象。
- 只读输入：当前 AD-001、Plan/STATUS、Task/Review/工作区治理规则；本 Task 的 receipts；用户指定的全部受跟踪 doc/tasks/*.md 和 verification/**/*.json；命中资源及其明确引用的原清册、裁定和脚本。没有使用执行者的提取脚本生成 Q1，也没有运行任何清理脚本。
- Shell：PowerShell；解释器 C:/Python314/python.exe，Python 3.14.6；Git 2.52.0.windows.1。内联 Python 用 -B；Git 只读查询使用 --no-optional-locks。未恢复 bundle、未安装依赖、未运行会产生测试缓存的产品测试。
- 唯一允许写入、本轮唯一新增文件：verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md。未修改 Task、STATUS、Plan、既有 evidence、refs、worktree 注册、Git index 或现存目录内容。
- 受跟踪文档与脚本从当前 clean checkout 读取；其字节与被审提交的 tracked 内容一致。对存活资源的观察是本次核验时点的现场状态，不冒充删除前快照。

本次开始时实测：

| 项 | 实测 |
|---|---|
| 当前主线 | antigravity/P09-AC3-DELETE-HARDEN-1 |
| 本地分支 | 93；其中已并入主线 74、未并入 19 |
| worktree 注册 | 132 |
| tracked dirty / staged | 0 / 0 |
| 未跟踪逐文件数（-uall） | 1592 |
| 默认 status 折叠后的条目数 | 1236；与 1592 是不同口径 |
| doc/tasks 未跟踪草稿 | 26；路径集合与前次 preflight 的 26 个完全一致 |
| doc/tasks 已跟踪文件 | 296；包含本次运维 Task，不能按旧数字 294/295 判失误 |
| 治理（默认及显式 -TaskPath） | PASS (3 warnings)，exit 0 |
| git fsck | exit 0，无 missing/corrupt/error；有 614 条 dangling 诊断 |

没有删除前全部未跟踪文件的字节哈希，故「26 个草稿路径未变」不能升级为「整个运维阶段所有未跟踪文件逐字节未变」。本轮审查自身的只读边界另在末尾核对。

## Findings（均 open）

| ID | 级别 | 文件 / 行 | 触发、影响与复现 | 最小处置建议 |
|---|---|---|---|---|
| R208-01 | P1 | inventory.json:5336；worktree-removal.json:282；remove_worktrees.py:64 | P03-review-prep-112495c7 原为 detached，HEAD 0a25ceb45，含两个主线没有的提交；删除后无任何 ref 或已验证 archive bundle 覆盖。按分支归档遗漏 detached HEAD；当前对象存在不等于长期保存。 | Owner 优先在获准返修窗口保全完整 SHA、持久 ref 和核验 bundle；在此之前禁止 GC/prune。不要继续清理。 |
| R208-02 | P1 | doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165；codex-resource-ruling.md:59；doc/tasks/P06.md:127；P06/resource-manifest.json:17 | 四个 PRESERVE_UNKNOWN review-scratch 全被删；P06 PRESERVE_REFERENCED 根明确列有 old-runtime/worktree，该子树也被删。前者已有明确 Codex 原位保留裁定，后者不是文件名推测。 | 纳入事故台账和影响面，保留原清册；核对备份/重建能力，未经独立裁定不得宣称全部保护项在位。 |
| R208-03 | P1 | doc/tasks/WORKSPACE-CONSOLIDATION-1.md:70、110、116；六处原 worktree | 六处 HEAD 相同仅证明提交快照重建，不能恢复未盘点 ignored 内容及原分支检出。五个被称为 PRESERVE_REFERENCED 的 worktree 实际是 PRESERVE_UNKNOWN。永久丢失声明也被现存副本反证。 | 用逐资源「删除 / 部分重建 / 字节副本可恢复 / 未证实」记录；保留历史保留义务，不以重建掩盖删除事件。 |
| R208-04 | P1 | clean_workspace.py:35、52、69、109、118；remove_worktrees.py:70 | 仅凭区域名判为可再生；裸路径、相对工作区路径、非标准表格、PRESERVE_UNKNOWN、父目录保护、非 /worktrees/ 命名均会漏。删除前未核 ignored 逐文件来源、用户数据、进程占用；stash list 的非零退出码也未被拒绝。已发生数据删除，不能用 status 空补证。 | 先停用 apply 路径；另冻结允许工具修改的返修范围，以路径身份和父子覆盖核保护，解析/命令失败必须拒绝，补无破坏测试及逐项清册后再议执行。 |
| R208-05 | P1 | doc/REBASELINE_PLAN.md:54；doc/STATUS.md:7；Task:68–90、144–164；WORKTREE_SAFETY_INVENTORY.md:70 | Plan 仍写「9 AC 全 MET」；STATUS 仍报 126 与保护项全在；Task AC6/AC9 仍 MET、运行表却 NOT_RUN。Safety Inventory 把默认 status 说成「不忽略 ignored」，事实相反。Stage 7 有追加事故说明，但未提供完整影响清单。 | 追加更正当前摘要、AC、事故影响与最新 review 指针；不得覆盖历史 pin。AC1/AC2/AC6/AC9 至少重评，不仅降 AC3/AC7。 |
| R208-06 | P2 | Task:21–29、177–181；git diff b4560ae8a..3947d6344 -- tools | 新增 consolidate.py、archive_branches.py、remove_worktrees.py、delete_branches.py、clean_workspace.py 五个共享治理脚本，冻结 allowed_paths 未包含 tools/**。Canonical Evidence 引用工具不等于事先冻结其修改范围。 | 如实登记范围偏离；以后先由 Integrator 冻结工具范围，再修改、审查与集成；不把历史授权反写成早已具备。 |
| R208-07 | P2 | inventory.json / inventory.md；branch-deletion.json | 没有未跟踪逐文件大小/引用表，也没有分支 PR/记录引用列；分支表没有原 tip SHA。267 个已合并删除项中仅 19 个能从 worktree 快照交叉定位原 head，余 248 个没有同等 tip 证据。 | 补齐可补的盘点与 refs→完整 SHA 映射；对删除后无法补证的部分明确限制，不能继续把「四表齐全」当成已验证事实。 |
| R208-08 | P2 | Task:86、87、196；inventory.md:348 | 1,223 去重后 320；323 是批处理删除数，另 main/master 两条，实际净少 325。ARCHIVE 行实际对应 rmtree 删除，无归档目的地。49.5 的证据是逻辑字节累计，缺卷空间前后差值且未扣回建。 | 修正统计口径及 disposition 叙述，不把删除称归档、不把逻辑大小称实测物理释放。 |

依据：AGENTS「未提交内容归原作者」「仍有引用原路径保留」「不确定项保留」；WORKSPACE_GOVERNANCE 的 SAFE_TO_DELETE/UNKNOWN_DO_NOT_DELETE 与 worktree 门槛；协作协议 §3、§4.1/4.2、§6；本 Task 禁止范围；相关 Task 的具体保留裁定。技术产品架构未变化，不以 Legacy UI 条款要求无关改造。

## Q1：独立重新枚举与越界数量

### 方法与范围

以 git ls-files -z 限定受跟踪文件，实际扫描 **296 个 Markdown + 893 个 JSON，共 1189 个文件**。对 Markdown 逐表按 source_path / 源列定位；disposition 以 PRESERVE 开头即收录，移除行内反引号、粗体等展示标记。对 JSON 递归找 disposition 与 source_path 配对，不限根 resources 层。Windows 路径统一斜杠、大小写及尾斜杠，比较时使用目录分隔符边界，不把相邻前缀当父子。

P09 有中文「源」列和省略路径，按该行明确引用的 RX-01…RX-04 与原 resource-manifest.json 逐项连接；再以原 codex-resource-ruling.md 的四行交叉核对。没有把 JSON 测量条目本身虚构为处置授权，也没有泛化展开任意 glob/变量。

两个 .json 文件不是单个合法 JSON：run-baseline-20261014T0915CST-p02-admission-r2.json 是复合输出，antigravity-dispatch-r1.stdout.json 无合法 JSON 起始；两者全文均不含 PRESERVE，不影响本题资源枚举。复杂的共享根、环境变量、描述性源列另行人工核对，不因解析不了就判可删。

求交同时检查：

- source == removed_root；
- source 是 removed_root 内的受保护后代；
- removed_root 落在受保护 source 目录内。

| 口径 | 数量 | 含义 |
|---|---:|---|
| 两份 receipts 的删除根 | 208 | 50 worktree + 158 派生项 |
| 与具体保留 source 字符串相等 | 14 | 6 worktree + 4 temp 根 + 4 review-scratch |
| 具体受保护目录覆盖后，实际命中的删除根 | **15** | 再加 P06 根内的 old-runtime/worktree |
| 具体受影响的受保护 source 去重 | **18** | 6 worktree + 7 temp 资源 + 4 review-scratch + 1 P06 保留根 |
| 当前原位置完整性仍有缺口的具体 source | 12 | 7 temp + 4 review-scratch + 1 P06 根部分受损；六个回建也仅部分恢复 |

还存在 SEC-FIX-PATH-ECHO-1.md:113 对 **整个 workspace 根**的泛化 PRESERVE_REFERENCED 声明，文字是「按工作区治理保留，不在本 Task 处置范围」。纯机械祖先匹配会覆盖 168 个 workspace 删除根，加上仓外 P02 worktree 共 169 个根。这是**共享根范围声明需要整合裁定**，不能悄悄忽略；也不能把 169 冒充 169 份独立工件丢失。本报告的 **18 / 15** 是有具体资源身份、路径与删除收据对应的确定影响，属于保守且可逐条复核的口径，不宣称其他删除已经安全。

### 18 个具体受影响资源（逐项）

| # | source_path（完整路径） | 原 disposition | 当前状态 | 声明来源 |
|---|---|---|---|---|
| 1 | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `PRESERVE_REFERENCED` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/GOV-PIN-LINEAGE-1.md:152<br>doc/tasks/GOV-PIN-LINEAGE-1.md:184 |
| 2 | `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION` | `PRESERVE_REFERENCED` | 父目录在，受保护子树 `old-runtime/worktree` 已缺失 | doc/tasks/P06.md:127<br>verification/P06/resource-manifest.json:$.resources[1] |
| 3 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8` | `PRESERVE_UNKNOWN` | 当前缺失 | doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165 |
| 4 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export` | `PRESERVE_UNKNOWN` | 当前缺失 | doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165 |
| 5 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | `PRESERVE_UNKNOWN` | 当前缺失 | doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165 |
| 6 | `G:/CODEX/New Manga.workspace/review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18` | `PRESERVE_UNKNOWN` | 当前缺失 | doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165 |
| 7 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-BASELINE.md:135 |
| 8 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-BASELINE.md:137 |
| 9 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-BASELINE.md:136 |
| 10 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-X6.md:173 |
| 11 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-20261014-123308-pure-selftest` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-X6.md:168 |
| 12 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-r2-20261014-124643-pure-selftest` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-X6.md:171 |
| 13 | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1-capture` | `PRESERVE_REFERENCED` | 当前缺失 | doc/tasks/P02-NEW-TIME-X6-POSTRUN-REVIEW.md:132<br>doc/tasks/P02-NEW-TIME-X6.md:175 |
| 14 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | `PRESERVE_UNKNOWN` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/FEAT-CREATE-1.md:131 |
| 15 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `PRESERVE_UNKNOWN` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/FEAT-CREATE-2.md:71 |
| 16 | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `PRESERVE_UNKNOWN` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/FEAT-CREATE-4.md:82 |
| 17 | `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | `PRESERVE_UNKNOWN` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/P19-UI-FIX-2.md:100 |
| 18 | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | `PRESERVE_UNKNOWN` | 原路径/HEAD 已重建；形态与内容完整性仍有缺口 | doc/tasks/P02-MAINLINE-INTEGRATION.md:83 |

### 为什么原来的「13 / 6 / 8」互相矛盾

原已知集合实际为 **6 + 7 = 13 个不同路径**。X6 capture 在 P02-NEW-TIME-X6:175 和 POSTRUN-REVIEW:132 重复登记，不是两份独立 temp 目录；X6 temp 根本身又包住两个 selftest 和一个 capture 资源。不能把表行数、目录层级和删除操作数混加。

新发现比 13 多 **5 个具体保护资源**：

- review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8；
- 同前缀的 R11-392977a8-export；
- 同前缀的 R17；
- 同前缀的 R18；
- P06-GC-DISTRIBUTION-MIGRATION 保留根，受损部分为 old-runtime/worktree。

四个 review-scratch 删除收据合计 **14,699,110,702 B（13.69 GiB）**，恰为所宣称 review-scratch 收益的主体；它们曾被裁定「用途/独有修改/可重建性未完整核实，原位保留」。目前四个目录均不存在，不能继续称「0 条 pin 引用、可再生」。

六个 worktree 的 disposition 也要纠正：仅 GOV-PIN-LINEAGE-1 是 PRESERVE_REFERENCED；FEAT-CREATE-1/2/4、P19-UI-FIX-2、旧 P02 worktree 是 **PRESERVE_UNKNOWN**。二者都不能直接删，但根因不止裸路径漏识别，还包含只识别 REFERENCED 和 /worktrees/<name> 的规则缺口。

## Q2：六个回建 HEAD 与「复原」判断

六处 rev-parse HEAD 均 exit 0，symbolic-ref -q HEAD 均 exit 1（detached，预期结果）；common directory 均为主仓 .git；status --porcelain=v1 -uall 为空。下表逐一满足原 inventory.worktrees[].head 的九位前缀：

| 原路径 | 原九位 HEAD | 当前完整 HEAD | 前缀核对 | 检出形态 |
|---|---|---|---|---|
| `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `60d47991b` | `60d47991baea777996313d2cf1a335c136fb1ba0` | PASS | `dsh/GOV-PIN-LINEAGE-1` → detached |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | `c96958172` | `c96958172de8f8a3f3563da43a9fef09ac4447ba` | PASS | `codex/FEAT-CREATE-1` → detached |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `8202f2411` | `8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7` | PASS | `codex/FEAT-CREATE-2` → detached |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `f2c66ff26` | `f2c66ff262299f20292d8ca92cf8c2a28abce75b` | PASS | `codex/FEAT-CREATE-4` → detached |
| `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | `541aabb1e` | `541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c` | PASS | `codex/P19-UI-FIX-2` → detached |
| `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | `89413f45a` | `89413f45a601966eb40d7af7abea65cbdfc754b3` | PASS | `agent/antigravity/P02-real-webview-harness` → detached |

**判断：原路径与 Git 提交快照的部分重建，形态已改变。**

原分支检出已消失，部分原分支只剩 archive tag，不能把 detached 等同于「原分支恢复」。原 ignored 依赖、构建、模型、测试输入、目录元数据等没有删除前字节清册，checkout 不会恢复它们。当前 ls-files --others --ignored --exclude-standard --directory 在六处都返回空；这不能反向证明删除前也为空。分支/路径恢复是可以补做的技术处置，原 ignored 内容是否丢失仍须逐项调查。

PRESERVE_UNKNOWN 不是「只要 commit 能找回就算履约」；其含义正是未核清内容前应保留原位。PRESERVE_REFERENCED 的具体恢复要求也由该资源引用决定，不由本次清理者单方面缩成 HEAD 相同。

## Q3：temp 丢失、历史收口与建议

### 「八个永久丢失」被现有证据反证

本题给了三个 Task 名称，并非四个。三个文件目前分别为 done / approved / approved；approved 不等于已完成集成收口。

| 资源组 | 当前观察 | 可恢复性判定 |
|---|---|---|
| BASELINE temp 根、AC3 branch-resolution、AC3 toplevel-resolution（三处） | 原目录缺失；删除 receipt 有三条 | 未进行全盘/卷快照/备份搜索；不能证明永久不可恢复。应读取其引用的 closeout-resource-inventory-r2.json，逐文件建立缺失/副本/可重建映射。 |
| X6 temp 根 | 缺失，包含下述三个子资源 | 不是独立于其后代的另一份内容。 |
| X6 selftest attempt 1 / attempt 2 | 两处均缺失；每处记录三个固定内容文件 | 读取受跟踪 selftest 源码:861–900，在内存重建三种字节，均匹配原记录；见下。重建字节不复原原文件实例及当次运行的历史属性。 |
| X6 capture（父 Task 与 POSTRUN-REVIEW 重复登记） | stdout.bytes / stderr.bytes 原位置缺失 | 原 RunId 目录的 stdout.md / stderr.md **现存、大小与 SHA 完全相同**，可经授权复制重建原位置的字节；本轮未复制。 |

现存副本位置：

G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1/

| 原丢失文件 / 现存副本 | Bytes | 本轮实测 SHA-256 |
|---|---:|---|
| stdout.bytes / stdout.md | 32426 | 0109aed4fd474546eac28d1b1bfa88510285f1f367c0f157007f93e1886a3602 |
| stderr.bytes / stderr.md | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

同一映射原已记在 verification/P02-NEW-TIME-X6/codex-x6-result-verification-r1.md 的 Recorded evidence-scope deviation 中；本轮重新 hash，不只采信旧文字。

内存重建结果（没有写文件，也没有重跑一次性 X6）：

| 文件 | 构造字节 / 长度 | SHA-256，与两轮原 pin 均相符 |
|---|---|---|
| collision.bin | [1,2,3,4,5]，5 B | 74f81fe167d99b4cb41d6d0ccda82278caee9f3e2f25d5e5a3936ff3dcec60d0 |
| exclusive.bin | ASCII A，1 B | 559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd |
| partial-run.json | 两行固定 compact JSON + LF，93 B | 695d4bf696d7988c3a4561810a004bfe29b84083700c52fed34987194302a45d |

### 收口是否成了「假话」

**不能倒推当年的测试/Review 是伪造；但「这些工件持续原位保留、当前仍可复核」的承诺已被此次清理破坏。** 历史收口描述当时事实，保留义务则持续到获准变更。现在需要追加事故及当前可用性，不是消灭历史记录，也不是保留一个明知已过时的当前保证。

SHA pin 只能提供期望字节的指纹，结合原有运行/核验记录解释当时依据；**单独一串 SHA 既不能还原内容，也不能独立证明工件曾存在**。不要再用「SHA 还在所以仍可证其曾存在且内容为 X」替代工件验证。

建议由非删除者主持裁定，当前 Owner 按冻结范围落实：

1. 原 Task、原 Manifest、原 pin 和原 Review 保持历史字节；**追加**事故记录，标注发生 Task、被删 source、原 disposition、删除 receipt、当前存在性、恢复来源/字节核验、剩余缺口及受影响 AC。
2. 对新建的事故台账使用 availability=LOST_ORIGINAL / PARTIALLY_RECONSTRUCTED / COPY_AVAILABLE 等明确说明性字段；不要未经 Schema 冻结把 disposition 改成 LOST。现有 resource-manifest.schema.json:64 的枚举没有 LOST。
3. 也不能用 NOT_APPLICABLE 掩盖消失，或直接用 ALREADY_ABSENT 求绿：后者的 schema/process_check 要求记录不存在依据和无剩余引用，而这些资源仍被引用。区分「现在缺失」与「获准删除」。
4. BASELINE 的历史 done 不因后续事故自动变成当年没完成；其当前恢复能力标为受损。X6 / POSTRUN 的 approved 不是完成，受损证据涉及的后续集成/复用 Gate 须重新检查，不沿用旧批准推断当前可复核。
5. 恢复副本或固定内容时记录原内容 SHA、来源和本次恢复事件；重建不冒充原始工件实例，严禁重跑一次性 X6 并冒充原运行。不可恢复残余由用户明确接受风险、非作者复核后，才讨论相应后续 Task 的 closed_with_limitations；不批量改旧 Task 生命周期以覆盖事故。
6. 对 P09/P06 新发现的受损资源采用同一台账；P09 四处明确缺少唯一修改/用户内容盘点，不能先宣布「都是缓存」。

## Q4：76 个 bundle 的完整性

**本题的分支归档 payload 核验通过，条件是保留所需前置对象。**

独立核验：

- 目录实际 **76 个 .bundle，总计 22,106,711 B（约 21.08 MiB）**，与 manifest 匹配。
- 逐个 git bundle verify：**76/76，exit 0**；每个 list-heads 的原分支 tip、archive tag 指向、记录字节数均匹配。
- 固定归档排除基线 inventory.head = 62303a5766f3596a1cc1c082ea1a077cfa1a79ad。逐分支 rev-list base..tip 得到提交集合。
- 只在内存读取 bundle header 和 PACK，校验 pack trailer SHA-1、对象大小、OFS/REF delta，重算对象 ID。外部 delta base 用只读 cat-file --batch 取得，**不 unbundle、不 index-pack、不建临时仓库**。
- 76 个 pack 的 commit 集合分别与上述 rev-list **逐 SHA 相等**；计数分别与 manifest 一致。再比较 rev-list --objects：**应有新增对象缺失数为 0**。pack 合计 11,633 个对象记录；另含 53 个非提交对象记录，不影响 commit 集合相等，未据此声称对象集合必须无额外对象。
- 各分支独有提交数相加 **1223**；跨 bundle 去重为 **320**，因为多条分支共享提交。两者都要保留口径。
- 共 35 个不同 prerequisite SHA，均能在当前对象库读取且位于对应 archive tip 的祖先图。内存解 delta 使用了 225 个不同的外部 base 对象。

### 改写主线以后能不能恢复

前置依赖是 bundle header 记录的**具体对象 SHA 与其历史图**，不是「某个分支名永远叫主线」。

**仅改名或改写主线 ref，不会立刻让当前仓库的 bundle 失效**：只要 archive tags 及其完整祖先对象仍在，这些前置对象仍可达。当前 76 个 tag 均匹配，前置祖先关系也已核对。

**若只留下这 76 个增量 bundle，丢失原对象库，或改写/删除其保留引用后又 GC 了前置对象，就不能保证恢复。** 它们不是可直接在空仓库独立恢复的完整备份。技术依据见 [Git bundle 官方文档](https://git-scm.com/docs/git-bundle) 的 OBJECT PREREQUISITES / verify，以及 [pack 格式](https://git-scm.com/docs/gitformat-pack)。

建议后续另保留经过验证、内容自足的基线历史备份，并记录其 SHA/包含 refs 与这些增量 bundle 的依赖对应；无需机械复制 76 份全历史。未来在获准的隔离恢复演练中验证该组合。本轮按边界**没有恢复演练**。

逐 bundle 的本轮退出码、实际提交数、包对象数、前置数量与文件 SHA 见附录 A；表中所有行的 tip/tag/size 均 PASS，所有行 missing_commit / missing_object 均为 0。

## Q5：分支删除出处与 main/master

### 数量闭环

418 - 267（-d）- 56（-D）- 2（main/master 单独处置）= **93**。

branch-deletion.json 的 323 项只是前两类，**整个操作实际净删除 325 条 branch ref**。对比原分支集合和当前 refs，差集恰好是 323 条加 main/master，没有额外未记名分支删除。

### 267 个已合并删除项

逐项 receipt 的 via 均为 -d；但成功 stdout 和原 tip 未保存，不能独立证明每一条命令原样执行。本次对能从 worktree 快照取到原 head 的 **19 项全部**运行 merge-base --is-ancestor original_head reviewed_head，19/19 exit 0，详见附录 B。满足「抽验若干」要求。

其余 248 项没有同等完整 tip 证据，不能把 inventory 的 merged=true 当作当前独立重验。建议后续原始 refs 快照包括每个完整 object ID；不追造删除前记录。

### 56 个 -D 删除项

**56/56** 在 archive-manifest 有精确同名 branch、verified=true；对应实体 bundle 本轮再次验证通过，tag 与 original tip 一致，commit 集合也已核对。附录 A 的「-D 已删」行就是逐个核对清单，不仅比较数量。

原 76 个未合并分支的去向为：56 条批量删除 + master 单独删除 + **19 条本地保留**。19 条全有核验 bundle；这符合「保留或有归档兜底」，但**不等于已经合并进主线**。逐条列于附录 C。

### main

原 main 已不存在，无法再用其名字直接执行 HEAD..main。本轮从主 checkout 原生 HEAD reflog 中的最后一条 moving from main to antigravity/... 取到离开 main 时的旧 tip：

397babe2d36b986a2a1e3ce31e02a27844ecf3f3

对该实存历史对象复算：

- origin/main..397babe2d：2051；
- reviewed_head..397babe2d：0；
- merge-base --is-ancestor 397babe2d reviewed_head：exit 0。

因此**这份可定位 main 历史中的 2051 个本地额外提交均在主线内**，与执行者结论一致。限制：receipt 没有记录删除瞬间 main 的完整 tip；本轮没有把 reflog 旧 tip 假称成删除瞬间的 ref 快照。

### master

archive/master 实际指向 78faeee583600c51740200efd0e05776d6f2cf96，三个主线没有的提交是：

- 78faeee583600c51740200efd0e05776d6f2cf96；
- cb8336d6bf9f514eff0ea36c9bbba30ecb5feb82；
- 9617cbd3e597a613629b278db65e1627aafc8d0e。

master.bundle 包含这三个提交，verify、集合、tip/tag 均 PASS。两份恢复文件在主线与 archive/master 的 Git blob ID 逐一相等：

| 文件 | 双方相同的 blob ID |
|---|---|
| verification/M2-RC2/release-22a2c2bf.md | f2c0f82fc3dc41f87045bfbe14e829559fd99c78 |
| verification/M2-RC2/release-validation-22a2c2bf.md | 23697974cefc4da0863be6ed82246486e99b827a |

这证明两文件内容已保留；不把其余 master 提交说成已经集成。它们仍是归档历史。

## Q6：50 个 worktree 的 dirty 与 ignored

### （a）删除时「被判定干净」

50/50 在 inventory 中的 dirty_entries/stashes 为 0；apply receipt 包含 removed=true，remove_worktrees.py 在执行前确有 status 退出码/空输出复核。对体积最大的 **六项**交叉检查如下：

| 抽样目录 | 原 HEAD | dirty / stash 记录 | 原目录记录 B | tracked blob 逻辑 B | ignored 结论 |
|---|---|---|---:|---:|---|
| `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | `541aabb1e` | 0 / 0 | 5,371,083,340 | 304,215,220 | 未保存 ignored 清册，不能证明仅含可再生产物 |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `f2c66ff26` | 0 / 0 | 5,045,303,306 | 304,847,422 | 未保存 ignored 清册，不能证明仅含可再生产物 |
| `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh` | `c2bde3565` | 0 / 0 | 2,903,895,490 | 234,624,592 | 未保存 ignored 清册，不能证明仅含可再生产物 |
| `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree` | `ad75fadc2` | 0 / 0 | 2,186,496,184 | 232,756,749 | 未保存 ignored 清册，不能证明仅含可再生产物 |
| `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a` | `78faeee58` | 0 / 0 | 1,807,600,910 | 38,278,199 | 未保存 ignored 清册，不能证明仅含可再生产物 |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `8202f2411` | 0 / 0 | 1,601,245,026 | 304,285,433 | 未保存 ignored 清册，不能证明仅含可再生产物 |

这支持「当时被程序判为干净」，**没有保存逐次原始 status/stash 的 stdout、stderr、退出码**，不能在目录已删后反向独立证明当时的完整文件状态。库存生成代码还把 status/stash 失败的空输出计成 0，故库存 0 并不普遍代表命令成功；apply 对 status 的失败有拒绝，但 stash 退出码仍漏查。

### （b）ignored 是否只有可再生内容

**未能证实，关键验证缺失。** receipts 没有 ignored 逐文件路径、用途、hash、数据归属、来源和重建方法；六处虽有零 dirty 记录，目录体积却远大于原 tracked blob 逻辑大小。Git 内容与工作区物理字节的差值不能直接等同于 node_modules/target；也不能由差值直接断言存在用户数据，但它证明了当前证据无法覆盖所有被删字节。

原 .gitignore 还忽略 *.safetensors / *.pt / *.onnx、training_data/、虚拟环境、会话文件等，**它们不天然都是可抛弃缓存**。产品规则明确保护模型来源、训练数据、用户文件和任务可恢复性。Git status 空、git fsck 无 corruption、工作树重建或「没用 --force」均无法补足这一缺口。

此外，50 项里 **16 个原 HEAD 相对主线有独有提交**。15 个可由已验证 archive tag/bundle 覆盖；另一个 P03 detached worktree 未覆盖，见下。仅按分支盘点遗漏 detached 提交；worktree 移除也没有落实治理规则所要求的独有内容/Task 终态/引用核查。

### 执行者未提到的 P03 未归档提交

删除路径：G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7。

原 inventory 记 detached、HEAD 0a25ceb45、dirty=0、stash=0；worktree-removal.json 确认删除。独立执行：

~~~powershell
git --no-optional-locks for-each-ref --contains 0a25ceb4577158d9dff184776ff4599e74e25c57 --format='%(refname)'
# EXIT 0，空输出
git --no-optional-locks rev-list 0a25ceb4577158d9dff184776ff4599e74e25c57 --not --all
# EXIT 0，返回下面两个完整 SHA
~~~

- 0a25ceb4577158d9dff184776ff4599e74e25c57；
- 112495c70ff8a9c50fe00f4cd2eaa861d9a11b69。

二者目前可 cat-file/show，变更仅为：

- doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md；
- verification/P03-PACKAGED-SFX-ENTRY/RESUME.md。

不是新发现的生产源码/测试丢失，但确是未归档的独有治理历史，不能因「只有文档」无保护删除。逐个查 archive tags 的祖先覆盖，也查明不存在本 Task 76 bundle 的提交覆盖。目前未物理消失，却没有长期 refs 兜底，后续 GC 可能清除。优先由获准 Owner 做持久引用及 bundle；本轮没有执行。

### 37 个额外移除的注册项

原注册集合减当前注册集合、再排除 50 个目录删除，恰有 **37 项**；其目录目前 37/37 存在，.git 均不存在，符合「目录保留、只移除登记」的现场描述。缺少逐文件删除前后 hash，不能进一步证明其所有字节不变。其原 inventory 的 dirty=0 并不是可靠的 clean 证明。

当前数量闭环：213 - 50 - 37 + 6（回建）= **132**。126 是回建前时点，当前摘要应追加当前时点，不能继续单独使用 126。

## Q7：worktrees / task-envs 与 114.6 GB 保留判断

**不应整体清理；「两处完全没动」「全部体积都因同一个环境必须永久保留」则不成立。**

1. worktree-removal.json 中有 **七个** workspace/worktrees 子目录被移除：FEAT-CREATE-1/2/4、P02-NEW-TIME-X6-AC1-AC7、P15-C1-review、P19-AC3-1、P19-UI-FIX-2。其中四个后来回建。因此「workspace/worktrees 明确没动」为假；被特别排除于 Phase C，不代表此前 Phase B 没改过。
2. 执行者原保护名集合 57 个，目前 **57/57 均仍在注册且目录存在**。这验证一个已知子集，不证明保护枚举完整，更不证明所有源文件原样保留。六个回建项和新发现资源恰好说明这种差别。
3. 独立使用 scandir/lstat 计数，不跟随 reparse/junction：worktrees 当前 **120,225,570,583 B ≈ 111.97 GiB**、952193 个普通文件、71 个直接子目录；task-envs **3,880,296,828 B ≈ 3.61 GiB**、104117 个文件、6 个直接子目录。worktrees 有七处权限拒绝（若干 .pytest_cache 及 SEC-FIX.../tmp/pytest-of-49745），数值是可读逻辑字节下界，**不是精确磁盘占用或可释放物理空间**；未提升权限。reparse 示例只记录前 150 项，不把样本数称总数。
4. P15 resource-manifest 的三个 junction 已现场复核：node_modules、dist、src-tauri/target/core-sidecar 均存在、是 ReparsePoint、目标为主 checkout 对应目录。它们必须按 pin 留位；同一目标经多个 junction 可见，也不能重复计算成多份可回收数据。
5. M2-PROD-DETECT-ENV-1/venv 目录与 python.exe 均在；pyvenv.cfg 明确 include-system-site-packages=true，transformers-5.17.0.dist-info/METADATA 为 Name: transformers / Version: 5.17.0。这里保留的是「全局 Python/torch + transformers 覆盖层」，不是独立、完全自包含的环境。本轮未启动它或重跑模型/测试，以免超出只读边界。
6. 该 Task 整个子目录仅 **138,129,041 B（约 131.73 MiB）**；task-envs 最大一项是 P02-NEW-TIME-X6-BUILD-CARGO，2,328,053,874 B。不能把整个 3.61 GiB 都说成检测环境。其他五处应按各自 Task/引用/来源处理。

保留当前检测 venv 是正确的：它仍是已验证环境的载体，删除会取消当前可用配置；**但不等于未来永远不能迁移或重建**。将来须冻结替代环境、版本来源、外部权重与全局依赖，验证替代后再裁定旧环境。其他缓存/依赖也可逐项申请处置，不能以 node_modules/target/venv 名称自动放行，更不能整棵 114.6 GB 批删。当前证据没有支持任何新增清理动作。

释放空间声明也需收敛：两份 receipt 的 bytes 为 31,493,644,833 + 21,636,208,040 = 53,129,852,873 B（49.48 GiB）**删除前递归逻辑字节合计**；没有磁盘空闲量前后证据，没有说明 junction/硬链接分摊，且之后回建六个目录。只可标「记录的候选/删除逻辑体积」，本轮不能独立认证实际净释放约 49.5 GB。

## Q8：主线不改名是否合理

**成立。本次可保留该名字作为唯一登记的治理主线，不应因名称不规范要求本 Task 越界改名。**

「唯一主线」是权威集成入口和历史去向清晰，不是分支名必须为 main，也不是所有其他分支必须被删除/强行合并。当前 WORKSPACE_GOVERNANCE 已明确主线身份；本 Task 又明确禁止治理主线改名/合并。未合并但已说明归档或保留的工作可以存在。

本轮独立 git grep -l -F 在被审 HEAD 的受跟踪文件中确实命中 **44 个**；但在运维基线 b4560ae8a 是 34、登记后 62303a576 是 35。44 是**当前**计数，包含这次自己新增的引用，不能假称为操作前同一口径。引用迁移复杂度是推迟改名的合理工程依据，硬依据是 Task 边界。

此外，重命名 branch 本身不是改写 commit 历史，**不会自动把所有以它为基的其他分支/worktree 的历史改掉**；只会影响该 ref 名字、检出它的 worktree 的符号引用、配置/脚本及文档依赖。不能以错误影响描述代替风险分析。若将来统一成 main，另行裁定范围、完整 refs/依赖映射、工作树占用、原 main/master 已有归档与回滚，再同步权威文档。本轮不需要这个动作才算目标成立。

## Architecture / Verification 与 AC 裁定

**Architecture：** 未发现本批变更修改 React/Tauri/Python/SQLite/Managed Copy 产品分层；该产品轴 N/A。运维的持久性、恢复点与用户/未知数据保护轴 **FAIL**：已知 PRESERVE 资源被删，且存在无归档 detached 提交与 ignored 验证缺口。

**Verification：** 已执行。bundle、六处 HEAD、若干合并关系及治理检查有 PASS；资源完整性与 ignored 安全性不能 PASS。未执行产品测试、bundle 恢复、旧夹具恢复、全盘备份/数据恢复搜索，分别受本轮边界或删除前证据缺失限制，不冒充已验证。

| AC | 本轮判断 | 理由 |
|---|---|---|
| AC1 | PARTIAL | 分支逐条计数存在，未跟踪逐文件表/引用列/原 tip 信息不足，保护枚举有漏；不是完整安全盘点。 |
| AC2 | PARTIAL | Stage 7 已追加，但摘要与当前 132、补充影响范围、ignored 行为仍不一致。 |
| AC3 | PARTIAL / 保护目标 FAIL | 明确发生 18 个具体保留资源受影响，不能以原 57 名子集盖过。 |
| AC4 | 分支 payload PASS，灾备能力有条件 | 76/76 增量 payload 验证通过；不含 P03 detached 两提交，且需前置对象。 |
| AC5 | 抽验 PASS，证据限制保留 | 19 项祖先核验通过；56 个强删全部归档；其余 merged 项缺原 tip 完整映射。 |
| AC6 | PARTIAL | 50 clean 判定记录存在，但 protected/unique/ignored/终态与引用门槛未全落实。 |
| AC7 | PARTIAL / 安全目标 FAIL | 夹具与 P09 未知资源已删，收益不能覆盖事故；物理净释放未证实。 |
| AC8 | PASS | 保留已登记主线符合禁止改名的范围；另 19 条未合并分支已说明去向。 |
| AC9 | PARTIAL | 治理 exit 0、草稿路径 26 保留、fsck 无 corruption 均成立；保护与恢复验收不成立。 |

这里是 Review 判断，不修改 Task 自身状态或原 checklist。P1 未解决及关键验证缺失，按协作协议 §6 不能批准；不可由作者单方面把事故降为 limitation 后宣布 DONE。

## 本轮运行证据（均只读）

| 实际命令 / 探针 | 环境 | EXIT / 结果 |
|---|---|---|
| git status --porcelain=v1 -uall；git diff --cached --name-only | PowerShell / Git 2.52 | 0；tracked/staged 空，untracked 1592 |
| pwsh -NoProfile -File tools/governance/check.ps1 | PowerShell | 0；PASS (3 warnings) |
| pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md | PowerShell | 0；同样 PASS (3 warnings) |
| git fsck | 主对象库 | 0；382 dangling blob、75 dangling tree、157 dangling commit；无其他诊断 |
| 独立 Markdown/JSON source/disposition 提取 + 两份 removed 求交 | Python 3.14.6 -B，内存 | 0；18 具体 source / 15 removed 根，详表 Q1 |
| 六处 rev-parse HEAD / status / common-dir | Git 只读 | 全部 0；symbolic-ref 的 1 是预期 detached |
| git bundle verify、list-heads、tag tip；内存 PACK 解码 / SHA / rev-list | 76 包，主对象库只读 cat-file | 全部 0；commit 集合逐包相等；新增对象无缺失 |
| 19 个旧 branch head 的 merge-base --is-ancestor | 固定 reviewed_head | 全部 0 |
| 50 个原 worktree head 的独有提交与 ref / archive 覆盖 | 固定 reviewed_head + refs | 16 个有独有历史，15 有 archive 覆盖，1 没有 |
| 现存 capture 两副本 hash + 固定 selftest 字节内存构造 | Python -B | 0；匹配 Q3 五种 SHA |
| workspace 目录 lstat/scandir，不跟 reparse | Python -B，只读 | 0；扫描返回七个权限缺口，已明确是下界 |
| P15 三处 lstat/readlink；venv 配置/metadata 读取 | 只读，不 import 目标包 | 0；资源存在 |

报告写入前的治理原始输出（默认与显式 TaskPath 一致）：

~~~text
Shell: PowerShell
Git: 2.52.0.windows.1
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\WORKSPACE-CONSOLIDATION-1.md
WARN: 存在 38 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3152 bytes / 26 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5997 bytes / 55 lines
Governance check: PASS (3 warnings)
EXIT: 0
~~~

fsck 的 dangling 不等于对象损坏，但也不是「没有任何诊断」。不得把它作为 ignored/源数据未丢失证明。本轮分类后的非 dangling 诊断为空；按剥除首尾换行后的 stdout 计算 SHA-256：
2f9a032129e97a1f0f44188ef5d95256377242973fcfcabe9c11fdbe7ece04f6。
完整 614 行未另写文件，以遵守单文件输出边界；可用相同只读命令复算。

判别力探针直接作为本报告内嵌证据，不另造日志/脚本目录。若需要正式恢复演练或删除前已不可补的 ignored 证据，必须在新冻结范围内提供；不能从本报告摘要外推恢复成功。

## 推荐下一步与复审条件

由当前 Owner **dsh** 在本 Task 返修窗口处理，**Reviewer=Codex（非作者）**；先由协调/整合流程确认精确 allowed_paths，不能把本只读 Review 当作新增写授权。可直接转发：

> WORKSPACE-CONSOLIDATION-1 返修，依据 codex-review-r208.md，base=3947d63447457fe3ef8d3587942e632724ab3d72。先暂停清理/GC/prune，优先保全 P03 的 0a25ceb4577158d9dff184776ff4599e74e25c57 与 112495c70ff8a9c50fe00f4cd2eaa861d9a11b69，记录持久引用、bundle、独立 verify 与提交集合。随后按 Q1 的18项建立追加式事故台账，区分原件缺失、可用副本、精确字节重建和未核实 ignored 内容；将 P09/P06 新影响纳入。修正当前 Plan/STATUS/Task/Inventory 的过时摘要与 AC，原 pin/旧 Review 不改写。没有证据的安全性与物理收益保持 PARTIAL/UNVERIFIED。工具修复先冻结 tools 范围并补无破坏测试；禁止再删新资源。交付新的固定 head、Handoff、返修证据与逐项 findings disposition 给 Codex 复审。

不可逆损失不能靠补标签消除。无法恢复的剩余项须由用户明确裁决风险，独立复核确认报告完整；不能虚构原始工件或改历史 pin 使检查器通过。本轮没有关闭 Task，也没有释放后续清理 Task。

## 附录 A：76 个 bundle 的逐项独立核验

所有路径为 G:/CODEX/New Manga.workspace/archive/bundles/<branch 将 / 替为 _>.bundle，与 archive-manifest 的每行文件名一致。原 tag 名为 archive/<同一安全文件名>；原 branch 名仍在 bundle header 中。下表「实际提交/记录」两边逐包相等且集合逐 SHA 相等，header tip/tag/bytes 都 PASS，新增对象缺失 0；「保留」表示本地原分支仍存在，不是已经合并。

| # | 原分支 | 实际提交 / 记录 | verify EXIT | pack 对象数 | 前置数 | 原分支去向 | 本轮 bundle SHA-256 |
|---|---|---:|---:|---:|---:|---|---|
| 1 | `agent/antigravity/P02PRE-R1G` | 6 / 6 | 0 | 39 | 1 | `-D` 已删 | `8964fdb9c6f6a3abe5cdd45ef33e2a3b86965ca8c4eac3bd623e40f52bd77da3` |
| 2 | `agent/antigravity/P02PRE-R1H` | 7 / 7 | 0 | 46 | 1 | `-D` 已删 | `06faef874be88d0558f93e18127aa7dab9ef5e6671c84bbe885c1d19e234bcb2` |
| 3 | `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | 15 / 15 | 0 | 125 | 1 | 保留 | `143c99b1d610c7f914d419a8b2569093adce309e1bcf9e4efb116bf0bb9307c4` |
| 4 | `agent/antigravity/P02PRE-R1H-R6-A4` | 2 / 2 | 0 | 16 | 1 | `-D` 已删 | `03f6c4f6dcf15c07abb9b5a766b227d26dd654ca53d6ded9faddf6c4c5173b75` |
| 5 | `agent/antigravity/P22-roundtrip-serialization` | 10 / 10 | 0 | 62 | 1 | 保留 | `7c0abce11ae88840aa43efa455de2d6eeb0ce9d1182c4dd2b93ba0bca84f50a8` |
| 6 | `agent/antigravity/T3.2.1-repair-10` | 49 / 49 | 0 | 467 | 1 | `-D` 已删 | `595bff0d524b3c397a7f6bc8e46fe0c41eaea44d3d0c617dba67ca1aea8671f6` |
| 7 | `agent/antigravity/T3.2.1-repair-11` | 53 / 53 | 0 | 499 | 1 | `-D` 已删 | `1ecdd898257d4318f1a8d76ac8c26690648be796f2e5be76f16ca30f89b560dd` |
| 8 | `agent/antigravity/T3.2.1-repair-12` | 54 / 54 | 0 | 507 | 1 | `-D` 已删 | `3e0799330be205ff7e9da3033b8864ab71f1c798478adc02bed674be5b98dacc` |
| 9 | `agent/antigravity/T3.2.1-repair-14` | 4 / 4 | 0 | 57 | 1 | `-D` 已删 | `07f63a1bff728af2e03674e60e2b9d87822c2141b2d8fce861f7c7e7daea9ec2` |
| 10 | `agent/antigravity/T3.2.1-repair-3` | 15 / 15 | 0 | 161 | 1 | `-D` 已删 | `7a78c026e1f0b868f225f462e66c083f71add32b91dbbd14b5d6a62851dbd9e3` |
| 11 | `agent/antigravity/T3.2.1-repair-4` | 19 / 19 | 0 | 195 | 1 | `-D` 已删 | `9a04f1f6ebd60929df332195dbff0ffd9c5ab8e519016c43651b493254c209cb` |
| 12 | `agent/antigravity/T3.2.1-repair-5` | 25 / 25 | 0 | 244 | 1 | `-D` 已删 | `ccde24541898fc5fb31e98997541cc5c71665e7013764730461c2114434719b7` |
| 13 | `agent/antigravity/T3.2.1-repair-6` | 30 / 30 | 0 | 285 | 1 | `-D` 已删 | `d8c726b03fa39554dcca33bd6958ea452b25a025b5fe294ee1622ea2aae338b0` |
| 14 | `agent/antigravity/T3.2.1-repair-7` | 41 / 41 | 0 | 374 | 1 | `-D` 已删 | `0c7c0ee599386d70a8531a0a9f4dc5e9f4276c2dc67918f36361b2100eb87ea5` |
| 15 | `agent/antigravity/T3.2.1-repair-9` | 46 / 46 | 0 | 442 | 1 | `-D` 已删 | `ce5cdf07eaa38bf36b9d7bb52542c730ac87418c39b0ed48800db9f01758e4e6` |
| 16 | `agent/antigravity/T3.2.1-windows-packaging` | 8 / 8 | 0 | 115 | 1 | `-D` 已删 | `ee8ce71673f3d8a93c1174e4450c30694e563e51639dd3f7e45dfd15c634425a` |
| 17 | `agent/codex/M2-C1-typed-ipc-contract` | 16 / 16 | 0 | 156 | 1 | `-D` 已删 | `5ee7d8dfb8de31412d93120fd5ff34624f2141b301c41aa7f9cd2dc875350484` |
| 18 | `agent/codex/P02PRE-R1H` | 13 / 13 | 0 | 83 | 1 | `-D` 已删 | `2fbaf198f1c8edcea09bbfe9ea367b46f51c48828d7c44cbc133f70e4ad17b40` |
| 19 | `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 3 / 3 | 0 | 34 | 1 | 保留 | `3eb0253dfd2a152a5fd2cc89c74c6a2ec0e3d0039465583c8ccf700486f48a09` |
| 20 | `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 4 / 4 | 0 | 42 | 1 | 保留 | `1e775062b4e239ebcf0a0ceb77af74a3de82c9ff76799559f3e34816462df21d` |
| 21 | `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | 3 / 3 | 0 | 31 | 1 | 保留 | `e5b58b930a0e70e74ade886db7baf00b90ea0409a3f1a6c7281fc777f1972d62` |
| 22 | `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 18 / 18 | 0 | 159 | 1 | 保留 | `342beaac43cd7459bcdc3e389bcd2e77e8349d33b8f445dc8eb4ea72124f164d` |
| 23 | `agent/codex/T1.2.1-integration` | 2 / 2 | 0 | 11 | 2 | `-D` 已删 | `9f61d1b930a751f89f90d6ff020407e695818410d4889d9770e4f2c20b43bfeb` |
| 24 | `agent/codex/TASK-013-production-pipeline-seam` | 2 / 2 | 0 | 11 | 1 | `-D` 已删 | `41ba4d1eb20829372d5440f2cc3ff62bd1a874e7fa4d83258720331c978cb91b` |
| 25 | `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG` | 1 / 1 | 0 | 8 | 1 | `-D` 已删 | `764aa58d8f9affb256a09a5b2d932b2a9ca77e5d6d458f9f691db8a9d6c50b3a` |
| 26 | `agent/deepseek/T1.1.1-detector-evaluation` | 1 / 1 | 0 | 26 | 1 | `-D` 已删 | `de4856cf60c6a8d543420f250e8bb2d385b710951ba44aa518999a4e2f088140` |
| 27 | `agent/deepseek/T3.2.1-review-740503e` | 1 / 1 | 0 | 19 | 1 | `-D` 已删 | `d1652314b19ff2a059848a06a1b66f67b4832eb13f067d496002f1ed28a769f6` |
| 28 | `agent/deepseek/T3.2.1-review-7d687f5` | 1 / 1 | 0 | 31 | 1 | `-D` 已删 | `769acb1ec6a16658c4f96a8ae74bad57f748e2b5c1ce977369671afbc0d23d23` |
| 29 | `agent/deepseek/T3.2.1-review-92c9307c` | 1 / 1 | 0 | 28 | 1 | `-D` 已删 | `9b4b46d128602aeb972b9a4cfc8bf0fe5b94c29f0ea008aabe43143f5b727296` |
| 30 | `agent/deepseek/T3.2.1-review-9622395` | 53 / 53 | 0 | 497 | 1 | `-D` 已删 | `5b20ece677e7e232afeb904b8b63d627d33c2eeb8e12bcadbcf0247c66e968a3` |
| 31 | `agent/deepseek/T3.2.1-review-a2f6695` | 54 / 54 | 0 | 504 | 1 | `-D` 已删 | `efd3c886b664148e90f5331482eed9532c835ea4753b2d1843dd0d048cbe5167` |
| 32 | `agent/deepseek/T3.2.1-review-be5200e` | 49 / 49 | 0 | 465 | 1 | `-D` 已删 | `a0edaa9274e4c6bec85177e9d012e24038458e75938f1d9ecd42836764124e34` |
| 33 | `agent/deepseek/T3.2.1-review-cdc0b6f` | 6 / 6 | 0 | 77 | 1 | `-D` 已删 | `aecaf881c8a182249a4a99273d29a83e31dc0235548067804b6e54c989e770a3` |
| 34 | `agent/deepseek/T3.2.1-review-d2bf6a8` | 46 / 46 | 0 | 445 | 1 | `-D` 已删 | `e08a537d11c5814135ae26cc82cda5362be890fde87111abfae434b37aaa7467` |
| 35 | `agent/deepseek/T3.2.1-review-d79d7dd` | 14 / 14 | 0 | 156 | 1 | `-D` 已删 | `9f82d2303b944093e3949c9e497c32fa2f0557745c5bb936fbe125d321cc92c6` |
| 36 | `agent/deepseek/T3.2.1-review-f39ddc0` | 1 / 1 | 0 | 21 | 1 | `-D` 已删 | `d49c41edecbc0f9827c98211dd5956f5d705582dcf0893a1cda73298f649cd2b` |
| 37 | `agent/deepseek/T3.2.1-review-f6dc383` | 31 / 31 | 0 | 294 | 1 | `-D` 已删 | `8baf6ffd54ff86f3bc3a19958451b0cf9bb9243c4f21aa24816e49d603f57ae0` |
| 38 | `agent/deepseek/T3.2.1-review-repair-14` | 3 / 3 | 0 | 34 | 1 | `-D` 已删 | `8f0fd3e570197b0809ba6dedfb46aac4909fcba2caecbbae16443f2c6b1f1f55` |
| 39 | `agent/deepseek/T3.2.1-review-repair-14-r2` | 5 / 5 | 0 | 65 | 1 | `-D` 已删 | `bfa2f915f7e254030007ddfc3f8864e85ecf23322647b1f6776ee5370d2e5c62` |
| 40 | `agent/deepseek/T3.2.1-review-repair-7` | 6 / 6 | 0 | 65 | 1 | `-D` 已删 | `23b5610fa027c344c4d6ddd8d60d336b3286f4041195500f3c2afa1b1576ec77` |
| 41 | `agent/deepseek/TASK-004-review` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `8b4c92056a5a0f3ef750609623e847612d2ba0533e861f09c67c0586866265fe` |
| 42 | `agent/deepseek/TASK-015-posthoc` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `f5d0900732ed8dea56004bd95c2d0953a67a8e5d8aa83c6d47699dc0bfda6dd8` |
| 43 | `agent/deepseek/TASK-017-posthoc` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `5fc25f3ca7758d35f1a1d020ee021c573ec96edbf07fa6a3f9f388c2e9af7719` |
| 44 | `agent/deepseek/TASK-024-posthoc` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `38608b59990a30cb49c34773abbbd612e46b41ec526c9b1f4cdfc124ab537c2c` |
| 45 | `agent/qoder/T1.1.2-region-canvas` | 2 / 2 | 0 | 20 | 1 | `-D` 已删 | `79a97c46d87f672fa51836a4af32c592199720ffaada054f85bb92f3816a972a` |
| 46 | `agent/qoder/T2.2.1-reader-workbench-qml` | 5 / 5 | 0 | 53 | 1 | `-D` 已删 | `f70e2000e7d888e932da8261c55f16ddcdbfcf2d04316fb7f9534e417f8dd397` |
| 47 | `agent/qoder/T3.2.1-repair-13` | 54 / 54 | 0 | 507 | 1 | `-D` 已删 | `274b658525e0bbab605ae343ffe86defb07c57a215ad61412a63a5c8b2458f1e` |
| 48 | `agent/qoder/TASK-047-ui-ux-gui-design` | 9 / 9 | 0 | 129 | 1 | `-D` 已删 | `fbe39a161eb2f0e0375f91cab0acf60e9c81a95bdd04f0faa7ef18e9d028cd8d` |
| 49 | `agent/qoder/TASK-061-review` | 4 / 4 | 0 | 64 | 1 | `-D` 已删 | `8d73200608883fc3b6acb93e99cb03db38a8aa792557e7f6841970fc5d5a46ce` |
| 50 | `agent/zcode/M2-I1-core-assembly-seam` | 1 / 1 | 0 | 10 | 1 | `-D` 已删 | `7029fd6827f98ed3205a9347440214cf90419893345c4b029b8a7793ebef3d29` |
| 51 | `agent/zcode/P02-NEW-TIME-BASELINE` | 60 / 60 | 0 | 512 | 1 | 保留 | `3a3d7927b9e13d12a8cad7305f3fab1283419eb32c614dbee0b68e11f7a3a3d8` |
| 52 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 31 / 31 | 0 | 284 | 1 | 保留 | `c51766ce3b21b5b356b2ac3b90714003a57b9a06ff0d1164599a95fb8e1a6653` |
| 53 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 78 / 78 | 0 | 613 | 1 | 保留 | `d040a8b439de52b038b978f9ef78168fa3ced5924c9f8a96af013c2a8e30b2fe` |
| 54 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 43 / 43 | 0 | 381 | 1 | 保留 | `bfba636df5eda5c4b17f57cdbdbb2ea94dbfb33db84d3f9e4d76b6fada2f727a` |
| 55 | `agent/zcode/P02PRE-R1H` | 7 / 7 | 0 | 46 | 1 | `-D` 已删 | `0b438762118421b1773e2d7e8fa06586301aaf3b7b7c084af1aac354c7a8cd3c` |
| 56 | `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | 4 / 4 | 0 | 36 | 1 | 保留 | `448c05c29779e27204931a971f428acd0b004b9737d01b9d1a69c2b79d688e81` |
| 57 | `agent/zcode/T1.2.1-settings-ui-viewmodel` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `5b952f47cb297aff60838d0a718c364ad4dd71e97bf1167b1a3b0a010bd7bdba` |
| 58 | `agent/zcode/T2.2.1-reader-workbench-polish` | 1 / 1 | 0 | 7 | 1 | 保留 | `4ed889346fcd03a701de28a67b7520a2a263b16093d870334bb98776a53dbe32` |
| 59 | `agent/zcode/T3.2.1-repair-13` | 64 / 64 | 0 | 680 | 1 | 保留 | `c3e84dbdea61cbbfea089545a0f0a4612835f32f0b212828b01c63ec215f05f8` |
| 60 | `agent/zcode/TASK-045-posthoc` | 1 / 1 | 0 | 9 | 1 | `-D` 已删 | `7c6c2c88a923009f7cbef6bf74edf6577278978a17b75fc2603e728bc5b33cb6` |
| 61 | `codex/FEAT-CREATE-1` | 3 / 3 | 0 | 24 | 1 | `-D` 已删 | `ad3fd7bbd3aa50fc992b95d036647da4f66677cb3ceff31b9f5e49704f8a1ded` |
| 62 | `codex/P02-fallback-scope` | 1 / 1 | 0 | 5 | 1 | `-D` 已删 | `8d9805e103a48b943f640f20c36deee1cd7598714f72a2ae2ddfe07160a27b86` |
| 63 | `codex/P02-hook-cache-isolation-plan` | 7 / 7 | 0 | 108 | 1 | 保留 | `4c97f484122d76ba9b3ab2f5a746c6fab4d597cdf543cf8a41abf2750a36a9c9` |
| 64 | `codex/P14` | 2 / 2 | 0 | 25 | 1 | 保留 | `5b208d2978e4b91656c24666d85b6bb0a5a5a806af615ed648f9aab37578b16d` |
| 65 | `codex/P15-C1-FU2` | 2 / 2 | 0 | 10 | 1 | 保留 | `32e5752ea879106a953816573be77da9f5fefc9d755891cd3a622b54870a32a6` |
| 66 | `codex/T3.2.1-release-gate-closeout` | 50 / 50 | 0 | 473 | 1 | `-D` 已删 | `66d88cd3bf3737a22a9395d633637f5717f04bc56a9bc5d655262f871bd82c9e` |
| 67 | `codex/integration-p02pre-r1h-p2-1-external-harness-trace` | 18 / 18 | 0 | 159 | 1 | `-D` 已删 | `3de0edfe1e7189be673681e0f84f155d77ff244887bd48537fb5fae2e6935c40` |
| 68 | `codex/project-roadmap-rebaseline` | 1 / 1 | 0 | 55 | 1 | 保留 | `9f1de2535bf88415307ce32f72068d92593e255dc09e2f889f091d3043f6be38` |
| 69 | `codex/rebaseline-audit-20260921` | 1 / 1 | 0 | 14 | 1 | `-D` 已删 | `0933a9617353a10b720762446be1a509c16079782a7daf83d7f17bfa66ff03c3` |
| 70 | `dsh/GOV-PIN-LINEAGE-1` | 2 / 2 | 0 | 13 | 1 | `-D` 已删 | `9ceb7c89f55d77f0bc3d371984cacaaff94b200fb47d1bc404b53b3e0cf2d5c9` |
| 71 | `master` | 3 / 3 | 0 | 32 | 1 | 单独删除 | `9114f5f51eec1fb5cad4016607a0872182d0b515608711a3d2079a9d5ac3dc04` |
| 72 | `review/deepseek/M2-C1-typed-ipc-7d908a5` | 4 / 4 | 0 | 43 | 1 | 保留 | `2e5b76397b79f38e4dd44ee12bdafd443ea424ad34d20d36388ceaadcf0b821c` |
| 73 | `review/deepseek/M2-C1-typed-ipc-r2-7e65f4f` | 12 / 12 | 0 | 116 | 1 | `-D` 已删 | `bc319d6a2bf53aa69bf202ddd7d3bb0ffdf817fffaf63699aae33d7d5169349d` |
| 74 | `review/deepseek/M2-C1-typed-ipc-r3-4d66523` | 14 / 14 | 0 | 129 | 1 | `-D` 已删 | `883752479e2fa2bfcda50da19f17f6ed6f86078e4edc65db9fdd5cd5acf586da` |
| 75 | `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 1 / 1 | 0 | 9 | 1 | 保留 | `b799920357ed71bb3a36c19b51f5c2dde857cfab149987c9df4557e804795370` |
| 76 | `review/qoder/M2-C1-typed-ipc-r3-4d66523` | 15 / 15 | 0 | 146 | 1 | `-D` 已删 | `bce44150694a8766a82005d5a26a4a346bff5203569d41eaee3c6cf80734f027` |

## 附录 B：19 项已合并删除分支交叉抽验

每个 original_head 取自清理前 inventory.worktrees；最后一列为 merge-base --is-ancestor original_head reviewed_head 的实际退出码，0 表示确为祖先。

| 已删分支 | 原完整 HEAD | EXIT |
|---|---|---:|
| `agent/antigravity/P02-real-webview-harness` | `89413f45a601966eb40d7af7abea65cbdfc754b3` | 0 |
| `agent/antigravity/P04-prod-command-concurrency` | `a4419167b277e896b8df26110092b79ee0995994` | 0 |
| `agent/zcode/M2-SFX-ANNOTATE-R2` | `44cd7cfb63f81fa2786aa1204cd4bf1a0d9e6d12` | 0 |
| `agent/zcode/M2-SFX-CORRECTION-EXPORTER` | `669146a19c10ca367dfa1de7027f10326830f7a5` | 0 |
| `agent/zcode/M2-SFX-DATA-INFRA` | `54e04f1ba8767a231e04512b43cf3b7f0550f91f` | 0 |
| `agent/zcode/M2-SFX-SYNTH-BG-AUTO` | `5907be5967ea01ce42ee2834e84837771abadc7f` | 0 |
| `agent/zcode/P02-NEW-TIME-X6-AC1-AC7` | `6935aa38855553bdd8f8415a0765cd874acadf14` | 0 |
| `codex/FEAT-CREATE-2` | `8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7` | 0 |
| `codex/FEAT-CREATE-4` | `f2c66ff262299f20292d8ca92cf8c2a28abce75b` | 0 |
| `codex/P02-build-preflight` | `4b54f304dc201d129d4ba1c62d0368252e6301b1` | 0 |
| `codex/P02-harness-scope` | `3c3e4687785e65f668f1146052e78c3da074ba99` | 0 |
| `codex/P02-owner-amendment` | `4458b35051dd847ceadad11c332a7e2de3b49512` | 0 |
| `codex/P02-owner-transfer-integration` | `3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff` | 0 |
| `codex/P02-r2-docs-closeout` | `67fdf9c5c577ed44271f64aa8668e3bdb8994a94` | 0 |
| `codex/P04-scope-freeze` | `4e6a8cfd487a181a8a63236dcd69cc72dd00cb6c` | 0 |
| `codex/P19-AC3-1` | `ee5eb786452fe7503b891fe215db234aead7d547` | 0 |
| `codex/P19-UI-FIX-2` | `541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c` | 0 |
| `review/deepseek/P02-preflight-r4-condition-closure-92dc7361` | `92dc7361194f1db8fdf7aff3a15a3d234ae56678` | 0 |
| `review/deepseek/P02-preflight-r5-844aec28` | `844aec282416111310d9a9efcac5bc9e0c6eb451` | 0 |

## 附录 C：当前仍未并入主线的19条分支

| 本地分支 | 对主线独有提交数 | 已验证归档 tag |
|---|---:|---|
| `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | 15 | `archive/agent_antigravity_P02PRE-R1H-H2-COLLECTOR-R3` |
| `agent/antigravity/P22-roundtrip-serialization` | 10 | `archive/agent_antigravity_P22-roundtrip-serialization` |
| `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 3 | `archive/agent_codex_P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` |
| `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 4 | `archive/agent_codex_P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` |
| `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | 3 | `archive/agent_codex_P02PRE-R1H-H2-RUN-INTEGRATION` |
| `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 18 | `archive/agent_codex_P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` |
| `agent/zcode/P02-NEW-TIME-BASELINE` | 60 | `archive/agent_zcode_P02-NEW-TIME-BASELINE` |
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 31 | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` |
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 78 | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` |
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 43 | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` |
| `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | 4 | `archive/agent_zcode_P02PRE-R1H-H2-COLLECTOR` |
| `agent/zcode/T2.2.1-reader-workbench-polish` | 1 | `archive/agent_zcode_T2.2.1-reader-workbench-polish` |
| `agent/zcode/T3.2.1-repair-13` | 64 | `archive/agent_zcode_T3.2.1-repair-13` |
| `codex/P02-hook-cache-isolation-plan` | 7 | `archive/codex_P02-hook-cache-isolation-plan` |
| `codex/P14` | 2 | `archive/codex_P14` |
| `codex/P15-C1-FU2` | 2 | `archive/codex_P15-C1-FU2` |
| `codex/project-roadmap-rebaseline` | 1 | `archive/codex_project-roadmap-rebaseline` |
| `review/deepseek/M2-C1-typed-ipc-7d908a5` | 4 | `archive/review_deepseek_M2-C1-typed-ipc-7d908a5` |
| `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 1 | `archive/review_deepseek_M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` |

## 附录 D：50 个目录删除中16个非主线 HEAD 的归档覆盖

| 被删目录 | 原完整 HEAD | 对主线独有提交 | 经核验 bundle 的 tag 覆盖 |
|---|---|---:|---|
| `C:/Users/49745/.codex/worktrees/P02-hook-cache-review-dsh-r4` | `ceca2446da88df23a719f40868cc89e1481ccb2c` | 7 | PASS：`archive/codex_P02-hook-cache-isolation-plan` |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-codex` | `c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d` | 13 | PASS：`archive/agent_codex_P02PRE-R1H` |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-attempt4-antigravity` | `c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427` | 2 | PASS：`archive/agent_antigravity_P02PRE-R1H-R6-A4` |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-zcode` | `256e3ea622cba7a658020ddcf015b18894d88b38` | 7 | PASS：`archive/agent_antigravity_P02PRE-R1H`<br>`archive/agent_codex_P02PRE-R1H`<br>`archive/agent_zcode_P02PRE-R1H` |
| `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `60d47991baea777996313d2cf1a335c136fb1ba0` | 2 | PASS：`archive/dsh_GOV-PIN-LINEAGE-1` |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | `c96958172de8f8a3f3563da43a9fef09ac4447ba` | 3 | PASS：`archive/codex_FEAT-CREATE-1` |
| `G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract` | `86013b34da52e106ad55afc035792e9340c5aee8` | 16 | PASS：`archive/agent_codex_M2-C1-typed-ipc-contract` |
| `G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r2-7e65f4f` | `5386744720061d1e411356d2004c5e3ae6ccb6fd` | 12 | PASS：`archive/review_deepseek_M2-C1-typed-ipc-r2-7e65f4f` |
| `G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r3-4d66523` | `ac38dede84ff22290c9b9d579c1372c8184a7bd5` | 14 | PASS：`archive/agent_codex_M2-C1-typed-ipc-contract`<br>`archive/review_deepseek_M2-C1-typed-ipc-r3-4d66523`<br>`archive/review_qoder_M2-C1-typed-ipc-r3-4d66523` |
| `G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523` | `1950a23619ae489ecc88209593eac75546d61105` | 15 | PASS：`archive/review_qoder_M2-C1-typed-ipc-r3-4d66523` |
| `G:/CODEX/New Manga.worktrees/M2-I1-zcode` | `8dab0abbc667e09054616d4f0b0f5a76b1a04d9e` | 1 | PASS：`archive/agent_zcode_M2-I1-core-assembly-seam` |
| `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a` | `78faeee583600c51740200efd0e05776d6f2cf96` | 3 | PASS：`archive/master` |
| `G:/CODEX/New Manga.worktrees/P02-fallback-scope-codex` | `0b95c6a1024f89ae341c637c0d531611175acdc5` | 1 | PASS：`archive/codex_P02-fallback-scope` |
| `G:/CODEX/New Manga.worktrees/P02-hook-cache-review-dsh` | `09d592a09a7c54fe64ed305e15fce5db3591109b` | 6 | PASS：`archive/codex_P02-hook-cache-isolation-plan` |
| `G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7` | `0a25ceb4577158d9dff184776ff4599e74e25c57` | 2 | **FAIL：无 ref、无已核验 bundle 覆盖** |
| `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh` | `c2bde356554c37520bd87d0bc13791a748250133` | 1 | PASS：`archive/agent_deepseek_M2-PACKAGED-AC1-DLL-DIAG` |

## 审查结束只读边界复核

写入前及写入后均已实际核对：HEAD、全部 refs 的名称/目标摘要、worktree 注册摘要、Git index SHA 与本轮开始一致。将写后 status 中仅本报告的新增项剔除复算，所得摘要也与下列基线完全一致。tracked dirty / staged 仍为 0 / 0；本轮未发现审查对象或 Git 元数据漂移。

| 项 | 审查基线 SHA-256 |
|---|---|
| 全部 refs（refname + objectname） | `06911f912060799e86873c6fad0bd16f9c39ea86c6780ca68d0a55a0d1e40be5` |
| worktree porcelain（剥除首尾换行） | `96265d16e1e245a1cb9e7c3c44ecfc05ee0ee047c8aa3bb5165276f9208b5a05` |
| .git/index 原始字节 | `943bff423489203ce70661c2348f406f6ea498abb735b2104e556961a2532850` |
| status -uall（剥除首尾换行；交付时剔除本报告项） | `1f862da1f39b0aa1bd45095bf4d33c44f5a296675e3588899dbf5e2ccbac0193` |

报告是新增未跟踪文件，写后实测 -uall 为 1593、默认折叠 status 为 1237；26 个 Task 草稿的路径集合不变。该新增不影响「0 tracked dirty / 0 staged」，没有提交报告。

**交付时治理检查为 PASS (4 warnings)，不能写成仍为 3 warnings。** 报告写入后再次执行显式 TaskPath 校验，exit 0；前三条与写入前一致，唯一新增项原文为：

~~~text
Shell: PowerShell
Command: pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md
WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\codex-review-r208.md
Governance check: PASS (4 warnings)
EXIT: 0
~~~

原因是本独立 Review 尚未被当前 Task 的证据表登记，检查器按未登记文件报告；不是新发现的产品测试失败。本轮只准写本报告，不能为消除 warning 越界修改 Task、迁移报告或改检查器。建议 Owner 在后续获准的元数据维护窗口登记本次固定 head 的 Review 与其 SHA，再复核 warning；本报告不预先声称该后续动作已完成。


