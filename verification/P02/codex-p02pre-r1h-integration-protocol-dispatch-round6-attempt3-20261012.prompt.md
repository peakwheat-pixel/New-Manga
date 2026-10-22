# P02PRE-R1H Round6 attempt3 — 独立静态协议 Review

你是本轮非作者 Reviewer：DeepSeek Harness。请仅审查冻结的执行器和协议，不执行、修改或修复任何输入。

## 固定审查对象与状态

仓库：G:\CODEX\New Manga。主线固定为 main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b，index SHA-256=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C。Owner worktree 固定为 C:/Users/49745/.codex/worktrees/p02pre-r1h-codex，branch=agent/codex/P02PRE-R1H，HEAD=c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d，tree=96e7273ddd5fd27bee567bba27f19453cabe0842。

主要审查对象：

- Executor: verification/P02/p02pre-r1h-round6-integrator-20261012.ps1, 40604 bytes, SHA-256 DACDD544784A035E980F74250207D8EB561E13D0C5A06AA9F810DA9A1B29F222.
- Controlling protocol supplement: verification/P02/p02pre-r1h-round6-integration-protocol-attempt3-20261012.md, 11730 bytes, SHA-256 CAA5984BDAC01DE4A81E10154A9677D04F9A48DB40CB96804B6ECF8DA7F35313.
- Immutable prior protocol: verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md, SHA-256 26E152C31EF9111ECA55BAB96C3783F249329C5DE111909E9B8C55B2DD666697.
- Exact 40-input manifest: verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-attempt3-20261012.json.

本轮执行器、File.Replace、Parser/selfcheck、capability query、capture/getters、AppContainer/profile/registry/ACL API、动态隔离、Build/Cargo、系统 AC1–AC7 均未运行。历史 Round5 AC2=FAILED，不是本轮测试结果。当前 Gate 原值：private_registry_absence=UNPROVABLE；Technical Gate=NOT_SATISFIED；Owner Risk Acceptance=APPROVED；Gate Disposition=WAIVED_BY_OWNER；Build Authorization=AUTHORIZED_WITH_EXCEPTION；残余原句=technical condition unmet; user explicitly accepted residual risk；Build Gate=BLOCKED；Hard Build Barrier=EFFECTIVE；Build/Cargo=NOT_RUN；系统 AC1–AC7=BLOCKED / NOT_RUN。用户允许后续在依赖和安全检查满足后自动继续 P02PRE、动态验证、Build/Cargo、AC、修复/Review/重测/集成；这不把本协议审查或任何 Gate/AC 预先判为 PASS。Windows Sandbox 禁止触碰。用户已撤销任务完成后关机的要求。

## Pin 完整性

在开始静态审查前，以及完成审查后，逐一对 pins JSON 的 40 个 exact input path 读取文件原始字节，核对 byte length 和 SHA-256。只读这些明确列出的文件；不要目录遍历。不得运行 Git status，也不得访问 .tmp.driveupload。若文件缺失或有任一 hash/length 不符，停止内容审查并报告 BLOCKED_PIN_MISMATCH，逐项列明差异。只允许对 pins 中列出的输入做静态读取/hash，不得探查其他仓库路径。

## 静态审查要求

请重点独立判断：

1. protocol 与 executor 是否一致；每个写入目标是否精确、受 allowlist 限定，并通过 CreateNew 或唯一的三参数 System.IO.File.Replace 达成；是否有未列明的路径/API/写入或清理/重试。
2. 在 execution evidence CreateNew 之前是否严格无 status；S0、单独的 pre-stage-owner snapshot、stage/recovery/Handoff 与 S1 的顺序和 delta 是否正确；File.Replace 是否恰好一次；S2 是否为 Replace 返回后的第一个 child；S2/S3 与失败诊断是否符合冻结协议。
3. Git child executable/CWD/argv/environment 边界，固定 refs/index/status identity，status pathspec 是否把 :(exclude).tmp.driveupload 作为独立参数，status parser 与 delta comparator 是否 fail-closed。
4. Toolhelp process observer 的真实边界：P/Invoke 的定义 API/metadata 是否足以创建有效方法；native return/BOOL marshalling、SetLastError、Marshal.GetLastPInvokeError、PROCESSENTRY32W.dwSize/x86-x64 offsets、snapshot handle close、pid/descendant attribution、pipe drain/timeout和快速/短暂子进程遗漏风险。明确区分静态可证与必须运行后才能验证的事项。协议引用的 Microsoft Learn API 文档可作为一手依据。
5. File state/ACL/stream/index/hash/parent checks、protected input preservation、failure handling、partial evidence、无删除/rollback/retry是否足以避免数据损失或越权写入。
6. Reviewer 是否非作者；Review verdict 是否只能是静态协议批准，是否明确不构成执行、Gate、Build、AC PASS；残余风险与用户 waiver 是否被精确保留。
7. 指出任何 P0/P1/P2/P3 finding，给出精确文件、行号、证据、影响和最小修复建议；没有 finding 时也说明审查范围与剩余的 NOT_VERIFIED 限制。

## 执行限制

- 只做只读静态 Review；不得运行 p02pre-r1h-round6-integrator-20261012.ps1，任何测试、Parser/selfcheck/capability query、Git 命令、Windows API、profile/registry/ACL操作、Build/Cargo、capture/getter、AC 或 Windows Sandbox。
- 不要修改/覆盖/删除任何 input；不做自动修复。不要创建 Review 文件。将报告以文本返回到本次 DSH session stdout，由 Codex 原样保存到唯一 report target。
- 结论只允许 APPROVED_STATIC_PROTOCOL、CHANGES_REQUESTED 或 BLOCKED_PIN_MISMATCH。P0/P1/P2 任一大于 0 时必须为 CHANGES_REQUESTED；P3 不阻止静态批准，但必须记录。静态批准不是执行或 Gate release。

输出 Markdown，至少包含：Verdict；P0/P1/P2/P3 counts；前后 pin 核对数量与结果；实际读取对象；逐条 finding（精确路径/行号）；未验证限制；确认未运行/未修改输入。若模型/力度可见，按实际记录；否则写 UNKNOWN。