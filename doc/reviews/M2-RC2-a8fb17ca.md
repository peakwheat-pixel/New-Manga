# M2-RC2 独立 Review — DSH（非作者）

- Task：[doc/tasks/M2-RC2.md](../tasks/M2-RC2.md)（`kind: implementation`，Owner=ZCode）+ DSH 派发记录 [verification/M2-RC2/dispatch-review-a8fb17ca.md](../../verification/M2-RC2/dispatch-review-a8fb17ca.md)
- Reviewer：DeepSeek Harness（**非作者**；本实现与交付证据全部由 ZCode 产出，Reviewer 未参与实现，未审核自己的变更）
- 仓库/worktree：`C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`
- Branch：`agent/zcode/M2-RC2-resource-channel-hardening`
- 固定 base：`22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`
- **reviewed head：`4d4aef35`**（文档收口）；实现交付 head：`a8fb17cab78e53cdafb8656ab3d9e7044da0f411`
- 复核时分支 HEAD：`d93a233f`（仅新增派发记录 `verification/M2-RC2/dispatch-review-a8fb17ca.md`；`4d4aef35` 是其祖先，代码树与 `a8fb17ca` 逐字节相同 —— 见 §2.5）
- Reviewer 唯一写路径（本报告）：`doc/reviews/M2-RC2-a8fb17ca.md`
- Reviewer 原始转录目录（**未跟踪、Reviewer 证据**）：`verification/M2-RC2/review-dsh-a8fb17ca/`（Codex 可自行决定是否入库或删除）
- 复核日期：2026-09-27；环境：Windows 11、Python 3.14.6、Cargo 1.98.1、Node v24.15.0、npm 12.0.1、Vitest 2.1.9

---

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **changes_requested**，且**范围收窄到「claim 准确性 + 1 处校验补强 + 1 处失败证据补录」**：不要求重写实现；R2-01 是对已交付机制陈述的纠正，R2-02 是一处可复现的校验缺口 |
| 四条冻结命令复跑 | **PASS**（64 / 19 / 15 / GATE 10/10，全部 exit 0；见 §2.1–§2.4，含 EXIT 级转录） |
| 复跑产物可复现性 | **PASS**（`e2e-gate.json`、`e2e-catalog-loader.log`、`e2e-sidecar-import-isolation.log`、`e2e-environment.json` 复跑后与已入库 blob **逐字节相同**） |
| Task F-05 修前证据时序 | **PASS**（修前日志 15:34:49+08 落在 claim `b4a78f0c` 15:25:41+08 与首个实现提交 `9b50dedc` 15:40:16+08 之间） |
| `src/infrastructure/__init__.py` 条件路径 | **PASS（必要性 + 最小性均成立）**；并补做冻结命令之外的回归探测：`tests/storage/test_backup_restore.py` 19 passed |
| 范围核对 | **PASS**（`22a2c2bf..a8fb17ca` = 39 路径，与 `raw/final-diff-name-status.txt` 逐行相同；无禁改路径） |
| allow/deny 矩阵 | **部分 PASS**：`register_catalog` 删除、probe 条件注册、TTL 形状、catalog authority、fail-closed 五项与实现/测试一致；但矩阵**第 1 层（Tauri ACL/capability）在本应用命令面上不生效**（R2-01），且 TTL 校验可被 `NaN` 绕过（R2-02） |
| E2E 门控诚实性 | **PASS（NOT_RUN/MISSING 计失败已实现且可读）**，附加强度问题：R2-03（interactive gate）、R2-05（probe 期望场景集合无断言 / 判别 artefact 未入库）、R2-06（environment gate 恒 PASS） |
| interactive 证据边界（Handoff 已知限制第 1 条） | **接受为诚实披露**（title/close 通道不可用已由 raw 日志独立复现），但要求 gate 标签/表述与「矩阵未被执行验证」对齐（R2-03） |
| 诚实 Gate 底线 | **PASS**：S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED` 保持；未发现任何产品级安全/安装/打包就绪声明 |
| 残留 findings | 2×P1/P2（R2-01、R2-02）+ 4×P2/P3（R2-03…R2-06）+ 2 项观察（R2-07、R2-08）；无 P0 |

## 1. 复核方法与抗篡改手段

1. **复跑四条冻结命令**（§2.1–§2.4），每条都留 EXIT 级转录（落 `verification/M2-RC2/review-dsh-a8fb17ca/review-*.log`，关键行在 §2 内联）。
2. **先快照再复跑，复跑后还原**：运行 `run_e2e.py` 前把作者 `verification/M2-RC2/raw/` 全量复制到 `review-dsh-a8fb17ca/author-raw-snapshot/`（16 文件 + SHA256），跑完后逐文件比对；唯一差异是 `e2e-cargo-build.log` 的 `Finished ... in 0.41s` → `4.25s` 时间行，已用 `git checkout -- verification/M2-RC2/raw` 还原。交付树在复核结束时只有 Reviewer 未跟踪目录（`git status --porcelain` 仅 `?? verification/M2-RC2/review-dsh-a8fb17ca/`）。
3. **独立探针（不在冻结命令内）**：
   - `probe_ttl_nan.py`：直接对 `ResourceChannelService` 与 stdio wire 投喂非有限 TTL（`NaN`/`±Inf`），复现 R2-02；
   - 共享模块回归探测：`python -m pytest tests --collect-only -q` 与 `tests/storage/test_backup_restore.py`；
   - 依赖源码核对：`tauri 2.12.0` / `tauri-utils 2.10.0` / `tauri-build 2.6.3` 的本地 registry 源码（R2-01 的判据）。
4. **未审到的部分（明确记录）**：需要 PySide6 的测试在本环境无法运行 —— 全仓 `tests/**` collection 1009 tests / 16 errors，四套主要 `infrastructure` 消费方（storage/editing/reading_export/library）实跑 206 passed / 7 skipped / **1 failed + 17 errors 全部为 `ModuleNotFoundError: No module named 'PySide6'`**（**环境缺失，非本次 diff 造成**）；故这块只做到「导入级 + 非 Qt 子集」验证（§2.6）。`interactive` 阶段的页面内矩阵结果按设计无法离开页面，Reviewer 亦无法从外部取得（§3 R2-03）。

## 2. 复核清单逐条 disposition（Handoff §DSH 独立 Review 复核清单）

### 2.1 命令 1 — `python -m pytest tests/m2_resource_channel -q`

```text
== reviewer rerun: python -m pytest tests/m2_resource_channel -q ==
................................................................         [100%]
64 passed in 2.75s
EXIT=0
```

与 Handoff/Task 表（64 passed、exit 0）一致；claim 基线 43 passed（`raw/claim-baseline-pytest.log`）→ 43 + 17（`test_catalog_authority.py`：5 + 6 + 6）+ 4（`test_sidecar_isolation.py`）= 64，**差值解释闭合**。

### 2.2 命令 2 — `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked`

```text
== reviewer rerun: cargo test --locked ==
running 19 tests
... (19 行 test ... ok，含 production_surface_is_exactly_three_commands /
    probe_surface_adds_exactly_the_four_probe_commands / register_catalog_exists_on_no_surface /
    issue_wire_never_carries_path_or_ttl / real_core_sidecar_denies_uncataloged_and_extended_ttl)
test result: ok. 19 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.51s
EXIT=0
```

19 = claim 基线 12 + 新增 7 ✅。编译告警 3 条（`std::sync::Arc`、`CHUNK_SIZE`、`std::io::Write` 未使用）在 claim 基线日志中**已存在同一组**（`raw/claim-baseline-cargo.log`），非本次改动引入，不计 finding。

### 2.3 命令 3 — `npm test --prefix apps/desktop/frontend -- --run`

```text
== reviewer rerun: npm test --prefix apps/desktop/frontend -- --run ==
 RUN  v2.1.9 C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga/apps/desktop/frontend
 ✓ src/resourceChannel/client.test.ts (8 tests) 6ms
 ✓ src/resourceChannel/commandSurface.test.ts (7 tests) 7ms
 Test Files  2 passed (2)
      Tests  15 passed (15)
EXIT=0
```

15 = 8 + 7 ✅。

### 2.4 命令 4 — `python verification/M2-RC2/run_e2e.py`

```text
== reviewer rerun: python verification/M2-RC2/run_e2e.py ==
=== 4. desktop runtime build ===            cargo build exit=0
=== 5. PROBE phase ===                      [m2rc2-allowlist] probe:issue_resource_url,revoke_ref,revoke_resource_refs,probe_config,probe_write_results,probe_exit,probe_issue_url
                                            probe phase: exit_code=0 elapsed=5.5s
                                            E-00..E-09 + D-01/D-02/D-03 全部 PASS（13 行）
                                            summary: {'PASS': 13}
                                            PASS: probe allowlist exactly [...7 项...]
                                            PASS: probe: 9 project modules, all whitelisted
=== 6. INTERACTIVE phase ===                PASS: production allowlist exactly ['issue_resource_url','revoke_ref','revoke_resource_refs'];
                                            process stayed alive through the 10s watch; no probe results written
                                            PASS: interactive: 9 project modules, all whitelisted
=== 7. gate ===                             10 个 gate 全 PASS；GATE PASS: all phases green
EXIT=0
```

- `raw/e2e-gate.json`（已入库 blob `a731bb1827e44cf28a753a577fb38450c14cc15a`）与 Reviewer 复跑产物 **逐字节相同**；三个同源日志（catalog-loader / import-isolation / environment）同样逐字节相同 ⇒ stdout 转录与 `e2e-gate.json` **一致**（清单第 4 项 PASS）。
- Reviewer 另行直接读取 `%TEMP%/m2rc2-lab/` 产物独立核验：`sidecar-modules-probe.json` 与 `sidecar-modules-interactive.json` 各 **9 个项目模块**（`application{,.resource_channel{,.dto,.service}}` + `infrastructure{,.resource_channel{,.catalog_store,.handle_resolver,.scope}}`），**无** `infrastructure.filesystem`/`infrastructure.sqlite`/`domain.*`；probe 结果 JSON 恰好 13 行、全 PASS。
- 注：`probe-results.json` 与两份模块 dump **不落在 `raw/`**（前者被 interactive 阶段按设计 `unlink` 以验证「无结果文件」，后者留在 `%TEMP%`），因此「13/13」「9 模块」只能从 stdout 转录读，不能从入库 artefact 复算 → R2-05。

### 2.5 范围核对（清单第 5 项）— PASS

```text
$ git diff --name-status 22a2c2bf..a8fb17ca | wc -l      → 39（与 raw/final-diff-name-status.txt 逐行 Compare-Object = IDENTICAL）
$ git diff --name-status a8fb17ca..4d4aef35              → 4 路径（Handoff、Task、final-verification.log、final-diff-name-status.txt，纯文档）
$ git diff --name-status 4d4aef35..d93a233f              → 1 路径（dispatch 记录）
```

39 路径全部落在 Task 允许范围：`apps/desktop/src-tauri/**`（命令注册/capability/ACL/CSP + `gen/schemas` 4 文件）、`apps/desktop/frontend/**`（command 接线 + 测试）、`src/application|infrastructure/resource_channel/**`、条件路径 `src/infrastructure/__init__.py`、`tests/m2_resource_channel/**`、`verification/M2-RC2/**`、Task 文件。禁改面核对：`src/infrastructure/sqlite/**`（schema/migrations）未触碰、无 Legacy QML、无共享 Contract 文档、无根依赖/锁文件、`apps/desktop/src-tauri/Cargo.toml`/`Cargo.lock` 未改、`tauri.conf.json` 仅 `csp` 一行变化且 **`bundle.active` 保持 `false`**。`gen/schemas/capabilities.json`（原 `{}`）与 `acl-manifests.json` 确为 capability 收敛的真实再生产物（`m2rc1-commands.default_permission` 含 7 条 `allow-*`）。

唯一记录层偏差：`final-verification.log` §4 写 “`git diff --check` clean”，实测 **exit 2**、2 条 `new blank line at EOF`（`raw/e2e-catalog-loader.log:25`、`raw/e2e-sidecar-import-isolation.log:4`）→ R2-07。

### 2.6 Task F-05 侧车入口隔离（清单第 2 项）— PASS（必要性 + 最小性）

- **时序**：`raw/sidecar-import-before-fix.log` 头部自记 `2026-09-27T07:34:49Z`（= 15:34:49+08）+ claim head `b4a78f0c`；committer/author 时间：`b4a78f0c` = 15:25:41+08、`9b50dedc`（Python 半实现）= 15:40:16+08 ⇒ 证据**先于**任何实现提交，落在 claim 与实现之间，与 Handoff 叙述一致。文件 mtime（07:34:49Z）与同批 claim 基线日志（07:33:34Z–07:33:57Z）同段，非事后补造。
- **修前内容**：`infrastructure.filesystem`、`infrastructure.sqlite`、`infrastructure.sqlite.reading_export`、`domain.books.entities` 均在传递集合内 —— 与 `src/infrastructure/__init__.py` 修改前的 `from infrastructure import filesystem, sqlite` 因果一致。
- **必要性**：sidecar 入口是 `infrastructure.resource_channel.host_bridge`，导入它**必然先执行父包 `infrastructure/__init__.py`**，因此不修改该文件就无法切断传递导入；替代做法（把 sidecar 移出 `infrastructure` 包）属更大结构变更。Task 第 36 行已把该文件列为「仅当隔离测试证明必要时允许修改，且须留证据与理由」——条件满足。
- **最小性**：仅把两条 eager import 换成 PEP 562 `__getattr__`（`filesystem`/`sqlite` 两分支 + `AttributeError`），保留 `__all__`，不新增依赖、不改其它模块。
- **回归（冻结命令之外，Reviewer 补测）**：`import infrastructure as I` 不再加载 sqlite（`False`）；`from infrastructure import sqlite, filesystem` 与 `import infrastructure.sqlite.reading_export` 均可用；`tests/storage/test_backup_restore.py` **19 passed, exit 0**；进一步跑 `tests/storage tests/editing tests/reading_export tests/library -q`（这四套是 `infrastructure.sqlite.*` / `infrastructure.filesystem.*` 的主要消费方）得 **206 passed, 7 skipped, 1 failed, 17 errors**，其中 **1 failed + 17 errors 全部为 `ModuleNotFoundError: No module named 'PySide6'`**（环境缺失，含 `bootstrap/app.py:35`），与本 diff 无关；`tests/**` 全量 collection 1009 tests 的 16 errors 亦同因（`PySide6 installed: False`）。
- **改动影响面的结构性说明**：仓库内对 `infrastructure.sqlite.*` / `infrastructure.filesystem.*` 的消费基本都是**子模块导入**（如 `from infrastructure.sqlite.connection import open_database`），由导入系统直接处理、不经 `__init__` 的 eager 属性；受本改动影响的只有「父包属性」路径（`from infrastructure import sqlite/filesystem`、`infrastructure.sqlite` 属性访问），已由上述 smoke、`test_sidecar_isolation.py::test_lazy_infrastructure_attribute_access_still_works` 与 `tests/storage` 实跑覆盖。
- 结论：**接受**。措辞上仅一点建议（非 finding）：`__init__.py` 文档串称「product call sites」使用 `from infrastructure import sqlite`，实测仓库内没有这类调用点（测试用子模块导入），可改成中性表述。

### 2.7 allow/deny 矩阵逐行对照（清单第 3 项）

| 矩阵行 | 实现/测试核对 | 结论 |
|---|---|---|
| `register_catalog` 全模式删除 | Rust 侧仅剩注释与测试常量，`#[tauri::command] fn register_catalog` 已不存在；前端仅在刻意拒绝探针中调用（`App.tsx:109`、`IP-1`、`D-01`） | PASS（编译期） |
| probe 条件注册 | `main.rs:203-268`：`probe_mode = M2RC1_PROBE_OUT.is_ok()` → `generate_handler!` 两个字面清单；生产 3、probe 7，E2E 两阶段自报对照 PASS；`command_allowlist` 单测钉住集合 | PASS |
| TTL 形状 | `issue_resource_url(resource_id, revision)` 无 TTL 参数；`probe_issue_url(resource_id, revision, ttl_seconds)` 仅 probe 注册；`build_issue_params` 无 TTL 键（Rust 单测）；`D-02`/`IP-6` 走私 `ttlOverride` 惰性 | PASS（形状层） |
| catalog authority | host 侧 `StdioCoreChannel` 不再持有 catalog map；wire issue 只带 `resource_id`/`revision_fingerprint`，`rel_path`/`scope_class` 出现即 `REF_MALFORMED`（`host_bridge.py:82-86`）；store 写入校验 scope class + rel-path gate（`catalog_store.py:62-89`）；未编目 id `RESOURCE_NOT_CATALOGED` | PASS |
| fail-closed | 无 catalog 源时 `:memory:` 空库，issue 全拒但 ping/shutdown 仍响应（`test_fail_closed_without_catalog_source`）；`main()` 强制要求 `M2RC2_CATALOG_DB` | PASS |
| **第 1 层 Tauri ACL/capability** | capability 与 inlined plugin 清单确实生成（`gen/schemas/*`），但**对本应用命令不构成运行时门**；「其它窗口/来源在 ACL 层拒绝」无任何测试或可观察证据 | **FAIL → R2-01** |
| 任意 TTL（延长） | `service.py:106-114` 拒绝 `≤0`/`>300`/非数值；但 `NaN` 通过（实证） | **部分 FAIL → R2-02** |

### 2.8 诚实 Gate 底线（清单第 6 项 + 任务底线）

S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED` 在 Task（第 52 行）、Handoff（§诚实边界）、`final-verification.log` §5 三处措辞一致、**未被本 Task 关闭**；未见 `bundle.active` 变化，未见安装/分发/沙箱/产品级安全宣称；`allow-deny-matrix.md` §诚实边界亦显式否认。**PASS**。

## 3. Findings

> 编号说明：本报告 findings 统一用 `R2-xx`，以免与 Task 文本中的 RC1 延期项编号（`F-03` 命令面收敛、`F-05` 侧车入口隔离）混淆。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-01 | P1 | `apps/desktop/src-tauri/build.rs:8-24`、`capabilities/m2rc1-commands.json:1-7`、`gen/schemas/acl-manifests.json`；`verification/M2-RC2/allow-deny-matrix.md:5,48`；Handoff §RC2-AC1 第 3 点 | 交付把「Tauri ACL/capability」列为命令面收敛的**第 1 层生效边界**并称「只授权 main 窗口、其它窗口/来源在 ACL 层拒绝」，但该层对本应用自身命令**不生效**：应用命令由 `tauri::Builder::invoke_handler(generate_handler![...])` 注册、WebView 以**裸命令名**调用，而 inlined plugin `m2rc1-commands` 生成的 ACL 条目键为 `plugin:m2rc1-commands\|<cmd>`，两者永不匹配；同时 `acl-manifests.json` 无 `__app-acl__` 键 ⇒ `has_app_acl=false`，Tauri 对「本地来源 + 非 plugin 命令」直接跳过 ACL 检查。影响：AC1 中的 capability/ACL 证据属于**声明而非生效边界**，`IP-1/IP-2/IP-5` 的「ACL 拒绝」并没有实测支撑（其真实支撑是命令未注册/函数已删除） | ① `gen/schemas/acl-manifests.json` 顶层键 = `core*` + `m2rc1-commands`，**无** `__app-acl__`（build OUT_DIR 内 `acl-manifests.json` 同结论）；② `tauri-utils-2.10.0/src/acl/resolved.rs:250` `has_app_acl = has_app_manifest(acl)`、`tauri-utils-2.10.0/src/acl/mod.rs:352` 仅认 `__app-acl__`、`resolved.rs:190-199` 把非 app 键写成 `plugin:<key>\|<cmd>`；③ `tauri-2.12.0/src/webview/mod.rs:2085` 检查条件 `plugin_command.is_some() \|\| has_app_acl_manifest \|\| !is_local`；④ 反证：若该层生效，`issue_resource_url` 只存在 plugin 键条目 ⇒ 会被拒，而 E2E probe 阶段 13/13 全绿 | 二选一：(a) 让该层真正生效 —— build.rs 改用 `tauri_build::Attributes::new().app_manifest(tauri_build::AppManifest::new().commands(&[...]))`（tauri-build 2.6.3 `lib.rs:405-412`「Sets the application manifest for the Access Control List」）并重生成 `gen/schemas`、补一条 ACL 拒绝侧测试；(b) 若本轮不做，把矩阵第 1 层与 Handoff 措辞改为「已声明、当前非生效门（单窗口形态），生效门为运行时条件注册」，并在 AC1 证据表中把该层标为 `NOT_RUN`/`declared-only` | open |
| R2-02 | P2 | `src/application/resource_channel/service.py:106-114`、`134-140`、`192-193`、`151-158`；矩阵「任意 TTL（probe 命令）」行 | `ttl_seconds` 守卫为 `not isinstance(...) or <=0 or >default`，**`NaN` 三者皆不成立** ⇒ 被接受；`expires_at = clock + NaN`，`expires_at <= now` 恒为 `False` ⇒ 引用**永不过期**；`_enforce_limits` 用 `expires_at > now` 统计活跃引用，`NaN` 条目**不计入上限** ⇒ 32 条活跃引用上限可被绕过（表无限增长）。影响：Core 侧「调用方无法延长/放大引用生命周期」的矩阵结论不成立（`+Inf`/`-Inf`/`0`/`301` 均正确拒绝） | Reviewer 探针 `verification/M2-RC2/review-dsh-a8fb17ca/probe-ttl-nan.log`：`ttl=NaN ACCEPTED; expires_at=nan; still resolves after clock jump to 1e9 (never expires)`；stdio wire 直投 `{"ttl_seconds":NaN}` 返回 `{"result":{"id":"m2id.v1...","size":4}}`，而 `Infinity`/`999999` 返回 `REF_MALFORMED` | `service.py` 守卫加 `math.isfinite(ttl_seconds)`（并排除 `bool`：`isinstance(True,int)` 现被当作 1 s 接受），补 2 条 pytest 行（service 级 NaN + wire 级 NaN）；矩阵该行补注「非有限值亦拒绝」。可达性说明：生产面命令无 TTL 参数、serde_json 不接受 NaN，故仅主机/特权 probe 路径可构造 —— 属 Core 边界防御缺口，不是产品面可利用漏洞，建议本轮一并修 | open |
| R2-03 | P2 | `verification/M2-RC2/run_e2e.py:268-357`、`16-20`（陈旧 docstring）、`65-68`；`e2e-gate.json` 的 `interactive-deny-matrix` 键；Handoff 第 60、64 行 | interactive 阶段唯一运行时证据是「allowlist 自报 + 存活 10 s + 无结果文件」，**没有任何证据表明页面加载过或执行过 IP-1..IP-6/IA-1**：只要能起进程并打印一行 allowlist，即使 WebView 页面白屏或全部脚本抛异常，该 gate 仍 PASS；gate 名称暗示「拒绝矩阵已实测」。Handoff 已知限制第 1 条把「结果无法离开页面」讲清楚了（**接受为诚实披露**），但未点明「矩阵本身无任何机器校验」 | Reviewer 复现：`%TEMP%/m2rc2-lab/probe-runtime.log` 与 `interactive-runtime.log` 中 `[m2rc1-title]` 行始终是**静态窗口标题** `M2-RC1 resource channel runtime`，从不出现页面写入的 `M2RC1\|...` ⇒ title 镜像通道确不可用；`interactive-runtime.log` 全文仅 `[m2rc2-allowlist] production:...` + `[runner] elapsed=10.0s alive_through_watch=True`（runner 在读到 announce 后即停止读管道） | ① 把 gate 键/措辞改为中性（如 `interactive-production-surface`），或补一句「不声称矩阵已执行」；② runner 观察窗内继续读取 stderr 末尾（代价低，可留住未来任何可观察信号，也能保住崩溃/panic 输出）；③ 若要真正验证矩阵，需要设计一个非产品面的带外通道（属产品化决策，不在本 Task 内） | open |
| R2-04 | P2 | `apps/desktop/src-tauri/src/main.rs:39-58`（常量）vs `236-268`（字面注册清单）；`run_e2e.py:277-279` docstring；`allow-deny-matrix.md:48` | 两处证据文书写「allowlist 自报**来源与条件注册同一函数** `command_allowlist`」，但注册用的是 `generate_handler!` 的**字面标识符清单**，`command_allowlist()` 只是并行维护的常量数组；**没有任何测试或编译期约束把三者（常量数组 / `generate_handler!` 清单 / `build.rs` plugin commands 清单）绑定**。影响：未来向注册清单加命令而漏改常量数组时，interactive gate 的唯一运行时证据会报出**偏小的** allowlist 而仍然 PASS，形成静默漂移 | `main.rs:241-266` 与 `main.rs:43-58` 逐项对照；E2E 的 PASS 串也只是把自报值回显；`cargo test` 的 3 条 surface 单测只断言常量数组内部 | 至少把两处措辞改为「runner 对照的是与注册清单**手工同步**的常量数组（当前逐项一致，已由 `production_surface_is_exactly_three_commands` 等单测钉住常量，但注册为字面清单）」；更好：用运行时分发（按 `command_allowlist` 判定后 match 分发）让常量成为唯一事实源，或在 `main.rs` 注册处加不可省略的注释/断言 | open |
| R2-05 | P3 | `run_e2e.py:446-457`、`480-483`、`250-255` | ① `probe-phase` gate 只统计状态分布（`FAIL`/`MISSING`/`NOT_RUN` 计失败），**不断言期望场景集合**：若 `probe-results.json` 存在但为空数组或只含部分行，`failed_probe=0` 且 exit 0 ⇒ PASS；② 关键判别 artefact（`probe-results.json`、两份 sidecar 模块 dump）不落 `raw/`，其状态分布只能从 stdout 转录阅读 | 代码路径 `statuses` 由文件内容派生、无 `expected ids` 常量（`PRODUCTION_EXPECTED`/`PROBE_EXPECTED` 只管命令） | 在 runner 里声明 13 个期望 id（E-00..E-09、D-01..D-03）并断言集合相等；把 probe 结果 JSON 与模块 dump 复制进 `raw/`（避免与 interactive 阶段「删除结果文件」冲突，可先另存副本） | open |
| R2-06 | P3 | `run_e2e.py:403-412`；`final-verification.log:23-33` 与 §1 环境表 | stage 0「environment」gate **无条件 PASS**，且实际记录到 `npm: UNAVAILABLE: [WinError 2]`（Windows 下 `subprocess.run(["npm",...])` 需 `npm.cmd`/`shell=True`）。影响：环境记录缺失被 PASS 掩盖；`final-verification.log` §1 的 npm 12.0.1 来自另一份 claim 基线日志，读者易误以为命令 4 也采到了 npm | `raw/e2e-environment.json` 与 `raw/final-e2e-runner-stdout.log:6` 均为 `UNAVAILABLE`；gate 表同文件第 50 行仍 `environment PASS` | npm 探测改为 `npm.cmd`/`shutil.which`；工具缺失记 FAIL（或把 gate 明确命名为 `environment-recorded` 并给 `WARN`） | open |
| R2-07 | P3 | `final-verification.log:74` | 「`git diff --check` clean」与事实不符：实测 exit 2，2 条 `new blank line at EOF`。影响：证据层自述准确性（不影响门控） | `git diff --check 22a2c2bf..a8fb17ca` → `e2e-catalog-loader.log:25`、`e2e-sidecar-import-isolation.log:4`；`git diff --check 22a2c2bf..4d4aef35` 同 | 改述为「除两份 runner 生成日志的行尾空行外 clean」，或在 runner 写盘时去掉多余尾换行（注意这两份文件会被复跑原样重写） | open |
| R2-08 | P3 | `tauri.conf.json:19`；`resource_protocol.rs:3`、`554-556` | CSP 只覆盖 Windows 映射形态 `http://m2res.localhost`（`build_url` 硬编码 `http://`），而 `resource_protocol.rs` 同时接受原生 `m2res://localhost/...`；在非 Windows 目标上页面 `<img>`/`fetch` 会被 CSP 拦。本 Task 目标是 Windows 单平台，故仅作观察 | `resource_protocol.rs:465-469` 同时接受两种 host 形态；`SCHEME_HOST = "m2res.localhost"` | 若未来发布面扩平台，CSP 需同时放行 `m2res:` scheme；可先加一行注释说明该 CSP 的平台假设 | open |

### 3.1 未被采纳为 finding 的核对结论

- **`probe_config` 硬编码 `"probe_auto": true`**（`main.rs:108-114`）：因该命令仅在 probe 模式存在，语义自洽；前端 `if (!config.probe_auto)` 成为 probe 模式下的死分支，无害。反向也安全：probe 模式下若 `probe_config` 异常，页面会退化为 interactive 矩阵 → 不写结果文件 → `probe-phase` gate FAIL（整体 GATE FAIL），**失败方向闭合**，无需改动。
- **`REMOVED_COMMANDS` 常量与其单测**：`register_catalog_exists_on_no_surface` 只能断言「手写列表里没有该字符串」，不能证明命令未复活（真正证据是函数已删除 + vitest/E2E 拒绝）。属弱测试，但方向安全，不单列 finding。
- **`gen/schemas` 4 文件**：确为真实再生产物（`capabilities.json` 从 `{}` 变为含 `m2rc1-commands`），非手工编造。

## 4. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 冻结命令 1 | `python -m pytest tests/m2_resource_channel -q` | `4d4aef35` 树 / Win11 / Py3.14.6 | **PASS**（64 passed, EXIT=0） | `review-dsh-a8fb17ca/review-pytest.log`；§2.1 |
| 冻结命令 2 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | 同上 / Cargo 1.98.1 | **PASS**（19 passed; 0 failed，EXIT=0） | `review-cargo.log`；§2.2 |
| 冻结命令 3 | `npm test --prefix apps/desktop/frontend -- --run` | 同上 / Node 24.15.0 | **PASS**（2 files / 15 tests，EXIT=0） | `review-vitest.log`；§2.3 |
| 冻结命令 4 | `python verification/M2-RC2/run_e2e.py` | 同上 + WebView2 | **PASS**（GATE 10/10，probe 13/13，EXIT=0） | `review-e2e-stdout.log`；§2.4 |
| 复跑 vs 入库 artefact | `git hash-object` / SHA256 比对（复跑前先快照） | `a8fb17ca` | **PASS**（4 文件逐字节相同；cargo build 日志仅耗时行不同，已还原） | `author-raw-snapshot/`；§2.4 |
| Task F-05 修前证据时序 | git commit 时间 vs 日志头部时间戳 | base..`a8fb17ca` | **PASS**（15:34:49+08 ∈ (15:25:41, 15:40:16)） | `raw/sidecar-import-before-fix.log`；§2.6 |
| 条件路径必要性/最小性 | 读代码 + 语义论证 | `src/infrastructure/__init__.py` | **PASS** | §2.6 |
| 条件路径回归（冻结命令外） | `python -m pytest tests/storage/test_backup_restore.py -q` | 同上 | **PASS**（19 passed, EXIT=0） | `review-shared-module-regression.log` |
| 条件路径回归（扩大面） | `python -m pytest tests/storage tests/editing tests/reading_export tests/library -q` | 同上 | **PASS（非 Qt 子集）**：206 passed / 7 skipped；1 failed + 17 errors 全为环境缺 PySide6 | `review-shared-module-regression.log` |
| 全仓导入级回归 | `python -m pytest tests --collect-only -q` | 同上 | **NOT_RUN**（1009 collected / 16 errors，全部为环境缺 PySide6；非本 diff 造成） | `review-shared-module-regression.log` |
| 范围核对 | `git diff --name-status` + `Compare-Object` 对 `raw/final-diff-name-status.txt` | base..`a8fb17ca` | **PASS**（39 = 39，IDENTICAL） | §2.5 |
| 矩阵逐行对照 | 代码/测试人工对照（§2.7） | `a8fb17ca` | **PASS ×5 / FAIL ×1（R2-01）/ 部分 FAIL ×1（R2-02）** | §2.7、§3 |
| TTL 非有限值（Reviewer 负向探针） | `python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py` | 同上 | **FAIL**（`NaN` 被接受且永不失效） | `probe-ttl-nan.log`；R2-02 |
| E2E 门控逻辑 | 读 `run_e2e.py` + `e2e-gate.json` vs stdout | `a8fb17ca` | **PASS**（NOT_RUN/MISSING 计失败；两处一致）＋ R2-05/R2-06 强度问题 | §2.4、§3 |
| 诚实 Gate | Task / Handoff / final-verification 三处对照 | `4d4aef35` | **PASS**（S1-B3/B6/B8=NOT_RUN、S1-B5=UNVERIFIED；无产品级宣称） | §2.8 |

**Architecture 面结论**：分层方向正确且比 RC1 明显收紧 —— catalog authority 真正移到 Core/SQLite 独立 store、host 不再持有路径、TTL 只允许缩短、sidecar 入口导入面收敛到 9 个白名单模块且有真实进程 dump。**未发现**越权写入、路径走私或跨层泄漏；唯一架构层缺陷是 **R2-01：capability/ACL 这一层被列为生效边界但实际不参与判定**（措辞与实现不符，非新增暴露面 —— RC1 该处 capability 为 `{}`、CSP 为 `null`，本 Task 均未劣化）。

**Verification 面结论**：四条冻结命令全部复跑通过且产物可逐字节复现，claim 基线对照与差值解释闭合，修前 FAIL 证据时序成立，范围与禁改面核对无误。**关键验证未缺失**；缺口集中在 R2-02（一处校验未覆盖非有限值，已由 Reviewer 实证）与 R2-03/R2-05（judgement/gate 强度，非伪造）。

**Standards / Spec 视角**（可选，仅记一行）：Standards `executed` —— 未发现违反 `AGENTS.md`、09 协作协议允许/禁止范围与证据纪律的硬性项；唯一硬性偏差是 R2-07（`diff --check` 自述与事实不符）。Spec `executed` —— AC1/AC2/AC3 均有对应实现与证据，无 scope creep（39 路径全部在允许面内）；AC1 中 "capability、ACL" 一项为**部分完成**（见 R2-01）。

## 5. 结论与复审

**决定：changes_requested（范围收窄，仅需 4 项修订，不重写实现）**

必须在交 Codex 集成前处理：

1. **R2-01（P1）**：纠正「Tauri ACL/capability 为生效边界」的陈述 —— 要么让 `app_manifest` 生效并补 ACL 拒绝侧测试，要么在 `allow-deny-matrix.md`、Handoff 与本报告所指处改为 `declared-only / NOT_RUN`（并说明生效门是运行时条件注册）。
2. **R2-02（P2）**：`service.py` TTL 守卫加非有限值（`math.isfinite`）与 `bool` 排除，补 2 条测试，并更新矩阵该行。
3. **R2-03（P2）**：interactive gate 标签/措辞与「页面内矩阵未被机器验证」对齐（至少改键名或补一句限定），并注意 Handoff 已知限制第 1 条已把物理原因讲清 —— **Reviewer 接受该披露为诚实**，此处只要求把「已执行」的暗示去掉。
4. **R2-04（P2）/ R2-07（P3）**：修正「自报与注册同一 source of truth」这一表述（实为手工同步的三份并行清单），以及 `final-verification.log` §4 的 `git diff --check clean`。

可延后（建议记入后续切片或本轮顺手）：R2-05（probe gate 加期望 id 断言 + artefact 入库）、R2-06（environment gate 与 npm 探测）、R2-08（CSP 平台假设注释）。

**诚实 Gate 底线**：本 Review **不改变** S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED` 的状态，也**不接受**任何产品级安全、安装或打包就绪声明；`bundle.active=false` 与「无安装/分发/沙箱声明」保持。R2-01 的纠正方向是**减少**而非增加对外承诺。

**复审方式**：Owner 在 `agent/zcode/M2-RC2-resource-channel-hardening` 上追加修复 commit（勿改写已审历史；本报告 findings 逐条给 disposition，不抹掉旧记录），并更新 Handoff（新 head + 一行 disposition 表）。复审将复跑四条冻结命令、重跑 `probe_ttl_nan.py`、重核 `acl-manifests.json`/`build.rs`。若 Codex 判定 R2-01 采 (b) 纯文档收敛，则本决定可在该 head 上直接降为 approved；R2-02 不建议降级。

---

## 6. 下一任务建议

> 本 Review 未使 M2-RC2 进入 `done`，因此下一动作是**修复轮**而非新 Task。M2-RC2 集成完成后按 §5.1 需由 Codex 另行释放下一 Task（当前 `STATUS`/Re基线计划中的候选不在本 Review 授权范围内，Reviewer 不预判）。

1. **Task**：`M2-RC2-FIX`（findings 修复轮，挂靠 [doc/tasks/M2-RC2.md](../tasks/M2-RC2.md)；不需新 Task 文件，除非 Codex 要求）。启动条件：本 Review 报告已入库（`doc/reviews/M2-RC2-a8fb17ca.md`）；依赖 M2-RC2 delivery head `a8fb17ca`。
2. **Agent**：Owner=**ZCode**（作者修复自己的变更）；Reviewer=**DeepSeek Harness**（非作者，复审）。Codex 负责集成。
3. **Recovery point**：worktree `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`；branch `agent/zcode/M2-RC2-resource-channel-hardening`；base `22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`；当前 head `d93a233f`（实现交付 `a8fb17ca`，reviewed `4d4aef35`）。**不得 rebase/amend 已审提交**。
4. **Scope**：允许修改 `apps/desktop/src-tauri/{build.rs,capabilities/**,gen/schemas/**,src/**,tauri.conf.json}`（仅 R2-01/R2-04 相关）、`src/application/resource_channel/service.py` + `tests/m2_resource_channel/test_catalog_authority.py`（仅 R2-02）、`verification/M2-RC2/**`、`doc/handoffs/M2-RC2-*.md`、`doc/tasks/M2-RC2.md`。禁止：共享 Contract、SQLite schema/migrations、Legacy QML、根依赖/锁文件、打包发布面（`bundle.active` 必须保持 `false`），以及与本 Review findings 无关的重构。
5. **Deliverables**：修复 commit（含 `R2-01..R2-04/R2-07` 逐条 disposition）；更新后的 `verification/M2-RC2/allow-deny-matrix.md`、`final-verification.log` 与新的 `doc/handoffs/M2-RC2-<newhead>.md`（必须逐条回应 R2-01..R2-08，未修的写明 deferral 与理由）。
6. **Verification**（逐项不可省，未跑即写 `NOT_RUN`）：
   - `python -m pytest tests/m2_resource_channel -q`（≥64 passed，新增 TTL 非有限值用例后计数须给总数与差值解释），exit 0；
   - `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked`，exit 0；
   - `npm test --prefix apps/desktop/frontend -- --run`，exit 0；
   - `python verification/M2-RC2/run_e2e.py`，GATE PASS、exit 0；
   - `python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py`（Reviewer 负向探针）**必须变为全部 REFUSED**；
   - 若走 R2-01(a)：重生成 `gen/schemas/**` 并给出「无 capability 授权时命令被 ACL 拒绝」的实测证据。
   - 完成 Gate：以上命令全部 exit 0 且 R2-01/R2-02 有可复现证据；**禁止**把 planned/NOT_RUN/BLOCKED 写成 PASS。
7. **Forwardable instruction**（可直接转发给 ZCode）：

```text
Task: M2-RC2-FIX（findings 修复轮，非新 Task）
Worktree: C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga
Branch: agent/zcode/M2-RC2-resource-channel-hardening
Base: 22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5
Head: d93a233f（实现交付 a8fb17ca；本次被审 head 4d4aef35）
Reviewer 报告: doc/reviews/M2-RC2-a8fb17ca.md（决定 changes_requested，逐条见 §3 Findings）

要求逐条处理（不改写已审历史，追加 commit）：
1) R2-01（P1）：capability/inlined-plugin ACL 对本应用命令不生效（无 __app-acl__；裸命令名不被 ACL 检查）。
   二选一：(a) build.rs 改用 tauri_build::Attributes::new().app_manifest(AppManifest::new().commands(&[...]))
   使 ACL 真正生效、重生成 gen/schemas 并给出「未授权窗口/无该权限时被拒」的实测证据；
   (b) 若本轮不做，把 allow-deny-matrix.md 第 1 层与 Handoff §RC2-AC1 第 3 点改述为「已声明、当前非生效门（单窗口）」并标 declared-only/NOT_RUN。
2) R2-02（P2）：src/application/resource_channel/service.py TTL 守卫加非有限值拒绝（math.isfinite，并排除 bool），
   在 tests/m2_resource_channel/test_catalog_authority.py 补 service 级与 wire 级 NaN 用例，更新矩阵「任意 TTL」行。
   验收：python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py 输出中 NaN 一行必须为 REFUSED。
3) R2-03（P2）：interactive gate 名称/措辞与「页面内 IP/IA 矩阵未被机器验证」对齐（改键名或补限定语句）；
   建议顺带让 run_e2e.py 在观察窗内继续读取 stderr 末尾。
4) R2-04（P2）/R2-07（P3）：修正「自报 allowlist 与条件注册同一 source of truth」的表述（实为手工同步的三份清单，
   注册为 generate_handler! 字面清单）；修正 final-verification.log §4 的「git diff --check clean」（实测 2 条 EOF 空行告警）。
5) R2-05/R2-06/R2-08 可 defer，但须在新 Handoff 里逐条写明 disposition 与理由。

Scope 禁止：共享 Contract、src/infrastructure/sqlite/**（schema/migrations）、Legacy QML、根依赖/锁文件、
打包发布面（bundle.active 保持 false）。
Verification（全部留 EXIT 级转录并入库 raw/）：
  python -m pytest tests/m2_resource_channel -q
  cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked
  npm test --prefix apps/desktop/frontend -- --run
  python verification/M2-RC2/run_e2e.py
  python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py
交付：修复 commit + 更新后的 allow-deny-matrix.md / final-verification.log + doc/handoffs/M2-RC2-<newhead>.md
（逐条回应 R2-01..R2-08，新 head 精确 SHA）。完成后交 DeepSeek Harness 复审，再交 Codex 集成。
诚实底线：S1-B3/B6/B8 保持 NOT_RUN、S1-B5 保持 UNVERIFIED；不得宣称产品级安全/安装/打包就绪。
```

**无需下一步操作的部分**：除上述修复轮外，本 Review 不请求任何额外实现；若 Codex 对 R2-01 采纯文档收敛 (b)，可在同一 head 上直接复审并将决定降为 `approved`。
