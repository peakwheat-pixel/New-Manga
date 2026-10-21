---
task_id: GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
author: Codex
recipient: Codex
base_commit: f72dd96ee51f21cc24472b05cceaf488060b679a
delivery_head: 244d08e4eb5bb7aee1b6b54d0198093bcd16b48c
status: in_review
---

# Handoff：证据表实际注册

仅3个冻结Task的Canonical Evidence表内部空行删除15行；全部非空字节行/51条path/commit/SHA/class/原status/AC/Review完全不变，51原文件raw磁盘=blob=SHA。原Task不重开。实际注册9/12/0→19/19/13，0parser errors；保护1723→1753（修正时快照）只增，默认32错误完整身份不变。证据verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/registration-proof.json、report.md。无guard/正式表/用户/未跟踪内容/原证据变更，98/136、0删除/迁移/归档/远端操作。纯文档无产品测试，实际parser与raw pin核验均已执行。独审与最终治理/核销待完成。

下一步（用户已授权自动推进，但须另冻结）：GOV-NDJSON-EXCEPTION-CONFIG-1，Owner Codex/Reviewer DeepSeek Harness，依赖本Task独审done及已核定NDJSON研究。Recovery G:/CODEX/New Manga main，固定base/head=244d08e4eb5bb7aee1b6b54d0198093bcd16b48c；实现codex/gov-ndjson-exception-config-1及workspace工作树待Codex创建。允许写新tools/governance/non-declaration-json-exceptions.json（完整原67+两精确path/hash/reason）、clean_workspace.py仅DEFAULT_JSON_EXCEPTION_MANIFEST，自己Task/verification/Handoff/治理元数据及必要有界测试路径冻结后使用。禁止改旧Canonical表/旧Task/pin、原日志、其它guard逻辑、Schema/依赖、用户文件，禁apply/清理/迁移/GC/prune/push。交付69项来源矩阵、默认32→30/其它30身份与原保护集合不变、原67语义完整、raw旧证据保全、负例/独审/集成验证/Handoff。运行现有guard相关回归、pwsh -NoProfile -File tools/governance/check.ps1和diff-check；NOT_RUN/BLOCKED如实。可转发：Codex，在上述仓库main核对HEAD/租约，依244d08e4eb5bb7aee1b6b54d0198093bcd16b48c读取本Handoff，先冻结GOV-NDJSON-EXCEPTION-CONFIG-1再创建明确分支/worktree；只添加新当前配置和切换默认常量，原67+两固定raw条目不漂移，保持历史源/pin/保护及全部清理禁令。提交实际默认32→30/其它30身份/保护集合、原67及四输入raw保全、负例、固定commit独立DSH Review和Handoff，由Codex集成；此任务done不解除任何清理授权要求。

R1复核前置差异：base不存在的新JSON不能用空字节保留枚举；那会人为制造scope/proof两JSON_PARSE。正确base枚举排除新增文件，base32/head32相同、1722旧根是1758子集；三个base实际注册9/12/0、0error。新增证明冻结具体旧reviewed_head=fa18dc2c6，后续新增证据会改变HEAD枚举，但正确方法不变。未做历史未跟踪字节重建，不用Git冒称全体未跟踪文件未变。原3表/51pin/原证据不修改。
