# FEAT-CREATE-4 AC 结果

固定基线：`ae44d0047092c584c7f82cde203e229c56505156`。实现仅修改 `apps/desktop/frontend/**`；契约、Python Core、Tauri host、Schema、依赖、STATUS/PLAN 均未修改。验证时用户 `%APPDATA%` 的源 `catalog` / `data` 只读；所有 GUI 写入落在隔离 `NEWMANGA_DATA_ROOT`。

| AC | 结果 | 证据 |
|---|---|---|
| AC1 空书架建作品 | PASS：空书架工具栏和空态按钮均 enabled；提交真实调用 host command，成功后展示 host 返回的 `BookSummary`。 | `gui-r5/uia-run.log`、`gui-r5/initial-bookshelf.uia.txt`、`gui-r5/create-book.uia.txt`、`frontend-npm-test-delivery.log` |
| AC2 建章节并进入阅读器 | PASS：`create_chapter` 返回的章节进入列表；UIA 点击阅读并观测到阅读器返回按钮。 | `gui-r5/uia-run.log`、`gui-r5/chapter-created.uia.txt`、`frontend-npm-test-delivery.log` |
| AC3 导入转可用 | PASS：创建目标后导入对话框显示目标选择器、无 unavailable notice；选择章节后文件与文件夹入口均 enabled。 | `gui-r5/uia-run.log`、`gui-r5/import-available.uia.txt` |
| AC4 错误、重复标题、长度 | PASS：只把 §5.10 五个 `message_key` 映射到固定类别和本地文案，未知/原始错误统一映射安全兜底；测试覆盖带路径和 Secret 的 host 拒绝、重复作品名和章节名。输入无 `maxLength`，UI 只拒绝全空白值并原样提交非空输入。 | `frontend-npm-test-delivery.log`；实现：`apps/desktop/frontend/src/bookshelf/CreateTitleDialog.tsx`、`apps/desktop/frontend/src/library/client.ts` |
| AC5 前端测试与构建 | PASS：真实基线为 278 passed；本次 285 passed / 0 failed（增加 7 项）；`npm run build` exit 0。任务描述的“既有 274”与该 worktree 全量实测基线相差 4，按实际基线登记。 | `frontend-npm-test-baseline.log`、`frontend-npm-test-delivery.log`、`frontend-npm-build-delivery.log` |
| AC6 真实 GUI 与隔离 | PASS：按 `npm run build` → `build_sidecar.ps1 -Force` → `cargo build` 完成；5 个 sidecar 的 bundle/resource SHA-256 全相同；在隔离数据根通过 UIA 创建作品、章节、进入阅读器并验证导入可用。源 `%APPDATA%` 的 `catalog` 和 `data` 前后树哈希一致。 | `sidecar-build.log`、`cargo-build.log`、`sidecar-resource-hash.json`、`isolation-copy.json`、`gui-r5/uia-run.log`、`isolated-records-check.log`、`source-preservation-check.json` |
| AC7 交付与证据 | PASS：实现 commit、Handoff、Canonical Evidence 已固定；Task 状态 `in_review`。独立 Review 与 Coordinator 主仓库 closeout 尚未执行。 | 本 Task Canonical Evidence 表与 Handoff |

## 验证细节

- 调用形状完全按 M2-C1 §5.10：`library_create_book` 使用 `{ payload: { title } }`；`create_chapter` 使用 `{ payload: { book_id, title } }`。不由前端合成成功记录；列表项来自真实 host 返回值。
- `npm test`：Vitest 28 个文件，285 passed，0 failed，0 skipped，exit 0。新增用例覆盖空书架创建、命令名/参数、错误脱敏、重复作品标题、重复章节标题和无长度上限。
- `npm run build`：`tsc && vite build`，exit 0。
- GUI 验收使用本机 Windows UI Automation 操作真实 Tauri 应用，不是浏览器 mock。测试标题为 `MangaCreate4UIA20261017` 和 `MangaChapter4UIA20261017`；隔离数据库复核为 1 个作品、1 个章节。
- 隔离准备从 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}` 复制数据到 `apps/desktop/src-tauri/target/feat-create-4-isolation-20261017`，`derived` 等目录为空；只对复制出的 catalog 做 namespace rebind。源数据树哈希前后相同。
- `cargo build` 曾生成 `apps/desktop/src-tauri/**` 行尾差异；已恢复生成文件。交付差异中 Tauri/Core 路径为零，最终工作区 Tauri 路径干净。
- 测试环境输出既有 React `act(...)` 警告；测试全部通过。构建输出有既有 Rust unused-code warnings，无失败。

## GUI 复验顺序

1. UIA 初始树确认 `+ 新建作品` 与空态 `新建作品` 都 `IsEnabled=True`。
2. 提交标题 `MangaCreate4UIA20261017`；UIA 观测作品卡出现。
3. 提交章节标题 `MangaChapter4UIA20261017`；UIA 观测章节行出现并启用阅读，点击后进入阅读器。
4. 返回书架打开 `导入作品`；目标选择器出现、没有 unavailable notice；章节级导入的文件与文件夹按钮均启用。
5. 应用 exit code 0；隔离数据库精确匹配 1 本作品 / 1 个章节；源 AppData `catalog` / `data` 未变化。
