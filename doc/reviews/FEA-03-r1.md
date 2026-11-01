---
document_id: FEA-03-r1
kind: independent_implementation_review
reviewer: fea03-impl-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams fresh 独立上下文 teammate `fea03-impl-reviewer`，由 Team Lead `lead` 派发；未参与 FEA-03 起草、范围冻结/UNFREEZE 载体、实现或返修"
reviewer_independent: true
reviewed_by_implementer: false
author: "codex（实现交付）+ dsh（据 GOAL-PROGRESS 3D 的集成侧修复与提交）"
base_commit: b83bc7703
reviewed_head: 7a31c331e
reviewed_head_full: 7a31c331e19ed5730b269fab2b8b704036506531
repository_under_review: "G:/CODEX/New Manga.workspace/FEA-03（branch feat/fea-03，只读审查）"
main_head_at_review: 8c40fe011
date: 2026-11-02
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 5
p2_count: 9
---

# Review：FEA-03 实现复核（base `b83bc7703` / reviewed_head `7a31c331e`）

**结论：`changes_requested`（P0 × 0 / P1 × 5 / P2 × 9）。**

本报告只对 `7a31c331e` 这一个 head 有效，不构成集成批准、不构成 Task done、不构成 Gate 关闭。
审查者 `fea03-impl-reviewer` 为 DSH fresh 独立上下文 teammate（Team Lead `lead` 派发），**未参与** FEA-03 的起草、范围冻结、实现与返修；本次只读被审 head，未改 worktree/主仓库源码或文档，未 commit/push，测试产物写入 `%TEMP%`。

**关键判断**：交付的 CORE/BRIDGE 主体与冻结卡 v6 的规则高度对应，测试是真实的（我实跑 1050 passed，与 DSH checkpoint 3D 记录一致），范围/冻结字节也干净；但存在 5 条 P1（token/幂等语义、崩溃残留 `.lock` 回收、同进程锁重建、AC6/V13 + AC11/V19 未满足、孤儿草稿假冲突），且 Handoff/证据与交付 head 不一致（R-09）。在这些问题修复并由 DSH 重新指派复审前，不能进入集成。

---

## 0. 复核对象、方法与环境

| 项 | 值 |
|---|---|
| 主仓库 | `G:\CODEX\New Manga`，审查期间 main HEAD 由 `c171b92df` 前进到 `8c40fe011`（仅 `doc/checkpoints/GOAL-PROGRESS-2026-11-01.md` 7 行，记录 FEA-03 交付与 DSH 集成验证，不属被审实现） |
| 实现 worktree | `G:\CODEX\New Manga.workspace\FEA-03`（branch `feat/fea-03`，HEAD `7a31c331e`，工作区 clean） |
| 被审范围 | `git diff b83bc7703..7a31c331e`：25 文件，+3164/−50 |
| 契约/依据 | `doc/tasks/FEA-03.md`（v6，r5 approved）、`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`（v6，pin `8faf1e80…`）、`doc/reviews/CONTRACT-UNFREEZE-C13-2026-11-01.md`、`doc/plan/FEA-CONTRACT-FROZEN-C13.md` |
| 环境 | Windows；CPython 3.14.6；pytest 9.1.1（已安装）；Pillow 12.3.0；.NET SDK 10.0.401；`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`；dotnet artifacts 指到 `%TEMP%` |
| 未执行 | 未做真实 OS ACL/只读挂载（V22 只能复核测试源）；未运行 `check.ps1`（治理指针检查，非本次代码复核必需）；未重审 C-13 字节语义（pins 已证未变，r3/r5 已审）；未审 Host/IPC（本卡明确不接线） |

**审查者来源声明**：`reviewer_kind: subagent`；独立上下文、只读被审 head；未参与实现，也未参与修复。

---

## 1. 逐项核查（1–12）

### 1. 越界 / 写域 / 冻结字节 — PASS

命令与结果：

```text
git -C <worktree> diff --name-status b83bc7703..7a31c331e
A apps/desktop-avalonia/src/NewManga.ApplicationCore/DraftBuffer.cs
A apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/DraftBufferTests.cs
A doc/handoffs/FEA-03-b83bc7703.md
A src/application/editing/drafts.py
M src/application/editing/errors.py
M src/application/editing/ports.py
M src/bootstrap/core_assembly.py
A src/domain/drafts/__init__.py
A src/domain/drafts/entities.py
A src/infrastructure/filesystem/draft_journal.py
M src/infrastructure/sqlite/regions.py
M tests/core/test_region_write_commands.py
A tests/domain/conftest.py
A tests/domain/test_drafts.py
A tests/editing/test_draft_protection.py
A tests/infrastructure/draft_journal_crash_worker.py
A tests/infrastructure/test_draft_journal.py
A verification/FEA-03/{baseline-file-outcomes,manual-smokes,pins,summary,test-commands,v-matrix}.md
A verification/FEA-03/{component_sqlite_smoke,crash_probes}.py
```

- 全部 25 个路径均落在卡 `allowed_paths`（`src/domain/drafts/**`、`src/infrastructure/filesystem/**`、`src/infrastructure/sqlite/**`、`apps/desktop-avalonia/{src/NewManga.ApplicationCore,tests}/**`、`tests/{domain,editing,infrastructure}/**`、`tests/core/test_region_write_commands.py`、`verification/FEA-03/**`、handoff）。**未越界**。
- 冻结面零变更：`git diff --stat … -- src/application/editing/service.py src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrations doc/plan/ doc/contracts/` 为空；`apps/**` 其它面为空（仅 ApplicationCore 两文件）。
- 冻结契约字节：主仓库 `pwsh tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`（C13=`8faf1e805eac`）；对 worktree HEAD blob 独立重算同 15 项也全部匹配。worktree 直接运行因全局 `core.autocrlf=true` 全量 mismatch 属检出字节差异，`pins.md` 诊断与 fixture 复验方法成立。
- 唯一 whitespace 问题：`git diff --check b83bc7703..7a31c331e` → **EXIT=2**，`src/infrastructure/filesystem/draft_journal.py:419: new blank line at EOF.`（证据声称 PASS，见 R-08）。
- `tests/core/test_region_write_commands.py` 仅 3 处 `conn.close()`→`close()`，未降低既有断言（`git diff` 确认）。

### 2. R-DRAFT — PASS（实现）/ 证据见 §9

- 11 字段：`src/domain/drafts/entities.py:32-46`；`to_json()` 恰 11 键（`:107-121`）；`tests/domain/test_drafts.py:17-21`、`tests/infrastructure/test_draft_journal.py:43`、`tests/editing/test_draft_protection.py:76-96` 均有断言。
- DraftSequence 0 起、每 patch +1：`entities.py:18-29`、`apply_patch` `:102`；`test_drafts.py:24-27` 断言 0→3。
- PageBindingVersion 不透明注入：`entities.py:51-54` 仅校验 int；grep `page_bindings` 在 `drafts.py`/`entities.py` 零命中（未读 `page_bindings`，满足 L-1）。
- 五个强制 flush 点：`drafts.py:37-39`、`force_flush`/`flush_pending` `:557-570`；`test_draft_protection.py:304-318` 逐点断言 journal 持久化（Core 侧）。
- flush 失败：`drafts.py:533-555`（DRAFT_FLUSH_FAILED、缓冲保留、conflicted）；`test_draft_protection.py:319-333`、`:336-351`。
- 防抖实测：BRIDGE `DraftBuffer.cs:105` 默认 400ms；`DraftBufferTests.cs:102-134` 的默认防抖测试实测 n=12，证据记 p50=405.3ms/p95=407.6ms（`manual-smokes.md`）；我实跑 `dotnet test` 复现 p50=406.0ms/p95=415.3ms。Core 侧 `threading.Timer(0.4s)`（`drafts.py:62,690-697`）未单独给 p50/p95——卡 R-DRAFT-2 只要求“实现实测”，BRIDGE 证据可接受，列为小项。

### 3. R-JOURNAL / 收据 / 意图 — PARTIAL（R-02、R-03 缺陷）

- 原子写：`draft_journal.py:358-377` = `open("xb")` → `flush` → `fsync` → `os.replace` → `_fsync_directory`；Windows 目录 fsync 降级在 `:379-394` 登记（`durability_limitations`），符合 R-JOURNAL-2。
- `*.tmp` 清理：`:181-195`（root+receipts），启动时 `:86`；`test_draft_journal.py:90-102`。
- CRASH-A/B/C：真实子进程 `tests/infrastructure/test_draft_journal.py:53-74` + `draft_journal_crash_worker.py`；我实跑 `python verification/FEA-03/crash_probes.py` → `[{"phase":"A",...},{"phase":"B",...},{"phase":"C",...},{"phase":"LOCK","second_exit":73,"after_release_exit":0}]`，A/B 恢复 old、C 恢复 new、tmp 清理。**单元级异常注入缺失**（R-06）。
- 损坏丢弃：`:396-402`、`load_drafts` 异常分支 `:248-249`；`test_draft_journal.py:77-87`。
- `.lock` 单写者：`:101-138` 目录锁 + pid 文件；跨进程 `test_draft_journal.py:118-136` 通过（第二进程 exit 73、释放后 exit 0）；但**崩溃残留回收不可用**（R-02）且**同进程 close→reopen 不重建锁**（R-03）→ R-JOURNAL-4 单写者语义不完整。
- 只读 fail-closed：`:352-356`；`test_draft_journal.py:157-166`（monkeypatch 注入，非 OS ACL，见 R-07）。
- receipt 多序列：`:255-272`；`test_draft_journal.py:28-49`（seq 0/1 各自可读）。
- commitIntent per-Region digest 兜底：`drafts.py:633-670`；`test_draft_protection.py:383-413` + `component_sqlite_smoke.py` 的 `receipt_failure_intent_recovery:PASS`（我复跑输出一致）。
- R-JOURNAL-1/5：`write_draft` payload = 11 字段+`commitIntent`（`:197-205`）；`end_session` 清 journal、保留 receipt（`drafts.py:233-255`；`test_draft_protection.py:354-372`）；孤儿 `discard_orphans`（`:257-271`，但有 R-05 副作用）。

### 4. R-TOKEN / R-CAND — PARTIAL（R-01）

- token 字段与过期：`entities.py:140-162`；`drafts.py:368` 过期检查先于 receipt 读取（代码顺序正确，但测试未覆盖该顺序，R-07）。
- 幂等：**实现与 SC-D04/AC4 不一致**（R-01，两条复现）。
- candidate 四字段、仅内存、跨命令找回：`entities.py:165-178`、`drafts.py:76,291-359`；`test_draft_protection.py:80-96`（prepare 后 pointer/count 不变，apply 后 pointer 改变）。跨重启不找回由内存 registry 结构保证（`__init__` 不加载 candidate），未单独断言。
- candidate 生成不写 `current_revision_id`：`prepare_candidate` 只读 repository，未调用任何写口（`:314-355`）。

### 5. R-APPLY — PASS（实现主体）

- 复用/扩展 `commit_region_batch`：`ports.py:96-114`；`regions.py:297-338` 将原入口委托私有 `_commit_region_batch`，新增 `commit_region_batch_guarded` 走同一实现；**既有签名未变**。
- 事务内 stale/三锁/digest：`regions.py:351-426`（`BEGIN IMMEDIATE` 后先读现指针、再读 `text_json` 计算 5 位 digest，任一不符 rollback 返回 `STALE_BASE_REVISION` / `LOCK_CHANGED`，全部写在写入之前）。
- 重放优先于 stale：`drafts.py:368-388`（receipt 命中先返回）→ 未命中才 `:401-479` 进入构造/DB；过期在 receipt 之前（`:368`）。
- 事务原子性：3 Region 第 3 个 stale 全回滚，`test_draft_protection.py:142-177` 断言前 2 个 pointer/count 不变。
- apply 失败清 intent：`drafts.py:510-531`（未提交时 `write_draft(draft)` 去掉 `commitIntent`）；receipt 写失败 → `_fail_closed=True` 并抛 `DRAFT_JOURNAL_UNWRITABLE`（`:489-506`），重启 intent 恢复：`:633-670`。
- `revision_by_id` 新增：`ports.py:36`、`regions.py:173-178`，供恢复逐 Region 校验。
- 注意：`_recover_commit_intent` 的异常包装见 R-14。

### 6. R-LOCK / STYLE / DIGEST — PASS

- 三锁 × 三域（candidate 路径）：`drafts.py:324-335`；`region_locked` 拒绝 text/geometry/style；`translation_locked` 拒绝 text、允许 style；`inpaint_locked` 不对 style 断言（符合 SC-D09）。`test_draft_protection.py:215-254` 断言 region_locked 拒 style、translation_locked 拒 text、inpaint_locked 下 font_size/text_color 允许。
- 6 键白名单：`_STYLE_KEYS = TextStyle.__dataclass_fields__`（`drafts.py:31`，实际 6 键：auto_font_size_enabled/font_family/font_size/stroke_color/stroke_width/text_color）；外键 → `STYLE_KEY_NOT_ALLOWED` 且 message/details 含键名（`:307-313`）；`test_draft_protection.py:249-254` 断言 `customFoo` 在错误文本中。
- digest = 三锁 + `text_json.translation_locked` + `text_json.manual_edited`：`drafts.py:721-731` 与 `regions.py:411-421` 两处公式一致（同键、排序 JSON、sha256）；`test_draft_protection.py:180-212` 对 5 个位逐一断言 `LOCK_CHANGED` 且 revision count 不变。
- apply 路径：guard 在事务内重算 digest（`regions.py:394-426`），失败映射 `LOCK_CHANGED`（`drafts.py:473-474`）。

### 7. R-LEGACY — PASS（行为）/ V19 证据缺口见 R-04

- `src/application/editing/service.py` **未改**（diff 空）；`C073` append-only 语义保持。
- 旧路径回归：`python -m pytest tests/core -q` → **885 passed**（含 `test_region_write_commands.py`/`test_region_batch_locking.py`）；`test_draft_protection.py:98-103` 断言同文两次旧保存产生 2 revision（2→4）。
- 旧→新（刷新/未刷新）、新→旧组合（V19）**无测试**，AC11 未闭环（R-04）。

### 8. BRIDGE — PASS（已实际构建/测试）

- `DraftBuffer.cs`：11 字段投影（`DraftSnapshot`，1–56）、单串行队列（`SemaphoreSlim(1,1)`，`:107,133-149`）、可注入 flush seam（`:109,115-126`）、5 个强制触发点（`DraftFlushTrigger` 枚举 + `FlushAsync` 拒绝 Debounce，`:151-158`）、失败保留 patch 并 `conflicted`/`DRAFT_FLUSH_FAILED`（`:160-198`）；无 Host/IPC/CoreClient 引用（文件无 using，仅 namespace）。
- `DraftBufferTests.cs`：11 字段、队列合并、防抖合并、五触发、失败语义、默认防抖实测 6 个断言。
- **实际执行**：`dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r1-dotnet` → `已通过! - 失败: 0，通过: 31，已跳过: 0，总计: 31`（含 DraftBufferTests 6/6；p50=406.0ms/p95=415.3ms）。Handoff 的“dotnet test restore 阻塞”在当前环境不复现（R-09 记录环境变化）。

### 9. 测试真实性 — PARTIAL（测试真实、矩阵/证据滞后、V13/V19 缺失）

实际执行（均 EXIT=0，worktree 保持 clean）：

```text
python -m pytest tests/domain tests/editing tests/infrastructure -q
  → 165 passed in 35.10s
python -m pytest tests/core -q
  → 885 passed, 1 warning in 62.15s
python -m pytest tests/domain/test_drafts.py tests/editing/test_draft_protection.py tests/infrastructure/test_draft_journal.py -q
  → 28 passed in 2.91s
python verification/FEA-03/component_sqlite_smoke.py
  → {"apply_and_receipt_replay":"PASS","edit_open_and_candidate_only":"PASS","receipt_failure_intent_recovery":"PASS","session_conflict_and_owner_gate":"PASS","three_region_stale_atomic_rollback":"PASS"}
python verification/FEA-03/crash_probes.py
  → [{"phase":"A","recovered":"old","tmp_clean":true},{"phase":"B",...},{"phase":"C",...},{"phase":"LOCK","second_exit":73,"after_release_exit":0}]
```

新增 165 + 基线 885 = **1050 passed**，与 DSH `doc/checkpoints/GOAL-PROGRESS-2026-11-01.md:70-75`（3D）记录一致；无 skip/xfail，无空断言。**“未执行写通过”没有发生**：Handoff/证据对未跑项如实标 PARTIAL/BLOCKED。

V1–V25 与实际断言对照（★ = 我重跑后的状态；括号差异为相对 `v-matrix.md` 的变化）：

| V | 卡要求 | 实际断言位置 | 我的重跑状态 |
|---|---|---|---|
| V1 | 11 字段、序号 0→N | `test_drafts.py:17-27`；`test_draft_journal.py:43`；`test_draft_protection.py:76-96` | ★PASS（矩阵原 PARTIAL） |
| V2 | 主窗/浮窗同 Session 同 DraftId | `test_draft_protection.py:257-275` | ★PASS（原 NOT_RUN） |
| V3 | 五个强制 flush 点 | `test_draft_protection.py:304-318`；C# `DraftBufferTests:62-86` | ★PASS（原 NOT_RUN；C# 也已跑） |
| V4 | flush 失败保留缓冲/conflicted | `test_draft_protection.py:319-351`；C# `:89-100` | ★PASS（原 NOT_RUN） |
| V5 | 两会话只读、转移 owner | `test_draft_protection.py:270-301` | ★PASS（原 PARTIAL） |
| V6 | 文本冲突双方 conflicted、禁自动合并 | `test_draft_protection.py:288-298` | ★PASS（原 PARTIAL） |
| V7 | 几何/样式按键合并、草稿阶段无新 revision | `test_drafts.py:30-47`；C# `:22-40` | ★PASS（域/BRIDGE 单测；无 production 端到端断言，属小项） |
| V8 | 同 token 重放 ×2 同 revisionIds、不新增 | `test_draft_protection.py:90-96` | ★PASS（原 PARTIAL） |
| V9 | 过期 token 拒绝、无 revision | `test_draft_protection.py:126-139` | ★PARTIAL：拒绝通过；**未先产生 receipt，“过期先于 receipt”未被断言**（R-07） |
| V10 | CRASH-A/B/C（单元级注入 + 真实进程各一） | `test_draft_journal.py:53-74` 仅真实进程 | ★PARTIAL：进程级通过；**单元级异常注入未实现**（R-06） |
| V11 | 损坏 journal 丢弃不阻塞 | `test_draft_journal.py:77-87` | ★PASS（原 NOT_RUN） |
| V12 | prepare 后指针不变、candidate 四字段 | `test_draft_protection.py:80-88` | ★PASS（原 PARTIAL） |
| V13 | 翻译产物先成 candidate、指针不变 | 无测试；`prepare_candidate(origin="machine")` 无生产调用点 | ★FAIL（未实现/未验证，R-04） |
| V14 | 3 Region 第 3 个 stale 全回滚 + 独立连接不可见 | `test_draft_protection.py:142-177`（回滚断言有；独立连接可见性无） | ★PARTIAL（原 PARTIAL，准确） |
| V15 | 三锁 × 三域、candidate/apply 两路径 | `:215-256`（candidate 部分）+ `:180-212`（apply 的 5 位 digest） | ★PARTIAL：apply 路径未覆盖“锁存在时允许/拒绝”的完整 3×3 矩阵（R-07） |
| V16 | 六键白名单、错误含键名、真实键允许 | `:243-254` | ★PASS（原 NOT_RUN） |
| V17 | 改任一 protection 位 → LOCK_CHANGED | `:180-212`（5 位参数化） | ★PASS（原 NOT_RUN） |
| V18 | 旧路径同文两次 = 2 revision | `test_draft_protection.py:98-103`；旧回归 885 passed | ★PASS（原 NOT_RUN） |
| V19 | 旧→新（刷新/未刷新）、新→旧组合 | 无测试 | ★FAIL（未覆盖，R-04） |
| V20 | 重启后 receipt 命中 / intent 兜底 / current mismatch | `:383-413` 覆盖 receipt-write-crash→intent 恢复；旧 token receipt 命中在 `:408` | ★PARTIAL：current mismatch 分支未断言（原 PARTIAL，准确） |
| V21 | 同 token 不同内容 / 多序列 / 过期优先 | `:106-123`（内容）；`test_draft_journal.py:28-49`（多序列）；`:126-139`（过期，但无 receipt） | ★PARTIAL：过期优先未真正断言（R-07） |
| V22 | data-root 不可写（OS ACL）/ 只读挂载 | `test_draft_journal.py:157-166` 仅 monkeypatch `_probe_writable` | ★PARTIAL：非 OS ACL（原 NOT_RUN；矩阵表述低估） |
| V23 | 双进程 `.lock` fail-closed、释放后可启动 | `test_draft_journal.py:118-136` + `crash_probes.py` | ★PASS（原 PASS 手工；现已 pytest） |
| V24 | C# DraftBuffer + dotnet test | `DraftBufferTests`；我实跑 dotnet test | ★PASS（原 PARTIAL/BLOCKED；实测 31 passed） |
| V25 | 活跃登记/Session 清理/孤儿/receipt 保留 | `test_draft_protection.py:354-380` | ★PASS（原 PARTIAL） |

> 矩阵差异：`v-matrix.md` 多行 `NOT_RUN` 在可复跑环境已实际通过（V9/V15/V16/V17/V18/V22 测试存在并 PASS），属证据滞后（R-09）；V10 的“单元级异常注入 pytest 未执行”实为**未实现**（R-06）；V13/V19 为真实缺口（R-04）。

### 10. 证据 / 诚实性 — PARTIAL

- 正面：Handoff 对 BRIDGE dotnet、V 部分项、pytest 环境缺失均**明确标注未完成/未执行**，没有把未跑写成通过；`summary.md` 明确“不满足 done Gate”。
- **唯一“未执行写通过”**：`verification/FEA-03/test-commands.md:18` 记 `git diff --check | PASS，exit 0`，但在被审 head 实际为 **EXIT=2**（`draft_journal.py:419` new blank line at EOF）；该命令在提交前只覆盖已跟踪文件，对未跟踪新文件是空检查（R-08）。
- Handoff/`summary.md` 与交付 head 不一致：仍写“HEAD b83bc7703、改动未提交、delivery_head: null”（`doc/handoffs/FEA-03-b83bc7703.md:6,14,81`；`verification/FEA-03/summary.md:3`），而交付 commit `7a31c331e` 已包含这些文件；且据 main `GOAL-PROGRESS…:70-75`（3D），head 内含 DSH 集成侧修复（目录锁/同进程共享/PID 清理/`CoreServices.close()`），Handoff 未记录（R-09）。
- `v-matrix.md` 状态滞后于本轮可复跑结果（见 §9 表），但未出现虚假 PASS。

### 11. `ports.py` — PASS（既有签名未变；有 P2）

- 既有 `RegionRepository`/`RegionRevisionCommitter` 方法签名未变；`commit_region_batch` 仍为原签名（`ports.py:96-107`）。
- 新增（卡授权范围内）：`RegionRepository.revision_by_id`（`:36`，R-APPLY-3 明示新增）、`commit_region_batch_guarded`（`:109-114`，R-APPLY-1 的“扩展”）、`RegionProtectionGuard`（`:61-66`）、`RegionCommitStatus.STALE_BASE_REVISION`（`:48`）、`RegionCommitResult.revision_ids`（`:57`）。均为 additive，不改变既有方法语义。
- **唯一问题**：删除了既有 `commit_region_batch` 的完整契约 docstring（原 50 行，现仅 `":106 Existing composite write contract; its signature stays stable."`），而冻结记录铁律 2 明确“不改 `ports.py` 契约”。虽未改签名，但冻结端口上的契约文档被移除（文本被搬到实现私有方法），建议恢复（R-10）。
- 无新错误码外泄：`DraftError` 仅在 `application/editing/{drafts,errors}.py` 使用，未进入 `CoreServiceServer` 命令面/wire 白名单（L-2 维持 N/A）。

### 12. 质量 — PARTIAL

- 事务边界：`BEGIN IMMEDIATE` 内先读后写、任一失败 rollback、提交后回填指针，正确（`regions.py:351-526`）。
- 异常路径：apply 的 DraftError/generic 两分支均清 intent（`drafts.py:510-531`）；receipt 写失败 fail-closed（`:489-506`）。
- Windows 文件锁：目录锁在同一进程共享、跨进程互斥的**干净路径**可用，但崩溃残留回收与同进程重开存在缺陷（R-02/R-03）。
- journal 与 receipt 一致性：正常/崩溃窗口基本一致；token 身份参与 receipt 命中使跨重启新 token 重放不一致（R-01）。
- 调试残留：`draft_journal.py:91-94` 重复赋值、`:5` 未使用的 `errno`、`:419` 文件尾空行；`drafts.py:510-531` 两段 except 清 intent 代码重复（R-11）。
- 生产关闭：`CoreServices.close()`（`core_assembly.py:792-807`）已加，但生产调用点仍是 `conn.close()`（`src/bootstrap/app.py:182,445`、`src/bootstrap/core_service.py:5822`，不在本卡写域），锁释放依赖 `__del__`；正常解释器退出实测可释放，崩溃/嵌入场景风险见 R-13。

---

## 2. Findings

| ID | 级别 | 位置 | 问题 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | **P1** | `src/application/editing/drafts.py:148,368-400`；测试 `tests/editing/test_draft_protection.py:63,90,126-139` | **token/幂等语义与 SC-D04/AC4 不一致**：①`open_draft`（edit-open）在 `:148` 签发 token，其 `DraftSequence` 固定为签发时值；`:399-400` 要求 apply 时 `draft.draft_sequence == token.draft_sequence` → 任何 patch 后正常 open→patch→apply 被 `EDIT_TOKEN_REUSED` 拒绝；测试 helper 在 patch 后重新 `issue_edit_token` 才通过，掩盖该缺陷。②`:375-378` receipt 命中要求 `tokenId` 与 receipt 相同；跨重启用新 token 重放同 `(DraftId,DraftSequence)` 被 `EDIT_TOKEN_REUSED` 而非返回同 `revisionIds`（AC4/AC15/R-APPLY-2）。旧 token 重放可命中。 | 生产装配复现：token seq=0 → patch 后 draft seq=1 → apply → `DraftError EDIT_TOKEN_REUSED token sequence does not match the draft`；重启后 open 得新 token，`apply_candidates(new_token)` → `EDIT_TOKEN_REUSED receipt replay token does not match`，`apply_candidates(old_token)` → 返回原 `revisionIds`。 | 明确 token 签发点并在卡/契约对齐；幂等键用 `(DraftId,DraftSequence)`（+ contentDigest），token 仅做归属/过期校验；token 序列不匹配用独立错误或重新签发；补“edit-open token 直接 apply”与“新 token 跨重启 replay”测试。 | open |
| R-02 | **P1** | `src/infrastructure/filesystem/draft_journal.py:5,27-50,110-127`（尤其 `:117`） | **崩溃残留 `.lock` 回收路径不可用且会抛 NameError**：①`:117` 使用 `shutil.rmtree` 但文件未 `import shutil` → 一旦进入回收分支抛 `NameError`，构造器只捕获 `DraftJournalError`/`OSError`，Core 装配直接失败（重启失败）；②Windows `_process_is_alive` 在 `OpenProcess` 失败（死 PID 无剩余句柄）时返回 True，死进程被当活 → 回收分支实际不可达，崩溃后 `.lock` 永久残留、journal 永久 `available=False`（DRAFT_JOURNAL_UNWRITABLE）。 | 手工构造 `.lock`+死 pid 后构造 `DraftJournal` → `RAISED NameError: name 'shutil' is not defined`（traceback 指向 `:117`）；真实 `os._exit` 后重启 → `stale lock exists: True`，第二个 Core `drafts available: False`（不回收）。 | `import shutil`；Windows 区分 `ERROR_INVALID_PARAMETER`（死 pid）与权限错误，或记录 pid+进程创建时间/改用 `msvcrt.locking` 独占锁；补“崩溃残留锁 → 重启成功”测试（与 V23 相邻）。 | open |
| R-03 | **P1** | `src/infrastructure/filesystem/draft_journal.py:52-53,104-109,153-173` | **同进程 close→reopen 后磁盘 `.lock` 不重建**：`_SHARED_LOCKS` 条目在引用计数归零后未删除；再次构造同路径 journal 时直接复用旧句柄并自增计数，不执行 `mkdir` → 磁盘上无 `.lock`，另一进程可同时取得锁，R-JOURNAL-4 单写者语义失效。 | 复现：`j1=journal; j1.close()` → `.lock` 不存在；`j2=journal`（available=True）但 `.lock exists on disk: False`；此时子进程 `LOCK` 探针返回 **0（取得锁）**（应为 73）。现有测试 `test_draft_journal.py:105-117` 未断言 `.lock` 存在性。 | refcount 归零时 `del _SHARED_LOCKS[key]` 并确保路径锁重建；补“close 后重开仍有 `.lock`、第二进程仍被拒”的断言。 | open |
| R-04 | **P1** | `verification/FEA-03/v-matrix.md:19,25`；AC6/AC11（`doc/tasks/FEA-03.md:134,139`） | **AC6/V13 与 AC11/V19 未满足**：①无“翻译产物先成 candidate”的实现/接线/测试（`prepare_candidate(origin=...)` 在生产 `src/**` 无调用点；V13 要求产物为 candidate 且指针不变）；②旧→新（base 刷新/未刷新）、新→旧组合（V19）无测试，AC11 的 3 个子场景无证据。 | v-matrix 两行 NOT_RUN；grep `prepare_candidate(` 在 `src/**` 零命中；`test_draft_protection.py` 仅覆盖旧路径 append（`:98-103`），无跨路径组合。 | 补 V13/V19 实现或由 DSH 明确 deferral 并更新冻结矩阵/Handoff；若属 FEA-04 接线范围，需在卡中登记 deferral 后再重审。 | open |
| R-05 | **P1** | `src/application/editing/drafts.py:257-271`（`discard_orphans`）、`:672-688`（`_detect_text_conflict`） | **孤儿 discarded 草稿造成永久假文本冲突**：`discard_orphans` 只把状态置 `discarded`，不从 `_drafts`/`_target_by_session` 移除；`_detect_text_conflict` 不按状态/活跃 Session 过滤 → 新 Session 对同一 page 级 target 的文本 patch 被判 `DRAFT_TEXT_CONFLICT`，且每次重试都冲突。 | 生产装配复现：orphan 草稿写文本 → `discard_orphans(set())` 成功 → 新 Session 打开同 page target → `patch_draft` 抛 `DraftError DRAFT_TEXT_CONFLICT text changes conflict across Sessions`。 | 冲突检测过滤 `discarded`/无活跃 Session 的草稿；discard 时清理 `_target_by_session`；补 V25 相邻回归测试。 | open |
| R-06 | P2 | `tests/infrastructure/test_draft_journal.py:53-74`；`v-matrix.md:16` | V10 要求“单元级异常注入 + 真实进程 kill 各一”，目前只有真实子进程三阶段；矩阵把缺口写成“pytest 未执行”，实为**单元级注入测试未实现**。 | 只有 `test_real_process_crash_a_b_c_*`；无 monkeypatch/`_atomic_json_write` 注入测试。 | 补 temp 写前/rename 前/rename 后的单元级注入测试，或在卡中明确“进程级替代”并修订 V10 期望。 | open |
| R-07 | P2 | `tests/editing/test_draft_protection.py:126-139`；`v-matrix.md:15,21`；`tests/infrastructure/test_draft_journal.py:157-166` | 测试名/矩阵声称的若干分支未被断言：V9/V21 的“过期先于 receipt”测试未先产生 receipt；V14 独立连接提交前不可见、V15 apply 路径完整 3×3、V20 current-mismatch 分支、V22 真实 OS ACL 均未覆盖（V22 仅 monkeypatch `_probe_writable`）。矩阵把部分项标 NOT_RUN 是低估，但关键顺序/隔离语义仍无证据。 | 逐行核对测试源（见 §9 表）；V9 测试无 `write_receipt` 前置；V22 用 monkeypatch 而非 ACL/只读挂载。 | 逐项补断言或修订矩阵口径；V22 用受控只读目录/ACL 测一次并在证据中记录命令。 | open |
| R-08 | P2 | `verification/FEA-03/test-commands.md:18`；`src/infrastructure/filesystem/draft_journal.py:419` | **证据失真**：`git diff --check` 记为“PASS，exit 0”，但被审 head 实际 **EXIT=2**（`draft_journal.py:419: new blank line at EOF.`）。该命令在提交前只覆盖已跟踪文件，对未跟踪新文件是空检查。 | `git -C <worktree> diff --check b83bc7703..7a31c331e` → exit 2。 | 删除文件尾空行；证据重跑并记录真实 EXIT；提交前用 `git add -N` 或 `git diff --check --cached` 覆盖新文件。 | open |
| R-09 | P2 | `doc/handoffs/FEA-03-b83bc7703.md:6,14,81`；`verification/FEA-03/summary.md:3`；`v-matrix.md` 多行 | **交付证据未更新到交付 head**：Handoff/summary 仍写 `b83bc7703`/“改动未提交”/`delivery_head: null`，而 commit `7a31c331e` 已含这些文件；据 main `GOAL-PROGRESS-2026-11-01.md:70-75`（3D）head 内含 DSH 集成侧修复（目录锁/同进程共享/PID 清理/`CoreServices.close()`），Handoff 未记录；v-matrix 的 NOT_RUN/PARTIAL 未按可复跑结果更新。 | `git show -s 7a31c331e`、`git log --oneline b83bc7703..7a31c331e`；Handoff 文本与 checkpoint 3D 对照。 | DSH 更新 Handoff/summary/v-matrix 并注明集成侧修复与实测结果；`delivery_head` 填 `7a31c331e`。 | open |
| R-10 | P2 | `src/application/editing/ports.py:96-107` | 既有冻结端口 `commit_region_batch` 的契约 docstring 被删除（原 50 行，仅剩一行），把文档缩到实现私有方法；冻结记录铁律 2 要求“不改 `ports.py` 契约”。签名未变、新增方法有卡授权，但冻结面文档出现分叉。 | `git diff b83bc7703..7a31c331e -- src/application/editing/ports.py`（-50 行主要是该 docstring）。 | 恢复原 docstring（可在实现侧补扩展说明），避免冻结端口文档缺失。 | open |
| R-11 | P2 | `src/infrastructure/filesystem/draft_journal.py:5,91-94,419`；`src/application/editing/drafts.py:510-531` | 代码卫生：重复赋值（`available`/`startup_error` 各两遍）、未使用 `errno`、文件尾空行；apply 的 `except DraftError` 与 generic 分支重复清 intent 逻辑。 | 代码阅读/`git diff --check`。 | 清理重复、去未用 import、抽公共清理函数（注意不要改变异常语义）。 | open |
| R-12 | P2 | `apps/desktop-avalonia/src/NewManga.ApplicationCore/DraftBuffer.cs:69,233-241` | ①`DraftSnapshot.Apply` 无条件把 `Status` 置 `Active`，与 Core `patch_draft`（`drafts.py:180-181` 保持 `Conflicted`）不一致，flush 失败后下一次 patch 会丢失 conflicted 标记；②`DisposeAsync` 在 flush 期间若收到取消会抛 `OperationCanceledException` 出 Disposal，且 dispose 与 debounce 任务存在 `SemaphoreSlim`/CTS 竞态（未观测任务异常）。 | 代码对照；C# 测试未覆盖“conflicted 后继续 patch”与 dispose 取消。 | 统一 conflicted 保持语义；dispose 内吞取消并等待/取消 debounce；补对应单测。 | open |
| R-13 | P2 | `src/bootstrap/core_assembly.py:792-807`（新增 `close()`）；`src/bootstrap/app.py:182,445`；`src/bootstrap/core_service.py:5822` | `CoreServices.close()` 已实现但没有生产调用点，生产仍是 `conn.close()`；`.lock` 释放依赖 `DraftJournal.__del__`（正常解释器退出实测可释放，但崩溃/嵌入/多实例场景不可靠）。这些文件不在本卡写域，属集成接线。 | grep 调用点；`app.py`/`core_service.py` 片段；正常退出后 `.lock` 消失、`os._exit` 后残留（R-02）。 | 在 FEA-04/Host 接线时统一调用 `core.close()`（或把 journal 释放挂到既有 shutdown 路径），并加重启测试；本卡只需在 Handoff 登记 deferral。 | open |
| R-14 | P2 | `src/application/editing/drafts.py:633-670` | `_recover_commit_intent` 把 `_content_digest` 的 `PAGE_SIZE_UNAVAILABLE` 等具体错误统一包装成 `DRAFT_JOURNAL_UNWRITABLE`，并在 `__init__` 抛出使 Core 无法启动；fail-closed 方向合理，但错误码/启动策略需 DSH 明确（是拒绝启动还是降级为 journal unavailable）。 | 代码阅读；`_content_digest` 在 `:605-631` 抛 `PAGE_SIZE_UNAVAILABLE`，外层 `except Exception` 包装。 | 保留具体 cause_code；明确启动策略并补页尺寸缺失的恢复测试。 | open |

---

## 3. 验证记录

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| CORE 新增+既有（domain/editing/infrastructure） | `python -m pytest tests/domain tests/editing tests/infrastructure -q -p no:cacheprovider` | worktree `7a31c331e`；CPython 3.14.6 / pytest 9.1.1 | **PASS**：`165 passed in 35.10s`，EXIT=0 | job output（本次会话） |
| CORE 基线（tests/core） | `python -m pytest tests/core -q -p no:cacheprovider` | 同上 | **PASS**：`885 passed, 1 warning in 62.15s`，EXIT=0 | job output |
| 新增测试单独 | `python -m pytest tests/domain/test_drafts.py tests/editing/test_draft_protection.py tests/infrastructure/test_draft_journal.py -q` | 同上 | **PASS**：`28 passed in 2.91s` | job output |
| BRIDGE 构建/测试 | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r1-dotnet` | .NET SDK 10.0.401 | **PASS**：通过 31、失败 0、跳过 0；DraftBufferTests 6/6；p50=406.0ms/p95=415.3ms | job output |
| 组件 SQLite smoke | `python verification/FEA-03/component_sqlite_smoke.py` | worktree | **PASS**：5 项 JSON 全 PASS，EXIT=0 | 命令输出 |
| 崩溃/锁探针 | `python verification/FEA-03/crash_probes.py` | worktree | **PASS**：A/B/C + LOCK(73/0)，EXIT=0 | 命令输出 |
| 越界检查 | `git diff --stat/--name-status b83bc7703..7a31c331e` | worktree | **PASS**：25 文件全部在 `allowed_paths` | 命令输出 |
| 冻结字节 | `pwsh tools/governance/verify_pins.ps1`（主仓库）；HEAD blob sha256 重算（worktree） | main `8c40fe011` | **PASS**：15/15 | 命令输出 |
| 禁止路径 | `git diff --stat … -- service.py schema.py migrations doc/plan apps/` | worktree | **PASS**：无变更（仅 ApplicationCore 两文件） | 命令输出 |
| whitespace | `git diff --check b83bc7703..7a31c331e` | worktree | **FAIL**：EXIT=2，`draft_journal.py:419` new blank line at EOF | 命令输出（R-08） |
| 崩溃残留锁 | 手工 `.lock`+死 pid → `DraftJournal(root)` | worktree | **FAIL**：`NameError: name 'shutil' is not defined`（R-02） | 临时脚本 `%TEMP%\fea03-r1-repro\repro.py` 输出 |
| 崩溃后重启 | `os._exit(0)` 装配 Core → 重新 `assemble_production_core` | worktree | **FAIL**：`.lock` 残留，第二次 `drafts.available=False`（R-02） | 临时脚本 `%TEMP%\fea03-r1-restart\s1.py,s2.py` |
| 同进程锁重建 | `j1.close()` → 新建 `j2` → 子进程 LOCK 探针 | worktree | **FAIL**：磁盘 `.lock` 不存在，子进程 exit 0（取得锁）（R-03） | 临时脚本 `%TEMP%\fea03-r1-lock.py` |
| token 正常流 | open→patch→prepare→apply(open token) | worktree 生产装配 | **FAIL**：`EDIT_TOKEN_REUSED token sequence does not match the draft`（R-01） | 临时脚本 `%TEMP%\fea03-r1-tokenflow.py` |
| 跨重启 replay | apply→close→reassemble→open 新 token / 旧 token replay | worktree 生产装配 | **FAIL（新 token）**：`EDIT_TOKEN_REUSED receipt replay token does not match`；旧 token 返回同 revisionIds（R-01） | 临时脚本 `%TEMP%\fea03-r1-replay.py` |
| 孤儿草稿冲突 | orphan 写文本→`discard_orphans(set())`→新 Session patch | worktree 生产装配 | **FAIL**：`DRAFT_TEXT_CONFLICT`（R-05） | 临时脚本 `%TEMP%\fea03-r1-orphan.py` |
| OS ACL 不可写（V22） | — | — | **NOT_RUN**（未做真实 ACL/只读挂载；仅复核 monkeypatch 测试源） | — |
| check.ps1 | — | — | **NOT_RUN**（非本次代码复核必需；main checkpoint 3D 记为 PASS，未复核） | — |

---

## 4. 边界声明与剩余风险

1. 本报告只审 **实现交付**（`7a31c331e` 的代码/测试/证据），**不构成集成批准、不构成 Task done、不构成 Gate 关闭**；集成、契约解释与 finding 处置由 DSH 负责。
2. 审查者 `fea03-impl-reviewer` 为 DSH fresh 独立上下文 subagent，**未参与** FEA-03 起草/冻结/实现/返修；本次只读 worktree，未 commit/push，未修改被审文件；测试与复现均在 `%TEMP%`，worktree `git status` 全程 clean。
3. 本报告写于主仓库工作区 `doc/reviews/FEA-03-r1.md`（未提交）；被审 head 若变化（含返修 commit），本报告自动失效，需对新的 fixed head 重新审查。
4. 剩余风险：R-01/R-02/R-03/R-05 是可在返修中收敛的实现缺陷；R-04 需要 DSH 决定“补实现/补测试”还是“登记 deferral”；R-08/R-09 属证据/文档一致性，必须在集成前修正，否则集成记录会引用与实际 head 不符的 Handoff/矩阵。测试证据为**真实执行**（1050 passed、dotnet 31 passed、pins 15/15），未发现“未执行写通过”的测试结论；唯一例外是 R-08 的 `git diff --check PASS` 记录。
