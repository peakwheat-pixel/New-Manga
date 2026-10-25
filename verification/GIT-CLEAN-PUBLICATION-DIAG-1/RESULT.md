# DSH blocked Review 处置与诊断

2026-10-24 / Codex。源 main 固定 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；父候选仍为独立 root `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。父 Task 保持 `in_review`，DSH r1 `blocked`，不 push、不 done。以下为 Owner 诊断与裁定，不是独立批准。

## R-001：已复现测试共享污染，产品并发 Gate 保持阻断

隔离副本首次构建因未生成 frontend dist 停止（编译失败，没有执行测试）；随后在本副本离线 npm ci/build 均 exit 0。第二次运行默认并发：`cargo test --locked --offline -- --skip packaged_sidecar_tests::`，明确 unset `RUST_TEST_THREADS`，未传 `--test-threads=1`。

结果：**151 passed / 2 failed / 1 ignored / 12 filtered，exit 101**。`ac4_unreaped_worker_registry_tracks_and_reaps_finite_lifecycle` 在 9150 断言 tracking 成功失败；`ac1_consecutive_lock_timeouts_keep_the_handle_and_the_holder_registers_it` 在 9278 断言 holder 最终注册失败。日志含 capacity(32) 告警。缺失 sidecar 用例本轮已通过。

对照：上述两个失败测试、`ac2_saturated_registry_answers_boundedly_and_never_loses_the_handle`、`ac4_unreaped_worker_registry_capacity_cap_and_lock_failure_retains_handle` 各在独立测试进程执行，**4/4 exit 0**；每次 1 passed，其余 filtered 仅为精确选择对照，不计全套 PASS。

静态裁定（基于同一 r4 的 `library_bridge.rs`）：

- 1606–1608：MAX=32 与 `Mutex<Vec<UnreapedWorker>>` 是进程级全局，覆盖真实 reader/writer 回收路径（3793–3955）；既不是 test-local，也不能据此直接判为产品缺陷。
- 9233 的测试持有同一个全局锁跨过整个超时窗口；9297–9344 的饱和测试填入 32 个长寿命 worker 并最终全局 reap。9143–9162 的生命周期测试同时假定立即可注册且自己能观察/回收，未冻结其他测试写入/回收。即使单个 Mutex 操作互斥，跨调用序列的断言也不具测试隔离；全局 reap 可回收另一测试的已结束 worker。
- 1625–1679：只有容量与锁确认后才 take handle，饱和时有限重试返回 false，保留调用者的 handle；1696–1734 holder 背压重试并处理 spawn 失败。生产饱和会真实触发这一背压，**不能将 registry 改为线程局部或放宽 MAX 来解决测试**。
- 本轮证明默认套件存在共享状态干扰，并确认四条路径在独立进程可通过；**没有证明真实多 channel 持续饱和时的公平性、资源上限或回收时限**。R-001 诊断已交付，生产并发安全未排除，父 AC4 仍 BLOCKED。后续测试隔离修复/产品压力验证须另冻范围、固定新 head 并独审；不以串行对照代替默认套件绿灯。

## R-002：原始事件冻结；错误信息仅在隔离副本保留

`core-r2-source-pins.json` 逐一记录原 r2 pytest basetemp、checks SHA、三个主 DB 的来源/副本 SHA、查询和完整 `plugin_error` 行。三个 DB 均为 344064 bytes；每个 before_export 都含 `PLUGIN_HOOK_UNAVAILABLE / cannot grant sandbox access to python.exe`，opt2 另含 after_export。原位置 WAL 在复制前后均为 0 bytes；Windows 拒绝读取 WAL，不强制解锁、不改 ACL。因 WAL 为空，复制已 checkpoint 的主 DB，副本以 `mode=ro&immutable=1` 查询；SHM 是协调状态，不参与历史事件证明。原 DB 前后 hash 相等。副本在本 Task workspace 和补充冻结包中均保留，local-only。

隔离 `source/src/infrastructure/plugins/sandbox.py::_grant` 非零返回仍抛 `SandboxError`，在异常对象的 `returncode`、`stderr` 保存 icacls 原始字段，用户可见 `str(error)` 保持非敏感原消息。失败不缓存；成功缓存逻辑不变。`PluginService` 仍以相同 `str(error)` 转成 `PLUGIN_HOOK_UNAVAILABLE`，未改 IPC/Schema/用户界面。两个 mock 测试覆盖失败诊断、成功缓存、启动 OSError，不执行真实 icacls，exit 0。

这些字段只在隔离副本生效，**不追溯补造 r2 的 returncode/stderr，也未集成到 main/父候选**。r2 真实 icacls 错误码仍 UNKNOWN；“权限/能力不足”是静态推断，不能宣称已排除产品缺陷。Core 全套不重复，仍 771 passed / 1 个参数化用例的 3 组参数失败。

## R-003–R-008：冻结、日志与串行披露

追加 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package-r2/`；旧 `review-package`、DSH 文件、原始 JSON/log 不改。`PACKAGE_MANIFEST.json` 固定 62 个文件 SHA；验证器拒绝缺失的机器元数据 log 引用，逐项验证所有 SHA。

- R-003：加入 169 行 `(outer_object, embedded_git_object, payload_sha256)`，去重 338 禁止 ID，并 pin 原 disposition 的 SHA；不含 JPEG payload。
- R-004：复制所有原 checks/log，包括 checks-r3、npm-ci-r4、frontend-build-r4、core-tests-isolated-deps；新增 `checks-r4-clarified.json` 显式记录 12 filtered 原因，原 checks-r4 不改。
- R-005：19 个旧 raw log 全部原样冻结；另建 19 个带 EXIT/argv/cwd/shell/环境的 **RETROSPECTIVE_ENVELOPE**，EXIT 来自原 checks，缺失 venv/环境字段写 UNRECORDED，绝不伪装成当时采集的日志头。新诊断日志由运行器即时写 RUN_HEADER 和实际 EXIT。旧运行环境完整性仍无法追溯补齐，复审须接受该限制或另授权有新变量的运行；不为补头盲重跑失败。
- R-006：r2 串行 **152 passed / 1 failed / 1 ignored / 12 filtered，exit 101**；r3 串行同为 **152/1/1/12，exit 101**（缺 P22 优先夹具，P04 fallback 等待请求，受控停止自有子进程）；r4 补齐 P22 源夹具后串行 **153/0/1/12，exit 0**。这不是“串行一次即通过”。r2 默认并发 150/3，本轮 r4 默认并发 151/2，registry 仍失败。
- R-007：候选只允许 Git tracked 对象/分支方式交付；禁止直接复制/压缩 live 工作目录；其中 node_modules/dist/运行日志为 ignored 本地产物。此冻结包含测试 DB 与本机路径，也仅作本地复审，不能随源码发布。
- R-008：仓内历史过程文件保留并逐项登记 SOURCE_PIN；外部补包以 manifest 为冻结权威，仓内副本是来源，不是另一套判定口径。

## 低优先级说明 R-009–R-013

Core 是一个参数化用例的三组失败。第六个 samples/manifest.json 同由 `experiments/TASK-016/generate_samples.py` 创建，其当前 manifest 未单列 generator 字段；这里补充说明，不修改旧候选。Git 实际为 1 loose ref、无 packed-refs。`private_profile_path_hits=[]` 只指真实个人目录标识 49745 已移除，源测试的 Alice/sec-fix-path-echo/settings-secret-agent/USERPROFILE 占位仍保留，不声称无任何 C:\Users 文本。源同路径五 PNG/manifest 是旧渲染批次；候选从固定生成器重建，SHA 与旧批次不同。未导出 .gitattributes；r4 以 core.autocrlf=false 固定换行，新诊断 clone 初始受全局 autocrlf 影响产生状态缓存差异，已设 false，Git diff HEAD 无语义改动；不将这些状态报告为生产修复。

## packaged 与复审决策

独立 `packaged-source` 从同一 e34 root 建立，无 remote；使用已有 Python 3.12 构建环境，只读其解释器/依赖，新构建 sidecar，显式 SkipWeights，不复制原仓 ignored bundle。源码 733 文件 SHA 与工具版本在构建前冻结；sidecar 必须全文件 SHA 冻结后才运行 12 packaged。构建/测试实际结果后续追加于本节，未完成前 NOT_RUN。

本轮不升级父候选 head。隔离 _grant 补丁不是父候选交付，仍需固定 head、重新 Appointment Review；旧 DSH Review 不覆盖它。补充证据只能供复审，不能由 Owner 擅自将 blocked 改 approved。

### packaged 实际结案记录（仅本验证项）

构建 exit 0（PyInstaller 6.22.3 / Python 3.12.3），sidecar 全文件清单 `packaged-sidecar-frozen.json` 在首次测试启动前已写成；`packaged-final-postcheck.json` 证明第二次前后全部文件 SHA 不变。最终 `packaged-tests-fixed-head.log/json`：**12 passed / 0 failed / 0 ignored / 154 filtered，exit 0**，明确 M2RC1_PACKAGED=1，unset M2RC1_SRC_ROOT/M2RC1_PYTHON/RUST_TEST_THREADS。154 filtered 是本次仅选 packaged 的 source 用例，绝不视为它们通过。这里验证的是 e34 未改的 packaged 源码，非 fed 诊断补丁的发布版本。

首轮 packaged 同为12 passed/0 failed/exit0，但长时间运行器的head字段错误地记录诊断仓库fed，cwd实际是packaged-source/e34；完整原日志保留，`packaged-source-head-probe.json` 与构建输入manifest固定正确来源。修正运行器按cwd记录head后，用同一冻结bundle补跑12项，最终记录head=e34、无tracked diff。这次补跑只消除证据绑定歧义。无模型/安装包/真实GUI/产品release结论。

补充冻结验证器3个负向/防覆盖测试通过（防不同字节覆盖、缺失log、篡改hash）；_grant两测试在固定fed head再跑2 passed/exit0。旧日志环境字段的UNRECORDED、Core真实旧icacls错误码UNKNOWN与产品并发风险继续披露。父r1 blocked不因这些证据由Owner改判。

推荐下一步：DeepSeek Harness 按 APPOINTMENT 对诊断 head fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1 与当前 Canonical Evidence 执行只读独审；先决定测试隔离修复/真实并发压力验证及 Core 新环境诊断范围，再考虑父候选升级。当前不产生新父head，不push，不done，不改源main。

## DSH r1 approved 后的口径处置（追加说明优先）

DSH只批准fed诊断交付；不批准父候选升级/集成/发布。本段取代前文“待DSH执行”等运行状态。当前Review原字节不变，Appointment执行记录为workspace/review-disposition-r1/REVIEW_EXECUTION.json。原RESULT冻结副本仍在review-notes/RESULT.md，不覆盖；本文件是追加后的当前披露。

- **R-01**：父候选升级前必补。六份早期证据rust-default-parallel-r1/r2、registry-isolated-1..4由早期未冻结运行器生成，其原版本及SHA未保存。已知可见差异是缺tracked_changes字段；不能证明脚本仅有这一差异，不能用最终diagnose.py冒充当时脚本。argv/head/unset/计数由DSH独立核对。该书面限制声明提交父复审裁定，不补造旧版本。

- **R-02**：父候选升级前必补。DIAGNOSTIC_FREEZE仅42文件，不含3个DB二进制；DB字节由DIAG-50..52、core-r2-source-pins.json以及review-package-r2/PACKAGE_MANIFEST.json的core-db条目交叉覆盖。原freeze不扩写。

- **R-03**：父候选升级前必补。首轮packaged-tests.json/log的head字段无效，不可作为绑定依据。只以packaged-source-head-probe.json及packaged-tests-fixed-head.json/log、packaged-final-postcheck.json绑定实际e34。保留首轮错误字段，禁止自动选择首测记录作为canonical。

- **R-04**：governance-final-GIT-CLEAN-PUBLICATION-1与-DIAG-1的json/log共4件晚于原freeze，是未冻结辅助产物，不在原42/53项内；不得宣称原包已包含。此次不改这4件字节，不作为产品通过证据。

- **R-05**：冻结时观测原WAL为0B；该观测不说明此前未被其他进程打开。DSH核实WAL/SHM mtime为20:13:27，晚于主DB约19:32:24。主DB三处SHA一致；更早打开痕迹不改写为从未打开。

- **R-06**：75个git status M是stat缓存假阳性：索引保留CRLF检出stat、工作树现为LF且与HEAD字节一致；DSH以75/75 hash-object、空git diff HEAD/cached核实，不是75处源码改动。

- **R-07**：隔离仅指测试数据、APPDATA/LOCALAPPDATA/TEMP/TMP；六次Rust运行共享父Task cargo-target构建缓存。日志显示重新从DIAG source编译crate；不是完全独立构建缓存，也非复用测试结果。

- **R-08**：r2未记录tracked_changes，也未保存git diff断言输出；不能追溯补造。仅以DSH核实时间线（r2结束约20:31:25，sandbox修改20:31:44）及当前空diff作补证，不等于运行时完整脏树证明。后续运行器必须在RUN_HEADER保存断言exit/输出与运行器SHA。

- **R-09**：19个旧raw log的venv和部分env不可追溯，UNRECORDED为接受的已知限制；不改为已知值，不为补头复跑达到上限的Core原条件失败。

- **R-10**：mock只覆盖_grant原语；未覆盖PluginService到PLUGIN_HOOK_UNAVAILABLE端到端，也未断言icacls argv完整内容。OSError原样传播未变；mock错误码5不是旧机器真实grant返回码。

- **R-11**：packaged-build env中的M2RC1_SRC_ROOT指向DIAG source，但build_sidecar.ps1/spec忽略该变量，按脚本/spec位置定位packaged-source/src；实际输入以e34的733项SHA和module search path为准。不得称使用fed源码打包。

- **R-12**：旧review-package-r2内checkpoint.md/RESULT.md/HANDOFF.md是20:33:55冻结时快照，非当前父披露。同名父文件随后更新；最新披露读取主仓verification/GIT-CLEAN-PUBLICATION-1并继续读取本追加说明。原包是旧checks/log、envelope、禁止ID及DB冻结容器，不保证其内叙述文档为最新。

- **R-13**：freeze_review.verify仅检查manifest SHA/缺log/EXIT与标记，不验证envelope内部raw_sha256/metadata_sha256或body等于raw。本次不修改脚本；DSH已独立验证19/19 body等于raw，不能声称该能力由原验证器实现。

父证据交叉引用表在本次追加 PACKAGE_MANIFEST.json：DIAG-50..52 → 三库原SHA → 父已有DB条目；DIAG-53 → 旧review-package-r2/PACKAGE_MANIFEST.json → 三库包内条目。父要升级须重新Appointment精确新head，并由独立Reviewer裁定R-01–R-03及产品Gate，不能继承本次诊断approved。

后续决定：GIT-CLEAN-RUST-ISOLATION-1另冻并ready给Antigravity，DSH独审；从e34隔离仓库开始，不带fed补丁。GIT-CLEAN-CORE-ENV-2仅proposed：V2–V5标签未定义，先补具体变量及无系统ACL写入的可执行方案再释放。两项当前都没有新交付head；因此不得伪造绑定未知head的新Appointment，必须各自交付固定head后新任命，旧Review不沿用。
