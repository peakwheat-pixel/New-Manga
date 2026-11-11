---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
reviewed_head: bf377705783da10eebcf6585316178984ef663d8
adjudicator: ZCode CLI fresh session
session_id: sess_d4df68bf-4fa3-4828-8ac6-47c25717be76
turn_id: turn_a90afd6b-821e-4494-983b-a5da890dada1
decision: ACCEPT_CONTINUE_WITH_T_SIDE_BASELINE_ANCHOR
mode: read-only adjudication
date: 2026-11-12
---

# FEA-15-PIN-BASIS-ENFORCE-1 AC4 STOP 判定独立裁决（2026-11-12）

**裁决者**：ZCode CLI fresh session（只读；未参与 AC4 执行、AC2/AC3 实现或 Review，满足 2026-10-31 上下文独立口径）
**裁决对象**：主裁决 `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-adjudication-2026-11-12.md` §5.7 停止条件在候选 HEAD `bf3777057…` 两 fresh clone 实测结果上的适用性
**决定**：`ACCEPT_CONTINUE_WITH_T_SIDE_BASELINE_ANCHOR`——两项观察均判为已解释的 autocrlf=true 确定性效应，登记 T 侧预期锚后**允许继续 AC4 A.1/A.2 inventory/delta**；不释放 AC5、不构成终裁。

## TL;DR（大白话）

- **T 侧 16 个 pin mismatch：不是 STOP。** 这 16 个文件的 pin 是按 LF 字节打的，而 fresh true checkout 会把所有文本文件统一变成 CRLF，必然对不上。T/F 两边 mismatch 集合刚好互补（一边错的另一边全对、合起来正好 18 个），这证明内容没变、纯粹是换行符问题。同一个现象在 AC1c A 侧（也是 true checkout、同样 16 mismatches）已经被之前的独立裁决 `ACCEPT_CONTINUE` 接受过一次。
- **T 侧 Plan 预算 FAIL：不是 STOP。** 预算检查读的是工作树磁盘字节（`check.ps1:627`）。CRLF 让 64 行的 Plan 文件刚好胖了 64 bytes（6971→7035），跨过 7000 上限。差值 100% 可由 autocrlf 解释，且 AC1c A 有同构先例（7056 vs 6992，同样 +64）。
- **但有个真问题要单独记住**：LF 口径下 Plan 已 6971/7000（99.6%）、STATUS 3183/3200，只剩 29/17 bytes 余量。AC4 证据入库（main 是 LF 口径）随时可能真超预算——那时不能用“CRLF 解释”豁免，得缩文或另获裁决。
- **可以继续 inventory/delta**，但要先补两个动作：① 对 16 个文件跑一次“CRLF→LF 归一化后哈希=pin”的对称确认（把我的推断升级为实测）；② 先做 generator 字节同一性断言。

## 一、判定依据

### 已实测事实（logs + 代码，本 session 直接读取）

| # | 事实 | 来源 |
|---|---|---|
| F1 | `verify_pins.ps1:23` 用 `Get-FileHash -Path $src` 对 **worktree 原始字节**哈希，无任何 EOL 归一化；pin 值取自冻结记录文件 | `tools/governance/verify_pins.ps1:23` |
| F2 | T 侧 pins FAIL(16)：C01b C02 C03 C05–C16 FEA01 mismatch、C04b/C17 OK；F 侧 FAIL(2)：仅 C04b/C17。**T∩F=∅，T∪F=18，精确互补** | 两个 actual logs |
| F3 | F 侧结果与 `dd637242…` 基线 false 侧完全一致（同 C04b/C17）→ §5.4 的 clone-F 预期**已满足** | `ac2ac3-baseline-controls.log:56-76` |
| F4 | 基线记录中 "main true checkout 18/18" 是**既有 main worktree**（非 fresh clone）；主仓四文件形态为 C01b mixed / C02 LF / C04b LF / C17 CRLF 的混合遗留状态；仓库中不存在任何 fresh true clone 的 18/18 记录 | controls log:81-103 + 用户提供实测 + Explore 全仓检索 |
| F5 | `check.ps1:629` 预算判定：`REBASELINE_PLAN.md` 7000 bytes / 64 lines，**严格大于**即 error（exit 1）；`:627` 用 `(Get-Item).Length` 测 **worktree 磁盘字节** | `tools/governance/check.ps1:622-631` |
| F6 | T=7035 bytes FAIL，F=6971 bytes WARN(80%)；差恰 64 bytes = 64 行 × CRLF 每行 +1 byte；行数两侧同为 64（`Get-Content` 按行分割与 EOL 无关，不触发行维度）。STATUS.md 同构：3183 vs 3152（差 31 = 31 行），两侧均 < 3200 仅 WARN | 两个 actual logs + check.ps1 代码 |
| F7 | API 两侧 EXIT=0、86 项一致；basis suite T=17 passed+9 subtests、F=15 passed+2 skipped+9 subtests，相对既有口径（true 13 / false 11+2sk）**两侧各 +4**，恰等于已释放的 R-001 四类负例（§5.1 明示以追加后 HEAD 为准），互补机制保持 | 两个 actual logs + 主裁决 §5.1/§5.2 |
| F8 | **AC1c A 直接先例**：A clone（autocrlf=true）pins 同为 16 mismatches、Plan 工作树 7056 bytes vs blob 6992（+64），default/TaskPath FAIL——已由独立 ZCode session `ACCEPT_CONTINUE` 裁定“将 A 侧预期锚精确化为 autocrlf=true 环境的确定性结果” | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md:66,93-94` 及其引用的 AC1c 裁决 |

### 推断（高置信，机制性；本 session 无法跑命令直接验证）

| # | 推断 | 依据链 |
|---|---|---|
| I1 | pin 表字节形态 = 16×LF 哈希 + C04b/C17×CRLF 哈希 | F1 + F2 互补：T 下 C04b actual=pin（worktree CRLF）⟹ 其 pin 为 CRLF 形态；16 文件 F 下 actual=pin（worktree LF）⟹ pin 为 LF 形态 |
| I2 | 16 个 mismatch 均为**纯 EOL 差异、无内容漂移** | F 侧 16 文件 OK ⟹ F worktree 字节哈希=pin；autocrlf=false checkout 下 worktree=blob 原始字节 ⟹ blob 内容与 pin 记录一致；T 侧 mismatch 只能来自同一 blob 的 CRLF 化 |
| I3 | 主仓 18/18 依赖“16 文件 LF + C04b/C17 CRLF”的混合遗留状态，该状态不是任何 fresh checkout 的产物 | F1/F4 + I1：fresh true 统一 CRLF（16 必错）、fresh false 统一 blob LF（C04b/C17 必错） |

**推断 I2 的残余风险**：依赖“.gitattributes 无 eol 指令干预、md 均按 text 处理”这一前提（由 T/F 四文件 `ls-files --eol` 样本与基线复现佐证，未对 18 文件逐个实测）。故下文将“16 文件归一化对称确认”列为继续执行的**前置登记义务**，把 I2 升级为实测。

### 裁决文本的缺口认定

§5.4 明文限定“**clone-F 侧**预期仅 C04b/C17 mismatch（与 `dd637242…` 基线集合一致）”——该基线集合的出处（controls log）是 **false 侧**记录。主裁决对 **clone-T 侧的 pins 结果没有明文预期**；其隐含参照物是“main true checkout 18/18”，而 F4/I3 证明该参照物不是 fresh true checkout 的字节状态。**这是裁决文本缺口，不是执行偏差。** 按项目纪律（事实与文档不一致→交裁决处置），由本裁决补齐。

## 二、逐问裁决

### Q1：T 侧 16 个 EOL pin mismatch —— 不 STOP，追认为已解释的 T 侧基线限制

1. **机制确定性**（F1+I1）：fresh true checkout 将全部 text 契约文件统一 CRLF 化，16 个 LF 形态 pin 必然 mismatch、C04b/C17（CRLF 形态 pin）必然 OK。这不是候选 HEAD 的内容属性，任何 fresh true clone @ 同一 HEAD 都会得到同集合的 16 mismatch。
2. **内容漂移已排除**（F2+I2）：T∩F=∅、T∪F=18 的精确互补在机制上排除内容变化（内容漂移会使同一文件在两侧同时异常）。
3. **直接先例**（F8）：同一现象（同 16 pin、true checkout、16 mismatches）已在 AC1c A 由独立裁决 `ACCEPT_CONTINUE` 接受为预期锚。若把 §5.7 第②条的 C04b/C17 集合机械套用到 T 侧，会与该已裁决预期锚直接矛盾——故第②条应解读为 false 侧基线集合（§5.4 上下文一致），“新 mismatch”指**无法由 autocrlf 解释**的 mismatch（与第③条本质判据同构）。
4. **义务定义**（§5.2）：verify_pins 的明文义务是“记录逐 pin 结果与任何 EOL mismatch”，非两侧 PASS。

**处置**：T 侧 `PIN AUDIT: FAIL (16)` 如实登记为 limitation（与 F 侧 C04b/C17 的 FAIL/limitation 处置同构），不得改写为 PASS、不得改 pin（§5.6 不变）。本裁决显式登记 **T 侧预期锚**（见 Q3）。

### Q2：T 侧 Plan 预算 FAIL —— 不 STOP，判为 autocrlf=true 的确定性二次效应

1. **归因闭合**（F5+F6）：预算输入是 worktree 磁盘字节；7035−6971=64=行数，差异 100% 可由 autocrlf 解释——§5.7 第③条（本质判据）不命中。行维度两侧同为 64、不超限，进一步排除内容增量。
2. **同构先例**（F8）：AC1c A 的 Plan 7056 bytes（+64 vs blob）同因 FAIL，已被 `ACCEPT_CONTINUE` 精确化为“autocrlf=true 环境的确定性结果”。
3. **警告差异同样闭合**：T=1 error+2 warnings、F=3 warnings，唯一差异是 Plan 维度在 T 侧从 WARN 升级为 error（`if/elseif` 不叠加，`check.ps1:629-630`）。

**处置**：如实登记 EXIT=1 与成因（7035=6971+64 CRLF），不改写。**独立登记（本裁决不豁免）**：LF 口径下 Plan 6971/7000（余 29 bytes）、STATUS 3183/3200（T 侧余 17 bytes）均为预算临界；AC4 证据/README 增量在 main（LF 口径）入库时若超预算即为真超，须缩文或另获预算裁决，不得引用本裁决的 CRLF 归因。

### Q3：下一步 —— 允许继续 inventory/delta，附前置与停止条件

**允许**（限 Addendum A.1/A.2 三层对照 + §5.2 证据补全）：

| # | 前置/控制 | 判定 |
|---|---|---|
| C1 | **16 文件归一化对称确认**（新增，继续 inventory 前必做）：对 16 个 T mismatch 契约文件逐一验证“T worktree 经 CRLF→LF 归一化后 SHA-256 = pin”，只读命令完成，输出入 `ac4-*.log` | 全部闭合 → I2 升级为实测；任一不闭合 → 立即 STOP |
| C2 | **generator 字节同一性断言先行**（§A.2 既有）：AC4 wrapper 运行前比对被测 clone 内 generator SHA-256 与冻结源 | 不一致即停 |
| C3 | R0 基准 inventory 只在保留 R0 clone（false、clean）生成；两 clone 检出后为冻结态，clone 内禁改任何文件 | — |
| C4 | 行级对照按 §A.2 归一化口径：T 历史行差异逐行经 CRLF→LF 归一化闭合于 R0；REMOVED≠0 逐行归因；ADDED/CHANGED 逐行归因 A.1 的 11 路径允许集 | 不闭合/无法归因即停 |
| C5 | **T 侧预期锚（本裁决登记）**：pins FAIL(16)（集合=C01b C02 C03 C05–C16 FEA01）+C04b/C17 OK；check default/TaskPath FAIL(1 error: Plan 7035B)+2 warnings；API EXIT=0/86；basis 17 passed+9 subtests。F 侧锚：pins FAIL(2)、check PASS+3 warnings、API EXIT=0、basis 15+2sk。**任何偏离锚的新 mismatch/新失败 = STOP** | — |

**禁止**（§5.6/A.4 全部不变，另强调）：不改 pins/`.gitattributes`/`verify_pins.ps1`/历史字节；不 renormalize；不 AC5 集成、不 close、不 push、不清理/prune/GC/repack；T/F 侧 FAIL 不改写为 PASS；Linux 记 `NOT_RUN`；`*-invalid-wrong-cwd.log` 不得作为证据（已重命名隔离，处置正确）。

**程序**：AC4 完成后仍按主裁决 §7.5 由新的独立 ZCode session 处置并决定是否释放 AC5；本裁决不释放 AC5。

## 三、可复现条件

- **复现 T 侧 16 mismatch**：`git clone --no-checkout --no-hardlinks` → checkout 前写 clone-local `core.autocrlf=true`、`core.longpaths=true` → checkout `bf3777057…` → 在 clone 内运行 `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → 必得同集合 FAIL(16)。
- **复现 T 侧 Plan 预算 FAIL**：同上 clone 运行 `check.ps1` → 必得 `7035 bytes / 64 lines` FAIL（前提：`doc/REBASELINE_PLAN.md` blob 为 64 行 LF、6971 bytes——任一后续提交改变该文件即改变数字）。
- **判定不变的边界**：若未来任何 HEAD 上出现 T/F 互补破裂（同一文件两侧同时 mismatch 或集合非互补）、或 C1 归一化不闭合、或 F 侧出现 C04b/C17 之外的 mismatch——立即回到 §5.7 STOP。

## 四、落盘与执行要求（Owner：codex）

1. **落盘本裁决**：本报告即裁决落盘（frontmatter session/turn 为真实值）；提交为 docs commit 后，在 Task 卡 `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` 的 rolling checkpoint 登记：T 侧预期锚（C5）、T 侧两项观察的 limitation 定性、Plan/STATUS 预算临界警示与本裁决引用。
2. **按 C1–C5 前置继续 AC4 A.1/A.2 inventory/delta**：证据入 `verification/FEA-15-PIN-BASIS-ENFORCE-1/`（`ac4-*.log` 命名），README 增补 AC4 段落，Linux 记 `NOT_RUN`；全部停止条件（§5.7 + §A.4 + 本裁决 C1–C5）任一命中即停、保留现场、回报裁决。
3. **完成后停**：AC4 结果交新的独立 ZCode session 处置并决定是否释放 AC5（主裁决 §7.5）；AC5 仍未释放，本裁决不构成终裁。

## 五、可转发指令

```
任务：FEA-15-PIN-BASIS-ENFORCE-1 AC4 STOP 判定裁决已下（ACCEPT_CONTINUE_WITH_T_SIDE_BASELINE_ANCHOR：T 侧 16 个 EOL pin mismatch 与 T 侧 Plan 预算 FAIL 均判为 autocrlf=true 确定性效应，不 STOP；登记 T 侧预期锚后允许继续 inventory/delta）。请依次执行：
1) 确认裁决报告 doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac4-stop-adjudication-2026-11-12.md 已提交入库；在 Task 卡 doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md 的 rolling checkpoint 登记 T 侧预期锚（pins FAIL(16)：C01b C02 C03 C05-C16 FEA01，C04b/C17 OK；check default/TaskPath FAIL(1 error: Plan 7035 bytes)+2 warnings；API EXIT=0；basis suite 17 passed+9 subtests）与本裁决引用；
2) 前置 C1（必做，先于 inventory/delta）：在 ac4-clone-t 对 16 个 mismatch 契约文件逐一验证 CRLF→LF 归一化后 SHA-256 = 对应 doc/plan/FEA-CONTRACT-FROZEN-<id>.md 记录的 pin；只读完成，输出入 verification/FEA-15-PIN-BASIS-ENFORCE-1/ac4-clone-t-pin-eol-normalization.log；任一不闭合立即停止并回报；
3) 前置 C2：按 Addendum A §A.2.3 新建 AC4 wrapper 前，先断言被测 clone 内 verification/FEA-15-PIN-POLICY-1/pin_inventory.py 与 pin_inventory_delta.py 的 SHA-256 与 2df8db7…/bfae0b9… 冻结源一致；不一致即停；
4) 执行 A.1 文件级对照（git diff --name-status bfae0b9… bf3777057… 路径集须精确等于 11 路径允许集）与 A.2 三层对照（R0 基准 inventory 在保留 R0 clone 生成；生成 R0→clone-T、R0→clone-F 两份行级 delta；clone-T 历史行差异逐行经 CRLF→LF 归一化闭合于 R0 对应行；REMOVED 行逐行归因；ADDED/CHANGED 行逐行归因允许集）；证据入 verification/FEA-15-PIN-BASIS-ENFORCE-1/（ac4-*.log 与 *.json），README 增补 AC4 段落，Linux 记 NOT_RUN；
5) 停止条件：偏离 T/F 预期锚的任何新 mismatch 或新失败、C1 归一化不闭合、diff 出现第 12 路径或 D 状态、generator SHA-256 与冻结源不一致——任一命中即停、保留现场、回报裁决；
6) 禁止不变：不改 18 frozen pins、.gitattributes、tools/governance/verify_pins.ps1 与任何历史字节；不 renormalize；不集成、不 close、不 push、不清理/prune/GC/repack；T/F 侧 FAIL 不改写为 PASS；Plan/STATUS 预算临界（LF 口径 6971/7000、3183/3200）如超预算须缩文或另获裁决，不得引用本裁决的 CRLF 归因豁免；
7) 完成后停：AC4 结果交新的独立 ZCode session 处置（主裁决 §7.5）；AC5 未释放。
```

## 六、诚实性边界

- 本裁决 session 全程只读：未改文件、未提交、未 push；裁决依据仅来自仓库文档、两份 `ac4-clone-{t,f}-gates-actual.log`、`ac2ac3-baseline-controls.log`、`verify_pins.ps1`/`check.ps1` 源码与 Task 卡既有记录。落盘动作本身按用户对本 session 的明确指示执行，仅创建本报告文件，未触碰 Task/STATUS/Plan/证据或任何冻结文件。
- T 侧 pins FAIL(16)、T 侧 check EXIT=1、F 侧 pins FAIL(2) 均保持原状态登记为 limitation/确定性效应；任何后续文档不得将其改写为 PASS。
- frontmatter session/turn ID 按落盘指示登记为用户提供值（`sess_d4df68bf-4fa3-4828-8ac6-47c25717be76` / `turn_a90afd6b-821e-4494-983b-a5da890dada1`）；伪造、篡改或回退为占位符均视为证据缺陷。
