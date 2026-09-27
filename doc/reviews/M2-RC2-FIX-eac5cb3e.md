# M2-RC2-FIX 复审 Review — DSH（非作者复审，R2-01..R2-08 修复轮）

- Task：[doc/tasks/M2-RC2.md](../tasks/M2-RC2.md)（`in_review`）+ 修复轮 `M2-RC2-FIX`
- Reviewer：DeepSeek Harness（**非作者**；实现与修复均由 ZCode 产出，Reviewer 未参与实现）
- 仓库/worktree：`C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`
- Branch：`agent/zcode/M2-RC2-resource-channel-hardening`（**追加 commit，无历史改写**）
- 固定 base：`22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`
- **复审 head：`eac5cb3ed56b4531106cfa98ec6d4ea11ce8d51b`**（验证树）；文档 head：`dc8e5c95`
- 已审历史（未重审实现本体）：`a8fb17ca`（交付）/ `4d4aef35`（文档）/ `d93a233f`（派发）；FIX 追加：`4cd97397` → `eac5cb3e` → `dc8e5c95`（docs）
- Review 输入：[doc/reviews/M2-RC2-a8fb17ca.md](M2-RC2-a8fb17ca.md)（本 Reviewer 上一轮，changes_requested）；FIX 回应：[doc/handoffs/M2-RC2-FIX-eac5cb3e.md](../handoffs/M2-RC2-FIX-eac5cb3e.md)
- Reviewer 本轮写路径：本报告 + `verification/M2-RC2/review-dsh-eac5cb3e/`（本轮转录，未跟踪）
- 复审日期：2026-09-27；环境：Windows 11 / Python 3.14.6 / Cargo 1.98.1 / Node 24.15.0 / npm 12.0.1 / Vitest 2.1.9

---

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **approved**（依据仓库 Review 门槛：P0/P1 未解决或关键验证缺失才不可批准——本轮 P1 已闭环并独立复现）。附 **1 项 P2 文案更正（R3-01，零代码）**，须在 Codex 集成前完成 |
| 六条复审命令 | **全部 PASS、exit 0**：66 passed / 20 passed / 15 passed / GATE PASS 10/10 / 探针全 REFUSED / `git diff --check` exit 0（§2） |
| R2-01（P1，ACL 层失效） | **已闭环（采 (a)，实测）**：`__app-acl__` 已生成、capability 授 app 级 7 项；真实 WebView 的 `register_catalog` invoke 返回 **`Command register_catalog not allowed by ACL`**；allow 侧（E-01/D-03）同时 PASS（§2.5、§3.1） |
| R2-02（P2，NaN TTL） | **已闭环**：`math.isfinite` + `bool` 排除；我的探针（含本轮独立副本）NaN/±Inf/0/301 全 REFUSED、300 接受；wire 级 `NaN`/`Infinity` 均 `REF_MALFORMED`（§2.6） |
| R2-03/04/05/06/07 | **均已修复**（gate 改名 `interactive-production-surface` + 显式披露、三份清单手工同步表述、期望 13 id 集合断言 + artefact 入 raw、npm/which + 缺工具 FAIL、`diff --check` exit 0 且如实记录上一轮失实）（§3.2–§3.6） |
| R2-08 | **已声明**（矩阵新增平台假设节；不改代码，与 P3 observation 处置一致）（§3.7） |
| 本轮新 findings | 1×P2（R3-01，文档证据失实）+ 4×P3 观察（O-01…O-04，可选）+ 1 项 Codex 自有事项（O-05：STATUS/Plan 仍是 `proposed / NOT_RELEASED`，非 ZCode 责任）（§3.8） |
| Reviewer 写路径完整性 | **PASS**：上一轮报告与 `review-dsh-a8fb17ca/` 仍 untracked、mtime 未变、从未进入任何提交；本轮探针脚本与上一轮脚本**逐字节相同**（§2.7） |
| FIX 范围 | **PASS**：`d93a233f..eac5cb3e` = 31 路径，逐行与 `raw/fix-diff-name-status.txt` 相同；累计 58 路径与转录相同；禁改面无命中（§2.8） |
| 诚实 Gate 底线 | **PASS**：S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED`；无产品级安全/安装/打包声明；`bundle.active=false` |

## 1. 复审方法与抗篡改手段

1. **先快照再复跑**：跑 E2E 前把 FIX 版 `verification/M2-RC2/raw/`（26 个文件）全量复制到 `review-dsh-eac5cb3e/author-raw-snapshot/` 并记 SHA256；复跑后逐文件比对，再 `git checkout -- verification/M2-RC2/raw` 还原（当前 worktree 仅剩两个 Reviewer 未跟踪目录）。
2. **探针不可篡改验证**：把上一轮由我撰写的 `probe_ttl_nan.py` 内容重新落一份到本轮目录，与仓库内脚本做 SHA256 比对 —— **IDENTICAL**（`C374E02F…9CC0B`），故"探针改为 REFUSED"不是改探针得来的；两条路径各跑一次，输出一致（§2.6）。
3. **语义级 artefact 比对**（不止字节）：对 `e2e-probe-results.json` 做 id/status/observed 三键比对，对两份 sidecar 模块 dump 做集合比对，确认差异只落在易变字段（§2.4）。
4. **依赖源码核对**：沿用上一轮对 `tauri 2.12.0` / `tauri-utils 2.10.0` / `tauri-build 2.6.3` 本地 registry 源码的判据，核对 `__app-acl__` 路径是否真能进入 ACL 判定（§3.1）。
5. **未审到的部分**：FIX 轮未触碰前端（`git diff` 无 `apps/desktop/frontend/**`），故 vitest 只是回归；interactive 页面内矩阵仍**按设计不可外部验证**（R2-03 已披露，本轮接受）。

## 2. 复审验证（EXIT 级转录）

### 2.1 `python -m pytest tests/m2_resource_channel -q`

```text
== re-review rerun: python -m pytest tests/m2_resource_channel -q @ eac5cb3e ==
..................................................................       [100%]
66 passed in 3.26s
EXIT=0
```

66 = 交付 64 + R2-02 新增 2（`test_service_level_non_finite_and_boolean_ttl_refused`、`test_wire_level_nan_literal_refused`）✅ 与 Handoff 计数解释一致。

### 2.2 `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked`

```text
== re-review rerun: cargo test --locked ==
running 20 tests
... test tests::app_acl_manifest_is_generated_and_enforced ... ok
test result: ok. 20 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.51s
EXIT=0
```

20 = 交付 19 + R2-01(a) 新增 1 ✅。编译告警仍为交付轮同组 3 条（`std::sync::Arc` / `CHUNK_SIZE` / `std::io::Write`，claim 基线已存在），非本轮引入。

### 2.3 `npm test --prefix apps/desktop/frontend -- --run`

```text
== re-review rerun: npm test --run ==
 Test Files  2 passed (2)
      Tests  15 passed (15)
EXIT=0
```

### 2.4 `python verification/M2-RC2/run_e2e.py`

```text
== re-review rerun: python verification/M2-RC2/run_e2e.py ==
=== 0. environment ===   {"python":"Python 3.14.6","cargo":"cargo 1.98.1 ...","rustc":"rustc 1.98.1 ...",
                         "node":"v24.15.0","npm":"12.0.1"}          <- R2-06：npm 现可探测
=== 3. sidecar import isolation ===  PASS: 10 project modules, all whitelisted
=== 4. desktop runtime build ===     cargo build exit=0
=== 5. PROBE phase ===               E-00..E-09 + D-01/D-02/D-03 全 PASS（13 行）；summary: {'PASS': 13}
                                     PASS: probe allowlist exactly [...7...]；PASS: probe: 9 project modules
=== 6. INTERACTIVE phase ===         PASS: production allowlist exactly [...3...]; process stayed alive
                                     through the 10s watch; no probe results written; the in-page IP/IA
                                     matrix itself is NOT machine-verified (R2-03)
=== 7. gate ===                      environment PASS / lab PASS / catalog-seeding PASS /
                                     sidecar-import-isolation PASS / runtime-build PASS / probe-phase PASS /
                                     probe-allowlist-announcement PASS / sidecar-module-dump-probe PASS /
                                     interactive-production-surface PASS / sidecar-module-dump-interactive PASS
                                     GATE PASS: all phases green
EXIT=0
```

- gate 键已由 `interactive-deny-matrix` 改为 **`interactive-production-surface`** ✅（R2-03）。
- **字节级比对**：复跑产出的 `raw/e2e-gate.json`、`raw/e2e-environment.json`、`raw/e2e-catalog-loader.log`、`raw/e2e-sidecar-import-isolation.log` 与 FIX 入库版**完全相同**；`e2e-cargo-build.log` 仅耗时行不同（已还原）。
- **语义级比对**（差异仅易变字段，无一项状态差异）：
  - `e2e-probe-results.json`：id 集合相同 = 13、status 分布相同（全 PASS）；仅 `E-06`（opaque id 尾）与 `E-07`（p95/timings）不同 —— 且 **`D-01` 的 observed 文本逐字节相同**：`"Command register_catalog not allowed by ACL"`；
  - `e2e-sidecar-modules-{probe,interactive}.json`：项目模块集合各 9、完全相同；差异仅 `pid`（probe dump 另有 3 个 `encodings.gbk` 类条目，源于我的控制台编码，**无项目模块差异**）。
- **reader 线程验证**：本轮 `%TEMP%/m2rc2-lab/interactive-runtime.log` 已含观察窗内的 4 行 `[m2rc1-title]` + `[runner] elapsed=10.3s alive_through_watch=True`（上一轮该文件只有 allowlist 一行）⇒ R2-03 的"观察窗内持续读 stderr"确实生效。

### 2.5 R2-01(a)：`build.rs` app_manifest 形态与「ACL 真的生效」

| 检查 | 事实 | 结论 |
|---|---|---|
| `build.rs` | `tauri_build::try_build(Attributes::new().app_manifest(AppManifest::new().commands(&[7 命令])))`；inlined plugin 声明已删除，并附 R2-01/R2-04 说明 | PASS |
| `gen/schemas/acl-manifests.json` | 顶层键 = **`__app-acl__`** + `core*`（**不再有 `m2rc1-commands`**）；`__app-acl__.permissions` 含 `allow-issue-resource-url` / `allow-revoke-ref` / `allow-revoke-resource-refs` / `allow-probe-{config,write-results,exit,issue-url}` 共 7 项 | PASS |
| `capabilities/m2rc1-commands.json` | identifier 改为 `m2rc1-command-surface`；`windows: ["main"]`；permissions = **app 级** `allow-*` 7 项（不再是 `m2rc1-commands:default`） | PASS |
| `permissions/autogenerated/*.toml` | 7 个文件（每命令 allow/deny 两条），tauri-build 真实产物，已入库 | PASS |
| 判定链 | `__app-acl__` 存在 ⇒ `has_app_acl=true`（`tauri-utils resolved.rs:250` + `acl/mod.rs:352`）；`tauri 2.12.0 webview/mod.rs:2085` 的条件 `plugin_command.is_some() \|\| has_app_acl_manifest \|\| !is_local` 因此对**裸命令名**成立 ⇒ 本地来源也走 ACL；app 级权限键为裸命令名（`resolved.rs:193-199` 仅对非 app 键加 `plugin:` 前缀） | PASS |
| 运行时实测（拒绝侧） | `raw/e2e-probe-results.json` 的 `D-01`：`"Command register_catalog not allowed by ACL"`（上一轮为 command-not-found 类） | PASS |
| 运行时实测（放行侧） | 同一 ACL 下 `E-01-issue-fetch-digest`、`E-02-img-render`、`D-03-probe-issue-allowed-in-probe-mode` 全 PASS ⇒ capability 授权不误伤产品命令 | PASS |
| 构建产物断言 | Rust 单测 `app_acl_manifest_is_generated_and_enforced` 用 `include_str!("../gen/schemas/acl-manifests.json")` 断言 `__app-acl__` 存在、7 条 `allow-*` 齐备、全清单不含 `register_catalog` | PASS（但见 O-01） |
| 无实测断言清理 | 矩阵原句「其它窗口/来源在 ACL 层拒绝」已删除，改为「单窗口形态下无法从本切片构造，**不断言**未经实测的场景」 | PASS |

### 2.6 R2-02：非有限值 / bool TTL（Reviewer 独立探针）

```text
== A. service.issue() with non-finite ttl_seconds ==
  ttl= NaN  REFUSED (REF_MALFORMED)      <- 上一轮为 ACCEPTED / never expires
  ttl=+Inf  REFUSED (REF_MALFORMED)
  ttl=-Inf  REFUSED (REF_MALFORMED)
  ttl=   0  REFUSED (REF_MALFORMED)
  ttl= 301  REFUSED (REF_MALFORMED)
  ttl= 300  ACCEPTED; expires_at=1300.0; expired (REF_EXPIRED)
== B. stdio wire: raw JSON NaN / Infinity literals ==
         NaN -> {"error":{"code":"REF_MALFORMED"},"id":1}
    Infinity -> {"error":{"code":"REF_MALFORMED"},"id":1}
      999999 -> {"error":{"code":"REF_MALFORMED"},"id":1}
EXIT=0
```

- 反篡改：仓库内 `review-dsh-a8fb17ca/probe_ttl_nan.py` 与本轮独立副本 **SHA256 相同**（`C374E02F…9CC0B`）⇒ 脚本未被改动，结论来自代码修复。
- 代码核对：`service.py` 守卫新增 `isinstance(ttl_seconds, bool)` 与 `not math.isfinite(ttl_seconds)`，并加注释解释 NaN/bool 成因；pytest 新增 service 级（NaN/±Inf/True/False + `active_reference_count()==0`）与 wire 级（`NaN`/`Infinity` 原始 JSON 字面量）两用例。

### 2.7 Reviewer 写路径完整性（重点复核项）

| 检查 | 事实 | 结论 |
|---|---|---|
| 是否进入任何提交 | `git log --all -- doc/reviews/M2-RC2-a8fb17ca.md verification/M2-RC2/review-dsh-a8fb17ca` = **空** | PASS |
| 是否仍 untracked | `git status --porcelain` 仅列 `?? doc/reviews/M2-RC2-a8fb17ca.md`、`?? verification/M2-RC2/review-dsh-a8fb17ca/`、`?? verification/M2-RC2/review-dsh-eac5cb3e/`（本轮 Reviewer 目录） | PASS |
| 是否被改写 | 报告 mtime `2026-09-27T10:56:21Z`（我上一轮最后一次编辑）、探针 `10:49:24Z`、各日志 `10:47–10:54Z`，**全部早于** FIX commit（`11:16Z`/`11:19Z`/`11:21Z`）且未变 | PASS |
| 内容抽查 | 报告仍含 `changes_requested`、R2-01…R2-08 表体与 §6 指令；探针字节比对 IDENTICAL | PASS |

Handoff 自述"两次误 add 均已在入库前撤销"无法追溯验证，但**入库前的可验证事实全部支持**：这些路径不在任何 commit 的 tree 中，且文件未被触碰。

### 2.8 FIX 范围与禁改面（重点复核项）

```text
$ git diff --name-status d93a233f..eac5cb3e   → 31 路径（与 raw/fix-diff-name-status.txt Compare-Object = 相等）
$ git diff --name-status 22a2c2bf..eac5cb3e   → 58 路径（与 raw/final-diff-name-status.txt 相等）
$ git diff --name-only 22a2c2bf..eac5cb3e | grep -E 'infrastructure/sqlite|\.qml$|Cargo\.(toml|lock)$|package-lock|pnpm-lock|doc/contracts|bundle'  → 无命中
$ grep '"active"' apps/desktop/src-tauri/tauri.conf.json   → "active": false
```

31 路径构成：`build.rs`、`capabilities/m2rc1-commands.json`、`gen/schemas/{acl-manifests,capabilities,desktop-schema,windows-schema}.json`、`permissions/autogenerated/*.toml`（7 新增）、`src/main.rs`、`src/application/resource_channel/service.py`、`tests/m2_resource_channel/test_catalog_authority.py`、`verification/M2-RC2/{allow-deny-matrix.md,run_e2e.py,raw/**}`。**无前端改动、无共享 Contract、无 SQLite schema/migrations、无 Legacy QML、无根依赖/锁文件**；`doc/tasks/M2-RC2.md` 与 `final-verification.log` 的更新在文档提交 `dc8e5c95` 内（另加 FIX Handoff、两份 diff 转录），均属 Codex 授权的记录面。

## 3. 逐条 disposition（对照 review §3）

### 3.1 R2-01（P1）→ **FIXED（option a），已独立复现**

判定链、构建产物与运行时两侧证据见 §2.5。上一轮的两个判据（`plugin:<name>|<cmd>` 键不匹配、缺 `__app-acl__`）都已从根上消除：inlined plugin 声明删除、`__app-acl__` 生成、capability 改授 app 级权限；**拒绝侧有真实 ACL 文本、放行侧有 13/13 场景**，双向实测。**接受。**

### 3.2 R2-02（P2）→ **FIXED**：见 §2.6，硬性验收条件（探针 NaN 行 = REFUSED）满足。**接受。**

### 3.3 R2-03（P2）→ **FIXED**：gate 键改名、runner docstring/日志/矩阵三处显式声明"页面内 IP/IA 矩阵未被机器验证（白屏也会 PASS）"，reader 线程实测生效（§2.4）。物理原因披露未被推翻。**接受。**

### 3.4 R2-04（P2）→ **FIXED（表述）**：`main.rs` 注册处注释、`run_e2e.py` docstring、矩阵第 2 层均已改为"三份手工同步视图、无编译期绑定"，并说明各层各自的钉住手段（常量单测 / ACL 构建断言 / runner 按模式对照自报值）。运行时分发重构按 P2 措辞要求未做（属"更好"档位）——可接受。**接受。**

### 3.5 R2-05（P3）→ **DONE（未 defer）**：`EXPECTED_PROBE_IDS`（13 项）集合断言（missing/unexpected/non-PASS 分别入 `e2e-gate.json`），`probe-results.json` + 两份模块 dump 已入 `raw/`。我复跑确认这些 artefact 存在且语义一致（§2.4），并确认"空/部分结果也 PASS"的洞已被堵住（`probe-phase` 需 `results is not None and exit_code==0 and not missing_ids and not unexpected_ids and not bad_ids`）。**接受。**

### 3.6 R2-06 / R2-07（P3）→ **FIXED**：`shutil.which`（含 `.cmd`）使 npm 12.0.1 可记录，缺工具 → gate FAIL；runner 写盘统一 `rstrip()+"\n"`，`git diff --check 22a2c2bf..eac5cb3e` = **exit 0**；`final-verification.log` §4 如实改述并明确记录"delivery 版 clean 声明是错的、命中 blob 保留在已审历史、不做历史改写"。**接受**（诚实处置到位）。

### 3.7 R2-08（P3）→ **DOCUMENTED**：矩阵新增「R2-08 平台假设声明」节（CSP 只覆盖 Windows `http://m2res.localhost`；扩平台须放行 `m2res:` 并重新验证）。**接受。**

### 3.8 本轮 findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-01 | P2（文档，零代码） | `verification/M2-RC2/allow-deny-matrix.md:5`（并波及同文件「参数注入面矩阵」第一行的"错误文本见 raw 证据"） | 新矩阵称 **「E2E D-01（probe 模式）与 IP-1（interactive 模式）对 `register_catalog` 的 invoke 拒绝错误文本记录于 `raw/e2e-probe-results.json` 与 `raw/final-e2e-runner-stdout.log`」**。IP-1 那一半不成立：① 全部入库 artefact 中**没有任何 `IP-*` 行**，含 ACL 文本的只有 probe 阶段的 `D-01`；② `raw/final-e2e-runner-stdout.log` 是**交付轮**（`a8fb17ca`）的 probe stdout（2877 B、自交付轮未改），不含任何 interactive 拒绝文本；③ interactive 阶段的矩阵结果按设计无法离开页面（即同一份文档 R2-03 节的披露）。这条失实陈述恰好落在本轮为"证据准确性"修订的文档里，会误导下游引用者以为 interactive 侧也有归档 ACL 证据 | `grep -n 'IP-1\|not allowed by ACL' verification/M2-RC2/raw/*` → 唯一命中 `e2e-probe-results.json:86`（`D-01` 的 observed）；`Select-String -Path raw/fix-e2e-runner-stdout.log -Pattern 'D-01'` → 只有 `D-01-register-catalog-denied PASS`（无文本）；我复跑的 `interactive-runtime.log` 亦无 IP-* 文本 | 改一句：拒绝文本证据**仅**来自 probe 阶段 D-01（`raw/e2e-probe-results.json`），并明确"interactive 模式的 IP-1 属页面自检，无归档输出（R2-03）"；「参数注入面矩阵」同行的证据引用同步收窄为 D-01 + Rust 构建断言 | open |
| O-01 | P3（可选） | `run_e2e.py` 的 probe 门控；`App.tsx` 的 `expectCommandDenied`（本轮未改前端） | `D-01` 的"ACL 拒绝"归因**未被门控**：页面侧任何 rejection 都算 PASS，runner 只断言 id/status，故若将来退化为 command-not-found，gate 仍 PASS，只有人读 `e2e-probe-results.json` 才会发现。机制回归（`__app-acl__` 丢失）已由 Rust 构建断言拦住，故风险低 | `run_e2e.py` 的 `bad_ids/missing_ids/unexpected_ids` 只比较 id 与 status；`D-01` 的 observed 仅入库不回判 | 可在 `e2e-gate.json` 增记 `d01_observed` 并断言包含 `ACL`（避免断言完整文案以兼容 Tauri 版本差异） | open（可选） |
| O-02 | P3（可选） | `raw/fix-cargo.log`（227 B）、`raw/fix-vitest.log`（351 B） | FIX 轮的 cargo/vitest 原始日志是**截尾**转录（仅摘要 + 最后一个用例），而交付轮的 `final-cargo.log`（1.6 KB，20 行用例名）是全量；证据完整度/口径与上一轮不齐 | 文件大小与内容对照（§2.2/§2.3 我的复跑为全量） | 与交付轮统一口径：全量 stdout 入库（我的复跑日志可直接比对） | open（可选） |
| O-03 | P3（可选） | `capabilities/m2rc1-commands.json`（文件名）vs 内部 `identifier: m2rc1-command-surface` | 文件名与 identifier 不一致；identifier 改名是**必要**的（旧 `m2rc1-commands` 曾引用已删除插件的 `:default` 权限集），但文件名保留旧名易引起"是否还有插件残留"的误读 | `git diff` 显示 identifier 变更、文件未改名；`gen/schemas/*` 中已无 `m2rc1-commands` 键 | 建议把文件一并改名为 `m2rc1-command-surface.json`（纯重命名），或在文件内加一行说明 | open（可选） |
| O-04 | P3（可选） | `verification/M2-RC2/final-verification.log:11,17-18` | 文本把 `git rev-parse HEAD` 的转录指向「§6」，但 §6 是 Findings disposition index，其中没有 rev-parse 输出（HEAD 出现在 §0/Handoff front-matter） | 读 §6 全文（L96-102） | 把交叉引用改为 §0 或 Handoff front-matter | open（可选） |
| O-05 | Codex 自有 | `doc/STATUS.md`（`Current Active Task: None`、`M2-RC2 is proposed / NOT_RELEASED`）、`doc/REBASELINE_PLAN.md` | 治理文档仍停留在 M2-RC2 未释放的状态，与 Task 文件 `in_review` + `release_state: RESOURCE_CHANNEL_COMMAND_SURFACE_RELEASED` 不符。**非 ZCode 范围**（Task 明确 STATUS/Plan/Task 索引归 Codex） | `Select-String doc/STATUS.md -Pattern 'M2-RC2'` | Codex 在集成时补 M2-RC2 release/FIX/integration checkpoint 与 Active Task 行 | open（Codex） |

## 4. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 复审命令 1 | `python -m pytest tests/m2_resource_channel -q` | `eac5cb3e` / Win11 / Py3.14.6 | **PASS**（66 passed, EXIT=0） | `review-dsh-eac5cb3e/re2-pytest.log` |
| 复审命令 2 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | Cargo 1.98.1 | **PASS**（20 passed; 0 failed, EXIT=0） | `re2-cargo.log` |
| 复审命令 3 | `npm test --prefix apps/desktop/frontend -- --run` | Node 24.15.0 | **PASS**（2 files / 15 tests, EXIT=0） | `re2-vitest.log` |
| 复审命令 4 | `python verification/M2-RC2/run_e2e.py` | + WebView2 | **PASS**（GATE 10/10, probe 13/13, npm 12.0.1, EXIT=0） | `re2-e2e-stdout.log` |
| 复审命令 5 | `python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py` | 同上 | **PASS**（NaN/±Inf/0/301 REFUSED、300 接受、wire NaN/Infinity 拒绝, EXIT=0） | `re2-probe-ttl-nan.log` |
| 复审命令 6 | `git diff --check 22a2c2bf..eac5cb3e` | 同上 | **PASS**（exit 0） | 本报告 §2.8 |
| 探针防篡改 | SHA256 比对仓库探针 vs 本轮独立副本 | 同上 | **PASS**（`C374E02F…9CC0B` 相同） | §1.2、§2.6 |
| ACL 机制（静态） | 读 `build.rs` + `gen/schemas/acl-manifests.json` + capability + 7 个 `permissions/autogenerated/*.toml` | `eac5cb3e` | **PASS**（`__app-acl__` + 7×`allow-*`；无 plugin 残留） | §2.5 |
| ACL 机制（运行时） | D-01 observed 文本 + E-01/D-03 放行 | 同上 | **PASS**（拒绝侧 `not allowed by ACL`；放行侧 13/13） | `raw/e2e-probe-results.json`（我的复跑逐字节同文本） |
| 复跑产物一致性 | 字节比对（gate/environment/2 logs）+ 语义比对（probe results / 模块 dump） | 同上 | **PASS**（4 文件逐字节相同；2 文件差异仅易变字段） | §2.4 |
| TTL 负向探针 | 见复审命令 5 | 同上 | **PASS**（上一轮 FAIL 已转为全 REFUSED） | §2.6 |
| Reviewer 写路径 | git log / status / mtime | `dc8e5c95` | **PASS**（untracked、未入历史、mtime 未变） | §2.7 |
| FIX 范围 | `git diff --name-status` + 转录比对 + 禁改面扫描 | `d93a233f..eac5cb3e` | **PASS**（31/58 路径一致，无禁改路径，`bundle.active=false`） | §2.8 |
| 诚实 Gate | Task / Handoff / final-verification §5 三处对照 | `dc8e5c95` | **PASS**（S1-B3/B6/B8=NOT_RUN、S1-B5=UNVERIFIED；无产品级宣称） | §5 |

**Architecture 面结论**：R2-01 的修复方向正确且落到机制层——命令面从"插件式声明（永不匹配裸命令名）"改为"应用 ACL 清单（`__app-acl__` ⇒ 裸命令名参与 ACL 判定）"，并且**拒绝/放行两侧都有真实 WebView 实测**；capability 收窄为 `main` 窗口的 7 项 app 级权限，未引入任何新的命令或放宽面。其余架构结论（catalog authority、wire 形状、导入隔离）沿用已审交付，本轮无改动。**未发现新的越权/泄漏路径。**

**Verification 面结论**：六条命令全部复跑通过且 exit 0；FIX 轮证据的**可复现性**比上一轮更强（gate/environment/日志逐字节可复现，probe 结果语义一致，探针脚本字节可比对）。R2-01/R2-02 两个阻断项的修复都经独立复现，而非只读作者日志。**关键验证无缺失。**

**Standards / Spec 视角**（可选）：Standards `executed` —— 追加 commit、无历史改写、Reviewer 写路径未被触碰、范围与禁改面干净、原始日志带 EXIT/时间头，符合协作协议与证据纪律；唯一硬性偏差是 R3-01（文档陈述与事实不符）。Spec `executed` —— R2-01..R2-08 逐条有对应改动与证据，无 scope creep（31 路径全部落在授权修复面内），未借修复扩大产品承诺。

## 5. 诚实 Gate 底线（不变）

| 项 | 状态 | 核对 |
|---|---|---|
| S1-B3（DACL/完整性，产品级） | `NOT_RUN` | `final-verification.log:90`、Handoff §诚实边界、Task §测试要求——三处一致 |
| S1-B5（生命周期） | `UNVERIFIED` | 同上（L91，注明 unchanged） |
| S1-B6（冷页缓存 1 s） | `NOT_RUN` | 同上（L92） |
| S1-B8（打包/沙箱） | `NOT_RUN` | 同上（L93） |
| 产品级安全/安装/打包就绪 | **未宣称** | 全量扫描 FIX 轮文档：仅出现"**不**宣称/不构成"语境；`bundle.active=false` 未变 |

R2-01(a) 的方向是把 ACL 从"声明"变为"可实测的生效门"，**不新增**对外承诺 —— 我确认本轮新增文本没有把"ACL 生效"升级为"产品级安全边界"。

## 6. 结论与复审

**决定：approved**（`eac5cb3e` 验证树；`dc8e5c95` 文档树同属本轮）。依据仓库 Review 门槛（P0/P1 未解决或关键验证缺失才不可批准）：上一轮唯一的 P1（R2-01）已按 (a) 修复并以真实 WebView 的 ACL 拒绝文本 + 放行侧 13/13 双向实测闭环；P2（R2-02）已修复且我的探针（脚本字节未变）从 ACCEPTED 转为 REFUSED；R2-03..R2-08 逐条有改动与证据。**未发现新的 P0/P1。**

集成前须完成（零代码，一次 docs commit 即可）：

1. **R3-01（P2）**：`allow-deny-matrix.md:5` 删去"IP-1（interactive 模式）…记录于 raw/…"的表述，改为"ACL 拒绝文本证据仅来自 probe 阶段 D-01（`raw/e2e-probe-results.json`）；interactive 模式的 IP-1 属页面自检，按 R2-03 无归档输出"；同文件「参数注入面矩阵」第一行的证据引用同步收窄。

建议（不阻断集成，可并入 Codex 集成 docs commit 或后续切片）：O-01（D-01 归因入 gate）、O-02（cargo/vitest 全量日志）、O-03（capability 文件改名）、O-04（`final-verification.log` §6 交叉引用）。

**剩余风险**：① interactive 生产面除"allowlist 自报 + 存活 + 无结果文件"外仍无页面内验证（已披露、已接受，且 R2-03 后 gate 名称不再暗示相反结论）；② ACL 归因未被门控（O-01），机制回归由 Rust 构建断言兜住；③ 需要 PySide6 的非目标测试套件在本环境仍不可运行（**环境限制**，非本 diff 造成，沿用上一轮结论）。以上均不构成阻断。

**复审方式**：本决定只对 `eac5cb3e`（实现/证据）与 `dc8e5c95`（文档）有效；R3-01 更正后交 Codex 集成。集成后由 Codex 记录集成验证（复跑命令、范围、契约 blob 不变），Reviewer 不再重复验证已审历史。若 Codex 认为 R3-01 可并入集成记录一并修正，我接受该处置。

**Codex 集成清单（提示，均属 Codex 自有职责）**：① 以 `eac5cb3e`+`dc8e5c95` 为输入做集成合并（保留 Owner 链与两份 Review 报告，不改写）；② 导入本报告与上一轮报告（当前均为 untracked，按 M2-C2 先例可在集成 commit 中逐字节导入并记录 SHA256）；③ 更新 [doc/STATUS.md](../STATUS.md)、[REBASELINE_PLAN](../REBASELINE_PLAN.md) 与 Task 索引（O-05：仍写 `M2-RC2 proposed / NOT_RELEASED`、`Current Active Task: None`）；④ 复跑四条冻结命令 + 探针并留 EXIT 级转录；⑤ 集成时同步落 R3-01 的文案更正。

---

## 7. 下一任务建议

1. **Task**：本 Review 通过后，M2-RC2 进入 Codex 集成（含 R3-01 文案更正）。集成为 `done` 后，**下一 Task 须由 Codex 依据 [REBASELINE_PLAN](../REBASELINE_PLAN.md) 与 [STATUS](../STATUS.md) 释放** —— 当前 STATUS 仍写 "no Active Task is released"，且其 M2-RC2 状态行已过期（O-05），因此**不存在可安全直接启动的已授权下一 Task**；Reviewer 不臆造 Task ID。
2. **Agent**：集成=**Codex**（Lead/Integrator，唯一有权改 STATUS/Plan/共享契约）；R3-01 文案更正可交 **ZCode** 一次 docs commit，或由 Codex 在集成记录中一并修正。
3. **Recovery point**：worktree `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`；branch `agent/zcode/M2-RC2-resource-channel-hardening`；base `22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`；FIX head `eac5cb3ed56b4531106cfa98ec6d4ea11ce8d51b`；docs head `dc8e5c95`（Owner 链不再前进，除非做 R3-01）。
4. **Scope**：R3-01 只允许改 `verification/M2-RC2/allow-deny-matrix.md`（必要时 `final-verification.log` 的对应引用）；禁止改代码、Contract、Schema、QML、依赖/锁、打包面。
5. **Deliverables**：R3-01 的 docs commit（或 Codex 集成记录中的等价更正）+ 集成合并 + 集成验证记录（含四条命令与探针的 EXIT 级转录、范围核对、报告导入 SHA256）。
6. **Verification**：`python -m pytest tests/m2_resource_channel -q`（66）、`cargo test --locked`（20）、`npm test -- --run`（15）、`python verification/M2-RC2/run_e2e.py`（GATE PASS 10/10）、`python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py`（全 REFUSED）、`git diff --check <base>..<integrated>`（exit 0）——全部 exit 0 方可关闭 Task；**禁止**把 NOT_RUN/BLOCKED 写成 PASS。
7. **Forwardable instruction（交 Codex 集成）**：

```text
Task: M2-RC2 集成（DSH 复审已 approve：doc/reviews/M2-RC2-FIX-eac5cb3e.md）
输入: fix head eac5cb3ed56b4531106cfa98ec6d4ea11ce8d51b（验证树）+ docs head dc8e5c95
      base 22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5
      Owner branch agent/zcode/M2-RC2-resource-channel-hardening @ worktree
      C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga
1) 集成合并：保留 Owner 提交链与两份 DSH 报告（不改写历史）；冲突按既有规则（master 为基底 + Owner backfill）处理。
2) 集成前先落 R3-01 文案更正（allow-deny-matrix.md:5 及「参数注入面矩阵」首行）：
   拒绝文本证据仅来自 probe 阶段 D-01（raw/e2e-probe-results.json）；interactive 的 IP-1 属页面自检、
   按 R2-03 无归档输出。可交 ZCode 一次 docs commit，或写进集成记录。
3) 导入 doc/reviews/M2-RC2-a8fb17ca.md、doc/reviews/M2-RC2-FIX-eac5cb3e.md 与
   verification/M2-RC2/review-dsh-*/（当前 untracked），逐字节记录 SHA256。
4) 更新 doc/STATUS.md、REBASELINE_PLAN 与 Task 索引（现仍写 M2-RC2 proposed / NOT_RELEASED、
   Current Active Task: None —— 已过期），登记 M2-RC2 release/FIX/integration checkpoint；
   doc/tasks/M2-RC2.md 置 done + integration_commit。
5) 集成验证（全部留 EXIT 级转录）：
   python -m pytest tests/m2_resource_channel -q                # 66 passed
   cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked   # 20 passed
   npm test --prefix apps/desktop/frontend -- --run             # 15 passed
   python verification/M2-RC2/run_e2e.py                        # GATE PASS 10/10
   python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py        # NaN/±Inf/0/301 全 REFUSED
   git diff --check 22a2c2bf..<integrated>                      # exit 0
6) 诚实底线：S1-B3/B6/B8 保持 NOT_RUN、S1-B5 保持 UNVERIFIED；bundle.active=false；不得宣称产品级
   安全/安装/打包就绪。集成后按 §5.1 由 Codex 释放下一 Task（须先修正 STATUS 的过期状态）。
```

**无需下一步操作的部分**：R2-01..R2-08 无需任何进一步实现改动；O-01/O-02 可由我（Reviewer）在后续切片复跑时补证，不阻塞集成。
