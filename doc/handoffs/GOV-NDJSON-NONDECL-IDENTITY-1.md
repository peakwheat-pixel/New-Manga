---
task_id: GOV-NDJSON-NONDECL-IDENTITY-1
author: Codex
recipient: Codex
base_commit: 50d784300ac74d6ded633685bfce201cdddb630a
delivery_head: 488ab6cbec7774df8c0c3b2e8a9e169750a92101
status: in_review
---

# Handoff：两份NDJSON身份核验

结果详verification/GOV-NDJSON-NONDECL-IDENTITY-1/report.md、identity-proof.json、mechanism-proof.json、manifest-provenance.json及probe-run.log。R23未跟踪，raw bdabb170f9a415dd42855a0978fe557cae4ca1df97466ca143750b1ae288f7a1；R24已跟踪，raw caac6afde8d479cabcd839e2b74fdd86a1ecd8b59e5e8c88100a552382a9458e。原件不改写/不提交替代。总值6/64，种类1/4/1与1/62/1；每值用实际声明parser核验0声明/0错误；存在path/pin字符串，不能丢其证据或引用价值。

候选/负例6例EXIT0，正式默认before/after均32且完整身份相同；候选仅移除两项到30，其他30/保护集合保留。错路径/错hash/内存字节漂移拒绝，变化后的合法资源被解析；刻意登记合法资源新hash则可绕过，明确表明例外需可信内容审查，非安全PASS。没有真实改名/修改源；首次mock文件描述符错误已仅修workspace探针后复验，初始记录保留。产品/构建回归NOT_RUN，无产品/guard实现变更。98heads/136worktrees，无apply/清理/迁移/GC/prune/push。

现行默认表被旧Task EV-JSON-EXCEPTIONS固定为cacd1c021/blob SHA c2f185fb489e4b89be28cdfb139eb649c7022a718d0d27877be4ca0d8fa4adc4，磁盘既有CRLF raw238039dd3a9a70243ff8ffaee8dbf5b080e211cb8dc747de1a5da29211efdef2，已区分、不改旧pin。正式例外表未登记新项。DeepSeek独审待完成，源/工具/正式表raw及状态不变；全部资源保留，父Task继续blocked与STATUS/r212禁令有效。

## 下一任务建议（未释放）

Task：拟议GOV-NDJSON-EXCEPTION-CONFIG-1，建立当前配置并仅登记已核定两项。依赖本研究独审/closeout通过，先单独冻结Task/Plan/STATUS，不重开旧Task。Owner Codex / Reviewer DeepSeek Harness，理由是共享保护配置与默认入口须Lead负责。

Recovery：G:/CODEX/New Manga，main，固定base/head=488ab6cbec7774df8c0c3b2e8a9e169750a92101，后续治理尾部commit启动时实测；实现分支codex/gov-ndjson-exception-config-1、workspace工作树均待Codex创建，不把示例当现成资源。

允许写路径待冻结：tools/governance/non-declaration-json-exceptions.json（新当前配置，保留旧67逐项完整＋两精确path/raw SHA/reason）、tools/governance/clean_workspace.py仅DEFAULT_JSON_EXCEPTION_MANIFEST默认入口、自身Task/verification/Handoff、治理元数据。旧verification/WORKSPACE-DECLARATION-REMEDIATION-1表/Task/pins、原始P02日志、其它函数、用户数据、Schema/依赖禁止改写；不新增通用坏JSON/NDJSON匹配，不运行collector/Legacy，不apply/清理/归档/迁移/GC/prune/push。两条source raw一旦漂移即停，不能自动刷新hash。

交付与Gate：新配置语义来源矩阵、原67＋2条覆盖比较、仅默认常量改动、原日志/旧表raw与旧Git blob pin保全、默认实际仅32→30且其它30身份一致/原保护集合不减；错路径/hash/字节漂移/合法声明负例继续成立。使用现有机制/本研究有界探针作依据，若需新增源码测试则先冻结精确路径。pwsh -NoProfile -File tools/governance/check.ps1、git diff --check、必要回归与独立固定head Review/Handoff后由Codex集成；30残余仍fail-closed，不叫清理PASS。环境PowerShell/Python -B，NOT_RUN/BLOCKED明确记录。

可转发指令：Codex，请在G:/CODEX/New Manga的main核对实际HEAD/唯一租约，以488ab6cbec7774df8c0c3b2e8a9e169750a92101为恢复点读本Handoff和研究证据，先冻结拟议GOV-NDJSON-EXCEPTION-CONFIG-1（依赖本Task独审done，Owner Codex/Reviewer DeepSeek）。只新建当前配置tools/governance/non-declaration-json-exceptions.json保留原67＋固定两项，并仅切换clean_workspace.py默认配置常量；实现branch/worktree待Codex创建。保护旧表/旧Task/原pin/原日志，不改解析函数、Schema/依赖，不运行旧collector，不清理/GC/prune/push。源漂移则停，不自动重签hash。交付真实before/after32→30/其它30身份/保护集合和旧67完整证明、负例与旧证据raw/历史pin检查、固定commit独立Review/Handoff及治理check；本建议不是释放，不自动实施。

R1要求修正本Task证据表断行：新增table-registration-proof证明原10pin实际注册，同行原日志Manifest断行也同根因修复。旧checkpoint原字节作为历史SOURCE_PIN保留，当前指针改checkpoint-r2.md；report明确旧1704为修正前快照。只有本Task metadata/evidence变化，源/guard/正式表未动；旧10pin中仅本研究report修订后须重签自身新版本，其余内容保持原字节。
