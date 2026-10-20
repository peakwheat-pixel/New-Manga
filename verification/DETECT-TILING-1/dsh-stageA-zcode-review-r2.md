# ZCode 独立 Review r2：DETECT-TILING-1 阶段 A 处置复核

- **Reviewer**: ZCode（同 r1，非实施者）
- **复核对象**: r1 Review 之后的新增提交 `07e414773` / `de788b212` / `96bc66d93`（含其间入库的 `01fcffe95`：r1 Review 文件、重测证据与重写后的 `stageA-rejection-memory.json`）
- **复核日期**: 2026-10-20
- **方式**: 只读——三个 commit 全量 diff 逐行核对 + 新测试静态推演 + sha256 独立复算（工作区口径与 `git show <commit>:<path>` blob 口径均测）+ Task/remeasurement/JSON 交叉核对。未执行任何代码。

## 结论

**APPROVE_WITH_COMMENTS** —— 处置是实质性的而非应付：P1-1 的双臂测试质量超出 r1 建议，P2-2 的处置主动撤回了交付自己的核心数字（37.3 MB）并补齐了同源对照，这是自我否定式的诚实。但复核新发现两条 P1：remeasurement §四 对 CONTROL 样本的归因与自身 JSON 数据直接矛盾（探针 crash 被解读成产品拒绝），六个 sha256 的登记口径是「写表时工作区」而非 pin commit 的 blob（4/6 按表不可验证）。两条均可在本 Task 范围内修复，但在修复前，remeasurement §四 不得作为「字节上限路径已验证」的依据、Canonical Evidence 表的 sha256 列不得作为可验证 pin 使用。

## 逐项判定

| 项 | 判定 | 依据 |
|---|---|---|
| P1-1 顺序守卫 | **已真修** | `07e414773` 新增 `test_detect_oversized_rejected_before_any_pixel_decode`：monkeypatch `Image.Image.convert` 为 spy，dispatch 4096×4096 超限页后断言 `conversions == []`。机制成立：handler 内 `from PIL import Image` 与测试 patch 的是同一模块对象，`PngImageFile` 实例方法查找走 MRO 必命中被替换的 `Image.Image.convert`。若像素检查被移到 convert 之后，spy 记录 `(4096, 4096)`，断言失败，失败消息 `'convert was called with [(4096, 4096)]'` 与 commit message 声称逐字吻合（该格式可由代码直接推出，逻辑必然）。对照组 `test_detect_within_cap_does_reach_convert` 断言不超限页 `conversions != []` 且 provider 被调用——堵死了「reject everything 也能过第一个测试」的假满足，双臂设计优于 r1 的单点建议。测试内 `assert len(encoded) < MAX_DETECT_PAGE_BYTES` 确证触发的是像素门而非字节门。改进项见 N-4（spy 未覆盖 `load`/`tobytes`） |
| P1-2(a) AC4 矛盾行 | **已真修** | `de788b212` 将状态行改为「PNG 与合成 JPEG 均已测（见下『AC4 收口』）；真实超限 JPEG 仍不存在，该项限制保留」——矛盾消除且保留了限制披露，与收口小节语义一致 |
| P1-2(b) commit pin | **已真修** | EV-DT1-JPEG 的 commit 改为 `783434e5b`；本 Review 独立验证 `git show 783434e5b:stageA-jpeg-rejection-memory.json | sha256sum` = `e330c215…` 与登记值一致。pin 现在可验证 |
| P1-2(c) sha256 补录 | **半修，口径错误（新 P1，见 N-2）** | 登记值是真实摘要且合成 JPEG 的 `84592ff425ae348313ef202230d59583ef727cada9aca55027dfcc1f800bee5f` 经本 Review 独立复算一致（文件存在，313,627 B ≈ 0.3 MB，与 JSON `file_mb` 吻合）。但六个值的口径不统一且与 commit 列矛盾：MEMJSON/S1/S2/R35 四项登记值等于**写表时（de788b212）工作区文件**的摘要，而按表去 pin commit 取 blob 验算全部不匹配（如 MEMJSON 登记 `7a469ead`，`843cfe705` blob 实为 `8b414a7f`；S1 登记 `47995fc2`，`b5253ebfc` blob 实为 `3ed4a07e`；S2/R35 同）。根因含行尾（工作区 CRLF vs blob LF，四文件均无 .gitattributes 约束）。EV-DT1-MEM 的登记值如今连当前工作区都不再匹配（96bc66d93 追加勘误后），六个值中每个的可验证对象互不相同 |
| P1-2(d) AC4 口径追认 | **正确地未处置** | 明确留待 Codex 追认，本轮无越权自行裁定（与上一轮的 (d) 形成对照）。收口影响见下文「收口阻断判定」 |
| P2-1 同源对照 | **已真修，超出预期** | `stageA-remeasurement-20261020.md` §二：同一样本、同一探针、双臂对照——PNG 690×62133 拒绝峰值 141.7 MB vs `full_decode`（convert+tobytes）峰值 479.8 MB（3.4×）；合成 JPEG 53.2 vs 242.2 MB（4.6×）。r1 要求的「同一份文档内自证的对照」达成。数量级与算术自洽：拒绝路径 141.7 ≈ 进程基线 70.3 + 编码文件处理 ~71 MB，与满幅 163.5 MB 的页级分配不吻合；full_decode 的 398.5（convert 后）/479.8（tobytes 后）与页级分配量级吻合。**AC1「拒绝不触发整图像素分配」在新口径下依然成立** |
| P2-2 指标口径 | **已真修，并揪出 r1 未识破的真缺陷** | 根因分析正确：`SetProcessWorkingSetSize(-1,-1)` 只 trim 当前工作集、不动 peak 计数器，导致 `ws1-ws0` 与 `pk1-pk0` 两个增量不同源——这正是 r1 P2-2 观察到的 63.3 > 37.3 之谜的答案。修复为逐检查点记录绝对值并加 `ws <= peak` 不变量自检，JSON 全部 6 样本无违规。**旧值 37.3/19.5 MB 确系错误口径产物，撤回正确。** 这同时意味着：r1 Review 引用的 37.3 MB 及交付 commit `843cfe705` 标题「37 MB peak, not 163」的数字口径均已过时（commit 历史不可改写，收口时应注明）。r1 当时已将口径疑点列为 P2 但低估了严重度——它实为推翻原核心数字的证据缺陷，此处自我更正 |
| P2-3 勘误 | **已真修** | `96bc66d93` 在 `stageA-rejection-memory.md` 末尾追加勘误：原值保留可见、指明 §四/§五 陈述在提交时已过时、明确 §二 数字被 141.7/53.2 取代且引用必须改用重测值。留痕式勘误符合 r1 建议。小笔误见 N-5 |
| P2-4 弱断言 | **已真修** | 断言改为 `f"{4096 * 4096 / MAX_DETECT_PIXELS:.2f}x over"`（即 `"1.50x over"`），与消息生成侧同一算式同一格式——删掉消息中的比例或改格式，测试必然转红。声称的删词转红实验逻辑必然（未独立复现，见「未核实」） |

**对三个提问的直接回答**：

1. **是真解决，不是形式应付。** 两条 P1 与四条 P2 中，五条真修、一条（P1-2(c)）半修且带新口径缺陷。最能说明态度的是 P2-2：重测推翻了自己交付 commit 标题里的数字并公开撤回，这不是应付者的行为。但每批提交都带新的记录层缺陷（r1 抓 4 条 → 修复批带 2 条新的 + 一族滞后），「算数、写表、归因」环节的严谨度是这个交付链的系统性弱点。
2. **有新问题**：N-1（P1，证据错误归因）、N-2（P1，sha256 口径）、N-3（P2，处置状态表滞后家族）、N-4/N-5/N-6（P2）。
3. **P1-2(d) 构成 Task 收口阻断，不构成阶段 A 代码面阻断**（详见下节）。

## 新发现的问题（按严重度）

### P1（应修）

**N-1 remeasurement §四 对 CONTROL 样本的归因与自身数据矛盾，错误事实已写入 canonical 证据。** §四 声称对照样本 `600×18401`「仍然被拒绝……原因：编码字节数超过 `MAX_DETECT_PAGE_BYTES`（32 MiB）」并称之为「有价值的意外——验证了字节上限路径也在正确拒绝」。但同一文件引用的 `stageA-rejection-memory.json` 中该样本记录为 `file_mb: 1.6`（远小于 32 MiB；像素 11,040,600 也小于 11,184,810 上限，本不应被拒）、`error_type: "AttributeError"`、`message: "'CoreServiceServer' object has no attribute '_core'"`——这是**探针 harness 自身崩溃**，不是产品拒绝：被字节门拒绝会抛 `DetectRequestError`（typed INVALID_REQUEST），不可能抛 AttributeError。1.6 MB 触发 32 MiB 字节门的归因在任何读者面前都站不住。附带判断：崩溃点在 `getattr(self._core, "detector")`（core_service.py:1448），晚于 convert（L1432）与 tobytes（L1440），故该行 `peak_mb: 204.8` 实为**不超限页走完解码的真实峰值**——数据反而有价值，但必须先更正归因才能引用。字节门正确性已有单测覆盖（`test_detect_oversized_payload_rejected_before_decode` + `test_detect_decoded_length_guard_backs_the_text_guard`），无需这个假证据背书。处置：更正 §四（探针 bug + 崩溃点定位 + 204.8 的真实含义），「正常页通过 handle_detect 产出 region」的实测对照缺口他们已如实登记，保持登记即可。

**N-2 Canonical Evidence 表 sha256 口径错误，4/6 按表不可验证。** 如逐项判定 P1-2(c) 所述：登记值对应「写表时工作区快照」，与 commit 列（pin 时点）合起来自相矛盾；四个文件的行尾差异（工作区 CRLF / blob LF）使两种口径的摘要系统性不同。这是 r1 P1-2(b)「pin 指向不含文件的 commit，无法被任何人验证」的同型教训在修复动作里重演。处置（二选一，推荐前者）：(1) sha256 列统一改算 pin commit 的 blob 摘要（`git show <commit>:<path> | sha256sum`，或直接用 `git rev-parse <commit>:<path>` 的 blob hash——后者不受行尾与 autocrlf 影响，更稳）；(2) 表头声明「sha256 = de788b212 时点工作区快照」并接受 MEM md 行随勘误失效的事实。同时建议在仓库治理层登记 autocrlf/行尾对证据指纹的影响。

### P2（建议）

**N-3 处置状态表滞后家族（第三次同型问题）。** 多份记录各自描述「写入时点」的状态、无交叉引用与终态收口，读者以任一处为准都会得到过时结论：
- Task L197「实测关键数：……拒绝时峰值 **37.3 MB**」与 L239「37.3 MB 是 trim 基线产物（已撤回，141.7）」同文件并存——这是 r1 P1-2(a) 的同型矛盾，本轮最应避免却仍出现；
- Task AC4 收口小节表格（L172-175）内的 37.3/19.5 未标注已被取代；
- Task 处置表 L240/241 写 P2-3/P2-4「未修」——一分钟后 `96bc66d93` 已修；
- remeasurement §五 表写 P1-1/P1-2(a)(b)(c)「未修」——其后三个 commit 已修；
- Task L195 AC5 行「回归已跑 34 通过；独立审查未做」——现为 36 个测试，且 r1 独立审查已做（Task L229 自己引用了 r1 文件）；
- frontmatter L12 reviewer「当前 Session 无人可派」——ZCode r1/r2 已执行两轮。
处置：以 Task 处置表为唯一终态表，加「截至 commit」戳；其余文件的状态段标注「时点快照，终态以 Task 为准」；37.3/19.5 在 Task 内出现的两处加「已被 141.7/53.2 取代」内联标注。

**N-4 spy 覆盖面。** 顺序守卫只拦 `Image.Image.convert`。AC1 措辞是「任何触发像素解码的操作」；handler 现状唯一解码入口是 convert，当前够用，但若未来回归以 `image.load()` / `tobytes()` 先行，守卫不响。建议 spy 同时覆盖 `load` 与 `tobytes`（三行改动）。

**N-5 勘误表笔误。** `stageA-rejection-memory.md` 勘误段测试名写作 `test_within_cap_does_reach_convert`，实际函数名为 `test_detect_within_cap_does_reach_convert`。

**N-6 「实测证明」声称无留痕。** 注入回归实验（07e414773）与删比例转红实验（96bc66d93）在 commit message 与 Task 处置表中被表述为已证事实，但实验本身未留下可重跑的脚本或输出记录。本 Review 通过静态推演确认两个实验的逻辑必然性（失败消息格式可由代码直接推出），判定其可信；但按本项目证据纪律，「实测证明」声称应有独立可复核载体。建议将注入实验固化为一个标记性测试或脚本留档，或将表述弱化为「验证过（未留痕）」。

## 明确未核实的内容

1. **pytest 未复跑**（本 Review 全程只读）。声称 36 passed（34+2）；静态清点当前文件测试条目与声称数量一致；两个红/绿实验（注入 convert、删比例）未独立复现，以静态推演确认其必然性（见 N-6）。
2. **内存重测数值未复现**：141.7 / 479.8 / 53.2 / 242.2 / 204.8 MB 均为提交方数据。本 Review 做的是内部一致性核对——全部检查点 `ws <= peak` 不变量通过、双臂数量级与像素算术吻合、基线（~51-70 MB）合理——外部复现未做。
3. **r35 裁定原文仍未核**（r1 遗留项，与本轮判定无关）。

（sha256 六值与合成 JPEG 摘要本轮**已独立复算**，结果已写入逐项判定与 N-2，不属于未核实项。）

## 收口阻断判定（P1-2(d) 及整体）

**P1-2(d) 构成 Task 进入 `done` 的阻断项**：AC4 从「真实 test-materials 样本」改为「合成 JPEG」是验收口径变更，按 AGENTS.md 属 Codex/用户职权；未经追认，AC4 不能计为闭合，Task 不能收口。它**不阻断阶段 A 代码面**——代码、测试与内存证据本身均已通过两轮 Review。

**收口前必须清零的清单**（按本轮终态）：① P1-2(d) Codex 追认（或退回补真实样本）；② N-1 remeasurement §四 错误归因更正；③ N-2 sha256 口径统一；④ N-3 至少清除 Task 内 37.3 与撤回声明的并存矛盾；⑤ AC2/AC3 完成（按 Task 现状未开始）。⑥（建议级）N-4/N-5/N-6。

**对 r1 结论的修订**：r1 判定表 3.4 中「stageA 拒绝峰值 37.3 MB ≪ 满幅 122.7 MB」一段基于当时未识破的错误口径，应按「拒绝峰值 141.7 MB vs 同源解码 479.8 MB（3.4×）」重述；r1 的其它判定（代码正确性、消息准确性、测试结构、诚实性）不受影响。AC1 的核心结论「拒绝路径不触发整图像素分配」在修正口径后依然成立。
