# M2-PROD-SFX-PROBE-1 非作者独立复核 r2（定点复审，只读静态）

方法：全程只读，未执行任何 shell/git/构建/探针命令，未写文件。独立证据源=worktree reflog（`G:\CODEX\New Manga\.git\worktrees\M2-PROD-SFX-PROBE-1-zcode\logs\HEAD:9-11`，只读）+ 交付文件逐行复算 + r1fix 落盘 raw。r1fix 三 commit 链与实报 tip 一致：`b1dd1ad4 → 441f4ab5（runner 加固）→ f6a25d69（r1fix 重跑+range 落盘）→ 4d95a2e7（docs+spec+README）`，base=`d298ecd0`。

---

## 1. 终判

**approved_with_conditions（= 实质通过、建议集成；不构成 changes_requested，无需再开 Review 轮）**

- 0×P0、0×P1。r1 的 **C1/C2/C3 全部实质闭合**，**C4/P3-1/P3-3/P3-4/P3-5 与 P4-2/3/4/5/6/8 闭合**，其中 C3 是**代码面 + 重跑证据双闭合**（新判据真落到 `if` 条件里，而非只写文档）。
- 残留 = **1×P2（Handoff 未随 r1fix 同步且残留被推翻的"onnxruntime 面"表述）+ 2×P3（SP-L2 "三键在场"仍未落到代码；Task 引用的 r1 报告文件路径待归档）+ 8×P4（措辞/机制/卫生）**。全部可在集成 commit 内顺笔闭合；闭合后即等价 approved。
- 特别裁决（P3-3，用户点名）：**认可集成方的实测登记，不持异议**；我 r1 的"range check 应为空"预期在机制上错误，详见 §2-C4 与 P4-R4/R5。

---

## 2. 逐项核对表（C1–C4 + 另核）

| 项 | 判定 | 关键证据（path:line） | 说明 |
|---|---|---|---|
| **C1（P1-1）三处「逐位一致」更正** | **CLOSED** | `doc/tasks/M2-PROD-SFX-PROBE-1.md:73`；`verification/.../deploy-record.md:34`（+`:35`）；`doc/handoffs/...:14`、`:32` | 四处全部改为「同源同页 + 锚点值 `0.9046694040298462` + conf 差 1.79e-7 在 GPU-EP-1 ≤2e-06 漂移窗口内 + 回归容差 abs=1e-3」，且 Task 明令"位级可复现不得写入任何证据"。我全仓枚举 `逐位一致`：交付面仅余 3 处且**均属实**——① 页文件 sha256 `28dab503…` vs 锚点 `frame_sha256`（同值同域，见 `experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json:9`）；② r0 与 r1fix 的 **DML 同形态** conf 同值 `0.9046692252159119`；③ 权重 sha "逐字一致"=生产 pin。无残留错误陈述。 |
| **C2（P2-1）闭包归属更正** | **CLOSED（主体）** | `packaging/m2ac5/core_sidecar.spec:77-94`（第二份 torch/transformers/doctr 闭包 + `detection_doctr.py:226` 函数体静态 import 机理）、`:97-103`（断言范围注记）；`deploy-record.md:51`；`doc/tasks/...:57`；`packaging/m2ac5/README.md:128` | spec 注释已改为事实口径且明确"断言 onnxruntime 在场 ≠ PYZ 仅 onnxruntime"；Task 追注点明原声明被推翻。**残留 1 处见 P2-R1**：`doc/handoffs/...:39` 仍写 "sfx_detect_probe 8455 modules **onnxruntime 面**"，与同文件 `:67` 的更正自相矛盾。 |
| **C2（P2-2）增量三选一取舍登记** | **CLOSED** | `deploy-record.md:51`；`core_sidecar.spec:86-91`；`doc/handoffs/...:67` | (a) 接受（零产品风险、回退=revert spec 第五行+sanity gate 行）＝集成裁决；(b) core_service 一次性 CLI 模式（0 B）**被拒**，理由=分叉产品主入口启动行为、与"零触碰既有冻结入口"纪律冲突；(c) 瘦身 import 面属产品 src 重构留后续 slice。理由登记完整，我接受该权衡结论。 |
| **C3（P2-3）runner 判据加固** | **CLOSED** | runner `is_frozen()` `:162-165`；SP-L1 判据 `:332-340`（`is_frozen` + 权重 pin + 三键）；SP-L2 判据 `:400-410`（`is_frozen` + 候选>0 + device/sfx_ep + **权重 pin**）；observed `:315`、`:373`、`:390`；`--raw-subdir` 隔离 `:258-262`、`:270` | 新判据进入 PASS 条件（非仅记录）。重跑证据：`packaged-sfx-detect-probe-results-r1fix.json:4` verdict=PASS、4 场景全 PASS、`:26`/`:44` `frozen_in_process=true`、`:34`/`:58` `weights_sha256_matches_pin=true`、`:6` installer `3ffa03f5…`、`:7` build_head `2b4e4946`、`:5` build_venv_note 已填；`raw/r1fix/sp-l2-real-page.log:4` 实测 `frozen: true`、conf `0.9046692252159119`、权重 sha=pin；`raw/r1fix/sp-l3-core-service-ping.log:3-4` ready/stopped。r0 证据未被覆盖（`raw/sp-l1-synthetic.log:2` 仍 wall 2339/elapsed 1846；`raw/sp-l2-real-page.log` 仍 r0 形态；主 `results.json` 仍无新字段=零触碰）。 |
| **C4-P3-1 README 五入口** | **CLOSED** | `packaging/m2ac5/README.md:117-128` | 标题"五个 frozen 入口"+ 表新增 `sfx_detect_probe.exe` 行，并带 P2-1 归属注（"PYZ 含第二份 ML 闭包"）。 |
| **C4-P3-2 SP-L2 判据描述** | **PARTIAL** | `deploy-record.md:80`、`doc/tasks/...:73` 声称判据含"三键在场"；runner `:400-410` | 代码只判 `device`/`sfx_ep` 非空，**仍不检查 `sfx_ep_fallback` 键在场**（SP-L1 `:306-311` 有）。探针本体恒写三键（`src/bootstrap/bootstrap... detection_sfx` 侧 `:737` 与 probe `:287-289`），实际风险≈0，但"描述更新"方向反了 → 见 P3-R2。 |
| **C4-P3-3 range `git diff --check`（特别裁决）** | **CLOSED（实测口径已落盘）** | `raw/r1fix/range-diff-check-delivery.log`（55 行）、`range-diff-check-r1fix-chain.log`（同 55 行）、`range-diff-check-delivery-excl-raw.log`（0 行）；`deploy-record.md:56`、`doc/tasks/...:75`、`:84` | **认可，不持异议**。我独立复核了落盘原文：报错集=5 个文件 27 处 trailing whitespace（`m2ac5-gate-artifacts-thisrun/{ac1-run1×4, ac1-run2×4, probe-stdout×7, r1-library-probe×7}` + `raw/sp-l3×5`）+ **1 处 `new blank line at EOF`（`raw/tauri-build.log:302`，属另一 whitespace 类）**；5 个 trailing 文件我逐行验证确为 CR-at-EOL（`\r` 命中数=行数），唯一无 CR 的 `tauri-build.log` 恰好就是 blank-at-EOF 那条 → git 的判定确为 CR 语义，集成方"CRLF 忠实形态"结论成立，沿 GPU-EP-1 先例豁免、不改证据的处置正确。**我 r1 的"应为空"预期机制性错误**：我的检索式 `[ \t]+\r?$` 要求 CR 前必须有空格/制表符，结构上不可能命中**裸 CR**；权威检查只有 `git diff --check` 本身。仅留 2 处措辞精度 → P4-R4/R5。 |
| **C4-P3-4 base_commit 更正** | **CLOSED** | `doc/tasks/...:11` = `d298ecd0` + 注记；reflog `logs/HEAD:1-3` 佐证；`doc/handoffs/...:5`、`deploy-record.md:4` 三处一致 | 更正说明与 STATUS 释放基点 `72807d30` 的语义区分清楚（同款双值问题在兄弟 Task `doc/reviews/M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md:54` 亦被登记）。仅留 frontmatter 值内嵌长解释的格式瑕疵 → P4-R9。 |
| **C4-P3-5 溯源字段 + page sha 域注记** | **CLOSED** | `r1fix.json:5-7`（venv note/installer sha/build head）；runner `:239-256`（三个新 flag）、`:376-380`（`page_sha256_domain_note` + `page_file_sha256=sha256_file(page)`）；`r1fix.json:47-48` | 保留 r0 `results.json` 原样（证据不可变）+ r1fix JSON 承载 provenance，处置正确。附注 2 条 → P4-R7（字段为 CLI 传入、runner 未实测/校验）与 P4-R8（r1fix 轮无 runner stdout 归档）。 |
| **P4-2 cleared env (0) 注记** | **CLOSED** | `deploy-record.md:27` | 明写"宿主环境本就无该类变量、零干预——非曾存在被剔除"。 |
| **P4-3 envelope minor=3** | **CLOSED** | runner `:186-198`；`raw/r1fix/sp-l3-core-service-ping.log:1-4` | 冒烟信封已用 minor 3（冻结面），实测 ready/stopped。 |
| **P4-4 场景枚举补 CS-A4/A5** | **CLOSED** | `deploy-record.md:41` | 我按 `thisrun/cleanstart-gate.json` 逐 id 复算=**25**（含 CS-A4-restored-reader、CS-A5-export），枚举已补全。 |
| **P4-6 删 dev 冒烟对账句** | **CLOSED** | `deploy-record.md:37` | 明写删除原因（无 raw 落盘支撑）。 |
| **P4-8 page_file_sha256** | **CLOSED** | runner `:380`；`r1fix.json:48` = `28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4` | 与锚点 `frame_sha256`（anchor `:9`）**同字符串**，页身份从"仅路径"升级为"文件级互证"，是比 r0 更强的证明（探针侧实测计算，非抄录）。 |
| **P4-5 双 pin 同步登记** | **CLOSED** | `deploy-record.md:80` | runner 自带 `SFX_WEIGHTS_SHA256` 常量与探针 JSON `weights.expected_sha256` 的两处同步义务已登记。 |
| **P4-1 main.rs/CS-Z3** | **OPEN（登记保持）** | `deploy-record.md:14` | `main.rs:374-379` 注释仍列四入口；`run_clean_start_e2e.py:805-807` CS-Z3 残留名单不含 `sfx_detect_probe.exe`（GATE 不启动第五入口故无影响）。按零 src-tauri diff 纪律留集成侧，合理。 |
| **P4-7 spec 断言串联** | **OPEN（备注）** | `core_sidecar.spec:104`、`:294-295`（r0 行号同位） | 断言以 `SFX_PROBE_ENTRY` 常量串联，改名而常量不改则断言静默不跑；`build_sidecar.ps1:209-213` 名称 gate 为有效兜底，保持备注即可。 |
| **另核：Task `review_events` + §DSH r1 登记** | **PARTIAL** | `doc/tasks/...:14`（review_events r1 已登记）、`:80-84`（登记节齐全，含被推翻预期如实登记） | 登记完整；唯 `:82` 引用的 `doc/reviews/M2-PROD-SFX-PROBE-1-b1dd1ad4-dsh-r1.md` **worktree 与主工作树均不存在** → P4-R3（先例 `doc/reviews/M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md` 存在于 master，说明惯例是集成/合并时归档）。 |
| **另核：deploy-record §5 闭合语义精确化** | **CLOSED** | `deploy-record.md:64`；`doc/handoffs/...:14` | 已按 r1 §4.1 写全三点：闭包面闭合（同一 onedir/同一 in-bundle 权重/同一 provider 装配类）≠「core_service.exe 进程内可达」≠ manga slice，且"后续不得把命令面扩展当作该 NOT_RUN 的既定收敛条件"。 |
| **另核：r1fix 轮改动面与免重跑正当性** | **CLOSED** | `core_sidecar.spec:77-103`（纯注释）、`README.md`（纯文档）、runner（`verification/**` 工具） | r1fix 三 commit 未触 `src/**`、`tests/**`、ENTRIES 结构/`SFX_PROBE_HIDDENIMPORTS` 值，故 r0 的 1835 回归/GATE 25:25/包体积证据继续有效、免重跑构建与 tauri 的处置正当（符合我 r1 §4.6 认可路径）。 |

---

## 3. 分级发现

### P0（阻塞集成）
无。

### P1（必须返修）
无。

### P2（应返修）
**R-1 `doc/handoffs/M2-PROD-SFX-PROBE-1-zcode-20261004.md` 未随 r1fix 轮同步，并残留已被推翻的归属表述**
- `:39` 仍写 "sfx_detect_probe 8455 modules **onnxruntime 面**"，与同文件 `:67`（已按 P2-1 更正为"第二份 torch/transformers/doctr 链"）**同一文档内自相矛盾**；spec/Task/deploy-record/README 均已更正，仅 Handoff 漏改。
- 未同步的其余项：frontmatter `:6` `delivery_head: 33e824e4` 与 `:46`/`:57` head 陈述未映射到实测 tip `4d95a2e7`；`:18-22` commit 链缺 `441f4ab5/f6a25d69/4d95a2e7`；`:28-40` 验证证据表无 r1fix 行（4/4 PASS、`raw/r1fix/`、`-r1fix.json`）；`:38` 仍写"`git diff --check`；…EXIT=0"（deploy-record/Task 已改 range 实测口径）。
- 影响：Handoff 是接收方/后续 Agent 的第一消费入口；仅读 Handoff 会重新传播错误归属、误判 head 与证据集（这正是 r1 P2-1/P3-3 要消除的形态）。一行修正 + 一段 r1fix 追加即可，属文档级。

### P3（应返修）
**R-2 SP-L2「三键在场」仍非代码判据**
- `packaged-sfx-detect-probe.py:400-410` 只判 `device`/`sfx_ep` 非空，**不检查 `sfx_ep_fallback` 键在场**；而 `deploy-record.md:80` 与 `doc/tasks/...:73` 现称 SP-L2 判据为"…+ 三键在场 + 权重 sha256=pin"。
- 处置二选一（建议前者，一行）：在 SP-L2 条件补 `and "sfx_ep_fallback" in result`；或把两处措辞改为"device/sfx_ep 在场 + `sfx_ep_fallback` 记录（探针恒写）"。探针本体恒写三键，实际风险≈0。

**R-3 r1 报告路径为悬空前向引用**
- `doc/tasks/...:82` 写"报告=doc/reviews/M2-PROD-SFX-PROBE-1-b1dd1ad4-dsh-r1.md，集成方导入"，但该文件在本 worktree 与主工作树 `G:\CODEX\New Manga\doc\reviews\` 均不存在（同族先例 `M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md` 已在 master 归档）。
- 处置：在 merge commit 归档 r1（与本 r2）报告，或把 Task 措辞改为"报告由集成方于集成 merge 归档（当前 out-of-band）"。**本 r2 报告同样在会话内交付、未落盘**，请一并归档。

### P4（备注）
- **R-4 P3-3 措辞精度（2 点）**：实报内容宜写"**6 个 raw 文件：27 处 trailing whitespace + 1 处 `new blank line at EOF`（git 输出共 55 行）**"——现行"55 行 trailing whitespace"把输出行数当成错误条数、且把 `tauri-build.log:302` 的 blank-at-EOF 并入 trailing 类；并且 6 个文件中 `tauri-build.log` 与 CRLF 无关（我实测该文件无 CR）。另建议机制表述写"**git blob 层行尾**"：`raw/sp-l1-synthetic.log`、`raw/sp-l2-real-page.log`、`thisrun/cleanstart-gate.json` 工作区同为 CRLF（逐行 `\r` 命中）却**未入报**，说明入报集由 blob 行尾决定，写成"工作区 CRLF"会让按工作区复现的人对不上账。
- **R-5 更正对 DSH r1 方法的归因**：`doc/tasks/...:84` 的"（DSH 静态文本检索抹掉 CRLF 的 CR 所致）"不准确——我的检索式 `[ \t]+\r?$` 要求 CR 前有空格/制表符，**结构上无法命中裸 CR**（并非被"抹掉"）。建议改为"r1 用文本检索核 whitespace（口径为空格/制表符），未覆盖 git 默认 `cr-at-eol` 关闭下的裸 CR，故其'应为空'预期被实测推翻"。
- **R-6 `core_sidecar.spec:66-71` 头部注释未随五入口/事实更新**：仍写"only the production library entry (core_service) carries the detect chain… (the other **three** entries keep their released stdlib+repo closure — do not widen them)"；实际非 ML entry 已有四个，且探针（"other"之一）经 modulegraph 携带 ML 闭包（下方 `:77-94` 已自陈）。建议改为"the other entries take no ML hiddenimports/assertion; note the probe's PYZ nonetheless carries the ML closure transitively — see below"。
- **R-7 "programmatic provenance" 表述过强**：runner `:244-246` 注释称新字段可"bind the probe results to the installer artifact and the build HEAD without relying on out-of-band logs"，但 `--installer-sha256`/`--build-head` 是 **CLI 传入并原样记录**（`:247-256`、`:436-437`），工具不测量、不校验。建议注释改"caller-supplied provenance（与 GATE CS-E2 实测值交叉核对）"或增加 `--installer-path` 让 runner 自算 sha256。
- **R-8 r1fix 轮证据完整性（2 点）**：`raw/r1fix/` 只有 sp-l1/l2/l3 + 3 份 range 日志，缺 runner stdout 归档（对比 r0 的 `raw/probe-runner.log`），4/4 PASS 的 `[PASS]` 行只剩 results JSON；另 3 份 range 日志无命令头/EXIT 标记，`range-diff-check-delivery-excl-raw.log` 为**空文件**（看不出排除 pathspec 与 EXIT=0）。建议补一行命令头（含 range + exclude pathspec）+ `# EXIT=0`。
- **R-9 frontmatter 值内嵌解释**：`doc/tasks/...:11` 把长段更正说明写进 `base_commit` 字段值，可能干扰按 hash 解析 base 的工具/脚本；建议值保持 `d298ecd0`，解释移入正文（§DSH r1 登记节）。
- **R-10 交付目录残留 `__pycache__`**：`verification/M2-PROD-SFX-PROBE-1/__pycache__/packaged-sfx-detect-probe.cpython-312.pyc`（r1 时点不存在，r1fix 轮新增）。`.gitignore:1` 覆盖 `__pycache__/`，故**不会入库**、`git status` 亦不显脏；仍建议清理或用 `python -B` 运行（同类项在 GPU-EP-1 r2 曾以 N-P4-5 清理）。
- **R-11（保持登记）**：P4-1（`main.rs:374-379` 四入口注释 + CS-Z3 名单）与 P4-7（spec 断言的常量串联 + `build_sidecar.ps1` 名称 gate 兜底）状态不变，按集成侧/备注处理即可。

---

## 4. AC1–AC5 复核（r2）

| AC | r1 | r2 复核 | 一句话理由 |
|---|---|---|---|
| **AC1 命令面扩展** | PASS | **PASS（维持）** | r1fix 未触 `src/bootstrap/core_service.py`（`PROTOCOL_MINOR=3`，无 probe 命令）、未触 `doc/contracts/**`、未触 `run_clean_start_e2e.py` 场景集（`SIDECAR_EXES` 仍 4 项、CS-I1 `:231-234` 仍 at-least）；spec/README 改动为注释与文档，ENTRIES 结构不变；AC1③ 不适用维持。 |
| **AC2 frozen 进程内真实运行** | PASS | **PASS（证据面加强）** | 新增 `python.frozen is True` 与 SP-L2 权重 pin 两个**判定面**断言并在既有 GATE 安装态重跑 4/4 PASS（`r1fix.json:26,34,44,58`），页身份升级为文件级 sha 与锚点同值（`r1fix.json:48`）；conf 仍 `0.9046692252159119`、三键 dml/dml/null、elapsed 696ms、权重=pin。唯一扣分项是文档"三键在场"与代码不一致（R-2，非证据问题）。 |
| **AC3 既有面零破坏** | PASS | **PASS（维持）** | GATE 25/25（installer `3ffa03f5…`，`thisrun/cleanstart-gate.json:4,12`）与 M2-AC5 快照/还原证据未被 r1fix 改动；包体积 Δ 计算与归属现已按事实登记（第二份 ML 闭包）并给出三选一裁决；range `diff --check` 由"空转口径"改为实测落盘 + 排除 `raw/**` 后 EXIT=0（豁免经本 r2 认可）。 |
| **AC4 回归与纪律** | PASS | **PASS（维持）** | r1fix 未改 `src/**`/`tests/**`，1835=1823（GPU-EP-1 末轮 `pytest-full-regression-r2run.log:399`）+12 仍成立；`base_commit` 元数据已更正；白名单/禁改面零 diff 结论未受 r1fix 影响（改动面=runner+文档+注释）。残余仅 P3-3 的计数/机制措辞（P4-R4/R5）。 |
| **AC5 文档** | PARTIAL | **PARTIAL → 可转 PASS（附 R-1/R-3）** | 载体齐全、闭合声明已按 r1 §4.1 精确化（`deploy-record.md:64`）、`review_events` 与返修登记节在位；仍判 PARTIAL 的唯一原因=Handoff 残留错误归属+未同步（R-1，P2）与 r1 报告未归档（R-3）。**R-1/R-3 闭合后 AC5 可改判 PASS。** |

---

## 5. 残留风险与集成建议

1. **集成 commit 顺笔闭合清单（预计 1 个 docs commit，无需重跑）**：
   - R-1：Handoff `:39` 归属改事实口径（照 `:67`/spec 措辞）；`:6`/`:46`/`:57` 补 `delivery_head=33e824e4 + r1fix 441f4ab5/f6a25d69/4d95a2e7（tip）` 映射；验证表补 r1fix 4/4 行（`raw/r1fix/` + `-r1fix.json`）；`:38` 换成 range 实测口径 + 豁免说明。
   - R-2：SP-L2 条件补 `"sfx_ep_fallback" in result`（一行），或同步改两处措辞。
   - R-3：归档 r1（及本 r2）报告至 `doc/reviews/`，或注明"集成 merge 归档"。
   - R-4/R-5/R-9：三处措辞/格式更正（计数拆分、机制归因、frontmatter 值清爽化）。
2. **推荐一并落实（低成本、提高可复现性）**：R-6（spec 头部注释）、R-7（provenance 表述或 `--installer-path` 自算）、R-8（r1fix runner stdout + range 日志命令头/EXIT）、R-10（清 `__pycache__`）。
3. **闭合语义的对外表述（维持 r1 §4.1）**：STATUS/Release 记录须保留三点——① 本 Task 闭合的是"**随包 frozen 入口进程内**能跑通生产 `SfxDetectionProvider.detect` 并给三键"（闭包面）；② **不等于** `core_service.exe` 进程内 detect 可达；③ **不含** manga slice（仍 NOT_RUN）。GPU-EP-1 当时预期的"需命令面扩展"路径已被 catalog_loader 先例形替代，建议由 Codex 在集成记录中显式追认该路径差异。
4. **确定性口径纪律（延续 r1）**：DML↔CPU 的末位漂移（本例 1.79e-7）是既有事实，`≤2e-06` 窗口 + 回归 `abs=1e-3` 是正确判据；任何证据不得再写"位级可复现/逐位一致"（除同形态同域比较：文件哈希、DML run-to-run、权重 pin）。本 Task 现存的 3 处"逐位一致"均属此类，可保留。
5. **静态审查边界（集成方复核项）**：本会话无法执行 git，故 `contracts/**`/`src-tauri/**`/`STATUS`/`REBASELINE_PLAN`/GATE 场景集零 diff、以及 r1fix 三 commit 的 `--name-status` 仍未由我实测；建议集成 Gate 落一份 `git diff --name-status d298ecd0..<merge前tip>` 与 `--check` 输出（可与 R-8 合并成一份带命令头的日志）。
