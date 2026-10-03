我已完成静态审查（只读，未修改任何文件；沙箱无法执行命令，所有运行级结论均为对 `raw/` 日志与 JSON 的静态核对，未复跑）。

# M2-REGION-OVERLAP-ARBITRATION 独立 Review（Reviewer=DeepSeek Harness，非作者）

## Verdict

**changes_requested**

理由（三条，均为交付层面而非实现工艺层面）：

1. **AC2（合同自标"核心验收"）字面未达成，且 Task 目标段的"可观察交付"落空。** 合同 AC2 要求「BJ13 误路由 case … 在仲裁后红转绿——原 SPEECH 乱译路径不再发生」；Task 来源与目标段要求「可观察交付：BJ13 误路由 case 在全链 rerun 中不再产生 speech 乱译渲染」。交付的真实双 provider rerun 证明该路径**仍然发生**（`manga-1`/`manga-3` 仍以 SPEECH 前缀进对话链，仲裁 relabels=None），且 Handoff 风险 1 自承「本仲裁对当前生产权重下的 BJ13 误路由乱译损害**无直接缓解**」。即：本 Task 的净生产效果对原始损害为零。
2. **AC2 的替代口径未经授权，且替代证据不成立。** 把 AC2 从「场景级红转绿」降级为「合成近重复形态闭环 + 不可达登记」是验收标准的实质变更；合同只授权 AC1 的**提案**经 DSH review 确认，未授权变更 AC2；用户裁决③授权的是"重叠仲裁契约"，未授权"接受 BJ13 不闭合"。更关键的是替代证据本身：口径 B 把 sfx 框构造成与 primary 同心、0.95 线性缩放（`experiments/.../arbitrate_bj13.py:364`），得 IoU=(0.95²)/(2−0.95²)=**0.9025**，仅高出冻结阈值 **0.0025**——它验证的是「实现会按阈值改标」这一同义反复（tautology），与「BJ13 形态是否被覆盖」无逻辑关联。
3. **AC3 的 KO 域零变化要求完全无证据、亦未登记。** 合同 AC3 明文「KO 既有 qualification case 检测 region 计数与全链产物零变化」，风险①更把「BJ06+**KO** 对照回归」指定为 precision 损害的缓解手段。但 `arbitration-report.md`、Handoff、Task 测试要求表、`raw/` **全文零处提及 KO**（已 grep 确认），也未在 §8 Known limitations 登记为"未测"。KO 恰是 sfx 信号最强的域（DETECT-EVAL：sfx 类 11/29），是 0.90 阈值安全性最关键的反证面，缺失它使"零变化"结论仅立于 BJ06 单页。

**但须明确区分**：不可达性论证本身成立（见下），实现工艺质量高（零回归、AC1/AC4/AC5 达标、证据链大部分可手工溯源）。因此本 changes_requested **不要求 ZCode 重写实现**，返修主体是**合同层裁定 + KO 证据补齐**。

---

## 发现清单

### P0
无。（无用户数据/契约/源文件破坏；无静默失败；违约面已在报告 §8 部分登记。）

### P1

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P1-1 | `doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md` AC2 / L25 目标段；`arbitration-report.md` §0/§2 | AC2 字面验收与 Task"可观察交付"均未达成：BJ13 乱译路径在真实 rerun 中仍在，仲裁对其零作用。报告 §0 以 DELIVERED 表述该 AC，实际是"目标不可达 + 登记"。 | 由 Codex/用户二选一裁决：(a) 正式把 AC2 修订为「结构性不可达（typed 诊断登记）+ 近重复双检出形态闭环」，并在 Task 依赖链上写明"本仲裁在 sfx 召回恢复前为 no-op"；(b) 若坚持 AC2 字面，判本 Task 目标在当前约束下不可达，关闭/重置并把投入重定向到 ⑤ UI 缓解。裁决前 Task 不得进 done。 |
| P1-2 | Task AC3 L31、风险① L59；`arbitration-report.md` §3（无 KO 段）；Handoff 验证表 | AC3 的 KO 零变化**无任何运行证据且未登记为未测**。KO 域 sfx 候选与 primary 候选高度共存，是本规则最可能触发之处；若 KO 存在 sfx×speech IoU≥0.90 对，真对白会被改标为 SFX → SKIP → 用户可见漏译。 | 补 KO qualification rerun（off/on 逐位对照），或至少跑 KO 域 sfx×primary IoU 上界扫描；若确实不跑，必须在 report §8 显式登记"KO 未测"并由集成方书面接受。若 KO 实测出现 ≥0.90 对，升级 P0 并回退/加第二道门。 |
| P1-3 | `experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py:356-377`；`arbitration-report.md` §2.2 口径 B | 绿态证据为阈值边缘自证输入（IoU≈0.9025 vs 阈 0.90，余量 0.0025；且为同心缩放的**最优情形**，真实双检出必带位移）。不能作为 AC2 场景级红转绿的替代。 | 把 §2.2/§0 的"绿态闭环"改述为"实现路径验证（代码级）"；AC2 的真实发生面据实登记为"0.90+ 形态至今 0 观测"。 |

### P2

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `src/bootstrap/core_assembly.py:1041-1045`；`src/application/translation/context/gate.py:32-42`；report §1.3/§2.2 | 「改标即闭合乱译」依赖 `settings.sfx.policy=skip`。域默认确为 SKIP，但 **qual-BJ06 实测 8 个 sfx region 全是 `sfx_policy="translate"`**（`qual-BJ06.json:1033-1124`）。translate 配置下改标仅把 region 从对话链换成 SFX 翻译链，仍 OCR→仍翻译→仍渲染，损害是否消除取决于 SFX 链质量，未验证。报告以"（默认 SKIP）"一笔带过，未登记该条件敏感性。 | 在 report/Handoff 显式登记：AC2 绿态的成立条件 = `sfx.policy=skip`；translate 配置下的行为差异与残余损害未评估。 |
| P2-2 | `src/infrastructure/providers/detection_sfx.py:734-757`；report §8.3 | 单向规则**只有 IoU 一道门**，无 sfx confidence 门/一致性门。反向风险（sfx 通道误检真对白框 → 真对白被改标 → SKIP → 漏译）仅以"至今 0 观测"背书；"0 观测"是样本事实，不是阈值域排除——这在逻辑上无法由 0.90 保证。AC4 的 fail-closed 只覆盖 env 解析，不覆盖语义误判方向。 | 评估第二道门（如 `sfx.confidence ≥ primary.confidence` 或 sfx conf 下限、或要求 sfx 框区域内主检测无文本证据），并在 report 中把该风险从"理论/未观测"提升为量化边界。 |
| P2-3 | `raw/arbitrate-manifest.json:64-72`；report §1.3 | 口径 B 下改标候选与原 sfx 候选**同位置并存**：labels 为 `sfx-arb-manga-1/2/3 + sfx-1 + sfx-near1/2/3`，6 个候选挤在 3 个位置。SKIP 下无害，translate 下会重复翻译/重复重绘。AC1 允许"改标/抑制"两种语义，但选型理由（§1.3）未评估"同位置双 SFX region"的下游副作用。 | 补选型论证：说明为何不抑制其一，或登记为已知副作用 + 未来去重切片。 |
| P2-4 | report §1.4 表格；`detection_sfx.py:196-197` | 0.90 相对域内最高 0.8862 的 margin 仅 **0.0138**，且域内实测 3 对相交中有 2 对是"sfx 完全内含于 speech"形态（IoU = 面积比，我手工复核：0.870 = 106764/122715、0.728 = 132132/181560，与报告完全吻合）。该形态下只要 sfx 框面积 ≥ speech 框 90% 即触发——同一页重跑或权重微变更即可跨越。margin 的鲁棒性未论证，且 0.90 恰好落在实测分布尾部。 | 补 margin 依据（跨页/跨域分位数）或引入第二道门；至少在 §8 登记"0.0138 margin + 内含形态"的敏感性。 |
| P2-5 | report §1.4（BJ06 生产 region bbox 口径 0.8862 vs BJ13 **目检参照框**口径 0.5501） | 结构性定案是**跨口径比较**（一端真实 sfx region，另一端人工参照框，因 BJ13 生产 sfx 候选为零）。量级结论成立且方向正确，但未在同口径（合成召回候选 → 真实 region）下重算，结论强度受参照框 ±10-20px 约束。报告在 §8.4 只以"不影响量级判定"带过。 | 明确标注该论证的跨口径性质与不确定性方向（真实框可能更贴合 → BJ13 IoU 可能上移，但需 >0.886 才改变结论）；或补一次同口径重算。 |

### P3

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P3-1 | `raw/pytest-three-suites.log`（57 行，止于 QML 噪声） | 声称的 `EXIT=0` 在落盘日志中**无显式记录**；仅能从"627 passed, 1 skipped"且无 failed 行推定。 | 落盘时显式追加退出码（或在 Handoff 注明"EXIT 由 pytest summary 推定"）。 |
| P3-2 | report §5、§8.7 | detect options 新增 2-4 个键（`sfx_arbitration*`）的 **wire 可达性未审计**：未证明这些 options 不进 IPC payload / DB / 客户端 schema 校验，仅以"套件全绿"背书"非 wire 契约"。 | 补一次 options 消费方审计（option → handler → step record / IPC 的路径），或在报告中明确其存储面。 |
| P3-3 | report §3.2 环境注记；`raw/pytest-t111-py312.log:339` | GPU venv 口径记"6 failed/619 passed"，实际日志为 `6 failed, 619 passed, 2 skipped`，且未列 6 个失败名逐项证明"与本 Task 无关"；另 619 vs 627 差 8、skipped 2 vs 1 的 collect 差异未解释。 | 列出 6 个失败名与失败原因分类，解释 collect 差异。 |
| P3-4 | report §1.4 末行（chiqui7 text 框 × ogkalu speech 否决） | 否决理由只写"带交叠 + 语义不通"；量化上 BJ06 上界 0.821 vs BJ13 下界 0.830，分离带仅 **0.009**，远小于参照框 ±10-20px 不确定度。语义理由（双 text 一致不构成 sfx 证据）成立，但量化脆弱性未点明。 | 补"分离带 0.009 在标注不确定度内"作为该信号被否决的量化理由。 |

### P4

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P4-1 | `detection_sfx.py:737` | `arbitratedRoute` 用 camelCase，违反仓库 snake_case 风格。 | 改 `arbitrated_candidates`。 |
| P4-2 | `experiments/.../arbitrate_bj13.py:154-163, 378` | `_ReplaySfx.__init__(result, extra)` 的 `extra` 参数存而不用（`detect` 返回 `self.result`，死参数）；line 378 直接 `replayed.sfx = ...` 就地改写 provider 属性。 | 删 `extra` 参数；把两次口径做成两个 provider 实例。 |
| P4-3 | Task L54「14 仲裁测试」；Handoff L17/L35「14 仲裁用例」；report L94「14」vs L116「15 个仲裁用例」 | 用例计数措辞不一。实际：`test_detection_sfx.py` 共 15 个仲裁用例（14 红 + 1 绿 `test_arbitration_degraded_sfx_provider_skips_arbitration`），加 `test_sfx_assembly.py` 的 `sfx-arb-` 矩阵行共 **16** 新增（与 627−611=16 吻合）。 | 统一为"15 用例（14 红 + 1 绿）+ 1 矩阵行 = 16 新增"。 |
| P4-4 | `experiments/.../arbitrate_bj13.py:243`；report §8.6 | `best_primary_label` 零相交时填 `0.0` 而非 null（`best[0] and best[1]` 惯性），报告选择"登记"而非修脚本。 | 直接修为 `best[1] if best[0] > 0 else None`，避免下游 JSON 消费方类型混淆。 |

---

## 逐 AC 结论

- **AC1 — PASS**：层位选型（provider 拼接层）论证充分（§1.1 五条理由：两端候选唯一共视点、零契约面、降级路径天然隔离、provenance 先例）；度量 bbox IoU 与上游证据同口径；阈值 0.90 依据可溯源——**我手工复核 BJ06 域内 3 对相交全部吻合报告数字**（0.8862 = 85715/96720（sfx 2eeaa2c4 × speech 5b76a907）、0.870 = 106764/122715、0.728 = 132132/181560）；规则 directional 描述清晰。仅 P2-4/P3-4 的 margin 与信号量化需补强。
- **AC2 — FAIL**：红态真实对位成立（我逐位核对 rerun `manga-1`(2124.1,257.5,2493.9,1270.9) = qual region#1 `ffed29e8`(2124,258,370,1013)、`manga-3`(471.8,2668.2,780.1,3669.6) = region#3 `de83b0c4`(472,2668,308,1002)，亚像素级吻合）；BJ15 零相交登记成立；但 BJ13 **未红转绿**，替代绿态为阈值边缘自证（P1-3），口径变更未授权（P1-1）。
- **AC3 — PARTIAL**：BJ06 off/on 逐位一致（脚本 `_fingerprint` 逻辑正确 + manifest `bit_identical_candidates=true`）、rerun 与 qual 17=17 对位、三套件 627+1sk（日志核实，算术 627−611=16 与"15 用例+1 矩阵行"吻合，**自洽**）均达标；**KO 零变化完全缺失（P1-2）**。
- **AC4 — PASS**：`_arbitration_config()` 在 `detect` 入口、primary 推理前调用（`detection_sfx.py:695`），非法值 `ValueError` naming the variable；空串/未知词/非数字/0/1.5/负数 7 组参数化 + "primary 未被调用"探针（`_ProbePrimary` 抛 AssertionError）齐备；`nan`/`inf` 亦被 `not 0.0 < x <= 1.0` 拒绝，健壮；不可达形态 typed 可诊断（`sfx_arbitration_partial_overlap`，代码分支 `elif max_partial > 0.0` 与 BJ13 raw 的"有 sfx 候选但零相交 → 字段缺席"一致）。
- **AC5 — PASS**（含 P3-2 注记）：`core_assembly._detected_region_type` 逐字未改（`startswith(SFX_LABEL_PREFIX)`，`sfx-arb-manga-3` 天然落入 SFX）、`region_creator` 五参签名未动、`doc/contracts/**` 无任何仲裁字样（grep 确认）、未触发停等。options 新增键的 wire 可达性建议补审计。

---

## 对重点问题 1 的明确裁定

**裁定：AC2 判 FAIL，属 changes_requested 级；但这是"合同未达成 + 验收降级未授权"，不是"实现缺陷"。**

三层依据：

1. **事实层（客观未达成）**：AC2 与 Task 目标段要求的是**可观察的损害消除**（BJ13 乱译路径不再发生）。真实 rerun 证明该路径仍在，仲裁对现状零作用，Handoff 自承"无直接缓解"。这不是口径之争，是交付物是否产生了它声称的产品效果。

2. **证据层（替代证据不成立）**：口径 B 的输入被构造成 IoU≈0.9025（阈 0.90 +0.0025，同心缩放最优情形），它只能证明"实现按阈值改标"这一代码事实——用「IoU≥0.9 的合成输入」验证「IoU≥0.9 会改标」是同义反复。真正的场景级证据（0.90+ 的真实双 provider 双检出实例）**至今 0 观测**（report §8.3 自承）。因此"绿态闭环"只能支撑"实现路径正确"，无法替代 AC2 的场景验收。

3. **程序层（降级未授权）**：把 AC2 从"红转绿"改写为"不可达登记 + 形态级闭环"，是验收标准的实质降级，须 Codex/用户裁决。Worker 在 claim/实施阶段就应基于上游已明示的依赖（`diagnosis-and-options.md` §4 交叉要点："chiqui7 召回修复（①②③任一）后…乱译渲染损害不消失，重叠仲裁（sfx 框覆盖 speech region 时改标）属 region 创建语义变更"——即**重叠仲裁被上游定位为召回修复的配套件**，而非独立闭合手段）提交范围修订请求，而不是交付后期待 Review 追认。

**同时明确对作者有利的部分（不可达性论证成立，予以确认）**：在「纯几何 bbox IoU 单阈值 + sfx 单向驱动」的规则空间内，阈值的单调性使该规则**必然**二选一失败——阈值 ≤0.8862 则 BJ06「！！！」真对白（`5b76a907`）先被改标（违反 AC3），阈值 >0.5501 则不覆盖 BJ13。我已独立复核这两个数字的来源（`qual-BJ06.json:1019-1064` 与 `raw/arbitrate-pages.json:173-198`），计算无误。加上 BJ13 现状 sfx 候选为零（第一层不可达），结论"BJ13 在本 Task 约束下不可达"是正确的物理判断，而非偷工。报告对该结论的登记是诚实的，值得保留；问题只在于**它不能被追认为 AC2 的达成**。

**返修前置条件（满足任一即可推进）**：
- (a) Codex/用户正式修订 AC2 为「结构性不可达登记 + 形态级闭环」，并把"BJ13 误路由损害的自动化闭合"显式挂到 sfx 召回恢复 Task 的依赖链（写明本仲裁在召回恢复前为 no-op）；**且** ZCode 补齐 KO 零变化证据（P1-2）或由集成方书面接受"KO 未测"。
- (b) 集成方认定 AC2 字面为硬门 → 本 Task 应关闭/重置为"目标不可达"，投入转 ⑤ UI 缓解（M2-SFX-MISROUTE-UI-MITIGATION）。
- 在 (a)/(b) 决策前，Task 不得进 done；实现代码无需返工。

---

## 重点问题 2-6 答复

**问题 2（结构性定案证据链）**：
- 反向不可分离的**数字全部可溯源且我独立复核通过**：BJ06 域内最高 0.8862（生产 region bbox，sfx `2eeaa2c4`(1534,3517,223,395) × speech `5b76a907`(1540,3500,222,425) → inter 217×395 / union 96720 = 0.8862）；另两对 0.870、0.728 我亦手算吻合；BJ13 误路由 0.5501（ref2(420,2560,760,3400) × rerun `manga-3` → 210904.76/383426.86 = 0.5501）、0.4902（ref1 × `manga-1`，我算 0.4903，四舍五入边界差）。rerun 与上游 E2E 口径差异（0.452/0.544）也已在 §1.4 并列登记。
- **口径 A/B 划分清晰、无偷换**：A = 参照框当作召回恢复的 sfx 候选（诚实不可达，partial 0.5501）；B = 同心 0.95 缩放的合成近重复（构造绿态）。两者在 manifest 中字段分离、label 明确，未互相冒充。**唯一的偷换风险不在 A/B 之间，而在 B 被用来充当 AC2 的场景证据**（P1-3）。
- 弱点：主结论是跨口径比较（P2-5），且缺 KO 域分布（P1-2）。

**问题 3（0.90 冻结依据 + env 实现质量）**：
- 依据方向正确（域内最高 0.8862 之上是 AC3 约束下的最小可行阈值），**但充分性不足**：margin 仅 0.0138，且域内实测 2/3 相交对是"内含形"（IoU=面积比），该形态对框边缘极敏感；0.90 落在实测分布尾部而样本仅 1 页 72 对，未跨页/跨域校验（P2-4）。建议补分位数依据或第二道门。
- env 实现质量**好**：strip+lower 归一、空值走同一 typed 路径、`(0,1]` 闭开域严格、nan/inf 被拒、fail-fast 位置在 primary 之前（有专用探针锚定）、`off` 语义可逐位回到 pre-arbitration。唯一可挑的是 `_arbitration_config()` 每次 detect 重读环境变量（可接受，且是测试可注入性的代价）。

**问题 4（AC3 自洽性）**：算术自洽——627−611=16，与"`test_detection_sfx.py` 15 用例（14 红 + 1 绿）+ `test_sfx_assembly.py` 1 矩阵行"精确吻合（我从 red-phase log 的 `14 failed, 1 passed` 反推确认）；BJ06 off/on 17=17 的脚本逻辑（`_fingerprint` 全字段含 polygon 精确比较）正确，且 off 等价于 pre-arbitration 行为，故"on 未触发 ⇒ 与基线一致"的推理链成立。**不自洽处**：KO 条款未闭合（P1-2）；`EXIT=0` 无显式日志（P3-1）；用例计数措辞不一（P4-3）。

**问题 5（directional 单向性论证）**：
- "为什么 sfx 驱动而非 text 驱动"的论证**成立**：sfx provider 是 SFX 专用信号，其候选具有类别语义；反向（text 驱动）需要"主检测的 text 候选含 SFX 证据"这一前提，而主检测本身无 SFX 类，无法提供该证据。报告 §1.4 对唯一可替代信号（chiqui7 text 框 × ogkalu speech）的否决理由（"双 text 一致不构成 sfx 证据"）在语义上正确。
- **反向风险（text/真对白被误判为 sfx）未被阈值域排除**：0.90 只保证"BJ06 已观测的 3 对不触发"，不排除"chiqui7 对某页真对白产生高 conf sfx 误检且几何近乎重合"的形态。报告 §8.3 以"至今 0 观测"背书，属样本事实而非结构性保证；且规则无 sfx confidence 门/一致性门作第二道防线（P2-2）。附带量化脆弱性：域内已有 3 对相交、2 对为内含形，内含形下 sfx 框面积只要 ≥0.90× 对白框面积即触发——这不是"未来形态"，是当前形态分布的紧邻延伸。

**问题 6（范围纪律与 Handoff/Task 回填质量）**：
- **范围纪律好**：改动仅 `detection_sfx.py` + 2 个测试文件 + `experiments/` + `verification/` + Task/Handoff；未触 `handlers.py`、`core_assembly.py`、`doc/contracts/**`、`doc/STATUS.md`、`packaging/**`、`apps/**`、前端；未改权重/未触 OCR；experiments 脚本只读 import 生产代码（`_detected_region_type`、provider 类）。符合允许/禁止范围。
- **Handoff 质量好**：AC 对照逐条、验证证据表含命令/环境/commit/日志路径、下一任务建议完整（含可直接转发指令）、回退方法（revert 或 env off）、失败样例声明。Task 交付记录含 UI-MITIGATION 对齐注记且**未越权改写他人 Task 文件**（正确地把转写建议交 Codex），这一点尤其合规。
- **回填缺陷**：① KO 条款在 Task 测试要求表、report、Handoff 三处**一致缺失**（不是笔误，是系统性遗漏，P1-2）；② AC2 的 DELIVERED 表述与实际不符（P1-1）；③用例计数口径不一（P4-3）；④`EXIT=0` 无日志落点（P3-1）。

---

**只读声明**：本次审查未修改任何文件；沙箱无法执行命令，`git diff`/pytest/rerun 均**未复跑**，所有运行级声明为对 `raw/` 落盘证据的静态核对（IoU/算术为独立手算复核）。建议 verdict 文档落 `verification/M2-REGION-OVERLAP-ARBITRATION/`（Review 面），由集成方按 `doc/templates/REVIEW.md` 归档并回填 Task 的 Review 字段。

**推荐下一步**：由编排会话（代行 Codex）就 P1-1 的 (a)/(b) 二选一作出裁决，并指令 ZCode 在 1 个切片内补齐 P1-2 的 KO 零变化证据（或书面接受"KO 未测"）；两项完成前本 Task 保持 in_progress，不得进 done、不得集成。
