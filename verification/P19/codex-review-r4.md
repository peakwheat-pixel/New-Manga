---
task_id: P19
reviewer: Codex
owner: dsh
author: dsh
base_commit: 157e00f67b48bfa3452006f03734bdad485741d7
reviewed_head: 2117933b0294ccc1a80dfd86d39f59c697bdf165
decision: changes_requested
---

# P19 独立复核 R4

## 固定范围

本 Review 固定审查用户指定的 `2117933b0294ccc1a80dfd86d39f59c697bdf165`。复核期间共享工作区 main 前进到 `1a5a7fd681314d9c4be7a54d2f4c71c264976784`；该后续提交仅更改 `run-d-acceptance-v3.ps1` 与 `rebuild-and-verify.ps1`，不纳入本次结论。当前报告只创建本文件；未改 Task、STATUS、Plan、实现代码或现有 dirty 文件。

| AC | R4 判定 | 依据 |
|---|---|---|
| AC1 | 沿用 R3 的 PASS，本文未重做 D/D+ 用户裁决 | Task 与 Handoff 对 D+ / D 的记载仍不一致，列入 AC6 |
| AC2 | **FAIL / 未闭合** | ①②③ 在 0047 真实 GUI 与隔离 DB 通过；Run、导出未走有效章节入口，翻页后仍显示第 1 页 |
| AC3 | **FAIL** | 已并入的 58 命令扫描实际复现合成 Windows 路径经设置接口回显 |
| AC4 | **PASS（现有可见未交付控件范围）** | 设置九分区在 UIA 中可见且 `IsEnabled=False`；工作台未冻结控件有禁用态和原因 |
| AC5 | **PASS（新三轮产物）** | 新 AC2/AC4 运行有逐步 trace、UIA、截图、时间戳及 runner 退出码 |
| AC6 | **FAIL** | 新证据未进入 Canonical Evidence pins；Resource Manifest 缺失，Closeout pending，Handoff 仍为 R3 |

## 1. AC2 ①②③：建作品、建章节、导入

**复核命令与结果：**

- 只读打开 `%TEMP%\p19-ac2-main-62cd3a8a\library.db`（SQLite URI `mode=ro`），查询 `books`、`chapters`、`pages` 计数及 pages 行。
- 对 `%TEMP%\p19fx\A\001.png`、`002.png` 读取磁盘字节，计算长度和 SHA-256；对照 `verification/P19/ac2-main-20261018-0047/uia/07-after-import.uia.txt`、`08-reader.uia.txt`、`09-reader-after-next.uia.txt`。

隔离库计数为 **1 book / 1 chapter / 2 pages**。`001.png` 为 **67,780 B**, SHA-256 `1bb7f48ea396ed081ebe7706b909081ab3b1f86f7b4e2a7518fc3568ce3e887a`；`002.png` 为 **2,282 B**, SHA-256 `6eac55349be7e1a9effade65bb694c48b6c25b1e6b2f6b35319ffb42c93a31ec`。fixture 两文件逐项同长度、同 hash。0047 的 UIA 转储显示书架作品、章节和导入报告（2 imported）；Reader 显示 `1 / 2` 且 `Next page` 可用。故本轮独立判 **①②③ PASS**。

边界：0047 的 runner 自身 metadata 把 `pages_after_import` 记为 `-1`、`reader_total=5`，与直接 DB 查询/UIA 不符；我没有采用这些 runner 汇总值。另 `09-reader-after-next.uia.txt` 仍显示 `Image|Page 1` 与 `1 / 2`，所以阅读器翻页尚无 PASS 证据。0051 是另一隔离根；trace 记录选择器找不到 001/002、DB 查询 0 页、runner exit 1，不作为导入通过证据。

## 2. AC2 ④Run / ⑤导出：阻塞与根因（首要裁决）

**复核命令与结果：**

- 读取 `ac2-main-20261018-0051/uia/07-after-import.uia.txt`、`11-workbench.uia.txt`、`trace.log`、`run-metadata.txt`，并检查 `07-after-import.png`、`11-workbench.png`。
- 检查 `apps/desktop/frontend/src/shell/AppShell.tsx`、`workbench/WorkbenchPage.tsx`、`bookshelf/ChapterList.tsx`、`workbench/WorkbenchToolbar.tsx` 及 `run-ac2-mainflow-v1.ps1` 的对应代码。

0051 的书架 UIA 确实显示 `P19Ac2Book` 和 `P19Ac2Ch1`；工作台 UIA 显示 `ListItem|暂无作品`、`启动 en=False`、`导出选择页 en=False`，截图也一致。trace 记录先选中作品，之后直接点击侧栏 `🛠️ 工作台`。因此“这次直接侧栏路径上列表为空、两个按钮禁用”成立。

但“因为空列表，所以 Run/导出永久不可执行”不成立为本次证据结论：

- `AppShell` 使用四页 keep-alive 容器，工作台启动时即挂载；`WorkbenchPage` 的 `listBooks()` 只在 `[booksRetry, clients]` 变化时读取，没有跟随页面激活或书架建书刷新。空库启动后再从书架创建作品、用侧栏进入工作台，会留下空列表。这是**直接侧栏路径的产品状态刷新缺陷**。
- 同一书架章节行有实际 UI 操作 `翻译`（`ChapterList.tsx` title 为“进入工作台翻译”），它调用 `onEnterWorkbench(bookId, chapterId)`；`AppShell` 将两个 ID 传给工作台，`WorkbenchPage` 据此设置选中的作品/章节并读取章节页。toolbar 的 Run 以 `hasChapter` 为前置；导出另外要求 `selectedPageCount > 0`。
- 0051 runner 没点击章节行的 `翻译`，也没在工作台选页。其执行路径不能证明产品没有 Run/Export 能力。

**独立定性：**对“Run/Export 因空列表而无法执行”这一阻塞，判 **(c) runner 未走上下文入口及选页前置操作**，不是“能力未实现”；空列表本身是可单独记录的**产品刷新缺陷**。可行 UI 路径：书架选中作品后，在目标章节点 `翻译`；待工作台章节页列表出现后，Run 选 `全章翻译` 并启动；导出先点选页列表中的页面，再打开 `导出选择页`。**该路径只有源码支撑，现有 GUI 运行没有执行它**，所以 AC2 ④⑤仍为 NOT_RUN/FAIL，不能据此关闭。是否另立缺陷 Task 或接受限制留给用户裁决。

补充：0051 的 TEMP 库在运行 trace 于 00:49:08 记录 0 页，之后文件修改时间为 00:49:22 且读到 3 页；这是可变 TEMP 状态，不能反推 00:49:08 的页面状态，也没有用于本项结论。

## 3. AC4：设置分区与四页禁用态

**复核命令与结果：**

- 读取 `d-run-20261018-0056/trace.log`、`run-metadata.txt`、`uia/04-settings.uia.txt`、`04-settings.png`，并对照 0053/0055 运行目录。
- 读取固定 head 211 上的 `run-d-acceptance-v3.ps1` 中 `PR` 断言。

0056 为 **24 checks / 9 fails / runner exit 1**；逐行重数为 **15 PASS、9 FAIL**，不是分析稿所称“14 项全 PASS”。15 项涵盖窗口、页面导航、Provider 表单四字段、OCR toggle、保存和 profile-visible。九个真实 Settings 分区在 04-settings UIA 中均显示“未开放：等待 section schema 冻结”、`en=False`；trace 对各项均记录 `invoke=failed`。截图可见这些分区灰化且原因仍显示。结合旧四页 UIA 中工作台未冻结写操作也为禁用并带原因，我判定**已枚举的 AC4 控件满足可见、禁用、有原因**；因此 AC4 在该已知控件范围为 PASS。

runner 的九条 FAIL 来自额外的 Pane 名集合判据：211 上代码把 `$b` 与 `$a` 的 `PN` 集合比较，并把 `PAGE_UNCHANGED` 纳入断言；trace 记录的是 `PAGE_CHANGED`。但报告引用的 `panes=[]` 实为另一变量 `$na`（筛选 Pane 名中含“未开放”的项），**它不是**比较用的 `$a`，所以“调用后 Pane 集合为空”的解释没有被 trace 证明。直接的 `en=False`、`invoke=failed` 与 UIA 截图支持控件禁用；runner 的最终 exit 1 仍应保留，不应改写成脚本 PASS。

**PAGE_CHANGED 判据：P2 遗留项，不是产品阻断。**改进方向是断言 `IsEnabled` 和 Invoke 的明确结果/异常类型，并记录调用前后稳定的路由标记或 UIA 树；不要以 Pane 名称集合差异代替交互结果。注意：后续提交 `1a5a7fd68` 已改该判据并扩充 smoke 导航，但超出本 Review 的固定 head，未在本结论中验证。0055 有 14 checks/0 fails，但没有执行九个分区探测；0053 探测名称不匹配。因此有效的九分区探测证据主要是 0056 一轮。

## 4. 原始产物完整性（R3-004）

**复核命令与结果：**

- 对 0044、0047、0051、0053、0055、0056 目录递归计数 `*.uia.txt`、PNG，并检查 `trace.log`、`run-metadata.txt` 中的 started/ended/exit_code。
- 对 `ac2-run2..12` 做相同清单检查。

新证据六轮均有 trace、metadata（开始/结束时间、runner exit code）、UIA 和截图：AC2 三轮分别是 **6/6、12/12、13/13** 份 UIA/PNG；AC4 三轮分别是 **8/8、7/7、8/8**。新证据补足了 R3-004 对新运行缺原始轨迹、UIA、截图和退出码的缺口。

旧目录描述需修正：`ac2-run2..9` 各有 trace，但没有 UIA、PNG、metadata 或独立 exit 文件；`ac2-run10..12` 各只有 app stdout/stderr。新运行的完整产物已解决“新验收没有原始证据”的问题；旧失败尝试仍不完整，但不再作为当前 AC PASS 依据。判 **R3-004 CLOSED（新运行）**。

## 5. Runner 基建（R3-005）

**复核命令与结果：**只读检查 `run-ac2-mainflow-v1.ps1`、`run-d-acceptance-v3.ps1`、`rebuild-and-verify.ps1` 的输出目录、覆盖保护及退出码分支，并对照各次 metadata。

三个 runner 默认创建带时间戳的新目录；已有非空目录默认拒绝（exit 4；显式 `AllowOverwrite` 除外）；关键断言失败以非零退出，metadata 记录结果。故 R3-005 的**通用输出/失败码基建满足要求**。

仍有两个具体限制：AC2 runner 的 `SelectFixtures` 在文件夹导航前缓存 `$dlg`，导航后未重新获取 UIA dialog；0051 的 `PICKER_MISSING` / `PICKER_VISIBLE_ITEMS=0` 与此一致。AC4 在固定 head 211 的 Pane 集合断言见第 3 项。两者不推翻 0047 的成功导入，也不代表产品流程通过；后续修订需有与 runner 源码对应的真实 GUI 复跑证据。

## 6. 交付闭环与 Canonical Evidence（R3-003）

**复核命令与结果：**

- 用 PowerShell `Get-FileHash -Algorithm SHA256` 逐行重算 Task 现有 10 条 Canonical Evidence，检查 `git ls-files --error-unmatch`、文件引入 commit。
- 检查 `doc/tasks/P19.md`、Handoff、Plan、STATUS，并检查 `Test-Path verification/P19/resource-manifest.json`。

| Task 表中的文件 | 当前磁盘字节 SHA-256 | 结果 |
|---|---|---|
| `ac2-partial-r1.md` | `25d2d56e81b6d4b8d17aa3bd31aa373e1b4d7a5de835e020cd573c0246d675a7` | MATCH |
| `ac4-verified-rebuilt-r5.md` | `6dd84e34ac66980be3f12a162e0f399b3689d503ede132124a25ebebd9b07063` | MATCH |
| `d-acceptance-r2.md` | `d5bffd9ea35702acd7f50ed7dd539037e0e33008e44b3ee36ea01bd8092ac6f8` | MATCH |
| `run-d-acceptance-v2.ps1` | `7553429282234107c08225d7abaf86e3316661d3d4fbca39bcac8ca1a2965837` | MATCH |
| `codex-review-r1.md` | `32f7e2fc93d8677055679c0487f4ba1fb17cf090b179402a2fe941aedce5cce4` | MATCH |
| `codex-review-r2.md` | `d9009ae93f714a2e6b631eb341537ec97baaa3e3f460c95e6337ce3f6910da1c` | MATCH（当前 dirty） |
| `codex-review-r3.md` | `3ec922c16139807ee608e3c16fcaaf94dc37ce0959524e0181edec5b4e8a20cd` | MATCH |
| `d-run-v2/trace.log` | `6ce28ef237c08b93017d394c50e93fad2cc898f27c5ce6269ad1abfd540e12c9` | MATCH |
| `import-no-response-r4.md` | `05cb83b7bcbe8e5ae339e933cef4d98c4d47fe3b931aca602ec0f2c903a3a83f` | MATCH |
| `create-work-and-import-r6.md` | `39f5bbe4326a095aea2e86d92794389b8591c14d150cfe9101b0af6204c966fa` | MATCH |

**合计 10 MATCH / 0 SHA mismatch；10 项路径均 tracked。**但这不构成闭环：`codex-review-r2.md` 的工作树字节虽匹配 Task pin，却与 HEAD 中对象 hash 不同且为 dirty；依用户指令保留不碰。R1 现在已 tracked，`git log --diff-filter=A` 显示首次纳入 commit 为完整 SHA `2117933b0294ccc1a80dfd86d39f59c697bdf165`，但 Task 表该行 commit 仍空。其余 9 个 commit 格式均为短 SHA，不符合 Task AC6 的原样完整 commit 要求。应将 R1 行补为上述完整 SHA。

其他闭环仍失败：Task 的新 `delivery_head=4fb8fc8aacc3798cdcc46049171cc6c9d740a5d3` 是存在的 full SHA，但 AC2/AC4/P20 新产物由 211 提交且没有加入 pins，Handoff 仍为 R3；Task `canonical_evidence_status=in_progress`，Closeout Record 却写 `pending`；`resource_closeout_status=pending`，且被引用的 `verification/P19/resource-manifest.json` 不存在。Resource Manifest 仍只列 22 个旧 TEMP 根，未列本轮 `p19-ac2-main-*`、`p19v3-*`、`p19-smoke-*`。Handoff 仍把导入写为未完成、AC3 写为待 P19-AC3-1；这与现有 0047 导入实测及 7b1 merge 后的事实不一致。Task 与 Plan/STATUS 的阶段仍一致为 `in_review`，P20 为 `proposed`；STATUS 仍链接 R3，R4 指针尚未登记（本轮按授权未改 STATUS）。Task 的验收方法仍写 D+，Handoff 写 D，口径仍需协调。

**AC3 子 Task 独立复核：**`git merge-base --is-ancestor 7b1fcc45a HEAD` exit 0；CSV 有 **58 rows（51 production / 4 probe / 3 AC1）**，扫描 exit 0 代表扫描完成。矩阵 `settings_get` 与 `settings_update_section` 的 return 都标 FAIL；`raw/settings-path-roundtrip.stdout.txt` 实际含两次 `C:\\private\\synthetic-source.cbz` 回显，`synthetic_secret_returned=false`、`file_io_attempted=false`。这不是用户数据泄漏证据，而是合成输入已证明通用设置响应可把 OS 路径交给 WebView，违反 P19 AC3 的“返回无文件系统路径”。静态 WebView ACL/SQLite/模型边界证据有价值，但不能抵消这个反例；另有 30 个 production error projection 标为 code-only/unvalidated。**R3-002 的扫描交付已完成，AC3 本身仍 FAIL。**

## 7. P20 发布 Gate 预审

**复核命令与结果：**读取 `bundle-resource-hash.json`、`run-metadata.txt`、`gate-trace.log` 并对两条记录路径执行 `Get-FileHash`。

JSON 中 bundle/resource SHA-256 均为 `6ab8ada366cbac79720818c4b42eb66888a44138366c50f73e55a55d83b0be5d`，`equal=true)；当前两目标文件 hash 也相同。Gate trace 记 `SMOKE window_found=True exit=0`，隔离根为 `%TEMP%\p19-smoke-b1b816a7`；metadata 为 **checks=5 / fails=0 / exit_code=0**。因此启动 smoke 确实找到真实窗口并退出成功。固定 head 211 的该次日志没有 `SMOKE_PAGE` 路由记录；它证明窗口可达，不证明四页导航。后续 head 1a5 增加的四页 smoke 代码不属于本次被审 head。

## 阻断项

1. **P1 AC2 未闭合**：④⑤没有通过实际章节 `翻译` 入口、选页后运行；Reader “下一页”也没有翻页后的 Page 2 证据。AC2 不能判 PASS。请用户基于本独立定性，裁决是否另立“侧栏直达工作台列表不刷新”产品缺陷 Task，以及 P19 是否只能按限制收口；本 Review 不替用户作该裁决。
2. **P1 AC3 失败**：合成 OS 路径实际由通用 Settings API 返回到 WebView，且错误投影尚有未验证类别；不得按 AC3 PASS 关闭。
3. **P1 AC6 未闭环**：新证据 pin、manifest、资源盘点、closeout 和 Handoff/状态叙述未同步；不能作为已完成交付关闭。

## 遗留项

- **P2 AC4 runner 判据**：固定 head 211 的 `PAGE_CHANGED` 对比脆弱，虽不推翻已观察到的禁用态，但运行结果仍是 exit 1；应以新判据运行一次并保存匹配源码版本的 metadata/trace。
- **P2 AC2 runner 选择器**：选择文件夹后应重新获取 UIA dialog 树；0051 的 0/2 选择失败是运行器问题。新三轮已满足 R3-004 的归档完整性，旧 run2..12 留作不完整历史证据。
- 本 Review 未删除任何 TEMP 根，资源处置应等正式 closeout。

## 与 Codex R3 的差异

- R3-001：从“导入未完成”推进到 0047 的 ①②③ PASS；Run/Export 仍未验证，且 Reader 下一页未证明。
- R3-002：全域扫描现已并入 main，但扫描发现设置 OS 路径回显，故证据交付不等于 AC3 PASS。
- R3-003：R1 Review 已入库，10/10 磁盘 hash 匹配；但 r1 commit 空、其余 commit 短、r2 仍 dirty，且新证据/manifest/closeout/Handoff 未闭环。
- R3-004：新 AC2/AC4 三轮原始产物补齐；旧目录不是全部“仅 app 日志”——run2..9 有 trace，run10..12 才只有 app stdout/stderr。
- R3-005：目录拒覆写与断言非零基建已具备；211 上 AC4 Pane 判据仍造成 9 个 runner FAIL。1a5 的后续修改未在本 Review 内验证。
- R3-006：仍是 Codex 治理项；本轮未修改上游 Task。

## 结论

`changes_requested`。AC2 需要按真实章节上下文路径完成 GUI 验收，或等待用户授权限制收口；AC3 的路径回显反例未解决；AC6 交付闭环未完成。固定 head 211 不能批准集成或关闭。当前 Task/STATUS 的 `status` 未修改。

