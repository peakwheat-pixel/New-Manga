---
id: P22-REBASE-1
title: 当前main基线的单通道往返串行化修复与确定性验收
kind: bugfix
governance_version: 2
status: proposed
approval: user_authorized_next_implementation_slice_20261015_pending_release_review
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-PAGE-NAV-PROJECTION-1, P08]
followup_of: P22
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
branch: codex/p22-rebase-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1
delivery_head: null
reviewed_head: null
integration_commit: null
integration_target: main
integration_status: not_started
dispatch_state: NOT_DISPATCHED
profile: ANTIGRAVITY_FOCUSED
revisions: {implementation: 0, test: 0, evidence: 0}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P22-REBASE-1
---

# P22-REBASE-1

## 来源与目标

由本轮用户授权和PROJECT-ROADMAP-RELEASE冻结。P22代码来源92093792与R10交付链4a707db8、P04交付faea1a2c均非当前main祖先；原代码/测试没有运行闭环。目标只修复现存StdioLibraryChannel::round_trip在并发时stdin/stdout分段锁导致的响应归属风险，基于当前main重做最小移植与运行验收，不整枝合并旧分支，不重做旧R3–R10文案返修。不得以新ID重置既有返修预算：原P22冻结交付属首次移植输入；本切片仅首次当前基线适配I0，返修最多I1/I2，触发旧finding时引用原lineage交Codex收敛。

## Acceptance Criteria

- [ ] AC1：单实例的一次request write/flush与对应response read受同一事务锁保护；所有构造路径初始化锁；不同实例保持独立，原typed错误/EOF/stop/drop与startup ping回收语义保留；不改wire shape或request_id合同。
- [ ] AC2：确定性测试必须实际调用生产round_trip，双调用方、不同payload/响应，以channel/barrier等同步强制竞争并核各自响应归属；不能只测独立锁helper、sleep或概率循环；不得ignore测试。提供去掉事务锁时失败的mutation证据与单实例通过证据，等待均有上限，失败清理自有子进程。
- [ ] AC3：定向回归覆盖EOF/写读失败或现有对应测试、startup ping timeout停止回收，保持原行为；完整library_bridge测试集通过且skip原因逐项分列。P04常量精确断言与完整生产桥接并发验收留给P04，不在本切片假称完成。
- [ ] AC4：输入源/环境/源零写与范围验证、固定head独立DSH Review、Codex集成后复跑及资源closeout完成后才done；P04仍blocked直至其自身AC完成。新锁功能获独立审查，R10 Handoff批准不沿用。

## 允许修改范围

- apps/desktop/src-tauri/src/library_bridge.rs：仅per-channel串行化、所有构造初始化、必要test-only同步钩子和对应测试；先查全部round_trip/构造/startup/Drop调用方。
- verification/P22-REBASE-1/**：自有确定性Python sidecar/测试运行脚本、运行与mutation证据；复用旧sidecar设计，拷入本切片新路径后改，不写旧证据。
- 本Task与doc/handoffs/P22-REBASE-1-*.md。
- 自有workspace下builds/P22-REBASE-1、task-envs/P22-REBASE-1、temp/P22-REBASE-1、agent-output/antigravity/P22-REBASE-1；先冻结manifest再执行。

## 禁止范围

不改main.rs、build.rs、Cargo.toml/Cargo.lock、前端、Python Core、IPC/schema/业务契约、依赖或模型；不写用户源文件/真实数据库/旧worktree/旧P04/P22原始证据；不合main/push。不运行GUI/NSIS/Sandbox、profile/registry/ACL API/进程枚举/模型，不重跑P02/X6。若必须扩大文件范围，先交Codex裁决，不擅改。

## 执行授权与环境

本Task的ready释放单独授权上述有界Cargo单测及测试Python子进程，不是沿用旧P02 Build许可，也不解除旧Technical Gate/13项缺失。仅使用自有复制/新建scratch env；不运行真实Core/用户数据库。CARGO_TARGET_DIR=G:/CODEX/New Manga.workspace/builds/P22-REBASE-1/cargo-target；CARGO_HOME、TEMP/TMP、PYTHONPYCACHEPREFIX均在自有task-envs/P22-REBASE-1。M2RC1_PYTHON使用独立Python3.12 venv；基础Python exe源见本轮environment-sources.json，创建后重验exe/version/hash。公开Cargo锁定依赖可在该cache按--locked下载，不修改lock；禁解析凭据/私有registry。

build.rs所需sidecar资源只从G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/core-sidecar/core-sidecar只读来源复制到本worktree期望路径。不得创建空目录/假exe绕过build.rs；复制前冻结完整相对路径/size/hash清单、复制后逐项一致；测试不执行该真实Core bundle。源不可用/散列不符则测试NOT_RUN并交Codex，不能冒称READY即前置预检已PASS。该步骤是本Task AC4执行前置，不要求重跑完整打包。

## 测试要求

在本worktree/apps/desktop/src-tauri：cargo test --locked library_bridge::tests -- --test-threads=1（包括新增并发回归）；mutation在自有temp副本执行同一判别用例，去锁必须非零exit且不是编译/环境错误。脚本记录shell、toolchain/Python版本、commit、argv/env、stdout/stderr/EXIT、passed/skip/timeout与所有输入hash。启动前先Owner PREFLIGHT；无真实调用不标in_progress。

## 依赖、风险与阻塞

依赖PAGE-NAV/P08已集成；不依赖P04 done，无环。治理后继commit相对base仅文档/证据变化，进入前由Codex固定source_tree与launch HEAD。旧P22/P04可达性/原审查范围的证据见PROJECT-ROADMAP-RELEASE。原Task未闭合事实不改写。架构文档Gate仍阻断P09；不阻断本既有IPC根因修复。

## 交付与运行记录

NOT_DISPATCHED；无实现、无Cargo/产品测试运行。本Task获审后由Codex将proposed改ready并登记Plan；下一Owner凭本文件认领，不对旧Owner工作区写入。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

Owner固定交付进入Review前填写。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

Owner登记并由Codex关闭；旧资源全部PRESERVE_REFERENCED/PRESERVE_UNKNOWN，不删除。

## Closeout Record

尚未实施；不得预填完成或清理。
