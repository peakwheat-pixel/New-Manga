---
id: TASK-040
title: 接通 TASK-039 的 clean_probe 生产注入（含 F-12 口径修正）
kind: bugfix
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Codex
depends_on: [TASK-039]
base_commit: 40d97d52d272035db723018102970ba40c9c9f62
branch: agent/zcode/TASK-040-clean-probe-injection
worktree: G:/CODEX/New Manga.worktrees/TASK-040-zcode
integration_commit: e1be885bb3a26f962a6b1ce01a8f220949c6ab03
---

# TASK-040：接通 TASK-039 的 `clean_probe` 生产注入（含 F-12 口径修正）

**READY（2026-09-18 用户指示"先 TASK-040 还是 43"后由 Codex 释放，排列为次优先）**：Owner=`ZCode`、Reviewer=`Codex`（**非作者**）、base=`40d97d5`、branch/worktree 见顶部元数据。开工前置 `in_progress` 并 `git merge master`。

## 背景（本切片是"已修好但生产不可达"的第三例）

[TASK-039](TASK-039.md) 修好了 planner 的 Clean 可用性判定（`_clean_available` 改为探测 artifact 而非"无人写入的 stage"），但修复是以 `PipelineService.clean_probe` **可选参数**形式落地的，而**生产装配从未注入它**（`git grep clean_probe src` 仅命中 `application/tasks/service.py`）。

- 后果：生产环境里 render-only 命令（`RERENDER_*`）跨 run 仍规划 `BLOCKED(missing_clean_artifact)` —— **不比修前差、也不是回归**，但修复等于未生效。
- 同时登记有 **[F-12](../../doc/reviews/POSTHOC-WINDOW-DSH-2026-09-18.md)**：`src/application/tasks/service.py:~486` 的 docstring 声称 `clean_probe` "injected at assembly (AC 2)"，而事实并非如此 → **口径与实现不一致**。
- 本窗口同类问题已出现三次（tile 工厂、文档导入、`clean_probe`）→ 本切片须把"**接线断言**"作为交付的一部分（见 AC ②）。

## Acceptance Criteria

- [x] **AC ①（注入）**：在装配处（`src/bootstrap/app.py`）为 `PipelineService` 注入 `clean_probe`。**必须复用既有能力**（如 artifact 仓储/locator 对 `clean` 的 current 查询），**不得新造第二套 Clean 判定**；探针的**来源与语义须在 Handoff 写明**（谁提供、判什么、返回什么）。
- [x] **AC ②（接线断言，必做）**：在装配契约测试（`tests/core/test_bootstrap.py`）中新增断言：**生产装配得到的 `PipelineService` 携带非 `None` 的 `clean_probe`**。这是本切片的核心价值——让"接线漏做"不再可能悄悄通过。
- [x] **AC ③（生产行为 + 判别力）**：给出对照证据——当页**存在 current Clean artifact** 时，render-only 命令**不再** `BLOCKED(missing_clean_artifact)`；**缺失**时仍 fail-closed 且原因入 provenance（既有守卫不得放宽）。新用例对**修前代码**失败并留证。
- [x] **AC ④（F-12 口径修正）**：把 `service.py` 中"injected at assembly (AC 2)"的表述改为与实现一致（注明：**由本切片接通**）；并同步 [TASK-039](TASK-039.md) 的 AC ② 注记口径（在其 Task 文件或 STATUS 记一处修订，**不得**回改已入档的 Review 结论）。
- [x] **AC ⑤（回归与证据）**：`tests/core`、`tests/pipeline`、`tests/providers` 与全仓 **passed 不减少**；全仓串跑 **≥5 次**逐次记录（同一 shell + 同一 venv：PowerShell + `TASK-012-py312`），**passed/skipped 分列 + skip 原因**；不得新增 `skip`/`xfail`。
- [ ] **AC ⑥** 交付 Handoff、取证，经**非作者** Review 与 Codex 集成后才能 done；并在 STATUS 记录 F-12 关闭。（Handoff 已交付，待 Codex Review 与集成）

## 允许修改范围

- `src/bootstrap/app.py`
- `src/application/tasks/service.py`（**仅** docstring/口径，**不得**改判定逻辑——那已在 TASK-039 收口）
- `tests/core/**`、`tests/pipeline/**`
- `doc/tasks/TASK-040.md`、`doc/handoffs/TASK-040-*.md`、`verification/TASK-040/**`、`doc/STATUS.md`（仅登记关闭与口径修订）

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、路由判定算法、SFX 策略语义（TASK-032/035 已冻结）、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`；不得把 `BLOCKED`/`NOT_RUN` 记为通过。
- **不得**借本切片顺手改 `_clean_available` 的判定逻辑或把探针默认值改成"永远有 Clean"之类的宽松实现（探针必须真实反映 current Clean 的存在性）。

## 依赖、风险与阻塞

硬依赖：TASK-039（`done`，提供 `clean_probe` 可选参数）。

风险：注入后**生产行为会变化**（render-only 命令由 BLOCKED 转 RUN）→ AC ③ 的对照证据必须证明"仅当 Clean 真实存在时才转 RUN"，并覆盖"缺失 Clean"的负例。

## 交付与运行记录

- Handoff：[TASK-040-977ef65.md](../handoffs/TASK-040-977ef65.md)（含探针来源/语义、**assembly.py 白名单偏差声明**、验证证据表）。
- Review：尚无（待 Codex 非作者 Review）。
- 实际执行/测试：见 `verification/TASK-040/`——基线全仓 **798 passed / 0 skipped** exit 0（= master `c5aa664`）；实现后定向 `tests/core+pipeline+providers` **261 passed / 0 skipped** exit 0；全仓 ×5 **每次 800 passed / 0 skipped** exit 0（798 基线 + 2 新增，passed 不减少）；修前判别力（src 回退 `c5aa664`）**2 failed / exit 1** 留证后恢复复跑 2 passed。全部同一口径：`powershell.exe`（继承 PATH 含 openssl）+ `TASK-012-py312` + `-p no:cacheprovider`。
- **最近状态（当前，唯一）**：2026-09-18 ZCode 实现交付 `977ef65`（文档 `2afabf2`），随后**尾部 merge master `84bdda7`（TASK-043 集成，与本切片零文件重叠；STATUS 冲突保留双方登记行）→ 分支 head `004f00e`**，merge 后复跑全仓 ×5 **每次 810 passed / 0 skipped** exit 0、定向 261 passed / 0 skipped exit 0（802+2 新例+6 条 network 在本 shell 口径转正，收集总数一致），`status=in_review`。**注意**：实现含一处**白名单偏差**——物理构造点 `src/infrastructure/pipeline/assembly.py` 不在任务书允许列表，本切片以"可选形参透传"3 行接入并已在 Handoff 声明理由（F-12 原文证据位置即含该文件），**交 Codex Review 裁决**。


## Review 与集成记录（2026-09-18）

- **Review**：[doc/reviews/TASK-040-977ef65.md](../reviews/TASK-040-977ef65.md)（Reviewer=Codex，**非作者**；commit `826bc90`；decision=**`approved`**；0 P0/P1）。
- **Reviewer 独立复跑（非复用作者证据）**：定向 `tests/core tests/pipeline tests/providers` **261 passed / 0 skipped**；全仓 **804 passed / 6 skipped**（6 条全为既有 `tests/network` `openssl unavailable`；作者同口径 `810/0` ⇒ **804+6 = 810，收集总数一致**）；**判别力独立复现** 新测试 + master `src` → **2 failed / 14 deselected**（接线断言 FAILED；生产对照 FAILED 于 `blocked:missing_clean_artifact != run:`）；`service.py` 经 diff 核对**仅 docstring**、`tests/core` **零断言/零测试删除**、`src`+`tests` 空白干净；`build_production_pipeline` 的另 2 个调用点不传新参数 ⇒ 修前装配行为不变。
- **白名单偏差（R-01，本 Review 明示授予）**：`src/infrastructure/pipeline/assembly.py` 不在原白名单，作者为其新增**可选形参** `clean_probe: Callable[[str], bool] | None = None` + 透传（默认 `None` ⇒ 既有调用方逐字节不变）。授予理由：`PipelineService` 的**物理构造点在 assembly.py**（`app.py` 只是调用方）；白名单内注入只剩"跨模块写 `pipeline._clean_probe` 私有属性"一途（更差）；该改动为**加法式、默认保持**、未动 seam 其他语义；**F-12 的证据位置本身含 `assembly.py`**；作者**主动声明偏差 + 给出回滚路径**（程序上正确）。
- **流程修正（Codex 自查）**：释放 TASK-040 时把"装配处"指认为 `src/bootstrap/app.py`，未沿到物理构造函数所在文件——这是**释放方的核对遗漏**。今后涉及"装配/接线"的切片，白名单须包含构造函数所在文件（或用 `rg "^def build_"` 先定位物理装配点）。
- **Findings 处置**：R-01 **granted**（见上）；R-02（白盒接线断言读 `_clean_probe`）**accepted**（本切片禁止改 `service.py` 逻辑 ⇒ 无法加公开访问器；仓库已有同风格先例；建议将来加只读访问器后改公开/行为式断言）；R-03（口径差）**accepted/记录**；R-04（探针每次判定一次只读 DB 查询）**accepted（观察项）**。
- **集成**：`integration_commit=e1be885`（merge，parents `826bc90` + `9b9c2da`；分支尾部含 `004f00e` = merge master `84bdda7`）。master 复验：定向 **261 passed / 0 skipped**、全仓 **804 passed / 6 skipped**。
- **关闭**：**F-12 关闭**；TASK-040 置 `done`。