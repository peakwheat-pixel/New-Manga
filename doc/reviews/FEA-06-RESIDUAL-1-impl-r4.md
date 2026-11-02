---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh session，独立上下文 Reviewer）
reviewer_kind: agent
author: Codex CLI R3-001 实现会话（原 Task 含 ZCode / DSH 实现）
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
implementation_head: 3c3afe17007ee785f018c3bf78c7018caa1c65d5
workspace_head: 55fd2b3b7631d730c0a600524744f6d4f261d9b3
decision: approved
verdict: approved
p0: 0
p1: 0
p2: 1
provenance:
  agent: Codex CLI
  session_id: 01a19d7c-b58c-71d3-b2fa-389dc08fad8a
  appointment: 用户 impl-r4 fresh-session Prompt；Task reviewer 与 rolling checkpoint 第117节（job pwsh-61019e8683e3416a）
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-1 impl-r4

**approved：P0=0 / P1=0 / P2=1。** R3-001 的实际输入反例已修复：原附录 A 原样复跑，full/reduce 同坐标连续点击均可双向切换；新增生产时钟探针在 full/reduce/navigation-off 三态下，经真实 2s 自动隐藏后点击，Down 仅切换一次、Up 不切换且从释放时续 2s，detach 停止计时。未发现本增量新增的产品阻断。R4-001 为当前证据入口仍停在 1233 快照的 P2，交 DSH 处置。

四条验收命令全部 EXIT=0。单次无过滤全量 **1245 passed / 0 failed / 57 skipped，总1302**，较 impl-r3 的 1233/0/57 增12，较本轮验收基线1245/0/57无变化。测试数不代表全部 AC 达成；本结论不关闭 Task，不批准 D-8 暂缓，不豁免 I-4/完整Tab遍历 NOT_RUN 或 B-1…B-7。

## 范围与依据

仓库 `G:\CODEX\New Manga`，branch=`main`，Git common directory=`.git`，开始时工作树干净。实际 HEAD 为55fd2b3b7；`git diff --name-only 669a4ae02 HEAD` 仅列 Task 与 rolling checkpoint，且 `git diff --exit-code 669a4ae02 -- apps verification doc/design` EXIT=0。因此固定 reviewed_head 为上述669a4ae02；55fd2b3b7只提供最新 Appointment，不扩大被审生产/测试字节。

已读 AD-002 当前架构、STATUS/PLAN 当前段、Task 范围v3/AC/禁止范围/Canonical Evidence/待裁决项、rolling checkpoint 第115–117节、REVIEW 模板与协作协议§4/§5.1；按指定顺序读取 impl-r3 原文及附录、impl-r3-rework Handoff、完整实跑日志、冻结设计07 Reader与02 motion。定位并读取 R2-005 原finding及当前四表；没有默认扫描历史文档目录。

重点审阅 `git diff 13a67e75f 669a4ae02`，其中生产增量仅 ReaderPageView.cs（12增2删），测试仅 FluentR2ReworkTests.cs（233增0删）；其余是 R3报告/Task/checkpoint/Handoff/新日志。另核对 Task base→head 的69条路径、禁止范围、R2受影响调用链及旧测试。R2其余实现与测试未在本轮返修改写；复核依据为当前源码、原finding、当前全量实跑与本轮独立探针，不以交付者自述替代。

采用项目 REVIEW 模板的 Architecture/Verification 两面，Standards/Spec作为补充视角。模板已取消 code-review 双子代理强制项，本轮无子代理。当前会话没有参与实现或返修。唯一仓库交付是本文件；未改源码、Task、旧Review、verification或pins，未commit/push。构建生成常规ignored产物；重复运行日志与探针脚本放在既有 workspace 的 `agent-output/codex/FEA-06-RESIDUAL-1/impl-r4/`，关键输出与完整新增探针一并嵌入下文，接收不依赖仓外材料。

## Architecture（executed）

Reader取消 PageSurface 上第二个 press 处理入口，改为 Reader 单个 tunnel handler先判原始Source是否属于PageSurface/图像后代，再按中部坐标调用Toggle，最后 `NotifyInteraction(reveal: !centerTap)`。切换发生在任何本处理器唤醒之前；中部不会先Poke再Toggle；覆盖控件保留普通唤醒，release仅续时。未设置额外Handled、不新增异步任务、计时器、静态持有链或后台UI写入。Source遍历与VM/控件更新处于Avalonia输入UI线程。

计时仍复用既有 DispatcherTimer + 单调时钟deadline；隐藏会Stop并清deadline，detach同样Stop/清空。动画继续使用有限帧与generation取消：旧completion不能覆盖新开状态，detach收敛。Appearance后台Changed仍在Post执行时复查订阅、attach generation与挂载状态；MotionScope继承配置覆盖动态子控件，反馈状态使用ConditionalWeakTable。上述R2路径字节未改，全量相关测试通过。

没有新增依赖、许可材料、Host/IPC/Schema、持久化或源文件操作；没有修改Current V2、FEA-07稳定窗口接线或组合根。FocusRing仍由Fluent绑定offset=1，Current默认0。禁止路径检查及两生成器检查通过。

**Architecture结论：** 记录范围内未发现新增分层、契约、线程或生命周期阻断。headless与Add-Type探针不替代原生触摸硬件、长期内存profiler或DPI/a11y验收。

## Standards（executed）

生产改动限于本次冻结的Reader输入语义，未扩展产品范围。新测试块移除后可逐字还原13a67e75f的原测试文件（仅归一LF），原断言未改弱；新增两组theory共12例。基线禁止路径、依赖/入口及旧证据均保全。

增量 `git diff --check 13a67e75f 669a4ae02` EXIT=2，唯一输出是已冻结 impl-r3.md:369 EOF多空行，保留原字节，不作为新产品finding。未另列工具已强制项或无实际影响的smell建议。

## Spec（executed）

Task I-10要求“顶部/底部条 = 无操作2s淡出、点击中部切换显隐、reduce直接切换”；设计07:23及R3-001进一步明确事件前状态与release语义。三态真实输入、deadline边界、计时器与detach核验通过；其他控件press/wheel/被shell消费Ctrl+K的唤醒测试亦通过。AC5要求日志/矩阵与当前回归事实可复算；当前四表的最新入口未随1245更新，见R4-001。

### R3-001 与新增测试判别力

| 核验 | 本轮观察 | 结论 |
|---|---|---|
| 原附录A原样复跑 | Full/Reduce各三次、每次onPage=True：True→False、False→True、True→False，Up均保持Down结果；中途无MouseMove/Poke | 原始反向反例FIXED；mode开头Poke仅复位原探针初态，不作为自动隐藏后唤回的证据 |
| 自动隐藏后的双向点击 | 本轮附录B新探针每态新建窗口；只在开始MouseMove一次，真实Dispatcher MainLoop等2350ms；工具条已自动隐藏，再固定坐标连续三次Down/Up | Full、Reduce、Full+Feedback-only（navigation-off）均False→True→False→True，每次实际命中页面中部；无测试前Poke/NotifyInteraction |
| press一次、release零次 | 观察AreToolBarsVisible的PropertyChanged次数；每次Down增1，Up后仍只增1 | 不是只检查最终bool，能识别一次事件内先唤醒再隐藏的双变化 |
| release续2s | Down后约400ms才Up；deadline延长约406–417ms；press+约2.15s仍显示，release+约2.25s自动隐藏 | 生产计时器/MainLoop实跑，不直接调用CheckIdleDeadline；精确1999/2000ms由新可控时钟测试补齐 |
| 降级与detach | reduce/navigation-off在Down后、未推进帧即IsVisible=false/Opacity=0；detach清deadline、停timer，真实再等2150ms仍保持显示 | PASS；精确手动时钟detach后+3000ms亦通过 |
| 其他控件/滚轮/handled键 | R3001第二组3态×3输入，从idle隐藏状态开始；恢复侧栏按钮press唤醒、release仍完成Click，wheel唤醒，Ctrl+K实际打开命令面板并续时 | 9例在本轮全量内通过；原R2003五例同时保留通过 |
| 新测试是否会掩盖反例 | 第一组先CheckIdleDeadline自动隐藏，再Down断言true，且计数只增1；每次AssertPageHit仅UpdateLayout/Pump(20)，不MouseMove、不Poke，也不推进手动clock。原生产会在首Down仍false并发生两次变化 | 新增用例对旧事件顺序有判别力；后续同坐标click2/3覆盖双向，非只测初次隐藏 |

交付日志中的“旧生产3失败、修复后3通过”是已读取的历史记录，本轮未重构建旧head或修改源码做mutation；不将其写成本轮执行。判别力结论来自所读断言、旧源码的事件次序和本轮独立真实输入结果。

### R2-001…006 反例回归

| 原finding | 当前核验 | 结论/限制 |
|---|---|---|
| R2-001 | R2001 Reader两条80/159/160ms与wake取消；Settings离开/普通确认、Shelf对话框/抽屉四路100/199/200ms进入、80/159/160ms退出及scrim160ms；reduce/navigation-off即时；冻结hover曲线 | 全量通过，旧测试字节保留；Reader淡出160ms，浮层进入200ms，未以Transitions存在替代中间值 |
| R2-002 | R2002 Providers/Backup重建、分类切换、再次重建后的真实hover/press与颜色/缩放中间值；AnimationCompletion的WorkbenchDraftEdit重建 | 全量通过，继承MotionScope/pressed兜底未改；I-4其他格仍NOT_RUN |
| R2-003 | 原press/release/wheel/handled键deadline与detach用例；新增三态其他输入9例；新生产计时器中心探针 | 全量及独立探针通过；R3-001修复未牺牲普通输入唤醒或release续时 |
| R2-004 | 后台真实Changed→detach或快速reattach→pump的两分支；订阅0/1及过期generation回调 | 全量通过；未冒充长期原生泄漏profile |
| R2-005 | 旧字节13/13、57 skip逐条原因脚本通过；新日志/Handoff/Task为1245；但四表“当前/最新”仍1233，旧脚本固定8b39b1398 | 当前口径未全对齐，P2 R4-001；机械PASS只证明R2历史快照，不证明本轮最新台账正确 |
| R2-006 | FocusRingOffsetTests标准/高对比stroke实时2→3→2、四边gap=1、外尺寸、滚动gap裁剪/恢复；R2006 Fluent继承1/Current0 | 全量通过，offset实现未改；原生200%DPI/完整Tab遍历仍NOT_RUN |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R4-001 | P2 | verification/FEA-06-RESIDUAL-1/ac-coverage.md:28、38；item-status.md:39；component-state-matrix.md:47；batch-b-verification.log:138；verify-r2-evidence.py:9、44 | 本次实现/测试已到3c3afe170、1245/0/57，但四份入口仍写“本节取代前文当前/最新”“本轮最新1233/0/57”，AC表还停在待impl-r3。消费者按现有当前快照或只跑旧脚本，会把旧head/计数当本次覆盖；不影响R3产品修复，但用户本轮要求的台账一致性未达成。 | 本轮全量App626、总1245；新日志/Handoff与Task一致。四表仍固定8b39b1398、App614/总1233；脚本HEAD常量8b39b1398且断言1233，因此PASS仅是旧快照审计。缺少将四表统一降为R2历史、并指向1245新快照的当前入口。 | DSH集成处置时保留旧文件/旧pin原字节，追加统一的本轮证据索引或获授权的追加快照，明确669a4ae02/3c3afe170、1245/0/57（+12）、本轮R3核验及NOT_RUN/D-8；更新Task当前canonical入口。旧脚本保留为历史审计，另核验当前入口，不用全局替换改写旧记录。 | open，待DSH处置；不要求Reviewer改证据或参与实现返修 |

未发现新的P0/P1。R4-001属于AC5与证据维护，不将正确的新日志计数、历史字节保全或Reader行为判为失败；当前 `canonical_evidence_status: pending` 也不因检查器PASS自动变complete。

## Verification（executed）

环境：Windows NT10.0.26300.0，PowerShell Core7.6.8，`C:\Program Files\PowerShell\7\pwsh.exe`，dotnet SDK10.0.401，测试目标net9.0，Avalonia11.3.22。VIRTUAL_ENV、NEWMANGA_CORECLIENT_SIDECAR_DIR、NEWMANGA_CAPTURE_FLUENT_PNGS、NEWMANGA_EVIDENCE_SYNC均未设置。探针运行在PowerShell .NET10宿主，Add-Type内存编译；VSTest是net9.0，二者分开记录。AppearanceStore使用不存在的隔离临时路径且不Save；无真实APPDATA/源文件写入。

| 场景 | 实际命令/步骤 | 结果与EXIT | 判别力证据/限制 |
|---|---|---|---|
| 构建 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | PASS，BUILD_EXIT=0 | 0 warnings / 0 errors，附录C原始输出 |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | PASS，TEST_EXIT=0 | 8程序集1245/0/57，总1302；附录C原始输出与逐条skip原因；不叠加探针或历史计数 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | PASS，CHECK_EXIT=0 | 3既有warnings：9非终态Task、STATUS/PLAN预算80% |
| 冻结pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | PASS，PINS_EXIT=0 | 15/15；不替代语义复核 |
| 两生成器 | TokenGen/ThemeGen DLL各`--check`，完整命令见附录C | PASS，各EXIT=0 | byte-for-byte up-to-date |
| 原始反例 | R3附录A原样执行 | PASS，ORIGINAL_PROBE_EXIT=0 | 附录A输出，两态双向真实Down/Up |
| 生产时钟三态 | 附录B完整探针 | PASS，LIVE_PROCESS_EXIT=0 | 自动隐藏、三次切换、property change计数、release deadline及detach；未用Poke/NotifyInteraction/手动CheckIdleDeadline |
| R2与新增测试 | 当前全量内的R2001/2/3/4/6、FocusRingOffset、AnimationCompletion、Current比较 | PASS | 具体断言见前表，原R2测试文件除新增块外逐字保留 |
| 旧证据 | `python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py` | PASS（历史），HISTORICAL_EVIDENCE_EXIT=0 | raw13/13、57逐条原因；不能推出当前四表已到1245，R4-001 |
| 历史保全 | `git diff --exit-code 227eab304 669a4ae02 -- verification doc/reviews doc/design ':!verification/FEA-06-RESIDUAL-1/impl-r3-rework-verification.log'` | PASS，OLD_EVIDENCE_DIFF_EXIT=0 | 唯一新verification为R3日志，其他既有verification/Review/设计零diff |
| 旧PNG | `git diff --exit-code 82529a3d5864a39f362e414b67bca774d743f862 HEAD -- verification/FEA-06/screens` | PASS，PNG_EXIT=0 | 四图SHA在附录C；默认测试未覆盖旧PNG |
| 写域/禁止路径 | Task base→head 69路径审计；Core/Host/CoreClient/Presentation、Current、Shell、冻结设计/生成物/依赖/入口等diff检查 | PASS，PROHIBITED_PATHS_EXIT=0，FORBIDDEN_PATH_AUDIT_EXIT=0 | 入口通配`*lock*`仅额外命中测试ManualFluentMotionClock.cs，并非依赖锁文件；逐路径核实无越界 |
| 测试保留 | 对比13a67e75f/669a4ae02 FluentR2ReworkTests源码；移除新增块复原原文件 | PASS，R2_TEST_CONTENT_RETENTION_EXIT=0 | 233行只增，9个public void/Task方法保留（含helper Advance，不冒充9个独立测试）；增加2组theory共12例 |
| 增量空白 | `git diff --check 13a67e75f 669a4ae02` | EXIT=2（历史文档） | 仅impl-r3.md:369 EOF空行，保留字节，不新增finding |
| 当前台账一致性 | 四表最新段对照Task/Handoff/本轮全量 | FAIL（P2） | R4-001；无缺失产品关键输入证据 |
| 原生验收 | 200%DPI、触摸硬件、原生a11y、逐像素视觉/完整Tab遍历、PNG opt-in | NOT_RUN / BLOCKED | B-5/D-1与既有I-4缺口保持，不混入57个xUnit skip |

**Verification结论：** R3-001关键行为证据齐备，四命令及全量通过，R2产品反例未回退；当前证据入口有一项P2。不能从1245通过推导AC1–AC5全部MET。AC1仍有B-1/2/3/6/7，AC2仍有I-4/完整Tab/D-8/B-5，AC3仍有B-4；AC4本轮PNG opt-in与原生视觉未重跑；AC5当前索引/DSH集成/closeout待完成。

## 结论与复审

固定669a4ae02可交DSH进行Review处置与集成验证；没有P0/P1要求重新修改Reader产品代码。R4-001、D-8、原生验收及其他已登记限制均由DSH处置，批准本轮返修不等于批准Task done/关闭或后续节点释放。如生产/测试head变化，需按新head重新Appointment；本会话不得参与后续finding实现返修。

推荐下一切片：Task=`FEA-06-RESIDUAL-1` Review处置/集成验证，Agent=DSH；启动条件=接收本报告。Recovery point=`G:\CODEX\New Manga`、main、同一worktree，base=82529a3d5864a39f362e414b67bca774d743f862，reviewed_head=669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431，当前文档head=55fd2b3b7631d730c0a600524744f6d4f261d9b3。下一任务建议不释放新节点。

可直接转发给DSH：

> 在 G:\CODEX\New Manga 的 main 接收 doc/reviews/FEA-06-RESIDUAL-1-impl-r4.md：approved，P0=0/P1=0/P2=1。Task=FEA-06-RESIDUAL-1，base=82529a3d5864a39f362e414b67bca774d743f862，reviewed_head=669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431（生产3c3afe170），当前文档head=55fd2b3b7631d730c0a600524744f6d4f261d9b3；先核对HEAD/dirty。请处置R4-001，保留旧证据/pin字节，冻结并登记当前证据索引的追加路径，将1245/0/57（较1233+12）与四表R2历史快照明确区分；更新Task当前Canonical Evidence。保持I-4/完整Tab NOT_RUN、D-8待裁决、B-1…B-7及B-5/D-1原生限制，不据测试数写全部AC MET。按当前授权运行集成验证（已有integration-verify.ps1，先核对脚本范围），实跑报告列出的四条命令、两生成器及旧PNG/历史字节对比，记录实际head、shell/EXIT、单次计数和57条skip原因；基线1245/0/57只增不减。允许写Task/STATUS/PLAN/当前证据索引与集成日志等DSH治理域；不改旧Review/旧证据、Core/契约/Schema/依赖/生成物/冻结设计/Current/组合根/FEA-07 seam。交付findings处置、集成验证日志与当前evidence pin、Resource Manifest closeout；按真实AC及已有授权决定终态，不能由本Review直接关闭Task或释放新节点。本Reviewer不执行push，push由DSH按现有授权另行处理。

## 附录A：原R3附录A原样复跑

在仓库根的新PowerShell7进程，提取原报告的完整代码块并执行（未改其mode初始化或输入序列）：

```powershell
$r=Get-Content -Raw doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md
$a=$r.Substring($r.IndexOf('## 附录A：'))
$b=[regex]::Match($a,'(?s)```powershell\r?\n(.*?)\r?\n```').Groups[1].Value
Invoke-Expression $b
```

