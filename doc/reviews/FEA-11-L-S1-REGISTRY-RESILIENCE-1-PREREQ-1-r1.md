---
task: FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
title: Review r1：C-15 v1.5 UNFREEZE（Registry 文件损坏与「根身份当前不可用」分离）
reviewer: fresh subagent（独立上下文；未参与起草；只读）
session: 94eab07b-7235-422e-b1f0-569c603e4cf7
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 821b309a0f6145ba085af2581541ee946cd5f949
reviewed_worktree: dirty（UNFREEZE 待提交字节；快照 2026-11-07T07:38:35+08:00）
verdict: changes_requested
---

# Review r1：C-15 v1.5 UNFREEZE（Registry 文件损坏与「根身份当前不可用」分离）

> 审查对象：`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md`、`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/**`。
> 审查口径：只读；事实以工作树最终字节为准（快照 `2026-11-07T07:38:35+08:00`，HEAD `821b309a0`）；未运行项一律 `NOT_RUN`。背景只读：`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`、`SourceAccessRegistry.cs:98-140`。

## 0. 结论先行

**verdict：`changes_requested`。P0 = 0 / P1 = 2 / P2 = 5 / P3 = 9。**

**C-15 v1.5 条款字节本身语义合格**：§5 的拆分保持了文件级损坏的整库 fail-closed、`SOURCE_REGISTRY_UNAVAILABLE`、`.corrupt-*` 复制与「不创建空文件/不覆盖」；根级不可用明确 `List` 可用、其余根不受影响、`Authorize` 逐请求重核验、该请求 typed 拒绝且零写；缺失根 ≠ 无授权；不自动重建/重授权/恢复；恢复与撤销语义未被放宽；错误码闭集零新增；C-16/C-17 及其余契约零字节。pin 可复算（`f9e376a0…`），`verify_pins` **18/18 PASS**，其余 17 pins 与 HEAD 记录逐项相同（抽查 4 项均一致）。本复核**未发现 P0，也未发现安全语义上的 P1**。

但**冻结包整体不能批准**，两条 P1 均为可窄面修复的簿记/门禁问题，不是 C-15 条款语义问题：

1. **P1-A 冻结矩阵 C-15 行未更新**（`FEA-CONTRACT_FREEZE_MATRIX.md:36` 仍是 `FROZEN v1.1` 2026-11-04、`verify_pins 17/17`），与同文件 `:3` 的 `C-15 v1.5`、C-15 状态行、FROZEN-C15 §1/§7 直接矛盾；载体 §2 D 明写的「C-15 行 → `FROZEN v1.5`（2026-11-07）」未落地，AC-T3 的「矩阵更新」未满足。
2. **P1-B `check.ps1` 门禁未通过且证据即为 FAIL**：`logs/check.log` 记录 `FAIL (2 errors)`，`logs/check-taskpath.log` 记录 `FAIL (4 errors)`；本复核重跑默认与 `-TaskPath` 均为 `FAIL (4 errors)`（`TASK_LEDGER` 528/529、10/11；PREREQ 未登记当前 DAG/READY）。AC-T3 的「`check.ps1`（默认 + `-TaskPath`）PASS」未满足，C-15 §9 条件③的 check 门禁未满足。且修复所需文件（`doc/TASK_LEDGER.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`）**不在 PREREQ 卡 `allowed_paths` 内**，需 DSH 以 Lead 身份单独治理更新或扩展本卡范围，不能靠卡内 P1 修复自然闭环。

另有 5 条 P2（A 卡工作树额外改动、`check.log` 不可复现/`EV.md` 缺失、跨契约错误码语义、派生状态未明示、AC-T4 指定措辞缺失）与 9 条 P3，见 §4。建议先完成 P1 与证据刷新，**若 C-15 字节保持不变**（当前 `f9e376a0…`），可做仅针对记录/门禁/证据的窄面复审；**若改动 C-15 任何字节**，须重算 pin、更新 FROZEN §1/§1B/§7 并重新窄面复核。

## 1. 只读基线（实测）

| 项 | 命令/对象 | 结果 |
|---|---|---|
| 分支 / HEAD | `git rev-parse --abbrev-ref HEAD`、`git rev-parse HEAD` | `main` / `821b309a0f6145ba085af2581541ee946cd5f949` |
| 工作树 | `git status --porcelain=v1 -uall`（07:38:35） | `M` C-15、FROZEN-C15、矩阵、**A 卡**；`??` 载体、证据目录 7 文件、**L-S4 scope-r1（并发）** |
| tracked diff | `git diff --name-only HEAD` | C-15 / FROZEN-C15 / 矩阵 / **A 卡**（PREREQ 卡已在 HEAD 提交，不在 diff 内） |
| C-15 实测 sha256 | `Get-FileHash -Algorithm SHA256` | `f9e376a0ed4ce2aaf87c5c698798b0f7a802a3b87a0de9845bc96c3f9bfff4d6` |
| C-15 `git hash-object` | `git hash-object` | `b0360cc975d361c3f1431b4c7e644bc1735981ab` |
| HEAD 原 v1.1 blob | `git rev-parse HEAD:doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `a0286bac06aa89587a6a7cbcf08461aae8add865`（sha256 `d8c0a3bc…`） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**；C15 `f9e376a0ed4c`；C16 `ad25fb3c89bb`；C17 `aefa0fa5b17e` |
| 治理检查（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **FAIL (4 errors, 3 warnings)**，exit 1 |
| 治理检查（本卡） | `... -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | **FAIL (4 errors, 3 warnings)**，exit 1 |
| 证据 pins | `logs/pins.log` | 18 行 OK + `PIN AUDIT: PASS (all 18)`（与重跑一致） |
| 证据 check | `logs/check.log` / `logs/check-taskpath.log` | `FAIL (2 errors)` / `FAIL (4 errors)` |
| 证据 pre/post | `pre-post.sha256` | pre `d8c0a3bc…`（= HEAD v1.1 blob 字节）/ post `f9e376a0…`（= v1.5 pin） |

**并发说明**：复核期间观察到另一会话的 `doc/reviews/FEA-11-L-S1-L4-LOCATION-AUTH-REFRESH-1-scope-r1.md` 时隐时现（07:32 出现、07:33 消失、07:38 再出现），且 07:40 后 `doc/tasks/FEA-11-L-S1-L4-LOCATION-AUTH-REFRESH-1.md` 也出现并发修改；两者均不在被审集，未读取、未用于任何结论。A 卡 mtime `2026-11-07T07:29:48` 晚于本复核开始（07:29:27）。以上均非本报告产物。

## 2. A–G 逐项

### A. diff 最小性 — **FAIL**

| 检查 | 结果 | 证据 |
|---|---|---|
| `git diff --name-only HEAD` 文件集 | **含 1 个未列入被审集的 tracked 文件**：`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`（A 卡，+58/−19，`proposed`→`ready`、`depends_on`→PREREQ、`allowed_paths` 增 `SourceAccessRegistry.cs` 与两测试文件、新增 AC-L1…L8）；C-15/FROZEN/矩阵在集内；PREREQ 卡已在 HEAD 提交、不在待提交 diff | `git diff --name-only HEAD`、`git diff HEAD -- doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` |
| C-15 逐行对应载体 §2 | **PASS**：仅 4 个 hunk——①头部状态/日期（对载体 §2 A）②§5 三行拆分：文件级损坏 / 根身份不可用 / 恢复（对载体 §2 B）③§9 条件⑤（对载体 §2 C）④变更记录 v1.5 行（对载体 §2 C）；无未登记 C-15 改动 | `git diff HEAD -- doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`；`FEA-C15_SOURCE_STORAGE_DRAFT.md:3-4,312-314,347,354` |
| FROZEN-C15 对应载体 §2 D | **基本 PASS**：冻结时间、§1 version/pin/hash-object/blob、§2 条件行 5、§7 v1.5 段均在 §2 D 的「pin + 重冻记录」范围内；但 §1B 新增「v1.5 复核字节 = f9e376，pending」为**复核前预填复核字节值**（见 P3-F08） | `FEA-CONTRACT-FROZEN-C15.md:4,15-18,36,46,75-85` |
| 矩阵 | 文件在集内，但**只改了状态行 `:3`，C-15 行 `:36` 未改**（见 E / P1-A） | `FEA-CONTRACT_FREEZE_MATRIX.md:3,36` |
| 证据 | 目录 7 文件为 untracked（`carrier.md`、`pre-post.sha256`、`changed-lines.diff`、`other-17-pins.txt`、3 个 log）；载体 §7 还引用 `EV.md`，**该文件不存在**（P3-F11） | 目录清单、`CONTRACT-UNFREEZE-2026-11-07-C15.md:58-61` |
| src/apps/tests/tools | **零 diff** | `git diff --name-only HEAD` 不含这些路径 |

**判定**：C-15 字节改动本身是最小的且逐项可对账；但 UNFREEZE 提交面不干净——A 卡是**未披露的关联工作树改动**（不属于载体 §0 的「载体 + C-15 + 冻结记录 + 矩阵」提交集，也不在 PREREQ 卡 `allowed_paths`），且 PREREQ 卡不在待提交 diff（已在 HEAD）。若以 `git add -A` 形成 UNFREEZE 提交，会污染最小 diff。**A = FAIL**。

### B. 语义审查（重点） — **PASS**

**① 文件级损坏仍整库 fail-closed — PASS。** `FEA-C15_SOURCE_STORAGE_DRAFT.md:312` 明确「文件级损坏（magic/version/长度/DPAPI/JSON 任一不合法）= 损坏：fail-closed，不创建空文件、不覆盖；所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`；原字节复制 `registry.v1.dat.corrupt-<utc>`（复制，不移动）」。`:311` 的「文件缺失 = 合法空 Registry」未变；`:316-318` 的 ACL/加密、备份交接、日志约束未变。旧 `roots identity` 从损坏条件移出是本次唯一语义移动，落在 ②。

**② 根身份当前不可用 — PASS。** `:313` 明确：根不存在、路径不可读、卷/文件 identity 与登记不符**不再判文件损坏**；registry 文件仍合法可读；该根条目以「当前不可用」参与读取（`List` 可用、其余根不受影响）；`Authorize` 对请求路径所属根**逐请求**重核验 identity；不可用/不匹配 → 该请求 typed 拒绝（沿用既有 `SOURCE_REGISTRY_UNAVAILABLE`，零新错误码）、**零写**。生产调用面与「授权期」一致：`SourceReadCoordinator.cs:400/403/467` 与 `HostOperationOrchestrator.cs:132/296` 都经 `SourceAccessRegistry.Authorize` 铸造型授权；`List` 由 watcher/scan/coordinator/orchestrator 读取（`SourceWatcher.cs:416`、`SourceScanScheduler.cs:1566/1874/2080`、`SourceReadCoordinator.cs:622`）。扫描枚举路径另有既有 `VerifyEnumeratedTarget` 身份核验（`SourceScanScheduler.cs:1561-1632`，identity 不符/缺失 → `SOURCE_REGISTRY_UNAVAILABLE`），watcher 只规划 watch、不授予读取（`SourceWatcher.cs:409-523`）；因此移除 `Load` 身份校验后，**所有实际读取仍经 `Authorize` 或该既有身份核验 fail-closed**，未发现绕过路径（背景只读，非被审字节）。

**③ 缺失根 ≠ 无授权、不得自动重建/重授权/恢复 — PASS。** `:313` 三处明文：「**缺失根永不等于「无授权」**」「不得自动重建 identity、不得自动重授权/自动恢复」；`:314` 再次禁止「因根缺失而静默重建」。这与 scope review 的 I-3 红线（不得自动重新授权）一致。

**④ 恢复语义未被放宽 — PASS。** `:314`：文件级损坏仍由显式 `source_reset_registry {confirm:true}` 移入 `quarantine/` 后创建新空 Registry（用户显式操作）；根级恢复（重新授权/重定位）由显式用户操作完成，不得自动、不得静默重建。旧「显式用户操作」约束保留，新增「根级不得自动」是收紧而非放宽。P3：合同未明写 reset **不得**用于根级恢复（仅能由「文件级损坏仍由…」推得），存在用户以 reset 清空全部授权的误用面（见 P3-F14）。

**⑤ 撤销零改动、错误码闭集零新增 — PASS。** `:315` 撤销行与 v1.1 **逐字节相同**（diff 无该行）：generation+1、持久化 `revoked_at`、`RevokeSourceReadGrant`（C-16）+ Core ACK、ACK 失败仍持久化撤销。`:313` 明确「沿用既有 `SOURCE_REGISTRY_UNAVAILABLE`，零新错误码」；C-16 §6 错误码表（`FEA-C16_SOURCE_READ_WIRE_DRAFT.md` §6；`PAGE_UNAVAILABLE_CODES` 为该表的 11 码子集）字节未变。**P2**：C-16 §6 表把该码描述为「Registry 不可读/不可写/损坏」（internal/retryable），C-06 §2.2「失败」行又写「identity 变化 → `SOURCE_ACCESS_DENIED`」（`FEA-C06_SOURCE_AUTH_DRAFT.md:44`）；C-15 v1.5 把同码用于「该请求所属根不可用」并宣示「缺失根 ≠ 无授权」，与两处冻结文字存在定义漂移。该漂移已被 scope review 指出、D-2 裁决保留现状码、A 卡 limitation #3 登记；但 C-15/载体未显式引用该裁决与 precedence（见 P2-F05）。

**⑥ 未被悄悄放宽 — PASS。** 文件级损坏仍整库 fail-closed；根级只影响该根相关请求；无路径回退；无部分读取；无自动重授权/自动恢复；其余根不受影响；`Authorize` 失败零写。未发现「把失败根当作已授权」「允许路径回退」「允许部分读取」的改写。P3 语义清晰度项：条目结构校验未列入文件级枚举（F12）、条目保留未显式禁止删除（F13）、「当前不可用」未写明 derived/不持久化（F06→P2）、`Authorize` 检查顺序与 revoked/generation 的优先级未规定（F15）。

### C. 不变量零改动 — **PASS**

| 不变量 | 结果 | 证据 |
|---|---|---|
| C-16 / C-17 | 字节零改动 | `git diff --name-only HEAD` 不含；`verify_pins` C16 `ad25fb3c89bb`、C17 `aefa0fa5b17e` 均 OK |
| 其余 17 契约 | 字节零改动 | 同上；`other-17-pins.txt` 17 行 `UNCHANGED`；抽查 C05/C06/C16/C17 工作树 hash 与 pin 一致，且对这 4 文件 `git diff HEAD` 为空 |
| wire / 命令集 / 能力 / TTL / schema / 依赖 | 零改动 | C-15 仅改 Host 语义句，未新增字段/命令/能力；C-15 §5 JSON schema 未变；C-16 ≤300s TTL 未变；无 `src/**`、`apps/**`、`tests/**`、`tools/**` diff；无依赖文件 diff |
| `CORE_PROTOCOL_MINOR` | 不变 | `src/bootstrap/core_service.py:320` `PROTOCOL_MINOR = 3`；无 src diff；证据脚本口径 `CORE_PROTOCOL_MINOR=3` |
| 错误码闭集 | 零新增 | C-16 §6 错误码表未变（`PAGE_UNAVAILABLE_CODES` 11 码子集亦未变）；C-15 复用 `SOURCE_REGISTRY_UNAVAILABLE`；无新码字符串 |

### D. pin 可复算 — **PASS**

| 项 | 期望（记录/任务） | 实测 | 结论 |
|---|---|---|---|
| C-15 v1.5 工作树 sha256 | `f9e376a0ed4ce2aaf87c5c698798b0f7a802a3b87a0de9845bc96c3f9bfff4d6` | `f9e376a0ed4ce2aaf87c5c698798b0f7a802a3b87a0de9845bc96c3f9bfff4d6` | **MATCH** |
| `git hash-object` | `b0360cc975d361c3f1431b4c7e644bc1735981ab` | `b0360cc975d361c3f1431b4c7e644bc1735981ab` | **MATCH** |
| blob 内容 sha256（LF） | `f9e376a0…`（FROZEN §1A） | `git cat-file blob b0360cc9…` → `f9e376a0…` | **MATCH**（v1.5 三口径一致） |
| HEAD 原 v1.1 字节 | `d8c0a3bc…`（pre-post pre） | `git cat-file blob a0286bac0…` → `d8c0a3bc…` | **MATCH** |
| `verify_pins` | 18/18 PASS | 18 行 OK + PASS，exit 0 | **PASS** |
| 其余 17 pins | 与 HEAD 记录逐项相同 | `verify_pins` 全 OK；`git diff HEAD` 对 17 契约为空；抽查 C05 `f6e6f3cb`、C06 `99831a20`、C16 `ad25fb3c`、C17 `aefa0fa5` 与各自记录 pin 一致 | **PASS** |
| `verify_pins.ps1` | 不改 | `git diff HEAD -- tools/governance/verify_pins.ps1` 为空 | **PASS** |

**P3-F16（pin 复算的环境依赖，pre-existing）**：`core.autocrlf=true`、`git ls-files --eol` 显示 C-15 为 `i/lf w/lf attr/`（无 `eol` 规则）；若干净 checkout 把工作树写成 CRLF，C-15 的 `Get-FileHash` 将变为 `6d87093cd695f926fae01425a14029c580438fef40dac59fb2e77afcb5af6e10`，`verify_pins` 会失败。C-17 当前就是 `w/crlf` 并按 CRLF pin（`aefa0fa5…`），说明仓库 pin 口径绑定工作树 EOL；C-05/C-06/C-16 的 LF pin 同样存在此风险。当前工作树 PASS，但该口径跨 checkout 不稳。建议为冻结契约加 `text eol=lf`（`doc/.gitattributes` 或根 `.gitattributes`）或把 pin 口径改为 blob sha256；两者均不在本卡 `allowed_paths`，需另案/登记 limitation。

### E. 冻结记录/矩阵一致性 — **FAIL**

**PASS 部分**：

- FROZEN-C15 版本/pin/历史 pin/§1A/§1B/§2 条件行/§7 自洽：`FEA-CONTRACT-FROZEN-C15.md:15` v1.5、`:16-18` 三指纹、`:36` v1.5 复核字节、`:46` 条件 5 `⏳`、`:75-85` §7 段；历史 v1.0 `6da686…`、v1.1 `d8c0a3bc…` 保留；v1.5 `f9e376…` 与 C-15 实测一致。
- 「无复核前预填 approved」：载体 §6 `r1: pending`（`:53`）、FROZEN §2 行 5 `⏳`、§7「pending」——**PASS**。FROZEN §1B 预填的是「复核字节值」而非 approved（P3-F08）。
- C-15 状态行 `:3` 只写「v1.5 独立 byte-level 复核见载体」，未写 approved；日期行 `:4` 补 v1.5；§9 条件⑤ `:347` 与变更记录 `:354` 与 v1.5 一致。

**FAIL 部分**：

- **矩阵 C-15 行 `FEA-CONTRACT_FREEZE_MATRIX.md:36` 仍为 `FROZEN v1.1` 2026-11-04，条件 `verify_pins 17/17`**，而同文件 `:3` 已写 `C-15 v1.5` 2026-11-07；与 C-15 `:3`、FROZEN-C15 `:15-18/:75-85` 矛盾。载体 §2 D 明写「C-15 行 → `FROZEN v1.5`（2026-11-07）」，未落地；AC-T3「矩阵更新」未满足 → **P1-A**。
- 矩阵 `:37` C-16 行依赖列仍写 `C-15 v1.1`。这是 C-16 冻结时的历史依赖记录（C-16 v1.4 冻在 C-15 v1.1 之后），C-15 v1.5 是兼容收紧，不构成字节冲突；建议在修 `:36` 时改为 `C-15 v1.5` 或明确标注 historical（P3 备注，不单列 finding）。
- FROZEN 头部 `:6`「授权：FEA-09-PREREQ-1；独立复核 r7 approved」只覆盖 v1.0/v1.1；v1.5 的授权/触发在 §7，头部未提（P3-F10）。
- FROZEN §2 条件 5 的证据列只引载体 §6 + `pins.log`，未把 AC-T3 的 `check.ps1` PASS 纳入条件；在 check 为 FAIL 的当前状态下，该条件行没有暴露门禁失败（P1-B 的一部分）。
- FROZEN §3 `:50` 仍写 C-05 v1.1/C-06 v1.1（矩阵/现状已 v1.2），pre-existing 陈旧；v1.5 未触碰，不构成新不一致，但读记录时需注意（P3 备注）。

### F. 载体/卡不夸大 — **PASS**

| 要求 | 结果 | 证据 |
|---|---|---|
| 保留 A/B/C 拆卡 | **PASS** | PREREQ 卡 D-3（`:48`）；载体 §0「A 实现另卡 / B 恢复另卡」（`:5`）；A 卡 limitation 列 B/C（`:69-74`） |
| 「恢复路径今天不存在」 | **PASS** | 载体 §3「恢复路径今日不存在（App 无调用）：B 卡接线，不因本契约自动可用」（`:38`）；A 卡 limitation「B 不存在…另卡」（`:71`）；scope review `:28` 同结论 |
| A 必须补 `Authorize` 校验（只删不补 = 安全回退） | **PASS** | 载体 §3 `:37`、§4 风险②`:42`；A 卡红线 `:42`、In.3 `:49`、AC-L3 `:62`（「只删 Load 校验不补 Authorize → RED」） |
| 不把契约就绪写成实现/产品可用 | **PASS（措辞 P2）** | 载体 §3 用「新实现…（受 A 卡控制）」将来时、§4 回退「A 卡不释放」；PREREQ 卡首段「只起草 + 独立复核 + 重冻；不实现」；A 卡「待实施」`:87`；无「已实现/可用」宣称。但 **AC-T4 要求的字面「契约就绪 ≠ 实现/产品可用」在载体中缺失**（P2-F07） |
| 未改 Run wire/schema/依赖 | **PASS** | C 项已列；载体 §3 `:36`「错误码不变、wire 不变、无 schema/依赖变化」 |

### G. 证据真实性 — **FAIL**

| 证据 | 结果 | 说明 |
|---|---|---|
| `pre-post.sha256` | **PASS** | pre `d8c0a3bc…` = HEAD v1.1 blob LF 字节（`git cat-file blob a0286bac0` 实测同值）；post `f9e376a0…` = v1.5 pin/工作树实测同值 |
| `changed-lines.diff` | **PASS** | 与 `git diff --no-color HEAD -- doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` 归一化（CRLF→LF、去尾换行）**逐字符相等**；含全部 4 个 hunk；行数 39/40 差异仅为尾换行 |
| `logs/pins.log` | **PASS** | 与重跑 `verify_pins` 输出逐行相同（18 OK + PASS） |
| `logs/check-taskpath.log` | **PASS（可复现）** | 与重跑 `check.ps1 -TaskPath …PREREQ-1.md` 的 4 errors/3 warnings 完全一致 |
| `logs/check.log` | **FAIL（不可复现/已过期）** | 记录 `FAIL (2 errors)`；当前同命令为 `FAIL (4 errors)`，多出「当前 DAG 未登记非终态 Task：FEA-11-L-S1-REGISTRY-RESILIENCE-1」「READY Task 未出现在 Plan 的 READY 节点」。原因（推断）：记录生成时 A 卡仍为 `proposed`（默认检查经 STATUS 行首个 task 链接选中 A 卡，proposed 不触发 DAG/READY 错误），A 卡在 07:29:48 被并发改为 `ready` 后同一命令出现 4 errors。记录与最终工作树不一致 → P2-F04 |
| 日志元数据 | **FAIL（弱证据）** | 3 个 log 只有输出文本，无命令行、无时间戳、无 HEAD/工作树快照、无 exit code；无法独立复现生成条件 |
| `EV.md` | **FAIL（缺失）** | 载体 §7 `:60` 明确列举 `carrier.md`、`EV.md`；证据目录无 `EV.md`（`Test-Path` = False）→ P3-F11 |
| `carrier.md` | **PASS（内容一致，链接相对位置失效）** | 与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md` 归一化后**相同**；但作为 `verification/.../carrier.md` 副本，文内 `../plan/…` 链接从 verification 目录解析不到 `doc/plan`（不影响被审字节，P3-F11） |

## 3. 安全语义逐条判定

| # | 安全断言 | 判定 | 证据 / 说明 |
|---|---|---|---|
| ① | 文件级损坏（magic/version/长度/DPAPI/JSON 任一不合法）→ 整库 fail-closed、`SOURCE_REGISTRY_UNAVAILABLE`、corrupt 复制、不创建空文件/不覆盖 | **PASS** | C-15 `:312`；`Load()` 现有文件级校验路径 `SourceAccessRegistry.cs:101-118,132-138`（背景） |
| ② | 根身份当前不可用/不匹配 → `List` 可用、其余根不受影响、`Authorize` 逐请求重核验、该请求 typed 拒绝、零写 | **PASS** | C-15 `:313`；生产 `Authorize` 调用点 `SourceReadCoordinator.cs:400/403/467`、`HostOperationOrchestrator.cs:132/296`；`List` 读点 `SourceWatcher.cs:416`、`SourceScanScheduler.cs:1566/1874/2080`、`SourceReadCoordinator.cs:622` |
| ③ | 缺失根 ≠ 无授权；不得自动重建 identity/自动重授权/自动恢复 | **PASS** | C-15 `:313`：「缺失根永不等于「无授权」」「不得自动重建 identity、不得自动重授权/自动恢复」；`:314`「不得因根缺失而静默重建」 |
| ④ | 恢复：`source_reset_registry` 仅文件级损坏；根级恢复仅显式用户操作；语义未放宽 | **PASS** | C-15 `:314`；旧「显式用户操作」保留并增「不得自动」。P3：未明写 reset 不得用于根级（F14） |
| ⑤ | 撤销生成+1/`revoked_at`/C-16 ACK 零改动；错误码闭集零新增（复用既有码） | **PASS** | C-15 `:315` 与 v1.1 同字节；`:313` 明写零新码；C-16 §6 错误码表未变。P2：跨契约码义漂移（F05） |
| ⑥ | 无悄悄放宽（失败根≠已授权、无路径回退、无部分读取、无自动恢复） | **PASS** | 文件级仍整库 fail-closed；根级只拒绝该请求；无路径回退/部分读取/自动重授权。P3 清晰度项 F12/F13/F15 |
| C 项 | wire/命令集/能力/TTL/schema/依赖/C-16/C-17/其余 17 契约/CORE_PROTOCOL_MINOR 零改动 | **PASS** | 见 §2.C；`PROTOCOL_MINOR=3`；无 src/apps/tests/tools diff |

**总体安全结论**：C-15 v1.5 的拆分是**可用性放宽**而非**授权放宽**——不可用根仍被 `Authorize` 拒绝，且缺失根不被当作「无授权」，不存在自动重授权/自动恢复。文件级损坏的整库 fail-closed、corrupt 复制、不创建/不覆盖均保留；撤销与恢复未被放宽。**本复核未发现安全语义 P0/P1。**

## 4. Findings

| ID | 级别 | 位置 | 问题 | 处置建议 |
|---|---|---|---|---|
| F-01 | **P1** | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:36` | C-15 行仍 `FROZEN v1.1` 2026-11-04、`verify_pins 17/17`；与 `:3` 的 v1.5、C-15 `:3`、FROZEN §1/§7 矛盾；载体 §2 D 未落地；AC-T3「矩阵更新」未满足 | 改为 `FROZEN v1.5` 2026-11-07，条件改为 v1.5 复核 approved / C-16/C-17 零改 / `verify_pins` 18/18 / `check` PASS；`:37` 依赖列同步 v1.5 或标 historical |
| F-02 | **P1** | `logs/check.log`、`logs/check-taskpath.log`、当前重跑 | `check.ps1` 默认与 `-TaskPath` 均 `FAIL (4 errors)`：TASK_LEDGER 528/529、10/11；PREREQ 未登记 DAG/READY；默认检查还因 A 卡 ready 未登记报错。AC-T3 的 check PASS 未满足，C-15 §9③ 门禁未满足；D-8「已修台账」与实际不符。且修复文件（TASK_LEDGER/REBASELINE_PLAN/STATUS）不在 PREREQ `allowed_paths` | 由 DSH 以 Lead 身份跑 `task_ledger.py --write`、把 PREREQ 登记进当前 DAG/READY（并同步 STATUS），或扩展本卡范围；重跑默认 + `-TaskPath` 至 PASS 并刷新日志 |
| F-03 | **P2** | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | A 卡工作树 +58/−19（`proposed`→`ready`、`depends_on`→PREREQ、`allowed_paths` 增生产源码/测试、AC-L1…L8），不在载体 §0 的 UNFREEZE 提交集，也不在 PREREQ `allowed_paths`；与 STATUS/Plan 的 `proposed` 不一致；是默认 check 额外错误的直接来源；mtime 07:29:48 疑为并发写入 | 与 UNFREEZE 提交**分离**：或回退为 proposed、或按 A 卡自身流程单独提交并在 Plan/DAG 登记；UNFREEZE 提交不得 `git add -A` 带入 A 卡。若 DSH 确认 A 卡属于本批，则升为 P1 |
| F-04 | **P2** | `logs/check.log`、证据目录 | 记录为 FAIL(2) 而当前为 FAIL(4)，不可复现；3 个日志无命令行/时间戳/HEAD/exit code；`EV.md` 被载体 §7 引用但不存在；`carrier.md` 副本 `../plan` 链接从 verification 目录失效 | 在最终工作树上重跑并刷新日志（含命令、时间、HEAD、exit code）；补 `EV.md` 或从载体 §7 删除引用；副本链接改为 `../../doc/plan/…` 或只保留源文件 |
| F-05 | **P2** | C-15 `:313`；C-16 §6 `:177`；C-06 §2.2 `:44` | 复用 `SOURCE_REGISTRY_UNAVAILABLE` 表示「该请求根不可用」，与 C-16 表「Registry 不可读/不可写/损坏」及 C-06「identity 变化 → `SOURCE_ACCESS_DENIED`」存在定义漂移；C-15/载体未显式引用 D-2 裁决与 precedence，limitation 仅落在 A 卡 #3 | 在载体 §3/§4 或 C-15 §5 加一句：该码在本契约下的含义 = 文件级损坏或该请求所属根当前不可用；按 D-2 保留现状码，词表细化另案；冻结记录 §7 标注 limitation。若改 C-15 字节需重算 pin |
| F-06 | **P2** | C-15 `:313`；PREREQ I-2 `:65`；A 卡 In.2 `:48` | 「该根的条目以『当前不可用』状态参与读取」未写明状态是 **derived/不持久化**；可能被实现为新增持久字段或 `List` wire 字段，撞 C-15 `format_version=1` 与 C-16 §1 零改 | 在 C-15 §5/载体加「不可用状态为派生态、不持久化、不新增 wire 字段」；A 卡 In.2 同步，避免 List 投影被读成 C-16 §1 增补（B 卡范围） |
| F-07 | **P2** | `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md:33-38` | AC-T4 要求载体「明写『契约就绪 ≠ 实现/产品可用』」，载体只有「新实现（受 A 卡控制）」「恢复路径今日不存在」「A 卡实现必须补」等间接表述，无该字面句 | 载体 §3 增一句「本载体仅冻结契约字节，不构成实现授权/产品可用证据；A/B 实现另卡」 |
| F-08 | **P3** | `FEA-CONTRACT-FROZEN-C15.md:36` | §1B 在 r1 复核前预填「v1.5 复核字节 = f9e376（= 冻结字节；r1 复核 pending）」；值本身与最终字节一致且有 pending 标注，但程序上属复核前预填 | 复核后把该行改为「r1 复核确认 f9e376」或保留 pending 至 DSH 追加结论；不得预填 approved |
| F-09 | **P3** | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md:68` | I-2 写「§10 冻结条件追加 v1.5 条」，C-15 实际章节为 **§9**（载体 §2 C 也写 §9） | 改为 §9 |
| F-10 | **P3** | `FEA-CONTRACT-FROZEN-C15.md:6`、`:50` | 头部「授权：FEA-09-PREREQ-1；r7 approved」只覆盖 v1.0/v1.1；v1.5 授权在 §7，头部未提；§3 仍写 C-05 v1.1/C-06 v1.1（现状 v1.2） | 头部补「v1.5 见 §7」；§3 依赖版本改为 v1.2 或标注 historical（pre-existing 陈旧项可一并修） |
| F-11 | **P3** | 载体 §7 `:58-61`；证据目录 | 引用 `EV.md` 不存在；`carrier.md` 副本内 `../plan/…`、`../reviews/…` 从 verification 目录解析失效 | 补 `EV.md` 或删引用；副本链接改为 `../../doc/…` 或注明「副本，链接以源文件为准」 |
| F-12 | **P3** | C-15 `:312` | 文件级损坏枚举为 magic/version/长度/DPAPI/JSON，未写「条目结构」（generation/registryId/roots 非空/root 规范化/`readable`）；A 卡 In.1 明确把「条目结构」留在文件级。严格读者可能把结构异常误归根级 | 在 `:312` 括号内加「条目结构」或在 §5 加一句「结构校验仍属文件级损坏」 |
| F-13 | **P3** | C-15 `:313` | 未显式禁止删除/静默丢弃不可用根条目；A 卡 In.2 有「不删除条目、不静默丢弃」，但契约本身未写 | 在 `:313` 加「条目保留、不删除、不静默丢弃」 |
| F-14 | **P3** | C-15 `:314` | 未明写 `source_reset_registry` **不得**用于根级恢复；仅能从「文件级损坏仍由…」推得，用户可能用 reset 清空全部授权 | 加一句「根级不可用不得以 reset 作为恢复路径；reset 仅用于文件级损坏」 |
| F-15 | **P3** | C-15 `:313` | `Authorize` 的检查顺序（revoked / generation / identity）未规定；若 identity 检查先于 revoked，不可用根可能掩盖 `SOURCE_GRANT_REVOKED`，与 C-16 §6 失败优先级不一致 | 明确 revoked/generation 先于 identity；identity 失败仅在未撤销时返回 `SOURCE_REGISTRY_UNAVAILABLE` |
| F-16 | **P3** | C-15 pin 口径 | `core.autocrlf=true` 且 C-15 无 `eol=lf`；干净 checkout 若写 CRLF，`Get-FileHash` = `6d87093c…`，`verify_pins` 将失败；C-17 已按 CRLF pin、C-05/C-06/C-16 为 LF pin，口径不统一（pre-existing） | 为冻结契约加 `text eol=lf`（或统一 pin 为 blob sha256）；不在本卡 `allowed_paths`，另案/登记 limitation |

## 5. 最终 verdict 与处置建议

**verdict：`changes_requested`。**

- **P0 = 0**：未发现数据损坏、授权放宽、fail-open、静默自动恢复或冻结字节污染。
- **P1 = 2**：F-01 矩阵行未更新；F-02 check 门禁 FAIL（且修复路径超出本卡 allowed_paths）。
- **P2 = 5**：F-03 A 卡额外改动；F-04 证据不可复现/EV 缺失；F-05 跨契约错误码定义漂移；F-06 派生状态未明示；F-07 AC-T4 字面缺失。
- **P3 = 9**：F-08…F-16。

**最小放行路径**（建议按序）：

1. 更新矩阵 `:36`（v1.5/2026-11-07、18/18、check PASS），`:37` 依赖同步/标注。
2. 由 DSH 以 Lead 身份更新 `doc/TASK_LEDGER.md`、`doc/REBASELINE_PLAN.md`（当前 DAG/READY 登记 PREREQ）、`doc/STATUS.md`；若不愿扩卡，需在 PREREQ 卡外单独记录该治理更新的授权与证据。
3. 重跑 `check.ps1`（默认 + `-TaskPath`）至 PASS；在最终工作树重生成 `logs/check.log`、`logs/check-taskpath.log`（含命令/时间/HEAD/exit code）；补 `EV.md` 或删引用；`pins.log`/`pre-post`/`changed-lines` 可在同一快照刷新。
4. A 卡与 UNFREEZE 提交分离：UNFREEZE 提交只含 C-15/FROZEN/矩阵/载体/证据；A 卡按自身流程（或先回退 proposed）另行登记提交。
5. P2 建议在本次或紧随的窄面修订中处置，尤其 F-05（码义/裁决引用）与 F-07（AC-T4 字面）；若触碰 C-15 字节（F-05/F-06/F-12…F-15 的合同措辞修订），必须重算 pin、更新 FROZEN §1/§1B/§7 与证据，并重新窄面复核。

**关于 C-15 字节**：若只修记录/门禁/证据而**不动 C-15**，`f9e376a0ed4ce…` 仍是有效 pin，无需重签；若采纳 F-05/F-06/F-12…F-15 中任何 C-15 文字修改，pin 必然变化，需按冻结纪律重走窄面复核。

### 5.1 复核后状态（07:42，供 r2 参考；不改变 r1 快照结论）

本报告快照（07:38:35）之后，工作树出现并发修复，已实测：矩阵 `:36` 已改为 `FROZEN v1.5` 2026-11-07（条件 v1.5 复核 / C-16/C-17 零改 / 18/18 / PASS）；`doc/REBASELINE_PLAN.md` READY 节点已含 `...PREREQ-1`、`...REGISTRY-RESILIENCE-1`、`...L-S4...`；`doc/STATUS.md` 当前 Task 已登记 PREREQ/A/L-S4；`doc/TASK_LEDGER.md` 已更新；`verification/.../EV.md` 已补；`logs/check.log`、`logs/check-taskpath.log`、`logs/pins.log` 已于 07:42 刷新为 **PASS**。重跑默认与 `-TaskPath` 均 **PASS (3 warnings)**，`verify_pins` **18/18 PASS**，C-15 仍为 `f9e376a0…`（未变）。因此 **F-01、F-02、F-04 的 P1/证据面在 07:42 字节上已消除**；F-03 的 A 卡已进入 Plan READY/STATUS，不再是未登记状态（仍需与 UNFREEZE 提交分离）。**r2 应基于 07:42 后的字节复核**：确认证据已刷新且与最终字节一致、A 卡与 UNFREEZE 提交隔离，并处置剩余 P2（F-05/F-06/F-07）与 P3；若 C-15 字节未变，pin 仍为 `f9e376a0…`，无需重签。

## 6. 真实性声明

- 本报告作者为**独立上下文 fresh subagent**（session `94eab07b-7235-422e-b1f0-569c603e4cf7`），未参与本 UNFREEZE 的起草、前轮复核或实现；本报告是本次复核**唯一写入的文件**。
- 未修改 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`doc/tasks/**`、`verification/**` 的任何字节；未执行 `git add`/`commit`/`push`。
- 事实以 `2026-11-07 07:29–07:38 +08:00` 的工作树字节为准，`reviewed_head = 821b309a0f6145ba085af2581541ee946cd5f949`；工作树为 dirty（UNFREEZE 待提交字节），已在 §1 记录快照。
- 已运行：`git rev-parse/status/diff/hash-object/cat-file`、`Get-FileHash`、`verify_pins.ps1`、`check.ps1`（默认与 `-TaskPath`）、`Select-String`、`Get-Content`、目录/时间戳检查。**未运行**：pytest/.NET 构建与测试、真机 IPC、DPAPI 原生往返、A 卡实现测试、B 卡恢复流程——均标 `NOT_RUN`，不作为本报告结论依据。
- 复核期间观察到并发写入（A 卡 07:29:48、L-S4 scope-r1 时隐时现）；本报告未把并发未完成状态当作被审 UNFREEZE 字节，但已把其对 `check`/证据的影响记入 F-02/F-03/F-04。
