## Verdict
**approved_with_conditions**

核心实现（协议 minor bump、`core.detect` handler、torchvision stable-ABI 闭包修复、frozen 进程内真实推理证据）静态核对**未见 P0/P1，未见伪造**；技术正确性与证据强度足以进入集成。放行条件（5 条）集中在：禁改面追认与契约自相矛盾修订、cargo 红灯闭合、IPC 错误消息 §8 路径泄漏的处置、§10 base64 大媒体的契约裁定、以及若干文档/测试口径更正。**不建议整体回退**。

---

## 逐项核对表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| **A. 协议扩展正确性** | **通过（附 2 处措辞更正）** | `PROTOCOL_MINOR=1` `src/bootstrap/core_service.py:64`；minor 增命令合规（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:87`「同 major 下 minor 可增加新 command」）；`core.detect` 分支 `core_service.py:499-563`；base64 `validate=True` fail-closed `:290-294`；文本上限 `:285-288`、解码字节上限 `:295-298`、宽高一致性 `:313-318`；typed envelope `:502-537`；三命令分支未触碰（diff 仅在 ListBooks 与 shutdown 之间**插入**新分支），Unknown 仍走 `:577-592`。**问题**：`elapsed_ms` 语义 docstring 与实现不符（见 R6）；"byte-identically" 失实（R7） |
| **B. handler→provider 路径** | **通过** | `CoreServices.detector` 新字段带默认值且为末字段 `src/bootstrap/core_assembly.py:574`，装配置 `:1034`，唯一构造点 `:1010`（无位置参数构造，向后兼容）；与 pipeline **同一对象**：`build_production_handlers(detector=detector)` `:899` → `handlers.py:170,250,275`；三路径赋值齐全 `core_assembly.py:764-771`（mock）/`:813-820`（manga）/`:821-833`（doctr）；`DetectionRequest` rgb24 与两 provider 契约一致 `detection_manga.py:193-212`、`detection_doctr.py:142-160`；`page_id="core.detect"` 仅作 provenance 不写库 `core_service.py:336-346`；输出直通匿名 label `:350-364`。**唯一瑕疵**：mock 路径 registry 里的实例与 `detector` 是**两个不同对象**（`mock_local.py:132-136` 新建），但该类无状态、行为等价——「同一实例」措辞在 mock 路径略强（R8 一并处理） |
| **C. 测试质量** | **通过（3 处覆盖缺口）** | `tests/core/test_core_detect.py`：12 函数 = 30 收集用例（5 参数化 typed 错误 + 15 参数化 INVALID_REQUEST），与 core 77→107 算术自洽；正常直通/空候选/无 detector/真实无权重 manga provider/坏 base64/不可解码/宽高不符/缺失与非法尺寸/超限双层/Unknown/shutdown/ping 1.1 全覆盖；`FakeDetectionProvider` 命名诚实、无冒充；既有断言同步最小（`tests/core/test_core_service.py:149-150,227-228` 两处 + 追加 e2e）。**缺口**：mock-assembly 一致性未真走装配（R8）、无装配 wiring 断言（R9）、e2e 断言非 hermetic（R5） |
| **D. torchvision 修复** | **通过（定性恰当）** | spec pin `packaging/m2ac5/core_sidecar.spec:96-106` + binaries 断言 `:146-159` + `hiddenimports` 注入 `:191-193`（仅 `core_service`，`:64-69`）；机理经**源码实证**：`torchvision/extension.py:29` `_load_library("_C_stable")` → `torch.ops.load_library(_get_extension_path(...))`（`_internally_replaced_utils.py:26-51`），静态分析不可见；hook 仍 pin 旧名 `torchvision._C`（build log `:1833-1834` 依旧 not found）；DETECT-2 全证据中 `_C_stable`/`image_stable` **零痕迹**，唯一痕迹是 `verification/M2-PROD-DETECT-2/warn/CLASSIFICATION.md:42` 被误判为软告警的 `torchvision._C`；修复后 build log `:1829-1830, 2089` 断言通过。**「DETECT-2 探针部分失效」定性恰当**：L3=闭包外等价推理（`verification/M2-PROD-DETECT-2/integration.md:44` 已把 AC5 收窄为 PARTIAL），结论不受影响；需注记的是 `integration.md:34` 与 `CLASSIFICATION.md:42` 的**闭包完整性强表述** |
| **E. frozen 探针证据自洽** | **通过（1 处数字无 artifact）** | 真 spawn 安装态 frozen exe：`verification/M2-PROD-DETECT-3/frozen-detect-probe.py:1390-1399, 1626`；FD-1 合成页 900x1300 / 16,549 B → base64 22,068 chars（与我实测 PNG 尺寸/编码长度逐位一致），2 候选 `manga-1/manga-2` conf 0.943/0.927（真实 provider 判别力充分，mock 的 label 为空）；FD-2/2b/3 与 `raw/fd*.log` 逐条一致（警告出现/消失/doctr 警告）；NSIS `ea34041c…` 与 GATE CS-E2 逐字符一致（`raw/cleanstart-runner-stdout.log` CS-E2 vs Handoff）。**瑕疵**：`cold 21.4s` 无 raw 支撑（见 R12） |
| **F. 禁改面与范围** | **通过，唯一偏差须裁定** | 20 文件全部落允许路径，唯一例外 `packaging/m2ac5/run_clean_start_e2e.py`（Task:73 允许 vs Task:81 禁止**自相矛盾**）；改动恰 2 处字面量（`:436-443` 请求、`:495` 断言），严格相等未放宽、25 场景与判定标准未变、无第三处；providers/ports/acceptance_bridge/apps/tauri.conf.json/requirements/experiments **零 diff**（diff 文件清单核对）；权重零 tracked（无 safetensors/.pt/.bin） |
| **G. GATE 与回归** | **通过（口径如实，1 项红灯转入集成）** | GATE 25/25 `raw/cleanstart-runner-stdout.log`（含 CS-R1..R4 Rust 宿主真实运行）；cargo 43+1 failed+1 ignored，失败= `apps/desktop/src-tauri/src/main.rs:1228` 过期断言（`:1194` MockChannel 桩自洽仍过，`library_bridge.rs:299` 自产 minor 0；`decode_response` `:82-114` 不校验 minor、`:414-419` 仅校验 major → 产品路径确实无影响）；pytest 289+1/35/107 算术自洽（DETECT-2 main 401=289+35+77，+30=431）；T3 基线漂移已在 Handoff 登记（「T3 范围」），Task/STATUS 未同步——**基本如实**，但 main 当前 291+1 skipped 需集成方复跑确认 |

---

## Findings

**R1 [P2]｜`src/bootstrap/core_service.py:532`（映射）+ 实证 `verification/M2-PROD-DETECT-3/frozen-detect-probe-results.json` FD-3 `observed.message_head`｜provider 错误消息把本地绝对路径送上 IPC 线。** `message=str(error)[:500]` 直通 ProviderError 文本，而真实 provider 的 NOT_CONFIGURED/模型错误消息必含绝对路径（FD-3 落库原文：`PROVIDER_NOT_CONFIGURED: docTR weights are not installed: C:\Users\49745\AppData\Local\Temp\...\fast_base-688`）。这违反 Contract §8 `message` 约束（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:229`「不得含 secret/本地绝对路径」）与 M2-IPC1 的冻结安全边界（`doc/tasks/M2-IPC1.md:46`「OS 路径…永不出 Core」）。缓解事实：该面仅为验证/工具面、本地 stdio、Tauri host 未注册（`apps/**` 禁改），暴露面有限。**建议**：集成方二选一——(a) 在集成 commit 或紧随 slice 里对 provider 消息做路径脱敏（保留 `error_code`+稳定短句，细节只走 stderr/provenance，需重建）；(b) 若接受现状，必须在 Task/契约注记中显式登记该 §8 例外并开后续修复 slice，不得静默。**不可**只写「typed 直通」而回避 §8。

**R2 [P2]｜`src/bootstrap/core_service.py:499-563`（core.detect wire 设计）｜新增命令与 Contract §10 的大媒体禁令冲突，未经契约裁定。** `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:262` 明写「Do not encode large images, Webtoon page/tile resources, or model weights in ordinary JSON/Base64 IPC. No IPC command/event in this contract accepts those byte arrays」，并要求大媒体命令须先独立 spike（容量/权限/生命周期/威胁模型）。本 Task 由裁决②授权 base64 PNG/JPEG，且该命令**随发布 exe 出厂**（探针即证明）。**建议**：集成方按 §Revision history 流程登记一条显式例外/修订（理由：验证面、本地 stdio、无网络面、32 MiB 上限、无写库），或在 DETECT-2/Task 注记中把该命令标注为 **dev/verification-only、非产品 IPC 面**。属契约层裁定，非 Owner 实现缺陷。

**R3 [P2]｜`doc/tasks/M2-PROD-DETECT-3.md:73` vs `:81`；AC5 行 `:40`｜契约允许/禁止范围自相矛盾，且 AC5 勾选与「禁改面空」不成立并存。** 同一文件既列入允许（`packaging/m2ac5/**`）又列入禁止（`run_clean_start_e2e.py`）；AC5 仍被勾选为 `[x]`「禁改面空」，而同文件证据表 `:66` 又登记唯一偏差。**建议**：集成 commit 内 (a) 追认该偏差，(b) 修订 Task 的允许/禁止表述与 AC5 措辞（例：禁改面「除经追认的 GATE 协议字面量同步外为空」），(c) 在 DETECT-2 注记里说明 GATE oracle 随协议 minor 同步。参见「偏差裁定建议」。

**R4 [P2]｜`apps/desktop/src-tauri/src/main.rs:1228`｜cargo 红灯带入 main。** Owner 受 `apps/**` 硬禁改约束未修，处置为「转集成方」——定性可接受（AC5 只要求「cargo/vitest 留痕」，且该断言确系裁决①后承）。但仓库不应把 1 failed 合并进 main。**建议**：集成 commit 内把 `:1228` 断言 `0`→`1`（`:1194` 为 mock 自洽桩，无需改；若改需同步 `library_bridge.rs:299`），复跑 cargo 期望 44 passed + 1 ignored，再把 GATE/探针证据绑定到该集成 commit。

**R5 [P3]｜`tests/core/test_core_service.py:192-195`｜新增 e2e 断言非 hermetic。** `env = os.environ.copy()` 未净化 `NEWMANGA_DETECTOR_WEIGHTS` / `NEWMANGA_DETECTOR_BACKEND`：若宿主/CI 指向真实权重，子进程会真加载模型、`PROVIDER_NOT_CONFIGURED` 断言必失败（或超时）。**建议**：子进程 env 显式 `pop` 两变量或指向不存在的临时目录。

**R6 [P3]｜`src/bootstrap/core_service.py:269-271` vs `:347`｜`elapsed_ms` 语义与实现不符。** docstring 称「decode + detect」，但 `started = time.perf_counter()` 在解码之后（`:309-325` 解码 → `:347` 计时），实测只覆盖 detect（含懒加载模型）。探针的 `elapsed_ms_incl_model_load` 解释因此正确，但 docstring 应改为「detect（含首次模型加载）」。

**R7 [P3]｜`src/bootstrap/core_service.py:25`、`doc/handoffs/M2-PROD-DETECT-3-983a50d5.md:33`｜「byte-identically / 字节级行为零变化」失实。** `PROTOCOL_MINOR` 0→1 使**每个响应**的 `version.minor` 与 `core.ping.protocol_version` 字节发生变化（这正是 GATE CS-L1 需要同步的原因）。Task:29 的「行为零变化」是准确口径；Handoff/注释应改为「命令语义（payload/result/错误码）零变化；envelope 的 protocol minor 随协议 bump 由 0→1」。

**R8 [P3]｜`tests/core/test_core_detect.py:198-206`｜「mock 装配一致性」未真正覆盖装配。** 该测试直接 `core.detector = MockLocalDetectionProvider()`，从未调用 `assemble_core_services(..., mock_local_providers=True)`，与 docstring「under the mock assembly」不符；`core_assembly.py:764-771` 中 registry 实例与 `detector` 也非同对象（无状态故行为等价）。**建议**：补一条真装配测试（mock 打开 → 断言 `core.detector` 为 mock 类型且 `core.detect` 返回 mock 候选），并在 Handoff 把 mock 路径措辞降为「行为一致（实例不共享）」。

**R9 [P3]｜`tests/core/**`（缺）｜无装配 wiring 回归断言。** 全仓库无任何测试断言 `assemble_production_core(...).detector is not None` 或与 `handlers.deps.detector` 同一对象——「与 pipeline 同源」目前只由发布态探针 FD-1 间接证明。**建议**：补 `assert core.detector is core.pipeline…` 类断言（或至少 `isinstance(MangaDetectionProvider)`），成本极低。

**R10 [P3]｜`src/bootstrap/core_service.py:76-82, 285-298, 309-319`｜32 MiB 只约束编码图像字节，解码后 raw RGB 无像素上限；注释措辞易误读。** 上限作用于 base64 解码后的 PNG/JPEG 文件长度（`len(encoded)`），而 `Image.convert("RGB")`/`tobytes()` 的像素缓冲不受约束：高压缩比 PNG 可解到远大于 32 MiB 的 RGB（Pillow 默认在 >2×89.5M 像素才抛 DecompressionBombError，即最坏 ~537 MB）。注释「enforced on the DECODED image bytes」易被读成像素字节。**建议**：(a) 在 `convert` 前加 `width*height <= N` 的像素上限（可复用声明宽高），(b) 注释改为「base64-decoded file bytes」。

**R11 [P3]｜`src/bootstrap/core_service.py:20, 250`｜「PNG/JPEG」为文档承诺但未强制。** 未校验 `image.format`，BMP/TIFF/WEBP/多帧 GIF 等 Pillow 支持的格式一并接受（测试只覆盖「不可解码」）。**建议**：要么显式 `image.format in {"PNG","JPEG"}` fail-closed，要么把文档改为「任意 Pillow 可解码图像」。

**R12 [P3]｜`doc/tasks/M2-PROD-DETECT-3.md:59`、Handoff:53、`verification/M2-PROD-DETECT-3/README.md:25`｜`cold 21.4s` 无 raw artifact 支撑。** 已入库 FD-1 会话日志记 `wall 5392ms`，results JSON 记 `elapsed_ms_incl_model_load: 4687`（二者自洽，且 stderr 含 `Loading weights`）；21.4s 出现在 3 处叙述但无对应日志/JSON。**建议**：删除该数字，或补一条绑定该测次的 raw 记录；同时把「热 4.7s」改为可判读的表述（该 4.7s **本身含模型加载**，与 DETECT-2 的稳态 273ms/页不是同一口径）。

**R13 [P3]｜`doc/tasks/M2-PROD-DETECT-3.md:12,15`｜交付锚点三处不一致。** Task frontmatter `base_commit: 095e314d…`（非分支实际 base `46f079e8`，Handoff:6 与 diff 均为 46f079e8）、`delivery_head: 9bcfd969`（分支 tip 为 b9c82779；评审输入又称 46d20842）。**建议**：集成方在 Task 内同步 `base_commit`/`delivery_head` 到最终合并锚点。

**R14 [P3]｜`src/bootstrap/core_service.py:531`（category）｜`category="internal"` 套用到全部 ProviderError，含 `INVALID_INPUT`。** §8 分类表（contract:228）中「我方请求错误」更接近 `validation`；未映射异常用 `internal` 亦与 §8「未映射用 unknown」有差。与 M2-IPC1 r2 P3-4 属同源既有口径。**建议**：至少在契约注记中登记；更优做法是按 error_code 给 category 一个小映射表。

**R15 [P3]｜`src/ports/detection/ports.py:59`（本 Task 禁改）｜`DetectionRequest` docstring 写「the image arrives as encoded bytes」，与两 provider 的 raw-pixel 契约（`detection_manga.py:191`, `detection_doctr.py:170-172`）相反。** 这恰好坐实裁决②的「事实修正」属实且必要，但端口层文档本身仍误导后续调用者。**建议**：开一个 doc-only 后续 slice 修该 docstring（本 Task 禁改正确）。

**R16 [P4]｜`verification/M2-PROD-DETECT-3/README.md:23,16`｜两处小数字口径。** (a) NSIS「439.44 MiB」：460,814,288/1,048,576=**439.4668→439.47**（与 tauri log `:10839` 的 439.47 一致），属截断笔误；(b) pyz「8,571 模块」vs 构建期「8572 pure modules」——两者统计面不同，建议注明（`analysis.pure` 含 PYZ 未列项）。

**R17 [P4]｜`verification/M2-PROD-DETECT-3/frozen-detect-probe.py:1508,1545-1554`｜探针 rename/restore 无 try/finally。** FD-2 改名失败或 FD-2/2b 之间异常会把安装目录 `models/` 留在 `models.probe-parked`（后续复跑需人工复原）。证据工具，风险低；**建议**加 `try/finally` 复原。

---

## 偏差裁定建议

**1) `packaging/m2ac5/run_clean_start_e2e.py` 偏差 → 建议「接受追认（accept & ratify）」，不要求回退。**
理由：①改动仅 2 处协议字面量（`:436-443`、`:495`），严格相等断言与 25 场景计数/判定标准零变化，不构成 gate 放宽；②裁决①必然使 `core.ping` 携带 minor 1，server 恒返回 1.1，任何情况下该断言都会 24/25——**回退在技术上不可行**（除非同时回退 minor bump，即放弃本 Task 目标）；③`packaging/m2ac5/**` 在允许清单内，虽与禁止清单字面冲突，但属契约内部矛盾而非 Owner 越权。**追认须同时满足**：(a) 集成 commit message/集成记录写明「追认 run_clean_start_e2e.py 协议字面量同步」；(b) 修订 Task:81 与 AC5(:40) 的自相矛盾表述；(c) 集成方复跑 GATE 以绑定新 sha。
**若集成方坚持「禁改面绝对空」**：唯一闭合方式是把 GATE oracle 的字面量改为只断言 `major==1` 且 `capabilities` 不变（同样是一次改动），**不解决**禁令问题——因此仍以追认为正解。

**2) cargo `real_library_sidecar_round_trip_and_eof` failed → 建议「集成方一行修复 + 复跑」，不留红灯。**
`main.rs:1228` 断言 `minor==0`→`1` 是裁决①的直接后承，语义上必须同步；`:1194` 为 MockChannel 自洽桩**不应**顺带改（改它需连带 `library_bridge.rs:299`）。集成后方可把 AC5 的「cargo 留痕」升级为「cargo 全绿（44 passed + 1 ignored）」。GATE 25/25（含 Rust 宿主真实运行）已足以支撑 Ac5 的产品路径结论，但不足以豁免仓库红灯。

**3) R1（§8 路径泄漏）处置建议（供集成方）**：优先在集成 commit 或紧随的极小 slice 内脱敏（ProviderError → 线上仅 `error_code` + 固定安全短句，细节写 stderr/provenance），因为这属于**已冻结契约的硬约束**；若因重建成本暂不修，必须在 Task/契约注记中登记为例外并开后续 slice，**不得**默认「typed 直通」即合规。

---

## NOT_VERIFIED

- pytest 三套件（289+1 / 35 / 107）与 cargo（43+1+1 ignored）、vitest（31）**实跑计数**——纯静态，未复跑；仅核对其内部算术自洽与 T3 基线登记。
- `git diff --check 46f079e8..HEAD EXIT=0`、`git ls-files` 权重为零、porcelain 干净、分支未 push——无 git 执行能力（本会话 pwsh 不可用），仅按 diff 文件清单反推。
- NSIS 全量 sha256 逐字节比对（仅核对 `ea34041c…` 前缀与 CS-E2 一致）。
- FD-1..FD-3 探针**复跑**（推理确定性、冷/热耗时、失败面）——归集成方。
- M2-AC5 runner 对 `gen/schemas`/`permissions` 的 `git checkout --` 还原**实际执行**（Handoff:64 自述，无 artifact）。
- 合并 T3 后的 main 基线（题述 291+1 skipped 与 Owner 分支 289+1 failed 的差异归因）。
- Task frontmatter `base_commit: 095e314d` 与分支实际 base 的关系（无法读 git 历史确认其是否线性祖先）。

---

## 集成方闭合清单

1. **追认 `run_clean_start_e2e.py` 偏差**（集成 commit + 集成记录），并修订 `doc/tasks/M2-PROD-DETECT-3.md:73/81` 与 AC5(:40) 的自相矛盾表述。
2. **修 `apps/desktop/src-tauri/src/main.rs:1228`** `0`→`1`，复跑 cargo（目标 44 passed + 1 ignored），仅此项。
3. **处置 R1（§8 路径泄漏）**：或做 provider 消息脱敏（需重建），或登记为显式契约例外 + 开修复 slice；二者必选其一并留字。
4. **登记 R2（§10 base64 大媒体）契约裁定**：在 `M2-C1_TYPED_IPC_CONTRACT.md` Revision history 加例外，或在 Task 内把 `core.detect` 标注为 verification-only 非产品 IPC 面。
5. **给 M2-PROD-DETECT-2 加注记（不改历史）**：`verification/M2-PROD-DETECT-2/integration.md:34` 与 `warn/CLASSIFICATION.md:42`（「torchvision 本体与 C 扩展已随闭包收集」已证伪；958 missing 中无 `_C_stable` 痕迹），并把 AC5 NOT_RUN 子项改标 RUN。
6. **同步 Task 锚点**：`base_commit`→46f079e8、`delivery_head`→最终合并交付 commit；`status`→done 由集成方处理。
7. **更正取证措辞**：删/补 `cold 21.4s`；`elapsed_ms` docstring 改「detect（含模型加载）」；「byte-identically」改「命令语义不变，minor 0→1」；`ports.py:59` docstring 开 doc-only slice。
8. **补两条廉价测试**（可并入后续 slice，非阻塞）：子进程 e2e env 净化（R5）、装配 wiring/同一实例断言（R9）。
9. **合并后复跑并记录**：pytest 三套件（T3 后基线）、GATE 25/25（绑定集成 commit 的 NSIS sha）、确认 `git status` 干净与 `diff --check`。
10. **开后续 slice（登记不释放）**：`core.detect` 像素上限与格式白名单（R10/R11）、provider 错误消息脱敏（若选例外路径）、`ports.detection` docstring 修订（R15）。

---

## 推荐下一步

集成方先在集成 commit 内完成「追认 run_clean_start_e2e.py + 修 main.rs:1228 + 登记 §8/§10 两条契约处置 + 给 DETECT-2 加闭包注记」，再复跑 pytest/cargo/GATE 并回填 Task 锚点与 STATUS。
