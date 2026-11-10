---
task_id: FEA-14-READ-1
reviewer: fresh 独立上下文子 agent（续接 r1；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 82ea7ca82
reviewed_head: d0b77ed1a
decision: changes_requested
---

# Review：FEA-14-READ-1（r1 处置后复核，r2）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `d0b77ed1adffeeeabe3f853886dc3e0c3659f274`**。审查开始 `2026-11-10T13:15:58+08:00`、结束 `13:17+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`a44c631cb..d0b77ed1a`，**10 文件**（Host/IHost/CoreClient 各 1 行默认值、inventory/pin/UNFREEZE、卡面、r1 报告、`reading_export.py` 页面口径、storage 测试）。全部 ⊆ READ-1 allowed_paths（OUT=0）。
- 按用户要求 front-matter 记 base `82ea7ca82`；但 `82ea..a44c` 仍无 src/apps 代码，实际实现起点是 `f9bf922aa`（卡面 `base_commit` 已改 f9bf）。本报告比较 r1→r2 处置并核对 head 代码。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/定向日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-1-r2\`。

## 1. 结论

**`changes_requested`**（P0=0 / **P1=1** / **P2=2** / **P3=3**）。

页面口径在 **store** 层确实修好（2 页 100% 测试通过），但 **wire handler 没有同步修改**：`core_service.handle_get_book_reading_progress` 仍读 `completed_chapters`/`total_chapters`，所以 P14 的 `read_pages/total_pages` 仍是章节数——**r1 的 P1 仍在**。P10 partial patch 的修复也没有落到 `service.py`（无该文件 diff），卡面“已修”与代码不符。P15 默认 confirm 已改 false，inventory 合计/pin 已修，allowed/base 已补。

## 2. r1 findings 关闭判定

| r1 ID | r1 级别 | r2 判定 | 依据 |
|---|---|---|---|
| R-001 | P1 | **PARTIAL（P1 仍未关闭）** | `reading_export.py:627-666` 已按页面统计（pages JOIN、percent×chapter_pages、deleted 页排除、0 页边界），storage 测试断言 2 页 100%；但 **`src/bootstrap/core_service.py:5085-5088` 未改**，仍把 `completed_chapters` 写 `read_pages`、`total_chapters` 写 `total_pages`，`finished` 也按章节相等；wire P14 仍是章节口径（R2-001） |
| R-002 | P2 | **PARTIAL（P2）** | P15 `confirm` 默认已在 IHostController/HostController/CoreServiceClient 改 false；但 P12/P15 Host 返回类型（`Task<string?>`/`Task<int>` vs PREQ `Task<BookmarkInfo?>`/`Task<bool>`）、P15 请求键 `confirm` vs `confirm_token?` 只是“登记偏差”，AC5 仍写「按 PREQ §8 形状」MET，不一致（R2-002） |
| R-003 | P2 | **CLOSED** | P15 三处默认 `confirm=true` 均已改 false（diff 三处 1 行）；Core 的 `confirm=False` 拒绝逻辑未变 |
| R-004 | P2 | **OPEN（P2）** | 卡面称 P10 partial patch 已修，但 `src/application/reading/service.py` 无 diff：`save_preferences` 仍对缺省字段使用默认值（`:549-582`），partial 保存仍会把未提供字段重置；无 partial 测试（R2-003） |
| R-005 | P2 | **CLOSED** | inventory 合计改 **68**；`generate_api_inventory.py --check` EXIT 0（渲染 61/68 与文档一致）；C-07 pin 改 `59ab90f7…`；`verify_pins` 18/18 |
| R-006 | P2 | **PARTIAL（P3）** | UNFREEZE 记录新 pin 已填 `59ab90f7…`，但同段仍写 **`vverify_pins`**（多一个 `v`），未修干净 |
| R-007 | P2 | **CLOSED** | allowed_paths 已补 `doc/reviews/CONTRACT-UNFREEZE-*.md`、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py`；`a44c..d0b` 10 文件 OUT=0 |
| R-008 | P2 | **CLOSED（范围注记）** | 卡面 base 改 `f9bf922aa`；但用户给的 base `82ea7ca82` 仍在实现之后，`82ea..a44c` 无代码。报告按用户 base 记，实际审 f9bf..head；建议 DSH 在 Task/交接中统一 |
| R-009 | P3 | **OPEN（P3，登记未补）** | Reader 定向 70 仍无独立日志；`dotnet-app-tests.log` 只有 App 全量 867/0/11 |
| R-010 | P3 | **OPEN（P3，登记未补）** | pytest 首轮 5 failed/3482 passed、EXIT 1 仍在 log；README 只写最终 3487/0/10 |
| R-011 | P3 | **OPEN（P3，登记未补）** | AC1 仍无两次装配/重启测试；P14 非空页数未在 wire 层断言 |

## 3. R2 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R2-001 | **P1** | `src/bootstrap/core_service.py:5081-5089`；`reading_export.py:627-666`；`tests/core/test_read_wire.py:86-90` | **P14 wire 仍按章节数返回**：store 已返回 `read_pages/total_pages`，但 handler 仍 `progress.get("completed_chapters")`/`total_chapters`；wire 测试只断言空书 `total_pages==0`，无法捕获。AC3「按页面数计算」在 wire 层未成立。 | 把 handler 改为 `read_pages=progress["read_pages"]`、`total_pages=progress["total_pages"]`、`finished=progress["finished"]`；补非空 2 页/50% 的 wire 测试 |
| R2-002 | **P2** | 卡面 R-002 记录；`IHostController.cs:196,205`；PREQ `:41-47,102-108`；README AC5 | P12/P15 签名/请求键偏差被登记，但 **AC5 仍标 MET**（“七命令按 PREQ §8 形状”）。登记偏差是 DSH 可接受路径，但 AC5 应降 PARTIAL 或先改形状；当前卡面证据自相矛盾。 | 改 AC5 为 PARTIAL/带 limitation，或按 PREQ 改签名/请求键；在 README 明确偏差与接受人 |
| R2-003 | **P2** | `src/application/reading/service.py:549-582`；卡面 R-004「已修」 | **P10 partial patch 未实现**：`save_preferences` 的缺省参数仍覆盖原值；无 service.py diff，也无 partial 测试；卡面“已修”是虚假处置。 | 读现有 prefs 合并 patch 后保存；补“先 mode 后 zoom”的 partial 测试；更新卡面 |
| R2-004 | P3 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md:11` | `vverify_pins` 拼写仍错（多 `v`）；pin 值本身已正确。 | 改 `verify_pins`；重算 UNFREEZE 载体/冻结记录 hash（若影响 pin） |
| R2-005 | P3 | `tests/core/test_read_wire.py:86-90`；`tests/storage/test_reading_preferences.py:129-150` | P14 只在 store 测了 2 页 100%，wire 只测空；缺少“非空页面 + 50%”端到端测试，导致 R2-001 漏网。 | 加非空页面 wire 测试（2 页 50% → read_pages=1/total_pages=2/percent=50/finished=false） |
| R2-006 | P3 | 用户 base `82ea7ca82`；卡面 `f9bf922aa`；`82ea..a44c` 无代码 | 范围注记：用户 base 仍指实现之后；卡面已改 f9bf，但 Task 指令/交接未统一。 | 统一 base=f9bf922aa（或「实现 diff f9bf..head」）；r1 报告已记录该异常 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好持久化 | **PARTIAL** | Core schema/P9/P10 往返；P10 partial 仍未修（R2-003）；UI 未接线；无两次装配/重启（R-011） |
| AC2 书签 | **PARTIAL** | Core/P11-P13 CRUD/跨书通过；UI 未接线；P12/P15 签名偏差登记（R-002） |
| AC3 整书进度 | **PARTIAL** | store 页面口径已修并测 2 页 100%；**wire handler 仍章节口径（R2-001，P1）**；UI 未接 |
| AC4 迁移无损 | **MET** | v10 additive；旧 reading_progress 行字段级保留；v1-v9 bytes 未改；`test_v10_migration_preserves_legacy_progress_rows` 通过 |
| AC5 契约/门禁 | **PARTIAL** | inventory 68/check EXIT 0、pins 18/18；但 P12/P15 偏差仅登记而 AC5 仍 MET；UNFREEZE `vverify_pins` 拼写（R2-002/R2-004） |
| AC6 证据 | **MET（P3）** | App 867/0/11、pytest 3487/0/10、targeted 24/0；Reader 70 无日志、首轮 5 failed 未说明（R-009/R-010） |

## 5. 门禁与定向

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:16:33 → 13:16:36 | PASS（3 warnings：11 非终态 / STATUS 3173 B·31 L / PLAN 6926 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-1.md` | 13:16:33 → 13:16:36 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:16:33 → 13:16:36 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:16:33 → 13:16:36 | **EXIT 0；渲染 61/68 与 inventory 合计 68 一致** | **0** |
| 5 | `python -m pytest tests/storage/test_reading_preferences.py tests/core/test_read_wire.py tests/core/test_v9_migration.py -q` | 13:16:36 → 13:16:40 | **24 passed** | **0** |
| 6 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:15:58 / 13:17+ | 两次均 **clean**；HEAD 均 `d0b77ed1a…` | — |
| 7 | 范围/Canonical | 13:16+ | `a44c..d0b` 10 文件全部 ⊆ allowed（OUT=0）；READ-1 Canonical **5/5 sha256 匹配** | — |

## 6. NOT_RUN / 未验证

- Fluent Reader UI 的偏好/书签/进度/reset 确认：仍未接线（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、READ-2 跨内容序列：NOT_RUN。
- 未重跑 App 全量/pytest 全量；采用 `verification` 日志（App 867/0/11、pytest 3487/0/10，首轮 5 failed 见 R-010）。
- 未修改产品/测试/契约/卡面/证据。

## 7. 处置建议

1. **R2-001（P1）**：同步 `handle_get_book_reading_progress` 到 store 新键，补非空页 wire 测试；否则 AC3 wire 不成立。
2. **R2-003（P2）**：真正实现 P10 partial merge（读现有→合并→保存），补测试；不要保留“已修”假声明。
3. **R2-002（P2）**：AC5 降 PARTIAL/li­mitation 或按 PREQ 修正 P12/P15；记录 DSH 接受。
4. **P3**：修 `vverify_pins` 拼写；补 Reader 70 日志/首轮失败说明/两次装配测试（或明确留 READ-2）；README/卡面同步。
5. 修后重跑 check/pins/API/targeted；真实 UI 保持 NOT_RUN。

## 8. 审查者声明

本报告由未参与 FEA-14-READ-1 实现的独立上下文子 agent 出具（续接 r1；r1 报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/逐行核对；未执行项在 §6 记 NOT_RUN；P1 的 wire 章节口径按 head 代码实测（handler 未改）记录。
