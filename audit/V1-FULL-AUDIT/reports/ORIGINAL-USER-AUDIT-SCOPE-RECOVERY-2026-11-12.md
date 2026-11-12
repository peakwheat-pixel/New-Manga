# 原始 V1 全审指令恢复记录

**来源**：旧审计会话 01a16991-6e34-7191-b1c3-cfb72f78a5ff 中用户粘贴的请求附件 已粘贴的文本.txt。
**源文件长度 / SHA-256**：25572 bytes / 3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF。
**版本化副本**：audit\V1-FULL-AUDIT\source\ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt，长度与 SHA-256 已逐字节核对一致。
**恢复时 HEAD**：9bf7fa87499e710191b691437b2bd930675ee7d4（branch main，工作树 clean）。

此文件恢复了 AUDIT-00–14 的原始逐项要求及总体验收条件。它解决“原始指令无法从仓库 Git 历史找回”这一来源缺口；尚未据此更改专项状态或将任何检查项标为 PASS。架构、测试范围和执行边界仍需结合当前 AD-002、Task、后续 ZCode 裁决进行映射。

恢复命令、源/目标指纹和时点记录见 original-instructions-recovery-20261112.log。本记录不修改原始用户附件。

Git 当前 core.autocrlf=true；源文件通过一次性命令 git -c core.autocrlf=false add --renormalize 按指定路径写入 index，已验证 raw worktree blob 与 index blob 相同（
b775b8663c3827ed4a75d6b64ff2236b92151038
），未修改仓库 Git 配置。git diff --cached --check 对原始用户文本中的 15 行 Markdown 硬换行尾随空格发出提示；这些字节按原文保留。细节见 original-instructions-stage-preservation-20261112.log。
