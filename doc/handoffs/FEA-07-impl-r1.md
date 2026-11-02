# FEA-07 Handoff（impl-r1 返修完成，待 r2 复核）

- Task：`doc/tasks/FEA-07.md`（status: in_progress；owner: dsh；approval: scope_review_r2_approved_2026-11-02）
- 范围：运行期双 UI 切换/稳定主窗/WindowBroker/switch journal/safe startup/双屏 DPI memento；`--presentation-host` 为 opt-in 开关；`--shell=legacy` 保持最高优先级。
- 交付：
  - 新模块 `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/`（SwitchJournal/FrontendSwitchCoordinator/WindowBroker/ExitCoordinator/DisplayTopology/WindowStateMemento/FrontendContentHost）。
  - App 接线：`PresentationWindow`（稳定身份、内容切换、memento/拓扑 clamp、ExitCoordinator 阻断关闭）、`FrontendHostCoordinator`（selector/单写者/回滚/UI 线程）、`SafeStartupPlanner`（fail-safe 单源）、`--presentation-host`、Fluent content surface 抽取、内容树缓存复用。
  - 测试：App.Tests 504（497 passed/7 skipped）；Presentation.Avalonia.Tests 38；全量 **1106/0/57**。
- Review：`doc/reviews/FEA-07-impl-r1.md`（changes_requested P0=0/P1=7/P2=5）；处置记录见 Task「impl-r1 处置」；R-007 生命周期字段已在本 handoff/卡内登记，R-011 精确 head 证据见 `verification/FEA-07/final-evidence.log`（提交后补）。
- 证据：`verification/FEA-07/evidence-index.md`（SHA-256 索引）、`performance-baseline-release.json`（Release p95 344.93ms；W-5 ≤1000ms PASS）、`generators-check.log`（两生成物 byte-for-byte up-to-date）、各切片日志。
- 待办：r2 独立复核（fresh Codex CLI，被审本 head）→ 若 approved → DSH 集成验证 → done；AC5 原生双屏/拔屏/DPI 矩阵仍 BLOCKED（D-1 无硬件）；AC1/AC2/AC6/AC8 的残余项按卡内 PARTIAL 理由继续保留或转 residual。