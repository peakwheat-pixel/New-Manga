---
task_id: M2-S2
reviewer: Antigravity
author: ZCode
base_commit: 67c3d56ea77acd5b214877509bbcd1cffe5890f7
reviewed_head: fbdf1bc237a2c34db7546e76990f3aad29dfae8d
decision: approved
---

# Review：M2-S2 — Resource Channel Security Verification Spike

本 Review 是由 **Antigravity** 对 **ZCode** 交付的 `M2-S2`（Resource Channel Security Verification Spike）执行的非作者独立审查。
被审基线与提交：
- **base_commit**：`67c3d56ea77acd5b214877509bbcd1cffe5890f7`（`master` 分支 M2-S1 集成收尾提交）
- **delivery_head**：`d502aa5af88159a78ad1b39030f8780cca4021f7`
- **reviewed_head**：`fbdf1bc237a2c34db7546e76990f3aad29dfae8d`（含正式 Handoff 与 Task 状态置为 `in_review`）

---

## 范围与依据

### 1. 依据文档与输入事实
- 规划事实源：[REBASELINE_PLAN.md](file:///g:/CODEX/New%20Manga/doc/REBASELINE_PLAN.md)、[STATUS.md](file:///g:/CODEX/New%20Manga/doc/STATUS.md)
- 协作协议：[09_COLLABORATION.md](file:///g:/CODEX/New%20Manga/doc/09_COLLABORATION.md) §6
- 需求来源：[M2-S1 研究报告](file:///g:/CODEX/New%20Manga/doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md) §8.2 的安全 Blocker **S1-B11**（TOCTOU）与 **S1-B12**（引用保密性），以及用户授权代行裁决的 [M2-S1 §7 产品阈值裁决](file:///g:/CODEX/New%20Manga/verification/M2-S1/product-thresholds-ruling-67c3d56.md)（裁决 T5.4 分层信任模型）
- 任务定义：[doc/tasks/M2-S2.md](file:///g:/CODEX/New%20Manga/doc/tasks/M2-S2.md)
- 交付成果：[doc/research/M2-S2_SECURITY_VERIFICATION_SPIKE.md](file:///g:/CODEX/New%20Manga/doc/research/M2-S2_SECURITY_VERIFICATION_SPIKE.md)、[doc/handoffs/M2-S2-d502aa5a.md](file:///g:/CODEX/New%20Manga/doc/handoffs/M2-S2-d502aa5a.md)、`verification/M2-S2/**`

### 2. 变更路径核查（`git diff --name-status 67c3d56e..fbdf1bc2`）
共涉及 24 个文件，全部严格落在 Task 授权的 4 类路径范围内：
1. `doc/tasks/M2-S2.md`（A，内容源于治理提交 `7671f0c1`，仅追加运行记录与 AC 回填）
2. `doc/research/M2-S2_SECURITY_VERIFICATION_SPIKE.md`（A，研究报告）
3. `doc/handoffs/M2-S2-d502aa5a.md`（A，正式 Handoff）
4. `verification/M2-S2/**`（A，21 个文件，包含基线自检、原型代码、探针测试套件、原始日志与结果 JSON）

**禁止范围核查**：
- 未修改 `src/**`、`tests/**`、`packaging/**`、`src-tauri/**`；
- 未修改 React/QML、Schema/migration、依赖文件（`requirements*.txt`）；
- 未修改 `doc/contracts/**`、`AD-001`、`doc/00_INDEX.md`、`doc/STATUS.md` 或 M2-S1 既有交付物；
- `git diff --check 67c3d56e fbdf1bc2` 执行退出码为 0，无任何代码空白格式或冲突标记。

### 3. 未审到的部分
本 Task 为隔离研究与安全验证 Spike（`kind: research`），不包含产品运行时代码。真实生产环境的 Tauri asset protocol 绑定、React consumer 挂载、MSIX/AppContainer 打包沙箱复跑（依赖 S1-B8）以及系统 DACL/完整性级别设计（依赖 S1-B3）未在此处实现，已如实列入报告的 `NOT_RUN` 清单，未做超出原型范围的审查推断。

---

## Standards 视角

1. **协作与治理规范**：
   - 严格遵循 [09_COLLABORATION.md](file:///g:/CODEX/New%20Manga/doc/09_COLLABORATION.md) 规定的多 worktree 协作模型与命名规范；作者（ZCode）与审阅者（Antigravity）明确隔离，无作者自审或擅自合并主线行为。
2. **代码与架构边界**：
   - 原型实现位于 `verification/M2-S2/probes/`，完全使用 Python 3.14 标准库（`ctypes`, `hashlib`, `hmac`, `secrets`, `pathlib`），未对生产环境引入任何未冻结的第三方库或侵入 `src/**`。
   - 所有测试 fixture 均在 `%TEMP%\m2s2-lab` 临时目录下生成，严格保护用户真实数据与本地资产。
3. **证据纪律（D08 / Q-009）**：
   - 交付物中完整归档了权威转录日志 `verification/M2-S2/raw/00-run-all.log`，包含每步的 shell 类型、Python 解释器路径及命令 exit code；
   - 判别力证据具备结构化 JSON 成果（`toctou-result.json`, `mapping-result.json`, `09-repeat-consistency.json`），数据完全可机器核验与人工复核，未以无日志散文替代证据。

---

## Spec 视角

对 [M2-S2 Task](file:///g:/CODEX/New%20Manga/doc/tasks/M2-S2.md) 定义的 6 项 Acceptance Criteria 进行逐项对照核查：

| AC 项 | 规范要求 | 实际实现与证据 | 审阅判断 |
|---|---|---|---|
| **S2-AC1 范围与基线** | 固定 base `67c3d56e`；记录 `git rev-parse` 五件套；Contract blob 核对一致；不触碰主工作区 | `verification/M2-S2/baseline-selfcheck.md` 完整记录，Contract blob `4b503a17...` 严格一致 | **PASS** |
| **S2-AC2 参考解析器** | 隔离原型实现 open-then-verify-from-handle；身份+大小+包含性从句柄校验；读取仅经句柄；docstring 诚实标注边界 | `verification/M2-S2/probes/m2s2_lab.py::HandleVerifiedResolver`；严密校验顺序；保留 `UNVERIFIED` 边界 | **PASS** |
| **S2-AC3 负向探针** | 覆盖并发内容替换（大/小）、目录 junction 与符号链接、等大小内容替换、scope root 与父目录可写；全部类型化拒绝；对照组正常 | `probe_s2_toctou.py` 覆盖 16 个场景（T-01P..T-21），16/16 全部产生匹配的类型化拒绝码，restore 恢复检查全部通过 | **PASS** |
| **S2-AC4 映射 ID 原型** | Core 侧不透明随机映射 ID；探针证明无 Core 时无法还原路径/资源标识；无映射表泄漏；撤销/过期类型化 | `probe_s2_mapping.py` 覆盖 8 个场景（M-01..M-08），8/8 全部通过，归纳性证明边界如实标注 | **PASS** |
| **S2-AC5 报告与证据** | 形成研究报告，逐条对照 M2-S1 §8.2 解除条件，明确列出 NOT_RUN / UNVERIFIED 清单，不宣称产品级保证 | `doc/research/M2-S2_SECURITY_VERIFICATION_SPIKE.md` §6 对照，§7 包含 11 项 NOT_RUN 与 3 项 UNVERIFIED | **PASS** |
| **S2-AC6 范围与交接** | 保存 diff 快照与 whitespace check；核心代码零改动；正式 Handoff 文档齐全 | `doc/handoffs/M2-S2-d502aa5a.md`、`verification/M2-S2/raw/10-delivery-diff.log` 完整记录 | **PASS** |

### 重点核查项（五项核实）
1. **解析器校验顺序与错误码语义（`m2s2_lab.py`）**：
   - 顺序：Token 校验（结构/HMAC/过期/撤销/scope/mode/词法）→ 预打开 reparse walk 早期拦截 → 单次 `CreateFileW` 打开（带 `FILE_FLAG_BACKUP_SEMANTICS` 与共享模式）→ 句柄层校验（`GetFinalPathNameByHandle` containment 防逃逸 → `GetFileInformationByHandle` 文件身份 `volume serial + file index` → 文件大小校验与探针上限 → 句柄 reparse tag）→ 仅经句柄读取（`ReadFile`）→ 内容 SHA-256 digest 校验 → 读后句柄身份复核。
   - 错误码语义：全部采用稳定的一级错误码常量（`REF_OUT_OF_SCOPE`, `FILE_IDENTITY_CHANGED`, `FILE_SIZE_CHANGED`, `MEDIA_TOO_LARGE_BY_HANDLE`, `CONTENT_DIGEST_MISMATCH`, `OPEN_FAILED_SHARING_VIOLATION` 等），无模糊字符串匹配。
2. **digest 层“签发时刻内容可信”前提**：
   - 报告 §3 与 §7 明确指出：SHA-256 保证的是“解析读取的内容 = 签发时刻的内容”，该层的前提是签发时刻内容本身已由 Core 生产发布流程保证为合法的。报告未将其夸大为能自发验证源内容合法性。
3. **NTFS file index 复用限制**：
   - 报告在 docstring 及 §1.5、§7 中明确披露：在 NTFS 文件系统上，文件删除后 file index 理论上可能被新文件复用；因此句柄身份检查配合签发时刻的内容 digest（以及窄共享锁）构成了深度防御链条。该物理局限性已被诚实记录。
4. **映射 ID 不透明性的归纳性表述**：
   - 报告 §5 与 §7 明确说明：M-02..M-05 的“不可还原”是基于所构造的有限攻击空间（涵盖子串提取、各种常见编解码、哈希字典、5,225 次猜测枚举及近邻变体），属于“归纳性证据（inductive evidence）”，并非信息论密码学证明，且 Core 内存态映射表在攻击者攻破操作系统 host 时超出保护边界。表述客观严谨。
5. **NOT_RUN 清单真实性**：
   - S1-B11 条件③中的“目标打包/沙箱形态（MSIX/AppContainer）下复跑”被明确标记为 `NOT_RUN`（依赖 S1-B8）；
   - S1-B11 条件④“DACL/完整性级别”被明确标记为 `NOT_RUN`（依赖 S1-B3）；
   - 共有 11 项明确的 `NOT_RUN` 与 3 项 `UNVERIFIED`，未发生将未执行项冒充为通过的虚假报告。

---

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **R-001** | P2 | `verification/M2-S2/probes/run_all.ps1:16`<br>`verification/M2-S2/probes/m2s2_lab.py:758, 892` | **Windows 中文 GBK 控制台环境下运行探针发生 `UnicodeEncodeError`**：<br>1. `make_junction` 中 `cmd.exe /c mklink /J` 输出中文字符“为”（GBK 编码 `0xCE 0xAA`），被误以 UTF-8 解码为希腊字母 `\u03aa`；<br>2. `emit()` 中调用 `print(text)`（`ensure_ascii=False`），在未设置 UTF-8 环境变量的中文 Windows 控制台（默认代码页 936 / cp936）下抛出 `UnicodeEncodeError: 'gbk' codec can't encode character '\u03aa'`，导致直接调用 `run_all.ps1` 退出码为 1。 | 在默认 PowerShell 会话中直接运行：<br>`pwsh -NoProfile -File verification/M2-S2/probes/run_all.ps1`<br>直接在 step probe S2-TOCTOU 抛出编码异常。<br>规避方式：显式注入 `$env:PYTHONUTF8='1'` 后即可全通。 | 建议在后续脚本维护或契约实现中：<br>1. `run_all.ps1` 开头显式声明 `$env:PYTHONUTF8 = "1"` 与 `$env:PYTHONIOENCODING = "utf-8"`；<br>2. 或在 `m2s2_lab.py` 的 `emit()` 中设置 `ensure_ascii=True` 或对 `sys.stdout` 执行 UTF-8 reconfigure。 | deferred（P2，不阻塞本研究 Spike 结论；在 UTF-8 声明下 24 场景全通） |

> **Findings 统计**：P0 = 0，P1 = 0，P2 = 1（非阻塞，已提供明确规避与复现方案）。

---

## 验证

### 1. 实际复跑与环境核实

| 场景 / 步骤 | 实际执行命令 | 执行环境 | 结果 | 证据 |
|---|---|---|---|---|
| **Git 范围与空白核查** | `git diff --name-status 67c3d56e..fbdf1bc2`<br>`git diff --check 67c3d56e fbdf1bc2` | Reviewer 独立 worktree（`G:/CODEX/New Manga.worktrees/M2-S2-antigravity-review-fbdf1bc2`） | **PASS** | 24 个文件全部在授权范围内；`--check` 退出码 0，无空白违规 |
| **S2 探针全套复跑** | `pwsh -NoProfile -Command "& { $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; pwsh -NoProfile -File verification/M2-S2/probes/run_all.ps1 }"` | Windows NT 10.0.26200.0, Python 3.14.6, 临时数据目录 `%TEMP%\m2s2-lab` | **PASS** | 所有步骤全部 exit 0：<br>- make fixtures: exit 0<br>- TOCTOU (first): 16/16 PASS, exit 0<br>- MAPPING (first): 8/8 PASS, exit 0<br>- make fixtures (repeat): exit 0<br>- TOCTOU (repeat): 16/16 PASS, exit 0<br>- MAPPING (repeat): 8/8 PASS, exit 0<br>- repeat consistency: exit 0, `consistent: true` |
| **脚本哈希与换行符核实** | 对比磁盘文件哈希与 `01-script-hashes.log` | Python 3.14 / git 仓库树比对 | **PASS** | Windows 检出时为 CRLF，经规范化 LF 后 SHA-256 与作者提交日志记录 100% 一致 |
| **重跑一致性比对** | `compare_runs.py` 对比首轮与复跑结果 | 同上 | **PASS** | `raw/09-repeat-consistency.json` 显示 `differences: []`, `consistent: true` |

### 2. 双面结论
- **Architecture 维度：PASS**
  参考解析器 `HandleVerifiedResolver` 提出的“单次打开，从句柄校验路径包含性、文件物理身份与大小，且仅经该句柄读取”方案，逻辑自洽，成功切断了 `check-then-use` 竞态窗口。映射 ID 方案遵循分层信任边界（WebView 层仅见不透明 ID，Core 侧查表解析），有效保护了本地文件系统路径与资源标识。
- **Verification 维度：PASS**
  全套 24 个测试场景（16 个 TOCTOU 负向/正向攻击与恢复测试 + 8 个映射 ID 不透明性、格式、字典枚举、零泄漏与生命周期测试）在独立审查环境中全部真实执行并通过，复跑一致性完全满足要求。

---

## 结论与复审

- **审查结论**：`approved`
- **处理建议**：
  ZCode 交付的 M2-S2 研究成果、原型脚本、原始日志与研究报告严密完备，AC 逐项落地，各项诚实边界与限制说明完整。P0/P1 缺陷为 0。唯一的 P2 缺陷为测试脚手架的控制台编码兼容性，已查明机理并不影响核心安全验证结论。
- **推荐下一步**：
  交由 **Codex** 执行主线集成，将 `agent/zcode/M2-S2-resource-channel-security`（head `fbdf1bc2`）以及本 Review 报告集成进 master，更新 `doc/STATUS.md` 与任务索引。
