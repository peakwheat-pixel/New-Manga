# Codex 集成前验证 — 当前判别力记录

2026-10-24；Owner=ZCode，Codex代跑已授权验证并修正两处编译错误。固定实现head `3b035365682db0965bbde4b0a6113e3e000ae7e7`，parent/base `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。源main仍349e61faf，父候选仍e34/r1 blocked；不push、不done、不改系统ACL。

## 接收与修正

ZCode CLI 0.17.0、mode=edit，session `sess_8b77c6dc-c9ff-4fda-81dd-f353190d17e0`，实际exit0，有效返回为PARTIAL/BLOCKED；其Bash没有permission client，无法执行cargo/npm/git写操作。未升权、未改mode。原始交付文档/Task快照保存在workspace/review-package-r1/zcode-delivery，当前RESULT/HANDOFF中“未运行/无新head”属于该Owner阶段，以下Codex实际执行记录取代其运行状态。

Codex按既有Task授权代跑：离线npm ci/build均exit0；首轮未提交源码编译exit101，两处E0373（采样闭包借用局部sampler_started）。仅把两处计时变量移入闭包，第二轮编译exit0，源码前后SHA不变；随后只提交library_bridge.rs/main.rs/multichannel_stress_tests.rs三个文件，得到上述head。探针.git-probe-tmp.md保留未暂存，不按Owner建议删除；不进入交付commit。未改生产MAX/kill预算或断言阈值。

## 固定 head 实测

| 场景 | 实际结果 | 判定/限制 |
|---|---|---|
| cargo check --locked --offline | exit0 | 正常非test构建配置可编译；不是installer/release/GUI验收 |
| 默认并发source-r1 | 151 passed / 2 failed / 6 ignored / 12 filtered，exit101，11.53s | child_lock_contention…与real_core…startup_ping失败 |
| 默认并发source-r2 | 152 passed / 1 failed / 6 ignored / 12 filtered，exit101，11.53s | child_lock_contention…再次失败，达到同条件2次上限；不再重复 |
| child-lock单测试进程对照 | 1 passed / 170 filtered，exit0 | 新隔离变量；不能冒充默认全套通过，也未裁定生产缺陷已排除 |
| 真实Core：1/8/20 channel正常关停 | 三场景各1 passed，exit0 | 每channel ping成功；各自独立进程，各170 filtered；全局registry峰值均0，remaining=0 |
| 真实Core：20 channel并发取消/关停 | 1 passed，exit0 | 峰值0、remaining=0；不是饱和 |
| 故障注入：20阻塞管道 | 0 passed / 1 failed / 170 filtered，exit101，23.85s | peak_registry=0 <32，remaining=0；触界断言失败，AC3保持BLOCKED |
| packaged/安装包/模型/GUI | NOT_RUN | 未用本head新建冻结sidecar，不继承e34的12通过 |

计数：base共有166测试；本head新增5个独立压力测试（显式ignore，仅默认不执行），总171。默认过滤packaged12，故running159=153原可执行+1旧性能ignored+5新压力ignored。不能说“新增测试不改变默认计数”；6 ignored逐项原因是旧perf_chunk_request_digest_cost和上述5个专用压力场景。五压力场景此次均单独显式--ignored --exact运行；170 filtered只是精确选择，不计PASS。

默认两轮均unset RUST_TEST_THREADS/M2RC1_PACKAGED，无--test-threads=1；APPDATA/LOCALAPPDATA/TEMP/TMP均在本Task隔离。依赖编译缓存共享父Task cargo-target，crate从本Task源码重新编译；不是完全独立构建缓存。M2RC1_PYTHON与SRC_ROOT明确指向本机既有Python314和本Task源码，PYTHONUSERBASE只读恢复既有依赖。实际环境/完整argv/cwd/head/git diff断言/源码SHA/runner SHA/真实EXIT均见codex-validation-r1。ZCode两个ps1是未执行草案，不是实际canonical运行器；此次实际使用codex_verify.py，不能移植其未执行脚本的环境声明。

## 未解除的 Gate

- 原两个registry测试在两轮默认执行中均通过，但出现其他失败，**AC2不满足连续两次全套通过**。child-lock日志实际显示taskkill /F /T超过250ms且fallback reaper未确认wait；单独进程通过仅支持负载/隔离相关假设，不能将它写成已确认的纯测试问题或修改生产预算刷绿。
- private registry override与Box::leak的测试真实性、跨线程holder仍走全局的竞态是否充分解决，须DSH独审；当前不自批AC1。
- 故障注入的res.is_err()不能单独证明writer在OS write阻塞；当前指标标签blocked_request_timeout=true需Reviewer核查错误种类与注入有效性。serial Drop能否形成同时饱和、10ms采样能否捕获短暂占用亦未证明。**不放宽32、不把0<=32当饱和通过**；不为重复失败而盲跑同一场景。
- 实现只产生局部新head，不是父候选升级/main集成。当前Appointment只绑定3b03536；任何修订head需新Appointment。

## 下一步与恢复

按APPOINTMENT交DeepSeek Harness独立Review，优先裁定AC1真实性、child-lock负载失败以及饱和注入/观测缺口。Reviewer只写dsh-review-r1.md，不改实现/Task状态/系统ACL，不重跑已达上限的默认失败。得到具体裁定后，Codex决定是否在现有测试范围内交ZCode修订，或因需要生产逻辑变更另冻Task；当前不得越界修改生产kill语义。
