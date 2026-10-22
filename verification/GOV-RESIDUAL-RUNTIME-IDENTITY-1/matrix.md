# 七项剩余历史运行身份 — 逐项取证矩阵

Task：GOV-RESIDUAL-RUNTIME-IDENTITY-1；Owner dsh（epoch 10 lease `37230d7822a141fcae8f46acd7841890`）；取证日 2026-10-22。
基线：`main` HEAD `43a7d73c850f669cc2595343a1747a661c277f2e`；common dir `G:/CODEX/New Manga/.git`。
复现命令：`python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/audit`
实测结果：`2627 declaration(s), 1926 protected root(s), 7 error(s), 276 warning(s)`，EXIT=2（见 `raw/audit-run.log`、`raw/declaration-audit.json`）。
保护命中评估：`probe-protected.py`（只读，未改解析器）→ `raw/protection-evaluation.json`。

分类口径：**FACT** = 由仓库内既有 tracked 证据或当前字节直接证明；**INFERENCE** = 由多条一致证据推出但无单一直接记录；**UNKNOWN** = 现有证据不足以判定。
本 Task 不使用「当前 `%TEMP%`/`%APPDATA%` 值」作为历史位置的证明；历史展开值单独取证，见 `historical-env-evidence.json`。

---

## 逐项结论

### E1 `DECL_RELATIVE_AMBIGUOUS` — `worktrees/P19-AC3-1`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_RELATIVE_AMBIGUOUS`；message=`declared path 'worktrees/P19-AC3-1' looks workspace-relative; it may mean the workspace root or the repository root and is refused`；file=`doc/tasks/P19.md`；audit locator=`line 5`（Resource Manifest 表格第 5 数据行，文件实际第 112 行） |
| 原文 | `\| P19 子 Task worktree（5 个）\| worktrees/P19-AC3-1 \| DELETE_SAFE \| - \| doc/WORKTREE_SAFETY_INVENTORY.md \| **已不存在**（closeout 前按清单核实后清理）；原记录的 PRESERVE_REFERENCED 与事实不符，已按事实更正 \|` |
| 归属 | `P19`（status `closed_with_limitations`，owner `dsh`，reviewer `Codex`，integration/delivery `4c860d882a44580a955b5d090d8bc5d23180ede5`） |
| 引用 | `doc/WORKTREE_SAFETY_INVENTORY.md:183` 记录 `workspace/worktrees` 实际移除 7 处含 `P19-AC3-1`，与「已不存在」一致 |
| 实际路径 | **FACT**：仓库根无 `worktrees/` 顶层目录（故只能是 workspace 相对）；`G:/CODEX/New Manga.workspace/worktrees/P19-AC3-1` 经 `Test-Path` 判定不存在；`git worktree list` 无该注册。 |
| disposition | `DELETE_SAFE`（非保护性） |
| 现存真实资源 | 无 |
| 保护缺口 | 无。该路径若重建，已被 `doc/tasks/WORKSPACE-CONSOLIDATION-1.md:11/12`、`doc/tasks/SEC-FIX-PATH-ECHO-1.md:5` 的广域根声明覆盖（probe hits=2）。 |
| 技术可解 | 是：显式绑定 workspace 相对根 + `ALREADY_ABSENT` 语义，不猜根 |
| 需用户裁决 | 否 |

### E2 `DECL_ENV` — `%TEMP%/p19-ac2-r1`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_ENV`；message=`declared path '%TEMP%/p19-ac2-r1' contains an environment variable or shell home token`；file=`doc/tasks/P19.md`；locator=`line 6`（实际第 113 行） |
| 原文 | `\| 测试隔离根 \| %TEMP%/p19-ac2-r1 \| DELETE_SAFE \| - \| verification/P19/r3-closure-checklist.md \| 22 个 p19* 临时隔离根，**已清理**（2026-10-18，Coordinator）；非用户数据 \|` |
| 归属 | `P19`（同上） |
| 引用 | `verification/P19/r3-closure-checklist.md`、`verification/P19/codex-review-r1.md` |
| 实际路径 | **FACT**：`%TEMP%` 历史展开值 = `C:/Users/49745/AppData/Local/Temp`（见 `historical-env-evidence.json` E-TEMP，三条独立 tracked 证据）；故目标 = `C:/Users/49745/AppData/Local/Temp/p19-ac2-r1`，当前不存在。**现状佐证**：当前该 Temp 下 11 个 `p19*` 目录中无 `p19-ac2-r1`（仅佐证，不作历史证明）。 |
| disposition | `DELETE_SAFE`，原文自称已清理、非用户数据 |
| 现存真实资源 | 无 |
| 保护缺口 | 无。`%TEMP%` 不在解析器四受管根（`review-scratch`/`builds`/`temp`/`tmp` 于 workspace 下），声明失败不产生删除候选。另：当前 Temp 残留 11 个其他 `p19*` 测试根（约 1.9 MiB），本 Task 不处置，交用户裁决是否需要专门清理授权。 |
| 技术可解 | 是：绑定历史展开值 + `ALREADY_ABSENT` 语义 |
| 需用户裁决 | 否（E2/E3 本身）；Temp 残留清理另属未授权事项 |

### E3 `DECL_ENV` — `%TEMP%/p19-ac2-main-1`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_ENV`；message=`declared path '%TEMP%/p19-ac2-main-1' contains an environment variable or shell home token`；file=`doc/tasks/P19.md`；locator=`line 7`（实际第 114 行） |
| 原文 | `\| 本轮新增隔离根 \| %TEMP%/p19-ac2-main-1 \| DELETE_SAFE \| - \| verification/P19/codex-review-r1.md \| 12 个（AC2x8 / AC4v3x3 / smokex1），**已清理**；非用户数据 \|` |
| 归属/引用 | 同 E2 |
| 实际路径 | **FACT**：同 E-TEMP 展开 → `C:/Users/49745/AppData/Local/Temp/p19-ac2-main-1`，当前不存在；当前 Temp 无该目录。 |
| 现存真实资源 | 无 |
| 保护缺口 | 无（同 E2） |
| 技术可解/需裁决 | 是 / 否 |

### E4 `DECL_UNKNOWN_DISPOSITION` — `%TEMP%/.tmp* created by Rust tempfile tests`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_UNKNOWN_DISPOSITION`；message=`resource '%TEMP%/.tmp* created by Rust tempfile tests' has unknown disposition 'CLEANED_BY_OWNER'`；file=`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`；locator=`$.resources[7].disposition` |
| 归属 | `ENV-BUNDLE-1-FU1`（资源清单 captured_at 2026-10-16；worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1` 仍注册保留） |
| 原文 | `resource_type=test_temp_data`；`source_path="%TEMP%/.tmp* created by Rust tempfile tests"`；`disposition="CLEANED_BY_OWNER"`；`destination_path=null`；`reference_check="Rust TempDir values dropped at test completion; ... cleaned up."` |
| 契约冲突 | **FACT**：`tools/governance/resource-manifest.schema.json` 的 disposition 枚举不含 `CLEANED_BY_OWNER`，且明文规定「`ALREADY_ABSENT` 是唯一允许用于列出但目标已不存在的资源的取值」→ 该值确为 schema 违规。 |
| 但单改值不足 | **FACT**：即使换为 `ALREADY_ABSENT`，`source_path` 同时含 `%TEMP%`（DECL_ENV）与 `*`（DECL_GLOB），仍会被拒绝；两条路径都要求改原件或引入解释层。 |
| 现存真实资源 | 无（Rust `TempDir` 在测试结束时 drop；声明即如此记录） |
| 保护缺口 | 无 |
| 技术可解 | 是：解释层登记「该行是已自动消失的测试临时数据、其 disposition 语义等价 `ALREADY_ABSENT`」，不改原件 |
| 需用户裁决 | 否 |

### E5 `DECL_DESTINATION_UNRESOLVED` — `Same ignored target/dist locations in this worktree`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_DESTINATION_UNRESOLVED`；message=`declared relative path 'Same ignored target/dist locations in this worktree' is not an existing repo top-level entry; identity is ambiguous`；file=`verification/P19-UI-FIX-1/resource-manifest.json`；locator=`$.resources[1].destination_path` |
| 归属 | `P19-UI-FIX-1`（status `done`，branch `codex/P19-UI-FIX-1`，delivery `f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0`） |
| 原文 | `resource_type=generated-build-artifacts`；`source_path="apps/desktop/src-tauri/target/{core-sidecar,debug/resources,debug/m2rc1-desktop.exe}; apps/desktop/frontend/dist"`；`destination_path="Same ignored target/dist locations in this worktree"` |
| 契约对照 | **FACT**：schema 规定 `destination_path` 可为 prose（示例 `Same source location`），「checker 仅当它本身是可解析路径时才解析」；但解析器 `is_path_like()` 把含 `/` 的值视为 path-like，进而 `DECL_DESTINATION_UNRESOLVED`（F-03 加固，刻意如此）。两者对「path-like prose」边界定义不同。 |
| 实际路径 | **FACT**：语义目标 = 该 worktree 内三个产物路径；`Test-Path` 确认 `apps/desktop/src-tauri/target/core-sidecar`、`apps/desktop/src-tauri/target/debug/resources`、`apps/desktop/frontend/dist` 均存在。 |
| 现存真实资源 | 是（ignored 构建产物），但已被 `$.resources[0]` 的 worktree 声明及广域根覆盖（probe hits=3） |
| 保护缺口 | 无 |
| 技术可解 | 是：解释层登记该值为「非身份 prose」，或显式绑定到三个已存在目标路径；不采用宽泛 path-like 启发式降级 |
| 需用户裁决 | 否 |

### E6 / E7 `DECL_ENV` ×2 — `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}`

| 项 | 内容 |
|---|---|
| 完整身份 | code=`DECL_ENV`；message=`declared path '%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}' contains an environment variable or shell home token`；file=`verification/P19-UI-FIX-1/resource-manifest.json`；locator=`$.resources[2].disposition`（E6）与 `$.resources[3].disposition`（E7） |
| 归属 | `P19-UI-FIX-1`（同上） |
| 原文 | E6：`resource_type=isolated-user-data-copy`，`disposition=PRESERVE_REFERENCED`，目标副本 `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017`，`process_check` 声明源四个文件 before/after SHA 相符。E7：`resource_type=user-data-source`，`disposition=PRESERVE_REFERENCED`，`destination_path="Same source location"`，`modified=false`。 |
| locator 精度 | **FACT（解析器缺陷，非安全问题）**：两条 JSON 声明错误的 locator 被记为 `$.resources[2].disposition` / `$.resources[3].disposition`，而实际拒绝原因来自 `source_path`。`add_declaration` 传入的 locator 固定为 disposition 字段路径，导致 JSON 声明的错误定位只对 disposition 类错误准确。本 Task 只记录，不改解析器。 |
| 实际路径 | **FACT**：`%APPDATA%` 历史展开值 = `C:/Users/49745/AppData/Roaming`（见 `historical-env-evidence.json` E-APPDATA；证据为其他 Task 的 tracked 日志/gate JSON 明文记录，非当前环境推断）。目标目录 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/{catalog,data,derived}` 全部存在。 |
| 字节交叉校验 | **FACT**：`data/library.db` 当前 SHA-256 `7809968c4ae9f12ca4e5936a875ce027a5c7fb8e6c19aa79e5a786a9692768e4` 与 P19-UI-FIX-1 `appdata-source-before.json`、`appdata-source-preservation-check.json` 记录的 before/after 完全相等；`data/library.db.run-owner.lock`、`derived/.preview-lifecycle.lock` 亦相等 → 同一文件谱系，历史展开值成立。`catalog/catalog.sqlite` 当前 `b16c8a30…` ≠ 记录 `0f094275…`（后续 Task 于 2026-10-18 修改），属已记录 delta，不削弱根路径结论。 |
| 现存真实资源 | **是，真实用户数据**：`catalog/`（catalog.sqlite 24,576 B）、`data/`（library.db 311,296 B + run-owner.lock）、`derived/`（pages/ + .preview-lifecycle.lock 325 B）、`managed/`；mtime 覆盖 2026-09-29…2026-10-20。 |
| 保护缺口 | **是，唯一真实缺口**：`probe-protected.py` 对该目录及 catalog/data/derived 三个子路径的 `evaluate` 全部 **hits=0** —— 该目录当前不受任何声明保护。原因即 E6/E7 声明因 `DECL_ENV` 被拒后没有注册为保护根。 |
| 技术可解 | 是：解释层把两条声明绑定到规范路径并**新增保护根**（只增不减）；不全局展开 `%APPDATA%`，只对这 2 条精确绑定 |
| 需用户裁决 | 否（属「增加保护」方向，与用户数据保护原则一致；实施 Task 须声明新增保护不等于任何清理授权） |

---

## 汇总判定

| # | 身份 | 现存真实资源 | 保护缺口 | 技术可解 | 需用户裁决 |
|---|---|---|---|---|---|
| E1 | `worktrees/P19-AC3-1` | 无 | 无 | 是 | 否 |
| E2 | `%TEMP%/p19-ac2-r1` | 无 | 无 | 是 | 否 |
| E3 | `%TEMP%/p19-ac2-main-1` | 无 | 无 | 是 | 否 |
| E4 | `%TEMP%/.tmp*` + `CLEANED_BY_OWNER` | 无 | 无 | 是 | 否 |
| E5 | destination prose | 有（产物，已覆盖） | 无 | 是 | 否 |
| E6 | `%APPDATA%/…/{catalog,data,derived}` #1 | **有（用户数据）** | **有** | 是 | 否 |
| E7 | 同上 #2 | **有（用户数据）** | **有** | 是 | 否 |

结论：
1. 七项中只有 E6/E7 存在真实安全影响 —— 真实用户数据目录未被任何声明保护；其余五项无现存资源、无保护缺口。
2. 七项均无须用户裁决的对象；差异全部可由技术方案（精确历史身份解释层）解决。
3. **唯一需要用户知悉但不阻塞**的事项：当前系统 Temp 下另有 11 个 `p19*` 测试隔离根（约 1.9 MiB，非用户数据）未被任何声明覆盖；因清理禁令与「非本 Task 范围」，本 Task 不处置、不删除，仅登记。
4. 不改任何历史原件（`doc/tasks/P19.md`、两份 `resource-manifest.json` 的字节保持），不改解析器语义；修复方向为新增精确绑定的解释层（既有 `tools/governance/historical-evidence-interpretation.json` 已有同类机制与先例）。

## 与既有 Review 的关系

`doc/reviews/WORKSPACE-DECLARATION-REMEDIATION-1-66e597282-codex-r1.md` 第 4 节已逐条裁定这七项「保留 fatal，另立 Task 裁定」，并要求「逐项确认目标、不按变量名整体豁免、解析到具体规范路径并记录依据」。本矩阵正是该裁决要求的逐项确认交付；本 Task 未解除任何 fatal，也未修改检查语义。
