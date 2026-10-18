# 裁决后执行预案（2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`ba6c309fe` · **本文件只做准备，未实施任何一项**

已有材料：`f001-disposition-options.md`（三方向）、`m2-c1-rev2.11-draft.md`（方向 A 的契约文本）、`pending-rulings-options.md`（四项处置）、`readiness-dependency-chain.md`（依赖链）。本文件补齐**其余方向的落地步骤**，使每项裁决后都能直接执行。

---

## 一、F-001 方向 B（回退命令注册）的精确步骤

**先决条件**：用户裁决「禁止范围优先于 AC1」。**若未裁决，不得执行本预案。**

### 步骤

| # | 动作 | 具体 |
|---|---|---|
| 1 | 回退 Tauri 三处注册 | `0f661f3c5` 中 `main.rs` 的 `PRODUCTION_COMMANDS` 条目、`generate_handler!` 条目、命令名白名单条目，以及 `library_bridge.rs` 的 `list_recycle_bin_books` trait 默认实现与 impl |
| 2 | 回退 Core 命令面 | `5edf207b8` 中 `core_service.py` 的 `if command == "ListRecycleBinBooks":` 分支与 `handle_list_recycle_bin_books` |
| 3 | **保留** | `393e5e7e1`（UI 失败不静默）—— 与命令是否存在**无关**，仍然正确且必要 |
| 4 | **改造** | `899b72b65` 的断路断言：从「命令**在**生产面」改为「命令**不在**生产面」+ 注释说明 AC1 因范围冲突未实施。**保留** Rust 侧断言的形式，只反转期望 |
| 5 | AC1 标记 | Task 中 AC1 保持 `[ ]`，并注明「因 AC1 与禁止范围冲突，按用户裁决不实施」 |
| 6 | Task 收口 | `status: in_review` → **`closed_with_limitations`**；`delivery_head` 固定到回退后的新 head |
| 7 | **另立承接 Task** | 「M2-C1 契约冻结：回收站读取命令」—— **必须**，否则 AC1 变成悬空项（参见 `dir4-exceeded-scan.md`）|
| 8 | 指针同步 | `STATUS` / `REBASELINE_PLAN` 记录新 Task 与收口 |

### 风险

- **回退会使回收站继续无法读取**（UI 会正确显示失败提示，但功能缺失）—— 这是方向 B 的**真实代价**，必须在收口记录中写明，不得含糊。
- 第 4 步的断言反转**不得删除测试**，只改期望方向（禁止范围明令「不得用删测试让 AC 通过」）。

---

## 二、AC5 的证据登记模板

**用户跑完 `run-desktop-close-verification.ps1` 后**，我按此登记：

| 字段 | 值 |
|---|---|
| AC | AC5 |
| 命令 | `pwsh -NoProfile -File "G:\CODEX\New Manga\verification\P20-CLOSE-BOUND-1\run-desktop-close-verification.ps1"` |
| 执行者 | **用户**（交互桌面；`GameInputSvc` 抢占前台使自动化不可信）|
| 时间 | （用户提供）|
| 退出码 | （用户提供的输出）|
| stdout | 存为 `verification/P20-CLOSE-BOUND-HARDEN-2/ac5-desktop-run.stdout.log` |
| sha256 | **按磁盘字节实算**（CRLF 检出）|
| 结论 | 据实际输出判定；**不得**由我代为判 PASS |

**若用户明示「无法执行」**：AC5 标注「因环境限制长期无法执行」，并提议 `P20-CLOSE-BOUND-HARDEN-2` 按 `closed_with_limitations` 收口（AC 6/7 + 1 项环境受限），**理由是让 AC5 无限期停在 `in_review` 正是 P22 与 P20-ISOLATION-1 的成因**。

---

## 三、`P22` / `P20-ISOLATION-1` 的收口文本要点

两者**形状不同，记录不得套同一模板**：

| 项 | `P22` | `P20-ISOLATION-1` |
|---|---|---|
| AC 状态 | **0/5**（一项都未勾）| **4/4**（全部完成）|
| review 规模 | 22 份文件，≥9 轮 | 3 轮（R1 7×P1、R2 6×P1、R3 3×P1+2×P2）|
| 卡点性质 | **实现未收敛** | **仅 review 未通过** |
| 收口记录须含 | 5 项 AC 为何全部未完成、缺陷面是否仍需 | **3×P1+2×P2 逐项列出**（引用 `codex-review-r3.md`）|
| 资产保留 | — | **7 个注入脚本**（`run-r010-ac3-real-injection.ps1` 等）必须保留 |

**两者共同的收口动作**：`status` → `closed_with_limitations`；在 `STATUS.md` 保留项**显式列出**；如需续做，**另立承接 Task**（不得在原 Task 内续轮，那会再次违反 DIR-4）。

---

## 四、`P20` / `ARCH-DOC-REBASELINE` 的改派与阻塞文本

### `P20` 改派（照 HARDEN-2 先例）

```yaml
suggested_owner: dsh
owner: dsh
reviewer: Codex          # 保持不变，确保 owner != reviewer
```

正文加「执行方改派（2026-10-19 用户指令：本对话不再调用 agy）」一节，格式与 `P20-CLOSE-BOUND-HARDEN-2`、`P09-AC3-DELETE-HARDEN-1` 的既有改派记录一致。

### `ARCH-DOC-REBASELINE` 标 blocked

```yaml
status: blocked
blocked_reason: 其 AC5 裁决被 P20 关闭前置（Task 自述的解除条件）；AC4–AC6 属消费者责任
```

**理由**（来自 `readiness-dependency-chain.md`）：其**最后的动作被 P20 锁住**，改派给任何人都无法推进 —— **`blocked` 比名义 `ready` 诚实**。

**注意**：该 Task 的 AC7 **本身已完成**（三项构成全达成），其 `[ ]` 标的是**整 Task 未完成**（AC7 原文「某项未完成不标整 Task done」）。**收口记录不得写成「AC7 未完成」** —— 那是错的。

---

## 五、本文件性质与准备工作清单

**只读准备，未实施**：未改任何 Task 的 `status`/`owner`/`reviewer`，未回退任何提交，未改契约，未触碰 `PLAN`/`STATUS`。

**至此已备好的材料（全部入库）**：

| 文件 | 覆盖 |
|---|---|
| `verification/P09-AC3-DELETE-HARDEN-1/f001-disposition-options.md` | F-001 三方向 + 代价 |
| `verification/P09-AC3-DELETE-HARDEN-1/m2-c1-rev2.11-draft.md` | 方向 A 的契约文本 |
| `verification/P20-CLOSE-BOUND-HARDEN-2/pending-rulings-options.md` | 四项处置方案 |
| `verification/P20-CLOSE-BOUND-HARDEN-2/readiness-dependency-chain.md` | 依赖链（链头 = P20 AC4）|
| `verification/P20-CLOSE-BOUND-HARDEN-2/dir4-exceeded-scan.md` | 超限滞留扫描 |
| `verification/P20-CLOSE-BOUND-HARDEN-2/antigravity-owned-tasks-inventory.md` | Owner 波及范围 |
| `verification/P20-CLOSE-BOUND-HARDEN-2/p02-untracked-reference-inventory.md` | P02 引用盘点 |
| **本文件** | **方向 B / AC5 / 收口 / 改派 的落地步骤** |

**这意味着：五个待裁决项中的每一项，现在都已从「需要设计的开放问题」变成「一个字母或一句话」。** 我本人已无可自主推进的执行工作。
