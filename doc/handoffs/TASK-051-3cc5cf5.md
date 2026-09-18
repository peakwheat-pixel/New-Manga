# Handoff — TASK-051 工作台三档视图解析 translated/compare（§11 P-6）

- 分支 head：见 Task 元数据（实现提交 `3cc5cf5`；base 侧 `a2306e3` = in_progress + master c083f60）
- worktree：`G:/CODEX/New Manga.worktrees/TASK-051-zcode`
- Review 材料：`git diff a2306e3..3cc5cf5` + 本文件 + `verification/TASK-051/**`

## 实施范围（对 Task 白名单）

| 文件 | 变更 |
|---|---|
| `src/bootstrap/app.py` | `_ManagedPageCatalog`：构造注入 `SqlitePageArtifactLocator`（与 reader_catalog 同 conn 同源）；`image_url` 支持 `translated`/`compare`；新增 `image_state`（typed 空态）；`_uri_within` 提取（根内校验逻辑不变）；模块顶部补 `ArtifactType` import；装配点传入 locator |
| `src/ui/viewmodels/workbench/viewmodel.py` | 新增 `viewerImageStateFor(mode)` Slot（typed 空态暴露；QML 零改动） |
| `tests/core/test_page_catalog_modes.py`（新） | 3 用例（解析+同 revision+compare 左图 / invalid 诊断 / 契约退化） |

白名单核对：`src/ui/qml/**`、Schema/migration、`requirements.txt`、pipeline seam 零改动；既有测试文件零改动（tests 仅新增 1 文件）。

## compare 语义的依据（Task 风险项裁决）

Task 要求"从 D 文档与既有 QML 绑定推出，不得自创"。证据链：
1. `ViewerPanel.qml:85` 注释 **`// Compare pane (D05 §20.1 左右双图)`**——compare = 左右双图；
2. 左 pane `source: viewer.imageUrl`（原图，带"原图"角标，ViewerPanel.qml:70-78），右 pane `source: viewer.translatedUrl`（译图，ViewerPanel.qml:99）；
3. `WorkbenchView.qml:30`：`wViewerTranslated = vm.viewerImageUrlFor("translated")`；
4. VM `viewerImageUrlFor` docstring："Compare pane needs the translated variant, D05 §20.1"。

⇒ **compare = 左右双图（左=原图 Managed Copy，右=当前 TRANSLATED revision）**，无需产品裁决，不 BLOCKED。

## AC 逐条

### AC ① 解析规则 — 达成

`image_url(page_id, mode)`：
- `translated` → `SqlitePageArtifactLocator.locate_current(page_id, ArtifactType.TRANSLATED)` → `revision.managed_path` → Managed 根内校验（`path.relative_to(root)`，不绕过）→ `file://` URI；
- `compare` → 与 `original` 相同：页的 immutable Managed Copy（左右双图的左 pane）；
- 其他 mode（含 `clean`）→ `""`（不静默给错图；clean 不在本 Task AC 内，用例钉住不扩散）。

### AC ② 与阅读器一致（同页同 revision）— 达成

`test_translated_and_compare_resolve_like_the_reader`：装配发布当前 TRANSLATED revision（`ArtifactStepWriter.prepare_revision + adopt_current`，与 TASK-040 生产发布路径相同）后，workbench `viewerImageUrlFor("translated")` 解码出的文件路径 == `_ManagedReaderCatalog(...).list_pages(...)` 的 `translated_path`（同一 locator 类、同一 conn、同一 `locate_current` 语义）。

### AC ③ 缺失语义 — 达成

URL 面保持既有 QML 契约（一切失败 → `""`，QML 空态文案"译图尚未产出"/"该模式暂无产物"已就绪、零改动）；新增 typed 通道：
- `catalog.image_state(page_id, mode)` → `"ok" | "missing" | "invalid"`（missing=页/产物不存在；invalid=引用存在但逃出 managed 根或文件消失）；
- VM `viewerImageStateFor(mode)` Slot 暴露（无页时 `"missing"`；catalog 无该能力的旧装配退化 `"missing"`）。

`test_invalid_paths_stay_diagnosable_not_silent`：删除 managed 文件后 `translated` 从 `ok` 变 `invalid`（非 `missing`）、URL 仍 `""`、`original` 不受影响——"无数据"与"路径非法"可区分。

### AC ④ QML 不改 — 达成

`git diff a2306e3..3cc5cf5 --stat -- src/ui/qml` 为空。VM 侧仅**新增** Slot（不改既有属性/方法），既有绑定不受影响；区分态的 QML 呈现待 TASK-047 设计门后另开切片。

### AC ⑤ 判别力 + 不回归 — 达成

- **行为级判别（修前 detached 树 `a2306e3`）**：新用例 2 条 FAILED、exit 1（`viewerImageUrlFor("translated")==""` 断言失败 + `viewerImageStateFor` AttributeError），`discriminating-new-tests-vs-prefix.log`；第 3 条（legacy 契约）仅钉既有行为，**声明不计判别**。
- **双树探针对照**（`viewer_modes_probe.py`，同一页同一 Managed Copy、发布 translated 后）：

| 树 | original | translated | compare | state 通道 |
|---|---|---|---|---|
| 修前 ×2 | resolved | **EMPTY** | **EMPTY** | unavailable |
| 修后 ×2 | resolved | **resolved** | **resolved** | ok |

（`probe-pre-fix-run{1,2}.txt` / `probe-post-fix-run{1,2}.txt`；P-6 复核签名"workbench translated/compare 恒空、reader 非空"在修前列复现。）

- **不回归**：定向 `tests/core tests/workbench` **87 passed**（`targeted-core-workbench.log`，含 QML 契约测试）；全仓 ×5 **895 passed / 0 skipped / exit 0**（892 master 基线 +3 新用例），逐次 `full-suite-post-fix-run{1..5}.log`。无新增 skip/xfail、既有断言零改动。

### AC ⑥ Handoff/证据/Review/集成/台账

本文件 + `verification/TASK-051/**`；Review、集成、台账在本提交后进行（结果回填 Task 文件）。

## 设计取舍（Review 关注点）

1. **locator 注入而非模块级单例**：catalog 与 reader_catalog 用同一 `SqlitePageArtifactLocator(conn)` 实例化点（同一 conn），AC② 的"同一 revision"由同源查询保证，不靠巧合。
2. **URL 面不扩协议**：所有失败仍 `""`（QML 契约不变），可诊断性放 `image_state` 新通道——避免为错误码发明 URL 之外的字符串协议。
3. **compare 复用 original URI**：不复制文件、不生成第二 URI；左右双图的左 pane 本来就该是原图。
4. **unknown mode 仍 `""`**：`clean` 等模式本 Task 不实现，行为与修前一致（用例钉住），避免静默给错图。
5. **VM Slot 判 `getattr(self._page_catalog, "image_state", None)`**：容忍测试替身/旧 catalog 无新方法（退化 `missing`），与既有 `_image_url` 的 getattr 风格一致。

## 证据索引（`verification/TASK-051/`）

| 文件 | 内容 |
|---|---|
| `probe-post-fix-run{1,2}.txt` | 修后三 mode resolved、state=ok |
| `probe-pre-fix-run{1,2}.txt` | 修前 translated/compare EMPTY、state=unavailable |
| `discriminating-new-tests-vs-prefix.log` | 新用例对修前树 2 failed / exit 1 |
| `targeted-core-workbench.log` | 定向 87 passed |
| `full-suite-post-fix-run{1..5}.log` | 全仓 895 passed ×5 |

## 已知边界 / 留给后续

- `clean` 模式的解析不在本 Task AC 内（工作台 clean 档仍为空态），如需可与 TASK-052 失败可见化一起评估。
- QML 侧消费 `viewerImageStateFor` 呈现区分文案属 TASK-047 设计门后的实现切片。
- compare 右 pane 的"译图"URL 与 compare 模式左 pane 的刷新时序由既有 `viewerChanged` 通知承担，未加新信号。
