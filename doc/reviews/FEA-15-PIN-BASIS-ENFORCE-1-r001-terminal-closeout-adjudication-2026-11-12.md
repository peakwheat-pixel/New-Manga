# FEA-15-PIN-BASIS-ENFORCE-1 R-001 终态 closeout Resource Manifest 只读裁决

- **裁决**：`AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION`
- **ZCode 来源**：主会话 fresh context；session `sess_2a379865-1182-4371-9b7c-63e47ef8b603`；turn `turn_27b225f9-9f41-4f6b-b2fb-a9dec02ba719`；CLI `EXIT=0`
- **审查基点**：clean base HEAD `e59469986553a63876a2685ad4388f1d65df58a6`（原回执记录的完整 HEAD 见下文；以回执为准）
- **原始回执**：`verification/FEA-15-PIN-BASIS-ENFORCE-1/zcode-r001-closeout-manifest-adjudication-20261112.jsonl`
- **CLI 过程日志**：仓外 `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/zcode-r001-closeout-manifest-adjudication-20261112-process.log`

以下为 ZCode 返回的裁决全文，原文保留：

---
全部材料核实完毕。以下为正式裁决。

---

# FEA-15-PIN-BASIS-ENFORCE-1 终态 Resource Manifest 门禁冲突只读裁决（2026-11-12）

**审查者身份与来源**：ZCode 主会话（fresh context，全程只读；reviewed clean base HEAD `e59469986553a63876a2685ad4388f1d65df58a6`，工作树仅含未提交恢复/记录改动，`git status` 快照与用户描述一致）。**sessionId 说明**：本模型上下文未暴露自身 session/turn ID，无法自报 sessionId；落盘登记时按先例（r001-correction-review 第 20 行同情形）以「ZCode 主会话（fresh context，只读，reviewed base HEAD e5946998…）+ 本裁决全文」为来源标注。本会话未修改任何文件、未运行任何门禁（plan mode 强制只读，git status/diff 亦被拦截，未提交 diff 未能本会话直接复核，依据 gitStatus 快照、两份 workspace 日志内嵌 GIT_STATUS 段与卡面记录判定）。

## TL;DR（大白话）

终态关卡的 43 条错误，除 1 条是当时把 Plan 的「READY 节点」声明改坏（已恢复）外，全部来自 Task 卡的 Resource Manifest 表：很多格子填的是说明文字（“同源保留”、“README”、带 `SHA-256 ` 前缀的哈希），而 checker 要求这些格子必须是**真实存在的路径**或**裸 64 位哈希**。其中有一条（61E 行）被上一轮裁决冻结不许改——但 checker 对它的格式要求永远过不去，两头死锁。**裁决：不存在不改这行、不改 checker 还能关门的路（已穷举证明）；本裁决行使再裁权，授权对这一格做最小修正——只删 `SHA-256 ` 前缀**，删完后这个哈希值恰好就是该行指向的仓内文件当前内容的真实指纹，checker 会拿真实文件验证它，不是凑数。其余 30+ 行不受保护，按统一规则规范化。程序照旧：证据入库 → 独立 Review → 终态四门全绿 → 才关 R-001 和 Task；任何一步失败就停下再裁。

---

## DECISION

**`AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION`**——允许在现 Task（in_progress，不释放新 Task）内完成：

1. 43-error 原始失败证据与恢复证据入库并 pin（原分类不变）；
2. Resource Manifest 全部**未受保护行**按本裁决第 Resource Manifest 节规则规范化；
3. **对受保护 61E 行（"Post-evidence-commit gates at 4fa651d"）发布有界修订授权**：仅允许删除其 sha256/manifest 列的 `SHA-256 ` 前缀；hex 值 `61E3622AB89C5CA60F06E93C1B73FD97F676E7C47DAF7598BCDD40792F6B2688` 本身与其余五列一字节不动；
4. 之后按 sess_1bff86d4 原条件与既有停止条件走完关闭序列（fresh 独立 Review → 终态四门 EXIT=0 → 最终全节 audit EXIT=0 → R-001 关闭、Task=closed_with_limitations）。

**STOP 替代分支**：若执行时发现 61E 行 destination 仓内文件当前工作树字节实测值已 ≠ `61E3622A…`（值漂移），或任何 workspace 资源路径已不存在，即停止、不修改、回报再裁。

## Resource Manifest

**checker 语义（check.ps1:852-919，已逐行核实）**：closeout 校验由任何终态状态触发（done/closed_with_limitations/cancelled/superseded/historical，或 approved+integration_commit，check.ps1:848-849）；in_progress 不触发——与恢复后 r2 日志 TaskPath PASS 一致。对 PRESERVE_* 表格行要求：① `destination_path` 必须解析为**实际存在的路径**（表格分支没有 JSON 分支的 sentinel 豁免，none/空/`-` 同样报错）；② `sha256/manifest` 列要么是**裸 64-hex**（此时与 destination 文件**当前工作树字节**的 Get-FileHash 比对，PowerShell `-ne` 大小写不敏感），要么是**实际存在的文件路径**。

**43 条错误逐类核实**（按日志原文，不以汇总数为准）：1 条 Plan READY 声明（终态候选改坏，已恢复，非 Manifest 问题）；35 条 `Resource manifest 不存在`（integrity 列 7 条非 hex 非路径值 + 28 条 `SHA-256 ` 前缀值）；7 条 `Resource 最终路径未验证`（6 条“同源保留” + 1 条 "Workspace original; incomplete attempt only"）。乱码转录下逐条对账存在 ±1 计数不确定，**处置面按 checker 规则覆盖全部 Manifest 行、执行后以 checker 全行重验为准，不按错误条数打补丁**。

**逐类规范化授权**（未受保护行，均在 allowed_paths 内）：

| 类别 | 行 | 处置 |
|---|---|---|
| 目录型资源（main worktree / 各 clone / worktree） | 294-301 | `destination_path` 由「同源保留」改为该资源**实际绝对路径**（同源保留语义 = destination 即 source 原路径）；行 300 T/F 一行两路径**拆为两行**；行 301 glob 行 destination 改为 workspace Task 目录实际路径。`sha256/manifest` 填存在的文件路径（推荐 `verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md`；行 296 保留原语义补全为 `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1c-b-r0-assertions-taskpath-bfae0b9.log`）。目录 destination 不触发 hash 比对（check.ps1:916 仅 Leaf） |
| 文件型资源（外部原件→仓内副本） | 302-323、325-328 | `sha256/manifest` 去 `SHA-256 ` 前缀，且**以 destination 仓内文件当前工作树实测 Get-FileHash 为准**；若实测 ≠ 原登记值（原值多为外部原件 SHA，仓内副本 EOL 归一化后可不同，如 daaed811 log 61E/cab7/e95 三值先例），填实测值，原外部值**移入最右 result 列文字登记**（如「外部原件 SHA-256 \<原值\>」），不得丢弃 |
| 行 316 interim audit | 316 | destination 改为 workspace 原件实际路径；integrity 去前缀并须与该文件实测一致 |
| NOT_APPLICABLE 行 | 329 | 不动（checker 跳过，无错误） |

**受保护 61E 行（行 324）**：

- **在 r001-crlf-pin-adjudication 现行边界下，该行必须全部字节不动——该边界本裁决予以有界修订**，理由四点：① 该裁决冻结意图是防止 discrepancy 被静默抹平、防止当时执行会话扩大改动面，而非永久冻结活跃卡数据行的格式错误；其「超出第 1-6 项禁止」语义 = 需新裁决授权，本裁决即为该新裁决（与 `61e→e95` 单列修正的程序先例完全同构：发现新失败 → 回报 → 再裁授权 → 执行 → 独立 Review）；② 去前缀后 `61E3622A…` 恰为该行 destination（仓内 `main-post-r001-review-pinbackfill-gates-daaed811.log`）**当前工作树字节的真实 SHA-256**（crlf 裁决实测：工作树含 1 CR、SHA=61e…，去 CR 得 blob e95…）——不是凑数，checker 将以真实文件字节验证它；③ source 外部原件（实测 `cab7…`）与 61E 的 discrepancy 已由卡面第 282-286 段及 crlf 裁决报告永久登记，格式修正不抹除任何事实；④ 旧形态（`SHA-256 61E…` 带前缀）须在本裁决说明段登记 old→new 轨迹。**执行前置实测义务**：修改前重新 Get-FileHash 该仓内文件，确认仍为 `61E3622A…`；漂移即 STOP 分支。
- **是否存在不改该行、不改 checker、仍能让 closed TaskPath PASS 的合法办法：不存在。** 穷举证明：(i) 所有终态均触发 closeout 校验，无豁免状态；(ii) 该行 integrity 为 `SHA-256 61E…`（非 64-hex）时唯一通过条件是该字符串解析为存在的文件（check.ps1:911-913）——不可能成立，除非创建名为该字符串的垃圾文件，属 checker-gaming，禁止；(iii) 改 disposition 为 NOT_APPLICABLE = 改该行字节 + 虚假分类（资源实存且保留），双重违规；(iv) 改用外部 JSON manifest 分支需**删除全部表格行**（含 61E 行），违反字节保留。**故若不接受本裁决的前缀修订，则约束冲突不可解：该 Task 无法以任何终态通过机器关卡，只能无限期停留 in_progress 等待新裁决。**

## 状态

- **R-001：OPEN；Task：in_progress**（当前已恢复，确认正确，勿动）。
- 终态达成条件不变：本裁决序列全部通过（规范化落地 → fresh 独立 Review → 终态四门 EXIT=0 → 最终全节 audit EXIT=0 且日志入库 pin）后，方按 sess_1bff86d4 **原条件、不修订**关闭 R-001，`canonical_evidence_status`/`resource_closeout_status` 置 complete，Task=`closed_with_limitations`。
- **终止口径（消除 audit pinbackfill 无限回归）**：R-001 关闭前的最后一轮全节 audit 必须覆盖当时卡面全部 Canonical Evidence 行（含本裁决报告与全部新 pin 行）且 EXIT=0；该 audit 日志入库 pin 后即视为满足原条件，pin 该日志本身新增的 2 行不再触发新一轮 audit——其正确性由终态 TaskPath 的 Canonical Evidence 机器校验（closeout 时逐行 worktree/blob 验证）与 fresh 独立 Review 覆盖。
- 任一步 EXIT≠0 或新失败：停止、回退状态字段至 in_progress/R-001 OPEN、原始日志保留、回报再裁（既有停止条件延续）。

## 证据与 Gate

**必须先提交/pin 的原始证据**（复制入 `verification/FEA-15-PIN-BASIS-ENFORCE-1/`，原分类不变）：① `preliminary-closeout-gates-e59469986-fail.log`（43 errors/EXIT=1，永久 FAIL 记录）；② `post-failure-recovery-gates-e59469986-r2.log`（恢复后四门 EXIT=0）；③ 仓外 120/120 post-pinbackfill full-section audit 日志；④ 本裁决报告落盘 `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-terminal-closeout-adjudication-2026-11-12.md`；⑤ 上述全部 pin 进 Canonical Evidence（六列旧格式，commit/SHA 实测）。README 追加汇总（纯追加，不改历史句）。

**复跑序列**（各阶段 clean HEAD）：
1. 证据+裁决+规范化（含 Rolling Checkpoint 轨迹：FAIL→恢复→本裁决→授权）提交后：default check、本卡 TaskPath（in_progress 下应 PASS 3 warnings）、full-section audit（覆盖全部行，EXIT=0）。
2. **fresh 独立 Review**（上下文独立；本裁决会话与执行会话均不得审）：核查规范化边界、61E 行处置、零越界、discrepancy 披露完好；须 P0/P1=0 且无修正范围新 finding；报告入库+pin。
3. 终态候选（Task=closed_with_limitations、两 closeout 字段 complete、STATUS 无 Active Task、Plan/TASK_LEDGER 更新、Handoff 终态补充）：default、TaskPath（**closeout 校验激活，须 EXIT=0**）、`verify_pins.ps1`（18/18）、API inventory（1/79/6=86）。Plan 守 7000 bytes 红线（当前 6999，终态指针更新须同步压缩）且 `READY 节点：` 声明行保留（终态候选曾改坏，不得重犯）；TASK_LEDGER 重跑 `task_ledger.py --write`（non-terminal 11→10）。
4. 通过后：最终全节 audit EXIT=0 入库 pin，Closeout Record 完成，R-001 关闭。

**失败处理**：任何 EXIT≠0 → 停止、回退状态、原始日志保留、回报再裁；绝不改写任何 FAIL；Plan 超预算即压缩既有行而非删 READY 声明。

## 限制

**允许**（仅此清单）：`doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`（Resource Manifest 上述各列规范化 + 61E 行仅删前缀；Canonical Evidence 纯追加新 pin 行；Rolling Checkpoint/Closeout Record 追加；frontmatter approval/reviewer 现时字段同步；通过后的终态字段）；`doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-*.md`（本裁决报告 + fresh Review 报告）；`doc/handoffs/FEA-15-PIN-BASIS-ENFORCE-1-e69fc2dc.md`（终态补充：61E/cab7 双运行口径、P3-O1/O2、历史 FAIL、Linux NOT_RUN、P2 limitation）；`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`（终态指针）；`verification/FEA-15-PIN-BASIS-ENFORCE-1/**`（新日志入库与 README 纯追加）。

**禁止**：改 61E 行除删前缀外的任何字节（hex 值不变、其余五列不动）；改 check.ps1 / verify_pins.ps1 / task_ledger.py 源码（Ledger 仅 `--write` 再生成）；改 18 frozen pins、既有 12 行订正、fe6e 审计记录、既有 Canonical Evidence 全部行（只许追加）；改任何历史 Task/Review/Handoff/evidence 字节、外部原件、被审计门禁日志字节；**为通过 913 行存在性检查创建任何占位/垃圾文件（尤其名为 `SHA-256 <hex>` 的文件）**；改 disposition 为虚假 NOT_APPLICABLE；push、清理/gc/prune/repack、worktree prune；把任何 FAIL（FEA-06 13 errors、CHAPTER-SELECTOR 6 errors、full suite 3 failed/EXIT=1、fe6e 103 审计 1 FAIL、本次 43 errors）改写为 PASS；Linux/full suite NOT_RUN 分类变动。填入的每个 SHA 值必须是执行时实测值，禁止复制未实测值。

---

**推荐下一步**：由 Codex 写会话按上述序列执行（可直接转发）：

```
任务：FEA-15-PIN-BASIS-ENFORCE-1 终态 closeout 预检 43 errors/EXIT=1（HEAD e5946998，日志 preliminary-closeout-gates-e59469986-fail.log）已由 ZCode 只读裁决处置（2026-11-12，AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION，报告落盘为 doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-terminal-closeout-adjudication-2026-11-12.md 并 pin）。执行序列：1) 将 43-FAIL 日志、恢复 r2 日志、仓外 120/120 audit 日志复制入 verification/FEA-15-PIN-BASIS-ENFORCE-1/ 并连同裁决报告提交、pin 进 Canonical Evidence（六列旧格式，实测 commit/SHA），README 纯追加；2) 按 Resource Manifest 规则规范化：目录行 destination 改实际绝对路径（T/F 行 300 拆两行），文件行 integrity 去前缀并以 destination 当前工作树实测 Get-FileHash 为准（原外部值移入 result 列登记）；受保护 61E 行仅删 'SHA-256 ' 前缀——修改前必须实测该仓内文件 hash 仍为 61E3622A…，漂移即停回报；旧形态在说明段登记轨迹；3) Rolling Checkpoint 记录 FAIL→恢复→裁决轨迹，提交后在 clean HEAD 复跑 default/TaskPath（in_progress，应 PASS 3 warnings）与全节 audit EXIT=0；4) fresh 独立上下文 Review（P0/P1=0、无修正范围新 finding）→ 报告入库 pin；5) 终态候选：Task=closed_with_limitations、canonical_evidence_status/resource_closeout_status=complete、STATUS 无 Active、Plan（守 7000 bytes、保留 READY 节点声明行）/TASK_LEDGER（--write 重跑）/Handoff 更新，clean HEAD 四门 default/TaskPath/18 pins/API 须全 EXIT=0；6) 最终全节 audit EXIT=0 入库 pin 后按 sess_1bff86d4 原条件关闭 R-001、完成 Closeout Record；任一步 EXIT≠0 即停、回退 in_progress/R-001 OPEN、回报再裁。全程禁改：checker/verify_pins/task_ledger 源码、18 frozen pins、历史字节、外部原件、61E 行除前缀外字节；禁止创建占位文件骗校验；不 push、不清理；所有历史 FAIL/NOT_RUN 原分类保留。
```
