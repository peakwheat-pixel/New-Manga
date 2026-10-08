# 桌面新架构与 Windows 分发审计（2026-10-08）

## 口径、权限与恢复点

- **静态审计输入**：`G:/CODEX/New Manga`，`main@e4242ecd419eb0eea098d2f63b40f709aa5caeea`，Git common directory=`G:/CODEX/New Manga/.git`。本报告由 Codex 父任务委派；只新增本文件，不改生产、契约、Task、Plan、STATUS，不构建、不跑全量测试、不启动 GUI。
- 已阅读 `AGENTS.md`、`doc/REBASELINE_PLAN.md` 当前覆盖层与新架构树、`doc/00_INDEX.md`、`doc/STATUS.md` 顶部、`doc/09_COLLABORATION.md`，并追踪实际 `apps/**`、Python 装配、packaging 与相关测试/入库证据。
- 当前授权：`doc/STATUS.md:5` 与 `doc/REBASELINE_PLAN.md:5-13` 明确 **无 Active/released Task**。下述路线全部是候选，不构成释放；Reader/四页全量产品范围尤其不得自行解冻。
- 进入时已有他人内容：`.qoder-credits/report.json` modified；`.qoder-credits/通路探测__8602db50.canvas.tsx`、Runner Guard 的本地 dispatch JSON/stderr untracked。均未改动、未纳入本报告。
- `PASS` 仅引用已入库证据的固定提交；本轮动态执行一律 `NOT_RUN`。当前工作树静态存在性与旧提交验证结果分别陈述。

## 结论

**新架构不是空仓：Tauri host、真实 stdio Core、SQLite/Managed Copy 权威、受控资源协议、书目读取、SFX 设置、工作台页导航与 region 修订/重渲染均已落地。它仍是基础设施与有界产品竖切的组合，不能称完整四页 React 产品完成。** 当前默认生产窗口仍为资源通道控制台，只有 Console/Workbench 两按钮；书目与设置作为控制台 section，独立 React Reader 不存在。

**Windows 分发已有真实 NSIS + 五入口 frozen bundle 与本机安装态验证。** RG1 有用户明确接受“本机视为干净 Windows 基座”的裁决，故该历史 Gate 的 `done/PASS` 有效；技术证据仍仅覆盖相应固定产物、本机 Windows 11 与有界 workflow。不能将它扩写为独立干净 Windows/Win10、当前完整四页生产用户旅程或所有依赖动态闭包已验证。

## 实际启动、命令、资源与事件链

| 链路 | 真实 As-Is 与源码锚点 | 实现边界 |
|---|---|---|
| React 启动 | `apps/desktop/frontend/src/main.tsx` → `App.tsx:21` 获取全局 Tauri invoke；`:74` 默认 `console`；`:478-528` 只切 Console/Workbench并挂载 Library/Settings | 生产分支仍运行 deny/allow matrix（`App.tsx:109-203`），探针/AC1 分支直接进入测试 driver。生产界面不是已完成的四页导航壳 |
| Tauri 配置 | `apps/desktop/src-tauri/tauri.conf.json:3-16` 产品名/标题仍 `m2rc1-desktop`/resource-channel runtime，前端 dist；`:21-29` CSP 与关闭 asset protocol；`:33-42` NSIS/resource 映射 | probe 命名和产品壳状态一致；配置本身不能证明真实用户导入/翻译/阅读/导出流程 |
| installed/dev 选择 | `src-tauri/src/main.rs:583-605` 由显式 flag 或无 SRC_ROOT 且 installed host exe 存在进入 packaged；`:608-617` `%APPDATA%/com.newmanga.m2rc1.desktop`；`:650-703` 数据与资源根 | packaged 无系统 Python 回落；dev 仍需 SRC_ROOT/资源根环境。源文件/数据库路径不向 WebView公开 |
| Core 生命周期 | `main.rs:712-773` 生产 Core 先启动，30s startup ping 后启动 host_bridge；AC1/probe不启动生产 library sidecar；`library_bridge.rs:324-374` 超时停止并回收自身子进程 | 有初始 ready Gate；Core运行后掉线/重连/事件重放不是已完成能力。主要 startup 失败仍由 `expect` 结束应用，尚无产品恢复引导页 |
| 生产 command surface | `main.rs:53-77`、`:862-878` 15命令：资源 issue/revoke、ping/book、settings、region list/retype/history/restore/rerender、page resolve、chapter/page nav；ACL与 `build.rs` manifest同步 | `core.detect` 是 Python stdio探针面（`src/bootstrap/core_service.py:18-37,1237`），**未注册产品 invoke**。没有生产 ImportPages、StartRun/控制、TaskProjection、ReaderProjection、进度保存、Export/CancelExport |
| Python权威 | `src/bootstrap/core_service.py:327-379` 组装真实 Core；`:648,734,809,840,851,890,1002,1028,1053` 对应 settings/retype/list/history/restore/render/nav/resolve；`core_assembly.py:779-817,1087-1100,1148-1149`迁移、仓库、Managed Copy、pipeline恢复、reading/export服务 | 服务存在不等于IPC或React消费存在。不得把 `CoreServices.reading/export_service/pipeline/importer` 存在性记作产品全链完成 |
| 页资源与预览 | `WorkbenchPage.tsx:264,303,348` book→chapter→page→resolve；`workbench/pageImage.ts:17-28` fresh issue→chunk fetch→Blob URL；`main.rs:804-819` m2res handler；`:394-432` 重渲染预览旧引用先撤销/退休；`core_service.py:1741-1807` 启动GC/namespace保护 | 原图自动目录化已闭合；手输resource/revision仍保留 debug fallback，不能再沿旧第一刀报告称“生产自动目录化不存在” |
| 大媒体安全 | `resource_protocol.rs:13-25,40-41,446-489` Windows handle重验containment/identity/size、每请求单趟全文digest并捕获被返回chunk，16MiB chunk、256MiB承诺上限；`resourceChannel/client.ts:91-106` 前端将所有chunk组装Blob | host内存边界不等于WebView全页解码内存边界；未实现React Reader tile消费。S1-B3/B6/B8、密钥生命周期限制见 RC1集成证据 `verification/M2-RC1/integration-2f6a31cd/integration.md:43`，本轮无新实测覆盖 |
| 事件/进度 | `TaskProgressPanel.tsx:1-5,31-35` 明示静态占位；`main.rs:788-801`仅title轮询stderr；Core `serve_forever`为命令应答 | 无React/Tauri业务事件订阅、seq/replay、断线后snapshot重同步。title/stderr探针进度不等于业务任务事件通道。契约 §6/§7仍为后续方案 |

命令常量、`generate_handler!`、build manifest/ACL与runner仍有手维护多份视图（`main.rs:823-830` 自述）。Runner snapshot oracle已让已知漂移可判别，并不需要为此立即引入新的注册框架。

## 四个一级页：完成与缺口分开

| 一级页 | 真实新架构完成 | 空壳/未接线/未来范围 |
|---|---|---|
| 书架 | `LibraryPanel.tsx:24-48,153-184`真实ListBooks读取、刷新/空态/错误/页数unknown；`library/client.ts:55-76`真实invoke；三级章节/页列表由Workbench消费 | 独立Bookshelf路由、书目CRUD、导入源授权与Managed Copy交互、封面/筛选/排序/页重排等均不能按完成计。现有书库UI不能从空安装态创建自己的内容 |
| 工作台 | 五区骨架；真实page image与归一化region overlay；改标确认/短时undo、修订历史与guarded restore、重渲染preview；page epoch/request版本防迟到结果；resolve/region各300ms debounce (`WorkbenchPage.tsx:85,586,609,720,759,883-925`) | `WorkbenchToolbar.tsx:1-8`只context/计数，StartRun/翻译与viewer模式后置；TaskProgress静态；人工译文编辑、Lock/Pin、创建/拖拽/删除region、三档视图/多页选择的完整parity尚缺。当前“疑似拟声词”suspect集是React本地状态，不等于训练/纠错持久投影 |
| 阅读器 | 共享Python reading/export服务与acceptance `reader_pages`是真实业务服务（`core_assembly.py:1148-1149`，`acceptance_bridge.py:436-481`） | `apps/desktop/frontend/src` 无reader组件目录；生产command surface无ReaderProjection/SaveReadingProgress/StartExport。AC1 driver中reader/export是测试模式调用与核验，不是产品Reader页。**当前明确不做的Reader范围须单独解冻，不能借审计授权实现** |
| 设置 | `SettingsPanel.tsx:10-25,58-108`真实SFX三策略读取/保存，typed失败；`settings/client.ts`通过现有IPC；重启/只对新region生效文案见`:46-47` | 独立Settings页、Provider profiles/绑定、CredentialRef安全交换、网络/TLS/代理、模型/缓存/诊断等产品面未React化；普通settings property bag不能代替secret通道冻结 |

工作台不再是第一刀“全只读”：后续 RC4/IMPL 已补真实交互。证据须以当前代码为准；`doc/tasks/M2-WORKBENCH-REACT-1.md:117-124` 的手输page、自动资源缺口和选中缺失是该Task历史交付边界，已被后续页导航/资源/IMPL覆盖。另一方面 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:39,118` 的总括“无runtime/全部proposal”是初始来源文字，必须结合页首rev1.8与逐条落地注记读；它不能否定当前已实现15命令，也不能替尚未实现命令宣告完成。

### 测试证据层次

| 当前测试锚点 | 实际检查面 | 不能替代的验证 |
|---|---|---|
| `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:527-771,850-1135`；library/settings/client与组件测试 | DOM点击改标/undo/history/render、失败反馈、迟到结果、三级导航、debounce；client注入mock invoke | 真实WebView2/ACL/安装态Python跨进程用户动作未由DOM mock证明；占位本身被`:306`测试钉住，不是任务进度功能测试 |
| `tests/core/test_core_service.py:188`；`test_rc4_stdio_render_preview.py:84,252` | real subprocess stdio往返、Pillow文字渲染预览与轮换退休 | 生产React整旅程、普通业务并发关联/冻结child故障，不因stdio单次往返而自动通过 |
| `tests/core/test_page_nav_projection.py:75-146`；`test_page_resource_resolve.py:105-301` | sorted/unknown-parent空列表、输入拒绝；资源首次发布/idempotent/缺文件/逃逸/失败分类/自愈 | 安装后用户导入、Reader进度和tile渲染仍另需Gate |
| `apps/desktop/src-tauri/src/main.rs:1494,1560,1692,1748,1785,2190-2250`及`resource_protocol.rs`模块测试 | real dev sidecar、settings/retype/RC4、mode/ACL、handle/digest安全断言 | 忽略项/环境要求应按原日志披露，不能把测试源码存在记作本轮PASS；latest installed只覆盖runner明定场景 |
| `tests/m2_acceptance/test_acceptance_loop.py:170-245`；`apps/desktop/frontend/src/ac1/driver.ts`；`src/bootstrap/acceptance_bridge.py` | deterministic synthetic Mock/Local pipeline→持久化→重组→reader数据→PNG export | 真OCR/远程翻译质量和完整生产Reader产品页 |

当前Plan最新完整baseline记录在 `doc/REBASELINE_PLAN.md:149`：GC2 integration=`cea610ed`、pytest1941+1sk / cargo62+1ign / vitest140。它是固定历史集成证据，**本轮未执行同一套件**；之后Guard局部8/16项及packaged26项按自己的source/head追踪，不能合并为“当前全产品验收全绿”。

## Qt/Legacy seam：复用证据不能冒充已迁移

- 新架构生产 `core_service` library/settings/revision/page projection 与rerender采用headless Pillow adapters（`core_service.py:341-375`），没有启动Legacy QML UI；RenderService的SQLite/Revision保护是共享Core能力。
- production装配仍注入 `_PassthroughImageDecoder`，固定1×1 `image/rgb`，source-style analyzer返回空数组（`core_service.py:313-324`）。当前已开放命令不走图片import，故不能直接定性当前UI bug；**未来Import runtime释放前必须提供真实decoder，并验证尺寸/格式/大图失败不入库**，不能只接现有importer后称生产导入完成。
- `core_assembly.py:253-329` 的 `_ManagedPageImageSource`仍lazy import QImage/QBuffer并整图读取，`:1060-1074` 将它接入pipeline；Reader tile factory也沿共享Python实现。模块顶层Qt-free与完整pipeline运行Qt-free不是同一命题。若后续长任务/Reader要求完全无Qt闭包，须独立契约/adapter迁移；本审计不自行释放Legacy修复。
- acceptance assembly明确构造QGuiApplication/Qt decoder/layout/compositor、注册Mock/Local（`acceptance_bridge.py:164-194`）；seed synthetic fixture/预建regions（`:281-324`），reader/export用共享Core（`:436-527`）。packaged bundle含Qt有实际原因，不能以目标架构为据声称“包已不含PySide6”；这也不代表Legacy QML产品仍继续演进。

## Windows packaging 与验证证据

| 事实/证据 | 固定提交/结果 | 适用范围与不能外推之处 |
|---|---|---|
| 当前打包链 | frontend tsc+Vite → `packaging/m2ac5/build_sidecar.ps1` → PyInstaller单onedir五入口 → Tauri NSIS；`tauri.conf.json:37-42`将目录作为resources；`core_sidecar.spec:75-104,430-498`五Analysis/EXE/COLLECT | fresh checkout先生成sidecar/dist；`build.rs` fail-closed指引。sidecar脚本存在“目录已存在即跳过”，正式新源码绑定必须fresh/Force并记录hash，不能以目录存在推断当前源码已打包 |
| AC5历史与RG1 | AC5 done=`9db08dc7`；RG1 done=`b796bed3`；RG1 `doc/tasks/M2-RG1.md:32`用户接受本机基座，`:80`Windows11本机build26200已验证，Win10/其他build NOT_RUN | 尊重Task PASS，**不撤销既有用户范围豁免**。RG1冷启动为测录无阈值（`:61-70`），NSIS卸载NOT_RUN、签名/更新/bit-for-bit重复构建非范围（`:90,109`） |
| 最新fresh组合证据 | `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/build-fingerprint.json:3-8` source=`3d532c1f99e49da703d2076bd67d46b710866637`；installer=`ef617573ab39c0469079203489f4db4af78ae4e3437f8d97d87a3565bb40fa75`，579545058B；五exe hash入库。Dev 10/10+probe13/13；Packaged26/26；Sidecar/NSIS EXIT0 | producer logs固定输入有效。`doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md:91-111`逐项读证；Reviewer现场Gate NOT_RUN。integration=`73588624`核对差量/oracle通过，未重建；当前审计也未重建 |
| 安装态Gate实际覆盖 | `run_clean_start_e2e.py:423-525` installed core ping/空ListBooks/shutdown；`:527-670`资源probe和两次Mock/Local AC1；`:672-732`production存活10s、目录创建、公告marker存在、无spawn失败 | 生产阶段不操作真实书架/设置/Workbench按钮，不校验公告完整15条、不核验in-page IP/IA结果。不覆盖用户从空库导入→真翻译→Reader→导出的生产旅程；与Vitest DOM mock/test-core证据层次不同 |
| 第五入口缺口 | `core_sidecar.spec:75-104`与fingerprint已有`sfx_detect_probe.exe`；runner `SIDECAR_EXES`=`host/core/acceptance/catalog`仅四项（`:66-71`），进程回收也仅四项（`:852-864`）；DSH r4 R-003 deferred | 五入口**构建/hash存在**已证明；第五入口**安装态文件、实际frozen推理/产物绑定与回收assertion覆盖**不能从26/26推出。原SFX probe专用证据只适用于其固定产物，非最新installer自动追认 |
| ICU修复 | code=`4499217d`，integration=`65ba3014`；`core_sidecar.spec:307-409,483-490`仅隔离确认外部poppler污染，未知外部候选fail-closed，Qt6Core避免icuuc遮蔽；Runner fresh日志verified0shadowing | Windows System32 ICU运行依赖存在。DSH r2 R2-002/R2-003保留“fresh构建隔离分支未命中”/PE原始绑定局限；静态PE直接/延迟导入扫描不是任意动态LoadLibrary传递闭包证明。Windows10所需系统符号未实测 |
| Runner历史保护 | Guard code=`e167e723`，review=`8b867e02`，integration=`e7d1f7f8`；`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/integration-validation.log`两Python各8passed、CLI缺参exit2、oracle16、历史raw61hash保持 | 本Task按范围没有重跑Sidecar/NSIS/完整Gate；不能给本轮HEAD追加新的26/26或新installer验证日期 |

“Packaged通过”应完整写成：**固定source/hash的本机净化PATH与隔离APPDATA安装态、有界resource/Mock/Local acceptance通过；RG1用户范围豁免下Gate有效，独立干净Windows、多Windows版本与完整产品旅程仍未验证。** 当前HEAD更新主要是治理/工具收口，禁止将旧测试日期改成本轮现测。

## 静态风险候选：先验证，未定性当前故障

1. **请求/响应并发关联**：`library_bridge.rs:263-310`单独锁stdin写入、解锁，再锁stdout读取；`decode_response:89-117`未比对request_id/protocol/version。`core_bridge.rs:206-237`资源控制面同样分开两锁且request id恒1。两调用者可能A写→B写→B先读A响应；trait为Send+Sync且资源protocol可并发，结构上有候选风险。**本轮未实测线程交错，Tauri同步handler实际调度和现有单次请求路径也未测，不能直接宣布生产bug或立刻修改**。最小下一诊断应使用可控child/屏障重现响应归属，核对全部caller后再决定单一round-trip锁/协议守卫等最小修复。
2. **普通命令与关闭无统一期限**：production library只有startup ping有deadline（`library_bridge.rs:324-374`），普通read_line阻塞；resource `Drop`直接wait（`core_bridge.rs:240-253`）。当前Gate正常关闭成功，只证明正常路径；故障child/中途卡死/EOF/restart需要定向故障注入，不据此推断已挂死或自行扩大Task。
3. **全页Blob/解码预算**：React `fetchAll`累积parts；安全资源上限不保证长条漫/多数页查看时WebView内存/首屏时延。后续Reader若解冻，应单独冻tile/virtualization预算；不为当前有界工作台新增缓存框架。

## 两轨候选路线与 Gate

以下为 **Proposal**。Owner/Reviewer建议遵循当前角色：Qoder主责React/交互；Codex契约/集成；ZCode或Antigravity实现冻结Core/Host切片；DSH非作者验证。不得自动派发。

| 顺序/轨道 | 切片与依赖 | Owner / 非作者Reviewer | 最小完成Gate |
|---|---|---|---|
| 当前收口A | R-003最新installer第五入口packaged覆盖；依赖Runner Debt、Guard、ICU均done；Codex先冻结允许runner/verification范围和对最新hash的要求 | Antigravity（验收工具实现）/ DSH；Codex集成 | 真正构建输入/installer/五entry hash绑定；安装态第五文件与一次frozen SFX探针结果、错误/无进程残留assertion；保留26项及历史raw；正常/破坏第五exe对照；不改src/apps/model/阈值 |
| 当前收口B | stdio并发/错误envelope/卡死候选定向验证，依赖当前两bridge；诊断只读产品，是否有缺陷由证据决定 | DSH（诊断）/ Codex | 可控child强制交错、各请求回包归属与协议错误、EOF/timeout观察入库；无法触发或handler串行事实照实记录；无修复先行。复现后另冻实现Task |
| 范围解冻节点 | 四页产品需求/parity与Reader“明确不做”范围等待用户/Lead单独裁决；利用现有UI1映射，逐项区分需要产品能力与历史Legacy行为 | Codex（范围/契约）+ Qoder（UI）/ DSH | 单Task冻结四页范围、路由/空态/错误/数据保护；不新增第五一级页；把无source/未运行质量能力保留Unknown；无需重做现有视觉研究 |
| 完整产品1 | 书架/设置/工作台独立导航壳，只消费已存在15命令；依赖范围解冻，reuse Library/Settings/Workbench | Qoder / 非作者DSH或Codex | 真实Tauri窗口导航、empty/error、键盘基础、state/mount/resource cleanup；保留probe/AC1surface；不为静态导航扩IPC；Reader不可用不得造mock结果 |
| 完整产品2 | 书目/章节创建与导入最小旅程；依赖范围解冻和ImportSourceRef宿主授权契约、真实production decoder | Codex契约；Antigravity或ZCode Core/Host；Qoder UI / DSH | 从空安装态创建/授权源/Managed Copy/尺寸；拒绝逃逸/损坏/大图/半导入、源hash零变动；重启恢复；受控源引用不得传任意OS路径/大图Base64 |
| 完整产品3 | StartRun→snapshot/task projection→控制/故障恢复；依赖冻结长任务接受时点/runner与事件或查询策略；复用pipeline，不新造调度层 | Codex契约；ZCode Core/Host；Qoder UI / DSH | 真生产provider明确configured/unavailable；九状态与控制能力由Core投影；人工/Lock/current/pinned冲突、退出排空、重启恢复、错误可见；静态Tasks占位撤除需真实数据Gate |
| 完整产品4 | 人工译文/Lock/Pin/region编辑按需求逐小切片；依赖生产命令/Revision并发契约与workbench | Codex契约；ZCode或Antigravity Core；Qoder UI / DSH | expected_revision冲突判别、人工优先、仅一笔revision/atomic pointer、保护pin/lock；拖拽/编辑不能只本地画图后宣告已保存 |
| 完整产品5 | Reader projection、original/translated模式、进度与受控导出；**依赖Reader范围先解冻**、成熟page/resource/Task结果和OutputTarget授权契约 | Codex契约；ZCode Core/Host；Qoder Reader UI / DSH | 生产命令从Core服务闭环；真实阅读与重开恢复；stale/missing/lineage导出保护、源零写、取消；长条tile/内存预算单独证据；不得借AC1 mock reader测试替代 |
| 完整产品6 | Provider/Credential/网络与运维设置；依赖secret host exchange、错误与设置effect时点冻结 | Codex契约；Antigravity Core/Host；Qoder UI / DSH | secret不出普通日志/事件、TLS危险确认/失败不写半配置、configured能力投影、重启生效说明；复用既有配置存储服务 |
| 发布合流 | 重新固定release source/installer，生产四页E2E与目标Windows矩阵；依赖已选择产品切片done与质量Gate | Codex Gate / DSH非作者 | fresh构建+hash链、真实生产UI journey、五入口闭包/进程回收、故障恢复、安装/升级/卸载范围裁决；Win10或独立干净机若用户要求则实测，保留既有本机裁决；签名/更新不自行增Scope |

## 可直接转发的下一步（仅释放准备，不启动实现）

**推荐当前先交Codex冻结R-003验收覆盖Task；Reader/完整产品路线留在单独等待范围解冻节点。** 当前没有已释放可实施下一Task，故本审计后 **无需下一步操作（实施层）**；可以立即开展的仅是父审计汇总与Lead的候选评估/释放准备。

可转发给Codex：在唯一仓库 `G:/CODEX/New Manga`，以本报告审计 `base/head=e4242ecd419eb0eea098d2f63b40f709aa5caeea` 为证据起点，先核对最新Plan/STATUS（当前无Active/released）和未提交归属。建议单独冻结 `M2-PACKAGED-FIFTH-ENTRY-GATE`（建议ID，尚未创建/释放），Owner=Antigravity、非作者Reviewer=DeepSeek Harness、Integrator=Codex；Owner branch/worktree与实际实施base/head **待Codex创建和登记，不臆造**。只授权 `packaging/m2ac5/run_clean_start_e2e.py`、必要工具专用测试、自有 `verification/<Task>/` 与Handoff/Task记录；禁止生产src/apps、Schema、依赖、模型/阈值、历史raw、用户源文件与宿主APPDATA写入。复用已冻结latest installer SHA与fresh构建证据，加入第五入口安装态/一次probe/typed失败/回收与破坏对照，不把仅目录存在或exe hash当完整runtime验证。交付固定code head、逐项AC、含shell/解释器/HEAD/EXIT的dev与packaged日志、installer/five-entry fingerprint和Handoff；DSH非作者审查、Codex集成验证后方可done。如需要修改生产面或重建源变化，先修订范围并重新绑定fresh产物。未完成正式释放登记前不得派发实现。

## 本轮验证边界

只执行文件读取、`rg`定位与Git状态/HEAD/分支/common-dir/相关最后提交查询；相关production/app文件只读。无构建、无npm安装、无cargo/pytest/vitest产品执行、无外部网络或模型请求，动态验证=`NOT_RUN`。测试文件存在性可证明检查覆盖设计，不证明当前HEAD现测通过；本报告所有已有PASS均保留其原source/hash/日期与适用范围。
