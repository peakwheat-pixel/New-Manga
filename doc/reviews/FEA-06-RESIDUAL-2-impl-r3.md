---
task_id: FEA-06-RESIDUAL-2
reviewer: Codex CLI fresh session（独立上下文 impl-r3 Reviewer）
reviewer_kind: agent
author: DSH 与此前实现会话；本轮 R2R2 为另一 fresh Codex CLI 实施会话
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: 4da4410f7d3a79dcd216f7f19c3d4f7bb6377ff4
implementation_head: 6b602c3fe72a31b4bafa0e6c61d6b73ba9bfc43d
evidence_head: 445afc0acfa36568ed3adaaf24e19c47bf0f7b7c
prior_review: doc/reviews/FEA-06-RESIDUAL-2-impl-r2.md
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 2
p2: 4
provenance:
  agent: Codex CLI fresh session /root
  appointment: 用户本轮 impl-r3 独立复核指令；DSH checkpoint §146 job pwsh-96fc40f29fce4204
  implementation_participation: none
  subagents:
    - /root/architecture_audit（只读生产代码与生命周期，未实现/返修）
    - /root/spec_audit（只读需求与断言，未实现/返修）
  mode: read_only_except_this_report
  date: 2026-11-03
  environment: Windows 10.0.26300 / PowerShell 7.6.8 / dotnet SDK 10.0.401 / net9.0 / Avalonia 11.3.22
  workspace: G:/CODEX/New Manga / main / common-directory .git
  head_moved_during_review: 445afc0ac -> 4da4410f7（仅 Task delivery_head 与 checkpoint 文档，无代码/测试/证据变化）
---

# Review：FEA-06-RESIDUAL-2 impl-r3

**changes_requested：P0=0 / P1=2 / P2=4。164 图逐图签署：158 PASS / 6 REJECT / 0 NOT_RUN（仅指已交付文件）。缺失的冻结视觉格仍为 NOT_RUN。**

本轮真实修复了上一轮的假 light 页面、空 Reader、空进度/缩略条、无效 IconButton checked、系统蓝 Slider thumb、被遮住的粒子与资源订阅泄漏。门禁实跑为 build 0 warnings/0 errors、全量 **1281 passed / 0 failed / 57 skipped**，不减于本轮基线；固定 head 副本 opt-in 重捕获的 **164 PNG 全部与被审 PNG 逐字节一致**。这些结果可采信。

仍不能批准完整 AC：冻结的 NavRail 折叠、StatusBand 错误/运行中格未交付；light 渐变全序列仅有 0–4 色阶变化，无法视觉签署为可辨的循环；另有 DangerButton 按下态约 1.18:1 的文字对比度，以及两个实际复现的生命周期组合缺陷。实施 Handoff 对大部分残项诚实，不把范围缺口变为 PASS。DSH 仍须处置 findings；本卡保持 in_progress，不写 D-14、OUT、BLOCKED、原生 DPI/a11y 达成。

## 范围与依据

开始时 HEAD=445afc0ac，工作区干净。审查中 DSH 提交 4da4410f7，只更新 Task delivery_head 和 checkpoint §146；本报告按用户允许的“其后仅文档提交”固定 reviewed_head=4da4410f7。代码/测试/PNG 与445afc0ac完全相同。已读 AD-002、STATUS、REBASELINE_PLAN 当前 DAG、rolling checkpoint 当前段及用户指定 Task、scope-r3、D-14 ADJ、impl-r2 Review、disposition、最终日志、Handoff；对照真实生产/测试文件和冻结设计02-motion、03-accessibility、10-component-inventory。

审查 diff 为 `git diff 013c24dfd^ 445afc0ac`，逐一核对 `013c24dfd / a5a3663ae / 050c794ea / 6b602c3fe / 445afc0ac`。禁止范围另按Task base `669a4ae02` 比较。真实文件数=pages8/components142/decor10/shell4；inventory164行、SHA164唯一、逐项SHA与文件匹配。未采信“唯一SHA=视觉正确”。完整逐图签署及字节绑定见附录A。

Reviewer及两只读子检查均未参与实现或返修；主审完成全部图像检查、门禁和仓外复现。唯一仓库写入为本报告，未改源码/Task/证据，未commit/push。临时 build、TRX、contact sheets、失败复现与固定head捕获副本放在 workspace 的 `agent-output/codex/FEA-06-RESIDUAL-2/impl-r3-review/`，不作为唯一证据：关键数据、失败输出、逐图SHA及skip原因均内联在本报告。

## Architecture（executed）

分层及禁止范围通过：本轮未改 Core/Host/IPC/schema/共享契约/依赖/用户数据，也未修改冻结设计、生成物、Current V2、组合根、FrontendSelector、FEA-07 seam 或旧 FEA-06 证据。样式修复及装饰执行器均在冻结允许路径。

真实主题链成立：`Residual2Evidence.cs:43-65` 从 App.axaml 的三项 ResourceInclude 重建资源，`DesignSystemThemeManager.Initialize` 并传入 `FluentShell.CreateRoot`，AppearanceStore使用workspace下Guid临时根，Dispose删除该根。四页light/dark非文本patch `(4,80,30,600)` 的18000/18000像素均不同（白背景与dark 26/28/31），不再只差 appearance.mode 文本。

资源解绑成立：`FluentTokenGradient.Bind` 仅attach订阅ResourcesChanged、detach解除，reattach刷新；粒子前景非命中，帧内仅Opacity/TranslateTransform，Canvas定位仅SizeChanged。Window Deactivated/IsVisible接线与单场景暂停恢复确实存在。但“无遗漏生命周期”不成立：detach清除失焦状态、重新attach重启，以及切reduce未取消暂停粒子，见004/005。旧 `Controls/FluentUi.cs` 未调用粒子工厂及反向using仍保留，处置表016诚实记为域外NOT_RUN；活跃执行路径已解除依赖，本轮不据死代码本身另加阻断。

**Architecture结论：契约/数据/依赖边界通过；装饰生命周期为PARTIAL。**

## Standards（executed）

按AGENTS、Task写域、协作协议§4/§4.1与冻结动效约束核验。未发现本轮越界写入或新增依赖许可问题。当前权威指针仍有旧状态冲突（006）。无足够影响证据的Fowler风格判断不列finding。

## Spec（executed）与 AC

| AC | 判定 | 依据 |
|---|---|---|
| AC-1：IN-1.1/1.2三态降级/暂停/无泄漏/视觉签署 | PARTIAL | 真粒子可见、首中尾生产clock采样及单场景测试通过，dark渐变序列可辨；light full序列未签署、失焦重挂与reduce组合缺陷实际失败。 |
| AC-2：16+1组解析后属性=令牌 | PASS（限冻结组） | Thumb/实际Border/track、派生九类、焦点环、D-11九值均有有效断言；D-14显式特判保留。额外交付的Danger pressed视觉不成立，不能由disabled属性测试外推其全部状态通过。 |
| AC-3：IN-2B像素格+独立签署 | PARTIAL | 158图PASS/6图REJECT；缺NavRail折叠和StatusBand错误/运行中。1280/1024默认壳不能替代缺格。 |
| AC-4：回归/生成器/治理/pins/旧SHA/写域 | 机械门禁PASS；权威指针PARTIAL | 全量1281/0/57、生成器/check/pins/旧SHA/禁止范围通过；默认零仓库写入，副本opt-in仅visuals；STATUS/PLAN仍待DSH统一。 |
| D-14 / OUT / BLOCKED / 原生200%DPI/a11y | 未达成 | 不属于本卡可认领成果；未运行原生测试，没有把headless96DPI写成原生验收。 |

## Findings

以下ID按本轮重新编号；已诚实披露的残项仍影响AC，不因披露而自动关闭。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R2R3-001 | P1 | `doc/tasks/FEA-06-RESIDUAL-2.md:116`；`FluentResidual2VisualEvidenceTests.cs:112-120`；`FluentShellSurface.axaml.cs:373-389` | 冻结IN格仍缺：NavRail折叠、StatusBand错误/运行中。1280与1024两宽度均显示NavRail，1024实际Medium而文件标compact；没有驱动专用状态。 | 四张shell图仅默认/较窄布局；截图底部明确Medium1024–1279 / Compact1280–1599。没有折叠、错误或运行状态文件。对应R2R2-005诚实PARTIAL。 | DSH裁决补齐通道或正式重冻结不可行格，不能由实施者自行移OUT/BLOCKED；补真实状态像素与签署。 | open；AC-3 |
| R2R3-002 | P1 | `FluentResidual2VisualEvidenceTests.cs:145-156`；`ShelfPageView.cs`渐变令牌与Opacity；两张light full渐变PNG | 真实light渐变虽不同SHA，但全帧first→mid最大RGB差仅2，first→reduce最大4，背景均值差约1.00/1.62；独立目视无法辨识循环变化。以tolerance=1/>1000像素只能证明数值抖动，不能替代可辨度签署。 | 原始1048×720光栅：light任一对差>8的像素为0；静态reduce保留为真实对照PASS，full first/mid REJECT。dark first→reduce最大13、163236个纯背景像素差>8，本轮dark序列可辨，区别对待。 | 用既有令牌/授权范围内提高light可辨度，或交DSH裁决明确感知验收；不添加新色/伪造帧，不以PNG字节差关闭002。 | open；AC-1/3；不是伪造指控 |
| R2R3-003 | P2 | `Styles/Controls.Fluent.axaml:324-326`及`:404-405`；两张danger-button pressed PNG | 控件pressed把Foreground切Bg.App，但真实PART_Root仍StatusMuted.Failed，控件Background与模板Background不一致，按下时文字几乎消失。 | dark文字(15,16,18)/背景(45,29,27)对比1.181:1；light文字(244,243,240)/背景(235,222,216)对比1.185:1。截图均REJECT，模板和解析后前景规则可直接解释。 | 对齐实际模板pressed背景与前景，增实际PART_Root/ContentPresenter及像素可读性断言；不以disabled组PASS外推pressed。 | open；AC-3 |
| R2R3-004 | P2 | `FluentDecorativeMotion.cs:129-145,173-184` | 窗口已失焦，导航切离书架再返回时DetachWindow清除_windowDeactivated；OnTargetAttached无条件Resume，未等Activated就重启8s循环，违反失焦暂停。 | 仓外反射复用既有Create/ManualClock：HandleDeactivated→Workbench→Library；`Assert.False(IsRunning)`实际True。见附录C，实跑FAIL。粒子新建路径同样不检查已失焦，但未单独实跑，不另计finding。 | 保留/重新读取真实Window失焦状态；重挂载、新播放和IsVisible恢复均遵循同一状态门禁；补组合回归。 | open；R2R2-011 PARTIAL，AC-1 |
| R2R3-005 | P2 | `ReaderPageView.cs:305-311`；`FluentDecorativeMotion.cs:260-289` | 粒子播放100ms后失焦暂停，切reduce仅更新后续时长，不移除现存层/取消闭包。再次Activate旧动画用原400ms余时继续运行，reduce下仍有帧回调。 | 仓外复现切reduce→Activate→clock.Advance(100)，期望PendingFrames=0，实际1；旧粒子层仍非null。附录C实跑FAIL。 | 策略归零时取消并移除已有粒子；覆盖reduce、auto系统关、category-off在播放中/暂停中切换。 | open；R2R2-011 PARTIAL，AC-1 |
| R2R3-006 | P2 | `doc/STATUS.md:10`；`doc/REBASELINE_PLAN.md:42`附近旧“下一节点”段 | 当前STATUS仍写“无READY节点”，PLAN已列READY D-14；旧DAG段仍将已closed的RESIDUAL-1写in_progress/下一节点。恢复入口相互矛盾。 | 4da4410f7已修Task.delivery_head并追加checkpoint146，但未修这两处；处置表015为NOT_RUN，不能判FIXED。 | DSH在授权治理写域统一当前指针，历史原字节保留或明确标历史，勿让旧段冒充当前状态。 | open；R2R2-015残项 |

## R2R2-001…018 逐条复核

FIXED只表示该finding在本轮被证实关闭，不表示整卡AC通过。

| 原finding | 本轮核验 | 证据/处置真实性 |
|---|---|---|
| 001 | FIXED | App资源+Manager+workspace隔离+四页非文本patch18000/18000差异，组件双主题真实。 |
| 002 | PARTIAL | 粒子前景与同帧隔离可见性修复，dark渐变通过；light仍不可辨。实施表明确渐变待签，诚实，不能把该条整体写FIXED。 |
| 003 | FIXED | thumb、真实模板Border及track已令牌化；default/hover/disabled光栅无系统蓝；新断言读取实际模板，非只Foreground。 |
| 004 | FIXED | NmIcon.Settings + fluent-icon/checked，checked可见金色背景与边框，不同于default；双主题均签PASS。 |
| 005 | PARTIAL | 真实Host ReaderPageData页图、60/100进度、两缩略页、三章列表均可见；缺IN格见001；Handoff诚实。 |
| 006 | FIXED | expected-tokens逐态明确键/属性/file:line，D-11四态↔九值、D-14例外齐全；未拿普通Panel默认表面冒充特殊状态表面。 |
| 007 | FIXED | RequiredSelectors补九类；Chapter/Streaming/Reader/Progress/SettingsGroup/SettingsField/TabStrip解析后属性实际断言。 |
| 008 | FIXED（剩compact标签见001） | inventory164行16列，SHA/尺寸/viewport/frame/frontend命令EXIT/source head准确；capture head6b602c3fe与后续证据提交分开，无自指hash回填。 |
| 009 | FIXED | 最终日志1281/0/57、57条skip原因准确；旧impl-in*.log保留历史字节，本次独立全量复现。 |
| 010 | FIXED | ResourcesChanged attach/detach成对；reattach换主题回归实跑通过；重复checked规则已去除。没有对全部进程GC泄漏作无依据承诺。 |
| 011 | PARTIAL | Deactivated/IsVisible接线、生产clock采样与detach清理成立；组合状态004/005实际失败，“已修复接线”不能扩成完整AC-1通过。 |
| 012 | FIXED | Tab键聚焦SearchField内部TextBox，外nm-focus-ring可见并为Accent.Base/Border.Focus；旧注释已纠偏。 |
| 013 | FIXED（交付文案）；治理部分PARTIAL | Handoff准确164图/真实主题/限制；4da4410f7把Task.delivery_head更新445afc0ac；尚余006。 |
| 014 | FIXED | 原仓默认全量后status无源码/证据变化；旧目录SHA不变；固定head副本opt-in成功，仅本卡visuals变化，164PNG与原字节完全一致。 |
| 015 | PARTIAL / NOT_RUN残项 | Task.delivery_head已由DSH修；STATUS/PLAN旧段未处置，006保留。 |
| 016 | PARTIAL / 域外清理NOT_RUN | HasMotion限定finite、活跃粒子按归一化progress，帧内无布局写入；旧未调用工厂/using仍在域外，记录诚实，不凭清理未跑虚称FIXED。 |
| 017 | FIXED（新证据）；历史治理PARTIAL | 全部新图frontend=builtin.fluent，decor与pages同数据Host；checkpoint146追加新交付与未完成项。旧142/143过度声明留原字节且由新文档纠偏，仍需DSH统一当前入口。 |
| 018 | 保持后续卡 / NOT_RUN | D-14裁决A与独立ready卡保留，StatusCatalog未改，本卡NotStarted特判保留；不写其达成。 |

## Verification（executed）

运行头：Windows10.0.26300、pwsh7.6.8、SDK10.0.401/net9、head445afc0ac开始，结束4da4410f7；两者代码/测试/证据字节相同。输出中的PASS仅限实际运行项。

| 场景 | 实际命令或步骤 | 结果/EXIT | 判别证据 |
|---|---|---|---|
| build最终重跑 | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | PASS / 0 | 0 warnings/0 errors。首次因既存testhost62764锁DLL失败；未终止他人进程，锁释放后同命令成功。 |
| 无过滤全量 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo --logger trx --results-directory <workspace>/impl-r3-review/results-normal` | PASS / 0 | 1281/0/57，总1338；逐程序集及逐条skip见附录B；无filter。 |
| 隔离输出尝试 | build/test加`--artifacts-path <workspace>/impl-r3-review/artifacts` | build PASS；test中止，不计门禁PASS | 新Residual2Evidence.Root仅向上寻找Task文件，仓外artifact路径找不到；这一尝试的错误不混入最终全量数字。 |
| 默认零写入 | 运行前后`git status --short`及旧证据SHA；测试内状态/旧目录SHA断言 | PASS | 本报告落盘前status为空；HEAD仅DSH文档前进，没有源码/证据dirty。 |
| opt-in独立复跑 | workspace中`git clone --shared --no-checkout --no-hardlinks --no-tags`，sparse-checkout所需apps/doc/tasks/证据，checkout445afc0ac；build App.Tests后`NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1`，运行inventory记录的App.Tests视觉类filter | PASS / build0、test0 | 1/0/0；164PNG全部同字节；副本status仅`M verification/FEA-06-RESIDUAL-2/visuals/visual-inventory.md`（capture head由6b变445，符合真实运行head）。未写原仓证据。此filter仅为捕获，不冒充全量。 |
| TokenGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | PASS / 0 | 292 rows，byte-for-byte up to date。 |
| ThemeGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | PASS / 0 | generated theme artifacts match frozen token source。 |
| governance | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS / 0 | 15 current documents；3 warnings（10非终态Task、STATUS/PLAN体量预算80%），非语义裁决。报告落盘后再跑同命令。 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PASS / 0 | 15/15。 |
| 旧四PNG | `Get-ChildItem verification/FEA-06/screens -Filter *.png \| Get-FileHash -Algorithm SHA256` | PASS | 四值完整列于下表。 |
| 禁止范围 | `git diff --exit-code 669a4ae02 445afc0ac -- <禁止路径集合>` | PASS / 0 | doc/design、DS/Generated、DS/Themes、verification/FEA-06、Presentation.Avalonia、ApplicationCore、CoreClient、Host、doc/contracts、App/Shell、App.axaml/.cs、MainWindow.axaml.cs、FrontendSelector均零diff。 |
| 生命周期组合 | 仓外Probe读取被审build DLL，反射复用现有测试Create/ManualClock，仅在workspace建测试文件 | FAIL / 1 | 两个判别断言失败，非原全量内测试；源码/关键输出见附录C。 |
| 原生DPI/a11y/桌面触控 | 未执行 | NOT_RUN | B-5/D-1，不用headless96DPI替代。 |

旧FEA-06四SHA：

| 文件 | SHA256 |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

**Verification结论：机械回归通过；视觉缺格、6图REJECT和两个组合失败使AC-1/3仍PARTIAL。**

## 结论与复审 / 推荐下一步

建议DSH接收本报告，先处置R2R3-001/002的范围与验收，再释放最小返修；当前head不满足整卡approved门槛。D-14继续单独后续卡，不在本审查中实施。复审需固定新head及逐条disposition，保留本报告原字节；不得只附新的测试总数申请通过。

下一工作为 **FEA-06-RESIDUAL-2 findings处置与返修范围登记**，Agent=DSH；启动条件=接收本报告，依赖当前scope-r3。Recovery point：仓库`G:/CODEX/New Manga`，main/同工作区，base669a4ae02，reviewed_head4da4410f7，代码6b602c3fe，证据445afc0ac。建议DSH先在其授权doc/tasks、STATUS、PLAN及追加裁决中决定缺格通道/渐变验收并修当前指针；源码返修仍由DSH另行分配Codex或ZCode、明确allowed_paths，不自动扩共享接口/schema/依赖。交付为本轮finding disposition、固定返修commit、Handoff和本卡verification。验证必须重跑build、无过滤≥1281/0/57、生成器/check/pins/旧SHA、附录C组合回归与6张拒绝图加缺格真实签署；上下文独立Review后由DSH集成验证。

可直接转发给DSH：

> 请在G:/CODEX/New Manga的main接收FEA-06-RESIDUAL-2-impl-r3.md（changes_requested，0/2/4；base669a4ae02，reviewed_head4da4410f7，implementation6b602c3fe/evidence445afc0ac）。请先处置R2R3-001缺冻结IN格、002浅色渐变可辨度及006当前指针，不把缺格自行改OUT/BLOCKED；在Task/STATUS/PLAN及追加裁决登记最小返修范围、Owner、基线和allowed_paths。再分配Codex或ZCode修003模板pressed前景/背景、004失焦重挂、005播放中/暂停中降级清理，并补判别断言；只写授权Fluent/DS样式/测试和本卡证据/Handoff，不改Core/Host/IPC/schema/冻结设计/生成物/CurrentV2/组合根/用户数据，不push，不做D-14。交付固定head、逐项处置、真实截图与Handoff；build及无过滤≥1281/0/57、57条skip原因、生成器/check/pins、旧四SHA和禁止写域全部复验，并复现本报告附录C及逐图拒绝/缺失格；另Appointment独立上下文Reviewer。当前Task保持in_progress。

## 附录 A：164 PNG逐图签署

签署人：Codex CLI本独立Review会话，2026-11-03。路径统一相对`verification/FEA-06-RESIDUAL-2/visuals/`。每一行均已查看对应原图在标名contact sheet中的实际像素；重点Reader/粒子/渐变/模板另核代码、原尺寸像素与配对差。缩放图只用于并排查看，未修改提交证据。SHA锁定被签字节。

PASS只签署该文件所标场景的真实可见内容，不签署整组件所有状态、原生DPI/a11y或缺失格。StreamingThumb lazy的静态骨架是Task显式允许的懒加载态；AlertBanner普通Panel仅作为其真实基底，九值以glyph/标签差异核验，不冒称九种专属表面。reduce静态图仅签真实对照，不替代full动效证据。

| file | 签署 | 理由 | SHA256 |
|---|---|---|---|
| `components--alert-banner--blocked--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `889624c7872462760cc7545756717001ea63349fd747c19b4b39b22bc77a5b24` |
| `components--alert-banner--blocked--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `5d540e07adc5dcda6252092cb9e7b01708fbb2079d4755bddc412378f623154a` |
| `components--alert-banner--done--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `7a4d26627e72ace2020ff5ea0e51adc970e4b03184e30a8acbd5fa1386c8474e` |
| `components--alert-banner--done--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `163a6a8d34bc3115045d0ca15df288d686880733d038319321a454bdef346cf8` |
| `components--alert-banner--failed--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `4e795504d6985ae9096333d8fb4eef07d5619a75dc5c8456669ac7b0871da9b0` |
| `components--alert-banner--failed--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `c0c0ff3836fba3fceb4f8a4bc58423f3d8fb0e77d10c94e7b53abbdf4376c719` |
| `components--alert-banner--locked--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `dd5a7ffc3450eeeb9dbb85065152f8f1c5a3714caba00d585420077e5f71a78a` |
| `components--alert-banner--locked--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `bc5b80643145d8192e36d9b3f1a81ad4d3db0c1212559f9aaaa0343b57e446e7` |
| `components--alert-banner--notstarted--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `bbaa2d452fc25923a23d2ad06a4c4f75fbe5a04a8d650fb4cb51b267db021eef` |
| `components--alert-banner--notstarted--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `e2154725e7c1eae2a64f9e84a8b8cba298bdaa5fe74cb08b04a793e1f1d61f3a` |
| `components--alert-banner--queued--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `41f70aa437e62c3463760aab8ded163ee5bcc76b12f609c13370eebae3d6b0c5` |
| `components--alert-banner--queued--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `0f10612d149089d0d9aed4ee66177f239f1fa9b67f704bd96f2b0381c42b53fb` |
| `components--alert-banner--running--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `99c5e3c53622e072898c86ea2aae0d2029d9d4e0b7fd8b83c35f0719f7356ce2` |
| `components--alert-banner--running--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `4b694feb9fd9888e13eec5e5fe60bc49b2c82469c5486bbb123d61db9e232e11` |
| `components--alert-banner--skipped--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `a0ffe5811f77b4772115d3455cc443e94f938f6cf57c4f7a3eae992b073da157` |
| `components--alert-banner--skipped--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `c8bb612c824489e5a896f5e3aa2138c32550a2f30df26f390fbdd43c689331e1` |
| `components--alert-banner--stale--full--dark.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `c3bc9b631b8eb5b51282a81e0c7fcfebf274fda9bb3effaecb3a105b3145afca` |
| `components--alert-banner--stale--full--light.png` | PASS | 状态glyph/标签可见；基底与九值映射相符 | `a87e56fd424452afbec7746b1fb573ce28f317f00d5d075dc65c0fba8baeb64b` |
| `components--book-card--default--full--dark.png` | PASS | 书名卡可见；禁用格按Opacity降级 | `2b49270515c35d9d25a4ed2af95627d95ec92ec6df94e2abdfa8f43fca7567b7` |
| `components--book-card--default--full--light.png` | PASS | 书名卡可见；禁用格按Opacity降级 | `4155acd86a1b6a0fe18a8ca2adbd0eda43dc88665f52811e56531d94c23458d8` |
| `components--book-card--disabled--full--dark.png` | PASS | 书名卡可见；禁用格按Opacity降级 | `a379dba17d8109c2da45f7bddf371ae47dd8bd9db5d3f7e22baa7169f88594bc` |
| `components--book-card--disabled--full--light.png` | PASS | 书名卡可见；禁用格按Opacity降级 | `611bd5b99caf77161b02dabc5a81d92113e924141b54e036423060453286005e` |
| `components--book-row--default--full--dark.png` | PASS | 书名行可见；禁用格按Opacity降级 | `d4be22a5228aa3f8930cd8e2ae25789cdcd843780146a68d1d5f61228a89afdf` |
| `components--book-row--default--full--light.png` | PASS | 书名行可见；禁用格按Opacity降级 | `f3e1043e9fca4fe3bedc316a8b6d9e16a1d3e810e3456da80eaeec343df48324` |
| `components--book-row--disabled--full--dark.png` | PASS | 书名行可见；禁用格按Opacity降级 | `661615cb6d3be9fd287c54c36ba03082bcc02d78a0c686110fc0369d9c9167e6` |
| `components--book-row--disabled--full--light.png` | PASS | 书名行可见；禁用格按Opacity降级 | `17d95b8b06885f6bc4a6e676169a50885a30b011701f29bcad0a8e89c662f32c` |
| `components--chapter-list--default--full--dark.png` | PASS | 三章行完整可见，无旧顶部裁切 | `54d5facd816f38d120a9fc5adcfcdd8a31b3258c182b8949a077dfefeaa33386` |
| `components--chapter-list--default--full--light.png` | PASS | 三章行完整可见，无旧顶部裁切 | `f4bc1e72aa58d8bfb6f4045028e95badfc02bb6255f0535ade7252bdd32159d5` |
| `components--command-palette--empty--full--dark.png` | PASS | 实际搜索输入与零行/真实命令结果可见 | `90ac667c6329844e3d9ca99b8a181530f019a920b491bb1394a333bfc941ddb4` |
| `components--command-palette--empty--full--light.png` | PASS | 实际搜索输入与零行/真实命令结果可见 | `fdbe84a4793048856a47e34c134a73e201e0c64a2ac845843e79970e47975d48` |
| `components--command-palette--result--full--dark.png` | PASS | 实际搜索输入与零行/真实命令结果可见 | `3e3117b108988ca8ea69eb623237ac5fcb72b02755ddf7c24ff7b72312010dbb` |
| `components--command-palette--result--full--light.png` | PASS | 实际搜索输入与零行/真实命令结果可见 | `bc29b1dead005a23b2b1728ae0cd7e7c656acecf2b83992bf93cd6b8e2220085` |
| `components--context-menu--disabled-item--full--dark.png` | PASS | 实际菜单打开，禁用项有可见降级 | `8a58e962dd4219c04b2daaa5914999a34acf64f073b4039e970cab33ab8191bc` |
| `components--context-menu--disabled-item--full--light.png` | PASS | 实际菜单打开，禁用项有可见降级 | `66d6d2856d808299064b6c7e5986856f335185c2510d438607fbab9862ce49ac` |
| `components--danger-button--default--full--dark.png` | PASS | 实际按钮状态与主题可见 | `6a41f040ec40ba869973b2cb31e89b16a71380e79693f2a06956b33bcd0281d2` |
| `components--danger-button--default--full--light.png` | PASS | 实际按钮状态与主题可见 | `1d8455eaf665cdd6b7571a30a955bb5a67b886c80dc1ec1c9865e2ca780adcc7` |
| `components--danger-button--disabled--full--dark.png` | PASS | 实际按钮状态与主题可见 | `860f0a294d694add33ba817e43cc852d2e8e823ccba920e3603cef19aab4d0ed` |
| `components--danger-button--disabled--full--light.png` | PASS | 实际按钮状态与主题可见 | `9149c20ee24a91492f1add37dcc719686595390af0869a50973bc497ebedcf42` |
| `components--danger-button--hover--full--dark.png` | PASS | 实际按钮状态与主题可见 | `be969a6bb952c675bda2e1172da9dfe5d50fac5fd55cef03e324495b24359d4a` |
| `components--danger-button--hover--full--light.png` | PASS | 实际按钮状态与主题可见 | `9dc59d68f89479997baecd320880b65cd967d841753286d0a4f1d71452a926df` |
| `components--danger-button--pressed--full--dark.png` | REJECT | R2R3-003：文字与实际模板背景约1.18:1，按下态不可读 | `a19ca3dda2c87b7078d994ff559baefdc32d9cd2e2a2baebe5ad536c5f8a2f77` |
| `components--danger-button--pressed--full--light.png` | REJECT | R2R3-003：文字与实际模板背景约1.18:1，按下态不可读 | `5bc2d9c8bfec5f98c805bd28f2a1154399077306355a35de47aac6e12aabb24b` |
| `components--dialog--closed--full--dark.png` | PASS | 开态内容可见/关态内容移除；只签开关 | `8ac09c4e2df3f412b5a45695aadf0bddc7035b3faf45d4dd063405bc0e3de48a` |
| `components--dialog--closed--full--light.png` | PASS | 开态内容可见/关态内容移除；只签开关 | `12417c1281d9511903ddfe5d90ec27972402b28cbfd53d27a81704e9d0128659` |
| `components--dialog--open--full--dark.png` | PASS | 开态内容可见/关态内容移除；只签开关 | `658516ddfb910a804a2a1c903f79d86b637918c312e4ad0cefdefb7bba306651` |
| `components--dialog--open--full--light.png` | PASS | 开态内容可见/关态内容移除；只签开关 | `d0802f517cce8b3ffb55e3a210536bcf1eee78dc8ce173c2a8b06987e6b41dfd` |
| `components--drawer--closed--full--dark.png` | PASS | 实际抽屉开关内容可见/移除 | `3a23880327ee14fa9bb2129e23db725f4a0fa7b602295ba53331d7fe92dd95e5` |
| `components--drawer--closed--full--light.png` | PASS | 实际抽屉开关内容可见/移除 | `87da9a58f004be601d18b043b2eddb80a881d96a35e9a295c0a2851855c9b08b` |
| `components--drawer--open--full--dark.png` | PASS | 实际抽屉开关内容可见/移除 | `89177c7a4d87f7c6d47ba499e2dd8def32ac4ad6d53793efa20a1d650b22b301` |
| `components--drawer--open--full--light.png` | PASS | 实际抽屉开关内容可见/移除 | `f2af162bb59466d6d3af98961b858c52c9966d80f32814f3ee1a0ac667abe2be` |
| `components--empty-state--default--full--dark.png` | PASS | 标题、提示与导入动作可见 | `00ebe5a1fb4d8f0bcae9cad3b1a8a1ad705e828c67ba93649fa61eeabf94ca2c` |
| `components--empty-state--default--full--light.png` | PASS | 标题、提示与导入动作可见 | `fc608c250bd153f58ba53625b92ec5aeefba30f188c89c6b451811b0b066d36a` |
| `components--error-state--retryable--full--dark.png` | PASS | 错误提示与有/无重试动作可见 | `95e877efe79f19166792bef6df47f17f376e677aba7bccc1870d996447fd6275` |
| `components--error-state--retryable--full--light.png` | PASS | 错误提示与有/无重试动作可见 | `d14df0c76fddc633c968a984575d190192e80840a876734bfbd8083e5984cf65` |
| `components--error-state--unrecoverable--full--dark.png` | PASS | 错误提示与有/无重试动作可见 | `5433294d678ee91518da15555b8b3630d74a04e8d83475f1b50da405e9433af5` |
| `components--error-state--unrecoverable--full--light.png` | PASS | 错误提示与有/无重试动作可见 | `403d1287e9e6e0e5fc7b7a634362bfab9bde3b624a6bd31f1fd69a46b7aba622` |
| `components--icon-button--checked--full--dark.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `92fd3d87c790490f7abef0ff92f0b47e0af790063bb71f01123d9df360a165a3` |
| `components--icon-button--checked--full--light.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `d009b3061519b65f92451ea1c08ba9c8f88fc8e00a56bf3e31204bbb5a4db589` |
| `components--icon-button--default--full--dark.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `a76694f35f67dc4fc002b0d0bf7f331f93fe77d86b8c5d5921a7cbb782e87cbe` |
| `components--icon-button--default--full--light.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `dbe9ead20b6ee7668251604d59e9eac257327fd84f1f64927b9331d027ff06b6` |
| `components--icon-button--hover--full--dark.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `36739cad328ce06cd45e1e060651668ceeff5b1b13d0154c9a51018034d554b2` |
| `components--icon-button--hover--full--light.png` | PASS | 真实NmIcon；checked边框/背景、hover可见 | `0ee78de15661439f7382201ba67dab8d7123a1803cb9451ce5665d338fd1e74c` |
| `components--page-thumb-strip--default--full--dark.png` | PASS | 两张真实fixture缩略页及页码可见 | `c0a1b356140f095b360aa0e13525b2577cc506a432020068441f36b95fea6626` |
| `components--page-thumb-strip--default--full--light.png` | PASS | 两张真实fixture缩略页及页码可见 | `232e323c050233cde9ef3a2be0cdeded6948a3e6812cd49c7062c6b23597db7b` |
| `components--primary-button--default--full--dark.png` | PASS | 主题化按钮与所标交互态可见 | `11fa85f9e7a5f03e6a32b8ef79bd2f944556310d4a506e888c03db45f7de794e` |
| `components--primary-button--default--full--light.png` | PASS | 主题化按钮与所标交互态可见 | `ccaf77f6cfc0095e4f14951805384f820a4895fba409900d0718ef165f112849` |
| `components--primary-button--disabled--full--dark.png` | PASS | 主题化按钮与所标交互态可见 | `19096cdb5df881d61ad3ae2f43f8ff6ac34aadbed4e5e501bc0a163790e65c3d` |
| `components--primary-button--disabled--full--light.png` | PASS | 主题化按钮与所标交互态可见 | `1ea6a98c677b17d93fb066256cac6a0894ac05bd0d2ef59b4ec527ab67f42834` |
| `components--primary-button--hover--full--dark.png` | PASS | 主题化按钮与所标交互态可见 | `058ccb1d999c4e4f39f51328c51faaebbf7d0d10425e2493bb9569546405c27a` |
| `components--primary-button--hover--full--light.png` | PASS | 主题化按钮与所标交互态可见 | `a221df936ec221b8a3e4abfc2c64ef1e4f0e0389fb52cdcadd5a7d5c0483e34f` |
| `components--primary-button--pressed--full--dark.png` | PASS | 主题化按钮与所标交互态可见 | `7bd2d5cf594bcbe8527a3e59a3b7706b3b63b67ed2285de07f1550c0c1c2a955` |
| `components--primary-button--pressed--full--light.png` | PASS | 主题化按钮与所标交互态可见 | `966913b84077ce64a6cd571bb7b158b78b3d0b859d7e4663355ec4d662301f01` |
| `components--reader-page--single--full--dark.png` | PASS | 真实fixture图像，非空章节占位 | `bcc7af72ece3d9b5e125c63a71c403d5c33be00bbab7ceda1532bb4efab95182` |
| `components--reader-page--single--full--light.png` | PASS | 真实fixture图像，非空章节占位 | `e3f00ce494d670cf1e68710b0fb1c7a82491ef1a401a23ecba369bc103cccd55` |
| `components--reader-progress--default--full--dark.png` | PASS | 实际60%进度填充可见 | `58c8d0d619c7e0bd14466c858781cb6124ced8c676744020b9309b97f7bf690a` |
| `components--reader-progress--default--full--light.png` | PASS | 实际60%进度填充可见 | `0beab56ff843af1299a11b62a6eecf27871645195cd620dab18f689d3a045a31` |
| `components--region-box--default--full--dark.png` | PASS | 区域边框与hover填充可见 | `f3b894536c2572c74ec509e12d62a10c47cb8108c1f275ccf2af1e602d3e4426` |
| `components--region-box--default--full--light.png` | PASS | 区域边框与hover填充可见 | `c9d3be1cc6e7142e8f8beb303619091a6644123948e672f920da4acd21bc0051` |
| `components--region-box--hover--full--dark.png` | PASS | 区域边框与hover填充可见 | `f62a1758ab3074ac07b2434cbf4e9dce6f55640331522edb2e706b4554d6d42d` |
| `components--region-box--hover--full--light.png` | PASS | 区域边框与hover填充可见 | `17f44ae5eb9b98aa30a1e446bdd0809522d3f376ecdf578addd59d3bf11ac600` |
| `components--search-field--default--full--dark.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `dbc55aaef36076c30c35a6bc0f18da5f79ce9299fa457ebfe5251836b0290bae` |
| `components--search-field--default--full--light.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `27a98ef1deb62665126467e998639b74f366c4f8d76ac89abce5ad383c05cc5d` |
| `components--search-field--focus--full--dark.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `ca1645c4d6675445eb86d444829d8419e5256471524f8e462fab4b20f143a747` |
| `components--search-field--focus--full--light.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `b9d104868ae380e64b973d609c369f0a7a1883c886f5583edb8633d2204c089c` |
| `components--search-field--value--full--dark.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `eff1c117102189d659c3c4d224d121ba36388b96ba74a8f5f4c1518f012acce1` |
| `components--search-field--value--full--light.png` | PASS | 输入/值/Tab焦点外环与所标状态相符 | `9357d1f26a74a6bd8b6cfda1f20f515ea1698208b56aa62690cd8104152d3267` |
| `components--secondary-button--default--full--dark.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `6225650c0f4293b861aa2eccc06c726ca717c977c935a68598443d2aa19f9220` |
| `components--secondary-button--default--full--light.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `e3bfe1fbe83bb94888ee20dd3818dd5bc8b6d80f85beb6aa945e1eab3b4c2a14` |
| `components--secondary-button--disabled--full--dark.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `36721b2c032c5db03e353bfdd3d3f44677c27b6cce80a6ac4620a8cac133c131` |
| `components--secondary-button--disabled--full--light.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `2884f66463b69191dcefff138ed22551c1957cdce4f79620ca6b02b3b6e4ae98` |
| `components--secondary-button--hover--full--dark.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `bb96910170e0fbdf3a921f6b58c89ce7b6da7fb79b0842da46b6763cf71b2615` |
| `components--secondary-button--hover--full--light.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `e57ed5263bca2e360471898acbf01495f5115fda904c3101a6dea021837e3a8f` |
| `components--secondary-button--pressed--full--dark.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `61222ad0c8aaf2811461c14e78bd344af3294bad1c3452f9066823699169e4ed` |
| `components--secondary-button--pressed--full--light.png` | PASS | 实际默认/hover/pressed/禁用态可见 | `b0be52d745db064b268341b035a824771300f4f6e039616fe66322818e43c516` |
| `components--segmented-control--hover--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `28a542455894ce62b044bab1e8aac9497c5ea143f9dc0eaa1571f7d6bfb14122` |
| `components--segmented-control--hover--full--light.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `465c95af1b22d85ebf8abc205b3109b524e48e79c8b8a851c5c6df7169f6f18b` |
| `components--segmented-control--pressed--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `a3943901f5d06267c9ce416b44a73f1eb2543c1bd39263c5393095f497fcde47` |
| `components--segmented-control--pressed--full--light.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `29ce0fbc6992550f8d840354daa1370e7d45fc735433aac023cda548284f1336` |
| `components--segmented-control--selected--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `e3009ea3f427ce92841d2c2288b8cc847dc1fab4ab44c2c2ac9c467608520500` |
| `components--segmented-control--selected--full--light.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `b0eb26a82c36024b2007657eeee301567c888526e077f24eb0f89e64f8f8794d` |
| `components--segmented-control--unselected--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `5cb43a0b3307144d3fbb88636825b62638cb7462658cc9b70d8b017326ae7e40` |
| `components--segmented-control--unselected--full--light.png` | PASS | 目标项选中/未选中/hover/pressed可见 | `8488e5063a86e0fd17beeafa260569714e3491cfbf0b902152e45248da22676d` |
| `components--settings-field--disabled--full--dark.png` | PASS | 字段值及错误边框/禁用降级可见 | `6860034d4c29c33658afcbc3752a3c187516d6dd411c167562eed1aea058ddc0` |
| `components--settings-field--disabled--full--light.png` | PASS | 字段值及错误边框/禁用降级可见 | `0e5f8d1d74f77f6aecb4bfc5a6f372c81165953393ac537b5bf0ceb202f625d3` |
| `components--settings-field--error--full--dark.png` | PASS | 字段值及错误边框/禁用降级可见 | `8bc7233b0d73cf6f53de6b975933f9215075ede8b1f7030a136af4f3a20dcb86` |
| `components--settings-field--error--full--light.png` | PASS | 字段值及错误边框/禁用降级可见 | `d7550f543ac0d743f328a2f832b3b667bb1942e58d703864a16094ab3dabf19b` |
| `components--skeleton--bookcard--full--dark.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `b4c23048c005e5586c44d05f505205fe395f0115de5f7ebc4e9f28ce3808c274` |
| `components--skeleton--bookcard--full--light.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `851e1f1010efe1f3f8f0b47e4e1bb615a23120d5c8bca9d8e9fd06d11704a3d3` |
| `components--skeleton--panel--full--dark.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `80b35caafbc126f921557f83f286d8181faf3ab4da629d3bdf28026605c10623` |
| `components--skeleton--panel--full--light.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `51e7b0bae6c7e7a3d756ed912156ae74bc4f0d549b8145b75097cc3a2532f22c` |
| `components--skeleton--row--full--dark.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `c467ecc7edf60eb05436ff3b6ce28dced2b37ada5ed218177ac7542a3bbd22e3` |
| `components--skeleton--row--full--light.png` | PASS | 所标骨架形状可见；尺寸不同非同SHA占位 | `f0d55c31d58648991c094e2010dd09034075d7c5986d077652b846cb02c40deb` |
| `components--slider--default--full--dark.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `ce971a4da37eb85f49984872bd59047eae23a6b1ddfc6de7dace352492d97768` |
| `components--slider--default--full--light.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `a9c0e297603c3bcfb861df94a0e2abdd483bee21ed5de80f88968174e453ee4d` |
| `components--slider--disabled--full--dark.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `afc956e90e3da7f0ea600c29adf7bf3ca1b506a61f269d11d9dbfc48efe571ea` |
| `components--slider--disabled--full--light.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `be751e7678927cc6a76d8f135538293e418f1f497d3d7c2a5b4d266dfc295dbc` |
| `components--slider--hover--full--dark.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `006731cca2a8e34b29dd5c5742d6c19c4e5e210cc59174b862cb0837e1e6a037` |
| `components--slider--hover--full--light.png` | PASS | 真实thumb/填充轨道，无系统蓝；状态令牌可见 | `7632eb4ee7f4f58f7897dd72fc78986b68b7ae5d33472ed8b13d8bff176ed6e4` |
| `components--streaming-thumb--lazy--full--dark.png` | PASS | Task允许的lazy骨架态可见；不作已加载图像签署 | `70da80c565c842c894ff3ad7ca3d8be6ba6c903de1b0bf5f9b7146f02d0e5231` |
| `components--streaming-thumb--lazy--full--light.png` | PASS | Task允许的lazy骨架态可见；不作已加载图像签署 | `9fe5f380156f6c1efe36f680e43b27820ad8858a9f1a5ab1127a3cd0c9f79938` |
| `components--surface-card--default--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见 | `a1b460f11e58a8d929ae23da500b4c5a0b81773b12fc590b722cd87de9df721a` |
| `components--surface-card--default--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见 | `4749378885e3e70debe7fe35002fd1e3c9289e8963dd5a1e3c889a8be74b89e6` |
| `components--surface-card--disabled--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见 | `165d3b8bdcab65efa970b623293d1fa78a602396ba2e60570d9f62fd2669200c` |
| `components--surface-card--disabled--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见 | `ac7ae33a835b6de04820ee3424d4a0b3a18b273d25da71390368aa4c3fe39849` |
| `components--surface-card--hover--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见 | `0015cb721aad1d66d06b48185a24ea331401e92df1804c573b843f0ea1178830` |
| `components--surface-card--hover--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见 | `be6d587c1a2ba68e7d46e2d42e83fd953e37e527f9ba28f0762d4b8c5133f8c5` |
| `components--surface-card--selected--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见 | `4efa48c6452907a3a924900bdf81891da0c67e5f664a082ec071923d74d3bf36` |
| `components--surface-card--selected--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见 | `2039281e84b426718778c598d8a4d5dff5dee7a69c10e4fd78acdde9783051a7` |
| `components--tab-strip--hover--full--dark.png` | PASS | 实际Tab选中/未选中/hover可见 | `623b8ea1a98828ec37d781355254ebfab850ed923783c579a40fc573739d3665` |
| `components--tab-strip--hover--full--light.png` | PASS | 实际Tab选中/未选中/hover可见 | `658d18952dcbbea6904f41678644cd738d7419745ac8c2f658f6c5fb5a8ae21d` |
| `components--tab-strip--selected--full--dark.png` | PASS | 实际Tab选中/未选中/hover可见 | `19f32c0ca252617b9f73971d3069ae7cd22b59551ca65aa7c34275d8552ad84e` |
| `components--tab-strip--selected--full--light.png` | PASS | 实际Tab选中/未选中/hover可见 | `1490841169568214e09db6778d3e2a35c1fdf2534223768d444b661281637f7a` |
| `components--tab-strip--unselected--full--dark.png` | PASS | 实际Tab选中/未选中/hover可见 | `f297bca8d40097d2d4745750baa7bf59fc59bccadbcf2185547838fca6b9febd` |
| `components--tab-strip--unselected--full--light.png` | PASS | 实际Tab选中/未选中/hover可见 | `f5925ef1b3727fb1b3e2c452630c8e19535d8c2845b02002163e42b9377f5820` |
| `components--toggle-switch--disabled--full--dark.png` | PASS | 开/关/禁用切换控件可见 | `7e34408cb5a2f821aace06faa7c44062dd6117b00dbf9159072d221f986f9f7b` |
| `components--toggle-switch--disabled--full--light.png` | PASS | 开/关/禁用切换控件可见 | `d68de31cc8842ba81d9e7fad06218af91878e9d85b79de09636acd9d4847dd68` |
| `components--toggle-switch--off--full--dark.png` | PASS | 开/关/禁用切换控件可见 | `0c2923ce72c87666b9118d66bf5055fd07a2ef9fd691f0e2df2967230651c721` |
| `components--toggle-switch--off--full--light.png` | PASS | 开/关/禁用切换控件可见 | `5c480ea9f571df916d0bdac7f24fee7d0f3ab57dbf50c872e77bea2d34938177` |
| `components--toggle-switch--on--full--dark.png` | PASS | 开/关/禁用切换控件可见 | `3f7443f2bd2d5bc4b56026a0e7de252ae45bf3510b2b8b58c0290ca63f56fe85` |
| `components--toggle-switch--on--full--light.png` | PASS | 开/关/禁用切换控件可见 | `e170cbc574001e2be3156434f5260f3858522dc03cdeb2983cadea70be186668` |
| `components--tooltip--opened--full--dark.png` | PASS | 实际提示文本弹出可见 | `0e289319b382638cb22078db49434dab763d5c8ef05b8220d4c34affc4bd262b` |
| `components--tooltip--opened--full--light.png` | PASS | 实际提示文本弹出可见 | `ef8d97e3980922b0e47039f8af4037011ff2afcdaeb9851165028bb2e22ef5cd` |
| `decor--page-turn-particles--mid--full--dark.png` | PASS | full稀疏前景金色粒子可见且不遮内容 | `14c1dcc32f450c4ba1846d05783736fe7dc9cae91f2e03b96cb205b404040a86` |
| `decor--page-turn-particles--mid--full--light.png` | PASS | full稀疏前景金色粒子可见且不遮内容 | `0864dfc650398625f8769ea671149575682407407fa3e866100fd9e6becf9cdc` |
| `decor--page-turn-particles--none--reduce--dark.png` | PASS | 真实reduce对照，无粒子层 | `bab63c8cc33bd41a4928e72d14416f50017f9d038f5bd3923054957a17ad4dfe` |
| `decor--page-turn-particles--none--reduce--light.png` | PASS | 真实reduce对照，无粒子层 | `8c9eab59f3ac10634cbe1ea4e5f90421ea994d3da420dd6b42dcd2cf81a76fe2` |
| `decor--shelf-gradient--first--full--dark.png` | PASS | 真实dark渐变序列可辨，相位与裁切元数据相符 | `020dcad839edbbaf4436759d324be37a9f6e3231e3a483617fa5ecc6acb97e9d` |
| `decor--shelf-gradient--first--full--light.png` | REJECT | R2R3-002：first→mid最大RGB差2；真实但循环不可辨 | `cbd2002b9a9d35685d0e65be3f785cfd4b73df73c95d1f0a53943823ef916b04` |
| `decor--shelf-gradient--mid--full--dark.png` | PASS | 真实dark渐变序列可辨，相位与裁切元数据相符 | `dd83438a906d69d37ca6b6604edeb332851bc9bf28ba99ab056278fa09ee0608` |
| `decor--shelf-gradient--mid--full--light.png` | REJECT | R2R3-002：first→mid最大RGB差2；真实但循环不可辨 | `47a27ce65e02c437c58bf96337b15c0d50ee8aef6ccdb98a1f3006a0fbb9efd8` |
| `decor--shelf-gradient--static--reduce--dark.png` | PASS | 真实dark渐变序列可辨，相位与裁切元数据相符 | `b28c71ef98e10e9acd4d9fb20eb88faabd538455b90e91dbb5d02d00d48099ce` |
| `decor--shelf-gradient--static--reduce--light.png` | PASS | 真实light reduce静态对照；不代表循环可辨 | `802d443320310f55eb8bd7cad0164b2a11edffa58f3c1a055ae0a58ea4e7cf85` |
| `pages--reader--default--full--dark.png` | PASS | 真实双主题页面，非文本背景有差异；页图与页码/进度可见 | `45ee45c0a7a58f034e8fbd8a5336feac3bb06b1df1c7e23ffa0e158bac6cc7bd` |
| `pages--reader--default--full--light.png` | PASS | 真实双主题页面，非文本背景有差异；页图与页码/进度可见 | `75d9fb3ebee3fff8b5b7a05210271dd8706b818fac59976457f6d9b9e6d494a7` |
| `pages--settings--default--full--dark.png` | PASS | 真实双主题页面，非文本背景有差异 | `1d6c9ac14cfc37923a2999c8ea9b3248dd13813ce41d575f3439f56e7c08df2b` |
| `pages--settings--default--full--light.png` | PASS | 真实双主题页面，非文本背景有差异 | `2baf4e65dcb70bc36751c4f9d3757e4374d12413b4215488c2d29a37ff565402` |
| `pages--shelf--default--full--dark.png` | PASS | 真实双主题页面，非文本背景有差异 | `b61390e148a05d50e574c0174022ab493609436a32d7f6fafd03496f02a8fa19` |
| `pages--shelf--default--full--light.png` | PASS | 真实双主题页面，非文本背景有差异 | `70f3633d1c88d3708f0452cc2692cdc4b2bd4b3557ab928d0916eac032065df1` |
| `pages--workbench--default--full--dark.png` | PASS | 真实双主题页面，非文本背景有差异 | `d035f48dc31f550f23f37e702d5df838b860b6de6c822ea5331ef97d25f18862` |
| `pages--workbench--default--full--light.png` | PASS | 真实双主题页面，非文本背景有差异 | `4ed18c299cd6bec1e994542288abc0c1b819f2a91c2b66c36c15090a52c5c2e4` |
| `shell--top-nav-status--compact--full--dark.png` | REJECT | R2R3-001：实际Medium，Nav仍展开，不能签作所标紧凑/折叠格 | `8992866848b4e6885b0e8305e1d6bacd9b3ab5221c5683c9fa4b81aff12ee0f9` |
| `shell--top-nav-status--compact--full--light.png` | REJECT | R2R3-001：实际Medium，Nav仍展开，不能签作所标紧凑/折叠格 | `fd72cd595af889868e52bfa06b33e1851e5b9fe930244515cece16444988d0c9` |
| `shell--top-nav-status--default--full--dark.png` | PASS | 默认真实Top/Nav/Status；仅签此默认状态 | `3ae8b01c0ebaa6bf96ca7ed9e85b885209f049854e0b14e07282207849163c07` |
| `shell--top-nav-status--default--full--light.png` | PASS | 默认真实Top/Nav/Status；仅签此默认状态 | `ab66fb2897e977bb0c91063cc048b6ed350581b00c7995875db6ec7e42efb0b3` |

签署合计：158 PASS / 6 REJECT / 0 NOT_RUN；164/164有签署。缺失NavRail折叠、StatusBand错误/运行中仍NOT_RUN（无文件不混入164图统计）。

## 附录 B：本次无过滤全量与57条skip

逐程序集由本次TRX实读；skip不算passed。相对用户1281/0/57基线差值=0/0/0；相对上一轮1274/0/57为+7/0/0，总数1338。

| 程序集 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Appearance.Tests.dll | 21 | 0 | 0 | 21 |
| NewManga.Presentation.Avalonia.Tests.dll | 38 | 0 | 0 | 38 |
| NewManga.Host.Tests.dll | 51 | 0 | 28 | 79 |
| NewManga.ApplicationCore.Tests.dll | 31 | 0 | 0 | 31 |
| NewManga.CoreClient.Tests.dll | 128 | 0 | 22 | 150 |
| NewManga.ThemeEngine.Tests.dll | 253 | 0 | 0 | 253 |
| NewManga.DesignSystem.Tests.dll | 114 | 0 | 0 | 114 |
| NewManga.App.Tests.dll | 645 | 0 | 7 | 652 |
| 合计 | 1281 | 0 | 57 | 1338 |

57项的实际原因相同：`needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)`；以下逐条列出，均NOT_RUN而非PASS。

| # | 测试 | 实际skip原因 |
|---|---|---|
| 1 | `NewManga.Host.Tests.LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 2 | `NewManga.Host.Tests.ExportE2ETests.Export_Cancel_LeavesNoArtifact` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 3 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 4 | `NewManga.Host.Tests.RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 5 | `NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 6 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 7 | `NewManga.Host.Tests.StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 8 | `NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 9 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 10 | `NewManga.Host.Tests.ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 11 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 12 | `NewManga.Host.Tests.WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 13 | `NewManga.Host.Tests.WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 14 | `NewManga.Host.Tests.StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 15 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 16 | `NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 17 | `NewManga.Host.Tests.CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 18 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 19 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 20 | `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 21 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 22 | `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 23 | `NewManga.Host.Tests.StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 24 | `NewManga.Host.Tests.WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 25 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 26 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 27 | `NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 28 | `NewManga.Host.Tests.ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 29 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 30 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 31 | `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 32 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 33 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 34 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 35 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 36 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 37 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 38 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 39 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 40 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 41 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 42 | `NewManga.CoreClient.Tests.SidecarFailureTests.StartupTimeout_IsTyped_NotAHang` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 43 | `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 44 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 45 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 46 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 47 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 48 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 49 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 50 | `NewManga.CoreClient.Tests.Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 51 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 52 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 53 | `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 54 | `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 55 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 56 | `NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 57 | `NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason` | reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |

## 附录 C：仓外失败复现（未改源码）

目的：补足原测试只分别覆盖失焦/重挂和reduce初始态的盲区。Probe直接引用隔离build的真实App/App.Tests DLL，复用既有私有Create、CreateWithPages与Motion，未替换生产执行器。构建期间无源改动；引用的代码等价implementation_head6b602c3fe。下面保存完整实际Probe源，便于不依赖仓外文件恢复。

```csharp
using System.Reflection;
using Avalonia.Headless;
using System.Runtime.CompilerServices;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Tests;
using NewManga.App.Views.Fluent;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using Xunit;
[assembly: AvaloniaTestApplication(typeof(TestAppBuilder))]
public class LifecycleProbe {
 static readonly BindingFlags All=BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static;
 static object? Get(object o,string n)=>o.GetType().GetProperty(n,All)!.GetValue(o);
 static void Motion(FluentShellSurface s, MotionMode m=MotionMode.Full)=>typeof(FluentResidual2DecorativeTests).GetMethod("Motion",All)!.Invoke(null,new object[]{s,m,MotionCategories.Decorative});
 static (Window,FluentShellSurface,object) Create(string n){var t=(ITuple)typeof(FluentResidual2DecorativeTests).GetMethod(n,All)!.Invoke(null,null)!;return ((Window)t[0]!, (FluentShellSurface)t[1]!,t[2]!);}
static void Advance(object c,double ms)=>c.GetType().GetMethod("Advance",All)!.Invoke(c,new object[]{ms});
 static void Deactivate(Window w)=>typeof(WindowBase).GetMethod("HandleDeactivated",All)!.Invoke(w,null);
 [AvaloniaFact] public void InactiveReattachMustNotRestart(){var(w,s,c)=Create("Create");try {Motion(s);var loop=Get(Get(s,"ShelfView")!,"DecorativeLoop")!; Deactivate(w);Assert.False((bool)Get(loop,"IsRunning")!);s.Navigate(FluentPage.Workbench);Dispatcher.UIThread.RunJobs();s.Navigate(FluentPage.Library);Dispatcher.UIThread.RunJobs();Assert.False((bool)Get(loop,"IsRunning")!);} finally{w.Close();}}
 [AvaloniaFact] public async Task ReduceMustCancelPausedParticles(){var(w,s,c)=Create("CreateWithPages");try {Motion(s);s.Navigate(FluentPage.Reader);Dispatcher.UIThread.RunJobs();var reader=Get(s,"ReaderView")!;await (Task)reader.GetType().GetMethod("LoadAsync",All)!.Invoke(reader,new object[]{"book-1","chapter-key",CancellationToken.None})!;var vm=Get(s,"ReaderViewModel")!;await (Task)vm.GetType().GetMethod("NavigateAsync",All)!.Invoke(vm,new object[]{1,CancellationToken.None})!;Dispatcher.UIThread.RunJobs();Advance(c,100);Assert.NotNull(Get(reader,"DecorativeParticleLayer"));Deactivate(w);Advance(c,0);Motion(s,MotionMode.Reduce);w.Activate();Dispatcher.UIThread.RunJobs();Advance(c,100);Assert.Equal(0,(int)Get(c,"PendingFrames")!);Assert.Null(Get(reader,"DecorativeParticleLayer"));}finally{w.Close();}}
}



```

Probe为net9.0测试项目，引用Microsoft.NET.Test.Sdk17.12.0、xunit2.9.2、runner.visualstudio2.8.2、Avalonia.Headless.XUnit11.3.22，以及真实App.Tests输出目录的DLL；将该输出`runtimes/win-x64/native/*.dll`复制到Probe输出解决Skia原生加载，属于测试装配，不改产品。首次装配缺using/内部ManualClock类型，随后改用ITuple/object反射；首次运行缺原生DLL，补齐后才得到以下产品断言失败。均未把装配错误当作产品finding。

最终实跑命令：`dotnet test <workspace>/impl-r3-review/probe/Probe.csproj --nologo --logger trx --results-directory <workspace>/impl-r3-review/probe/results`，pwsh7.6.8，EXIT=1：

```text
LifecycleProbe.InactiveReattachMustNotRestart [FAIL]
Assert.False() Failure
Expected: False
Actual:   True
LifecycleProbe.ReduceMustCancelPausedParticles [FAIL]
Assert.Equal() Failure: Values differ
Expected: 0
Actual:   1
失败: 2，通过: 0，已跳过: 0，总计: 2
```

第二场景在此前同序列的断言版本也确认旧DecorativeParticleLayer仍为Border而非null；最终版本推进100ms读取PendingFrames=1，证明reduce后并非只剩无帧静态对象。两次均从CreateWithPages新建独立Window开始。未实跑“失焦期间异步新翻页完成”第三序列，不把它标作已复现。
