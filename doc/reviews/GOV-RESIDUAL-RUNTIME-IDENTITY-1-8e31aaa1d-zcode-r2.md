---
task_id: GOV-RESIDUAL-RUNTIME-IDENTITY-1
reviewer: zcode
author: dsh
base_commit: 43a7d73c850f669cc2595343a1747a661c277f2e
reviewed_head: 8e31aaa1dff113e5f95ca7db5ece0de00126059a
decision: approved
---

# Review：GOV-RESIDUAL-RUNTIME-IDENTITY-1（r2 限定复审，zcode）

复审日 2026-10-22。只读复审，未修改除本文件外的任何文件。**范围限定：仅复核 r1 三项 findings（R-001/R-002/R-003）的处置与 r1→r2 增量的反向检查；r1 已核实的取证结论（七项错误身份、历史展开值、SHA 交叉校验、唯一保护缺口、禁止范围合规）不重开。**

## 范围（r1→r2 增量）

- 提交链：`56260c145` → `a161cfb7e`（自指两行修复，2026-10-22 09:30）→ `8e31aaa1d`（r1 返修应用）。`git rev-parse HEAD` = `8e31aaa1d`。
- 增量 diff：5 个文件、+27/−10——`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md`、`doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md`（+13）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。全部在 Task `allowed_paths` 内。
- 与 r2 指令预期的「4 个文件」偏差 1 个：Handoff +13 行。经 Read 核实为「交付后自查返修（2026-10-22，dsh）」段（Handoff L49-60），内容为两行修复披露、修复后复跑 7 errors、计数时效说明与 EV pin 未动声明——属允许范围且内容属实，**不构成越界**。
- 证据目录 `git diff 56260c145..8e31aaa1d -- verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/` **输出为空**：EV-01..EV-07 全部字节未动。
- 复审环境披露：主会话 Bash 不可用（同 r1），git 核验与活树复跑经只读 Explore 子代理执行，命令限于授权清单（`--out` 仅写 `G:/CODEX/New Manga.workspace/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/zcode-review-r2-audit/`；未跑 `--apply`；无 git 写操作）。

## R-001（P1，verification-log §4 COUNTS 矛盾）— 判定：已处置

1. Task「交付与运行记录」L85 追加勘误段：COUNTS 行（2627/1926/7/276）取自 Task 文件入库前的 probe 运行，`raw/protection-evaluation.json`（2636/1934/9/281）由入库后的运行写入；两次运行的 7 项目标错误身份完全相同，差异仅为本 Task 自身文档新增声明与 2 个自指 fatal；EV-07 字节不改、该段为唯一勘误来源。**与我 r1 的独立复跑证据（活树 2636/1934/9/281）完全吻合。**
2. EV-05/EV-07 字节未动：证据目录区间 diff 为空（见上）。
3. 勘误以追加方式落 Task（未改写已 pin 日志正文）——符合 r1 处置要求。

## R-002（P2，自指两行引入 2 个 fatal）— 判定：已处置

1. `a161cfb7e` 经 `git show` 核实仅改 Task Resource Manifest 两行为 `NOT_APPLICABLE`（`| branch | NOT_APPLICABLE | NOT_APPLICABLE | — | … |` 与 `| temp（系统 Temp 遗留观察） | NOT_APPLICABLE | NOT_APPLICABLE | — | … |`）并附自查返修记录；Handoff L49-60 同步披露。
2. 口径条款在位（Task L86 + Handoff L58）：`2627/1926/7/276` 为 base 时点（本 Task 入库前）口径；入库后实测 `2636/1934/281`、返修后 errors 回到 7；后续 Task 的「7 errors」断言必须指「7 项历史错误身份」或以实施时实时基线为准。
3. 活树复跑（本 Review 独立执行）：`2636 declarations / 1934 protected roots / 7 errors / 281 warnings`，`EXIT=2`；7 条 ERROR 逐条核对**全部**来自 `doc/tasks/P19.md`、`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`、`verification/P19-UI-FIX-1/resource-manifest.json` 的历史身份，**不含本 Task 文件**。
4. 保护集合未缩小：两行修复前因 `DECL_RELATIVE_UNRESOLVED`/`DECL_GLOB` 被拒、从未注册为保护根（修复前后 protected roots 均为 1934）；11 个 `p19*` Temp 遗留目录的登记信息保留在文字列与 `historical-env-evidence.json` 的 `residual_temp_observation`。与「不缩小既有保护集合」禁令相容。

## R-003（P2，导航状态漂移）— 判定：已处置

三处权威导航当前原文（本 Review Read 核实）：`doc/STATUS.md:7`（`in_review`）、`doc/REBASELINE_PLAN.md:9`（`in_review（七项身份只读取证已交付；R1 3项返修完成待r2；…）`）、`doc/TASK_LEDGER.md:44`（`in_review`）——三处一致，且与 Task frontmatter `status: in_review` 对齐。

## 反向检查

- 禁止路径：`git diff --name-only 56260c145..8e31aaa1d -- tools/governance/ doc/tasks/P19.md verification/ENV-BUNDLE-1-FU1/resource-manifest.json verification/P19-UI-FIX-1/resource-manifest.json` 为**空**（Handoff 出现在另一组过滤中属 allowed_paths，见范围节）。
- 无新声明错误：活树复跑 7 errors 全为历史身份（见 R-002 第 3 条）。
- 工作树 tracked 修改 0（`git status --porcelain` 非 `??` 行为空）；`git diff --check` 与 `git diff --cached --check` 均 exit 0。
- 无删除/迁移/归档/GC/prune/push/reset/stash 痕迹；两个新提交均为文档返修。

## 备注（不构成 finding，不阻塞）

1. Task L86「本 Task 入库后同一时刻实测为 `2636/1934/7/281`」中「同一时刻」措辞有歧义——`7` 是 `a161cfb7e` 返修后的 errors（入库后、返修前为 9，已在 L85 勘误段如实记录）。数字经本 Review 复跑验证为真（返修后口径）。
2. `STATUS.md`/`REBASELINE_PLAN.md` 中「待 r2」字样在本 Review 通过后应由维护者在集成/done 流程更新，属预期内导航维护。

## 结论

**decision: approved（限 reviewed_head `8e31aaa1d`）。**

r1 三项 findings 全部按处置要求到位：R-001 勘误真实且与独立复跑证据吻合、EV 字节未动；R-002 自指修复有效（活树回到 7 项历史错误）且口径条款在位；R-003 三处导航同步一致。反向检查无越界、无新增声明错误、无保护削弱。r1 已核实的核心取证结论（唯一真实保护缺口 = `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（E6/E7，hits=0）；其余五项无现存资源/无缺口；无一项需用户裁决）维持有效。

重申边界：本 approved **不解除任何 fatal 声明错误、不构成任何清理/删除授权、不改变解析器语义**；后续 `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` 须按 Handoff §5 的范围与禁止清单实施。按 Task AC6，done 前仍需 Owner（dsh）在 main 完成集成复验。
