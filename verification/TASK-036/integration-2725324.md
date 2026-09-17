# TASK-036 集成验证：`2725324`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `edfdcf2fe923c8c6e97d19377c61c4b8bba25abc`（本 Task 固定 base；分支起点 `81ffd83` = 释放纯文档提交） |
| reviewed head（delivery） | `c931db0` |
| 元数据 / 分支 head | `5606221` |
| Review 报告 commit | `addf669` → [`doc/reviews/TASK-036-c931db0.md`](../../doc/reviews/TASK-036-c931db0.md)（Reviewer=Codex，**非作者**；decision=`approved`；四轴均 `executed`、逐轴小结、不跨轴排名） |
| implementation merge / integration commit | `27253240d0fb2a8df82b15f34546cd74dc9b717f`（merge，parents `addf669` + `5606221`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；全部 `-p no:cacheprovider` |

## 复验结果（master `2725324`，Reviewer 独立重跑）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/providers tests/core tests/reading_export tests/editing -q -p no:cacheprovider -rs` | 0 | **274** | **0** | `274 passed` | 无 |
| 2 | `…python.exe -m pytest -q -p no:cacheprovider -rs -rf`（全仓，3 次） | 0 / 0 / **1** | **737** / **737** / 736 | **6** / **6** / **6** | 2 次 `737 passed, 6 skipped`；**1 次 `1 failed, 736 passed, 6 skipped`，失败用例为 `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`（= 已登记 flaky，本轮已定性）** | 6 条 skip 全为既有 `tests/network` 的 `openssl unavailable` |
| 3 | 输入矩阵（Reviewer 独立探针，base `edfdcf2` 导出树 vs HEAD 各跑一遍） | 0 | — | — | **PASS** 8 类合法输入前后逐字相同（含 `same_default` 身份判定）；非法输入一律 typed `ProviderInputError` 且消息含字段名与实测类型 | — |
| 4 | 发布顺序（读代码 + 逐槽观测） | 0 | — | — | **PASS** after = `changed(True) → changed(True) → 终态信号(True) → changed(False)`；`running = Property(bool, _running, notify=changed)` ⇒ 清标志后再发 `changed` 属**必需** | — |
| 5 | 边界 | 0 | — | — | **PASS** `src/` 恰为 **2** 个允许文件（`application/translation/inpaint/router.py`、`ui/viewmodels/export/viewmodel.py`）；`src/ui/**` 仅该 viewmodel；Schema/依赖/seam/`AGENTS.md` 命中 **0** | — |

## R-02 更正（Evidence 快照口径）

`verification/TASK-036/changed-paths.txt` 是 **`1b0c89e` 时刻的快照**，未含其后 `dcba248` 新增改动的 `tests/reading_export/test_qml_contract.py`。**实测口径（本文件为准）**：Owner 改动 = `git diff --name-status edfdcf2...5606221` **减去** 释放提交 `81ffd83` 自带的 `doc/STATUS.md`、`doc/tasks/README.md`，即

```text
src/application/translation/inpaint/router.py
src/ui/viewmodels/export/viewmodel.py
tests/providers/test_handlers_pipeline.py
tests/providers/test_route_policy_settings.py
tests/reading_export/test_qml_contract.py      <- 快照遗漏（dcba248）
tests/reading_export/test_viewmodels.py
tests/providers/… （新增用例均在这些既有文件内）
verification/TASK-036/**
doc/handoffs/TASK-036-c931db0.md
doc/tasks/TASK-036.md
```

**全部落在允许范围（`tests/**` 含该文件），越界 0**；`git diff --check edfdcf2..5606221` 退出码 0。作者原始材料**未被改动**。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3 | `safe_property` 的**字符串**占位被用于**数值比较**的等待条件 → `str > int` 抛 `TypeError`，把"RuntimeError 掩蔽 AssertionError"换成"TypeError 掩蔽"（Reviewer 独立复现；仅在等待期间对象销毁时可达，**不造成假通过**） | **open（非阻塞）**：建议数值场景改用返回数值兜底的辅助（如 `safe_number(..., default=0)`）；纳入 R-06 修复切片一并处理 |
| R-02 | P3 | `changed-paths.txt` 为过期快照，漏 `tests/reading_export/test_qml_contract.py` | **fixed（记录更正）**：见上节；未改作者材料 |
| R-03 | P3 | 作者主动扩大的两处行为（`route_policy: null`、`requirements` 非 mapping → typed error） | **accepted**：与 TASK-034 R-2「present but non-mapping」原则一致；`null` 属"存在且类型错误"，R-1 的身份返回只适用于**键缺失**；`requirements` 非 mapping 此前已是失败（裸 `ValueError`），本次仅类型化 |
| R-04 | P3 | 新顺序下 **DirectConnection** 的终态信号处理函数内读到 `running == True`（已由测试断言为新契约） | **accepted 并记录**：这是"`running == False` ⇒ 终态已发布"的必要代价；QML 走 auto/queued 投递不受影响 |
| R-05 | P3 | Handoff 内部数字不一致（"3 次失败" vs "两次失败"） | **open（P3，纯文档）** |

## 已登记 flaky：本轮**首次定性**（R-06，非本 Task 引入；未记为通过）

- **签名**：`pump(2s): iterations=98 elapsed_ms=2000 ok=False scroll_contentY=-0.0 saved_scroll_offset_y=0.0`；失败断言 `test_qml_contract.py:312`（`scroll_offset_y is saved through the service`）。
- **机制（比此前假设更贴近证据）**：`setProperty("contentY", 240.0)` 被 Flickable 按 `StopAtBounds` **夹回 0**（前一处断言只保证 `contentHeight > 0`，未保证内容可容纳 240）→ 值未变 → `onContentYChanged` 不触发 → 节流保存不启动。
- **附带修复**：`dcba248` 的 `safe_property()` 使**诊断不再掩蔽真实 `AssertionError`**（此前第 8 次复现报的是 `test_qml_contract.py:153: RuntimeError`）——这一改动**已接受**（但见 R-01 的数值用法缺口）。
- **归属**：**不归因本 Task**。结构性依据：该用例早于本 Task 由 TASK-017 R-007 / TASK-019 T-1 登记；本 Task 对该测试文件仅做诊断稳健化（无断言/预算/时序改动，diff 逐行核对）；本 Task 产品码改动不在读者 QML 执行图上；作者对照组在**纯净 `edfdcf2`** 上复现同一用例。
- **Reviewer 独立复现的诚实边界**：我在 **head** 上 mandated 命令第 1 次即命中该用例；随后 head 全仓 **5/5** 绿、master 全仓 **2/3** 绿（1 次命中同一用例）；我在**纯净 base `edfdcf2`** 上跑 mandated 命令 **8 次 0 命中**（**未能复现基线**）。故频率不可用小样本定论，归属依据为上述结构性证据。
- **状态**：仍 **open**，但由"**未定性**"升级为"**已定性（含可读签名与最小修复候选）**"。最小候选：等 `contentHeight >= 240` 后再设 `contentY`，或设值后断言 `contentY == 240` 再等保存。**本 Task 不修**（禁止范围）。

## 集成结论

- [x] 非作者独立 Review 绑定固定 base/head，四轴均 `executed`、逐轴小结、**未跨轴排名**；**并行偏差已按固化结论声明**（§6 第 6 条兜底：两遍相互隔离检查；不再重复派发本环境不可用的双轴线程）。
- [x] AC ①～⑦ 全部集成为生产基线；作者的核心数字（274/0、737/6）与输入矩阵、发布顺序、冻结清单均由 Reviewer 独立复核。
- [x] 6 条 skip 全为既有 `openssl unavailable`；**未新增 skip、未放宽任何断言**（diff 正则 + 冻结解除清单逐条核对）。
- [x] 边界：Owner 改动全在允许范围，`src/` 恰为 2 个允许文件，越界 0；未 push。
- [ ] **已登记 flaky 仍 open**（已定性，后续切片修复）；**未记为通过**。真实端点/模型端到端仍 `NOT_RUN`。
- [x] Task 收口：AC ①～⑦ 完成、非作者 Review 通过、集成完成 → **TASK-034 登记的 R-02 / R-05 / R-07 三项全部关闭**（R-07 的冻结由本 Task 解除）。
