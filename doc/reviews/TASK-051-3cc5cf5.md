decision: approved_subagent

# Review — TASK-051 工作台三档视图解析 translated/compare

- Reviewer：独立子对话（非实现作者）
- 日期：2026-09-19
- 审查对象：`git diff a2306e3..9d22999`（实现提交 `3cc5cf5`，head `9d22999` 为 handoff 文档提交）
- worktree：`G:/CODEX/New Manga.worktrees/TASK-051-zcode`（HEAD `9d22999`，审查开始时工作区干净）
- 依据：Task `doc/tasks/TASK-051.md`、Handoff `doc/handoffs/TASK-051-3cc5cf5.md`、仓库代码与测试、`verification/TASK-051/**`；全部结论由本 Reviewer 独立复跑/亲读取证，未采信 Handoff 叙述。

## 1. 白名单核对 — 通过

`git diff --stat a2306e3..9d22999` 全部 17 个文件逐一核对，仅落在允许范围：

| 范围 | 文件 | 判定 |
|---|---|---|
| 允许 | `src/bootstrap/app.py`（+70/-16 区段） | OK |
| 允许 | `src/ui/viewmodels/workbench/viewmodel.py`（+15） | OK |
| 允许 | `tests/core/test_page_catalog_modes.py`（新增 151 行） | OK |
| 允许 | `doc/tasks/TASK-051.md`、`doc/handoffs/TASK-051-3cc5cf5.md` | OK |
| 允许 | `verification/TASK-051/**`（11 个证据文件 + probe 脚本） | OK |

禁止范围实测零改动（diff 行数为 0）：`src/ui/qml/**`、`src/ports/**`、`src/infrastructure/providers/step_writes.py`（pipeline seam）、`requirements.txt`、`pyproject.toml`。tests/ 仅新增 1 文件，无既有测试文件改动（无断言放宽）；全 diff grep `skip|xfail` 无匹配（无新增 skip/xfail）。Task 文件改动仅为 AC 勾选、测试要求表回填与状态更新，内容与实现一致。注：`doc/STATUS.md` 台账行未在本切片内（属 AC⑥ 集成步骤，与本 Review 并行，不算违规）。

## 2. 代码审读 — 通过（3 条 P3 观察见 §7）

### 2.1 compare 语义依据（Task 风险项）— 成立，非自创

亲读证据链，四点全部核实：

1. `src/ui/qml/workbench/ViewerPanel.qml:88`：注释 `// Compare pane (D05 §20.1 左右双图).`；右 pane `viewerComparePane` 的 `Image.source: viewer.translatedUrl`，带"译图"角标，`visible: viewer.translatedUrl === ""` 时文案"译图尚未产出"；
2. 左 pane `viewerImagePane` `source: viewer.imageUrl`，compare 模式下带"原图"角标；
3. `src/ui/qml/workbench/WorkbenchView.qml:30`：`wViewerTranslated: vm.viewerImageUrlFor("translated")`，:110 传入 `translatedUrl`；
4. `src/ui/viewmodels/workbench/viewmodel.py:421` `viewerImageUrlFor` docstring："Compare pane needs the translated variant, D05 §20.1"（既有代码，非本切片新增）。

且 `doc/05_UI_MAPPING.md` §20.1（:761 起）确实写明 Compare 可支持"左右双图"。⇒ compare = 左右双图（左=原图 Managed Copy，右=当前 TRANSLATED revision）从 D 文档 + 既有 QML 绑定推出，符合 Task"不得自创"约束，无需产品裁决、不 BLOCKED。实现中 `image_url(page_id, "compare")` 返回 original URI 正是左 pane 所需。

### 2.2 根内校验等价性 — 通过

`git show a2306e3:src/bootstrap/app.py` 亲读修前 `image_url`：修前内联逻辑（`storage.root.resolve()` → `absolute_path(ref).resolve()` → `relative_to(root)` 捕 ValueError 返回 `""` → `as_uri() if is_file()`）与修后 `_uri_within`（`src/bootstrap/app.py:170-177`）逐行等价，仅方法提取，`path.relative_to(root)` 未绕过。`image_state`（:162-168）同样走 `relative_to`。行为差异仅一处无害：修前 unknown mode 在 `get_page` 之前短路返回 `""`，修后在之后返回，返回值相同。

### 2.3 translated 与 reader 同源 — 通过

装配点 `src/bootstrap/app.py:732-737`：`page_catalog` 与 `reader_catalog` 均以 `SqlitePageArtifactLocator(conn)` 注入，`conn` 同源于 `app.py:527` `open_database(...)`（`repository` 亦用此 conn）。两者解析 translated 均调用 `locate_current(page_id, ArtifactType.TRANSLATED)`（catalog :131，reader catalog :313-315），locator 实现亲读确认取 `media_artifacts.current_revision_id` → `artifact_revisions.managed_path`。AC② 用例断言 `_uri_path(viewerImageUrlFor("translated")) == str(reader_page.translated_path)`，路径相等即同一 managed_path（同一 current revision）。

### 2.4 image_state 四分支判定 — 正确

`src/bootstrap/app.py:142-168`：页缺失 → `missing`（:151-152）；translated 无产物（locate_current None）→ `missing`（:155-156）；ref 为空 → `missing`（:160-161）；逃出 managed 根 → `invalid`（:164-167）；文件消失 → `invalid`（:168）。测试覆盖了 ok→invalid（删文件）与 missing（无产物页）两态，且断言 invalid 时 URL 仍 `""`、original 不受影响——"无数据"与"路径非法"可区分成立。

### 2.5 VM Slot 与既有行为 — 无回归

`viewmodel.py:427-440` 新增 `viewerImageStateFor` 为**纯新增** Slot；既有 `viewerImageUrlFor`/`_image_url` 未改。getattr 退化（catalog 无 `image_state` → `"missing"`）与既有 `_image_url` 的 `getattr(self._page_catalog, "image_url", None)` 风格一致。既有断言 `tests/workbench/test_workbench_viewmodel.py:468`（无 artifact 场景 `viewerImageUrlFor("translated") == ""`）修后语义不变且复跑通过。

## 3. 测试复跑 — 与声明一致

环境：指定 venv `G:\CODEX\New Manga.task-envs\TASK-012-py312`，PowerShell，未设 `QT_QPA_PLATFORM`，以目录形式运行。

| 套件 | 实测 | 退出码 | 证据 |
|---|---|---|---|
| 定向 `pytest tests/core tests/workbench -q -rs -p no:cacheprovider` | **87 passed**, 0 skipped, 12.87s | **0** | `verification/TASK-051/review-rerun-targeted.log` |
| 全仓 `pytest -q -rs -p no:cacheprovider` | **895 passed**, 1 warning, 0 skipped, 43.20s | **0** | `verification/TASK-051/review-rerun-full.log` |

与 Task 测试要求表（87 / 895×5）及 Handoff AC⑤ 声明一致；本次复跑为 ×1（声明侧已有 ×5 日志 `full-suite-post-fix-run{1..5}.log`，抽读 run1 亦为 895 passed）。warning 为既有 `imghdr` 弃用告警，非本切片引入。

## 4. 探针复跑 — 通过

`python verification/TASK-051/viewer_modes_probe.py` 复跑 1 次，exit 0：

```
MODE original: resolved state=ok
MODE translated: resolved state=ok
MODE compare: resolved state=ok
```

留证 `verification/TASK-051/review-probe-rerun.txt`。probe 脚本亲读确认：与 AC② 用例同构（import → publish TRANSLATED revision via `ArtifactStepWriter.prepare_revision + adopt_current` → VM 断言），`state=unavailable` 为 probe 对修前树 AttributeError 的显式 fallback（脚本 :64-66 注释写明），诚实无伪装。

## 5. 判别力复核 — 声明成立

1. `discriminating-new-tests-vs-prefix.log`（修前树 `a2306e3`）：`2 failed, 1 passed, 30 deselected`——失败的正是 `test_translated_and_compare_resolve_like_the_reader` 与 `test_invalid_paths_stay_diagnosable_not_silent`。2 failed ⇒ pytest 退出码必为 1（Handoff 的 "exit 1" 是必然推论；log 本身未记录退出码，见 P3-3）。
2. 第 3 条用例 `test_page_catalog_degrades_without_a_locator` 亲读：仅断言 original → `file:` URI 与 unknown mode → `""`，两者均为修前已有行为（修前代码亲读核对）；其以 `__new__` 构造并手动设属性，修前代码不读 `_locator`，故在修前树 pass（log 中 1 passed）。"仅钉既有行为、不计判别"声明**成立**。
3. 双树探针：`probe-pre-fix-run{1,2}.txt` = original resolved / translated、compare EMPTY / state=unavailable；`probe-post-fix-run{1,2}.txt` = 三 mode resolved / state=ok。P-6 缺陷签名（workbench translated/compare 恒空）在修前树复现、修后消除。

## 6. Handoff vs 事实 — 逐条属实

| Handoff 声明 | 核验结果 |
|---|---|
| 白名单零改动（QML/Schema/requirements/pipeline seam、既有测试零改动） | 属实（§1 实测） |
| compare 语义四点证据链 | 属实（§2.1，注意注释实际在 ViewerPanel.qml:88 而非 85） |
| AC① locate_current 复用 + 根内校验不绕过 | 属实（§2.2/§2.3） |
| AC② 同 revision 路径断言 | 属实（§2.3；reader 断言在修后树成立） |
| AC③ typed 空态可区分 | 属实（§2.4；invalid/missing 断言 + URL 恒 `""` 的双通道设计合理） |
| AC④ QML 零改动 | 属实（diff 实测 0 行） |
| AC⑤ 判别力（2 failed）+ 87/895 不回归 | 属实（§3/§5 复跑复现） |
| 设计取舍 1-5（同 conn 注入 / URL 面不扩协议 / compare 复用 original / unknown mode `""` / getattr 退化） | 与代码逐条相符 |
| "P-6 复核签名……在修前列复现" | 半句成立：修前 probe 仅复现"workbench 恒空"，未含"reader 非空"断言（probe 无 reader 侧输出）；reader 侧非空由 AC② 用例在修后树断言。见 P3-3 |

## 7. 问题清单

无 P0 / P1 / P2。

- **P3-1 测试命名与覆盖错位**：`tests/core/test_page_catalog_modes.py:129` `test_page_catalog_degrades_without_a_locator` 名为"无 locator 退化"，实际手动注入了 locator，测的是 legacy 构造下 original/unknown-mode 行为；真正"无 `image_state` 能力退化"的路径（`viewmodel.py:439` getattr → `"missing"`）无测试覆盖。不影响正确性，建议后续改名或补一条 VM 退化用例。
- **P3-2 `image_state` 对 unknown mode 的语义未定义**：`app.py:158-159` else 分支对任意非 translated mode（含 `"nonsense"`）按 original ref 判定，可能返回 `"ok"` 而同 mode 的 `image_url` 为 `""`（ok/空 URL 组合）。当前无 QML 消费者（TASK-047 gated）且 `set_viewer_mode` 白名单挡住未知 mode 进入 viewer 状态，无实际影响；建议 TASK-047 切片消费前补齐 unknown-mode 语义。
- **P3-3 证据形式小瑕疵**：(a) `discriminating-new-tests-vs-prefix.log` 未记录 pytest 退出码（"exit 1"由 2 failed 必然推得）；(b) Handoff 引 `ViewerPanel.qml:85` 实际为 :88；(c) Handoff 称修前 probe 复现 P-6 签名含"reader 非空"，probe 实测仅覆盖 workbench 侧。三者均不动摇结论。

## 8. 结论

AC①②③④⑤ 在代码与复跑证据层面全部成立；白名单与禁止范围零违规；判别力声明经修前树日志与双树探针核实；Handoff 与事实一致（3 条 P3 为措辞/命名级瑕疵，不阻塞）。**decision: approved_subagent**。AC⑥ 剩余步骤（集成验证、STATUS 台账行、post-hoc Review）按协作协议由 Codex 后续执行。

本 Review 新增留证（未提交）：`verification/TASK-051/review-rerun-targeted.log`、`verification/TASK-051/review-rerun-full.log`、`verification/TASK-051/review-probe-rerun.txt`。
