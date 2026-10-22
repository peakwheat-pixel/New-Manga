# P02PRE-R1 R4 manifest 状态文字窄复核意见

**结论：`APPROVED`（仅 Review 判断，不是技术 Gate PASS，也不是执行授权）**
计数：P0=`0` / P1=`0` / P2=`0` / P3=`0`（无 finding；仅 3 条不影响结论的观察，列于 §四）
本轮**未重跑源码 Review**，**未执行任何命令**，**未复算任何 hash**。以下结论全部基于给定文件内可见文字。

---

## 一、复核问题 1｜manifest 第 9、13 行与流程顺序

**`manifest:9`（现文，逐字）**：
> 本对象=`R4_FROZEN_FOR_ONE_READ_ONLY_CAPTURE`；R4 全量 Review 与两次 focused follow-up 已完成：19 项历史 findings、`P3-DOC-1` 和 `P3-PIN-1` 均已关闭；`P3-PIN-1` 是 Reviewer 报告转录错误。R3 的路径/ACL 修订已在 R4 审查，脚本与 R4 parser bytes 未变。**Codex 必须先对最终 manifest/script pins 作 pre-run adjudication，之后才可按本 Task 运行唯一一次只读取证。**

- ✅ **不再声称等待已完成的 R4 Review**：R4 全量 Review 与两次 focused follow-up 明确写成“已完成”，对象状态改为 `R4_FROZEN_FOR_ONE_READ_ONLY_CAPTURE`，已无“须经第四轮独立 Review”之类的待办表述。
- ✅ **顺序可辨**：“**先** pre-run adjudication → **之后**才运行唯一一次只读取证”，前置关系清晰，且“唯一一次”明确。

**`manifest:13`（现文，逐字）**：
> ……R4 parser command 只用 Windows PowerShell 5.1 `ScriptBlock::Create` 解析脚本，不执行脚本；**host capture 仅在最终 manifest/script pins 经独立 Review 且 Codex 完成 pre-run adjudication 后单独调用一次**。

- ✅ 已删除上一版“第二轮 Review”的过期前置；现要求的是“最终 pins 经独立 Review **且** Codex 完成 pre-run adjudication”，与 `:9` 一致，无相互矛盾。
- ✅ 仍明确“parser 不执行脚本”“host capture 单独调用一次”，未扩张执行语义。

**判定：问题 1 = 通过。** 两行合起来可清楚看出“最终 manifest/script pins → pre-run adjudication → 唯一一次只读取证”的顺序。

---

## 二、复核问题 2｜文字是否如实记录

| 需如实的陈述 | 文件依据（可见文字） | 判定 |
|---|---|---|
| 19 个历史 findings 均 closed | `Task:76`「Round 1/2/3 的 19 项 findings 全部判为 `CLOSED`」；`manifest:9`「19 项历史 findings……均已关闭」（11+5+3=19 与 Task 各轮记录一致） | ✅ 一致 |
| `P3-DOC-1` closed | `followup#1` 判 P3-DOC-1 闭合（`Task:82` 复述）；本轮 `manifest:9` 列其已关闭 | ✅ 一致 |
| `P3-PIN-1` closed，且系 Reviewer 自身转录错误 | `followup#2:5`「`CLOSED` —— 确认是我上一份报告的转录错误，不是仓库 pin/证据不一致」；`:34`「`97400A9E...` 是唯一共同值；`97D00A9E...` 仅存在于我的报告文字中」；`manifest:9`、`Task:84` 同述 | ✅ 一致 |
| 不声称 DSH 独立 hash | `followup#2:43、52、67`：「未独立复算任何 hash」「hash 级独立绑定未成立」；`Task:76`「hash pins 未独立复算」；`manifest:9` 无任何独立 hash 声明 | ✅ 一致 |
| script/parser bytes 未变 | 各处 pin 一致：script `38729 bytes / 97400A9E…84AB`（`plan:11`、`status:11`、`Task:78`、R4 prompt L10）；parser `2086 bytes / 1AE3462C…5841`（`Task:78`、`plan:11`；JSON 三处 `inputSha256` 与 `inputByteCount` 自洽） | ✅ 一致（内容级；字节级见 §五） |
| R4 full Review 结果 | 给定 pin `18995 bytes / DD099DCD…ED98`，`0/0/0/1`，仅剩 P3-DOC-1 —— 与 `Task:76` 记载一致 | ✅ 一致 |

**判定：问题 2 = 通过**（逐项如实，无拔高，无“已批准/已通过”的虚假声明）。

---

## 三、复核问题 3｜两处 prose 更新是否扩张范围

- `:9`/`:13` 的改动**只涉及状态与前置顺序**，未新增任何执行对象。`:13` 仍指向同一脚本、同一执行 shell 精确路径（`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`）、同一 argv（`-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1-capture.ps1`）与同一 CWD。
- `:14` 子进程 allowlist 未变（仍仅 `git.exe` 四组固定参数 + `whoami.exe /all`，无 shell/package manager/compiler/network/COM）。
- **写入范围未扩张**：`ps1` 全文检索（`CreateNew|New-Item|Out-File|Set-Content|Add-Content|Remove-Item|Set-Acl|New-ItemProperty|Set-ItemProperty|Add-Type|Start-Process|Invoke-Expression|Registry::|CreateAppContainerProfile|DeleteAppContainerProfile`）**仅命中 1 处**：`p02pre-r1-capture.ps1:546` 的
  `[IO.File]::Open($EvidencePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)` —— 与 `manifest:15` 记载的唯一 evidence target（`…\verification\P02\p02pre-r1-evidence-20261011.json`）完全相同。
- **无 AC / Gate 权限扩张**：manifest 与 Task 中 Gate 文字未变；`Task:23` 仍逐字保留 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、`technical condition unmet; user explicitly accepted residual risk`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo 与 AC1–AC7=`NOT_RUN`。manifest `:16-17`（64 MiB partial 语义）、`:46`/`:48`（leaves 只读）、`:69`（禁止项：无 profile API/registry 写/ACL 修改/canary/build/Cargo/AC/Sandbox）、`:71`（分类口径）、`:73`（停机规则）与上一版逐字一致。

**判定：问题 3 = 通过**——未扩张执行对象、路径、进程、argv、写入范围、AC 或 Gate；证据写入仍只有那一处 `CreateNew`。

---

## 四、Findings 与观察

**Findings：无（P0/P1/P2/P3 = 0/0/0/0）。** 以下 3 条为**不影响结论**的文字观察，建议在 Codex adjudication 记录中一并留痕，无需回头修改（若一并修正，属同批文档微调，不需重跑审查）：

1. **`manifest:9` 三分类并列的读法**：文字为“19 项历史 findings、`P3-DOC-1` 和 `P3-PIN-1` 均已关闭”。字面读法含混（19 项属 Round 1–3，`P3-DOC-1` 属 R4 全量 Review，`P3-PIN-1` 属 follow-up #1 的自纠）。`Task:76`/`:82`/`:84` 的逐轮记录已把归属写清，故仅为同一事实的压缩表述，不构成误导性声明。
2. **`manifest:13` 的“经独立 Review”未限定轮次**：结合 `:9`（R4 全量 + 两次 follow-up 已完成）可正确解读为“已完成的那一轮独立 Review”，但句子本身未点明轮次编号，建议后续版本文本可补“(R4 + focused follow-up)”。
3. **R4/F4 两处记录时间戳未在本轮核查**：manifest 的 12615 bytes 与 pin 一致但我无法复算（见 §五）；未做时间序列核对，故本轮不就“先后顺序的时间戳证据”表态。

---

## 五、DSH 是否独立复算 hash

**没有。** 本会话 `pwsh` 工具仍在沙箱准备阶段失败：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)
```

按指令**未**做 ACL 修改、未提权重试、未绕行、未换 shell，也未执行 `Get-FileHash`/`certutil` 等任何 hash 命令。因此：

- `12615 / 38729 / 2086 / 18995 / 15629 bytes` 及各自 SHA-256 与 pin 的**匹配未经我独立确认**；
- 我的结论仅限于**文件内可见字符串之间是否自洽**（例如 parser JSON 三处 `inputSha256` 与 `inputByteCount`、各 prompt/Task/Plan/STATUS 的 pin 字面值一致性）；
- **`NOT_VERIFIED` 项**：任何 bytes/SHA 的独立复算、script 字节级未变性的独立证明、scratch 实际 HEAD/tree、任何宿主/OS 条件。
- 静态复核**不证明脚本已运行**，也不证明任何宿主条件通过。

---

## 六、当前 bytes 是否可进入 Codex pre-run adjudication

- **可以进入 Codex pre-run adjudication**。理由：三问均通过；无未闭合 finding；manifest `:9`/`:13` 已准确反映 R4 全量 Review 与两次 focused follow-up 的结论与顺序，且未扩张任何执行/写入/Gate 权限；脚本仍只有 `:546` 一处 `CreateNew` 证据写入；证据文件 `verification/P02/p02pre-r1-evidence-20261011.json` 当前不存在（此前 glob 实测，本轮未复核其存在性 → 该项 `NOT_VERIFIED`）。
- **adjudication 前置条件（不可省略）**：adjudicator 需对**最终 manifest（`12615 bytes / A5510774…C67A`）与脚本（`38729 bytes / 97400A9E…84AB`）pins** 作独立复算与绑定；在 adjudication 完成并绑定这些 pins 之前，不得运行 capture。
- adjudication 通过后，方可按 `manifest:13` 执行**唯一一次**只读采集；期间不得创建证据 JSON，不得进行任何 profile/ACL/registry/canary/build/Cargo/AC/Sandbox 动作。
- **Gates/状态保持原样（本 Review 不授权任何变更）**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

**（本报告为静态只读窄复核；`APPROVED` 仅为 Review 判断，不是技术 Gate PASS，也不等于执行授权；hash 级独立绑定未成立，见 §五。）**
