# verification/TASK-062 — 证据索引

切片：**TASK-062 后置复审残留收口**（Q-006 诊断脱敏 + TASK-046 R-001 多过滤器补证 + R-009）。
Owner=`Codex`；Reviewer=`Qoder`（**非作者**）；base=`41d7aee`；branch `agent/codex/TASK-062-posthoc-residuals`。

环境口径（协议 §6 第 12 条）：PowerShell（pwsh 7.6.6）+ `TASK-012-py312`
（`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`，Python 3.12.3）、
`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、**不设 `QT_QPA_PLATFORM`**（E-1 口径）。
每份日志带 EXIT 码与 shell/venv 头。

## 1. 交付物清单

| 文件 | 内容 |
|---|---|
| `full-suite-run{1,2,3}.log` | 全仓套件 ×3（工作树状态，未提交，`@4c81dca`） |
| `full-suite-run4-post-commit.log` | 全仓套件（**delivery head 提交后**，见 Handoff 的 delivery head） |
| `diagnostics-suite.log` | `tests/diagnostics` 定向 |
| `reading-export-suite.log` | `tests/reading_export` 定向 |
| `webtoon-tiles-targeted.log` | 新用例定向（`-k qt_encoded`） |
| `qt-encoded-filter-probe.{py,txt}` | AC ④ 独立探针：Qt 编码页的行过滤器类型 + overlap 0/64 瓦片字节同一性 |
| `discriminating-prefix-tree.txt` | **AC ⑥ 判别力 artefact**：新用例跑在**修前树**（`git archive 41d7aee`）上的结果 |
| `r009-erratum.md` | R-009（TASK-060 复审 P3 记录勘误）的逐条勘误记录与可直接套用的更正文本 |

## 2. 结果汇总

### 2.1 全仓套件（AC ⑤）

| 运行 | collected | passed | skipped | EXIT |
|---|---|---|---|---|
| run1（`@4c81dca` 工作树） | 930 | **924** | 6 | **0** |
| run2（同上） | 930 | **924** | 6 | **0** |
| run3（同上） | 930 | **924** | 6 | **0** |
| run4（delivery head 提交后） | 930 | **924** | 6 | **0** |

- 基线（`41d7aee`，TASK-060 集成后）= **923 collected**（本机口径 917 passed / 6 skipped）。
  本切片 **+7 例**（`tests/diagnostics` +6、`tests/reading_export` +1）⇒ 930。**未跌破 923**。
- 6 条 skip 逐条原因（全部为**既有** `tests/network` 环境缺失，非本切片引入）：
  `tests/network/test_connection_tester.py:106`、`test_transport_tls.py:39,47,62,69,83` —— 均 `openssl unavailable`。
- 口径换算：6 条 skip 在 openssl 可用的机器上转为 pass ⇒ **openssl 可用口径 = 930 passed / 0 skipped**，总数一致。
- 无 `xfail`、无新增 skip、未放宽既有断言。

### 2.2 定向套件（AC ①②④）

| 套件 | 修前（`41d7aee`） | 本切片 | 变化 | EXIT |
|---|---|---|---|---|
| `tests/diagnostics` | 19 passed | **25 passed** | +6 | 0 |
| `tests/reading_export` | 112 passed | **113 passed** | +1 | 0 |
| 合计 | 131 passed | **138 passed** | +7 | 0 |

修前列由 `discriminating-prefix-tree.txt` 的同一棵 `git archive 41d7aee` 树实测（用 `git show` 取回**原版**测试文件后运行）。
两套件通过数**均未减少**（AC ⑤）。

### 2.3 AC ④ 探针（Qt/libpng 编码页）

`qt-encoded-filter-probe.txt`（EXIT=0）：

- Qt 编码页的行过滤器类型集合 = **[0, 1, 4]**（`all filter-0? False`）⇒ 新用例的夹具**不是**退化夹具。
  按 PNG 规范，1 = **Sub**、4 = **Paeth**（0 = None）。即本夹具覆盖到 `None`/`Sub`/`Paeth`；
  R-001 列举的 `Up`/`Average` 在本夹具中未被 libpng 选中——**如实标注**：这是"非退化自适应过滤器"
  这一性质上的补强，不等于对每种过滤器各出一条夹具。若要将缺口收得完全，需在后续小切片构造能稳定
  诱发 `Up`/`Average` 的图样（`Up` 需行间高相关、`Average` 需中等梯度）；本切片不改该测试选择器，
  以免把"性质被覆盖"退化为"绑定到某个 libpng 版本的启发式"。
- overlap `0` 与 `64` 的瓦片文件 **3/3 逐字节相同**（`ALL BYTE-IDENTICAL: True`）。
- 瓦片行拼接 **== 整页**（`union == whole page: True`，page_width 600）。

### 2.4 AC ⑥ 判别力（artefact，非散文）

`discriminating-prefix-tree.txt`：把**新测试文件**放进 `git archive 41d7aee` 的修前树运行。
`git diff --name-only 41d7aee -- src` 只列出一个文件（`src/application/maintenance/diagnostics.py`）⇒
webtoon 用例面对的是**与修前逐字节相同**的 `src`。

| 新用例组 | 修前树结果 | 判别力 |
|---|---|---|
| `tests/diagnostics/test_report.py::TestRedactionReachesEverySection` | **4 failed / 14 passed，EXIT=1** | **有**（4/6 例判别） |
| `test_overlap_choice_on_a_qt_encoded_page` | **1 passed，EXIT=0** | **无**（如实声明：钉的是原本未被覆盖的性质，`src` 未改动） |

判别失败的四例（修前树）：

1. `test_credentials_are_masked_in_the_application_and_database_sections`
2. `test_credentials_are_masked_in_recent_errors_values_and_keys`
3. `test_embedded_credential_shapes_are_caught_anywhere_in_a_value`
4. `test_the_documented_boundary_is_the_actual_boundary`

另两例（`test_benign_values_survive_every_section`、`test_ordinary_paths_versions_and_words_pass_through`）
在修前树**同样通过**——它们是防误伤（假阳性）方向的钉子，不是判别用例；此处一并如实标注。

## 3. 复现命令

```powershell
$py = "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
cd "G:\CODEX\New Manga.worktrees\TASK-062-codex"

& $py -m pytest tests/diagnostics -q -rs -p no:cacheprovider        # 25 passed / EXIT 0
& $py -m pytest tests/reading_export -q -rs -p no:cacheprovider     # 113 passed / EXIT 0
& $py -m pytest tests -q -rs -p no:cacheprovider                    # 924 passed / 6 skipped / EXIT 0（930 collected）
& $py verification/TASK-062/qt-encoded-filter-probe.py               # 见 qt-encoded-filter-probe.txt
```
