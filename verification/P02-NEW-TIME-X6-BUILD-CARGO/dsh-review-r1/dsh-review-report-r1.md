# P02-NEW-TIME-X6-BUILD-CARGO — DSH 独立 Initial Review（BC-AC6）

## 0. Review 绑定核实（只读）

| 项 | 期望 | 实测 | 判定 |
|---|---|---|---|
| DSH worktree HEAD | `708ac7938c72fbcccd0d68c7ca60635552cbcaaf` | `.git` → `gitdir: G:/CODEX/New Manga/.git/worktrees/P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW`；其 `HEAD` = `708ac7938c72fbcccd0d68c7ca60635552cbcaaf`（detached） | ✅ 一致 |
| 作者 worktree HEAD | delivery 分支 | `.../P02-NEW-TIME-X6-BUILD-CARGO/HEAD` = `ref: refs/heads/agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO`；该 ref = `708ac7938c72…` | ✅ 两 worktree 同点 |
| delivery_head | `db4870ab…` | Task front matter L17 = `db4870ab87d36f0663b5e45e4f7b2e3cf9b77917`；Handoff L6 同值 | ✅ 回填已生效 |
| 工作区 clean | 应 clean | **不 clean：存在我的探针残留文件（见 §2 污染披露）**；除该文件外无其他 DSH 侧写入 | ⚠️ 见 §2 |

> Review 范围内**未运行**任何构建、cargo test、产品 AC1–AC7、安装包/应用/UI/OS/profile/registry/ACL/API 检查；**未执行** `m2rc1-desktop.exe` 与 `…_x64-setup.exe`；未修改/创建/删除任何交付文件（唯一例外是 §2 披露的探针残留）。

---

## 1. 审查方法与硬性限制（必须先读）

### 1.1 本会话 shell 完全不可用（影响结论强度）

`pwsh` 在**进程启动前**即失败，与命令内容无关：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW)
```

`danger-full-access` 一次性重试被拒（`requires approval, but no approval channel is available`）。因此本 Review **无法运行 git、无法用 Get-FileHash 重算任何 SHA-256**。

**由此产生的结论边界（重要）**：下文所有哈希/字节数均为**多源记录一致性核对**与**非哈希的独立重推导**，**不是**我重算的密码学结果。按 BC-AC7，pins 重算仍必须由 Codex 执行——这一点在 Task 设计中本就是 Codex 的职责，但读者不得把本报告读作"DSH 已重算全部 hash"。

### 1.2 我用只读工具独立重推导出的事实（不依赖 shell）

| # | 独立复核 | 方法 | 结果 |
|---|---|---|---|
| 1 | `desktop-schema.json` 行尾 | `grep "\r$"` | DSH worktree：2579 行全部命中 → **CRLF**；build worktree：254 in 2579 → **CRLF**；`tauri-generated-post-build-r1` 同路径快照：**0 命中 → LF**。CRLF/LF 二分独立成立 |
| 2 | 源 manifest ↔ 换行 provenance | 子代理逐项只读比对 | `files` 数组 **318** 项、无截断；24 条 `frozen_manifest_crlf_bytes/sha256` **24/24 全部一致**（0 mismatch） |
| 3 | `gen/schemas/` 覆盖 | 同上 | 源 manifest 该前缀实为 **4** 项（`acl-manifests.json`、`capabilities.json`、两个 schema），provenance 只列 2 项 → F-08 |
| 4 | Tauri CLI 版本 | 读 `task-envs/.../npm-cache/_npx/269d4a6afb27e793/node_modules/@tauri-apps/cli/package.json` 及其 win32-x64-msvc 包 | **main 与 `cli-win32-x64-msvc` 均为 2.12.2**，`.node` 产物在位 |
| 5 | 缓存隔离（BC-AC4 关键） | glob `task-envs/P02-NEW-TIME-X6-BUILD-CARGO/**`（55,805 路径） | `cargo-home/registry/src/index.crates.io-1949cf8c6b5b557f/…`（真实 crates.io 源码树）、`npm-cache/_cacache`、`npm-cache/_npx/…`、`venv/Scripts/python.exe` 均落在 Task env → **CARGO_HOME / NPM_CONFIG_CACHE / venv 重定向为真** |
| 6 | 前端产物未被改写 | 读 ZCode `01/pre-package-hashes.txt` 与 `02/post-build-verify.txt` | `package.json` `56c9b286…`、`package-lock.json` `520be490…` **构建前后完全相同**；后者与源 manifest 第 35 行 `520be4900b855e…` 一致；`dist/index.html` 276 B/`a05b375c…`、`dist/assets/index-B18Ljq2o.js` 200805 B/`8a4e4252…` |
| 7 | 关键 manifest 条款 | 读 `source-manifest-r1.json` L356–361、L377–382 | `desktop-schema.json`=132848/`71c37b6e…f4ee`/blob `5ac0c11d…`；`ac1_exit.toml`=359/`006f6552…9b99`/blob `22658add…` → 与 provenance r2 完全吻合 |
| 8 | 安装包大小自洽 | 读 `07/stderr.log` | Tauri 报 `554.54 MiB`；`581475034 / 1048576 = 554.5399` ✅ 与 manifest 字节数自洽 |
| 9 | 命令顺序证据 | 读 `07/tool-versions.txt` | pre-Tauri 快照记录 `release/m2rc1-desktop.exe: PRESENT 9368576 / 14DB8EB7…` → **Cargo 产物在 Tauri 启动前已存在**，顺序成立（并引出 F-04） |
| 10 | `run-r1/stderr.log` 字节算术 | 读内容 | 61 字符 + CRLF = **63 B**，与 supplement 声明一致 ✅ |
| 11 | 44 dirs / 87 pyc | `grep "cpython-312.pyc"` = **87**；路径去重前缀计数 = **44** | 与 scope-audit 声明一致 ✅ |
| 12 | 主 checkout 未被 AGY 写文档 | 读 `G:\CODEX\New Manga\doc\tasks\P02-NEW-TIME-X6-BUILD-CARGO.md` | 仍为派发前状态（`status: ready`、`owner: ZCode`、`branch: agent/zcode/…`、`delivery_head: null`）；主 checkout `doc/handoffs` 下**无** BUILD-CARGO Handoff → **实质写入确实落在隔离 worktree**（见 F-12） |
| 13 | 不存在的 Review Task ID | glob `doc/tasks/*BUILD-CARGO*` | 仅 `P02-NEW-TIME-X6-BUILD-CARGO.md`，确认 Handoff 推荐的 `…-REVIEW` Task **不存在**（F-09） |
| 14 | 两版 preflight 的 write scope | 对比 `preflight-live-r2`（ZCode）与 `preflight-antigravity-r1/live-r1-stdout.json` | ZCode 解析为 worktree 路径；AGY 解析为 `G:\CODEX\New Manga\doc/tasks`、`G:\CODEX\New Manga\doc/handoffs`（主 checkout）→ F-12 |
| 15 | AGY 自述 commit 列表 | 对比 `run-r1/stdout.json`、`06/environment.txt`、gitdir HEAD/branch ref | 自述含 2 个**不存在**的 hash（F-05） |
| 16 | 交付产物确实存在 | glob `**/m2rc1-desktop*.exe` | `…\target\release\m2rc1-desktop.exe` 与 `…\release\bundle\nsis\m2rc1-desktop_0.1.0_x64-setup.exe` **均在位**（子代理"exe 不存在"的回报系其 glob 写法错误，**已作废、不采信**） |

---

## 2. Review 自身限制与污染披露

- **探针残留（需人工清理）**：为判定工作区是否可写，我派的探针子代理用 `write` 创建了
  `G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW\.dsh-write-probe.tmp`（内容一行 `probe`）。
  本会话**无 delete 工具且 pwsh 不可用**，我无法自行清除。该文件使"DSH worktree 应 clean"这一绑定条件当前**不成立**（仅此一个 untracked 文件，非交付内容）。**建议由用户或 Codex 执行 `Remove-Item` 清除**，并把它计为本次审查的流程瑕疵，而非交付缺陷。
- **未能重算哈希/git**（§1.1）。
- 一个子代理曾报告"target/release 下 exe 不存在"，经我用多个 glob 复核为**误报**，未采信、未写入结论。

---

## 3. BC-AC1 – BC-AC5 逐项评估

### BC-AC1（冻结输入 / preflight）— **PASS（有证据质量保留）**
- 318 项源 manifest（`source_commit 55ad8205…`、`generator v1`、`frozen_git_checked: true`）+ `supplemental-inputs-r1.json`（3 项 generator 排除 + 4 个外部模型 pin + npm metadata + toolchain）齐备；官方 verifier r4 `verify=PASS / files_checked=318 / problems=[]`，`exit=0`、stderr sha=`E3B0C4…`（空文件），与 `codex-final-verification-r2.json` 记录一致。
- 工具链冻结值与实测一致：cargo 1.98.1(797e8a9bc)、rustc 1.98.1(48a229cea)、node v24.15.0、npm 12.0.1、Python 3.12.3、agy 1.3.5、Tauri CLI 2.12.2。
- npm registry integrity 双向复核：ZCode `00-preflight/npm-metadata/{main,windows}-integrity.txt` 与 supplemental 的 pin **逐字符相同**；AGY `07/tool-versions.txt` 在 Tauri 前再次回显同值。
- preflight：ZCode live r2 `overall=PASS / dispatch_allowed=true`；AGY live r1 `overall=PASS / dispatch_allowed=true`（`attestation.json` = quota OK / permission OK / conversation_usable true）。
- 保留项：AGY preflight 的 write-scope 文本把 `doc/tasks`、`doc/handoffs` 解析到**主 checkout**（F-12，已由 §1.2#12 实证否定实质风险）；AGY 自述 commit 列表含假 hash（F-05）。

### BC-AC2（前端）— **PASS**
命令 `npm ci --no-audit --no-fund`、`npm run build` 记录于 ZCode `run-r1/{01,02}`，Codex 独立 partial verification `result=PASS`。`package.json`/`package-lock.json` 构建前后哈希**完全相同**（§1.2#6），`dist/index.html` + `assets/index-B18Ljq2O.js` 存在且哈希被 AGY 独立重算一致。BC-AC2 的原始记录在 ZCode（`profile: ZCODE_HEAVY` 阶段），不在 AGY 接管范围，AGY 未重跑 —— 符合 Task 约束。

### BC-AC3（sidecar）— **PASS（含一处已记录的环境偏离）**
attempt 1 失败日志与 attempt 2 成功日志分别保留（`05-sidecar-build` 76629 B、`05-sidecar-build-attempt2` 77287 B）；9/9 pip pin MATCH；5 个入口 exe + 4 个权重在 AGY `06/tool-versions.txt` 中**被重新 hash**，与冻结 pin 一致（`037930A8…`、`B6D70793…`、`7E9E2245…`、`944E8114…`）；Codex 记录 5,610 files / 1,296,373,783 bytes 独立校验 PASS。
保留：两 attempt 的 PyInstaller 日志均出现 `C:\Users\49745\AppData\Local\pyinstaller` → 用户 profile 写入（F-02）。

### BC-AC4（Cargo / Tauri / installer）— **PASS（含一处表述精确性保留）**
- `06-cargo-build-attempt2/command.txt` = `cargo build --locked --release`；`stderr.log` 以 ``Finished `release` profile [optimized] target(s) in 1m 10s`` 收尾；`exit.txt`=`0`。
- `07-tauri-build-attempt1/command.txt` = `npx --yes @tauri-apps/cli@2.12.2 build`；`stderr.log` 以 `Finished 1 bundle at: …m2rc1-desktop_0.1.0_x64-setup.exe (554.54 MiB)` 收尾；`exit.txt`=`0`。
- 顺序：07 的 pre-Tauri 快照证明 Cargo 产物已完成（§1.2#9）；prompt 明确"Cargo 失败即停止"，日志未见反向证据。
- 缓存隔离：`environment.txt`（两目录同 hash `CF02BB19…`）列出 TEMP/TMP/PYTHONPYCACHEPREFIX/PYINSTALLER_CONFIG_DIR/NPM_CONFIG_CACHE/NPM_CONFIG_USERCONFIG/NPM_CONFIG_GLOBALCONFIG/PIP_CACHE_DIR/CARGO_HOME 全部指向 Task env；并由 §1.2#5 **独立证实**这些目录真的被写入（cargo-home 含 55,805 路径、npm-cache 含 `_npx` Tauri CLI 2.12.2、venv Python 3.12.3）。
- 产物：exe 9,367,040 B / `92AC7B8E…`，installer 581,475,034 B / `A1DD05B6…`，文件在位（§1.2#16），大小与构建日志自洽（§1.2#8），且与 `build-artifacts-manifest-r1.json`、Handoff、Task Canonical Evidence、`codex-final-verification-r2.json` 四源一致。
- 保留：交付 exe 的哈希是 **Tauri 重编译后**的产物，不是 `cargo build` 自身输出（F-04）。

### BC-AC5（scope / integrity）— **PARTIAL（不可判 PASS；建议"残留接受"闭合）**
拆成两个子句：

1. **"未改生产代码/共享契约/依赖清单/lockfile/构建脚本"** — **证据充分**：
   - `scope-audit-r1.json` 的 `tracked_diff_since_base` 仅列 doc/**、verification/**（无 `src/**`、无 `Cargo.toml/lock`、无 `package*.json`、无 `packaging/**`）；
   - `package.json`/`package-lock.json` 前后哈希不变（§1.2#6）；
   - `--locked` 构建成功 ⇒ Cargo.lock 未被改写；
   - Tauri 生成的 24 个 tracked 文件为**逐文件证明的纯 CRLF/LF 差异**：provenance r2 给出 24 条 `git_blob` / LF / CRLF / 重建 CRLF 的四元组，我复核其中 2 条与源 manifest 完全一致、24 条在子代理逐项核对下 0 mismatch，且 LF 快照 24/24 存在于 `tauri-generated-post-build-r1/**`；作者未自行 restore/clean（符合 Task），Codex 在"逐文件证明"前提下恢复了这 24 条路径的冻结 CRLF 字节（我在 build worktree 独立确认 CRLF）。
2. **"所有产物只在声明的 ignored build 路径产生"** — **不能判 PASS**：
   - 44 个 `src/**/__pycache__` 目录 + 87 个 `.pyc` **位于** scope-audit 自己声明的 `allowed_ignored_roots`（仅 node_modules/、dist/、target/）**之外**；
   - 无运行前 ignored inventory ⇒ 创建/覆盖 **UNKNOWN**（87/87 mtime 落在 2026-10-14 14:55–14:57，处于 ZCode sidecar 构建窗口内，但"Task 之前是否已存在"不可证）；
   - 另有用户 profile 的 PyInstaller 缓存写入（F-02）。
   - 影响评估：两者均为 **ignored、非 tracked、内容无关**（`.pyc` 为 tracked 源码的派生字节码；profile 目录为 PyInstaller 工具缓存），**不进入 Git、不进入 installer payload、不改变任何共享契约或安全面**；因此我判定为**非阻断的残留**，而非"未知来源的源码污染"。

---

## 4. Findings

严重度口径：**无 P0/P1/P2**。P3/P4 记 backlog。

| ID | 严重度 | 位置 / 证据 | 事实 | 影响 | 当前 AC blocker | 最小修复建议 |
|---|---|---|---|---|---|---|
| F-01 | **P3** | `scope-audit-r1.json` L6–8、L535–539；`src/**/__pycache__` | 44 dirs / 87 `.pyc` 落在声明的 allowed ignored roots 之外；无运行前 inventory，来源/覆盖 UNKNOWN | 源码树内出现 ignored 构建残渣；不进入 Git / installer / 共享契约；杜绝"清理即解决" | 否（BC-AC5 设计为 partial→adjudication） | 在 Task Resource Manifest 登记残渣（路径/字节/hash/mtime + 归属 UNKNOWN），确认无 `.pyc` 为 tracked、`src/**` tracked 文件与 HEAD 逐字节一致；随后按"接受残留、不清除"闭合 BC-AC5 |
| F-02 | **P3** | `zcode …/05-sidecar-build/record.txt:12`、`05-sidecar-build-attempt2/record.txt:17` | PyInstaller 缓存写入 `C:\Users\49745\AppData\Local\pyinstaller`（用户 profile） | 违反"不写入用户 profile"的环境隔离要求；来源为 ZCode 阶段（AGY 阶段已 `PYINSTALLER_CONFIG_DIR` 重定向） | 否 | 记为已知偏离；后续构建保持重定向；**不清理**该目录 |
| F-03 | **P3** | `codex-final-verification-r2.json` `worktrees.build_status`（24×` M` + 1×`??`）vs `codex-schema-permission-integrity-r2.json` `disposition` | integrity r2 声明"已恢复为冻结 CRLF"，但 final-verification r2 记录的 tracked 状态仍是 24 条 modified；恢复后的 clean 状态缺单独记录 | 若日后在该 worktree 执行 `git add -A`，理论上可能把换行差异带入提交 | 否 | Codex 补一条 **post-restore** NUL 分隔 porcelain 记录，显式证明这 24 路径 clean（或明确列为待处理残留并指定处置） |
| F-04 | **P3** | `07-tauri-build-attempt1/tool-versions.txt:15` vs `build-artifacts-manifest-r1.json` | pre-Tauri exe = 9,368,576 B/`14DB8EB7…`；交付 exe = 9,367,040 B/`92AC7B8E…`（Tauri 触发重编译并覆盖）。Handoff/BC-AC4 把该 exe 称为"Cargo Release 可执行程序" | 证据表述不精确；功能与安装包不受影响（installer 由同一路径最终 exe 打包） | 否 | 在 Handoff / artifacts manifest 注明"该 exe 为 Tauri build 重编译产物；standalone cargo 输出已被正常覆盖，仅 pre-Tauri 快照留证" |
| F-05 | **P4** | `run-r1/stdout.json` commits[] vs `06/environment.txt` GIT_HEAD、`.git/refs/heads/agent/antigravity/…`、final-verification r2 `build_head` | 自述含不存在的 hash：`8bf60dd944ce2f5b…`（权威 `8bf60dd9636c120e…`）、`708ac7937397e5fc…`（权威 `708ac7938c72fbcc…`） | wrapper 自述不可作 pin；命令/产物哈希不受影响 | 否 | Codex adjudication 以 git/独立记录为准，标注 AGY 自述 commit 列表不可信 |
| F-06 | **P4** | Handoff L5 `base_commit: 04ecc800…` vs Task L13 `base_commit: 49d2a2f9…` | 前者实为 AGY 派发基线，字段语义与 Task 冲突 | 元数据易误读 | 否 | Handoff 拆分为 `source_base_commit` / `dispatch_base_commit` |
| F-07 | **P4** | `antigravity-run-evidence-manifest-r1.json`（15 项）vs 磁盘 `run-r1/**` | `run-r1/exit.txt`（3 B/`13BF7B30…`）存在于磁盘但未列入 manifest，仅由 `codex-run-output-supplement-r1.json` 覆盖 | manifest 非目录全集，闭合依赖 supplement | 否 | 已由 supplement 覆盖；建议后续 manifest 生成改为目录全集 |
| F-08 | **P4** | 源 manifest `gen/schemas/` 共 4 项（含 `acl-manifests.json`、`capabilities.json`）vs provenance r2 只列 24 项 | 两个生成物未被 provenance 显式枚举，仅靠"porcelain 恰好 24 条"隐式覆盖 | 覆盖表述不完整 | 否 | provenance 报告显式声明这两项未变（或纳入 26 项） |
| F-09 | **P4** | Handoff L47；`doc/tasks` glob | 推荐了**不存在**的 Task `P02-NEW-TIME-X6-BUILD-CARGO-REVIEW` | 派发元数据错误 | 否 | 记 backlog；本次 Review 即同 Task 的 BC-AC6，**不新建该 Task** |
| F-10 | **P4** | Task front matter / Canonical Evidence 表 | `reviewed_head: null`、`review_decision: pending`；交付后 Codex 产物（final-verification-r2、schema-permission-integrity-r2、run-output-supplement-r1、tauri-generated-post-build-r1/**）未入表 | `canonical_evidence_status` 无法闭合 | 否 | adjudication 时回填 pins/路径/hash 与 review 结论 |
| F-12 | **P4** | `preflight-live-r2/stdout.json:67` vs `preflight-antigravity-r1/live-r1-stdout.json:68` | AGY preflight 把 `doc/tasks`、`doc/handoffs` 解析到**主 checkout**，ZCode 同项解析到 worktree | 弱化"write scope 冻结于隔离 worktree"的证明文本；**实质风险已否定**（§1.2#12：主 checkout 仍为派发前内容、无 Handoff） | 否 | 修正/说明 preflight 的 write-scope 解析；建议裁决时补一条主 checkout tracked/untracked 状态记录 |

---

## 5. 整体结论

> **APPROVED（无 P0/P1/P2 blocker；附证据补全条件与限制）**

依据：
1. **BC-AC1 / BC-AC2 / BC-AC3 / BC-AC4 = PASS**：冻结输入 318 项与官方 verifier r4 PASS 一致；两条命令顺序正确、均 `exit=0`；缓存/venv/CARGO_HOME/npm cache 被**独立实证**落在 Task env；exe 与 NSIS installer 在位且大小与构建日志自洽；安装包 581,475,034 B / `A1DD05B6…` 与 exe 9,367,040 B / `92AC7B8E…` 在四个独立记录中一致。
2. **BC-AC5 = PARTIAL**，但两个残留（未知来源 `.pyc`、profile PyInstaller 缓存）均为 **ignored / 非 tracked / 内容无关**，**不构成 P0–P2**，且 24 条 tracked 差异已被逐文件证明为纯 CRLF/LF 表示差异并保留 LF 快照。
3. 因此 **BC-AC7 所需的"当前 P0/P1/P2 blocker = 0"在我这一侧成立**；所有发现为 P3/P4，按 Task 规则记 backlog，不要求返修。
4. **限制（不隐藏）**：本会话 shell 不可用，我**未重算任何 SHA-256、未运行 git**；哈希结论为多源记录一致性 + 非哈希独立重推导。**Codex 必须按 BC-AC7 独立重算 pins/scope/闭合性**，不得仅凭本报告的"一致"字样放行。

**BC-AC5 closure 建议（给 Codex adjudication）**：可闭合为"残留接受（PRESERVE_ALL，无内容变更）"，**前提**是补 F-01 的残渣登记 + F-03 的 post-restore tracked 状态两条证据；否则应保持 PARTIAL。**不得**以清理 `.pyc`/profile 缓存来"解决"该不确定性。

---

## 6. 覆盖范围与未覆盖风险

**已覆盖**：Task/Handoff 事实与原创命令；源 manifest 318 项与 24 条换行 provenance；官方 verifier r4；Cargo/Tauri 原始 command/environment/tool-versions/stdout/stderr/exit；artifact 存在性与多源一致性；AGY evidence manifest 15 项 + Codex supplement 闭合；scope-audit 计数；缓存隔离的**文件系统级**实证；两 worktree HEAD；主 checkout 抽查。

**未覆盖 / 明确缺项**：
- **任何 SHA-256 的独立重算**、任何 `git` 命令（`git status/diff/log`）、commit 差异（`708ac793` 是否 docs-only）的独立重推导 —— 缺 shell，只有 Codex 自述 `708ac_changes_only_task_handoff: true`；
- NSIS payload 内部结构、exe 可执行性/签名、安装与运行；
- 产品 AC1–AC7、`cargo test`、UI/OS/profile/registry/ACL/API；
- sidecar 5,610 文件清单的逐项复核（仅依赖 `codex-partial-verification-manifest-r1.json` 的 PASS 记录）；
- 主 checkout 的**完整** dirty/untracked 集合（只抽查了 Task 文件内容与 Handoff 缺失）；
- 44 个 `__pycache__` 之外其它 ignored 路径的完整盘点；
- 我未收到/未使用任何 `review_input_manifest`。

---

## 7. 推荐下一步

1. **立即（人工/Codex，机械清理）**：删除我的探针残留 `G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW\.dsh-write-probe.tmp`，恢复 DSH worktree clean。
2. **Codex 执行 BC-AC7 adjudication**（`evaluate-result` / `classify-revision` / `decide-convergence.py --mode converge`），输入＝本报告 + F-01/F-03 两条补证：
   - 重算全部 pins（本报告未重算，不可替代）与 `reviewed_head`/`delivery_head` 差异；
   - 记录 BC-AC5 为"PARTIAL-resolved: accepted residual"，并把 F-01/F-02/F-04/F-05/F-06/F-07/F-08/F-09/F-10/F-12 作为 backlog 写入 Task 状态；
   - 在 Task front matter 回填 `reviewed_head: 708ac7938c72fbcccd0d68c7ca60635552cbcaaf`、`review_decision` 与新增 Codex 证据 pins。
3. **暂不派发下游产品 AC1–AC7 Task**：本轮已满足"P0/P1/P2=0"，是否放行产品 AC 由 Codex 按 convergence 决定；在 BC-AC5 的两条补证落地前，不应把 Build/Cargo 标为 done。

**可直接转发给 Codex 的指令**

```
请对 Task P02-NEW-TIME-X6-BUILD-CARGO 执行 BC-AC7 adjudication（official evaluate-result / classify-revision /
decide-convergence.py --mode converge），输入为 DSH BC-AC6 Review 报告。
绑定：delivery_head=db4870ab87d36f0663b5e45e4f7b2e3cf9b77917，reviewed_head=708ac7938c72fbcccd0d68c7ca60635552cbcaaf。
必须：① 独立重算 source-manifest/supplemental/build-artifacts/antigravity-run-manifest/supplement 全部 pins
（DSH 侧沙箱不可用、未重算任何 SHA-256，不得引用其"一致"作为验证）；② 核实 708ac793 相对 delivery_head 仅
doc/tasks+doc/handoffs 的 delivery_head 字段变化；③ 就 BC-AC5 补两项证据后按"残留接受、PRESERVE_ALL、不清理"
闭合：(a) 补一条 post-restore NUL 分隔 porcelain 记录证明那 24 条 tracked 生成路径 clean，
(b) 在 Resource Manifest 登记 44 个 src/**/__pycache__ / 87 .pyc 与 C:\Users\49745\AppData\Local\pyinstaller
的路径/字节/hash/mtime 及归属 UNKNOWN；④ 把 F-01/F-03/F-04/F-05/F-06/F-07/F-08/F-09/F-10/F-12 记为 backlog；
⑤ 不运行 cargo test / 产品 AC1–AC7 / 安装包 / 应用 / UI/OS/profile/registry/ACL/API；⑥ 回填 Task front matter 的
reviewed_head 与 review_decision，并处置 build worktree 内未跟踪的 codex-schema-permission-integrity-r1.json。
另请人工删除 DSH worktree 内的审查探针残留 .dsh-write-probe.tmp。
```
