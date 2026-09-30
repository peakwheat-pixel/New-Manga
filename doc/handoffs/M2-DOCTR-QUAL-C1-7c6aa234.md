---
task_id: M2-DOCTR-QUAL-C1
author: ZCode（阶段一 Owner）
recipient: 用户本人（阶段二人工判定）→ 其后 ZCode 汇总、DSH 非作者 Review、代行 Codex 集成
base_commit: 0d4d07a9
delivery_head: 7c6aa234
status: phase-2 delivered, awaiting DSH non-author review
---

# Handoff：M2-DOCTR-QUAL-C1 阶段一（agent 全自动交付）→ 阶段二等待用户人工判定

## 交付结果

两阶段 Task 的**阶段一**全部完成（AC1-AC5 的 agent 可自动部分），Task 停在 `WAITING_USER_LABELING`——这是协议内预期停点，非 BLOCKED。

| AC | 交付 | 状态 |
|---|---|---|
| AC1 导出开关（N2 闭合） | `experiments/M2-DOCTR-QUAL/eval_detection_manga.py` 新增 `--export-frames` / `--export-pairs`（flag 守卫纯附加，判定/评分路径零改动；无 flag 时行为与输出与 C4 逐字节一致） | ✅ RUN |
| AC2 抽样清单（N7 闭合） | `experiments/M2-DOCTR-QUAL/build_spot_audit_sample.py` + `verification/M2-DOCTR-QUAL/spot-audit/spot-audit-sample.{json,csv}`：6 层 50 单元，种子 `20260930` 冻结，B 层 conf 十分位分层明细，同种子重生成逐字节一致 | ✅ RUN |
| AC3 预览图+工作表 | 50 张裁剪预览图（gitignored 外部 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews/`）+ `labeling-worksheet.csv`（**verdict/rationale 列全部为空**）+ `README.md` 判定指引 | ✅ RUN |
| AC4 R7 归档 | `spot-audit/repro-evidence.md`（正式 JSON sha256、集成复跑摘引、导出重跑 raw log 外部+committed 摘要、分母核对表、确定性证据） | ✅ RUN |
| AC5 范围纪律 | diff 仅允许路径（详见下）；已集成文件与 C4 三个正式 JSON 零改动 | ✅ 自检 |
| AC6 阶段二 | **等待用户人工判定**（本 Handoff 的接收动作） | ⏸ WAITING_USER_LABELING |

提交链：`0d4d07a9`（release）→ `efdc07a0`（claim）→ `7c6aa234`（implement）→ 本 Handoff commit。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 行为不变性 | `--limit 8` 冒烟两遍（带/不带新 flag），out JSON 逐字段 diff | C4 隔离 venv（torch 2.11.0+cu128 / transformers 5.17.0）、`7c6aa234` | PASS：0 diff（排除运行元数据），stdout 仅多 2 行 export 行 | 外部 `.../C1/tmp/smoke-*.stdout.txt`；repro-evidence.md §4 |
| AC1 全量导出重跑 | 全量 511 region，cuda，conf 0.5，`--export-frames`+`--export-pairs` | 同上 | PASS：EXIT=0，elapsed=21.7s；rerun vs C4 正式 JSON **summary/per_region/candidate/manifest_sha256 全等（0 diff）**——导出重跑与正式分母同源 | `spot-audit/data/frames-rerun.json`；raw log 外部 `.../C1/logs/export-rerun-stdout.txt` |
| AC2 分母核对 | 抽样脚本内置三源 fail-closed 核对（rerun per_region ≡ 正式 JSON ≡ §7.2 冻结常数） | 同上 | PASS：A1=6、A2=2 region/4 框、B1=78 框/49 region、B2=30/23、D=78（72+6）全一致；**C 实测 2 对 <20 → fallback 全查触发（协议内）** | `spot-audit/repro-evidence.md` §6 |
| AC2 确定性 | `--self-check`（同进程重建两次比对）+ 同参数跨进程重跑 + 异目录无 flag 重跑，三文件 SHA-256 比对 | 同上 | PASS：三个清单文件逐字节一致 ×3 | `spot-audit-sample.json` sha256 `deb3814e…`；外部 `.../C1/logs/sample-run{1,2,3}*` |
| AC3 工作表纪律 | 逐行检查 verdict/rationale 列 | 同上 | PASS：50 行全部为空，无任何 agent 预填 | `spot-audit/labeling-worksheet.csv` |
| AC5 范围 | `git diff --name-only 0d4d07a9..HEAD` + 正式 JSON/已集成文件专项 diff | `7c6aa234` | PASS（见交付时自检记录）：全部变更在允许路径 | 本 Handoff commit 后的最终自检 |

未运行项：AC6 汇总/报告/Review/集成——按两阶段契约等待用户判定，**不属于阶段一范围**。

## 接收方式（给用户：接下来要做什么）

1. 打开判定指引：`verification/M2-DOCTR-QUAL/spot-audit/README.md`（先读，2 分钟）。
2. 打开工作表：`verification/M2-DOCTR-QUAL/spot-audit/labeling-worksheet.csv`（Excel/文本编辑器，UTF-8）。
3. 到预览目录 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews/` 按工作表 `preview_file` 列逐张开图（50 张）。
4. 每行填 `verdict`（该层枚举二选一，原文照抄）+ `rationale`（一句话）；不确定可写「不确定：…」但不可留空；**只填这两列**。
5. 填完后在会话中交付工作表路径（说「labeling-worksheet.csv 已填完」即可）→ 阶段二启动：ZCode 汇总出 `c1-spot-audit-report.md` → DSH 非作者 Review → 代行 Codex 集成。

复现命令（如需核验）：见 `spot-audit/repro-evidence.md` §3/§5（C4 隔离 venv 路径、全量导出与清单重生成命令原样可跑）。

## 下一任务建议（必填）

- Task ID / 标题：M2-DOCTR-QUAL-C1 阶段二（同一 Task，无需新建）
- 推荐 Agent / Reviewer：Owner=ZCode（汇总报告）；Reviewer=DeepSeek Harness（非作者）；Integrator=代行 Codex
- 推荐原因与前置依赖：**前置=用户交付填写完毕的工作表**（阶段二启动条件，Task 契约明文）
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`agent/zcode/M2-DOCTR-QUAL-C1`；worktree=`G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode`；delivery head=`7c6aa234`（+本 Handoff commit）
- 允许修改路径：`verification/M2-DOCTR-QUAL/spot-audit/**`（汇总产物 + 用户填毕的工作表副本）、`doc/tasks/M2-DOCTR-QUAL-C1.md`、新 Handoff、STATUS
- 禁止范围与新增授权条件：不得改动用户填写的 verdict/rationale 内容；不得改动阶段一清单/导出数据；报告对 FAIL 分支（大量真实漏检）必须如实呈现，不得粉饰
- 交付物：`verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md`（分层统计、盲区率校准、C4 Gate 结论真实目标重解读）
- 验证命令、环境与完成 Gate：汇总脚本（阶段二释放时定）重算统计与工作表一致；DSH Review 通过；Codex 集成验证
- 可直接转发给 Agent 的指令：**当前无可转发指令——等待用户人工判定**（用户交付工作表后，向 ZCode 发出：「阶段二启动：工作表在 <路径>，按 Task 契约 AC6 汇总出 c1-spot-audit-report.md，走 DSH Review 与集成」）

## 风险与遗留

- C 层仅 2 对（fallback 全查）：§5.2 同源性直接检验的样本量极小，报告须如实限定该层结论强度（meanCov 0.9965 的反面即贴合对稀缺，本身是 C4 结论的支撑性观察）。
- FN-partial 27 框（23 个部分命中 region）在冻结 6 层协议之外：已导出留证（frames-export.json 标记 `FN-partial`）未入清单；若用户判定显示问题集中于此，可作为后续 Task 候选交 Codex 裁决，本 Task 不扩权。
- A2 与 B1 框级重叠（K07 r109/K08 r3 的 4 框同属 B1 分母 78 框）：抽样命中 B1-U11 已标注；两判定单元视角不同（region 级错位 vs 单框 FP），无冲突。
- 判定对象为版权素材：预览图与 raw 日志均落 gitignored 外部路径，入库仅文本证据。

## 实验附录（仅实验任务）

- 数据来源与许可：KO webtoon 伪 GT 评测集（`noncommercial_research_source_restricted`，与 C4 相同 manifest `4f16425a…`）；预览图为其衍生的标注裁剪图，仅落 gitignored 外部路径不入库。
- 模型/权重：ogkalu/comic-text-and-bubble-detector（RT-DETR-v2，Apache-2.0），权重 SHA-256 pin `037930a8…`，C4 隔离 venv（`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`，torch cu128 + transformers 5.17），cuda。
- 参数：conf 0.5、生产 pad（strip_block_pad=0）、生产 merge（MERGE_PAD_PX=6）、iou_match_threshold/severe 定义取冻结 thresholds.json；抽样种子 `20260930`（每层子种子 `f"{SEED}/{layer}[…]"`）。
- 运行次数：全量导出重跑 ×1（EXIT=0，21.7s）；冒烟 ×2；清单生成 ×3（一致性验证）。
- 原始结果：`spot-audit/data/{frames-rerun,frames-export,pairs-export}.json`（与 C4 正式 JSON 0 diff 同源证明见 repro-evidence.md §3）。

---

# 阶段二（2026-09-30 追加）：人工判定汇总完成 → 待 DSH 非作者 Review

## 审核结果

用户 50/50 单元逐条人工审核完成（判定权威=用户本人）。执行流程：AI 初判预填（GLM-5.3-flash 视觉直读，草稿留存 `labeling-worksheet-ai-draft.csv` 作对照证据）→ 用户逐单元看图审核 → 编排会话写入正式工作表。**46 行采纳 AI 初判**（经逐条审核采纳，rationale 保留 `[AI]` 前缀）+ **3 行人工修订**（`[人工修订]`/`[人工修订确认]` 前缀 + `user_rationale` 列记录用户裁决依据，全部朝该层更严格方向）；**1 行 r2 集成澄清**（B1-U11，DSH r1 R1，非用户人工修订）。用户此前独立判定过的 4 张（A1-U05/A1-U06/A2-U02/B1-U01）与 AI 初判 4/4 一致（来源=本会话记录，R10 更名：非标注者间一致性）。流程差异（阶段一契约原定「工作表留空」）已按 R7 登记：用户授权原文入 Task 禁止范围条款（AI 预填 → 用户逐条审核为最终判定），人工审核为最终判定权威。

## 3 处人工修订明细（r2 更新：另含 1 处集成澄清）

| 单元 | AI 初判 | 终判 | 依据（rationale 摘要） |
|---|---|---|---|
| B1-U10（K07 r127） | 盲区 FP | **模型幻觉**（用户人工修订） | T 恤红色标签上小字无具体形状、语义不可辨，不可辨认为可读文字（R4 澄清后自洽表述；真值以用户裁决为准） |
| C-U01（K01 r35，coverage 0.5568） | 真匹配 | **粒度不达标**（用户人工修订） | 检出完整盖住标题行「ART X vol.2」，但 GT 含下方两行小字，检出只盖 GT 的 56%——贴合非伪造，切分不完整（user_rationale 入表） |
| C-U02（K03 r91，coverage 0.5160） | 真匹配 | **粒度不达标**（用户人工修订） | GT 两段真实对白，检出只盖上半段；下半段被另框检出但一对一匹配落选（切分差异非漏检，R8 更正）——用户原话「下面的画面对话没识别」 |
| B1-U11（K08 r3，conf 0.9161） | 盲区 FP | **粒度不达标**（r2 集成澄清，DSH r1 R1） | 检出落在已标注 GT 合并块内（两段对白均已标注）=切分重复检出非盲区；跨层同源 A2-U02，同一物理检出只计一次 |

## 汇总统计（脚本 `summarize_c1_spot_audit.py` r2 计算，EXIT=0）

终版分布（n=50）：盲区 FP 25 / 伪 GT 噪声 7 / GT 盲区帧 5 / 一致帧 5 / 模型幻觉 4 / 粒度不达标 4（4 单元=3 处独立位置，K08 r3 跨层计 2 单元）；**「真实文字漏检」=0**。三条校准结论（方向性证据，R3）：①Recall 分母 8/35（A1/A2 全查域）=7 噪声+1 粒度+0 真实漏检→与「0.9618 对真实对白低估」方向一致（域内修正估计 0.9692–0.9703；FN-partial 27 未校验不外推，R2）；②Precision 0.8909 与污染下界方向一致（抽检 30 FP 中 n_eff=29：盲区 FP 25、真幻觉 4；保守修正 0.9149、外推 0.9839，均只依赖幻觉数不受 R1 影响）；③D 层 GT 盲区率 5/10（全部 SFX/屏幕小字，无一对白）。C 层 2/2 粒度不达标——同源性疑虑收窄为「贴合非伪造，但低 coverage 匹配存在系统性切分差异（方向=模型偏细粒度）」。Gate PASS 真实世界重解读（方向性）：**「PASS=对真实对白文字检测能力的保守下界」与全部可校验证据一致**；反方向限定 7 条（含 R3 新增锚定效应未测量）见报告 §5.2。

## 报告指针

- 核心交付：`verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md`
- 正式判定表：`verification/M2-DOCTR-QUAL/spot-audit/labeling-worksheet.csv`（用户审核后版）；对照证据：同目录 `labeling-worksheet-ai-draft.csv`
- 汇总脚本：同目录 `summarize_c1_spot_audit.py`（复现：`python verification/M2-DOCTR-QUAL/spot-audit/summarize_c1_spot_audit.py`，EXIT=0 含四项纪律校验）

## 下一步（DSH 非作者 Review → 代行 Codex 集成）

- Task ID / 标题：M2-DOCTR-QUAL-C1 阶段二 Review 与集成（同一 Task，状态已置 `in_review`）
- 推荐 Agent / Reviewer：Reviewer=DeepSeek Harness（非作者静态审查；ZCode 为汇总作者，不得自审）；Integrator=代行 Codex
- 推荐原因与前置依赖：阶段二汇总已交付且脚本自检 EXIT=0；Review 对象=报告统计口径、三条校准结论的计算正确性、方法论披露与 C4 只读产物的零触碰
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`agent/zcode/M2-DOCTR-QUAL-C1`；worktree=`G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode`；delivery head=阶段二 commit（见 git log）
- 允许修改路径：`verification/M2-DOCTR-QUAL/spot-audit/**`、`doc/tasks/M2-DOCTR-QUAL-C1.md`、本 Handoff（Review 意见按协作协议走独立 Review 产物）
- 禁止范围与新增授权条件：不得改动用户判定的 verdict/rationale 内容；不得改动 C4 三个正式 JSON 与 c4-manga-domain-report.md、license-evidence.md；不得改动阶段一清单/预览引用/repro-evidence；STATUS 由编排会话统一维护
- 可直接转发给 DSH 的指令：「对 M2-DOCTR-QUAL-C1 阶段二做非作者 Review：读 doc/tasks/M2-DOCTR-QUAL-C1.md（AC6）、verification/M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md，核对报告统计与 labeling-worksheet.csv 一致性（重跑 summarize_c1_spot_audit.py 应 EXIT=0 且数字可复现）、三条校准结论计算、C 层与同源性表述的诚实性、反方向限定完整性；产出 Review 报告后交代行 Codex 集成」

---

# r2 返修记录（2026-09-30 追加）：DSH r1 changes_requested（R1-R14）逐条处置完成

DSH 非作者 Review r1：**changes_requested**（0×P0、4×P1、4×P2、4×P3、2×P4；三条校准结论算术全部 PASS），全文见 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/dsh-review-r1.md`。Owner（ZCode）在 worktree 内完成 r2 返修（全部为文本/分类修订，无重抽样、无评测重跑）。

## R1-R14 处置对照

| 项 | 处置 | 落点 |
|---|---|---|
| R1（P1）B1-U11 重分类 | 盲区 FP→**粒度不达标**（检出落在已标注 GT 合并块内=切分重复检出；跨层同源 A2-U02 只计一次）；B 层枚举纪律就此一例让位于事实正确性（报告 §1 声明）；3.b 重算：盲区 FP 25/30、**n_eff=29**、幻觉 4 不变 | CSV、报告 §1/§3.b、脚本（枚举扩展+n_eff） |
| R2（P1）分母域 | Recall 结论域收窄为 **A1/A2 两层（8/35）**，FN-partial 27 不外推；「剩余空间更小」降为「在可校验范围内更小」 | 报告 §3.a/§5.1/§8、脚本文案 |
| R3（P1）锚定+强度 | §5.2 增第 7 条「锚定效应未测量」；全文「确认」降为「方向性证据/与…一致」；§2 写入 directional evidence 裁定 | 报告 §0/§2/§3/§5/§8 |
| R4（P1）B1-U10 自洽 | rationale 改「[人工修订确认] 用户裁决=模型幻觉（小字无具体形状、语义不可辨）」，消除与「非纯图形装饰」的矛盾；verdict=幻觉不变、幻觉数 4 不变、0.9149/0.9839 不变；**集成记录再次向用户披露** | CSV、报告 §1/§4 |
| R5（P2）用户裁决入表 | CSV 新增 `user_rationale` 列（3 行人工修订各记录用户裁决依据；C-U02 引用户原话） | CSV、报告 §4 |
| R6（P2）脚本校验补实 | draft-diff 补 unit_id 集合 + layer/case/region/description/preview_file 逐字段比对 fail-closed；A1/A2 完全划分接入 failures | summarize_c1_spot_audit.py |
| R7（P2）授权登记 | Task 禁止范围条款修订为「agent 不得生成未经用户逐条审核的最终判定」+ 用户授权原文要点登记；AC3 证据行改写为与实际交付一致 | doc/tasks/M2-DOCTR-QUAL-C1.md |
| R8（P2）C-U02 表述 | rationale 更正为「下半段被另框检出但一对一匹配落选（切分差异）」（frames-export.json K03 r91 det#1 佐证）；报告 §1 同步 | CSV、报告 §1 |
| R9（P3）stricter 映射 | 逐层显式映射（A1=真实文字漏检、A2/C=粒度不达标、B1/B2=模型幻觉、D=GT 盲区）+ 纳入 failures | 脚本 |
| R10（P3）旁证更名 | 「标注者间一致性」→「用户历史判定 vs AI 初判一致率（来源=本会话记录）」 | 报告 §2 |
| R11（P3）哈希与 commit | 报告 §7 补正式表/草稿/清单/脚本 sha256 + base/release/claim/implement/阶段一 head 对应表 | 报告 §7 |
| R12（P3）AC6 时点 | AC6 勾选退回 `[ ]`（待 DSH 复审+集成闭合，已注明）；**C4 报告 cross-reference（§5.2 限定已由 C1 收窄）超本 Task 权限，转交代行 Codex 在集成时处理** | Task、本 Handoff |
| R13（P4）tie-break note | sample JSON `b_layer_stratification_N7` 增 `tie_break_note`（units payload 零改动；去 note 重生成即阶段一逐字节版本） | spot-audit-sample.json |
| R14（P4）表述微差 | Task「70 个左右」→「50（C 层 fallback 全查）」；报告 §5.1 severe 行补 D 分母含 6 个 A1 region 注；README 示例文件名改用真实文件 `B1-U09__K07_R007.png` | Task、报告、README |

**不改项确认**：用户 3 行人工修订的 verdict 方向（B1-U10 幻觉、C-U01/C-U02 粒度不达标）与 A 层全部判定零改动；正式 CSV 除 B1-U11 重分类（R1）与 R4/R8 rationale 澄清外不动；C4 三个正式 JSON、c4-manga-domain-report.md、license-evidence.md、阶段一 repro-evidence.md 零触碰。

## 下一步（更新）

1. **DSH r2 复审**（同一 Reviewer 会话）：核对 R1-R14 闭合清单——重跑 `summarize_c1_spot_audit.py` 应 EXIT=0 且输出 25/30、n_eff=29、0.9149/0.9839；核对 CSV B1-U11/B1-U10/C-U02 行与报告 §1/§3.b/§4 一致。
2. 复审通过后 **交代行 Codex 集成**：Task 置 done + AC6 闭合；同步在 C4 报告或索引加一行 cross-reference（R12：§5.2 同源性限定已由 C1 收窄，避免读者误认为限定仍开放）。
3. B1-U10 真值（用户裁决=模型幻觉）已按 R4 落表；集成记录中再次向用户披露该裁决依据。
