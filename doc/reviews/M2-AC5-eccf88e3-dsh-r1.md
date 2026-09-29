# M2-AC5 独立非作者 Review（DeepSeek Harness）

decision: **approved_with_conditions**

审查方式声明：本次为严格只读静态审查——未执行任何命令（沙箱拒绝命令执行），未写入任何文件。因此凡需要 `git diff/status/log` 才能定论的比对项（base↔head、name-status、diff --check、工作区干净）一律标 `not_verified`，**不以 Owner 自述代替证据**；这些项均已给出可由 Integrator 一条命令闭合的具体条件。

---

## A–H 判定表

| 项 | 判定 | 依据（path:line） |
|---|---|---|
| **A** AC2 fail-closed 与 dev 零变化 | **partially_verified** | ①判据逻辑 verified：`resolve_packaged_sidecar_dir` 显式优先、裸启动以 `host_bridge.exe` 存在为闸、`exe_dir=None` 永不 packaged（`main.rs:283-299`），判定输入取自 `current_exe()`（`main.rs:334-341`）。②**dev 误判风险 verified（低）**：`M2RC1_SRC_ROOT` 存在即短路（`main.rs:291-297`），现有 dev/runner 环境全带 `M2RC1_*`；4 个新单测全部显式传参、不读环境（`main.rs:1238-1299`），不受 ambient env 影响。③缺失分支在 `Command` 前 typed 失败 verified（`core_bridge.rs:146-148` 先 `is_file()` 返回，149 才 `Command::new`）。④绝不回落系统 python verified：packaged 三个分派点 Some 臂只指向 frozen exe（`main.rs:410-420/422-435/445-462`），dev 的 `python_exe/src_root` 在 Some 时置空且不在 Some 臂使用。⑤**dev spawn 与 base“逐字不变”not_verified**：无 `git diff` 落盘；且 Handoff 自述“两者共享 `adopt_child`”（Handoff:58-59），而 `adopt_child` 全仓库仅出现于 `core_bridge.rs:132/158/161`——若为本次抽取，则 dev spawn 体内联 `take()` 已被重构，**字节级**断言不成立（行为等价）。⑥4 单测钉死范围 partially：解析优先级矩阵 3 测充分，**缺失分支仅 1 测**（`main.rs:1286-1299`），Handoff:42 的“4 单测钉死缺失分支”措辞不准。 |
| **B** AC3 证据链 | **partially_verified** | ①PATH 剔除断言 partially：`where python` exit=1（`verification/M2-AC5/raw/cleanstart-final.log:14`、`raw/cleanstart-gate.json:9-26`）只证明“PATH 不可解析”；真正口径由净化 PATH + frozen exe 全流程服务共同支撑，且已在 Task:43/Handoff:83-85/verification-results:6 如实标注 host-simulation。②三模式参数与结果自洽 verified：`probe_env/ac1_env/production_env`（`packaging/m2ac5/run_clean_start_e2e.py:286-321`）、三份 stdout `exit=0`、gate 20/20（`raw/cleanstart-gate.json:6,7-221`）、13/13 与 PID/2 页/1122 bytes/163 文件全部对得上。③**重启语义 verified**：desktop pid 4540→43864 取自 runner 自身 spawn 的 `proc.pid`（`run_clean_start_e2e.py:332,427`），core pid 39180→48160 为 Core 自报 `os.getpid()`（`apps/desktop/frontend/src/ac1/driver.ts:139,172`）；run1.saved 的页面 sha 在 run2.viewed/exported 复现，且与 M2-AC1 冻结证据逐字一致（`verification/M2-AC1/e2e-evidence/sample-a/run1.json:1`）。④**ListBooks 元素 not_verified**：production 真窗口确实隐式触发 `library_list_books`（`App.tsx:472` → `LibraryPanel.tsx:35-40` → packaged `core_service.exe`），但 gate **无任何 scenario 采集其结果**；唯一直接往返证据是预安装冒烟的 `core.ping`（`raw/sidecar-entries-smoke.log:15-18`），非安装态、且非 ListBooks。⑤裸启动启发式未被端到端覆盖：三模式均显式置 `M2RC1_PACKAGED=1`（`run_clean_start_e2e.py:288/301/319`）。 |
| **C** PySide6 进闭包裁决 | **verified（裁决与披露），含 2 项披露缺口** | ①硬依赖代码证据 verified：`assemble_acceptance_core` docstring 明示 "Requires PySide6" 并函数内 `from PySide6.QtGui import QGuiApplication`（`src/bootstrap/acceptance_bridge.py:164-173`），在 `M2AC1_TEST_MODE=1` 时由 `main()` 调用（`:615-616`）。②偏差已如实披露 verified：Task:34 释放注记 + 风险裁决点（Task:64）、Handoff:46-51、`packaging/m2ac5/core_sidecar.spec:15-25`、`requirements-build.txt:11-18`、verification-results:21。③不触碰“产品运行时依赖清单零改动” verified（内容层面）：`requirements.txt:1-2` 已 pin 同版本，`requirements-build.txt:25-26` 一致，无需改动；**但“零改动”的 diff 证据缺失**。④**许可影响未披露**（全篇无 LGPLv3/GPL 义务讨论）；**体积影响未量化**（161 项 sidecar 资产中约 150 项为 PySide6/shiboken，仅给安装包 26.62 MiB）。 |
| **D** AC1 可复现 | **partially_verified（核心断言被自有证据否证）** | ①**“157 文件 hash 全同”不成立**：`raw/ac1-repro-sidecar-diff.txt:14` 与 `:18` 显示 `_internal/base_library.zip` runA `CA06B78B…` vs runB `98ECF8B4…` 不同；两份 hash 清单同为 161 行、文件集合相同（`raw/ac1-repro-sidecar-runA.txt:1-161`、`runB.txt:155-161`）→ 实为 **156/157 相同，5 个文件不同（4 入口壳 + base_library.zip）**。Task:41、Handoff:30、verification-results:12、checkpoint:14 四处表述均需更正。②时间戳差异解释 partially：4 入口壳差异（PyInstaller PKG/PYZ 内嵌 timestamp）与 host exe/NSIS 差异（Rust 链接/NSIS 打包）解释合理，**但摘要未涵盖 base_library.zip**，缺该文件的差异归类。③构建命令/输入 hash partially：frontend dist(2)+sidecar 输出(161) 有 hash；`raw/ac1-input-hashes-build1.txt:1,167` 记录的 HEAD=71b0e9aa **早于 `packaging/m2ac5/**` 的提交（eccf88e3）**，spec/entries/src 闭包无实际 hash；`build_sidecar.ps1` 未被任何 tauri 构建钩子调用（`tauri.conf.json:6-8` 无 beforeBuildCommand），单独 `npx tauri build` 只打包既有 sidecar；且被两处引用的 `packaging/m2ac5/README.md` **不存在**（`build_sidecar.ps1:25`、`requirements-build.txt:6`）。 |
| **E** AC4 | **partially_verified** | ①数据根解析 verified：`%APPDATA%\com.newmanga.m2rc1.desktop\{derived,managed,catalog\catalog.sqlite,data}`，首启动 `create_dir_all`，显式 env 优先（`main.rs:305-309,356-396`）。②安装目录零变化 + 源 fixture 不变 verified：`run_clean_start_e2e.py:599-612`，gate `changed_entries: []`（CS-Z1）、`files: 4`（CS-Z2）。③进程零残留 partially verified：`tasklist /FO CSV /NH` 前缀匹配（`run_clean_start_e2e.py:354-368`），四 frozen exe 计数 0（CS-Z3）；`python.exe: 6` 为记录性观察且已如实说明。④**“不写源码树”无断言**：CS-Z2 只覆盖 lab 的 `probe/scope/derived`；且 `spawn_packaged` 不设 `current_dir`（`core_bridge.rs:149-156`），sidecar 继承宿主 cwd（与 dev 的 `src_root` 约定不一致）。⑤production 阶段直接 rmtree 宿主真实 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}`（`run_clean_start_e2e.py:493-503`），可用 `APPDATA=<lab>` 隔离（`main.rs:305-309` 正是读环境变量）。 |
| **F** 范围 | **partially_verified（git 侧全部无法静态确认）** | ①`git diff --name-status` 对照两级允许路径 **not_verified**：证据包内无该原始日志，仅 checkpoint:17-19、Handoff:95-97、verification-results:16 的散文断言。②`src/**` 零改动 **not_verified**（同上）；间接支持：pytest 35 / vitest 31 不回退（`raw/baseline-pytest-m2-acceptance.log:4`、`raw/baseline-vitest-run.log:15`），`packaging/m2ac5/entries/*.py` 以 import 复用 `src` 而非复制。③gen/schemas+permissions 还原 **not_verified**（无 `git status` 落盘）。④`requirements.txt` 零改动 verified-by-content（见 C），diff 证据缺失。⑤构建产物 gitignored **verified**：`apps/desktop/.gitignore:1-3` 覆盖 `src-tauri/target/`、`frontend/dist/`、`node_modules/`；根 `.gitignore:1-2` 覆盖 `__pycache__/`、`*.py[cod]`（`packaging/m2ac5/__pycache__/*.pyc` 存在但被忽略）。 |
| **G** 证据纪律 | **partially_verified** | ①27 份 raw 数量 ✓（raw/ 27 文件 + README.md）。②shell/解释器头 + 固定 HEAD + EXIT partially：`baseline-*` ✓（头+HEAD+EXIT）、`sidecar-entries-smoke.log` ✓、`artifact-inventory-final.txt` ✓；**`tauri-build-run1.log`/`run2.log` 无 shell 头/HEAD/EXIT**（`run2.log:1-60` 以 npm notice 起、以 bundle 行止）而 `raw/README.md:23` 称“均 EXIT=0”；**`cleanstart-final.log`/`run5.log` 无头/EXIT** 而 `raw/README.md:41` 称 EXIT=0；`cleanstart-gate.json` 为数据件。→ `raw/README.md:3` “全部日志带 shell/解释器头与 EXIT”不成立（约 5 份）。③`diff --check` 区间 **not_verified**；`raw/README.md:5-8` 自述为满足该 gate 对 5 份日志做了 CRLF→LF/去尾空白规范化（已如实披露，但该 gate 依赖对证据的事后清洗）。④数字一致性 partially：一致项——cargo 38+1（`raw/baseline-cargo-test.log:63`）、pytest 35、vitest 31、probe 13、20 场景、PIDs、163 文件、26.62 MiB、1122 bytes；**不一致项**——“剔除 **10** 条目”（Handoff:32、verification-results:14）vs gate 实际 **11** 条（`raw/cleanstart-gate.json:13-25`）。 |
| **H** 遗留登记 | **partially_verified（主要项完整，漏项见 P3）** | 真干净机 NOT_RUN ✓（Task:65、Handoff:83-84、verification-results:47、`run_clean_start_e2e.py:20-22`）；NSIS 卸载未测 ✓（Handoff:85、verification-results:48，AC 未要求）；bit-for-bit 候选 ✓（Handoff:86-88、verification-results:50）；PDF/MOBI 闭包候选 ✓（Handoff:89-90、verification-results:49）**但“PyInstaller warn 留痕”无工件入库**，且 spec 四段 Analysis 共用同一 warn 路径（`raw/pyinstaller-build-closure-pyside6.log:44,103,164,226`）→ 只有最后入口的 warning 存活，`core_sidecar.spec:28-29` 的“must fail at build analysis time”与 PyInstaller 实际行为（写 warning、不失败）不符。 **未登记**：Qt/PySide6 许可与体积影响；安装目录多出第 4 个可执行 `catalog_loader.exe`（产品分发面增项）；Qt 字体缺失告警（`raw/cleanstart-ac1-run1-stdout.log:4-5`）。 |

---

## 新问题分级

**P0：none**
**P1：none**

核心实现（packaged 判据、fail-closed、三 channel 分派、resources 路径映射）经静态审查自洽，未发现可致数据损坏/错误 exe/系统 python 回落的缺陷。

**P2（5 项，须闭合后才可 `done`）**
1. **AC1 核心断言与自有证据矛盾**：`raw/ac1-repro-sidecar-diff.txt:14,18` 证明 `_internal/base_library.zip` 两次构建 hash 不同，而 Task:41 / Handoff:30 / verification-results:12 / checkpoint:14 均写“157 文件 hash 全同”。须更正为 156/157，并补该文件的差异归类。
2. **AC3 “ListBooks workflow 返回”无断言**：production 阶段虽隐式走通 `library_list_books`（`App.tsx:472`+`LibraryPanel.tsx:35-40`+packaged `core_service.exe`），但 gate 无观测；直接往返证据仅 `raw/sidecar-entries-smoke.log:15-18` 的 `core.ping`（非安装态）。
3. **`packaging/m2ac5/README.md` 缺失**，而 `build_sidecar.ps1:25` 与 `requirements-build.txt:6` 均指向它——AC1“构建命令留痕”缺构建 venv 创建流程。
4. **runner 破坏宿主真实用户数据**：`run_clean_start_e2e.py:493-503` 无条件 rmtree `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}`；`packaged_user_root()` 读环境变量（`main.rs:305-309`），本可用 `APPDATA=<lab>` 隔离。
5. **AC5 自检无原始痕迹**：`git diff --name-status 6f79c040..HEAD`、`git diff --check` 两项 AC5 硬 gate 只有 checkpoint:17-19 的散文，无日志入库。

**P3（按主题归并）**
1. **证据摘要精度**：`raw/README.md:3,23,41` 的“全部日志带头+EXIT”“tauri build 均 EXIT=0”“gate EXIT=0”与工件不符；Handoff:32/verification-results:14 的“10 条目”与 `raw/cleanstart-gate.json:13-25` 的 11 条不符；Handoff:42“4 单测钉死缺失分支”实为 1 测缺失 + 3 测矩阵。
2. **runner 未处理解码路径**：`run_clean_start_e2e.py:155-157` 的 `where host_bridge.exe` 缺 `encoding="mbcs"`，中文 locale 下抛未捕获 `UnicodeDecodeError`，污染 `raw/cleanstart-final.log:1-11` 与 run2-5 首行（因 `where` 的 GBK 错误信息被按 UTF-8 解码）；判定值不受影响（用 `returncode`），但日志首行为 traceback 且该解码路径未覆盖。
3. **fail-closed 覆盖面**：typed `PACKAGED_SIDECAR_MISSING` 只覆盖 `host_bridge`；`core_service.exe`/`acceptance_bridge.exe` 缺失是 `.expect` panic（`main.rs:421,431,458`），且文案仍写 “python core sidecar”。
4. **构建链脆弱性**：resources 源指向 `target/` 内部（`tauri.conf.json:30-32`），无 beforeBuildCommand，`cargo clean` 或忘记先跑 `build_sidecar.ps1` 会静默打包陈旧/缺件 sidecar（缺件时由 runner 的 CS-I1 兜底）。
5. **裸启动分支未端到端覆盖**：真实用户路径（双击安装后的 exe，无任何 `M2RC1_*`）仅单测覆盖（`main.rs:1253-1264`）。
6. **可移植性**：NSIS `/D=` 依赖无空格路径（`run_clean_start_e2e.py:183-191`，docstring:7-8 仅顺带提及，无 guard）；`install_dir` 固定不唯一（`:578`）；按子串 marker 净化 PATH 会误删含 "python/venv/conda" 的无关路径（fail-closed 方向正确）。
7. **测试设计**：AC4“不写源码树”无断言，且 `spawn_packaged` 不设 `current_dir`（`core_bridge.rs:149-156`），建议对齐 dev 约定设为 sidecar 目录；`main.rs:360-362` 的 `create_dir_all` 错误被 `let _` 吞掉。
8. **可追溯性**：`raw/cleanstart-gate.json:3` 只记 installer 路径不记 sha256，“被测=5410e29e” 需靠时间线 + `raw/ac1-repro-run2-hashes.txt:1` 交叉推断；首次 sidecar 构建输入未 commit-pinned（`raw/ac1-input-hashes-build1.txt:1,167`）。
9. **产品面观察**：安装目录额外落地 `catalog_loader.exe`（写 catalog 的 CLI），虽已披露（Handoff:42-44）且不扩 stdio 命令面，仍属分发面增项；Qt 字体缺失告警未在任何摘要披露。

---

## 是否达到可集成标准

**结论：达到“可集成 + 条件闭合”标准，未达到“直接置 done”标准。**

判据：底层能力为真——自包含 sidecar 在净化 PATH 下真实服务了三种模式（`raw/cleanstart-ac1-run1-stdout.log:4` 的 Qt 字体路径 `…\install\resources\core-sidecar\_internal\PySide6\…` 是“加载的是安装态 frozen 闭包”的硬证据），ac1 页面 sha 与 M2-AC1 冻结证据逐字一致，安装目录 163 文件 hash 零变化、frozen 进程零残留；fail-closed 分支在 `Command` 前 typed 失败且无 python 回落。因此缺陷集中在**证据表述精度**与**个别 AC 子元素缺断言**，不需要推翻实现重做。

**可由 Integrator（Codex）一条命令/一次落字闭合（无需改实现）**
- P2-1：按 `ac1-repro-sidecar-diff.txt` 更正四处“157 全同”表述为 156/157 + base_library.zip 归类。
- P2-5 + F/A 全部 not_verified：在集成 head 上执行并入库 `git diff --name-status 6f79c040..<delivery_head>`、`git diff --check 6f79c040..<delivery_head>; echo EXIT=$?`、`git status --porcelain`、以及 `git diff 6f79c040..eccf88e3 -- apps/desktop/src-tauri/src/core_bridge.rs`（用于裁定 A-⑤“字节不变”是否为抽取 `adopt_child` 后的不实措辞；若确有抽取，应把 Handoff/verification 的“字节不变”改写为“行为等价、argv/cwd/env 契约不变”）。
- P3-1/P3-8：随 corrigendum 一并更正数字与措辞，并在 gate.json 补记 installer sha256。

**须 Owner（或 Integrator 以变更身份）改代码/脚本后重跑才能闭合**
- P2-2：在 packaged production 阶段加一条可观测断言（例如 runner 直接对 `core_service.exe` 做 `core.ping`/`ListBooks` 往返，或把 WebView 的 `library_list_books` 结果落到 stdout/结果文件）后重跑 gate；或由用户/Codex 明确裁决该元素由隐式挂载 + M2-AC1 证据覆盖（此举需要落字授权，非 Reviewer 可代决）。
- P2-3：补 `packaging/m2ac5/README.md`（build venv 创建命令 + 固定版本 + 与 `requirements.txt` 的隔离声明）。
- P2-4：`production_env` 改为 `APPDATA=<lab>/roaming` 隔离（`packaged_user_root()` 读环境变量，语义不变），去掉对宿主真实用户目录的 rmtree。
- P3-2/3/4/6：runner 补 `encoding="mbcs"`、补 install_dir 无空格 guard、`spawn_packaged` 设 `current_dir`；可选把两个非 host_bridge 的缺失路径也收敛为 typed 错误。

---

## 下一任务建议（协议 §5.1）

1. **Task**：M2-AC5 条件闭合（非新 Task，属 review→integration 切片）；依赖=本次 Review 结论。
2. **Agent**：Owner 侧修 P2-2/3/4 → 建议 **ZCode**（原实现者，worktree 已在位）；条件闭合与复跑、merge、`done` 判定由 **Codex（Integrator）** 执行；Reviewer 须换非作者（本 Reviewer 已出具结论，不得自审闭合结果）。
3. **Recovery point**：`G:/CODEX/New Manga.worktrees/M2-AC5-zcode`，branch `agent/zcode/M2-AC5-package-clean-start`，`base_commit=6f79c040`，当前 `implementation_head=eccf88e3`，交付 tip `783fc74f`（请 Codex 以实际 `git log` 校正 self-referential hash）。
4. **Scope**：仅 `packaging/m2ac5/**`（runner/spec/README）、`verification/M2-AC5/**`、`doc/handoffs/M2-AC5-*.md`、`doc/tasks/M2-AC5.md`；**禁止** `src/**`、`requirements.txt`、`doc/contracts/**`、`library_bridge.rs`/`ac1_bridge.rs`；不得放宽既有基线（cargo/pytest/vitest）。
5. **Deliverables**：更正后的 verification-results/checkpoint/Handoff（含 156/157 与 11 条目更正）、`git diff --name-status`/`--check`/`status` 原始日志、新增的 packaged ListBooks/core_ping 断言与重跑终版 gate、`packaging/m2ac5/README.md`。
6. **Verification**：`git diff --check 6f79c040..HEAD` EXIT=0；`git diff --name-status` 全落允许路径；`src/**` 零改动；`cargo test --bin m2rc1-desktop`（≥38 passed + 1 ignored）/`pytest tests/m2_acceptance -q`（≥35）/`npx vitest run`（≥31）全 EXIT=0；clean-start 终版 gate 全 PASS 且新增断言在案。
7. **Forwardable instruction**：
   > Codex（Integrator）接手 M2-AC5 @ worktree `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`（branch `agent/zcode/M2-AC5-package-clean-start`，base `6f79c040`，implementation head `eccf88e3`）。已收到 DSH 非作者 Review 结论 `approved_with_conditions`。请先按该结论的 P2-1/P2-5 落字更正证据（`_internal` 实为 156/157 hash 相同，`base_library.zip` 不同；净化 PATH 实为 11 条目）并入库 `git diff --name-status`/`--check`/`status` 原始日志与 gate 用的 installer sha256；同时派 ZCode 在 `packaging/m2ac5/**` 内闭合 P2-2（packaged production 增加 ListBooks/core_ping 可观测断言并重跑 clean-start）、P2-3（补 `packaging/m2ac5/README.md`）、P2-4（`production_env` 用 `APPDATA=<lab>` 隔离，不再 rmtree 宿主 `%APPDATA%\com.newmanga.m2rc1.desktop`），禁止改动 `src/**`、`requirements.txt`、`library_bridge.rs`、`ac1_bridge.rs`。闭合后由另一非作者 Reviewer 复核，再 merge、复跑三层基线并置 `done`。

**无需下一步操作**（若用户或 Codex 决定将 P2-2 作为范围裁决关闭，则仅剩 P2-1/3/4/5 与 P3，此时下一步为 Integrator 单方面闭合，不需要新 Task）。