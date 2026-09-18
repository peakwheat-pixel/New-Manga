# TASK-043 集成验证：`b29427a`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `1c171dcdeafc1cbffe6111d503dd0cd598e22dea`（Task 固定 base；开工 fast-forward 至 master `c5aa664`，无冲突） |
| reviewed head（delivery） | `d8e9406`（22 文件：实现+测试+证据） |
| 元数据 / 分支 head | `d765f22`（+Handoff / Task 记录 / 证据索引） |
| Review 报告 commit | `4d11b81` → [`doc/reviews/TASK-043-d8e9406.md`](../../doc/reviews/TASK-043-d8e9406.md)（Reviewer=Codex，**非作者**；decision=`approved`） |
| integration commit | `b29427a648d2079a533750307e64f4588fee8c15`（merge，parents `4d11b81` + `d765f22`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；`-p no:cacheprovider` |

## 复验结果（master `b29427a`，Reviewer 独立重跑）

| # | 命令 / 方法 | 退出码 | 结果 |
|---:|---|---:|---|
| 1 | `pytest tests/import_formats tests/library tests/providers -q -rs` | 0 | **225 passed / 0 skipped** |
| 2 | `pytest -q -rs`（全仓） | 0 | **802 passed / 6 skipped**；6 条全为既有 `tests/network` 的 `openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`） |
| 3 | **F-1 两棵树像素探针**（自建 `c5aa664` 导出树以隔离 PYTHONPATH） | 0 | 基线：红→`(0,0,255,255)`、蓝→`(255,0,0,255)`（**SWAPPED**）、绿不变（R↔B 下恒等 ✓ 印证作者说明）；交付树：三色均 OK；两次 `using tree` **确为不同路径** |
| 4 | **判别力**：新测试文件放入 `c5aa664` 导出树运行 | 1 | **8 failed / 8 passed**（red/blue + 4 条 pending 记账 + 2 条 F-9）；并验证加载树为该导出树 |
| 5 | **BGRA 分支字节序**（独立探针） | 0 | BGRA 字节 `(00,00,FF,FF)` 经 `Format_ARGB32` → `pixel == 0xffff0000`（纯红）⇒ 与 `0xAARRGGBB` little-endian 布局一致 |
| 6 | `tests/` diff 删除面 | — | **零断言/零测试删除**（`-.*assert` / `-def test_` 均 0 命中） |
| 7 | 消费者面 | — | `src/ui/**` 无 `cancelled`/`pending_after_cancel` 消费者；图片导入 use case（`tests/library/test_import_images.py`）不受影响；共享 dataclass 位于 `application/importing/images/ports.py:91-99` |
| 8 | 空白/EOF | — | 集成前 `git diff --check 1c171dc d765f22` = exit 2（2 处 EOF 空行 + 捕获日志尾随空格）；**`src/`+`tests/` 范围 0 命中**；两处 EOF **已在集成提交修掉** |

## 结论来源标注（用户要求）

- **独立复跑**：第 1/2/3/4/5/6/7/8 项——即**关键路径全部由 Reviewer 自己跑出**（含 F-1 两树对照、判别力 8F/8P、BGRA 字节序、回归数字）。
- **复用作者证据（已在 Review 中声明）**：作者 5 次逐次全仓日志（`full-suite-runs.log`）、`bgra-basis*.txt`、`pdf-builder-identity.txt`（helper 搬迁的字节恒等——我只做**间接核对**＝tests 侧无断言删除）。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3 | `git diff --check` exit 2：`TASK-043.md:81`、`TASK-044.md:99` EOF 空行 + `verification/TASK-043/pre-fix-*.txt` 捕获日志尾随空格 | **fixed**：两处 EOF 空行已在本集成提交修掉；日志类**不改作者材料**，口径在此更正（同 TASK-032/035 R-01 一类） |
| R-02 | P3 | `pending_after_cancel`（共享端口 `application/importing/images/ports.py:98`）名称与新语义（"失败后未开始的页"）偏差 | **deferred**：登记跨层中性改名切片（该文件不在本切片白名单，且被图片导入共用） |
| R-03 | P3 | `except (ImportError, OSError)` 宽度可能把无关 `OSError` 归为 `MISSING_DEPENDENCY` | **accepted**（原始信息保留在 `detail`、消息区分"未安装/原生库无法加载"⇒ 可诊断、不静默）+ 建议将来收窄为 `ImportError` |
| R-04 | P3 | 修复前已导入页保留互换像素且 `source_hash` 为错误字节 ⇒ 重导不去重、产生重复页 | **deferred**：登记为待决，绑定"文档导入入口接线/发布"前裁决（当前**无用户可触发路径**，故本 Task 不做迁移合理） |

## Handoff「待 Reviewer 裁定」四项结论

1. **`cancelled` 语义收紧**（`bool(pending)` → `was_cancelled`）：**接受**（校正性；`src/ui/**` 无消费者；图片导入路径与本切片的取消用例均不受影响）。
2. **`pending_after_cancel` 名不改**：**接受**（→ R-02 登记）。
3. **`MISSING_DEPENDENCY` 新码 + `except` 宽度**：**接受**（→ R-03 附建议）。
4. **修复前已导入页不迁移**：**接受**（→ R-04 登记）。

## 集成结论

- [x] 非作者 Review 绑定固定 base/head；**Architecture 与 Verification 两面均覆盖**（口径按 2026-09-18 更新后的 §6：Standards/Spec 为可选视角，本报告一并给出，**不再需要并行子代理/隔离/偏差声明**）。
- [x] **F-1（P1）/ F-3（P2）/ F-9（P3）关闭**；TASK-043 置 `done`。
- [x] 边界：作者改动恰为 3 个 `src/` 白名单文件 + 1 个 `tests/` 文件 + `verification/TASK-043/**`；越界 **0**；未改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task；未 push。
- [x] 6 条 skip 全为既有 `openssl unavailable`；**未新增 skip、未放宽/删除任何断言**；独立基线 `792/6` ⇒ +10 恰为新增 10 例。
- [x] 未把任何 `BLOCKED`/`NOT_RUN` 记为通过。
- [x] **对下游的直接影响（重要）**：`importing.py` 的缓冲→`QImage` 映射已修正 ⇒ [TASK-041](../../doc/tasks/TASK-041.md)（MOBI）**可以从正确的像素路径往上扩展**（这也是我在排序裁定里要求"043 先于 041"的原因）。
