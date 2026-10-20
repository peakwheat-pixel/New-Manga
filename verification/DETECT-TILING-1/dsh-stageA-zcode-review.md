# ZCode 独立 Review：DETECT-TILING-1 阶段 A

- **Reviewer**: ZCode（非实施者；实施者为 DSH，符合 AGENTS.md 非自审约束）
- **审查对象**: delivery_head `843cfe705`（base `5885b182e`，分支 `agent/antigravity/DETECT-TILING-1`）
- **审查日期**: 2026-10-20
- **方式**: 只读——diff 逐行核对 + `handle_detect` 全函数静态分析 + 证据文档/JSON 交叉核对 + Task/Handoff 诚实性检查。已核实 `5885b182e..843cfe705` 区间仅此一个 commit；其后的 88ad7a8de / 783434e5b / 2106671be 三个 governance commit 只动 `doc/` 与 `verification/`，未触碰 `src/`、`tests/`，工作区代码面与 delivery_head 一致。

## 结论

**APPROVE_WITH_COMMENTS** —— 代码改动成立：像素上限检查位置未动（仍在 `Image.open` 之后、`convert()` 之前），错误信息三处数字准确且动态计算，「拒绝先于解码」静态可证并有实测佐证，Task 无任何未完成项被写成 PASS；但「拒绝先于解码」缺自动回归守卫（P1-1），且 Task/证据存在 AC4 记录矛盾、commit pin 错误与越权自行裁定（P1-2），两项应在 Task 收口前处置，均不需动 `src/`。

## 逐项判定

| 项 | 判定 | 依据 |
|---|---|---|
| 3.1 代码正确性（拒绝时机未变） | **通过** | `src/bootstrap/core_service.py:1413` 的条件 `image.width * image.height > MAX_DETECT_PIXELS` 原样保留；`raise` 在 L1420-1430，`image.convert("RGB")` 在 L1432。`Image.open`（L1396）惰性只读 header，检查与 raise 之间仅访问 `image.format / width / height`（header 属性，不解码像素）。diff 只新增注释、局部变量（`width_px/height_px/pixels/ceiling_edge`）与消息文本，`if` 条件与位置零改动；未引入 `crop()/reduce()/draft()` 或任何其它 Pillow 像素访问路径 |
| 3.2 错误信息准确性 | **通过** | `ceiling_edge = int(MAX_DETECT_PIXELS ** 0.5)` = int(3344.37…) = 3344；3344² = 11,182,336 ≤ 11,184,810，3345² = 11,189,025 超限——floor(sqrt) 的平方恒 ≤ 原值，所以「about 3344x3344」永远是一个真实可达的目标，不会误导用户。`3.83x` 为运行时 `pixels / MAX_DETECT_PIXELS` 动态计算（42871770 / 11184810 = 3.833），构造上不会漂移；JPEG 证据中同型消息 `1.79x over`（20000000/11184810 = 1.789）亦吻合。拒绝条件为严格 `>`，恰等于上限的页被放行，与消息 "at most 11184810 pixels" 口径一致。「rejected before any pixel decoding」不是裸断言：静态成立（代码位置 + Pillow 惰性语义）+ 阶段 1 `open_only` 三样本峰值增量实测全 0.0 MB（open 不分配像素）+ stageA 拒绝峰值 37.3 MB ≪ 满幅 RGB24 122.7 MB（3.3× 差距，测量噪声不可桥接） |
| 3.3 测试质量 | **部分通过（P1-1）** | 无写死 `3344`：测试内 `ceiling_edge = int(MAX_DETECT_PIXELS ** 0.5)` 重算并断言 `f"about {ceiling_edge}x{ceiling_edge}"`，`str(MAX_DETECT_PIXELS)` 动态断言；若 `MAX_DETECT_PIXELS` 变化，`assert 4096 * 4096 > MAX_DETECT_PIXELS` 前提断言使测试诚实失败而非静默通过。把 "before any pixel decoding" 从代码删掉，`assert "before any pixel decoding" in message` 会失败——消息回归保护成立。**但**测试验证的是消息内容 + `core.detector.seen_request is None`，后者只证明「先于 provider 调用」，不证明「先于解码」：若把像素检查挪到 `convert()` 之后，全部现有断言仍绿。测试守的是消息，不是行为顺序，见 P1-1 |
| 3.4 证据可信度 | **基本可信（P2-1/P2-2）** | 四个「不要用」的理由真实且对症：tracemalloc 只跟踪 Python 堆、Pillow 在 C 层分配；单进程 PeakWorkingSetSize 不回落故须独立子进程；SetProcessWorkingSetSize 在 kernel32 非 psapi；GetProcessMemoryInfo 未声明 argtypes 时 HANDLE 截断、返回 False、读到全 0——第 4 条「三版都读了 0 而从未检查返回值」的自我披露是诚实的。37.3 MB 确实包含约 20 MB 编码文件读入，md §二已如实说明该开销性质；但它不构成「拒绝仍分配了像素缓冲」的疑虑——满幅 RGB24 122.7 MB 与实测峰值差 3.3×。**对照组**：阶段 1 有明确对照样本 A（600×18401，不超限）在同一修正方法下实测 `open_only 0.0 / convert_full 60.7 / tobytes 124.0 MB`，方法灵敏度有实证；但 stageA 探针自身（新探针、新样本 690×62133）没有同一样本的解码对照行，「满幅 163.5 MB」是该样本的算术推算（42,871,770 × 4 B，已复核精确）而非实测解码峰值——「方法能看见解码级分配」的论证目前靠跨文档、跨样本拼接，见 P2-1 |
| 3.5 诚实性 | **通过，附 P1-2** | Task 文件 AC checkbox 全部 `- [ ]` 未勾选；AC2/AC3 明确「未开始」、AC5 明确「独立审查未做」；stageA md §五「明确未做」与 Handoff「未完成项（不得写为 PASS）」逐项如实登记；Task L221 甚至明文「任何『已自审通过』的记录都是伪造，我没有写」。**没有任何未完成项被标 PASS 或打勾。** 但发现记录层矛盾与证据 pin 错误（属应修，非虚报完成）：见 P1-2 |

## 发现的问题（按严重度）

### P0（阻断）

无。

### P1（应修）

**P1-1 「拒绝先于解码」无自动回归守卫。** `test_detect_decoded_pixel_cap_rejected` 的全部断言（INVALID_REQUEST、消息子串、`seen_request is None`）在像素检查被移动到 `convert()` 之后时仍然通过。AC1 的核心属性——本 Task r35 改向后的全部存在意义——目前只受静态代码位置和一次性内存探针保护，无任何测试能捕获顺序回归。建议（在本 Task 允许范围 `tests/**` 内）：monkeypatch `PIL.Image.Image.convert`（或 `load`）记录调用/抛错，dispatch 超限请求后断言 convert 未被调用且仍得到 typed 拒绝——廉价、确定性，且不受「tracemalloc 看不见 C 层分配」限制（拦截的是 Python 方法入口，不依赖内存计数）。

**P1-2 AC4 记录矛盾 + 证据 pin 不实 + 越权自行裁定，需 Codex 处置。** 四个子项：

- (a) `doc/tasks/DETECT-TILING-1.md` 内并存矛盾：L165-181「2026-10-20 AC4 收口（合成 JPEG）」声称已补齐，L192 的 AC 状态表仍写 `PARTIAL —— JPEG 超限样本不存在`。按 commit 时间序（88ad7a8de 写表 → 783434e5b 加收口小节）后者为新，但旧表未更新，读者以任一处为准都会得到错误结论。
- (b) Canonical Evidence 表 EV-DT1-JPEG 的 commit 写 `843cfe705`，但 `stageA-jpeg-rejection-memory.json` 实际由 `783434e5b` 添加（已核实 843cfe705 的文件清单不含它）。证据 pin 指错 commit，破坏可验证性。
- (c) 证据表 sha256 列全部为 `(worktree)` 占位，而 frontmatter 写 `canonical_evidence_status: complete`；且合成 JPEG 样本无 sha256 记录，违反 AC4 自己的「样本引用方式为路径 + sha256」——PNG 样本路径内嵌对象存储 sha256（02499d71…275f）算满足，JPEG 不满足。
- (d) AC4 改用合成 JPEG 属验收口径变更：stageA md §三原文「我未选。这是 AC 措辞问题，应由 Codex 裁定」、Handoff 同样列为「需 Codex 裁定的三个选项」，但 783434e5b 由实施者自行裁定选项 A（虽有披露「按推荐自行裁决」）。按 AGENTS.md，需求取舍与冲突决策属 Codex/用户，此裁定需追认或退回。

### P2（建议）

**P2-1 stageA 探针补解码对照行。** 在同一探针、同一样本（690×62133）上补一行强制解码（如 `convert_full`）的实测峰值，使「拒绝 37.3 MB vs 解码 ≫ 37.3 MB」的对比自含于同一份证据；或在 md 中显式引用阶段 1 样本 A 作为灵敏度对照，并说明跨样本佐证的局限。

**P2-2 内存指标口径未写明。** stageA JSON 中 `ws_increase_at_rejection_mb: 63.3` **大于** `peak_increase_at_rejection_mb: 37.3`，而阶段 1 各表中 ws_delta 普遍**小于** peak_increase——两组探针的基线定义（SetProcessWorkingSetSize trim 时机、peak 是否含解释器启动峰值）未记录，跨文档不可复构。建议在 md/JSON 中写明指标与基线定义。

**P2-3 stageA md 自述过时。** `stageA-rejection-memory.md` §四写「测试未补、Handoff 未写」、§五写「未提交」，但该 md 与测试改动、交付 commit `843cfe705` 同批入库——committed 状态下这些陈述已不真。Task/Handoff 已用更新记录纠正，建议 md 加一行勘误注记，避免 CANONICAL 证据自含矛盾陈述。

**P2-4 弱断言。** `assert "over" in message` 判别力过弱（任何含 "over" 的措辞都过）；可改为断言计算值（如 `f"{4096 * 4096 / MAX_DETECT_PIXELS:.2f}x over"`，当前为 `1.50x over`）。

## 明确未核实的内容

1. **pytest 未复跑**（本 Review 全程只读约束）。Handoff 声称 `python -m pytest tests/core/test_core_detect.py -q` → `34 passed in 1.85s`；我对该文件手工清点测试条目为 7 + 5（typed-errors parametrize）+ 15（invalid-requests parametrize）+ 7 = 34，与声称数量一致，但执行结果未由本 Review 复现。
2. **workspace 样本现存性未盘点**：PNG 对象 `G:\CODEX\New Manga.workspace\test-materials\objects\sha256\02\02499d71….png` 与合成 JPEG `G:\CODEX\New Manga.workspace\DETECT-TILING-1\synthetic\oversized-5000x4000.jpg` 两个路径未核实存在。
3. **合成 JPEG 的 sha256 未计算**（AC4 要求路径 + sha256，JSON 中只有路径，见 P1-2(c)）。
4. **内存探针未复现**：122.7 / 163.5 MB 已做算术复核（像素数 × 3/4 字节精确吻合）；37.3 / 17.6 / 19.5 MB 为实测值本身，未重测。
5. **r35 裁定原文未核**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-tiling-stage2-r35.md` 未读取，本 Review 依据 Task 内引用的裁定摘要。
6. **governance check.ps1 的「PASS (1 warnings)」声明未复核**；AC2/AC3 按 Task 记录未开始，无审查对象。

## 处置建议（供 Codex/编排）

- P1-1（测试行为守卫）与 P1-2(a)(c)（记录修正 + sha256 补录）可在本 Task 允许范围内由非作者完成；P1-2(b)(d)（pin 修正、AC4 口径追认）属 Codex 裁定项。
- 本 Review 通过的是**阶段 A 代码面**：AC1 的完成以补 P1-1 为宜，AC4 以 P1-2 处置为先，AC2/AC3 待后续阶段；在此之前 Task 应保持 `in_review`，不得进入 `done`。
