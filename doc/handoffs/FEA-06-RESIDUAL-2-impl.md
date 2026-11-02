# FEA-06-RESIDUAL-2 R2R2 实施 Handoff

Task 保持 `in_progress`，本轮交付返修代码和可复核证据，**不声明 AC-1/AC-3 MET**。所有 PNG 的独立签署仍为 NOT_RUN。主要未完成：StatusBand 错误/运行专用通道、独立 NavRail 折叠视觉格、原生 200% DPI/a11y；域外治理指针/历史过度声明及 Controls 死代码清理交 DSH。D-14 为单独 ready 后续卡，未认领达成。

## 恢复点与提交

- 仓库：`G:/CODEX/New Manga`；branch/worktree=`main` / 用户指定同一 checkout；Git common directory=`G:/CODEX/New Manga/.git`。开始工作区干净，串行返修，无 worktree 删除/清理，无 push。
- Task base=`669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431`；本轮 start=`693567c202db0e7e132599e82cd03b13620363f3`。impl-r2 reviewed_head=`5944f96527b0adee6964a8b1266ddfa00de4e0d6`；其后漂移为 DSH 文档登记，本轮用户明确授权继续 scope v3。
- `013c24dfd`：真实资源/双主题/粒子前景/Reader视口/资源解绑/生命周期/状态断言第一切片；其 1280/0/57 仅为历史中间验证，后续逐图发现模板空白后继续修复。
- `a5a3663ae`：真实 Progress/ItemsControl 基类模板、模板状态覆盖、RepeatButton 动画边界、像素非空与全 SHA 唯一断言、渐变裁切与相位真实采样。
- `050c794ea5873a90a248009fc566fa9aff5ba589`：轨道刷子从 Binding 修为显式 DynamicResource，DesignRules 原检查不变。a5a 全量曾被该规则拦下，不作为最终 PASS。
- **最终 implementation/capture source head：`6b602c3fe72a31b4bafa0e6c61d6b73ba9bfc43d`**：失焦时重应用策略保持暂停；粒子暂停后 detach 也清理缓存层；原有18项装饰测试补充边界断言且计数不减。
- 本 Handoff、最终 PNG/inventory/log/处置表在 implementation head 之后作为证据文档提交；文件不伪造自己的 commit hash。inventory.head 精确记录捕获命令运行时 HEAD，不回填后来的文档提交。

## 实现与 finding 对照

**逐项 R2R2-001…018** 见 `verification/FEA-06-RESIDUAL-2/r2r2-findings-disposition.md`，包括 FIXED/PARTIAL/NOT_RUN、证据和待 DSH 项；期望键与 file:line 锚点见 `expected-tokens.md`。旧 Review、三份 impl-in*.log、旧四张 FEA-06/screens PNG、冻结设计与 pin 均保留原字节。

本轮代码仅在 Views/Fluent、ViewModels/Fluent、DesignSystem/Styles、App/DesignSystem tests 中；未改 Core、共享契约、Schema、生成物、Current V2、组合根、FrontendSelector、FEA-07 seam、Themes 或 Controls/FluentUi.cs。未新增依赖/随包字体/图片资产。Reader 输入为测试内存生成的线稿 fixture，通过 Host ReaderPageData 供给；不接触用户文件。

关键变化：真实 App.axaml 资源栈 + DesignSystemThemeManager + workspace 隔离 AppearanceCoordinator；每个组件做 light/dark；ReaderPage 真实加载页图且受视口高度约束；进度和缩略条显式基类模板；IconButton 使用 NmIcon/fluent-icon；Slider 实际 thumb/track 走令牌；粒子为前景稀疏点、同帧像素差覆盖<1%且可见，生产 clock 首/中/尾采样；渐变只选既有 Bg.Canvas/Bg.Overlay，原像素裁切注明 viewport/raster；资源订阅 detach 解除；Window Deactivated/IsVisible 真实接线。

## 验证与视觉证据

最终全量 **1281 passed / 0 failed / 57 skipped**（较1274 +7；App645/0/7、DesignSystem114/0/0），build=0/0，opt-in EXIT=0；生成器/check/pins均EXIT=0，旧四SHA不变。最终完整结果、实际命令和 EXIT 以 `verification/FEA-06-RESIDUAL-2/impl-r2-rework-verification.log` 为准。无过滤全量、opt-in 捕获、TokenGen/ThemeGen --check、check.ps1、verify_pins、旧四 SHA、禁止写域均须记录真实输出；任何未执行项不计 PASS。

- 默认运行零仓库写入；opt-in 前后 git status 只出现本卡 `visuals/**` 的替换/新增/删除，完整列表入日志。
- 视觉输出 **164 PNG：pages 8 / components 142 / decor 10 / shell 4**；同数 inventory 表行，全部含 source HEAD、frontend=builtin.fluent、mode、viewport、raster size、实际帧位、完整命令、EXIT 与 SHA。独立签署 NOT_RUN，不能以自动化渲染通过代替。
- pages：4页×light/dark，Canvas token 不同，并断言远离文字的背景 patch 像素差；ReaderPage 不再是空章节。
- 组件：IN-2A各组状态/AlertBanner九值 + Error/Skeleton/Empty/StreamingThumb + ChapterList/Thumb/Reader/Progress + Dialog/Drawer开关 + CommandPalette实际搜索结果/空 + ContextMenu/Tooltip。
- decor shelf：viewport=1280×900，raster=1048×720，crop=[216,95,1048,720]；first=0ms，中间帧=2000ms（不虚标精确4s半周期），reduce=static；生产 clock 另外采样0/4000/7950ms。
- decor reader：full=200ms真实粒子帧，reduce不创建层；同帧隐藏粒子做像素控制组；粒子只占阅读区<1%，不拦截命中。

## AC / 限制

| AC | 实施交付判断 |
|---|---|
| AC-1 | 行为/生命周期/像素断言补齐；视觉感知与独立签署仍 NOT_RUN，不写 MET。 |
| AC-2 | 16+1组属性/模板断言、派生选择器覆盖、D-11映射/锚点已补；D-14交叉例外保留。 |
| AC-3 | 空白/虚标主题/同SHA格已返修并扩展清单；StatusBand错误/运行专用通道无现成实现、NavRail独立折叠/原生DPI未跑，范围仍 PARTIAL；逐图签署仍 NOT_RUN。 |
| AC-4 | 本轮机械结果见最终日志；Task/STATUS/PLAN指针仍需DSH在授权写域更新，不能由本实施会话越界回填。 |
| OUT/BLOCKED/D-14 | 原分类与依赖保持，不写达成，不自行缩减冻结范围。 |

本轮使用当前用户更窄的 allowed_paths：因此未改 Task delivery_head、STATUS下一步、PLAN旧下一节点和全局 checkpoint §142/143；本 Handoff/处置表纠正其主题/计数/泄漏/失焦完成声明，DSH接收时追加当前说明。旧 Controls/FluentUi.cs 的粒子工厂/反向using已不在播放路径上，但死代码清理超本轮授权，明确 NOT_RUN。

## 下一接收者和可转发指令

推荐下一步：**DSH 接收返修并处置剩余清单/治理项，重新 Appointment fresh 独立 Reviewer 做 impl-r3**；本会话不自审、不关闭 Task、不释放新实现卡。Reviewer 可用 ZCode 或新的独立 Codex 上下文。

> 在 G:/CODEX/New Manga、main 接收 FEA-06-RESIDUAL-2 R2R2；Task base=669a4ae02，最终 implementation/capture source head=6b602c3fe72a31b4bafa0e6c61d6b73ba9bfc43d，证据提交见当前 git rev-parse HEAD。先读本 Handoff、impl-r2 Review、r2r2-findings-disposition.md 与最终 verification log；核验源代码 head 与 evidence bytes。允许 Reviewer 只写 doc/reviews/FEA-06-RESIDUAL-2-impl-r3.md；只读被审 head，不参与返修，不改 Core/契约/生成物/冻结设计/Current V2/组合根/FEA-07 seam。逐项复核 R2R2-001…018，逐图签署164 PNG（inventory=164行），检查真实light/dark、Reader页图/进度/缩略项、Slider/按钮模板实际像素、粒子可见性/覆盖面积、渐变crop/相位、ResourceChanged解绑/窗口暂停，以及声明的NOT_RUN；重跑build、无过滤全量（不少于本轮结果，57skip逐项归因）、生成器--check/check/pins/旧四SHA。opt-in仅写本卡visuals且要重新记录捕获HEAD，不改旧FEA-06。DSH须先处置R2R2-005剩余IN格、015/017域外治理和016死代码清理授权，再决定范围/后续Gate；未签署不写AC-1/AC-3 MET，不写D-14达成，不push。
