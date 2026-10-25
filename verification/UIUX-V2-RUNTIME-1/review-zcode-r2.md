# Review：UIUX-V2-RUNTIME-1（ZCode r2 增量复审）

decision: approved
reviewed_head: af421b9e6（修复 head；其后继 df48a14b3 为纯文档提交——r2 任命段与 Task 卡指针更新，仅动 2 个 doc 文件，已核 `git diff af421b9e6 HEAD --stat`）
base_commit: b51d202c9（r1 基准不变；本报告只裁定增量 `1853f0a07 → af421b9e6`）

- Reviewer：ZCode（与 r1 相同，未参与实现；独立复跑 + 独立复做变异核验）。
- 复审日期：2026-10-25（Asia/Shanghai）。
- 复审范围（按任命书 r2 段）：F-1/F-2 是否真正修复、F-3/F-4/F-6 是否落实、F-5/F-7 债务登记是否如实、修复本身是否引入新问题。其余六轴 r1 已 PASS，未重走；未发现修复引入的新问题触及那些轴的既有结论。
- 增量事实（`git diff --stat 1853f0a07 af421b9e6`）：src 改动 4 文件（`pages/Shelf.test.tsx` 新增 179 行、`dev/devMockBridge.ts` +11/-6、`ui/PageState.tsx` 1 行、`components/PrimaryNav.tsx` 注释 5 行）+ 证据重采（tsc-run/vitest-run/shots-03/visual-verification）+ 治理文档（APPOINTMENT/Task 卡/PLAN/STATUS/LEDGER/handoff）。区间另含两个 r1 时期的 docs 提交（66013fc33 任命与 Task 卡入库、d6c119fe1 证据 pin 与 AC13 置回 PARTIAL），无技术内容。`package.json`/`package-lock.json` 零改动；无 Rust/Python/契约改动；无测试删除或弱化（59→60 文件、561→564 测试，全为净增）。

## 对 r1 七条 finding 的逐条处置判定

| id | r1 严重度 | 判定 | 依据 |
|---|---|---|---|
| F-1 书架页运行时诚实数据零测试守卫 | P1 | **CLOSED** | 新增 `src/pages/Shelf.test.tsx`（3 例）覆盖任命要求的全部面：①真实字段在场先行断言（listBooks 被调、书卡渲染书名/`128 页`、原名进详情面板、`page_count: null` 显式「页数未知」——防止「不出现」断言因空页面假通过，`Shelf.test.tsx:133-142`）；②反回填断言（`.nm-progress` 0 个、全网格无 `\d+%`、无 `VOL.`、无七态 `status-*` 标记、无 fixtures 假作者名/假计数，`145-153`）；③章节页数来自 IPC（`3p` 非 fixtures 的 `24p`）且章节无状态标记（`156-169`）；④空书架诚实空态（`171-178`）。**本审查独立复做变异核验**：`progress: null → 42` → `Shelf.test.tsx` **1 failed**（正是反回填断言）→ Edit 原样还原 → **3 passed**（见复跑记录 M-3/M-4），判别力实证，与 r1 的 561 条零拦截形成对照 |
| F-2 dev mock 枚举闭集外值 | P2 | **CLOSED** | `dev/devMockBridge.ts:126-132`：`region_type` = `speech`/`narration`/`sfx`，`origin` = `machine`/`machine`/`user`，`sfx_policy` = `translate`/`skip`/`translate`——逐值对照 `region/types.ts:14-37` 冻结闭集（RegionType 六值 / RegionOrigin 四值 / SfxPolicy 三值）全部合法；且顺手修复了 r1 未单独点名的 `sfx_policy: "preserve"`（同样闭集外），并在注释中引用 F-2 来源。`shots/03` 已重截（Blob 447931→448928 bytes），经视觉模型逐行核对：三行区域条目完整（**对白 1**（蓝色色条可见）/**旁白 2**/**拟声 3**，右侧 `r1 · 机器` 等来源文字完整无空），r1 观察的残缺渲染不复存在；`visual-verification.md` 新增「ZCode 独立审查 r1 的处置」段逐条登记。生产路径不受影响面与 r1 相同（Core 侧闭集门） |
| F-3 tsc 证据占位未披露时序 | P3 | **CLOSED** | `tsc-run.txt` 首行占位 `REVIEW_HEAD_PENDING` 已移除，替换为「采集时点：修复提交头（review r1 处置后）」+ F-3 来源说明两行；`vitest-run.txt` 同步重采并标注采集时点 |
| F-4 PageEmpty 无显式 role | P3 | **CLOSED** | `ui/PageState.tsx:66` 根节点加 `role="status"`，四态 role 一致（loading/empty/blocked=status、error=alert）。语义核对：`status` 隐式 `aria-live=polite`，与 PageLoading 的显式 polite 无冲突；空态块作为新插入 live region 的播报行为是标准可接受做法。全量 60 文件 564 测试全绿，证明该属性未与任何既有断言冲突（含 `Settings.test.tsx` 的 settings-preview-blocked 等 PageEmpty 消费者） |
| F-5 两处 base 冻结字面色值未令牌化 | P3 | **CLOSED（按债务登记处置）** | `doc/tasks/UIUX-V2-RUNTIME-1.md:90`（R7）逐字点名两处：`.nm-window-btn--close:hover` 的 `#FFFFFF`、`.nm-command-backdrop` 的 `rgba(0,0,0,0.32)`，注明「均为 DESIGN-V2-IMPL-1 既有、本 Task 未新增」，并入后续「控件几何 + 装饰色令牌」Task。与 r1 建议（登记或令牌化）一致 |
| F-6 入库版任命书范围描述不符 + PrimaryNav 注释过时 | P3 | **CLOSED** | ①APPOINTMENT.md 第 9 行已为披露版（明确区间含治理提交 `f7e63c70c`、指示跳过；r1 审查时为工作树未提交修订，现已入库）；②`components/PrimaryNav.tsx:39-41` 注释更新为「当前五个消费点（运行时四页经 `ui/UiRoot`、静态设计预览经 `pages/DesignPreview`）」，与实际渲染点相符 |
| F-7 设计预览「Esc 返回」假提示 | P3 | **CLOSED（按债务登记处置）** | R7 同段点名「设计预览 fixture 底栏未实现的『Esc 返回』keyhint」，注明 base 既有、运行时分支无此假提示，并入「设计预览清理」Task。与 r1 判定（base 既有、不属本 Task 引入）一致 |

## 修复本身是否引入新问题

- **新测试质量（F-1 守卫）**：无假断言结构——每条「不出现」断言之前都有「真实数据在场」断言兜底（注释明示防假通过意图）；fixtures 假值名单（南野灯/绫濑千景/18 话/1280 页/设计预览）取自真实 fixtures 常量；无时序 hack（`mountShelf` 用 4 跳 microtask 显式等待两级取数链，`Shelf.test.tsx:109-114`）。变异核验证明判别力真实。
- **mock 改动影响面（F-2）**：`devMockBridge.ts` 无任何测试直接消费（`Workbench.test.tsx`/`Reader.test.tsx` 等自带独立 mock），改动只影响 dev 浏览器预览；全量 564 通过证明零回归。
- **role 属性影响面（F-4）**：见上，无断言冲突、无 aria 语义冲突。
- **增量范围纪律**：src 仅 4 文件且全部对应 r1 findings；无越界路径、无依赖改动、无测试弱化。
- **发现两处处置记录精确性瑕疵（新 P3，不阻塞）**：
  - **N-1**：`visual-verification.md:61` 处置表 F-2 行声称「重截 `shots/03` 并**更新本文件第 03 行**」，但第 03 行（`visual-verification.md:17`）文字未改。实质无害——原 03 行描述（「检查器显示真实区域 3 条与『未识别』OCR 说明」）在修复后依然准确（且不再有残缺行），但处置记录与事实有一处不符。建议 DSH 集成时顺手把 61 行的「并更新本文件第 03 行」删去或补一次真实更新。
  - **N-2**：处置表 F-5 行的处置/证据写「并入 **R6** 的后续 Task｜证据：Task 卡 **R6**」，实际登记位置是 **R7**（`doc/tasks/UIUX-V2-RUNTIME-1.md:90`；R6 是间距字面值债务）。实质均已登记（F-5/F-7 都在 R7），仅交叉引用条目号不一致。建议顺手订正。

## 复跑记录

| # | 命令（cwd=`apps/desktop/frontend`） | 结果 | 与证据比对 |
|---|---|---|---|
| R-3 | `node node_modules/typescript/bin/tsc --noEmit` | exit 0，无输出 | = 重采后 `tsc-run.txt`（exit_code 0、output 空）✅ |
| R-4 | `npx vitest run --reporter=basic` | exit 0；Test Files 60 passed (60)；Tests 564 passed (564)；Duration 5.99s | = 重采后 `vitest-run.txt`（60/564/exit 0/5.94s）✅（较 r1 净增 1 文件 3 测试 = Shelf.test.tsx） |
| M-3（变异核验，独立复做） | 将 `pages/Shelf.tsx:356` 运行时 `progress: null` 改为 `progress: 42` → `npx vitest run src/pages/Shelf.test.tsx` | **1 failed / 2 passed，exit 1**——失败正是 `renders only IPC-backed fields and never fabricates progress/volume/state` | F-1 守卫判别力实证；与 DSH 在 `visual-verification.md` §变异核验 登记的结果（1 failed → 还原 3 passed）一致 ✅ |
| M-3 还原 | Edit 原样改回（未用 git checkout）→ 复跑 `npx vitest run src/pages/Shelf.test.tsx` | **3 passed，exit 0** ✅ | `git status --porcelain` 对 `src/**` 零输出（本 review 写入前全仓干净） |
| 证据核对 | `git diff 1853f0a07 af421b9e6` 增量逐 hunk；`shots/03` 视觉模型逐行核对；`git diff af421b9e6 HEAD --stat` | 增量与处置声称吻合（除 N-1/N-2 两处记录精确性）；截图三行区域完整（对白 1 蓝条/旁白 2/拟声 3，来源文字完整）；df48a14b3 纯文档（Task 卡 12 行 + APPOINTMENT r2 段 16 行） | ✅ |

## 对 AC 的增量判断

- **AC8（r1 判「实现成立、证据主张 PARTIAL」）**：F-1 修复后，四页反 fixtures 回填断言齐全（Workbench/Reader/Settings + **Shelf**），r1 的缺口闭合，AC8 证据主张升级为完整成立。
- **AC11**：59/561 → 60/564，本审查复现。
- **AC13**：r1（changes_requested）+ 本 r2（approved）构成完整独立审查链；`integration_commit` 回填与 Task 收口交 DSH。
- 其余 AC 无增量改动，r1 判定维持。

## 结论与放行条件

**decision: approved**。

- r1 的 1×P1 + 1×P2 已实质修复且经独立复跑与独立变异核验实证；5×P3 中 F-3/F-4/F-6 直接修复、F-5/F-7 如实登记为 R7 债务。
- 修复未引入新问题；新增两处处置记录精确性瑕疵（N-1/N-2，均为 P3 观察项，不构成放行条件）：建议 DSH 在集成收口时顺手订正 `visual-verification.md:61` 的两处交叉引用表述。
- 维持事项：真实 Tauri + Python Core 端到端仍为 HUMAN_VERIFY（`visual-verification.md` §未验证项），不因本复审解除；R6/R7 债务按 Task 卡解除条件另立后续 Task。
- 本 review 为只读复审 + 唯一写入 `review-zcode-r2.md`；结束时工作树除本文件外零改动。
