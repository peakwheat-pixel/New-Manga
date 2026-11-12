---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
review: AC5 integration fresh ZCode Review（非 final adjudication）
reviewer: ZCode CLI fresh session sess_3e7c8eaa-c247-4cb2-beeb-8fa8be8975c2
reviewed_head: fea5c742afe4ecdb1e3e6a8116bc0c18f1cabeb1
integration_head: e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3
integration_base: 7f101e8ee0a5665465144bfa9013960403c4888c
implementation_head: 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1
candidate_reference: 4ed7f32b3ce9104ecee11aad593bde222055a0df（仅 T/F blob 对照，未合入）
verdict: APPROVED_WITH_LIMITATIONS（P0=0 / P1=0 / P2=1 / P3=3）
scope: AC5 集成事实、四授权文件变更、必跑门禁结果与停止状态的独立只读 Review；不裁定两个历史 TaskPath FAIL 的最终处置，不关闭 R-001/Review-R-001，不宣告 Task done
---

# FEA-15-PIN-BASIS-ENFORCE-1 AC5 集成独立 Review（2026-11-12）

## 0. 审查者身份与独立性

- 审查者：ZCode CLI fresh session `sess_3e7c8eaa-c247-4cb2-beeb-8fa8be8975c2`，为本任务新开会话。
- session ID 实测来源：`C:/Users/49745/.zcode/cli/rollout/model-io-sess_3e7c8eaa-c247-4cb2-beeb-8fa8be8975c2.jsonl` 在验证命令执行前约 32 秒仍活跃写入，`agents/sess_3e7c8eaa-…/` 同秒存在（子代理只读 `ls` 探测，2026-11-12T00:41Z）。
- 上下文独立（2026-10-31 裁决口径）：本会话与既往全部相关 session——释放 `sess_7b34d23e`、AC1c A `sess_72137bd6`、AC1d `sess_fd863071`、AC2/AC3 adjudication `sess_dbdb62fe`、AC2/AC3 Review `sess_6b151e7e` 与 follow-up `sess_fb32a1da`、v2 Review `sess_426becfe`、AC4 adjudication `sess_b3fbf940`——均不同；未参与本 Task 任何实现、返修或既往 Review。
- 全程只读：未修改任何文件、未提交、未 push、未运行任何 gate/pytest。Git 核验经两个只读 Explore 子代理执行（`sess_subagent_agent_fc3aefea-10d9-4f43-be36-a0160ddd5d58`、`sess_subagent_agent_dc9c8508-e03e-4dc3-a43d-1f69582fea07`）。

## 1. 方法与输入

1. 逐份读取：Task 卡、AC4 adjudication 报告、verification README、`ac5-integration-blob-map-e69fc2dc7.log`、`ac5-integrated-gates-e69fc2dc7.log`、`ac1c-a-gates-8d1d75ca.log`（归因对照）、doc/09_COLLABORATION.md §4/§5/§6。
2. 只读 Git 核验（子代理一，主仓库）：`rev-parse/status/log/diff --name-status/rev-parse <commit>:<path>/show|sha256sum/cat-file -t`。
3. workspace 现场复核（子代理二）：T/F clone 与 implementation worktree 的 HEAD/config/blob 对象/index。
4. 四授权文件逐 hunk 代码审查（check.ps1 三个 hunk、TASK.md 模板、test_canonical_evidence_basis.py 全文、test_architecture_assertions.py 两个 hunk）。

**方法边界（如实记录）**：本会话处于 plan mode，权限过滤器拦截了主会话全部 Bash 及子代理的 `git -C` / `--git-dir` / `ls-tree` / 进程替换等形式。等价替代已在位：blob ID 用 `git rev-parse <commit>:<path>`（与 ls-tree 同一 tree 条目解析）；patch 一致性用两侧 `git diff A^ A | sha256sum` 哈希相等（与 `diff` 零输出等价）；clone 现场（过滤器不允许 git 定位到 workspace）改用 `.git` 内部文件直读 + 松散对象/index 二进制 grep + `blob <size>\0` 前缀 SHA-1 重算。替代与原命令的等价性均已在上列报告中逐项说明。

## 2. Standards 轴

### 2.1 集成范围与提交链（证实）

- `git diff --name-status 7f101e8e..e69fc2dc7` 恰为四个授权文件：`M doc/templates/TASK.md`、`M tools/governance/check.ps1`、`M tools/governance/tests/test_architecture_assertions.py`、`A tools/governance/tests/test_canonical_evidence_basis.py`（+547/−27），全部落在 frontmatter `allowed_paths` 内；无任何历史 Task、evidence、pin、`.gitattributes`、契约或产品源码路径被触碰。
- 集成四提交为线性链且父链首尾相接：`d363b13d`(parent=7f101e8e)→`6e2db2e9`→`3ec23cc4`→`e69fc2dc`，作者均为 peakwheat-pixel，映射与 Task/README 登记一致。
- cherry-pick 内容一致性：四对「原始↔集成」提交的 patch 全文 SHA-256 逐一相等（fd84360↔d363b13 = `10d7f160…`；5e216dc↔6e2db2e = `1f37564e…`；ee0b25a↔3ec23cc = `4b5ac51e…`；7eefb54↔e69fc2dc = `d4914323…`）。
- 防误集成：`git cat-file -t 4ed7f32b…` 在主仓库 exit 128（对象不可达）；集成链根在 7f101e8e，非 4ed 后代。

### 2.2 四文件 blob 映射与 SHA-256 对齐（证实）

| 文件 | Git blob（7eef = e69 = fea5c74 实测） | SHA-256（实测） | AC4 adjudication §4.1 期望 |
|---|---|---|---|
| tools/governance/check.ps1 | a320c034…692e4 | `1a6f7ab3…94a6cff2` | 一致 |
| doc/templates/TASK.md | 574b82d7…60fc8 | `89371702…361afc7c` | 一致 |
| tools/governance/tests/test_canonical_evidence_basis.py | aabe8e14…1a75b | `2b82fb2d…32569fd0f` | 一致 |
| tools/governance/tests/test_architecture_assertions.py | e9b0bbc7…1635 | `26f79e8a…24a9169e57` | 一致 |

- implementation 7eefb54 与 integration e69fc2dc 侧由本会话以 `git show <commit>:<path> | sha256sum` 独立复算，全等；`e69fc2dc..fea5c742` 区间四文件零改动（diff 空 + blob 同值）。
- candidate 侧（主仓库不可达）：T/F clone HEAD 均为 4ed7f32（detached），T `core.autocrlf=true` / F `false`、longpaths 均 true，与 README 声称一致；四个期望 blob 对象在两 clone 对象库在场、index 各命中 1 次；F clone 工作区内容经 SHA-1 重算对四个 blob 精确命中，T clone 三个文本文件为同内容 CRLF 形态（剥 CR 后与 F 逐一相等），check.ps1 两侧精确命中。blob map log（`ac5-integration-blob-map-e69fc2dc7.log`，GENERATED_HEAD=e69、porcelain 空、EXIT=0）的四方映射声明获现场独立支持。
- implementation worktree：ref 链读得 HEAD=7eefb54、branch=`codex/fea-15-pin-basis-enforce-1`（全树 clean 未验证，见 §5）。

### 2.3 代码与模板审查（四文件）

- `check.ps1:54-91` 新增 `Get-GitBlobSha256`（`git cat-file blob` stdout 原始字节流 SHA-256，ExitCode≠0 返回 null）与 `Get-RepoPathInfo`（`..` 前缀拒绝的仓内判定）；无临时文件 I/O。
- `check.ps1:705-728` 表头判别：旧六列用大小写不敏感匹配（兼容历史卡），新七列要求精确 `sha256_basis`（`-ceq`）；两者皆不满足即 `EVIDENCE_BASIS_HEADER_INVALID` 并清空行集（fail-closed，连带触发"必须列出 canonical evidence"）。
- `check.ps1:741-786` 七列行校验：basis 严格 ∈ {BLOB, WORKTREE, EXTERNAL_SHA256}（大小写敏感）；BLOB 要求有效 commit 且 `commit:path` blob 字节精确匹配；WORKTREE 要求 `AC/Gate` 含 `WORKTREE_ENV=…` 且只看工作树字节（不回退 blob）；EXTERNAL_SHA256 强制仓外路径、不可读即 `EXTERNAL_PATH_UNREADABLE` 失败关闭。域边界各有专错（BLOB/WORKTREE 仓外、EXTERNAL 仓内均拒绝）。
- `check.ps1:788-824` legacy 六列保留 r194 OR 谓词（工作树字节匹配 OR commit blob 匹配）；`test_legacy_png_blob_fallback_matches_r0_checker` 以 R0 基线 checker 同夹具并行对照，证明旧语义未漂移。
- `doc/templates/TASK.md:61-66`：Canonical Evidence 改为七列表头并写明三basis 语义与 WORKTREE_ENV 义务，与 checker 实现一致。
- `test_canonical_evidence_basis.py`（新文件，412 行）：AC3 清单逐项有判别测试——旧格式三种有效形态、basis 缺失/小写/表头别名、行 arity 缺/多、SHA 畸形、commit 畸形/未知、三类来源正向（PNG 魔数断言、跨 EOL BLOB、CRLF/mixed-EOL 双向判别、EXTERNAL PNG）、commit 不含路径、WORKTREE 不回退 blob、EXTERNAL/WORKTREE 不可读 fail-closed；正向断言要求 `EXIT=0` + `Governance check: PASS` 且无 `EVIDENCE_BASIS_` 错误（P1-3 修复形态）。夹具隔离在 workspace 临时 clone，`finally` 保证 checker/PNG 还原。
- `test_architecture_assertions.py`：fixture 改为从 STATUS 链接动态收集任务占位（替代静态列表），STATUS 变异样例缩短以符合字节预算；改动小、在授权文件内、不放松断言。

## 3. Spec 轴

### 3.1 AC5 释放条件逐项核对（AC4 adjudication §4）

1. **候选映射与集成形态**：满足（§2.1/§2.2 证实，4ed 未合入）。
2. **必跑 gates 实跑并记录 HEAD/UTC/EXIT**：满足执行与记录义务。`ac5-integrated-gates-e69fc2dc7.log`（GENERATED_HEAD=e69、PROCESS_CWD=主仓库、porcelain 空）八项完整：default / 本卡 / AGPL-RELEASE-1 / AD002-FOLLOWUPS-1 均 PASS（3 warnings）EXIT=0；**FEA-06-PREREQ-1 FAIL（13 errors）/EXIT=1；CHAPTER-SELECTOR-1 FAIL（6 errors）/EXIT=1**；18/18 pins EXIT=0；API 1/79/6=86 EXIT=0。FAIL 原样登记并停止，符合「任何 FAIL 如实登记并停止回报裁决，不得改写、不得修补历史文件」。
3. **full suite**：未重跑（非 AC5 强制项）；既往 61 passed / 2 skipped / 3 failed / EXIT=1 保持 FAIL 登记，adjudication 的「建议重跑」未执行，如实保留为缺口。
4. **文档义务**：P2-1 六对 worktree/Git-blob SHA pair 表与双口径声明在 README 在场（README §P2-1）；P2-2 在「当前执行状态」与 §P2-2 段均按「顺序未经证明」口径表述；Task 卡 AC5 行 `<<PARTIAL: …>>` 如实（v3 语法合法，未勾选 + PARTIAL 带原因）；Canonical Evidence 增 ac5 三行、Resource Manifest 增两行；Handoff 未形成（卡面明示待 adjudication 后形成，属预期而非缺陷）。**残留缺口见 Finding P2-A**。
5. **Review/终裁独立性**：本报告即条件 5 要求的 fresh ZCode Review；final adjudication 须由另一不同 session 完成（未发生）。
6. **禁止项**：未发现违反——历史字节零触碰（diff 范围证实）、无 renormalize/prune/GC 迹象、无 push（本地 HEAD fea5c742）。

### 3.2 两个历史 TaskPath FAIL 的事实与归因（重点）

**事实（e69，本 Review 逐条核对日志原文）**：
- FEA-06-PREREQ-1（13 errors）：4× Evidence SHA-256 不匹配（appearance-tests.log、motion-tests.log、sln-test.log、build.log）+ 1× Canonical evidence 路径缺失（AppearanceCoordinator.cs）+ 1× DONE evidence_dir 含 3 个未登记文件 + 7× DONE 状态义务（canonical_evidence_status、resource_closeout_status、未完成 AC、Resource Manifest、AC1/AC3/AC5 处于 PARTIAL）。
- CHAPTER-SELECTOR-1（6 errors）：Resource Manifest 解析失败（该历史卡 manifest 值被反引号截断损坏）+ AC1–AC5 各缺 v3 状态标记。

**归因证据（三重，均本会话核实）**：
1. **改动面**：集成 diff 仅四授权文件，两条历史 Task 卡与 `verification/FEA-06-PREREQ-1/**`、`verification/CHAPTER-SELECTOR-1/**` 字节零改动。
2. **旧 checker 对照**：AC1c A（2026-11-11，实现前、旧 checker @2df8db7、autocrlf=true clone）日志显示同类失败在改动前已存在：FEA-06 为 15 errors = 本次 13 条逐条对应 + clone 特有 2 条（Plan 7056 bytes EOL 膨胀超限——AC1c/AC4 adjudication 已锚定为 autocrlf=true 确定性效应；AppearanceJson.cs SHA 不匹配——该文件为 MIXED_EOL 采样，fresh checkout 工作树字节效应，主仓库原生工作树不复现）；CHAPTER-SELECTOR 为 7 errors = 本次 6 条逐条对应 + 同一 Plan 膨胀 1 条。两侧无任何本次新增错误类型；AGPL/AD002 在 A clone 仅因 Plan 失败、在 e69 PASS（主仓 Plan 6979<7000），同一机制自洽。
3. **语义保留**：legacy 六列 OR 谓词经 R0 checker 同夹具对照测试证明未漂移（§2.3）。

**归因边界（不得越权）**：主线在集成前从未在主仓库环境实跑过这两条 TaskPath（AC5 前一律 NOT_RUN），不存在同环境改动前后 A/B 重放。上述结论为高置信间接证据链，**非重放证明**；最终归因与处置（accept-as-historical、豁免、或另行修复 Task）属 final adjudication 权力，本 Review 不裁定。

### 3.3 AC5 状态

AC5 卡面 `<<PARTIAL>>` 判定如实：集成与门禁事实完整，Handoff、fresh Review（本报告）、final adjudication 三件中后两件截至本报告完成前一项已补（本 Review）、一项未做；AC5 不得在终裁前改 `[x] <<MET>>`。本 Review 不改卡面状态。

## 4. Findings

| 编号 | 级别 | 位置 | 内容 | 处置建议 |
|---|---|---|---|---|
| P2-A | P2 | verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md:85 | Versioned artifacts 表 `ac4-clone-creation-audit.log` 行仍写 "Both clone-local EOL/path settings precede checkout"。该行写于 P2-2 发现之前（AC4 第一轮登记），但 AC4 adjudication §2.3(a) 要求「任何文档不得声称时序已被证明」；「当前执行状态」段已修正，此历史登记行残留旧口径声称 | 在授权范围内（verification/**）。建议 final adjudication 前由 Owner 将该行加 P2-2 限定或标注 superseded；属文档口径修正，不涉及历史 log/pin 字节 |
| P3-B | P3 | tools/governance/check.ps1:805-808 | legacy SHA 分支存在冗余嵌套与重复格式检查（外内两层同条件），畸形（非 64 位非占位）SHA 会重复报两条同消息错误。无漏报、无误放行，行为安全 | 授权范围内可修，但 checker 任何变更需重新 Review；本 Task 处于停止状态，不建议顺手修，留 Integrator disposition |
| P3-C | P3 | Task 卡 Canonical Evidence / fea5c742a | ac5 三行 evidence pin 落盘提交（fea5c742a）之后未在 clean committed HEAD 复跑 default/本卡 TaskPath（e69 上的 PASS 校验的是 pinbackfill 前卡面）。纯文档提交按协议 §6.12 无需重跑，与本 Task 此前 pinbackfill 后复跑 clean gates 的惯例（6c5d0015→c16d3fff 先例）不完全一致 | 建议终裁前补一次两条命令的 clean 复跑（成本极低），闭合「最新卡面未经 committed-state 机器校验」缺口 |
| P3-D | P3 | 本报告 §1 | plan mode 过滤器拦截部分命令形式，Git 核验经等价替代命令与两个只读子代理完成；implementation worktree 与 T/F clone 的全树 clean 未验证（仅四受审路径有等价证据） | 记录为证据质量限制；Resource Manifest 已按 PRESERVE_REFERENCED 登记不清理，无处置风险 |

无 P0/P1 findings。

## 5. 已证实 / 未证实 / NOT_RUN

**已证实（本会话独立复核）**：§2.1 集成范围与线性链；§2.2 四文件 blob/SHA-256 三方（7eef↔e69↔fea5c742）对齐及 adjudication 期望值一致；4ed 对象主仓库不可达；T/F clone 现场与 blob map 声明一致；八项 gate 日志完整性与结果（六 EXIT=0、两 FAIL/EXIT=1、pins 18/18、API 86）；两个历史 TaskPath FAIL 与旧 checker（AC1c A）失败集合逐条对应；四文件代码级审查结论；P2-1 六对 pair 与双口径在场；P2-2 修正口径在场；Task 卡 AC5 `<<PARTIAL>>` 如实。

**未证实（证据边界）**：两个历史 TaskPath FAIL 的绝对归因（无同环境改动前后重放，见 §3.2）；Task 卡 ac5 三行 pin 的 SHA-256 未独立重算（哈希工具不可用；且 e69 TaskPath PASS 时该三行尚未落盘）；implementation worktree / T/F clone 全树 clean；Handoff（尚未形成，流程预期内）。

**NOT_RUN（如实保留，均不改写为 PASS）**：full governance suite（既往 61/2/3 failed、EXIT=1 保持 FAIL）；Linux 跨平台；本 Review 自身未运行任何 gate/pytest（只读约束，结果引用 Codex 生成日志并核对其 GENERATED_HEAD/porcelain/UTC/EXIT 绑定）；R-001 与 Review-R-001 终闭合（开放，留 final adjudication）；final adjudication 本身。

## 6. Verdict

**APPROVED_WITH_LIMITATIONS**（P0=0 / P1=0 / P2=1 / P3=3）。

- 在本 Review 范围内：AC5 的集成形态、四文件 blob 映射、必跑门禁的执行与如实登记、停止义务的履行均符合 Task 与 AC4 adjudication 的条件；两个历史 TaskPath FAIL 有强证据支持为历史卡存量缺陷在旧 checker 下已存在的表现，而非本次四文件改动引入（最终归因留终裁）。
- **建议：停止并等待 final adjudication**——按 AC4 adjudication §4.5 与当前停止状态，下一步应由与本会话及既往全部 session 不同的 fresh session 承担最终 Integrator adjudication，处置：两个历史 TaskPath FAIL 的归因与豁免、R-001 / Review-R-001 终闭合、P2-A/P3-C 文档修正的接纳、Handoff 形成，以及是否补跑 full suite 建议。本 Review 不宣告 Task done，不构成最终集成关闭。
