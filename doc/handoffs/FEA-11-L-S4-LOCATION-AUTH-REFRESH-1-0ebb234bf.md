---
task_id: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
author: l-s4-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 55306cb84
start_head: db12dc5e5
delivery_head: 0ebb234bf
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S4-LOCATION-AUTH-REFRESH-1（A：location auth 原地刷新；零契约）

- Task：`doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`（Owner=`l-s4-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=55306cb84`；实现起点 `db12dc5e5`（`main`，工作树 clean，实测）
- **delivery_head=`0ebb234bf`**（测试提交 `0ebb234bf` + 实现提交 `6dd36aad7`；本 Handoff/卡面/证据为随后同批文档提交）
- 权限依据：卡面（`status: ready`，零契约 0/18 pins）+ DSH 裁决 D-1…D-6 + `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md`（**READY-TO-FREEZE 仅 A 面**）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移

## 1. 交付结果（AC-LS4-1…8 全 MET；卡面已勾选，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-LS4-1 单点实现** | MET | `SqliteLibraryRepository.refresh_source_location_auth` 为全 `src/**` **唯一** `UPDATE source_locations SET registry_id` 字节（grep 判别测试）；`service.py:504-515` 旧内联 UPDATE 删除；relink 行为不变（既有 5 例全绿）；生产调用者 ≥3（repository 页单元 + D-2 独立写单元 + apply face） |
| **AC-LS4-2 重导入/relink 刷新** | MET | relink 跨 registry（rename 同 inode → `reg-2`）：三列刷新、`last_verified_at` 非空 ISO、`location_id`/身份键/`observed_at`/`is_current`/binding 逐列不变、无新 location 行；同 registry 代次 `1→2` 跟随而 binding 代次不被抬升；import 复用（同源第二 project）页单元内刷新 |
| **AC-LS4-3 sync apply 刷新（含 D-2）** | MET | 同容器 resync 跨 registry 在 apply 事务内刷新（页/binding 代次不变）；整源 skip 仅一次条件刷新（`imported_pages=0/skipped_sources=1`，页/版本/位置计数不变）；`import_as_new` 全已引用零页路径同样一次刷新 |
| **AC-LS4-4 撤销/负例 fail-closed** | MET | 撤销（plan 后/apply 或 start 前）→ typed `SOURCE_GRANT_REVOKED`/`SOURCE_ACCESS_DENIED`，location/binding 逐字节不变、无 operation；import skip 撤销 → 行 `tuple()` 全等零写；identity 不符（同 digest 拷贝、错 digest/volume/file）→ 0 行；folder 错键 → 0 行 |
| **AC-LS4-5 幂等/单调/审计** | MET | 同值重复 → `rowcount 0` + 快照不变；同 registry 代次回退 → 0；跨 registry 代次 1 允许；`last_verified_at` ISO 可解析；只写三列 |
| **AC-LS4-6 枚举闭环** | MET | 生产单点刷新后 `source_list_scan_targets` 返回新 `registry_id/generation` 而 `identity_digest`/`project_ids` 不变；枚举仍零写（14 表快照）；代次回退被拒 → 枚举不倒退 |
| **AC-LS4-7 零漂移/门禁** | MET | pins **18/18**；check（默认 + `-TaskPath`）**PASS(3 warnings)×2**；API inventory **EXIT=0**；scope **PASS changed=7 全 ALLOWED + zero-drift 空 + `PROTOCOL_MINOR=3`**；全量 pytest **3317/10**（基线 3305/10）、全量 .NET **1570/0/92**（基线 1562/0/91，增量归因并发 L-S1）；跑后 `git checkout -- verification/FEA-09` |
| **AC-LS4-8 不夸大** | MET | EV/Handoff/卡面保留 L-S4-1/L-S4-2；不宣称「只读切片已可恢复」/零交互自愈/L-R1 全修/撤销后自动放行 |

## 2. 验证证据（实跑；`delivery_head=0ebb234bf`）

| 场景 | 命令 | 环境与被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| 定向（卡面命令） | `C:/Python314/python.exe -m pytest tests/core/test_core_scan_target_commands.py tests/fea11/test_source_relink.py tests/fea09/test_import_source.py tests/fea09/test_source_sync_operations.py -q` | delivery tree（=0ebb234bf） | **PASS 26 passed in 1.22s**（基线 14：relink 5 + core 9；本卡 +12） | `logs/feature.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | `repo_head=0ebb234bf` | **PASS 3317 passed / 10 skipped / 11 warnings in 245.79s**（基线 3305/10，不降） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | `repo_head=89757f193`（并发 L-S1 **docs-only** 提交；`git diff --stat 0ebb234bf..89757f193 -- apps/` **为空**） | **PASS 1570 / 0 / 92（8 程序集）**（基线 1562/0/91；+8/+1 归属并发 L-S1 Host 测试，**不归属本卡**） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | delivery tree | **PIN AUDIT PASS (all 18)** / **PASS(3 warnings) ×2** / **EXIT=0** | `logs/gates.log` |
| 范围 | `python verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/scope_validation.py --commits 6dd36aad7,0ebb234bf` | 自有 commit 链 | **PASS changed=7 全 ALLOWED；zero-drift=[]；out_of_scope=[]；PROTOCOL_MINOR=3；卡 status 未改** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/discrimination.py` | delivery tree | **PASS 7/7 RED_AS_EXPECTED + 7/7 字节级恢复（sha256 MATCH）+ 恢复后复绿 + tree CLEAN** | `logs/discrimination.log` |

- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`
  （`logs/gates.log` 末尾 `FEA09_STATUS=CLEAN`）。
- **并发披露**：`main` 共享工作树同期由 `l-s1-impl` 使用（`1ac8cc0b7`/`b56c5a0e6`/`89757f193`，`apps/**` 为 L-S1 变更）；
  本卡提交均显式 pathspec，未夹带他人字节。全量 .NET 的 `repo_head` 比 delivery head 多一个 docs-only 提交，`apps/**` 零 diff。

## 3. 已知 limitation（closeout 必须保留）

- **L-S4-1（本卡登记，未解决）**：A 修完仍缺「触发器」——撤销→重注册后若**无既有写路径**（重导入 / 同步 apply）介入，
  冷启动/周期只读枚举仍被 Host 旧 auth typed skip，**不会自动恢复**；零交互恢复需 B（C-16 v1.5 另卡，1/18 pins）。
  **不得**表述为「只读切片已可恢复」。
- **L-S4-2（未修，登记保留）**：folder 身份键口径（首成员 facts vs 目录 identity）不在本卡；本卡只保证刷新复用写入时同一算法，
  folder 在 apply 路径键不一致时 **0 行 fail-closed**（已有测试），不静默「假成功」。
- **撤销语义不变**：撤销后不刷新、不自动放行、不自动重授权。
- **D-2 行为变化（显式）**：import 整源 skip 不再绝对零写——「live grant + 同 identity」时一次单行条件刷新；其余 skip 语义/计数不变。
- **D-4 store 口径**：单点实现留在 `SqliteLibraryRepository`；sync 面经 `self._repository`（两 store 共用 `conn`）调用；
  `src/infrastructure/sqlite/source_sync.py` 在 allowed_paths 内但**未改动**（无第二份 SQL）。
- **测试文件命名事实**：卡面 allowed 的 `tests/fea09/test_import_source.py` / `test_source_sync_operations.py` 在起点**不存在**，
  本卡按卡面路径**新建**；未改卡外测试文件。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `db12dc5e5`；**delivery_head=`0ebb234bf`**（未 push、未建 worktree）。
- 复现（repo root）：
  1. `C:/Python314/python.exe -m pytest tests/core/test_core_scan_target_commands.py tests/fea11/test_source_relink.py tests/fea09/test_import_source.py tests/fea09/test_source_sync_operations.py -q` → **26 passed**
  2. `C:/Python314/python.exe -m pytest tests -q` → **3317 passed / 10 skipped**（跑后必要时 `git checkout -- verification/FEA-09`）
  3. `cd apps/desktop-avalonia; dotnet test NewManga.sln -c Release` → **1570 / 0 / 92**（跑后同样恢复 `verification/FEA-09`）
  4. 治理/范围/判别性见 `EV.md` §2/§3 与 `logs/gates.log`、`scope-validation.log`、`logs/discrimination.log`
- 接收者下一步：①Lead 指派**独立上下文** Review（只读 `0ebb234bf`；重点：AC-LS4-1 单点 grep 判别、AC-LS4-3 D-2「skip 一次条件写」的
  事务/范围、AC-LS4-4 撤销与 identity 零写、单调/幂等 SQL 语义、AC-LS4-6 枚举闭环、7/7 判别性与零漂移）；
  ②核对 `EV.md` 与 `RESOURCE-MANIFEST.json` 逐文件 sha256；③Lead 集成门禁重跑与 closeout（本 Handoff 不改卡 `status`；
  卡面 frontmatter `delivery_head` 已按 L-S1 先例回填为 `0ebb234bf`，若 Lead 口径不同可回退）。

## 5. 下一任务建议

- **本卡 Review/集成前不释放后续实现**。
- 建议 Lead 在 Review r1 通过后二选一（由 DSH 裁决）：
  1. **`FEA-11-L-S4-B`（零交互自动恢复/只读枚举切片）**：需 C-16 **v1.5 UNFREEZE（1/18 pins）** + 新 host-control 命令，
     与 L-S1-B（恢复/重授权入口）重叠，应先做设计/scope review 再冻结；前置=本卡 A 通过。
  2. **`FEA-11-RUN-GRANT-2C`（长 Run 授权续期 L-G1）**：需独立设计卡（300s TTL），与本卡无共享写域。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / base `0ebb234bf`（本卡 delivery_head；未创建 worktree，若需隔离 worktree 待 DSH 创建）。

## 6. 风险与遗留

- **R1 语义外溢风险（中）**：刷新使枚举由「被 skip」变「可通过」，读起来像「自动恢复」；本卡口径固定为「记录事实」——
  前提是用户已在 Host 显式重新授权（live grant），且需一次既有写路径。Review 时请按此口径检查措辞。
- **R2 folder 静默 0 行（高，已按 fail-closed 处理）**：本卡不重算 folder 身份键（L-S4-2）；apply 路径键不一致 → 0 行不刷新
  （测试覆盖），**不得**被读成「folder 源 refresh 成功」。
- **R3 事务边界**：页单元刷新在既有 page-unit 事务内（失败回滚）；apply 刷新在 `BEGIN IMMEDIATE` 内；D-2 skip 路径无页单元，
  为**单行独立写单元**（显式登记的行为变化）。
- **R4 并发共享工作树**：证据已按自有 commit 链与 `repo_head` 归因；Lead 集成时若 HEAD 已前进，需按其集成 head 重跑门禁。
- **回退**：`git revert 0ebb234bf 6dd36aad7`（两个提交，或按文件 checkout）；无 schema/数据迁移，回退无数据风险。
