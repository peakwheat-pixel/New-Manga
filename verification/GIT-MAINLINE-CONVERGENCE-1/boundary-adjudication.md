# 保护与独有支线处置边界 — Codex 技术裁定

2026-10-21；用户要求先明确边界再继续，并明确 STATUS/r212 禁令仍有效。Git基线 b13d4f25b；主控 Codex epoch9；原有 tracked dirty=0。

## 已明确的边界

1. 所有135工作树继续原位保留；125个已有保护命中不得解除，dirty/untracked/ignored/会话/源数据不移动、不改写、不删除。不把这一裁定当作迁移/归档/清理授权。
2. main 是唯一开发/集成主线；旧支线不释放新实施。旧主线引用按现规则保留。19个未合并分支的内容路线如下，实际操作统一是保留分支及工作树；路线分类不等于用户放弃独有提交。
3. P14/P22的现代代码只进入未来只读评估候选：P14由ZCode主责UI相关设计/实现，P22由Codex先核对共享传输边界。任何修复另冻Task并独审，本轮不改产品代码。
4. 两个patch全等价分支不重复集成；Legacy实现、旧规划和历史证据不盲合并、不覆盖当前权威文件。历史工具不启动旧Task、不再释放Legacy诊断/修复。
5. 77项声明错误先分离：45项标准模板路径列表头兼容是技术修复候选；其余32项仍保持错误，泛化/环境/歧义/损坏/未知disposition需逐项取证或来源Owner裁定，禁止统一忽略。
6. 唯一获准备释放的下一实施范围为固定表头兼容：只识别完整字面量 path（仓库相对路径或绝对路径），同时处理重复身份列；其他别名/模糊匹配不接受；不得减少原有保护根。此项共享工具语义变更须单独Task冻结与独立Review，不沿用旧Task批准。
7. 普通-d无法移除的19支线仍保留；不使用-D/update-ref等旁路，不为数量目标合并旧代码。任何未来迁移/删除需新备份（含适用未提交/ignored/会话）、源/目标/hash映射、占用确认、精确授权窗口。

## 19条支线逐项内容路线

|分支|固定tip|内容路线|依据/禁止项|
|---|---|---|---|
|agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3|c763efa27db0f10949a52416f1374e88173a31e2|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/antigravity/P22-roundtrip-serialization|4a707db80499f11e93cee163a9a10bf6392b1a92|NEW_ARCH_READ_ONLY_ASSESSMENT|实际涉及 React/Tauri 代码；先核对当前实现/需求/测试，禁止直接合并|
|agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION|4569093db896b019cfab401e35b66ed4bcea673d|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW|a6f33f7be1fc13cca64539ecaaa4bd9528a0184e|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION|06990b7993d042ae5e74ab479e291e494b622588|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE|23bec747df77e67e93ec1fa9fd859d077219e941|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/P02-NEW-TIME-BASELINE|7ab5b7d0574041f2ca9fa1424ca5b440ff298aaf|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION|10c35daed241aa3717b248da14c1b9b959ff1fba|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION|0af8980884e9d027042ef145cd966577d86b5bc5|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION|14da1e814931e1e32ebc1f76a12bc3685b63646e|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/P02PRE-R1H-H2-COLLECTOR|4a90d820a5d58a54cbc190665fbd87d563bc19af|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|agent/zcode/T2.2.1-reader-workbench-polish|df637df1f9d6e8468bc73d6ff585bbf55e8e9a64|PATCH_EQUIVALENT_HISTORY|非 merge patch 已等价移植；保留原提交及证据，不代表 refs 可删|
|agent/zcode/T3.2.1-repair-13|13ae23f65e963cf1d5aea19634572627e5e709db|LEGACY_HISTORY_ONLY|包含 QML/PyInstaller 历史实现；不进入新架构实施|
|codex/P02-hook-cache-isolation-plan|ceca2446da88df23a719f40868cc89e1481ccb2c|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|codex/P14|41c3206942730536bc9b41e871f23ad9b3de3f1d|NEW_ARCH_READ_ONLY_ASSESSMENT|实际涉及 React/Tauri 代码；先核对当前实现/需求/测试，禁止直接合并|
|codex/P15-C1-FU2|0aa01eddcd751adf9c4d2e3894f4cce9ec657909|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|codex/project-roadmap-rebaseline|000cbfe9909c3eb566fd4d077c77199ce4d7c86e|UNRELEASED_PLAN_HISTORY_ONLY|未释放旧规划草案；不得覆盖当前 Plan/STATUS|
|review/deepseek/M2-C1-typed-ipc-7d908a5|e6fc3a59b913f2aef1ab8c7a77ff47df0cd114a1|HISTORICAL_EVIDENCE_OR_CONTRACT|含证据/工具/旧契约修订，保存历史，不用旧状态激活；需要的现代行为另行专项复现|
|review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2|daab1996b99c7036108bc505cc3db29b744fdf9d|PATCH_EQUIVALENT_HISTORY|非 merge patch 已等价移植；保留原提交及证据，不代表 refs 可删|

## 兼容模拟的核验门槛

只在内存替换列名识别和重复列检测，不改任何源文件：baseline 77 errors /1277保护根；simulation 32 errors /1687保护根。旧保护根集合是新集合子集，新增410根。重复 path+别名 被拒绝，任意其它中文说明列和source_path别名不接受。完整原始错误矩阵见 header-alias-simulation.json。

模拟不是实现批准。后续Task要跑真实实现的正反例、既有安全回归、真实仓库审计与同快照保护集合对比；即便32错误不再是77，仍然fail-closed，不发布删除清单。

GIT-MAINLINE-CONVERGENCE-1 完整目标仍blocked；可先推进不触碰保护资源的独立工具兼容Task，不能因此改成done。
