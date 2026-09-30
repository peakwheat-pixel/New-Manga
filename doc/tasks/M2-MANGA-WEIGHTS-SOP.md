---
id: M2-MANGA-WEIGHTS-SOP
title: "manga 权重 fetch/verify 脚本与安装 SOP（M2-PROD-DETECT-1 遗留 slice②/DSH r1 R6；Goal T2，自治执行 2026-10-01）"
kind: feature
status: in_review
approval: user_autonomous_mode_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-PROD-DETECT-1]
base_commit: 095e314dad490781ec5d8c1b5b88d53ae0b5d39c（契约编写时基线；分支/worktree 实际 base=46f079e8——release GOAL-DETECTOR-DEBT-CLEARING 在该契约基线之上，R-A10）
branch: agent/zcode/M2-MANGA-WEIGHTS-SOP
worktree: G:/CODEX/New Manga.worktrees/M2-WEIGHTS-SOP-zcode
---

# M2-MANGA-WEIGHTS-SOP：manga 权重 fetch/verify 脚本与安装 SOP

## 来源与目标

- 来源：M2-PROD-DETECT-1 DSH r1 R6——manga 三文件 pin 仅存在于代码，仓库内无 docTR 同款（`verification/T1.1.1/scripts/fetch_doctr_weights.py`）的 sanctioned 获取+校验路径；遗留 slice②（GOAL.md T2）。
- 目标：入库 `verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py`（从 HuggingFace 下载 ogkalu 三文件到目标目录、逐文件 SHA-256 校验=pin、幂等）+ `verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`（源码 venv 与发布形态两种安装路径 SOP）。

## 设计决策（代理裁决）

1. 脚本独立零重依赖（stdlib urllib，代理环境变量尊重 HTTP_PROXY/HTTPS_PROXY；可选 huggingface_hub 加速但非必需）。
2. 三 pin 常量与 HF revision `16e8a622` 硬编码+注释来源（与 detection_manga.py pin 同源声明，注释说明「代码 pin 为权威，脚本常量为部署便利副本，两者不一致时脚本 fail」）。
3. 默认目标目录=`<data root>/models/detector/ogkalu-comic-text-and-bubble-detector/`（`--dest` 可覆盖）；已存在且 hash 符合=跳过（幂等）；不完整/损坏=重下。
4. SOP 覆盖：源码 venv（fetch 脚本）、发布包（权重随包无需操作）、发布形态换权重（data root 覆盖）、代理环境。

## AC

- [x] AC1 脚本：`fetch_manga_weights.py`（下载/校验/幂等/--dest/--source-revision；离线校验模式 `--verify-only`）—— `verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py`（implement commit `1019ed6b`）：stdlib-only（urllib，尊重 HTTP_PROXY/HTTPS_PROXY，启动打印生效 proxy）；pin 常量为 `detection_manga.py` 权威 pin 的部署便利副本+fail-closed 注释；dest 解析 `--dest` > `NEWMANGA_DETECTOR_WEIGHTS`（目录语义；仅「存在且非目录」拒绝 EXIT=2，带点目录名放行——R-A4）> `<default_data_root()>/models/detector/ogkalu-comic-text-and-bubble-detector/`（复刻 `core_assembly.default_data_root`：`NEWMANGA_DATA_ROOT` > `%LOCALAPPDATA%`/`$HOME` + `New Manga`，脚本 docstring 注明镜像责任）；幂等（已验证 skip）/损坏重下/下载失败 EXIT=1；`--verify-only` 离线校验；`--source-revision` 漂移模式强制显式 `--dest` 且标注 UNVERIFIED（re-pin 流程见 SOP §5）。
- [x] AC2 SOP 文档：WEIGHTS-SOP.md（四场景如上）—— `verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`：场景 A 源码 venv（跑脚本）/ B 发布包（权重随包零操作，`_resolve_detector_weights_path` bundle fallback）/ C 发布形态换权重（数据根覆盖包内 + env override）/ D 代理环境（127.0.0.1:7890 示例、scheme 前缀、TLS 中间人、离线机搬运）；另含 pin 漂移 re-pin 流程与故障排查速查表。
- [x] AC3 实测：对本地快照 `--verify-only` PASS（EXIT=0 三文件 hash 符合）；真实下载路径实测一次（代理）或如实登记网络受限—— 两项均 PASS：(1) `--verify-only --dest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"` EXIT=0，三 hash 全符；(2) 真实下载经代理 `http://127.0.0.1:7890`（环境自带）从 HF `resolve/16e8a622/` 拉取三文件（含 171,543,900B model.safetensors）全部 pin 校验通过 EXIT=0（两轮：显式 `--dest` + `NEWMANGA_DATA_ROOT` 默认布局各一轮）；幂等二跑全 skip；篡改 config.json 后重跑自动重下恢复 pin；缺失目录/篡改文件 `--verify-only` EXIT=1；revision drift 无 `--dest` EXIT=2。
- [x] AC4 纪律：diff --check；权重不入库（.gitignore 面）；pytest 相关目录不受影响—— 变更仅 `verification/M2-PROD-DETECT-2/{scripts/fetch_manga_weights.py,WEIGHTS-SOP.md}` + 本 Task + Handoff；权重只落 task-envs 临时目录（实测后已清理）与 `%LOCALAPPDATA%` 布局，永不入库；`tests/**`、`pytest.ini`、`src/**`、`requirements*.txt`、`packaging/**` 零触碰。**R-A9 注（DSH r1）**：根 `.gitignore` 现无 `*.safetensors`/`*.pt`/`models/detector/` 条目，「权重不入库」护栏目前是**过程性纪律**（默认 dest 在仓库外 + `--dest` 纪律），无 gitignore 兜底；`.gitignore` 不在本 Task 允许路径，**gitignore 兜底规则由集成方补**（窄规则建议：`*.safetensors`、`*.pt`）。

## DSH r1 返修处置（2026-10-01，approved_with_conditions → 全条件闭合）

- **R-A1[P2] 已闭**：`download_file` 改为只落 `.part`；调用方在 `.part` 上校验 pin，通过才 `tmp.replace(target)`（对照 `fetch_doctr_weights.py:81-90` 先例）；mismatch 分支 `tmp.unlink()`，文案改「mismatched bytes were DELETED and nothing was installed — <target> is unchanged」；docstring 与 SOP §1 同步。复证：AC3d 篡改重下恢复 pin EXIT=0 + **错 pin 反证 PASS**（stub 错 pin 调 `download_and_verify` → EXIT=1、预置旧好文件逐字节原样、无 `.part` 残留——未验证产物零落盘）。
- **R-A2[P2] 已闭**：SOP 场景 B 路径改 `<安装目录>\resources\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector\`（与 `core_service.exe` 同目录，安装根 `%LOCALAPPDATA%\m2rc1-desktop`）；§0 第 3 条同步精确化；§6 加「路径缺 `resources\core-sidecar` 段 → 必然 EXIT=1」排查行。
- **R-A3[P2] 已闭（采 --force 方案）**：drift 模式目标目录非空 → EXIT=2，`--force` 放行并**全量重下**（不信任既有文件）；`--verify-only` 帮助注明忽略 `--source-revision`（R-A6 一并闭）；SOP §5 登记 drift 语义 + 「每次 drift 取件用新目录」建议。复证：非空无 --force EXIT=2 / 空目录 EXIT=0（3 文件 UNVERIFIED）/ `--force` 全量重下 EXIT=0。
- **顺手闭**：R-A4（env override 仅 `exists() and not is_dir()` 拒绝，带点目录名放行）、R-A5（`download_file` 异常 `tmp.unlink(missing_ok=True)` + SOP §6 `.part` 残留行）、R-A7（`dest.mkdir` 失败 → EXIT=2 + 指引）、R-A8（SOP 场景 C 加 `NEWMANGA_DATA_ROOT`/Tauri 用户根派生提示）。R-A9/R-A10 见上（AC4 注 + frontmatter 注）。
- **r1 修后复跑全录**：`--verify-only` 快照 EXIT=0；真实下载一轮（代理）3 文件全装 EXIT=0；drift 正反三用例见 R-A3；AC3d + 错 pin 反证见 R-A1。

## 允许/禁止

允许：`verification/M2-PROD-DETECT-2/scripts/**`、`verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`、Task/Handoff。禁止：src/**、requirements、packaging/**、权重入库。
