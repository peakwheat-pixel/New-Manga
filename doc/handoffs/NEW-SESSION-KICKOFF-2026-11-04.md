# 新会话启动包（New Session Kickoff）— 2026-11-04

> 用途：用户将新开一个 DSH 对话，继续 New Manga 项目自动推进。**新会话先读本文件，然后按提示词区直接开工**；不需要用户再补充上下文。

## 1. 当前快照（交接事实）

| 项 | 值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main`（唯一真实仓库） |
| HEAD（交接时） | `fc158e5aa7232913bac1665675ac0a85fe0a781e`；工作树 clean；**未 push** |
| 当前权威指针 | `doc/STATUS.md` 当前 Task：**FEA-10 `ready`**；`doc/REBASELINE_PLAN.md` READY 节点：**FEA-10** |
| 前序刚完成 | `FEA-10-PREREQ-1` **done**（M2-C1 rev 2.12 协议注册 + host `allowedRunErrorCodes`；集成 `728c8bb0`；实现 Review r1 approved P0/P1=0，P2=1 非阻断债务 `DEBT-FEA10P-01`） |
| FEA-10 状态 | **ready**；scope 经 r1–r6 独立 review 收敛，**r6 approved P0=0/P1=0/P2=2**；Appointment 已由 DSH 完成（`doc/reviews/FEA-10-appointment.md`）；Owner=Codex 待认领；硬前置已 done |
| FEA-10 卡 | `doc/tasks/FEA-10.md`（AC1–AC10、文件级写域、验证矩阵） |
| 冻结面 | 17 个 pin（`verify_pins.ps1` 17/17）；C-05 v1.2/C-15 v1.1/C-16 v1.1/C-07 等**字节不得改**；FEA-08/FEA-09 closeout 文件不得改；共享组合根 DSH 单点提交 |
| 工作区派生产物 | 只放 `G:\CODEX\New Manga.workspace\`；不得清理/GC/prune 受保护资源 |
| 最近门禁基线 | build 0/0；.NET 全量 **1344 passed / 0 failed / 74 skipped**（PREREQ 交付时）；`check.ps1` PASS（3 warnings）；pins 17/17；C-07 inventory `--check` PASS |

## 2. 用户本轮长期授权（立即生效，写进新会话目标）

原文授权要点（用户 2026-11-04，新会话延续）：

- **不要停下来问我、不要等我确认**；需要拍板的写进进度文件「待裁决」区并附推荐，但不要卡住。
- **裁决优先交 Codex**；**Codex 没有额度就交给别人**（本项目既有故障转移候选为 **ZCode**；若 ZCode 也不可用，DSH 作为 Lead/Architect 可自行裁决并在进度文件记录结论与依据，继续推进非阻塞工作）。
- 全部授权：范围冻结、Agent 分配、Review Appointment、findings 处置、集成验证、Task 生命周期、提交（**不 push**）；用户已授权自动推进。
- 唯一停止条件：**可推进项耗尽**，或**同一阻塞连续 3 轮无进展**；否则持续自动推进。
- 安全/范围红线：不 push；不改冻结契约字节；不碰真实用户数据/AppData/外部卷/回收站；不新建依赖；UI 不直连 DB；Review 必须上下文独立（实现者不得自审）。

## 3. Agent 调用资料（新会话直接用）

### Codex（裁决/实现/Review 首选）

- 当前可执行文件：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\a159911ff70742e9\codex.exe`（版本 `codex-cli 0.166.0-alpha.6`）。
- 若路径随更新变化：扫描 `C:\Users\49745\AppData\Local\OpenAI\Codex\bin\*\codex.exe`，取存在 `codex.exe` 的目录。
- 只读 Review/裁决：
  `codex.exe exec --skip-git-repo-check -s read-only -m gpt-6.1-sol -c model_reasoning_effort="medium" -o <out.md> "<prompt>"`
- 实现（可写工作树）：把 `-s read-only` 换成 `-s workspace-write`；仍**禁止 commit/push**（DSH 提交）。
- 额度耗尽时错误含 “usage limit / try again at HH:MM”；记录重置时间，立即切 ZCode，不要空等。

### ZCode（Codex 不可用时的首选故障转移）

- 命令模板：
  `node "E:\Program Files\ZCode\resources\glm\zcode.cjs" -p "<prompt>" --cwd "G:\CODEX\New Manga" --mode yolo --surface terminal --locale zh-CN --json`
- 只读 Review 用 `--mode plan --disallowed-tools "Edit Write"`。
- 环境变量：
  `ZCODE_DATA_BASE_DIR=G:\zcode`；`ZCODE_BUILTIN_PROVIDER_CONFIG_FILE=E:\Program Files\ZCode\resources\config\provider\zcode-builtin.json`；`ZCODE_PERSONAL_PROVIDER_CONFIG_FILE=G:\zcode\.zcode\v2\provider_config.json`
- 429/额度耗尽：与 Codex 同样记入进度，切下一可用路径（fresh Codex 会话或 DSH 子 agent 实现/审查；DSH 不得自审自己实现）。

### Review 独立性

- 每个 Review 用**全新上下文**；不得由实现/返修者自审。
- DSH 主会话不得审核自己实现的变更；可派独立子 agent，或交 Codex/ZCode 新会话。
- Review 报告归档 `doc/reviews/`；记录 reviewed_head、身份/来源、NOT_RUN。

## 4. 新会话开工顺序（不要问用户）

1. 读 `AGENTS.md` → 本文件 → `doc/STATUS.md` → `doc/REBASELINE_PLAN.md` → `doc/tasks/FEA-10.md`、`doc/reviews/FEA-10-appointment.md`、`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`。
2. `git status --short`、`git rev-parse HEAD`、`pwsh tools/governance/check.ps1`、`verify_pins.ps1` 确认基线。
3. 用 goal 工具建立自动推进目标（max rounds 256；目标=按 STATUS/PLAN 自动完成当前 ready Task 直至无可推进项/同一阻塞 3 轮），然后按下方提示词执行。
4. 释放 FEA-10 给 Codex Owner：写 `status: in_progress`、claimed_at；实施 FEA-10 卡；按门禁跑 build/定向/全量/真实 IPC/check/pins；证据 `verification/FEA-10/**`；Handoff；置 `in_review`。
5. DSH 集成提交 → 全新 Codex 实现 Review → approved 后 closeout `done`（含 EV commit 回填、Resource Manifest、closeout 记录）。
6. 继续下一 Task（FEA-11 建卡/scope review；其后 FEA-12 需 `G-DELETE-IMPL`、FEA-13/14/15 视情况；GIT-CLEAN 线按 Codex 裁决排序）。
7. 每轮写 progress/checkpoint；阻塞连续 3 轮无进展才停。

## 5. FEA-10 实施提示（给 Owner Codex）

- 只写 `doc/tasks/FEA-10.md` frontmatter `allowed_paths`；不改冻结字节/组合根/FEA-08/09 closeout/Run runtime 之外范围。
- AC1–AC10 与验证矩阵见卡；关键：PreparedRun 零 DB/零执行、preparedDigest 冻结四元组、payloadDigest 同源、retry 两分支、SC-R09 durable receipt、candidate-only + 10 项故障注入、多 Region vs Pipeline seam 事务单位、真实 Host↔Core IPC（`NEWMANGA_FEA10_IPC=1`）。
- 不 push、不 commit（DSH 提交）；证据/Handoff/AC 矩阵必须含命令/EXIT/隔离 DataRoot。
- 测试可能重写 `verification/FEA-09/**`（wire-redacted/ipc）；跑完用 `git checkout` 恢复，保持 FEA-09 证据零 diff。
- 注意 P2 非阻断：`DEBT-FEA10P-01`（dispatcher 接线级测试）可在 FEA-10 或后续小修补。

## 6. 新会话首条提示词（可直接粘贴）

见用户消息中的代码块（由 DSH 在聊天回复给出）；核心是：读取本启动包、建立长期 goal、按 STATUS/PLAN 自动推进、裁决 Codex 优先/额度耗尽转 ZCode/再转其他可用 Agent、不询问用户、不 push。
