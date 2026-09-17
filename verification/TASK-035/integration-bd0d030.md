# TASK-035 集成验证：`bd0d030`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `2e1bf2d3d9610c1c53537f45abc12e82e8e5ee4f`（切片 diff base；分支起点 `e8e1750` = 释放纯文档提交） |
| reviewed head（delivery） | `6ddd955` |
| 元数据 / 分支 head | `092957e` |
| Review 报告 commit | `9d82f0b` → [`doc/reviews/TASK-035-6ddd955.md`](../../doc/reviews/TASK-035-6ddd955.md)（Reviewer=Codex，**非作者**；decision=`approved`） |
| implementation merge / integration commit | `bd0d030`（merge，parents `9d82f0b` + `092957e`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；未设 `QT_QPA_PLATFORM` |

## 复验结果（master `bd0d030`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/rendering tests/pipeline -q -p no:cacheprovider -rs` | 0 | **124** | **0** | `124 passed` | 无 |
| 2 | `…python.exe -m pytest tests/core tests/storage tests/providers -q -p no:cacheprovider -rs` | 0 | **159** | **0** | `159 passed` | 无 |
| 3 | `…python.exe -m pytest -q -p no:cacheprovider -rs`（全仓） | 0 | **679** | **6** | `679 passed, 6 skipped` | 6 项均为既有 `tests/network` 的 `openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`） |
| 4 | 新增用例点验 `-k "real_default or non_sfx_policy or defaults_agree"` | 0 | **7** | **0** | `7 passed, 58 deselected` | 无 |

## 缺陷面关闭核对（F-1 渲染面）

- **默认值实测（master 上直接探针）**：`RegionSnapshot('r','p').sfx_policy` → `skip`（修前为 `translate`）；`Region('r2','p').sfx_policy.value` → `skip`。实体 / Snapshot / SQLite Schema 三方默认一致（D03 §7）。
- **门控前置生效**：`src/application/rendering/service.py` 的两处判定（`rerender_region`、`_prepare_region`）均改走 `_sfx_gate_allows` → `application.translation.context.gate.decide_sfx_translation`；渲染层 `rg "SfxPolicy\."` 仅余 `:540` 的逃生口取值判断，**无第二份策略映射**。
- **用户可见症状消除**：普通 `speech` Region 在真实默认 `skip` 下，批量 `rerender_page` 记为 `rendered`（不再 `skip_policy`）、单 Region `rerender_region` 返回 `committed`（不再 `BLOCKED/SKIP_POLICY`）；`sfx` + `skip` 仍被拦截、`sfx` + `manual` 仅 `allow_manual_sfx=True` 放行——原意未放宽。
- **F-1 状态**：由「部分关闭（规划面 closed / 渲染面 open）」改为 **`closed`**（规划面由 TASK-032 关闭，渲染面由本 Task 关闭）。

## 验收结论

- [x] 非作者独立 Review 绑定固定 base/head，四轴（Standards / Spec / Architecture / Verification）均 `executed`，逐轴小结、未跨轴排名；**并行偏差已在报告显式声明**（未能取得两条独立 sub-agent 线程 → 按 §6 第 6 条兜底做两遍相互隔离检查）。
- [x] 集成后四条命令通过且 pass/skip 分列；6 项 skip 均为既有 `openssl unavailable`，本 Task 未新增 skip。
- [x] 判别力（Reviewer 独立复现）：修前 `src/`（`e8e1750` 导出树）+ 本次测试 → **5 failed / 119 passed**，与作者记录一致。
- [x] 白名单：`git diff --name-only e8e1750 092957e` = 18 个路径（非证据 6 + `verification/TASK-035/**` 12）全部在允许范围内，越界 **0**；未改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task；未 push。
- [x] **R-01 已更正**：`verification/TASK-035/changed-paths.txt` 记录的 `git diff --check 2e1bf2d..HEAD` 退出码 `0` 与实测不符。**实测口径**：代码交付范围 `git diff --check e8e1750..6ddd955` = **退出码 0**（干净）；含证据材料的集成范围 `git diff --check 2e1bf2d..bd0d030` = **退出码 2**，命中的 **14 处**尾随空白**全部**位于 `verification/TASK-035/discriminative-prefix.log`——即被原样捕获的 pytest `E `/续行输出（行尾填充空格）。作者原始日志**未被改动**，此处仅更正其可复现性声明口径：**代码/测试/文档本身无空白问题**。与 TASK-032 R-01 同类。
- [x] **R-02 转派**：`tests/providers/**` 裸 `from conftest import …` 与 `tests/editing/conftest.py` 的收集顺序冲突（`tests/providers tests/editing` → 4 collection errors；反向顺序 137 passed）为**既有**基础设施缺陷（两个目录均不在本切片 diff 内）→ 登记为 [TASK-034](../../doc/tasks/TASK-034.md) 范围（该 Task 仍 `proposed`、**未释放**）。
- [x] **R-03 保留 open（非阻塞）**：渲染层逃生口仍直接命名 `SfxPolicy.MANUAL`；语义正确，作为后续硬化候选记录。
- [x] **未把任何 `BLOCKED`/`NOT_RUN` 改记为通过**：真实端点/模型端到端图像质量仍为 `NOT_RUN`（环境无端点/权重/依赖），与本 Task 无关且不因集成而改变。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3 | `changed-paths.txt` 的 `git diff --check` 退出码声明不可复现 | **fixed（记录更正）**：见上；不改动作者的原始捕获日志 |
| R-02 | P3 | `tests/providers` 裸 `conftest` 导入与 `tests/editing/conftest.py` 冲突 | **deferred** → 转 [TASK-034](../../doc/tasks/TASK-034.md)（`proposed`，未释放） |
| R-03 | P3 | 渲染层逃生口自行命名策略取值 `SfxPolicy.MANUAL` | **open**（非阻塞）；后续硬化候选 |
| N-2（作者登记） | P3 | 非 SFX 的域外策略不再抛错 | **accepted**：AC ① + D06 §85 前置的必然结果；实体 setter 与 Schema 已限定取值域，实际不可达 |
| N-3（作者登记） | P3 | `rerender_region` 策略校验位于"缺 Clean / 无 final"之后 | **accepted（不变更）**：返回顺序与修前一致，无回归；若产品希望策略优先属用户裁决 |

## 记录勘误（透明化）

- **Review 文档**：`doc/reviews/TASK-035-6ddd955.md` 在**集成元数据提交**中做了两处**非结论性**更正——① R-01 的尾随空白计数由 `15` 更正为实测的 `14`；② R-01 处置列补记"已由集成记录更正"。Review 结论 `approved` 与固定对象（base `2e1bf2d`、reviewed_head `6ddd955`）**不变**；Review 报告 commit 仍为 `9d82f0b`，上述更正落在集成元数据提交。
- **作者证据未改动**：`verification/TASK-035/**` 的作者材料（含 `changed-paths.txt`、`discriminative-prefix.log`）**逐字保留**，未做任何编辑；R-01 的口径更正只存在于本文件。
