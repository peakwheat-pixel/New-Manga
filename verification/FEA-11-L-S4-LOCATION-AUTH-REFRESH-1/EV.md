# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1（A）Canonical Evidence：location auth 原地刷新

> **结论先行。** 本卡按 DSH 裁决 **D-1…D-6** 只做 **A 面（零契约，0/18 pins）**：兑现 C-15 §2
> 「重授权/重新注册**原地更新**该行，不新建重复 location」与 §3.3「跨 Registry 命中同一物理身份时同样复用并原地更新注册信息」
> 两条**既有冻结条款**（conformance，不新增语义）。实现内容：
>
> 1. **单点实现**：`SqliteLibraryRepository.refresh_source_location_auth` 成为 Core **唯一**的原地刷新 SQL
>    （身份三键 `content_digest/volume_serial/file_id` + `is_current=1` + 同 registry generation 单调 + 幂等守卫；**事务中立**，
>    不自己开/提交事务）；`service.py` 的 relink 内联 `UPDATE source_locations` 被删除（relink 行为不变）。
> 2. **接线**：C-17 apply 写路径在「live grant 的 digest/volume/file == 当前 location 行」时刷新（relink 与同 identity 的
>    resync/repoint 均覆盖；changed container/copy 走既有 supersede+insert，不刷新）；import 复用路径在**第一页单元事务内**
>    刷新一次；整源 skip / 全页已引用的零页路径按 **D-2** 做**一次**条件写（独立单行写单元，无页单元可依附）。
> 3. **不刷新面**：撤销/过期 grant（resolve typed 失败）、identity 不符、scan（零写）、非 current 行、同 registry 代次回退。
>
> **判别性 7/7**：删 apply 调用、删页单元刷新、删 D-2 skip 刷新、恢复第二份内联 SQL、删单调守卫、删身份守卫、删 `is_current`
> 守卫 → 目标用例 **全部 RED**，随后**字节级恢复**（sha256 匹配 + `git status` CLEAN）。
> 全量 **pytest 3317 passed / 10 skipped**（基线 3305/10；+12 = 本卡新增测试）；全量 **.NET 1570 / 0 / 92**（基线 1562/0/91）。
> **不夸大**：本卡**不实现**「零交互自动恢复」——用户重新授权后仍需**一次既有写路径**（重导入 / 同步 apply）才刷新 location；
> 冷启动/周期只读枚举的自动恢复需要 B（C-16 v1.5 另卡，**limitation L-S4-1 保留**）；folder 身份键缺陷**L-S4-2 保留未修**；
> **撤销后不自动放行、不自动重新授权**；本卡不改契约/pins/apps/schema/依赖。

| 项 | 值 |
|---|---|
| task | `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`（冻结卡 `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`；`status` 未改，仍 `ready`） |
| Owner | `l-s4-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=55306cb84`；实现起点 `db12dc5e5`（`main`，工作树 clean，实测） |
| delivery_head | **`0ebb234bf`**（测试提交；实现提交 `6dd36aad7`） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK 10.0.401（测试目标 net9.0）/ Windows 11 |
| 契约字节 | **本卡零变更**：`doc/plan/**`、`doc/contracts/**` 本卡零 diff；`verify_pins` 18/18；`PROTOCOL_MINOR=3`；命令/能力/错误码闭集零新增 |
| 依赖 | **零新增**；`schema.py` / `migrator.py` 零 diff（`registry_id`/`authorization_generation`/`last_verified_at` 三列已存在） |
| 判别性 | `tools/discrimination.py`（7 破坏点，见 §3） |
| 资源清单 | `RESOURCE-MANIFEST.json`（本证据树 + 交付改动文件逐文件 sha256） |

## 1. 交付 commit 链（起点 `db12dc5e5` → delivery_head `0ebb234bf`）

```text
0ebb234bf test(fea-11-l-s4): refresh discriminators (single point, relink/apply, import skip, enumeration closure)
6dd36aad7 feat(fea-11-l-s4): single in-place location auth refresh wired into import reuse and sync apply
db12dc5e5 (起点 HEAD，工作树 clean)
```

> **共享工作树说明（必须）**：`main` 工作树同期由 `l-s1-impl` 并发使用，`b56c5a0e6`/`1ac8cc0b7`（L-S1 Host 实现，`apps/**`）
> 落在本卡起点与本卡提交之间；**本卡 commit 全部为显式 pathspec 提交，只含上表文件**。文档提交（本卡 / Handoff / 本证据树）为随后
> 同批提交，均在 `allowed_paths` 内。`delivery_head` 取**测试提交**（与 2B / L-S1 先例一致），文档提交不改实现字节。

本卡交付的仓库文件（7，见 `changed-files.txt`）：

```text
src/infrastructure/sqlite/library.py
src/application/sources/service.py
src/application/importing/referenced/runtime.py
tests/core/test_core_scan_target_commands.py
tests/fea11/test_source_relink.py
tests/fea09/test_import_source.py            (新文件；卡 allowed_paths 指定名)
tests/fea09/test_source_sync_operations.py   (新文件；卡 allowed_paths 指定名)
```

> 说明：卡面 `allowed_paths` 指定的 `tests/fea09/test_import_source.py` / `test_source_sync_operations.py` 在实施起点**并不存在**
> （`git ls-files` 实测）；按卡面路径**新建**这两个测试文件承载 import 复用 / sync apply 的刷新判别，未触碰卡外测试文件。

## 2. 门禁实测

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向（卡面命令） | `C:/Python314/python.exe -m pytest tests/core/test_core_scan_target_commands.py tests/fea11/test_source_relink.py tests/fea09/test_import_source.py tests/fea09/test_source_sync_operations.py -q` | **26 passed in 1.22s, EXIT 0**（relink 5→9，新增 import 4 / sync 3 / core 1） | `logs/feature.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **3317 passed, 10 skipped, 11 warnings in 245.79s, EXIT 0**（基线 3305/10，+12 全为本卡测试；无回归） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **1570 passed / 0 failed / 92 skipped（8 个测试程序集）, EXIT 0**（基线 1562/0/91） | `logs/full-dotnet.log` |
| 治理 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | `logs/gates.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`） | **PASS (3 warnings) ×2** | `logs/gates.log` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **OK: rendered counts match FEA-C07 doc, EXIT 0** | `logs/gates.log` |
| 范围 | `C:/Python314/python.exe verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/scope_validation.py --commits <delivery commits>` | **PASS：changed=7 全 ALLOWED；`out_of_scope=[]`；`zero_drift_violations=[]`；`PROTOCOL_MINOR=3`；卡 `status` 未改** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `C:/Python314/python.exe verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/discrimination.py` | **result=PASS breaks=7 全部 RED_AS_EXPECTED + 字节级恢复 + 恢复后目标用例绿 + `restored_tree_git_status=CLEAN`** | `logs/discrimination.log` |

**归因与并发披露（如实）：**

- 全量 pytest 的 `repo_head` 为 **`0ebb234bf`（本卡 delivery_head）**；全量 .NET 的 `repo_head` 为 **`89757f193`**（并发 L-S1 的
  **docs-only** 提交）。实测 `git diff --stat 0ebb234bf..89757f193 -- apps/` **为空** → .NET 测得的 `apps/**` 字节与 delivery_head 相同，
  但 .NET 的 **+8 passed / +1 skipped** 来自并发 L-S1 已提交的 Host 测试（`b56c5a0e6`），**不归属本卡**；本卡 Host 零改动。
- 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；跑后已执行 `git checkout -- verification/FEA-09`
  （`FEA09_STATUS=CLEAN`，见 `logs/gates.log` 末尾）。
- 已知环境噪声：pytest 会打印 PySide6/QML `TypeError: ... of null` 警告（不影响 PASS）；本轮**未命中** `library.db-shm`
  锁 flaky（定向与全量均一次通过；若命中会按卡要求隔离复跑并如实记录，不静默重试）。

## 3. 判别性验证（7 破坏点；删掉实现必须变红）

`logs/discrimination.log`：逐个破坏**一个已提交的实现点** → 运行**一个**目标用例 → 要求 RED（exit≠0）→ 按**原字节**恢复并
复核 sha256 → 恢复后再跑该用例要求绿；最后 `git status`（3 个被破坏源文件）必须 CLEAN。

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| B1 | apply 面刷新调用被禁用（relink/resync 同身份不再刷新） | `tests/fea09/test_source_sync_operations.py::test_resync_same_identity_refreshes_the_location_auth` | RED_AS_EXPECTED / RESTORED |
| B2 | import 页单元不再携带刷新（重导入新项目不刷新） | `tests/fea09/test_import_source.py::test_reimport_into_another_project_refreshes_location_auth_in_place` | RED_AS_EXPECTED / RESTORED |
| B3 | 整源 skip 的 D-2 条件刷新被删除 | `tests/fea09/test_import_source.py::test_whole_source_skip_refreshes_location_auth_once` | RED_AS_EXPECTED / RESTORED |
| B4 | 恢复第二份内联 `UPDATE source_locations`（单点实现被破坏） | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_is_the_single_implementation` | RED_AS_EXPECTED / RESTORED |
| B5 | 同 registry generation 单调守卫被移除 | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_fail_closed_guards` | RED_AS_EXPECTED / RESTORED |
| B6 | 物理身份三键守卫被移除（identity 不符也刷新） | 同上 | RED_AS_EXPECTED / RESTORED |
| B7 | `is_current = 1` 守卫被移除（已 supersede 旧行也被刷新） | 同上 | RED_AS_EXPECTED / RESTORED |

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性/真实证据 | 证据 |
|---|---|---|---|
| **AC-LS4-1 单点实现** | MET | `refresh_source_location_auth` 是唯一含 `UPDATE source_locations SET registry_id` 的字节（grep 实测全 `src/**` 1 处）；`service.py` 内联 UPDATE 已删除；生产调用者 ≥3（repository 页单元 + D-2 写单元 + apply face）。判别 B4（恢复第二份内联 SQL → RED） | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_is_the_single_implementation`、`logs/discrimination.log` |
| **AC-LS4-2 重导入/relink 刷新** | MET | relink 跨 registry：同物理文件（rename，同 inode）重授权 `reg-2` → `registry_id=reg-2`、`last_verified_at` 非空 ISO、`location_id/source_id/digest/volume/file/size/observed_at/is_current/created_at` 与 binding 逐列不变、location 行数仍 1；同 registry 代次 `1→2` 跟随且 binding 代次仍 1（不越权抬代次）。import 复用：同源导入第二个 project（新 `reg-2`）→ 页单元内刷新、无新 location 行、无重复 source。判别 B1/B2 | `tests/fea11/test_source_relink.py::test_relink_refreshes_location_auth_in_place_cross_registry`、`::test_relink_refresh_follows_same_registry_generation_bump`、`tests/fea09/test_import_source.py::test_reimport_into_another_project_refreshes_location_auth_in_place` |
| **AC-LS4-3 sync apply 刷新（含 D-2 skip 一次条件刷新）** | MET | 同容器 resync 跨 registry 刷新（apply 事务内，页/binding 代次不变）；整源 skip（D-2）**只写一次**条件刷新、`imported_pages=0/skipped_sources=1`、页/版本/位置计数不变；`import_as_new` 全已引用零页路径同样一次刷新。判别 B1/B3 | `tests/fea09/test_source_sync_operations.py::test_resync_same_identity_refreshes_the_location_auth`、`tests/fea09/test_import_source.py::test_whole_source_skip_refreshes_location_auth_once`、`::test_all_pages_already_referenced_import_as_new_still_refreshes` |
| **AC-LS4-4 撤销/负例 fail-closed** | MET | 撤销 grant（plan 后、apply/start 前）：typed `SOURCE_GRANT_REVOKED`/`SOURCE_ACCESS_DENIED`、`source_locations`/`page_bindings` 逐字节不变、无 operation 行；import skip 路径撤销 → 保持 skipped、location 行 `tuple()` 全等（零写、不放行）；identity 不符（同 digest 的**拷贝**新 inode；错误 digest/volume/file）→ 0 行更新；folder 错误身份键 → 0 行（不静默成功）。判别 B6/B7 + 撤销用例 | `tests/fea09/test_source_sync_operations.py::test_identical_copy_never_refreshes_the_recorded_location`、`::test_revoked_grant_never_refreshes_and_never_publishes`、`tests/fea09/test_import_source.py::test_revoked_grant_never_refreshes_on_a_skip_path`、`tests/fea11/test_source_relink.py::test_refresh_source_location_auth_fail_closed_guards` |
| **AC-LS4-5 幂等/单调/审计** | MET | 同值重复刷新 → `rowcount 0` 且逐行快照不变；同 registry 代次 15→14 → `rowcount 0`（不倒退）；跨 registry 代次 1 允许（新注册）；`last_verified_at` 非空且可被 `datetime.fromisoformat` 解析；刷新只写三列（其余列逐列断言不变）。判别 B5 | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_fail_closed_guards` |
| **AC-LS4-6 枚举闭环** | MET | 生产单点刷新后 `source_list_scan_targets` 返回**新** `registry_id/generation`，`identity_digest`/`project_ids` 不变；枚举本身仍零写（14 表快照不变）；同 registry 代次回退被拒 → 枚举不倒退 | `tests/core/test_core_scan_target_commands.py::test_location_auth_refresh_is_followed_by_cold_start_enumeration` |
| **AC-LS4-7 零漂移/门禁** | MET | pins 18/18；check（默认 + `-TaskPath`）PASS、API inventory EXIT=0；scope `changed=7` 全 ALLOWED、`doc/plan`/`doc/contracts`/schema/migrator/依赖/apps/STATUS/PLAN/LEDGER 零 diff、`PROTOCOL_MINOR=3`；全量 pytest 3317/10（基线 3305/10）、全量 .NET 1570/0/92（基线 1562/0/91，增量归因并发 L-S1）；跑后 `git checkout -- verification/FEA-09` | `scope-validation.log`、`changed-files.txt`、`logs/gates.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |
| **AC-LS4-8 不夸大** | MET | 本 EV/Handoff/卡面明写：**不得**宣称「只读切片已可恢复」（需 B / C-16 v1.5 另卡）；L-S4-1（缺触发器，冷启动自动恢复需 B）与 L-S4-2（folder 身份键）保留；撤销后不自动放行；不宣称 L-R1 全修、不宣称零交互自愈 | 本文件 §5、Handoff §3、卡「已知 limitation」 |

## 5. 已知 limitation（closeout 必须保留）

- **L-S4-1（本卡登记，未解决）**：A 面修完仍**缺触发器**——用户「撤销→重注册」后若**没有任何既有写路径**（重导入 / 同步
  apply）介入，冷启动/周期只读枚举仍会因旧 `registry_id/generation` 被 Host typed skip，**不会自动恢复**。零交互自动恢复需要
  B 面：C-16 v1.5（1/18 pins）新 host-control 命令，**另卡**。**不得**把本卡表述为「只读切片已可恢复」。
- **L-S4-2（未修，登记保留）**：folder 身份键（import 写路径用首成员 `volume_serial/file_id` 与 folder manifest digest 组合；
  C-15 §2.3 的「目录 identity」口径疑似不一致，是否真缺陷需另卡确认）。本卡只保证刷新**复用写入时同一算法/同一来源**
  （import：`scanned.container_digest` + `_volume_serial/_file_id(resolved)`；apply：当前 location 行自身键 + grant facts 比对），
  **不改身份模型**；folder 源在 apply 路径用不一致键 → **0 行静默不刷新是预期的 fail-closed**（测试覆盖）。
- **撤销语义不变**：撤销后不刷新、不自动放行、不自动重新授权；恢复仍走既有显式流程。
- **D-2 行为变化（显式登记）**：import「整源 skip」不再是绝对零写——满足「live grant + 同 identity」时写**一次**单行条件刷新
  （D-2 裁决）。其余 skip 语义/计数不变；无 page/version/entry/binding/operation 写入。
- **并发共享工作树**：`main` 同期被 L-S1 使用；本卡证据按**自有 commit 链**计算 scope，不依赖 `base..HEAD` 区间。
- **Store 归属（D-4 口径）**：单点实现留在 `SqliteLibraryRepository`；sync 面经 `self._repository` 调用（两 store 共用同一
  `conn`），未在 `SourceSyncStore` 复制第二份 SQL；`source_sync.py` 因此无需改动（allowed 但未改）。

## 6. 证据清单（逐文件 sha256 见 `RESOURCE-MANIFEST.json`）

```text
EV.md                      本文件
RESOURCE-MANIFEST.json     交付改动文件 + 本证据树逐文件 sha256（生成时快照）
changed-files.txt          交付 commit 改动文件（7）
scope-validation.log       scope 校验实测（含 allowed_paths 解析与 zero-drift 判定）
logs/feature.log           定向 26 passed
logs/full-pytest.log       全量 3317 passed / 10 skipped
logs/full-dotnet.log       全量 .NET 1570 / 0 / 92
logs/gates.log             pins / check ×2 / API inventory / FEA-09 恢复
logs/discrimination.log    7/7 破坏点 RED + 字节级恢复 + 恢复后复绿
tools/discrimination.py    判别性驱动（可复跑）
tools/scope_validation.py  scope 驱动（`--commits` 显式交付链）
tools/gen_manifest.py      资源清单生成器（可复跑）
```

## 7. 真实性声明

1. **实跑 vs NOT_RUN**：上表所有 PASS 均为本轮实跑并落盘日志；**没有**把未跑项写成 PASS。本轮无 NOT_RUN 门禁项
   （pytest / .NET / pins / check / API / scope / 判别性全部真跑）。
2. **唯一写入**：本卡只改 `allowed_paths` 内 7 个代码/测试文件 + 卡/Handoff/本证据树；**未**改 `apps/**`、契约
   （`doc/plan/**`/`doc/contracts/**`）、schema/migrator/依赖、STATUS/REBASELINE_PLAN/TASK_LEDGER、卡 `status`；未 push、
   未建 worktree、未动真实用户数据。
3. **判别力**：7 破坏点逐一让目标用例 RED，恢复后复绿；不是「写了测试但无判别力」的自证。
4. **不夸大**：只声明 A 面（C-15 §2/§3.3 conformance + 两条既有写路径接线 + 判别测试）；**不**声明零交互自动恢复、
   **不**声明「只读切片已可恢复」、**不**声明 L-R1 全修、**不**声明撤销后自动放行；L-S4-1/L-S4-2 原文保留。
5. **并发披露**：`main` 共享工作树同期存在 L-S1 实现与文档提交（`1ac8cc0b7`、`b56c5a0e6`、`89757f193`）；本卡提交均为
   显式 pathspec、未包含他人字节；全量 .NET 的 `repo_head=89757f193` 与 delivery head 的差集经 `git diff --stat -- apps/`
   实测为空，但 +8/+1 的 .NET 增量归属并发 L-S1，**不据他人证据判本卡通过**（本卡 Python 改动对 .NET 无影响，全量 .NET 已实跑 EXIT=0）。
6. **数据优先级**：所有断言来自被审代码字节与本地实跑；未采信卡面/旧 Handoff 自述。
