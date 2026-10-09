# DeepSeek Harness Review：P02 Process Isolation r2

```yaml
task_id: P02
reviewer: DeepSeek Harness
author: Codex
base_commit: 09bb1a2783052cdb6d514070e32f0ca9a2e48a04
reviewed_head: 3555213a748a7b407400589e1490a387353dec16
reviewed_tree: 38f312374c88713b7e10269c9b4ecc5eb8e1eeda
decision: APPROVED
scope_of_approval: 仅 P02 Scratch Build Process Isolation Design r2 的「方案/设计」审查
```

- Decision：**APPROVED**（方案审查通过）。**不等于** smoke 授权、build 授权、Build Gate PASS、AC1–AC6 PASS 或任何运行态事实 PASS。本 APPROVED 最多允许 Codex 依 proposal 自带的 preflight 与停止规则**尝试**一次 isolation smoke；build 仍须独立 Build Gate。
- 本 Reviewer 非作者（author=Codex，Integrator=Codex），全程 detached 只读 checkout。本报告以消息交付，未写入仓库；Review 前后 `git status --porcelain --untracked-files=all` 均为空。
- 视角：Architecture=executed；Verification=executed（只读命令级复核 + 运行态逐项 NOT_RUN/NOT_VERIFIED）；Standards=executed（范围/协作协议）；Spec=executed（P02 Task boundary / scope delta / 子任务契约）。

---

## 1. Exact base / candidate / tree

| 项 | 值 | 我的复核 |
|---|---|---|
| Base | `09bb1a2783052cdb6d514070e32f0ca9a2e48a04`（`docs(P02): checkpoint isolation r2 repair start`） | 与请求一致 |
| Candidate HEAD | `3555213a748a7b407400589e1490a387353dec16`（`docs(P02): revise sandbox isolation gate r2`） | `git rev-parse HEAD` 一致 |
| Candidate tree | `38f312374c88713b7e10269c9b4ecc5eb8e1eeda` | `git show -s --format=%T` 一致 |
| HEAD parent | `09bb1a27…`（= base） | 一致 |
| base..HEAD commit 数 | 1 | `git rev-list --count` = 1 |
| r1 候选（历史） | `c542a31b102cdc5c129efd9df155a2760ed777b2`，tree=`5af3d8b4de75da0be13ce3fbbc81df26fabb9f7f` | 对象存在；是 HEAD 祖先（`merge-base --is-ancestor` EXIT=0）；tree 与 r1 报告一致 |
| build source commit | `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a` | 是 `549a6544…` 与 HEAD 的祖先；`7ce3c40..549` 恰好 8 个 `doc/**`+`verification/**` 路径（无产品源码），佐证 proposal L7 |
| live root | `main@549a6544f0be1eec66c09ece393fd1a409f10bf3`，203 dirty/untracked，0 staged | `git --no-optional-locks -C "G:/CODEX/New Manga"` 复核一致 |

## 2. Worktree cleanliness and reviewed paths

- Review worktree：`C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r2`，detached（`## HEAD (no branch)`），HEAD=候选。
- 清洁性：Review 开始时、中途、结束时 `git status --porcelain --untracked-files=all` 均为空；无 stash。**未编辑任何文件**。
- 未执行：Sandbox 启动/连接、任何 `wsb` 命令、Windows Optional Feature 查询/修改、build、P02 runner、Vitest、GUI/WebView。唯一执行的"产品侧"脚本是只读规划校验器 `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`（EXIT=0，196 节点，末行 `Product tests/build/GUI: NOT_RUN (planning-only)`）。
- base..HEAD 变更 = **8 路径**，`git diff --numstat`：

| 路径 | +/− | 是否在 scope delta r2 许可内 |
|---|---|---|
| `doc/tasks/P02.md` | 1/1 | ✅（仅 `Codex-only scratch-build output boundary` 段 L62 一行） |
| `verification/P02/codex-checkpoint-p02-process-isolation-r2-candidate.md` | 21/0 新增 | ✅（checkpoint 附件） |
| `verification/P02/codex-p02-wsb-smoke-config-r2.xml` | 22/0 新增 | ✅（evidence/artifact） |
| `verification/P02/codex-process-isolation-root-start-manifest.json` | 8/1 | ✅ |
| `verification/P02/codex-scratch-build-gate.md` | 10/0 | ✅ |
| `verification/P02/codex-scratch-build-plan.md` | 17/7 | ✅ |
| `verification/P02/codex-scratch-build-process-isolation-proposal-r1.md` | 90/48 | ✅ |
| `verification/P02/dsh-review-process-isolation-r1.dispatch.md` | 1/1 | ✅（dispatch 附件） |

- 未触及 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、任何产品代码/依赖/共享契约/Owner allowlist。`git diff --summary` 仅两个 `create mode 100644`，无 mode 变化、无二进制。
- **产品范围/Task 状态**：P02 仍 `in_progress / ACTIVE`，AC1–AC6 仍 `BLOCKED`，Build Gate 仍 `BLOCKED`，build 仍 `NOT_AUTHORIZED / NOT_RUN`；与 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（`##当前检查点` 与 P02 行"build需先过scratch/sidecar隔离Review"）一致。候选未把任何未验证事实写成 PASS。

## 3. R-01..R-11 closure table

依据：`dsh-review-process-isolation-r1.response.md:52–68`（finding 原文）、`codex-scratch-build-process-isolation-proposal-r1.md:95–107`（closure map）、实际文件内容。

| ID | r1 级别 | 状态 | 证据（路径:行） | 判定理由 |
|---|---|---|---|---|
| R-01 | P1 | **CLOSED（设计）** | proposal:18,20,23；plan:27,38；`doc/tasks/P02.md:62` | `git clone --no-local --no-hardlinks --no-checkout` + private common-dir、无 alternates、`git remote -v` 空、逐 object `fsutil hardlink list` link count=1、权限不足即不得启动。官方 git-clone 语义与我实测（`fsutil hardlink list` 非提权可执行、git 2.52 支持 `--path-format=absolute`）支持该检查可执行。运行态 clone=NOT_RUN。 |
| R-02 | P2 | **CLOSED（设计）** | proposal:27–42；XML:11–20；inventory:10–21,45；plan:40 | 10 条 mapping 三处逐条一致；`pyvenv.cfg` 实测 `home = C:\Users\49745\AppData\Local\Programs\Python\Python312`（= 映射的同一绝对路径）、`include-system-site-packages=false`、3.12.3；`build_sidecar.ps1:31,41,49` 的 host 默认值均由 plan:40 的 guest 参数显式覆盖；脚本以 `& $PythonExe -m PyInstaller`（`:224`）调用，不依赖 venv 内嵌绝对路径入口。残留见 F-01/F-02（P3）。 |
| R-03 | P2 | **CLOSED** | `doc/tasks/P02.md:62`；scope delta:13,19；diff 1 行 | 形态由 "scratch worktree" 改为固定 `G:\CODEX\P02-scratch-build-source` non-linked clone，含来源 commit/`--no-local --no-hardlinks`/private common dir/无 alternates/origin/硬链接复核/占用即 BLOCKED；未改 Owner allowlist、AC、Task 状态。 |
| R-04 | P2 | **CLOSED（设计）** | proposal:46–54；plan:40,69；inventory:25–30 | 缓存**不**做只读映射，改为 Build Gate 前 host 侧 seed 到 clone 内已登记 cache：npm 仅 `_cacache`（排除 `.npmrc`/日志），Cargo 仅 `registry`+可选 `git`（排除 `credentials*`/`config*`/`bin`/`rustup`）；`npm ci --offline --cache <clone>/verification/P02/npm-cache`（与 `_cacache` 布局自洽）、`cargo build --locked --offline`。覆盖完整性明确留给 Build Gate。残留见 F-08（P3，secret 扫描）。 |
| R-05 | P2 | **CLOSED（设计）** | proposal:58–62 | config 串逐字节冻结 + SHA-256 绑定；任何字段/映射变化即 hash 失效并重新 Review；ProtectedClient 被拒或 `wsb exec`/连接不可用 → BLOCKED/NOT_VERIFIED；不猜 token、不关 ProtectedClient、不换映射；smoke 不使用 clipboard。官方 ProtectedClient 段（AppContainer，可能限制 copy/paste）与该表述一致。运行态 N/A。 |
| R-06 | P2 | **CLOSED（设计）** | proposal:64–70 | 交互式**非提权** host PowerShell 启动、pre-start manifest 记录身份/PS 版本/令牌完整性/提权状态/`wsb` 路径 hash 版本/CLI 原始输出与 exit；先 `wsb connect` 再 `--run-as ExistingLogin` 执行 probe；probe I/O 只写 scratch；UI 截图（`list_apps/list_windows` → `get_window_state(include_screenshot)`）绑定 window/session/时间戳/文件 hash；受限 shell、无法绑定窗口、截图无法落盘均 BLOCKED。与官方 CLI 文档（exec 需活跃会话、不返回进程 I/O，需 connect）一致。残留见 F-03/F-07（P3）。 |
| R-07 | P2 | **CLOSED（已在仓库内实证一致性）** | proposal:19,58；plan:27–29,38；checkpoint:18 | 我实测三个 pin 与 **CRLF 工作树字节**逐一命中：`build_sidecar.ps1=07e12e80…`（CRLF，LF 形态为 `44513fbd…`）、`core_sidecar.spec=c73d6fe0…`、`requirements-build.txt=c50edd6c…`；clone 显式 `core.autocrlf=true` 后再 checkout，语义自洽（若误配为 LF 只会自伤式 BLOCKED，不会产生伪 PASS）。 |
| R-08 | P2 | **CLOSED（设计）** | proposal:74–83 | smoke 明确使用后续 build 依赖的**真实** HostFolder 集合（非 synthetic）：逐 RO mapping 读样本/hash + RO canary 写拒绝、RW nonce canary、未映射 live root 与 common `.git` 不可见、host 可达 TCP endpoint 对照 + guest default-route/TCP 失败；任一不符 → Smoke Gate=BLOCKED/NOT_VERIFIED 并保留现场。运行态 NOT_RUN。 |
| R-09 | P3 | **CLOSED** | proposal:58,76,81 | 停止后只要求目标 session `status != running`（接受 stopped 条目），与官方 CLI `list`（status 可为 running/stopped）一致；`Networking` token 差异显式登记为 NOT_VERIFIED、无 fallback（评估见 F-04，结论：可接受）。 |
| R-10 | P3 | **CLOSED** | proposal:60；plan:70；gate:49 | smoke 显式 `MemoryInMB=2048`，host 可用内存阈值 ≥4096 MiB，实时读不到或低于阈值即 BLOCKED；Build Gate 必须另定数值与"配置值+2048 MiB"阈值，不得沿用 smoke 数值。 |
| R-11 | P3 | **CLOSED（已独立复算）** | manifest tail `entries_sha256_recipe`；checkpoint:5 | 我按记录的 replay 命令复算：`json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(',',':'))` → **36,985 bytes**，SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`，与 manifest 字段完全一致。 |

**结论**：R-01–R-11 **无一项**被含糊带过或伪造闭合；P3 项（R-09/R-10/R-11）也是真实闭合。r1 报告确实**没有**批准 smoke/build（`dsh-review-process-isolation-r1.response.md:16,94–102`），且 r2 三处文件（gate:45、checkpoint:17、proposal:3）均如实复述该限制。

## 4. 独立核验通过的事实（我的只读复算，非作者声明转述）

| 核验项 | 命令/方法 | 结果 |
|---|---|---|
| Candidate XML canonical bytes | python 读 raw、仅 CRLF→LF、SHA-256 | `2397` bytes，`sha256=dcb95da5252709f9ada9899cd92dcc90c388fa81f4ba23cdb60f18663ac691b6` = 记录值 ✅；raw CRLF 形态为 `4d9ff7be…`（≠记录值，未被混用）✅ |
| XML 提交字节是否即 canonical | 对 LF 归一内容算 Git blob SHA-1 | `4d030b6b44241e4583d2fbf9066a04d0d0653e2e` = `git rev-parse HEAD:<xml>` ✅（证明提交的是 LF canonical，而非 review worktree 的 CRLF raw） |
| XML 结构 | `xml.etree` 解析 | 无 BOM（首 3 字节 `<Co`）、无 XML 声明、格式良好、`MappedFolder` 10 条、1 RW / 9 RO、无 `LogonCommand` ✅ |
| root 起点 manifest 聚合 hash | 按记录的 replay 命令复算 | 36,985 bytes / `3a54fa97…` = 记录值 ✅ |
| root manifest vs live root | 203 项逐项 size+SHA-256 + status 集合比对 | 203/203 MATCH、0 MISMATCH、0 MISSING；onlyLive=0、onlyManifest=0；状态 4×`" M"` + 199×`"??"`；`doc/tasks/P02.md` 不在 dirty 清单（root clean）✅ |
| host inventory 可执行文件身份 | 对 8 个 host 文件逐一 size+SHA-256 | **8/8 全 MATCH**（Python312 python.exe 103192 / venv python.exe 274712 / node.exe 91694408 / npm.cmd 538 / vcvars64.bat 39 / vswhere.exe 469456 等）✅ |
| `pyvenv.cfg` 与映射一致性 | 直接读 host 文件 | `home` = XML 中同路径映射、`include-system-site-packages=false`、3.12.3 ✅；venv `Scripts` 无 DLL（由 `home` 解析），故"base 同路径映射"是 venv 在 guest 可执行的必要条件，设计已满足 ✅ |
| scope delta 许可 | 逐路径比对 | 8/8 路径落在许可内 ✅ |
| 规划校验器 | `python -B -X utf8 verify_plan.py` | EXIT=0，196 节点、live P01/P02/P03/P08 一致、`git diff --check` EXIT=0 ✅ |
| 凭据文件 | `git ls-files` 过滤 `npmrc/.env/credentials/netrc/pypirc` | 候选树内 0 个受跟踪凭据文件（clone = committed tree，故不会把 root 的未跟踪现场带入 guest）✅ |
| r1 原始 stdout 归档 hash | 对 checkout 外归档文件复算 SHA-256 | `1354AC518ED45FAE630CF0E908A9BB83236FD17971439229E6FB879281E6513B` = `dsh-review-process-isolation-r1.dispatch.md` r2 记录值 ✅ |
| `fsutil hardlink list` 可执行性 | 本机非提权实测 | EXIT=0，输出单一路径 → R-01 的 link-count 检查在本环境可执行 ✅ |

## 5. Findings（P0/P1/P2/P3）

**P0 = 0；P1 = 0；P2 = 0。** 以下 10 项均为 **P3**（不阻断本方案 Review，但必须在 smoke preflight 或 Build Gate 各自收口前处理/登记）。

| ID | 级别 | 路径/行 | 触发条件 | 影响 | 最小修复 |
|---|---|---|---|---|---|
| F-01 | P3 | `packaging/m2ac5/build_sidecar.ps1:187–188`；`codex-scratch-build-plan.md:40`；XML:11–20；`codex-scratch-build-input-host-inventory-r1.md:10–21,45` | Build Gate PASS 后按 plan:40 在 guest 执行 sidecar 构建 | 脚本在 `$ErrorActionPreference="Stop"` 下先执行 `git -C $repoRoot rev-parse HEAD`；guest **无任何 git 来源**（我 grep 整个 `verification/P02` 无 `git.exe`/`Program Files\Git`/portable git；XML 无该映射），故必然抛 CommandNotFoundException，build 必失败（fail-closed，不会伪 PASS，但会让一次 Build Gate 尝试无效/易被误记为"隔离失败"）。plan:40 的"先完成工具链环境 inventory；任一输入缺失即停止"可缓解但未登记 git | 在 host inventory/pre-start 清单与 plan 的工具链环境 inventory 中**显式登记 guest git**（只读映射 host 安装 `C:\Program Files\Git` 并记版本/hash，或 pin 便携 git 并记来源/hash）；注明该映射只进 **Build 阶段独立 config**（smoke 不需要）并因此触发 config/hash 重冻结与复审；不得依赖 guest 镜像自带 git（运行时 NOT_VERIFIED） |
| F-02 | P3 | `codex-scratch-build-plan.md:40`；inventory:42,45 | cargo `--release` 链接阶段 | 命令序列未显式激活 MSVC 环境（`vcvars64.bat`/`VsDevCmd`），而 inventory 自述 `cl.exe/link.exe` 不在 host PATH、"guest toolchain resolution is not verified"；若 rustc 无法定位 `link.exe`，Build Gate 阶段会失败 | 在 plan:40 显式写出 MSVC 激活或 `link.exe` 定位步骤及其证据，纳入 Build Gate"工具链闭包" |
| F-03 | P3 | proposal:58,66；plan:70 | smoke 启动、`wsb` CLI 解析 `--config` | 已如实登记差异与无 fallback，但未覆盖"parser **静默忽略**未知 token"这一失败模式（若静默忽略，Networking 可能回落默认 Enable） | 在停止规则中写明：若 CLI 未明确拒绝也未生效，则以 default-route/TCP probe 为唯一边界证据（step 4 已有）；preflight 归档 CLI 对精确字符串的接受/拒绝原文与 exit code。**不需要**为此单独重新 Review |
| F-04 | P3 | proposal:60；plan:70 | Build Gate 若设定 `MemoryInMB > 4096` | 官方文件仅述"默认启动上限 4GB"与"不足时自动提升到最小 2048MB"，**未定义可设上限**；>4096 是否被接受/生效为 NOT_VERIFIED（smoke 用 2048 无风险） | Build Gate 定值时先实测确认接受与生效；不可测则记 NOT_VERIFIED 并据此下调 workload 或停止 |
| F-05 | P3 | proposal:76；plan:70 | smoke preflight | 内存阈值已量化（2048/4096 MiB），但磁盘/CPU 仅写"达标"；官方 install 文档给出 ≥1 GB 空闲磁盘、≥2 CPU 核（≥4 GB RAM） | 把上述数字写进 smoke preflight 的判定式 |
| F-06 | P3 | proposal:19,83；plan:38 | clone 检出后工作树不 clean 或出现未登记文件 | 仅"pin 不符 ⇒ BLOCKED"被显式写成停止规则；"不 clean"未列入 L83 的 BLOCKED 清单 | 在 L83/plan 停止规则补一条"clone 工作树不 clean 或含未登记文件 ⇒ BLOCKED，不清理" |
| F-07 | P3 | proposal:78 | RO mapping 的只读强制**未**生效时执行 RO canary | 该 canary 的设计意图就是尝试写入 host 只读目录（如 `C:\Program Files (x86)\Windows Kits\10`、Python base 目录）；一旦 RO 失效，会真实产生 stray 文件（无破坏性，但违反"不写非 scratch host 路径"并需人工处置） | 预登记补救规则：canary 命名唯一化；写成功即 BLOCKED、记录 stray 文件精确路径/size/SHA-256、纳入前后 manifest 差异、处置（删除/保留）由单独 scope 决定 |
| F-08 | P3 | proposal:44；inventory:23,28 | pre-start manifest 对**全部**映射文件递归记 size+SHA-256（含 VS BuildTools/Windows SDK 等数万至十万级文件、数十 GB） | 可执行但成本与 manifest 体量不可忽略，且缺"配方"会使第三方无法复算 | 定级证据配方：clone 内全量递归 hash；超大只读工具链根用"目录树聚合 hash + 实际调用的可执行文件/权威样本 hash"；把配方与复算命令写死。另外 seed 的 `_cacache` 建议加一次秘密扫描（设计已排除 `.npmrc`，此项为补充） |
| F-09 | P3 | `codex-checkpoint-p02-process-isolation-r2-candidate.md:8–15` | 复核该"记录时工作树内容 SHA-256"表 | 口径不一致且非整表可复现：`P02.md`/manifest/dispatch 复现为 **CRLF** 形态，`gate.md`/`plan.md` 仅在 **LF 归一**形态复现，`proposal` 两种形态**都不复现**（HEAD 内容 16245 B，109 CRLF/LF）。不影响 canonical XML hash（我已独立复核）与任何 Gate，但交付记录不可整表复核 | 统一配方重生成（建议统一记 Git blob SHA-1 + canonical LF SHA-256） |
| F-10 | P3 | base 版 `dsh-review-process-isolation-r1.dispatch.md:7` → r2 版同文件:7 | r1 raw 证据可追溯性 | base 版指向 `verification/P02/dsh-review-process-isolation-r1.stdout.jsonl`，但该路径**从未被 Git 跟踪**（`git ls-files`/`git log` 为空）；r2 改为 checkout 外归档路径 + SHA-256（我已独立复算 MATCH）。改进属实，但 repo 内 Reviewer 无法仅凭仓库复核 r1 raw | 后续把 raw stdout 归档进 `verification/P02/`，或把"外部归档 + hash"写成正式登记口径 |

## 6. 独立 Gate 状态（互不推导）

| Gate | 状态 | 依据 |
|---|---|---|
| **方案 Review（本报告）** | **APPROVED**（0×P0/P1/P2；10×P3） | 本报告 §3–§5 |
| **Isolation Smoke** | **NOT_AUTHORIZED / NOT_RUN**（尚未获得 Codex 的 start-config 冻结与 preflight） | 本 APPROVED 最多允许 Codex 冻结 start config/hash、exact HostFolder manifest、preflight 与 UI 取证后**尝试** smoke；smoke 仍须按 proposal:74–83 的停止规则执行，任一不符即 BLOCKED/NOT_VERIFIED |
| **Build Gate** | **BLOCKED / build=NOT_AUTHORIZED / NOT_RUN**（未被本 Review 改变） | proposal:87–91；gate:49–50；hook/cache 闭包仍未证明；F-01/F-02 应先登记 |
| **产品 AC1–AC6** | **BLOCKED**（未被本 Review 改变，无产品代码差量） | `doc/tasks/P02.md:40–45`；`doc/STATUS.md`；proposal:89 |
| 独立 Gate 分离表述 | 正确 | 候选所有文件（proposal:3,74,83,87；gate:45,50；checkpoint:17,21；scope delta:34–36）均明确"Review 通过最多允许尝试 smoke，不授权 build"，无一处把 XML parse、设计推导或文档承诺写成运行态 PASS |

## 7. 官方来源及实际支持的结论

| 来源 | 实际支持的内容（我据此核对的候选表述） |
|---|---|
| [Windows Sandbox CLI](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)（last updated 2025-01-24） | `start --config <formatted string>` 确为"formatted string"（不传文件路径，候选正确）；CLI 示例**逐字**使用 `<Networking>Disabled</Networking>`（候选选择有第一方依据）；`list` 的 status 可为 running/stopped（R-09 处理正确）；`exec` **不返回进程 I/O** 且需先 `connect` 建立活跃用户会话，`-r ExistingLogin\|System`（proposal:68 准确）；`share --allow-write` 存在（候选禁用它，方向为 fail-closed，正确） |
| [Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)（2026-03-29） | 默认值：vGPU/Networking/Audio/Clipboard=Enable，Video/Printer/ProtectedClient=Disable（候选逐项反向显式设置= fail-closed）；`Networking` 受支持值仅 **Enable/Disable/Default**（无 `Disabled` → 候选的 NOT_VERIFIED 登记**属实**）；`MappedFolders.HostFolder` "must already exist on the host, or the container fails to start"（候选的路径存在性预检正确）；`SandboxFolder` 不存在则创建；`ReadOnly` 支持 true/false、默认 false（候选 10 条全部显式，正确）；Protected client = AppContainer 隔离（Credential/Device/File/Network/Process/Window）且**可能**限制 copy/paste（proposal:62 准确）；`MemoryInMB` 不足时自动提升到最小 2048 MB（smoke 取 2048 不会被上调） |
| [Install Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install)（2026-03-29） | Feature 名为 `Containers-DisposableClientVM`；前置：AMD64、BIOS 虚拟化、≥4 GB RAM（建议 8 GB）、≥1 GB 空闲磁盘、≥2 CPU 核（→ F-05） |
| [git-clone](https://git-scm.com/docs/git-clone)（2.54.0） | 本地路径默认 `--local`，"files under `.git/objects/` are **hardlinked**"；`--no-local` 覆盖默认、改用常规 Git transport；`--no-hardlinks` 改为复制；`--shared` 才会建立 `objects/info/alternates`（候选未用）；`-n/--no-checkout`；"Cloning into an existing directory is only allowed if the directory is empty"（与候选"已存在但可安全判定为空"的放行口径自洽）。→ R-01 的隔离论证成立 |

## 8. 未验证事实与是否阻止本 Review 决策

**不阻止本决策**（它们正是 smoke/Build Gate 要测的对象，且候选已逐项标注 NOT_VERIFIED/NOT_RUN）：

1. `Containers-DisposableClientVM` feature 是否已启用（查询需提权 → UNKNOWN）。
2. `wsb` 在交互非提权 host shell 的可用性与版本（候选记录 `0.8.107.0`，我未复现；DSH 受限 shell 无法验证）。
3. 本机 parser/runtime 是否接受 `<Networking>Disabled</Networking>`（见 F-03；被拒即 BLOCKED，不 fallback）。
4. guest 内 10 条映射的实际可见性/ACL、RO 强制、未映射路径不可见性、default-route/TCP 结果。
5. guest 工具链闭包（含 F-01 git、F-02 MSVC 激活）、cache seed 覆盖完整性、Build 阶段 `MemoryInMB` 最终值与上限。
6. UI 取证链（`computer-use` / `node_repl` + `@oai/sky`）在**执行方**环境是否可用：本 Reviewer 的 skill catalog 中**不存在** `computer-use`，故该工具链可用性记 NOT_VERIFIED；候选已规定"无法绑定窗口/截图即 BLOCKED"（fail-closed），不构成方案缺陷。
7. `MemoryInMB` 可设范围（F-04）。
8. `_cacache`/seed 内容的秘密扫描结果（F-08 补充项）。
9. 环境观察（非候选缺陷）：共享仓库 `G:/CODEX/New Manga/.git` 存在 `refs/codex/turn-diffs/checkpoints/...` 无效对象，导致 `git log --all` 报 `fatal: bad object`；不影响 HEAD/tree 解析与本 Review，但会影响使用 `--all` 的复核命令。

**结论**：以上均不阻止"方案审查通过"，但**均不得**被表述为真实环境 PASS。

## 9. 推荐下一步（可直接转发）

> 将本 Review 转交 Codex。指令：`在 branch codex/P02-process-isolation 上：(1) 在同一 scope（verification/P02/** + P02.md Codex-only boundary 段）内登记 P3 F-01（guest git 输入）与 F-02（MSVC 激活），F-01 若新增 Build 阶段 mapping 必须重冻结并复审 config/hash，smoke config 不因此变化；(2) 生成 smoke pre-start 证据：exact HostFolder manifest（含 F-08 的分级 hash 配方）、冻结 start config 与 canonical SHA-256=dcb95da5…（smoke 前重算）、交互非提权 host shell 身份与 wsb 版本、feature 启用证明、磁盘/CPU/内存阈值（F-05）、UI 取证方法可用性；(3) 依 proposal §Isolation smoke 步骤 1–6 执行一次 smoke，逐项归档 RO 写拒绝/RW canary/未映射 root 与 common .git 不可见/default-route 与 TCP 失败/前后 manifest 对比；(4) 提交固定 commit 与证据，送 DeepSeek Harness 对 smoke 证据做 exact-head 复审。smoke 未通过前不得运行产品 build；build 仍需独立 Build Gate，AC1–AC6 保持 BLOCKED。` 本 Review 不授权 build，也不把任何 NOT_VERIFIED 转为 PASS。
