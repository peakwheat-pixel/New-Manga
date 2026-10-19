# AC1 — 逐 AC 溯源

**Task**: GOV-SOURCE-RECORDS-1 · **性质**: 记录维护 · **基线**: `32f95fdf9`

判据：每个 AC 必须有**书面依据**（Canonical Evidence 的 AC/Gate 标注、
Closeout Record 的记账、或 Handoff），不得凭 `status: done` 推定。

## EXPORT-REVEAL-1

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **`MET`** | Canonical Evidence `EXPORT-REVEAL-CONTRACT` 的 AC/Gate 列标为 **AC1**（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`，commit `b1e4d87d4`）；「交付与运行记录」记载 contract rev 2.4 与 production-only host command 实现先于测试完成。 |
| AC2 | **`MET`** | 「交付与运行记录」记载「contract rev 2.4 与 production-only host command 实现先于测试完成；实现固定 commit `5f95aac0f`」；`EXPORT-REVEAL-ALLOWLIST-REFUSALS` 覆盖 allowlist 断言。 |
| AC3 | **`MET`** | 「交付与运行记录」记载使用了官方 `tauri-plugin-o…`（dialog/opener 系列）并在 Handoff 说明理由；Closeout 的 `NIT` 未涉及非官方依赖。 |
| AC4 | **`PARTIAL`** | **① 与 ② 达成**：`EXPORT-REVEAL-ALLOWLIST-REFUSALS`（AC/Gate = AC4-①/②）记录生产面存在、probe 面不存在的 allowlist 断言与拒绝面测试。**③ = `BLOCKED`（原样保留）**：Closeout 原文「真实『成功导出 → reveal → 文件管理器打开』未跑通：测试 fixture 无有效 book，且无头 Windows 无法取得 WebView2 窗口句柄（`0x80070578`）」，对应证据 `EXPORT-REVEAL-FROZEN-ATTEMPT` 与 `EXPORT-REVEAL-GUI-BLOCK`。 |
| AC5 | **`MET`** | Closeout 记载「语义冲突解决与 §5.8 未变核验见 `verification/EXPORT-REVEAL-1/merge-resolution.md`」；该文件登记为 `EXPORT-REVEAL-POST-MERGE-RESOLUTION`（AC/Gate = Integration）。 |
| AC6 | **`MET`** | `EXPORT-REVEAL-CORE-TESTS`（AC6）与 `EXPORT-REVEAL-RUST-PACKAGED`（AC4-③/AC6）分别为 Core 与 Rust 测试日志；Closeout 记载合并后重跑 **source 88 passed / 0 failed / 1 ignored**、**frozen 打包 10 passed / 0 failed**。 |
| AC7 | **`MET`** | `EXPORT-REVEAL-POST-MERGE-HANDOFF`（AC7）为合并后 Handoff；Closeout 记录固定 commit、`--no-ff` 三方合并、delivery_head 按 BL-15 冻结。 |

小计：`MET` 6 / `PARTIAL` 1 / `UNKNOWN` 0（共 7）

## P15

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **`MET`** | Canonical Evidence `E6`（AC/Gate = **AC1/AC2**）为 `apps/desktop/frontend/src/settings/SettingsPage.test.tsx`；`E1`（AC1–AC5）为前端套件日志；`E8`（AC1–AC6）为独立 Review。 |
| AC2 | **`MET`** | 同 `E6`（AC1/AC2）。Closeout 逐项验证记载「只开放契约 §7 清单内 **4 个面**（Provider+Capability / Network / SFX），**11 个禁用分区逐条**『可见/不可操作/有原因』」。 |
| AC3 | **`MET`** | `E7`（AC/Gate = **AC3**）为 `client.p15.test.ts`，即 wire/Secret 反例断言源；Allout 的 `RV-P15-01` 判定 `client.ts` 的 `Error.message` 不构成泄露。 |
| AC4 | **`MET`** | `E1`（AC1–AC5）前端套件 + `E8`（AC1–AC6）独立 Review；Closeout 记载独立 Reviewer 工作树亲手复跑 **28 files / 274 tests passed**。 |
| AC5 | **`MET`** | `E2`–`E5` 全部标注 AC/Gate = **AC5**（前端构建、Core 回归、Rust source、Rust packaged）；Closeout 记载 BL-17 包含性逐条成立。 |
| AC6 | **`MET`** | `E8`（AC1–AC6）为独立 Review；Closeout 记载「固定 commit + Handoff + Canonical Evidence，sha256 按磁盘字节」，并更正了 `RV-P15-04` 的 LF/CRLF pin 问题。 |

小计：`MET` 6 / `PARTIAL` 0 / `UNKNOWN` 0（共 6）

## 结论

- `EXPORT-REVEAL-1`：**6 个 MET + 1 个 PARTIAL（AC4）**。
  AC4 的 ①/② 有证据，**③ 为 `BLOCKED`**，因此 AC4 **保持未勾选**并加注。
- `P15`：**6 个全部 MET**，全部补勾。

**合计补勾 12 项，保留 1 项未勾（`EXPORT-REVEAL-1` AC4）。**

