---
task_id: SIDECAR-REBUILD-1
reviewer: reviewer-sid
reviewer_kind: subagent
author: DSH
base_commit: 6ad457c62
reviewed_head: ae9231c3a
reviewed_at: 2026-11-17T17:36:27+08:00
decision: REJECTED
---

# Review：SIDECAR-REBUILD-1 收口（closed_with_limitations）

## 0. 结论摘要

- **reviewed_head**：`ae9231c3a`（main，包含本卡收口提交）。
- **reviewer**：`reviewer-sid`，独立上下文子 agent；**未参与** `SIDECAR-REBUILD-1` 的实现、诊断、返修或收口。
- **decision**：**`REJECTED`**（针对**当前这份收口记录**，不是对 sidecar 重建结果的否定）。
- **P0 / P1 / P2**：**2 / 4 / 4**。
- **核心实测**：
  1. 卡面称“13 个失败未修”，但 reviewed_head 用新 sidecar 跑夹具模式：`CoreClient 258/0/0/258`、`Host 364/0/44/408`，**13 个失败测试全部通过**（定向 `4/4` + `9/9`）。不是本卡修的：Host 9 由 `CORE-PIPE-EXCLUSIVE-1`（E-6，集成 `dff3d41a5`）修复；CoreClient 4 由 `2026-11-16` 的测试返修提交改为按实际能力分支。**“13 个失败”已不是当前事实。**
  2. 卡面称 `yolo11s-seg.onnx` “全工作区不存在、需用户提供”，但该文件实际存在于构建脚本期望的路径：`G:\CODEX\New Manga.workspace\task-envs\M2-SFX-DETECT\weights-v2b\yolo11s-seg.onnx`（40,824,255 B，sha256 `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`，创建时间 `2026-11-16T03:35:54+08:00`）；当前 bundle 内同名文件同哈希。**“缺失”不成立。**
  3. AC5 三项目在 reviewed_head 的**干净重跑**复现卡面数字：`Host 334/0/74/408`、`CoreClient 227/0/31/258`、`App 962/0/11/973 ⇒ 1523/0/116/1639`，三项目 EXIT 0；但首次重跑 Host 为 `333/1/74/408` EXIT 1，失败是无关的 `HostFileIdNormalizationTests` 环境探针 flake（两次全量重跑恢复 334/0）。AC5 数字可复现但**不是确定性的**。
  4. `RESOURCE-MANIFEST.json` 的 sha256 **完全一致**：`54096522b0a16c52b783ad64cc0e44bdff2625db6df6661da22de39c54202170`；3 个 destination 均存在；但 manifest 只登记 **2 个** resource，未覆盖第三个 destination（bundle）。
  5. `check.ps1 -TaskPath doc/tasks/SIDECAR-REBUILD-1.md`：`Governance check: PASS (3 warnings)`，**EXIT 0**。

**明确回答：该卡不能按当前这份记录保持 `closed_with_limitations`。** 当前记录的两条决定性理由（13 个失败未修；SFX 权重缺失需用户提供）均与 reviewed_head 实测相反。状态是否仍取 `closed_with_limitations`、还是可升为 `done`，应由 Lead 在**重写记录、重跑并更新 AC4/AC5 证据**之后裁决；本复核不代签。

---

## 1. 范围、身份与方法

- 只读复核；除本报告外**未修改**仓库文件；未提交、未推送、未 checkout；未修改任何测试 gate 或产品源码。
- 测试证据写入 `G:\CODEX\New Manga.workspace\tmp\review-sid\`（AC5）与 `...\tmp\review-sid\ac4-fixture\`（夹具复测）；报告落盘前 `git status --porcelain` 为空。
- 已实测：AC1 的 `pip-freeze.txt` 与 `requirements-build.txt` 对照；AC2/AC3 的 sidecar 产物、build manifest、直接 NDJSON probe；AC4 的夹具模式全量；AC5 的无夹具三项目全量；AC6 的 11 个相关提交逐提交文件清单；15 行 Canonical Evidence 的 BLOB 哈希；Resource Manifest 的 sha256 与 3 个 destination；治理门禁。
- 未审到/未执行：带新 sidecar 的 `App.Tests` 7 个 sidecar 测试；用新 sidecar 重跑 publish 冒烟；sidecar 全量命令面的逐命令穷举（AC3 只实测了 capabilities、`ReorderChapters`、`ListTrash` 与 README 已列命令）。
- 本复核以 `git cat-file blob ce0cc85c1:<path>` 作为 BLOB 基准；卡面 `sha256_basis: BLOB`，因此工作树 CRLF 差异不构成哈希不匹配（见 §4）。
- **审查期间 HEAD 前进**：复核启动时 `HEAD=ae9231c3a`；复核过程中出现并发提交 `ba215b823`（`docs(reviews): 落盘 Codex 裁定（CORE-ENV-2 / FEA11 / Gate 条件 3-4-5）`，只新增 `doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` 102 行）。该提交不触及本卡、`verification/SIDECAR-REBUILD-1/**`、SFX 或测试；本报告的所有判定仍固定对 `ae9231c3a` 有效。若 Lead 要求把复核绑定到新 head，应以同一口径重跑并另写复审，不覆盖本报告。

---

## 2. 五项逐条判定

| 项 | 判定 | 依据（摘要） |
|---|---|---|
| 1. AC 真实性 | **FAIL（部分项不成立）** | AC1/AC3 成立；AC2 证据对应 11-15 的失败构建，不是 11-16 实际 bundle；AC4 的“13 failed”在 head 已不成立；AC5 数字可复现但首次重跑 1 failed（无关 flake）；AC6 结论成立但提交清单错误。 |
| 2. Canonical Evidence 15 行 | **PASS** | 15/15 路径存在，15/15 sha256 与 `ce0cc85c1` 的 BLOB 一致；§4 抽 8 行逐项列出。 |
| 3. Resource closeout | **FAIL（覆盖不完整）** | `RESOURCE-MANIFEST.json` sha256 与卡面完全一致；3 个 destination 均存在；但 manifest 只登记 2 个 resource（证据目录 + 构建 venv），未登记第三个 destination（bundle，1,967 文件 / 875,823,531 B）。 |
| 4. 收口是否成立 | **FAIL** | 13 个失败在 head 已全部通过（Host 9 由 E-6 修复、CoreClient 4 由测试返修分支化）；SFX 权重实际存在且已进 bundle。当前 `closed_with_limitations` 的两条决定性理由均不成立。 |
| 5. 门禁 | **PASS** | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SIDECAR-REBUILD-1.md` → `PASS (3 warnings)`，EXIT 0。 |

---

## 3. AC 逐项核对（实测 vs 卡面）

### AC1 构建环境：成立

- `verification/SIDECAR-REBUILD-1/pip-freeze.txt` 共 63 行；`packaging/m2ac5/requirements-build.txt` 的 7 个直接钉死版本（`pyinstaller 6.22.3`、`torch 2.14.0`、`torchvision 0.29.0`、`transformers 5.17.0`、`python-doctr 1.1.0`、`safetensors 0.8.0`、`onnxruntime-directml 1.24.4`）在 freeze 中**全部同版本存在**。
- `G:\CODEX\New Manga.workspace\task-envs\m2ac5-build` 存在（venv 40,334 文件 / 1,310,861,487 B）。
- 判定：**PASS**。卡面“63 包全部成功、记录实际安装版本”有 `pip-freeze.txt` 支撑。

### AC2 构建成功：**证据不成立（最终产物与卡面记录不是同一个构建）**

卡面/README 的记录：

- 卡面 AC2 行（`doc/tasks/SIDECAR-REBUILD-1.md:78`）与 README §2 称：PyInstaller `Build complete`，**753 MB**，5 exe，3 ONNX；**最后复制 SFX 权重一步失败并 exit 1**；`yolo11s-seg.onnx` **全工作区不存在**。

实测：

- 当前 bundle `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`：**1,967 文件 / 875,823,531 B**（约 835.3 MiB），5 个 exe，**4 个 ONNX**（detector 163.7 MB、**sfx 38.9 MB**、ocr encoder 327.5 MB、decoder 112 MB）。
- `build-manifest.json`：`schema_version: 14`、`git_head: f7d273d9ab49a03eab25f5ec3f3416667515771a`、`pyinstaller: 6.22.3`、`built_at_utc: 2026-11-15T19:36:51.0177500Z`（= `2026-11-16 03:36:51 +08:00`）。
- 该 manifest 只在 `build_sidecar.ps1` 的**完整构建路径**末尾写入（`:359-383`）；skip 路径在 `:269` 直接 exit。因此当前 bundle 是 **11-16 03:36 的完整构建**，且构建时复制了 SFX 权重（bundle 内 yolo 创建于 `03:36:44`，与源文件同哈希）。
- 卡面 AC2 要求的“产物 sha256”在 README 中**一条也没有**（`Select-String '[0-9a-fA-F]{64}'` 在 README 计数为 0）；构建时间也未以文本记录，只能从 bundle 内的 `build-manifest.json` 反查。
- 卡面/README 的“753 MB”与实测 875,823,531 B 不符；按卡面 11-15 的失败构建口径，它也不是 AC4/AC5 实际使用的那个 bundle。

判定：**FAIL（证据层面）**。最终构建结果大概率成功（manifest 完整构建路径 + 5 exe + 4 ONNX + SFX 同哈希），但**卡面没有记录这个最终构建的日志、尺寸、sha256 与构建时间**，而是引用了更早的失败构建。**不能**据此说 AC2 的“记录产物尺寸、sha256、构建时间与构建日志”已满足。

### AC3 命令面：成立（独立复核确认，非自说自话）

我用 `verification/SIDECAR-REBUILD-1/probe_core.py` 相同协议直接以 NDJSON 探测**新旧两个 sidecar**（新：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe`；旧：`apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe`，2026-10-23）：

| 探测 | 新 sidecar | 旧 sidecar（2026-10-23） |
|---|---|---|
| `core.ping` capabilities | **17 条**，含 `library.delete.preview/1`、`library.trash.read/1`、`library.trash.write/1` | **1 条**：仅 `library.list_books` |
| `ReorderChapters`（payload `{}`） | `INVALID_REQUEST`（命令被识别，进入校验） | `UNKNOWN_COMMAND` |
| `ListTrash` | 正常响应，无 error | `UNKNOWN_COMMAND` |

⇒ 卡面 AC3 的核心结论成立：**新 sidecar 确实包含旧 sidecar 缺失的命令面**，且不只是 capabilities 字符串。README §3/§7 没有直接展示 `ReorderChapters` 的调用差异（该命令不在 capabilities 列表中），但独立 probe 补上了这一格。

判定：**PASS**；证据包存在一处小缺口（见 R-08）。

### AC4 skip 下降：结论成立，但“13 failed”已不是 head 事实

卡面（`:80`）：CoreClient `208/4/0/212`、Host `342/9/44/395`，skip `100→44`，新增 13 failed。

我在 reviewed_head 用新 sidecar 复测：

| 项目 | 卡面（11-15 口径） | 本次夹具复测（head） |
|---|---|---|
| `NewManga.CoreClient.Tests` | 208 / 4 / 0 / 212 | **258 / 0 / 0 / 258** |
| `NewManga.Host.Tests` | 342 / 9 / 44 / 395 | **364 / 0 / 44 / 408** |
| 合计 | 550 / 13 / 44 / 607 | **622 / 0 / 44 / 666** |

- CoreClient 258 全通过（含原先 4 个“Frozen Core”失败）；Host 364 通过 / 0 失败 / 44 skip（含原先 9 个失败）。
- **定向复核**：4 个 CoreClient 原失败测试 `4/4 passed`；9 个 Host 原失败测试 `9/9 passed`（均 EXIT 0）。命令见 §7。
- 原因（不是本卡修的）：
  - Host 9：`CORE-PIPE-EXCLUSIVE-1`（E-6，集成 `dff3d41a5`）修复了 `CoreServiceClient` 的 `request_id` 配对/管道独占；该卡已 `done`。
  - CoreClient 4：`2026-11-16` 的 `fix(tests)` 提交 `05d0395e2`、`c2cf33dbb`、`938a9e450`、`728648fe1` 将 B1/B2 补上 preview digest，并把两个 Fea12 测试改为**按实际 capabilities 分支**；原“缺失能力”的 fail-closed 分支仍保留在代码中，但在当前新 sidecar 上不执行（见 R-06）。
- skip 下降：新 sidecar 下 Host skip 44，CoreClient skip 0；相对旧 sidecar 的 74 + 26 = 100，仍为 **100→44**，结论成立。

判定：**PASS（skip 下降）/ 记录失真（13 failed 已不成立）**。

### AC5 不回归：数字可复现，但首次重跑不是 0 failed

按用户指定口径执行（**不设置** `NEWMANGA_CORECLIENT_SIDECAR_DIR` / `NEWMANGA_MODELS_SIDECAR_DIR`；`NEWMANGA_EVIDENCE_DIR` 与 `NEWMANGA_READER_OVERLAY_EVIDENCE_DIR` 指向 `G:\CODEX\New Manga.workspace\tmp\review-sid\`）：

| 项目 | 卡面 | 本次首次重跑 | 本次两次全量重跑 |
|---|---|---|---|
| Host | 334 / 0 / 74 / 408 | **333 / 1 / 74 / 408，EXIT 1** | **334 / 0 / 74 / 408，EXIT 0** |
| CoreClient | 227 / 0 / 31 / 258 | **227 / 0 / 31 / 258，EXIT 0** | — |
| App | 962 / 0 / 11 / 973 | **962 / 0 / 11 / 973，EXIT 0** | — |
| 合计 | 1523 / 0 / 116 / 1639 | 1522 / 1 / 116 / 1639 | 1523 / 0 / 116 / 1639 |

首次 Host 唯一失败：

```
NewManga.Host.Tests.HostFileIdNormalizationTests.DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex
Assert.True(strong is not null,
  "no freshly created file under C:\Users\49745\AppData\Local\Temp\ had a raw NTFS file index
   above 2^53 within 64 attempts ...")
```

- 这是**与 sidecar 无关**的、按 `%TEMP%` 卷 file-id 序列探测的环境敏感测试；其注释明确要求“不要弱化成 tautology”。同一测试随后单独跑 3 次均 `3/3 passed`，两次 Host 全量均 `334/0/74/408` EXIT 0。
- 因此：卡面的 334/0 在干净重跑中**可复现**；但“0 failed”**不是确定性的**，卡面的 AC5 证据日志没有记录该 flake，且其中 App.Tests 的数字注为“本会话早前实测”，不是同一次三项目序列。

判定：**PASS（干净重跑）/ 证据稳健性不足**（见 R-05）。我没有、也不建议修改该测试的严格断言。

### AC6 零产品代码改动：结论成立，提交清单错误

卡面（`:60`）列出 6 个提交：`83f452607`、`92349bc4e`、`acb8a89b2`、`0b458eeba`、`18bc51bc9`、`f1a2e8805`，称“均无 `src/**` 或 `apps/**` 改动”。

逐提交 `git show --name-only` 实测：

- 上述 6 个提交**确实没有** `src/**` 或 `apps/**` 文件。
- 但 **`f1a2e8805` 不是本卡的实现/诊断提交**：它是 `feat(gov): AC3/AC7 收口`，共 52 个文件（`doc/tasks/**`、`tools/governance/**`、`verification/GOV-...`）；它只顺带改了本卡 Resource Manifest 的一行声明。
- 本卡真正的实现/证据提交未列入：`860878d64`（`feat(sidecar): 重建 sidecar ...`）、`473e7e145`、`b9695e78a`、`ce0cc85c1`（AC5 证据）。
- 我对 **11 个相关提交**（上述 6 + `860878d64`/`473e7e145`/`b9695e78a`/`ce0cc85c1`/`ae9231c3a`）逐提交检查：**零 `src/**`、零 `apps/**`**。
- 新 bundle 位于 `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`；`git check-ignore -v` 指向 `.gitignore:22:/apps/desktop-avalonia/build/`；`git ls-files apps/desktop-avalonia/build` 为空 ⇒ 未提交进仓库。

判定：**PASS（实质结论）/ FAIL（提交清单与归属）**（见 R-07）。

---

## 4. Canonical Evidence 15 行

- 15 行全部有 `path`、`commit=ce0cc85c1`、`sha256`、`class`、`sha256_basis=BLOB`；15 个路径全部存在。
- 我用 `git cat-file blob ce0cc85c1:<path>` 逐行计算 BLOB 哈希：**15/15 与卡面声明完全一致**。
- 说明：`EV-SR-01`、`EV-SR-03`、`EV-SR-06`、`EV-SR-14`、`EV-SR-15` 的**工作树文件字节**与 BLOB 不同（Windows CRLF 规范化），但卡面声明的是 `BLOB` 基准，属于正确口径；不是 finding。

抽查 8 行（4 CANONICAL + 4 SOURCE_PIN）：

| evidence_id | class | 声明 sha256 | `ce0cc85c1` BLOB 实测 | 一致 |
|---|---|---|---|---|
| EV-SR-01 | CANONICAL | `2b89ef4935c6a432b4618a9a4b1d731abfbfbc8c4faf7c2a5dab9af75bd8df59` | 同左 | ✅ |
| EV-SR-02 | CANONICAL | `34fce28ee73959c023992fff4887afa511fbd48de9c3c5f96dc5ebd6b056d7ee` | 同左 | ✅ |
| EV-SR-03 | CANONICAL | `ad4369ec58c9fc3a28d20e809f21371d7685132ef0db0ce04ecf019d1721f598` | 同左 | ✅ |
| EV-SR-04 | CANONICAL | `76781ecd5a3f6dc403a75eec17ed16ad6376b0f6520e41f53d867a193f5b9039` | 同左 | ✅ |
| EV-SR-05 | SOURCE_PIN | `3e96befdb95de81139bf7611f7f8fc6b536bb101c3bcd811f304bfcfe0c7fd1b` | 同左 | ✅ |
| EV-SR-08 | SOURCE_PIN | `db869682eccead1d41ec76ffcc29e1f8c89b416157893aeafbe8f9efc5c07136` | 同左 | ✅ |
| EV-SR-12 | SOURCE_PIN | `77605d4c121c63304cfcddcb5a6f35710de6548fbbefc0a4d9f63e198874d4a7` | 同左 | ✅ |
| EV-SR-15 | SOURCE_PIN | `f238611bb63ac0539e36b74e0d387b1f30eedf8e413394553cf2786303faf606` | 同左 | ✅ |

**判定：PASS。** 但注意：`EV-SR-02`（README）内容停留在 11-15，顶部仍写“状态：`in_progress`（未收口）”；它是历史证据，不能作为 reviewed_head 的现状说明（见 R-09）。

---

## 5. Resource closeout

| 检查项 | 实测 | 结果 |
|---|---|---|
| `RESOURCE-MANIFEST.json` 存在 | `G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\RESOURCE-MANIFEST.json`（793 B） | ✅ |
| manifest sha256 = 卡面 `54096522b0a16c52b783ad64cc0e44bdff2625db6df6661da22de39c54202170` | `54096522b0a16c52b783ad64cc0e44bdff2625db6df6661da22de39c54202170` | ✅ 完全一致 |
| destination 1：`task-envs/SIDECAR-REBUILD-1` | 存在；现 171 文件 / 55,837,886 B（含 manifest 自身 793 B；manifest 记 170 / 55,837,093） | ✅（自计数差异可解释） |
| destination 2：`task-envs/m2ac5-build` | 存在；40,334 文件 / 1,310,861,487 B，与 manifest 完全一致 | ✅ |
| destination 3：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar` | 存在；1,967 文件 / 875,823,531 B；git-ignored；**未出现在 manifest 的 `resources` 数组** | ⚠️ 存在但未登记 |
| manifest 合计 | `total_file_count=40,504`、`total_bytes=1,366,698,580` = 170 + 40,334；55,837,093 + 1,310,861,487 | ✅ 算术自洽，但**不含第三个 destination** |
| 卡面“3 行 PRESERVE_REFERENCED” | 卡面表格有 3 行；manifest 只有 2 个 resource | ❌ 覆盖不完整 |

判定：**FAIL（覆盖度）**。sha256 与 3 个路径的存在性都通过；但 `resource_closeout_status: complete` 与“3 行”的表述不成立：第三个 destination 没有 manifest 条目/content digest，且其 1,967 文件 / 875,823,531 B 未进入合计。证据/构建 venv 两个 resource 的完整性没有问题。

---

## 6. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | **P0** | `doc/tasks/SIDECAR-REBUILD-1.md:100-104,143-154`；`verification/SIDECAR-REBUILD-1/README.md:75-109` | 收口把“13 个失败未修/未归因完成”作为不能 done 的决定性理由；但 head 上 13 个测试全部通过。影响：`closed_with_limitations` 的核心事实基础不成立。 | 夹具模式 `CoreClient 258/0/0/258`、`Host 364/0/44/408`，EXIT 0；定向 4/4 + 9/9；见 §7 命令与 `ac4-fixture-review.log`。Host 9 由 `CORE-PIPE-EXCLUSIVE-1`（`dff3d41a5`）修复；CoreClient 4 由 `05d0395e2`/`c2cf33dbb`/`938a9e450`/`728648fe1` 测试返修。 | 重开本卡收口：把“13 失败”改为“已在 head 消除（附归因）”；不要把失败写成通过，也不要把测试返修伪装成本卡修复。 | open |
| R-02 | **P0** | `doc/tasks/SIDECAR-REBUILD-1.md:105-106,151`；`verification/SIDECAR-REBUILD-1/README.md:41-53` | 收口称 `yolo11s-seg.onnx` 全工作区不存在、需用户提供（goal blocked 判据）；实际文件存在且已进当前 bundle。影响：向用户提出了一个不存在的阻塞条件，并误记 AC2 为失败。 | `G:\CODEX\New Manga.workspace\task-envs\M2-SFX-DETECT\weights-v2b\yolo11s-seg.onnx`：40,824,255 B，sha256 `944e8114…d418d`，创建 `2026-11-16T03:35:54+08:00`；bundle 内同哈希，创建 `03:36:44`；`build-manifest.json` `built_at_utc=2026-11-15T19:36:51Z`。 | 删除“SFX 缺失/需用户提供”的 limitation；AC2 以 11-16 成功构建重写并补 sha256/尺寸/时间/日志。 | open |
| R-03 | P1 | `doc/tasks/SIDECAR-REBUILD-1.md:78`；`verification/SIDECAR-REBUILD-1/README.md:25-53` | AC2 证据引用的是 11-15 的失败构建（753 MB、3 ONNX、SFX 复制失败），不是 11-16 实际 bundle；README 中 0 条 64-hex sha256；实测 bundle 875,823,531 B、4 ONNX。影响：AC2 的“记录产物尺寸、sha256、构建时间与构建日志”未满足，且证据与 AC4/AC5 使用的产物不一致。 | 卡面/README 对照；`build-manifest.json`；bundle 文件枚举；`Select-String '[0-9a-fA-F]{64}'` 计数 0；实测尺寸见 §3/§5。 | 以最终 bundle 重新生成 AC2 证据：尺寸、逐 exe/ONNX sha256、`built_at_utc`、完整构建日志；若确实有过 11-16 的完整构建日志，应入库。 | open |
| R-04 | P1 | `doc/tasks/SIDECAR-REBUILD-1.md:137-141,146`；`RESOURCE-MANIFEST.json` | 卡面称 3 行 `PRESERVE_REFERENCED` 且 `resource_closeout_status: complete`；manifest 只有 2 个 resource，未登记 bundle（1,967 文件 / 875,823,531 B）。影响：第三项资源没有 manifest/content digest，不能声称“3 行闭环”。 | 见 §5；`resources` 数组长度 2；合计 40,504 / 1,366,698,580 不包含 bundle。 | 把 bundle 作为第三个 resource 写入 manifest（文件数/字节/digest），或把第三行改标 `NOT_APPLICABLE`/明确说明为何不登记；重算 manifest sha256 并更新卡面。 | open |
| R-05 | P1 | `doc/tasks/SIDECAR-REBUILD-1.md:59`；`verification/SIDECAR-REBUILD-1/ac5-no-fixture-2026-11-17.log` | 卡面 AC5 明确写“三项目仍 0 failed”；首次按指定口径重跑 Host 为 333/1/74/408 EXIT 1（`HostFileIdNormalizationTests` 环境 flake），两次全量重跑才恢复 334/0。影响：0-failed 可复现但非确定性；证据日志是手写摘要，App 数字为“本会话早前实测”，未记录 flake。 | `ac5-review.log` Host 首轮失败堆栈；随后 3 次单测 3/3、2 次全量 334/0/74/408。 | 在 AC5 证据中登记：干净重跑 1523/0/116/1639 的原始输出；说明该非 sidecar 环境测试可能 flake（不得弱化其断言）；App 应与 Host/CoreClient 同批重跑或注明来源。 | open |
| R-06 | P1 | `doc/tasks/SIDECAR-REBUILD-1.md:100-102,150`；`CommandIntegrationTests.cs`、`CommandWiringB1/B2Tests.cs` | 卡面要求 CoreClient 4 个“Frozen Core”测试“不得删除、需改为显式模拟旧 capabilities”；实际返修是按当前 core 的实际 capabilities 分支（`coreHasDeleteTrash`）。当前新 sidecar 下只执行正分支，`CORE_CAPABILITY_MISSING` 的负分支不被执行。影响：13/13 全绿不等于 fail-closed 语义已被验证；这是当前最真实、但未被收口准确记录的残余。 | `git show 938a9e450`/`728648fe1`/`05d0395e2`/`c2cf33dbb`；当前 `core.ping` 含 3 条 delete/trash 能力；定向测试 4/4 pass。 | 在收口中把该残余写清楚（“fail-closed 负分支未在当前 sidecar 执行；需专门 fake/旧 capabilities 夹具覆盖”），并另立/登记覆盖任务；不要把它说成“已由显式模拟旧 capabilities 覆盖”。 | open |
| R-07 | P2 | `doc/tasks/SIDECAR-REBUILD-1.md:60` | AC6 的“本卡 6 个提交”清单包含 `f1a2e8805`（GOV 卡提交，52 文件），遗漏 `860878d64`（本卡主 feat）、`473e7e145`、`b9695e78a`、`ce0cc85c1`。影响：提交归属与审计链错误；实质结论（零 `src/apps`）仍成立。 | 11 个相关提交逐提交 `git show --name-only`；全部零 `src/**`/`apps/**`；`f1a2e8805` 文件清单含 `tools/governance/**`、45 张历史卡。 | 修正为真实相关提交集合，并保留“零产品代码改动”的独立核对命令。 | open |
| R-08 | P2 | `doc/tasks/SIDECAR-REBUILD-1.md:53-55,79`；`verification/SIDECAR-REBUILD-1/README.md:55-65,118-147` | AC3 要求证明“尤其 `ReorderChapters` 所在命令”；读 README §3/§7 只能看到 capabilities 与 `ListBooks`，没有 `ReorderChapters` 的调用证据。影响：证据包本身不足以独立复核该子项；我的 probe 补上了。 | 新 sidecar `ReorderChapters` → `INVALID_REQUEST`，旧 sidecar → `UNKNOWN_COMMAND`；`ListTrash` 新正常/旧 UNKNOWN。 | 把该 probe 的请求/响应原文入库（或引用本次复核 §3），避免依赖“capabilities 差异”间接推断。 | open |
| R-09 | P2 | `verification/SIDECAR-REBUILD-1/README.md:3,75-109`；`doc/tasks/SIDECAR-REBUILD-1.md:102,150` | README 顶部仍写“状态：`in_progress`（未收口）”；README §5 仍称 13 失败未修与 SFX 缺失；卡面正文 `:102` 说 Host 9“归因未做”，closeout `:150` 说“已由第七轮诊断定位根因”。影响：恢复入口/收口记录自相矛盾，读者无法判断哪个是当前事实。 | 直接读上述行；与 §3/§6 的实测对照。 | 在重开收口时同步 README/正文：明确它是 11-15 的历史证据，并新增 11-17 head 状态段（或另写复测日志），不要覆盖历史字节。 | open |
| R-10 | P2 | `doc/tasks/SIDECAR-REBUILD-1.md:11,95` | frontmatter `reviewer: null`，正文“Review：尚无”；closeout 没有独立 Review 记录。影响：本报告是首次独立复核，卡片当前没有把复核身份/结论链接进生命周期。 | 读 frontmatter/body；本报告。 | 由 Lead 在处置后把 `reviewer` 置为 `reviewer-sid`（或实际审查者）并链接本报告；若重开重收口，保留本报告的 reviewed_head。 | open |

**计数：P0=2，P1=4，P2=4。**

> 说明（遵守用户硬约束）：上表 R-01 的“13 个测试全部通过”是**实测结果**，不是建议把失败写成通过；R-06 同时指出其中 4 个的 fail-closed 负分支并未被当前 sidecar 执行。**不得**据此把“CORE_CAPABILITY_MISSING fail-closed 语义已验证”写成通过，也不得弱化任何断言。

---

## 7. 验证（实际命令与结果）

| 场景 | 命令/步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| AC5 Host（首次） | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Debug --no-build` | head `ae9231c3a`；未设 sidecar 目录；evidence 指向 `tmp\review-sid` | **333 / 1 / 74 / 408，EXIT 1**；失败 `HostFileIdNormalizationTests.DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex`（环境探针） | `G:\CODEX\New Manga.workspace\tmp\review-sid\ac5-review.log` |
| AC5 Host（重跑 ×2） | 同上 | 同上 | **334 / 0 / 74 / 408，EXIT 0**（两次） | 同上/本次会话记录 |
| AC5 CoreClient | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Debug --no-build` | 同上 | **227 / 0 / 31 / 258，EXIT 0** | `ac5-review.log` |
| AC5 App | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Debug --no-build` | 同上 | **962 / 0 / 11 / 973，EXIT 0**（4m56s） | `ac5-review.log` |
| AC4 CoreClient 夹具 | 设 `NEWMANGA_CORECLIENT_SIDECAR_DIR=apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar`；CoreClient 全量 `--no-build` | head；新 sidecar（11-16 bundle） | **258 / 0 / 0 / 258，EXIT 0** | `G:\CODEX\New Manga.workspace\tmp\review-sid\ac4-fixture-review.log` |
| AC4 Host 夹具 | 同上，Host 全量 `--no-build` | 同上 | **364 / 0 / 44 / 408，EXIT 0** | 同上 |
| 13 个原失败测试定向 | CoreClient filter 4 个；Host filter 9 个 | 同上 | **4/4 passed**、**9/9 passed**，EXIT 0 | 本次会话输出；可复跑 |
| AC3 双 sidecar probe | `python cap-probe.py` / `cmd-probe.py`（NDJSON `core.ping`、`ReorderChapters`、`ListTrash`） | 新/旧 sidecar，隔离 data root | 新 17 capabilities、`ReorderChapters` `INVALID_REQUEST`、`ListTrash` 正常；旧 1 capability、两者 `UNKNOWN_COMMAND` | `G:\CODEX\New Manga.workspace\tmp\review-sid\cap-probe.py`、`cmd-probe.py` |
| Canonical 15 行 | `git cat-file blob ce0cc85c1:<path>` + SHA256 | head `ae9231c3a` | **15/15 匹配**（8 行见 §4） | 本次会话输出 |
| Resource manifest | `Get-FileHash RESOURCE-MANIFEST.json`；`Test-Path` 3 个 destination；读 `resources` | workspace | sha256 匹配；3 个路径存在；manifest 2 resources；bundle 1,967 / 875,823,531 B 未登记 | §5 |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SIDECAR-REBUILD-1.md` | head `ae9231c3a` | `PASS (3 warnings)`，**EXIT 0** | 本次会话输出 |
| 工作树清洁 | `git status --porcelain` | 全部测试结束、报告落盘前（HEAD 仍 `ae9231c3a`） | **为空**（测试未写仓库证据）；报告落盘后仅新增本报告；并发 Codex 裁定文件随后由 `ba215b823` 单独入库（仅 `doc/reviews/`，非本复核创建） | 本次会话 |

---

## 8. Architecture / Verification 结论

- **Architecture**：sidecar 重建本身可用；新 bundle（schema v14，git_head `f7d273d9`）具备当前 FEA-12 能力与 `ReorderChapters`；未发现本卡引入产品源码改动。资源处置的架构性缺口是第三个 destination 未进入 manifest。
- **Verification**：AC1/AC3 成立；AC5 数字在干净重跑中复现；AC2 证据失效/不完整；AC4 的 13-failed 记录在 head 已不成立；AC6 实质成立但提交清单错误；Resource closeout 覆盖不完整。**P0 未解决、关键验证记录与事实不符 ⇒ 不可批准 current closeout。**

---

## 9. 明确回答：该卡能否保持 `closed_with_limitations`

**不能按当前这份记录保持。** 理由不是“13 个失败应写成通过”，而是：

1. 当前记录把“13 个失败未修”作为 `closed_with_limitations` 的决定性理由；reviewed_head 实测 13/13 已不再失败（Host 9 由 E-6 修复；CoreClient 4 由测试返修分支化）。该理由已不成立。
2. 当前记录把“SFX 权重缺失、需用户提供”作为第二条理由；实测权重存在且已进当前 bundle。该理由不成立。
3. 但**仍存在真实残余**：CoreClient 4 的 `CORE_CAPABILITY_MISSING` 负分支未在当前新 sidecar 上执行（测试按实际能力分支）；`App.Tests` 的 7 个 sidecar 测试与 publish 冒烟未做；资源 manifest 未覆盖 bundle。这些可以作为**改写后的** `closed_with_limitations` 依据，但不能用“13 个失败未修”和“SFX 缺失”来充当。

**建议 Lead 的动作**（不改变本复核只读边界）：

- 重开本卡收口，按 reviewed_head 重跑夹具模式并入库原始输出（`CoreClient 258/0/0/258`、`Host 364/0/44/408`）。
- 把 R-01/R-02 的两条 false limitation 删除或改为“已由 E-6/测试返修在 head 消除（附 commit/归因）”。
- 把 R-06 的 fail-closed 负分支未覆盖、App sidecar 测试/publish 冒烟未做，写成新的 limitation。
- 修正 AC2 证据（11-16 最终 bundle 的尺寸/sha256/时间/日志）、AC6 提交集合、Resource Manifest 第三项，并更新 README/正文的 in_progress 旧状态。
- 是否把状态从 `closed_with_limitations` 升为 `done`，由 Lead 按 AC/门禁裁决；在 R-03/R-04/R-06 未处置前，本复核不支持 `done`。

---

## 10. 声明

**本复核不构成产品发布验收。** 本报告只覆盖 `reviewed_head=ae9231c3a` 的只读复核、进程内测试与静态证据核对；不覆盖 Windows 安装矩阵、签名、真实模型/网络、完整 publish 冒烟、带新 sidecar 的 App.Tests 全量，也不对 Release Gate 条件 3/4 或产品发布状态作出认可。测试通过不等于产品验收；本报告中的任何数字都不能被引用为发布放行依据。

改动边界：除本报告外未修改仓库文件；未提交/推送/checkout；未修改测试 gate；测试证据只写入 `G:\CODEX\New Manga.workspace\tmp\review-sid\`。
