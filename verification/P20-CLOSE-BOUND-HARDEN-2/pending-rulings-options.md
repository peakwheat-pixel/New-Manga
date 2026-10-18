# 待裁决事项的处置方案（2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`e5adef5bd` · **本文件只做准备，未实施任何一项**

F-001 的方案已单独写在 `verification/P09-AC3-DELETE-HARDEN-1/f001-disposition-options.md`。本文件覆盖其余三项，同样只做准备。

---

## 一、`P22` 收口（22 份 review 未收敛）

**现状**：`status: in_review`；`owner: Antigravity`；`reviewer: DeepSeek Harness`；`delivery_commit: 92093792ba0bc653f9423dda2486d558226caf86` 已固定；**AC `[x]=0 / [ ]=5`**（5 项全部未勾选）；证据目录 22 份 review 文件（2026-10-10）。

**判据**：**远超 DIR-4 的 2 次上限**，且 **AC 一个都没勾上**说明 9 轮以上复审**没有收敛**，不是"差最后一轮"。

**方案（照既有先例）**：

| 步骤 | 动作 |
|---|---|
| 1 | `status: in_review` → **`closed_with_limitations`** |
| 2 | 记录：22 份 review 未收敛，达 DIR-4 上限后无承接；**5 项 AC 全部未完成** |
| 3 | 在 `STATUS.md` 保留项**显式列出**（防止再次静默滞留） |
| 4 | 如需继续该缺陷面，**另立新 Task 承接**（不可在本 Task 内续做第 23 轮） |

**先例对照**：`P09-AC3-DELETE-1`（R3 超限）→ `closed_with_limitations` + `P09-AC3-DELETE-HARDEN-1` 承接；`P20-CLOSE-BOUND-HARDEN-1`（R4 超限）→ 同构。**`P22` 形状完全一致，只是轮次更多、更早被遗忘。**

**替代方案**：若你认为该缺陷面**不再需要**（P22 是 `同通道 round_trip 响应归属串行化修复`，其上游 `M2-PAGE-NAV-PROJECTION-1` 可能已使问题消失），则直接 `closed_with_limitations` 且**不另立承接 Task**，并在记录中写明"缺陷面经评估不再需要"。

---

## 二、`P20-ISOLATION-1` 收口（3 轮 `changes_requested`）

**现状**：`status: in_review`；`review_status: changes_requested（R1 7×P1、R2 6×P1、R3 3×P1+2×P2）`；**AC `[x]=4 / [ ]=0`**（实现完成）；`delivery_head: baf4ec90c`。

**关键区别（与 P22 不同）**：**AC 已全部完成**，卡的是 **review 未通过**。且有 **`depends_on: [P20]`**，而 `P20` 本身仍在 READY（Owner 亦为 Antigravity）。

**方案**：

| 步骤 | 动作 |
|---|---|
| 1 | `status: in_review` → **`closed_with_limitations`** |
| 2 | 记录：AC 4/4 完成；3 轮 review 均为 `changes_requested`，达 DIR-4 上限；**未闭合的 3×P1+2×P2 逐项列出** |
| 3 | 如需继续，**另立承接 Task** 并引用 `codex-review-r3.md` 的 finding 清单 |
| 4 | 在 `STATUS.md` 保留项显式列出 |

**注意**：该 Task 的 **7 个注入脚本已入库**（`probe-fault-isolation-backend.ps1`、`run-ac6-ui-verification.ps1`、`run-r004-timeline.ps1`、`run-r010-ac3-real-injection.ps1` 等），**无论是否收口都应保留** —— 它们是故障注入能力的既有资产。

---

## 三、`P20` / `ARCH-DOC-REBASELINE` 的 Owner

**现状**：两者 `status: ready`，`owner: Antigravity`；用户已停用 agy → **READY 列表当前无一可派**。

**方案（照 HARDEN-2 先例）**：

| 项 | 改法 |
|---|---|
| `owner` | `Antigravity` → **`dsh`** |
| `suggested_owner` | 同步改为 `dsh`（并注明改派理由） |
| `reviewer` | **保持不变**（`P20`: Codex；`ARCH-DOC-REBASELINE`: DeepSeek Harness）以确保 **owner ≠ reviewer** |
| 正文 | 加一节「执行方改派（2026-10-19 用户指令：本对话不再调用 agy）」，与 `P20-CLOSE-BOUND-HARDEN-2`、`P09-AC3-DELETE-HARDEN-1` 的既有改派记录格式一致 |

**改派前必须先评估工作量**（我的建议）：`P20` 涉及发布 Gate 与四个一级页面，`ARCH-DOC-REBASELINE` 的 AC4–AC6 按 STATUS 记载「属消费者责任」—— **改派后可能仍有部分无法由我完成**。因此建议：

- **先只读评估两者的剩余 AC 与阻塞性质**，再决定改派还是标 `blocked`
- 若评估显示**大部分 AC 可自主完成** → 改派 dsh
- 若**大部分 AC 依赖他人** → 标 `blocked`（原因：Owner 已停用且剩余项非执行方可完成），比名义 `ready` 更诚实

**替代方案**：保持 `ready` 不动，由你统一处置 Antigravity 名下全部 13 个非终态 Task（参见 `antigravity-owned-tasks-inventory.md`）。缺点：READY 列表继续名不副实。

---

## 四、`AC5`（交互桌面验证）

**这是唯一必须由人执行的项**，无替代方案。

```powershell
pwsh -NoProfile -File "G:\CODEX\New Manga\verification\P20-CLOSE-BOUND-1\run-desktop-close-verification.ps1"
```

**背景**：Windows 的 `GameInputSvc` 会间歇性抢占前台，使 `SetForegroundWindow` / `bring_to_front` 失效，**只有人类点击能可靠恢复** —— 因此自动化无法可信完成此项。

**预期**：脚本会运行真实关闭流程并产出日志。**把输出贴回即可**，我会据此登记证据、勾选 AC5、把 `P20-CLOSE-BOUND-HARDEN-2` 推进到收口。

**若无法执行**：请明示，我会把 AC5 标注为「**因环境限制长期无法执行**」，并据此提议该 Task 按 `closed_with_limitations` 收口（AC 6/7 + 1 项环境受限），**而不是让它停在 `in_review`** —— 那正是 P22/P20-ISOLATION-1 的成因。

---

## 五、本文件性质

**准备工作，非实施**。未改任何 Task 的 `status` / `owner` / `reviewer`，未触碰 `REBASELINE_PLAN` / `STATUS`，未回退提交，未删改历史 pin。目的是把四个待裁决项各自压缩成**一个可以点头的动作**。

**贯穿性提醒**：`P22` 与 `P20-ISOLATION-1` 的存在证明「超限后缺强制收口路径」；**若裁决其中任一项，请一并决定是否登记该流程要求**（详见 `dir4-exceeded-scan.md` §5），否则同样的滞留会再次发生。
