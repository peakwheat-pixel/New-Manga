---
id: M2-MANGA-WEIGHTS-SOP
title: "manga 权重 fetch/verify 脚本与安装 SOP（M2-PROD-DETECT-1 遗留 slice②/DSH r1 R6；Goal T2，自治执行 2026-10-01）"
kind: feature
status: in_progress
approval: user_autonomous_mode_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-PROD-DETECT-1]
base_commit: 095e314dad490781ec5d8c1b5b88d53ae0b5d39c
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

- [ ] AC1 脚本：`fetch_manga_weights.py`（下载/校验/幂等/--dest/--source-revision；离线校验模式 `--verify-only`）
- [ ] AC2 SOP 文档：WEIGHTS-SOP.md（四场景如上）
- [ ] AC3 实测：对本地快照 `--verify-only` PASS（EXIT=0 三文件 hash 符合）；真实下载路径实测一次（代理）或如实登记网络受限
- [ ] AC4 纪律：diff --check；权重不入库（.gitignore 面）；pytest 相关目录不受影响

## 允许/禁止

允许：`verification/M2-PROD-DETECT-2/scripts/**`、`verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`、Task/Handoff。禁止：src/**、requirements、packaging/**、权重入库。
