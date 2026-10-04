## 审查方式与前提交代

静态只读审查（沙箱禁命令，运行级声明一律标注未验证）。已完成的**文件级独立取证**：

- Git 事实（读 `.git` 内部文件，非运行级）：`.git/worktrees/.../logs/HEAD` reflog 完整证明 `4c12e8af`（base）→ `e2438ed3`（claim）→ `6b73c92a`（delivery）→ `d23fde31`（Handoff+Task 回填=分支 tip）；`refs/heads/agent/zcode/M2-SFX-FINETUNE-PREFLIGHT` 与 `HEAD` 分支名与合同一致。
- 依赖门：`depends_on` 三项 `M2-SFX-DETECT-DOMAIN-EXT-DIAG` / `M2-SFX-PROD-1` / `M2-REGION-OVERLAP-ARBITRATION` 均 `status: done`；下游 `M2-SFX-DATA-INFRA` 确为 `ready`。
- src 交叉核对（只读）：`SFX_HF_REVISION=7f5f5c04…`(:108)、`SFX_WEIGHTS_SHA256=d87389af4350…`(:110)、`SFX_CLASS_MAP`(:137)、`_build_engine`(:391-445 含 SHA 门/names 断言/`_parse_imgsz`)、`_sfx_boxes`(:535-589 conf→全类 NMS→sfx 过滤→/scale) — 与报告引用逐条一致。
- raw 复算：b2/b4/b8 显存 1940/4030/7488 MiB、吞吐 = `it_s×batch` = 36.5/57.3/67.0 img/s、`best.onnx` 40,824,248 B / sha256 `b1bb877f…`、`(1,40,21504)`（128²+64²+32²；40=4+4+32）均自洽；`names`/`imgsz="[1024, 1024]"` 与导出物 metadata 一致。
- **未验证**：`git diff --check`/`git status` 改动面（6b73c92a 文件清单）、venv 与外部树实体、任何联网抓取（HF / docs.ultralytics.com / ultralytics.com）。

## Verdict

**approved_with_conditions**

0×P0、0×P1。核心交付（A 受阻的否定性结论、A′ 建议、四类策略选项 1、显存/吞吐、导出链 EXIT=0 与零 src 纪律）均有多重文件级证据支撑，且我独立复算的数值与 raw 一致；不需要重跑实验。但存在 3 条 P2 必须文本返修：①AC5 备案表中「densho810 追加利用报告已发」与仓库既有登记直接矛盾且凭据 commit 引用错误；②AC1-③「选项 3 技术不可行」论证不完备、措辞强于前提；③两处改变计划的否定性联网结论（chiqui7 无 `.pt`、HF 全站无第二个 sfx 类模型）未排除非默认 revision/branch 口径、且无原始响应落 raw。

## 发现清单

### P0
无。

### P1
无。

### P2-1｜AC5 素材来源②事实与凭据双错（许可义务状态误报）
- 位置：`verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md:117`
- 问题：写「densho810｜**追加利用报告已发**（vol03 48/60/159 页，窗口 2026-11-02 前达标，`74fa71e9`）」。仓库既有登记相反：`doc/handoffs/M2-SFX-E2E-MATERIAL-40a8ceec.md:68` 与 `doc/tasks/M2-SFX-E2E-MATERIAL.md` 遗留段均为「densho810 报告邮件=**用户待办**（TA2B 草稿覆盖本批同源新增）」；`74fa71e9` 在仓库中的实际身份是 `doc/tasks/M2-SFX-DATA-INFRA.md:12` 与 `M2-REGION-RETYPE-CONTRACT.md:12` 的 `base_commit`，无任何证据与「追加利用报告」相关。vol03 p0048/p0060/p0159 三页确为 E2E-MATERIAL 新入池页（该 Handoff:20 可溯源），但新增页的 1 个月报告义务是**新窗口**，不是已履行。
- 建议：改为可溯源表述——「TA2B 2026-09-30 报告已履行（覆盖 BJ01–BJ12 源 PDF）；vol03 新增 3 页报告义务窗口至 2026-11-02，仓库登记状态=用户待办（`M2-SFX-E2E-MATERIAL-40a8ceec.md:68`）」；删除或替换 `74fa71e9` 引用。备案表在「非阻断」语境下也必须状态准确，否则用户可能误判义务已闭环。

### P2-2｜AC1-③「选项 3 技术不可行」论证不完备、语气过强
- 位置：`preflight-report.md:39`、`doc/tasks/M2-SFX-FINETUNE-PREFLIGHT.md:28`
- 问题：唯一论据是 freeze 文档「by index or module name」＋cls 分支为共享 conv nc 通道。两点缺失：(a) 类级梯度屏蔽（自定义 loss/梯度 mask）在技术上是可实现的，只是超出 Ultralytics 开箱配置面与 T0 零 src 边界——「不可行」应为「配置面不可实现＋实现代价越界」；(b) 即便冻结 cls 输出通道，共享 backbone/neck 仍会更新，非 sfx 类输出照样漂移，这正是选项 3 想解决的问题——报告未讨论这层，反而把「不可行」当成唯一排除理由，结论强度高于前提（与本仓库 DSH 历史判例「结论语气强于前提」同型）。另外 freeze 文档引文是运行级声明，未落 raw。
- 建议：改为「Ultralytics 官方 `freeze` 不提供按类通道冻结；类级梯度屏蔽需自定义训练代码（超出零 src 与开箱配置面），且无法抑制共享 backbone 漂移，故排除」；并把 docs 抓取原文落 `raw/`。

### P2-3｜两处改变计划的否定性联网结论缺可复核证据与排除口径
- 位置：`preflight-report.md:23-27`（chiqui7 无 `.pt`）、`:60`（HF 全站无第二个带 sfx 类模型）；`raw/` 无对应文件
- 问题：合同停点（「A 受阻→交编排裁决」）完全依赖「无 `.pt`」这一否定性结论，但证据仅为默认 revision 的 `siblings` 摘录，未排除：非默认 branch/tag/旧 revision 携带 `.pt`、LFS 指针明细（`siblings[].lfs`）、`usedStorage` 的存储口径。报告引用的 `usedStorage: 41227478`（≈ONNX 单文件）其实是**很强的全 revision 排除旁证**（若任一 revision 存在 20.7MB 的 `.pt`，该数字不会如此），却没有被用作论证。AC2 的「HF 全站无第二个 sfx 类模型」只有报告叙述（「两查询、约 20+ 仓库」），既无原始响应也无「如何判定每个候选类别面」的穷举口径，实质是沿用 `M2-SFX-DETECT-EVAL` 的既有 surveyed 结论。
- 建议：补抓并落 `raw/`——(a) `GET /api/models/chiqui7/yolo11-manga-seg`（保留 `siblings[].lfs`、`usedStorage` 原文字段）；(b) `GET /api/models/chiqui7/yolo11-manga-seg/revision/main`；(c) `.../refs`（证明无训练分支/标签）；(d) `/tree/main?recursive=true`；(e) `README.md` raw 快照。报告中显式写出 `usedStorage` 排除逻辑与 AC2「沿用既有 surveyed 口径、非全站穷举证明」的限定语。

### P3-1｜AC2/AC5/AC1 的运行级引文与基座身份缺 raw
- 位置：`preflight-report.md:60`（HF 搜索）、`:113`（ultralytics.com/license 原文）、`:39`（freeze 原文）、`:52`（基座 `yolo11s-seg.pt` 20,669,228 B / sha256 `1caa81c0…`）
- 建议：沿本仓库 `verification/M2-SFX-DETECT-EVAL/license-evidence.md` 先例（外部树存原始响应 + sha256 + 报告摘录）落地；基座 sha256 的**原始哈希输出**也应有 raw（目前 `vram_probe.py` 仅假设权重已存在，下载步骤未脚本化、无日志）。

### P3-2｜「≈810 MiB/张」与实测数据不符
- 位置：`preflight-report.md:90`
- 问题：按 raw 线性拟合，斜率 ≈(7488−1940)/6 = **924.7 MiB/张**（截距 ≈90.7），不是 810；报告中由该斜率推出的 b12≈11GB、b16≈14.5GB 反而与 925 MiB/张 拟合一致 → 结论对、斜率标注错（笔误型自洽缺口）。
- 建议：改为「≈925 MiB/张（reserved 线性拟合）」，或注明 810 的口径来源。

### P3-3｜「epoch 墙钟」列名与实际口径不符；峰值显存同样未拆口径
- 位置：`preflight-report.md:83-87`
- 问题：`epoch_wall_s` 实为整个 `model.train()` 调用墙钟（含数据集扫描、AMP checks、optimizer 构建、且 `val=False` 实测仍执行 final validation），与 `per_iter_median×40`（2.19/2.79/4.78s）差一个量级；列名「epoch 墙钟 ×/40iter」会被读成纯训练时长。峰值 VRAM 亦含 final validation 阶段，报告未拆分训练/验证口径。
- 建议：列名改「整段 train() 墙钟（含初始化+final val）」，或补一列纯 40 iter 训练时长；峰值标注含 final val。

### P3-4｜batch=8 的显存安全边际未与「真实域更密」口径一致化
- 位置：`preflight-report.md:90`、`:123`、Handoff §风险 2
- 问题：时长外推已按 2-3× 折减，显存推荐（b8，7.49GB vs 16.27GB）却直接用 COCO 小图峰值，而报告自己声明真实 manga 页实例更密、mask/assign 开销更高。
- 建议：推荐 b8 的同时登记「首训第 1 个 epoch 实测真实数据峰值显存，超阈降 b4」的前置动作；或给 b4 为保守首训档。

### P3-5｜`vram_probe.py` docstring/常量注释与实测不符（过时注释）
- 位置：`experiments/M2-SFX-FINETUNE-PREFLIGHT/scripts/vram_probe.py:1,9-10,39`
- 问题：docstring 写「b2=5x/40 张、b4=10x/80 张、b8=20x/160 张」「使 epoch 恰为 20 iter」「各 20 iter」，且 `BATCH_REPEAT` 注释 `coco8-seg train=4 张 → repeat 后每 epoch 恰 20 iter`；实测 `repeat=20/40/80 → 80/160/320 张、40 iter`（console log 与 Handoff 均按 40 iter 记录）。
- 建议：把 docstring/注释改为 20x/40x/80x、每档 40 iter（与交付证据一致，避免复现者按注释误会）。

### P3-6｜训练 `data.yaml` 的 names 顺序契约未登记为下游硬约束
- 位置：`preflight-report.md:101`、`:54`
- 问题：「类面零漂移」实际来自冒烟 `dataset.yaml` 按 `bubble/panel/sfx/text` 写 names；这条对齐关系是**训练侧配置纪律**，不是架构天然属性。T1a/T1b 若把 names 顺序写错，导出物会在 `_build_engine` 处 fail-closed（好行为），但会浪费一次训练。
- 建议：在报告定案建议与 Handoff 里登记为 T1a/T1b 硬约束「训练 `dataset.yaml` names 顺序必须逐字等于 `SFX_CLASS_MAP`」。

### P3-7｜AC1①「ONNX 不可回训」未登记替代路径的排除理由
- 位置：`preflight-report.md:27`
- 建议：补一行说明为何不把 `onnx2torch` 类图转换当作续训路径（权重/优化器状态缺失、算子兼容风险、无原训练配置），使「路线 A 受阻」的论证闭合。

### P3-8｜A′ 的标注量代价未作为裁决输入前置
- 位置：`preflight-report.md:52-56`（§2 建议段）
- 问题：COCO 无域先验的风险已在 §2/§7.1 登记，但只在 §7.1 说「上限取决于数据投入」；§2 建议段没有把「BJ/KO GT 标注量下限」写成 A′ 的隐性成本，裁决方在不知道标注预算的情况下被建议采纳 A′。
- 建议：§2 建议段补一行「采纳条件/输入：T1b 承诺的最小标注量（页数下限）与召回基线回归口径」，与 `M2-SFX-DATA-INFRA` AC1–AC5 对齐。

### P3-9｜导出链环境变更未登记（AutoUpdate 装包）
- 位置：`raw/export_smoke_console.log:7-19`、Handoff §实验附录（Provider/Runtime）
- 问题：导出时 Ultralytics `requirements AutoUpdate` 联网安装了 `onnxslim==0.1.97`（并提示需重启运行时生效），`onnx 1.23.1` 亦未登记；导出物的 slimming 依赖该包，venv 依赖未锁定。
- 建议：附录补记 onnx/onnxslim/onnxruntime 精确版本与 AutoUpdate 事件，并标注「导出产物经 onnxslim slim（影响 sha256，重跑需同版本）」。

### P4
- **P4-1**｜引用行号微差：`preflight-report.md:38` 引 `detection_sfx.py:181`，pre-NMS peak 0.0855 实际在 `:179-180`。
- **P4-2**｜`export_smoke.py:27-31`、`nms_chain_probe.py:20-21`、`vram_probe.py:29-36` 硬编码 worktree/外部树绝对路径（含本 worktree 名与 `RAW_OUT`），目录改名即失效；建议参数化或 HEAD 相对化。
- **P4-3**｜`export_smoke.py:86` 的进程内常量重指建议在报告 §5 明示「未写回 src/环境变量/registry，进程结束即失效，生产 pin 仍为 `d87389af…`」（目前只写「仅运行时模块常量」）。
- **P4-4**｜措辞：`preflight-report.md:103` 把「1-epoch 半随机权重零候选」称 `fail-closed`（实为低质量权重零检出，门本身未触发）；§5 结论「可直接进入生产通道」宜前移「仅需按供应链流程更新 pin sha256」限定（尾句已有）。
- **P4-5**｜`raw/vram_probe_console.log` 内含 val 的 mAP 数字（coco8 重映射、无精度意义），报告正文未引用且已声明不含精度结论；建议在 §8 证据索引加一行「raw 日志中的 mAP 数字为合成/重映射冒烟的副产物，不构成精度证据」，防下游误读。
- **P4-6**｜`raw/vram_probe_summary.json` 的 `it_s` 与 `per_iter_median_s` 互为倒数（同一量两列），b2/b4/b8 的 `per_iter_all_median_s` 与 median 完全相同，冗余但不误导；可保留。

## 逐 AC 结论

- **AC1 PASS** — 「无 `.pt`」有多重旁证（siblings 三文件、`usedStorage≈41MB`、README 无外链、既有 `license-evidence.md:20-23` 同 revision 交叉印证）；②官方训练入口（换头 nc=4、`export`）实测在位 ✓；③策略选项 1 定案理由链成立且与二次裁决一致（选项 3 论证需按 P2-2 收敛，不改变定案）；④`imgsz=1024` 经 `_parse_imgsz` 列表路径命中 ✓。证据完备性见 P2-3。
- **AC2 PASS** — B/C 各一段静态深评已按合同「A 受阻即升级」执行，候选登记与类别面引证与 `M2-SFX-DETECT-EVAL` 一致；缺原始搜索证据（P2-3/P3-1），不改变「维持备胎」结论。
- **AC3 PASS** — 显存/吞吐数字与 raw 完全一致（我逐值复算 ✓），40 iter 超出合同下限，b8 推荐有依据；venv/CUDA 为运行级声明（未验证）。两处口径瑕疵 P3-3/P3-4。
- **AC4 PASS** — 链路 EXIT=0 证据链完整：SHA 门先证在位（`PROVIDER_FAILED`、pin `d87389af4350` 与 src 一致）→ 进程内重指 → names 逐字一致（经 src 断言把关，非自述）→ `metadata_parsed` → `(1,40,21504)` 同构 → 注入补齐非空路径（`_sfx_boxes` 签名/过滤顺序/NMS/2× 映射与 src 逐行吻合）。合成冒烟与精度结论切割干净（正文零精度主张，§7/附录均声明）。见 P4-3。
- **AC5 PARTIAL** — 备案表齐备、明确「不产出资格门」、用户接受声明指向 `DOMAIN-EXT-DIAG:69-74` 与 frontmatter 准确 ✓；但素材来源②状态与凭据错误（P2-1），且 ultralytics 立场引文无 raw（P3-1）。
- **AC6 PASS** — 静态可证：脚本对 `src` 仅只读 import、产物只写 `experiments/**`、`verification/**` 与外部树（worktree 内无 `task-envs/`），`doc/STATUS.md` 未被本 Task 触碰（STATUS 中本 Task 条目属释放时登记）。提交面 `git diff --check`/`git status`/6b73c92a 文件清单在无 shell 沙箱内**未验证**（reflog 已确认提交链与 base 一致）。

## 推荐下一步

本 Review 为**有条件通过**，条件闭合无需重跑实验（3 条 P2 全为文本/证据补档，P3 可择批处理）。基于当前仓库状态：

- **推荐 Agent：ZCode 子 agent（返修 r1）**，Reviewer 仍为 DSH 非作者；返修范围仅限 `verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md`、Handoff、Task 回填与新增 `raw/` 抓取快照，`src/**` 保持零触碰。
- **可直接转发指令**：

  > 在 worktree `G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode`（分支 `agent/zcode/M2-SFX-FINETUNE-PREFLIGHT`，delivery `6b73c92a`，tip `d23fde31`）执行 DSH r1 返修：①按 P2-1 修正报告 §6 素材来源②为可溯源表述（TA2B 2026-09-30 已履行；vol03 新增页窗口至 2026-11-02、状态=用户待办，引用 `M2-SFX-E2E-MATERIAL-40a8ceec.md:68`），删除 `74fa71e9` 误引；②按 P2-2 收敛选项 3 判语（「官方 freeze 配置面不可按类冻结＋类级梯度屏蔽越界且不解决共享 backbone 漂移」）；③按 P2-3 补抓 HF API 原始响应（`/api/models/chiqui7/yolo11-manga-seg`、`/revision/main`、`/refs`、`/tree/main?recursive=true`、README raw）落 `raw/`，并在报告中显式写出 `usedStorage` 的 revision 排除逻辑与 AC2「沿用既有 surveyed 口径」限定；④择批闭合 P3-1..P3-9 中与本次改动同文件的条目（尤其 P3-2 斜率数字、P3-5 脚本注释、P3-6 names 契约）。**禁止**：改 `src/**`、`tests/**`、`doc/STATUS.md`、生产 pin/registry/env；不得重跑 GPU 实验（如确需重抓网络，走用户代理）。完成后回填 Handoff r1 段与 Task 交付记录。
- **可并行释放**：`M2-SFX-DATA-INFRA`（T1a，`status: ready`，底座无关）已在 STATUS 中登记为三 Task 并行，不依赖本 r1 闭合；本 Task 的路线裁决（A′）可由编排会话在 r1 文本闭合后一并处理——裁决前无需新的下游 Task。
