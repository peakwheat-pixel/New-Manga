## verdict: APPROVED_WITH_MINOR_ISSUES —— 准予进入集成（FAIL 结论与冻结口径逐项相符）；P1 仅 1 项集成裁定项，P2/P3 为报告数值与可复现性修正，均不改变正式结论

**审查方式声明（沙箱限制）**：本会话 `pwsh` 不可用（每次调用均以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` 失败），**未执行任何命令**，也未用 Python 复算。全部取证为只读静态：`read` / `glob` / `grep` + `.git` 元数据文件（`.git/HEAD`、`.git/refs/heads/main`、`.git/refs/heads/agent/zcode/M2-DOCTR-QUAL-RUN`、worktree `.git` 指针）。数值核对以"行号对齐读取 + grep 计数"完成，下文所有计数均可按同一方法复现。

基线核验：`.git/refs/heads/main = 5b3a477a371a662288998f86d23ae56439179524`（与 Task base 完全一致，且主仓工作区即 base 快照，因此主仓文件可直接充当 base 侧对照）；`.git/refs/heads/agent/zcode/M2-DOCTR-QUAL-RUN = eb01cd76989d6e95ee059d39e2c1b4138267f5e2`（= 分支头，与派发信息一致）。

---

## P0–P3 清单

### P0（阻断）：无

### P1

**P1-1（集成裁定项，非本交付缺陷）：必须"接受 `f9894184`"而不是 revert，否则 master 上 runner 与冻结口径永久互斥。**
- 事实：`thresholds.json` 在 base `5b3a477a` 已是裁决后嵌套 `gates` 契约（主仓与 worktree 两份文件逐字相同，20 行），而 base 的 `eval_detection.py` verdict 段仍读扁平 `THRESHOLDS["min_recall"]`（`G:\CODEX\New Manga\experiments\M2-DOCTR-QUAL\eval_detection.py` L375/380/385）。即 base 上"冻结口径 + 交付 runner"必然崩溃——这正是 `raw/formal-run1-*.log` 的 `KeyError: 'min_recall'`、EXIT=1。
- 影响：若集成方把 P1 误判为"越权改动"而 revert，则主仓 `eval_detection.py` 对现行 `thresholds.json` 100% 不可运行，且 `README.md` 的 preflight 复现命令（L36-40）同样失效。
- 处置建议：接受 `f9894184`（其测量逻辑零改动已由我独立确认，见角度 B），并把"runner 与阈值契约单一化"记入集成说明；如需回退，必须同时回退 `thresholds.json` 或另提修复，不得只 revert runner。

### P2

**P2-1（报告 §6 数值自相矛盾，实测应为 314 而非 312）。**
报告 L100："fail to cover … in **312/416** regions; only **102/416** regions are fully matched" —— 312+102=414≠416。用证据反推：`"fn_block_coverage": 0` 在 `results-formal-fast_base-cuda-seg05.json` 中共 **197** 处，其中零 GT region 为 **95** 处（`"n_gt": 0` grep 计数=95，与 511−416=95 吻合；零 GT region 的 fn 恒为 0），故完全匹配的含 GT region = 197−95 = **102 ✓**（报告这一半正确）；含 GT region 总数 416 ⇒ 未完全覆盖 = **314**。同一口径的另一佐证：`"tp_block_coverage": 0` 共 **266** 处，减 95 = 171 个含 GT region 全零匹配，与 416−102−171=143 个部分匹配相加为 314。
- 该数字不进入任何 Gate 计算（Recall=438/917 与它无关），但它是正式报告里用于刻画失败模式的核心陈述，需改正为 314/416（若作者原意是"有块但未覆盖"则应剔除 4 个零检出 region，写 310/416，并在文中说明口径）。

### P3

- **P3-1（§7 C2 数字无产物支撑）**：报告 L111 "hard upper bound from zero-detection regions alone is ~**+9 GT boxes** (<1 pp)"。`consistency-and-summary.json` 的 `zero_detection_regions` 只有 4 个 region，n_gt = 2+1+1+1 = **5**（K06 r74/r94、K09 r75/r110），即 5/917 = 0.55 pp。结论方向（<1 pp、不足以改变 verdict）不受影响，但 +9 无法从任何已提交产物复现，应改为 5。
- **P3-2（README 口径陈述过期）**：`experiments/M2-DOCTR-QUAL/README.md` L21-23 仍写"IoU≥0.5；Recall≥92%；**Precision≥85%**；Mean IoU≥60%"，与现行 `thresholds.json`（Precision 非 Gate、`min_mean_coverage`）冲突；L34-40 的 preflight 复现命令在当前 threshold 契约下会 KeyError。建议标注"L21-40 为 preflight 历史段落，现行口径见正式 qualification run 段"。
- **P3-3（汇总脚本的死代码与非自包含默认值）**：`summarize_qualification.py` L135 `args.qual_dir if hasattr(args, "qual_dir") else args.qualification_dir` 为不可达分支；L24-25 默认 baseline 路径为仓库外硬编码绝对路径（`G:/CODEX/New Manga/...` 与 task-envs work 目录），且只比对 `summary`/`per_region`、不校验 baseline 文件自身的 sha256。跨机复现时会直接 FileNotFoundError。建议报告中把 `--baseline-dir` 显式写入复现命令并记录 baseline 文件指纹。
- **P3-4（legacy verdict 键改名未在 §4 披露）**：新 verdict 段对旧扁平阈值文件会输出 `mean_coverage` 而非旧 `mean_iou`（`gates.get("min_mean_coverage", gates.get("min_mean_iou"))`）。我已 grep 全仓 `*.py` 确认阈值文件/verdict 的唯一消费者是 `eval_detection.py` + `summarize_qualification.py`（`smoke_adapter_check.py` 仅 `from eval_detection import build_engine`），故无实际破坏；但"旧文件保持 legacy 行为"的说法在键名层面不完全成立，建议在 §4 补一句。
- **P3-5（`--previews 0`）**：正式跑未产出 severe-miss 预览图（handoff Risks 已披露）；C1 人工审计前需按清单补生成，属已知遗留而非缺陷。
- **P3-6（下一任务建议的 Gate 偏粗）**：handoff §下一任务建议把 C1 完成 Gate 定为"可解释 ≥90% 未匹配 GT 样本"，该 90% 为自拟阈值、无依据；建议改为"逐样本判定覆盖 100% 抽样集 + 噪声修正 recall 的置信区间"，避免用一个新拍脑袋阈值替代旧问题。

---

## 审查角度逐项结论

### A. 冻结口径一致性（Gate 三项 / Precision 不得入 Gate 表）——**通过**

| 口径项（Task 冻结） | 报告 | results JSON | 判定 |
|---|---|---|---|
| 主判定层 `block_coverage` + 生产 pad 6px | §1 标题、§8 | `strip_block_pad: 0.0`、`task: M2-DOCTR-QUAL-RUN` | ✔ |
| Recall ≥ 0.92 | 0.4776 FAIL | 0.4776444929116685（tp 438 / gt 917） | ✔ |
| Mean coverage ≥ 0.60 | 0.7531 PASS | 0.7530730500617262 | ✔ |
| severe ≤ 0.05 | 0.0385（16/416）PASS | 0.038461538461538464 | ✔ |
| **Precision 非 Gate** | §1 Gate 表**仅 3 行**，Precision 单列 §2 | 三份 JSON 的 `verdict.precision` 均为 `"gate": false`、**无 `pass` 键**；全 qualification 目录 grep 无扁平 `"min_precision"`、无 `"gate": true` | ✔ 严格满足"Precision 不出现在 Gate 表" |
| 附报项 | §3 表含 block_strict / pad 抵消 / db_resnet50 / raw_strict | padoffset、db JSON 齐备 | ✔ |
| 检测 only | §"Recognition outputs never consulted"（多处） | 代码路径无 recognition 调用 | ✔ |
| 不得为凑 PASS 改口径/数据 | — | worktree `thresholds.json` 与 base **逐字相同**；manifest sha256 与 preflight 相同；权重 sha256 相同 | ✔ |

`all_pass=false` 由 `verdict` 中仅含 `pass` 键的 3 项合取（`precision` 无 `pass` 被排除），逻辑上不可能被 Precision 拉低或抬高。

### B. `f9894184` 契约适配是否最小、测量逻辑是否零改动——**通过（我独立复算 diff）**

以主仓（= base `5b3a477a`）文件为对照，逐段行号对齐读取后，worktree 版（517 行）与 base 版（487 行）的差异**只有 3 处、合计 +30 行**：

1. 新增 `--task` 参数：worktree L190-196（7 行）；
2. verdict 段替换：worktree L375-425 对 base L368-395（净 +23 行，含 `gates = THRESHOLDS.get("gates", THRESHOLDS)`、`min_mean_coverage` 兼 fallback、`gate: false` 的 Precision 分支）；
3. `out_payload["task"]`：worktree L432 `args.task` 对 base L402 硬编码字符串（同 1 行）。

其余全部一致：L1-160（docstring / 权重 pin / `sha256_file` / `build_engine` / `iou` / `match_greedy` / `blocks_to_rects`）、L160-374 度量主循环与 summary 构建、L427-517（payload、`_py`、打印、`main` 入口）——worktree 与 base 在这些区间**逐行同文**，偏移恒为 +7 或 +30。结论：**匹配、coverage/IoU、FP 归因、per_region 与 summary 生成逻辑零改动**；改动面确如披露（verdict schema 读取 + Precision 非 Gate + `--task` 元数据）。全仓仅 `eval_detection.py` 读 `thresholds.json`，无其他被连带破坏的调用点，说明适配范围"最小且充分"。

### C. 报告数值 × results JSON 交叉核对——**除上述 2 处叙述数字外全部吻合**

- Gate 三项、tp/fp/n_gt：§1 与 JSON/summary 完全一致（见上表）。
- Precision §2：0.1250 = 438/3505 ✔；"3067 FP against 917 pseudo-GT" ✔；union 层 2985 FP / **2 with text evidence** / 2983 pure ✔（主仓 `results-fast_base-cuda-union.json` L92-97 实测 2985/2/2983）。
- §3 观测表逐格核对：block_strict 0.4515(414/917)/0.1181/meanIoU 0.7034/severe 0.0385 ✔；pad 抵消 0.2628(241/917)/0.0688/0.6842/**0.1034**(43/416) ✔；db_resnet50 0.6085(558/917)/0.1858/0.7751/0.0192(8/416)/17.2 s ✔；raw_strict 0.1941(178/917)/0.0333/0.6622 ✔。
- §3 派生结论：db +13.1 pp（0.1309）✔、距 Gate 31.2 pp（0.3115）✔、"severe halved" ✔、"pad 为净正贡献" ✔。
- §6 逐案表：per-case n_gt 合计 917 ✔、tp 合计 438 ✔、10 个 recall 与 tp/n_gt 逐项相等 ✔、"spread 3.2x"（0.6991/0.2178=3.21）✔、severe 清单 16 条与 `consistency-and-summary.json` 完全一致 ✔、K10 = 6/16 ✔、零检出 4 region ✔；**仅 312 一处错误（应为 314，P2-1）**。
- §7 C2 "~+9 GT boxes" 与产物不符（应为 5，P3-1）。

### D. §7 调参/换模型候选建议——**有数据支撑、未越界实施**

- C1 伪 GT 盲区校准：依据（416 个含 GT region 中 314 个未完全覆盖、零检出仅 4 region、union 层 2983/2985 FP 无文本证据）全部可追溯；定位"决定 0.92 是否可测"而非"提分"，表述诚实。
- C2 阈值扫描：数据依据（3505 检出 vs 917 GT 过生产）成立，明确"参数 plumbing 在 eval 侧、生产常数不动、不期待改变 verdict"——与 Task 禁止范围一致。
- C3 db_resnet50：+13.1 pp / severe 0.0192 / 17.2 s 均实测；明确"生产 wire/behavior 变更需另行 Codex 释放"。C4 标注"decide after C1"。C5 用 block_strict≈block_coverage 与 pad-offset 反证"粒度不是主因"，站得住。
- **未越界**：worktree `experiments/M2-DOCTR-QUAL/` 仅比 base 多出 `summarize_qualification.py`（glob 实测：base 6 文件 + 新增 1），无阈值扫描脚本、无 DBNet 接入、无 `src/` 改动；`src/**` grep `M2-DOCTR|qualification` 零命中。§7 全部是"建议 + 成本/风险"，符合 Task"不宣称调参/换模型实施"。

### E. 一致性自检可信度——**可信（我做了独立抽样复核）**

- 手法可信：`summarize_qualification.py::_diff` 递归比对 `summary` 与全部 511 条 `per_region`，类型+键集+长度+值都覆盖，`deterministic_reproduction` 需 manifest sha 相符且三类 diff 全空，失败即显式记录。
- manifest 指纹：三组 `manifest_sha256_formal == baseline == 4f16425a…1e`，我直接读了主仓 preflight JSON 与 worktree formal JSON 头部，均为 `4f16425a8ba72435051ef5f671bf36084a74adc7c4d05800ea2ae2150cf6f11e` ✔。
- **独立抽样（不依赖作者脚本）**：formal 与主仓 preflight 的行偏移恒为 +7，逐条对齐后抽检 3 处 —— K01 r1（头）、K06 r122（中）、K10 r146（尾）11 个字段全部相同；pad-offset 与 `task-envs/.../results-fast_base-cuda-seg05-pad0.json` 尾部记录相同；db 侧主仓 baseline `tp 558 / recall 0.608505997818975 / severe_miss_regions 8` 与 formal db 完全一致；pad0 的 `block_coverage` 与 formal pad-offset 完全一致（0.2628135223555071 / 0.6842480690495881 / 0.10336538461538461）。与集成方"deterministic reproduction = True"结论一致。
- verdict 值一致性（报告 §5 仅文字声明）：我逐项比对 preflight verdict（recall 0.4776444929116685 / precision 0.12496433666191155 / mean_iou 0.7530730500617262 / severe 0.038461538461538464）与 formal 三项——**数值全等**，仅键名 `mean_iou`→`mean_coverage` 且 Precision 改为非 Gate，属披露范围内。
- 局限：比对基准是仓库外绝对路径文件（P3-3），且 summary JSON 未把 verdict 差异作为机器可读断言留存（仅文字披露）。

### F. 范围纪律与证据纪律——**基本达标，缺 1 份 diff 证据**

- 路径集合与 Task 允许范围吻合：`experiments/M2-DOCTR-QUAL/**`（含新增 `summarize_qualification.py`）、`verification/M2-DOCTR-QUAL/qualification/**`（9 个文件，无越界产物）、Task、Handoff。`doc/STATUS.md` 前 40 行与主仓逐字相同，未被本分支改动（另 grep 到的 `GOAL.md`/`tasks/README.md` 引用均来自 base 释放提交）。
- 生产零改动：主仓 HEAD == base 已由 refs 证实；抽查 `src/infrastructure/providers/detection_doctr.py` 两处关键区间（L55-84 权重 pin/`MERGE_PAD_PX=6.0`、L319-363 `cluster_words_into_blocks`，两文件同为 405 行）**逐字相同**；`src/**` 无实验标记字符串。
- 证据纪律良好：4 份 raw log 均带 `# shell=… cwd=… HEAD=… date=… cmd=…` 头与 `# EXIT=n` 尾；崩溃首跑（HEAD `6384c807`，L3 指向 base 487 行版本）与三次成功跑（HEAD `f9894184`）时序自洽；每份结果 JSON 均带 `manifest_sha256` 与权重 sha256；报告 §9 + README 均给复现命令。
- 缺口：本分支未提交任何 changed-file 清单/`git diff --stat`/`diff --check` 输出（preflight 曾有 `verification/M2-DOCTR-QUAL/git-evidence.txt`），AC5 的"diff 仅限…"只能靠集成方 git 侧证明；我在沙箱内无法运行 git，故以"base refs + 逐文件抽样对齐"替代，属**可接受的替代证据但非等价证据**。

---

## 缺失证据

1. **提交化的 diff 证据**：无 `git show --stat`/`--numstat` 或 `diff --check` 产物随分支提交（AC5 自证不足，依赖集成方与我的静态替代核验）。
2. **§6 "312" 与 §7 C2 "+9" 的机器可读来源**：`consistency-and-summary.json` 未导出"完全匹配 region 数""零检出 GT 总数"两个字段，导致报告叙事数字无法被脚本自动复核（这两处正是我人工反推发现的差错）。
3. **verdict 差异的机器可读断言**：一致性检查只覆盖 `summary`/`per_region`；verdict/gates 差异仅文字声明（虽经我人工核对相等）。
4. **severe-miss 预览图**：`--previews 0`，无 16 个 severe region 的可视证据（已披露，C1 前需补）。
5. **baseline 文件指纹**：三组确定性比对所依赖的 preflight/pad0 基准文件仅有 manifest sha256，无基准文件自身 sha256（基准可被无声替换）。
6. 与本次审查环境有关：`pwsh` 不可用，未复跑 `summarize_qualification.py`、未做 GT/坐标级重算（仅行号对齐 + grep 计数）。

---

## AC 逐项裁定

| AC | 裁定 | 依据 |
|---|---|---|
| **AC1 正式主跑** | **成立** | `results-formal-fast_base-cuda-seg05.json`（511/511 regions、`task=M2-DOCTR-QUAL-RUN`、`strip_block_pad=0.0`、elapsed 22.22 s）+ `raw/formal-run2-*.log`（HEAD `f9894184`、EXIT=0）；Gate 逐项：Recall 0.4776 **FAIL** / MeanCov 0.7531 PASS / severe 0.0385 PASS |
| **AC2 附报诊断** | **成立** | pad 抵消 JSON+log（0.2628 / 0.6842 / 0.1034）、db_resnet50 全量 511 regions（0.6085 / 0.7751 / 0.0192）、block_strict 与 raw_strict 全量入 §3；数值与 JSON 逐格相符（P2-1/P3-1 仅是 §6/§7 叙事数字，不影响本项） |
| **AC3 正式报告** | **成立（附 1 处数值更正）** | `qualification-report.md` 含 §1 Gate 表（3 行、无 Precision）、§3 观测表、§5 preflight 一致性核对、§7 候选流程、§9 复现附录；**唯 §6 "312/416" 需更正为 314/416**（P2-1），§7 C2 "+9" 更正为 5（P3-1） |
| **AC4 可复现** | **成立** | 三份 results JSON 均带 `manifest_sha256=4f16425a…`（另带权重 sha256、`thresholds` 全量内嵌）；`README.md` L71-91 与报告 §9 给出完整复现命令；raw log 带 shell/cwd/HEAD/cmd/EXIT 记录。复现前提（仓库外 weights/manifest/GPU venv）已如实写明 |
| **AC5 范围纪律** | **条件成立（交 Codex 裁定）** | 路径集合在允许范围内（`experiments/**`+`verification/…/qualification/**`+Task+Handoff），生产 `src/**`/`requirements*.txt` 零改动（主仓 HEAD==base + `detection_doctr.py` 抽样逐字相同）。唯一偏差：`f9894184` 修改了 Task 明示"不改"的已集成评测逻辑文件；我独立确认改动仅 3 处、度量逻辑零改动，作者在 Task AC5 注记 / 报告 §4 / Handoff Risks **三处主动披露**，并给出崩溃根因证据（`raw/formal-run1-*.log` EXIT=1）。**建议：接受该适配（勿 revert，见 P1-1），并在集成说明中把"runner↔thresholds 契约一致性"记为已收敛项** |

**总体判断**：交付物在用户冻结口径下自洽、可复现、可交叉核对，正式结论 **FAIL（Recall 0.4776）** 正确且未被粉饰；契约适配是最小必要修复且测量中立，已构成可接受的披露偏差。发现的 6 项问题全部为叙事数字、文档口径、脚本卫生与证据形式，**不改变 Gate 判定、不触及生产行为**，可在集成时或紧随其后一并修正。

---

## 推荐下一步

1. **Codex（集成方）**：按 P1-1 接受 `f9894184` 并把 Task 置 `done`（集成 commit 记入 Task `integration_commit`）；合入前顺手修正 P2-1（312→314）与 P3-1（+9→5），这是唯一需要改文件的项，且属报告文字，无重跑成本。
2. **下一 Task（建议）**：采纳 Handoff §下一任务建议的 `M2-DOCTR-CANDIDATE`（C1 GT 伪标注校准 + C2 FAST 阈值扫描附录），但把 P3-6 建议纳入其 Gate 写法。前置：本 Task 集成完成；C1 的人工判定环节需用户或用户授权标注者参与（不可由 Agent 自造 GT）。
3. 可直接转发给 Agent 的指令：

> 在 `experiments/M2-DOCTR-QUAL/` 下新建候选流程 Task（依据 `verification/M2-DOCTR-QUAL/qualification/qualification-report.md` §7，DSH Review 已 APPROVED_WITH_MINOR_ISSUES）：①对分层样本（16 个 severe-miss regions 全量 + 随机 ≥35 个含 GT regions，清单取自 `consistency-and-summary.json`）逐条未匹配 GT 判定"真文字 / 伪 GT 噪声"，产出噪声修正后的 recall 重估报告，判定结论必须覆盖 100% 抽样集而非"≥90%"；②实现 eval 侧 FAST 阈值扫描（`box_thresh`/`bin_thresh`/`unclip` 矩阵，零 `src/` 改动），并用现有 4 个零检出 region（n_gt 合计 5）标定扫描上限。复用既有 GPU venv 与 `eval-manifest.full.seg05.json`（sha256 `4f16425a…`），不得修改 `thresholds.json` 冻结口径；C3/C4 决策待 C1 结论后再立项。
