---
task_id: TASK-056
author: ZCode
recipient: Codex
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
delivery_head: cae3dd3
status: delivered
---

# Handoff：TASK-056 缓存·版本·模型清理（TASK-021 冻结子集②）

## 交付结果

- **受控清理框架**（`src/application/maintenance/cleanup.py`，新增）：
  - **AC ① 安全边界（两个清单）**——可清理＝相对路径命中 `CACHE_SAFE_PREFIXES = ("cache/",)` 的受控副本（生产：`cache/webtoon-tiles/` 瓦片各代）；**永不清理**＝用户源文件（managed root 外，注入 remover 结构性拒绝）、current/pinned revision 与一切业务行（清理不开数据库；revisions 不在 `cache/` 前缀下）、Lock 保护对象与任务恢复数据；前缀外条目一律 `skipped`（带原因）且**从不**递交 remover。模型/权重目录可后续注册；本切片不注册真实模型路径（真实 provider/端点属窗口排除项）→ 声明 NOT_RUN。
  - **AC ② 预览与结果**——`preview()` 返回 `CleanupPreview(targets, total_bytes)`；`run()`/`retry_pending_cleanups()` 返回结构化 `CleanupOutcome`（per-target ok/failed/skipped + reason，`to_dict()`）。
  - **AC ④ 幂等与失败**——`remove_managed` 对已消失文件静默跳过 ⇒ 重复 run 幂等；删除失败**不静默**：失败清单持久化进 manifest `pending_cleanups` 段（**复用 TASK-053 清单化模式**：原子写、`_record_pending` 全清则摘除段），`retry_pending_cleanups()` 重试。
- **瓦片缓存跨代回收**（AC ③）：`src/infrastructure/imaging/tile_cache_sweep.py` 的 `WebtoonTileCacheSweeper(cache_root, managed_root)` 枚举 `tile-*.png` 全部代（`_TILE_CACHE_FORMAT` v1 遗留/TASK-045 R-005 的升版孤儿即被覆盖）；只列举不删除，删除统一走注入 remover（managed-root 边界单点强制）；相对路径以 managed root 推导，防错。
- **白名单核对**：改动仅 `src/application/maintenance/{ports?×无,cleanup}.py`、`src/infrastructure/imaging/tile_cache_sweep.py`、`tests/maintenance/{conftest?,test_cleanup}.py`——纯新增两文件 + 一个测试目录，**未触碰** TASK-045/046 已审文件（`webtoon_tiles.py` 零改动）、零 Schema/依赖/QML/AGENTS/其他 Task；无放宽断言、无新增 skip。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC ③ 跨代枚举 | `pytest tests/maintenance`（`TestSweeperInventory`） | 本分支，Git-Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设 | **PASS**：两代 tile 文件均被列举（相对 managed root）；缺失目录=空 | `tests/maintenance/test_cleanup.py` |
| AC ② 预览与结果 | `TestPreviewAndRun` | 同上 | **PASS**：preview 字节合计正确；run 结构化结果（removed=2）；重复 run 幂等（第二次 removed=0） | 同上 |
| AC ① 边界 | `TestSafetyBoundary` | 同上 | **PASS**：前缀外（managed original 形态路径）被 skipped 且文件幸存；managed root 外路径被 remover 拒绝、user source 逐字节幸存 | 同上 |
| AC ④ 失败可重试 | `TestRetryableFailures`（FlakyRemover 首删失败 → pending_cleanups=1 → retry 清除） | 同上 | **PASS**：8 例全过 | 同上 |
| AC ⑤ 判别力 | 新能力切片：**声明不适用**（无修前行为；`CleanupService`/`pending_cleanups` 修前不存在——与 TASK-055/053 新能力同口径）；全部用例为防回归钉住（前缀白名单、幂等、pending 重试） | 同上 | 声明已记录 | 本表 |
| AC ⑤ 全仓 ≥5 次 | `pytest -q -rs -p no:cacheprovider` ×5 | 本分支（= master `c083f60` + 本切片） | **PASS ×5：900 passed / 0 skipped，EXIT=0**（41.77–44.34s；=892 基线 + 8 新用例；无新增 skip/xfail） | `verification/TASK-056/full-suite-run{1..5}.log` |
| 真实模型/权重目录清理 | 未注册、未执行 | — | **NOT_RUN**：真实 provider/模型路径配置属窗口排除项；框架就绪，注册即用 | — |

口径：同一 shell（Git Bash）+ 同一 venv（`TASK-012-py312`）+ `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`，`QT_QPA_PLATFORM` 未设；退出码 + passed/skipped 逐次分列。

## 接收方式

- 分支 `agent/zcode/TASK-056-cache-version-cleanup`，worktree `G:/CODEX/New Manga.worktrees/TASK-056-zcode`。
- 复现：`pytest tests/maintenance -q -p no:cacheprovider`；全仓 `pytest -q -rs -p no:cacheprovider`。
- 前置：master 已含 TASK-053（pending 清单模式同源）与 W0–W3/W6–W8（开工 merge master `c083f60`）。

## 风险与遗留

- **生产接线 NOT_RUN**：清理服务未注入 bootstrap（与 TASK-055 同口径——装配切片统一接线；QML 入口受 TASK-047 设计门）。
- **模型目录未注册**：`CACHE_SAFE_PREFIXES` 仅含 `cache/`；模型/权重清理等注册真实路径后再启用（窗口排除项）。
- **`pending_cleanups` 与 F-7**：manifest 损坏退化同 TASK-053 的既有面（pending 段与 batches 段同文件同损）；清理对象是可再生缓存，损失=多扫一轮，无业务风险。
- **回退**：`git revert <实现提交>`（纯新增文件）。

## 追加登记（作者修订，首轮 Review approved_subagent 后的 R-001 守卫）

首轮独立子对话 Review（03:15–03:44，decision=`approved_subagent`，报告见 [TASK-056-4c8b8a7.md](../reviews/TASK-056-4c8b8a7.md)）0 项 P0/P1，R-001（P2）防御纵深：`_is_safe` 纯字符串前缀匹配可被 `..` 组件绕过（`cache/webtoon-tiles/../../books/...` 会放行并删除 root 内业务文件；生产唯一 inventory 输出受控不可达，root 外逃逸仍被 remover 硬拒绝）。守卫已随修订落地：

- `_is_safe` 改为 `PurePosixPath` 组件检查（含 `..`/`.` 的路径一律 False）后再判前缀；docstring 记录理由。
- 新回归用例 `test_dotdot_components_are_rejected_even_under_safe_prefix`（sneaky 路径 skipped、业务文件幸存）；判别力=守卫移除必失败。
- R-002/R-003/R-004（P3：run 的 ImmutablePathViolation 中止边界、Protocol 归位、测试私有成员访问）维持 open，不阻塞。
- 修订后取证：新套件 9/0；全仓 ×5（901/0 预期口径）→ 实测 4×901/0 + run2 1 failed（`test_worker_run_and_main_thread_access_coexist`，TASK-048 的并发用例在全仓负载下的时序 flaky——单跑 ×6 全过、复跑全仓 901/0；诊断入 `flaky-diagnostic.log`；**与本切片变更面无关**，归 TASK-048 R-2 已注记的强度事项，登记 STATUS flaky 跟踪）→ `verification/TASK-056/revision-full-suite-run{1..5}.log`。
