---
task_id: GIT-CLEAN-PUBLICATION-1
verifier: verifier-gcp1-close
verifier_kind: subagent
verifier_source: DSH 子 agent `verifier-gcp1-close`（父 agent `lead`；独立上下文，未参与该 Task 的实现、诊断、返修、收口或 push）
verified_head: 529febcf9609a5450c1d1aa03808aa40dfadf25e
verified_head_short: 529febcf9
verified_branch: main
verified_worktree_clean: true
verified_at: 2026-11-17T17:00:42+08:00
timezone: Asia/Shanghai
verify_kind: closeout-execution-verification
decision: ACCEPTED_WITH_FINDINGS
p0: 0
p1: 1
p2: 2
p3: 3
---

# 收口验证：GIT-CLEAN-PUBLICATION-1 @ `529febcf9`

> 本验证只核对 **CP-1…CP-6 是否被正确执行、终态是否自洽、AC4/AC5 是否未被绿洗**。
> **本验证不构成产品发布验收**（见 §7）。

## 0. 身份、范围与只读边界

- **验证者**：`verifier-gcp1-close`（DSH 子 agent，父 agent `lead`）。**独立上下文**，未参与 `GIT-CLEAN-PUBLICATION-1` 的实现、诊断、返修、push 或本轮收口；与作者 Codex、复核者 `reviewer-gcp1` 均非同一会话。
- **被验证 head**：`529febcf9609a5450c1d1aa03808aa40dfadf25e`（`main`），parent = `1a855c27eb64cbbdf12f62e4cd5404392e4c4433`。验证开始时 `git status --porcelain` 为空（工作区干净），提交列表仅 4 个 `doc/` 文件。
- **被验证对象**：`doc/tasks/GIT-CLEAN-PUBLICATION-1.md`（终态卡）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/reviews/GIT-CLEAN-PUBLICATION-1-REASSIGNED-REVIEW-2026-11-17.md`（收口依据）、`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/RESOURCE-MANIFEST.json`、`verification/GIT-CLEAN-PUBLICATION-1/**`（只读复算）、候选仓 `source-export-r{1,2,3,4}` 与 `publish/clean-snapshot-20261026`、`publish/clean-snapshot-20261102`。
- **只读声明**：除写入本报告外，未修改任何文件；未提交、未推送、未 checkout、未清理/移动任何资源；未改动 `verification/**`、候选仓、publish 副本、Task 卡或 STATUS/PLAN/LEDGER。所有命令均为读操作（`git show/diff/cat-file/rev-parse/ls-files/rev-list`、`Get-FileHash`、`Test-Path`、`Get-ChildItem`、`check.ps1`、`task_ledger.py --diff`）。
- **方法**：先核 head/工作区与提交边界，再按 CP-1…CP-6 逐项重跑可复算量（sha256、路径存在性、门禁、指针解析、限制条数），最后比对卡面文字与实际字节。卡面数字与实测不符时一律以实测为准并写明命令。

## 1. 结论摘要

**decision: `ACCEPTED_WITH_FINDINGS`。**

- CP-1…CP-6 在**实质内容上全部执行**：收口依据已写入卡面；Resource Manifest 12 行全部落地为真实路径/处置且无“待生成”占位；STATUS 指针 `e8147c6c` 可解析、PLAN 已移出表外节点、LEDGER 已按脚本重生成；L-1…L-12 共 12 条齐备且可核；终态为 `closed_with_limitations`，**AC4/AC5 原始行字节未改、未改 MET、无绿洗**；`verification/` 无任何改动。
- **但收口提交在本轮新增的 `## Closeout Record` 与 L-1…L-12 两段中引入了字节损坏**（17 处“反斜杠 + 控制/换行字节”，106 个反斜杠取代反引号），损坏了 `e34a90d`、`e8147c6c`、`verification`、`test_assets`、`rust-default-parallel-r2` 等标识符，并**回归**了已 `done` 的 `DOC-CTRLCHAR-FIX-1` 的“TAB=0、孤立 CR=0”残留指标（P1，F-01）。这属于可在不改任何判定/标记的前提下修复的文档字节缺陷，故不判 REJECTED，但必须在下一提交修复，不得把当前字节当作干净终态。
- 另有 2 条 P2 可核性缺口（Resource Manifest 3 行指向的 manifest 不含其摘要；卡面文件/字节数是 manifest 口径、排除 `.git/`）与 3 条 P3 说明项。

## 2. CP-1…CP-6 判定表

| CP | 要求（来源：复核报告 §6 / 卡面） | 判定 | 关键实测 |
|---|---|---|---|
| **CP-1** | 新增 `## Closeout Record` 写明收口依据：交付目标（固定 SHA + push 记录）已完成；AC4 前端/Rust 属 AD-002 已取代的 Tauri/React 旧栈；Python Core 仍属当前架构、其 3 项环境失败仍作 limitation；不得改 AC4/AC5 为 MET | **执行**（内容正确；段内字节受损见 F-01） | 卡面 L253-264 存在 `## Closeout Record`；明写“该目标已由 `e34a90d…` 与 2026-10-25/26、2026-11-02 推送记录完成”“AC4 前端/Rust 属已被 AD-002 取代的 Tauri/React 旧栈”“Python Core 仍属当前架构，其 3 项 Hook 失败仍作为 limitation 保留”“不置 done、不宣称产品发布验收”；依据可核：`AGENTS.md:54`、AD-002 `Status: ACCEPTED_TARGET_ARCHITECTURE` |
| **CP-2** | Resource Manifest 实际核销：行内写真实 destination/处置，全部 `PRESERVE_REFERENCED`（材料为 `PRESERVE_USER_DATA`）；`resource_closeout_status: complete`；不留“待生成” | **执行（有缺口）** | 12 行；11 行 destination 实测存在、仅第 12 行 `exchange` 为 `NOT_APPLICABLE`/`—`；manifest 存在且 sha256 与卡面一致；frontmatter `resource_closeout_status: complete`；表内无“待生成”。缺口：F-02（3 行摘要不可复算）、F-03（计数为 manifest 口径） |
| **CP-3** | STATUS `clean-snapshot-20261026` 更正为可解析 head；PLAN 把本卡移出“表外节点”；LEDGER 反映终态 | **执行（口径说明见 F-04）** | `doc/STATUS.md:22` 现为 `clean-snapshot-20261026`=`e8147c6c`；`git cat-file -t e8147c6c` → `commit`（`e8147c6c8a7edde4e5784999454acb5732a869fb`）；PLAN L61 表外节点已不含本卡；LEDGER `closed_with_limitations` 65→66、本卡已从非终态表移除，`task_ledger.py --diff` 复算与提交一致 |
| **CP-4** | 卡面 `reviewer:` 改为 `reviewer-gcp1` 并写明 subagent 来源；改写历史 Review 字节 | **执行** | frontmatter `reviewer: reviewer-gcp1（DSH 子 agent，独立上下文…）`；卡面 L234-243 有改派 Appointment 段；`antigravity-review-push-r1.md` 与 `dsh-review-r1.md` 未被本提交改动（`git diff … -- verification/` 为空） |
| **CP-5** | 把 L-1…L-12 共 12 条限制写入卡面，每条保留可核文件/命令；不得改弱 AC4/AC5 标记 | **执行（段内字节受损见 F-01）** | 卡面 L266-282 恰 12 条，编号 L-1…L-12 连续；抽查 L-1/L-4/L-7/L-9/L-10/L-11 全部与证据一致（§3.5） |
| **CP-6** | 只置 `closed_with_limitations`，不得置 `done`，不得宣称发布验收/Gate 通过 | **执行** | frontmatter `status: closed_with_limitations`；卡面明写“不置 done”“不宣称产品发布验收或 Gate 通过”；AC4 仍 `<<BLOCKED: …>>`、AC5 仍 `<<PARTIAL: …>>` |

## 3. 逐项实测证据

### 3.1 提交边界（历史证据字节）

```
$ git show 529febcf9 --stat --format='commit %H%nparents %P%nsubject %s'
commit 529febcf9609a5450c1d1aa03808aa40dfadf25e
parents 1a855c27eb64cbbdf12f62e4cd5404392e4c4433
subject docs(tasks): 收口 GIT-CLEAN-PUBLICATION-1 为 closed_with_limitations（CP-1/2/3/5 执行完毕）
 doc/REBASELINE_PLAN.md               |  2 +-
 doc/STATUS.md                        |  2 +-
 doc/TASK_LEDGER.md                   | 13 ++++----
 doc/tasks/GIT-CLEAN-PUBLICATION-1.md | 62 ++++++++++++++++++++++++++++++------
 4 files changed, 61 insertions(+), 18 deletions(-)

$ git diff --name-status 529febcf9^ 529febcf9 -- verification/
（空输出，exit 0）
```

结论：本收口提交**只**改 4 个 `doc/` 文件，**没有修改 `verification/` 下任何既有文件**；4 个路径均在卡面 `allowed_paths` 内。

### 3.2 CP-2：Resource Manifest 与 manifest 摘要

| 行 | resource_type | disposition | destination 实测 | 结果 |
|---|---|---|---|---|
| 1 | worktree | `PRESERVE_REFERENCED` | `G:/CODEX/New Manga` | EXISTS |
| 2 | task-env（整体） | `PRESERVE_REFERENCED` | `…/task-envs/GIT-CLEAN-PUBLICATION-1` | EXISTS |
| 3 | source-export（r1） | `PRESERVE_REFERENCED` | `…/source-export` | EXISTS |
| 4 | source-export（r2/r3/r4） | `PRESERVE_REFERENCED` | `…/source-export-r4` | EXISTS |
| 5 | build-cache | `PRESERVE_REFERENCED` | `…/cargo-target` | EXISTS |
| 6 | test-env（rust） | `PRESERVE_REFERENCED` | `…/rust-check-environment` | EXISTS |
| 7 | test-env（core） | `PRESERVE_REFERENCED` | `…/core-check-environment` | EXISTS |
| 8 | test-env（pytest） | `PRESERVE_REFERENCED` | `…/pytest-temp-4353953f…` | EXISTS |
| 9 | review-package | `PRESERVE_REFERENCED` | `…/review-package` | EXISTS |
| 10 | task-env（DIAG） | `PRESERVE_REFERENCED` | `…/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1` | EXISTS |
| 11 | user-material | `PRESERVE_USER_DATA` | `G:/CODEX/New Manga/.tmp.driveupload` | EXISTS（2,148 文件） |
| 12 | exchange | `NOT_APPLICABLE` | `—` | 允许的 `—` 行（唯一一行） |

manifest 摘要（独立重算）：

```
$ (Get-FileHash '…/task-envs/GIT-CLEAN-PUBLICATION-1/RESOURCE-MANIFEST.json' -Algorithm SHA256).Hash
654a7d8eb159e7686b42823d228829b635507093a0c7d12237a1198b7ff28d0f   ← 与卡面 L145 完全一致（match=True）
```

manifest 自身口径（`schema=resource-manifest/1`，`generated_at=2026-11-17 16:45:41`）：`resources=16`、`total_file_count=28,920`、`total_bytes=3,898,062,555`、`sum(bytes)` 与 `sum(file_count)` 均等于汇总值 —— 与卡面 L145/L150 的“16 目录 / 28,920 文件 / 3,898,062,555 B”**完全一致**。

门禁（原样输出）：

```
$ pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\GIT-CLEAN-PUBLICATION-1.md
WARN: 存在 7 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6786 bytes / 64 lines
Governance check: PASS (3 warnings)
EXITCODE=0
```

补充：`git status --porcelain --ignored` 不在本验证范围；`check.ps1` 的 PASS 只说明机械条件成立，不代表本验证结论。

### 3.3 CP-3：指针

```
$ git cat-file -t e8147c6c        → commit（exit 0）
$ git rev-parse e8147c6c          → e8147c6c8a7edde4e5784999454acb5732a869fb
$ git -C publish/clean-snapshot-20261026 rev-parse HEAD → e8147c6c8a7edde4e5784999454acb5732a869fb（tracked=875）
```

- **STATUS**：L22 `push \`clean-snapshot-20261026\`=\`e8147c6c\`、\`clean-snapshot-20261102\`=\`ac7d488e\``。`e8147c6c` 可解析；历史不可解析值 `892b946e` 已不在 STATUS（该改正发生在更早提交，非 529febcf9）。
- **PLAN**：L61 表外节点 = `GIT-CLEAN-PUBLICATION-DIAG-1、GIT-CLEAN-RUST-ISOLATION-1、GIT-CLEAN-CORE-ENV-2、INSTALLER-MATRIX-1`，**已不含本卡**（diff 只删本卡一项）。
- **LEDGER**：`closed_with_limitations 65 → 66`、`non-terminal 8 → 7`、本卡从非终态表移除；`python -B tools/governance/task_ledger.py --diff` 复算输出（666 / 658 / 7 / 66 / in_review=1）与提交文件逐项一致，**可复现**。台账按设计只列非终态 Task，故没有本卡的逐卡行（见 F-04）。
- 附注：STATUS 的 `clean-snapshot-20261102`=`ac7d488e` 在主仓对象库不可解析（`git cat-file -t ac7d488e` → exit 128），但在 `publish/clean-snapshot-20261102` 可解析（HEAD 即 `ac7d488e1944…`，tracked 1413）——与复核报告“至少一个本地对象库可解析”的口径一致（见 F-05）。

### 3.4 无绿洗：AC 原始行字节

```
AC4 行 sha256 = 71d533cf8676073f9b2b2f18144909a7d862c9328a3145e9929c95cab46c4517
AC5 行 sha256 = 363336447ab8870c8a298e1ec18561da355d5f3695580e6651055e9e54061036
与 529febcf9^ 同两行逐字节比较：identical=True / identical=True
```

- AC4 仍为 `- [ ] **AC4**：… <<BLOCKED: Core三组参数失败且旧icacls错误码未知，默认并发registry失败复现，packaged以诊断记录为准>>`。
- AC5 仍为 `- [ ] **AC5**：… <<PARTIAL: DSH r1独立Review为blocked，补充证据不等于批准push或Task完成>>`。
- F-02 的更正以**追加段**（L46-49 的 blockquote）存在，原 AC5 行未被改写；追加段自述“标记不变，不得改 MET”。
- 全文 `<<MET>>` 仅出现在 AC1/AC2/AC3 行；AC4/AC5 行无 MET 字样；L240 判定段明写“AC4 `<<BLOCKED>>` 与 AC5 `<<PARTIAL>>` 如实、不得改 MET”。

### 3.5 CP-5：12 条限制与抽查

`L-1…L-12` 计数：`limit_count=12`，编号连续（1..12），无缺号、无重复。

| 抽查 | 卡面陈述 | 独立实测 | 判定 |
|---|---|---|---|
| **L-1** | Core 771 passed / 3 failed（同一参数化用例 3 组参数）；r4 默认并发 151/2/1/12 exit 101；packaged 12/0/154 exit 0 | `verification/GIT-CLEAN-PUBLICATION-1/core-tests-r2.log` 尾 = `3 failed, 771 passed, 1 warning in 49.64s`；`rust-tests-r4-serial.log` 尾 = `153 passed; 0 failed; 1 ignored; 12 filtered out`；`frontend-tests-r3.log` 尾 = `Tests  435 passed (435)` | 与卡面/复核一致 |
| **L-4** | `verification/GIT-CLEAN-PUBLICATION-1/` 有 19 个原始 `.log`，无 EXIT/shell/venv 头 | `Get-ChildItem -Filter *.log` = **19**；`Select-String '^EXIT|^exit=|Exit code|EXITCODE'` 命中 **0** | 一致 |
| **L-7** | 收口时仍未做现场 `ls-remote`（复核时 proxy 失败 exit 128），远端只能间接核验 | 复核报告 §5.3 原文：`NOT_VERIFIABLE：proxy 连接失败 exit 128`；本验证**未重试远端查询**，保持该限制 | 一致（保持 NOT_VERIFIABLE） |
| **L-9** | 2026-10-26 卡面 `test_assets(81)` 与实测 86 不符；283+243+226+81+18+14+5=870≠875；总量 875 正确 | `git -C publish/clean-snapshot-20261026 ls-files -z`：tracked=**875**，顶层 = apps 283 / src 243 / tests 226 / **test_assets 86** / packaging 18 / tools 14 / 根文件 5；283+243+226+86+18+14+5 = **875** | 一致（卡面 81 确为错值） |
| **L-10** | `SOURCE_MANIFEST.json` 的 `generated_files[5]`（`experiments/TASK-016/samples/manifest.json`）缺 `generator`；其余 5 项有 | Python 读取 `source-export-r4/SOURCE_MANIFEST.json`：`generated_files=6`，index 0-4 均含 `generator=experiments/TASK-016/generate_samples.py`，index 5 无 `generator` | 一致 |
| **L-11** | Core 771/3 实测于 r2 `b1e6935`、前端 435 实测于 r3 `87accae`，非 e34 同 head 重跑；绑定依赖 tree 等价 `src=1571a2ca84…`、`tests/core=da2f41fb16…`、`apps/desktop/frontend=662ad099f9…` | r2/r3 中 `b1e6935`、`87accae` 均为 commit；`e34:src`=`1571a2ca84e7…`、`e34:tests/core`=`da2f41fb16feb…`、`e34:apps/desktop/frontend`=`662ad099f9a7…`；r2.b1e6935 三个 tree 全部相同；r3.87accae 三个 tree 全部相同 | 一致 |

### 3.6 其余可复算量（支撑“终态自洽”）

- **Canonical Evidence 59 行**：`EV 9 + SRC 37 + SUP 3 + DB 3 + DISP 5 + PUSH 2 = 59`；用 `Get-FileHash -LiteralPath` 逐行重算 → **MATCH=59 / MISMATCH=0 / MISSING=0**（与卡面 L255、复核报告 §3.1 一致）。
- **候选 r4**：`HEAD=e34a90d001cce1fa966aec7d2b032bb5ad1cf148`、`tracked=733`、`remote -v` 空、root commit 数=1、`rev-list --count HEAD=1`、commit 无 parent。
- **候选 r1**：`HEAD=9ee673f9a776583531e21853e00670d4c9d3f65e`（卡面“首版 9ee673f9a 保留不推送”一致）。
- **push-gate Review**：`verification/GIT-CLEAN-PUBLICATION-1/antigravity-review-push-r1.md` frontmatter `decision: approved`、`reviewed_head: e34a90d…`；`doc/PUSH_RECORD_2026-10-25.md` 存在 —— 支撑 F-02 追加段的理由更正。
- **材料根**：`.tmp.driveupload` = **2,148** 个文件、**131,654,202 B**；文件为 `78 01`（zlib）压缩外层 blob，无任何 JPEG/PNG/GIF/WebP 魔数；`audit/V1-FULL-AUDIT/evidence/push-material-disposition.json` 的 `objects`=**169**，每个对象含 `outer_object` + `embedded_git_object` 两个 ID（合计 **338** 个禁止对象 ID），`outer_path` 全部位于 `.tmp.driveupload/`。卡面“169 个私有 JPEG / 338 个禁止对象 / 2,148 项”在**内容口径**上成立（见 F-06 的措辞说明）。

## 4. Findings

### P0（0）

无。

### P1（1）

**F-01｜P1｜收口提交在新增收口段引入控制字符/字节损坏，回归 `DOC-CTRLCHAR-FIX-1` 残留指标**

- **位置**：`doc/tasks/GIT-CLEAN-PUBLICATION-1.md` L253-282（`## Closeout Record` 与 L-1…L-12 两段）。
- **实测**：
  - HEAD 卡面含 **17 处**“反斜杠 + 控制/换行字节”：`0x1B`(ESC)×5、`0x0B`(VT)×3、`0x07`(BEL)×2、`0x08`(BS)×2、`0x09`(TAB)×2、`0x0D`(CR)×2、`0x0A`(LF)×1；同样是这些段内共 **106 个反斜杠**（本卡其余部分 0 个）取代了反引号。
  - 父提交 `529febcf9^` 的同一文件控制字符数 = **0**；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 本提交均为 0 ⇒ 损坏**由本提交引入**，且仅限上述两段。
  - 受损标识符（首字母/字母被吃掉或被换行截断）：`e34a90d…`→`"34a90d…"`、`e8147c6c`→`"8147c6c"`（2 处）、`verification/`→`"erification/"`（2 处）、`review-package-r2`→`"eview-package-r2"`（CR 断行）、`rust-default-parallel-r2`→`"ust-default-parallel-r2"`（CR 断行）、`venv=UNRECORDED`→`"env=UNRECORDED"`、`node_modules`→`"ode_modules"`（LF 断行）、`ac7d488e`→`"c7d488e"`、`test_assets`→`"est_assets"`、`experiments/`→`"xperiments/"`、`b1e6935`→`"1e6935"`、`tests/core`→`"ests/core"`、`apps/desktop/frontend`→`"pps/desktop/frontend"`、`b1c1f5a5`→`"1c1f5a5"`。
  - 复现命令：`$b=[IO.File]::ReadAllBytes('doc/tasks/GIT-CLEAN-PUBLICATION-1.md')`；`[regex]::Matches($t,"\\[\x00-\x1F]").Count` → `17`；对父版本同命令 → `0`。
- **受影响面**：`check.ps1` 仍 PASS（它不扫描控制字符），因此该缺陷不会被门禁拦住；但 `DOC-CTRLCHAR-FIX-1`（`status: done`）的残留 AC 已写明“TAB=0、孤立 CR=0”，本提交使 `doc/tasks` 重新出现 TAB×2、孤立 CR×2 及 12 个其他 C0 字节（ESC×5、VT×3、BEL×2、BS×2），并注入 1 个断行 LF，属于**对已关闭卫生卡的回归**；同时这些字节正是 CP-1（收口依据）与 CP-5（限制清单）要求的正文，读者复制 `e34a90d`/`e8147c6c`/`test_assets` 等会拿到错误文本。
- **建议修复（不弱化任何断言）**：用追加式 errata 或独立的“字节修复”commit 只把 `\`+控制字符还原为反引号/原字母（**不得**改 AC1-AC5 行、不得改 L-1…L-12 的语义与数值、不得改任何 Review 或 `verification/**` 字节）；修复后在 `DOC-CTRLCHAR-FIX-1` 或新卡登记“doc/tasks 控制字符回归已清零”。本 P1 不改变 `closed_with_limitations` 终态，也不要求改 AC4/AC5 标记。

### P2（2）

**F-02｜P2｜12 行 Resource Manifest 中 3 行的 `sha256/manifest` 指向的 manifest 不含该行摘要，只能核到路径存在/计数**

- **位置**：卡面 L149（worktree）、L158（DIAG task-env）、L159（user-material）；对应 `RESOURCE-MANIFEST.json`。
- **实测**：manifest 的 16 个 `resources` 全部是 `GIT-CLEAN-PUBLICATION-1` task-env **内部**目录（cargo-target、core/rust-check-environment*、pytest-temp*、review-package*、source-export*、empty-hooks），**不含**主仓 `G:/CODEX/New Manga`、不含 `GIT-CLEAN-PUBLICATION-DIAG-1`、不含 `.tmp.driveupload`。因此这 3 行的 `sha256/manifest` 列无法从该 manifest 复算出本行摘要；可独立核实的只有 `Test-Path` 与（第 11 行）`2,148` 项计数。
- **影响**：CP-2 的“每行 disposition/destination/sha256 可验证”对 8 行成立、对 3 行只成立到“路径存在”；对最重要的用户素材（169 个嵌入 JPEG / 338 个禁止对象 ID）没有在 Resource Manifest 行内给出可复算摘要（审计侧 `push-material-disposition.json` 仍有 payload sha256，但卡面未引用）。
- **建议**：在 Resource Manifest 行内为 worktree / DIAG / user-material 补独立摘要或不歧义地写“摘要见 `<另一 manifest>`”；或扩展 `RESOURCE-MANIFEST.json` 覆盖这三处。属证据补强，不需要改处置（仍为 PRESERVE）。

**F-03｜P2｜卡面“28,920 文件”是 manifest 口径（排除 `.git/`），与磁盘实测 32,454 文件不同；manifest 不 attest 候选 `.git` 对象库**

- **位置**：卡面 L145/L150；`RESOURCE-MANIFEST.json`。
- **实测**：4 个 `source-export*` 目录下 `.git/` 内文件数分别为 874 / 884 / 887 / 889（合计 **3,534**）；manifest 的 16 个目录在磁盘上的实际文件总数 = **32,454**，而 manifest/卡面口径 = **28,920**（差额恰为 `.git/` 内部文件）。manifest 的 `note` 与字段只说明“目录原地保留 + `(相对路径, 长度, sha256)` 汇总”，未写“排除 `.git/`”。
- **影响**：卡面数字**与 manifest 自身完全一致**（不是算错），但读者会把它当作磁盘全量；被排除的恰是候选仓对象库——CP-2 核销的重要内容载体。候选对象库的完整性另有 AC3 证据（733 tracked、fsck、无 remote、59 项 pin）支撑，故不提升为 P1。
- **建议**：在卡面/manifest note 明示“文件数/字节数不含 `.git/`”，或另附候选 `.git` 目录摘要。

### P3（3）

**F-04｜P3｜`doc/TASK_LEDGER.md` 没有本卡的逐卡行，CP-3 的“显示 closed_with_limitations”只能间接核**

- 台账由 `tools/governance/task_ledger.py --write` 生成，按设计只列非终态 Task；本卡终态化后表现为 `closed_with_limitations` 计数 65→66 + 从非终态表移除。脚本 `--diff` 复算与提交一致（可复现），且脚本头注明“Do not edit by hand”，故不属实现缺陷；仅提示 CP-3 的字面要求在台账层面无法逐卡显示。

**F-05｜P3｜`doc/STATUS.md` 的 `clean-snapshot-20261102`=`ac7d488e` 在主仓对象库不可解析**

- `git -C "G:/CODEX/New Manga" cat-file -t ac7d488e` → `fatal: Not a valid object name`（exit 128）；在 `publish/clean-snapshot-20261102` 内 → `commit`，HEAD=`ac7d488e1944…`（tracked 1413）。该值不在 CP-3 的改正范围（CP-3 只要求 20261026），复核口径接受“至少一个本地对象库可解析”；作为 P3 记录，避免读者在主仓直接 `cat-file` 失败时误判记录错误。

**F-06｜P3｜Resource Manifest 第 11 行“169 个私有 JPEG”是内容级表述，不是文件级**

- `.tmp.driveupload` 内 2,148 个文件全部以 `78 01`（zlib）开头，JPEG/PNG/GIF/WebP 魔数命中数为 **0**；169 个 JPEG 是这些压缩外层 blob 内嵌的 payload（审计 `push-material-disposition.json`：`objects=169`，每个含 outer + embedded 两个对象 ID = 338 个禁止对象 ID）。行文“169 个私有 JPEG / 338 个禁止对象 / 实测存在（2,148 项）”在审计口径下成立，但“JPEG 文件”易被误读为目录内直接存在 169 个 `.jpg`；建议改写为“169 个嵌入 JPEG（压缩外层 blob 2,148 个）”。不影响处置（仍 `PRESERVE_USER_DATA`）。

## 5. 实测命令与关键数值汇总

| 项 | 命令/方法 | 实测值 | 卡面值 | 一致 |
|---|---|---|---|---|
| head | `git rev-parse HEAD` | `529febcf9609a5450c1d1aa03808aa40dfadf25e` | — | ✔ |
| 工作区 | `git status --porcelain` | 空 | — | ✔ |
| 收口提交文件 | `git diff-tree --name-status -r 529febcf9` | 4 个 `doc/` 文件 | — | ✔ |
| `verification/` 改动 | `git diff --name-status 529febcf9^ 529febcf9 -- verification/` | 空（exit 0） | 未改 | ✔ |
| Canonical Evidence | `Get-FileHash` × 59 | MATCH 59 / MISMATCH 0 / MISSING 0 | 59 行全部 MATCH | ✔ |
| manifest sha256 | `Get-FileHash RESOURCE-MANIFEST.json -Algorithm SHA256` | `654a7d8eb159e7686b42823d228829b635507093a0c7d12237a1198b7ff28d0f` | 同值 | ✔ |
| manifest 汇总 | `ConvertFrom-Json` 求和 | 16 目录 / 28,920 文件 / 3,898,062,555 B | 同值 | ✔ |
| 磁盘全量（同 16 目录） | `Get-ChildItem -Recurse -File -Force` | 32,454 文件（含 `.git/` 3,534） | 28,920（manifest 口径） | 口径差异（F-03） |
| Resource Manifest 行 | `Test-Path -LiteralPath` × 12 | 11 EXISTS + 1 `NOT_APPLICABLE`/`—` | 12 行 | ✔ |
| check.ps1 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | `PASS (3 warnings)`，exit 0 | 期望 PASS | ✔ |
| STATUS 指针 | `git cat-file -t e8147c6c` / `git rev-parse e8147c6c` | `commit` / `e8147c6c8a7edde4e5784999454acb5732a869fb` | `e8147c6c` | ✔ |
| PLAN 表外节点 | `Select-String GIT-CLEAN-PUBLICATION doc/REBASELINE_PLAN.md` | 本卡已不在表外节点 | 已移出 | ✔ |
| LEDGER | `task_ledger.py --diff` / diff | `closed_with_limitations` 66；非终态 7；本卡已移出 | 应反映终态 | ✔（F-04） |
| 限制条数 | `[regex] '^\s*\d+\.\s+\*\*L-(\d+)｜'` | 12（1..12） | 12 | ✔ |
| AC4/AC5 原行 | SHA-256 + 与父提交逐字节比较 | 未变（identical=True） | 未改、非 MET | ✔ |
| Core 测试 | `core-tests-r2.log` 尾 | `3 failed, 771 passed` | 771/3 | ✔ |
| Rust 串行 | `rust-tests-r4-serial.log` 尾 | `153 passed; 0 failed; 1 ignored; 12 filtered out` | 153/0/1/12 | ✔ |
| 前端 | `frontend-tests-r3.log` 尾 | `Tests 435 passed (435)` | 435 | ✔ |
| 原始日志数 | `Get-ChildItem -Filter *.log` | 19；EXIT 头命中 0 | 19 个无头 | ✔ |
| 快照 875 | `git -C publish/clean-snapshot-20261026 ls-files -z` | 875；test_assets 86 | 875 总量 / 81 分项（L-9） | ✔（L-9 成立） |
| 候选 r4 | `rev-parse/cat-file/remote/ls-files` | `e34a90d…`、733 tracked、1 root、无 remote | 同 | ✔ |
| 候选 r1 | `rev-parse HEAD` | `9ee673f9a776583531e21853e00670d4c9d3f65e` | `9ee673f9a` | ✔ |
| 损坏字节 | `[regex]::Matches($t,"\\[\x00-\x1F]")` | **17 处**；父版本 0；本文件 `\` 共 106 个（全在 L253-282） | — | 缺陷（F-01） |

## 6. 未验证 / 不可验证项

- **远端现场状态**：本验证**未重试** `git ls-remote`；L-7 保持 NOT_VERIFIABLE。远端 refs 只能由本地记录、本地对象库与 publish 副本间接支持，不能写成“远端现场已核验”。
- **删除/迁移为 0**：卡面声明“删除/迁移/归档 0”。本验证能确认的只有“12 个 destination 全部存在 + candidate/publish 副本存在 + `verification/` 未改”；无法回放历史证明期间从未删除过文件，只能与 manifest/复核证据交叉支持。
- **产品级 Gate**：安装包、签名、真实 GUI/模型、完整审计、Core 环境 ACL 等仍 `NOT_RUN`/失败；本验证不重跑这些项，也不改其结论。
- **AC4/AC5 判定**：本验证只确认标记未被改动；**不认同也不建议**把 AC4/AC5 改成 MET。

## 7. 声明

**本验证不构成产品发布验收，也不构成 push 授权、Gate 通过或 Task `done` 的依据。** 本报告只对 `529febcf9` 时点的收口程序执行与终态自洽性负责；`closed_with_limitations` 仍是带限制终态，AC4 保持 `<<BLOCKED>>`、AC5 保持 `<<PARTIAL>>`，L-1…L-12 继续有效。P1/P2 findings 的修复不得改动 AC1-AC5 原行字节、不得弱化任何限制或断言。

---

**验证者**：`verifier-gcp1-close`（DSH 子 agent，独立上下文，未参与实现/收口）
**验证时间**：2026-11-17T17:00:42+08:00（Asia/Shanghai）
**decision**：`ACCEPTED_WITH_FINDINGS`（P0=0 / P1=1 / P2=2 / P3=3）
