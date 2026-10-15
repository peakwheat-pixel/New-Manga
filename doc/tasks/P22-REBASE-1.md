---
id: P22-REBASE-1
title: 当前main基线的单通道往返串行化修复与确定性验收
kind: bugfix
governance_version: 2
status: ready_for_review
approval: user_authorized_next_implementation_slice_20261015_released_20261015
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-PAGE-NAV-PROJECTION-1, P08]
followup_of: P22
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
branch: codex/p22-rebase-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1
delivery_head: 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f
reviewed_head: null
integration_commit: null
integration_target: main
integration_status: not_started
dispatch_state: DISPATCHED
profile: ANTIGRAVITY_FOCUSED
revisions: {implementation: 1, test: 1, evidence: 1}
implementation_repairs_used: 1
max_implementation_repairs: 2
canonical_evidence_status: complete
resource_closeout_status: registered
evidence_dir: verification/P22-REBASE-1
---

# P22-REBASE-1

## 释放记录

- 释放时间：2026-10-15（Asia/Shanghai）；释放者=Active Coordinator `dsh`（epoch=5，lease=`264c2000541748298000f93fb25a52de`），经 `guarded-write` 将 `proposed` 改 `ready` 并就地登记 Plan（READY 节点）。
- 依据：`PROJECT-ROADMAP-RELEASE` AC3（范围/分支/worktree/Owner/Reviewer/路径/环境/判别力冻结）通过，且其 R2 有界复审为 `approved_with_conditions`（`object_binding=VERIFIED`，19/19 pin 一致）；用户 2026-10-15 授权释放一个下一实施切片。
- 冻结坐标：base=`0dcc94f3`；branch=`codex/p22-rebase-1`；worktree=`G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1`（已存在，HEAD=`0dcc94f3`）。
- 角色：Owner=Antigravity；Reviewer=DeepSeek Harness（`Reviewer != Owner`，且非本 Task 参与者）；Integrator=Codex。
- 返修预算：继承 P22 的 `implementation_repairs_used=1/2`，**不因本切片重置**；同 finding 最多一次 I2，不允许 I3。
- 派发边界：本 Task 已 `ready`，但**释放不等于自动派发**（见 PROJECT-ROADMAP-RELEASE 禁止范围）；须由 Coordinator `route-agent.py`/`preflight-agent.py` 确认 Owner 与独立 Reviewer 后，由 Owner 凭本文件认领启动。

## 派发记录

- 时间：2026-10-15（本地 19:05，Asia/Shanghai）；派发者=Active Coordinator `dsh`（epoch=5，lease=`264c2000541748298000f93fb25a52de`）。
- Owner：Antigravity（`agy` 1.3.5）；Coordinator 侧 PREFLIGHT=`PASS`，write-scope 全部落在本 worktree 内。
- 命令：`agy -p <Task 摘要+冻结范围> --project "New Manga" --output-format json --dangerously-skip-permissions`，cwd=本 worktree；代理显式注入 `HTTPS_PROXY/HTTP_PROXY=http://127.0.0.1:7890`（agy 不读 Windows 系统代理）。
- 原始输出：`G:/CODEX/New Manga.workspace/agent-output/antigravity/P22-REBASE-1/agy-owner-r1.json`（`response` + `conversation_id`）与同名 `.err.log`。
- 状态：Owner（Antigravity）已完成实现、单测、Mutation 证据记录与 Handoff 文档。

## 来源与目标

由本轮用户授权和PROJECT-ROADMAP-RELEASE冻结。P22代码来源92093792与R10交付链4a707db8、P04交付faea1a2c均非当前main祖先；原代码/测试没有运行闭环。目标只修复现存StdioLibraryChannel::round_trip在并发时stdin/stdout分段锁导致的响应归属风险，基于当前main重做最小移植与运行验收，不整枝合并旧分支，不重做旧R3–R10文案返修。不得以新ID重置既有返修预算：继承P22的R1→R2一次源码返修，implementation_repairs_used=1/2；本切片移植既有修复不重置预算，后续同finding最多一次I2。触发旧finding时引用原lineage交Codex收敛，不另建任务刷新计数。

## Acceptance Criteria

- [x] AC1：单实例的一次request write/flush与对应response read受同一事务锁保护；所有构造路径初始化锁；不同实例保持独立，原typed错误/EOF/stop/drop与startup ping回收语义保留；不改wire shape或request_id合同。
- [x] AC2：确定性测试必须实际调用生产round_trip，双调用方、不同payload/响应，以channel/barrier等同步强制竞争并核各自响应归属；不能只测独立锁helper、sleep或概率循环；不得ignore测试。提供去掉事务锁时失败的mutation证据与单实例通过证据，等待均有上限，失败清理自有子进程。
- [x] AC3：定向回归覆盖EOF/写读失败或现有对应测试、startup ping timeout停止回收，保持原行为；本切片获准的library_bridge测试集合通过；唯一显式排除real_core_sidecar_answers_startup_ping_on_fresh_catalog（会启动真实Core），其结果为NOT_RUN，留P19/P20许可环境验收。现有synthetic startup timeout/own-child回收测试必须运行；新增并发回归不得ignore或skip。P04常量精确断言与完整生产桥接并发验收留给P04，不在本切片假称完成。
- [ ] AC4：输入源/环境/源零写与范围验证、固定head独立DSH Review、Codex集成后复跑及资源closeout完成后才done；P04仍blocked直至其自身AC完成。新锁功能获独立审查，R10 Handoff批准不沿用。

## 允许修改范围

- apps/desktop/src-tauri/src/library_bridge.rs：仅per-channel串行化、所有构造初始化、必要test-only同步钩子和对应测试；先查全部round_trip/构造/startup/Drop调用方。
- verification/P22-REBASE-1/**：自有确定性Python sidecar/测试运行脚本、运行与mutation证据；只读输入固定为git 92093792ba0bc653f9423dda2486d558226caf86:verification/P04/deterministic_concurrent_sidecar.py；准确快照/hash见verification/PROJECT-ROADMAP-RELEASE/source-manifest.json。Owner复制到本切片新路径后适配；若改为全新最小echo fixture需说明映射，不写旧证据。
- 本worktree的apps/desktop/src-tauri/target/core-sidecar/core-sidecar/**：Owner仅从冻结只读来源复制完整bundle并逐项hash，不修改内容、不执行真实Core；该ignored资源是build.rs按CARGO_MANIFEST_DIR要求的输入，不受CARGO_TARGET_DIR重定向。
- 本Task与doc/handoffs/P22-REBASE-1-*.md。
- 自有workspace下builds/P22-REBASE-1、task-envs/P22-REBASE-1、temp/P22-REBASE-1、agent-output/antigravity/P22-REBASE-1；先冻结manifest再执行。

## 禁止范围

不改main.rs、build.rs、Cargo.toml/Cargo.lock、前端、Python Core、IPC/schema/业务契约、依赖或模型；不写用户源文件/真实数据库/旧worktree/旧P04/P22原始证据；不合main/push。不运行GUI/NSIS/Sandbox、profile/registry/ACL API/进程枚举/模型，不重跑P02/X6。若必须扩大文件范围，先交Codex裁决，不擅改。

## 执行授权与环境

本Task的ready释放单独授权上述有界Cargo单测及测试Python子进程，不是沿用旧P02 Build许可，也不解除旧Technical Gate/13项缺失。仅使用自有复制/新建scratch env；不运行真实Core/用户数据库。CARGO_TARGET_DIR=G:/CODEX/New Manga.workspace/builds/P22-REBASE-1/cargo-target；CARGO_HOME、TEMP/TMP、PYTHONPYCACHEPREFIX均在自有task-envs/P22-REBASE-1。M2RC1_PYTHON使用独立Python3.12 venv；真实基础解释器见本轮environment-sources.json中kind=base_interpreter项（从旧venv的sys._base_executable实测）；不可把venv launcher当独立安装。创建后重验exe/version/hash、pyvenv.cfg与sys.base_prefix。公开Cargo锁定依赖可在该cache按--locked下载，不修改lock；禁解析凭据/私有registry。

build.rs所需sidecar资源只从G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/core-sidecar/core-sidecar只读来源复制到本worktree期望路径。不得创建空目录/假exe绕过build.rs；复制前冻结完整相对路径/size/hash清单、复制后逐项一致；测试不执行该真实Core bundle。源不可用/散列不符则测试NOT_RUN并交Codex，不能冒称READY即前置预检已PASS。该步骤是本Task AC4执行前置，不要求重跑完整打包。

## 测试要求

在本worktree/apps/desktop/src-tauri：cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog（包括新增并发回归；唯一授权排除项如上）；mutation在自有temp副本执行同一判别用例，去锁必须非零exit且不是编译/环境错误。每条Cargo命令wall timeout=1800s；单测试同步等待/测试sidecar响应超时≤30s；超时FAIL并清理本Task自有子进程，不枚举或结束未知进程。预先cargo test --locked library_bridge::tests -- --list保存筛选集，分别统计passed/ignored/filtered，明列该生产Core集成项NOT_RUN，不宣称完整集成套件PASS。脚本记录shell、toolchain/Python版本、commit、argv/env、stdout/stderr/EXIT、passed/skip/timeout与所有输入hash。启动前先Owner PREFLIGHT；无真实调用不标in_progress。

## 依赖、风险与阻塞

依赖PAGE-NAV/P08已集成；不依赖P04 done，无环。治理后继commit相对base仅文档/证据变化，进入前由Codex固定source_tree与launch HEAD。旧P22/P04可达性/原审查范围的证据见PROJECT-ROADMAP-RELEASE。原Task未闭合事实不改写。架构文档Gate仍阻断P09；不阻断本既有IPC根因修复。

## 交付与运行记录

- 2026-10-15：Owner（Antigravity）认领实施。
- 环境：已建立专属 Python 3.12.3 venv，并逐项验证 5610 个 sidecar bundle 文件哈希。
- 实现：在 `apps/desktop/src-tauri/src/library_bridge.rs` 中为 `StdioLibraryChannel` 引入事务互斥锁 `transaction_lock: Mutex<()>`，两处构造路径初始化完成，`round_trip` 读写整段处于同一事务锁保护下，并提供测试局部钩子。
- 运行：`cargo test --locked library_bridge::tests -- --test-threads=1 --skip real_core_sidecar_answers_startup_ping_on_fresh_catalog` 运行通过（11 passed, 0 failed, 1 NOT_RUN, EXIT=0）。
- Mutation：在 `temp/P22-REBASE-1/mutation` 副本去除事务锁，运行判别用例精确触发锁竞争探测断言 panic，退出码 101，编译成功且无环境错误。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVD-P22-REBASE-1-PREFLIGHT-ENV | AC4 | verification/P22-REBASE-1/preflight-env.json | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | e8863315bea027fa90d9e0a9eebd00b7b94325a917494585079e34a773bbea69 | primary |
| EVD-P22-REBASE-1-SIDECAR-MANIFEST | AC4 | verification/P22-REBASE-1/sidecar-bundle-manifest.json | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 887b3e5f1e0c859be23e55f2b87dcdf8ff06f4453f52783140a6335107ca0a56 | primary |
| EVD-P22-REBASE-1-SIDECAR-VERIFY | AC4 | verification/P22-REBASE-1/sidecar-bundle-verification.json | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | e3fb849f376aacf70eebf98ab9a8fc97e198107c51537a3fdee32db1e0288f25 | primary |
| EVD-P22-REBASE-1-TEST-LIST-OUT | AC3 | verification/P22-REBASE-1/cargo-test-list.stdout.log | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 99e7248d783a4e170f20653243f0b9aa35368b910425f4a986c77c80a4c333e1 | primary |
| EVD-P22-REBASE-1-TEST-LIST-EXIT | AC3 | verification/P22-REBASE-1/cargo-test-list.exit | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9 | primary |
| EVD-P22-REBASE-1-TEST-RUN-OUT | AC2/AC3 | verification/P22-REBASE-1/cargo-test-run.stdout.log | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 4935f64a3cbc0ed266249b3d9712092c25b6f11292a2dd433e3824c74c9deb02 | primary |
| EVD-P22-REBASE-1-TEST-RUN-EXIT | AC2/AC3 | verification/P22-REBASE-1/cargo-test-run.exit | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9 | primary |
| EVD-P22-REBASE-1-TEST-SUMMARY | AC2/AC3 | verification/P22-REBASE-1/test-run-summary.json | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 1c3b141edb387bda2e06fa7ecf424a25b0643ec0b78991b8eaacf3089f6834cf | primary |
| EVD-P22-REBASE-1-MUTATION-REPORT | AC2 | verification/P22-REBASE-1/mutation-report.json | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 9ab20a0627ebe387f0b12203d701493d88026d807ba22c9d6ac1f162afb7e51a | primary |
| EVD-P22-REBASE-1-MUTATION-EXIT | AC2 | verification/P22-REBASE-1/mutation-test.exit | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 16dc368a89b428b2485484313ba67a3912ca03f2b2b42429174a4f8b3dc84e44 | primary |
| EVD-P22-REBASE-1-MUTATION-STDERR | AC2 | verification/P22-REBASE-1/mutation-test.stderr.log | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | ff877a219a05a4d2398c710ab916c3b431c479010aea624d619a73a4477c9f0d | primary |
| EVD-P22-REBASE-1-DIAGNOSTIC-JSONL | AC2 | verification/P22-REBASE-1/diagnostic_p22_42432_1792063346986.jsonl | 61c806c9e17d3c756b15b328dfc95f5aa5a6c72f | 0158661fed32b574f9abe378d992c7a11295f359fcf7d44417e6ee444b7e53ac | primary |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| core-sidecar bundle | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/core-sidecar/core-sidecar | PRESERVE_REFERENCED | apps/desktop/src-tauri/target/core-sidecar/core-sidecar | 887b3e5f1e0c859be23e55f2b87dcdf8ff06f4453f52783140a6335107ca0a56 | 5610/5610 verified identical (status: VERIFIED_IDENTICAL, mismatches: 0) |
| base_interpreter | C:\Users\49745\AppData\Local\Programs\Python\Python312\python.exe | READ_ONLY_SOURCE | N/A | 15b41a488c356c0e331facdea6c836a6cec021f12d5fde9844e7ca4a1aa0361a | Python 3.12.3 verified identical |
| task_venv | C:\Users\49745\AppData\Local\Programs\Python\Python312\python.exe | ACTIVE_TASK_ENV | G:/CODEX/New Manga.workspace/task-envs/P22-REBASE-1/venv | e8863315bea027fa90d9e0a9eebd00b7b94325a917494585079e34a773bbea69 | Dedicated isolated venv verified |
| deterministic_concurrent_sidecar.py | verification/PROJECT-ROADMAP-RELEASE/inputs/verification/P04/deterministic_concurrent_sidecar.py | PRESERVE_REFERENCED | verification/P22-REBASE-1/deterministic_concurrent_sidecar.py | 6923586b2b409c31fff9d7f2e4c6b7afa11ca4f1caa43b70336cefcdeb441286 | Byte-identical copy verified |

## Closeout Record

Owner Antigravity 已完成本切片实施与交付物固化，等待 DeepSeek Harness 独立复审与 Codex 集成收口。

## R1 独立 Review 记录

- reviewed_head=`5181facbb095be8c7a45924b699d4e3a481aeb50`；reviewer=DeepSeek Harness；decision=`approved_with_conditions`。
- AC1–AC3：PASS。
- 独立复跑：EXIT=0，11 passed / 0 failed / 0 ignored / 53 filtered。
- 独立 mutation 复现：EXIT=101，按 Review 记录确认触发并发响应错配断言。
- Findings 摘要：F1 Task add/add 集成风险，已采用分支侧并保留释放/派发记录；F2 Owner 原运行日志对应提交前的 0dcc94f 源树，Review 在交付 head 上独立复跑通过，时间口径在集成证据中说明；F3 `registered` 非规范资源状态，closeout 改为 `complete`；F4 Handoff `draft` 待集成转为 `delivered`；F5 sidecar manifest 约 1.08 MB/5610 项，记录为非阻塞体量项。
- Review 路径：`verification/P22-REBASE-1/dsh-review-r1.md`。
