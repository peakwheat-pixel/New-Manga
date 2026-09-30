---
task_id: M2-PROD-DETECT-1
author: ZCode
recipient: Codex（集成）
base_commit: 2fee7d6efe4af8939762cc38f692f3fe8a207339
delivery_head: d7faea391b18aef1017dfb01d6a498c233a26869（实现 commit；本 frontmatter 记录的是实现时点，≠ Task frontmatter 的 delivery_head（随 review-fix 前移至 a016d38c）与锚点表语义——见「交付锚点记账」节）
status: ready_for_review
---

# Handoff：M2-PROD-DETECT-1（生产检测器集成第一刀）

## 交付结果

C4/C1 双背书的 manga 域检测器（ogkalu/comic-text-and-bubble-detector，RT-DETR-v2，Apache-2.0，HF revision `16e8a622`）接入生产检测路径。commit 链：`2e1d3deb`（claim）→ `d7faea39`（实现）→ 回填/记录 commit（Task frontmatter `delivery_head`）。

- **AC1** `src/infrastructure/providers/detection_manga.py`（新增，418 行；review-fix 后 436 行）：`MangaDetectionProvider` 实现 `ports.detection` 接口（**契约零修订**，`ports/detection/ports.py` 一行未动）。fail-closed 四纪律与 docTR 姊妹实现完全同款：①零依赖存在性探测（目录+三文件缺失=`PROVIDER_NOT_CONFIGURED`，消息带配置指引，含 "weights are not installed" 措辞以兼容既有 m2_acceptance 断言）；②懒加载 torch/transformers（缺失=`PROVIDER_DEPENDENCY_MISSING`，无重依赖机器照常启动）；③三文件逐文件 SHA-256 pin 在模型构建前校验（不符=`PROVIDER_FAILED`）；④`from_pretrained(..., local_files_only=True)` 即使联网也绝不到 hub。推理序列复刻 C4（processor→model→`post_process_object_detection` 源尺寸回映射，conf 0.5 冻结）；三类过滤保留 1=text_bubble/2=text_free、丢 0=bubble（计数入 options 审计）；text 框以 word 角色进**冻结合并**——`MERGE_*` 常数与 `cluster_words_into_blocks` 从 `detection_doctr` **import 复用**（测试断言对象身份，未复制未改值）；匿名 `manga-<n>` label、coordinate space=page-global、空页=零候选、推理/载荷异常 typed。
- **AC2** `src/bootstrap/core_assembly.py`（仅检测器装配段 + 对应 import 行）：`NEWMANGA_DETECTOR_BACKEND=manga`（**默认**，代理裁决已登记、可撤销）|`doctr`。doctr 分支代码原样保留（切回后行为零变化）；`NEWMANGA_DETECTOR_WEIGHTS` 覆盖语义保持但按 backend 分义（manga=目录、doctr=文件）；默认路径均为 `<data root>/models/detector/<...>`；未知 backend 装配期 `ValueError`（消息列合法值）；`mock_local_providers` 路径零触碰。装配段之外的其他行零改动（`git diff` 可核）。
- **AC3** requirements.txt 追加 `transformers==5.17.0` + `safetensors==0.8.0`（pin + 出处注释；torch/doctr 行未动）。**CPU 兼容门 PASS**：torch 2.14.0+cpu × transformers 5.17.0，权重快照三文件 SHA-256 校验 OK，加载 0.4s（770 张量，42,733,137 params），单页真实推理 EXIT=0。未降级 torch、未换模型。
- **AC4** `tests/providers/test_detection_manga.py`（27 项，review-fix 后 28 项——新增 NaN 几何 typed 用例：fail-closed 矩阵、bubble 过滤纯函数、detect 诚实性、合并常数身份、Qt-free 装配 backend 选择 5 场景）+ `test_detection_manga_real.py`（2 项真实权重推理；权重经 `NEW_MANGA_MANGA_WEIGHTS` env 或已知本地快照，缺失 module-skip 显式原因）。既有 `test_detector_assembly.py` 做**最小适配**：显式 `NEWMANGA_DETECTOR_BACKEND=doctr`（默认 backend 变 manga 后该测试若不适配必然失败；适配后其验证语义——docTR 装配 fail-closed——不变。属允许路径 `tests/providers/**` 内的必要适配，登记给 reviewer）。
- **AC5** `verification/M2-PROD-DETECT-1/envelope.md`：CPU 315.6 ms/页（n=5 真实 manifest region，稳态，310–319）vs C4 GPU 76.1 ms/页（38.9s/511）≈ 4.1×；sidecar 体积前后对比同文件。
- **AC6** sidecar 构建回归 PASS + runner 25/25 PASS + 体积 +21.6 KB/+0 文件（ML 栈懒加载未进闭包；spec 未动）。口径（DSH r1 R1 措辞更正）：**构建不回退 + ML 栈不进闭包（发布形态需外部运行时）**——build venv 为 pyinstaller-only，+0 文件正说明 transformers/torch 不进闭包；发布包内默认 manga backend 的 detect 会 `PROVIDER_DEPENDENCY_MISSING`（docTR 在 base 同样如此，非本 Task 回归），分发/运行时方式登记为后续 slice 候选（见「风险与遗留」）。
- **AC7** 回归与纪律全过（见验证证据）。

## 交付锚点记账（三值统一，DSH r1 R10）

| 锚点 | 值 | 来源 |
|---|---|---|
| release base | `c8eefb4b` | Task frontmatter `base_commit`——释放时 main 的 HEAD（见 `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`） |
| branch base | `2fee7d6e` | release commit 之后创建 `agent/zcode/M2-PROD-DETECT-1` 分支的实际 base；本 Handoff frontmatter `base_commit` 与所有 diff/复跑基线用它 |
| delivery_head | `40d4ab64` | `0b0c9bc7` 为证据+handoff commit；`40d4ab64` 仅是记录 delivery_head 的 commit（Task frontmatter 以记录 commit 为准） |

review-fix（DSH r1）后：delivery_head 前移至 **`a016d38c`**（review-fix 终态，最后实质 commit；Task frontmatter 已同步，其后仅存在单独更新该行的记录 commit，零内容变化）。

envelope 的 `params=42,733,137`（加载后 tensor 元素计数）与 C4 记录的 safetensors `F32=42,861,209`（文件张量口径）口径不同，非矛盾——注已补入 `verification/M2-PROD-DETECT-1/envelope.md` §AC3。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC3 CPU 门 | `"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" "G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-1-work/ac3_cpu_gate.py"` | torch 2.14.0+cpu、transformers 5.17.0、@d7faea39 | PASS（EXIT=0；2 text box + 2 bubble 丢弃） | envelope.md §AC3 |
| AC1/AC4 单元+装配 | `PYTHONPATH=src <主 venv> -m pytest tests/providers/test_detection_manga.py -q` | 同上 @d7faea39 | PASS（27 passed） | handoff 复跑可现 |
| AC4 真实集成 | `PYTHONPATH=src <主 venv> -m pytest tests/providers/test_detection_manga_real.py -v` | 本地快照（三 hash 逐文件校验） | PASS（2 passed，8.15s） | 同上 |
| AC5 envelope | `<主 venv> "G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-1-work/envelope_cpu.py"` | 同上，预热 1 页不计 | PASS（n=5，315.6 ms/页均） | envelope.md §AC5 |
| AC6 sidecar | `powershell -File packaging/m2ac5/build_sidecar.ps1 -Force`（worktree 与主 repo base 各一次） | HEAD=d7faea39 / base=2fee7d6e，build venv 未动 | PASS（`build_sidecar: OK` 两次；+21,604 B/+0 文件） | envelope.md §体积 |
| AC6 clean-start | `<主 venv> packaging/m2ac5/run_clean_start_e2e.py --installer <NSIS>` | 安装包 27,924,371 B @d7faea39 | PASS（**GATE PASS 25/25**，EXIT=0） | verification/M2-PROD-DETECT-1/{cleanstart-gate.json,cleanstart-runner-stdout.log} |
| AC7 pytest | `PYTHONPATH=src <主 venv> -m pytest tests/providers tests/m2_acceptance -q` → `tests/m2_acceptance -q` → `tests/core -q` | @d7faea39 | providers+m2_acceptance 309 passed + 1 既有环境性失败（见下）；m2_acceptance **35 passed 基数保持**；core 77 passed | Task 测试表 |
| AC7 cargo/vitest | `cargo test`（src-tauri）、`npx vitest run`（frontend） | sidecar bundle 在位 | PASS（44 passed + 1 ignored；31 passed） | Task 测试表 |
| AC7 纪律 | `git diff --check 2fee7d6e..HEAD`；`git diff --name-only`；禁改路径专项 diff | @d7faea39 | EXIT=0；8 文件全在允许路径；ports/doctr/experiments/apps/spec/runner/PLAN/STATUS 专项 diff 为空 | 本表 |
| NOT_RUN | 真实 CUDA 路径的 provider 实测 | 无 GPU wheel 授权（torch CPU wheels=支持配置） | NOT_RUN（C4 GPU 数字为资格证据；GPU wheels 属 T3.2.1 范围） | — |

**既有环境性失败（非本 Task 回归）**：`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment` 断言本环境无 torch（TASK-019 时代的环境证据测试）；T1.1.1 起主 venv 自带 torch，该断言在 base `2fee7d6e` 上用同一 venv 复跑同样失败。属前 Task 遗留的环境耦合断言，修复（条件化/挪舱）需另立 slice，本 Task 未越权处理。

**证据卫生说明**：clean-start runner 会重写 `verification/M2-AC5/raw/` 下 6 个历史文件；本轮产物已移入 `verification/M2-PROD-DETECT-1/`，历史文件经 `git checkout --` 原样还原（M2-AC5 证据零改动）。

## 接收方式

- 分支 `agent/zcode/M2-PROD-DETECT-1`，worktree `G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-1-zcode`，实现 head `d7faea39`。
- 复现检测链：安装 transformers 后（或用主 venv）`PYTHONPATH=src` 跑上表命令；真实推理需本地权重快照（`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`，sha256 `037930a8…`/`b6d70793…`/`7e9e2245…`；权重永不入库/下载）。
- backend 行为：默认 `manga`（无权重时 detect 步 typed `PROVIDER_NOT_CONFIGURED`，不静默回退）；`NEWMANGA_DETECTOR_BACKEND=doctr` 切回 docTR，行为与 T1.1.1 交付逐字节一致。

## 下一任务建议（必填）

- Task ID / 标题：M2-PROD-DETECT-1 的非作者 Review（reviewer=DeepSeek Harness）→ Codex 集成；无需新立实现 Task。
- 推荐 Agent / Reviewer：DSH（非作者静态 review）→ acting Codex 集成。
- 推荐原因与前置依赖：本 Task 已 in_review；协作协议要求非作者审查 + 集成验证后才进 done。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-PROD-DETECT-1`，worktree 已存在（`.../M2-PROD-DETECT-1-zcode`），base `2fee7d6e` / 实现 head `d7faea39`。
- 允许修改路径：review 意见处理限于本 Task 允许路径（detection_manga.py / core_assembly.py 检测器段 / requirements.txt 追加行 / tests/providers/** / Task/Handoff/verification/M2-PROD-DETECT-1/**）。
- 禁止范围与新增授权条件：同本 Task 禁止范围（ports/、detection_doctr.py 行为、experiments/**、C4/C1 产物、tauri.conf.json、core_sidecar.spec 等）；默认 backend=manga 为代理裁决，review/集成中若被质疑，撤销只是装配段默认值翻转（测试已双向覆盖）。
- 交付物：Task 测试表 + 本 Handoff + envelope.md + cleanstart 证据两件。
- 验证命令、环境与完成 Gate：上表「验证证据」全部命令可复现；Gate=AC1-AC7 证据齐 + 非作者 review 通过 + Codex 集成验证。
- 可直接转发给 Agent 的指令：对 `agent/zcode/M2-PROD-DETECT-1` @ `d7faea39` 做 M2-PROD-DETECT-1 非作者 review：重点核 `src/infrastructure/providers/detection_manga.py` 的 fail-closed 四纪律与 hash pin、`core_assembly.py` 装配段 backend 选择语义与 doctr 分支零变化、`test_detector_assembly.py` 最小适配的正当性、以及 Task 测试表与 handoff 证据的一致性；模板用 doc/templates/REVIEW.md。

## 风险与遗留

- **默认 backend 切换是产品行为变化**（无权重用户从 docTR 可用变为 manga typed 缺失）：代理裁决已登记（Task §设计决策），用户可撤销；错误消息带配置指引。
- **CPU 性能**：315.6 ms/页 ≈ 4.1× GPU；detect 逐页一次性成本，性能优化不在本 Task（Task 风险②如实记录）。
- **envelope 外推限制**：n=5 页均来自 K01 案例、690px 宽；长条 webtoon 大页未测（envelope.md §已知边界）。
- **transformers 依赖面**：5.17.0 引入 typer/rich/tokenizers 等传递依赖进主 venv（requirements 已 pin 主版本）；sidecar 闭包不进（懒加载+EXCLUDED 纪律），分发体积影响 +21.6 KB。
- **registry_readiness 环境断言遗留**：见上，需另立小 slice 处理（条件化或挪至显式环境门）。
- **后续 slice 候选（DSH r1 review-fix 登记）**：①发布形态检测器运行时/权重分发（R1：发布包内默认 manga backend 的 detect 报 `PROVIDER_DEPENDENCY_MISSING`，docTR 在 base 同样如此；本 Task 仅源码 venv 形态可用 + 闭包纪律）；②manga 权重 fetch/verify 脚本与部署 SOP（R6：本 Task 仅代码级 pin，仓库内无 docTR 同款 sanctioned 获取+校验路径）。
- 回退方法：装配段 `NEWMANGA_DETECTOR_BACKEND=doctr` 一键回退（零代码回退）；彻底回退 revert 实现 commit 即可，docTR 路径未动。

## review-fix 记录（DSH r1，2026-09-30）

DSH 非作者 Review r1（`approved_with_conditions`，2×P2+8×P3/P4，报告在 task-env `M2-PROD-DETECT-1/dsh-review-r1.md`）返回后，Owner（ZCode）按裁决完成 R1–R10 处置：文档口径更正（R1/R2）、测试守卫收紧（R3 全量 hex + `is` 身份断言）、docstring 引用对齐（R4）、错误消息 backend 指引（R5）、slice 登记（R6）、空串 env 边界差异注释（R7）、numpy/字体 skip（R8）、NaN 几何 typed 校验（R9）、锚点三值记账（R10）。改动仅落允许路径；行为变化仅 `detection_manga.py` 的 NaN 拒绝（新增 typed 校验）与缺目录消息追加指引，docTR 路径与装配语义零变化。详见 Task「DSH r1 review-fix 记录」与测试表 review-fix 行。

## 实验附录（不适用）

本 Task 为 feature 实现；模型/权重证据（来源、许可、hash、硬件、网络策略）已冻结于 C4/C1 产物与 `verification/M2-DOCTR-QUAL/`，本 Task 仅消费。
