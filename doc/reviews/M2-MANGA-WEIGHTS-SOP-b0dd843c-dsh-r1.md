## Task A Verdict

**approved_with_conditions**

（核心三 pin 保真、dest 镜像、幂等/fail-closed 退出码均静态可确认；但有 3 项 P2 需修：一处代码与文档声称相反、一处 SOP 命令路径错误、一处 drift 模式语义缺口。条件闭合后可交集成。）

### A 逐项核对（A1-A5 一行一结论+依据）

| 项 | 结论 | 依据 |
|---|---|---|
| A1 pin 副本逐字一致 + URL | **PASS** | 脚本 `fetch_manga_weights.py:75-93,100` 的 `HF_REPO/HF_REVISION/WEIGHTS_DIRNAME/三 filenames/三 SHA256` 与 `detection_manga.py:77-93` 逐字相同；且被两份独立来源第三次佐证：`packaging/m2ac5/build_sidecar.ps1:80-82` 同三 pin、`verification/M2-PROD-DETECT-2/raw/installed-weights-sha256.txt:4-7` 为 NSIS 安装态实测 hash=pin；URL `https://huggingface.co/{repo}/resolve/{rev}/{file}`（`:150-151`）形式正确、三文件名与生产 loader 检查的三文件（`detection_manga.py:261-265`）完全对应 |
| A2 dest 解析与 core_assembly 真实一致 | **PASS（附 P4 注）** | 脚本 `:119-124` 的 `default_data_root` 与 `core_assembly.py:641-647` 逐字（含 `if root:` 空值回落语义，与 `core_assembly.py:613` 的 `if override:` 一致）；默认权重路径 `default_data_root()/models/detector/<dirname>` 与生产 `_resolve_detector_weights_path` 的 `data_root_candidate = Path(db_path).resolve().parent/...`（`core_assembly.py:610-616`）+ `core_service.py:76` `db_path = data_root/"library.db"` 等价；镜像责任已在 `:113-117` 注释声明；解析优先级（`--dest` > env > 默认）与生产（env > 数据根探针 > frozen bundle > 默认）语义不冲突。差异仅：生产用 `.resolve()`（symlink 级）、脚本对 env 值做了 `.suffix` 拒绝（R-A4，属故意加严且有注释） |
| A3 幂等/校验/fail 逻辑 | **FAIL（部分）** | 正确：已存在且 pin 命中→skip（`:192-196`）；缺目录 `--verify-only`→EXIT=1（`:243-249`）；持续不符/网络失败→EXIT=1（`:229-233`）；drift 无 `--dest`→EXIT=2（`:310-316`）；中断用 `.part` + rename，不会把半截文件当成品。**但**：pin 校验发生在文件已被搬到目标路径之后（R-A1，且报错文案与磁盘事实相反）；drift 模式对已存在文件一律跳过且 EXIT=0，截断/旧 revision 文件永远不会被重下（R-A3） |
| A4 SOP 与脚本行为一致 + 四场景 | **FAIL（一处）** | 四场景 A/B/C/D + §5 re-pin 流程 + §6 排查表齐备，iframe 序号与生产查找顺序（含 frozen bundle 第 3 层）描述正确，§6 报错字符串与 `verify_only` 实际文案一致（`MISSING at` / `sha256 ... != pinned`）、`.pt` env 误配置 EXIT=2 描述与 `:131-145` 一致；**但**场景 B 的示例校验路径与仓库事实不符（R-A2，照抄必然 EXIT=1），§1「新字节校验通过才覆盖旧文件」与代码相反（R-A1） |
| A5 范围纪律 | **PASS（附 P4）** | diff 恰为 4 文件（Task/Handoff/WEIGHTS-SOP.md/fetch_manga_weights.py），无二进制、无权重字节；`src/**`、`tests/**`、`requirements*`、`packaging/**` 零触碰。附注：`.gitignore`（根，仅 6 行）无任何权重/safetensors 规则，AC4「权重不入库（.gitignore 面）」目前只是过程纪律（R-A9）；`git diff --check`/tree 级检查无法静态复跑（NOT_VERIFIED） |

### A Findings

**R-A1｜[P2]｜`verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py:174`（+`:182-184`、`:214-222`）；`WEIGHTS-SOP.md:79-81`；`doc/handoffs/M2-MANGA-WEIGHTS-SOP-1019ed6b.md:33-34`｜校验时机在安装之后，且失败文案与磁盘事实相反｜** `download_file` 在 `:174` 执行 `tmp.replace(target)`（把新字节搬到生产权重路径）之后，调用方才在 `:214` 做 SHA-256 对比。于是：(1) docstring `:182-184`「the replacement only lands after the fresh bytes verify」与 SOP §1「新字节校验通过才覆盖旧文件」**与实现相反**；(2) 不符分支 `:216-222` 自称 "kept nothing"，而实际不匹配的字节就留在 `target`（且旧文件已被销毁）。对照同款先例 `verification/T1.1.1/scripts/fetch_doctr_weights.py:81-90` 是先校验 `.part` 再 `replace`。生产端因 loader 会重新校验 pin 而仍 fail-closed（`detection_manga.py:277-285` → `PROVIDER_FAILED`），但一个未验证产物落进生产权重目录 + 误导性诊断不符合本脚本自称的供应链纪律。**建议**：在 `tmp` 上校验通过后再 `tmp.replace(target)`；不符时 `tmp.unlink()` 并保留/删除旧文件的语义写清；把「kept nothing」改为「mismatched bytes left at <target>, delete and retry」；同步 docstring 与 SOP §1。

**R-A2｜[P2]｜`verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md:90-93,100`｜场景 B 的发布形态路径错误，唯一一条发布包校验命令必然失败｜** 证据链：`apps/desktop/src-tauri/tauri.conf.json:30-32` 把 onedir 作为 `resources/core-sidecar` 资源打入，`core_assembly.py:617-619` 的 bundle 候选是 `Path(sys.executable).parent/models/detector/<name>`，`raw/installed-weights-sha256.txt:3` 记录安装态实际为 `resources\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector`。故真实路径是 `<安装目录>\resources\core-sidecar\models\detector\<dir>\`（安装根当前为 `%LOCALAPPDATA%\m2rc1-desktop`，`tauri.conf.json:3`），而 SOP 写的是 `C:\Program Files\NewManga\models\detector\...`——安装根与 `resources\core-sidecar` 段两处都缺。照抄该命令会得到 `weights directory ... does not exist` EXIT=1，而 §6 排查表又会把它误导向「先跑下载（场景 A）」。SOP §0 第 3 条自己写的是「exe 旁」，SOP 内部自相矛盾。**建议**：改为 `<安装目录>\resources\core-sidecar\models\detector\<dir>\`（并说明「与 `core_service.exe` 同目录」），§6 增加一行「场景 B 路径不含 `resources\core-sidecar` → 校验失败」。

**R-A3｜[P2]｜`fetch_manga_weights.py:191,197-202`｜drift（`--source-revision` 非 pin）模式对已存在文件静默跳过且 EXIT=0，截断文件永不修复｜** `expected = None` 时只要 `target.is_file()` 就打一行 `already present (UNVERIFIED revision drift)` 并 `continue`：不校验、不下载、不计入 failures。后果：(1) 目标目录复用旧 revision 时，`--source-revision <new>` 实际什么都没取件，但退出码 0；(2) drift 模式没有 pin 可对，一个「流干净结束但被截断」的文件会被永久接受（pinned 模式有 hash 兜底，drift 模式没有）。而 SOP §5 正是把这个模式定位为 re-pin slice 的取件通道，drift 语义（存在即跳过）在 SOP 中也未登记。**建议**：drift 模式要求 `--dest` 目录不存在或为空（或引入 `--force`），否则 EXIT=2；至少在 SOP §5 明确「EXIT=0 不代表目标目录就是该 revision 的完整取件结果」并建议每次 drift 取件用新目录。

**R-A4｜[P3]｜`fetch_manga_weights.py:134`｜`candidate.suffix` 误拒合法目录（env override）｜** `if candidate.is_file() or candidate.suffix:` 会把 `NEWMANGA_DETECTOR_WEIGHTS=D:\cache\weights.v2` 这类合法目录判为「file 误配置」并 EXIT=2；`suffix` 对不存在的路径同样非空，导致带点的目标目录无法由脚本创建。生产端（`core_assembly.py:613-614`）对该值 verbatim 接受，故这是脚本单方面加严且判别不准。**建议**：改为只在 `candidate.is_file()`（或 `exists() and not is_dir()`）时拒绝，保留 `.pt` 指引；不存在路径放行或提示后仍放行。

**R-A5｜[P3]｜`fetch_manga_weights.py:162-174`（+`:187`、`:207-223`）｜失败/中断残留 `.part` 与半装目录未清理、未在 SOP 登记；171MB 无断点续传｜** `tmp.unlink()` 只在**下一次**尝试开头执行（`:163-164`），下载中途失败（网络断、超时、`Dest` 目录被占用）会把一个接近 171MB 的 `*.part` 留在权重目录（若有人对发布包目录跑该脚本则留在包内）；`--verify-only` 看不到它，SOP §6 也无清理条目。另有：失败后逐文件安装留下半装目录（EXIT=1，生产 fail-closed 可接受），但脚本/SOP 未给「重跑下载路径即可收敛」的一句话；无 Range/resume（代理不稳时只能从 0 重来）。**建议**：`download_file` 内 `except BaseException: tmp.unlink(missing_ok=True); raise`；SOP §6 加「残留 `*.part` 可安全删除 / 重跑收敛」一行。

**R-A6｜[P3]｜`fetch_manga_weights.py:310-325`｜`--verify-only` 也会触发 drift 判定与 WARNING，但实际仍按 pin 校验｜** `unverified_drift` 与 `parser.error`/WARNING（`:311-325`）在 `args.verify_only` 分支（`:335-336`）之前执行，故 `--verify-only --source-revision main --dest X` 会打印「fetching revision main … the per-file SHA-256 pins do not apply」，而 `verify_only()` 始终按 pin 比对、永不触网。诊断自相矛盾。**建议**：把 drift 判定/强制 `--dest` 收进 `if not args.verify_only:`，并在 `--verify-only` 帮助文本注明忽略 `--source-revision`。

**R-A7｜[P4]｜`fetch_manga_weights.py:187`｜`dest` 为已存在文件时抛裸 traceback，违反脚本自述的 EXIT=2 用法错误契约（`:384-386`，docstring）｜** `dest.mkdir(parents=True, exist_ok=True)` 遇到 `FileExistsError/NotADirectoryError` 未捕获。**建议**：捕获后 stderr 提示 + `raise SystemExit(2)`。

**R-A8｜[P4]｜`WEIGHTS-SOP.md:112-122`｜场景 C 未提示数据根可变｜** frozen 形态的数据根由 `NEWMANGA_DATA_ROOT` 决定（`core_service.py:370-372`），Tauri 侧配置了用户根时会被写成 `<user_root>\data`（`apps/desktop/src-tauri/src/main.rs:446-453`），此时照抄 `%LOCALAPPDATA%\New Manga\...` 会放错位置。**建议**：场景 C 增加一句「若目标机设置了 `NEWMANGA_DATA_ROOT`（含 Tauri 用户根派生），以该值为准」。

**R-A9｜[P4]｜`.gitignore:1-6` vs `doc/tasks/M2-MANGA-WEIGHTS-SOP.md:36`｜「权重不入库（.gitignore 面）」无对应规则｜** 根 `.gitignore` 无 `*.safetensors`/`*.pt`/`models/detector/` 任何条目；权重不入库目前完全依赖「默认 dest 在仓库外 + `--dest` 纪律」。本次 diff 确无权重字节（可静态确认），但过程护栏缺失。**建议**：加一条窄规则（如 `verification/**/weights/`、`*.safetensors`），或在 Task/SOP 明确「该护栏是过程性的，无 gitignore 兜底」。

**R-A10｜[P4]｜`doc/tasks/M2-MANGA-WEIGHTS-SOP.md:12` vs Handoff `:8` / 本次 Review 基线｜Task frontmatter `base_commit: 095e314dad…` 与分支 base `46f079e8`（Handoff 声明）不一致｜** 元数据级不一致，可能让后续复核者按错基线取 diff。**建议**：集成时统一为分支真实 base 或注明该字段为契约编写时基线。

### A NOT_VERIFIED

- **全部运行期结论**（静态沙箱无命令执行）：AC3a `--verify-only` 三 hash 全符、AC3b 经代理真实下载两轮（含 171,543,900 B `model.safetensors`）、AC3c 幂等二跑、AC3d 篡改自动重下、AC3e 三条失败路径退出码、AC3f `NEWMANGA_DATA_ROOT` 默认布局 —— 均为 Owner 自报，本 Task 未入库 raw 日志（Handoff 只写「本行命令可复现」）。171,543,900 B 这一数字有仓库内独立记载（`doc/tasks/M2-PROD-DETECT-2.md:31`、`doc/handoffs/M2-DOCTR-QUAL-C4-19d1772e.md:41`、`verification/M2-DOCTR-QUAL/qualification/license-evidence.md:39` HF API `size`），但「本轮脚本实测成功」无法静态确认。
- **网络面**：`resolve/16e8a622/<filename>` 三文件在 HF 侧的可用性、302→CDN 与默认 opener 走代理的实际行为；`16e8a622` 作为 revision 的服务端解析。
- **git 面**：`git diff --check 46f079e8..HEAD` EXIT=0、`git status --porcelain` 干净、变更范围恰 4 文件、改动树内无权重字节（我只能确认 review-input.diff 内无二进制与未新增路径；无法确认未提交/未跟踪文件）。另：Task frontmatter base 与分支 base 的祖先关系无法静态判定。
- **R-A1/R-A3 的现场表现**：mismatch 分支实际落盘状态与「复用目录 + drift」复跑行为未实测（结论由代码路径静态推出）。
- **中断恢复**：真实断网/超时下的 `.part` 残留与重跑收敛未实测。

## Task B Verdict

**approved_with_conditions**

（条件化本身正确、最小、判别力保留、范围干净；两项条件均为**文档级**：Handoff 的修复前基线数字错误、skip 理由中「构建期断言接管」的方向性表述不成立。可并入集成/ hygiene commit，无需改行为。另测出 3 项 P4。）

### B 逐项核对（B1-B5 一行一结论+依据）

| 项 | 结论 | 依据 |
|---|---|---|
| B1 skip 条件正确性 | **PASS（附 P4）** | 触发探针 `importlib.util.find_spec("torch")`（`tests/providers/test_registry_readiness.py:216`）与断言循环所用探针**完全相同**（`:226-227`），故 skip 恰好发生在「原循环首个断言必失败」的同一条件下——不存在相对原语义的误 skip；`find_spec` 只查 spec 不 import，无重型副作用。skip 理由自包含可诊断：`torch==2.14.0`、`transformers==5.17.0`（与 `requirements.txt:17,28` 一致）、TASK-019 前提、`packaging/m2ac5/core_sidecar.spec _assert_ml_closure`、M2-PROD-DETECT-2 均可追。残留：信号只取 `torch`（R-B3）、`find_spec` 是「存在」而非「可导入」（R-B4） |
| B2 原断言保留完整性 | **PASS** | diff 对该文件只有**一个** hunk（`@@ -188,7 +188,41 @@`），新增全部落在 docstring 与 skip 块；循环 `for module in (…)` / `assert importlib.util.find_spec(module) is None` / 失败消息三行在 diff 中以 context（空格前缀）出现（`review-input.diff:187-189`），且旧窗口 7 行=文件头+docstring+循环前三行，无第二 hunk ⇒ 循环其余行与 `test_registry_readiness.py:226-230` 逐字未动 |
| B3 「闭包无 ML」防护是否由构建期断言接管 | **PASS（有保留）** | 引用位置真实存在且描述准确：`packaging/m2ac5/core_sidecar.spec:77-81`（`ML_HIDDENIMPORTS` 三 pin）、`:106-123`（`_assert_ml_closure`，`pure_names` 缺失即 `SystemExit` 失败）、`:84-103`（`_archive_warn_file` per-entry warn 归档），`verification/M2-PROD-DETECT-2/integration.md:33-35` 有 GATE 25/25 与断言输出实证。**但方向相反**：该断言保证「ML **在**发布闭包内」，并非「本机环境**没有** ML runtime」；被替换的功能（TASK-019 环境前提固化）是作废而非转移（R-B2） |
| B4 意图判定与登记是否成立 | **PASS** | 判定有仓库证据：`doc/tasks/TASK-019.md:27`（释放缺口第 3 条「本环境无 torch/diffusers/numpy（已实测）…按 BLOCKED 交付」）、`:91` 同述、`verification/TASK-019/ac-status.md:48` 的 BLOCKED 条目、以及前序 Review `doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r1.md:20`（「断言 venv 无 torch/numpy … 另立 slice 合理」）。Owner 在 Task 意图小节（`doc/tasks/M2-FIX-REGISTRY-READINESS-ENV.md:40-46`）纠正了契约 设计决策#1 的事前猜测（「大概率=闭包/registry 防护」）并在 claim commit 登记；方案 a 与 设计决策#2 一致，AC2 把契约预估的「402 passed 0 failed」修正为「401 passed + 1 skipped」也正确（skip 不计 passed；与 `release-notes.md:67` 的 pre-fix 289+1 自洽） |
| B5 范围纪律 | **PASS** | diff 恰 3 文件（测试 + Task + Handoff）；零 conftest；`src/**`、`packaging/**`、`requirements*`、其他测试语义零触碰（diff 可证） |

### B Findings

**R-B1｜[P3]｜`doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md:48-50`（「未运行项」段）｜修复前基线数字错误，且与仓库内既有实测记录矛盾｜** Handoff 写「修复前全套=288 passed + 1 failed 可由『修复后 289+1 skip、唯一变化即该测试』严格推出」。仓库内既有实测是 providers **289 passed + 1 failed**、三套件 **401 passed + 1 failed**（`verification/M2-PROD-DETECT-2/release-notes.md:67`、`integration.md:38~39`）。且 failed→skipped 不会让 passed 减一，正确推导是 289 passed + 1 failed（290 项不变）。该数字会被集成方写进 STATUS 口径，属会被传播的错误。**建议**：改为「修复前 providers 289 passed + 1 failed（三套件 401 + 1 failed，见 verification/M2-PROD-DETECT-2/release-notes.md:67）」或直接引既有记录而非自行推导。

**R-B2｜[P3]｜`tests/providers/test_registry_readiness.py:203-207` 与 `:221-224`｜「闭包级保证由 `_assert_ml_closure` 接管」方向性不成立，且与本 Task 自己的意图判定相左｜** docstring/skip 理由称被替换的是「deployment-level 'no unverified ML closure' guarantee … now enforced at BUILD time by … `_assert_ml_closure`」。但 `core_sidecar.spec:106-123` 断言的是「transformers/rt_detr/rt_detr_v2 **已**进 PYZ」（缺了才失败），与「本环境无 ML runtime」是**相反**命题；而 Task 意图小节 `M2-FIX-REGISTRY-READINESS-ENV.md:43` 明确该测试「不是 registry/闭包语义防护」。真正成立的只是「TASK-019 前提被已批准依赖推翻 → 该证据职能作废」，不是「转移到构建期」。**建议**：skip 理由与 docstring 改写为——本机既有 ML 栈，TASK-019 的「无 runtime」证据已作废（不是被替代）；发布侧另有**独立**保证：构建期断言 ML 闭包完整性（`packaging/m2ac5/core_sidecar.spec:106`，方向相反，勿混同）。

**R-B3｜[P4]｜`tests/providers/test_registry_readiness.py:216`｜skip 门比被断言的集合窄（仅 `torch` vs 五模块元组）｜** 「无 torch 但 numpy 在位」的环境会走循环并在 `numpy` 上报错（TASK-019 原报文），而 Handoff 风险段（`:58-61`）把它解释为「保留的漂移报警」，但 skip 理由本身没写这层意图，未来读者会把它读成 flaky。**建议**：在 skip 理由或相邻注释一句话说明「门只取 torch，其余四个模块的缺位在有 torch 环境下必然一并成立/无 torch 环境下仍逐字断言」。

**R-B4｜[P4]｜`tests/providers/test_registry_readiness.py:216`｜`find_spec` 是存在性而非可导入性探针｜** torch 目录存在但 import 失败（半装/DLL 缺）时同样 skip，此时 `diffusers/paddleocr/manga_ocr` 完全不再被检查；与原循环探针一致故不算回归，但属已知盲区。**建议**：在 docstring 记为已知限制，或加一个 `try: importlib.import_module("torch") except Exception: pass` 的更严格判据（需权衡变慢）。

**R-B5｜[P4]｜`doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md:47`｜「判别力双路径模拟」证据不可复跑｜** 受控 stub 探针「跑后已删」，AC1 的判别力论证只剩 diff 推理 + 一行文字，集成方无法复现。**建议**：把该模拟固化为一个小型参数化测试（或提交探针脚本到 `verification/`），使其成为可独立复跑的判别力证据；否则至少把探针源码片段写入 Handoff。

### B NOT_VERIFIED

- **全部运行期计数**（静态沙箱无命令执行）：单文件 `7 passed, 1 skipped` / fix 前 `1 failed, 7 passed`、providers `289 passed + 1 skipped`、m2_acceptance `35`、core `77`、合计 `401 + 1 skipped 0 failed` —— 均为 Owner 自报，本 Task 未入库 pytest 原始日志。
- **判别力双路径模拟**：探针已删，无法复核；只能确认「skip 分支唯一触发条件为 `find_spec("torch") is not None`，否则循环逐字执行」这一静态结论。
- **真实无 torch 环境**的行为（Owner 自述本机可用 Python 均带 ML 栈，故以 stub 替代）。
- **git 面**：`git diff --check 46f079e8..HEAD` EXIT=0、`git diff --name-only` 范围恰 3 文件、`git status --porcelain` 干净。
- **STATUS 口径同步**：`doc/STATUS.md` 未在本 diff 中（不在 Owner 允许路径，属集成方动作），故「历轮 +1 既有环境性失败条目终结」尚未落地。

## 集成方闭合清单（两 Task 合并按优先级）

1. **[A/R-A1，P2，代码+文档]** `download_file` 改为「先校验 `.part` 通过再 `replace`」，并把不匹配文案从 "kept nothing" 改为「不匹配字节留在 `<target>`，需删除后重试」；同步 `fetch_manga_weights.py:182-184` docstring 与 `WEIGHTS-SOP.md:79-81`。修后由集成方复跑 AC3d（篡改→重下恢复 pin）并加一条「故意错 pin → 目标目录不得出现未验证文件」的反证。
2. **[A/R-A3，P2，代码或文档]** drift 模式决定：要么要求 `--dest` 为空/不存在（否则 EXIT=2）或加 `--force`，要么在 SOP §5 显式登记「存在即跳过、EXIT=0 不代表取件完整」并规定每次 drift 取件用新目录。二者择一必须留痕。
3. **[A/R-A2，P2，文档]** 修正 SOP 场景 B 示例路径为 `<安装目录>\resources\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector\`（当前安装根 `%LOCALAPPDATA%\m2rc1-desktop`，productName 见 `tauri.conf.json:3`），并在 §6 增加对应排查行。
4. **[B/R-B1，P3，文档]** Handoff「修复前全套=288 passed + 1 failed」改为 289 passed + 1 failed（或直引 `verification/M2-PROD-DETECT-2/release-notes.md:67`），避免错误基线写进 STATUS。
5. **[B/R-B2，P3，文档]** 改写 skip 理由/docstring：TASK-019 环境证据前提**作废**（非被替代）；发布侧 ML 闭包完整性由 `packaging/m2ac5/core_sidecar.spec` 构建期断言**独立**保证（方向相反，勿混同）。
6. **[B，集成方动作]** 按 Task B AC2 注记 STATUS 新口径「providers 289 passed + 1 skipped（env-conditioned）」，删除历轮「+1 既有环境性失败」条目。
7. **[低优先，可并入同一 hygiene commit]** A/R-A4（`.suffix` 误拒合法目录）、A/R-A5（`.part` 残留与无续传的 SOP 说明）、A/R-A6（`--verify-only` 不应触发 drift WARNING）、A/R-A7（`mkdir` 失败应 EXIT=2）、A/R-A8（场景 C 提 `NEWMANGA_DATA_ROOT`）、A/R-A9（权重 gitignore 护栏或改述 AC4）、A/R-A10（Task frontmatter base 与分支 base 不一致）、B/R-B3/B4（skip 门与探针语义注释）、B/R-B5（把判别力模拟固化为可复跑证据）。
8. **[复现门禁]** A：`--verify-only --dest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"` + 一个临时目录的真实下载 + drift 空/非空目录各一次；B：`PYTHONPATH=src <主venv>/python -m pytest tests/providers tests/m2_acceptance tests/core -q -rs`；两 worktree 各自 `git diff --check`/`--name-only` 范围核对。任一门禁不过，按协作协议回落 Owner 修链而非直接合入。

## 推荐下一步

让 ZCode 在各自 Task 分支补一个 fix/hygiene commit 闭合 A-R-A1/A2/A3 与 B-R-B1/B2（含 A 侧复跑 AC3d 与一条 mismatch 反证），再由集成方在合并前复跑 A 的两行命令与 B 的三套件并按清单第 6 项注记 STATUS。
