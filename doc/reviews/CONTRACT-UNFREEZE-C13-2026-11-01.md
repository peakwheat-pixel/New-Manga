# CONTRACT-UNFREEZE-C13-2026-11-01（SC-D11 适用范围修订）

**载体类型**：UNFREEZE 记录（冻结契约的字节修订留痕）
**日期**：2026-11-01
**执行人**：DSH（Lead / Architect / Integrator）
**任务**：[FEA-03](../tasks/FEA-03.md)（草稿与保护协调）
**触发**：FEA-03 范围复核 r1/r2（[r1](FEA-03-scope-r1.md) P0-01、[r2](FEA-03-scope-r2.md) P0-01）——C-13 SC-D11 `:151-153` 要求「新旧路径统一去重键」，与已冻结的 `V11R_REGION_WRITE_CONTRACT` C073（旧保存路径 append-only、非幂等、不静默去重）直接冲突；FEA-03 无法在不违反任一冻结契约的前提下实现。

---

## 1. 为什么需要 UNFREEZE

C-13（草稿与保护）于 2026-11-01 冻结（v5，pin `d2cb8de4…`）。其 SC-D11「旧非幂等写兼容」写有两处明文：

> - 新旧路径**不得双写产生两个 revision**：无论走新 token 还是旧路径，都以最终去重键 `(RegionId, BaseRevisionId, 内容摘要)` 判幂等；
> - **最终去重键统一为 `(RegionId, BaseRevisionId, 内容摘要)`**——新 token 路径与旧路径都以它为最终判据（token 只防重放，不单独决定去重）；
> - **验证**：同一内容先后走旧路径、新路径 → 断言只产生一个 revision。

而 C073（`V11R_REGION_WRITE_CONTRACT`，FROZEN v1.5）对**同一保存路径**（`src/application/editing/service.py` 用户保存）规定 append-only、非幂等、**不静默去重**（`service.py:1244` 注释明写"同文两次保存产生两个 revision"）。

两者是**同一代码路径的相反要求**：任一实现都必然违反另一份冻结契约。按 C-13 冻结记录 §1 与 §1A 纪律，修订必须走 `CONTRACT-UNFREEZE-<DATE>` 载体 + 重新独立复核 + 重新冻结，**不得只重算 pin**。

## 2. 修订内容（只动 SC-D11 的适用范围，不动其它条款）

在 C-13 草案 SC-D11 末尾**追加**修订段（原文保留，不改字）：

> **修订（CONTRACT-UNFREEZE-C13-2026-11-01）**：本条「统一去重键」的约束范围**限定为新 token 路径**。旧保存路径（`editing/service.py:1239`）在过渡期保持既有 **append-only / 非幂等**语义（由 `V11R_REGION_WRITE_CONTRACT` C073 承载），本契约**不要求旧路径去重**，也不因本契约引入而改变旧路径行为；新旧路径的统一去重由独立 follow-up Task 在 C073 与本契约协调后实施（本修订不改 SC-D01…SC-D10、SC-D12）。

同时状态行由 `FROZEN v5` 更新为 `FROZEN v6 / SC-D11 适用范围经 CONTRACT-UNFREEZE-C13-2026-11-01 修订`。

**语义变化边界**：
- 旧路径：**行为完全不变**（append-only；同文两次 = 2 revision）；不再要求"旧路径也去重"。
- 新 token 路径：`(RegionId, BaseRevisionId, 内容摘要)` 去重键**仍然有效**（C-13 SC-D11 的原意保留），token 仍只防重放。
- 未改：SC-D01…SC-D10、SC-D12、§7 接口、§8 Gate 关系、§9 冻结条件。

## 3. 字节与 pin

| 项 | 值 |
|---|---|
| 修订前（v5，冻结字节） | `d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c` |
| 修订后（v6，本次） | `8faf1e805eac500ab20037d8628b8594f8720e455387a85639897f1127afd45c` |
| 改动范围 | ①状态行（版本标注）②SC-D11 末尾追加修订段；其余字节未动 |
| 校验 | `verify_pins.ps1` 的 C13 期望值由冻结记录读取，随冻结记录更新后自动复验 |

## 4. 复核与重冻

- **复核**：本载体 + 修订后 v6 字节随 FEA-03 范围复核 r3 一并送上下文独立复核（`doc/reviews/FEA-03-scope-r3.md`）；复核须确认「改动仅在 SC-D11 适用范围与状态行、无越界新增」。
- **重冻**：复核通过后，冻结记录更新为 v6 + 新 pin（本记录 §5 落表）。
- **不构成**：本载体不构成实现授权、不构成 Gate 关闭、不构成 push 授权；`G-DELETE-IMPL` 仍 OPEN。

## 5. 冻结记录更新（复核通过后生效）

| 项 | 旧 | 新 |
|---|---|---|
| 版本 | v5 | **v6** |
| pin | `d2cb8de4…` | `8faf1e80…` |
| §1B 复核 | r4 approved（v5） | **r3（FEA-03 scope）对 v6 修订范围复核** |

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：SC-D11 适用范围修订（旧路径不打折 C073；统一去重键限新 token 路径）；pin v5→v6；随 FEA-03 范围 r3 复核 | DSH |
