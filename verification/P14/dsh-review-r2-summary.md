# P14 独立 Review R2 摘要

- Reviewer：dsh
- Session：`session-00f8deab-fe9d-44a7-8afe-ed7bab570981`
- 审查提交：`e99be4d6209ba2c11171b215c55d20ff41fc17cc`
- Review 结论：`changes_requested`
- Reviewer 使用提交树静态检查，没有运行测试、build、Core / Rust 套件或 GUI e2e。

## Findings

| ID | 级别 | Finding | 后续处理 |
|---|---|---|---|
| F-01 | P1 | 4 条 Canonical Evidence SHA256 与审查提交树字节不符：前端 tests/build meta、Rust packaged meta、禁用入口证据。 | AC6 文档收尾按磁盘字节重算全部登记项，并由真实提交包含性校验。 |
| F-02 | P1 | `delivery_head` 和 12 条证据 commit 均指向旧提交 `8f3fddc`；R2 源码与新日志未登记，测试计数仍为 18/190。 | 固定最终实现/证据提交；登记最新 19/204 tests 与 build 原始日志、meta。 |
| F-03 | P2 | Task、Handoff 与 checkpoint 的状态不一致；R1 摘要错误声称 Task 已是 `in_review`。 | 修正 R1 摘要；Task、Handoff、checkpoint 统一为合法状态 `in_review`。 |
| F-04 | P2 | Handoff 声称源树自记录后未变化，且测试数与提交已过时。 | 更新 Handoff 为实际固定提交、测试结果与证据路径。 |
| F-05 | P3 | 章节或页面投影返回 `CORE_UNAVAILABLE` 时没有按设计 §3.4 显示全区块错误卡。 | 已在后续前端修复中覆盖 `books`、`chapters`、`pages`、`regions` 四类 Core 不可用状态，并添加 chapters/pages DOM 回归断言。 |
| F-06 | P3 | PageList 的作品/章节/页面空与加载占位仍为英文。 | 已改为简体中文。 |

## R1 finding 复核

- R-001 至 R-009 在 `e99be4d` 源树上已实质解决；R-001 的全区块 Core 错误卡仍有 F-05 的章节/页面覆盖缺口，已在后续修复中补齐。
- R-010 在 `e99be4d` 提交树上仍未解决；Task 状态随后在 AC6 文档收尾中修正。

## Gate 摘要

- AC2、AC3、AC4、G15 禁用状态、导出面板路径投影及本轮 `m2res` 专用媒体显示例外核对通过。
- `m2res` 只用于 Viewer 页图的短期媒体显示链路；请求、返回、事件、错误中未发现路径、grant 材料、会话凭据或可解码路径字段，且未发现 URL/opaque handle 持久化或日志/事件泄漏。
- AC5 静态复核引用归档日志；Reviewer 未自行重跑。GUI e2e 为 `NOT_RUN`，原因是无头 WebView2 窗口句柄错误 `0x80070578`。
- AC6 在本轮不通过；文档修订与最终磁盘字节哈希尚待随下一固定提交核验。

## 后续状态

本摘要记录 R2 当时 `changes_requested` 的事实，不代表已接受。实现 Owner 随后修复 F-05/F-06 并重跑前端 tests/build；最终 Handoff 仍须交由非作者独立 Review。
