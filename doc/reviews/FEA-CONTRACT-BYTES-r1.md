---
document_id: FEA-CONTRACT-BYTES-r1
kind: independent_review
task_id: task-29（FEA-PIN-CORRECTION 补核）
round: 1
scope: 4 份契约「冻结字节 vs 复核字节」差异的极窄复核（只核复核后新增/改动的行 + §1B 记载）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-29"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 45607a090
reviewed_head_full: 45607a0901d7d8c651ee6b2c6ffa40de4424e291
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 45607a090）；task-29 不存在，按 Lead 指令直接执行、报告名不变"
reviewed_documents:
  - doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md（v6，blob c188cf94…，== 冻结 pin ✓）
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md（blob 46573968…，== 冻结 pin ✓）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v4，blob 37586fb2…，== 冻结 pin ✓）
  - doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md（v5，blob d2cb8de4…，== 冻结 pin ✓）
  - doc/plan/FEA-CONTRACT-FROZEN-*.md（11 份 §1B）
reviewed_sha256:
  C-03: c188cf947cda971103a1ea17e1312ab6ce7ed27f0f734b975c6073a33ac1612e
  C-06: 465739684111bfa080ca71e684eccafd8c5162a5142a54dac5f8f898df4cbd3c
  C-08: 37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9
  C-13: d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c
baseline: "复核态：C-03 @ FEA-GOV-12-review（reviewed_head 2a540fcc3，blob 45063eaa）；C-06 @ FEA-GOV-6-c05-c06-r3（0b553d3ae）；C-08 @ GATE-CLOSURE-RULING-r8（0cd6d62e9，blob aa118d28）；C-13 @ FEA-C13-r4（4c69a27ba）；裁定 v2 R-1′/v6 R-4；用户裁决 U-03=B"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 3
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T10:02:42+08:00
captured_by: c01b-reviewer
---

# 独立复核：4 份契约「冻结字节 vs 复核字节」（补的那次极窄复核）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 3）。**

**4 份的差异行我逐行核了：语义方向全部在复核结论内，没有「顺手加别的东西」式越界；4 份当前字节与 pin 一致（`c188cf94…`/`46573968…`/`37586fb2…`/`d2cb8de4…` = 各自冻结 pin ✓）。**

**但按 Lead 自己给的判据（「§1B 记载准确」才能 approved），C-13 的 §1B 不准确**：它只写「U-03 段 + §9 条件 2 + 状态行」，而 r4 之后到冻结之间还发生了 **4 条 K 项内容修订**（K-1…K-4，v5 提交 `3a852340f`）——这 4 条在方向上没问题（就是我 r4 的建议），但 §1B 漏记，导致「冻结字节 vs 复核字节」这一步的账目又少了一页。

| 契约 | 差异行是否在复核方向内 | 有无越界新增 | §1B 记载是否准确 | 判定 |
|---|---|---|---|---|
| **C-03** | ✓（FEA-GOV-12 的 P2-1…P2-4） | ⚠ 映射「浮层→decorative」语义不准确（P2-1） | ✓（仅漏变更记录行，可忽略） | 方向 ✓ / P2×1 |
| **C-06** | ✓（裁定 v2 R-1′） | ⚠「缓存预算自含」超出裁定口径（P2-2） | ✓ | 方向 ✓ / P2×1 |
| **C-08** | ✓（裁定 v6 `:96`/`:100`） | **无** ✓ | ✓ | **干净** |
| **C-13** | ✓（r4 的 K-1…K-4 + U-03=B） | **无** ✓ | **✗ 漏 4 条 K 项修订（P1-1）** | 方向 ✓ / **P1×1** |

另：11 份 §1B 中 **C-01b 的「复核后到冻结的改动：无」不准确**（P2-3），其余 6 份与非 4 份均与实际相符。

---

## 2. 4 份逐份判定（差异行 → 复核方向 / 越界 / §1B）

核对方法：对每份取 `git diff <最后一次复核的 head>:<契约> HEAD:<契约>`，逐 hunk 对照对应复核报告/裁定的原文。

### 2.1 C-03（v6，冻结 pin `c188cf947cda…`）

| 实测差异行 | 复核来源 | 在方向内？ |
|---|---|---|
| 状态行 DRAFT→FROZEN v6 | 冻结动作 | ✓ 元数据 |
| `:866`→`:874`（补 `:1041`）两处 | FEA-GOV-12 P2-1（我原文：「`:866` 实为 `:874`；另 `:1041` 亦写…」） | ✓ |
| U-05c 补第三案 C（三案 A/B/C） | FEA-GOV-12 P2-2（「U-05c 选项不完整（缺第三种合理设计）」） | ✓ |
| §2.3 新增「与方案 r4 的命名映射」段 | FEA-GOV-12 P2-3（「三态/三类命名未映射」） | ✓（映射内容见 P2-1） |
| 兼容段新增「等价性限定（持久化值域 / overlay 加载失败瞬时不纳入）」 | FEA-GOV-12 P2-4（「旧 true 分支的加载失败路径未纳入等价性说明」） | ✓ |
| 变更记录 v6 行 | 处置留痕 | ✓ 元数据 |

**越界判断**：无新增义务/无新增判据；唯一问题是映射段的**语义准确性**（P2-1）。
**§1B**（`:24-26`）：「最后一次独立复核 v5 approved（FEA-GOV-12-review）/ 复核后到冻结的改动 v6 四处内容修订（行号/U-05c 案 C/命名映射/等价性限定）+ 状态行 / 需补极窄复核」——与实测一致 ✓（仅未单列变更记录行，属元数据，可忽略）。

### 2.2 C-06（冻结 pin `465739684111…`）

| 实测差异行 | 复核来源 | 在方向内？ |
|---|---|---|
| 状态行 DRAFT→FROZEN | 冻结动作 | ✓ |
| 条件③：「`G-CONTRACT` **关闭**」→「**对 C-06 不再构成阻塞**」（+授权面子集自述、lease 归属、缓存预算自含、未覆盖项、Gate 保持 OPEN、引 R-1′） | 裁定 v2 R-1′（我 r2 已 approved） | ✓ 主干一致；「缓存预算自含」见 P2-2 |

**越界判断**：
- `lease` 由 C-01b SC-25/29/31 承载——实核 ✓（`FEA-C01b_STORAGE_CONTRACT_DRAFT.md:84/88/95` 确为检测/重取/删除流程相关条款，lease 在其中）；
- 「重定位/同步、容器页映射 目前无承载条款，仍属 D05 未覆盖项」——与裁定「Gate 保持 OPEN 直至这些落地」一致 ✓；
- 「4 命令 + 9 条安全约束」——C-06 自身范围自述 ✓；
- **「缓存预算在本单 `budget{maxBytes,maxDecodeBytes}` 内自含」**——裁定原文是「D05 的 lease/重定位·同步/容器页映射/**缓存边界**由 C-01b、C-09 及后续契约分担」；此处把「缓存预算」划归本单，属**冻结前新增的覆盖判断**（见 P2-2）。`budget{…}` 本身是 `RequestSourceRead` 的既有请求字段（`:51`），不是新机制。
**§1B**（`:23-25`）：「r3 approved（FEA-GOV-6-c05-c06-r3）/ 条件③ 文本扩展（分担归属）+ 状态行 / 需补极窄复核」——与实测一致 ✓。

### 2.3 C-08（v4，冻结 pin `37586fb2bfd2…`）

| 实测差异行 | 复核来源 | 在方向内？ |
|---|---|---|
| 状态行 DRAFT→FROZEN v4 | 冻结动作 | ✓ |
| 前置（b）：「§8 taxonomy 例外说明」→「§8 taxonomy 例外 + **`:1119` retryable 证据规则例外**」 | 裁定 v6 `:96`（「§8 `:1119`/`:1122` 的例外说明」）与 `:100`（「§8 `:1119` 的 retryable 证据规则例外（C-08 三码的 retryable 为契约级提案值…）」）；r8 复核 approved；r7 我的 K-2/P2-1 曾指出缺失 | ✓ 精确对齐裁定 |
| 变更记录 v4：「处置裁定 r6 的 P1×2 + P2×5」→「**r6/r7 的 P1×5 + P2×8**」 | r6（P1×2/P2×5）+ r7（P1×3/P2×3）累计 = P1×5/P2×8 | ✓ 计数正确 |

**越界判断**：无。仅把裁定已批准的两处例外补进契约文本，未扩大语义。
**§1B**（`:22-24`）：「r8 approved（GATE-CLOSURE-RULING-r8）/ 前置（b）`:1119` 例外 + 变更记录 + 状态行 / 需补极窄复核」——与实测一致 ✓。

### 2.4 C-13（v5，冻结 pin `d2cb8de4dd79…`）

| 实测差异行 | 复核来源 | 在方向内？ |
|---|---|---|
| 状态行 DRAFT→FROZEN v5 / U-03=B | 冻结动作 + 用户裁决 U-03=B | ✓ |
| `:89` 裸 candidate → `RegionCandidate` | **FEA-C13-r4 的 K-2** | ✓ |
| `:102` 补 `schema.py:256-257` 指针 | **r4 K-1** | ✓ |
| `:181`「语义与既有 `LOCK_CHANGED` 对齐」→「保护位（含 manual 位）复用拒绝语义；`RegionLockSnapshot`（`ports.py:56-63`）只含三把区域级锁，实现需把 manual 位纳入快照比对（实现 Task 的 AC，不是改 `ports.py` 契约）」 | **r4 K-3** | ✓ |
| §7 C-04b 行补「SC-D12 是编辑层保护摘要，不接入删除 preflight（C-04b §4A L-1）」 | **r4 K-4** | ✓ |
| U-03 段改写（「⚠ 尚未裁决…」→「已裁决 B…本条款即最终口径」） | 用户裁决 U-03=B | ✓ 状态标注 |
| §9 条件 2 改写（「若裁决不同先修订再冻结」→「已裁决 B…口径一致」） | 同上 | ✓ 状态标注 |
| 变更记录 v5 行 | 处置留痕 | ✓ |

**越界判断**：无——4 条 K 项都是 r4 的建议原方向，措辞也未扩大义务（K-3 还明确了「不是改 `ports.py` 契约」）✓。
**§1B（`:24`）：「复核后到冻结的改动 = U-03 段 + §9 条件 2 改写（状态标注型，语义未变）+ 状态行」——与实际不符**：漏了上表 4 条 K 项内容修订（发生在 `3a852340f`「C-13 v5 处置 r4 的 4 条 K 项」，早于冻结提交 `050d80c0a`）。`§1B` 的用途正是「把差异显式化」，漏 4/6 处实质编辑会让读者误以为冻结只加了状态标注 → **P1-1**。

---

## 3. Findings

### P1

**P1-1 — C-13 §1B 漏记 4 条 K 项内容修订（冻结字节 vs 复核字节账目不完整）**
- 位置：`doc/plan/FEA-CONTRACT-FROZEN-C13.md:20-27`（§1B 表格行 `复核后到冻结的改动`）。
- 实测：r4（`4c69a27ba`）→ 冻结（`45607a090`）之间 C-13 共有 6 处改动 = 状态行 + 4 条 K 项（`:89`/`:102`/`:181`/§7）+ U-03 段 + §9 条件 2；§1B 只写了后两者。
- 影响：与本次修正的目的（把「冻结 ≠ 复核」的差异显式化）相反——最需要列出的内容编辑反而没列。内容本身无越界（见 §2.4），但记录不准确。
- 修法：§1B 改为「v5 的 K-1…K-4 四处内容修订 + U-03 段 + §9 条件 2 + 状态行」，或直接附 `3a852340f` 与 `050d80c0a` 两个提交的 diff 摘要。

### P2

1. **P2-1（C-03 映射语义不准确）**：`:49`「方案「浮层」→ `decorative`」。方案 r4 `:874` 的三类是 **page-transition/overlay/hover**；C-03 §2.3 三类是 `navigation`（页面切换/Tab）/**`feedback`（按钮 hover、状态变化）**/`decorative`（**背景渐变移动、粒子**）。→ 方案 **overlay（浮层过渡）与 C-03 `decorative`（装饰型环境动效）不是同一语义**；现文却给出一对一等价，且未加「语义近似」限定，会顺带得出「浮层动画按 `decorative` 在 `reduce` 下完全禁用」这一未经评估的行为结论。建议改为「方案 overlay 在本草案归入 `decorative`（语义近似：浮层过渡 vs 装饰动效；如需严格对齐应在实现 Task 细分）」，或注明 C-03 无 overlay 专类。
2. **P2-2（C-06 缓存预算口径）**：`:80`「缓存预算在本单 `budget{maxBytes,maxDecodeBytes}` 内自含」——裁定 v2 R-1′ 原文把「**缓存边界**」划给「C-01b、C-09 及后续契约分担」。`budget{…}` 是 `RequestSourceRead` 的既有字段（`:51`），说「其由本单定义」成立；但「缓存预算自含」是对 D05 覆盖面的**新判断**，与裁定的分工口径字面不一致。建议限定为「本单只含 **per-request 解码预算**；D05 的缓存边界（策略/淘汰/持久化）仍由 C-01b/C-09 分担」，避免后续 Gate 覆盖记账混淆。
3. **P2-3（C-01b §1B「无」不准确）**：`FEA-CONTRACT-FROZEN-C01b.md:26` 写「复核后到冻结的改动：**无（冻结前已 approved）**」；但冻结提交 `1017ea648` 对 C-01b 实际改了 6 行：状态行 + 边界声明改述（「未冻结」→「已于 2026-11-01 冻结…」）+ 新增「冻结执行记录」段（均元数据，非条款）。建议改为「仅元数据：状态行 + 边界声明改述 + 冻结执行记录」。
   （其余 6 份 §1B 与实际相符：C-02/C-05/C-07/C-11/C-12 = 仅状态行 ✓；C-04b = 仅状态行 + 变更记录 ✓。）

---

## 4. 治理（本次实跑）

- `check.ps1`：`PASS (3 warnings)`，EXIT=0（warning：9 个非终态 Task、`STATUS.md` 3185 B、`REBASELINE_PLAN.md` 6598 B）。
- `origin/main..HEAD` = 218（**未 push**）✓；`git status --porcelain` 为空 ✓。
- 被审 4 份契约当前 blob 与冻结 pin **逐一相符**（见 YAML `reviewed_sha256`，与记录 §1 pin 对比 4/4 一致）。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文；**task-29 不存在**，按 Lead 指令直接执行、报告名不变。
- **未参与** 4 份契约的冻结/修订（作者 = DSH）；我出具过 C-03/C-06/C-08/C-13 的复核报告（如实披露）。
- **利益披露**：C-03 的 v6、C-13 的 v5 修订内容来自我 FEA-GOV-12 与 FEA-C13-r4 的建议；本轮我按「冻结字节是否被复核覆盖、§1B 是否如实记账」标准核，未因「采纳我的建议」而放宽（C-13 §1B 漏记正是我判 P1 的原因）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 6. NOT_RUN

- 未运行程序/pytest；全部为 git 对象/文本 diff 比对结论。
- 未重核 4 份契约中**复核前就存在**的条款（只核复核后新增/改动的行）。
- 未核方案 r4 `:874` 三类与 C-03 三类的完整语义对齐（只按条款示例做语义判断，未查 Avalonia 实现）。
- 未核 C-06 `budget{…}` 在 D05 语义下的完整归属（只按裁定 v2 R-1′ 原文与 C-06 自身字段判断）。
- 未核 11 份记录中 §1A/§1B 之外的段落。
- 未核用户原始核账工单（按 Lead 给的 4 份差异清单定位后独立核对）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×3；4 份差异均在复核方向内、无越界，阻塞点为 C-13 §1B 漏记 4 条 K 项与 3 条 P2 措辞/记账）。
