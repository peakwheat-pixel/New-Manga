# M2-SFX-BJ13-RECALL-1 定点复审 r2（非作者 · DSH）

## 1. 方法段

**本会话工具面限制（先声明，影响可核对粒度）**：`pwsh` 在本会话沙箱下无法启动（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-BJ13-RECALL-1-zcode)`；升级 `danger-full-access` 因无审批通道被拒）。因此**本轮无法运行 `git status / show --stat / diff`、无法做哈希级 diff**；改用「直接读 git 元数据 + 逐行静态比对 + mtime 序」三条替代路径取证，凡替代路径不能覆盖的点在文中显式标注。

读取清单（全部只读）：

- 交付面：`doc/tasks/M2-SFX-BJ13-RECALL-1.md`、`doc/handoffs/M2-SFX-BJ13-RECALL-1-zcode-20261006.md`、`verification/M2-SFX-BJ13-RECALL-1/recall-report.md`、`raw/recall-probe.json`（1092 行，全文）、`raw/recall-probe-run.log`、`raw/r1fix/recall-probe.json`（1092 行，全文）、`raw/recall-probe-run-r1fix.log`。
- 被引证据：`M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l1-fullpage-conf-scan.json`（:3、:5320-5344、:5541）、`M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:67`、`M2-SFX-T4-SWITCH/switch-report.md:67` 与 `raw/rollback-drill.json:16`、`M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md:214`、`arbitrate-bj13` 侧由 raw json 内证。
- 生产代码（只读引用核对）：`src/infrastructure/providers/detection_sfx.py`（:139、:270-271、:282-367、:556-562）、`src/bootstrap/core_assembly.py:867-868`。
- Git 元数据（只读）：`G:/CODEX/New Manga/.git/worktrees/M2-SFX-BJ13-RECALL-1-zcode/{HEAD,logs/HEAD}`、`G:/CODEX/New Manga/.git/refs/heads/agent/zcode/M2-SFX-BJ13-RECALL-1`、`G:/CODEX/New Manga/.git/logs/HEAD`（:842-843）。
- 页图忽略规则（跨 worktree 只读）：`M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/.gitignore:26`。
- 触碰面替代取证：本 worktree 全量 glob（6596 条，按 mtime 升序 spill 文件），末 18 条即最新改动文件。

**独立确认的 Git 事实**：分支 ref = `04d5f621d56cf877b9aa0d63d6889c736f1d7df7`；worktree reflog 链 `2a1a9f73 → 0f175b89（claim）→ 47df4dbc（impl）→ d95bbdfe（verify）→ e6b4684c（docs）→ 04d5f621（fix(review)，单 commit）`，与 r1 tip `e6b4684c`→r1fix tip `04d5f621` 完全一致。

## 2. 终判

**approved —— r1 三项集成条件（C1/C2/C3）与全部顺笔项（P3-1/P3-5/P4-3/4/5/6/7；P4-1/2 登记）逐条真实闭合，核心事实层未被返修改动（r1fix 只落字与证据，零数字变化），0 新 P0/P1/P2；建议集成。**

## 3. 逐条闭合表

| r1 项 | 判定 | path:line 证据（本轮实读） |
|---|---|---|
| **C1 = P2-1**（1280→1024 + 基线形态） | **CLOSED** | `recall-report.md:27` 已写 1024 并给 CPU(chiqui7, ORT 1.30.0)↔DML 声明；四项记录逐条复核成立：`l1-fullpage-conf-scan.json:3` `"letterbox": 1024`；`M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:67`「onnxruntime 1.30.0 CPU，letterbox 1024」（同时支撑 ORT 版本断言）；`M2-SFX-T4-SWITCH/switch-report.md:67` imgsz=1024；`M2-SFX-T4-SWITCH/raw/rollback-drill.json:16` `"imgsz": 1024`。全交付面 grep `1280` 仅剩 `M2-SFX-BJ13-RECALL-1.md:60` 的更正登记（允许）；Handoff 残留已修（`...-zcode-20261006.md:72` 现写 1024） |
| **C2 = P3-4**（base_commit 对账） | **CLOSED** | frontmatter `M2-SFX-BJ13-RECALL-1.md:11` = `2a1a9f73`（无残留注记）；注记移正文 `:56`；Handoff `:5`、report `:4` 同值。释放链独立复核：`.git/logs/HEAD:842` `3a65150b→630c3f51 (release 三件)`、`:843` `630c3f51→2a1a9f73 (release-followup: PLAN 三行回填，防自引用)`，worktree `logs/HEAD:1` 起点=2a1a9f73 ⇒ 统一值正确、链注记与真实 reflog 逐字对应。残余 `3a65150b` grep 命中仅两处他 Task 的合法 base（`M2-SFX-MISROUTE-UI-IMPL-1.md:11`、`M2-WORKBENCH-REACT-1.md:11`），非本交付残留 |
| **C3a = P3-2**（§6 limitation 6） | **CLOSED** | `recall-report.md:123` 新增 limitation 6：8 region 为 chiqui7 自证清单/无独立 GT，且「域内锚定=生产链等价性证明，非独立召回 GT」；承继来源核到 `diagnosis-and-options.md:214`（行号精确命中该限制原文） |
| **C3b = P3-3**（§1 两点口径差异） | **CLOSED** | `recall-report.md:32`：①conf 过滤次序 + 对 ≥0.5 子集数学等价 + G7 逐框实证；②模块常量不读 env。代码面复核：`detection_sfx.py:139` `SFX_CONF_THRESHOLD = 0.5`，env 覆盖点在装配层 `core_assembly.py:867-868`（`NEWMANGA_SFX_CONF_THRESHOLD`）——「probe 取常量、不跟随 env」陈述与代码结构一致 |
| **P3-1**（tile 不可适用） | **CLOSED** | `recall-report.md:108` 给出 aspect≈1.41 不满足「宽≤690 且 aspect≥8.0」且谓词属冻结域；代码复核 `detection_sfx.py:556-562` 谓词 + `:270-271` 默认 690/8.0 逐字对应 |
| **P3-5**（r1fix 重跑证据） | **CLOSED** | `raw/recall-probe-run-r1fix.log:2` date、`:3` 完整命令行（含 `--out-dir ...raw/r1fix`）、`:4` venv、`:5` Python 3.12.3、`:6` ORT 1.24.4/numpy/PIL、`:7` worktree+分支、`:13` `ep_effective=dml`、`:30` 落点、`:31` `EXIT=0`；行号与时间自洽：log 22:05:01+0800 ↔ r1fix json `generated_at_utc` 14:05:03Z(=22:05:03+0800)；原 raw 时间自洽（13:33:27Z ↔ verify commit reflog 1791293902≈13:38Z） |
| **P4-3**（「域内一致性」措辞） | **CLOSED** | `recall-report.md:56` 改为「两代权重在该区（DOMAIN-EXT-DIAG 判定域外页 BJ13）**判定一致**…措辞按 DSH r1 P4-3 修正，不称『域内』」；同步 `M2-SFX-BJ13-RECALL-1.md:53`、Handoff `:21`。全交付面 grep `域内一致性` 零命中 |
| **P4-4**（87×103 仅 b5b747d0） | **CLOSED** | `recall-report.md:69` 已限定「其中仅 b5b747d0 为 87×103 小框，属三者中的最小尺寸」；raw 复核 `raw/recall-probe.json:261-279`：ab8974e1=170×294、c3781c28=217×492、b5b747d0=[2494,1895,2581,1998]=87×103 ⇒ 限定与「最小」均成立 |
| **P4-5**（页图路径在 peer worktree test_assets） | **CLOSED** | `recall-report.md:29`、`M2-SFX-BJ13-RECALL-1.md:32`+`:42`、Handoff `:43`+`:71`；被引忽略规则独立核到 `M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/.gitignore:26` = `/01_black_jack_official/`，行号与语义精确；页图 `vol03_p0048.png/vol03_p0060.png` 实测存在于该目录 |
| **P4-6**（4.4x/42x 跨形态声明） | **CLOSED** | `recall-report.md:114` 显式声明 4.4x/42x 属 CPU(chiqui7, ORT 1.30.0)↔DML(v2b) 跨形态比较、量级远超 ≤2e-06 漂移窗口、两代同 imgsz 无 letterbox 混杂；比值复核 0.3727/0.0855=4.36、0.1796/0.0043=41.8（与 4.4x/42x 相符） |
| **P4-7**（类别翻转证据） | **CLOSED** | `recall-report.md:55`；原始证据复核 `l1-fullpage-conf-scan.json:5327-5332`（同一 ref1 候选 `argmax_cls=text`、`sfx 0.0855 / text 0.5195`）与 `:5541`（`sfx 0.0043`）⇒ 数字与归属准确，v2b 侧 `raw/recall-probe.json:456-467` sfx 0.3727/text 0.0 |
| **P4-1 / P4-2**（登记不改） | **CLOSED（登记）** | `M2-SFX-BJ13-RECALL-1.md:66`（relabels 口径 + 未来以 `detection_sfx.py:1359-1368` 为准）、`:67`（probe 恒 letterbox 未自证谓词，四页 page_w=2946>690 必为 letterbox） |
| 措辞纪律（清单第 4 项） | **合规** | `recall-report.md:33`「全树逐位一致（排除 generated_at_utc/inference_s）…同形态（DML→DML）」「非跨形态声明」；`:114` 对 G7 对位保守降级为跨运行口径、不称位级。全交付面 `位级可复现` 仅出现在**禁止性**表述（`M2-SFX-BJ13-RECALL-1.md:43`、Handoff `:38`/`:66`、report `:114`）⇒ 与 M2-PROD-SFX-PROBE-1 r2 确立的「同形态同域（文件哈希/DML run-to-run/权重 pin）例外」完全对齐，**未外溢成跨形态声明** |
| Task/Handoff/report 一致性（清单第 5 项） | **一致** | Task: review_events `:14` + 返修段 `:58-73` + status `in_review` `:5`；Handoff: status/delivery_head `:6-7`、r1fix 验证行 `:36`、风险 `:66`；report: 基线 `:4`、r1fix 段 `:33`。三处对「r1fix 零数字变化」的断言同口径，且与两份 json 的实测差异一致。fix commit hash 三处均以「见 git log 分支头」表述（自引用约束），本轮由 ref/reflog 独立锚定为 `04d5f621` |
| r1fix 证据可静态核对性（清单第 3 项） | **成立** | 两份 json 行数相同（各 1092 行）；全文逐行比对差异仅 `:3`（`generated_at_utc` 13:33:27Z→14:05:03Z）与 `:47`（BJ06 `inference_s` 0.016→0.022），BJ13/14/15 的 `inference_s` 亦相同；另以 37 个跨页数值样本（0.8719/0.5446/0.9283/0.9401/0.8512/0.9257/0.9627/0.8732/0.7576/0.8914/0.3727/0.1796/0.5118/0.0162/`5048bab6…`/`b5b747d0…` 等）做 grep 成对核对，**原 json 与 r1fix json 在同一行号返回逐字相同文本**。属静态行级比对（非哈希 diff，见 §1 工具限制） |
| 原 raw 零触碰 + 落点独立（清单第 3 项） | **成立** | ①落点独立：新证据在 `raw/r1fix/` 子目录 + `raw/*-r1fix.log` 新文件；②mtime 序（全量 glob 升序 spill 末 9 条）：`src/**/__pycache__/*.pyc`(6579-6587) → `experiments/.../recall_probe.py`(6588) → 原 `raw/recall-probe-run.log`(6590)、原 `raw/recall-probe.json`(6591) → r1fix `json`(6592)、r1fix `log`(6593) → `doc/tasks`(6594)、`doc/handoffs`(6595)、`recall-report.md`(6596)——**原 raw 两个文件严格早于 r1fix 证据与文档，未被 fix 触碰**；③原 log 无 r1fix 头、原 json 保持 13:33:27Z，未被重跑覆盖；④fix 触碰面（末 9 条）全部落在允许路径，`src/**` 仅 gitignored `__pycache__` 字节码缓存（非 tracked 变更）、`tests/**` 零出现 |
| 新引入问题扫描（清单第 6 项） | **通过** | grep `3a65150b`：本交付内仅 `M2-SFX-BJ13-RECALL-1.md:56`（允许的释放链注记）；grep `1280`：交付面仅 `:60` 更正登记。未见返修改坏事实层（三态数字/BJ06 5/8/0.8732/BJ13 0.0/BJ15 0.5118 与两份 json 全同） |

## 4. 新发现（均为 P4，非阻塞；不构成新条件）

- **N-1 [P4] 证据清单行未随 r1fix 更新**：`recall-report.md:6` 的「raw 证据」与 `M2-SFX-BJ13-RECALL-1.md:52` 的 AC5 行仍只列 `raw/recall-probe.{json,-run.log}`，未列 `raw/r1fix/recall-probe.json`、`raw/recall-probe-run-r1fix.log`（正文 `recall-report.md:33`/Task `:65` 已列，故仅为枚举完整性）。建议下次文档触碰时补齐，无需单独返修。
- **N-2 [P4]「log 第 5 行」指代未限定**：`recall-report.md:27` 现存在两份 raw 日志，`log 第 5 行`（ENGINE OK）仅对原 `raw/recall-probe-run.log` 成立（r1fix 中日志该行为 `:13`）。建议写成 `raw/recall-probe-run.log:5`。
- **N-3 [P4] 头部措辞精确性**：Task `:65` 与 Handoff `:36` 称 r1fix log「含命令行/venv/EP/EXIT 头」；实读 `raw/recall-probe-run-r1fix.log:2-7` 的头部仅含 date/cmd/venv/Python/runtime/worktree，EP provenance 与 `EXIT=0` 在正文（`:13`、`:31`）。内容齐全，仅「头」字口径可收窄。
- **N-4 [P4] 一条断言不可自证**：`recall-report.md:32` ②「本 Task 全程未设该 env，两者实际一致」依赖 Owner 陈述；新 log 头部未落 `NEWMANGA_*` env 快照，故该句在证据面不可复算（不影响 conf 0.5 结论；未来重跑可在头部加 env dump）。
- **N-5 [P4] `.pyc` 侧效应**：探针 import 使 `src/infrastructure/providers/__pycache__/detection_sfx.cpython-312.pyc` 等被再生成（mtime 最新区段）；属 gitignored 缓存，「零 src」在 tracked 面成立，无需动作，仅登记避免未来误读 mtime。
- **N-6 [P4] 复审落档方式与 Handoff 指令不一致**：「可直接转发指令」（Handoff `:56`）要求把 r2 结论写入 `doc/reviews/M2-SFX-BJ13-RECALL-1-<head>-dsh-r2.md`，而本轮 r2 授权为「全程只读、报告一次输出」。本轮**未新建任何文件**；如需仓库内落档，请集成方按上述文件名补写（内容可直接取本报告）。
- **未能替代取证的残余（诚实标注，非缺陷）**：`git diff --check EXIT=0`、`git status` 的 tracked 零变更（Task `:51`、report `:113`）本轮无法用命令复核；已用「全仓 mtime 序 + 允许路径全集」作替代，结论未见反例。

## 5. 集成建议

1. **建议直接集成收口（approved）**：无 src/tests 集成动作；AC2 提案（维持 0.90 冻结域）与 AC3 推荐序 ③维持现状 → ②ai-direct 补画扩展 → ①BJ13 补标，按 r1 复核意见**双分支双口径呈报用户裁决**，不要由集成方代取其一。
2. **Task/文档状态**：status 保持 `in_review` 直至 Codex 收口；收口时可一并把 §4 的 N-1/N-2/N-3 三条文案项作为「同 commit 顺笔」处理（不必单开返修轮），N-4/N-5/N-6 仅登记。
3. **依赖链**：若用户选 ③，BJ13 自动化闭合注记保持 open，复测点=下一次 sfx 权重迭代，直接复用 `experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`（命令与 venv 见 Handoff `:43`；r1fix 已证同形态 run-to-run 逐位可复现，复测结果可直接与本次 5/1/0/1 + 0.3727/0.1796 对表）。
4. **推荐下一步（可转发）**：交 Codex 执行集成收口——核 r2 报告后置 Task 状态、把 AC2/AC3 交用户裁决并落 Review 文档（如需仓库内 r2 存档，写 `doc/reviews/M2-SFX-BJ13-RECALL-1-04d5f621-dsh-r2.md`）；无需新的实现 Task 被释放。
