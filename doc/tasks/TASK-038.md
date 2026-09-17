---
id: TASK-038
title: 生产装配收口：reader/export ViewModel 注册 + tile_factory 注入 + 文档导入接线
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode（窗口内子 agent，结论仅 approved_subagent）
depends_on: [TASK-015, TASK-019, TASK-020, TASK-023, TASK-033]
base_commit: 047164ea080651741b38b20a36470115d4830a0d
branch: agent/zcode/TASK-038-production-assembly
worktree: G:/CODEX/New Manga.worktrees/TASK-038-zcode
integration_commit: f835ac9bc2355ee2af6f018991d035da94626950
---

# TASK-038：生产装配收口（reader / export / 文档导入）

**READY（2026-09-18 ZCode 全权窗口 W5，用户指示"再布置任务"）**：Owner=`ZCode`、Reviewer=窗口内子 agent（结论**只能** `approved_subagent`/`changes_requested`）、base=`047164e`、branch/worktree 见顶部元数据。开工前把 `status` 改为 `in_progress`，并 `git merge master`。

## 为什么这是当前最高价值的切片

窗口内 W3（TASK-020）与插队项（TASK-023）各自把能力做出来了，却都因白名单不含装配点而**移交**；更根本的是：**生产装配从未把阅读器/导出接入 QML**。Codex 实测（master `047164e`）：

- `src/bootstrap/app.py::assemble_engine` 只注册 **3** 个 context property——`navigationViewModel`、`bookshelfViewModel`、`workbenchViewModel`（`:461-464`）；**`readerViewModel`、`exportViewModel` 从未注册**。
- `AppServices`（`:312-323`）也没有 reader/export 字段。
- 仓库自己记录了这一点：`tests/reading_export/test_qml_contract.py:224` 的 docstring 写着「**生产装配尚未注入 readerViewModel**：页面必须可加载且显示空状态」——即生产阅读器是**惰性页面**，只有测试手工注入 VM 才真正可用。
- 因此 TASK-020 的 `tile_factory`（`src/ui/viewmodels/reader/viewmodel.py:56`）与 TASK-023 的 `ImportDocumentsUseCase`（`src/application/importing/documents/service.py:64`）在生产路径上都**不可达**。

**目标**：把这三条断链接上，使窗口内做的能力在产品里真正可用。

## Acceptance Criteria

- [ ] **AC ①（reader 接入）**：生产装配构造并接入 reader 的 ViewModel，使 `ReaderView.qml` 在生产 engine 中拿到真实 VM（不再依赖"未注入 → 空态"）。**必须同步更新** `tests/reading_export/test_qml_contract.py:224` 那条以"尚未注入"为前提的用例（**改为断言已注入后的行为，不得删除**），并说明前提变化。
- [ ] **AC ②（export 接入）**：export 的 ViewModel 按既有契约接入生产（注意 `export/viewmodel.py` 的 docstring：reader 发起时以 `readerViewModel.exportController` 交接；独立导出窗口另有注入）。**在 Handoff 列明实际注册名与两条路径的对应关系**，并以测试锁定。
- [ ] **AC ③（tile_factory 注入）**：生产装配把 tile 工厂注入 reader VM（实现复用 `src/infrastructure/imaging/webtoon_tiles.py` + managed storage），使 TASK-020 的分块阅读在生产路径可达；**QML 不得直接访问文件/模型**（工厂只能从 Python 侧注入）；源文件超出可解码范围时仍 fail-closed。
- [ ] **AC ④（文档导入接线）**：`ImportDocumentsUseCase` 在装配处构造并接到导入入口（与既有 `ImportImagesUseCase` 同构；`src/bootstrap/app.py:364/312` 是范式）；PDF 导入在生产可达。**MOBI 仍 `BLOCKED`**（无批准解析依赖），不得伪造。
- [ ] **AC ⑤（装配契约测试）**：新增/扩展"生产 engine 注册了全部所需 context property"的契约测试（现有 `tests/core/test_bootstrap.py:299` 只断言了 `workbenchViewModel`）；断言集合须与 AC ①②③④ 的实际接线一致。
- [ ] **AC ⑥（TASK-020 遗留收口）**：TASK-020 Handoff 的 disposition 表中标注"随生产装配切片收口"的 R-002/003/005/006 在本 Task 内逐条处置（fixed/deferred 均须写明理由）。
- [ ] **AC ⑦（回归与分列）**：`tests/core`、`tests/providers`、`tests/pipeline`、`tests/reading_export`、`tests/import_formats`、`tests/library` 与全仓 **passed 不减少**；全仓串跑**≥5 次**逐次记录（**统一用同一种 shell 与同一 venv**，见下方证据纪律）。
- [x] **AC ⑧** Handoff=[doc/handoffs/TASK-038-317f33e.md](../handoffs/TASK-038-317f33e.md)；Review=[doc/reviews/TASK-038-317f33e.md](../reviews/TASK-038-317f33e.md)（**approved_subagent**，报告 commit `fcf791f`，四轴 executed；R-001～R-003 全 P3 不阻断）；集成=`f835ac9`（merge，parents `047164e`+`fcf791f`），集成后复验全仓 **772 passed / 0 skipped**、exit 0（PowerShell 继承 PATH 口径，与全切片一致）。

## 允许修改范围

- `src/bootstrap/app.py`（装配与 context property 注册——本 Task 的核心）
- `src/ui/viewmodels/reader/**`、`src/ui/viewmodels/export/**`、`src/ui/viewmodels/bookshelf/**`
- `src/infrastructure/imaging/**`
- `src/application/importing/**`
- `tests/**`
- `doc/tasks/TASK-038.md`、`doc/handoffs/TASK-038-*.md`、`verification/TASK-038/**`
- **需先申请**：`src/ui/qml/**`（若确需 QML 侧小改以匹配注入名，须先说明具体文件与理由）

## 禁止范围

- 不得让 QML 直接访问数据库/文件/模型（产品边界，见 `AGENTS.md`「产品边界」）。
- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、路由判定算法、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言（**AC ① 的用例更新是"前提变化后的等价更新"，不是放宽**），不得新增 `skip`/`xfail`；不得把 `BLOCKED`/`NOT_RUN` 记为通过。
- 不处理 R-06（webtoon flaky 的历史登记）、MOBI（待用户批准依赖）、超大 webtoon 像素解码（BLOCKED）。

## 证据纪律（本窗口新增要求）

- **统一证据口径**：所有基线/回归数字必须**同一 shell、同一 venv**（建议 Windows PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`），并在证据里写明所用 shell。窗口报告 v1/v2 曾把 PowerShell 的 `737/6` 与另一 shell 的 `764/0`（openssl 可用，故 6 条 network skip 变为通过）并排呈现，容易被误读为"skip 被消除"——**不要重复该口径混用**。
- 每条命令记退出码 + passed/skipped 分列；失败用 `-rf` 记用例名。

## 测试要求

- 主命令：`python -m pytest tests/core tests/providers tests/pipeline tests/reading_export tests/import_formats tests/library -q -p no:cacheprovider -rs`
- 全仓：`python -m pytest -q -p no:cacheprovider -rs -rf`（≥5 次逐次记录）
- AC ③ 须给出"注入 tile_factory 前/后"的生产路径差异证据；AC ①② 须给出 engine 级契约证据。

## 依赖、风险与阻塞

硬依赖：TASK-015（reader/export 交付）、TASK-019（provider 层）、TASK-020（tile 实现）、TASK-023（文档导入用例）、TASK-033（渲染装配先例）——均 `done`。

风险：
- **这是一个"接线"切片，风险在于隐藏的产品缺陷被暴露**：接上 reader 后，此前从未在生产路径跑过的 reader 代码可能暴露问题。若发现缺陷：
  - 属本 Task 白名单内的 → 就地修并加回归；
  - 属白名单外（如 `src/application/reading/**`）→ **先留证并回抛 Codex 裁决**，不得自行扩范围。
- export 的两条交付路径（reader 发起 vs 独立窗口）语义易混，须在 Handoff 写清，避免"注册了但用不到"。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **历史状态**：2026-09-18 由 Codex 在 ZCode 全权窗口第二轮创建为 `ready`（用户指示"再布置任务"）；`base=047164e`。
- **最近状态（当前，唯一）**：2026-09-18 08:5x 由 ZCode 在窗口第二轮开工（W5，status→`in_progress`）；分支 `git merge master` 快进至第二轮基线（W1-W3/插队全部集成的 HEAD）；实现 head=`317f33e`（reader/export/documents 装配 + tile_factory + 契约测试 ×2 + :224 等价更新 + AC⑥ R-003/R-006 fixed）；Review `fcf791c`=**approved_subagent**（3×P3）；集成 `f835ac9`，复验 772 passed/0 skipped exit 0。**TASK-038 已收口 `done`；期满后须 Codex + DSH 外部 post-hoc 复审（可推翻）。**遗留：R-001（R-002 disposition 口径改 accepted）、translated 文本导出接线、R-005 QML 清理。

