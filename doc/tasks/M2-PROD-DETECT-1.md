---
id: M2-PROD-DETECT-1
title: "生产检测器集成第一刀：manga 域 RT-DETR-v2 provider + 装配 backend 选择（用户「继续」推进 2026-09-30）"
kind: feature
status: in_review
approval: user_directive_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30）
depends_on: []
base_commit: c8eefb4b
branch: agent/zcode/M2-PROD-DETECT-1
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-1-zcode
handoff: doc/handoffs/M2-PROD-DETECT-1-d7faea39.md
delivery_head: 0b0c9bc7
---

# M2-PROD-DETECT-1：生产检测器集成第一刀

## 来源与目标

- 来源：C4 评估（Gate 全 PASS：Recall 0.9618）+ C1 抽检校准（0 真实对白漏检、Precision 方向性下界）双重背书后，用户在本会话对「释放 docTR 检测器生产集成 Task」的建议回复**「继续」**（2026-09-30）——授权按推荐推进检测器家族的下一个自然 Task。
- 目标：把 C4 评估过的 manga 域检测器（ogkalu/comic-text-and-bubble-detector，RT-DETR-v2，**Apache-2.0**，HF revision `16e8a622`，model.safetensors sha256 pin `037930a8…`）接入生产检测路径，作为新的 production detection provider。
- **一个可观察的交付结果**：应用经配置选择 manga 检测器后，detect 链路产出真实 Region（真模型推理），docTR 保留为可切回 backend；CPU 路径 envelope 实测；sidecar 构建回归通过。

## 设计决策（代理裁决，用户可撤销）

- **默认 backend = manga**（`NEWMANGA_DETECTOR_BACKEND=manga|doctr`，默认 `manga`；可切回 `doctr`）。理由：本 Task 的产品目的就是启用更好的检测器；权重缺失时 fail-closed 语义与 docTR 同款（typed 错误+配置指引），不静默回退。此为产品行为变化，属本 Task wire 变化的实质，集成记录再次登记。
- **契约零修订优先**：`ports/detection/ports.py`（DetectionRequest/DetectionResult/RegionCandidate，provider 中立+匿名 label）预期无需改动——manga provider 输出 text 框作「word」角色进**既有冻结合并策略**（`detection_doctr.py` 的 MERGE_* 常数，**import 复用其值，不复制不改值**——C4/C1 的对照口径建立在生产合并上）。如实现中发现确需改契约/合并常数，**即停下登记待裁决，不得擅自改**。
- **权重形态**：目录（`model.safetensors` + `config.json` + `preprocessor_config.json`，逐文件 SHA-256 pin）默认解析 `<data root>/models/detector/ogkalu-comic-text-and-bubble-detector/`，`NEWMANGA_DETECTOR_WEIGHTS` 可覆盖（指向目录）；**无运行时下载**（fail-closed：目录/文件缺失=PROVIDER_NOT_CONFIGURED，hash 不符=PROVIDER_FAILED，同 docTR T1.1.1 纪律）。
- **懒加载**：transformers/torch 栈懒加载（同 docTR 模式），无重依赖的机器照常启动，首次 detect 报 typed 依赖缺失。

## Acceptance Criteria

- [x] AC1（provider 实现）：新增 `src/infrastructure/providers/detection_manga.py`——实现 `ports.detection` 接口；复刻 C4 评测的加载序列（`from_pretrained` 本地目录 + 三文件 SHA-256 逐文件 pin `037930a8…`/`b6d70793…`/`7e9e2245…`）；仅 text 类（1/2）出框、bubble 类丢弃；输出 word 角色框进冻结合并；fail-closed 四纪律（无下载/pin/缺失 typed/无伪造输出）全数落实。
- [x] AC2（装配 backend 选择）：`core_assembly.py` 装配段按 `NEWMANGA_DETECTOR_BACKEND` 选择 manga（默认）或 doctr；权重路径解析按 backend 各自默认；docTR 原路径行为零变化（切回 doctr 后现有行为/测试不受影响）；mock_local_providers 验收路径不受影响。
- [x] AC3（依赖授权与 CPU 实测）：`requirements.txt` 授权新增 `transformers==5.17.0` + `safetensors`（版本 pin；torch/doctr 不动）；**torch 2.14.0 CPU wheels 上模型加载+单页推理实测 EXIT=0**（C4 全程 GPU，CPU 兼容性是本 Task 必须闭合的缺口）；不兼容即停下登记（不得降级 torch）。
- [x] AC4（测试）：`tests/providers/test_detection_manga.py`（mock/单元：fail-closed 矩阵——缺目录/缺文件/hash 错/懒加载缺失依赖/空输出/bubble 丢弃）+ `test_detection_manga_real.py`（真实权重集成，权重缺失时 skip 并显式原因）+ 装配 backend 选择测试；全部先红后绿或与既有测试同风格。
- [x] AC5（envelope 实测）：CPU 路径延迟实测（ms/region，n≥3）入 `verification/M2-PROD-DETECT-1/envelope.md`；GPU 对照引用 C4（38.9s/511 regions ≈ 76ms/region）；sidecar 体积膨胀（如可测）如实记录。
- [x] AC6（sidecar 构建回归）：`packaging/m2ac5/build_sidecar.ps1` 构建通过（含新依赖）；M2-AC5 clean-start runner 25/25 保持 PASS；体积变化如实记录。
- [x] AC7（回归与纪律）：pytest 相关目录全绿（providers/m2_acceptance 35 passed 不回退）；cargo/vitest 留痕（预期零影响）；`git diff --check` EXIT=0；禁改路径零触碰。

## 允许修改范围

- `src/infrastructure/providers/detection_manga.py`（新增）
- `src/bootstrap/core_assembly.py`（仅检测器装配段）
- `requirements.txt`（仅追加 transformers/safetensors 行 + 注释）
- `tests/providers/**`（新增 manga 测试）、`tests/m2_acceptance/**`（如需增补装配场景）
- `packaging/m2ac5/build_sidecar.ps1`（如需最小适配；tauri.conf.json/spec 不动）
- `doc/tasks/M2-PROD-DETECT-1.md`、`doc/handoffs/M2-PROD-DETECT-1-*.md`、`verification/M2-PROD-DETECT-1/**`

## 禁止范围

- `ports/detection/ports.py` 及一切 contracts（契约零修订优先；确需改即停）
- `src/infrastructure/providers/detection_doctr.py` 现有行为（docTR provider 保留为可切回 backend；**其 MERGE_* 常数只可 import 不可改值**）
- `experiments/**`、C4/C1 全部产物（三个正式 JSON、c4 报告、license-evidence、spot-audit/**）
- `apps/**`、`packaging/**` 其余文件（tauri.conf.json、core_sidecar.spec 等）
- 训练/fine-tune、数据集策展
- 模型/大文件入库（权重只在本地/gitignored 路径；测试用绝对/环境路径引用）

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC4 单元 | pytest tests/providers/test_detection_manga.py | 权重可选（mock） | RUN：**27 passed**（含装配 backend 选择 5 场景） | implement commit；本表 |
| AC4 真实集成 | pytest tests/providers/test_detection_manga_real.py | 本地权重（task-envs C4 快照） | RUN：**2 passed**（合成漫画页 ≥1 候选 + 空白页零候选；权重缺失 module-skip 显式原因） | implement commit |
| AC3 CPU 实测 | 主 venv（torch 2.14.0 CPU）加载+单页推理 | transformers 安装 | RUN：**EXIT=0**（2.14.0+cpu × 5.17.0；加载 0.4s/770 张量；K01_R001 690x672 推理 2 text box + 2 bubble 丢弃） | verification/M2-PROD-DETECT-1/envelope.md |
| AC5 envelope | CPU n≥3 计时 | 同上 | RUN：**315.6 ms/页平均（n=5，310–319）**；GPU 对照 76.1 ms/页（C4 38.9s/511），CPU/GPU ≈ 4.1× | verification/M2-PROD-DETECT-1/envelope.md |
| AC6 sidecar | build_sidecar.ps1 + M2-AC5 runner | 打包链 | RUN：**构建 OK**（HEAD=d7faea39，pyinstaller 6.22.3，build venv 零改动）；runner **GATE PASS 25/25**；onedir 99,308,142 B/161 文件 vs base 99,286,538 B/161 文件（**+21.6 KB，+0 文件**）；NSIS 26.63 MiB vs 基线 26.62 MiB | verification/M2-PROD-DETECT-1/{cleanstart-gate.json,cleanstart-runner-stdout.log}、envelope.md 体积表 |
| AC7 回归 | pytest（providers+m2_acceptance+core）+ cargo + vitest | — | RUN：providers+m2_acceptance **309 passed + 1 既有环境性失败**（`test_no_model_runtime_is_installed_in_this_environment`：TASK-019 时代断言 venv 无 torch；在 base 2fee7d6e 上同 venv 同样失败，非本 Task 回归）；**m2_acceptance 35 passed 基数保持**；tests/core 77 passed；cargo **44 passed + 1 ignored**；vitest **31 passed**；`git diff --check 2fee7d6e..HEAD` **EXIT=0**；禁改路径专项 diff 为空 | 本表、handoff 验证表 |

## 依赖、风险与阻塞

- 依赖：无未完成前置（C4/C1 done 提供选型与校准背书；权重快照在 task-envs）。
- 风险：①**torch 2.14.0 CPU × transformers 5.17 兼容性未知**（C4 用 2.11.0+cu128）→ AC3 首先闭合，不兼容即停（合法登记）；②CPU 延迟可能显著高于 GPU（RT-DETR-v2 42.9M params）→ envelope 如实记录，性能优化不在本 Task；③sidecar 体积膨胀（transformers 数十 MB）→ 如实记录，分发优化后置；④默认 backend 切换对无权重用户是行为变化（docTR 可用→manga typed 缺失）→ 代理裁决已登记，错误消息带配置指引。
- 阻塞：无。

## 交付与运行记录（终态）

- 交付（2026-09-30，Owner=ZCode）：commit 链 `2e1d3deb`（claim）→ `d7faea39`=**实现**（`src/infrastructure/providers/detection_manga.py` 418 行 + `core_assembly.py` 检测器装配段 backend 选择 + requirements 授权 + 3 个测试文件 + envelope 证据；`test_detector_assembly.py` 显式 pin doctr backend 的最小适配一并登记）→ handoff/回填 commit（见 frontmatter `handoff`；`delivery_head` 由后续记录 commit 固定）。base=`2fee7d6e`。
- AC3 go/no-go 门：**PASS**——torch 2.14.0+cpu × transformers 5.17.0 兼容（加载 0.4s/770 张量；单页真实推理 EXIT=0），C4 cuda-only 缺口闭合；未降级 torch、未换模型。
- 装配语义：`NEWMANGA_DETECTOR_BACKEND=manga`（**默认**，代理裁决可撤销）|`doctr`（原路径逐字节保留）；`NEWMANGA_DETECTOR_WEIGHTS` 覆盖语义按 backend 分别指向目录（manga）/文件（doctr）；未知 backend 装配期 `ValueError`；mock 路径零触碰。
- 冻结合并：MERGE_* 常数与 `cluster_words_into_blocks` 从 `detection_doctr` **import 复用**（测试断言对象身份），未复制未改值。
- envelope：CPU 315.6 ms/页（n=5）vs C4 GPU 76.1 ms/页（≈4.1×）；sidecar 体积 +21.6 KB/+0 文件（ML 栈懒加载未进闭包）。
- 既有环境性失败留痕：`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment` 在主 venv（torch 已装）恒失败，base 上复现同样失败——TASK-019 时代的环境断言与 T1.1.1 后的 venv 事实冲突，属前 Task 遗留，非本 Task 回归（修复需另立 slice）。
- runner 证据卫生：`run_clean_start_e2e.py` 会重写 `verification/M2-AC5/raw/` 下 6 个历史文件；本轮产物已移至 `verification/M2-PROD-DETECT-1/`，历史文件经 `git checkout --` 原样还原（专项 diff 为空）。
