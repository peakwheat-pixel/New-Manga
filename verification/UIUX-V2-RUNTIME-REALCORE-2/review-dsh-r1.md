# UIUX-V2-RUNTIME-REALCORE-2 — DSH 独立复核 r1

verdict: changes_requested

复核对象：`3d038732a`（Codex 交付，自标 partial）
复核人：DSH（未参与本轮实现；本卡 Owner 为 Codex）
复核依据：`git show 3d038732a`、`verification/UIUX-V2-RUNTIME-REALCORE-2/`（README、run-i29/report.json、test-*.log）、`doc/handoffs/UIUX-V2-RUNTIME-REALCORE-2-handoff.md`，以及本机复跑核对。

## 先确认做对的部分（不吝惜）

- **G4 达成，且实现方式正确。** `core_bridge.rs` 新增 `ascii_only_request_line()`：线上形式保持不变，一旦载荷含非 ASCII 就返回 `CORE_BRIDGE_NON_ASCII_PAYLOAD`，让"隐式全 ASCII 假设"变成**可见失败**而不是静默乱码；附定向单测。选择方案 (b) 而非统一转义的理由（该通道字段是 uuid/rev/sha，不该出现非 ASCII，出现即契约漂移）写在代码注释里，站得住。
- **G5 达成。** `Shelf.test.tsx` 补了 `commandOpen=true` 分支；vitest 60 files / 567 tests 全过（原 566 + 1）。
- **G2 的证据质量高于它的自评。** `run-i29` 的 S9 实际连续终止了 3 个 sidecar 进程（21752 / 34104 / 13868），第 3 次时设置页出现 `错误代码：CORE_UNAVAILABLE`、书架页出现 `✗失败 Core 连接异常 Core 不可用 0 部作品`，随后新 PID 50360 拉起、`coreReady=true`、`books=1` 读回。这是真实的故障注入与自愈，不是 mock。
- **诚实度合格。** commit message 自标 `(partial)`；交付说明明说"不能据此将 Task 标记为 done"；没有把 G1 说成达成。
- **未越界。** `git show --stat` 里没有 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`tauri.conf.json`。
- **未污染用户数据。** Codex 本轮 11:57 开工；`%LOCALAPPDATA%\New Manga` 下的 `library.db-wal/-shm` 时间戳是 11:12:30，早于它开工，是我本轮之前只读核查产生的，**不计入它的账**。

## 问题清单

| id | 严重度 | 位置 | 现象 | 依据 | 建议处置 |
|---|---|---|---|---|---|
| **R1** | **P1** | `apps/desktop/frontend/e2e/uiux-v2/run.mjs`（S8，约 L170-260） | G1 未达成，**且方法选错**：派发文本把它列为第一选项的 CDP `DOM.setFileInputFiles` 完全没采用，改为 PowerShell + `UIAutomationClient` 去驱动 Windows 原生文件对话框（找 HWND、找 filename 控件 ID 1148、模拟提交），最终失败 | `run-i29/report.json` S8 最后一条：`Error: native picker filename control unavailable: {... "filenameControl":3082134, "foregroundWindow":1116940, "dialogThread":8496 ...}`；`git show 3d038732a:...run.mjs` L177-253 全是 UIAutomation | 改用 CDP：`DOM.getDocument` → `DOM.querySelector('input[type="file"]')` → `DOM.setFileInputFiles`（由页面内的 `<input type=file>` 直接收文件，**不触发原生对话框**）。断言：导入后书架出现作品、Core 页数与 UI 一致、错误路径显示错误码 |
| **R2** | **P1** | `run.mjs`（S9） | G2 只断言了设置页与书架的 `CORE_UNAVAILABLE`；工作台、阅读器的错误态未覆盖，因此它自评"G2 部分达成" | `run-i29/report.json` S9 checks 只有 `settings-error` 与 `shelf-error` 两条 | 杀 sidecar 后依次切到四页，各页断言错误码可见（不是空白/假成功）；恢复后再断言四页各自回到正常态 |
| **R3** | **P2** | 产品布局（`pages/pages.css` / `ui/ui.css`） | **真实产品缺陷（本卡最有价值的产出）**：900×700 窗口下 `docWidth=1024`、`clientWidth=900`，横向溢出 124px。这不是脚本 bug | `run-i29/report.json` S10：`{"docWidth":1024,"clientWidth":900,"pageWidth":1024}`；同时 `blurLayers=2`、状态条可见、无重叠均通过 | **超出本卡"不改产品视觉"约束**，不在本卡修。单独立 Task（窄窗响应式 / 900px 断点），本卡只保留"发现 + 证据" |
| R4 | P3 | `verification/.../README.md` | `cargo test --release` 23 failed 被列为"未通过"，但没有说明原因是环境前置、也没有给出定向复跑方式；容易让人误读成回归 | `test-cargo-release.log`：`test result: FAILED. 146 passed; 23 failed`，失败全部落在 `library_bridge::tests::*`（6）与 `packaged_sidecar_tests::*`（12），报错为 `M2RC1_PYTHON must be explicitly set ...`、`M2RC1_PACKAGED_DIR` 类断言 | README 写明需要的 env（`M2RC1_PYTHON`、`M2RC1_PACKAGED_DIR` 等）与复跑命令；并单独贴出"本卡改动模块的定向测试 exit 0"证据 |
| R5 | P3 | `run-i29/report.json` | `checks[].status` 全是空串，每条断言的 PASS/FAIL 状态没落盘，只能靠文本猜 | 读取 report.json 时 `$_.checks | ForEach-Object { "[$($_.status)] ..." }` 输出全为 `[]` | 修 `record()`/`check()`，让每条断言带明确状态字段 |

## 复核者独立核实的两件事（避免冤枉实现者）

1. **23 个 Rust 失败不是本卡引入的回归。** 失败测试全部属于 `library_bridge`（需要 `M2RC1_PYTHON`）与 `packaged_sidecar_tests`（需要 packaged 环境变量）；Codex 本轮改动的 `core_bridge.rs` / `ac1_bridge.rs` 的测试**没有一条失败**，其新增定向测试 exit 0。
2. **未越界、未碰用户数据。** 见上文"先确认做对的部分"最后两条。

## 判定

`changes_requested`。理由：G1 完全未达成且方法走偏（R1），G2 覆盖不足（R2），另有三项证据/可读性问题（R4、R5）；G3 的部分失败里含一个**应单独立项的真实产品缺陷**（R3）。

**不能收口为 done。** 返修范围：R1、R2、R4、R5；R3 另立 Task。

## 可复现性判断

验收脚手架本身是可复现的：`node e2e/uiux-v2/run.mjs` 一条命令、隔离数据根、失败轮 `report.json` 入库、exe SHA 记录在案。S1–S7 连续多轮稳定 PASS。S8 的失败是**方法选择**问题（UIA 驱动原生对话框），不是脚手架不可用——改回 CDP 文件注入即可。
