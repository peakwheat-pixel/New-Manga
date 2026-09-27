# M2-RC1-FIX 复核 Review — DSH changes_requested 修复轮复验

- Task：[M2-RC1](../tasks/M2-RC1.md)（`kind: implementation`，Owner=ZCode）+ 修复轮 `M2-RC1-FIX`
- Reviewer：DeepSeek Harness（**非作者**；本实现与修复均由 ZCode 产出，Reviewer 未参与实现）
- 仓库/工作区：`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`
- Branch：`agent/zcode/M2-RC1-large-media-resource-channel-runtime`
- 固定 base：`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`
- **reviewed head：`702b02b06946f1174c8fc981c9ed79c98afd88b4`**（修复 commit）；其后文档提交 `7d20b4ca839051d9f45e3b331fd47a8589d1a866`（FIX Handoff）
- 被复核的上游 Review：[`doc/reviews/M2-RC1-f8ce10a2.md`](M2-RC1-f8ce10a2.md)（changes_requested，1×P1 + 5×P2 + 7×P3）
- 修复 Handoff：`doc/handoffs/M2-RC1-FIX-702b02b0.md`
- Contract 固定 blob：`fc35913801297ee1876ea395f9c5041a16226f20`（版本 1.1，§10.1/§10.2）
- 复核日期：2026-09-27
- 报告路径（Reviewer 唯一写路径）：`doc/reviews/M2-RC1-FIX-702b02b0.md`

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **changes_requested**（范围收窄：**仅证据/记录层**，F-01/F-02 实现已闭环，不要求重写实现） |
| F-01（P1，上游阻断项） | **PASS — 已修复**（每请求经 Core resolve + 拒绝即逐出 + typed 传播；两条定向回归测试与之匹配；e2e E-04 改为暖缓存变体） |
| F-02（P2，与 F-01 同源） | **PASS — 已修复**（`verified_mtime` 绑定 `LastWriteTime`；等大小原地改写触发全量流式重验；回归测试存在） |
| 准入项 | F-04 **PASS**；F-11 **PARTIAL**；F-13 **PARTIAL**（详见 §5） |
| 复跑四条命令 | **BLOCKED（本会话 shell 不可用）→ 交叉核验：计数 PASS、EXIT 级证据 FAIL（未入库）**（详见 §2） |
| 无回归 | **PASS**（原 35 pytest 场景与 9→12 Rust 测试语义未见削弱） |
| 诚实边界 | **PASS**（S1-B3/B6/B8 NOT_RUN 保留；无产品级安全/打包就绪宣称） |
| 残留 findings | 3×P2 + 2×P3（`FIX-01`…`FIX-05`，全部为证据/记录与 disposition 准确性问题，无正确性缺陷） |

## 1. 复核方法与工具限制（必须先读）

本会话 `pwsh` 在启动阶段稳定失败，与上游 Review 会话同源：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-RC1-zcode)
```

对任意命令、任意 `workdir`（含 `C:\Windows\Temp`）复现；`sandbox_permissions: danger-full-access` 一次性重试被拒：`requires approval, but no approval channel is available`。因此本 Reviewer **无法执行任何进程**（`git`、`pytest`、`cargo`、`npm`、`run_e2e.py` 均不可跑）。

替代方法（全部只读文件系统工具 read / glob / grep；并新增一条上游 Review 未使用的独立证据链）：

1. git 事实取自主仓库 reflog 文本 `G:/CODEX/New Manga/.git/worktrees/M2-RC1-zcode/logs/HEAD`（13 行，末行即 `7d20b4ca`，其父为 `702b02b0`）。
2. **mtime 排序反演**：`glob **/*` 返回全仓 12 450 条路径的修改时间序（由新到旧可定位最近改动集），用于反演**修复轮实际触碰的文件集合**——这是本次相对上游 Review 新增的独立核验面（见 §2.3、§8）。
3. 测试运行的**残留产物**交叉核验：`.pytest_cache/v/cache/nodeids`（40 条）与 `lastfailed`（`{}`）、`apps/desktop/frontend/node_modules/.vite/vitest/results.json`、`src-tauri/target/debug/.fingerprint/**` 的 `test-bin` 指纹与 `deps/m2rc1_desktop-*.exe`。
4. 语义审查：逐行阅读 `resource_protocol.rs`（568 行）、`main.rs`（491 行）、`core_bridge.rs`（344 行）、`service.py`/`dto.py`、`run_e2e.py`、`App.tsx`、两个测试文件与全部 verification 产物。

**能力边界**：本报告不构成运行验证。凡 `BLOCKED` 项，解除条件为「在有 shell 且 worktree 可写 ACL 的会话中复跑」。

## 2. 复跑四条命令（复核清单 1）

### 2.1 判定表

| 命令 | 期望 | 本 Reviewer 实测 | Owner 证据 | 交叉核验 | 判定 |
|---|---|---|---|---|---|
| `python -m pytest tests/m2_resource_channel -q` | 40 passed, exit 0 | 无法执行 | Handoff 散文「40 passed, exit 0」，无日志/EXIT 头 | `.pytest_cache/v/cache/nodeids` = **40** 条（含 5 条 `TestF13CoverageAdds`）；`lastfailed` = `{}` | **BLOCKED（复跑）/ PASS（计数）/ FAIL（EXIT 级证据未入库，§6.12①）** |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | 12 passed, exit 0 | 无法执行 | 同上，散文「12 passed, exit 0」 | `main.rs` 恰 **12** 个 `#[test]`；`target/debug/.fingerprint/m2rc1-desktop-c2118cdc632a8f23/{output-,}test-bin-m2rc1-desktop` 与 `deps/m2rc1_desktop-c2118cdc632a8f23.exe` 存在（测试二进制确被构建） | **BLOCKED（复跑）/ PASS（计数）/ FAIL（无通过 artefact）** |
| `npm test --prefix apps/desktop/frontend -- --run` | 8 passed, exit 0 | 无法执行 | 同上，散文「8 passed, exit 0」 | `client.test.ts` 恰 **8** 个 `it(`；`node_modules/.vite/vitest/results.json` = `[[":src/resourceChannel/client.test.ts",{"duration":5.15,"failed":false}]]`（1 文件、未失败） | **BLOCKED（复跑）/ PASS（计数+文件级通过）** |
| `python verification/M2-RC1/run_e2e.py` | 10/10 PASS, exit 0 ×2、逐项一致 | 无法执行 | 同上，散文「10/10 PASS ×2, exit 0」 | `raw/fix-e2e-results-first.json` 与 `raw/fix-e2e-results-repeat.json` 各 **10 条全 PASS**，id 集合一致（含改名后的 `E-04-revoke-after-cached-fetch`）；`raw/fix-repeat-consistency.json` = `PASS 10/10`、`differences {}`、`consistent true` | **BLOCKED（复跑）/ PASS（计数）/ PARTIAL（exit code 与「逐项一致」无生成脚本）** |
| `git diff --name-status 2dca20cd..702b02b0` | 仅授权路径 | 无法执行 | Handoff 声称 49 文件 | 文件清点推算 = 50（HEAD `7d20b4ca`）／49（`702b02b0`，不含 FIX Handoff 自身），与声明自洽；但**无入库转录** | **BLOCKED / PARTIAL（见 FIX-04）** |

### 2.2 结论

- 四条命令的**测试计数**可独立复核（40 / 12 / 8 / 10×2），与 Handoff 声明完全一致；pytest 与 vitest 还有「未失败」残留证据。
- 但按仓库协作协议 **§6.12①**：「凡以『N passed』充当证据的运行日志，**必须带 EXIT 码与 shell/venv 头**并**逐次入库**；只有末两行或只写『×N 全绿』的日志**不可复核，按未提供处理**」。修复轮的四条命令**没有任何逐次入库的日志**，只有 Handoff 表格里的计数散文；`exit 0` 无 artefact。→ 形式上是「未提供」，记为 **FIX-01**。
- 全仓 grep `fix-verification|fix_cargo|fix-pytest` 零命中；`verification/M2-RC1/` 下只有未更新的 `final-verification.log`（见 §5.2）。

### 2.3 修复轮触碰面（mtime 反演，独立核验）

`glob **/*` 的修改时间序尾部（最近改动）依次为：`App.tsx`(12351) → `main.rs`(12354) → `resource_protocol.rs`(12380) → `run_e2e.py`(12420) → `.pytest_cache/.../nodeids`(12421) → `target/debug` 测试二进制(12422–12442) → `node_modules/.vite/vitest/results.json`(12443) → `raw/fix-e2e-results-{first,repeat}.json`(12444–12445) → `raw/e2e-fixtures.json`(12446) → `raw/fix-repeat-consistency.json`(12447) → `raw/leakage-scan.json`(12448) → `doc/handoffs/M2-RC1-FIX-702b02b0.md`(12449) → `doc/tasks/M2-RC1.md`(12450)。更早一批为 `test_service.py`(12078)、`core_bridge.rs`(12037)、`final-verification.log`(12032)、`run-log.md`(12033) 等。

两点直接推论：

1. **修复轮实际触碰的文件全部落在授权路径内**，未见 `doc/contracts/**`、`src/ui/**`、`packaging/**`、根依赖/锁文件等禁改路径进入最近改动集。
2. **`final-verification.log`(12032) 的 mtime 早于修复轮的源码/证据文件(12351+)** → 它在修复轮**未被重写**；与 §5.2 的内容事实互相印证。

## 3. F-01（P1）核验 — PASS

| 复核点 | 证据 | 判定 |
|---|---|---|
| 每个请求（含缓存命中）都调 `channel.resolve` | `resource_protocol.rs:476-487`：先 `channel.resolve(&full_id)`，**无条件**在缓存查表之前；缓存只在 resolve 通过后才被读取/刷新（`:498-527`） | **PASS** |
| Core 拒绝 → 逐出缓存 + typed 拒绝 | `:483-486` `Err(error) => { cache.map.lock().unwrap().remove(&full_id); return typed_error(&error); }`；`typed_error`（`:116-123`）按码映射 404/410/403/503 并保持 `no-store` | **PASS** |
| Core 通过 → 以返回 grant 刷新缓存 | `:502-527`；且当 `sha256/size/rel_path` 变化时强制 `digest_verified=false, verified_mtime=None`（`:506-512`）——补上了「同一 ID 指向内容变化」的重验 | **PASS** |
| 回归测试 `f01_fetch_then_revoke_then_fetch_must_be_typed` | `main.rs:361-382`：`registered()` → 首次请求断言 **200** → `channel.revoke(&opaque)` → 第二次请求断言 **410 + `{"code":"REF_REVOKED"}`**。与上游 Review §9 F-01「复现 1」逐字一致 | **PASS** |
| 回归测试 `f01_ttl_expiry_invalidates_cached_grant` | `main.rs:384-419`：经 `ttl_override=Some(0.3)` 签发 → 首次 **200** → `sleep(500ms)` → 第二次断言 **410 + `REF_EXPIRED`**；`MockCoreChannel.resolve`（`core_bridge.rs:308-322`）确实现查 `expires_at` | **PASS** |
| e2e E-04 改为先暖缓存再 revoke 再 fetch | `App.tsx:156-169`：`issue("res-probe","rev-2")` → `fetchAll(...)`（断言 `warmed.size === revocable.size`）→ `revoke` → `fetchChunk(...)` 期望 `REF_REVOKED`；结果 id 已改名为 `E-04-revoke-after-cached-fetch`，`raw/fix-e2e-results-*.json:34-37` 观测值 = `REF_REVOKED` | **PASS** |

**判别力（「修前必 FAIL」）的记账**：Handoff 声称两条回归「先证明修前 FAIL（`200 vs 410`）」。以当前工作区代码与缓存命中分支的读法，修前行为确实会是 200（缓存命中直接返回），逻辑上判别力成立；但仓库内**没有修前失败运行的 artefact**（无日志、无探针输出）。按协议 §6.12②「判别力证据必须是 artefact，缺失即记 `NOT_RUN`，不得以散文代替」→ 该条应降级为 **NOT_RUN**，见 `FIX-02`。

## 4. F-02（P2）核验 — PASS

| 复核点 | 证据 | 判定 |
|---|---|---|
| `CachedGrant.verified_mtime` 绑定 `LastWriteTime` | `resource_protocol.rs:59-66`；mtime 由 `identity_size_mtime`（`:267-279`）从 `BY_HANDLE_FILE_INFORMATION.write_hi/write_lo` 合成（`(write_hi << 32) \| write_lo`，100 ns 粒度） | **PASS** |
| 等大小原地改写触发全量 digest 重验 | `:424-435`：`needs_digest = !entry.digest_verified \|\| entry.verified_mtime != Some(mtime)`；命中即 `stream_digest(handle, size)` 全量流式比对，失配 → `CONTENT_DIGEST_MISMATCH`，并仅在通过后写回 `verified_mtime` | **PASS** |
| 失败即逐出缓存 | `:531-544`：`FILE_IDENTITY_CHANGED` / `FILE_SIZE_CHANGED` / `REF_OUT_OF_SCOPE` / `CONTENT_DIGEST_MISMATCH` 四类错误均 `remove(&full_id)` | **PASS** |
| 回归测试 `f02_equal_size_rewrite_after_first_verify_rejected` | `main.rs:421-449`：首验 200 → `OpenOptions::new().write(true)` 持写句柄 `seek(0)` 后 `write_all(flipped)`（等长、翻转字节、保 file index、mtime 变化）→ 第二次断言 **400 + `CONTENT_DIGEST_MISMATCH`**。与 Review §9 F-02 的复现路径一致 | **PASS** |

`resource_protocol.rs` 顶部文档注释（`:14-16`）仍表述为「**first-verified** grant also streams the whole file once…」，与 `:424-435` 的「mtime 变化即重验」已不完全同步（注释未提 mtime 触发条件）。属文档一致性小瑕（P3 级），不单列 finding，随 `FIX-05` 一并记录。

## 5. 准入项核验

### 5.1 F-04（T3 尺寸与 P95）— PASS

- `run_e2e.py:44-45` 新增 `typical = write_noise_png(derived/"typical.png", 1600, 2400, seed=5202)`，并进入 fixture manifest（`:59`）。
- `raw/e2e-fixtures.json:8-11`：`typical.sha256=dc5cc22b…1d05`，**`bytes=11525983`**。
- `App.tsx:194-218`：注册 `res-hot` → `typical.png`，8 次「新引用 + `fetch(url?chunk=0)`」，`p95 = timings[min(len-1, floor(len*0.95))]`（len=8 → 取最大值，保守）。
- `raw/fix-e2e-results-first.json:51-68`：`p95_ms=87`；`...-repeat.json:51-68`：`p95_ms=88`。**均 ≤ 200 ms 预算**，`status=PASS`。
- 诚实披露：`App.tsx:196-199` 与 Handoff:29 都写明每样本含「新引用的首验全量 digest 流」，因此该数字是**含 digest 首验的保守上界**，不能与修复前「49 KB / ≈1–2 ms」直接对比——披露充分。
- 两处小瑕（不单列 finding）：① 数字标签「~11.5 MiB」与实际 `11,525,983 B`（= **10.99 MiB**）不符，逐字照抄 M2-S2 的「11.5 MiB」口径；② 样本名为「hot-cache」而每样本是新引用（OS 文件缓存热、grant 缓存冷），措辞可更精确。

### 5.2 F-11（文件数更正）— PARTIAL

| 要求 | 现状 | 判定 |
|---|---|---|
| Handoff 更正文件数 | 新 FIX Handoff:31、:63 改为 **49 文件**（`git diff --name-status 2dca20cd..702b02b0`）。经文件清点推算：HEAD `7d20b4ca` = 50，`702b02b0` = 49，**与声明自洽** | **PASS** |
| 附本 head 的 `git diff --name-status` 证据 | 仓库内**无**修复 head 的 diff 转录 | **FAIL** |
| Task 更正 | `doc/tasks/M2-RC1.md:57` 仍写「**30 文件全授权路径**」；`:58` 仍「**9 passed**」、`:59` 仍「**35 passed**」、`:60` 仍「热缓存 **P95≈1 ms**」 | **FAIL** |
| 引用的证据文件 | Handoff:31、:65 把 `verification/M2-RC1/final-verification.log` 标为「**（更新版）**」，但该文件实际仍是 f8ce10a2 之前的版本：标题 `delivery head 991097d7`（`:1`）、`35 passed`（`:5`）、`9 passed`（`:9`）、`8 passed`（`:14`）、§5 仍列 **41** 条旧路径（`:21-61`） | **FAIL（证据指针失效）** |

mtime 反演独立佐证了最后一条：`final-verification.log` 的修改时间早于修复轮全部源码/证据改动（§2.3）。→ `FIX-01` + `FIX-04`。

### 5.3 F-13（六类补测 / 或降级记录）— PARTIAL

新增 5 条 `TestF13CoverageAdds`（`test_service.py:162-240`，`nodeids` 第 22–26 行确认被收集）：

| 上游 F-13 要求 | 本次落实 | 判定 |
|---|---|---|
| ①17 T2 默认 300 s + `touch` 续期 | `test_default_ttl_is_300s_and_touch_renews`（`:165-179`）：`DEFAULT_TTL_SECONDS` 下 `now=290` resolve 通过 → `touch` → `now=305` 仍通过（滑动重臂） | **PASS** |
| ② pin release 别名撤销 | `test_pin_release_alias_revokes`（`:181-186`）：`revoke_bookkeeping_for("res-pin") == 1` → `REF_REVOKED`；别名实现见 `service.py:265-268` | **PASS** |
| ③ 在途 revoke 不中断 | `test_inflight_consumption_survives_revoke`（`:188-198`）：先 `resolve` 取 grant → `revoke` → `reader.read(grant, opaque)` 仍读完且摘要匹配 → 下一次 `resolve` = `REF_REVOKED` | **PASS（语义等价代理）** |
| ④ T2 20 线程并发矩阵 | `test_t2_concurrent_subscriber_matrix`（`:200-223`）：20 线程并发 `acquire_subscriber`，恰 16 接受、4 拒绝 | **PASS（订阅者面）/ 未覆盖引用面** |
| ⑤ T2 真实上限：32 个真实活跃引用 + 第 33 个被拒 | **无**：`test_active_reference_limit`（`:139-145`）仍用 `max_active_references=4`；无默认 32 的用例 | **FAIL** |
| ⑥ 同资源第 17 个引用被拒（issue 路径 `service.py:154-163`） | **无**任何用例走到 `_enforce_limits` 的 `same_resource + 1 > self._max_subscribers` 分支 | **FAIL** |
| ⑦ 只读约束（adapter 只读打开断言） | `test_read_only_channel_has_no_write_surface`（`:225-240`）实际断言的是「`service` 上不存在 `write*` 可调用入口」——**不是** upstream 要求的「`GENERIC_READ` / 写模式拒绝」断言；`handle_resolver.py` 的只读打开行为仍无测试 | **FAIL（弱代理）** |
| ⑧ open-once | 无 `CreateFileW` 计数/单句柄断言。Handoff:32 把该面「转由 Rust 每请求路径承担」——但 Rust 侧同样**没有** open-once 计数测试 | **FAIL** |
| ⑨ 读后身份复核 | `main.rs:338-355 identity_change_invalidates_cache_entry` 用 `remove_file + write` 造**新身份**，命中的是**读前**身份检查（`resource_protocol.rs:414`），**没有**触发 `:442-445` 的读后复核。Handoff:32 把两者等同，属口径混淆 | **FAIL** |

**替代路径未走**：上游 F-13 的 disposition 是 `must_record_or_fix`——「补六类测试，**或**把 AC3/AC4 对应覆盖项降级为『部分覆盖』并记录」。本次选择「补测」，但六类中约 2–3 类（⑤⑥⑦⑧⑨）仍缺，且 `doc/tasks/M2-RC1.md:34` 的 RC1-AC4 仍原样声称覆盖「…**只读约束**」，`:33` 的 AC3 仍 `[x]`，**没有任何降级标注**。→ 允许的替代路径未走，`FIX-03`。

## 6. disposition 合理性核验

### 6.1 F-03（命令面收敛）与 F-05（sidecar 独立入口）登记为后续 Task 前置项 — 可接受

- **F-05**：`core_bridge.rs:104-114` 的启动点为 `python -m infrastructure.resource_channel.host_bridge`，经 `src/infrastructure/__init__.py` 传递性导入产品模块；该文件在 `doc/tasks/M2-RC1.md:51` 的禁改范围内，**本 Task 无法修**。登记为后续 Task 属唯一合规处置。**接受**。
- **F-03**：`main.rs:44-50`（`register_catalog` 由 WebView 提供 `rel_path`）、`:76-104`（`probe_*`）、`:52-58`（`ttl_override`/`revision` 由 WebView 提供）仍在 `invoke_handler`（`:179-187`）与产品命令共面；收敛需要 capability/ACL/CSP 与「catalog 移回 Core/SQLite」的产品化决策面，超出本切片。**接受**，但前置条件必须与 Review 一致：关闭前不得宣称产品级安全。
  小瑕：所谓「登记」只落在 FIX Handoff 的表格里，仓库内**没有** `proposed` 的子 Task 文件承载这两项（`doc/tasks/` 下无 M2-RC1 后继 Task）。作为「前置项」的持久性弱于 `proposed` Task；建议 Codex 在集成记录中落一个 `proposed` Task。
- 缓解事实在本轮重新核对成立：`tauri.conf.json` `bundle.active=false`、`gen/schemas/capabilities.json` 为空、`csp: null`、`user-source` 不可达（`dto.py:69`、`resource_protocol.rs:50-56`）——与上游判定一致，不构成虚假声明。

### 6.2 F-07 错误码对齐矩阵 — 成立（PASS，带注）

逐条核对 Handoff:43-52 与 Contract §10.2 最小集（`M2-C1_TYPED_IPC_CONTRACT.md:292`，16 项）：

| 码 | 矩阵声明 | Reviewer 独立核对 | 判定 |
|---|---|---|---|
| `REF_MALFORMED`/`REF_UNKNOWN_ID`/`REF_REVOKED`/`REF_EXPIRED`/`REF_SCOPE_DENIED`/`REF_OUT_OF_SCOPE`/`REF_NOT_FOUND` | 已实现（Rust+Python） | `dto.py:72-85` 定义；`resource_protocol.rs:105-114` 状态映射；Python `service.py:175-188`、`handle_resolver.py` 抛出 | 成立 |
| `RESOURCE_TOO_LARGE`/`RESOURCE_LIMIT_EXCEEDED` | 已实现（T1/T2） | `dto.py:80-81`；签发 `service.py:62-69` 测试；handle 侧 `resource_protocol.rs:420-422` | 成立 |
| `FILE_IDENTITY_CHANGED`/`FILE_SIZE_CHANGED`/`CONTENT_DIGEST_MISMATCH`/`OPEN_FAILED_SHARING_VIOLATION` | 已实现（Python+Rust） | `resource_protocol.rs:324,377,415,418,431`；`handle_resolver.py` 对应分支 | 成立 |
| `REF_REPARSE_POINT` | Python 已实现；Rust 无 pre-open walk（句柄 containment 为权威层） | 事实一致：Rust `status_for` 只做映射（`:109`），`verify_and_serve` 无 reparse 检查；权威防线在句柄层，方向 fail-closed | **成立**（现状已如实描述） |
| `REF_READ_ONLY` | 不适用（read-only 通道、无写入口） | 实现中确无写模式请求形状 | 成立（理由充分） |
| `MEDIA_TOO_LARGE_BY_HANDLE` | 语义由 `RESOURCE_TOO_LARGE` 承载；wire 命名按 Contract 允许后续微调 | 实现确实只在 by-handle size 检查点（`resource_protocol.rs:420`、`handle_resolver.py`）报 `RESOURCE_TOO_LARGE`；Contract:292 明文允许「wire naming may be refined in a later contract revision without weakening the semantics」 | **成立但需提示集成方**：这是**真实 wire 名偏离**（语义保真、命名不同），应在集成记录中显式知会，不能当作「已实现同名码」 |
| `REF_SIGNATURE_INVALID` | 不适用（映射 ID 方案无签名 token） | 与 T5.4「映射 ID 方案」一致，签名层无产品面 | 成立 |

两处矩阵小瑕（P3，不单列 finding）：① `REF_UNKNOWN_ID` 出现**两次**（Handoff:45 与 :52 重复行）；② 矩阵只存在于 Handoff 内，未落到可长期引用的 `verification/**` 追溯文件里（对照 M2-C2 的 `clause-source-trace.md` 做法）。

## 7. 无回归与诚实边界（复核清单 6）

### 7.1 无回归 — PASS

- **pytest 原 35 场景语义未被削弱**：`client` 侧所有原用例名在 `.pytest_cache/v/cache/nodeids` 中原样保留（`test_service.py` 由 15→20、`test_handle_resolver.py` 12、`test_bridge_and_thresholds.py` 8，合 40）；逐行阅读 `test_service.py` 的 `TestIssueAndResolve`/`TestLifecycle`/`TestLimits` 未见断言松动（例：`test_active_reference_limit` 仍注入 `max_active_references=4`；`test_sliding_renewal_extends_window` 时钟轨迹与原判定一致）。
- **Rust 原 9 测试**：`main.rs` 现 12 个 `#[test]`，新增 3 条集中在 `:357-449`「M2-RC1-FIX regression tests」段；原有 `url_builder_is_opaque_only`、`malformed_ids_rejected_before_lookup`、`unknown_well_formed_id_typed_404`、`chunk_offset_beyond_size_rejected`、`responses_carry_no_store`、`revoked_id_propagates_typed_410`、`full_chunk_serving_matches_bytes_and_digest_check`、`identity_change_invalidates_cache_entry`、`real_core_sidecar_round_trip` 断言均保留。
- **语义面**：F-01 修复把「缓存命中不查 Core」变为「每请求查 Core」，属**收紧**（原缓存绕过被消除），未见任何放宽。副作用（Core 不可达时不再从缓存服务 → 503 fail-closed）方向正确。
- `resource_protocol.rs:439` 与 `:447` 对同一 chunk **读了两次**（第一次结果丢弃、第二次在身份复核后重读），是 I/O 冗余而非正确性问题，随 `FIX-05` 记录。

### 7.2 诚实边界 — PASS

| 项 | 证据 | 判定 |
|---|---|---|
| S1-B3 / S1-B6 / S1-B8 保持 NOT_RUN | FIX Handoff:69、Task:36/61；`run_e2e.py` 未引入任何清缓存或打包步骤 | **PASS** |
| 冷缓存 1 s 未宣称达标 | FIX Handoff:69「1 s 仍为目标值」；E-07 只测热缓存；`Task:60` 的旧「P95≈1 ms」表述虽过期但未升级为「冷缓存达标」 | **PASS** |
| 无产品级安全/打包就绪宣称 | FIX Handoff:69 明写「不宣称产品级安全或打包就绪」；F-03 未收敛的事实与宣称一致 | **PASS** |
| S1-B11 仍 UNVERIFIED、模型权重未实现 | `dto.py:3-6`、`handle_resolver.py:14-16` 注释保留；T7 无代码 | **PASS** |
| 新增「保守测量」披露 | `App.tsx:196-199` 主动说明 E-07 含 digest 首验成本 | **PASS（正向）** |

## 8. 范围与禁改路径（复核清单 6）

| 方法 | 结果 | 判定 |
|---|---|---|
| 修复轮触碰面（mtime 反演，§2.3） | 最近改动集 = `App.tsx`、`main.rs`、`resource_protocol.rs`、`run_e2e.py`、`test_service.py`、`core_bridge.rs`、`raw/fix-e2e-*`、`raw/e2e-fixtures.json`、`raw/fix-repeat-consistency.json`、`raw/leakage-scan.json`、`doc/handoffs/M2-RC1-FIX-702b02b0.md`、`doc/tasks/M2-RC1.md` —— **全部在授权路径内** | **PASS（间接）** |
| 交付总集 | 旧转录 41 条 + 后续新增 9 条（`final-verification.log`、`run-log.md`、`M2-RC1-39552370.md`、`M2-RC1-f8ce10a2.md`、`dispatch-review-f8ce10a2.md`、3×`fix-e2e`/`fix-repeat`、`M2-RC1-FIX-702b02b0.md`）= 50（HEAD）／49（`702b02b0`）；无禁改路径、无 `doc/contracts/**`、`src/ui/**`、`packaging/**`、根锁文件 | **PASS（间接）** |
| 构建产物 | `target/**`、`frontend/node_modules/**`、`frontend/dist/**`、`.pytest_cache/**`、`__pycache__/**` 均在 `.gitignore`（根 6 行 + `apps/desktop/.gitignore` 3 行）覆盖下，且不在交付清单内；工作区中这些目录确实存在（glob 可见） | **PASS** |
| `git diff --name-status` / `git diff --check` 的**独立复跑** | 无 shell → 无法执行 | **BLOCKED** |
| 工作区洁净度 `git status` | 无 shell → 无法排除「已跟踪文件的未提交修改」 | **BLOCKED** |

## 9. 残留 Findings

> 编号 `FIX-xx` 与上游 `F-xx` 区分。**本轮无 P0/P1 残留**；以下均为证据/记录与 disposition 准确性问题，无实现正确性缺陷。

### FIX-01 [P2] 修复轮四条命令的 Owner 证据未入库，且 Handoff 引用的证据文件是失效版本

- **文件/行**：`doc/handoffs/M2-RC1-FIX-702b02b0.md:56-65`（验证证据表 + 「完整转录：`verification/M2-RC1/final-verification.log`（更新版）」）；`verification/M2-RC1/final-verification.log:1,5,9,14,20-61`（实为 `delivery head 991097d7`／35／9／8／41 路径）。
- **触发条件**：集成方或后续 Reviewer 按 Handoff:65 打开「更新版」日志核对 40/12/8/10 与 exit 0。
- **影响**：按协议 **§6.12①**，无 EXIT 码、无 shell/venv 头、未逐次入库的「N passed」**按未提供处理**；此处连日志都没有，只有散文表格，且被指向的文件是**修复前**的版本（内容与 head 都不对）。审计者会读到 35/9/8 而非 40/12/8，从而误判修复轮未复跑。本 Reviewer 已用 `.pytest_cache`／`results.json`／`test-bin` 指纹交叉证实**计数**正确，但 EXIT 级证据仍缺。
- **复现**：`read verification/M2-RC1/final-verification.log`（61 行，标题 `delivery head 991097d7`）；`grep -r "fix-verification"` 零命中。
- **建议**：修复轮补一份逐次入库的日志（每条命令带 shell/解释器头 + 完整输出尾 + `exit code: N`），例如 `verification/M2-RC1/fix-verification.log`；把 Handoff:31/:65 的指针改到该文件；若无法重跑，则把四条命令记为 `NOT_RUN`/`BLOCKED` 并删除「（更新版）」表述。**纯记录工作，无需改实现。**

### FIX-02 [P2] 判别力证据（「修前 FAIL」）缺失，应以散文代替 artefact 的条目降级

- **文件/行**：`doc/handoffs/M2-RC1-FIX-702b02b0.md:26`（「回归测试**先证明修前 FAIL**（`200 vs 410`）」）、`:27`（「修前 200」）、`:29`（handoff 与 `App.tsx:154-155`「the pre-fix build served 200 here」）。
- **影响**：协议 **§6.12②** 明确要求「判别力证据（对修前失败/对照矩阵）必须是 artefact；artefact 缺失即记 `NOT_RUN`，不得以散文代替」。当前仓库无任何修前失败运行的日志或探针输出。
- **缓解**：逻辑上判别力成立（修前缓存在查 Core 之前返回 `entry.grant.clone()`），本 Reviewer 采信其**方向**，但按协议必须记账为 `NOT_RUN`。
- **建议**：把 Handoff 相应表述改为「修前行为由代码读法推定，判别力 artefact = `NOT_RUN`」，或补一份修前 commit 上跑出 `200` 的日志。

### FIX-03 [P2] F-13 六类覆盖只落实约一半，且未走允许的「降级为部分覆盖」替代路径

- **文件/行**：`tests/m2_resource_channel/test_service.py:139-145`（T2 仍用 4）、`:225-240`（只读面改为「service 无 `write*` 入口」的弱代理）；`doc/tasks/M2-RC1.md:33-34`（AC3/AC4 仍原样 `[x]` 并声称覆盖「只读约束」）；`doc/handoffs/M2-RC1-FIX-702b02b0.md:32`（把 open-once/读后复核「转由 Rust 承担」，但 `main.rs:338-355` 命中的是**读前**身份检查）。
- **缺口清单**：①默认 32 个真实活跃引用 + 第 33 个被拒；②同资源第 17 个引用被拒（`service.py:154-163` 分支）；③adapter 级只读打开断言；④open-once；⑤读后身份复核（`resource_protocol.rs:442-445`）。
- **影响**：上游 F-13 的处置是 `must_record_or_fix`，两条路任选其一。本次既未补齐全部六类，也未在 Task 中把 AC3/AC4 的对应覆盖项降级为「部分覆盖」，因此 AC4/AC3 的 `[x]` 在**覆盖维度**上仍强于实际证据；这些分支（尤其 T2 真实上限与读后复核）回归时可能被静默破坏。
- **建议**：①补 5 条测试（判定成本低、全部可确定性构造）；**或**②在 `doc/tasks/M2-RC1.md:33-34` 明确写「只读约束 / open-once / 读后身份复核 / T2 真实上限 = 部分覆盖（未覆盖清单…）」，并在 Handoff:32 去掉「已由 Rust 承担」的过度表述。

### FIX-04 [P3] F-11 的更正不完整：Task 数字仍过期，修复 head 的 diff 转录未入库

- **文件/行**：`doc/tasks/M2-RC1.md:57`（「30 文件」）、`:58`（`cargo test`「9 passed」）、`:59`（「35 passed」）、`:60`（「热缓存 P95≈1 ms」）；`doc/handoffs/M2-RC1-FIX-702b02b0.md:31,63`（49 文件，无转录）。
- **影响**：Task 与 FIX Handoff 并排呈现两组互相矛盾的数字；`49` 只能由文件清点推算，无法由仓库内 artefact 直接核对。
- **建议**：把 Task:57-60 更新为修复轮口径（49 文件 / 40 passed / 12 passed / P95=88 ms@10.99 MiB），并把 `git diff --name-status 2dca20cd..702b02b0` 的原文转录入库（可并入 FIX-01 的日志）。

### FIX-05 [P3] F-12/F-14 的 disposition 与代码现状不符

- **文件/行**：`doc/handoffs/M2-RC1-FIX-702b02b0.md:38`（F-12「本轮 raw JSON 均带 fixture SHA」）、`:39`（F-14「表述与断言已在修复轮同步更新」）vs 实际：
  - `apps/desktop/frontend/src/resourceChannel/client.test.ts:8-11`：mock 仍生成 **51** 字符 ID 且 URL 仍含 `m2id.v1.` 前缀（真实 `build_url` 剥前缀、段长 43），F-12 指出的「无法发现 ID 长度/形态回归」仍在。
  - `tests/m2_resource_channel/conftest.py:24-28`：冗余导入 `ResourceChannelService as _Svc` 仍在。
  - `pytest.ini:1-2`：无 `markers`/`strict-markers`，`@pytest.mark.slow` 仍未注册（`1 warning` 来源未消除）。
  - `verification/M2-RC1/raw/fix-repeat-consistency.json` 无生成脚本（F-12 的「证据可复现性」未处置）；`leakage-scan.json` 仍只由人工 8 词扫描、无生成器。
  - `resource_protocol.rs:14-16` 的文件头注释未同步 F-02 的 mtime 触发条件。
- **影响**：disposition 声称「已同步」但实为未改，属 Handoff 准确性缺陷（不影响实现正确性）。
- **建议**：把 F-12/F-14 的行改为「未处置（登记后续）」或实际完成；`target` 中 chunk 双读（`resource_protocol.rs:439,447`）与 `SetFilePointer` 返回值未检查（`:337`，在 T1 范围内无实际风险）一并留作 hardening 台账。

## 10. findings_disposition

| ID | 级别 | 处置 | 归属 |
|---|---|---|---|
| **F-01**（上游 P1） | P1 | **closed — 已修复并复验**（代码 + 2 条回归 + e2e 暖缓存变体） | ZCode |
| **F-02**（上游 P2） | P2 | **closed — 已修复并复验**（`verified_mtime` 绑定 + 回归测试） | ZCode |
| **F-04**（上游 P2） | P2 | **closed**（11,525,983 B fixture + p95 87/88 ≤ 200 ms，披露充分） | ZCode |
| **F-11**（上游 P3） | P3 | **partially_closed → FIX-04**（Handoff 已改 49；Task 未改；无 diff 转录） | ZCode |
| **F-13**（上游 P2） | P2 | **partially_closed → FIX-03**（补测约半数；未降级；5 项缺口） | ZCode |
| **F-03**（上游 P2） | P2 | **accepted_deferral**（后续 Task；但需落 `proposed` 子 Task 承载，且关闭前不得宣称产品级安全） | Codex（范围决策） |
| **F-05**（上游 P2） | P2 | **accepted_deferral**（`src/infrastructure/__init__.py` 属禁改路径） | Codex |
| **F-07**（上游 P3） | P3 | **closed**（矩阵逐条成立；MEDIA_TOO_LARGE_BY_HANDLE 为真实 wire 名偏离，需集成记录知会） | ZCode → Codex |
| **F-06/F-08/F-09/F-10/F-12/F-14**（上游 P3） | P3 | **record_only / 部分未处置 → FIX-05** | ZCode |
| **FIX-01** | P2 | **must_fix_before_close（证据入库，无需改实现）** | ZCode |
| **FIX-02** | P2 | **must_record（降级为 NOT_RUN 或补 artefact）** | ZCode |
| **FIX-03** | P2 | **must_fix_or_downgrade（补 5 条测试或明确标注部分覆盖）** | ZCode |
| **FIX-04** | P3 | **must_record** | ZCode |
| **FIX-05** | P3 | **should_fix（修正 disposition 表述或补做）** | ZCode |

## 11. 结论与决定

**决定：`changes_requested`（范围收窄：仅证据与记录层；不要求重写 F-01/F-02 实现）。**

修复轮的核心目标已达成，且经独立交叉核验成立：

- 上游唯一 P1（F-01：暖缓存绕过 Core 撤销）**确实修复**——`resource_protocol.rs:476-487` 每请求无条件 `channel.resolve`，Core 拒绝即逐出缓存条目并 typed 传播；两条定向回归测试（`main.rs:361-382`、`:384-419`）与上游 §9 的复现路径逐字对应；端到端 E-04 已改为「先 `fetchAll` 暖缓存 → `revoke` → 再 `fetchChunk`」，两轮 raw JSON 观测均为 `REF_REVOKED`。
- 同源的 F-02 **确实修复**——`verified_mtime` 绑定 `LastWriteTime`，等大小原地改写（保 file index、bump mtime）触发全量流式重验；回归测试 `main.rs:421-449` 断言 `CONTENT_DIGEST_MISMATCH`。
- F-04 已用 11,525,983 B 的 `typical.png` 重测，p95 87/88 ms ≤ 200 ms，且主动披露「每引用首验 digest 成本」的保守口径。
- 无回归：原 35 pytest 场景与 9 个 Rust 测试语义未见削弱；诚实边界（S1-B3/B6/B8 NOT_RUN、冷缓存未称达标、无产品级安全/打包就绪宣称）完整保留。
- 范围：修复轮触碰面（mtime 反演）与交付总集均落在授权路径内，无禁改路径、无构建产物。

不能转 `approve` 的原因集中在**证据纪律**与**准入项未闭环**，而非实现正确性：

1. 按仓库协议 **§6.12①/②**，修复轮四条命令的 Owner 证据**未带 EXIT 码、未逐次入库**（应「按未提供处理」），且 Handoff 指向的「更新版」`final-verification.log` 实际仍是**修复前**版本（head `991097d7`、35/9/8、41 路径）——审计者会被误导（`FIX-01`）；「修前必 FAIL」的判别力同样只有散文、无 artefact（`FIX-02`）。
2. §11 第 5 条要求的「更正 Handoff/Task 文件数 + 本 head 的 `git diff --name-status` 证据」只完成了一半：Task 仍写 30 文件 / 9 passed / 35 passed / P95≈1 ms（`FIX-04`）。
3. §11 第 7 条要求「按 F-13 补齐六类测试**或**把 AC3/AC4 降级为部分覆盖」：六类中 5 项仍缺，且 Task 未做任何降级标注（`FIX-03`）。

上述三项**全部是低成本记录/补测工作**，不触碰已闭环的实现。建议 Owner 在同一分支追加一个 `docs`/`test` 提交（补修复轮日志 + 更正 Task 数字与覆盖标注 + 降级判别力记账），随后由非作者做一次**限定范围复核**（只需核对 §9 FIX-01…FIX-05 的关闭证据），即可转 `approve`；Codex 若选择接受上述证据风险并先行集成，须在集成记录中显式写出接受理由与遗留项。

---

Reviewer：DeepSeek Harness（非作者）｜reviewed head `702b02b0`（Handoff `7d20b4ca`）｜决定 **changes_requested**｜上游 1×P1+5×P2+7×P3 中 **F-01/F-02/F-04/F-07 已闭环、F-11/F-13 部分闭环、F-03/F-05 登记接受**；新增 3×P2 + 2×P3（`FIX-01`…`FIX-05`，均无实现正确性影响）｜复跑 **BLOCKED**（本会话 shell 因 `SetNamedSecurityInfoW Win32 5` 不可用），已用 reflog + mtime 反演 + 测试残留产物交叉核验
