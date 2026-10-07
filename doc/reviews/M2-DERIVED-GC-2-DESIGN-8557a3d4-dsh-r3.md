# M2-DERIVED-GC-2-DESIGN 非作者限定复审（r3）— 结论：**changes_requested**

```yaml
task_id: M2-DERIVED-GC-2-DESIGN
reviewer: DeepSeek Harness（非作者；设计作者=Codex）
author: Codex
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
reviewed_head: 8557a3d4162d00dc7a985ede0dabda22809f60fd
delivery_head: 73e70536b9c5c3525607311892a44ec055805902
r2_reviewed_head: 3a6846758ebdb18e3ee696e0c1410aa698e43225
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r3
branch: codex/m2-derived-gc-2-design-review-r3
decision: changes_requested
findings: 0×P0 / 0×P1 / 1×P2 / 0×P3 / 4×P4(advisory)
scope: 仅复核 r2 剩余 R2-01(P2) 与 A1/A2/A3，及 r3 新增 bootstrap 段；r1 C1/C3/C4/C5/F6/F7 已 r2 闭合，不复审
dispatch: 真实 CLI 派发（本会话无法独立验证上游通道）｜web_visibility=unverified
```

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **changes_requested** —— R2-01 的**子项①（锁定位顺序循环）已闭合**；子项②（授权/入口覆盖）**部分闭合**，遗留 1 个 P2（R3-01） |
| 为何不是 approve_with_conditions | 缺口不是"Codex 治理/集成/后继恢复点准备未做"，而是**设计文本内尚未冻结的覆盖判据**：受支持入口的"首次绑定/迁移执行体"与受影响入口/测试清单。按用户口径，设计判据缺失必须如实 changes_requested |
| 是否安全倒退 | **否**。"未绑定一律拒绝"是 fail-safe，不含误删授权；R3-01 影响的是**可用性/验收可执行性与范围边界**，因此定 P2，不上 P0/P1 |
| r3 修订质量 | **高**：r2 建议 (b) 被逐字落实为可执行两段式；A1/A2/A3 三个 P4 全部按 r2 要求冻结落点；O-R2-1/2 闭合 |
| Architecture 面 | **PASS**（分层/依赖方向/持久化边界/零 wire/零命令表扩张/F-05 import 边界保持；删除仍以核验句柄为准） |
| Verification 面 | 设计范围内 **PASS（静态，executed）**；命令级复跑 **BLOCKED**（shell 不可用）；native/租约/回收/产品回归 **NOT_RUN**（后继 Gate，非设计缺陷） |

## 1. 方法与能力限制（如实）

- 本会话 `pwsh` 在**启动阶段**即失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DERIVED-GC-2-DESIGN-review-r3)`。**未**执行任何 `git`/`check_design.py`/pytest/cargo，**未**做双进程租约实验，**未**请求提升（无审批通道），**未**伪造任何 PASS。命令级：**BLOCKED**。
- 替代证据（我本人独立只读读取，非作者摘要）：
  - `.git/worktrees/DERIVED-GC-2-DESIGN-review-r3/HEAD` → `ref: refs/heads/codex/m2-derived-gc-2-design-review-r3`；同目录 `logs/HEAD` 两行均指向 `8557a3d4…`（本 worktree 创建即固定，无后续提交）。
  - `.git/worktrees/DERIVED-GC-2-DESIGN/logs/HEAD:1-9` → `69d7cc08 → a35915c2 → 8dd88c56 → 4a930c61 → be779967 → 3a684675 → 73e70536 → 8557a3d4`（末两条信息为 `freeze safe catalog lease bootstrap sequence`、`pin catalog bootstrap design recheck handoff`）；`.git/refs/heads/codex/m2-derived-gc-2-design` = `8557a3d4…`。
  - `.git/logs/HEAD:877-879` → `32f9b932 → ab4b7c11 → 69d7cc08 → 27cc01a1`，且**无** `8557a3d4/73e70536/3a684675/be779967`（r3 head 未并入 main）。
  - 逐行只读真实代码：`catalog_store.py`、`catalog_loader.py`、`acceptance_bridge.py`、`core_service.py`(main/_run_startup_gc)、`render_preview.py`、`host_bridge.py`、`library_bridge.rs`、`core_bridge.rs`、`main.rs`(启动排序/命令表/轮换)、`ac1_bridge.rs`，以及 `verification/M2-RC2/run_e2e.py`、`verification/M2-AC1/run_e2e.py`、`packaging/{m2ac5,release-gate}` runner、受影响测试。
- 本报告**未修改任何文件**、未实施、未合并、未删除任何 worktree/历史。
- 未采信项：作者 `design-check-r3.log` 的 `EXIT=0`、`review-disposition.md` 的自我描述、r2 报告对测试性质的转述（见 R3-A4，其中一条已被我实测推翻）。

## 2. 固定点独立核验

| 事实 | 我的独立来源 | 判定 |
|---|---|---|
| `reviewed_head = 8557a3d4` | review-r3 worktree `HEAD` + `logs/HEAD` | **核验成立** |
| `delivery = 73e70536` 是"修订设计"提交，`8557a3d4` 为其 Handoff/log 入库提交 | design worktree reflog:8-9 | **核验成立** |
| `base = ab4b7c11` = release `69d7cc08` 之父 | 主 `.git/logs/HEAD:877-878` | **核验成立** |
| 当前工作区内容 = `73e70536` 设计文本 | §2.3 两段式新文本存在且 r2 报告的旧 §2.3 文本已不存在 | **核验成立（推断，见下行）** |
| 工作区干净 / 命令级复跑 / SHA256 复算 | —— | **BLOCKED（无 shell；不采信作者自述数字）** |

## 3. R2-01 逐项 disposition

| r2 子项 | r3 落点（`73e70536` 树内文件:行） | 我的独立核验 | 判定 |
|---|---|---|---|
| **① 锁定位顺序循环**（"连接前取租约" vs "从 catalog 表读删除域"不可同时成立） | §2.3:68 冻结两段式：拒绝 reparse/固定 catalog 文件 identity → **URI `mode=ro&immutable=1` 只读 bootstrap 仅读单行 namespace**（不执行 `_SCHEMA`/DDL/PRAGMA 写/WAL checkpoint/业务查询、禁止创建缺失 DB）→ **关闭连接** → 绑定仅作**不可信 hint** → 取对应 derived 锁 → **业务连接重读并验证** namespace/version/catalog+derived identity 全一致 → 才初始化允许表并服务；缺行/旧 WAL 值/替换/半绑定/任一错误→拒绝，**不回退无租约**；并明示"只读定位不 issue/publish/删文件，故尚未取得租约不构成资源读写窗口" | 循环确实被打破：§2.3:62 的"连接前取租约"被 :64 限定为"业务连接/初始化表/任意业务读写前"，并把定位例外显式排除在业务访问之外；`catalog_store.py:53-58` 现状（`__init__` 直连 + 跑 `_SCHEMA`）证明该改造落在 `catalog_store.py`（**在 §5 allowed_paths**）；自锁规避见 §2.3:64（Core 已持独占时 store 借用，不自行取共享）；降级窗口不发业务见 §2.3:74 | **闭合** |
| **② 授权/入口覆盖缺口**（`catalog_loader.py:79`、`acceptance_bridge.py:411` 点名须覆盖，却不在 allowed_paths） | §2.3:66 仍点名两个入口"必须由同一构造入口覆盖，不在 CLI 各复制锁实现"；§2.3:70 明确"loader/acceptance_bridge **无需新增 root 参数**，**已绑定时**由 store bootstrap 覆盖，**未绑定时安全拒绝**"；§5:157-166 allowed_paths 仍**不含**这两个文件；§6:184 G3 增 bootstrap 判别（"只有 --db 的 loader/acceptance_bridge 能在**已绑定** catalog 定位并取得同一共享锁"） | "不改这两个文件也可覆盖（store 内建 bootstrap）"在**已绑定**前提下成立，r2 指出的字面授权冲突已消解。但"**谁在何时完成首次绑定**"没有任何落点：`catalog_loader.py:66-83` CLI 只有 `--db`；`acceptance_bridge.py:406-411,615` 只读 `M2RC2_CATALOG_DB`（**不读** `M2RC1_DERIVED_ROOT`）；`ac1_bridge.rs:57-74` 子进程仅继承宿主 env；`main.rs:745` 在 `M2AC1_TEST_MODE=1` 时 `is_production=false` → **不启动 production Core**；而既有验收入口都在**新库**上先 seed：`verification/M2-RC2/run_e2e.py:114-142`（`catalog_db.unlink(missing_ok=True)` 后 loader seed 5 行）、`verification/M2-AC1/run_e2e.py:177-189`（`M2RC2_CATALOG_DB=root/catalog.sqlite` 新库 + `M2RC1_DERIVED_ROOT`）、`packaging/m2ac5/run_clean_start_e2e.py:280-307`、`packaging/release-gate/run_release_gate.py:1035-1050`（loader seed lab root） | **部分闭合 → R3-01(P2)** |

## 4. A1 / A2 / A3 与 O-R2-1/2/3 disposition

| 项 | r3 落点 | 我的独立核验 | 判定 |
|---|---|---|---|
| **R2-A1** WebView 不得透传退役位 | §2.2:50（"前端没有调用该操作的 Tauri 命令/ACL"）；§6:184 G2 补充"WebView 可达 `revoke_resource_refs` 仍调用普通 revoke，不携 `retire_preview`；失败撤销新 key 同样不携该位"；§5:162"不改 public Tauri 命令表" | `main.rs:1012-1038` 15 条 production 命令表含 `revoke_resource_refs`；`main.rs:462-465` 其路由到裸 `revoke_resource`；`core_bridge.rs:94` trait 现签名无位 → 需要窄追加而非扩旧签名。设计四句否定判据齐备 | **闭合**（残留见 R3-A1） |
| **R2-A2** 启动握手 seam | §2.3:80 命名 `wait_startup_ping`：仅在尚未交给 AppState 的 `StdioLibraryChannel` 上协调**一次**现有 ping 与 30s 等待（`std::thread`/`mpsc`，无新依赖）；不改正常 `round_trip` 签名/序列化/读锁语义；超时**先 kill/wait 本次自有 child** 促 stdin/stdout 关闭=EOF，再回收该次读取 worker/读锁/句柄；**协调器持 child 锁执行退出，不等 stdout 锁制造死锁**；无法证明 worker/句柄退出即 **BLOCKED**，不把挂起 worker 交给服务，无通用 RPC 调度器 | `library_bridge.rs:188-193`（`child`/`stdin`/`stdout` 三个独立 `Mutex<…>`，`stdout=Mutex<BufReader<ChildStdout>>`）、`:294-302`（持 stdout 锁的 `read_line` 无 deadline，r2 主张成立）、`:320-334`（`wait_timeout_or_kill` 先例）、`:336-353`（`Drop` 走 `core.shutdown`+`wait_timeout_or_kill(5s)`）。设计描述与该结构可落地且锁序自洽 | **闭合**（残留见 R3-A2） |
| **R2-A3** mark 的 `busy_timeout=0` 落点 | §2.2:56（独立短事务 `busy_timeout=0`、零重试）；§2.2:58 冻结为**独立 SQLite 连接**：既存 catalog URI `mode=rw`、`timeout=0`、不跑 `_SCHEMA`、不改 journal/WAL/schema、不创建缺失 DB、一次短事务、`finally` 关闭、**借用 store 既有生命周期租约**、**不改 publisher/store 共享连接 busy 策略** | `catalog_store.py:53-58` 单连接 + `threading.Lock`、`sqlite3.connect` 默认 5s busy（无显式 `timeout`）→ 若在共享连接上改 PRAGMA 会污染 publish 路径，独立连接是正确选择；"借用租约"与 §2.3:64（host_bridge 全生命周期共享租约）自洽 | **闭合**（残留见 R3-A3） |
| **O-R2-1** K5 限定 | §4:125"managed-read-only…pages 原图、模型｜**live-preview sweep 必留**…既有第一刀 orphan/dead-row 另按原授权、同安全窗口运行，不扩大 pages 回收" | 文本核对成立；且 `render_preview.py:143-155` 只遍历 `previews/`、`pages/`，证明 §2.3:62 把 `.preview-lifecycle.lock` 放在 **derived root 根目录**（不在清理目录）不会被第一刀删除 | **闭合** |
| **O-R2-2** 命名 | §2.1:39"**拟议来源表字段**，逐字保存既有 `revision.managed_path` 与 `outcome.managed_path` 相同的值；**不是重命名主产品字段**，只用于证明，永不 unlink" | 澄清到位 | **闭合** |
| **O-R2-3** 测试名单 | §5:165 补列 `tests/m2_resource_channel/test_catalog_authority.py`、`test_bridge_and_thresholds.py` | file-backed 直接构造点确已覆盖：`test_derived_gc.py:29,114`、`test_page_resource_resolve.py:81,141`、`test_rc4_stdio_render_preview.py:175`、`test_catalog_authority.py:63-72`。但 `test_bridge_and_thresholds.py:26,38,76` 实为 `:memory:`（r2 转述有误、r3 沿用了该描述）；且**真正受新默认影响的 `tests/m2_acceptance/test_acceptance_loop.py:36-47,174` 未列** | **部分闭合 → R3-A4 / 并入 R3-01** |

## 5. Findings（本轮）

| ID | 级别 | 位置 | 触发与影响 | 证据 | 修订要求 |
|---|---|---|---|---|---|
| **R3-01** | **P2** | 设计 §2.3:66/70/72、§5:157-166、§6:184；`src/infrastructure/resource_channel/catalog_loader.py:66-83`；`src/bootstrap/acceptance_bridge.py:406-411,615`；`apps/desktop/src-tauri/src/ac1_bridge.rs:57-74`；`apps/desktop/src-tauri/src/main.rs:745` | **r2 R2-01 的残漏：受支持入口的"首次绑定/迁移"没有可执行路径。** 设计冻结"无绑定=默认拒绝写/拒绝服务"+"loader/acceptance 不加 root 参数"+"首次绑定必须在受控窗口"，但**未定义谁来执行首次绑定**，也未把执行体写入 allowed_paths。后果：既有生产前验收入口全部是"**新库 + loader 先 seed**"或"ac1 模式无 production Core"结构——(a) `verification/M2-RC2/run_e2e.py:114-142` 先 `unlink` 再 loader seed 新 catalog；(b) `verification/M2-AC1/run_e2e.py:177-189` 在 `M2AC1_TEST_MODE=1` 下新库启动，而 `main.rs:745` 该模式不启 production Core（唯一有 derived root 且被设计承认可绑定者）；(c) `packaging/m2ac5/run_clean_start_e2e.py:280-307`、`packaging/release-gate/run_release_gate.py:1035-1050` 同样以 packaged `catalog_loader.exe` seed 新 lab root；(d) `tests/m2_acceptance/test_acceptance_loop.py:36-47,174` 直接以新 `catalog.sqlite` 构造 `AcceptanceBridge` 并期待 `catalog_pages` 成功。这些在 r3 设计下都会**安全拒绝**，即设计边界内这些 Gate/测试**不可执行**，而 `verification/**`、`packaging/**`、`tests/m2_acceptance/**` 均不在 §5 allowed_paths；§2.3:66 末句"先补 Task 范围"正是 r2 已判定为"把参与方判据推迟到实现期"的同一形态。**安全方向未倒退**（拒绝而非误删），故非 P0/P1。 | `catalog_loader.py:66-83`；`acceptance_bridge.py:615`；`ac1_bridge.rs:57-74`；`main.rs:711-722,745-767`；四个 runner 与测试行号如上；`src/bootstrap/core_service.py:1680-1689`（唯一已有 derived root 的装配入口） | 二者同时冻结：**(a)** 在 §2.3 明示"**首次绑定/迁移登记的执行体**"= production Core（`core_service.main`，已有 `M2RC1_DERIVED_ROOT`）为唯一自动创建者；对无 production Core 的 lab/打包/验收流程给出显式受控初始化路径（由 runner/测试先以显式 derived root + 受控保护上下文完成绑定，之后 loader/acceptance 才按"已绑定"路径工作），并同步 §5 allowed_paths（补列 `catalog_loader.py`/`acceptance_bridge.py`，或明文"这两文件不改、初始化仅经 store 初始化 API 由外来调用方触发"并点名调用方）；**(b)** 把 §2.3:70"受控入口覆盖清单"落成**文件级最小清单**（`core_service.main`、`host_bridge.main`、`catalog_loader.main`、`acceptance_bridge.main/method_catalog_pages` + M2-RC2/M2-AC1/M2-AC5/release-gate runner + `tests/m2_acceptance/test_acceptance_loop.py`），并在 §6 G3 增"首次装配红-绿判别"：未绑定新库经受控入口可完成一次绑定、loader/acceptance 在绑定前拒绝/绑定后可用，且说明既有"loader 先于 Core"顺序如何迁移。 |
| **R3-A1** | P4 | §2.2:50、§5:162、§6:184 | A1 已闭合；仍缺一条**数字断言**层面的判据（r2-A1 的建议原文即"命令表保持 15 条"）。 | `main.rs:1012-1038`（`production_surface_is_exactly_fifteen_commands`） | 建议在 G2 补一句"`command_allowlist(false,false)` 仍恰好 15 条、不新增 wrap 命令"，实现期可直接复用既有断言。 |
| **R3-A2** | P4 | §2.3:80 | `wait_startup_ping` seam 已冻结，但未写"超时后未交付 channel 的**回收方式**"，与既有 `Drop`（发 `core.shutdown` + `wait_timeout_or_kill(5s)`）的先后/锁序未点明，实现者可能让 `Drop` 在协调器持 `child` 锁时再取锁或重复等待。 | `library_bridge.rs:320-334,336-353` | 建议补一句"超时路径显式 `kill`+`wait` 后按明确顺序释放/丢弃该 channel，不依赖 `Drop` 的 shutdown 顺序，也不再等待第二个 5s"。 |
| **R3-A3** | P4 | §2.2:58、§2.3:68 | 措辞精度：①"不改 journal/WAL"宜写成"**不改 journal_mode/WAL 配置**，仅允许一次正常事务的 rollback journal 文件"（`mode=rw` 独立连接在 WAL 库上仍会触碰 `-wal/-shm`；当前 `catalog_store.py` 未设 WAL）；②bootstrap 的 SQLite URI 需明确**正斜杠归一 + percent 转义**（Windows 路径/含空格或 `?`/`#` 的 catalog 路径直接 f-string 拼接会解析错误或被拒）。 | `catalog_store.py:55`（默认 journal 模式，无 WAL PRAGMA） | 建议在 §2.2/§2.3 各补半句，避免实现歧义（不影响判据成立）。 |
| **R3-A4** | P4 | §5:165 | 名单精度：`tests/m2_resource_channel/test_bridge_and_thresholds.py:26,38,76` 实为 `ResourceCatalogStore(":memory:")`，不属"file-backed store 隔离 fixture"；该文件列名无害，但"既有 file-backed…显式初始化"的描述会误导实现者去改一个不受影响的测试。 | `test_bridge_and_thresholds.py:26,38,76` vs `test_catalog_authority.py:63-72` | 建议改为点名 `test_catalog_authority.py::test_persists_across_connections` 等真实 file-backed 用例，并把 `tests/m2_acceptance/test_acceptance_loop.py` 的间接构造（经 `AcceptanceBridge(catalog_db=…)`）纳入 R3-01 的清单讨论。 |

**非 finding 的观察**：`render_preview.py:143-155` 证明 `.preview-lifecycle.lock` 放 derived root 根目录不会被既有第一刀删除（设计选择正确，无需改文本）；`core_service.py:1687` 已 `mkdir(parents=True, exist_ok=True)` catalog 父目录，与其成为首次绑定者的定位相容。

## 6. 两面结论

**Architecture — PASS。** 分层与依赖方向未变：来源权威在 production Core（§2.1:32），channel 仅获"更新既有 retired"窄写权限（§2.2:50/56），产品 app.db 仅 SELECT 且 `BEGIN IMMEDIATE` 同连接判定（§2.4:90），catalog 单事务、不跨库伪造原子提交（§3:102）；F-05 import 白名单内（`handle_resolver.py` 已列 allowed_paths，§5:158）；零 WebView wire/ACL/Tauri 命令扩张（§5:162,168）；删除仍以"核验句柄 + native delete disposition + 目录句柄"为准（§2.4:92-96），`resolve()+unlink` 明文拒绝。**无过度工程**：不新建 GC 框架/调度/引用计数；对未知历史、混合旧 runtime、非协作进程的保守保留是必要 fail-safe。R3-01 是覆盖判据的补齐，不要求放宽保守性。

**Verification — 设计范围内 PASS（静态，executed）；命令级 BLOCKED。** 我独立核对的是设计引用真实源码与设计内部一致性（§2.3 两段式顺序自洽：只读定位→关闭→取锁→业务连接重验；无自锁；降级窗口不发业务；mark 借用租约+独立连接；`.preview-lifecycle.lock` 不在清理目录）。作者 `design-check-r3.log` 记录了 `HEAD=73e70536`、`EXIT=0`、零产品 delta 与 `NOT_RUN` 声明，符合记录纪律，但**未**替代我的独立结论。

| AC | 判定 | 要点 |
|---|---|---|
| AC1 固定 head 调用链取证 | **PASS** | r3 未改 §1 七行事实；新增段落的行号引用（`catalog_loader.py:79`、`acceptance_bridge.py:411`）我逐行复核命中 |
| AC2 可删/必留/未知矩阵 | **PASS** | 13 行矩阵 + 逐项实证第二表未退化，Lock/主产品行显式（K5） |
| AC3 最小生命周期方案 | **PASS（带条件）** | 退役语义/在途读/八行中断矩阵/current-pinned 重读/句柄式删除成立；条件=R3-01 |
| AC4 后继 Task 准备 | **PARTIAL** | allowed_paths/共享变更边界/G1-G7 齐备；base/branch/worktree 明确留待设计集成后由 Codex 创建（未伪造未来路径）；限制=受支持入口首次绑定执行体与受影响清单缺口（R3-01） |
| AC5 零产品 delta + 非作者闭环 | **PARTIAL** | 零 delta 有 checker 断言与作者日志（我 **BLOCKED** 无法复跑）；条件未闭合、未集成，本报告即未通过 |

## 7. 能力矩阵（如实）

| 能力 | 状态 | 说明 |
|---|---|---|
| 固定 base/reviewed_head/delivery、提交链、分支归属、未并入 main | **executed** | 直读 `.git` worktree `HEAD`/`logs/HEAD`/ref 文件与主 `logs/HEAD` |
| 设计文本、r2 报告、disposition、r3 日志、Handoff、checker 关系核验 | **executed** | 全部逐行读取并交叉核对 |
| 真实调用链静态核对（含 4 个 runner/打包入口与受影响测试） | **executed** | 证据见 §3–§5 文件:行 |
| `git status/rev-parse/diff`、`check_design.py`、pytest、cargo | **BLOCKED** | `pwsh` 启动即 `SetNamedSecurityInfoW Win32 5`；未请求提升 |
| 双进程 OS 租约实验、native 句柄删除、实际回收、产品回归 | **NOT_RUN** | 本 Task 零产品改动；G1–G7 属后继 Gate，不冒充设计缺陷 |
| 本会话派发通道与 web_visibility | **UNKNOWN / unverified** | 无法从本会话独立验证上游 CLI 派发 |

## 8. 结论与推荐下一步

**结论：`changes_requested`。** r3 按 r2 建议 (b) 把 bootstrap 冻结成显式两段式，**R2-01 的锁定位顺序循环已真正闭合**；A1/A2/A3 与 O-R2-1/2 均按 r2 要求落点，架构与安全方向无倒退。剩余 1 个 P2：**受支持入口的"首次绑定/迁移执行体"与受影响入口/测试清单未冻结**，而现有 RC2/AC1/AC5/release-gate 的"新库 loader seed"结构在"无绑定即拒绝"下不可执行（`verification/**`、`packaging/**`、`tests/m2_acceptance/**` 又不在 allowed_paths）。这是**局部文本修订**，不是架构返工。条件闭合前**不释放** M2-DERIVED-GC-2（实现），不创建实际 worktree/base。

**推荐下一步（可直接转发）**：

```text
Codex：处理 DSH 非作者 r3 限定复审（reviewed_head=8557a3d4162d00dc7a985ede0dabda22809f60fd，delivery=73e70536b9c5c3525607311892a44ec05580592，决定 changes_requested，0×P0/0×P1/1×P2/0×P3/4×P4）。
在 worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN`（branch codex/m2-derived-gc-2-design）只改设计文本与验证器，不改 src/apps/tests/Schema/wire/依赖：
① 闭合 R3-01（必须）：
   - 在 §2.3 明示首次绑定/迁移登记的执行体=production Core（core_service.main，已有 M2RC1_DERIVED_ROOT）；对无 production Core 的 lab/打包/验收流程写明显式受控初始化路径与调用方；
   - §5 allowed_paths 同步（补列 src/infrastructure/resource_channel/catalog_loader.py、src/bootstrap/acceptance_bridge.py，或明文“不改这两文件、初始化仅经 store 初始化 API 由外来调用方触发”并点名调用方）；
   - §2.3:70 的“受控入口覆盖清单”落成文件级最小清单，至少含 core_service.main、host_bridge.main、catalog_loader.main、acceptance_bridge.main/method_catalog_pages、verification/M2-RC2/run_e2e.py:seed_catalog、verification/M2-AC1/run_e2e.py:launch_env、packaging/release-gate/run_release_gate.py(AC4)、packaging/m2ac5/run_clean_start_e2e.py、tests/m2_acceptance/test_acceptance_loop.py；
   - §6 G3 增“首次装配红-绿判别”：未绑定新库经受控入口可完成一次绑定；loader/acceptance 绑定前拒绝、绑定后可用；说明“loader 先于 Core”的既有顺序如何迁移（Core 先绑定或 runner 显式初始化），否则相关 Gate 不可执行。
② 顺手闭合 P4：A1 补“命令表仍恰好 15 条”断言；A2 补超时后 channel 回收方式（显式 kill/wait，不依赖 Drop 的 shutdown 顺序）；A3 精确化“不改 journal_mode/WAL 配置”并补 bootstrap URI 正斜杠归一/percent 转义；A4 修正 §5:165 对 test_bridge_and_thresholds.py（实为 :memory:）的描述并改为点名真实 file-backed 用例。
③ 提交新的设计 delivery head + 后续 metadata commit 入库 Handoff，交 DSH 在包含 Handoff 的实际新 HEAD 上做限定复核（仅覆盖 R3-01/新 disposition）。
④ 约定：安全方向未倒退，R3-01 只补覆盖判据，不放宽保守性（未绑定一律拒绝保留）。
不启动 M2-DERIVED-GC-2；不创建实际 worktree/base；不修改 r1/r2 报告与历史 attempt 日志。
```

---

Reviewer：DeepSeek Harness（**非作者**）｜base `ab4b7c11`｜reviewed_head `8557a3d4`（worktree `HEAD`/reflog 独立核验）｜delivery `73e70536`｜决定 **changes_requested**｜findings 0×P0 / 0×P1 / 1×P2 / 0×P3 / 4×P4｜命令级复跑 **BLOCKED**（`SetNamedSecurityInfoW Win32 5`，未请求提升）｜native/租约/回收/产品回归 **NOT_RUN**（不冒充设计缺陷）｜本报告未写入任何文件、未实施、未合并、未删除任何历史 worktree。

下一任务建议：**Codex 在 `codex/m2-derived-gc-2-design` 处理 R3-01 + 4×P4（纯设计文本/验证器，不触碰 src/apps/tests）**；处理完成后以新 delivery + Handoff metadata commit 交 DSH 限定复核。除此之外**无需下一步操作**（M2-DERIVED-GC-2 实现 Task 保持未释放）。