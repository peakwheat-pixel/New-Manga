# Codex adjudication：Forensic recovery r2

2026-10-13；DSH session-4bb6a005-5f18-4aac-a103-1449c329d9c7，r1/r2 exit0；r2 APPROVED_DIAGNOSTIC。Codex 是本诊断材料的整合作者，独立审查由非作者 DSH 完成；不声称 Codex 对自己的诊断是非作者。base/reviewed head=343895fb5f0329c0c07a7104ec321b698f967607，精确 artifact SHA 见 workspace review-r2-input-pins.json。

r2 五项输入前后逐 hash 一致；selected_spans 全部按 source byte_offset/bytes 重新读取且 SHA 一致；r1/locator 同一性逐字节核实；root index 仍 C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68。接受 r2 APPROVED_DIAGNOSTIC：限定目录恢复诊断已完成，15 项原工具结果未恢复。历史 H1 P2-1 OPEN，不改变 v2 verdict，不解除任何 Gate。

DSH r2 未复算 hash且 method manifest 读取有截断，已由 Codex 定向补核。DSH 未完全遵守 r2 的五文件读取列表（改读 manifest/r1），这是只读范围偏差，保留原日志且后续 Review 更严格冻结；不把越界读取用于授权判定。r1 中“须再次询问用户普通权限”、文件正文自引用 hash、新证据作为 X6 S0 等建议被拒绝；用户本轮自治授权及冻结 executor 协议优先。

诊断 Task 进入 approved，保留 root HEAD/index 的执行冻结，不提前声称集成/done。材料纳入后续受控集成窗口再记录 integration_commit。释放 H2 collector 源代码交付（ZCode Owner/DSH Reviewer），它只允许静态实现+纯 selftest；live collector、executor、Build、AC 不在本次释放。

Technical Gate NOT_SATISFIED；private_registry_absence UNPROVABLE；OwnerRiskAcceptance APPROVED；GateDisposition WAIVED_BY_OWNER；BuildAuthorization AUTHORIZED_WITH_EXCEPTION；residual technical condition unmet; user explicitly accepted residual risk；BuildGate BLOCKED；HardBuildBarrier EFFECTIVE；BuildCargo/AC/dynamic process closure NOT_RUN。
