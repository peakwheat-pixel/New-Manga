---
task_id: M2-RC1 / M2-RC1-FIX（第 4 轮限定范围复核）
reviewer: DeepSeek Harness（非作者）
author: ZCode
base_commit: 2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1
reviewed_head: 2f6a31cd67e983e789c02cb4e33c194f0e012f23
decision: approved
---

# Review：M2-RC1-FIX 第 4 轮限定范围复核 — 仅核对 R-01…R-06 关闭证据（head `2f6a31cd`）

- Task：[M2-RC1](../tasks/M2-RC1.md)（`kind: implementation`，Owner=ZCode）+ 修复轮 `M2-RC1-FIX`
- Reviewer：DeepSeek Harness（**非作者**；实现与三轮修复均由 ZCode 产出，Reviewer 未参与实现，本轮亦未修改任何实现／Task／Handoff／证据文件）
- 仓库/工作区：`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`
- Branch：`agent/zcode/M2-RC1-large-media-resource-channel-runtime`
- 固定 base：`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`
- **被复核 delivery head：`2f6a31cd67e983e789c02cb4e33c194f0e012f23`**（"FIX-3 closure"）
- 上游 review：[`doc/reviews/M2-RC1-FIX-702b02b0.md`](M2-RC1-FIX-702b02b0.md)（第 3 轮，changes_requested，R-01…R-06；其 §12:312 声明本轮只需核对关闭证据即可转 approve）
- 修复 Handoff：`doc/handoffs/M2-RC1-FIX-702b02b0.md`（末尾「复核轮收口（M2-RC1-FIX-3）」:105-125 为逐项处置）
- Contract 固定 blob：`fc35913801297ee1876ea395f9c5041a16226f20`（版本 1.1，§10.1/§10.2）
- 复核日期：2026-09-27
- 报告路径（Reviewer 唯一写路径）：`doc/reviews/M2-RC1-FIX3-2f6a31cd.md`（新路径；复核前经 `glob **/M2-RC1-FIX3*` 确认为不存在，未覆写任何既有 review 文件）

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **approve**（无新 P0/P1/P2；R-01…R-06 全部真实关闭） |
| R-01（P2）证据 head 归属 | **PASS — 已关闭**（§0 显式写出被验证树 + `git rev-parse` + `git status --porcelain` 转录；§6 62 条转录含 `raw/fix-pre-failure-demo.log` 并给出**已入库**结论；标题不再错置 head）。独立复跑 `git diff` = **BLOCKED（本会话 shell 不可用）**，已用 reflog + 全仓 mtime 尾序交叉核验 |
| R-02（P2）Task 数字 | **PASS — 已关闭**（`:57` = 62 文件；`:60` = 75/73 ms @ 11,525,983 B；无 30 文件残留；`49 文件`/`P95≈1 ms` 仅存在于带日期与轮次标签的历史运行记录） |
| R-03（P3）门控与生成器 | **PASS — 已关闭**（`run_e2e.py:145-152` 把 NOT_RUN 计入失败；两个生成器存在且与两份 FIX-3 artefact 结构逐字段一致；一致性 JSON 如实记录 4 条 observed 差异 + 白名单口径 `consistent: true`） |
| R-04（P3）只读断言 | **PASS — 已关闭**（`test_service.py:249-288` 包装模块级 `_k32` 真捕获 `CreateFileW` 实参并委派真实调用；恒真断言已删；43 nodeids + `lastfailed {}` 交叉成立） |
| R-05（P3）mock URL / 头注释 | **PASS — 已关闭**（`client.test.ts:16` URL 只含 43 字符段；`:57-61` 钉住 51/43 形态；`resource_protocol.rs:7-9`/`:15-18` 步骤 2/4 与 F-01/F-02 一致） |
| R-06（P3）E-07 口径 | **PASS — 已关闭**（两份 raw JSON 均为 `E-07-per-reference-first-byte-p95` + `scenario` + `typical.png (11525983 B)`；p95 75/73 ms ≤ 200 ms） |
| 范围与无回归（清单 7） | **PASS**（62 条转录路径全落在 `doc/tasks/M2-RC1.md:41-47` 授权模式内，无禁改路径；Rust 侧仅 `resource_protocol.rs` 头注释变化，已由「全部代码锚点统一 +2 行位移 + `main.rs` 491 行/12 `#[test]` 逐行对齐」独立证实） |
| 诚实边界（清单 8） | **PASS**（S1-B3/B6/B8 保持 NOT_RUN；无产品级安全/打包就绪宣称；E-07 保守口径披露保留） |
| 残留 findings | **无**（R-01…R-06 全部 `closed`；新增 6 条非阻断观察 `O-01`…`O-06`，均不影响可用性与诚实性） |
| 关键能力边界 | 本会话 `pwsh` 完全不可用（见 §1），**所有命令级复跑为 BLOCKED**；计数、门控、artifact 结构与 git 事实均以只读交叉核验取得，未把任何 BLOCKED/NOT_RUN 写成 PASS |

## 1. 复核方法与工具限制（必须先读）

本会话 `pwsh` 在启动阶段即失败，与上游两次 DSH 会话同源：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-RC1-zcode)
```

对默认 `workdir`、指定 `workdir`、以及 `C:\Windows\Temp` 三种形态复现；`sandbox_permissions: danger-full-access` 一次性升级重试被拒：

```text
Error: sandbox escalation to "danger-full-access" requires approval, but no approval channel is available
```

因此本 Reviewer **无法执行任何进程**（`git`、`pytest`、`cargo`、`npm`、`run_e2e.py`、`compare_e2e_runs.py`、`leakage_scan.py` 均不可跑）。**本报告不含任何运行验证**；凡需运行才能闭合的项一律标 `BLOCKED`。

替代核验手段（全部只读：`read` / `glob` / `grep`）：

1. **git 事实**：主仓库 worktree reflog 文本 `G:/CODEX/New Manga/.git/worktrees/M2-RC1-zcode/logs/HEAD`（16 行，末行即 `2f6a31cd`）、worktree `HEAD`（`ref: refs/heads/agent/zcode/M2-RC1-large-media-resource-channel-runtime`）、`refs/heads/agent/zcode/M2-RC1-large-media-resource-channel-runtime`（正文 = `2f6a31cd67e983e789c02cb4e33c194f0e012f23`）。
2. **全仓 mtime 序**（本轮新增的独立证据链）：`glob **/*` 的 12 464 条完整有序清单（spill 文本 `…\0c0e3f63b21f-glob-results.txt`）。该清单按「旧 → 新」排序，**其尾部即全仓最近被写过的文件**；据此可独立判断「最近触碰集」是否越界，并核对 §6 的 62 条转录内容是否与工作区事实吻合（方法局限见 §3.1 与 §7）。
3. **测试计数/来源**：`.pytest_cache/v/cache/nodeids`（43 条）与 `lastfailed`（`{}`）的**内容 + 其在 mtime 清单中的位置**；`main.rs`/`core_bridge.rs`/`resource_protocol.rs` 的行数与 `#[test]` 位置比对。
4. **语义与产物审查**：逐行阅读 `final-verification.log`（178 行）、`doc/tasks/M2-RC1.md`（81 行）、`doc/handoffs/M2-RC1-FIX-702b02b0.md`（125 行）、第 3 轮 review（322 行）、`run_e2e.py`、`compare_e2e_runs.py`、`leakage_scan.py`、两份 `raw/fix3-e2e-results-*.json`、`raw/fix3-repeat-consistency.json`、`raw/fix3-leakage-scan.json`、`raw/fix3-e2e-run{1,2}-console.log`、`raw/fix-pre-failure-demo.log`、`tests/m2_resource_channel/test_service.py`、`src/infrastructure/resource_channel/handle_resolver.py`、`apps/desktop/frontend/src/resourceChannel/client.test.ts`、`client.ts`、`resource_protocol.rs`、`App.tsx`。
5. **手工重算**：按 `compare_e2e_runs.py` 的算法手工对两份 raw JSON 做全字段比对，复算其应产出的一致性报告（见 §3.3）。

**能力边界**：解除条件 = 在 shell 可用且 worktree 可写 ACL 的会话中复跑 §8 所列命令。

## 2. 被复核 head 与工作区事实（独立取得）

### 2.1 head 链（reflog 文本，16 行，独立来源）

```text
2dca20cd ─(reset)→ a0e89f8f → 3948f767 → cd40ef26 →(amend) 7fcc272f →(amend) 991097d7
        → 39552370 → f8ce10a2 → 87ddc878 → 7d5057e7
        → 702b02b0（fix，Handoff 记为 pytest 40）
        → 7d20b4ca（repair-round Handoff） → 844c0395（log rewrite） → a33f3442（FIX-2 closure）
        → 2f6a31cd（FIX-3 closure：R-01…R-06 逐项，末行）
```

- `refs/heads/agent/zcode/M2-RC1-large-media-resource-channel-runtime` = `2f6a31cd67e983e789c02cb4e33c194f0e012f23`，与派发所述 delivery head 一致。
- reflog 共 16 行、无 `amend`/`reset` 尾随记录；**复核期间再次读取仍止于 `2f6a31cd`**（说明本会话内没有新提交）。
- 这独立证实了 `final-verification.log:17-22` 的 head 链叙述（702b02b0→7d20b4ca→844c0395→a33f3442→FIX-3）。

### 2.2 关于「工作区干净」的一处精确化

- 本会话开始时工作区已存在一个 **未跟踪**文件 `verification/M2-RC1/raw/fix3-review-dispatch.log`：其内容为**本次第 4 轮复核会话的直播转录**（含本会话的 `todo_write`、`pwsh` 失败、逐步 `read` 调用），且在本次复核过程中持续增长（第 1 次读 84+ 行 → 随后读得 165 行）。它与 `2f6a31cd` 的 reflog 时间戳无冲突，且 reflog 期间无新提交，故可判定它**晚于被复核 head 产生、不在 `2dca20cd..2f6a31cd` 内**。
- 因此严格意义的「`git status --porcelain` 为空」无法成立（存在该复核派发/插桩副产物；本报告落盘后同样会新增一个未跟踪文件）。这**不影响**本轮任何结论：它不属于被复核交付，也不改变 62 条转录的路径集合。见 `O-06`。
- 未执行 `git status --porcelain`（无 shell），故该判断基于「文件内容晚于 head + reflog 无新提交」的推理，而非命令输出。

## 3. 逐项复核（R-01…R-06）

### 3.1 R-01 [P2] `final-verification.log` 的 head 归属与 62 条转录 — **PASS（已关闭）；独立复跑 BLOCKED**

| 派发要求 | 证据 | 判定 |
|---|---|---|
| §0 写清被验证 head（a33f3442 + FIX-3 dirty tree） | `final-verification.log:5-16`：`Verified tree: HEAD = a33f34422f8604448954ccccf490605c4b4243f3 (commit "FIX-2 closure") plus the FIX-3 working-tree changes`，并逐项列出 FIX-3 触碰的 5 个代码路径与后置文档路径 | **PASS** |
| 附 `git rev-parse` 转录 | `:23`「`git rev-parse HEAD` at run time: `a33f34422f8604448954ccccf490605c4b4243f3`」 | **PASS** |
| 附 `git status --porcelain` 转录 | `:25-44` 代码块共 **16 条**（`M`/`A` 前缀齐全，含 ` M doc/tasks/M2-RC1.md` 的未暂存形态），与 Handoff:118「只新增/修改 porcelain 所列 16 路径」一致 | **PASS** |
| 标题不再错置 head | `:1` 标题为 `M2-RC1 final verification runs — FIX-3 ROUND (records/evidence closure after DSH round-3 review)`，不含任何 head SHA；`:19-22` 显式声明旧的「delivery head 702b02b0」标题错配即 R-01 并已改写 | **PASS** |
| §6 为 62 条 diff 转录 | `:99-174`；代码块 `:112-173` 逐条计数 = **62**（61×`A` + 1×`M pytest.ini`），与 `:104` 的「49 @702b02b0 → 53 @a33f3442 → 62 @FIX-3」演进一致（53 + 9 新路径 = 62：2 个生成器、6 个 fix3 raw artefact、1 份 round-2 review 归档） | **PASS（计数与内容）** |
| 含 `raw/fix-pre-failure-demo.log` 且给出已入库结论 | 转录 `:163` = `A verification/M2-RC1/raw/fix-pre-failure-demo.log`；`:101-104` 明确「**is tracked** — it entered the tree in commit `a33f3442` (FIX-2 closure, git add -A)」，并说明旧 49 条为 `702b02b0` 时代清单 | **PASS** |
| **独立复跑** `git diff --name-status 2dca20cd..2f6a31cd` | 无 shell | **BLOCKED** |

**BLOCKED 项的替代核验（不构成等价复跑，仅作独立佐证）**：

1. **被验证树的一切数字都有 head 可归属**：`a33f3442` 出现在 §0（`:5`、`:23`）与 Handoff:118，不再是第 3 轮所指的「从未出现的 SHA」。
2. **§6 声明的命令是 `git diff --cached --name-status 2dca20cd`（运行时刻的 index 快照），而非 commit..commit**（`:106-109` 如实写明）。两者路径集合在本例等价，理由有二：① 该 index = a33f3442 tree + 16 条 FIX-3 暂存改动 → 53 + 9 = 62；② 运行之后才被 finalise 的两个路径（`doc/handoffs/M2-RC1-FIX-702b02b0.md`、本日志自身）在 a33f3442 时代已是 `A`，只改变内容不改变路径集合（见下条 mtime 证据）。
3. **全仓 mtime 尾序独立佐证 62 集合**：12 464 条有序清单的最后一段为 `:12373` `pytest.ini`（FIX-2）→ `:12374` `tests/m2_resource_channel/conftest.py`（FIX-2）→ `:12381` `doc/reviews/M2-RC1-FIX-702b02b0.md` → `:12382` `test_service.py` → `:12383` `client.test.ts` → `:12384` `resource_protocol.rs` → `:12385` `App.tsx` → `:12386` `run_e2e.py` → `:12387` `compare_e2e_runs.py` → `:12388` `leakage_scan.py` → `:12389` `doc/reviews/…-round2.md` → `:12391` `.pytest_cache/v/cache/nodeids` →（`target/release` 构建产物）→ `:12455-12460` 6 个 `raw/fix3-*` artefact → `:12461` `doc/tasks/M2-RC1.md` → `:12462` `final-verification.log` → `:12463` `doc/handoffs/M2-RC1-FIX-702b02b0.md` → `:12464` 本次复核的未跟踪日志。
   **除上述授权路径外，尾段没有出现任何其他被触碰路径**——即不存在「既不在 62 条内、又在运行后被写入」的路径，故 62 条转录的内容与工作区事实自洽。
4. **62 条中每一条在工作区中都真实存在**（`verification/M2-RC1/**` 22 个文件已由 `glob` 全量列出；`apps/desktop/src-tauri/src/` 恰 3 个 `.rs`；其余路径逐一 read/grep 时均已打开），无凭空条目；`pytest.ini` 的 `M` 亦与 `:107-109` 的说明（FIX-2 轮注册 `slow` marker）一致。

**结论：R-01 关闭。** 残留限制：无 shell，`git diff` 与 `git status` 未独立复跑；「工作区干净」以推理而非命令输出确认。

### 3.2 R-02 [P2] Task 数字口径 — **PASS（已关闭）**

| 要求 | 现状（`doc/tasks/M2-RC1.md`） | 判定 |
|---|---|---|
| RC1-AC1 行改「62 文件」 | `:57`「executed 2026-09-27：全项一致；**62 文件**（FIX-3 delivery head；head 链 702b02b0→a33f3442→FIX-3，49→53→62 演进见 final-verification.log §6 转录）全授权路径」 | **PASS** |
| RC1-AC5 行改「E-07 每引用首字节 P95 = 75/73 ms @ 11,525,983 B」 | `:60`「E-07 每引用首字节 **P95 = 75/73 ms @ 11,525,983 B**（≤200 ms 预算；每样本含新引用首验全量 digest 流——冷 grant 缓存/暖 OS 页缓存口径，R-06 改名后如实标注）；**冷页缓存 S1-B6 NOT_RUN**」 | **PASS（逐字符合）** |
| 不再有未标注的 30 文件 | 全文 grep `30 文件` = **0 命中** | **PASS** |
| 不再有未标注的 49 文件 / P95≈1 ms | `49 文件` 仅两处：`:57`（作为「49→53→62 演进」的历史刻度，已被 62 覆盖）与 `:71`（`2026-09-27（Owner ZCode，修复交付）` 修复轮当时的日期化运行记录）。`P95≈1 ms` 仅一处：`:76`（`2026-09-27（Owner ZCode，实现交付）` 原始交付轮的日期化运行记录，当时 fixture 为 49 KB）。二者均带日期与轮次标签，**只描述当时口径**，且当前口径行 `:57`/`:60`/`:70` 已改为 62/75-73 ms，不再互相矛盾 | **PASS（符合「历史轮次运行记录中的当时数字允许保留」）** |

`:34` 的 RC1-AC4「部分覆盖标注」保留（open-once 计数与读后复核直接外部断言不可构造），与 R-04 的处置方向一致。

### 3.3 R-03 [P3] runner 门控 + 一致性/泄漏生成器 — **PASS（已关闭）**

| 要求 | 证据 | 判定 |
|---|---|---|
| `run_e2e.py` 把 NOT_RUN 计入门控失败 | `:145-151` 注释「R-03: NOT_RUN is a gate failure, not a pass — the runner must be able to tell "scenario did not run" apart from "scenario passed"」；`failed = statuses.get("FAIL",0) + statuses.get("MISSING",0) + statuses.get("NOT_RUN",0)`；`:152` `return 0 if exit_code == 0 and failed == 0 else 1`。这条门控正对 `App.tsx:236`（E-08）与 `:248`（E-09）的 `NOT_RUN` 兜底——此前两者会让 runner 仍 `exit 0` | **PASS** |
| `compare_e2e_runs.py` 存在且为 `raw/fix3-repeat-consistency.json` 的生成器 | `compare_e2e_runs.py:1-119` 存在；其 `report` 字段（`:89-112`）与 JSON 的 12 个键**逐字段一致**，JSON `:2` 自带 `"generator": "verification/M2-RC1/compare_e2e_runs.py"`；`:114` 打印 `consistent=… -> out` 并以 `consistent` 决定退出码 | **PASS** |
| `leakage_scan.py` 存在且为 `raw/fix3-leakage-scan.json` 的生成器 | `leakage_scan.py:1-76` 存在；`report` 字段（`:62-68`）与 JSON 逐字段一致，JSON `:2` 自带 `"generator": "verification/M2-RC1/leakage_scan.py"`；9 个 `FRAGMENTS`（`:17-27`）与 JSON `:7-17` 相同 | **PASS** |
| fix3 一致性 JSON 如实记录 observed 差异、而非 `differences: {}` | `raw/fix3-repeat-consistency.json:14-57` 记录**恰 4 条**真实差异：E-06 `observed.first`（`lYS0b-jpm4` vs `vkE91UMmvM`）、E-06 `observed.second`（`RWd-0MR65w` vs `F_sgL8tgWA`）、E-07 `observed.p95_ms`（75 vs 73）、E-07 `observed.timings_ms`（`[73,73,73,73,74,74,74,75]` vs `[70,70,70,71,71,72,72,73]`）；`:11-13` status/缺失集全空；`:58` `unclassified_differences: []`；**无 `differences` 字段** | **PASS** |
| 以白名单口径定义 `consistent=true` | `compare_e2e_runs.py:23-28` 定义 `NONDETERMINISTIC`；`:78-81` 仅对不在白名单内的字段记入 `unclassified`；`:83-88` `consistent = 无 status 差异 ∧ 无缺失 id ∧ 无 unclassified`；`:109-111` 注释明确「NOT "no differences"」。JSON `:59-71` 回显该白名单（含 pre-rename 的 `E-07-hot-cache-p95` 兼容项），`:72` `"consistent": true` | **PASS** |

**独立手工重算**（按生成器算法对两份 raw JSON 做全字段 flatten 比对）：id 集合 10/10 相同、status 全 `PASS`、差异字段恰为上列 4 条，其余（E-00..E-05、E-08、E-09）逐字段相同 ⇒ 生成器应输出 `unclassified: []`、`consistent: true`，**与落盘 JSON 完全一致**。泄漏扫描同法复算：`typical.png` 命中 2 次（分别落在两份 raw JSON 的 E-07 `fixture` 标签内，`raw/fix3-leakage-scan.json:18-31`），其余 8 个片段 0 命中，`unclassified_hits: []` ⇒ 与 `final-verification.log:92-94`（"2 hits, both the probe-authored typical.png scenario label, 0 unclassified"）一致。

### 3.4 R-04 [P3] 只读约束断言改为真捕获 — **PASS（已关闭）**

| 要求 | 证据 | 判定 |
|---|---|---|
| 包装模块级 `_k32` 真捕获 `CreateFileW` 实参 | `test_service.py:256-271`：`import infrastructure.resource_channel.handle_resolver as resolver_mod` → 定义 `_K32Spy`（`:260-269`，`CreateFileW` 记录 `(name, desired_access, share_mode)` 后 `return self._real.CreateFileW(...)`，`__getattr__` 委派其余 API）→ `monkeypatch.setattr(resolver_mod, "_k32", _K32Spy(resolver_mod._k32))`。`handle_resolver.py:54` 的 `_k32 = ctypes.WinDLL("kernel32", …)` 是模块级全局，`:104-114` 的 `_open_read_handle` 在调用时按全局查找，故 monkeypatch 对真实实现路径生效 | **PASS** |
| 断言 GENERIC_READ-only、无 GENERIC_WRITE | `:278` `assert captured, "CreateFileW was never invoked through the resolver"`；`:280-282` 对**每一次捕获调用**断言 `access == resolver_mod.GENERIC_READ` 且 `access & resolver_mod.GENERIC_WRITE == 0`；`:283-286` 断言 share 模式只能是 `FILE_SHARE_READ` 或 `FILE_SHARE_READ|FILE_SHARE_WRITE` | **PASS** |
| narrow / share_write 两分支 share 模式各归其位 | `:275` `reader.read(grant, opaque)`（narrow）与 `:276` `reader.read(grant, opaque, share_write=True)`（宽共享）；`:287-288` 断言 `share_modes` 同时包含 `FILE_SHARE_READ` 与 `FILE_SHARE_READ|FILE_SHARE_WRITE`。两分支均有真实产生者（`handle_resolver.py:110` `share = FILE_SHARE_READ|FILE_SHARE_WRITE if share_write else FILE_SHARE_READ`，`:288` 由 `read(..., share_write=...)` 透传） | **PASS** |
| 断言不再恒真 | 第 3 轮所指的「把模块常量写给自己再断言」写法已不存在：`captured` 只由 spy 内的真实实参填充（`:264-266`），断言对象是实参而非常量回显。若实现改为写模式打开，`access == GENERIC_READ` 必失败 | **PASS** |
| pytest 43 passed 交叉核验 | `.pytest_cache/v/cache/nodeids:2-44` = **43 条**（`test_bridge_and_thresholds.py` 8 + `test_handle_resolver.py` 12 + `test_service.py` 23，含 `TestF13CoverageAdds` 8 条）；`.pytest_cache/v/cache/lastfailed:1` = `{}`。**且 mtime 序证明该缓存来自 FIX-3 运行**：清单 `:12382` `test_service.py` → `:12390` 其 `__pycache__` → `:12391` `.pytest_cache/v/cache/nodeids`，即 pytest 在全部 FIX-3 源码改动之后运行 | **PASS（计数/零失败；命令复跑 BLOCKED）** |

### 3.5 R-05 [P3] 前端 mock URL 形态 + Rust 头注释同步 — **PASS（已关闭）**

| 要求 | 证据 | 判定 |
|---|---|---|
| mock URL 只含 43 字符段 | `client.test.ts:9-13` 生成 `segment`（`padEnd(43,"0").slice(0,43)`，base36 字符集本就在 `[A-Za-z0-9_-]` 内，`replace` 为兜底）；`:13` `opaque = m2id.v1.${segment}`；`:16` `url: http://m2res.localhost/m2id/${segment}` —— URL 路径**只含 43 字符段，不含 `m2id.v1.` 前缀**，与 `resource_protocol.rs:554-556` 的 `build_url`（`rsplit('.')` 取末段）一致 | **PASS** |
| 51/43 形态断言 | `:57` `expect(issued.opaqueId).toMatch(/^m2id\.v1\.[A-Za-z0-9_-]{43}$/)`；`:58` `expect(issued.opaqueId.length).toBe(51)`；`:59-61` `issued.url.slice(prefix.length)` 匹配 `/^[A-Za-z0-9_-]{43}$/`（URL 段恰 43）。字段映射已核对：`client.ts:61-65` 从 `opaque_id` 取 `opaqueId` | **PASS** |
| `resource_protocol.rs` 头注释步骤 2 与 F-01 一致 | `:7-9`「2. EVERY request resolves via the Core control bridge **before** the grant cache is consulted (F-01): a Core rejection evicts the cached entry and propagates typed errors (REF_UNKNOWN_ID / REF_REVOKED / REF_EXPIRED)」，与 `:478-486` 的实现（`:486` `remove(&full_id)`）一致；第 3 轮所指的「grant cache miss ⇒ resolve」表述已不存在 | **PASS** |
| 头注释步骤 4 与 F-02 一致 | `:15-18`「4. the issue-time digest is re-verified through the handle whenever the grant has **never been verified OR its LastWriteTime moved** since the last verification (F-02: catches equal-size in-place rewrites) without materialising the file」，与 `:429` `needs_digest = !entry.digest_verified || entry.verified_mtime != Some(mtime)` 一致；第 3 轮所指的「first-verified grant also streams the whole file once」已改写 | **PASS** |

### 3.6 R-06 [P3] E-07 新 id / 口径标签 / 精确字节 — **PASS（已关闭）**

| 要求 | 证据 | 判定 |
|---|---|---|
| 新 id `E-07-per-reference-first-byte-p95` | `raw/fix3-e2e-results-first.json:52` 与 `raw/fix3-e2e-results-repeat.json:52` 均为该 id；`raw/fix3-e2e-run1-console.log:14`、`run2-console.log:14` 同名；`App.tsx:211` `record("E-07-per-reference-first-byte-p95", …)`；旧 id `E-07-hot-cache-p95` 仅作为历史兼容项留在 `compare_e2e_runs.py:27` 白名单注释中 | **PASS** |
| `scenario` 口径标签 | 两份 JSON `:67` 均为 `"scenario": "per-reference first-byte (cold grant cache, warm OS page cache)"`（`App.tsx:217` 同源）；对应 `App.tsx:194-199` 与 `doc/tasks/M2-RC1.md:60` 的保守性说明「每样本含新引用首验全量 digest 流」 | **PASS** |
| 精确字节 `typical.png (11525983 B)` | 两份 JSON `:66` 均为 `"fixture": "typical.png (11525983 B)"`（`App.tsx:216` 同源）；与 `run_e2e.py:46`（`write_noise_png(… 1600, 2400, seed=5202)`）及 `raw/e2e-fixtures.json` 的 `typical.bytes=11525983` 口径一致，不再是 `~11.5 MiB` | **PASS** |
| **E-07 p95 实测 75/73 ms ≤ 200 ms** | run1 `:55` `p95_ms: 75`（timings `:56-65` = 73…75）；run2 `:55` `p95_ms: 73`（timings = 70…73）；两轮 status 均 `PASS`（`:53`），判定式 `App.tsx:212` `status: p95 <= 200 ? "PASS" : "FAIL"`；`p95 = timings[min(len-1, floor(len*0.95))]`（`:210`，len=8 → 取最大值，保守）。75/73 ≤ 200 ⇒ 结论不变 | **PASS（数字；命令复跑 BLOCKED）** |

### 3.7 清单 7：范围与无回归 — **PASS**

| 复核点 | 证据 | 判定 |
|---|---|---|
| 62 条路径全部落在 Task 授权路径内 | 逐条归类（`final-verification.log:112-173`）：`apps/desktop/**`（22 条）、`doc/handoffs/M2-RC1-*.md`（2）、`doc/reviews/M2-RC1-*.md`（3）、`doc/tasks/M2-RC1.md`（1）、`pytest.ini`（1）、`src/application/resource_channel/**`（4）、`src/infrastructure/resource_channel/**`（4）、`tests/m2_resource_channel/**`（4）、`verification/M2-RC1/**`（21）= 62，全部落在 `doc/tasks/M2-RC1.md:41-47` 的授权模式内 | **PASS（转录级 + 存在性核验）** |
| 无禁改路径 | 列表内**无** `doc/contracts/**`、`src/ui/**`、`src/bootstrap/app.py`、非 resource_channel 的 `src/**`、`packaging/**`、根目录依赖/锁文件、AD-001、M2-S1/S2/C2/S3 原报告。**独立佐证（mtime 尾序）**：全仓清单中 `doc/contracts\**` 位于 `:44-48`、`packaging\**` 位于 `:477-480`、`src\bootstrap\**` 位于 `:551-553`、`src\ui\**` 位于 `:646-692`，与最近触碰段（`:12373-12464`）相差约 1.2 万条，说明这些禁改面**近期未被写入** | **PASS** |
| 非 resource_channel 的 `src/**` | 全仓 `src/**/*.py` 192 条的 mtime 尾序**末 8 条恰为** `src/application/resource_channel/{dto,ports,__init__,service}.py` 与 `src/infrastructure/resource_channel/{__init__,handle_resolver,scope,host_bridge}.py`，其余 `src/**`（含 `src/ui/**`、`src/bootstrap/app.py`、`src/domain/**`、`src/ports/**`）全部更旧 | **PASS** |
| Rust 实现文件本轮除 `resource_protocol.rs` 头注释外无改动 | ① porcelain `:30` 仅列 `resource_protocol.rs`；② `apps/desktop/src-tauri/src/` 恰有 3 个 `.rs`（`core_bridge.rs`、`main.rs`、`resource_protocol.rs`）；③ **头注释以外为纯注释改动的独立证明**：`resource_protocol.rs` 现 570 行（第 3 轮实测 568 行），第 3 轮引用的**全部代码锚点统一 +2 行位移**——`typed_error` `:116→:118`、`CachedGrant` `:59→:61`（`verified_mtime` 字段 `:67`）、`identity_size_mtime` `:267→:269`、`OPEN_FAILED_SHARING_VIOLATION` `:324→:326`、未检查的 `SetFilePointer` `:337→:339`、host 白名单 `:467→:469`、每请求 resolve `:476→:478`、`build_url` `:552→:554`、`FILE_IDENTITY_CHANGED` `:415→:417` / `FILE_SIZE_CHANGED` `:418→:420` / `RESOURCE_TOO_LARGE` `:420-422→:423` / `needs_digest` `:424-435→:429`；④ `main.rs` **491 行**（与第 3 轮一致）、恰 **12** 个 `#[test]`（`:270,278,288,297,307,315,325,338,361,384,421,453`），F-01/F-02 回归函数位于第 3 轮所引的**完全相同**的行号（`:339`、`:362`、`:385`、`:422`）⇒ `main.rs` 未被 FIX-3 触碰 | **PASS（间接但多点一致）** |
| 独立复跑 `git diff a33f3442..2f6a31cd -- apps/desktop/src-tauri/src/` | 无 shell | **BLOCKED** |

**旁注（非 finding，见 `O-03`）**：62 条中的 `pytest.ini` 是**根目录文件**，不在 `doc/tasks/M2-RC1.md:41-47` 的枚举授权清单内（但它既不属于 `:51` 的「根目录依赖/锁文件」，也未被 `:51` 列举禁止；§6:107-109 已主动披露其唯一改动为 FIX-2 轮注册 `slow` marker）。

### 3.8 清单 8：诚实边界 — **PASS**

| 项 | 证据 | 判定 |
|---|---|---|
| S1-B3 / S1-B6 / S1-B8 保持 NOT_RUN | `doc/tasks/M2-RC1.md:36`（未实测项保持 `UNVERIFIED`/`NOT_RUN` 并列解锁条件）、`:61`（S1-B3/S1-B8 NOT_RUN；S1-B5 部分；S1-B6 NOT_RUN）；Handoff:69（S1-B3/B6/B8 保持 NOT_RUN；S1-B11 仍 UNVERIFIED） | **PASS** |
| 无产品级安全/打包就绪宣称 | 同上两处均写「**不宣称产品级安全或打包就绪**」；F-03/F-05 仍为 `accepted_deferral`（Handoff:28,30,100,123）；`verification/M2-RC1/run_e2e.py` 未引入清缓存或打包步骤 | **PASS** |
| E-07 保守口径披露保留 | `App.tsx:194-199` 说明每样本含新引用首验全量 digest 流、冷页缓存属 S1-B6 且保持 `NOT_RUN`；两份 raw JSON `:67` 的 `scenario` 标签与 `doc/tasks/M2-RC1.md:60` 的「冷 grant 缓存/暖 OS 页缓存」一致；`:60` 同时写「**1 s 仅为目标未称达标**」 | **PASS** |
| 修前失败判别力如实降级 | `raw/fix-pre-failure-demo.log:1-15` 仍为 `Status: NOT_RUN`（§6.12② 口径），并给出替代论证链（review 复现路径 + 修后 cargo 12/12 对照） | **PASS** |
| S1-B11 仍 UNVERIFIED、模型权重未实现 | Handoff:69；Task:36 | **PASS** |

## 4. 本轮观察（非 finding、非阻断）

| ID | 观察 | 依据 | 影响 |
|---|---|---|---|
| **O-01** | `final-verification.log:8-9` 的措辞「The FIX-3 delivery commit adds/modifies **only the paths in that porcelain list**」在字面上不成立：`2f6a31cd` 还 finalise 了 `doc/handoffs/M2-RC1-FIX-702b02b0.md` 与 `verification/M2-RC1/final-verification.log` 本身（二者均不在 :27-44 的 16 条内）。紧接的 `:14-16` 已承认「doc/tasks、doc/handoffs、doc/reviews、this log 在运行后 finalise」。mtime 序亦证实这两份文件是在 FIX-3 代码批次（:12383-12389）之后写入（`:12462`/`:12463`） | 62 条**路径集合**不受影响（两者在 a33f3442 时代已是 `A`，只改内容），故 R-01 的 62 计数成立 | 表述精度；建议后续把该句改为「FIX-3 的**代码**改动限于该清单；doc/证据路径的最终定稿在运行之后」 |
| **O-02** | `compare_e2e_runs.py:24` 对 E-06 的白名单是整棵 `observed` 子树（`{"observed"}`），比第 3 轮建议的「E-06 随机段」更宽——E-06 的 observed 内容如发生变化（非仅随机片段）也会被记为可接受 | E-06 目前只含 `first`/`second` 两个随机引用片段（两份 raw JSON `:46-49`），实际不削弱本轮结论 | 口径略宽；后续若 E-06 增加确定性字段，应把白名单收窄到具体字段 |
| **O-03** | `pytest.ini`（根目录）属 62 条之一，但不在 Task 的枚举授权清单内（也不在禁止清单内） | `final-verification.log:107-109` 已主动披露；Task:51 禁改项为「根目录依赖/锁文件」，`pytest.ini` 非依赖/锁文件 | 建议集成记录知会；不阻断 |
| **O-04** | `doc/reviews/M2-RC1-FIX-702b02b0-round2.md`（第 2 轮 DSH 报告的归档副本）由 ZCode 提交，而 `doc/tasks/M2-RC1.md:46` 规定 `doc/reviews/M2-RC1-<reviewed-head>.md` 仅由非作者 Reviewer 编写。已核对该文件 `:1-13` 头部（reviewed head `702b02b0`、changes_requested、FIX-01…FIX-05）与第 2 轮 review 的自述一致，属**内容保真归档** | Task:72、Handoff:118、`final-verification.log:105` 均如实说明该归档动作与原因（原路径被第 3 轮报告取代） | 属流程边界而非内容失真；未做逐字节比对（无 shell） |
| **O-05** | R-04 的断言仍以 `resolver_mod.GENERIC_READ` / `GENERIC_WRITE` 常量作比较基准：若有人**同时**把模块常量改成写语义，断言会自洽通过 | `test_service.py:281-282` 对比的是捕获实参与同模块常量；但恒真性已消除（若实现改传 `GENERIC_WRITE` 字面量或改 share 模式，断言必失败） | 残余盲点，低风险；如需彻底消除可改为断言字面量 `0x8000_0000` / `0` |
| **O-06** | 工作区存在**未跟踪**的 `verification/M2-RC1/raw/fix3-review-dispatch.log`，内容为本次第 4 轮复核会话的直播转录（含本会话工具调用），在复核期间持续增长；reflog 在同期无新提交，故其晚于 `2f6a31cd`、不属于交付 | 该文件内容（session `session-308b366e-…`）与本会话逐步动作一致；`glob verification/M2-RC1/**` 首次调用即已列出它；reflog 两次读取均止于 `2f6a31cd` | 「工作区干净」需按此精确化；不影响 62 条转录与任何结论。本报告落盘后同样会新增一个未跟踪文件 |

## 5. findings_disposition

| ID | 上游/上轮对应 | 级别 | 本轮处置 | 关闭证据（行号） | 归属 |
|---|---|---|---|---|---|
| **R-01** | 第 3 轮 P2 | P2 | **closed** | `final-verification.log:1`（标题无 head）、`:5-16`（被验证树）、`:23`（rev-parse）、`:25-44`（porcelain 16 条）、`:99-174` + `:112-173`（62 条）、`:101-104`（`raw/fix-pre-failure-demo.log` 已入库结论）、`:163`（该条转录）；reflog `:16`、`refs/heads/…`；mtime 尾序清单 `:12373-12464` | ZCode |
| **R-02** | 第 3 轮 P2 / 上轮 FIX-04、F-11 | P2 | **closed** | `doc/tasks/M2-RC1.md:57`（62 文件）、`:60`（75/73 ms @ 11,525,983 B）；`30 文件` 0 命中；`49 文件`/`P95≈1 ms` 仅存于 `:71`/`:76` 的日期化历史运行记录 | ZCode |
| **R-03** | 第 3 轮 P3 / 上轮 F-12、F-14 | P3 | **closed** | `run_e2e.py:145-152`；`compare_e2e_runs.py:23-28,61-88,109-114`；`leakage_scan.py:17-27,62-72`；`raw/fix3-repeat-consistency.json:14-57,58,59-72`；`raw/fix3-leakage-scan.json:18-32`；`final-verification.log:88-94` | ZCode |
| **R-04** | 第 3 轮 P3 / 上轮 FIX-03、F-13⑦ | P3 | **closed** | `test_service.py:249-288`（真捕获 + 委派 + 两分支断言）；`handle_resolver.py:54,104-114`；`.pytest_cache/v/cache/nodeids:2-44`（43）、`lastfailed:1`（`{}`）；mtime 清单 `:12382,12390,12391` | ZCode |
| **R-05** | 第 3 轮 P3 / 上轮 FIX-05、F-12 | P3 | **closed** | `client.test.ts:9-16,55-61`；`client.ts:61-65`；`resource_protocol.rs:7-9,15-18`（实现侧 `:429,478-486`） | ZCode |
| **R-06** | 第 3 轮 P3 / 上轮 F-04 标签瑕疵 | P3 | **closed** | `raw/fix3-e2e-results-first.json:52,53,55,66,67`；`raw/fix3-e2e-results-repeat.json:52,53,55,66,67`；`App.tsx:210-217`；`raw/fix3-e2e-run{1,2}-console.log:6,14,17` | ZCode |
| F-01 | 上游 P1 | P1 | **closed（第 3 轮已确认，本轮不重开）** | `resource_protocol.rs:478-486`（每请求 resolve + 逐出 + typed）；`main.rs:361-382`、`:384-419`；E-04 两轮 `REF_REVOKED`（`raw/fix3-e2e-results-*.json:34-37`） | ZCode |
| F-02 | 上游 P2 | P2 | **closed（第 3 轮已确认，本轮不重开）** | `resource_protocol.rs:429-433`（mtime 触发重验）；`main.rs:421-449` | ZCode |
| F-04 / F-07 | 上游 P2 / P3 | — | **closed（第 3 轮已确认；F-04 标签瑕疵本轮由 R-06 关闭）** | `raw/fix3-e2e-results-*.json:52-68`；Handoff:41-52 | ZCode |
| F-11 / F-13 | 上游 P3 / P2 | — | **closed（分别经 R-02 / R-04 关闭）** | 同上 | ZCode |
| F-03 / F-05 | 上游 P2 / P2 | P2 | **accepted_deferral（不因本轮改变）**；仍只在 Handoff 散文中，`doc/tasks/` 下无 `proposed` 子 Task | Handoff:28,30,100,123；Task:66 | **Codex（范围决策）** |
| F-06/F-08/F-09/F-10/F-12/F-14 | 上游 P3 | P3 | **record_only / 部分修复（第 3 轮结论保留）** | 第 3 轮 review §11:281 | ZCode → Codex |
| FIX-01…FIX-05 | 第 2 轮 | — | **经 R-01…R-06 全部闭合**（FIX-01→R-01、FIX-03→R-04、FIX-04→R-02、FIX-05→R-05；FIX-02 已于第 3 轮 closed） | 同上 | ZCode |

**本轮无新 P0/P1/P2。** 6 条观察 `O-01`…`O-06` 均为表述精度、口径宽度或流程边界，不影响 approve。

## 6. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 四条命令复跑 | `python -m pytest tests/m2_resource_channel -q`；`cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked`；`npm test --prefix apps/desktop/frontend -- --run`；`python verification/M2-RC1/run_e2e.py` ×2 | 被验证树 `a33f3442` + FIX-3 改动；`2f6a31cd` | **BLOCKED**（本会话 `pwsh` 不可用，`danger-full-access` 升级被拒） | §1 |
| pytest 计数/零失败 | 静态读取缓存 | `2f6a31cd` | **PASS（交叉核验）** | `.pytest_cache/v/cache/nodeids:2-44` = 43；`lastfailed:1` = `{}`；mtime 清单 `:12391` 位于 test_service 改动之后 |
| cargo 12 passed | 静态计数 | 同上 | **PASS（交叉核验）** | `main.rs` 491 行、12 个 `#[test]`（`:270,278,288,297,307,315,325,338,361,384,421,453`） |
| vitest 8 passed | 静态计数 | 同上 | **PASS（交叉核验）** | `client.test.ts` 8 个 `it(`（`:28,37,40,43,49,66,79,92`） |
| e2e 10/10 ×2 | 静态读取两份 raw JSON + 两份 console log | 同上 | **PASS（交叉核验）** | `fix3-e2e-results-{first,repeat}.json:4-83`（各 10 条全 `PASS`）；`fix3-e2e-run{1,2}-console.log:6,17`（`exit_code=0`、`summary: {'PASS': 10}`） |
| 一致性 artefact 可复算 | 按 `compare_e2e_runs.py` 算法手工全字段比对两份 raw JSON | 同上 | **PASS** | 与 `raw/fix3-repeat-consistency.json` 逐字段一致（§3.3） |
| 泄漏扫描可复算 | 按 `leakage_scan.py` 片段表手工复核 | 同上 | **PASS** | 2 命中（`typical.png` 探针标签）、0 unclassified（`raw/fix3-leakage-scan.json:18-32`） |
| `git rev-parse HEAD` / `git status --porcelain` / `git diff --name-status 2dca20cd..2f6a31cd` / `git diff --check` | 无 shell | `2f6a31cd` | **BLOCKED** | 替代：reflog、refs、mtime 尾序、62 条存在性与归类（§2、§3.1、§3.7） |
| `git diff a33f3442..2f6a31cd -- apps/desktop/src-tauri/src/` | 无 shell | 同上 | **BLOCKED** | 替代：行数 + 锚点统一 +2 位移 + `main.rs` 行号完全对齐（§3.7） |
| Contract blob `fc359138…` 复核 | 无 shell（无法计算 blob 哈希） | 同上 | **BLOCKED** | 本轮无 `doc/contracts/**` 触碰（62 条 + mtime 尾序双重佐证），blob 未变的结论与第 3 轮一致 |
| 诚实边界逐项 | read/grep | 同上 | **PASS** | §3.8 |

**Architecture 面（本轮限定范围）**：无新架构变化——FIX-3 的代码改动限于 1 处测试断言、1 处前端测试 mock、1 处前端场景标签、1 处 Rust 头注释、1 处 runner 门控。分层/契约/依赖边界未动，`doc/contracts/**`、`src/ui/**`、`src/bootstrap/app.py`、`packaging/**` 未被触碰（62 条清单 + mtime 尾序）。
**Verification 面**：R-01…R-06 的关闭证据逐项成立；命令级复跑全部 `BLOCKED`，已如实标注，未以交叉核验冒充运行验证。

## 7. 结论与复审

**决定：`approve`（approved）。固定 head `2f6a31cd67e983e789c02cb4e33c194f0e012f23` 可交 Codex 集成。**

理由：

1. 第 3 轮 review 的 **R-01…R-06 全部真实关闭**，且关闭证据可按行号复核（§5 表）：证据 head 已显式归属并附 rev-parse/porcelain 转录、62 条转录含此前缺失的 `raw/fix-pre-failure-demo.log` 并给出**已入库**结论、Task 数字与当前口径统一、runner 门控把 NOT_RUN 计为失败且两个 artefact 有可复算生成器并如实记录 observed 差异、只读断言改为真捕获、mock URL 与 Rust 头注释与实现同步、E-07 改名与精确字节标签到位。
2. **无回归**：`main.rs` 未被触碰（491 行 / 12 测试 / 行号完全对齐），非 resource_channel 的 `src/**` 与 `src/ui/**` 均未写入（mtime 尾序末 8 条恰为 8 个 resource_channel 文件），原 43 个 pytest 用例与 12 个 Rust 用例语义未削弱。
3. **诚实边界完整**：S1-B3/B6/B8 保持 `NOT_RUN`、S1-B11 `UNVERIFIED`、修前失败判别力记 `NOT_RUN`、E-07 保守口径与「1 s 仅为目标未称达标」保留、无产品级安全/打包就绪宣称。
4. **无新 P0/P1/P2**；6 条观察均为非阻断项。

剩余风险与限制（不改变结论）：

- **命令级证据缺失**：本轮所有「运行」类判断均为只读交叉核验。解除条件：在 shell 可用、worktree 可写 ACL 的会话中复跑 §6 的 BLOCKED 行（`pytest`/`cargo test`/`npm test`/`run_e2e.py` ×2、`git diff --name-status 2dca20cd..2f6a31cd`、`git diff --check`、`git diff a33f3442..2f6a31cd -- apps/desktop/src-tauri/src/`、Contract blob 哈希）。建议由 **Codex 在集成验证时**执行这些命令并留存 EXIT 级转录（协议 §6.12②）。
- `O-01`（§0:8-9 措辞）与 `O-03`（`pytest.ini` 根目录路径）建议在集成记录中一句话说明即可。
- `O-06`：本轮复核自身在 `verification/M2-RC1/raw/` 留下一个未跟踪的会话转录；如需保持工作区严格干净，集成前应删除或加入忽略规则（**本轮 Reviewer 未改动它，仅报告**）。

**交付给 Codex（承接第 3 轮 §12 三点，其中两点仍未落实）**：

1. **仍未落实**：F-03（命令面收敛：capability/ACL/CSP、catalog 回 Core/SQLite）与 F-05（sidecar 独立入口）的 `accepted_deferral` 目前仍只存在于 Handoff 散文中，`doc/tasks/` 下**仍无** M2-RC1 后继 `proposed` 子 Task。请在集成记录或 Rebaseline Plan 中落一个，否则该前置项无持久载体。
2. **仍未落实**：`MEDIA_TOO_LARGE_BY_HANDLE` 是**真实 wire 名偏离**（语义由 `RESOURCE_TOO_LARGE` 承载，Contract §10.2 允许后续命名微调），集成记录须显式知会，不得当作「已实现同名码」；`REF_REPARSE_POINT` 为 Python-only 属如实描述。
3. 本轮新增：R-03 收紧了 `run_e2e.py` 门控（`NOT_RUN` 即失败），后续若引入合法 `NOT_RUN` 场景需同步调整门控口径（Handoff:125 已记录）。
4. 集成以 FIX-3 delivery head `2f6a31cd` 为准；`git status --porcelain` 在本轮复核结束时将含两个未跟踪文件（复核会话转录、本报告），均不属于交付。

---

Reviewer：DeepSeek Harness（非作者）｜被复核 head `2f6a31cd`（base `2dca20cd`）｜决定 **approve**｜第 3 轮 R-01…R-06 **全部 closed**，无新 P0/P1/P2；6 条非阻断观察 `O-01`…`O-06`｜命令复跑 **BLOCKED**（本会话 `pwsh` 因 `SetNamedSecurityInfoW Win32 5` 不可用、`danger-full-access` 升级被拒），已用 reflog/refs + 全仓 mtime 尾序 + `.pytest_cache` + 源码逐行 + raw JSON 手工复算交叉核验
