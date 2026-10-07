# M2-DERIVED-GC-2-DESIGN 非作者限定复审（r4）— 结论：**approve_with_conditions**

```yaml
task_id: M2-DERIVED-GC-2-DESIGN
reviewer: DeepSeek Harness（非作者；设计作者=Codex）
author: Codex
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
reviewed_head: e4c0967f83a08d9b9e2d84605d17923e81a844b6
delivery_head: af09c00d6dea1beef50d4bb7c6c2ada74670073c
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r4
branch: codex/m2-derived-gc-2-design-review-r4
decision: approve_with_conditions
findings: 0×P0 / 0×P1 / 0×P2 / 0×P3 / 2×P4(advisory)
scope: 仅 R3-01 首次新库入口覆盖 + A1/A2/A3/A4；r1/r2/r3 已闭合的 bootstrap 顺序、句柄安全、生命周期不复审
dispatch: 真实 CLI 派发（本会话无法独立验证上游通道）｜web_visibility=unverified
```

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **approve_with_conditions** —— r3 唯一 P2（R3-01）在设计文本层面**已闭合**；A1/A2/A3/A4 全部按 r3 修订要求落点 |
| 为何不是 changes_requested | 未发现**安全判据缺失**：绑定只发 metadata、不启 GC、不生成来源、不删字节/行；"未绑定一律拒绝"保留；"初始化≠G7 启用"写明。剩余 2 项均为 P4 精度（fail-closed，不改判据） |
| 为何不是 approve | 条件是 **Codex 集成/治理 + 后继 actual base/branch/worktree/allowed_paths 准备**，以及 G1–G7 全 NOT_RUN；另 2×P4 建议吸收进实现指令 |
| 安全方向 | **无倒退**。新增可信 loader flag 只能作用于"本次自有新建/空 catalog"；冲突/已有行/旧未知库拒绝；probe/ac1/`:memory:` 永不启动 GC |
| 当前仓库状态 | **仅设计**：`initialize_namespace` / `initialize-preview-namespace` / `preview_namespace` / `.preview-lifecycle.lock` 在 `src/apps/tests/packaging/verification`（非历史报告）中**零出现**（我独立全仓 token 检查） |
| Architecture 面 | **PASS**（分层、零 wire/命令表扩张、F-05 import 边界、句柄式删除权威均保持） |
| Verification 面 | 设计范围内 **PASS（静态，executed）**；命令级复跑 **BLOCKED**（shell 不可用）；native/租约/回收/产品回归 **NOT_RUN**（后继 Gate，非设计缺陷） |

## 1. 方法与能力限制（如实）

- 本会话 `pwsh` **启动阶段**即失败 3 次，均为 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...DERIVED-GC-2-DESIGN-review-r4)`。**未**执行 `git`/`check_design.py`/pytest/cargo，**未**做双进程租约实验，**未请求提升**（无审批通道），**未伪造 PASS**。命令级：**BLOCKED**。
- 替代证据：`.git` 只读直读（worktree `HEAD`/`logs/HEAD`、design 分支 ref、design worktree `logs/HEAD`、主 `logs/HEAD`/`refs/heads/main`）+ 逐行只读真实源码/驱动/测试 + 全仓 token 检索。未采信作者日志的 `EXIT=0` 作为我的结论。
- 本报告**未写入任何文件、未实施、未合并、未删除任何 worktree/历史**，也**未**重做已闭合项的全仓审计。

## 2. 固定点独立核验（静态）

| 事实 | 我的独立来源 | 判定 |
|---|---|---|
| `reviewed_head = e4c0967f` | `.git/worktrees/DERIVED-GC-2-DESIGN-review-r4/logs/HEAD:1-2`（创建即 `reset: moving to HEAD`，无后续提交）；`HEAD` = `ref: refs/heads/codex/m2-derived-gc-2-design-review-r4` | **核验成立** |
| design 分支 tip = e4c0967f，链 `8557a3d4 → af09c00d → fdfd2351 → e4c0967f` | `.git/worktrees/DERIVED-GC-2-DESIGN/logs/HEAD:10-12`（`freeze isolated preview namespace initialization coverage` → `pin first-run namespace coverage design handoff` → `clarify design handoff path count`）；`refs/heads/codex/m2-derived-gc-2-design` = e4c0967f | **核验成立** |
| `delivery = af09c00d` 为设计文本修订提交，e4c0967f 为其 Handoff/metadata 入库提交 | 同上 reflog 消息 | **核验成立** |
| `base = ab4b7c11` 是设计分支祖先 | 主 `.git/logs/HEAD:877-879`（`32f9b932 → ab4b7c11 → 69d7cc08 → 27cc01a1`） | **核验成立** |
| design 分支未并入 main | `refs/heads/main = 09634adb`；主 `logs/HEAD` 中**无** `e4c0967f/af09c00d` | **核验成立** |
| 设计文档内容 = r4 修订（§2.3:72/79-85、§7:214-222 均存在；r3 旧描写已被替换） | 工作区只读逐行 | **核验成立** |
| 产品 src/apps/tests/packaging/旧 driver/Schema/依赖**未改**（仅设计） | 全仓检索：`initialize_namespace`、`initialize-preview-namespace`、`preview_namespace`、`.preview-lifecycle.lock` 只出现在 `doc/contracts/...`、`doc/reviews/*`、`verification/M2-DERIVED-GC-2-DESIGN/review-disposition.md`；无 `src/apps/tests/packaging` 命中 | **核验成立（token 级）** |
| `git status` / `git diff` / `check_design.py` / SHA256 复算 | —— | **BLOCKED（无 shell）** |

## 3. R3-01 逐条 disposition

| r3 修订要求 | r4 落点 | 我的独立核验 | 判定 |
|---|---|---|---|
| (a) 首次绑定/迁移执行体 = production Core（`core_service.main`），唯一产品迁移登记者受 G7 控 | §2.3:72（`production Core首次新库也复用此步骤；旧产品库迁移仍须G7单独证明，不走fixture入口`）；§7:216（`production迁移登记由core_service.main在G7受控全退出/绑定身份核验后执行`）；§2.3:97 上线 Gate | `core_service.py:1680-1689`：`main()` 已有 `M2RC1_DERIVED_ROOT`（:1683）、`catalog_db.parent.mkdir`（:1687）、`ResourceCatalogStore(catalog_db)`（:1689）、`_run_startup_gc`（:1692/1703）；与"唯一有 derived root 的装配入口"定位相符 | **闭合** |
| (b) 无 production Core 的 lab/packaged/验收给出显式受控初始化路径 | §2.3:72 窄函数 `initialize_namespace(catalog_db, derived_root)`（只新/空自有 catalog、不启 GC、不生成来源、不删字节/行、不迁移旧库）；§2.3:79 loader 可信 flag `--initialize-preview-namespace DERIVED_ROOT` → 调同函数 → 关闭独占/转共享 → 普通 seed；缺参数不初始化、失败不继续 seed | `catalog_loader.py:64-83`：现 CLI 仅 `--db/--set/--remove/--dump/--count`，`store = ResourceCatalogStore(Path(args.db))`（:79）与设计点名一致；`acceptance_bridge.py:406-411` 仅 `self._catalog_db`，`main` 读 `M2RC2_CATALOG_DB`（:615），**不读** derived root → 必须由 launcher 先初始化，与设计一致 | **闭合** |
| (c) §5 allowed_paths 与冻结范围同步（或明文"两文件不改+点名调用方"） | §5:171 补列 `catalog_loader.py`（仅该 flag 接线）；§7:216 明文 `acceptance_bridge.main/method_catalog_pages自身不改`，由 launcher/_LoopHarness 预初始化后按已绑定路径调用；`ac1_bridge.rs` 继承 env 形状不改 | §5:168-182 逐行核对：`catalog_store.py`/`catalog_loader.py`/`handle_resolver.py`/`render_preview.py`/`core_service.py`/`host_bridge.py`/`core_bridge.rs`/`library_bridge.rs`/`main.rs`/8 个测试/2 个 packaged runner/2 个 dev driver/contracts 均在列；`acceptance_bridge.py` 不在列但已明文"自身不改" | **闭合** |
| (d) `§2.3:70` 覆盖清单落成**文件级最小清单** | §2.3:74-83 表（production Core / channel·probe·ac1 / 只有 `--db` 的 loader / loader 首次隔离 seed / AcceptanceBridge / 直接 store 的 pytest）+ §7:216 加 `run_e2e.py:114 seed_catalog`、`run_e2e.py:177 launch_env` 两个 dev driver 与两个 packaged driver | 逐点命中真实调用点：`catalog_loader.py:79`、`acceptance_bridge.py:411`、`host_bridge.py:70/198`、`core_service.py:1689`、`main.rs:1506/1561`（两处真实 sidecar seed，均 `python -m ...catalog_loader --db 新库 --set`）、`run_e2e.py:114`、`run_e2e.py:177`、`run_clean_start_e2e.py:279`（`def seed_catalog_packaged`，调用点 :763，lab derived 根 :242）、`run_release_gate.py:826`（`def roundtrip_catalog_loader`，seed 调用 :840，自带 `catalog-gate/scope/derived` :834-838） | **闭合** |
| (e) §6 G3 增"首次装配红-绿判别"，并说明"loader 先于 Core / ac1 无 Core"如何迁移 | §6:202（`loader显式初始化+seed→probe/ac1 shared服务、_LoopHarness预初始化→catalog_pages、main.rs真实sidecar seed、两个packaged runner fixture传参；无flag旧未知库不claim/不删，有绑定冲突flag不覆盖；初始化只metadata不代表G7批准启用`）；§7:222（`绑定前loader/acceptance拒绝→自有新库显式initialize→绑定后可用；已有行/旧未知库/冲突fixture初始化拒绝，不因测试红放开旧库`） | 与 r3 要求逐字对应；M2-RC2 链的实际顺序为 `prepare_lab`(:82-111，先建 `LAB/scope/derived` 与 asset) → `main`(:518) → `seed_catalog`(:522)，env `M2RC1_DERIVED_ROOT=LAB/scope/derived`(:220) ⇒ flag 接线可直接落地 | **闭合** |

**R3-01 判定：闭合（0 新 P0/P1/P2/P3）。** 覆盖缺口（谁首次绑定、受影响入口/测试清单、首装红绿）均已有冻结落点；保守性未放宽（"未绑定默认拒绝"、冲突不覆盖、初始化≠G7 启用）。

## 4. A1 / A2 / A3 / A4 disposition

| 项 | r4 落点 | 我的独立核验 | 判定 |
|---|---|---|---|
| **A1** 15 条命令断言 | §7:222 `command_allowlist(false,false)仍恰好15条，无退役wrapper`；§6:200 G2 复用该断言 | `main.rs:1012-1038` `production_surface_is_exactly_fifteen_commands` 断言 `command_allowlist(false,false)` 恰为 15 项（我逐项计数：issue_resource_url…list_chapter_pages = 15），任何新增/退役 wrapper 命令都会红 | **闭合** |
| **A2** timeout 显式 kill/wait、锁序、终止态 Drop | §2.3:93（超时先回收**本次自有 child**促 EOF；持 stdout 锁的 worker 不负责 child 锁，协调器持 child 锁退出、不等 stdout 锁；无法证明退出即 BLOCKED）；§7:220（`退出child锁区后join读取worker，再以child已回收的终止态丢弃channel；终止态Drop不得再次发shutdown/等待第二个5s；普通成功channel既有Drop顺序不变`） | `library_bridge.rs:188-193`（`child/stdin/stdout` 三个独立 Mutex）、`:294-302`（持 stdout 锁 `read_line` 无 deadline）、`:320-334`（`wait_timeout_or_kill` 先例）、`:336-353`（Drop = `core.shutdown` + `wait_timeout_or_kill(5s)`）、`:356-357`（`ping`→`round_trip("core.ping")`）——设计与现结构自洽，且明确禁止"持 child 锁期间触发 Drop" | **闭合** |
| **A3** 只禁 journal/WAL 配置变动 + URI `Path.as_uri` | §2.2:58（不改 journal_mode/WAL配置/schema）、§7:218（`mark"不改WAL"只指journal_mode/WAL配置，不禁止一次正常metadata事务的journal文件`；`所有SQLite URI复用stdlib绝对Path.as_uri的正斜杠/percent转义，再追加已冻结query参数；不把含空格/?/#的原始Windows路径直接插入URI`）；§7:218 同时保留 `不能用immutable忽略WAL所得缺行触发初始化旧库` | `catalog_store.py:53-58`（`sqlite3.connect(str(db_path))`，**无任何 PRAGMA/WAL 配置**，默认 rollback journal）与 A3 前提一致；`Path.as_uri()` 对空格/`?`/`#`/`%` 做 percent 转义（stdlib 语义），再拼 `mode=ro&immutable=1` 的 `file:///C:/...` 在 Windows SQLite 可解析 | **闭合** |
| **A4** `:memory:` 纠正 + 真实 file-backed 名单 | §7:222（`test_bridge_and_thresholds.py的store实际是:memory:，只用于mark行为/mock，不做file-backed初始化；直接file-backed fixture为test_catalog_authority/test_derived_gc/test_page_resource_resolve/test_rc4_stdio_render_preview，间接file-backed为test_acceptance_loop::_LoopHarness`） | 全仓 `ResourceCatalogStore(` 检索：`:memory:` 仅 `test_bridge_and_thresholds.py:26,38,76`、`test_catalog_authority.py:32`、`host_bridge.py:70/198`（launcher 兜底）；**tests 内** file-backed 直接构造恰为 `test_catalog_authority.py:65,68`、`test_derived_gc.py:29,114`、`test_page_resource_resolve.py:81,141`、`test_rc4_stdio_render_preview.py:175`（名单**完整**）；间接构造仅 `test_acceptance_loop.py:45-46`（`AcceptanceBridge(catalog_db=root/"catalog.sqlite")`；`test_sfx_policy_end_to_end.py:193` 只 `assemble_acceptance_core`，不涉 store） | **闭合** |

> 说明：§5:179 该行文本仍为泛化表述"既有 file-backed store 隔离 fixture 显式初始化"，未就地删改 `test_bridge_and_thresholds.py` 字样；但 §7:222 已显式纠正为 `:memory:` 并点名真实名单，判据无歧义，**不作为 finding**。

## 5. Findings（本轮新增，2×P4 advisory）

| ID | 级别 | 位置 | 触发与影响 | 证据 | 修订建议 |
|---|---|---|---|---|---|
| **R4-A1** | **P4** | §2.3:79-80、§7:216；`verification/M2-AC1/run_e2e.py:177-189,226-237`；`tests/m2_acceptance/test_acceptance_loop.py:39-47`；`apps/desktop/src-tauri/src/main.rs:664-673` | 无 Core 的首次装配还缺两句落地精度：①AC1 launcher 只有 `(sample_root/"root").mkdir()`（:230），而 `M2RC1_DERIVED_ROOT=root/scope/derived`（:186）在 AC1 dev 路径上**无人创建**（`user_root=None` ⇒ `main.rs:672` 直接取 env，无 `ensure_dir`），而 initialize 需要"已验证隔离 derived 根"（锁文件落在该根）；②`launch_env` 每轮都调用（:233-237 两轮复用同一 `root`），run1 后 catalog 已有行+绑定，字面"每次 spawn 前 initialize"会被"只接受新/空 catalog"拒绝。失败方向是 fail-closed（非误删），故 P4；但可能造成 G3/AC1 假红，甚至诱使实现者放宽"新/空"判据（那才是安全倒退） | `run_e2e.py:177-189,230,233-237`；`main.rs:664-673`；`test_acceptance_loop.py:39-47`（`_LoopHarness` 无 derived 语义、只建 library.db/managed）；§2.3:72"只接受本次自有新建/空 catalog" | 在 §2.3/§7 各补一句：AC1 launcher 在 initialize 前以 fixture 自身创建隔離 derived 根；initialize 仅在 catalog 缺失/未绑定时调用，**run2/已绑定走普通共享路径**；`_LoopHarness` 使用 `root/scope/derived` 自有根。G3 红绿须含"run2 复用已绑定 catalog 仍绿" |
| **R4-A2** | **P4** | §7:216"文件级最小覆盖"；`verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py:62-68`；`verification/M2-RC2/review-dsh-eac5cb3e/probe_ttl_nan_independent.py:62-68`；`verification/M2-RC2/integration-88f972fe/verify.ps1:15`；`doc/handoffs/M2-RC2-FIX-eac5cb3e.md:44`；`verification/M2-RC2/review-dsh-import-sha256.txt:3,26` | 两个 **SHA 冻结**的 reviewer 探针各自新建 tmp catalog 并 `upsert("res-nan","derived-read-only","asset.png")`，且被 M2-RC2 `verify.ps1` 第 5 条命令与 Handoff 列为可复跑证据；"未绑定拒绝业务写入"后原样复跑将失败，而 §5:181 又禁止改历史报告/日志/结果。对 G1–G7 无影响（设计未把 M2-RC2 历史 verify.ps1 作为后继 Gate），但"最小覆盖=完整"表述不精确 | 上述行号；`probe_ttl_nan.py:67` 与独立副本 SHA256 相同（`review-dsh-import-sha256.txt`） | §5/§7 补一句：这两个探针属历史证据（SHA 冻结），不在 M2-DERIVED-GC-2 后继 Gate 集；M2-RC2 的现行可执行 driver 是 `run_e2e.py`（已在 allowed_paths） |

**非 finding 的观察**（不计入 findings）：
- `host_bridge.main` / `catalog_loader.main` 在 §2.3 表以**模块粒度**点名（各模块 `main()` 唯一 CLI 入口，`catalog_loader.py:79` 已给行号），文件级覆盖无歧义，无需改文本。
- §7:218 的"所有 SQLite URI"应读作"本设计新增的 URI"：既有 `src/infrastructure/sqlite/connection.py:369` 用 `as_posix()` 直拼（未 percent 转义）且不在 allowed_paths，本设计未要求改它。
- `packaging/release-gate/run_release_gate.py:826–868` 的行区间未覆盖 `return` 字典尾部（函数实为 :826–874，seed 调用在 :840）；`m2ac5` 的 `:279–307` 精确。属引用精度，不影响判据。
- 正面证据：M2-RC2 `prepare_lab`(:82-111) 先建 derived 与 fixture，再 `seed_catalog`(:114)（`main` :518→:522）⇒ r4 的 `--initialize-preview-namespace <已有derived根>` 在该链上可直接落地；`release-gate` 的 AC4 只断言 `bool(source_confirmed_args)`（:1040），新增 flag 不会打破 `--db/--set/--dump/--count/--remove` 五参数确认。

## 6. 两面结论

**Architecture — PASS。** 来源权威仍在 production Core；channel 仍只有"更新既有 retired"窄写权限；产品 app.db 只 SELECT、不跨库伪造原子提交；零 WebView wire/ACL/Tauri 命令表扩张（A1 的 15 条断言可复用）；F-05 import 边界保持（`catalog_store.py`/`handle_resolver.py` 本就在白名单）；删除仍以"核验句柄 + native delete disposition + 目录句柄"为准。新增的可信 loader flag 只是"绑定 metadata"通道：不启 GC、不生成来源、不删字节/行、不改旧库、不加 WebView 能力，且 **binding ≠ GC 启用**（§6:202、§7:216）。无过度工程：不建通用初始化/调度框架，不放宽保守性。

**Verification — 设计范围内 PASS（静态，executed）；命令级 BLOCKED。**

| AC | 判定 | 要点 |
|---|---|---|
| AC1 固定 head 调用链取证 | **PASS** | e4c0967f/reflog/分支 ref/base 链/未并入 main 全部独立核验；设计引用的 10+ 个 file:line 逐点命中 |
| AC2 可删/必留/未知矩阵 | **不复审** | r3 已 PASS；本轮范围外，未重做 |
| AC3 最小生命周期方案（R3-01/A1-A4 段） | **PASS（带条件）** | 两段式 bootstrap、窄初始化函数、可信 flag、首装红绿、A1-A4 精度齐备；条件=2×P4 与后继 Gate |
| AC4 后继 Task 准备 | **PASS（设计层面）** | allowed_paths/共享变更边界/G1–G7 齐备；base/branch/worktree 留待 Codex 创建，未伪造 |
| AC5 零产品 delta + 非作者闭环 | **PARTIAL** | 独立 token 检查确认零实现（设计专属符号全仓仅存在于 doc/verification 记录）；完整 `git diff`/checker 复跑 **BLOCKED** |

## 7. 能力矩阵（如实）

| 能力 | 状态 | 说明 |
|---|---|---|
| 固定 base/reviewed_head/delivery、提交链、分支归属、未并入 main | **executed** | 直读 `.git` worktree `HEAD`/`logs/HEAD`、design worktree reflog、`refs/heads/*`、主 `logs/HEAD` |
| 设计 §2.3/5/6/7、Handoff、disposition r3 段、design-check-r4.log、r3 报告 findings | **executed** | 全部只读逐行并交叉核对 |
| 真实调用点静态核对（4 个 runner/打包入口、8 个测试、4 处直接 store fixture、2 个冻结探针、命令表、Drop/seam） | **executed** | 证据见 §3–§5 文件:行 |
| 全仓"零实现"token 检查 | **executed** | `initialize_namespace`/`initialize-preview-namespace`/`preview_namespace`/`.preview-lifecycle.lock` 无产品树命中 |
| `git status/rev-parse/diff`、`check_design.py`、pytest、cargo | **BLOCKED** | `pwsh` 启动即 `SetNamedSecurityInfoW Win32 5`（3 次），未请求提升 |
| 双进程 OS 租约实验、native 句柄删除、实际回收、产品回归 | **NOT_RUN** | G1–G7 属后继 Gate；零产品改动，不冒充设计失败 |
| 上游 CLI 派发通道 / web_visibility | **UNKNOWN / unverified** | 本会话无法独立验证 |

## 8. 批准条件（approve_with_conditions）

1. **C1 治理/集成**：Codex 按 §5 冻结的 `allowed_paths` 创建 M2-DERIVED-GC-2 实际 base/branch/worktree 并下发指令二；不得扩张到 `acceptance_bridge.py`（自身不改）或产品 schema/依赖/packaging spec。
2. **C2 后继 Gate 全 NOT_RUN**：G1–G7 必须以真实双进程共享/独占租约、真实句柄删除、真实产品 DB 保护证据关闭；**G7 未证明前 live-preview 与 orphan/dead-row sweep 恒禁用**，不得以本设计批准启用删除。
3. **C3 实现后再复核**：本批准只覆盖 `e4c0967f` 设计文本；实现交付必须在新固定 head 上再由**非作者** DSH 复核。
4. **C4 P4 吸收**：把 R4-A1（AC1/_LoopHarness 自有 derived 根 + run2 复用已绑定 catalog 的处理）与 R4-A2（冻结探针非后继 Gate）写成指令内精度要求或设计窄注记；不修改历史报告/日志/冻结探针。

## 9. 结论与推荐下一步

**结论：`approve_with_conditions`。** r3 的 R3-01（首次新库绑定/迁移执行体与受影响入口清单）在设计文本层面已**真正闭合**：窄函数 `initialize_namespace(catalog_db, derived_root)` + 可信 `--initialize-preview-namespace DERIVED_ROOT` + "未绑定默认拒绝" + Core 唯一产品迁移登记（G7）+ 文件级最小覆盖清单 + 首装红绿 Gate，"初始化≠G7 启用"明确。A1–A4 全部落点且经真实调用点核对（15 条命令、Drop/kill 锁序、journal_mode/WAL 配置语义 + `Path.as_uri`、`:memory:` 纠正与 file-backed 名单完整）。0×P0/P1/P2/P3，2×P4 advisory。当前仍为**纯设计**，src/apps/tests/packaging/旧 driver/Schema/依赖零改动，未来 Gate **NOT_RUN**，命令级复跑 **BLOCKED**（未请求提升，未假 PASS）。

**下一任务建议（可直接转发）**：

```text
Codex：DSH 非作者 r4 限定复审完成，reviewed_head=e4c0967f83a08d9b9e2d84605d17923e81a844b6，
delivery=af09c00d6dea1beef50d4bb7c6c2ada74670073c，base=ab4b7c110a7c828f20d2d0787bd71144336d2e44，
决定 approve_with_conditions，0×P0/0×P1/0×P2/0×P3/2×P4。
① 按既有流程集成设计提交（e4c0967f），回填 Task done；不改 src/apps/tests/packaging/Schema/依赖/历史报告。
② 在指令二/窄注记中吸收 2×P4：
   - AC1 launcher 在 initialize 前由 fixture 自建隔離 derived 根（当前 M2-AC1/run_e2e.py:230 只建 root，
     而 M2RC1_DERIVED_ROOT=root/scope/derived、main.rs:672 无 ensure_dir）；initialize 仅在 catalog 缺失/未绑定时调用，
     run2 复用已绑定 catalog 走普通共享；_LoopHarness 用 root/scope/derived 自有根；G3 红绿含 "run2 仍绿"。
   - 明确 verification/M2-RC2/review-dsh-*/probe_ttl_nan*.py 属 SHA 冻结历史证据，不在 M2-DERIVED-GC-2 后继 Gate 集；
     M2-RC2 现行 driver 为 run_e2e.py。
③ 准备 proposed M2-DERIVED-GC-2 实际 base/branch/worktree/allowed_paths 与完整指令二
   （Owner=ZCode、Reviewer=DSH、Integrator=Codex，G1-G7 不减）；G7 未证明前 sweep 恒禁用。
④ 实现交付后必须在新固定 head 上再由非作者 DSH 复核；本批准不覆盖未来实现。
不创建/启动实现 worktree，除非指令二已发布。
```

---

Reviewer：DeepSeek Harness（**非作者**）｜base `ab4b7c11`｜reviewed_head `e4c0967f`（worktree `HEAD`/reflog 独立核验）｜delivery `af09c00d`｜决定 **approve_with_conditions**｜findings 0×P0 / 0×P1 / 0×P2 / 0×P3 / 2×P4(advisory)｜命令级复跑 **BLOCKED**（`SetNamedSecurityInfoW Win32 5`，未请求提升）｜native/租约/回收/产品回归 **NOT_RUN**（不冒充设计缺陷）｜派发为真实 CLI，web_visibility=**unverified**｜本报告未写入任何文件、未实施、未合并。