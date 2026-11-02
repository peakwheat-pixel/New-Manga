# R2R3 findings 处置（实施者记录）

实施/捕获 head：`17a26d552e27a57bafebe0bc77d008094d1a6775`；开始 head：`9c6a2b474abeb39be8f7c362cd2b11597e53b9d4`（用户允许的8203b3d28之后文档提交）。Task 仍 in_progress。下表 FIXED 指实现和自动化/真实证据已交付；不等于 Reviewer approved、AC-1/3 MET 或 DSH 集成完成。本实现会话不签发自己的独立 Review。

已完整读取 `doc/reviews/FEA-06-RESIDUAL-2-impl-r3.md`（含164图签署及附录C）与 `r2r2-findings-disposition.md`；只写本轮用户 allowed_paths。R2R2 原处置表、旧 Review、旧最终日志与旧 FEA-06 证据保持原字节。

| Finding | 本轮处置 | 实现、判别证据与剩余事项 |
|---|---|---|
| R2R3-001 P1 | FIXED（实现/捕获）；独立签署 NOT_RUN | `FluentShellSurface` 增顶部 NavRailToggle，隐藏不占位、跨页保持、按钮恢复。SetViewportWidth 保留窗口宽度，surface SizeChanged 不再用扣边框宽度覆盖；真实1024/1280/1600断言Medium/Compact/Full并写入文件名。StatusBand订阅当前页真实State/Error：读取异常→错误；Host SaveGate 未结束→Running/正在保存阅读进度。`CaptureShellStates` :115起断言布局、状态与解析后状态令牌，双主题新增折叠/错误/运行帧6张与重命名/补宽度帧6张；不伪造默认帧。共shell12张。 |
| R2R3-002 P1 | FIXED（实现/像素与实施者目视）；独立签署 NOT_RUN | 仅既有 `Bg.Overlay→Bg.Sunken`，Opacity 0–1，8s周期不变；不新增颜色/资产、不改层级或内容布局。真实phase0/3000ms/reduce原像素裁切；纯背景横带60000像素上light first→mid有25114像素RGB差>8、max15；first→reduce有31699、max17。dark分别10475/max23、16219/max27。`FluentResidual2VisualEvidenceTests:189`使用tolerance=8、>5000纯背景像素，未用AA/文字或降阈值凑数；生产时钟首/中/尾及高对比令牌测试继续通过。实施者原图目视可辨，仅自测，不代独立签署。 |
| R2R3-003 P2 | FIXED；独立签署 NOT_RUN | pressed实际 `PART_Root.Background` 改为 Status.Failed，与公开Background基值相同；前景 Bg.App。捕获读取真实PART_Root/ContentPresenter，断言令牌及≥4.5:1；原图文字/背景实色light=(250,249,247)/(161,67,45)，5.9467:1；dark=(20,21,24)/(219,148,135)，7.4751:1。两张pressed拒绝图已更新。 |
| R2R3-004 P2 | FIXED | Loop DetachWindow不再把解绑当激活，attach从实际Window.IsActive恢复 `_windowDeactivated`；Run仍检查失焦/可见性。粒子创建同样读取IsActive、后续窗口可见性事件不覆盖失焦状态。新增ManualClock回归 `ShelfGradient_InactiveNavigationReturn_RemainsPausedUntilActivation` 与 `PageTurnParticles_InactiveNavigationAndNewTurn_StayPausedUntilActivation`（含失焦后新翻页）；暂停时PendingFrames=0、Activate后才恢复，全部Passed。 |
| R2R3-005 P2 | FIXED | 粒子Play返回可幂等取消句柄；Reader策略归零同步Cancel并移层，detach及新翻页也释放句柄。Cancel使旧animation generation失效、解绑Window事件，取消闭包不能被Activated唤醒。新增播放中/暂停中 × reduce/auto+系统关/category-off共6格，实测同步layer=null；排空已请求的单帧后PendingFrames=0，Activate及后续翻页不复活。帧源不提供撤销队列API，取消使已排队回调下次到来时无操作且不再排队，并非声称物理撤回平台回调。 |
| R2R3-006 P2 | FIXED by DSH（本轮未改） | DSH `8203b3d28`已统一STATUS/PLAN当前指针，`9c6a2b474` checkpoint §147确认。check/pins再次通过；本轮无权重写Task/STATUS/PLAN/checkpoint历史。 |

验证日志：`impl-r3-rework-verification.log`（shell/SDK/head/完整命令与EXIT、逐程序集和57条skip原因）。全量 **1289 passed / 0 failed / 57 skipped**（较1281/0/57 +8/0/0）；build 0 warnings/0 errors。TokenGen292/ThemeGen --check、check.ps1、verify_pins 15/15、旧四PNG完整SHA和禁止写域检查均通过。默认全量前后git status均空；随后opt-in单独执行，status只出现本卡visuals。

## 164 → 172 图与签署边界

- 本轮pages8/components142/decor10/shell12，共172 PNG / 172清单行 / 172唯一SHA，全部捕获HEAD为17a26d552。每态真实主题/视口/相位/命令/SHA见 `visuals/visual-inventory.md`。
- 对旧164：136同名同字节（均来自旧PASS）；24同名改字节；4旧shell标签文件移除（default2、误标compact2）；12新shell文件名。净增8。完整old→new SHA表见 `r2r3-evidence-audit.md`。
- 原 impl-r3 **158 PASS/6 REJECT** 的历史签署保持原字节，只约束原SHA。本轮没有新增独立签署，inventory全部**NOT_RUN**；不得把6张旧拒绝图重捕获直接写成6 PASS，或把136字节相同扩成整卡批准。待DSH Appointment的新上下文 Reviewer复核172图及代码。
- 实施者查看了双主题渐变、Danger pressed、折叠、错误/运行态和宽度原图；其余原PASS同字节可由上述SHA对应定位。自测不写 signed_by。

## 仍未完成 / 不认领

| 项 | 状态 | 后续责任 |
|---|---|---|
| 本轮新图与AC-1/3独立签署 | NOT_RUN；AC-1/3仍PARTIAL | DSH Appointment fresh Codex或ZCode Reviewer；本会话不得自审。 |
| 原生200%DPI、原生a11y、桌面触控/完整Tab矩阵 | NOT_RUN（B-5/D-1） | DSH恢复硬件条件或取得用户waiver后另行验证；96DPI headless不替代。 |
| Controls/FluentUi.cs未调用旧粒子工厂/using | NOT_RUN（域外清理） | DSH另授权后清理，不扩大本轮写域。 |
| D-14状态颜色、OUT/BLOCKED、其它产品范围 | NOT_RUN（后续卡/范围保留） | D-14独立ready卡待DSH顺序释放实施；本卡不改Catalog，不认领其达成。 |

推荐下一步：DSH接收固定代码/证据与Handoff，Appointment上下文独立impl-r4 Review，逐项处理本表与172图；通过后由DSH集成验证、更新其写域内当前指针与生命周期。不得仅凭1289/0/57关闭本卡，不push。
