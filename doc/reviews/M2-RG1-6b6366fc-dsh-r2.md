decision: **changes_requested**

---

## 1. 方法与边界

- **严格只读**：全程未执行任何 shell/git/构建/验收命令，未写入任何文件；全部结论来自 `read` / `glob` / `grep` 读取仓库文件，证据以 `path:line` 给出。
- **复核基准**：`doc/reviews/M2-RG1-a1100d75-dsh-r1.md`（r1，1×P1、3×P2、8×P3）全文已读；被审 tip 为工作区实际内容（`raw/rg1-final-scope-audit-r2.log:3,56-62` 给出终 tip 内容头 = 5 个 M 文件 + 该日志本身）。
- **未采信 Owner 自述**：v2 全部数字、场景集合、CW0/CW1/CW2/DC1a/DC1b 断言形态、`pids_of` 退化路径、注册表快照、v1 存档真实性均由我逐条从 raw artifact 重算。
- **本次新增的独立反证（关键）**：`timed_app_cold_start` 的 `round_env` **没有** pin `NEWMANGA_DATA_ROOT`（`packaging/release-gate/run_release_gate.py:472-481`；全文件 `NEWMANGA_DATA_ROOT` 仅 6 处命中：`:180`(清除) / `:409` / `:445` / `:658` / `:702` / `:802`，**无一处在该函数内**），而 7 处 release evidence/文档声明已 pin。详见 P1-1(N)。
- **`not_verified` 清单（各附集成方一条闭合命令；本沙箱只读，无法执行 git）**：
  1. 终 tip 上 `git diff --check` 的字面 EXIT → `git diff --check 875eb818..6b6366fc; echo EXIT=$?`（我在可读文本上已反证：`verification/M2-RG1/**`、`doc/tasks/M2-RG1.md`、`doc/handoffs/M2-RG1-a1100d75.md` 的 `[ \t]+$` 零命中）。
  2. `05a8f93a` / `6b6366fc` 各自文件集（范围逐 commit 隔离）→ `git diff --name-status 875eb818..05a8f93a; git diff --name-status 05a8f93a..6b6366fc`。
  3. P3-1「仅注释行」→ `git diff a1100d75..05a8f93a -- apps/desktop/src-tauri/src/main.rs apps/desktop/src-tauri/src/core_bridge.rs`（期望仅 `//` 行）。
  4. P3-3「`rg1-scope-audit.log` 自首次入库即无行尾空白且从未修改」→ `git log --oneline -- verification/M2-RG1/raw/rg1-scope-audit.log`，再 `git show --check --stat <首个含该文件的 commit>`。
  5. installer 当前字节哈希（r1 not_verified #3 仍未闭）→ `Get-FileHash apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe -Algorithm SHA256`（期望 `d222073b…`）。
  6. 交付后工作区干净度 → `git status --porcelain`（期望空输出）。
  7. 提交版 runner 是否真无该 pin（P1-1(N) 自证）→ `git show 05a8f93a:packaging/release-gate/run_release_gate.py | Select-String -Context 0,10 "def timed_app_cold_start"`。

---

## 2. 1–8 逐项判定表

| # | 复核项 | verdict | 证据（path:line） |
|---|---|---|---|
| 1 | **P1-1 闭合质量**：三处措辞一致且如实 | **verified** | `verification/M2-RG1/verification-results.md:36`、`verification/M2-RG1/raw/README.md:17`、`doc/handoffs/M2-RG1-a1100d75.md:56` 三处均为「首跑 FAIL 被复跑 stdout 重定向覆盖、从未入库、仅文字披露、不作伪造补充」；我独立 grep `MISCONFIGURED`：全 `verification/M2-RG1/**` 仅 2 处命中且都是上述披露文本本身，transcript 零命中；`raw/rg1-gate-run.log:1` 头为 v2 单跑（`@ HEAD=e218cc6533…`）、`:8-53` 仅一次 PASS、`:54` `EXIT=0`。**无虚构 transcript** |
| 1b | **集成方初查的重复条目** | **确认成立（编辑引入）** | `verification/M2-RG1/verification-results.md:34` 与 `:35` **逐字相同**（均为「2. **warn 文件布局**…」），序号重复为两个「2」，其后 3–7 顺延；非内容错误，属返修重写时的复制残留 → P3-1(N) |
| 2 | **P2-1 闭合质量**（重点） | **verified（含 2 处 P3 级注记缺口）** | 双类名落实：`run_release_gate.py:117` `CONSOLE_WINDOW_CLASSES=("ConsoleWindowClass","CASCADIA_HOSTING_WINDOW_CLASS")`，命中判定 `:246-252`（`:262` 亦排除双类）；**阳性对照断言非恒真**：`:600-647`，返回 `bool(scan_ok and len(hits)>=1)`（`:647`），命中 0 ⇒ FAIL，`:1103-1105` 以 `pass_or` 落 `RG1-CW0-positive-control-hits-console`；载体记载一致：`:623` `creationflags=0x00000010 # CREATE_NEW_CONSOLE — deliberately no CREATE_NO_WINDOW`（docstring `:608-616` 记 `cmd` 载体 125 无窗口的选型理由）；**静默退化已消除**：`:292-306` 解析失败返回 `None`→`:573-574` `scan_ok=False`→`:533-544` CW1 断言 `not hits and alive_through_hold and scan_ok and sidecar_pids_seen>=1`，`:587-597` `wait_sidecars_reaped` 不把失败当收割证据；注册表入 gate.json：`:269-289`/`:994` → `raw/rg1-gate.json:78-82` 双 null + `:83-86` 类名清单；CW1/CW2 v2 数据与文档一致：`:397-419`/`:449-471`/`:501-523`（三轮 `hits:[]`、`app_alive_through_hold:true`、`scan_ok:true`、`sidecar_pids_seen:2`：host_bridge+core_service）、`:423-429`/`:475-481`/`:527-533`（CW2 `hits:[]`、`sidecars_reaped:true`）；CW0 实据 `:354-377`（1 命中、`CASCADIA…`、hwnd 9571146、pid 25252、title=powershell.exe 路径、visible）。**缺口**：CW0 未记属主镜像名（`WindowsTerminal.exe` 仅见文档）；`packaging/release-gate/README.md:14` 称边界「disclosed in code + gate.json」，gate.json 只含类名清单+注册表+attribution 串，无边界文字 → P3-5(N) |
| 3 | **P2-2 闭合质量** | **partially_verified** | 历史注记已落 ✓：`verification-results.md:21`（「该区间在 `a1100d75` 时点（规范化前）EXIT=2…自 `b38a646c` 起 EXIT=0」）、`doc/tasks/M2-RG1.md:87`、`raw/rg1-final-scope-audit-r2.log:54`；反证 artifact 齐备 ✓：`raw/rg1-scope-audit.log:29-36`（`875eb818..HEAD`=a1100d75 时 EXIT=2、3 处 trailing whitespace）、`raw/rg1-final-scope-audit-r2.log:49,51-52,65-66`（working tree 与 `05a8f93a` 均 EXIT=0）。**但 r1 要求的「显式写成终 tip 字面量」未达成**：`doc/tasks/M2-RG1.md:87` 写成 `875eb818..05a8f93a7a96…`**（含 bookkeeping 终 tip）**——`05a8f93a` 恰恰**不含** bookkeeping commit，属自相矛盾；`doc/tasks/M2-RG1.md:117` 与 `verification-results.md:21` 用 `<终 tip>`/`<最终返修 tip>` 占位符；全仓 grep `6b6366fc` **零命中**，终 tip 哈希从未落字 → P2-1(N) |
| 4 | **P2-3 闭合质量** | **partially_verified（含 1×P1）** | 取证 artifact 存在且论证自洽 ✓：`raw/rg1-localappdata-newmanga-forensics.log:7`（目录节点 mtime 2026-09-29 12:50:09，与 run1 时间窗一致）、`:9-10`（library.db 303104 B 与 managed 树停留在 2026-09-26）、`:13-14`（`find -type f -newer` 无输出）——「无持久新文件、无内容写入」结论成立，且**诚实披露**唯一痕迹与 SQLite 瞬态 WAL/shm 解释；safety 论证改写 ✓：`verification-results.md:37` 前段、`raw/README.md:35-43`、`packaging/release-gate/README.md:35-42` 均正确表述「APPDATA pinning + host 侧派生并显式传递 NEWMANGA_DATA_ROOT + core_service 兜底 %LOCALAPPDATA%\New Manga」，与代码对得上（`main.rs:315-319` `packaged_user_root()`=APPDATA 派生；`main.rs:446-452` data_root；`library_bridge.rs:149-151` 显式传；`core_assembly.py:562-568` 兜底根）。**但 (b) 项被声称为已完成而代码中不存在** → P1-1(N) |
| 5 | **P3-1..P3-8 逐条** | 6 闭 / 2 半闭 | 见下表 5a |
| 6 | **v2 数字一致性** | **verified** | 25/25 逐条点数吻合：grep `"id": "RG1-` 在 `raw/rg1-gate.json` = **25** 条（`:129-691`），场景 ID 集合 = 旧 23（`raw/rg1-gate-run1.json:120-565` 同为可点数 23 条）∪ {`RG1-CW0`、拆分的 `RG1-DC1a`+`RG1-DC1b`} − {`RG1-DC1`}，verdict `PASS`（`:126`）；CW0 hit=1（`:354-377`）；DC1b `books_count=1` + `expect_books_min=1` + 8 键齐（`:226-265`，键集与 `run_release_gate.py:726` 一致）；三层基线 v2：app `46.9/49.9/160.2`（`:89-100`）、core `237.6/247.6/251.4`（`:101-111`）、ac1 `267.2/267.6/268.5`（`:112-122`）与 `verification-results.md:18`、`doc/tasks/M2-RG1.md:65-68` 一致；M2-AC5 回归 v2：`raw/rg1-m2ac5-cleanstart-gate.json:4,12`（同 installer、PASS）+ `raw/rg1-m2ac5-cleanstart-runner.log:1`（v2 复跑头）+ 25 条 `CS-*` 场景；cargo r2：`raw/rg1-baseline-cargo-test-r2.log:1,64,66`（`@HEAD=e218cc65`、38 passed/0 failed/1 ignored、EXIT=0）；installer 未重建有独立反证：**v1 存档与 v2 的 sha256 同为 `d222073b…`**（`rg1-gate-run1.json:74` = `rg1-gate.json:74`）→ 期间无重建。**唯一措辞瑕疵**：「未重装」（`Handoff:71`、`verification-results.md:43`）与 runner 每轮执行 `RG1-I1-silent-install`（`rg1-gate.json:153-157`）字面冲突 → P3-7(N) |
| 7 | **范围（含禁改路径与 M2-AC5 零提交）** | **verified（1 项 not_verified）** | 全区间 name-status（`raw/rg1-final-scope-audit-r2.log:6-49`）= 4 个条件允许 rs + `packaging/m2ac5/core_sidecar.spec`(注释) + `packaging/release-gate/**` + `verification/M2-RG1/**` + `doc/tasks`、`doc/handoffs`；**禁改路径零命中**：无 `src/**`、`requirements.txt`、`doc/contracts/**`、`apps/desktop/frontend/**`、`run_clean_start_e2e.py`、`tauri.conf.json`、`verification/M2-AC5/**`；M2-AC5 零提交另有反证：`raw/rg1-scope-audit.log:39-52` 的 transient tauri 生成文件（`gen/schemas`、`permissions/autogenerated`）在终态 name-status/status 中全部消失 = 净零；`05a8f93a`+`6b6366fc` 逐 commit 文件集需 git 复核 → not_verified #2。**注意**：`doc/reviews/M2-RG1-a1100d75-dsh-r1.md` 由集成方在 `e218cc65` 导入（r1 §5 第 7 条指令 + `doc/tasks/M2-RG1.md:123`），属**已授权的集成方行为**，可接受；但 Task `:96` 允许路径块未列入 `doc/reviews/**`，建议补齐（P3-8(N)，bookkeeping 级） |
| 8 | **v1→v2 证据链完整性** | **verified** | `raw/rg1-gate-run1.json` 确为 v1 快照，且**结构层面自证非伪造**：①23 条场景含单条 `RG1-DC1-core-service-ping-listbooks`（`:203`）、无 CW0；②旧计时 `46.0/48.2/157.1`、`239.1/240.5/240.9`、`266.5/268.2/280.1`（`:81-113`）与 v2 不同；③`environment` 段**无** `console_delegation_registry` / `console_window_classes_observed`（`:6-78`）= 加固前 runner 的字段集；④`lab` 路径不同（`:79` vs `rg1-gate.json:88`）。v2 侧引用对照充分：`verification-results.md:10,18,43`、`raw/README.md:6,19`、`doc/tasks/M2-RG1.md:68,86,115`、`release-875eb818.md:11-12`、`Handoff:84` |

### 5a. P3 逐条

| P3 | 位置 | 现状 verdict | 依据 |
|---|---|---|---|
| P3-1 注释更新 | `main.rs:23-27`、`core_bridge.rs:111-114` | **verified**（内容正确；「仅注释行」git 层未独立复核→not_verified #3） | `main.rs:5` 属性仍在最前且 `cfg_attr(not(debug_assertions)…)`；`main.rs:23-27` 已改为「dev 保留 / release GUI + sidecar CREATE_NO_WINDOW / stdio 语义不变」；`core_bridge.rs:111-114` 已改为「builder chain 重写为 `cmd` 绑定以插入 flag，stdio/spawn 等价」 |
| P3-2 README warn=1 / 删 RG1-Z1 | `packaging/release-gate/README.md:17` | **partially_verified** | README 已正确（「the ONE merged PyInstaller warn file」、无 RG1-Z1 引用），但**同一交付物的 runner docstring 未同步**：`run_release_gate.py:45-46` 仍写「the four PyInstaller warn files are copied into raw/」，`:53` 仍写「the runner-side proof is RG1-Z1」（gate.json 25 场景中无 RG1-Z1，且 gate 内也无该 APPDATA 断言场景）→ P3-2(N) |
| P3-3 行尾规范化权威清单 | `verification-results.md:39-42`、`raw/README.md:44-59` | **verified（10 份成立）** | 逐文件名两级清单+更正说明齐备；10 的**更正依据成立**：`raw/rg1-scope-audit.log:30-36` 的 EXIT=2 只列 3 份（diff/gate-run/os-detail），`:63` 显示 `rg1-scope-audit.log` 当时仍未跟踪，故不可能进入该 3 份；第二批 7 份为 CRLF→LF（不影响 `--check`），已如实分列；「从未被修改」的 git 历史子断言→not_verified #4 |
| P3-4 内存口径 | `verification-results.md:20` ✓ vs `:9` ✗ | **partially_verified** | `:20` 已统一为 `33.98 GB（33981165568 B）`，与 `raw/rg1-os-detail.log:22`（33981165568）一致；但 `verification-results.md:9` 仍写「32 GB」，P3-4 未全闭 → P3-3(N) |
| P3-5 DC1 seed 强化 | `run_release_gate.py:650-677,1053-1068` | **verified** | `RG1-DC1a`：`seed_fixture`(`M2AC1_TEST_MODE=1`)+shutdown（`gate.json:212-223`）；`RG1-DC1b`：`expect_books_min=1`（`:695,730`）→ `books_ok` 需 `len>=1` 且逐行 8 键（`:728-734`），空列表恒真已消除；实据 `books_count:1`、8 键全（`:251-262`） |
| P3-6 NSIS 残留披露 | `verification-results.md:38`、`Handoff:59`、`doc/tasks/M2-RG1.md:107` | **verified** | per-user 卸载项/开始菜单快捷方式可能残留 + `taskkill /F /IM` 宿主级杀进程 + 卸载链路 NOT_RUN，均已落字并登记候选 |
| P3-7 `__pycache__` 清理 | `packaging/release-gate/**` | **verified** | glob 该目录仅 `run_release_gate.py` + `README.md`，无 `__pycache__/`、无 `.pyc` |
| P3-8 debug 注记 | `doc/tasks/M2-RG1.md:53`、`verification-results.md:17` | **verified** | 两处均注明「`CREATE_NO_WINDOW` 仅按 `cfg(windows)` 门控 ⇒ Windows debug 构建下 sidecar 控制台窗口亦不再出现，stdio 语义不变」，与 `core_bridge.rs:134-139,169-174`、`ac1_bridge.rs:75-80`、`library_bridge.rs:153-158` 一致 |

---

## 3. 新问题分级

### P1（必须闭合方可 done）

**P1-1(N) release evidence 关于 `timed_app_cold_start` 行为的 7 处声明与所审代码不符（证据完整性）**
- 位置（声明侧）：`verification/M2-RG1/verification-results.md:18`、`:37`；`doc/tasks/M2-RG1.md:65`；`doc/handoffs/M2-RG1-a1100d75.md:57`、`:80`；`verification/M2-RG1/raw/README.md:39-40`；`packaging/release-gate/README.md:41-42`。
- 事实（代码侧）：`packaging/release-gate/run_release_gate.py:472-481` 仅 `pin_appdata(env, roaming)` + `WEBVIEW2_USER_DATA_FOLDER`，**没有** `NEWMANGA_DATA_ROOT`；全文件该变量仅 6 处命中（`:180` 由 `purged_environment()` 显式清除、`:409`/`:445`/`:658`/`:702`/`:802` 分别在 core/ac1/seed/DC1b/DC3 探针内），即 app 轮**不可能**继承到 lab 值。
- 影响：**不影响 Gate 结论与产品安全**——packaged app 的 `user_root` 由 `APPDATA` 派生（`main.rs:315-319,366-367`）且 data_root 逐级显式下传（`main.rs:446-452`；`library_bridge.rs:149-151`），因此 APPDATA pin 已足以隔离；但「额外逐轮 pin `NEWMANGA_DATA_ROOT`，堵住兜底路径」这条**被写进 5 份 release evidence 的加固声明是假的**，与 r1 P1-1 同属「证据文件声明与可验证事实不符」。次级风险：若 Owner 主张「实测 runner 与提交 runner 不同」，则升级为「提交物≠被执行物」，更严重。
- 建议（二选一）：**(a) 推荐、无需重建无需重跑**——把这 7 处改为如实措辞：「app 轮的零触碰仅由 APPDATA pin + host 侧 `packaged_user_root()` 派生保证；`NEWMANGA_DATA_ROOT` 仅在 core/ac1/seed/DC1b/DC3 全部探针内显式 pin（app 轮不 pin）」，并从 r1 P2-3 闭合表删除「显式 pin」字样；**(b)** 真的加一行 `round_env["NEWMANGA_DATA_ROOT"] = str(lab_round / "data-root")`，但此时提交的 runner 将不再等于产生 v2 gate.json 的 runner，必须重跑 gate 并重存档（本轮不建议）。

### P2（必须闭合方可 done）

**P2-1(N) r1 P2-2 只半闭：审计范围未落成终 tip 字面量，且 `doc/tasks/M2-RG1.md:87` 自相矛盾**
- 位置：`doc/tasks/M2-RG1.md:87`（`875eb818..05a8f93a7a96…`（含 bookkeeping 终 tip）——`05a8f93a` 不含 bookkeeping commit）、`:117`（`<终 tip>` 占位符）、`verification/M2-RG1/verification-results.md:21`（`<最终返修 tip>` 占位符）；全仓无 `6b6366fc`。
- 影响：r1 P2-2 的实质要求（把范围显式写成**终 tip**并保留历史注记）只完成了后半句；读者无法从任一交付文件复原「EXIT=0 成立在哪两个 commit 之间」。
- 建议：在 `doc/tasks/M2-RG1.md:87,117` 与 `verification-results.md:21` 写入**该时点真实终 tip 哈希**；修正后跑一次 `git diff --check 875eb818..<修正后 tip>; echo EXIT=$?` 并把该行原文贴入 `verification-results.md` AC6 行（不再新建 artifact 文件，避免「新文件又改变 tip」的循环）。

### P3（可由集成方落字闭合）

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P3-1(N) | `verification-results.md:34`,`:35` | 披露条目 #2 逐字重复（两个「2.」，编号顺延错乱） | 删除其中一行，保持 1–7 连续编号 |
| P3-2(N) | `run_release_gate.py:45-46`,`:53` | docstring 仍称「four PyInstaller warn files」且把 `RG1-Z1` 当作既有证明场景（gate 内不存在） | 改为「one merged warn-<spec>.txt」；把 `RG1-Z1` 改为「APPDATA 逐进程 pin（无独立场景 ID）」或删除该句 |
| P3-3(N) | `verification-results.md:9` | 仍写「32 GB」，与 `:20` 的 `33.98 GB（33981165568 B）` 冲突（r1 P3-4 未全闭） | 改为 `33.98 GB（33981165568 B）` |
| P3-4(N) | `raw/rg1-localappdata-newmanga-forensics.log:1-14`、`raw/rg1-final-scope-audit-r2.log:2-3` | 两份新增人工日志缺 `HEAD=<hash>` 纪律行（Task `:86` 的例外清单只覆盖 10 份规范化与 M2-AC5 runner 格式）；且 forensics `:14` 同时记 `EXIT=0` 又注「1 = no files newer」，exit 语义自相矛盾 | 补 `HEAD=<hash>` 行；把 `:14` 改为「`find` 无输出（无 mtime 晚于 12:33 的文件），EXIT=0」 |
| P3-5(N) | `rg1-gate.json:354-377`、`packaging/release-gate/README.md:14` | CW0 未记属主镜像名（`WindowsTerminal.exe` 仅见文档）；README 声称边界「disclosed in code + gate.json」，gate.json 内并无边界文字 | 若再做一次 v3 取证，把属主 `ImageName` 记入 `hits[]`（pid→镜像名），或在 README 改为「disclosed in code + registry snapshot」 |
| P3-6(N) | `doc/handoffs/M2-RG1-a1100d75.md:24-29,36-37` | 顶部表格仍为 v1 计时并引用 pre-rework cargo 日志，无内联 v1 标注（虽 `doc/tasks/M2-RG1.md:121` 声明为「初交付版 + r1 返修节」） | 在表头或 AC3/AC6 行加「v1 初交付数值（仅存档对照）」标注 |
| P3-7(N) | `Handoff:71`、`verification-results.md:43` | 「未重新构建、未重装」与 runner 实际每轮执行 `RG1-I1-silent-install`（`rg1-gate.json:153-157`）字面冲突 | 改为「未更换 installer 二进制（sha256 不变）」，重装动作由 runner 自证 |
| P3-8(N) | `doc/tasks/M2-RG1.md:96` | 无条件允许路径未列 `doc/reviews/**`，而 r1 报告实际在本分支（`e218cc65` 集成方导入，已授权） | 在允许路径块补 `doc/reviews/M2-RG1-*.md（集成方导入）` |

---

## 4. 是否达到可集成标准（可否 merge + done）

**未达到；当前不可 merge + done（`changes_requested`）。**

- 可以确认的部分：r1 的 **P1-1 真闭**（三处一致且如实，`grep` 反证 transcript 确不存在）、**P2-1 真闭且加固到位**（双类名、非恒真阳性对照 CW0 命中 1、`pids_of` 不再静默退化、注册表入 gate.json、CW1 断言存活+sidecar pid）、P3 中 6 项闭/基本闭；v2 的 25/25、DC1a/b、三层计时、M2-AC5 25/25、`d222073b…` 未重建，全部可逐条重算，**无虚增、无 P0、产品侧无正确性/安全缺口**。
- 但 r1 的 **P2-2 未全闭**（终 tip 哈希从未落字，`doc/tasks/M2-RG1.md:87` 自相矛盾），且返修**新引入 1 条 P1 级不实声明**（7 处文档称 `timed_app_cold_start` 已 pin `NEWMANGA_DATA_ROOT`，`run_release_gate.py:472-481` 无此代码）。按本项目「P0/P1/P2 必闭方可 done」规则，这两项必须先行闭合。
- 闭合成本极低：**纯文字修正（约 12 行）+ 一条 `git diff --check` 命令回贴，不需要改产品代码、不需要重建 installer、不需要重跑 gate**（若选 P1-1(N) 方案 (b) 加代码行，则反过来必须重跑 gate 并重存档，成本更高，不推荐）。

---

## 5. 可直接转发给 Codex（Integrator）的收口指令段

> **任务：M2-RG1（`agent/zcode/M2-RG1-release-gate` @ `G:/CODEX/New Manga.worktrees/M2-RG1-zcode`）r2 复核后的收口修正**
>
> 背景：DSH 非作者 r2 只读复核（报告即将入库，建议路径 `doc/reviews/M2-RG1-6b6366fc-dsh-r2.md` 或按修正后 tip 命名）结论 **`changes_requested`**。r1 的 P1-1、P2-1 判定**已真闭**；产品与 Gate 结论（25/25、`d222073b…`、M2-AC5 25/25、38+1/35/31）成立且可逐条重算。以下为**纯文字/证据修正，不需要改产品代码、不需要重建、不需要重跑 gate**：
>
> 1. **P1-1(N)（必闭，P1）——删除 7 处不实的 `NEWMANGA_DATA_ROOT` pin 声明**。被审代码 `packaging/release-gate/run_release_gate.py:472-481`（`timed_app_cold_start`）只 pin `APPDATA`，未 pin `NEWMANGA_DATA_ROOT`（全文件仅 `:180,409,445,658,702,802` 命中，均不在该函数）。请把 `verification/M2-RG1/verification-results.md:18`、`:37`、`doc/tasks/M2-RG1.md:65`、`doc/handoffs/M2-RG1-a1100d75.md:57`、`:80`、`verification/M2-RG1/raw/README.md:39-40`、`packaging/release-gate/README.md:41-42` 统一改写为：「零触碰由 APPDATA 逐轮 pin + host 侧 `packaged_user_root()`（`main.rs:315-319,366-367`）派生并显式下传 data root（`main.rs:446-452`、`library_bridge.rs:149-151`）保证；`NEWMANGA_DATA_ROOT` 仅在 core/ac1/seed/DC1b/DC3 全部探针内显式 pin，app 轮不 pin」，并从 r1 P2-3 闭合表中删除「显式 pin」字样。**不要**为对齐文字而临时加代码行（那会使提交的 runner 不再等于产生 v2 gate.json 的 runner，须重跑 gate）。
> 2. **P2-1(N)（必闭，P2）——把审计范围写成终 tip 字面量**：`doc/tasks/M2-RG1.md:87` 现写 `875eb818..05a8f93a7a96…（含 bookkeeping 终 tip）` 属自相矛盾（`05a8f93a` 不含 bookkeeping commit）；`:117` 与 `verification/M2-RG1/verification-results.md:21` 仍是 `<终 tip>` 占位符，且全仓无 `6b6366fc`。请写入本次修正后的真实终 tip 哈希，保留「`a1100d75` 时点 EXIT=2（3 份 evidence 日志行尾空白）、自 `b38a646c` 起 EXIT=0」历史注记，并把 `git diff --check 875eb818..<修正后 tip>; echo EXIT=$?` 的原文贴入 `verification-results.md` AC6 行（不要新建 artifact 文件）。
> 3. **P3-1(N)**：`verification-results.md:34` 与 `:35` 逐字重复的披露 #2 删除一行，编号改回 1–7 连续。
> 4. **P3-2(N)**：`packaging/release-gate/run_release_gate.py:45-46`（"four PyInstaller warn files" 改为 "the one merged warn-<spec>.txt"）、`:53`（`RG1-Z1` 引用改写或删除，gate 内无该场景）。
> 5. **P3-3(N)**：`verification-results.md:9` 的「32 GB」改为「33.98 GB（33981165568 B）」，与 `:20`、`raw/rg1-os-detail.log:22` 统一。
> 6. **P3-4(N)**：给 `raw/rg1-localappdata-newmanga-forensics.log`、`raw/rg1-final-scope-audit-r2.log` 补 `HEAD=<hash>` 纪律行；把 forensics `:14` 改为「`find` 无输出（无 mtime 晚于 12:33 的文件），EXIT=0」。
> 7. **P3-6(N)/P3-7(N)/P3-8(N)**（可选同日落字）：Handoff `:24-29,36-37` 顶部表加「v1 初交付数值（仅存档对照）」标注；「未重新构建、未重装」改为「未更换 installer 二进制（sha256 `d222073b…` 不变），重装由 runner `RG1-I1` 自证」；Task `:96` 允许路径补 `doc/reviews/M2-RG1-*.md（集成方导入）`。
> 8. **闭合验证命令（请贴回结果）**：`git diff --check 875eb818..<修正后 tip>; echo EXIT=$?`（期望 EXIT=0）；`git show 05a8f93a:packaging/release-gate/run_release_gate.py | Select-String -Context 0,10 "def timed_app_cold_start"`（自证无 pin）；`git diff --name-status 875eb818..<修正后 tip>`（期望全落允许路径、无禁改路径、无 `verification/M2-AC5/**`）；`Get-FileHash apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe -Algorithm SHA256`（期望 `d222073b…`）；`git status --porcelain`（期望空）。
> 9. 完成后把 r2 报告落到 `doc/reviews/`（命名按修正后 tip），更新 `doc/tasks/M2-RG1.md` 的 `review`/`dispatch_state` 与 `doc/handoffs/M2-RG1-*.md` 的 r2 节；`doc/STATUS.md` 终态由集成方按协议同步。因本轮为文字修正，无需再次发起完整重建类复核；建议集成方按第 8 条命令自证后直接合并。
>
> **下一步建议（给编排方）**：由 ZCode（Owner）执行上述 1–7，Codex（Integrator）执行第 8 条自证并合入；无需下一步其他 Agent 操作。