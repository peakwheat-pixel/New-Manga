## Verdict

**approved（可集成）** —— R1–R10 **全部 closed**（无降级处置、无越界、无新契约面）；返修未回潮 r1 的风险面（禁改路径零出现、MERGE_* 值与 docTR 行为零变化）。存在 **1 项新引入的 P3 文档死链（N1）**：Handoff 新增的「交付锚点记账」表把 release note 路径写错（指向 `doc/tasks/M2-PROD-DETECT-1/release-c8eefb4b.md`，实际在 `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`）。该表正是 R10 的产物、且会被集成记录直接引用，故要求**在集成修正 commit 内顺手改掉（doc-only，属允许路径，无需再开一轮返修）**；另有 3 项 P4 措辞/计数残留（N2–N4）可选闭合。

审查边界：全程静态、只读；`pwsh` 首次调用即被沙箱以 `SetNamedSecurityInfoW failed (Win32 5)` 拒绝（与 r1 同），此后未再尝试执行命令。我逐字比对了 review-fix.diff 的 8 个文件 `+` 侧与 worktree 现文件，**全部一致**，故该 diff 可作事实载体；diff 文件清单 = `doc/handoffs/M2-PROD-DETECT-1-d7faea39.md`、`doc/tasks/M2-PROD-DETECT-1.md`、`src/bootstrap/core_assembly.py`、`src/infrastructure/providers/detection_manga.py`、`tests/providers/test_detection_manga{,_real}.py`、`verification/M2-PROD-DETECT-1/{cleanstart-gate.json,envelope.md}`（8 文件）。

---

## R1-R10 逐条复核表

| 项 | 状态 | 依据（文件:行） |
|---|---|---|
| **R1[P2]** AC6 措辞 + 发布形态 slice 登记 | **closed** | `doc/tasks/M2-PROD-DETECT-1.md:41` 改为「**构建不回退 + ML 栈不进闭包**（…发布包内默认 manga backend 的 detect 会 `PROVIDER_DEPENDENCY_MISSING`…非回归）」；`doc/handoffs/…d7faea39.md:21` 同款口径 + `:80`① 登记；`verification/M2-PROD-DETECT-1/envelope.md:53` 明写「早期措辞（含新依赖）以本条为准」；Task`:90-92` + Handoff`:80`① 立「遗留 slice 候选」。全文已无未加限定的「含新依赖」主张（仅 `envelope.md:53` 以「已作废」形式引述旧措辞，属消歧、可接受） |
| **R2[P2]** GPU 对照口径注 | **closed** | `envelope.md:42` 新增：「C4 的 76.1 ms/页为**整轮 eval 循环**口径（含 PIL 解码、merge、计分、preview 落盘），**非纯推理**…二者不同域，**4.1× 仅作量级参考**」；与 `:43` 换算行、`:60`「不含 handler」自述一致，方向性说明（GPU 侧被压低→比值偏保守）保留 |
| **R3[P3]** 冻结守卫改身份 + 全量 hex | **closed** | `tests/providers/test_detection_manga.py:86-92` 四常数 `is`；`detection_doctr.py:67-74` 四值均为 **float**（0.7/8.0/8.0/6.0，不在小整数缓存域）→ 跨模块复制字面量必为新对象、`is` 为 False，**对 `from detection_doctr import MERGE_PAD_PX` 场景恒 True（正确）、对复制场景可捕获**；`:94-99` 保留元组 `==` 作次序断言（最坏退化到旧强度，不会更弱）。`:388-399` 三 pin 改全量 hex，与 `detection_manga.py:86/89/92` 逐字一致。附带一句实现依赖：身份断言依赖 CPython 不跨模块共享 float 常量这一事实（CPython 下成立） |
| **R4[P3]** real 测试 docstring 对齐实证 | **closed** | `test_detection_manga_real.py:49-53` 改引 envelope §AC3 实录：「on the real K01_R001 page (690x672, conf 0.5) … **2 text boxes** (scores 0.941 / 0.938) plus **2 dropped bubbles**」——与 `envelope.md:18` 逐字对应；断言仍为 `>= 1`（`:113`），未伪造强断言，引述错位已消除 |
| **R5[P3]** 缺配置消息加 backend 指引 | **closed** | `detection_manga.py:256-258` 追加「if `NEWMANGA_DETECTOR_WEIGHTS` still points at the docTR fast_base `.pt` file instead, set `NEWMANGA_DETECTOR_BACKEND=doctr`」；单测 `test_detection_manga.py:151-157` 以 `excinfo` 断言消息含 `NEWMANGA_DETECTOR_BACKEND=doctr`（与 `match="weights are not installed"` 并存，不破坏既有断言） |
| **R6[P3]** 权重 fetch/verify SOP 登记 | **closed** | `doc/tasks/M2-PROD-DETECT-1.md:93` + `Handoff:80`② 明确「本 Task 仅代码级 pin（三文件 SHA-256 常数在 detection_manga.py）；仓库内尚无 docTR 同款（`verification/T1.1.1/scripts/fetch_doctr_weights.py`）的 sanctioned 获取+校验路径」→ 后续 slice 补脚本或安装 SOP |
| **R7[P4]** 空串 env 边界差异登记 | **closed** | `core_assembly.py:702-708` 注释登记：空串 `NEWMANGA_DETECTOR_WEIGHTS` 走「override if override else default」回落默认，pre-Task docTR 装配 `os.environ.get(..., str(default))` 得 `Path("")`(cwd)，两者 detect 均 fail-closed，并声明这是与已发布行为**唯一**的 env 边界差异；与实现 `:728-737` 一字相符（保留回落语义，未改实现）。前 Task 原文本不在 worktree 内，该差异沿用 r1 已核 review-input.diff 的结论 |
| **R8[P4]** numpy/字体 skip | **closed** | `test_detection_manga.py:102/316/329/346` 四处 `pytest.importorskip("numpy", …)`，落点与 `detect()` 顺序（`_validate_request`→`_engine_or_raise`→`_frame_pixels`，`detection_manga.py:141-143`）精确对应：三个 request-validation 用例与六个 engine 用例都在 `_frame_pixels` 之前 fail-closed，故无需 skip；docstring `:4-9` 同步声明。`importorskip(..., reason=…)` 为文件内既有用法（`:186/:196/:214`，r1 基线 27 passed 已证可用），非新 API 面。real `:59-66` 字体缺失 `OSError`→`pytest.skip` 显式原因 |
| **R9[P4]** NaN 几何 typed | **closed** | `detection_manga.py:407-421` 于 clip（`:403-406`）之后、退化 skip（`:422`）之前对 x0/y0/x1/y1 四分量 `math.isfinite`，不满足即 `raise ProviderInvalidOutput(...)`（`import math` 见 `:49`）；**无新契约面**：类型为 `ports/providers/errors.py:129` 既有 `ProviderInvalidOutput`，其 `provider_id=`/`stage=` 关键字是基类既有签名（`errors.py:33-43`），`ports/**` 在返修 diff 中零出现（我确认 diff 8 文件清单无 ports 路径）。新增单测 `:265-279` 构造 `float("nan")` 首分量、`match="not finite"`，且 `:272` 前会先通过 `len(box)==4`/confidence 门（`:390-402`）——顺序正确可命中 |
| **R10[P4]** 锚点三值 / params 口径 / JSON 换行 | **closed** | `doc/tasks/M2-PROD-DETECT-1.md:16` `delivery_head: a016d38c`（与 Handoff`:32` 声明一致）；`Handoff:24-34` 三值表（release base `c8eefb4b` / branch base `2fee7d6e` / delivery_head `40d4ab64`→`a016d38c`）并注明差异来源，值可独立交叉核对（`release-c8eefb4b.md:5` release base=`c8eefb4b`；`Handoff:5` base_commit=`2fee7d6e`）；`envelope.md:21` params 口径注（42,733,137 加载后 tensor 元素计数 vs C4 `F32=42,861,209` 文件张量口径）；`cleanstart-gate.json` diff `:348-354` 仅移除 `\ No newline at end of file` 标记、其余全为 context，实际文件末行 `}`（ed 至 284 行）→ **内容零变化成立**。残余见 N1/N2 |

---

## 回潮与新问题

**N1 [P3]｜`doc/handoffs/M2-PROD-DETECT-1-d7faea39.md:28`｜新增锚点表内的 release note 路径为死链。** 该行写「见 `doc/tasks/M2-PROD-DETECT-1/release-c8eefb4b.md`」，但（a）`glob doc/tasks/M2-PROD-DETECT-1/**` 零命中、全仓 `release-*.md` 34 个文件**全部**位于 `verification/<TASK>/`（本 Task 为 `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`）；（b）`doc/STATUS.md:14` 用的正是正确路径 `../verification/M2-PROD-DETECT-1/release-c8eefb4b.md`；（c）release note 自身 `:5` 用 `../../doc/tasks/M2-PROD-DETECT-1.md` 反向引 Task，佐证其所在目录为 `verification/`。属本轮 R10 新写内容引入的事实错误（非 r1 遗留）。**要求集成修正 commit 内改为 `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`**（doc-only，允许路径）。三项锚点**值**本身正确，仅指针错误。

**N2 [P4]｜`Handoff:6` vs `Handoff:30/32`｜同一文件内 `delivery_head` 一名三义。** frontmatter `delivery_head: d7faea39…（实现；回填/记录 commit 见 Task frontmatter）`，而 R10 新表 `:30` 定义 `delivery_head=40d4ab64`、`:32` 前移为 `a016d38c`。虽有行内括注消歧，但 R10 的目标正是消除锚点歧义，建议把 frontmatter 字段改名为 `implementation_head`（或补「≠ Task frontmatter delivery_head」直注）。

**N3 [P4]｜`Handoff:16,19,41`｜实现期数字未随 review-fix 同步。** `:16` 称 detection_manga.py「418 行」（现文件 436 行）、`:19`/`:41` 称「27 项 / 27 passed」（Task`:72` review-fix 行已为 28）。`:41` 有 `@d7faea39` 锚定故历史可辩，但 `:16/:19` 为现在时表述；建议加一句「review-fix 后 436 行 / 28 项」或在两处挂指针。

**N4 [P4]｜`detection_manga.py:380`｜「非有限几何→typed」措辞略宽于实现。** 实现只对 **NaN** 触发（±inf 经 `min/max` 被 clip 成有限值后放行，属既有 clip 语义）；docstring 却称「a non-finite geometry … is a typed invalid output, never coerced」。行为正确（且 NaN 的 typed 拒绝正是 R9 所求），仅措辞应收紧为「NaN geometry」，避免与「never coerced」再次摩擦。

**其余 diff 逐处审阅结论**：`math` import（`:49`）有实际使用；`_text_boxes_from_results` 的 NaN 门仅对 text 类生效（bubble 类在 `:387-389` 先行丢弃，不会被 NaN 牵连）——语义合理、无旁路副作用；测试新增/改写的每处注释、`pytest.importorskip` 落点、hex pin、`monkeypatch` 用法与既有风格一致；Task/Handoff/envelope 新增段落无相互矛盾的数字（+21.6 KB/+0 文件、25/25、n=5/315.6 均三处一致）。**禁改路径零出现**：diff 8 文件中无 `ports/**`、`detection_doctr.py`、`experiments/**`、`apps/**`、spec、`MERGE_*` 常数值、`requirements*`（`detection_doctr.py` 未被触碰 ⇒ MERGE_* 值必然未变）；亦无 `packaging/**`、`verification/M2-AC5/**`。计数自洽性：`def test_` 静态点数 = **28**（27+NaN，逐类 2/3/6/7/3/2/5），`275 providers + 35 m2_acceptance = 310 = 309(基线) + 1(NaN 用例)`，core 77 不受注释级改动影响——全部算术自洽。

---

## NOT_VERIFIED（本轮静态无法复现、集成方须复跑）

1. **pytest 计数**：`test_detection_manga.py` 28 passed、`_real.py` 2 passed（字体在位）、`tests/providers` 275 passed + 1 既有环境性失败、`m2_acceptance` 35、`tests/core` 77——我仅静态点数与算术核对（28/275+35=310=309+1），未执行。
2. **SHA-256 复算**：三权重文件字节级 hash（我仅核对 pin 全量 hex 在 `detection_manga.py:86-92` 与测试 `:388-399`、envelope `:16` 间逐字一致）。
3. **git 层事实**：commit 链 `40d4ab64 → a016d38c → efd134c2`、**两 commit 的归属拆分**（`git show --stat a016d38c` / `efd134c2`；Task`:99`、Handoff`:32` 声称 efd134c2「零内容变化」，我无法静态证否——注意本 diff 是两 commit 合并视图，无法据其判归属）、`git diff --check 2fee7d6e..efd134c2` EXIT=0、禁改路径专项 diff 为空、Task frontmatter `delivery_head=a016d38c` 与分支实际 tip `efd134c2` 的关系需在集成记录内明确（建议集成方按 M2-AC5 惯例并记 tip）。
4. **`cleanstart-gate.json` 字节级末尾 LF**：我以 diff hunk（`:348-354`，仅 no-newline 标记移除）+ worktree 末行为 `}` 为据判定「内容零变化」，未做 hexdump/`git diff` 字节复核。
5. **继承 r1 未复跑项**：CPU 兼容门 EXIT=0（`ac3_cpu_gate.py` 在仓库外）、`envelope_cpu.py` 315.6 ms/页（n=5）、sidecar 两次构建与体积 99,286,538 / 99,308,142 B、NSIS 27,924,371 B、M2-AC5 clean-start GATE 25/25、C4 GPU 76.1 ms/页。
6. **环境可用性**：`transformers==5.17.0` / `numpy` 可导入性、`transformers.RTDetrV2ForObjectDetection`/`RTDetrImageProcessor` 导出面、本地权重快照目录与 `C:/Windows/Fonts/msgothic.ttc` 存在性（R8 的 4 处 numpy skip 与 1 处字体 skip 在报告环境中**不应**触发，需实跑确认仍是 28/2 passed 而非 skipped）。
7. **R7 的 pre-Task 代码文本**：`os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", str(default))` 原文不在 worktree 内，注释所述差异沿用 r1 对 review-input.diff 的已核结论。

---

## 推荐下一步

由 acting Codex 在分支 tip `efd134c2` 上复跑 NOT_VERIFIED 第 1/3/6 项（pytest 三组计数、`git show --stat a016d38c`+`efd134c2` 与 `git diff --check`、确认 R8 skip 未触发），在集成修正 commit 内把 Handoff:28 的 release note 路径改为 `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`（N1，必改）、可选顺闭 N2–N4，随后按惯例 merge、回填 `integration_merge`/`review` 并置 `done`。
