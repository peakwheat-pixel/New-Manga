---
task_id: FEA-06-RESIDUAL-2
author: Codex CLI fresh implementation session /root
recipient: DeepSeek Harness
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
start_commit: 9c6a2b474abeb39be8f7c362cd2b11597e53b9d4
delivery_head: 17a26d552e27a57bafebe0bc77d008094d1a6775
evidence_head: c70d5c348172920847da6e1ab0d08ed9f219a80e
status: delivered_for_independent_review
---

# Handoff：FEA-06-RESIDUAL-2 R2R3 返修

R2R3-001…005 的实现、回归与真实像素证据已交付；006由DSH先行修复。本会话未签发独立Review，Task仍为in_progress，AC-1/3仍PARTIAL，等待独立签署及DSH集成。未push。

## 固定提交与写域

- `17a26d552`：`fix(fea-06-residual-2): R2R3 repair visual states and decorative lifecycle`。Fluent Views、Controls.Fluent样式、App.Tests及本卡恢复点。
- `c70d5c348`：`fix(fea-06-residual-2): R2R3 record 172 real captures and verification`。本卡visuals、最终日志、逐finding处置、像素/TRX审计及期望令牌说明。
- 本Handoff为之后的文档提交，引用以上固定实现/证据head；其后没有生产代码变化。
- 未改Core/Host/IPC/schema/依赖、冻结设计/生成物、CurrentV2/组合根、FrontendSelector、FEA-07 seam、旧verification/FEA-06、Task/STATUS/PLAN。没有写真实用户数据或真实APPDATA。无新增产品依赖/字体/颜色/资产。

## 逐项结果

| Finding | 结果（实现者口径） | 交付证据 |
|---|---|---|
| R2R3-001 | FIXED；签署NOT_RUN | 顶部按钮折叠/恢复NavRail，跨页保持；1024/1280/1600分别Medium/Compact/Full；StatusBand由真实页State投影错误/运行中，双主题6张状态图，不用默认帧替代。保存帧来自未完成Host await，错误来自真实页图读取异常。 |
| R2R3-002 | FIXED；签署NOT_RUN | 仅Bg.Overlay→Bg.Sunken，Opacity0–1，8s循环；纯背景light first→mid最大差15、25114像素差>8；first→reduce最大17、31699像素差>8。实施者原图目视可辨，不作独立签署。 |
| R2R3-003 | FIXED；签署NOT_RUN | pressed实际模板Background=Status.Failed，文字=Bg.App；实际模板/文字令牌与≥4.5:1断言；原图light=5.9467:1，dark=7.4751:1。 |
| R2R3-004 | FIXED | attach读取实际Window.IsActive，解绑不清失焦；失焦→导航→返回书架仍暂停、粒子失焦返回后新翻页仍暂停，ManualClock两条新回归通过。 |
| R2R3-005 | FIXED | Reader策略归零同步Cancel并移层，解绑Window事件；播放/暂停×reduce/auto系统关/category-off六格通过，PendingFrames排空后为0、layer=null、Activate不复活。已请求的平台单帧无法物理撤回，generation取消使其无操作且不再排队。 |
| R2R3-006 | FIXED by DSH | `8203b3d28`修复STATUS/PLAN；本轮只核验，未改治理指针。 |

逐项实现/测试锚点与仍未完成项见 [r2r3-findings-disposition](../../verification/FEA-06-RESIDUAL-2/r2r3-findings-disposition.md)。原impl-r3报告、R2R2处置和历史日志保留原字节。

## 验证（executed）

环境：Windows10.0.26300、pwsh7.6.8（`C:/Program Files/PowerShell/7/pwsh.exe`）、dotnet SDK10.0.401/net9.0、Avalonia11.3.22/headless Skia 96DPI。源码/捕获head均为17a26d552。

| AC/场景 | 实际命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | PASS，0 warnings/0 errors，EXIT=0 | impl-r3-rework-verification.log |
| 无过滤全量 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo --logger trx --results-directory <workspace>/r2r3-final/results-normal` | **1289 passed / 0 failed / 57 skipped**，总1346，较基线+8/0/0，EXIT=0 | 同日志；r2r3-evidence-audit.md逐程序集及57条实际skip原因 |
| 默认零仓库写入 | clean source head上build/full前后`git status --porcelain` | PASS，前后均空 | 同日志normal段 |
| opt-in，仅本卡visuals | `$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS='1'; dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --filter FullyQualifiedName~FluentResidual2VisualEvidenceTests --nologo --logger trx --results-directory <workspace>/r2r3-final/results-capture` | PASS，1/0/0，status仅visuals；此filter仅捕获，不冒充全量 | 同日志capture段；visuals/visual-inventory.md |
| IN-1/IN-2A/IN-2B自动化 | 生产clock采样、ManualClock组合、实际模板/令牌、像素/布局断言均包含在无过滤全量 | PASS（自动化）；AC-1/3签署仍NOT_RUN | 测试源码、audit.md、disposition |
| TokenGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | PASS，292 rows，EXIT=0 | 同日志checks段 |
| ThemeGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | PASS，EXIT=0 | 同日志checks段 |
| 治理/pins | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PASS（3既有warnings）；pins15/15，EXIT=0 | 同日志checks及最终文档检查段 |
| 旧四PNG/写域 | 旧四SHA、禁止路径零diff、生产源码与17a26d552零diff | PASS | 同日志四个完整SHA；本轮git diff路径 |
| 原生DPI/a11y/触控 | 未执行 | NOT_RUN | B-5/D-1保持，不能以headless替代 |

57项skip均缺sidecar fixture，原样逐条登记，未删测试、未降skip计数。App=653/0/7，DesignSystem=114/0/0，其余程序集计数不变。原始TRX与运行日志保留在 `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-06-RESIDUAL-2/r2r3-final/`；关键数据已入库，不依赖仓外路径作为唯一证据。

## 图数与签署

当前172图=pages8/components142/decor10/shell12；172行、172唯一SHA，全部capture head=17a26d552。相对原164：136同名同字节、24同名改字节、移除4个旧shell标签名、增加12个真实shell状态/宽度名，净增8。

原impl-r3 **158 PASS/6 REJECT**只绑定原SHA并保留；本轮**新增独立签署=0**，inventory全NOT_RUN。136旧PASS同字节可由审计表定位，24更新/12新增须新审；不把捕获成功或唯一SHA当视觉PASS。完整old/new SHA、背景差分、pressed像素对比度和八条新增回归结果见 [r2r3-evidence-audit](../../verification/FEA-06-RESIDUAL-2/r2r3-evidence-audit.md)。

## 接收与推荐下一步

- Task：FEA-06-RESIDUAL-2 impl-r4独立复核；启动条件=DSH接收本返修并Appointment；依赖scope-v3及impl-r3 findings。
- Agent：DSH负责Appointment/处置/集成；推荐fresh Codex或ZCode独立上下文Reviewer，不能使用本实现会话。
- Recovery point：`G:/CODEX/New Manga`，main，同工作区/common directory `.git`；base=669a4ae02，start=9c6a2b474，源码17a26d552、证据c70d5c348；本Handoff之后无生产改动。若需独立worktree，待DSH创建，不创建/删除既有worktree。
- Reviewer允许写域：DSH另行Appointment的 `doc/reviews/FEA-06-RESIDUAL-2-impl-r4.md`；产品源码、冻结设计、契约/schema、证据原图/既有签署均只读。不由Reviewer返修，不push。
- 交付物：独立Review报告、172图逐图签署/准确SHA、R2R3-001…006逐条复核与实际门禁记录，未跑项继续NOT_RUN。批准不等于自动关闭，DSH另行集成验证/生命周期处置。
- Verification：重跑本表build、无过滤≥1289/0/57、生产clock/八条组合回归、真实shell缺格/宽度与渐变/pressed像素、生成器/check/pins/旧SHA/写域；如独立重捕获，在DSH分配的副本操作，原仓证据只读。记录所有skip及限制。

可直接转发给DSH：

> 请在G:/CODEX/New Manga的main接收FEA-06-RESIDUAL-2 R2R3返修：base669a4ae02，start9c6a2b474，源码/捕获17a26d552，证据c70d5c348及其后Handoff文档提交。全量1289/0/57，172图；R2R3-001…005实现/回归已交付，006由你在8203b3d28修复。本会话未独立签署。请固定实际接收head并Appointment fresh Codex或ZCode上下文独立impl-r4 Reviewer，只读产品和证据，只写你授权的新Review；不得使用本实现会话自审。完整阅读impl-r3报告、本Handoff、r2r3-findings-disposition、audit与最终日志，逐图复核172 PNG（原158 PASS/6 REJECT只绑定旧SHA），重点NavRail折叠/StatusBand真实错误运行、1024/1280/1600断点、light背景差>8、Danger≥4.5:1、失焦导航与六种粒子降级组合；实跑build、无过滤≥1289/0/57、生成器/check/pins/旧四SHA/禁止写域。只交独立报告与逐图签署，不返修、不push；原生DPI/a11y、域外死代码和D-14保持NOT_RUN。Review后由你处置并集成验证、更新其写域内指针/生命周期，当前Task不自动关闭。

## 遗留与资源

原生DPI/a11y/完整Tab矩阵、域外旧粒子工厂死代码、D-14后续卡、既有OUT/BLOCKED均未认领。新shell的Medium图只签真实断点与导航/状态格，不扩为整页原生布局验收。用户源文件、人工修改、Lock/current/pinned Revision未涉及。

没有移除worktree、执行prune/GC、清理历史资源或更改当前权威指针。DSH保留最终集成、Task生命周期和push权限。本返修可按上述固定提交评估回退；不得覆盖他人未提交内容或改写main历史。
