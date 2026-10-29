# V11R-C-3-I1 处置表（独立窄复审 r1）

- 分支：``v11r/c3-i1``，基线：``7bfb11033``（含 C-3 退役 + D-1 I3 + 字体审计修复）。
- 结论：r1 的 5 个 P2（+ 字体测试已在 D-1 I3 修复）逐条闭合；无 P1、无行为回滚。

| # | 复审发现 | 处置 | 证据 |
|---|---|---|---|
| 1 | 旧壳只切 ``RequestedThemeVariant``，不同步 DS palette | ``MainWindow`` 接收共享 ``DesignSystemThemeManager``；``CycleTheme`` 与设置页浅/暗行都走 ``ApplyAppearance`` → ``SetAppearance``；``OnThemeApplied`` 兜底同步；新增两条测试断言 manager 状态、``Nm.Color.Bg.App`` 解析值与渲染帧哈希变化 | ``LegacyAppearanceSyncTests``（2 例）；``verification/V11R-C-3/R6-*`` |
| 2 | ``--theme`` 迁移后外观丢失 | 新增 ``Services/LegacyStartupTheme``：迁移表给出 appearance/density，``App`` 初始化时传给 manager；显式 ``--variant`` 优先；App.axaml.cs 只改一小段，helper 隔离以便与 INT-2 合并 | ``LegacyStartupThemeTests``（5 例）；``App.axaml.cs`` |
| 3 | 5 条替代断言只构造旧 ``MainWindow`` | 新增 v2 等价断言：``AppShellV2`` 首帧非阻塞 + 共享 manager 外观切换 + 材质 fallback；旧设置页“主题中心已退役”属 legacy-only 行为，在 ``R4-ASSERTION-MAP.md`` 明确退役后随旧壳一并消失 | ``ThemeRetirementR4Tests.V2_*``（2 例）；``R4-ASSERTION-MAP.md`` |
| 4 | R6 ``workingTreeDirty=True``、缺完整文件清单、用 kill 代替优雅退出 | 在干净树重跑 R6：dependency-graph/矩阵/build/test/双 shell smoke，smoke 用 ``--exit-after-ms`` 优雅关闭并记录退出码与完整文件清单、``dirty=false`` | ``verification/V11R-C-3/R6-report-clean.md``、``R6-*`` |
| 5 | READY 包 6 个文件被原位覆盖 | 从 ``b5f7d88fc`` 逐字节恢复 READY 6 文件（``git diff`` 为空）；执行结果移到 ``verification/V11R-C-3/final/*.executed.*``；两个 tools 脚本默认输出改为 C-3 执行证据路径，README 说明 | ``READY-RESTORE.md``；``git diff b5f7d88fc -- verification/V11R-C-3-READY`` 为空 |
| 6 | ``LegacyChrome`` 硬编码 fallback 色/圆角 | fallback 色改为显式中性常量并注释“仅 DS 资源缺失时使用”；legacy 12/8/6 圆角登记为本任务兼容度量（契约 §2.4 例外，随旧壳退役消失），见 ``DEVIATIONS.md`` | ``LegacyChrome.cs``；``DEVIATIONS.md`` |
| 7 | 字体审计假阳性 | 已在 D-1 I3 ``70378f9`` 修复：只计 tracked 文件，且存在但未跟踪的字体必须被 gitignore；本分支已包含 | ``ThemeRetirementR4Tests.No_font_binaries_ship_with_the_application`` |
| 8 | D-1 r4 P2：FocusRing 泄漏测试名不副实（只断言最终唯一 ring，不能证明订阅释放） | ``FocusRing`` 增加 internal 可观测计数 ``IsSubscribedFor``/``PositionCallCountFor``（`InternalsVisibleTo` 仅测试程序集）；测试逐次断言订阅存在/释放、focus 驱动回调、禁用后 focus 不再触发回调，并保留最终唯一 ring 断言 | ``FocusRingBehaviourTests.Repeated_enable_and_focus_cycles_do_not_leak_rings_or_handlers`` |

## 验证

- ``dotnet build NewManga.sln -warnaserror``：0W/0E。
- ``dotnet test NewManga.sln --no-build``：0 fail（含新增 C-3-I1 测试）。
- 干净树终版 R6：``R6-report-clean.md``（源码 HEAD e41017aa、dirty=false、App 309+7/ThemeEngine 235/DS 85/Host 49+28/CoreClient 116+25、双 shell exit 0/0、v2 与 legacy host.log 齐全、SHA-256 清单）。
- 干净树 R6 重跑：见 ``R6-report-clean.md``。


