---
task_id: FEA-06-RESIDUAL-1
author: Codex CLI（本轮 fresh 实现会话）
recipient: DeepSeek Harness
base_commit: ff9da7dcf8eb70333a8165d7c83106156a3107af
delivery_head: 8b39b13982cfaae9e7606fe62f13353700be68fe
status: ready_for_independent_review
---

# Handoff：FEA-06-RESIDUAL-1 impl-r2 findings 返修

## 交付结果

实现提交 `8b39b13982cfaae9e7606fe62f13353700be68fe`，提交标题 `fix(fea-06-residual-1): R2-001..004 and R2-006 motion, idle and focus rework`。本 Handoff 与 R2-005 当前证据作为后续文档提交追加，不改变已测源码/测试。未 push，未关闭 Task，未代签独立 Review 或集成验证。

起点为 main / `ff9da7dcf8eb70333a8165d7c83106156a3107af`，工作树干净，common directory=`.git`。Task 原始 base=`82529a3d5864a39f362e414b67bca774d743f862`；本轮来源为完整读取的 [impl-r2](../reviews/FEA-06-RESIDUAL-1-impl-r2.md)（含附录 A/B）、[Task](../tasks/FEA-06-RESIDUAL-1.md) 和用户明确返修授权。

| Finding | 实施结果 | 可复现回归断言 |
|---|---|---|
| R2-001 | Reader 顶/底条复用有限帧动画实际淡出；按 Navigation 分类降级。Settings 离开/普通确认、Shelf 对话框/抽屉统一200ms进入/160ms退出，遮罩160ms。hover使用冻结SplineEasing(.4,0,.2,1) | `FluentR2ReworkTests.R2001_*`：80/159/160与100/199/200ms中间值/边界；Reader唤醒取消旧退出；reduce与feedback-only分类下上述真实浮层均瞬时终值 |
| R2-002 | 新增Fluent局部继承配置 `FluentMotionScope`，新逻辑/模板子控件与缓存树自动取得当前颜色及缩放配置。输入前的兜底准备也使用同一配置 | `R2002_RebuildHover_*`；增强既有 `WorkbenchDraftEdit_BadgeSurvivesRender_AndNewButtonsReceivePressedMotion`：Settings Providers/Backup、真实Workbench投影重建→真实hover/pressed→分类或reduce→再重建→full恢复。只注入Avalonia ClockBase脉冲，颜色由真实BrushTransition插值，30ms中间RGB按冻结曲线计算 |
| R2-003 | Reader统一观察press/release/move/wheel/key；Shell消费按键前通知Reader。生产DispatcherTimer与测试共用单调时钟deadline判断；释放仅续时，不反转中心点击隐藏；detach停止并清deadline | `R2003_RealInput_*`四路真实输入于1500ms发生，deadline=3500，2000/3499仍显示、3500隐藏，160ms淡出；detach推进3000ms不改变状态。`R2003_RealCenterPressAndRelease_*`真实图片命中、按下/释放仍隐藏 |
| R2-004 | 后台事件捕获attach generation，Post闭包执行时复查订阅、代次和挂载；detach使旧回调失效；reattach应用当前值且订阅一次 | `R2004_BackgroundEvent_*`：真实SaveAsync在各测试独立临时根写入后后台Changed→detach→pump；另验快速reattach当前full值、重复attach只有1订阅 |
| R2-005 | 旧三表和batch-b日志逐字节保留为前缀，追加明确取代历史口径的当前快照；57skip从本轮stdout逐项提取并逐条附fixture原因。新增字节manifest和只读证据检查脚本 | `python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py`：当前head/1233计数、57实际skip与原因精确集合、13项旧文件/前缀原始SHA以及四PNG对base字节比较 |
| R2-006 | 在既有I-11 FocusRing授权内新增可继承Offset附加属性，默认0；**只在Fluent根动态绑定既有Nm.Focus.Ring.Offset=1**。尺寸/位置/滚动裁剪都使用offset+stroke，Current几何保持0 | `FocusRingOffsetTests`4项：标准/高对比实时切换、四边gap、外宽高、仅gap被裁剪时隐藏/恢复、Current零offset对照；`R2006_*`另验Fluent/Current树继承边界 |

Shelf对话框首次实际打开的新回归另暴露缓存确认按钮仍挂在旧actions面板，重建会抛重复父节点异常；在原Fluent视图内只移除其旧父节点再加入新面板，四个真实浮层/降级测试覆盖此路径。未扩大产品范围。

写域仅为Fluent视图、共享Theming的FocusRing、两个授权测试项目、本卡verification和本Handoff。Core/契约/schema/依赖/生成物/冻结设计/Current V2/组合根/FrontendSelector/FEA-07 seam均无改动；没有新增依赖/许可证材料，没有写真实APPDATA。Task/STATUS/PLAN/历史Review原字节保持。

## 验证证据

环境：Windows，PowerShell Core 7.6.8，SDK10.0.401，测试目标net9.0，Avalonia11.3.22。完整命令、原始输出、EXIT、计数及逐finding断言见 [impl-r2-rework-verification.log](../../verification/FEA-06-RESIDUAL-1/impl-r2-rework-verification.log)。

| 实际命令 | 结果 |
|---|---|
| `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | EXIT=0，0 warnings / 0 errors |
| `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | EXIT=0，**1233 passed / 0 failed / 57 skipped**，总1290 |
| `pwsh -NoProfile -File tools\governance\check.ps1` | EXIT=0，PASS，3个既有warning |
| `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | EXIT=0，**15/15** |
| 两生成器二进制 `--check`（完整路径见日志） | EXIT=0/0，生成字节一致 |
| `python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py` | EXIT=0，原字节13/13、skip原因57/57、当前三表与日志一致 |

逐程序集 passed/failed/skipped：Appearance21/0/0、Presentation.Avalonia38/0/0、Host51/0/28、ThemeEngine253/0/0、DesignSystem97/0/0、ApplicationCore31/0/0、CoreClient128/0/22、App614/0/7。历史impl-r2基线1213/0/57→本轮1233/0/57，**+20通过用例（App+16、DesignSystem+4），没有删除既有用例**。定向55/55通过；旧Batch A仅时长对象断言已升级为真实淡出过程，原reduce/侧栏语义断言保留。

57 skip仍为未配置 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 的sidecar集成fixture（App7、CoreClient22、Host28）；完整名称和原因逐项位于新日志及batch-b当前补记，不把skip计为通过。默认PNG渲染用例在全量内运行，采证变量未设置；四张旧FEA-06 PNG与base完全同字节，SHA见日志和manifest。

## 接收方式与当前限制

在 `G:\CODEX\New Manga` 的main、同一worktree接收固定实现head。按日志中的筛选命令复跑 `FluentR2ReworkTests` / `FluentAnimationCompletionTests` 与 `FocusRingOffsetTests`；用上述四验收命令复跑全量及机械检查。数据只用FakeHost或隔离临时目录；不需要真实用户漫画库。

R2-001…006均已有实现或证据返修及可复现断言，**最终finding处置由fresh独立Reviewer和DSH作出**。本轮未完成项仍为本卡既有范围限制，不能据本轮测试全部通过宣称全Task AC达成：

- I-4剩余状态格（如Slider/ToggleSwitch disabled、checked/loading、Toast其余severity）仍NOT_RUN，其中普通headless可验证格属于测试缺口，不伪称硬件阻塞；完整清单见当前组件矩阵。
- D-8仍PENDING_DISPOSITION：三类decorative动画本体未实现；已有参数/分类/reduce禁用测试不等于批准暂缓。
- B-1…B-7继续按Task依赖/恢复条件登记；原生桌面/200%DPI/a11y/逐像素视觉、完整Tab遍历及本轮PNG opt-in采证NOT_RUN。
- Task的旧Canonical Evidence及STATUS/PLAN指针需要DSH按新证据提交登记；本轮严格限定写域，未改任务/状态/指针。当前check PASS不替代语义审查或授权。

## 下一任务建议

- Task：FEA-06-RESIDUAL-1，impl-r3上下文独立复核；启动条件为DSH接收本固定实现与证据提交并登记Review Appointment。
- 推荐Agent：DSH负责任命与处置；Reviewer=fresh Codex或未参与本返修的ZCode，不能使用本实现会话自审。
- Recovery point：`G:\CODEX\New Manga`，main，当前worktree；返修base=`ff9da7dcf8eb70333a8165d7c83106156a3107af`，实现head=`8b39b13982cfaae9e7606fe62f13353700be68fe`。本Handoff后续文档提交不改变源码/测试；接收时固定该文档提交的HEAD作为reviewed_head。无需新建worktree。
- Scope：Reviewer只读全部被审变更，只写`doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md`；不得返修生产代码、改冻结设计/契约/Core/schema/Current/组合根/FEA-07 seam或更新他人证据。DSH负责后续权威指针登记。
- Deliverables：精确base/head、Reviewer身份/上下文来源、逐R2-001…006处置与剩余NOT_RUN/D-8、四命令EXIT/计数/57skip、旧PNG/历史字节保全及新Review报告。
- Verification/Gate：Windows/.NET9目标，四验收命令、两生成器检查、上述行为筛选与只读证据脚本；不减少1233/0/57基线，不把NOT_RUN/BLOCKED算PASS。Review和DSH集成验证均通过前不关闭Task、不释放后续实现节点、不push。

可直接转发给DSH：

> 在G:\CODEX\New Manga的main接收FEA-06-RESIDUAL-1 impl-r2返修，base ff9da7dcf8eb70333a8165d7c83106156a3107af，固定实现head 8b39b13982cfaae9e7606fe62f13353700be68fe，并固定包含本Handoff和verification追加证据的当前文档HEAD。先核对git状态及禁止路径零diff，读取本Handoff、impl-r2 Review和本轮验证日志，登记fresh Codex或未参与返修的ZCode执行impl-r3。审查者只读被审head，唯一写域doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md；逐项复核R2-001…006的过程/中间值/真实输入/重建/生命周期/焦点几何及证据口径。实跑四验收命令、两生成器和python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py，记录EXIT、全量1233/0/57及57skip逐条原因，核对旧PNG/历史字节零漂移，保留I-4 NOT_RUN、D-8待处置和B-1…B-7限制；不改生产代码、冻结设计/契约/schema/Current/组合根/FEA-07 seam，不push。DSH随后处理findings、更新证据指针并运行集成验证，通过前不关闭Task、不释放新节点。
