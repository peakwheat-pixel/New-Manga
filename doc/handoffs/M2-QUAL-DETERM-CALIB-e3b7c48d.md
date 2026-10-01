---
task_id: M2-QUAL-DETERM-CALIB
author: ZCode
recipient: Codex（转发 DeepSeek Harness 非作者 Review）
base_commit: 8e0de8d0
delivery_head: e3b7c48d
status: delivered  # 待 DSH 非作者 review → Codex 集成；集成通过后 Task 方可 done
---

# Handoff：M2-QUAL-DETERM-CALIB（F5 确定性 Gate 重定义校准）

## 交付结果

- **续接说明**：本 Task 续接前一个熔断 agent 的半成品。接手时已存在未跟踪的 `experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` 草稿（含从 summary 提取译文对与 Levenshtein 相似度的主体逻辑，但从未成功运行）；未做：跑脚本、阈值建议落盘、权威口径修订、handoff、Task 回填、commit。本轮全部完成。
- **对半成品的修正**（详见 Task 交付记录与 commit message）：
  1. `main()` 内 `global SUMMARIES_DIR, OUT_DIR` 声明晚于 `argparse` 对全局的引用 → SyntaxError，脚本无法运行；已修（global 前置）。
  2. 补**浮动对子集统计**（AC1/AC2 的锚数字）：按各口径 `similarity < 1.0` 定义（不能用 `status=="variant"`——那是 raw 串比较，K11 ro=5/10 属 raw 浮动但 normalized=1.0，不得混入 normalized 浮动子集）。
  3. 修正合成探针判定语义：`single_char_ge4` 探针强制全部对浮动，其完整 gate FAIL（median=0.857）与草稿报告文字「单字替换保持 PASS」矛盾；现拆为 **min-leg（逐对 ≥0.70 → PASS，证明阈值容纳实测浮动量级）与完整 gate（median leg FAIL，演示全 region 系统性浮动被抓）** 双维度判定，报告文字与表格一致。
  4. 修正 median gate 边界推导数学（草稿版「~45% 浮动时 median≈0.83」不成立）：以实测浮动幅度 [0.75, 0.875] 计，18 对中浮动 ≤8 对 → median 恒=1.0；浮动 ≥9 对 → median ≤(0.875+1)/2=0.9375 <0.95 恒 FAIL。
- **交付物**（commit `e3b7c48d`，6 files，+1338/−7）：
  - `experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（stdlib、确定性、seed 固定、对齐失败 fail-closed）
  - `verification/M2-QUAL-DETERM-CALIB/calibration.json`（机器可读）+ `calibration.md`（逐对清单+分布+阈值推理+局限）
  - `verification/M2-TA3-B/quality-thresholds.md` §5 双轨条目 + F5 修订注、§7 总表第 10 行（AC3）
  - `verification/M2-TA3-B/phase2-plan.md` §1 交付物 / §2.1 确定性复跑 / §4 步骤 5（AC3 同步）
  - `doc/tasks/M2-QUAL-DETERM-CALIB.md` frontmatter `status: ready → delivered` + 交付记录段

### AC 对照

| AC | 结果 | 落点 |
|---|---|---|
| AC1 校准数据 | 完成 | 脚本 + calibration.json/.md；reading_order 对齐（reading_order 集合不一致即 fail-closed 退出）；双口径 raw/normalized；空对规则登记（双方空=1.0、单方空=0.0，实测仅出现双方空：K11 ro=9 OCR 空、ro=13 SFX SKIP） |
| AC2 阈值建议 | 完成 | **median ≥ 0.95 且 min ≥ 0.70（normalized 口径）**，推理全部锚定实测分布（见下），语义边界（翻译稳定性 ≠ 渲染/导出复现性）与 BJ02 上界参照写入 calibration.md §5 |
| AC3 权威口径修订 | 完成 | thresholds §5/§7 superseded-pending → 双轨新口径（remote=相似度 Gate；mock/deterministic=export 字节逐位，原口径保留）；phase2-plan 三处条目同步；修订来源标注「M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01『全部进行』」；其他阶段阈值数值零改动 |
| AC4 局限登记 | 完成 | calibration.md §6 五条：n=2 校准、无自然 FAIL 样本（判别力为合成对照演示）、极短译文粒度边界（3 字串单字浮动 0.667 会被 min gate 误报，fail-closed 方向）、Run1 层相似度未测（K11 export 根因未逐层隔离，不在本 Gate 范围）、归一化口径依赖（K11 浮动 raw 7 → normalized 5）；calibration.json `limitations` 同步 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 脚本可运行且确定性 | `python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（两次运行输出一致，无网络/无随机源——合成探针 seed=20261001 固定） | Python 3.12 stdlib；worktree HEAD e3b7c48d | PASS | calibration.json / calibration.md |
| AC1 K11 观察复现 | raw 口径 K11 浮动 **7/11 非空对**（quality-report F5 定案分母——dsh r1 R12 对齐：raw 全部对口径 7/13 仅为内部附报，不复引已修正的混用分母） | 同上 | PASS（与 quality-report F5 已登记观察一致） | calibration.md §2/§3 |
| AC2 实测分布 PASS | K11 → PASS、BJ02 → PASS（normalized median=1.0 ≥0.95，min=0.75 ≥0.70） | 同上 | PASS | calibration.md §2/§4.4 |
| AC2 判别力对照 | 合成探针：single_char_ge4 逐对 min=0.75 → min-leg PASS、median leg FAIL（全浮动场景）；drift_40 min=0.5、drift_70 min=0.2 → FAIL | 同上 | PASS（演示闭环成立；非自然 FAIL 实证） | calibration.md §4.3 |
| AC3 superseded-pending 解除 | `grep -n "superseded-pending" verification/M2-TA3-B/quality-thresholds.md` → 仅剩修订注内「解除」表述（历史引用） | 同上 | PASS | thresholds §5/§7 |
| 禁改面 | `git status --porcelain`（commit 后干净）+ commit 文件清单核对：无 `src/**`、`tests/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`、`doc/STATUS.md`；`qual-*.json` 等 TA3-B2 产物零改动（脚本只读） | 同上 | PASS | `git show --stat e3b7c48d` |
| 未运行项 | 未重跑 TA3-B2 qualification（本 Task 只复用已有产物校准，AC 无此要求）；未在真实 mock 链上执行双轨 Gate（runner 属未来 qualification run） | — | NOT_RUN（理由如左） | — |

**关键数字**（normalized=Gate 口径）：18 对（K11 ko 13 + BJ02 ja 5）；浮动对 6/18，全部为 1 次编辑差，幅度 [0.75, 0.875]；**K11 浮动对 n=5、min=median=0.75**（raw 口径 7/11 非空对浮动=复现 F5 观察；ro=5 换行位移、ro=10 空格差异被 §0 归一化吸收）；BJ02 浮动 1 对（`所谓强大`→`所谓强啊`，0.75）——其 Run1 渲染产物两次逐位相同=上界参照。全部对口径 median=1.0、min=0.75。

## 接收方式

- 分支 `agent/zcode/M2-QUAL-DETERM-CALIB`，worktree `G:/CODEX/New Manga.worktrees/M2-QUAL-DETERM-CALIB-zcode`，base `8e0de8d0`，delivery `e3b7c48d`（勿切分支/勿 reset）。
- 复现：`python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（可加 `--summaries-dir/--out-dir`，默认路径即仓库内）。
- Reviewer 检查建议：①核对 calibration.md §4 推理链与 §3 逐对清单数字一致性；②核对 thresholds §5/§7 修订未动其他阈值行（`git diff 8e0de8d0..e3b7c48d -- verification/M2-TA3-B/quality-thresholds.md`）；③审阅 min=0.70/median=0.95 的锚定逻辑与 n=2 局限表述是否足够保守。

## 下一任务建议（必填）

- Task ID / 标题：无新 Task——本 Task 进入 DSH review → Codex 集成流程（review 对象=e3b7c48d）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 Review）→ Codex 集成。
- 推荐原因与前置依赖：依赖本 delivery；F5 口径已按用户裁决 2026-10-01 落地，review 通过即可集成关闭。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch/worktree 如上；head=e3b7c48d。
- 允许修改路径：review 报告 `doc/reviews/`；集成修正限于本 Task 允许面（`experiments/M2-QUAL-DETERM-CALIB/**`、`verification/M2-TA3-B/**` 的 thresholds/plan 修订、`verification/M2-QUAL-DETERM-CALIB/**`、Task/Handoff）。
- 禁止范围与新增授权条件：同 Task 禁改面（`src/**`、`tests/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`、`doc/STATUS.md`、TA3-B2 已交付 run 产物 JSON）。
- 交付物：DSH review 报告；集成记录（含 STATUS Active Task 更新——STATUS 在本 Task 禁改面，须由集成方/Codex 更新）。
- 验证命令、环境与完成 Gate：上表复现命令 + `git diff --check` EXIT=0；完成 Gate=DSH 非作者 review 通过 + Codex 集成验证。
- 可直接转发给 Agent 的指令：
  > 对 M2-QUAL-DETERM-CALIB @e3b7c48d（worktree `G:/CODEX/New Manga.worktrees/M2-QUAL-DETERM-CALIB-zcode`）做非作者 Review：按 `doc/handoffs/M2-QUAL-DETERM-CALIB-e3b7c48d.md` 验证证据表逐项复核（重跑校准脚本核对 calibration.json/.md 数字；核对 thresholds §5/§7 与 phase2-plan 修订 diff 未动其他阈值；审阅 0.70/0.95 阈值锚定推理与 n=2 局限登记）。报告写 `doc/reviews/M2-QUAL-DETERM-CALIB-e3b7c48d-dsh-r1.md`。

## 风险与遗留

- **阈值 0.70/0.95 为 n=2 directional 校准**：仅锚定 18 对实测分布（浮动全为 1 编辑差），不支持生产结论外推；后续 qualification run 应同时落盘逐对相似度以滚动校准（calibration.md §6.1）。
- **极短译文粒度边界**：3 字及以下译文出现良性单字采样差（≈0.667）会被 min gate 判 FAIL（fail-closed 方向）；实测最短浮动串 4 字（§6.3）。
- **Run1 层确定性未解决**：K11 export 哈希不一致的根因（批量翻译/inpaint/render 之一，未逐层隔离，scratch db 已清理）不在本 Gate 范围；若需追责渲染/导出层复现性，须另立 Task（§6.4）。
- **归一化口径依赖**：若产品语义认定换行位置属译文的一部分，应引用 raw 口径附报（§6.5）——此为产品语义取舍，归用户裁决。
- 回退方法：revert `e3b7c48d` 即回到 base `8e0de8d0` 状态（含 thresholds/plan 修订一并回退）；无数据迁移、无外部副作用。
- 关联：M2-TA3-B2（数据源与 F5 裁决来源）、M2-TA3-A（mock 链字节逐位口径原出处）。

## r1 返修记录（DSH r1 approved_with_conditions，2026-10-01，R1-R14 逐条落点）

DSH r1 评审：`G:/CODEX/New Manga.task-envs/M2-QUAL-DETERM-CALIB/dsh-review-r1.md`。逐条处置（脚本类条目已重跑校准，**统计量逐值一致**：18 对、cases/aggregate 全部 distribution、三个合成探针、逐对 similarity/status、gate verdicts——与返修前 JSON 程序化对比零差异）：

| # | 级别 | 处置 | 落点 |
|---|---|---|---|
| R1 | P2 | **closed**：对齐逐 reading_order 断言两 run bbox 逐字段一致（不一致走同一 SystemExit FATAL 通道）；键集合相等无法检测同集合置换，bbox 是跨 run 唯一可用几何恒等（K11 13/13、BJ02 5/5 实测一致）。calibration.md §1.1 登记该假设与校验 | calibrate_determinism.py（build_pairs）+ calibration.md §1（脚本产物重跑生成） |
| R2 | P2 | **closed**：Gate 判定加覆盖前置——非空对 n≥1 方可判定，否则 NO_DATA（`case_gate_verdict`）；全空跑在相似度口径下平凡 PASS 的盲点由此闭合。关系句写入 thresholds §5 remote 行：「全空跑可 PASS 相似度 Gate，由 §7 translate 评分 Gate 兜底」；calibration.md §1.4 + §6.6 局限登记 | calibrate_determinism.py + thresholds §5 + calibration.md |
| R3 | P2 | **closed**：thresholds §5 补「region_count=0 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径），不阻断整体 Gate 但单独登记」；注明本次校准未覆盖 ko webtoon 家族（K01 两侧均 0 region；K11=ko P&C、BJ02=ja BJ） | thresholds §5 + calibration.md §1.4/§6.6 |
| R4 | P2 | **closed**：calibration.md §4.1 与脚本 reasoning 的「一个字符级余量」改为「**0.05 绝对值余量**」（与 thresholds 写法统一：4 字锚串 1 编辑差=0.25，0.05 仅为其 1/5）；§6.3 扩「长度相关悬崖」+ 4 字反例（2 编辑 → 2/4=0.5 FAIL） | calibrate_determinism.py（render_markdown + reasoning）+ calibration.md §4.1/§6.3 |
| R5 | P3 | **closed**：median 边界句限定「**在本校准样本的译文长度分布下**（浮动串长 4–16 字，幅度 [0.75, 0.875]）」；§6.7 局限登记「median 腿对低幅系统性漂移的分辨力随译文长度下降（20 字串 1 编辑差=0.95≥阈值，全 region 低幅浮动场景 median 腿可能 PASS，min 腿兜底）」 | calibrate_determinism.py（render_markdown §4.2）+ calibration.md §4.2/§6.7 |
| R6 | P3 | **closed**：抽 `is_nonempty(pair)` 供 case 级（build_pairs）与 aggregate（main）非空子集共用；`pair_status` 判空基准与 `similarity` 统一为 **normalize 后空串**（status 与 similarity 不再可能在仅空白差异上矛盾）。重跑零数字变化（当前空对恰为 ""） | calibrate_determinism.py |
| R7 | P3 | **closed**：①translate_details 必须覆盖全部 regions[]（否则 SystemExit，dropped reading_orders 落盘于 FATAL 消息）；②`order[detail["region_id"]]` 改显式缺失检查走同一 FATAL 通道（不再裸 KeyError）；③case 产物落盘 n_regions/n_translate_details/n_dropped_regions（两 run）——重跑实测 dropped=0 | calibrate_determinism.py + calibration.json |
| R8 | P3 | **closed（登记，探针不加）**：§6.8 局限登记词面口径固有误报方向——语义等价的合法重译（同义改写/整段重译，即 remote 漂移主形态）会被判低相似度 FAIL，Gate 在保守（假 FAIL）方向系统性偏置；同义改写代理探针**不加**并在局限中登记理由（词面框架内无法可靠构造确定性语义等价代理，需回译/向量相似度等语义度量，属后续独立工作） | calibrate_determinism.py + calibration.md §6.8 |
| R9 | P3 | **closed**：thresholds §5 尾注补可执行双轨判别规则——按 run 的 translate provider 绑定判轨（remote 采样 `deepseek/*` 等 → 相似度轨；mock/确定性 → 哈希轨），qualification runner 以 `--determinism-track remote|mock` 显式记录，声明与绑定不一致 fail-closed | thresholds §5 尾注 |
| R10 | P3 | **closed**：quality-report.md :189/:199 两条历史 superseded-pending 引用加关系注「已由 M2-QUAL-DETERM-CALIB + 用户裁决『全部进行』于 2026-10-01 落地解除」（该文件在本 Task 允许面 verification/M2-TA3-B/** 内；:199 注明 F4 部分仍待其自身 Task） | quality-report.md |
| R11 | P3 | **closed**：Task AC3 行改为实际修订面（thresholds §5 双轨条目+尾注 / §7 总表第 10 行；phase2-plan §1/§2.1/§4）并注明「§1 核对为空（R9 原注不在 §1）」 | doc/tasks/M2-QUAL-DETERM-CALIB.md |
| R12 | P4 | **closed**：本 handoff 验证证据表 AC1 行分母措辞对齐 quality-report 定案——「raw 口径 K11 浮动 7/11 非空对」（7/13 全部对口径仅作内部附报，不复引已修正的混用分母） | 本 handoff 验证证据表 |
| R13 | P4 | **closed**：calibration.json `calibration_source.summaries_dir` 改为相对仓库根路径（`verification\M2-TA3-B\phase2\summaries`；跨 checkout 可复现，非 `is_relative_to` 时回退绝对路径）；脚本重跑生成 | calibrate_determinism.py + calibration.json |
| R14 | P4 | **closed**：Task frontmatter 加 `fork_commit: 8996ca55` 注记（e3b7c48d 父提交=8996ca55，与 Task A 同一拓扑事实） | doc/tasks/M2-QUAL-DETERM-CALIB.md |

返修后验证（Python 3.12 stdlib，worktree 内默认路径）：

- 重跑 `python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` → 18 对（K11 13 + BJ02 5）、全部分布统计量/探针/verdict 与返修前**逐值一致**（程序化对比零差异）；gate verdicts K11=PASS、BJ02=PASS 不变。
- JSON 预期结构差异仅三类（均为返修要求）：`summaries_dir` 相对化（R13）、case 级 coverage 字段（R7）、method/limitations 文本增强（R1/R2/R4/R5/R8）。
- `qual-*.json` 等 TA3-B2 产物零改动（脚本只读，porcelain 复核见返修 commit）。
