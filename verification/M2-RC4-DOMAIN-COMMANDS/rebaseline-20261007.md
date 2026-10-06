# Refresh / rebaseline（2026-10-07，Codex）

实测仓库 G:/CODEX/New Manga，分支 main，HEAD 444210085dacaa92a56400bc21aadb64fce1fbf1；git status --short 为空，common directory=.git。git log 核对 A=108bf113（收口 ecbfe9cb）、B=b355757c（收口 44421008）、C=ec460508（收口 9c05d5f3），均为 HEAD 祖先。三 Task done，与 Review/Handoff/测试文件相互对应；不重新实现或重新打开。

用户本次确认：仲裁阈值保持 0.90；BJ13 维持现状，手动改标 UI + skip 兜底；不启动 BJ13 补标或 BJ13/14/15 补画，只有新证据与新业务裁决才考虑。STATUS 的“两裁决待答”、PLAN 中 A/C 初始 ready 与 00_INDEX 旧 current pointer 均为文档漂移，将在本次 release 更新，非产品/任务冲突。

最新 post-merge raw：verification/M2-SFX-MISROUTE-UI-IMPL-1/raw/main-regression-postmerge-{vitest,build,pytest}.log；vitest 105、build EXIT=0；pytest 1847 passed + 1 skipped + 1 failed（test_catalog 122≠97，EXIT=1）。这是既有报告，不冒充本次复跑；旧日志 header 不完整，本次所有新证据补足 shell/venv/commit/EXIT。

未决候选：RC-4（本次最高优先，已授权）、DOM 实际交互覆盖、token 真值链与 A13 视觉取证、Workbench production page→resource catalog/页导航读取面、test_catalog 固定数量断言漂移。先做 RC-4；完成后按当时新证据挑最高优先，不能把 legacy 隐患或已闭环研究重新释放。BJ13 扩展不进入可执行候选。

真实 RC-4 缺口：restore_revision 无 IPC，且应用层未传期望 current ID；history DTO/runtime 缺位；rerender_page 服务已存在，但 core_service 的 font/layout/compositor=object()，生产重渲染不可用；Tauri 三新命令未注册；Viewer undo/rerender 与 Inspector history 硬禁用，undo 窗口计时缺失。冻结方案见 doc/contracts/M2-RC4_DOMAIN_COMMANDS.md。

运行期权责恢复：Codex Lead/Integrator，不再沿 STATUS 历史 quota exhausted 委托；可用 Executor 实施（ZCode CLI/connector 未发现），DeepSeek 非作者 Review。没有覆盖或清理任何历史 worktree/用户数据。
