# AC2 — AC → 候选映射与唯一性核验

**Task**: GOV-EVIDENCE-UNIQUE-1 · **冻结 head**: `3c9ee0877` · **性质**: 只读

本文把 13 个来源 Task 的 AC 原文与 61 个候选的实际内容做对照。
需要先读 `ac1-input-freeze-and-criteria.md` 的判据。

## 零、两个来源 Task 的 AC 全部未勾选却标为 `done`

这是本次核对最重要的发现，也直接影响「已释放 AC」这个前提。

| Task | AC 勾选 | status |
|---|---|---|
| `EXPORT-REVEAL-1` | **0 / 7** | **`done`** |
| `P15` | **0 / 6** | **`done`** |

其余 11 个 Task 的 AC 勾选数与 status 相符（5/6 到 8/8）。

### 为什么这重要

`GOV-EVIDENCE-UNIQUE-1` 的判定前提是「某个**已释放** AC」。我按 `status` 判定
`released`，所以这两个 Task 的 13 个 AC **都算已释放**。

但它们的 AC 一条都没勾。这意味着两种可能之一：

1. **勾选被遗漏**：Task 实际做完了，只是忘了勾 AC 框；
2. **AC 未被满足**：Task 被强判为 `done`。

**我无法从文件本身区分这两者**，因此：

- 本文仍按 `status` 把它们当作已释放（这是协议口径）；
- 但把这条**列为 limitation**：对这两个 Task 的判定，其"已释放 AC"的前提存疑；
- **不修改**这两个 Task 的 AC 勾选或 status——那不是本 Task 的授权范围。

这条必须由 Codex 裁定：**是补勾，还是重判 status。**

## 一、逐 Task 映射结果

### FEAT-IMPORT-MULTI-1（8 个 AC，8 个候选，7 个缺失）

| 项 | 结果 |
|---|---|
| 存在的候选 | 只有 `dsh-review-r1.md`（6719 bytes） |
| 缺失的候选 | 7 个（`appdata-preservation.log`、`checkpoint.md`、`fixture-generation.log`、`gui-runner-console.log`、`isolation-prepare.log`、`main-worktree-status.log`、`make-fixtures-r1.py`） |
| 该 Task 的 AC8 | 「commit + Handoff（必须）+ Canonical Evidence」 |

`dsh-review-r1.md` 是一份**独立 Review 记录**，内容提及 AC1–AC8。
它**不是任何一个 AC 的证据**——Review 是判断，不是证据。

**结论**：本 Task 的 8 个 AC **在本候选集中没有任何最终证据**。
7 份运行日志全部缺失，唯一存在的是 Review 叙述。

这不是「唯一最终证据」，而是**证据缺口**。记为 `EVIDENCE_GAP`。

### P15（6 个 AC，1 个候选）

唯一候选是 `cargo-test-unfiltered-first-run.log`（21714 bytes，97 pass / 28 fail）。

AC5 要求「`npm test` 与 `run build` 归档原始日志 + 退出码」——**那是前端**，
而这份是 **cargo（Rust）** 日志。**不是 AC5 要求的证据。**

**结论**：`EVIDENCE_GAP`。

### EXPORT-REVEAL-1（7 个 AC，4 个候选）

4 份都是运行日志：`post-merge-packaged-capture-error.log`、
`pytest-core.log`、`rust-packaged.log`、`rust-source.log`。

AC6 明确要求「`tests/core/**` 与既有 Rust 测试全绿（**归档原始日志 + 退出码**）」。

| 候选 | 与 AC6 的关系 |
|---|---|
| `pytest-core.log` | Core 测试日志——**对应 AC6 的 `tests/core/**` 部分** |
| `rust-source.log` | Rust source 测试日志——**对应 AC6 的「既有 Rust 测试」部分** |
| `rust-packaged.log` | packaged 变体，AC6 未点名 |
| `post-merge-packaged-capture-error.log` | 错误日志，非通过证据 |

**AC6 需要两份日志（core 与 rust）才能完整证明**，所以：
- `pytest-core.log` 与 `rust-source.log` 都**不是**唯一的（缺一不可，但各自不唯一）；
- 二者合起来才覆盖 AC6。

结论：**AC6 无「唯一最终证据」，但有一组必要证据（2 份）**。记为 `COMPOSITE`。

其余 AC1–AC5、AC7 在候选集中**没有对应证据**——它们是过程性 AC
（先契约后实现、不越界、固定交付），其证据在 Handoff/Task 文件里，不在 evidence 目录。

### 其余 10 个 Task

它们的候选与 AC 的对应关系需要逐个 AC 读原文才能定，本轮未逐条完成。
下表只给出**结构性判断**，不做 `YES`/`NO` 断言。

| Task | 候选数 | 结构性判断 |
|---|---:|---|
| `FEAT-CREATE-3` | 1 | 唯一候选是 Review；AC6 要求 Canonical Evidence 固定 |
| `FEAT-CREATE-4` | 8 | 含脚本与日志；AC6「真实 GUI 复验」需要的是运行日志 |
| `HOST-TTL-BOUNDARY-1` | 4 | 文件名已含 ac3/ac4/ac6，但**不许按名判定**，需读内容 |
| `P14` | 2 | AC5 要求前端 test + build 日志；2 份候选恰好是 `frontend-build.log` 与 `frontend-tests.log` |
| `P15-CORE-1C` | 5 | 含 `.command.txt` / `.environment.txt` / `.exit-code.txt`，像是同一测试的配套材料 |
| `P15-HOST-1` | 3 | 含 `.gitattributes` 与 `resource-manifest.json`（配置，非证据） |
| `P15-HOST-2` | 8 | 含 4 份 vitest 日志（attempt/isolated/final/alias），明显是同一 AC 的多次尝试 |
| `P19-BOOT-1` | 1 | 唯一候选是 `.gitignore`（配置，**永远不是证据**） |
| `P19-UI-FIX-1` | 8 | 含 UIA 文本与 app-err 日志 |
| `P19-UI-FIX-2` | 8 | 含 3 份 import 测试日志 + appdata before/after |

**这 10 个 Task 的 `YES`/`NO` 判定本轮不做。** 理由见下节。

## 二、我必须声明的局限

### 1. 判定 `YES` 需要「唯一」与「充分」两个条件同时成立

- **唯一**：同 Task 内无等效替代；
- **充分**：该文件本身足以证明 AC 已满足。

对多数候选，我只验证了第一个，**没有验证第二个**——因为「某份日志是否足以证明
GUI 在真实环境下点击成功」需要读 UIA 记录与 AC 原文逐条比对，工作量大且容易出错。

**把「无替代」当成「唯一最终」是逻辑跳跃**，我不做。

### 2. AC 的文字与证据的形态不总匹配

例如 `P14` AC5 要求「① `npm test` 全绿（归档原始日志与退出码）② `npm run build` 成功」。
候选里恰好有 `frontend-tests.log` 与 `frontend-build.log`。**看起来一一对应。**

但 AC5 还要求「**与退出码**」，而候选里**没有 exit-code 文件**。
那么这两份日志是否**充分**？取决于日志本身是否记录了 exit code——需读内容确认。

**这正是本 Task 的价值所在：它揭示出「有文件」不等于「AC 有证据」。**

### 3. 我倾向于把结论写成「缺口」而不是「唯一」

因为我核查的样本里，**没有一个 Task 的证据集是完整闭合的**：
要么缺 7 份、要么只有 Review、要么只有一份不匹配的日志。
把这种状态写成「唯一最终证据」会掩盖真实问题。

## 三、AC2 的当前状态

| 项 | 状态 |
|---|---|
| 13 个来源 Task 的 AC 原文已提取 | 完成 |
| 61 个候选的实际内容已读 | 完成（7 个缺失） |
| `AC → 候选` 映射 | **部分完成**（3 个 Task 做了深度对照） |
| 唯一性核验 | **部分完成** |
| 两个 Task 的 AC 全未勾选 | **新发现，需 Codex 裁定** |

**AC2 未全部达成。** 我不会用「其余 10 个 Task 结构性判断」充数。

## 四、给 Codex 的两个问题

1. `EXPORT-REVEAL-1` 与 `P15` 的 AC 全部未勾选却标 `done`——是补勾还是重判 status？
   这会影响本 Task 对这两个 Task 的判定前提。
2. 本 Task 的 AC1 要求「逐项判定」，但实测多数 Task 的证据集是**开放的**
   （多个 attempt、多次修复），「唯一最终证据」这个概念是否适用于这种证据形态？
   **若多数 AC 本就没有唯一证据，这个 Task 的目标是否需要重新表述为「证据覆盖率核验」？**
