# M2-SFX-GATE-T3 · 独立 Review 报告（DSH，非作者，只读）

## 1. 审查前置声明

**只读边界**：本会话未修改、未创建任何文件；全部结论来自对已提交文件的静态阅读（read/glob/grep）。

**shell 不可用（重要限制）**：本 worktree 上 `pwsh` 会话初始化失败——`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-GATE-T3-zcode)`（含 `workdir` 指向子目录同样失败），`danger-full-access` 升级返回「requires approval, but no approval channel is available」。因此本轮**无法执行**：

| 未执行项 | 影响 |
|---|---|
| `git log/status/diff 87ca8724..e53a2629` | 提交链顺序、26 文件清单、零 src diff、pin base..HEAD 逐字一致——只能依赖盘上文件与作者自述 |
| `python eval_gate_t3.py / verify_data_integrity.py / recompute_eval_t3.py` | 断言复跑、36 格复算未独立复跑 |
| 三权重 onnx sha256 盘上重算 | 无法验证权重文件本体（含 v2a/v2b 是否与 V2 当轮同字节） |

**已完成的运行级替代验证（逐值静态核对）**：
- 36 格矩阵（`eval-matrix.json` 571 行）↔ 报告 §0/§3 表 ↔ `raw/run-full.log` 逐页行：**24 主格 + 12 letterbox 对照格全部逐值一致**；逐页 matched 求和与格值一致（如 chiqui7 ko-npd 19+18+2+2=41/135；v2a 9+19+3+4=35/135；v2b 14+26+5+3=48/135）。
- `n_tiles` 261 = 58+112+70+21（log 页级 tile 数）✓；四页耗时 17–18/50–52/71–74/77–81 s 与报告 §7.3 一致 ✓。
- 数据侧：`npd-judgments/consensus.json` per_page a=44+10+33+41=128、b=135、matched=106、only_a=22、only_b=29（与报告 §2.2 逐值一致）；`annotate-r4/judgments/consensus.json` a=13/b=17/matched=12/only_a=1/only_b=5 ✓；`divergence.json` 51 单元 status 计数 = keep19+keep-merged9+correct1+delete8+delete-duplicate14 = 51 ✓。
- 交叉核对 KO-TILE 参考：`verification/M2-KO-TILE-CALIB/eval-matrix.json` 的 chiqui7 tile 56/56 P0.8235 n_pred68、v2b tile 35/56 P0.3465 n_pred101（0.2 档 56/56 P0.6667 / 43/56 P0.2019）与 T3 重跑值**逐位相同**——「复现参考矩阵」声称成立。
- 代码口径：`detection_sfx.py:107-138` 行号与常量逐条对得上（`SFX_WEIGHTS_SHA256=d87389af…` :110-112、`SFX_CONF_THRESHOLD=0.5` :118、`SFX_NMS_IOU=0.7` :121、`SFX_CLASS_MAP` :137、`SFX_CLASS_ID=2` :138、names 装载期断言 :436-443、`_sfx_boxes` conf 过滤先于类无关 NMS :560-572）；`eval_gate_t3.py:104-106/194-226/428-429/477-487/509-519/711-712` 等被引行号全部命中。
- 措辞纪律：`verification/M2-SFX-GATE-T3/` 全域 grep「显著」仅出现在纪律声明中，**无一处用于模型优劣比较** ✓；无「独立复核（非作者）」类措辞 ✓。

---

## 2. Verdict

**approved_with_conditions**（P0=0 / P1=1 / P2=3 / P3=5 / P4=4）

判定理由：核心交付（Gate 定义冻结、双前置数据、36 格矩阵、G1/G2/G3/G8 逐门判定）在**数字层全部与盘上产物逐值一致**，FAIL 判定如实（v2a 双 FAIL、v2b 唯一候选），已知限制与循环性总登记到位，未发现虚构、未见自查冒充独立复核、未见「显著」滥用。**不构成 changes_requested**，因为唯一的 P1 是判定标签/裁决留痕问题、P2 均为证据档案与登记问题，均不需重跑评测；但**不可直接判 approved**，因为 G7 的无条件 PASS 与冻结定义 §4.G7 阈值③不一致（判定忠实性问题），且 G2-B 硬判据载体的仲裁物证链弱于 AC2。

---

## 3. 重点问题裁定

### Q1（最重要）· G7 无条件的 PASS 是否忠于 gate-definition v1.0 §4.G7？——**不忠实，须降级标注或由编排出裁决**

- 冻结定义（`gate-definition.md:113-121`）：口径=「进程内重指 → `SfxDetectionProvider.detect` → **SFX 产物按现役语义流入翻译链入口（SFX mask/policy/translate 入口既有链路，M2-SFX-TRANSLATE-ENTRY 产物，只读调用）**」；阈值③=「vs 基线同链对照：**下游错误/异常/超时新增数=0**」。
- 实际执行（报告自述 `gate-t3-report.md:143`）：「翻译链入口的深层调用（run_qualification 级 policy=translate 端到端…）在 T3 当轮与 T0/V2 均未以新权重执行——G7 链路证据止于检测契约面」。Handoff `:47` 亦列为 **NOT_RUN**。被引证据 `export-smoke-v2.json:66-87/150-170` 的 detect 步骤只产出 `DetectionResult`（candidates/class_filter/coordinate_space），**没有任何翻译链调用记录**；T3 的 36 格同样止于 detect。
- 即：判 PASS 的三条硬判据中，③「下游新增故障=0」**没有执行证据**，②「下游输入契约合法」也只验到 DetectionResult 面。
- 报告确实如实披露（§4.7 执行边界、§6-5 证据边界、§7.4-① T4 补证项），所以说谎谈不上；但**门判定的严格性**上，在冻结定义未按 §5.3 追加不回溯版本段的情况下，G7 不能维持「双候选 PASS」的无条件表述。
- **裁定**：G7 只能是「**PASS（条件性：T4 补证前置）**」或「INDETERMINATE-证据边界」；若编排/用户认为冻结口径的「沿 T0/V2 冒烟方式」一句已把边界锁定在检测契约面，须由**编排/Reviewer 出具显式裁决并写入 Task `review_events`**（§5.3 禁止回溯改定义）。此项不影响候选结论（v2a/v2b 同受影响，v2b 由 G1/G2/G5/G8 定资格）。

### Q2 · G5-① 收编 V2 当轮证据是否与 §4.G5 矛盾？——**不矛盾，收编合法**

- §4.G5 阈值依据原文即写「T0 §5…、V1 §3、V2 §3（两版 sha_gate.fired 先证+EXIT=0）——**三轮全过，正式门原样收编**」（`gate-definition.md:100`），并允许 AC4 使用「T3 轮如重训则含新产物」的候选集。定义自身授权了「收编」。
- 收编物与被测物**同字节**：`export-smoke-v2.json:5/:11` 的 v2a/v2b onnx sha（`27d162e9…`/`944e8114…`）与 `eval-matrix.json:17/:24` T3 被测 sha 逐字相同，故该证据是关于**本轮同一批工件**的机制验证，不是异批引用。
- 唯一需澄清处：T3 当轮脚本 `eval_gate_t3.py:477-487` 执行的其实是「盘上权重 sha 先验比对」，与①「外来 onnx 按生产 pin 加载被 PROVIDER_FAILED 拒跑」**不同型**；报告 §4.5-1 已如实点明，未冒充。
- **裁定**：合规、非阻断。建议 T4 部署前以 V2 同款冒烟复跑一次①（成本≈1 条命令），并在 §4.5-1 补一句「收编证据的 sha 与被测 sha 逐字相同」作为收编合法性依据（当前报告未写明该依据，容易被读成跨批引用）。

### Q3 · AC3 非派生 GT 的仲裁物证链是否够硬（G2-B 硬判据载体）？——**数据可用但档案不足，须补独立仲裁记录**

- AC2（BJ）有独占仲裁记录：`training_data/sfx-v1/annotate-r4/judgments/arbiter/batch-1.json`（6 单元，逐单元 verdict + rationale），`stage_r4_manifest.py:52/67-68` 还会断言其与 divergence status/xyxy 一致。
- AC3（npd，51 个分歧单元）**没有对应文件**：glob `training_data/sfx-v1/gate-t3/**` 无 `arbiter/` 目录；全仓 grep `R4-pre-k01-D00` 只命中 `finalize_npd.py:34/91/146`（仲裁终裁表 + rationale **硬编码在作者脚本内**）、脚本回写的 `divergence.json` 与三份 eval raw。
- 且 `npd-judgments/divergence.json:1050` 的 `"arbiter": "…；arbiter/batch-1.json"` 指向的是**不存在的路径**（该名字下存在的是 AC2 的 BJ 批次，只含 BJ33/35/36 共 6 单元）。
- 后果：`verify_data_integrity.py` S7「135 框逐框可溯」断言的对象（`divergence.json` + `npd-gt.json`）与仲裁表**同一产者**（`finalize_npd.py`），属构造性自洽而非独立复核；这不使数据无效（双 AI 独立标注、`consensus.json` 的 `iou_ab` min 0.5033/max 0.9893 证明无逐位重合、交集/差集统计真实），但「第三方仲裁」这一环的物证强度明显低于 AC2。
- **裁定**：**不判 G2-B 数据无效**（报告 §6-2 已把 ai-consensus 标注质量层误差如实登记，且 G2-B 是同一 GT 下的相对不回退比较，对该层误差较不敏感）；但必须补一项条件：把 51 单元终裁从脚本常量导出为 `gate-t3/npd-judgments/arbiter/batch-1.json`（与 AC2 同构），`finalize_npd.py` 改为读取该文件并断言，修正 divergence.json 指针，然后重跑 `finalize_npd.py` + `verify_data_integrity.py`。

---

## 4. 发现清单

### P1

**P1-1 · G7 判定标签与冻结 §4.G7 阈值③不符**
- 位置：`verification/M2-SFX-GATE-T3/gate-t3-report.md:18`（速览「双候选 PASS」）、`:135-143`（§4.7）、`:184`（§6-5）；`gate-definition.md:117-119`（口径/阈值③）。
- 证据：§4.7 自述翻译链深层调用「T3 当轮与 T0/V2 均未以新权重执行」；`doc/handoffs/M2-SFX-GATE-T3-zcode-20261005.md:47` 列 NOT_RUN；被引 `export-smoke-v2.json` 无译链调用记录。
- 处置：改标「PASS（条件性，T4 补证前置）」/ INDETERMINATE-证据边界 + 在 Task/Handoff 显式登记；或编排依 §5.3 出显式口径裁决（见 Q1）。建议 Owner=ZCode 改文档，裁决=编排/用户。

### P2

**P2-1 · AC3 仲裁无独立产物 + `arbiter/batch-1.json` 悬空指针 + 终裁表硬编码**
- 位置：`training_data/sfx-v1/gate-t3/npd-judgments/divergence.json:1050`；`experiments/M2-SFX-GATE-T3/finalize_npd.py:32-88`（VERDICTS/RATIONALES）、`:187-189`（写入 arbiter 字段）；对照 `training_data/sfx-v1/annotate-r4/judgments/arbiter/batch-1.json`（仅 6 个 BJ 单元）。
- 处置：补 `gate-t3/npd-judgments/arbiter/batch-1.json`（51 单元）+ `finalize_npd.py` 改为读取断言 + 修正指针；重跑后确认 `data-integrity-asserts.json` 与提交版逐位一致。

**P2-2 · challenge 结构 5 框→8 框（pre-bj32）未走 §5.2 变更登记，与「考卷…本轮零改动」措辞冲突**
- 位置：`gate-definition.md:76`（§4.G3 评测数据「考卷 vol05 组定义（Task 禁止范围——本轮零改动）」）；`doc/tasks/M2-SFX-GATE-T3.md:58`（禁止范围「考卷 vol05 组定义」）；`data-integrity-asserts.json:28-35`（S4 members=pre-bj17/18/**bj32**、boxes=**8**）；`prepare-train-v4-summary.json:39/184`。
- 证据：`eval_gate_t3.py:271-273` 断言 challenge=`["pre-bj17","pre-bj18","pre-bj32"]`。硬判据未受影响（G1 判据集冻结为原始 5 框，S4 `original_5box_bitwise_r2=true`），但 held-out 集合构成确实从 2 页 5 框变为 3 页 8 框，仅在 gitignored 数据摘要 + 报告 §2.1/§4.4 记录，未按 §5.2 追加「变更登记」并由非作者确认。
- 处置：在 `gate-definition.md` §6 追加**不回溯**版本行（v1.1：challenge 成员随 vol05 组转正扩展至 3 页 8 框；G1 判据集仍为原始 5 框），请 DSH 确认；或由编排在 Task 裁定「§4.G1 已预见、无需登记」并留痕。

**P2-3 · §5「复核记录」未标「作者侧」，其②的「独立脚本重算」无落盘脚本**
- 位置：`gate-t3-report.md:162-166`（②：「npd n=106 min 0.5033/max 0.9893，逐位相同=0；标注坐标 100% 整数 vs 模型 preds 整数占比 12.8%」）。
- 证据：全仓 grep `experiments/M2-SFX-GATE-T3` 无 `12.8`/`0.5033`/「整数」命中（仅 `finalize_npd.py:259` 的 coincidence_evidence）。min/max IoU 可在 `npd-judgments/consensus.json` 直验（1151 行 0.5033、1177 行 0.9893，max<1.0 即「无逐位重合」成立）；但「preds 整数占比 12.8%」所需未舍入坐标不在任何落盘产物（raw 只保留 `round(v,1)`），**不可复算**。
- 处置：按 V1/V2/KO-TILE 先例改称「作者侧复核（workflow 内 phase 5）」；把可复算部分落成脚本（如 `verify_annotation_independence.py`），删除或标注不可复算的 12.8%。

### P3

**P3-1 · G5-① 收编与 T3 当轮断言非同型**：`gate-t3-report.md:120` 已披露；建议 T4 复跑一次 PROVIDER_FAILED 反向验证，并补注「收编证据 sha 与被测 sha 逐字相同」（见 Q2）。

**P3-2 · G2-①「口径合规断言在位」实为代码常量+统计值**：`gate-t3-report.md:80` 列 `eval_gate_t3.py:104-106/218-226/194-215/428-429`，核验属实（我已逐行核对常量与实现），但脚本内**无运行期 assert**（无 tile 数/步长/锚点断言），`recompute_eval_t3.py` 只复算匹配与聚合、不复算 tile 参数。建议 T4/后续轮补 assert 或独立复算。

**P3-3 · G8-4 credit 义务判定过窄**：`gate-t3-report.md:156` 称 credit「仅在『使用 MangaSeg images or derived visual results』时触发——本项目不使用，未触发」；但 `b-base-readme-snapshot.md:91` 明示「If you use the model, its training data, or derived results, cite the MangaSeg paper」。引用义务已登记为备案项 ✓，建议将 credit 也改为**保守登记（若未来公布衍生权重/结果则触发）**，避免「未触发」被读成已免除。

**P3-4 · §8 证据索引漏列脚本**：`gate-t3-report.md:220` 列 7 个脚本，实际 `experiments/M2-SFX-GATE-T3/` 为 8 个（漏 `arb_previews_npd.py`，即仲裁预览生成器——恰是 AC3 仲裁过程的唯一工作产物生成者）。

**P3-5 · 「26 文件」与交付 head 不一致**：`doc/tasks/M2-SFX-GATE-T3.md:50/:71`、`handoff:20` 称 26 文件（1 doc + 8 experiments + 17 verification，对应 HEAD=2e95760a）。盘上本轮交付（e53a2629）实际为 **28** 个：verification 18（4 顶层 + `gate-t3-report.md` + 13 raw）+ experiments 8 + doc/tasks 1 + handoff 1。建议改述「26（HEAD=2e95760a）+2 docs（AC5）」。

### P4

**P4-1 · 「坐标逐位=R2 出厂」实为 round(v,1) 等值**：`verify_data_integrity.py:92-93`、`eval_gate_t3.py:286-288` 均为 `[[round(v,1)…]]` 比较；建议改述「逐值（0.1 精度）」。

**P4-2 · 提交脚本内遗留开发期注释**：`prepare_dataset_v4.py:72`「期望分集（页, 框）：train 904+12=916? 核算：…」——数值实为自洽（904+3 页/+12 框→907/2323，challenge 2+1 页→8 框，916 全量），但注释形态不应入册。

**P4-3 · 同一证据两种行号引用**：`handoff:30` 写 `export-smoke-v2.json:38-45/122-127`，`gate-t3-report.md:120` 写 `:38-43`；建议统一到实际证据行（sha_gate.fired = 38-43/122-127，sha_gate.ok = 44-50/128-134）。

**P4-4 · coincidence_evidence 单向表述**：`training_data/sfx-v1/gate-t3/npd-gt.json:9` 把「a 框与 R2 派生框 IoU≈0.92 独立重合」仅登记为「客观性旁证」；同一事实也可读作泄漏信号（决定性仍是作者自查字段 `task_brief_leak_check=PASS`）。建议登记为「双向解释、决定性不足，仅作旁证」。

---

## 5. 逐 AC 结论

| AC | 结论 | 依据与保留 |
|---|---|---|
| **AC1** Gate 定义冻结 | **PASS（附 P2-2/P4 措辞项）** | `gate-definition.md` 164 行、五节齐备：逐门定义/评测数据/口径/阈值/判定规则 + §5 冻结与变更登记 + §6 版本表 + §7 证据索引；G1/G7/G8 对齐提案语境、G2-G6 权威化并给出 §2 门数登记理由；行号引用 `detection_sfx.py:107-138` 全对。保留：§4.G3「考卷…本轮零改动」措辞与实测 8 框/3 页不符（P2-2）；§4.G7 口径内部张力（「沿 T0/V2 冒烟方式」vs「流入翻译链入口」）是 P1-1 的根因，建议在 v1.1 中显式界定。 |
| **AC2** R3-MISS 补画入册 | **PASS** | 盘上逐值核对：a=13/b=17/matched=12/only_a=1/only_b=5 ✓；终裁 15 框 = 12 consensus union + 3 arbiter keep（BJ32/33/34/35 = 3/3/3/6）✓；BJ36（a0/b2 双 delete）/BJ37（a0/b0）0 框如实、pseudo 留痕有 schema 先例；`ai-direct-annotation` 新口径 + `conf=null` + `human_review=false` 登记完整；`drawing 隔离`为双 AI 独立+第三方仲裁（`annotate-r4/judgments/arbiter/batch-1.json` 在位，6 单元含 a/b 两侧各被 delete/keep，非单侧裁决）。ask「BJ26-37 钉 train」与组隔离冲突按 §4.G1 处理并登记（BJ32→challenge）——处置可接受，但请编排显式 ack（见下一步）。 |
| **AC3** KO 非派生 + train-v4 | **PASS（附 P2-1 条件）** | npd 定稿 135 框（106 consensus + 29 arbitrated kept；removed 22）与 per_page 逐值一致；隔离旁证（IoU 连续、无 IoU=1.0）可直验；与派生 56 框交集 40/差集 16+95 与 S9 复算一致；train-v4 916 全量、指纹 `6bb0ea13…`、组隔离 0 违例、考卷 5 框逐位、期望分集 907/2323、4/53、2/5、3/8 全部对得上，9 断言落盘。保留：P2-1 仲裁物证链。 |
| **AC4** 三方×四数据集评测执行 | **PASS** | 12 raw JSON + run-full.log + eval-matrix 的 36 格与报告 §3 表逐值一致；tile 参数/实现与 KO-TILE 冻结口径一致且复现其 chiqui7/v2b 参考值**逐位相同**；letterbox 对照 12 格全 0 复现结构性事实；进程内重指 + finally 恢复（`:509-519/:529-531/:711-712`）+ chiqui7 pin 原样（sha 先验断言）纪律正确；宽/严 conf 双口径落盘。未复跑（shell 不可用）——作者自证的 `ALL CELLS RECOMPUTED` 未由我独立复现，但静态逐值核对未发现矛盾。 |
| **AC5** 逐门判定 + T4 终稿 | **approved_with_conditions** | G1/G2/G3 判定严格符合 §4 冻结语义且用 T3 当轮实测值（0.8333 / 0.3037 均为本轮值），FAIL 如实（v2a R 达线 P 不达线→FAIL；v2a KO-B 0.2593<0.3037→FAIL）；G4/G6 directional 登记齐（含「考卷对新回填形态零覆盖」原样入表、own-manga 418 不同权、低功效、循环性四层归因）；G8 v2b 7/7 出证、许可审计三项（Manga109-s 声明逐字在位 README:85、未分发范围、登记义务）到位；T4 四件（切换候选/许可结算/tile 化方案+性能 17–81 s 裁决前置/回退）齐。保留：**P1-1（G7）**、P2-1、P2-3、P3-3。 |
| **AC6** 零 src | **PASS（静态可核部分）** | `detection_sfx.py` pin `d87389af…` 现值在位、无候选权重写入；8 scripts + 18 verification + 2 docs 全落在 Task 允许路径（`experiments/M2-SFX-GATE-T3/**`、`verification/M2-SFX-GATE-T3/**`、Task/Handoff）；数据本体在 `training_data/`（`.gitignore:13` 命中）。**未能验证**：`git diff 87ca8724..e53a2629` 的 26/28 文件清单与禁止路径 diff=0、pin base..HEAD 逐字一致——属 shell 不可用导致的验证缺口，非发现异常；「26 文件」数字本身陈旧（P3-5）。 |

---

## 6. 推荐下一步

**Owner（ZCode，条件闭合；不重跑评测即可完成）**
1. `verification/M2-SFX-GATE-T3/gate-t3-report.md`：§0 表 + §4.7 + §7.4-① 将 G7 改标「PASS（条件性：T4 补证前置）」或（若编排裁决）「INDETERMINATE-证据边界」；§5 标题/首句加「作者侧复核」；§8 补 `arb_previews_npd.py`；§4.5-1 补「收编证据 sha 与被测 sha 逐字相同」。
2. 新建 `training_data/sfx-v1/gate-t3/npd-judgments/arbiter/batch-1.json`（51 单元 verdict+rationale，自 `finalize_npd.py:32-142` 常量原样导出）→ 改 `finalize_npd.py` 为读取该文件并断言（对齐 `stage_r4_manifest.py:52/67-68` 模式）→ 修正 `npd-judgments/divergence.json:1050` 指针 → 重跑 `python experiments/M2-SFX-GATE-T3/finalize_npd.py` 与 `python experiments/M2-SFX-GATE-T3/verify_data_integrity.py`，确认 `data-integrity-asserts.json` 与提交版逐位一致。
3. `doc/tasks/M2-SFX-GATE-T3.md:50/:71`、`doc/handoffs/…:20`：把「26 文件」改述为「26（HEAD=2e95760a）+2 docs（AC5）」。
4. 若采纳 P2-2：在 `gate-definition.md` §6 追加 **v1.1（仅追加、不回溯）** 版本行——「challenge 成员随 vol05 组转正扩展为 pre-bj17/18/32 三页 8 框；G1 判据集仍为原始 5 框」——并请 DSH 确认。
5. 顺手清理：`prepare_dataset_v4.py:72` 遗留注释；把「逐位=R2 出厂」统一为「逐值（0.1 精度）」。

**Integrator（编排会话代行 Codex）**
1. 就 Q1 出显式裁决并写入 Task `review_events`：接受「G7 冻结口径边界=检测契约面」→ 则要求报告改标条件性 PASS + T4 补证作为部署前置；不接受 → G7 维持带补证义务的未终判状态，T4 前不得把 G7 记为已过。
2. 确认 ask「own/synthetic/BJ26-37 钉 train」与 gate-definition §4.G1 组隔离优先的冲突处置（BJ32 入 challenge、BJ33-35 入 train、BJ36/37 零框留底册），在 Task 中留痕（当前仅登记于 `prepare-train-v4-summary.json` 与报告 §2.1）。
3. T3 集成后将 26/28 文件清单与 `pin base..HEAD 逐字一致` 的 git 实测补进集成记录（本 Review 因 shell 不可用未复核）；释放 T4 时把「PROVIDER_FAILED 反向验证复跑」与「BJ06 型 policy=translate 端到端补证」写成 T4 的完成 Gate。

**用户**
1. 裁决 v2b（`944e8114…`）切换与否——门判定支持下的裁决点，附带条件如实：KO 域切换零改善（letterbox 结构性全零，tile 化才是前置）、bj-ext 泛化未证超越基线、收益量级=考卷零误检 +1 框 + KO 非派生 +0.052（低功效）。
2. 裁决 KO tile 化性能预算（实测 17–81 s/页 @CPUExecutionProvider，58–112 tiles/页）。
3. 确认「翻译链深层端到端冒烟」是否作为切换前置（即 Q1 是否升格为硬补证）。

**复现命令（供 T4/异机复核，需先在位数据）**
```
python experiments/M2-SFX-GATE-T3/verify_data_integrity.py
python experiments/M2-SFX-GATE-T3/recompute_eval_t3.py
git diff --name-only 87ca8724..e53a2629     # 期望 28 文件且全在允许路径
```
（本轮我三项均未能执行：pwsh 沙箱 `grantWrite` 失败 + 无审批通道。）
