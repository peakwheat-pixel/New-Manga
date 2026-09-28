---
task_id: M2-AC1
reviewer: DeepSeek Harness (非作者)
author: ZCode (heavy_task_executor)
base_commit: 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d
reviewed_head: d8c1173b (branch tip；返修 5a59ddfe + 证据 d8c1173b)
previous_review: doc/reviews/M2-AC1-7d157858-dsh-r1.md (decision: approved, 条件批准)
decision: approved
review_mode: 静态 Review（沙箱仍无法执行 git / pytest / cargo / npm）
---

# Review r2：M2-AC1 end-to-end acceptance on the M2 baseline

- Task=M2-AC1
- reviewed head=branch tip `d8c1173b`（返修 `5a59ddfe` + gate 证据 `d8c1173b`）
- r1 被审 head=`7d157858f570fa6399073d0419b0adba6d13ee0f`；base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`
- disposition：[verification/M2-AC1/review-dsh-r1-disposition.md](../../verification/M2-AC1/review-dsh-r1-disposition.md)
- decision: **approved**

## 0. Review 口径与沙箱限制

**本报告仍是纯静态 Review。** 本会话 `pwsh` 工具在本沙箱内依旧完全不可用（任何命令都返回
`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-AC1-zcode)`）。
因此：

- 我**未执行**任何 git / pytest / cargo / npm / `run_e2e.py`；**未复跑任何测试**；
- 所有 PASS/FAIL 均为**引用 Owner 已入库证据**并做**内容自洽性核对**，不是我的独立复现；
- `implementation_commit` 的真实性（`5a59ddfe` 是否等于当前工作区父提交）**我无法用 git 验证**，只能核验它与证据内容是否自洽；
- r1 报告中标为 `NOT_RUN` 的 git 类断言（`git diff --name-status` / `--check`）在 r2 同样 `NOT_RUN`。

## 1. 逐条 F-xxx 复核结论

### F-001（P2，AC1 摘要比对口径）— **通过**

- 代码：`verification/M2-AC1/run_e2e.py` L295–L310 新增 `{sample}-restore-saved-matches-run1`：
  `sorted(saved2.pages, key=index) == sorted(saved.pages, key=index)` 且 `providers` 相等、`run_status` 双方 `completed`。**按 index 排序**已消除我指出的"枚举顺序隐含依赖"。
- 证据：`e2e-gate-full/raw/e2e-gate.json` L194–L217 `sample-a-restore-saved-matches-run1` PASS，`observed` 同时记录
  `run1_pages=[[0,"f66af60a9846"],[1,"4afc67386c25"]]`、`run2_pages` 同值；sample-b（L338–L361）同值。
- **非空断言核验（关键）**：我另行读取 `e2e-gate-full/sample-a/run1.json` 与 `run2.json`，确认 run2 的 `saved` 字段**确实存在**且两页 sha/size/providers/run_status 与 run1 完全一致。
  即该场景比较的是**两次真实进程各自读回**的摘要（run1 进程 vs run2 进程），不是自我比较的恒真断言。r1 的核心缺口（run2 摘要从未被消费）已闭合。
- **残留（P4，见 R2-04/R2-05）**：跨样本比对 `run_e2e.py` L422 `summary_a == summary_b` 仍用原始 list 相等，未做排序；该处仍是"越严越好"的方向（顺序不确定会 FAIL，不会假 PASS），故仅记为残留 nit，不否定修复。

### F-002（P2，恢复启动内部自洽）— **通过**

- 代码：`run_e2e.py` L311–L321 新增 `{sample}-restore-internals-match-restored-saved`：
  `bool(saved2_by_index)`（非空守卫）且 `viewed[i].sha256 == saved2_by_index[index]` 且
  `exported_sha(run2) == saved2_by_index[run2.exported.page_index]`。
- 证据：`e2e-gate.json` L220–L224（sample-a，`exported_sha=4afc67386c25` PASS）、L364–L368（sample-b PASS）。
- 该场景把 run2 的 Reader 取字节与导出字节**同时锚定到 run2 自己重读的持久化摘要**，正是我 r1 指出的"缺少同一次恢复启动内自洽断言"。**通过**。

### F-003（P2，ACL manifest 覆盖 ac1 命令）— **通过**

- 代码：`apps/desktop/src-tauri/src/main.rs` L454–L463 改为
  `command_allowlist(true, false).into_iter().chain(command_allowlist(false, true))` 逐条断言 `__app-acl__` 存在 `allow-*`。
  迭代集合 = probe 面 7 + ac1 面 6 = 13 条（含 3 条重复），**覆盖全部 10 个命令**，含 `ac1_request/ac1_write_results/ac1_exit`。
- 与被断言对象自洽：`ac1_bridge.rs`/`gen/schemas/acl-manifests.json` 实际含 `allow-ac1-request`/`allow-ac1-write-results`/`allow-ac1-exit`（r1 已核验），因此该断言现在**有判别力**（权限名写错即失败）。
- 证据：`cargo-test.log` L47 `test tests::app_acl_manifest_is_generated_and_enforced ... ok`，L56 `26 passed; 0 failed`。
- 残留（P4，见 R2-06）：该测试上方的文档注释 L431–L437 仍写"declares exactly the seven live commands"，未随断言范围更新。

### F-004（P3，gate 侧解码/像素摘要）— **通过**

- 代码：`run_e2e.py` L364–L377 新增 `png_pixel_digest()`（`QImage` 解码 → `Format_RGB32` → `sha256(constBits())`），L345–L354 新增 `{sample}-export-png-decodes`，断言 `width==240 and height==320`（fixture 尺寸）并把像素摘要写入 gate JSON。
- 证据：`e2e-gate.json` L235–L241（sample-a：`width 240 / height 320 / pixel_sha b191d8e5fad6` PASS）、L379–L385（sample-b：**同一** `b191d8e5fad6` PASS）。
- **额外收获**：两个独立数据根样本的导出 PNG 像素摘要**完全一致**，这比 r1 的字节 sha 一致更强，直接证据化了"同机同 Qt 下渲染像素确定性"（r1 §2(6) 曾只能靠字节 sha 推断）。AC5 的"像素摘要与 Reader 展示一致"现在在 E2E gate 层有独立记录，pytest 层的 `_assert_png_pixels_match` 不再是唯一像素证据。
- 残留（P4，见 R2-07）：`record_environment` 现在完全不探测 runner 解释器/PySide6，缺 PySide6 时该场景会记 FAIL 而非 gate 文档承诺的 `BLOCKED`（仍 fail-closed，不会假 PASS）。

### F-005（P2，gate 环境口径冲突）— **通过（根因诊断正确，修复到位）**

- **根因成立**：r1 矛盾的解释是——`EVN-python` 来自 `shutil.which("python")` 的 **PATH 工具链探测**（`C:\Python314`），而 runner 自身解释器是 venv（`venv_python = sys.executable`，L411）。这两者在我 r1 的读法里被混为一谈；Owner 的诊断准确。
- 修复：`record_environment` L96 移除 `python` 探测（`tools = ("cargo","rustc","node","npm")`），L91–L95 新增 `EVN-runner-python`（`sys.executable` + `sys.version`）；`write_gate` L453–L461 顶层新增 `implementation_commit` 与 `runner_executable`。
- **我按要求核验新证据字段**（读 `verification/M2-AC1/e2e-gate-full/raw/e2e-gate.json`）：
  - L2 `"implementation_commit": "5a59ddfeb6ddac1f846ec03bc570a687191f255d"` ✓ 与 disposition 声明一致；
  - L4 `"runner_executable": "G:\\CODEX\\New Manga.task-envs\\TASK-012-py312\\Scripts\\python.exe"` ✓ TASK-012-py312 venv；
  - L7–L12 `EVN-runner-python`：`executable` 同上、`"version": "3.12.3"` ✓；
  - 旧 `EVN-python-resolved` / `EVN-python` 已**不再出现**于该文件（对比 e2e-evidence 旧文件 L5/L12 仍在）✓。
  **歧义已消除**，且与 r1 stderr 中 `…TASK-012-py312\Lib\site-packages\PySide6` 的证据吻合，Task 表 L61 与 Handoff L47 的表述亦已同步。
- 残留（P3，见 R2-03）：`verification/M2-AC1/e2e-evidence/raw/e2e-gate.json` **未重跑/未加注**，仍是 r1 前的旧格式与旧记录（含 `C:\Python314`）。Task 表 L61 已用文字标注其为"r1 前另有两次 PASS 运行存档"，但文件本身无任何 stale 标记。

### F-007（P3，注释过度声称 detect 已验收）— **通过**

三处全部落实，且措辞与事实一致（我逐一读取核对）：

1. `src/infrastructure/providers/mock_local.py` L46–L52：明确"the `detect` step never executes … its detect path is NOT exercised or accepted by the M2-AC1 evidence"。
2. `src/bootstrap/core_assembly.py` L670–L673：明确"never executes ``detect``… exists so a region-less page still fails closed at the detect capability gap"。
3. `src/bootstrap/acceptance_bridge.py` L333–L340：明确"a single plan/execute pair completes the run…``resume_blocked`` … is NOT exercised by the released acceptance evidence"。

**与生产 planner 事实一致**（r1 已核验）：`src/application/tasks/service.py` L346–L358 仅在 `region is None` 时前置 `detect`；`sample-a/run1.json` 的 `run.providers` 只有 `{ocr, translate}`，确实无 detect。**通过**。

### F-009（P3，日志头尾 + 证据↔commit 绑定）— **部分通过（见 R2-02）**

- 已落实的部分 ✓：
  - `pytest-m2-acceptance.log`：L1–L2 解释器 + Python 3.12.3、L5 `# EXIT: 0`；
  - `vitest.log`：L1 toolchain 头、L16 `# EXIT: 0`；
  - `cargo-test.log`：L1 toolchain 头、L2 HEAD 头、L58 `# EXIT: 0`；
  - `pytest-full-suite.log`：L1–L3 解释器 + Python + HEAD 头、L389 `# EXIT: 0`（另核验 L388 为 `1322 passed, 5 skipped`，5 条 skip 原因与 r1 相同——docTR/torch/numpy 未安装，**无新增 skip**）；
  - gate JSON 顶层 `implementation_commit` ✓（L2）。
- **未通过的部分**：`cargo-test.log` L2 的 `# worktree HEAD: 7d157858…` 与**该日志正文自相矛盾**——L29 `ac1_bridge::tests::spawn_args_target_the_acceptance_module` 与 L41 `spawn_fails_typed_on_missing_python` 这两个测试名**只存在于返修后代码**（r1 的 `cargo-test.log` 在 7d157858 下记录的是旧名 `spawn_targets_the_acceptance_module`，且为 25 tests，见 r1 报告）。即：正文内容属于返修后代码，头部 commit 指向返修前提交。`pytest-full-suite.log` L3 同样写 `7d157858`（该套件内容与提交无关，故不构成矛盾，但与 cargo 日志一样未反映返修提交）。
- **我不认为这是结果造假**：cargo 日志正文自洽（26 tests、新名称、编译警告位置 `src\main.rs:355:66`/`357:9` 未变且位于测试模块之前，符合"仅测试体内新增若干行"的重跑特征，1.77s vs r1 1.86s）。最可能是**在 7d157858 的脏工作区上先跑套件、之后才提交 5a59ddfe**。但 F-009 引入该头的目的正是"证据↔commit 机器绑定"，一个**不含 dirty 标记、且指向不含被测代码的提交**的头，会误导审计者用 `git diff 7d157858..tip` 去核对这 26 个测试。此外 `vitest.log` 与 `pytest-m2-acceptance.log` **完全没有 HEAD 字段**，同一批日志未统一口径。
- 结论：**F-009 不通过（需补）**，见 R2-02。

### F-010（P4）— **(c) 通过；(a)(b) 接受 deferred**

- (c) ✓ **通过**：`run_e2e.py` L324–L328 对 `output_path` 做显式类型/非空校验，缺失即 `gate.record(f"{sample}-export-png","FAIL",...)` 并 `return None`（不再把 `"None"` 当路径）。fail-closed 方向正确（该 sample 不进 `samples`，总 verdict 转 FAIL）。
- (a)(b) deferred **接受**：`log_dir` 全局（L136/L157 仍在用）与"超时只在有输出时判定"（L194–L202）确未修。两次完整 gate 均未触发，属健壮性打磨；但 (b) 我仍建议补一个循环外的超时/进程树清理（静默挂起会阻塞到工具级超时），可作为后续 harness 迭代项。

### F-011（P4，spawn 目标无判别力）— **通过**

- 代码：`ac1_bridge.rs` L50–L55 新增 `pub fn spawn_args() -> Vec<&'static str>`，L67 `Command::new(...).args(spawn_args())` 实际使用它。
- 测试：L154–L162 `spawn_args_target_the_acceptance_module` **字面断言** `spawn_args() == vec!["-m","bootstrap.acceptance_bridge"]`；原失败路径测试更名为 L166 `spawn_fails_typed_on_missing_python`（名实相符）。
- 证据：`cargo-test.log` L29 / L41 两个新名字均 `ok`，26 passed。**通过**（替换 r1 那条名不符实的测试）。

### F-012（P4，前端 ac1 拒绝面无单测）— **通过**

- 代码：`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts` L21–L24 定义 `AC1_TEST_COMMANDS`（含注释说明其仅存在于显式测试启动配置），L86–L96 新增
  `"ac1 commands are denied on production and probe surfaces"`，对 `production` 与 `probe` 两个模式逐一断言三命令 `rejects`。
- 证据：`vitest.log` L9 `commandSurface.test.ts (8 tests)`（r1 为 7），L12 `19 passed`。**通过**。
- 备忘（非 finding）：该测试的 `AC1_TEST_COMMANDS` 是**前端侧独立常量**，与 Rust `main.rs` 的 `AC1_TEST_COMMANDS` 手工双份；这是该 mock 文件既有设计（`PRODUCTION_COMMANDS`/`PROBE_ONLY_COMMANDS` 同样如此），有漂移可能但属既有模式。

### F-013（P4，fixture Region origin 语义）— **通过**

- 代码：`acceptance_bridge.py` L315–L318 改为 `origin=RegionOrigin.MACHINE`，并加注释说明"harness-fabricated fixture region, not a user edit, so USER would misrepresent its provenance (F-013)"——与 detect 步骤的 `region_creator`（`core_assembly.py` `_create_detected_region` 用 `RegionOrigin.MACHINE`）同源，语义自洽。
- 证据：`pytest-full-suite.log` 报 1322 passed + 5 skipped EXIT 0（该改动影响的是 m2_acceptance 与既有 Region 测试面，Owner 报零回归）。**通过**。我未能独立复跑该套件（沙箱）。

### F-006（P4，status 二态诊断弱）— **接受 deferred**

Owner 的 deferred 理由成立：`method_status`（`acceptance_bridge.py` L270–L272）在"有页面无 translated revision"时返回 `empty`，随后 `method_seed_fixture` 的冲突守卫（L291–L294 的 `AC1_SEED_CONFLICT`）使闭环仍 **fail-closed**，不存在假 PASS 面。`partial` 三态属诊断增强，不阻断验收。**接受 deferred**（保留为后续 harness 迭代项）。

### F-008（P2 治理，3 组 ACL 联动文件的范围追认）— **维持 open，非 Owner 责任**

- Owner 立场不变（disposition L17）：3 组文件是 Task L41"测试 command 仅显式测试模式注册"的 Tauri ACL 机制必然产物，无生产面扩张。
- r2 我复核后**同意该技术论断更强了**：F-003 修复后，`__app-acl__` 对 ac1 三命令的权限存在性已有单测守卫，而生产/探测面命令集仍由 `command_allowlist(false,false)`/`(true,false)` 与生产 `generate_handler!` 三重钉死（`main.rs` L55–L64、L338–L342）。
- 但**范围授予权限在 Codex**，不在 Owner 也不在 Reviewer。**维持 open，提请 Codex 在 integration record 显式追认**（同 r1）。

## 2. 新增 findings（r2）

| ID | 级别 | 文件/行 | 触发与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R2-01 | P2 | `doc/handoffs/M2-AC1-zcode-delivery-20260928.md` L52、L53、L54（另 L51、L58、L35） | **Handoff §验证证据表未随返修更新**，与已更新的 Task 测试表及实际日志**直接矛盾**：L52 仍写"40/27 场景"（实为 44 + 旧 34）、L53 仍写"25 passed"（实为 26）、L54 仍写"18 passed"（实为 19）、L51 未提 gate 侧像素解码、L58 仍称"两次 gate 运行"（现为一次返修后 44 场景 + 一次 r1 前旧格式）。Handoff 是 Reviewer/Integrator 的**主要输入**，错误数字会被复制进 integration record | `doc/tasks/M2-AC1.md` L59–L61 已更新为 26/19/44；`cargo-test.log` L56 = 26；`vitest.log` L12 = 19；`e2e-gate.json` 44 场景 | 用与 Task 表一致的口径更新 Handoff L51–L55、L35、L58（含 ACL 组文件之外新增的 `verification/**` 路径与 reviewed-tip 的路径计数），并同步 front-matter `delivery_head` |
| R2-02 | P2 | `verification/M2-AC1/cargo-test.log` L2；`verification/M2-AC1/pytest-full-suite.log` L3 | F-009 新增的"证据↔commit"头**指向不含被测代码的提交**：cargo 日志正文含只存在于返修后的测试名（L29/L41）与 26 tests，而 L2 写 `worktree HEAD: 7d157858…`（r1 被审 head，当时为 25 tests 且测试名为旧名）。最可能是在该 HEAD 的**脏工作区**上先跑套件、之后才提交 5a59ddfe；但头部无 dirty 标记，审计者按 `git diff 7d157858..tip` 核对会得出错误结论。另：`vitest.log`、`pytest-m2-acceptance.log` **无 HEAD 字段**，同批日志口径不一致 | `cargo-test.log` L2 vs L29/L41/L56；r1 的 `cargo-test.log`（25 tests + `spawn_targets_the_acceptance_module`） | 二选一：(a) 在返修 tip 上重跑四个套件并重采日志；或 (b) 头部同时记录 HEAD 与工作区状态（如 `git status --porcelain` 是否为空 / `+dirty`），四个日志统一格式。**注意：正文数字本身自洽可信，我未发现结果造假迹象** |
| R2-03 | P3 | `verification/M2-AC1/e2e-evidence/raw/e2e-gate.json`（全文）L5、L12 | 该文件仍是 **r1 前的旧格式旧记录**：无 `implementation_commit`/`runner_executable` 顶层字段、仍含已删除的 `EVN-python-resolved`/`EVN-python`（`C:\Python314`）、缺 F-001/002/004 的 4 个新场景。Task 表 L61 已用文字说明其为旧存档，但**文件本身无 stale 标记**，F-005 想消除的歧义在该文件里依然存在 | 该文件 L5/L7（`EVN-python-resolved`/`C:\Python314`）、L303–L309；对比 `e2e-gate-full/raw/e2e-gate.json` L2/L4/L7 | 在 `e2e-evidence/raw/` 加 `NOTE.md` 注明"r1 前存档、被 e2e-gate-full 取代、不含 F-001/002/004 断言"，或用 `--skip-build` 在新 tip 重跑覆盖 |
| R2-04 | P4 | `verification/M2-AC1/run_e2e.py` L318（同类 L301–L302） | 新增场景对 `exported`/`pages` 使用 `run2.get("exported", {}).get(...)`：键**缺失**时优雅 FALSE，但键存在且值为 `null` 时会 `AttributeError` 使 gate **崩溃**（不写 gate JSON）。与其下方同用途的 `exported_sha()`（L358–L361，用 `or {}` 正确处理 None）不一致；`sorted(... key=lambda page: page["index"])` 亦假定每页必有 `index`。崩溃仍是非零退出、不会假 PASS，但丢失诊断输出 | `run_e2e.py` L318 vs L358–L361 | 统一改用 `(run2.get("exported") or {})`，并对 `pages` 元素做键存在性校验（缺失即记 FAIL） |
| R2-05 | P4 | `verification/M2-AC1/run_e2e.py` L438–L450 | `implementation_commit()` 只在 `OSError`/`TimeoutExpired` 时回退 `"UNKNOWN"`；git **非零退出**（例如不在仓库内）时 `stdout` 为空 → 返回 `""`，gate JSON 出现空的 `implementation_commit` 而**无任何信号**，F-009 想建立的机器绑定被静默架空 | L441–L448（`check=False` 且未检查 `returncode`） | 检查 `returncode`/空串并回退为 `"UNKNOWN"`；或在为空时记一条 `NOT_RUN` 场景使 gate 转 FAIL |
| R2-06 | P4 | `apps/desktop/src-tauri/src/main.rs` L431–L437 | 该 doc 注释仍写"pins the build artifact: the app manifest declares exactly the **seven** live commands"，而紧随其后的循环（L454–L463）现覆盖 probe ∪ ac1 共 **10** 条命令。注释陈旧（与 r1 F-007 同类的"注释与行为不符"） | L431–L437 vs L454–L463 | 更新为"ten commands (seven resource-channel + three M2-AC1 acceptance)" |
| R2-07 | P4 | `verification/M2-AC1/run_e2e.py` L91–L95、L96 | `record_environment` 现在完全不探测 runner 解释器能力：`EVN-runner-python` 用 `gate.pass_or(True, …)`，**永不可能失败**（仅作事实记录）；因此缺 PySide6/版本不符时，问题会以 `{sample}-export-png-decodes` 的 FAIL 或 `run1-exit-code` FAIL 出现，而非 gate docstring（L13）承诺的"unusable environment → BLOCKED" | L91–L95（无条件 True）、L345–L354（解码失败记 FAIL）、L364–L377 | 在 `record_environment` 增加 `EVN-pyside6` 探测（`import PySide6` 成功/失败），失败时按 BLOCKED 路径返回，保持 gate 的环境分类语义 |

**级别汇总（r2 新增）**：P0=0、P1=0、P2=2（R2-01、R2-02）、P3=1（R2-03）、P4=4（R2-04…R2-07）。

**r1 findings 最终台账**：fixed 通过 10（F-001、F-002、F-003、F-004、F-005、F-007、F-010c、F-011、F-012、F-013）；fixed 部分通过 1（F-009，见 R2-02）；deferred 接受 2（F-006、F-010ab）；open 待 Codex 1（F-008）。

## 3. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| `git diff --name-status` / `git diff --check` | 未执行（沙箱 `pwsh` 不可用） | — | **NOT_RUN** | §0 |
| `python -m pytest tests/m2_acceptance -q` | 未执行；引用 Owner 日志 | TASK-012-py312 / 3.12.3（日志头） | **NOT_RUN（引用 PASS：4 passed, EXIT 0）** | `pytest-m2-acceptance.log` L1–L5 |
| `cargo test --locked` | 未执行；引用 Owner 日志 | cargo 1.98.1 | **NOT_RUN（引用 PASS：26 passed, 0 failed, EXIT 0；但 HEAD 头与正文矛盾，见 R2-02）** | `cargo-test.log` L1–L2、L56、L58 |
| `npm test`（vitest） | 未执行；引用 Owner 日志 | node v24.15.0 / npm 12.0.1 | **NOT_RUN（引用 PASS：3 files, 19 passed, EXIT 0）** | `vitest.log` L1、L12、L16 |
| 全仓 pytest | 未执行；引用 Owner 日志 | TASK-012-py312 | **NOT_RUN（引用 PASS：1322 passed, 5 skipped, EXIT 0）** | `pytest-full-suite.log` L1–L3 |
| `python verification/M2-AC1/run_e2e.py`（完整构建版） | 未执行；引用 gate JSON | `runner_executable` = TASK-012-py312 venv；`implementation_commit` = `5a59ddfe…` | **NOT_RUN（引用 PASS：44 场景全 PASS，0 FAIL/NOT_RUN）** | `e2e-gate-full/raw/e2e-gate.json` L2/L4、L408 |
| 场景计数核验（静态） | 逐条枚举 gate JSON 的 scenario id | reviewed head | **PASS**（12 env/build + 15×2 样本 + 1 跨样本 + 1 总判定 = **44**；disposition/Task 声称 44 一致） | 同上，L7–L404 |
| F-005 字段核验（静态） | 读 gate JSON 顶层 + `EVN-runner-python`；确认旧 `EVN-python*` 已消失 | 同上 | **PASS**（`runner_executable` = `…TASK-012-py312\Scripts\python.exe`；`version` 3.12.3；无 `C:\Python314` 残留） | 同上，L2、L4、L7–L12 |
| F-001/F-002 非空性核验（静态） | 读 `sample-a/run1.json`、`run2.json` 的 `saved` 对比新场景 observed | 同上 | **PASS**（run2 `saved` 两页 sha `f66af60a…`/`4afc6738…` 与 run1 相同；场景非恒真） | `e2e-gate-full/sample-a/{run1,run2}.json`；gate JSON L194–L224 |
| F-004 像素确定性（静态） | 比对两样本 `export-png-decodes` 的 `pixel_sha` | 同上 | **PASS**（sample-a 与 sample-b 均为 `b191d8e5fad6`，240×320） | gate JSON L235–L241、L379–L385 |
| F-009/F-005 证据陈旧性（静态） | 读 `e2e-evidence/raw/e2e-gate.json` 顶层与场景表 | 同上 | **FAIL（该文件为 r1 前旧格式，见 R2-03）** | `e2e-evidence/raw/e2e-gate.json` L1–L12、L303–L309 |

**Architecture 面结论**：**通过，较 r1 更强**。返修未触碰生产装配缝：`mock_local_providers` 仍为唯一入口（`core_assembly.py` L675–L682），生产默认路径不变；ac1 命令面三处注册表仍未被生产面吸收，且现在 `__app-acl__` 对 ac1 命令的授权**有了单测守卫**（`main.rs` L454–L463）；`ac1_bridge::spawn_args()` 把 sidecar 目标变成可断言的**数据**而非硬编码字符串，降低了误指向生产控制面的风险。F-008 的范围追认仍归 Codex。

**Verification 面结论**：**通过（受限）**。返修把 r1 指出的四处最弱证据点实质补齐：run2 摘要首次被消费且锚定两次独立进程的读回（F-001/F-002）、ACL 单测覆盖到 ac1（F-003）、gate 侧独立解码并给出**跨样本一致的像素摘要**（F-004）、环境口径与 runner 解释器绑定（F-005）。新证据在**判别力**上优于 r1：新增的 4 个场景都能在对应缺陷回归时失败（我逐条核验过其非恒真性）。扣分项为 R2-01/R2-02/R2-03（文档与证据标注一致性），均为**记录精度**问题而非结论正确性问题；我未发现任何可导致假 PASS 的面（gate 仍对 FAIL/NOT_RUN/缺失 fail-closed）。

## 4. 结论

**decision: approved（条件下批准）**

- r1 的 13 条 finding 中，**10 条 fixed 通过**（F-001/002/003/004/005/007/010c/011/012/013），**1 条部分通过**（F-009，日志头与正文的 commit 绑定不一致，见 R2-02），**2 条 deferred 接受**（F-006、F-010ab），**1 条维持 open 待 Codex**（F-008，非 Owner 权限）。
- AC1–AC6 依据**增强**：AC1/AC2 现有"重启后从持久化重读 == 保存时"的跨进程断言（F-001），AC2/AC4/AC5 现有恢复启动内部自洽断言（F-002），AC5 现有 gate 层独立像素解码且两样本像素摘要一致（F-004），AC6 的诚实 Gate 属性未被削弱。
- **无新增 P0/P1**。r2 新增 2 条 P2、1 条 P3、4 条 P4，全部为文档/证据标注与健壮性打磨类问题。

**批准条件（交 Codex 集成前处理）**：

1. **R2-01（必须）**：更新 Handoff §验证证据表（L51–L55、L58、L35）使其与 Task 表及实际日志一致（26 / 19 / 44 场景 / 新增断言），并同步 front-matter `delivery_head`。否则 Integrator 会按过时数字登记。
2. **R2-02（必须）**：修正 `cargo-test.log`/`pytest-full-suite.log` 的 `worktree HEAD` 标注——在返修 tip 重跑四套件，或为四个日志统一补"HEAD + 工作区是否干净"头。
3. **R2-03（建议同批）**：为 `e2e-evidence/raw/e2e-gate.json` 加 stale 标注或以 `--skip-build` 在新 tip 重跑覆盖。
4. **F-008（必须，Codex 权限）**：在 integration record 中显式追认 `build.rs`、`capabilities/m2rc1-commands.json`、`gen/schemas/*.json` + `permissions/autogenerated/ac1_*.toml` 属 Task L41 机制必然产物。
5. R2-04…R2-07 为建议项，可并入后续 harness 迭代。

**剩余风险**：Qt/字体渲染的跨机不确定性仍为已声明的同机假设（本次两样本像素摘要一致进一步支持同机确定性，但不外推到跨机）；planner regionless `LOCK_CHANGED` 缺口仍未修且需另行登记；F-006/F-010ab 留待后续；本次 Review 未独立复跑，集成门的实际复跑与 `git diff --check` 仍应由 Codex 执行并单独立证。

**复审方式**：若 Owner 继续返修，请给新 head 与 R2-xx / F-xx 的逐条 disposition；复审追加新 head 记录，不抹掉 r1/r2 记录。

---
*本报告为只读评审产物，未修改任何实现文件、测试、Task 文件或证据。所有行号引用基于 reviewed tip 工作区静态内容。*
