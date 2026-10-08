# Codex 非作者 Review r1：changes_requested

base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；reviewed_head=f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50。
Owner=DSH；Reviewer/Integrator=Codex。真实DSH CLI EXIT0，session-7de56368-5e9b-44ed-9e2d-0c288fdc67ff。
DSH shell沙箱Win32 5使运行检查NOT_RUN；原报告/最终回答保留。没有产品修复或Gate通过。

- R1 P1：run_dll_diag_probe.ps1的installer hash缺失/不匹配仅打印BLOCKED/DRIFT后继续，不符合固定输入fail-closed。
- R2 P1：未传CopyBundle或robocopy失败后，RunBundle仍为其他Owner原证据Bundle，脚本继续启动acceptance_bridge.exe。
  与自有lab隔离写边界冲突；必须只从复制成功、自有且已校验的lab运行，复制失败立即停止。不采用/MIR删除式同步。
- R3 P2：REPORT与FINAL“Win32 126高置信”没有GetLastError实测；原日志仅是ImportError，具体Win32错误码应UNKNOWN。
  某DLL未出现在枚举bundle不能证明原安装树缺失/运行影响，候选根因仍UNKNOWN。

本轮未执行该PS探针。最小PE探针也未验证，不将其输出当系统Loader事实。请DSH只修以上有界问题，
保留原始FINAL-r1和NOT_RUN日志，Handoff改引用实际draft head并追加变更记录。
修正后仍须独立检查与实际隔离执行，Task不能done，不自动解除runner debt。
