# verification/TASK-045/posthoc-zcode — ZCode 独立 post-hoc 复审证据

报告：[doc/reviews/TASK-045-posthoc-zcode.md](../../../doc/reviews/TASK-045-posthoc-zcode.md)（decision = `uphold_with_findings`）。
被审代码面 = `cb93d66`（评审中工作区 fast-forward 至 `16f7d75`，src/tests 无差异）。
口径：PowerShell + `TASK-012-py312`（`G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`），
`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`；`PYTHONPATH` 指向被审树的 `src\`。

## 探针（本 Reviewer 新造，可复跑）

| 文件 | 用途 |
|---|---|
| `f4_multifilter_probe.py` → `f4-multifilter-probe-current.log` | **靶点 1**：F-4 裁剪等价在多过滤器页上——A 段 Qt/libpng 真实页（filter 直方图 {None:308, Sub:215, Up:2067, Average:239, Paeth:1171}，五种全出现）逐行/文件高/拼接断言；B 段手工逐行 0..4 过滤器 × RGB/RGBA/Gray/Gray+Alpha；C 段越界行为记录。复跑：`$env:PYTHONPATH='<src>'; python f4_multifilter_probe.py --suite all` |
| 同上 → `f4-multifilter-probe-pre-f4-6ea3dd3.log` | **判别力**：同探针在 `6ea3dd3`（临时 detached worktree，已删）exit 1——tile 1 高 1564（=1500+64 overlap）、拼接 4128 行 ≠ 4000，正是 F-4 修前症状 |
| `qml_shadow_probe.py` → `qml-shadow-probe.log` | **靶点 5**：Repeater 遮蔽语义复现——legacy（TASK-020 拼写）0 delegate / partial（1171bc5）2 / fixed（a165aa3）2。`model.tiles` 为 undefined ⇒ delegate 从未创建的历史勘误成立 |

## 测试复跑

| 文件 | 内容 |
|---|---|
| `targeted-reading-export.log` | 定向 `test_streaming_png.py + test_webtoon_tiles.py + test_qml_contract.py`：**45 passed / 0 skipped**，exit 0（含 AC⑧ `test_corrupt_idat_payload_fails_typed`、AC⑨ `test_band_read_peak_composition[单块/分块]`、AC⑩ rewind 记账、F-4/F-14/R-001 全部锁定用例） |
| `full-suite-run{1,2,3}.log` | 全仓 ×3：**848 passed / 0 skipped**，exit 0 ×3。口径声明：交接包期望 842/6 的差 = 6 条 `tests/network` openssl 依赖用例在本 shell（powershell.exe 继承 Git Bash PATH，openssl 于 `C:\Program Files\Git\mingw64\bin`）转正；**总数自洽，非 skip 消除**（与既有 P-02/R-006 口径勘误同型） |
| `network-tests-in-this-shell.log` | `pytest tests/network` 直接运行 **97 passed / 0 skipped**——转正直接证据 |

## 边界证据

本目录仅含探针脚本与运行日志；`src/**`、`tests/**`、Schema、依赖、`AGENTS.md`、其他 Task 全程零改动
（探针的页面/瓦片工作产物已清理，重跑即再生；判别力用临时 detached worktree，跑后已 `git worktree remove`）。
