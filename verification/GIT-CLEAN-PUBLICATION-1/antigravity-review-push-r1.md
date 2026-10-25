---
task_id: GIT-CLEAN-PUBLICATION-1
reviewer: Antigravity
author: Codex
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
reviewed_head: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
decision: approved
---

# Review：GIT-CLEAN-PUBLICATION-1（Push-Gate 独立审查）

日期：2026-10-25（Asia/Shanghai）。
Reviewer：Antigravity（独立 Reviewer，由 DSH 作为 Lead / Architect / Integrator 任命；非实现作者，非 DSH）。
实现作者：Codex。
任命来源：[APPOINTMENT-push-r1.md](file:///G:/CODEX/New%20Manga/verification/GIT-CLEAN-PUBLICATION-1/APPOINTMENT-push-r1.md)。

## 审查性质与边界声明

**本审查为 Push-Gate 独立审查，不是产品发布验收。**
审查目的仅为判断候选独立源码快照单一 root commit `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` 是否可由 DSH 作为 `origin` 新分支安全普通推送。

本审查明确不要求、亦不宣称：
1. 产品发布验收通过；
2. 父 Task `GIT-CLEAN-PUBLICATION-1` 状态置为 `done`（保持 `in_review`，AC4 仍为 `BLOCKED`，AC5 仍为 `PARTIAL`）；
3. Rust 容量饱和与并发安全通过（保持 `BLOCKED`）；
4. Core 3 组参数环境失败已修复（保持 `BLOCKED`）；
5. 安装包 / 代码签名 / 真实模型 / 真实 GUI / 完整审计通过（保持 `NOT_RUN`）；
6. 候选 commit 与 `main` 有共同历史或可合并入 `main`。

既有 Review [dsh-review-r1.md](file:///G:/CODEX/New%20Manga/verification/GIT-CLEAN-PUBLICATION-1/dsh-review-r1.md) 保持原字节与历史效力，不因本次 Appointment 改写。

---

## 范围与依据

- **审查对象（精确固定）**：
  - 源仓：`G:/CODEX/New Manga`，branch `main`，基线 base_commit `349e61faff5f93067af5d4ce2d9e394e0d665b8c`（源仓当前 HEAD 为治理移交 commit `a3c936f68748047aee41c4c60d732adc5bdf55f7`，仅涉及治理文档移交，无生产代码改动，两 commit 均不在候选对象库中）。
  - 候选：独立仓库 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`，branch `codex/clean-source-snapshot`，单 root commit `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（无父提交，无 remote）。
  - 治理与任务约束：[GIT-CLEAN-PUBLICATION-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GIT-CLEAN-PUBLICATION-1.md)、[APPOINTMENT-push-r1.md](file:///G:/CODEX/New%20Manga/verification/GIT-CLEAN-PUBLICATION-1/APPOINTMENT-push-r1.md)、[RESULT.md](file:///G:/CODEX/New%20Manga/verification/GIT-CLEAN-PUBLICATION-DIAG-1/RESULT.md)。
- **只读约束**：本审查为全流程只读核验；未修改候选仓库、源仓、生产代码、素材、系统 ACL、refs 或既有冻结证据；唯一写入路径为本审查报告。未在候选仓执行产生写缓存的构建或测试命令。
- **视角状态**：Architecture `executed`、Verification `executed`。

---

## Architecture

**结论：候选 commit 在 Git 历史隔离、禁止材料隔离、隐私路径脱敏以及推送目标安全性四个方面完全满足安全推送门槛；作为“独立干净源码快照”，可安全作为 `origin` 新分支普通推送。**

1. **Git 历史与对象库完全隔离**：
   - 候选仓库单一 root commit，`rev-list --count HEAD` 为 1，`--max-parents=0` 确认为 root commit，`rev-list --parents -n 1 HEAD` 仅含自身，无 parent。
   - 仅含 1 个 loose ref `refs/heads/codex/clean-source-snapshot`，不存在 `packed-refs`。
   - 不存在任何 remote 配置（`remote -v` 输出为空）。
   - `.git` 内部经逐项只读核验：无 `objects/info/alternates`、无 `objects/info/http-alternates`、无 `shallow`、无 `info/grafts`、无 `refs/replace`。
   - `git fsck` 结果 exit 0，无 dangling/missing 对象。
   - 源仓全部 4132 个 commit（包括 base `349e61faf` 与当前 HEAD `a3c936f68`）在候选对象库中完全不存在（`git cat-file -e` 返回码 1）。候选与源仓无共享对象库，不是 linked worktree。

2. **禁止材料绝对隔离**：
   - 依据 [push-material-disposition.json](file:///G:/CODEX/New%20Manga/audit/V1-FULL-AUDIT/evidence/push-material-disposition.json)，提取 169 组素材对象（`outer_object` 与 `embedded_git_object` 去重后共 338 个禁止 SHA）。
   - 在候选对象库对全部 338 个 SHA 逐一执行只读断言：**present=0, absent=338**，禁止对象 100% 缺失。
   - 候选仓库全部 733 个 tracked 文件经扩展名与内容扫描：**完全不含 `.jpg`, `.jpeg`, `.zip`, `.db`**（命中数为 0）。
   - 二进制文件恰 6 项：项目图标 `icon.ico`（首次引入源仓于 `991097d7...`，经核验为 32×32 DIB 图标而非漫画素材）以及 5 个由固定生成器 `experiments/TASK-016/generate_samples.py` 离屏绘制的测试合成 PNG，均无真实漫画内容。

3. **来源可追溯与隐私脱敏**：
   - 候选仓库 733 个 tracked 文件由 `SOURCE_MANIFEST.json` 完全覆盖并精确审计：
     - 724 个源文件来源于基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；
     - 其中 722 个文件逐字节与源仓 blob 一致；
     - 恰有 2 处受控脱敏变换（`packaging/m2ac5/README.md` 与 `tests/core/test_core_detect.py` 中的个人目录字面量 `49745` 替换为 `USER`）；全仓 733 个文件只读字节检索 `49745` 结果为 **0 命中**；
     - 6 个合成夹具文件（5 个 PNG + 1 个 manifest.json）经离屏生成器重建；
     - 3 个新增治理/说明文件（`README.md`, `.gitignore`, `SOURCE_MANIFEST.json`）；
     - 无任何未授权文件或来源不明的文件。

4. **远端与推送安全性**：
   - 通过 `git ls-remote --heads origin` 现场核验：远端当前仅存在单一分支 `refs/heads/main`（commit 为 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`）。
   - 目标新分支 `codex/clean-source-snapshot`（或其它指定的新分支名）在远端未被占用。
   - 绝对禁止 force push，绝对禁止 push main，绝对禁止改写远端现有分支；仅允许以明确的非 main 新分支名称进行普通引用创建。

5. **交付边界与介质限制**：
   - 候选工作树中的 `node_modules`、`dist` 以及测试运行产生的临时 `jsonl` 属于 ignored 本地产物，严禁以物理目录打包或 zip 形式交付（见 F-001）；必须严格且仅以 Git 对象/分支方式推送。

---

## Verification

| 场景 / 检查项 | 命令或核验步骤 | 验证环境 / 目标 commit | 结果 | 证据与只读输出摘要 |
|---|---|---|---|---|
| **1. 候选 Git 隔离** | `git -C <target> rev-parse HEAD`<br>`git -C <target> rev-list --count HEAD`<br>`git -C <target> rev-list --max-parents=0 HEAD`<br>`git -C <target> rev-list --parents -n 1 HEAD`<br>`git -C <target> show-ref`<br>`git -C <target> remote -v`<br>`git -C <target> fsck`<br>检查 `alternates` / `packed-refs` / `shallow` / `grafts` / `replace` | Win11 / pwsh / Python<br>候选 `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` | **PASS** | `HEAD` = `e34a90d0...`；<br>`rev-list --count` = 1；<br>`max-parents=0` = `e34a90d0...`；<br>`parents` 仅自身（无 parent）；<br>`show-ref` 仅 1 行 `refs/heads/codex/clean-source-snapshot`；<br>`remote -v` 输出为空；<br>`fsck` exit 0（0 errors）；<br>内部文件 `alternates`/`http-alternates`/`packed-refs`/`shallow`/`grafts`/`replace` 全为 False；<br>源 commit `349e61faf` 与 `a3c936f68` 在候选库 `cat-file -e` 返回码均为 1（absent）。 |
| **2. 禁止材料隔离** | 读 `audit/V1-FULL-AUDIT/evidence/push-material-disposition.json`（169 组），提取 338 个 unique SHA；在候选对象库逐个 `git cat-file -e` 断言缺失；检查 733 个 tracked 文件的扩展名与类型 | 候选 `e34a90d0` / 源仓 disposition | **PASS** | 338 个禁止 SHA：**present=0, absent=338**；<br>733 个 tracked 文件扩展名核验：`.jpg`, `.jpeg`, `.zip`, `.db` **命中数 0**；<br>二进制文件恰 6 个（`icon.ico` + 5 个合成 PNG，均已追溯且非私有素材）。 |
| **3. 来源与 Canonical Evidence SHA** | 计算并比对 Task 表中 8 项 Canonical Evidence 的 SHA-256：`EV-SOURCE`, `EV-GRAPH`, `EV-SELECT`, `EV-EXPORT`, `EV-R4`, `EV-RUST`, `EV-CORE`, `EV-FRONTEND` | Task Canonical 表 / `review-package/` / 候选仓 | **PASS** | 8/8 全部存在且 SHA-256 100% 精确匹配：<br>- `EV-SOURCE`: `be511fdb...` MATCH<br>- `EV-GRAPH`: `40d812e7...` MATCH<br>- `EV-SELECT`: `406a8945...` MATCH<br>- `EV-EXPORT`: `a9d7b71a...` MATCH<br>- `EV-R4`: `65733bec...` MATCH<br>- `EV-RUST`: `ab66e07c...` MATCH<br>- `EV-CORE`: `5b6db716...` MATCH<br>- `EV-FRONTEND`: `56f025c2...` MATCH |
| **4. SOURCE_MANIFEST 构成与脱敏** | 读 `SOURCE_MANIFEST.json` 键值结构，核对 724 源文件、6 生成文件、3 受控新增文件；搜索全仓 733 文件中的真实个人目录字面量 `49745` | 候选 `e34a90d0` | **PASS** | `source_commit` = `349e61faf...`；<br>`files` = 724，`generated_files` = 6，受控新增 = 3（`.gitignore`, `README.md`, `SOURCE_MANIFEST.json`），合计恰 733；<br>`transform` 恰 2 处（脱敏替换）；<br>全仓 733 文件 `49745` 检索结果：**0 命中**。 |
| **5. 前端构建与测试** | 读 `checks-r4.json` 与 `frontend-tests-r3.log` 尾部及 exit 记录；比对前端 tree | 候选 `e34a90d0` / r3/r4 | **PASS** | `npm-ci-r4` exit 0（2.8s）；<br>`frontend-build-r4` exit 0（4.27s）；<br>测试日志尾部：`Test Files 45 passed (45)`, `Tests 435 passed (435)`；<br>r3 与 r4 的 `apps/desktop/frontend` tree 逐条相同。 |
| **6. Rust 构建与测试限制披露** | 读 `checks-r4.json`、`rust-tests-r4-serial.log` 尾部、`rust-tests-r2.log`、DIAG-1 RESULT | 候选 `e34a90d0` / r2/r3/r4 | **BLOCKED**（口径如实披露） | r4 串行（`--test-threads=1`，跳过 packaged）结果：`153 passed; 0 failed; 1 ignored; 12 filtered out; exit 0`（1 ignored 为 `perf_chunk_request_digest_cost`，12 filtered 为 `packaged_sidecar_tests::`）；<br>默认并发测试未通过（r2 默认并发 `150 passed; 3 failed`，DIAG-1 r4 默认并发 `151 passed / 2 failed`，存在 `UNREAPED_WORKER_REGISTRY` 共享污染与容量 32 限制）；<br>并发缺陷风险未排除，作为产品 Gate 保持 **BLOCKED**；但测试记录真实披露，无伪造。 |
| **7. Core 771/3 失败与沙箱归因** | 读 `core-checks-r2.json`、`core-tests-r2.log` 尾部、DIAG-1 冻结 DB `plugin_events` | 候选 `e34a90d0` / r2 | **BLOCKED**（口径如实披露） | 结果：`3 failed, 771 passed, 1 warning in 49.64s`；无 skip/xfail；<br>失败为 1 个参数化用例的 3 组参数（`test_p16_reader_export.py:762, 780`）；<br>归因为 Windows AppContainer 沙箱 `_grant` 无法为本机 `C:\Python314\python.exe` 授予 ACL，原始 SQLite `library.db` 的 `plugin_events` 记录了 `PLUGIN_HOOK_UNAVAILABLE / cannot grant sandbox access to python.exe`；<br>环境限制未解除，不修系统 ACL 刷绿，作为产品 Gate 保持 **BLOCKED**。 |
| **8. Packaged Sidecar 测试** | 读 DIAG-1 RESULT 实际结案记录与固定日志 | e34 head 独立 packaged | **NOT_RUN（主流程）/ PASS（独立验证）** | 12 项 `packaged_sidecar_tests` 在 r4 测试中被 `--skip` 过滤；在 DIAG-1 的独立 packaged 构建与测试中，12 项测试在 e34 源码上全部通过（`12 passed / 0 failed / 0 ignored / 154 filtered, exit 0`）；不作为产品 release 依据。 |
| **9. 安装包/签名/模型/GUI/完整审计** | 检查 Task 范围与交付记录 | — | **NOT_RUN** | Task 明确声明不在此范围，不作为发布验收。 |
| **10. 远端与推送安全性** | 执行只读命令 `git ls-remote --heads origin` | 远端仓库 `origin` | **PASS** | 远端当前仅存在单一分支 `refs/heads/main = 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`；<br>目标新分支未被占用；只允许普通 push 新分支。 |
| **11. 治理检查** | 执行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | 主仓当前工作区 | **PASS** | 输出 `Governance check: PASS (4 warnings)`，exit 0；指针与规范一致。 |

---

## Findings

| ID | 级别 | 文件 / 范围 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F-001 | P2 | 候选工作树 `apps/desktop/frontend/node_modules/`、`dist/`、测试生成 `jsonl` | 候选工作树并非纯净目录：包含 ignored 的 `node_modules`（约 84MB）、`dist` 以及测试运行时产生的带本地绝对路径的 `jsonl` 文件。若以非 Git 方式（如物理目录复制或压缩包）交付，会泄漏本地环境绝对路径与构建产物。但对 Git 对象/分支推送完全无影响（tracked 文件仅 733 项，status clean）。 | 检查工作树存在 `node_modules`、`dist`、`verification/P04/*.jsonl`；`git ls-files` 严格为 733 项，不含上述产物。 | 明确本次交付与后续使用**严格仅允许 Git 对象/分支方式**（`git push`）；严禁直接复制或压缩候选目录用于外部传播。 | open（已披露约束） |
| F-002 | P2 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` (AC4, AC5) | 软件产品级 Gate 仍未关闭：Core 3 组参数因环境沙箱限制失败、Rust 默认并发存在测试间共享状态污染且未通过饱和压力测试、安装包/代码签名/真实 GUI/模型尚未运行。本次 push-gate 审查通过仅代表源码快照干净隔离，绝不代表产品已达发布验收标准。 | AC4 保持 `BLOCKED`，AC5 保持 `PARTIAL`；`core-tests-r2.log` 显示 3 失败，`rust-tests-r2.log` 显示并发 3 失败。 | 明确界定边界：禁止对外宣称产品发布验收通过；后续真实产品发布须另行在修复并发与环境问题后走完整发布 Gate 审查。 | open（边界已冻结） |
| F-003 | P3 | 源仓 HEAD vs 候选 `base_commit` | 候选快照的导出基准 commit 为 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；源仓最新 HEAD 为治理移交 commit `a3c936f68748047aee41c4c60d732adc5bdf55f7`。经核验，该提交仅包含治理规则与模板更新，未修改任何产品源码；且两 commit 在候选对象库中均不存在（present=0），源仓 index clean。 | `git -C "G:/CODEX/New Manga" show --stat a3c936f68` 仅修改治理与模板文档；`git -C <target> cat-file -e a3c936f...` 返回码 1。 | 记录该版本差异事实；不影响候选 commit `e34a90d0` 的完整性与可信度。 | closed（已确认一致） |
| F-004 | P3 | 远端 `origin` 推送操作规范 | 推送时若操作失误可能误推 `main` 或覆盖远端。远端当前仅有 `main = 6a68fdeb...`。推送命令必须显式指定目标新分支引用，并绝对禁止 force。 | `git ls-remote --heads origin` 确认远端只有 `refs/heads/main`。 | DSH 执行推送时必须严格使用只推新 ref 的命令，详见本报告结论。 | closed（操作规范已固化） |

---

## 结论与复审

### 审查结论

**decision: approved（Push-Gate 通过）**

**批准理由**：
1. **禁止材料绝对排除**：338 个私有漫画对象在候选对象库完全缺失（present=0, absent=338）；tracked 733 文件不含任何 `.jpg`, `.jpeg`, `.zip`, `.db`；个人目录字面量 `49745` 0 残留。
2. **Git 历史完全独立**：单 root commit，无父提交，无 remote，无 alternates/packed-refs/shallow/grafts/replace；源仓所有 4132 个 commit 在候选对象库完全不存在。
3. **来源与证据链闭环**：724 源文件逐字节绑定基线 `349e61faf`（仅 2 处受控脱敏替换）；6 个合成夹具由固定生成器离屏重建；8 项 Canonical Evidence SHA-256 100% 匹配；构建与测试证据真实披露，无虚构或瞒报。
4. **推送操作安全无冲突**：远端当前仅有 `main`，目标分支未被占用；普通推送新分支不会对远端现有分支或源仓造成任何破坏。

### Push-Gate 边界与约束

1. **不可宣称事项**：
   - 本批准**仅针对将精确 commit `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` 作为 `origin` 新分支普通推送**。
   - 本批准**不等于产品发布验收**，**不等于父 Task 置为 done**（父 Task 仍保持 `in_review`，AC4 保持 `BLOCKED`，AC5 保持 `PARTIAL`）。
   - 本批准未修改任何失败证据，Core 3 组参数失败与 Rust 并发隔离风险仍保持既有事实。

2. **DSH 推送执行指令规范**：
   - 必须由 DSH（作为 Integrator / Push 权限持有者）执行普通推送；
   - 目标分支名称建议采用 `codex/clean-source-snapshot`；
   - **绝对禁止使用 `--force`**；
   - **绝对禁止推送至 `refs/heads/main`**；
   - **绝对禁止设置上游 tracking 或改写远端 default branch**；
   - 推荐执行命令示例：
     ```bash
     git -C "G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4" push origin e34a90d001cce1fa966aec7d2b032bb5ad1cf148:refs/heads/codex/clean-source-snapshot
     ```
   - 推送后需运行 `git ls-remote --heads origin` 确认远端 `main` 未变且新分支精确等于 `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。

### 剩余风险

1. **工作树非 Git 交付风险**：候选 live 工作树中包含 ignored 本地产物（node_modules、dist、测试生成日志），不得以直接拷贝目录或压缩包形式交付（F-001）。
2. **产品并发与环境能力边界**：Rust 默认并发测试存在 `UNREAPED_WORKER_REGISTRY` 共享状态污染未解除，Core 存在 Windows AppContainer 沙箱 ACL 限制（F-002）。后续若推进产品发布，须在新 head 上另行进行测试隔离修复与多通道饱和压力验收。
