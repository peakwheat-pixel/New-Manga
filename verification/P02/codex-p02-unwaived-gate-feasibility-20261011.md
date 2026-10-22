# P02M11：未豁免安全门综合可行性审计

## 交付与裁决边界

Owner/Author=`/root/p02_gate_feasibility`；非作者 Reviewer/Integrator=`Codex /root`；日期=`2026-10-11`（Asia/Shanghai）。这是 Owner 静态审计交付，不是 Review、adjudication 或运行准入。实际 runtime model/effort=`NOT_VERIFIED / NOT_VERIFIED`：可用接口未暴露可核验值，Integrator 亦无法核实；不把请求的 `gpt-6.1-sol / high` 当实际配置。

仓库=`G:\CODEX\New Manga`；branch 实测=`main`；start/final HEAD 实测均=`cddff58469b56e181019a8ddfeade80684bc7eb9`；正确引用参数后 tree 实测=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；Git common-dir 实测=`G:/CODEX/New Manga/.git`。治理恢复点与派发基线一致；`RESUME_SAFE` 仅指本次静态 Task 范围和已绑定文档，不证明宿主执行状态、整个工作区或 index 无写。共享工作区未提交文档须按下表 SHA 单独绑定，HEAD 不包含它们的当前文本。

**结论：在当前 AppContainer/LPAC 架构、r6 条件及唯一 registry absence waiver 下，本轮没有建立满足全部未豁免条件的受支持执行链，`ALL_UNWAIVED_PRECONDITIONS=UNRESOLVED / BLOCKED`。** 新查的进程错误模式/WER exclusion 路线只提供局部语义，不能解决完整 WER destination/T0 条件，更不解决 profile-folder、Getter 和执行主体的强制写边界。结论受实际检查的来源范围限制；没有证明 Windows 永远不存在其他实现，也没有断言未知 API 分支必然写入。

用户原值精确保留：

- `private_registry_absence=UNPROVABLE`
- Technical Gate=`NOT_SATISFIED`
- Owner Risk Acceptance=`APPROVED`
- Gate Disposition=`WAIVED_BY_OWNER`
- Build Authorization=`AUTHORIZED_WITH_EXCEPTION`
- `technical condition unmet; user explicitly accepted residual risk`

唯一例外仍是“创建前无副作用证明目标 private registry storage 不存在”。不覆盖 profile-folder、Getter 资格/有效写权限/全分支副作用、WER/T0、身份、ACL、环境、protected hashes、controller/child/broker/write closure。本文不增加 waiver，也不把所有其它未知合并进已接受的 registry 风险。

按项目当前裁决沿用而非宿主复测：P02PRE=`BLOCKED`，profile=`NOT_CREATED`，ACL/registry=`NOT_MODIFIED`，OS preflight=`NOT_RUN`，Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`，build/Cargo=`NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`。本轮没有技术 Gate PASS。

## 判断方法与证据层级

本轮复用已独立 Review/Codex adjudicate 的 M7/M8/M9 和 r6，不重复其单项检索。首先把候选动作的输入、前置条件、被证明对象与保证边界连接起来，再检查新候选能否解除循环或补足至少一个未覆盖的硬条件。现有正式接口支持“测量一个字段”与支持“全部前置条件成立后安全运行”分开记。

- **合同保证**：官方正文明确声明的具体作用，限于对应 API、调用上下文和适用版本。
- **未说明**：来源没有保证的 absent/损坏/错误/初始化分支、完整 loader/controller/代理活动或对象映射。不能作反面实现断言。
- **推论**：从 r6 的依赖顺序及已知合同得出的准入判断；不能冒充 Microsoft 原文。
- **本机事实**：本任务禁止采集；旧运行留证只证明当次对象，不补本轮 token、profile、ACL、环境或 T0。

`SUPPORTED_PATH` 在下表只表示该单项有具体受支持的测量/比较方法，不是当前允许执行，更不是无条件的无副作用保证。只要完整执行前依赖未闭合，整体仍 BLOCKED。`UNRESOLVED / BLOCKED` 包括缺正式合同、缺当前对象证据和缺受审实现，逐项说明原因。

## 逐项可行性与交叉依赖

| 要件 | 判定 | 具体依据与完整链缺口 |
|---|---|---|
| exact profile-folder 创建前解析，无创建/初始化副作用，absence 分类 | `UNRESOLVED / BLOCKED` | M7 adjudication、M7 §2/§4–6、r6 profile/Gate 3。已审 SID Getter/known-folder/COM/token 路线都未提供“固定用户 + 尚未创建 exact moniker/SID + 成功/失败全分支 no-init + 可区分 absent/拒绝/损坏”的联合合同。本轮没有新官方候选满足它；不重搜 M7 同组 API。仅增加进程错误模式不改变这些 API 的文件夹解析合同。 |
| zero-capability LPAC Getter 资格 | `UNRESOLVED / BLOCKED` | M8 adjudication、M8 §4、r6 registry/Gate 6。现有 Launch 指南的 registryRead 前提没有已审 private-store 例外。已知 SID、同一用户、Create 成功或 requested `KEY_READ` 均不产生该例外。加入 capability、普通 AppContainer 或 broker 代开均超出冻结范围。 |
| Getter 返回引用的有效写边界 | `UNRESOLVED / BLOCKED` | M8 §4 的 RegOpen/RegCreate 通用合同：请求 mask 与对象安全描述符控制的有效创建能力不能混同；r6 禁止写 API 也不是 OS 拒写证明。exact store/view/SD 未提供且不允许猜测或枚举扩权。 |
| Getter 成功/失败全分支无创建/加载/初始化/写副作用 | `UNRESOLVED / BLOCKED` | M8 adjudication、M8 §3–4。Getter 签名、名称、关闭 handle、已有 Create API 和单次成功观察均不补完整内部分支合同。唯一 absence waiver 不豁免调用 Getter 本身的写入风险。 |
| WER actual reader/view/destination 绑定 | `UNRESOLVED / BLOCKED` | M9 adjudication、M9 §1–3、r6 WER。通用 view 规则不是 WER reader 绑定；未冻结所有 EXE/helper 架构、有效 per-image/global/policy 配置、展开 actor/用户与真实目的地。新候选 N1–N4 见下节，不能消除这些未知。 |
| T0 第一读取及 bootstrap 全程安全 | `UNRESOLVED / BLOCKED` | M9 §4、r6 WER/Gate 4。取得 actual destination 所需 identity/path/environment/policy 输入属于当前“任何 Phase A 读取前先 T0”约束所覆盖的读取；尚无已冻结输入或经独立保护的 bootstrap。N1 在目标入口执行不能回溯覆盖该进程启动前/loader 阶段；继承方案将前置义务移给尚未证明安全的 launcher。 |
| identity/SID 字段测量与逻辑绑定的局部方法 | `SUPPORTED_PATH`（仅方法） | 已审 advisor §2–3、r6 identity/Create/launch：固定 token handle 上 `GetTokenInformation` 的 user/elevation/type/statistics/AppContainer/LPAC/capability 字段，`DeriveAppContainerSidFromAppContainerName`，以 `EqualSid` 比较 derived/returned/actual SID；suspended launch 后用真实 process token 绑定。方法支持不等于当前 user/token/LPAC 已核实，也不保证 controller 全程无写。执行仍依赖 T0、受审 controller、folder/Get/Create 准入；当前 `actual_identity=NOT_VERIFIED / BLOCKED`。 |
| exact ACL/path/input/output/TEMP/cache 与 protected hashes | `UNRESOLVED / BLOCKED` | r6 输入表、环境表、13 leaves/canary、protected/Gate 5；已审 advisor §5–6 给局部 handle/file-ID/SD/hash 方法。没有当前对象、全部 aliases/streams/现存 ACL、实际 LPAC temp/cache readback 证据；零 ACL 修改必须坚持。目录字符串、env 字符串、单次 AccessCheck 和前后 hash 相等都不能证明所有路径全程拒写。profile-folder 未解析使 exact TEMP 根也未绑定。 |
| controller/native probe 及 launch/error/observer 闭包 | `UNRESOLVED / BLOCKED` | r6 controller/child/Gate 1/7；r6 Review 对源码/EXE/DLL/hash/argv/CWD/dependencies/API 错误路径全部 `NOT_FROZEN`。可信 host controller 自身及其 loader/WER 的写边界尚未证明；LPAC probe 的边界不能传递给调用 Create 或采样的宿主。 |
| child/broker/完整写入强制边界，安全停止与 evidence | `UNRESOLVED / BLOCKED` | r6 child/protected/stop；已审 advisor §7。Job/child restriction/debugger 的局部保证不覆盖 external broker/COM/WER；Job 通知/poll/self-report/hash 比较不能排除瞬时写和漏观测。零子进程 synthetic probe 不能替代需要 Node/Cargo/Python/WebView 子进程的 build。64MiB/16KiB buffer、CREATE_NEW、fail-stop 是候选规则，非已 pin 的实现或全 stop 证明。 |

identity 的 `SUPPORTED_PATH` 若要落成独立实施 Task，必须先由 Codex 另冻结：精确 native source/EXE/DLL/hash/PE architecture/依赖/argv/CWD、token 字段和读取权限、SID 比较及每个失败分支、bootstrap/T0 顺序、process handles 生命周期、内存 evidence 与全 stop 条件；非作者 Review 绑定同一对象。预执行证据包括 launcher/controller 身份与无写边界、既有环境/路径范围、image/dependency pins 和 protected baseline。未满足先验保护前该 Task只能做静态设计；本报告不释放 API/实现/build。`EqualSid` 的局部支持不能用来跳过其它 Gate。

### 不能靠重排解决的四个依赖

以下是 r6/已审合同的**依赖推论**，不是新的 Windows 行为结论：

1. **解析路径与创建的先验关系**：Create 的许可依赖创建前 exact folder absence/no-side-effect；Create 后返回路径只能服务后置核验。先 Create/先启动目标进程再解析路径，把后置事实替代先验条件，违反当前冻结范围。
2. **actual LPAC token 与前置安全项**：r6 的实际 LPAC `AccessCheck`/TEMP readback 与 token 验证需要一个合格 actual token。现有受审 launch 路线在 Create 之后产生进程 token；尚无已冻结、无 profile 初始化的创建前 token 获取路线。可以把当前用户/宿主 SD 的文本评估放前面，但它不等于最终 LPAC 的实际验证。若把这类后置检查直接移到 Create 后并声称 Create 的全部前置条件已满足，会改变准入条件；需另行冻结并证明替代先验屏障，不能自行移动。
3. **T0 与目的地发现**：从已经给定的所有 exact WER 对象开始可以定义快照顺序，但 r6 中 actual 对象尚未确定。先读取 identity/config/环境再叫它 T0，不证明此前无副作用。N1 的继承方案也需要一个已有安全 launcher，当前没有这个对象 pin 或合同。
4. **观察与强制边界**：给 hash/Job 消息加更多采样不能提升为全程无写保证。controller/probe/build/broker 是不同主体；对一个 probe 的 token/Job 限制不能自动约束其它主体或 OS 服务。

这解释了为什么“先完成较容易的身份/哈希预检，再补难项”仍不是当前可释放路线：容易项的执行主体与 T0/写入边界本身尚未闭合。它不否定这些局部方法的用途，也不要求为未知项添加新的 waiver。

## 本轮新增候选：进程错误模式能否移除 WER 前置依赖

这是对已审 M9 的一个有限补查：M9 查过 WerApi.h 和一般 WER 政策，但未建立下列进程模式/继承/exclusion 的联合合同。原 advisor 已警告 child error mode 不等于完整 WER 安全；本轮只检查其是否存在更强、可以解除循环的正式依据，不重做 view/目录研究。

| ID | 本轮实际打开的 Microsoft 一手来源 | 页面日期/支持范围 |
|---|---|---|
| N1 | [SetErrorMode](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-seterrormode) | Last updated 2024-06-26；XP/Server 2003 起；Kernel32；浮动 Learn 正文 |
| N2 | [Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) | Last updated 2025-07-14；XP/Server 2003 起；本轮只采用 error-mode 继承部分 |
| N3 | [SetThreadErrorMode](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-setthreaderrormode) | Last updated 2021-10-13；Windows 7/Server 2008 R2 起 |
| N4 | [WerAddExcludedApplication](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-weraddexcludedapplication) | Last updated 2024-02-22；Vista/Server 2008 起；Wer.dll |
| N5 | [WerSetFlags](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-wersetflags) | Last updated 2024-02-22；Vista/Server 2008 起；当前进程 reporting settings |
| N6 | [Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps) | Last updated 2024-07-18；Vista SP1/Server 2008 起；为 N1/N4 边界重读，复用 M9 同一正文 |

检索日期=`2026-10-11`。这六页正文均可读；页面模板同时显示 authorization 提示，但未阻止正文读取。没有获取不可变 MicrosoftDocs commit 或本机 Windows/SDK/DLL 版本，`DOC_IMMUTABLE_REVISION=NOT_CAPTURED`；页面更新日期不是 runtime pin。本轮未运行这些函数、启动进程、下载 header/binary 或改变 policy。

**N1+N2 的保证：**N1 对 process-wide `SEM_NOGPFAULTERRORBOX` 明文说明系统不调用 WER，并说明子进程继承 error mode；N2 指定 `CREATE_DEFAULT_ERROR_MODE` 会改用默认模式而不是继承。因此，“已经正确设置的 launcher + 不使用该 flag 的指定子进程”有局部继承依据。[N1](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-seterrormode)、[N2](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)

**未说明及准入推论：**两页没有给调用成功/失败和 loader/初始化的全程 no-file/no-registry-write 保证，没有绑定所有 LocalDumps/WER 目的地，也没有封闭外部 brokers。N6 明确 LocalDumps 与其余 WER 基础设施分别控制，即使 WER disabled 也能收集；它没有明确规定与 N1 flag 的所有交互。不能据此断言该 flag 必然留 dump，亦不能从“不调用 WER”外推所有独立收集/代理永不写。继承只把设置义务移到 launcher；launcher 自身启动/调用前区间仍需原安全证据，子进程可改模式的边界也未冻结。[N6](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)

**N3 不能无差别替换 N1：**线程函数对同名 flag 的正文只承诺不显示 WER dialog，并限定 calling thread；它没有给 N1 的整进程 WER invocation/子进程继承保证。不把相同常量名视为相同完整合同。[N3](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-setthreaderrormode)

**N4 明确不合当前写入范围：**exclusion list 是 HKCU 或 HKLM registry 中的配置更新，不是仅改变 probe 内存态；`bAllUsers=FALSE` 仍写宿主 HKCU。这超出当前只有 fixed profile Create API-owned store 副作用的写许可，而且 N4 未给独立 LocalDumps 全部取消保证。不能采用或测试。[N4](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-weraddexcludedapplication)

**N5 不补完整屏障：**正文列的是当前进程报告设置，减少 heap 信息/避免线程暂停/排队等，不是全程 no-write/WER destination closure。排队语义不能转写为无写。N1 将 UI 控制与不调用 WER 分开；UI 消失不是数据不落盘保证。[N5](https://learn.microsoft.com/en-us/windows/win32/api/werapi/nf-werapi-wersetflags)

新候选最终分类=`UNRESOLVED / BLOCKED`。N1+N2 可以是未来已受保护 launcher 的附加防护，但不能独立满足本轮 WER/T0 Gate；N4 因明文宿主 registry mutation 在当前范围直接排除。没有冻结任何新 flag、wrapper、policy 改动或执行步骤。

## 无全链路线时需要的具体新证据与用户决策

以下是**尚缺证据清单**，不是对 Microsoft 或第三方发送支持请求的授权，也不是重复研究 Task：

1. **folder 支持合同**：固定用户、尚未创建 exact SID/moniker 的真实路径解析，成功/失败/缺失全分支 no-init/no-create，错误分类与支持 Windows 范围。只有已知 SID 或 known-folder flags 不足。
2. **Getter 支持合同**：明确 zero-capability LPAC 对自身 store 的资格、对象/view/有效创建能力边界，以及全部成功/失败分支无 registry 初始化/写。一次试调用/成功/失败都不能补全。
3. **WER/bootstrap 支持链**：能够保护 launcher/controller 从启动至 T0 的独立强制边界；完整 image/helper/policy/view/展开 actor/实际 destinations 与可靠 T0 方法。若要用 N1 消除读取义务，需明确覆盖 LocalDumps/其它 reporter、所有线程/进程与调用前阶段的更强正式依据。
4. **实际对象及执行实现**：另冻结 controller/probe/build phases 的 source/binary/dependencies/flags/env/error paths，解决实际 token 到前置 ACL/TEMP 验证的顺序；取得每个精确对象的现存 ACL/path/ID/alias/cache/protected baseline，证明 host controller 与所有 child/broker 的强制写边界、全停止和真实证据落盘。静态合同成立以后，仍需单独释放的实际验证 Task；本文不能提供这层证据。

没有新支持合同/可验证保护链时，可以继续保持 BLOCKED；这不需要新的用户风险裁决。**仅在用户要求仍继续执行、且必须改变现有安全条件或隔离边界时，下一项才是 `HUMAN_REQUIRED`：是否授权 Codex 另开“安全准入/验证隔离方案重定界”的静态设计 Task。** 该一次决策应先审查完整边界方案与逐项风险，不等于同意额外 waiver、降低保护或采用任何指定替代环境。不能只再豁免 folder 就声称可执行：Getter、WER/T0、controller/write closure 等仍独立阻塞。当前不推荐逐个追加 waiver；不恢复未选架构、不查询/启用 Windows Sandbox。

推荐下一步为已经指定的 P02M11R 非作者静态 Review；不是 runtime。Review/adjudication 后，如仍无上述新证据，执行层无需下一步操作。

## 独立复算的项目文件 pins

以下为本次精确项目文档 `Get-Item Length` / `Get-FileHash -Algorithm SHA256` 的实际结果，batch exit=`0`。治理是当前工作区文本，不套用 r6 的旧治理 pin。复算时 M7–M9/r6 技术对象与既有裁决 pin 一致。

| 文件（相对仓库根） | bytes | SHA-256 |
|---|---:|---|
| `doc/REBASELINE_PLAN.md` | 220382 | `9F237FC0A943A4ADA011B972C4485EEC0E953747702A24EBCEDBAB28846B248F` |
| `doc/00_INDEX.md` | 40607 | `30C2286A2EB1D02FE6399FF55244F4265392894D54996848BB679CB47A7AA577` |
| `doc/STATUS.md` | 247814 | `29E465470FDBA3A6DAE50F917A5DEC7E92A6BE16393DE4821423C81F8500E667` |
| `doc/09_COLLABORATION.md` | 19131 | `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D` |
| `doc/tasks/P02.md` | 202455 | `825D88E129811BE2878C5DE90A1FA2BB9F762AEDE3D5A58523B4E42E0132BFFD` |
| `verification/P02/codex-checkpoint-p02-manifest-r6-reconciliation-20261011.md` | 14766 | `C40F07983439FF5E0EBBD2DDB39E4E6D858669572386A855B06EFB33040D3FBE` |
| `verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md` | 3985 | `DFE1F6EEAC9C3AF332D3050FD51CE281169264C6D4D56346AF82FE5791400631` |
| `verification/P02/codex-p02-zero-capability-registry-getter-adjudication-20261010.md` | 4259 | `7AA918590AF737A0824BFE292620DCA3824E5E9710AE97BC4D725E9FE5CB4E3C` |
| `verification/P02/codex-p02-wer-per-image-bootstrap-adjudication-20261010.md` | 3127 | `F59409529E0D4E8BB35A833D9B894B92B612068DEA1AD151231DF4ED76F9F334` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 44307 | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | 23380 | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | 5560 | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` |
| `verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md` | 23075 | `BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A` |
| `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md` | 15483 | `8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6` |
| `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` | 17105 | `6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3` |
| `verification/P02/codex-p02-execution-manifest-design-advice-20261010.md` | 26212 | `7A6B6D72C8484611B05DF6AC666A5A9D69A7F582EC21D2EC455D064938CB3C45` |

M7–M9 原文中的正式来源 URL/固定 Microsoft header revision 保留在上述已审对象，本轮不冒称重新抓取它们。下列局部支持直链仅为可追溯旧来源：

- profile：[GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)、[KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag)。
- Getter：[GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)、[RegOpenKeyExW](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw)。
- identity：[GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation)、[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)。
- local file/security/child methods：[GetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo)、[GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex)、[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)、[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)。

## 实际命令、错误与未执行项

Shell=`PowerShell`，cwd=`G:\CODEX\New Manga`。只读取上列治理/P02 文档、技能文本和 Git 项目元数据；没有采集目标 Windows 对象状态。

| 实际动作/命令 | 退出与限制 |
|---|---|
| `Get-Content -LiteralPath` 读取 Plan/Index/STATUS/协作协议/P02 Task/checkpoint/M7–M9 adjudications/research/r6/Review/adjudication/advisor；后续使用 `-TotalCount` / `Select-Object -Skip ... -First ...` | 各工具 shell batch exit=`0`；最初整份治理输出超过工具预算而截断，改用当前顶部、Task合同、正文及相关段落定向读取。没有从截断输出推断完整工作区或命令成功。 |
| `rg --files verification/P02 doc`、`rg --files doc`、`rg -n` 定位 P02/M11/checkpoint/相关 API 和官方 URL | batch exit=`0`；仅项目文件名/文本，不做 target profile/path/ACL probe。 |
| `Get-Content` 读取 ponytail `SKILL.md` | exit=`0`；复用已审 evidence，不创建实现、测试或无关抽象。 |
| `git rev-parse HEAD`、`git branch --show-current`、`git rev-parse --git-common-dir`、修正后的 `git rev-parse 'HEAD^{tree}'`、`git rev-parse --path-format=absolute --git-common-dir` | 成功 batch exit=`0`；HEAD/tree/branch/common-dir 如上。未运行 worktree list、remote/alternates/scratch 或 target environment 查询。 |
| 一次未引用 `git rev-parse HEAD^{tree}` | PowerShell 将 brace 参数错误处理；stdout 混入 `-encodedCommand` / `dAByAGUAZQA=`，Git 报 `fatal: ambiguous argument`。同 batch 后续命令返回 `0`，该失败子命令的独立退出码未捕获，记 `NOT_CAPTURED`；丢弃该 tree 输出，以引用修正的成功结果为准。 |
| 启动首批中的普通 `git status --short` | 实际调用，发生在当前 checkpoint 记载的 safe NUL snapshot 之后；没有 pre-index hash，个别子命令 stdout/exit 因整批输出截断未独立保留。批次最终 exit=`0`不能代替该子命令退出证据。**`index_side_effect=NOT_VERIFIED`**，不能声称无 index 写入。已告知 Integrator，后续不再运行 status，不恢复/覆盖/重新探测 index。 |
| `$p02AuditInputs` 精确 16 文档 `Get-Item -LiteralPath ... -ErrorAction Stop` / `Get-FileHash -Algorithm SHA256 -ErrorAction Stop`，随后 HEAD/tree | exit=`0`；pins 如上。只文档对象绑定，非受保护用户数据或 OS 对象采样。 |
| `web.run open` 两批，各三个 URL，分别 N1/N4/N5 与 N6/N2/N3 | 正文均读取成功；无 shell exit 概念。没有 search、community/Q&A、API调用、registry/WER读取、远程消息或下载执行。 |
| `apply_patch` 创建唯一 Owner 文件 | 只本报告；交付 bytes/SHA 另向 Integrator 报告，不把自 hash 嵌入文件。 |

上述普通 status 是本轮可避免的取证缺口，已如实限定；没有把后来的 HEAD/tree 或既有 index pin 回溯作“此次 index 无副作用”证明。它不提供 P02 执行准入证据。

禁止项均未执行：Windows OS/API/registry/WER/token/identity/path/environment/ACL 目标状态查询、preflight、profile/Create/Delete、Sandbox、提权、build/Cargo/AC、controller/probe启动、用户漫画/数据库/Lock/current/pinned Revision/凭据/模型内容访问。没有修改 r6、旧研究/Review/adjudication、共享治理或源码，没有 commit/reset/clean/stash/删除/覆盖他人内容。

## 非作者 Review 接力

Task=`P02M11R`；Agent=`Codex /root`（不是本文作者）；启动条件=Owner 文件固定 bytes/SHA + 确认 live M11 scope/HEAD 一致；依赖=M11 交付及已完成 M7R/M8R/M9R/M10R。Recovery point=`G:\CODEX\New Manga` / `main` / base=current HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。

Scope：只写 `verification/P02/codex-p02-unwaived-gate-feasibility-review-20261011.md`；不改本文/r6/研究/源码或用 Review 释放执行；adjudication 在随后独立文件由 Codex 处理。无共享接口/Schema/依赖变更。Deliverables：对象 pin、来源层级/依赖推论核对、material findings 或无发现、逐项 BLOCKED/NOT_RUN，之后独立 adjudication。

Verification：在该仓库用 `Get-Item -LiteralPath 'verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md'`、`Get-FileHash -LiteralPath 'verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md' -Algorithm SHA256` 和 `git --no-optional-locks rev-parse HEAD` 绑定文档/基线；静态核对唯一 waiver 原文枚举、每项方法/缺证、N1–N6 原文与推论、index/model 未验证记录；不执行目标 OS/API 或测试。Review 最多给静态文档结论，不写技术 Gate PASS，不把 `SUPPORTED_PATH` 的局部 identity 方法升级为当前调用授权。

可直接转发：“请在 `G:\CODEX\New Manga`、main@`cddff58469b56e181019a8ddfeade80684bc7eb9` 对固定 bytes/SHA 的 P02M11 Owner 报告做非作者 P02M11R 静态 Review。只写 `verification/P02/codex-p02-unwaived-gate-feasibility-review-20261011.md`。核对 M7–M10 pins、全部未豁免要件和四个依赖，特别是身份局部 SUPPORTED_PATH 不等于执行准入、SetErrorMode/WER exclusion 官方合同/未说明/推论边界、唯一 registry absence waiver 原文及 index/model NOT_VERIFIED。禁止 OS/API/registry/WER/token/path/environment/ACL/preflight/Create/Delete/Sandbox/提权/build/Cargo/AC/用户数据访问；不改 Owner 文件或自称 Gate PASS。交付后另作 Codex adjudication，Hard Build Barrier 继续 EFFECTIVE。”

未执行宿主安全验证；未取得实际 model/effort 和不可变新增网页 revision。
风险：现有证据无法闭合全部执行前安全条件；一次普通 status 的 index 副作用未验证，执行继续 BLOCKED。
