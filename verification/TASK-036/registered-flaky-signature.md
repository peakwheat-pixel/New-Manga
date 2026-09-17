# TASK-036：已登记 flaky 的首次捕获签名（含诊断掩蔽问题）

本文件独立于 [`intermittent-failure-repro.log`](intermittent-failure-repro.log)，用于把**两次复现**的原始签名与结论固定下来，供 flaky 跟踪节与后续切片使用。

## 复现 #1（诊断掩蔽，未定性 → 现已定性为"掩蔽"）

- 场景：TASK-036 head（`1b0c89e`）全仓串跑第 8 次。
- 结果：`1 failed, 736 passed, 6 skipped`（exit 1）。
- 报告：`tests/reading_export/test_qml_contract.py:153: RuntimeError`。
- 机制：该行位于**诊断辅助函数** `webtoon_save_diagnostics()` 内（`image.property("status")`）。即：被测用例的断言**已经失败**（= 已登记 flaky 触发），但构造失败消息时访问了**已被销毁的 QML C++ 对象**，`RuntimeError` 取代了真正的 `AssertionError`，**把 flaky 的真实签名掩蔽掉**。

## 复现 #2（诊断稳健化之后，真实签名）

- 前提：把诊断改为 `safe_property()`（`RuntimeError` → `<unavailable: …>` 占位）后。
- 场景：同 head 全仓串跑第 14 次（[`intermittent-failure-repro.log`](intermittent-failure-repro.log) run 6）。
- 结果：`1 failed, 736 passed, 6 skipped`（exit 1）。
- 报告（原文）：

```text
FAILED tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer
E  AssertionError: scroll_offset_y is saved through the service —
   pump(2s): iterations=98 elapsed_ms=2000 ok=False
   scroll_contentY=-0.0 saved_scroll_offset_y=0.0
   image_status="<unavailable: Can't find converter for 'QQuickImageBase::Status'.>"
   object_names=['label', 'readerChapterTitle', ..., 'readerWebtoonScroll']
tests\reading_export\test_qml_contract.py:312: AssertionError
```

## 复现 #3（稳健化之后，仅捕获用例名）

- 场景：同 head 追加全仓串跑第 3 批第 1 次（`full-suite-runs-post-diagnostics.log`）。
- 结果：`1 failed, 736 passed, 6 skipped`（exit 1），失败用例**同为** `test_reader_webtoon_swaps_in_vertical_viewer`。
- 该批次未开启 `--tb=long`，只记录了用例名；签名与复现 #2 一致（同断言、同路径）。

## 频率对照（本会话）

| 树 | 全仓串跑次数 | 失败次数 | 失败用例 |
|---|---:|---:|---|
| 本 head（TASK-036） | 17 + 3 = **20** | **3** | 全部为 `test_reader_webtoon_swaps_in_vertical_viewer` |
| 纯净基线 `edfdcf2`（无本 Task 任何改动） | **6** | **1** | **同为** `test_reader_webtoon_swaps_in_vertical_viewer`（run 2：`1 failed, 705 passed, 6 skipped`，见 [`flaky-rate-baseline.log`](flaky-rate-baseline.log)） |

**归属判断（结论）**：该用例属读者 QML 路径，TASK-036 的产品代码改动为 `inpaint` 路由设置解析与**导出** ViewModel，不在该用例执行图上；TASK-036 对该测试文件的改动仅为**诊断稳健化**（不改断言/预算/时序）。**纯净基线同样复现同一用例**（1/6），故本会话的高频次属既有 flaky + 环境时序，**不归因本 Task**。同时说明 STATUS 中 TASK-034 集成时登记的"1/14 未定性间歇失败（用例名未捕获）"**极可能就是这个已登记用例**。

## 可读结论（供 R-06 跟踪，**本 Task 不修**）

1. 失败点是既有断言 `assert pump(window, 2.0, lambda: reading.progress.scroll_offset_y == 240.0)`（`test_qml_contract.py:312`），即**节流保存未在 2 s 预算内发生**；98 次事件循环迭代、2000 ms 预算已耗尽（不是"事件循环饥饿"）。
2. 关键签名：`scroll_contentY=-0.0` —— 测试先前的 `scroll.setProperty("contentY", 240.0)` **被 Flickable 夹回 0**（`boundsBehavior: StopAtBounds`）。前一断言只验证 `contentHeight > 0`，**并未验证内容可容纳 240 的偏移**（即 `contentHeight - height` 至少 240）。
3. 因此 `onContentYChanged` 可能**根本没有触发**（值未真正变化），`scrollSaveTimer.restart()` 不会启动，服务端 `scroll_offset_y` 保持 `0.0`；这与"节流定时器被拖慢/被反复重启"的旧候选不同：**更可能是"设值被夹回 → 无变化信号 → 定时器未启动"**。
4. `image_status` 无法读取（`Can't find converter for 'QQuickImageBase::Status'`）——这是**诊断侧的 PySide6 转换限制**（与 flaky 无关），已用 `safe_property()` 兜住，不再掩蔽真实失败。
5. 归属：该用例属 `tests/reading_export` 的**读者 QML** 路径；TASK-036 改动为 `inpaint` 路由设置解析与**导出** ViewModel，不在该用例执行图上（TASK-036 对该文件仅做了诊断稳健化，未改任何断言或等待预算）。
6. **本 Task 不做修复**（R-06 明确不在范围）：若裁决方要根除，最小改动候选是"等待 `contentHeight >= 240` 后再设 `contentY`，或在设值后断言 `contentY == 240` 再等保存"，属后续切片。

## 对"未定性间歇失败"的影响

STATUS flaky 跟踪节此前把 TASK-034 集成时那 1/14 次失败登记为"**用例名未捕获**"。本次两次复现均落在**同一已登记用例** `test_reader_webtoon_swaps_in_vertical_viewer`，并给出了可读签名（`contentY=-0.0` + 保存未发生）。建议把该签名并入跟踪条目（由 Codex 决定是否更新 STATUS）。
