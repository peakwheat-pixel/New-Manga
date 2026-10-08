## M2-RUNNER-SNAPSHOT-DEBT 非作者独立 Review

**Reviewer 身份**：真实 DeepSeek Harness（非作者），角色限定为"技术实验 / 测试 / Bug 分析 / 独立 Review"。
**Owner**：Codex；**Integrator**：Codex。本报告不构成作者自批。
**审查方式**：**纯静态源码审查**＋对父侧（Codex）已落盘证据日志的交叉核对。**本轮我没有任何命令执行能力**（见 §0），因此**没有复跑任何 runner / 构建 / 检查**，全部"PASS"均为**父侧执行日志记录**，不是我的复跑结果。

| 固定项 | 值 |
|---|---|
| base | `968c8f34601b72667831f1fd15bb20cd2c8f3cb7` |
| reviewed_head | `7556cb2dbfb8077e2ff62532d010f0d545733f52` |
| 固定构建源码 head | `cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2` |
| 实现代码 commit | `d1c279db45904c6009dbc696d95a0b4a63ebd837` |
| branch / worktree | `codex/M2-RUNNER-SNAPSHOT-DEBT` / `G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex` |
| 唯一仓库 common-dir | `G:/CODEX/New Manga/.git` |

我用只读手段独立解析的真实引用（不依赖任何 Git 命令）：
`G:/CODEX/New Manga/.git/worktrees/RUNNER-SNAPSHOT-DEBT-codex/HEAD` → `ref: refs/heads/codex/M2-RUNNER-SNAPSHOT-DEBT`；ref 文件 → `a23a5333d00bfb3a54d3df45664b3810e3f7e6a1`。
`G:/CODEX/New Manga/.git/logs/refs/heads/codex/M2-RUNNER-SNAPSHOT-DEBT` 的 reflog 实测链路：
`968c8f34 →（ff）1ac7aa83 → a1705fbe → b3860981 → d1c279db（fix 实现）→ cfb5d2ee（test: 采集完整 fixed-head 证据）→ 7556cb2d（docs: 交付）→ a23a5333（docs: 保留原始 Windows 日志）`。
**结论：reviewed_head 是构建源码 head 的直系子提交，两者确为"代码 head + 治理/日志追加"关系；但"只差治理/日志"这一步**内容**上的验证我无法在本地完成（见 F-17）。**

---

### 0. 本次审查的能力边界（必须显式声明，避免伪造执行）

- `pwsh` 后端在本会话**完全不可用**：沙箱在工作区上 `grantWrite` 失败（`SetNamedSecurityInfoW failed (Win32 5)`），`workspace-write` 重试同样失败，`danger-full-access` 升级"无审批通道"被拒。**因此我未执行 `git`、未运行任何测试、未打开任何 exe、未哈希任何 installer。**
- 我的所有结论来自：`read` / `grep` / `glob` 可读的**文件内容**（含 `.git` 下的 HEAD/refs/reflog 明文）、以及**父侧已落盘的原始日志**。
- 边界声明：**我不会把父侧日志中的 `EXIT=0`、`GATE PASS` 声称为我复跑所得**；反过来，我读到的所有数字（计数、SHA、EXIT、判词）都按"父侧记录、与其它记录互证程度"评估。

**一个必须自曝的副作用（erratum）**：为准备暂存脚本我误调用了文件创建，产生了**唯一一个多余的未跟踪空文件**——`verification/M2-RUNNER-SNAPSHOT-DEBT/raw/_pytmp_placeholder.txt`。我已把内容改写为自述删除说明；**它不属于本轮证据，需删除**：
`Remove-Item "verification/M2-RUNNER-SNAPSHOT-DEBT/raw/_pytmp_placeholder.txt"`。除此之外我没有修改任何被跟踪文件、没有 commit、没有合并、没有改动依赖／产品／用户数据、没有调用任何其他 agent、没有输出凭证。

---

### 1. 两处快照修复（AC2 核心，逐条核对到行）

**1.1 packaged runner：请求 minor 3 保留、响应严格 1.6** — 与授权口径逐字相符
`packaging/m2ac5/run_clean_start_e2e.py:443-453` 注释明确"Keep the minor-3 request as a backwards-compatibility probe. The response must still declare the current protocol 1.6."，三封信封（`core.ping`/`ListBooks`/`core.shutdown`）全部使用 `{"major": 1, "minor": 3}`（`:448`）。
`run_library_probe` 的判词在 `:497-504`：
```
ping.get("error") is None
and ping_result.get("status") == "ready"
and ping_result.get("protocol_version") == {"major": 1, "minor": 6}
and "library.list_books" in (ping_result.get("capabilities") or [])
```
即**请求侧兼容保留（不挑 minor）、响应侧严格等于 1.6**，方向没有搞反。
服务端契约独立核对成立：`src/bootstrap/core_service.py:168 PROTOCOL_MINOR = 6`；`core.ping` 响应在 `:1176-1184` 直接回 `{"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR}`；版本校验（`:1151-1157`）**只校验 major**，所以 minor=3 的请求**合法且被接受**——这正是"兼容探针"的语义基础，不是把产品 wire 变更误判。CS-L1 在父侧安装态实测 PASS，`raw/packaged/cleanstart-gate.json` 记录 `protocol_version {"major":1,"minor":6}`。

**1.2 M2-RC2 runner：生产 9 → 15 且精确有序、probe 保持 7**
`verification/M2-RC2/run_e2e.py:312-328` 的 15 条，与 `apps/desktop/src-tauri/src/main.rs:53-77` 的 `PRODUCTION_COMMANDS` **逐项、逐序完全一致**（我逐条比对：`issue_resource_url, revoke_ref, revoke_resource_refs, core_ping, library_list_books, settings_get, settings_update_section, set_region_type, list_regions, list_region_revisions, restore_region_revision, rerender_page, resolve_page_resource, list_chapters, list_chapter_pages`）。
`PROBE_EXPECTED`（`:332-340`）仍为 7 条且与冻结历史原文一致：`raw/dev-runner-m2rc2.log`（GC-2 旧日志，字节未改）第 23 行 `[m2rc2-allowlist] probe:...` 与 `:43` 的 `PASS: probe allowlist exactly [...]` 完全对应。
**fail-closed 未被放宽**：`:448` 与 `:479` 都是**列表整体有序相等**（`commands != PRODUCTION_EXPECTED` / `!= expected`），`ALLOWLIST_RE = re.compile(r"\[m2rc2-allowlist\] (probe|production):(.*)")`（`:297`）无 `$` 锚但在 `split(",")`＋全等比较下**不可能被长度/包含关系绕过**；`check_announcement` 的 probe/production **模式互斥校验**（`:477-478`）也在。
**旧 FAIL 的原始载体未被改写**：`verification/M2-DERIVED-GC-2/raw/dev-runner-m2rc2.log:49` 仍在，原文就是 `announced [...15 条...], expected [...9 条...]` → 这正是"漂移确实存在、且该断言确实有判别力"的历史见证。我另外确认了 `verification/M2-RC2/raw/` 目录内**只有迁移前 `history-index-before.txt` 所列的历史文件，没有任何本轮新产物**。

**1.3 两处修复会不会是 packaged AC1 失败的因？——独立排除**
`packaging/m2ac5/core_sidecar.spec` 的 `ENTRIES` 只分析 `packaging/m2ac5/entries/*.py` + `pathex=[src]`，`Analysis()` 的源面**不包含 `packaging/m2ac5/run_clean_start_e2e.py` 与 `verification/**`**；`tauri.conf.json:31` 只把 `target/core-sidecar/core-sidecar` 映射为 `resources/core-sidecar`。两个 runner 是**验收工具**，不进安装包。→ **runner 快照改动与安装态 QtGui 导入失败之间不存在构造性因果通路**，作者的"非旧 minor3 快照失败、具体原因 UNKNOWN"是诚实的。

**1.4 一个历史对照（我实测，重要）**
`verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/tenth-round-build-and-run.log`：`[PASS] CS-A1-run1-completed {"exit":0,"phase":"run1"}`、`[PASS] CS-A1-run2-completed`，且 **唯一 FAIL=CS-L1**（`protocol_version {"major":1,"minor":6}` —— 即旧 runner 期望 1.3 而实际 1.6）；`second-round-full-stdout.log:10-11` 的 CS-A1-run1/run2 亦为 PASS；`build-chain.md:145,149` 记录第 4~10 轮稳定为"25 项 PASS、唯一 FAIL=CS-L1"。
**含义**：在 GC-2 的第 2/4/…/10 轮相同宿主、相同 build venv（`m2ac5-build`，PyInstaller 6.22.3）下，**acceptance_bridge 的 QtGui 是能起来的**。这是"同一宿主上曾经工作"的有力对照，指向**本轮 fresh 构建/安装链的环境性回归**，而不是产品源码回归。**但这仍是静态证据推断，不是复现实验。**

---

### 2. `--output-dir` 与自有 lab/install 隔离（AC5 核心）

- `verification/M2-RC2/run_e2e.py:502-506`：新增 `--output-dir`（`type=Path, default=RAW`），`RAW = args.output_dir.resolve()`，`RAW.mkdir(parents=True, exist_ok=True)`；**lab 由 `tempfile.mkdtemp(prefix="m2rc2-lab-")`（`:505`）每次执行自有**，不再复用 `%TEMP%/m2rc2-lab`。
- `packaging/m2ac5/run_clean_start_e2e.py:738-743`：新增 `--output-dir`（`default=RAW`）＋`RAW = args.output_dir.resolve()`；`lab = tempfile.mkdtemp(prefix="m2ac5-cleanstart-")`（`:743`），`install_dir = lab / "install"`（`:761`，且 `:764` 对 `/D=` 空格 fail-closed）。
- 父侧实跑证据与源码一致：`raw/dev-runner.log`/`dev-runner-r2.log` 命令含 `--output-dir verification/M2-RUNNER-SNAPSHOT-DEBT/raw/dev[-r2]`；`raw/packaged-runner.log` 含 `--output-dir .../raw/packaged` 且 lab=`%TEMP%\m2ac5-cleanstart-k50b12ik`。
- **保护历史字节的正确性**：我逐项对照 `history-index-before.txt`（172 行，列出 `doc/reviews/M2-DERIVED-GC-2-*`、`verification/M2-AC5/raw/*`、`verification/M2-DERIVED-GC-2/raw/*`、`verification/M2-RC2/raw/*`）与现存文件清单，**未发现任何被本轮输出新增/覆盖的痕迹**；`build-generated-normalization.json` 也把 Tauri 生成文件的 LF/CRLF 往返显式登记为"已断言内容等价后恢复"。
- **用户/宿主保护**：`CS-Z1-install-dir-zero-write {changed_entries: []}`、`CS-Z4-host-real-appdata-untouched {changed_entries: [], files: 4}`、`CS-Z2-user-source-files-byte-identical`、`CS-Z3-no-surviving-sidecar-processes`（四个 sidecar 全 0；`python.exe: 6` 为宿主自身进程，runner 已在 `:846-861` 注释为 record-only）在父侧日志中均为 PASS。

---

### 3. 最小 12 实际谓词检查的判别力评估（AC3）

**有判别力的部分（成立）**
`check_snapshots.py:58-81` 用 4 个 `response_version` ∈ {`1.6`(真值), `1.3`, `1.7`, `None`} 驱动**真实**的 `run_library_probe`：`assert (ping["status"] == "PASS") == (response_version == version)`。
→ 旧 minor（1.3）、新 minor（1.7）、字段缺失（None）都会把 CS-L1 判成 FAIL，**正确拒绝**；只有 1.6 PASS。这正是"不把 minor3 请求误判、但响应必须 1.6"的判别内核，且用的是实现里**真的**那个谓词（通过 `ast` 抽取 `Gate`/`run_library_probe` 并用 `SimpleNamespace(Popen=..., PIPE=-1)` 桩掉进程），不是复制的假测试。
命令面侧 `cases = [frozen, frozen[:9], frozen+["unexpected"], frozen[::-1], frozen+["probe_exit"], []]`（`:47-52`）覆盖**正确/截断 9 条/多一条/逆序/混入 probe/probe 列表被当生产**六种，全部按 `==` 期望 `commands == frozen` → 6 条，加 probe 2 条、版本 4 条，合计 **12** 与 `raw/check-snapshots.log:16` 的 `PASS: 12 actual-predicate cases` 相符，EXIT=0 亦相符。

**判别力缺口（不构成阻断，但必须登记）**
- **F-01（P3）**：`frozen` 是**从被测实现 `main.rs:53-77` 里正则抽出来的**（`:30-33`），再与 runner 内联的 15 条做全等——对"**顺序/内容**"这条轴，检查对象与 oracle 同源，**不是独立冻结来源比对**（Task doc:54 要求"对比独立冻结来源"）。真正留住了顺序/内容判别力的是**运行时**那条门（§1.2 的 `interactive-production-surface` 与 probe 公告），并且 `raw/dev-runner-m2rc2.log:49` 证明它**曾经真的 FAIL 过**，所以整体断言不是空转。建议（有界）：把 15 条**独立列出**（或引用契约 §5 的冻结清单）作为比对源，而不是从实现里抽；至少给 `frozen` 落一行来源说明。
- **F-02（P4）**：静态分支未断言 `capabilities == ["library.list_books"]`（桩回包固定带该值，故该维度在静态检查中是常量、无判别力）；运行时 CS-L1 已断言，影响有限。
- **F-03（P4）**：`frozen + ["probe_exit"]` 这个"probe 混入"用例在等值比较下等价于"多一条命令"，并不真正检验 probe 语义；真正的 probe 反向用例是 `:53-56`（probe 公告被当生产 → `not ...` 成立）。

### 4. allowed_paths / 范围

- Task doc `allowed_paths`（:63-72）恰含 `packaging/m2ac5/run_clean_start_e2e.py`、`verification/M2-RC2/run_e2e.py`、`verification/M2-RUNNER-SNAPSHOT-DEBT/**`、`doc/tasks/M2-RUNNER-SNAPSHOT-DEBT.md`、`doc/handoffs/M2-RUNNER-SNAPSHOT-DEBT-*.md`、`doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-*.md` 与 Codex 治理四件套。
- 我核对到的本轮新文件与改动对象**全部落在允许面内**：两个 runner、`verification/M2-RUNNER-SNAPSHOT-DEBT/**`（含本审查目录）、task doc、handoff、四个治理文件；**未发现新增依赖、Schema、`src/**`、`apps/**`、`tests/**`、打包 spec/build 流程的改动**（`build_sidecar.ps1` 原文未改：PS5 失败后 PS7 用同一未改脚本仍报 `Get-FileHash` 路径，见 `raw/sidecar-build.log:560-566` 与 `raw/sidecar-weights-retry.log`）。
- **F-04（P3，证据绑定缺口）**：Task doc:132 声称"含日志 harness 的固定 head=cfb5d2ee"，Handoff:16 又写"后续只提交文档/日志"，但**本轮证据里没有一份 `git diff cfb5d2ee 7556cb2d`（或 `--name-only`）的落盘输出**，也没有 `7556cb2d` 的 `rev-parse` 落盘。reflog 只能证明**父子关系**，不能证明**内容只差文档/日志**。我的静态分析给出的是**强间接证据**（实现 commit `d1c279db` 在 `cfb5d2ee` 之前；`7556cb2d` 的 message 为 `docs:`；两个 runner 不进安装包）。建议 Integrator 在集成前落一份 `git diff --name-only cfb5d2ee 7556cb2d`（期望仅 doc/verification）。

### 5. 证据与固定 head/SHA 的对应

| 断言 | 我的核对结果 |
|---|---|
| 所有本轮日志绑定 `HEAD=cfb5d2ee` | **成立**。`raw/npm-ci.log`、`frontend-build.log`、`check-snapshots.log`、`dev-runner.log`、`dev-runner-r2.log`、`sidecar-build.log`、`sidecar-weights-retry.log`、`nsis-build.log`、`packaged-runner.log` 的文件头 `HEAD=` 全为 `cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2` |
| installer SHA 单一真值 `1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8` | **成立（四份独立记录互证）**：`build-fingerprint.json:4`、`raw/packaged/cleanstart-gate.json:4`、`raw/packaged-runner.log:7` 的 `CS-E2-installer-present`、Handoff:54、`result-summary.json:11` 完全一致（我无法自行哈希该 589,904,619 B 文件，故只做互证） |
| dev Gate 10/10 + probe 13/13 | **父侧记录，自洽**：`raw/dev-r2/e2e-gate.json` 10 项全 PASS、`failed: []`、`probe_statuses {"PASS": 13}`、`probe_missing_ids/unexpected_ids/non_pass_ids` 全空；`result-summary.json` 与 Handoff:36 口径一致 |
| packaged 20 PASS + 1 FAIL，之后 5 项 NOT_RUN | **父侧记录，自洽且未粉饰**：`packaged-runner.log` 逐项列出 21 个判词（20 PASS/1 `CS-A1-run1-completed` FAIL），`result-summary.json:13-19` 显式列出 5 个 `not_run_after_ac1_run1_failure`；代码侧确证后续判词**不可能被执行**——`run_ac1_phase:623-624` 在 run1 无 payload 时**直接 `return`**，故 `CS-A2/A3/A4/A5` 连 `record` 都不会发生 |
| 旧日志原字节 | **强证据成立**：`raw/dev-runner-r2.log` 我的 `read` 直接报 `invalid UTF-8 text`（PowerShell 重定向的原生编码细节），与"未做空白/编码归一化"的声明一致；GC-2 旧日志 `dev-runner-m2rc2.log`、`tenth-round-build-and-run.log` 仍保留原文 FAIL |

**F-05（P3，QtGui 失败的定位缺口，虽属 workaround 记录但影响可复现性）**：`raw/packaged-runner.log:30` 记 `CS-A1-run1-completed {"exit": 1}`，而 `raw/packaged/cleanstart-ac1-run1-stdout.log` 头部是 `exit=1` + 立即 `ImportError: DLL load failed while importing QtGui`；Handoff/Task doc 的口径是"AC1 run1 无结果、既有 240 秒上限超时退出"。二者**并不矛盾但缺一个中间量**：`run_app`（`:372-390`）在超时分支 `kill()` 后返回 `proc.returncode`，理论上会返回非 0（如 1），所以"先超时被 kill、返回码恰为 1"也能自洽；但**"run1 是瞬间退出还是被 240s 上限杀掉"在证据里没有明确时间戳**，而 `EXIT=1; ELAPSED=312.8s` 与"run1+run2 两次上限"或"probe 上限 + run1 上限"的算术对不上。建议补一行 `run_app` 起止/`ELAPSED` 明细。**这不影响"未宣称 PASS"的诚实性**，只影响后续诊断的起点定位。

### 6. 证据诚实程度评估（总体：高，且未粉饰）

正面证据（我逐条验证过，非采信）：
1. **明确写了 NOT_RUN**：Task doc:57,143-146、Handoff:36,57-58、`result-summary.json` 三处一致列出 AC4=FAIL/BLOCKED、AC6=PENDING、5 项 NOT_RUN；**没有把 20 项 PASS 说成整个 Gate 通过**。
2. **主动自曝过程瑕疵**：Handoff:46-47 记初次 dev EXIT1（fresh checkout 无 sidecar）、PS5 `Get-FileHash` 失败整条 EXIT1；`baseline-evidence.md:11-12` 甚至自曝一次错误相对路径的 harness 调用与两次 JS 模板解析失败"未写任何文件"。这种自曝提升可信度。
3. **UNKNOWN 就写 UNKNOWN**：Handoff:67-68、Task doc:141-142 明确"具体 DLL/root cause UNKNOWN"，`checkpoint.md` 亦同。
4. **不含未跑的宣称**：Handoff:42-43 明确"没有全仓 pytest/vitest 复跑声称，没有干净 Windows 机/分发迁移保证"；`check_snapshots.py:84` 自己打印 `no product/runtime claim`。
5. **AC4 部分 PASS 的口径经我独立复核成立**：CS-L1 严格 1.6 在 `cleanstart-gate.json:65-80` 为 PASS，与"旧 minor3 快照失败"**明确区分**。

瑕疵（均为措辞精度，非事实虚构）：
- **F-06（P4）**：Handoff:49 说 PS7"复用本次 fresh bundle 完成两组模型哈希校验与复制"，但 `raw/sidecar-weights-retry.log:3` 的命令是 `[".../pwsh.exe","-NoProfile","-File","packaging/m2ac5/build_sidecar.ps1"]`（**去掉了 `-Force`**），第 4 行即 `target exists, skipping (use -Force to rebuild)`。即 PS7 只跑了 **skip 路径的 weights 段**（这是脚本设计内的行为，`build_sidecar.ps1:164-179`），并未重跑 PyInstaller。这不是造假，但"复用/跳过"的区别应写清，否则未来读者会误以为 PS7 重跑了整个构建。

### 7. 停止结论是否正确

**正确，且我独立复核后同意**：
- AC4 在 `run_clean_start_e2e.py` 的实际语义是**单一 verdict**（`Gate.verdict`：`FAIL` 一旦出现即 FAIL，`main` 返回 1），且 AC1 的 5 项判词依赖 run1 payload 才可能执行。父侧结果 = `CS-A1-run1` FAIL → 后续 5 项结构性地不可能运行 → **完整 packaged Gate 未通过**，与 `Task doc:55-57` 的 AC4 定义（"全 Gate 通过含 CS-L1；fresh 构建与固定 head/installer SHA/执行日志相互绑定"）不符。
- 因此 `TaskStatus=blocked` / `ExecutionState=CHECKPOINTED`、不合并主线 runner 实现、不伪造 done——**与证据一致，没有过度声明**。
- 额外支撑（我实测的 `tenth-round` 对照，见 §1.4）表明 AC1 在本宿主历史上是能过的，进一步说明"停在 blocked 并另开诊断"比"就地放宽 Gate"更符合事实；`build-chain.md:145,149` 也显示历史每轮都是"25 PASS + 仅 CS-L1 FAIL"。

### 8. 结论

#### 8.1 实现代码审查结论（本次静态审查可给的部分）
**`approve_with_conditions`（对两处快照修复 + 隔离 + 判别检查这一"实现面"）**
理由：两处漂移的修复**方向正确、内容与冻结面逐字逐序一致、fail-closed 未放宽、probe 7 条未动、输出/lab 隔离成立、历史字节未见改动、无产品/依赖差量**；**0 × P0 / 0 × P1 / 0 × P2**。条件（都不阻断合入，但应在集成前落实）：
- C1 落盘 `git diff --name-only cfb5d2ee 7556cb2d`，证明 reviewed_head 与构建源码 head 只差治理/日志（F-04）。
- C2 `check_snapshots.py` 的 15 条比对源改为**独立冻结来源**（或在文件中注明 `frozen` 来自实现），使序列轴具备独立 oracle（F-01）。
- C3 措辞/记录修正：PS7 skip 路径（F-06）、`run_e2e.py` 文档串与 usage 补 `--output-dir`（F-07）、run1 超时/返回码时间线（F-05）。
- C4 清理我误留的空文件 `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/_pytmp_placeholder.txt`。

#### 8.2 整个 Task 结论（能否批准/集成）
**`blocked` — 因 AC4 不能满足，本 Task 现在既不能 done、也不能集成。**
**作者不得用本次静态批准豁免 AC4**：我**没有**复跑 dev/packaged Gate，我的结论**不是**"验收通过"；`approve_with_conditions` 只覆盖"修复代码本身写对了"，**不覆盖** `packaged AC1 / 完整 Gate`，也不覆盖 AC6（真实非作者审查＋Codex 集成后检查闭合）。

**确切解除条件（全部满足才可回到 AC4/AC6 收口）**：
1. **先由 Codex 冻结并释放一个独立任务**（Handoff 建议名 `M2-PACKAGED-AC1-DLL-DIAG`，Owner=DSH、Reviewer=Codex、Integrator=Codex，仅只读诊断）：只跟踪安装态 `acceptance_bridge.exe` 的 `import PySide6.QtGui` 的 `DLL load failed`（`raw/packaged/cleanstart-ac1-run1-stdout.log:8`），定位到**具体 DLL**或明确写 UNKNOWN + 最小修复范围。
   - 我给出的诊断起点（静态，供该任务验证，**不是结论**）：目标 bundle 里 `Qt6Gui.dll / QtGui.pyd / pyside6.abi3.dll / MSVCP140*.dll / VCRUNTIME140*.dll / plugins/platforms/qwindows.dll` **均已存在**（`target/core-sidecar/core-sidecar/_internal/PySide6/**` 与 `target/release/resources/core-sidecar/_internal/PySide6/**` 实测存在），`warn-archive/warn-acceptance_bridge.txt` 也**没有** PySide6 shiboken 缺失项 → 更像"**fresh 全新构建 + PS5 半程失败后 PS7 skip 复用**"这条链上的环境/打包差异。**高价值差分实验**：与 GC-2 第十轮（`258ca6fe`，同宿主、同 `m2ac5-build` venv、PyInstaller 6.22.3，AC1 run1/run2 均 `exit=0`，`tenth-round-build-and-run.log:726-727`）做**安装目录 DLL 清单 + 版本**逐项差分；`-Force` 全量重建一次做验证性对照（**不删用户文件、不改 PATH 绕过 Gate**）。若诊断为环境性，则**不属于本 Task 授权范围内的 spec/依赖/入口修复**，需另开范围。
2. 修复或环境澄清后，在**固定 head**（新 head 需重新记录）上**全量 fresh 重建**，并**真实重跑** `verification/M2-RC2/run_e2e.py`（10/10）与完整 packaged `run_clean_start_e2e.py`（**21/21，含 CS-L1 与新判词**），并保证 installer SHA/日志/head 互证。
3. 事后把 dev+packaged 两次完整 Gate 的原始日志、installer SHA、新 head 与 `git diff --name-only` 绑定落盘，再交**真实 DSH 非作者 re-review**（本报告不可复用为新 head 的审查），最后 Codex 集成验证后检查闭合。

**我未做的事**：未改任何文件/依赖/用户数据、未 commit、未合并、未调用其他 agent、未输出凭证；除 §0 自曝那一个空文件外无任何写入。

---

无需下一步操作（本报告即为本 Task 在 AC6 上应交付的非作者审查输入）；若要继续推进，唯一有效动作是上面的第 1 步——由 Codex 释放独立诊断任务。