# M2-REGION-RETYPE-CORE 独立 Review（DSH 非作者 / 静态只读）

**审查方法说明**：本沙箱无法执行命令（`pwsh` 一律返回 `SetNamedSecurityInfoW failed (Win32 5)`），因此**无 git diff / 无 pytest/cargo/vitest / 无 GATE 复跑**。代码与文件全部用 read/grep 静态核对；diff 判定采用「主 checkout（`G:\CODEX\New Manga`）同名文件对比 + 全文件行数与关键锚点行号偏移算术」推定（方法见 Q1）。所有运行级数字（43/46/650/cargo 47/vitest 49/GATE 25/25）**均标未验证**，仅核其内部自洽性。

---

## Verdict

**approved_with_conditions**

理由：核心契约面（wire 逐字段、错误码字面量零新增、单笔新 revision/origin=user/UNREVIEWED、EV-8 重快照、乐观守卫 seam 内复检、读取面五字段升序、三视图+capabilities 同 commit、minor 2→3 与 RC2/CS-L1 旁路同步）静态核对**逐条成立，未发现 P0/P1**。但有两项须在集成前闭合：①**真正越权且违反既有证据惯例**——`verification/M2-AC5/raw/**` 6 个历史证据文件被本轮 GATE 覆盖后随本 Task 入库（且有可复现主 checkout 反证，说明「旧值=SETTINGS-IPC 时代 minor=2」表述可疑）；②**契约 §5.4 错误码表第 4 行未落地**——持久化失败（`DB_FAILED`）被 `_guard_status_of` 折叠成 `INPUT_REVISION_CHANGED/conflict`，而非 `UNKNOWN/internal`。另有若干 P3 登记项（gen/schemas 范围追认、被改模块自身既有 suite 未复跑、前端 commandSurface pin 未同步、契约「runtime 未实现」措辞待 Codex 修订）。

---

## 重点问题 Q1 裁定

**结论：`packaging/m2ac5/run_clean_start_e2e.py` 与 `verification/M2-RC2/run_e2e.py` 的 minor/EXPECTED 同步 → 追认（同批旁路同步合规，不返修）；但 `verification/M2-AC5/raw/**` 6 文件覆盖 → 判越权，须返修剥离。**

**diff 范围核查（两文件均为最小字面量改动）**

- `packaging/m2ac5/run_clean_start_e2e.py`：主 checkout 841 行 → 本 worktree 843 行（**+2**）。全文件 `minor|EXPECTED|version` 命中集在两边只差两处字面量（`:445` 请求 envelope `minor 2→3`、`:497` ping 严格相等断言 `minor 3`）+ 两条注释（`:440-441`）。行号锚点 `CS-BLOCKED`（主 722 → 本 724，偏移 +2）与文件尾 +2 完全一致 ⇒ **无其他净插入/删除**；本文件 `CS-R3` 只判公告前缀（`:692-696`），不 pin 命令条数，故无需其他同步。
- `verification/M2-RC2/run_e2e.py`：主 623 → 本 629（**+6** = 4 行注释 `:298-301` + 2 条命令 `:310-311`）；行号锚点 `ALLOWLIST_RE` 289→289、`:391→385`、`:450→444`、`def main 480→474`（**恒 +6**）⇒ 改动全部集中在 `PRODUCTION_EXPECTED 7→9` 一处，无第三处。
- 残余不确定性（如实声明）：无法 `git diff`，理论上「行数不变的行内改写」不可由行数算术排除；但版本/命令面相关字面量已**全量 grep 枚举**，仅上述两处，且严格相等断言未放宽。

**裁定理由**

1. 本 Task **AC5 原文即要求**「frozen-probe/EXPECTED 计数/**CS-L1 envelope minor** 沿 SETTINGS-IPC 登记口径同步」——CS-L1 envelope 正位于 `run_clean_start_e2e.py`；不修则 GATE 恒 24/25，回退技术上不可行（等价放弃 minor bump 与本 Task 目标）。与 M2-PROD-DETECT-3 r1 的「接受追认（accept & ratify）」裁定同构（其 Task 亦同时把 `packaging/m2ac5/**` 列允许、把 runner 列禁止，属**任务书内部自相矛盾**而非 Owner 越权）。
2. 判定标准零放宽：25 场景集合、判定条件、严格相等断言均未变；CS-L1 实测 minor=3 与 `raw/cleanstart-gate.json:70-73` 自洽。
3. **附条件（沿 DETECT-3 三条先例）**：(a) 集成记录/commit message 显式追认这两处旁路同步；(b) 修订 Task `:39` 禁止范围与 AC5 的措辞矛盾（如「`packaging/**` 除经追认的 CS-L1 协议字面量与 RC2 EXPECTED 计数同步外不改；spec 冻结」）；(c) GATE 已用改后 runner 复跑（bundle HEAD=cfbf3859，已满足）。另注：`run_e2e.py:294-297` 原注释称 RC2 EXPECTED「由 integrating slice 维护，不由 Owner 分支维护」，本次由 Owner 分支落并在 `:298-301` 自证——可接受且更自洽，但需集成方在记录中确认。
4. **越权部分**：`verification/M2-AC5/raw/**` 6 文件不在 AC5 明示同步对象内，且违反本仓已多次书面化的证据卫生惯例：M2-PROD-DETECT-1 Task:90、M2-PROD-DETECT-2 Task:57/59、M2-SFX-PROD-1 Handoff:44、M2-RG1 Task:105+Handoff:48（「runner 写死 M2-AC5 raw → 运行→搬运改名→restore，AC5 raw 不提交」，STATUS P3-9(b) 口径），且既有各 Task 均以 `verification/<TASK>/…cleanstart-*` 副本留证（如 `verification/M2-RG1/raw/rg1-m2ac5-cleanstart-gate.json`）。→ 见 P2-1。

---

## 发现清单

### P2-1｜`verification/M2-AC5/raw/**` 历史证据被本轮覆盖并入库（越权 + 证据溯源污染 + 披露存疑）
- **位置**：`verification/M2-AC5/raw/cleanstart-gate.json`、`r1-library-probe.log`、`cleanstart-probe-stdout.log`、`cleanstart-ac1-run1-stdout.log`、`cleanstart-ac1-run2-stdout.log`、`cleanstart-production-stdout.log`（正是 runner 5 处写盘点：`run_clean_start_e2e.py:473/529/577/687/837`）。现 `cleanstart-gate.json:3` 的 installer 指向 `…worktrees\M2-REGION-RETYPE-CORE-zcode\…`、sha `d6003ae7…`。
- **问题**：(1) 不在本 Task 允许路径（允许面枚举到 `verification/M2-REGION-RETYPE-CORE/**`），也不在 AC5 明示同步对象内，与既有「搬运+`git checkout --` 还原」惯例直接冲突；(2) M2-AC5 证据包的 installer 现绑定到另一个 Task 的 worktree，后续读者会把本 Task 的产物误读为 M2-AC5 自有证据；(3) Handoff §风险 4 称被覆盖旧值为「SETTINGS-IPC 时代 minor=2 的证据」——**该表述与仓库现状不符**：主 checkout 的 `cleanstart-gate.json` 是**原始 M2-AC5** 证据（installer `5410e29e…`、`M2-AC5-zcode` worktree、**minor 0**、25 场景含 CS-Z4），且未见任何 SETTINGS-IPC 时代 AC5 raw 副本。请 Owner/集成方以 `git show 1b765007:verification/M2-AC5/raw/cleanstart-gate.json` 核对后更正披露。
- **建议**：把本轮产物（gate json + 5 份 stdout 日志）落 `verification/M2-REGION-RETYPE-CORE/raw/`（可沿用 `rg1-m2ac5-*` 命名先例），对 `verification/M2-AC5/raw/**` 执行 `git checkout --` 还原；vetification.md/Handoff 的引用路径与「旧值」描述同步更正。**注意**：这会同时把 AC5 证据从本 Task 交付中剥离，AC5 的验收凭据变为本 Task 自己的 raw 副本 + bundle sha。

### P2-2｜持久化失败被映射为 `INPUT_REVISION_CHANGED`（冲突），违反 §5.4 错误码表第 4 行
- **位置**：`src/application/editing/service.py:78-81`（`_guard_status_of` 只把 `LOCK_CHANGED` 单列，其余一律 `INPUT_REVISION_CHANGED`，含 `DB_FAILED`）+ `:351-354`；`src/bootstrap/core_service.py:679-691`。
- **问题**：SQLite seam 的**任何异常路径**（busy_timeout/磁盘/序列化）都返回 `RegionCommitStatus.DB_FAILED`（`src/infrastructure/sqlite/regions.py:276-282`）。`set_region_type` 把它折叠成 `GuardStatus.INPUT_REVISION_CHANGED`，`core_service` 随即 `raise RegionConflictError` → wire 得 `INPUT_REVISION_CHANGED / conflict / false` + 固定语「region revision changed since it was read」。而契约 §5.4 表第 4 行明定「Core 侧未分类失败（持久化失败等）→ `UNKNOWN` / `internal`」。`core_service.py:685-691` 的注释表明作者**本意**是非 APPLIED 落 UNKNOWN，但该意图因 service 上游折叠而未生效。附带：`tests/core/test_core_service_retype.py:261-286` 的 UNKNOWN 断言用「假 editing 抛 RuntimeError」绕过了真实 `DB_FAILED` 路径，故该码位对真实持久化失败**零判别力**。
- **建议**：在 `set_region_type` 内显式处理非 APPLIED 分支（`DB_FAILED`→抛 `RuntimeError`（→UNKNOWN/internal），`LOCK_CHANGED`→同，`INPUT_REVISION_CHANGED`→返回冲突态），**不要改全局 `_guard_status_of`**（会波及机器写候选语义）；补一条以 fake committer 返回 `DB_FAILED` 的单测。

### P3-1｜`core_service.py` 模块 docstring 的 envelope 示例仍写 minor=2
- **位置**：`src/bootstrap/core_service.py:10`、`:13`、`:17`（`{"major": 1, "minor": 2}` / ping 结果 minor 2）；`:16` 的「Allowed production commands (M2-IPC1 + M2-PROD-DETECT-3 + M2-SETTINGS-IPC-CHANNEL)」未加 M2-REGION-RETYPE-CORE。
- **问题**：同一 commit 修改了本 docstring（`:58-80` 新增两命令条目）却漏改 envelope 见证行；本仓对「minor 后果同步」一贯从严（§5 旁路清单/测试 pin 全部同步）。无运行时影响。
- **建议**：三处改 3、`:16` 补家族名。

### P3-2｜`gen/schemas/**` 4 文件 + 2 个新 toml 的落库需集成方显式追认；且 Owner 给出的理由对本命令不成立
- **位置**：`apps/desktop/src-tauri/gen/schemas/{acl-manifests,capabilities,desktop-schema,windows-schema}.json`、`permissions/autogenerated/{set_region_type,list_regions}.toml`。
- **核对**：4 个 gen 文件确为实质内容变化（主 checkout 的 `acl-manifests.json` **不含** `set_region_type`；本 worktree 含 `allow-list-regions`/`allow-set-region-type`），且 `gen/`、`permissions/` 为 **tracked**（无 ignore 规则）——沿 M2-AC1（4 gen + 3 toml）与 M2-RC2「regenerated 快照入库」先例，**入库合理**；但它们不在本 Task 允许范围字面清单内。
- **问题**：(a) 范围需 Codex 在集成记录追认（先例：M2-AC1 F-008「Codex 显式追认 build.rs/capabilities/gen schemas/permissions 为机制必然产物」）；(b) 追认理由中的「被 Rust 单测 `include_str!` 断言引用」**对本两命令不成立**——`main.rs:774-806` 的 ACL 断言只链 `command_allowlist(true,false)`（probe 7）∪ `command_allowlist(false,true)`（ac1 6），**production-only 的 retype/settings 两对永不进入该循环**，写错亦全绿（与 M2-AC1 r1 F-003 同型缺口，当时只补了 ac1）。真正的强制力来自 tauri-build 对 capability 引用权限的解析（缺失即构建失败）。
- **建议**：断言循环改为同时遍历 `command_allowlist(false,false)`（覆盖 16 条），并补 production 表面拒绝性的负例；集成记录中追认 6 个 ACL 联动文件。

### P3-3｜回归证据未覆盖「被改模块自身的既有 suite」，且无原始日志入库
- **位置**：改动模块 `src/application/editing/service.py`；三套件口径=`tests/providers tests/core tests/m2_acceptance`（verification §6）。未复跑 `tests/editing/{test_region_geometry,test_sqlite_regions,test_text_protection}.py`、`tests/pipeline/*.py`（后者仅新文件被跑）。
- **问题**：改的是 `RegionEditingService`，其主管 suite 不在 650 口径内；证据表对基线/红态/绿态/回归只给「会话执行记录（/tmp/baseline_pytest.log）」——**未入库任何原始日志**（本仓大量 verification/*/raw/* 证明惯例是入库）。我在无命令沙箱下无法独立验证任何计数与红态 commit 内容（红态 43 failed 只能靠测试文件是否引用新 API 间接自洽：46=43+3 与 4 个文件逐函数计数吻合，这层算术成立）。
- **建议**：Owner 或集成方跑一次 `pytest tests/editing tests/pipeline -q`（或全量 `pytest tests`）并落 `verification/M2-REGION-RETYPE-CORE/raw/`；同时把基线/红/绿/三套件/cargo/vitest 的原始输出入库。

### P3-4｜新命令对没有 Rust→Core 真实 sidecar 覆盖（先例有）
- **位置**：`apps/desktop/src-tauri/src/library_bridge.rs:600-639`（仅 Mock 通道）与 `main.rs`（无 `real_core_sidecar_*retype*`）。
- **问题**：settings 先例含 `real_core_sidecar_settings_round_trip_and_typed_rejection`（`main.rs:1401+`），本 Task 只有 Mock pin，因此 Rust 桥的 payload 组装（`expected_revision` 仅在提供时入 payload）与 Core 侧错误码穿透**从未端到端跑过**。
- **建议**：低成本方案——加一条真实 sidecar 测试：`list_regions("no-such-page")` 得 `{"regions": []}`、`set_region_type("no-such-region", …)` 得 `TARGET_NOT_FOUND`（无需 seed region，覆盖链全断 + typed 映射）；若不做，请在 §9 登记为已知缺口。

### P3-5｜前端 commandSurface pin 未同步（§5.4 末条把其列入同 commit 纪律）
- **位置**：`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts:31-45`（production arms 只有 3 + settings 2，无 retype 对；注释自称 mirror `main.rs command_allowlist`）。
- **问题**：该 mock 现在**低报**真实 production 面；`apps/** 前端`在本 Task 禁改面内，故这是「契约纪律 vs 任务范围」冲突，须**登记为延迟同步**（归 Workbench UI 接通 Task），而不是无声跳过。零前端改动也解释了 vitest 49 持平。
- **建议**：在 Handoff/verification 增一条「§5.4 宿主同步纪律中之前端 pin 顺延至 UI Task」的显式登记。

### P3-6｜冻结契约的实现态措辞待 Codex 修订（非 Owner 面）
- **位置**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:3,7,165,221`（「runtime 未实现」「目标 minor=3 由实现 Task 落地」）、`:119-120`（§5 表两行「runtime 未实现」）、`:381`（Tauri command name 未裁决）。
- **建议**：集成后由 Codex 按契约修订流程登记实现态（本 Task 不得改 `doc/contracts/**`，Owner 未触碰 ✓）。

### P4（nit / 登记，不阻断）
1. **EV-8 非 sfx 分支为新写**：`service.py:339-343` 直接 `SfxPolicy.SKIP`，与 `core_assembly.py:1041-1045` 的创建期内联规则**各写一份**（无共享 helper 可复用）。建议抽 `effective_sfx_policy(region_type, global)` 供两条写路径共用，消除漂移风险。
2. **命令名口径**：Core stdio 字面量为 `set_region_type`/`list_regions`，§5 表 transport-neutral 名为 `SetRegionType`/`ListRegions`（既有 `ListBooks` 为 PascalCase 先例）。契约已明示 Tauri command name 未裁决（`:381`），属 runtime 决策；建议在 verification 记一句命名决策，避免后续 UI Task 猜名。
3. **seam 复检失败分支无测试**：`test_c4_optimistic_expectation_matching_passes_through_the_seam` 只覆盖通过分支；「预检通过、seam 内检出变更」这一 TOCTOU 分支无单测（可注入 fake committer 返回 `INPUT_REVISION_CHANGED`）。**原子性本身成立**：SQLite `BEGIN IMMEDIATE` + 事务内重读 `current_revision_id`（`regions.py:214-240`），无窗口。
4. **测试卫生**：`tests/core/test_core_service_retype.py:170-175` 算了 `revisions_before` 又 `del`（断言缺失，未验证「一笔」）；`tests/editing/test_region_retype.py:349` 的 `or key == "sfx_policy"` 使该子句恒真；`:74` 用例名 `…while_machine_write_is_stalled` 实际只模拟 lock。
5. **frozen 探针注记**：`verification/M2-PROD-DETECT-3/frozen-detect-probe.py:226-229` 的 FROZEN 注记只记到「minor bumped to 2 by rev 1.3」，未补 2→3；`verification/M2-SFX-PROD-1/frozen-sfx-probe.py:53` 仍 minor=1 且**无 FROZEN 标注**。两者均不被任何 GATE 重跑（RG1/AC5 25 场景只跑 CS-*），无判定影响；AC5「沿 SETTINGS-IPC 登记口径」若要严格对齐，应补注记。
6. **证据措辞精度**：verification §7「CS-R3…runner 断言 9 命令 PRODUCTION_EXPECTED」不准确——AC5 runner 的 CS-R3 只判公告**前缀存在**（`run_clean_start_e2e.py:692-696`）；9 命令 pin 在 `verification/M2-RC2/run_e2e.py:302-312`。9 命令确实出现在 `raw/cleanstart-production-stdout.log:3`，但那是原始日志不是门断言。
7. **同文件陈旧注释（先例遗留，非本 Task 引入）**：`main.rs:770-771`「exactly the ten live commands (seven resource-channel + three M2-AC1 acceptance)」与实际 16 不符；`main.rs:19-20` 仍称 inlined `m2rc1-commands` plugin（RC2-FIX 已改为 `__app-acl__`）。建议下一 slice 或集成轮顺手修（本仓对此类计数陈旧历史上有 P3 级先例）。

---

## 逐 AC 结论

- **AC1 PASS** — `service.set_region_type` 单笔新 revision 经既有 `_commit` seam（`apply_type`/`apply_sfx_policy` 只改两字段，`snapshot_state()` 证实 delta=region_type+sfx_policy）、`origin=USER`、`review_state=UNREVIEWED`、EV-8（sfx←调用时全局配置；非 sfx 强制 SKIP）、C4 预检 + seam 内按 id 复检、`core_service` 两命令 wire 逐字段=§5.4、写入端 typed fail-closed 先于持久化、错误码全大写复用既有字面量 ✓；**附条件= P2-2（DB 失败码位）**。
- **AC2 PASS** — 三视图（常量 `:51-104` / production `generate_handler!` `:665-675` / `build.rs:55-84`）+ `capabilities/m2rc1-commands.json` 十六项同 commit，probe/ac1 冻结面 7/6 不变，9 命令单测 pin `production_surface_is_exactly_nine_commands` ✓；**附条件= P3-2（gen/schemas 追认 + ACL 断言不覆盖 production-only）与 P3-4（缺 real-sidecar 覆盖）**。
- **AC3 PASS（附披露）** — 46 新测试 = core 22 + editing 20 + pipeline 3 + providers 1，与「43 failed + 3 既有机制即绿」算术自洽；C1-C7/P1-P4 逐条有对应用例，EV-8 三值矩阵 + 非 sfx 强制 + snapshot 逐字段 + review_state 齐备 ✓；**附条件= 层②（管线候选）为「catalog 状态模拟改标」的既有机制守护（已如实登记）、红态/绿态与 test count 无入库原始日志（P3-3）**。
- **AC4 PASS** — `{"regions": RegionListSummary[]}` 包装形状、五字段最小集、`reading_order` 升序、origin/revision_no 取 current 指针 revision、未知 page 空列表非错误（脚注 a）；SQLite 重开（P1）与 service/wire 两层断言覆盖 ✓。
- **AC5 PARTIAL** — 本体成立：`PROTOCOL_MINOR=3`、CS-L1 envelope 2→3、RC2 `PRODUCTION_EXPECTED` 7→9、PROBE_EXPECTED 冻结 7、4 处既有 minor pin 同步、server 只校验 major（`core_service.py:764-770`）故 frozen 探针可留、GATE 25/25 与 CS-L1 实测 minor=3（`raw/cleanstart-gate.json:12,66-73`，25 场景全 PASS 我逐条计数核对）✓；**扣分项= P2-1（AC5 raw 越权覆盖）与 P4-6/P4-5（措辞与 frozen 注记）**。
- **AC6 PASS（附条件）** — 650+1sk（627+1sk+23=core 22+providers 1）、cargo 47+1ig、vitest 49、m2_acceptance 35 的口径与新增文件计数自洽，三套件基线不回退 ✓；**附条件= 被改模块自身的 `tests/editing`/`tests/pipeline` 既有用例未复跑、计数无入库日志（P3-3，未验证项）**。

---

**集成前建议动作（按序）**：① Owner 还原 `verification/M2-AC5/raw/**` 并把本轮产物搬到 `verification/M2-REGION-RETYPE-CORE/raw/`（P2-1）；② Owner 修 `DB_FAILED` 码位 + 补单测（P2-2）；③ Codex 集成记录追认三处范围外文件组（packaging CS-L1、`capabilities`+`permissions`+`gen/schemas`）并修订 Task `:39` 禁止范围措辞（Q1 附条件）；④ 补跑 `tests/editing`/`tests/pipeline` 并入库原始日志、开启 ACL 断言 production 循环、登记前端 pin 顺延（P3-2/3/5）；⑤ 集成后由 Codex 更新契约实现态措辞（P3-6）。
