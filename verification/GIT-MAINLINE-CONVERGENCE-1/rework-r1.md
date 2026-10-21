# R1 修订与补充证据

R1 reviewed_head=83a8a15c259c82267c0a1001123f3cf4ede8a246；decision approved 只限非破坏性切片，原报告保存在 deepseek-review-r1.md。Task 不 done；删除/GC/prune 禁令未解除。

|Finding|处置|
|---|---|
|R-001|修正 branches.md/branch-analysis.json 的 main tip 为分析时 56272e40b；注明 preflight、分析、R1 三个时点；其他 96 tip 未变。|
|R-002|补存以 83a8a15c 为 committed base 的治理日志，并注明当时 dirty 元数据；R1 实测为 PASS 3 warnings。最终新 head 另存日志，不能复用旧结果。checkpoint 是滚动文件，其未登记 warning 明示保留。|
|R-003|STATUS 删除旧 322/309/ready2 统计，改为台账实算 325/312/13 并引用生成器；不批量关闭旧 Task。|
|R-004|Resource Manifest 明确备份截至 56272e40b；214 common refs/135 HEAD 是记录时快照，不覆盖后续治理提交或未提交/ignored。没有删除窗口；任何将来删除前须重新备份。bundle 广告有 349 项=214 common refs+135 HEAD 伪引用，非新增 349 本地分支。|
|R-005|Plan 删除快照不包含的 Legacy Mapping 措辞，仍显式继承实际节点/依赖/限制；源快照字节不变。|
|R-006|Task README 的 P22 下一实施切片改为明确历史/done/integrated，当前 READY 无。|

Owner 额外检查：原工作区证据 CRLF、Git blob LF，raw-byte hash 并不相同。R1 的 blob 一致性声明不作为 raw-byte 验证通过的依据；保留原 Review，不改写它。当前 Task 自有证据统一写 LF，保留目录 .gitattributes；源归档目录新增仅作用自身的 LF 属性。全部 EV/SRC pins 在新的 evidence commit 后重新签发；核验必须用 subprocess stdout bytes，不能 text=True 或 PowerShell 文本管道归一化后 hash。

补充 other-refs-analysis.json：117 个非 heads refs 全部逐项记录 tip、相对 main 的 unique count 与保持原样处置；19 未合并分支 unique 求和 351/去重224；全部 refs 去重334，其中支线集合以外110。均为提交可达性，不是产品价值判断。0 stash；refs/codex 不删除。

77 对比旧76的唯一新增项是 WORKSPACE-DECLARATION-REMEDIATION-1 自己的 Canonical Evidence 表头路径列解析失败；其余76项未变。源为已固定 audit-after.json 与本 Task post-evidence preflight 的 code/file/message 集合差。此归因不授权豁免或删除。

当前建议仍先对77声明错误冻结专门处理范围，不放宽保护，不移动或改写原 evidence/pin，不请求立即删除那一个表面候选。完整 Task AC4/AC5 保持 BLOCKED，尚未达到只剩 main。
