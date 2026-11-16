# 新会话启动包 — New Manga 目标续接

- 生成时间：2026-11-16 08:45 (+08:00)
- 生成者：DSH（lead），上一 goal 已用尽 100/100 轮
- 上一 goal id：`goal-10d37e8e-fe31-4a4c-adb1-0957c50880bf`
- **当前 head：`07a8f828b`**
- 工作区：干净（`git status --porcelain` 为空）

> 本文是**给下一个会话的唯一起点**。不要重读 100 轮历史；按本文的「下一步队列」推进即可。

---

## 0. 三十秒状态快照

| 项 | 状态 |
|---|---|
| HEAD | `07a8f828b`（main） |
| 四件套 | **全绿**：`check.ps1` PASS(3w) / `verify_pins` 18/18 / `api_inventory` 1/80/6=87 / `App.Tests` 962/0/4（基线 955/0/11，不退化） |
| `apps/desktop-avalonia/scripts/test.ps1` | **EXIT=0**（1579/1627 passed, 48 skipped） |
| 推送状态 | ⚠️ **`main` 无 upstream，领先 `origin/main` 1068 个 commit — 从未 push 过** |
| 上一 goal 轮次 | 100/100 已用尽 |

复跑四件套（每次会话开始都应确认）：

```powershell
cd "G:\CODEX\New Manga"
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
$env:NEWMANGA_WORKSPACE_ROOT = "G:\CODEX\New Manga.workspace"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1
```

⚠️ **`test.ps1` 会改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/{immersive-reader.png, render-info.md}`**
（测试副作用）。跑完记得 `git checkout -- verification/READER-OVERLAY-HEADLESS-PNG-1/` 再提交。

---

## 1. 原目标与达成情况

原目标（摘录）：从 `b8113e740` 起持续自动推进，直至同时满足 A/B/C/D。

| 目标 | 状态 | 缺口 |
|---|---|---|
| **A** 四件套持续通过 | ✅ **达成** | — |
| **B** Release Gate 六条中 Agent 可完成部分全部关闭或明确判定 | ⚠️ **未达成** | **缺「六条条件 → 状态 → 证据 → 剩余动作」映射表** |
| **C** 已登记技术债清零 | ⚠️ **未达成** | AC 豁免 ✅、控制字符 ✅、**AC blocked 剩 33 条待处置** |
| **D** 剩余仅 HUMAN-REQUIRED 逐条登记 | ⚠️ **基本达成** | `MICA-FIX-1` AC2 人眼判定部分待并入 `H-01` |

---

## 2. 下一步队列（按建议顺序，可直接接手）

### 队列 1 —— `HOST-CONCURRENCY-FLAKY-1` 的 AC6 重审（**最优先**）

上一轮 AC6 复核结论 `CHANGES_REQUESTED`，作者已逐条处置（见卡面「AC6 复核处置」节），
但**尚未送二次复核**。

- 卡：`doc/tasks/HOST-CONCURRENCY-FLAKY-1.md`（`status: proposed`，AC1/AC4/AC5 = PARTIAL）
- 原复核报告：`verification/HOST-CONCURRENCY-FLAKY-1/review-ac6.md`（361 行，署名 `reviewer-hcf`）
- 已处置：P0-1（`SourceReadCoordinator.cs:404/624` 归一化）、P1（15 行证据 pin commit 全改，现 18 行全部校验通过）
- **待办**：
  1. 派**新的**独立上下文子 agent 做二次复核（不得复用 `reviewer-hcf` 的上下文）
  2. `TileChannel.cs:437` 的同源 raw file index 风险 —— AC4 明确标了「待评估」，需判定它是否参与 identity 比较
  3. 复核通过后把 AC 标记收敛、`status` 定案（`closed_with_limitations` 或 `done`）

### 队列 2 —— 目标 B：Release Gate 六条映射表

需要产出 `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-<date>.md`：

- 六条条件逐条：定义 / 当前状态 / 证据（文件+commit+行号）/ 剩余动作 / 归属（Agent 可完成 or HUMAN-REQUIRED）
- 已有素材：`doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md`、
  `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md`、
  `doc/tasks/RELEASE-PACKAGE-1.md`、`doc/tasks/GATE3-COVERAGE-MATRIX.md`

### 队列 3 —— 目标 C：剩余 33 条可闭合 AC

素材：`doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`（41 条可闭合已核实，8 条已处置）

分类：`DOC` 8 / `RERUN` 5 / `IMPL` 20 —— **`FEA-04` 独占 8 条，需另立实现卡**。

### 队列 4 —— 目标 D 收口

把 `MICA-FIX-1` 的 AC2 人眼判定部分并入 `doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 的 `H-01`。

### 队列 5 —— 既有小债（低优先，可批量）

- `doc/tasks/RELEASE-PACKAGE-1.md` 含 NUL 字节
- `doc/tasks/M2-REGION-RETYPE-CORE.md` 重复 `integration_commit` 键
- `doc/REBASELINE_PLAN.md` 第 56/58 行漂移
- `test.ps1` 改写 `verification/` 下 2 个文件（见本文第 0 节警告）
- `main` 无 upstream、1068 commits 未推送（是否需要 push 需用户确认）

---

## 3. 本会话的关键技术事实（避免重复调查）

### 3.1 产品架构

Windows / C# .NET + Avalonia / Python Core / SQLite / ReferencedSource（AD-002）。
**Tauri/React/WebView2 已退役**，任何 `apps/desktop/src-tauri/**` 路径都是历史遗物。

### 3.2 core 命令名用下划线

`settings_network_profiles_create` ✅ / `settings.network_profiles_create` ❌（返回 `UNKNOWN_COMMAND`）。

### 3.3 删除命令的 payload 有严格 closed-shape

`core_service.py:2285` `_validate_single_delete_payload`：键集合必须**精确等于**
`{book_id, confirm_permanent_delete, inventory_digest}`。
`_validate_batch_delete_payload`：6 个键（含 `inventory_digest` + `inventory_digests`）。
digest 必须由 `library_preview_permanent_delete_books` 先取（返回 `inventoryDigest` + `inventoryDigests`）。

### 3.4 **诊断优先读仓库自带的 wire log，不要自造 probe**

`SidecarFixture.cs:312` 一直配着 `WireLogPath`，`test.ps1` 每次跑自动写 NDJSON：

```
G:\CODEX\New Manga.workspace\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\wire\
  commands-ns-b1-core-service.ndjson    ← 含 request/response 原文
```

字段是 `request` / `response`（小写）。**这是零侵入、不会失真的诊断手段。**

### 3.5 file identity 的 53 位契约（本会话修的缺陷）

`src/application/importing/referenced/identity.py:3-9` 原文要求：
**every producer and every comparator calls `normalize_identity` — never the raw `st_ino`**。

```python
_VOLUME_MASK = 0xFFFFFFFF        # uint 天然合规
_FILE_MASK   = (1 << 53) - 1     # ★ 关键
```

**实测 `%TEMP%` 新建文件 `st_ino > 2^53` 达 6/7**（见
`verification/HOST-CONCURRENCY-FLAKY-1/st-ino-measured.md`）。

C# 侧已修的点：
- `NewManga.CoreClient/Issuer/HostIssuer.cs`（`FileIdMask` / `NormalizeFileId`，`:563`/`:596-597`）
- `NewManga.Host/Sources/SourceReadCoordinator.cs:404`/`:624`（写 grant facts 处）
- `NewManga.Host/Sources/SourceSecurity.cs`（新增 `NormalizeFileId` / `CoreFileIdMask`）

**⚠️ 关键陷阱：不要在 `SourceSecurity.Identity` 内部 mask。**
该值被 `SourceAccessRegistry.cs:49/137` 持久化到 `registry.v1.dat` 作 `SourceRoot.FileId`
并在 `:140-141` 校验 —— 单边 mask 会让**既有 registry 全部 `SOURCE_REGISTRY_UNAVAILABLE`**。

---

## 4. 陷阱区 —— 本会话 7 次同类错误（务必内化）

| # | 错误 | 谁发现 | 代价 |
|---|---|---|---|
| 1 | 把测试夹具副本错认成产品 bundle，断言「安装包不可用」 | 独立复核 | 一轮 |
| 2 | 从 `weights not found` 警告推断 `pending` 的原因 | 自测推翻 | 一轮 |
| 3 | probe 用点号命令名 ⇒ 误判「settings 域未挂载」 | 自测推翻 | 一轮 |
| 4 | probe 自己传 `null` ⇒ 误判「发现 payload bug」 | 自测推翻 | 一轮 |
| 5 | 给测试插诊断块时把 `return` 放到断言前 ⇒ **断言被跳过、测试假通过** | 自测（"太干净"起疑） | 一轮 |
| 6 | **把 `dotnet test` 的 `EXIT=0`（含 skipped）当成 passed** | 自测（加 `--logger detailed`） | **3 轮方向错误** |
| 7 | 修完 `HostIssuer` 就宣称「唯一产品缺陷已修、test.ps1 全绿」，**没查还有 2 个 handle probe** | AC6 独立复核 | 一轮 |

**共同根因**：用自己的临时工具/推断下结论，却**不先验证那个工具/推断是否忠实反映真实链路**。

**必须遵守的纪律**：

1. **判断测试通过要看具体结果行**（`已通过` / `失败` / `已跳过`）。
   `EXIT=0` 只说明**没有失败**，不说明**跑过了**。
   —— 用 `dotnet test --logger "console;verbosity=detailed"` 看 `[SKIP]`。
2. **诊断必须零侵入**：加日志不能改控制流。优先读仓库已有证据（wire log、TRX、evidence）。
3. **"测试全绿" ≠ "没 bug"**：当测试覆盖不到那条路径时（如 opt-in 的 `NEWMANGA_FEA11_IPC=1`），
   绿是假的安全感。
4. **修 producer 前先查有几处**：`grep -rn "FileIndexHigh\|IndexHigh"`，
   不要修完一处就宣称修完。
5. **改持久化数据的 producer 前先想兼容**：既有数据是 raw，单边 mask 会破坏它。

---

## 5. 治理约束（不可绕过）

- **仓库**：`G:\CODEX\New Manga`（唯一事实来源）；派生**一律**进 `G:\CODEX\New Manga.workspace`
- **可用 Agent**：仅 DSH / Codex / ZCode。**`subagent_agy` 禁用**（Antigravity 已退出）
- **Review 独立性**：按**上下文独立**，不要求非作者。作者可派新子 agent 只读审查
- **AC 标记格式**：`<<MET>>` / `<<PARTIAL: 原因>>` / `<<BLOCKED: 原因>>` / `<<NOT_APPLICABLE: 原因>>`，
  **必须严格在行末**（后面连 HTML 注释都不允许）；说明放在标记**之前**
- **§4.3.1**：`blocked` **必须不勾选**，`verified` **必须勾选**，翻转是**替换**不是并存
- **DAG 检查**：只有 `ready`/`in_progress`/`blocked`/`in_review`/`changes_requested`/`approved`
  六个状态要求登记 DAG；**`proposed` 不检查**（可用于规划卡）
- **证据 pin**：新增 `evidence_dir` 文件必须同时登记 EV 行；
  **`commit` 列必须是「实际引入该文件的 commit」**（用 `git log --diff-filter=A -- <path>` 反查），
  否则 `git cat-file -e` 会返回 128 —— **`check.ps1` 不校验这个，要自己查**
- **提交**：长中文 commit message 用 `git commit -F <file>`，不要 `-m`

---

## 6. 交接用的关键文件索引

| 用途 | 路径 |
|---|---|
| 收尾总账（上一 goal） | `doc/handoffs/GOAL-WRAPUP-R100.md` |
| 本文（启动包） | `doc/handoffs/NEXT-SESSION-STARTER.md` |
| 待重审卡 | `doc/tasks/HOST-CONCURRENCY-FLAKY-1.md` |
| 上一轮复核 | `verification/HOST-CONCURRENCY-FLAKY-1/review-ac6.md` |
| 目标 C 素材 | `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md` |
| 目标 B 素材 | `doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md`、`doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md` |
| 目标 D 素材 | `doc/reviews/HUMAN-REQUIRED-2026-11-15.md` |
| 当前 DAG | `doc/REBASELINE_PLAN.md` |
| 当前状态 | `doc/STATUS.md` |

---

## 7. 一句话交接

**目标 A 已达成（四件套 + `test.ps1` 全绿）；B/C/D 有明确缺口且已逐条列出。**
**最优先事项是 `HOST-CONCURRENCY-FLAKY-1` 的 AC6 二次复核 —— 上一轮复核抓到了作者漏修 2/3 的 producer，
说明独立复核在本项目里价值极高，不要跳过。**
