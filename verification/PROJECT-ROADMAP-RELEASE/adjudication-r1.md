# Codex R1 finding adjudication — E1

R1 reviewed_head=657096b41042d7cfbbbee76baa856f96c28de24a，DSH为限定APPROVED（仅AC1–AC3文本，AC4未关闭），object_binding=NOT_VERIFIED。本裁决不释放任务；修正后的固定head将有界复审。

| finding | 裁决与证据 |
|---|---|
| P2-1 | 不同时间点而非错误对象：git-verification.log为初始base 0dcc94f3；verification.json.capture head 571d8970；R1 review head 657096b4。区间产品源码零差量；原始记录不改，REPORT追加时间口径。 |
| P2-1b | 本轮集合1525个可读文件、unknown=[]；CON未出现在该次git status集合，不推断其不存在；报告已明确条件策略与实测集合。真实INTERRUPTED命名文件按文件保留/hash。 |
| P2-2 | 补Owner对本worktree target/core-sidecar/core-sidecar/**的完整复制/hash权；build.rs固定路径与CARGO_TARGET_DIR区别已写明，禁止假目录与执行真实Core。 |
| P2-3 | 输入fixture固定git 92093792:verification/P04/deterministic_concurrent_sidecar.py，保存准确SOURCE_PIN；Owner只复制后适配新路径。 |
| P2-4 | cargo命令唯一显式排除real_core_sidecar_answers_startup_ping_on_fresh_catalog；该项NOT_RUN留P19/P20；其余synthetic/真实round_trip双调用/mutation/EOF/startup回收仍必须运行。 |
| P2-5 | P16/P17均增加DOC依赖，对应ARCH-DOC-REBASELINE AC6；P09/18/20分别对应AC1–3/4/5。 |
| P2-6 | 以权威来源规则消解：当前Plan持续冻结引用REPORT作为Gate输入，不使其独立维护状态，作者Task关闭不撤销Plan引用。现有Truth Map的Plan指定Task/evidence规则与Workspace的当前Gate/source pin保留规则适用；不存在因Task关闭可自动降级/移动的许可。未新增平行Plan。 |
| P2-7 | 正式登记ARCH-DOC-REBASELINE，proposed，Owner Codex/Reviewer DSH，AC/候选范围/消费者明确；执行base/worktree仍未冻结，不是第二READY。 |
| P2-8 | checker原始源码作为SOURCE_PIN；命令在live root准确执行，输出/argv/EXIT/context在workspace governance-r1.*，PASS/1 warning。明确不声称固定review worktree自包含可运行。root治理来源是未提交但已pin的用户内容，不捎带原路径。关闭后另跑最终检查并保留原始artifact。 |
| P2-9 | inputs/**和环境源记录统一SOURCE_PIN，结果/裁决CANONICAL；后续关闭全部文件逐项pin。 |

P3-6真实基础Python通过旧venv只读sys._base_executable实测，源exe hash已pin；P3-10明确单Cargo 1800s、同步等待≤30s。其它P3/P4保留backlog或关闭窗口元数据处理；不扩大产品切片。Root单独所有Git/hash验证不能冒充DSH执行；R2仍须独立明确结论。初次自动Git maintenance因既有坏checkpoint ref失败，提交成功；未主动运行gc/prune或修理引用，后续提交关闭自动maintenance。

