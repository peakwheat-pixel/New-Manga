> 【集成轮落盘注记】本报告为 DSH r1（非作者，只读，静态）审查原文，由集成方自 headless 会话输出原样落盘（DSH 沙箱只读未落盘）；审查对象 head=6464c4a3，其后 Owner 返修 bd23eaa8（P3-1/P3-3/P3-4/P4 条件闭合，docs-only）→ merge cff4923e。集成 Gate 实测（shell）：本 Task 提交面 29 文件全在允许路径、AC1 commit 零 src、contracts/apps diff 空、d87389af 残留恰 3 处登记性注释（src:120/packaging:137/requirements.txt:36，与 P3-1 清单一致）、worktree clean。

审查完成。全程无 shell（`pwsh` 在本 worktree 一律以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 失败，换 `workdir=C:\` 亦同），因此所有结论来自文件级静态核对 + 可读的 Git 元数据（reflog/ORIG_HEAD/packed-refs），运行级声称按「作者声称 + 静态一致性」采信并逐项标注。**按只读角色约束，我未落盘任何文件**，全文在此输出。

---

# M2-SFX-T4-SWITCH 独立审查报告（DSH r1，非作者）

## ① 审查前置声明

| 项 | 状态 |
|---|---|
| 角色 | DeepSeek Harness，非作者，**只读**；本次会话未创建/修改/删除任何文件（含未落盘本报告） |
| shell | **不可用**。`pwsh -Command "echo ok"` → `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-T4-SWITCH-zcode)`；`workdir=C:\` 同样失败 → 所有 git 命令（diff/status/log/show）均未执行 |
| 替代手段 1 | **Git 元数据直读**（不需 shell）：`.git/worktrees/M2-SFX-T4-SWITCH-zcode/logs/HEAD`（reflog，权威提交顺序+时间戳）、`.git/logs/refs/heads/agent/zcode/M2-SFX-T4-SWITCH`、`ORIG_HEAD`、`packed-refs` |
| 替代手段 2 | **文件级差分替身**：读取主 worktree `G:/CODEX/New Manga/`（master=`78faeee5`）的同名文件作为「改动前」参照。该参照在三个受影响文件上与 base 时点内容一致（pin 现值 `chiqui7/yolo11-manga-seg` + `d87389af…b646`，且行号 :108/:110-112/:118/:121/:137/:138 与 T3 `gate-definition.md:25`、`gate-t3-report.md:176` 引用逐条命中；测试文件为 `EVAL_PAYLOAD`/conf 0.9313 旧锚形态）→ 可作有效替身，但**非权威 base 5166ba7f 快照** |
| 采信口径 | 运行级结论（pytest/构建/探针/冒烟的 EXIT 与数值）作「作者声称 + 静态一致性」采信；凡未独立验证者在下文标 **【未独立验证】** |
| 明确未验证清单 | ①`git diff` 文件清单与 `--name-only` 输出；②`contracts/**`、`apps/**`（除 tauri.conf.json 抽点）零 diff；③`git status` clean；④提交内容清单（各 commit 触及哪些文件）；⑤pytest/构建/探针的真实运行；⑥`safe.directory`/ACL 相关无关项 |

---

## ② Verdict

**`approved_with_conditions`** — 0×P0、0×P1、0×P2、**4×P3、7×P4**。

实质结论：AC1–AC5 的**核心事实全部成立且证据链自洽**——AC1 的执行顺序纪律有 reflog 级硬证据，pin 切换面窄且干净，G7 补证、SHA 门反向验证、回退实测、回归锚迁移、回归计数、directional 纪律、G8 checklist 刷新均与 raw 证据逐项对得上。条件（P3）全部为**文档/证据口径与「越域残留身份文本」登记**问题，以及一项**只有集成方 shell 能完成的复核**；不触及任何 src 行为，可在一次 docs-only 提交 + 集成 Gate 内闭合。

### 分级发现清单

**P0**：无。
**P1**：无。
**P2**：无。

**P3-1｜pin 切换后的残留身份文本越域未登记**
- 位置/证据：`requirements.txt:30-36` 仍写「M2-SFX-PROD-1 standalone SFX detector (**chiqui7/yolo11-manga-seg ONNX**…)」+「sha256 **d87389af**4350…b646」；`src/infrastructure/providers/detection_sfx.py:286`（类 docstring「locally pinned **chiqui7** ONNX」）、`:24`、`:139-140`、`:498`；`src/bootstrap/core_assembly.py:958`（注释「the standalone SFX detector (**chiqui7** ONNX over…）」）；`packaging/m2ac5/build_sidecar.ps1:115`（段头「pinned **chiqui7** ONNX into the bundle」）。
- 影响：`switch-report.md:50`「grep 实证 src/packaging/tests 无 d87389af 活引用（残留 2 处=回退登记性注释）」在**其自述范围内成立**（src:120、packaging:137 恰为 2 处，tests 0 处），但**未覆盖 `requirements.txt:36`**（第 3 处残留），Task/Handoff「已知限制」也未登记任何一项。上列文件均不在 Task 允许路径内 → **未改是正确处置，缺的是登记**。
- 建议：Owner 以一条 docs-only 提交（仅 `doc/tasks/M2-SFX-T4-SWITCH.md` + `doc/handoffs/**`，均在允许面）登记「切换后残留身份文本清单（越域，交后续发布轮/Task 清理）」。

**P3-2｜生产级冒烟证据的 detector 身份标签已过期且未登记**
- 位置/证据：`experiments/M2-TA3-B/run_qualification.py:481` 硬编码 `detector="manga-ogkalu+chiqui7-sfx"`（与主 worktree 逐行同值 → **非本 Task 引入**）；后果落在 `raw/g7-smoke-v2b-console.log:4` 与 `raw/g7-smoke-v2b/summaries/qual-BJ06.json:45`：权重已是 v2b，摘要仍记 `chiqui7-sfx`。
- 影响：该字段不能再作为权重身份证据（本 Task 的权重身份改由 `harness-meta.json`+pin 重指+`qual-report.json:6` 承载，链未被污染）；但 merge 之后**所有** `run_qualification` 证据都会继续如此标注。
- 建议：登记为后续项（T5 前置或独立 docs/harness 小 Task），改为中性标签或由 `SFX_HF_REPO` 派生。

**P3-3｜AC1「新增故障=0」硬断言的计算面窄于 AC 文字**
- 位置/证据：`experiments/M2-SFX-T4-SWITCH/compare_g7_arms.py:47-49,67-69` 仅取 `qual-BJ06.json` 的 `attribution` 集合做差集 → `g7-compare.json:85-86` 的 `new_failure_count=0` 实为「新增 **attribution** =0」。`qual-report.json` 的 `"failures": 0`、`"rerun": []`（两臂，`g7-smoke-{v2b,chiqui7}/summaries/qual-report.json:41-42`）与逐 stage 状态**未被脚本消费**。
- 独立复核（我逐字段核对，未推翻结论）：两臂 `attribution: []`（`g7-compare.json:42,81`）、全部 stage `OK/COMPLETED`（`:8-20,:47-59`）、`both_pipeline_completed=true`、`fail_closed_chain_legal=true`、两臂 `failures=0/rerun=[]/truncated=false` → 结论方向正确，仅断言强度与「硬断言」措辞有落差。
- 建议：脚本补 `failures==0` 与「任一 stage 非 OK/COMPLETED」的合并断言（下次重跑时）。

**P3-4｜NSIS NOT_RUN 的理由与 AC2 允许条件不一致**
- 位置/证据：`doc/tasks/M2-SFX-T4-SWITCH.md:34` 允许 NOT_RUN 的条件是「**若 NSIS 随包验证在本环境不可行**」；实际理由写在 `switch-report.md:51` 与 `handoff:55` = 「**授权面边界**（tauri/NSIS 打包属 M2-AC5/PROD-1 交付链）」。
- 影响：声明本身诚实（全文无任何「NSIS/安装包已执行」的声称，grep 未见），但理由口径应改为 AC2 允许的口径，或明确列入 Task 的偏差登记段落（该段已存在，`doc/tasks/…:60`）。
- 建议：Task 偏差登记补一行。

**P4-1｜build-sidecar 证据的 commit 归属含糊**
`raw/build-sidecar-v2b-console.log:1` 记 `git HEAD=5d5ab592`（=AC1 commit），而 `switch-report.md:126` 把该产物登记在 `5d5b5…`→`5d835e44`（AC2）名下 → 说明构建发生在 **AC2 工作树未提交**状态。bundle 内容另有独立复算兜底：`frozen-v2b-probe-results.json:5` `bundle_sfx_weights_sha256=944e8114…`。建议 §10 加一句归属说明。

**P4-2｜探针/AC3/AC4 console 缺时间戳与进程级退出码捕获**
`raw/frozen-v2b-probe-results.json` 无 `generated_at_utc`；`raw/ac3-pin-switch-verify-console.log`、`raw/ac4-rollback-drill-console.log` 只有脚本自打印的 `AC3: PASS` / `AC4: PASS` / `EXIT=0 semantics`，**不是** shell 捕获的 `$LASTEXITCODE`（对比：两臂 g7 冒烟 log 末尾有真正的 `EXIT=0` 行 + `harness-meta.run_qualification_exit_code=0`）。建议下轮补时间戳与退出码捕获。

**P4-3｜双 base 未在同一处说明（diff 面口径风险）**
Task frontmatter `base_commit: 5166ba7f`，而分支真实 fork 点 = `3d4f20f1`（reflog `branch: Created from 3d4f20f1` + `ORIG_HEAD=3d4f20f1` + handoff「release=3d4f20f1」）。因此 Reviewer 建议命令 `git diff 5166ba7f..HEAD -- src/` 会**连带包含 5166ba7f→3d4f20f1 之间的其它提交**。建议 Integrator 双口径核对（`3d4f20f1..6464c4a3` = 本 Task 自身 5 个提交；`5166ba7f..6464c4a3` = 含间段的完整面），并在 Task 内写清。

**P4-4｜v2b 锚只覆盖 rgb24 面**
`extract_v2b_anchor.py:53-66` 只以 rgb24 字节提取；测试的 `rgb32` 参数（`test:925-931` 的 BGRA 编码）走同一 provider 路径但无锚值支撑（该面由独立测试 `test_rgb32_bgra_input_face_matches_rgb24` 钉住）。建议登记为锚的覆盖边界。

**P4-5｜「38/38」缺 per-file 原始日志**
我静态核到本文件 **38 个 collected node**（31 个 test 函数 + `test_arbitration_env_illegal_value_fails_fast_before_any_detect` 的 7 个参数 + `test_real_weights_reproduce_eval_payload` 的 2 个参数 = 38），与声称的 38/38 算术一致；但仓库内没有该文件单独一轮的 log。建议下轮落 `raw/`。

**P4-6｜冻结探针 FV-1 的 PASS 判据不含「sfx 候选存在」**
`frozen_v2b_probe.py:171-183` 的 FV-1 PASS 条件 = `ready && manga候选 && 无sha/PROVIDER_FAILED线`；`sfx_labels`/`best_sfx_conf` 仅为记录。观测值确实含 `sfx-1`/0.9046694040298462（`frozen-v2b-probe-results.json:15-17`），故结论不弱于声明，但断言面窄于记录面。建议下轮把 `bool(sfx_labels)` 并入判据。

---

## ③ R1–R8 逐项结论

### R1 执行顺序纪律 — **PASS（顺序有权威证据；AC1 三条件逐项支撑，含 1 项口径收窄 P3-3）**

**提交顺序（reflog 直读，权威）** `.git/worktrees/M2-SFX-T4-SWITCH-zcode/logs/HEAD`：

```
3d4f20f1 (分支创建) 
→ d7e11e5d claim            @1791211796 (2026-10-05T15:16:36Z)
→ 5d5ab592 AC1（零 src 补证） @1791214754 (15:39:14Z)
→ 5d835e44 AC2（src 变更）   @1791215635 (15:53:55Z)
→ d631f7ec AC3+AC4          @1791215698 (15:54:58Z)
→ 6464c4a3 AC5（tip）        @1791216973 (16:02:53Z)
```

父子链线性、时间戳单调：`5d5ab592` **先于** `5d835e44` ✓。运行级同向佐证：v2b 臂 `harness-meta.json` `production_pin_at_start=d87389af…`（`started 15:25:27Z / finished 15:36:55Z`），而 `run_g7_smoke.py:91-98` 在 pin≠chiqui7 时**直接 return 2 中止** → 冒烟确实发生在 src 仍是 chiqui7 的时点；AC1 console 时间戳（23:25–23:36 +0800）也落在 AC1 commit 之前。【未独立验证：`5d5ab592` 的文件清单（无 shell），「零 src」由 commit message + 上述运行时断言 + 时序一致性支撑】

**AC1 三条件（`g7-compare.json` verdict 逐项）**：
1. **EXIT=0** ✓：`raw/g7-smoke-v2b-console.log:26-27` = `run_qualification exit code = 0` + `EXIT=0`；chiqui7 臂 `:25-26` 同；两臂 `harness-meta.run_qualification_exit_code=0`。两臂 `pipeline_failures=0 rerun_pairs=0`。
2. **契约合法 / fail-closed 保持** ✓：`g7-compare.json:88-89` `both_pipeline_completed=true`、`fail_closed_chain_legal=true`（`compare_g7_arms.py:116-117` = 无 `defect:detect-crash` 且 run2 ∈ {completed, SKIPPED}）；全部 stage `OK/COMPLETED`；两臂 `attribution: []`。**口径说明**：两臂 region=14/17 均非零，故「0 候选=合法空输入」分支**未被触发**——`switch-report.md:26` 的措辞「语义未触发」如实，未越界声称。
3. **新增故障=0** ✓（结果）/△（面）：`g7-compare.json:85-86` `new_failures_v2b_vs_chiqui7=[]`、`new_failure_count=0`，来源为两臂空 attribution 集合；两臂 `qual-report.json:41-42` 另证 `failures=0/rerun=[]`。见 **P3-3**：脚本未消费 `failures` 字段，断言面窄于 AC 文字。

→ **AC1 PASS 判定成立**；task/handoff 对 AC1 的三条描述与 raw 无出入。G7「自此可记为部署就绪」与 T3 `gate-t3-report.md:210-①`（未补证前不得记部署就绪）约束一致。

### R2 src 变更面 — **PASS（静态替身法；contracts/apps 未独立验证）**

方法：主 worktree（改动前）vs 本 worktree，全量锚点比对 + 关键函数逐行读。

- **`src/infrastructure/providers/detection_sfx.py`**：802 行 vs 参照 786 行（+16）。33 个 `def/class/常量` 锚点文本全同、自 pin 段之后**恒定 +16 行偏移**（`PROVIDER_SFX` 102→105=+3 之后 +16；`_build_engine` 391→407、`_sfx_boxes` 535→551、`MangaSfxParallelDetectionProvider` 656→672 …）。**`_build_engine` 逐行比对**：参照 `:391-445` 与本文 `:407-459` 文本一致——文件存在性探测 → `sha256_file` → `PROVIDER_FAILED` 文案 → `_lazy_import("onnxruntime")` → session → names 断言 → `_parse_imgsz` 顺序与语义**零改动**。变更面 = ①模块 docstring 首段（+3，2026-10-05 裁决与 v2b 身份）②pin 注释块 3 行→16 行（+13）③三个常量值（`SFX_HF_REPO`/`SFX_HF_REVISION`/`SFX_WEIGHTS_SHA256`）。
- **`packaging/m2ac5/build_sidecar.ps1`**：217 vs 211（+6）。变更 = `-SfxWeightsSource` 默认 `weights` → `weights-v2b`（+3 注释）、pin 字面量 → `944e8114…`、缺文件报错文案 → v2b 指引、注释块扩写（+3）；其余锚点恒定 +6，fail-closed 语义（`Get-FileHash` 比对不符即 `throw`）原样。
- **`tests/providers/test_detection_sfx.py`**：974 vs 962（+12）。43 个锚点文本全同：前 85 行 +6、pin 块后 +6、真实权重复现函数内部 +6 后尾部 +12 → **仅两处改动**（详见 R4）。
- **`contracts/**`、`apps/**`**：**【未独立验证】**（无 shell，glob 对本 workspace 外不可用）。抽点：`apps/desktop/src-tauri/tauri.conf.json` 与参照**逐字节同**（34 行，`resources: target/core-sidecar/core-sidecar` 未变）→ 支持「resource 声明零变化」。`contracts/**` 零 diff 交集成方 shell 复核（C4）。
- **方法残余风险（如实声明）**：恒定偏移法无法排除「等量插入+删除」藏在未采样行；缓解 = 43/33 个锚点文本全同 + 安全关键函数逐行同 + 文件总行差与两处改动量精确吻合（+16=+3+13；+6=+3+3；+12=+6+6）。

### R3 来源字段语义 — **PASS（含 2 条 P4 级文字残留）**

- 字段值：`src:123` `SFX_HF_REPO="local-release:sfx-train-v2/v2b"`；`src:124` `SFX_HF_REVISION="c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08"`；`src:126-128` `SFX_WEIGHTS_SHA256="944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"` —— 与 `switch-report.md:12-14,37-38`、Task 交付记录逐字一致。
- **唯一消费点自洽** ✓：repo 全域 grep `SFX_HF_REPO|SFX_HF_REVISION` → 仅 `src:424-425`（`PROVIDER_NOT_CONFIGURED` 的 placement guidance）一处代码消费，无第二消费点、无破损调用。guidance 文案「place the pinned ONNX export of `local-release:sfx-train-v2/v2b` @ `c22f0175` there — …sha256 pinned in src/…」作为**放置指引**自洽；唯一措辞松弛处：把「非 HF 的本地发布通道」+「best.pt 的 sha」说成「ONNX export of X @ Y」（P4-6 同类，登记即可，非缺陷）。
- **全链 sha 逐字核对** ✓：`src:117-119` = `1f0fd609e7dc29c831255db67586ed5623f9bebae6a1e29fae197c1c6d7b77e0` / `c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08` / `944e8114…418d` —— 与 `switch-report.md:44-46` §2 表**逐字一致**，且与 V2 Handoff「基座 `1f0fd609…b77e0`→best.pt `c22f0175…131c08`→best.onnx `944e8114…418d`」同值；`SFX_HF_REVISION` 确为 best.pt 锚 ✓。
- 同文件旧身份文字残留（不在本 Task 声明修改面内，未改为正确）：`:24`、`:139-140`、`:286`、`:498` → 并入 P3-1。

### R4 tests 修改声明逐条核对 — **PASS（4/4 命中，另 2 条 P4）**

替身差分显示 tests 侧**只有两处改动区**，恰好覆盖声明的 4 项：

| 声明 | 证据 | 判定 |
|---|---|---|
| ①`REAL_WEIGHTS` → weights-v2b | `test:64-70`（`…/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`，参照为 `weights/`） | ✓ |
| ②锚来源迁移 | `test:73-81` 新 `V2B_ANCHOR`（`experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json`）取代 `EVAL_PAYLOAD`；`test:922` 读取路径改为 `payload["detections"]`（参照为 `payload["regions"]["K07_R123"]["chiqui7_yolo11s_seg"]["detections"]`） | ✓ |
| ③锚-pin 运行期断言 | `test:923-926` `assert payload["weights_sha256"] == SFX_WEIGHTS_SHA256`（含重提取指引文案） | ✓ |
| ④`REAL_SKIP` 文本 | `test:82-85` reason「real **v2b** weights / eval frame not present」+ `:64-67,:71-75` 注释更新 | ✓ |

- **锚 JSON 与 pin 逐字** ✓：`v2b-k07-r123-anchor.json:7` `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` == `src:126-128`。
- **提取脚本与被测测试同构** ✓：`extract_v2b_anchor.py:58-66` 用 `SfxDetectionProvider(weights_path=…).detect(DetectionRequest(page_id, rgb 字节, w, h))`，与测试 `test:946-947` + `_request()`（`test:97-105`）同一入口、同一契约类型、同一 rgb24 编码（`rgb.tobytes()`）。**边界**：锚只覆盖 rgb24（P4-4）。
- **锚值跨环境一致** ✓：锚 `conf=0.9046694040298462`（anchor:14）== 冻结探针 FV-1 `best_sfx_conf=0.9046694040298462`（frozen-v2b-probe-results.json:17）——开发 venv（部署副本 `weights-v2b/`）与 PyInstaller 冻结 bundle（包内副本）两独立环境同值。
- **旧 chiqui7 锚仅留档、不再被引用** ✓：`experiments/M2-SFX-DETECT/onnx-sfx-frames.json` 仍在盘，但 tests 内仅作注释/历史引用（`test:74`、`test:341`），无任何代码路径读取；其它命中均属别的 Task 脚本/文献。
- **pin 断言本体零改动** ✓：`test:44-53` 符号 import 区在第一条改动（参照 :64）之前 → 逐字节未动；全 tests 目录 grep 无 `d87389af` / 无 sha 字面量断言（全部走 `SFX_WEIGHTS_SHA256`）。
- **38/38 可算术复现** ✓（P4-5：无 per-file log）。

### R5 回归声称 — **PASS（3 个真实权重测试「在 passed 名单」由排除法坐实）**

- 终跑尾部（`raw/pytest-regression-console.log:397-398`）：唯一 `FAILED tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`；汇总 **`1 failed, 1780 passed, 1 skipped, 1 warning in 109.05s`** —— 与声称「1780 passed+1 skipped+1 failed」**逐字相符**。
- 既有失败定性 ✓：该失败为 `assert len(cases) == 97` vs 实到 122（log:382-386），属 `tests/m2_test_assets` 本地 gitignored 素材计数，与本 Task 改动面零交集；同一条失败 + **同一套件总数（1 failed/1780 passed/1 skipped）** 已在前序 Task 入库证据中记录（`verification/M2-REGION-RETYPE-CORE/raw/retype-r1-pytest-full.log:393`、`verification/M2-REGION-RETYPE-CORE/verification.md:107`、`verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md:186`）→ pre-existing 成立。
- **3 个真实权重测试在 passed 名单** ✓（log 为 `-q` 点阵，无 PASSED 清单，用排除法）：`REAL_SKIP` 恰好守 `test:914/962` 的 3 个 node；若权重/帧缺失则三者同跳（+ 既有 1 skip = ≥4 skipped），实测 `1 skipped` → 三者**未跳过**；且首跑「4 failed / 1777 passed / 1 skipped」（`switch-report.md:84`）中 1780−1777=3，与这 3 个 node 被 SHA 门拒跑一一对应 → 终跑里它们落在 passed。
- 「=main 基线一致」：**【未独立验证】**（未跑 main）——由上述前序同基线日志强支持。
- 首跑 log 已被终跑覆盖（`switch-report.md:98` 自述），首跑数字仅有文档承载（可接受，但属弱证据）。

### R6 NOT_RUN 与 directional 纪律 — **PASS（NSIS 理由口径见 P3-4）**

- NSIS **NOT_RUN 如实** ✓：`switch-report.md:51` §9 表 row1、`handoff:55`；全文（task/handoff/report）grep 无任何安装包已构建/已验证的声称；随包机制（`build_sidecar` + tauri resource）确有实测（见 R8）。**理由口径**与 AC2 允许条件不一致 → P3-4。
- **「显著」** ✓：全域 grep 仅 1 处命中 `doc/tasks/M2-SFX-T4-SWITCH.md:43`——正是纪律句本身（「禁用「显著」」），**无任何把该词用作证据描述**的情形。
- **directional 未作质量判定** ✓：`conf 0.9047 vs 0.9313` 在 `switch-report.md:49` + §9 row2 + `frozen_v2b_probe.py:12-14` + `handoff:57` 均标 directional 并说明「期望值为 chiqui7 时代锚值，不跨权重携带」；`BJ06 sfx 5 vs 8` 在 `switch-report.md:29` + §9 row3 + `handoff:56` 标 directional，明确「单一页、无 SFX GT、E2E-MATERIAL 口径、不作质量判定」。措辞「更保守的检出」（report:29 / handoff:56）是方向陈述且回指 T3 G1 已冻结判定（`gate-t3-report.md:55`：v2b 5/5 P1.0 vs chiqui7 P0.8333）→ 属可接受的 directional 表述（P4 级措辞提示，不构成质量判定）。

### R7 部署记录完整性 — **PASS（与 T3 §4.8/§7.4 登记一致）**

- **§5 G8 checklist 刷新** ✓：densho810 窗口 `2026-11-02`「在册未逾期」+ 履行登记 `74fa71e9`（`switch-report.md:75`）== T3 `gate-t3-report.md:160`（§4.8-7）与 `:198`（§7.2「部署时点核查归 T4」）→ T4 履行了该归口义务。许可三项（分发场景须复核 Manga109-s/MangaSeg 边界 / MangaSeg 引用备案 / credit 保守登记；当前本地未分发不触发）== T3 `:152-157`（§4.8-4「PASS 附登记义务」）与 `:198`。
- **§7 部署指引** ✓：①随包形态=新包自动就位、零手工步骤（与 `tauri.conf.json` 未变 + `build_sidecar` 默认源改指 v2b 一致）；②data-root 旧 chiqui7 文件在新 pin 下 = **typed `PROVIDER_FAILED`（有意的供应链保护，非回归）**——与 AC3 实证（`pin-switch-verify.json:12-18` gate fired）及 `verify_pin_switch.py:66-91` 语义一致，且不与 T3 §7.4 冲突（§7.4 只规定「单值恢复+权重在位」的回退，未规定 data-root 升级语义）→ 属 AC5 授权内的部署指引**新增**内容，已同时登记于 §9 row5；③回退 = pin 单值恢复 + `weights/` 在位 == T3 `gate-t3-report.md:209`（§7.4）。
- **T3 §7.4-④ 前置**（「pin 替换 src 变更须由 Codex 授权的 T4 专属 Task 执行，T3 零 src 红线不破」）✓：本 Task 即该授权 Task（`approval: user_ruling_2026-10-05_三件都同意`）。

### R8 Task/Handoff 与证据一致性 — **PASS（worktree clean 与零 diff 未独立验证）**

- **交付链** ✓：reflog == Task/Handoff 所述 `d7e11e5d`(claim) → `5d5ab592` → `5d835e44` → `d631f7ec` → **`6464c4a3`(tip=AC5)**，与 prompt 给的链一致；Task `status: in_review`（停写）✓、`review_events: []`（待集成回填）✓。
- **逐 AC 对表** ✓：AC1↔`g7-compare.json`+两臂 console/harness-meta；AC2↔`pin-switch-verify.json`（v2b_build）+`build-sidecar-v2b-console.log`+`frozen-v2b-probe-results.json`；AC3↔`ac3-*-console.log`+`pin-switch-verify.json`；AC4↔`ac4-*-console.log`+`rollback-drill.json`；AC5↔`pytest-regression-console.log`+`v2b-k07-r123-anchor.json`+`test_detection_sfx.py`。**AC3/AC4 时序自洽**：`rollback-drill.json`(15:54:29Z, pin=d87389af) → `pin-switch-verify.json`(15:54:37Z, pin=944e8114) → commit(15:54:58Z)，即「出证后恢复新 pin 终态」有**时间戳晚于回退 drill** 的独立产物兜底；当前 `src:126-128` = 944e8114 也印证终态。【注】`rollback-drill.json` 的 `weights_sha256_verified_by_gate` / `pin-switch-verify.json` 的 `v2b_build.weights_sha256` 是脚本常量回显（`verify_pin_switch.py:103,136`），不是独立重算——真正的证明是 `_build_engine` 内部比对通过；结论不受影响，但字段名易被误读（P4 级，建议改名 `expected_sha`）。
- **Handoff「Reviewer 建议核对点」5 条**：①顺序 ✓（reflog）；②src diff 面 ✓（替身法，contracts/apps 待 shell）；③tests 声明面 ✓（4/4）；④锚可信度 ✓（sha 逐字 + 双环境同 conf）；⑤运行级补跑 → 转集成方。
- **worktree clean**：**【未独立验证】**。间接证据（非等价）：reflog 最后一条动作是 AC5 提交，其后无 checkout/reset/merge；`src` pin = 终态值（=AC4 后 git checkout 恢复的结果）。未验证项含未跟踪文件/暂存状态 → 集成方 `git status --porcelain`。
- **P4-1/P4-3** 为本次发现的证据归属与 base 口径问题（不影响 AC 成立）。

---

## ④ 推荐下一步

**结论：`approved_with_conditions`（0×P0/P1/P2，4×P3、7×P4，条件均为文档/证据口径 + 集成侧 shell 复核，不触 src）。**

1. **Owner=ZCode（或 Integrator 代行）→ 一条 docs-only 提交闭合 P3-1/P3-3(限制登记)/P3-4**（全部落在允许路径 `doc/tasks/M2-SFX-T4-SWITCH.md`、`doc/handoffs/**`）：
   - 在 Task 偏差登记段补：①「pin 切换后残留身份文本清单（`requirements.txt:30-36`、`detection_sfx.py:24/:139-140/:286/:498`、`core_assembly.py:958`、`build_sidecar.ps1:115`、`run_qualification.py:481`）——均在本 Task 授权修改面之外，登记交后续发布轮/Task 清理」；②NSIS NOT_RUN 理由改为 AC2 允许的口径（或明标为口径偏差）；③AC1「新增故障=0」的断言面说明（`compare_g7_arms.py` 仅消费 `attribution`；`qual-report.failures=0` 为佐证未被消费）。
   - C3（可选，非阻断）：`compare_g7_arms.py` 把 `failures==0` 并入硬断言。
2. **Integrator（编排会话代行 Codex）→ 集成前 shell Gate（我无 shell 的空白项）**：
   - 双口径 diff：`git diff --name-only 3d4f20f1..6464c4a3`（本 Task 自身 5 提交）与 `git diff --name-only 5166ba7f..6464c4a3 -- src tests packaging contracts apps requirements.txt`；
   - `git show 5d5ab592 --stat` 确认 AC1 提交**零 src**；`git diff 5166ba7f..HEAD -- contracts/`、`-- apps/` 为空；`git status --porcelain` 为空；
   - 复核三个残留面：`grep -rn d87389af -- src packaging tests requirements.txt` 应恰为 src:120 / packaging:137 / requirements.txt:36 三处注释。
3. **集成动作**：merge 后回填 `doc/tasks/M2-SFX-T4-SWITCH.md`（`review_events` 追加本轮、`integration_commit`）、`doc/STATUS.md`/`REBASELINE_PLAN` 收口（T4 done、**解锁 [M2-SFX-T5-TILE-KO](doc/tasks/M2-SFX-T5-TILE-KO.md)**）、G8 densho810 窗口（2026-11-02）沿登记；并把本报告原文落 `doc/reviews/M2-SFX-T4-SWITCH-6464c4a3-dsh-r1.md`（**我按只读约束未落盘**）。
4. **可立即转发的下一步指令（给 T5 先行方或集成方）**：
   > 对分支 `agent/zcode/M2-SFX-T4-SWITCH`（base fork=3d4f20f1，tip=6464c4a3）执行集成 Gate：①`git diff --name-only 3d4f20f1..6464c4a3` 与 `5166ba7f..6464c4a3` 双口径，确认 src 仅 `detection_sfx.py`、tests 仅 `test_detection_sfx.py`、packaging 仅 `build_sidecar.ps1`，`contracts/**`/`apps/**` 零 diff；②`git show 5d5ab592 --stat` 零 src；③`git status --porcelain` 空；④`grep -rn d87389af -- src packaging tests requirements.txt`＝3 处登记性注释；⑤merge 后按 DSH r1 报告（approved_with_conditions，0×P0/P1/P2、4×P3、7×P4）闭合条件并落 `doc/reviews/`、回填 Task/STATUS、解锁 T5-TILE-KO。
