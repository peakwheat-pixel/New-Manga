# TASK-010 集成验证

日期：2026-09-15（Asia/Shanghai）  
固定被审范围：`2cceb1e..cd76d30`  
reviewed_head：`cd76d30fdc561eb8f22a849eeb5989473957dc5b`  
实现合并：`1ea9c80fe29d33da33d533e22278cd2f474cb31a`  
Review report：`008b1013a9863f4f506764d17d01245cb2403db1`（approved）  
integration_commit：`a225790d5eaf90227249039255bb554307f5b2cc9`

## 集成方式

在 `master` 上按协议 §6.6 依次保留两个 merge commit：先合并作者交付，再合并 approved Review 报告。未合并其他分支，未修改被审 `src/`/`tests/` 语义。

## 主线复验

解释器：`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`（Python 3.12.3）；`PYTHONPATH=src`；未设置 `QT_QPA_PLATFORM=offscreen`，使用默认 Windows Qt 平台。

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/knowledge -q` | **78 passed** |
| `python -m pytest tests/core/test_architecture.py -q` | **4 passed** |
| `python -m pytest tests -q -rs` | **322 passed, 6 skipped** |
| `git diff --check 2cceb1e..cd76d30 --` | 无输出 |

全量 6 个 skip 均为 `openssl unavailable`（TLS/连接测试环境缺少 OpenSSL），不计为 PASS；未执行或不适用项仍按原记录保持 `NOT_RUN`/`N/A`。

## 范围与 AC

- Review decision=`approved`，无 P0/P1。
- AC-1～AC-3 已实现并经 Review；AC-4 在本次集成后完成验证，四项均可勾选。
- F-01、F-02 已关闭；D03 §12.5/§14.4 已登记两个可调实现参数。
- `tests/rendering` 未修改。

## 后续移交项取证

ZCode 取证提交 `05effee` 已由 Codex 以 merge commit `014231f` 纳入主线。后续最小复现（无参数 pytest 形态）为 `2 failed, 1 passed`，失败为字体可用性与水平文本方向两例；带 `tests` 参数的全量仍为 `322 passed, 6 skipped`。根因已定位为 `experiments/TASK-004/test_smoke.py` 的 offscreen `QGuiApplication` 进程级单例污染；未修改测试套件，修复超出 TASK-010 范围。
