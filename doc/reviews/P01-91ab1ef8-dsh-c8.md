task_id: P01
reviewer: DeepSeek Harness（DSH，非作者）
author: Codex（Owner/Integrator）
round: C8（固定差量只读 Review — Addendum）
base_commit: 826bea12a132c5af2ac0cd1244d00e9170093c71
reviewed_head: 91ab1ef8ddaa1d00b0b34880a103937b4831590d
reviewed_tree: 6f8477d7fbc428b94aa031ae4fce1196cfb7e647  # NOT_VERIFIED（见 F-C8-05）
decision: changes_requested
delivery_commit: 9b12493616326af9cdd50a055282426c72516a5a
branch: agent/codex/P01-metadata-audit
historical_preserved: [R1@6f24006c=blocked, R2/C6@3e67d53=blocked]
---

# P01 C8 Review Addendum（固定头 91ab1ef8）

## 1. 口径与范围

本 Addendum 依据本 session 内已完成的差量包 **2090/2090 行分段读取**（`verification/P01/dsh-review-c8-input.diff`，包内 `diff --git` 43 条）、以及已读 Task / Gate / 来源证据。全程**只读**（`glob`/`read`）；**DSH 未运行任何 shell/Git/Python/validator/测试/构建/Gate 命令**，未修改/暂存/提交/集成文件。凡 `git …`/`EXIT=` 均来自 **Codex 侧已入库日志**（`verification/P01/ac7-*.log`），属 **Codex 执行证据**，**不是 DSH 复跑**。

固定对象锚定（DSH 读 Git 元数据文件）：`…/worktrees/P01-c8-review-dsh/HEAD` = `91ab1ef8…`（detached，单条 reflog）；`.git/refs/heads/agent/codex/P01-metadata-audit` = `91ab1ef8…`；reflog 链 `826bea12(branch created)→714138de→9b124936→dfe31bba→6f24006c→aaa27767→e95ebbf5→3e67d53→06f52f5a→91ab1ef8`。故 `HEAD==reviewed_head`、base 为祖先成立（依据为引用文件，非 `git rev-parse`）。

**未覆盖/未核**：`task-inventory.csv` 196 行全文与三份审计报告全文、worktree 外其他 worktree、远端、产品源码/测试/构建/GUI/模型；全部 SHA-256/blob OID/tree OID 未重算；工作树逐字节等于该 tree 未证明。

## 2. Architecture 结论

**架构轴：未发现阻断项。** 43 路径全在 `doc/**` 与 `verification/**`，**产品/测试/Schema/依赖零差量**（无 `src|apps|tests|packaging|doc/contracts|requirements*`；Codex 日志 `PRODUCT_CODE_PATH_COUNT=0`）。无 IPC/分层/契约/Schema 改动，无 WebView 直连 DB/OS/模型。唯一「代码」文件 `verification/PROJECT-ROADMAP-20261008/verify_plan.py` 属治理校验器，不进产品构建/运行路径。R2-03 加固点已在证据层成立：Codex 日志记 `CWD`、`VALIDATOR_ABSOLUTE`、`live HEAD=91ab1ef8`（`:129-132`），可静态推得 `ROOT` 落在 P01 worktree（脚本 `:8-9,28`）。

## 3. Verification 表（简）

| 检查 | 状态 |
|---|---|
| 差量包分段读取 2090/2090（1→2090，无截断） | **EXECUTED（DSH）** |
| 差量包 bytes 208116 / SHA-256 `97514615…` | **NOT_RUN（DSH，无哈希工具）** |
| 43 路径 ∈ P01 allowed paths（越界 0） | **EXECUTED（DSH 静态，对照 `P01.md:36-42`）** |
| reviewed_head / detached 锚定（`.git` 文件） | **EXECUTED（DSH）** |
| `reviewed_tree=6f8477d7…` | **NOT_RUN / NOT_VERIFIED**；全仓库仅命中 `dsh-review-c8.prompt.md:10`，无执行证据 |
| `git rev-parse/status/diff/--check/cat-file/merge-base` | **NOT_RUN（DSH）** |
| allowed paths / `git diff --check` base..head | **NOT_RUN（DSH）**；引用 Codex 日志（43 paths、`OUTSIDE_ALLOWED_COUNT=0`、`RANGE_DIFF_CHECK_PASS=True`、`EXIT=0`，`:33-78,122-128`） |
| `python … verify_plan.py` 执行 | **NOT_RUN（DSH）**；DSH 仅静态复算 Plan 表 21 行 `done 2/in_review 1/proposed 18`、ROADMAP 图 P08 唯一且 `done`、产品守卫范围为空（`verify_plan.py:60-82,112-119`） |
| C8 fixed-head Gate 日志（`:1-181`） | **Codex 执行证据**；DSH 仅只读核对自洽，未复跑 |
| 来源 Task 字段/状态、`doc/reviews` carrier 存在性 | **EXECUTED（DSH）**：GC2 `:19=cea610ed…`、DETECT3 `:6=8fe5199c6d05…`、SYNTH `:13=913ca3a9f9…` 且无重复字段、ANNOTATE-R2 `:5 in_review`/`:17 review_events: []`；`*ANNOTATE-R2*`、`*SYNTH*` 报告 glob 零匹配 |
| 导航/状态一致性交叉比对 | **EXECUTED（DSH）**：发现不一致（F-C8-01/F-C8-02） |
| SHA-256/blob/tree 重算；产品 pytest/cargo/vitest/GUI/build | **NOT_RUN**（未记为 PASS） |

## 4. Findings（全部实际发现）

**F-C8-01 — P1 — open**
- 文件/行：`doc/00_INDEX.md:3`、`:9`；`doc/12_ROADMAP.md:3`、`:9`（差量 hunk `dsh-review-c8-input.diff:8-9`、`:15-16`、`:34-35`、`:43`）。
- 触发：C8 把 P01 由 `blocked` 恢复为 `in_review` 时漏改这两个导航文件的「当前工作」段。
- 影响：`00_INDEX.md:11` 自我声明首段为当前事实，`AGENTS.md` 要求每次开始先读该文件；读到 P01=`blocked` 与权威面 `in_review` 矛盾，恢复/派发方可能误判 P01 受阻；AC7 要求导航状态一致，未满足；`verify_plan.py` 只查 Plan 表/ROADMAP 图/链接，覆盖不到该文本，故 Codex Gate 的 `ROUTE_VALIDATOR_PASS=True` 不能排除本项。
- 证据：`00_INDEX.md:3`「P01为唯一`blocked` Task，…blocked 1、proposed 18」；`:9`「当前唯一Active Task为[P01] `blocked`」；`12_ROADMAP.md:3`「唯一Active Task=P01 `blocked`」；`:9`「P01是唯一blocked Task」。对照：`P01.md:5 in_review`、`REBASELINE_PLAN.md:3`「done 2、in_review 1、proposed 18…状态=in_review」、`STATUS.md:3`、`README.md:5`、`PROJECT-ROADMAP…/ROADMAP.md:32`、`verification/P01/RESUME.md:2,93`。
- 建议：限 P01 allowed paths（`P01.md:42` 已授权）把四处改为 `in_review` 并同步 C8 口径；不改来源 Task 状态与 R1/R2 结论；改后产生新 fixed head 重审。

**F-C8-02 — P2 — open**
- 文件/行：`doc/STATUS.md:7`、`doc/REBASELINE_PLAN.md:74`。
- 触发：现在时/「当前步骤」停留在 C7/R2 口径。
- 影响：`STATUS.md:5` 标题已写「由C8 in_review取代」，`:7` 仍称「当前唯一 Active Task…TaskStatus=`blocked`」，与同文件 `:3` 矛盾；`REBASELINE_PLAN.md:74` 仍写「R2 blocked…后续尝试可执行的临时Review镜像」，未反映 C8 实际采用的只读固定差量+Codex Gate 方法（`:3`、`P01.md:84-88`），可能误导下一执行者重走已被取代方案。
- 建议：改过去时或标注「（历史；C8 起改用只读差量 Review）」，Plan `:74` 更新为 C8 方法。

**F-C8-03 — P3 — open**
- 文件/行：`verification/P01/ac7-c8-fixed-head-check.log`（整文件；`:3 SHELL=PowerShell unknown`）。
- 触发：C8 Gate 日志不在 base..head 的 43 路径内（差量 43 条与日志自录 43 条清单 `:34-76` 一致，均不含自身），为 head 之后 carrier。
- 影响：C8 越界/diff-check/validator 证据尚未随固定 head 版本化（与 R2-02 同类，延后一轮）；shell 头不完整，弱于 C5/C6/C7 的 `SHELL=PowerShell 7.6.6`，未完全满足 §6.12①。
- 建议：下一次 checkpoint 把该日志入库并补记 shell 版本与 SHA-256。

**F-C8-04 — P3（Integration 动作项）— open**
- 文件/行：`verification/PROJECT-ROADMAP-20261008/verify_plan.py:72-75`。
- 触发：`assert p01_state in {"in_progress","in_review","blocked"}` 与 `status_counts == {"done":2, p01_state:1, "proposed / 未释放":18}` 为硬断言。
- 影响：集成 commit 把 P01 置 `done` 后 `p01_state="done"` 越界、计数变 `done:3`，**主线 validator 必然报错**，除非同 commit 更新（`P01.md:44` scope note 已授权）。
- 建议：Integration commit 内同步扩展集合/计数，并记录新 validator `EXIT=0`。

**F-C8-05 — P3 — open**
- 文件/行：`reviewed_tree=6f8477d7fbc428b94aa031ae4fce1196cfb7e647`（唯一出现 `verification/P01/dsh-review-c8.prompt.md:10`）。
- 触发/影响：本次 fixed 对象声明 tree，但**无任何已执行证据绑定**——C8 Gate 日志未记 `--format=%T`/`HEAD^{tree}`；C7 只读预检第 4 条亦为 `NOT_RUN`（`verification/P01/dsh-preflight-canonical-root.md:21`）。DSH 工具无法求 tree OID（需 `git cat-file`/SHA-1），**不能独立核验**。固定对象仅锚定到 commit 层。
- 建议：Codex 在 Gate 中记录 `git rev-parse HEAD^{tree}` / `git show -s --format=%T` 输出与 EXIT。

**ENV-01 — P2（环境，非作者可修）— open**
- 位置：本