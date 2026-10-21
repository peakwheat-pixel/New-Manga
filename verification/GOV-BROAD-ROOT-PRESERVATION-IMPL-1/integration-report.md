# 主线集成与资源核销

DeepSeek R4 approved d5d21ff9f4cfbd667f0a6bcc5e1fefe104efff05（base f47c68969dac7d3cec0dddbe3fca4ea2fa7803db；source6e3bac7867c67a2e76e45e2facbbf859d5dba526），P0/P1=0。R3仅证据CRLF被拒，已转LF并重签，通过R4；未绕过检查器。正常merge a3bba87ce0eef4049be6e07dc2e46403af8597ca，无冲突。main代码blob等于审查source，正式24→12；旧保护保全，新增5广域根/12角色/12警告，剩余7历史运行身份、2模板、3NUL继续fail-closed。两旧源raw指纹、69例外和消费者代码未改。

Owner最终127=18+29+80，0skip；双事故回放各15REJECT/0deleted/0violations。Reviewer实际执行同数据新旧scan、EV注册/指纹、REAL_DRIFT及无副作用内存负例、check/diff；完整18fixture复跑NOT_RUN，127为Owner日志经Reviewer核验。主线audit/clean/remove拒绝探针均exit2/12errors/空候选；remove使用明确空合成inventory，仅验证拒绝，不冒称全盘清单。主线全部100/138 consolidate未重跑；产品构建NOT_RUN。

当前实现Task创建前99heads/137WT，创建后及本轮集成前后均100/138；父治理初始97/135，新增治理资源均保留，尚未达到只剩main。实现分支codex/gov-broad-root-preservation-impl-1固定d5d21ff9，已集成但按禁令保留。其余支线本切片无集成/删除/改名，独有工作和原证据仍原位，旧治理bundle不覆盖本轮新提交/未提交文件，不冒称已备份全部当前状态。所有现有refs/WT保留，尚未核销的19独有tip按父盘点保留，不据HEAD可达推断可删。

资源closeout：本Task WT、agent-output（含原始CRLF日志/失败尝试/DSH JSONL与会话恢复材料）PRESERVE_REFERENCED；六处R1空探针逐项原位PRESERVE_REFERENCED，Codex本轮实际枚举为空且真实scanner全保护，Reviewer内容枚举因ACL NOT_RUN。无既有用户/项目资产删除；R1自建探针部分自清与越界事实保留于历史中断记录，不宣称该轮完全无写入。未修改ACL或移除任何探针。Git tracked证据可从Canonical EV commit恢复；未提交/untracked/ignored原地保留，未用bundle替代内容备份。主线当前实测详见integration-validation.json。

证据计数随本Task新增而变：runtime-proof-r3为22EV登记时快照；DSH R3实测31，R4实测32；integration-validation为32EV追加集成证据前快照。每份均为其时点，不是永久实时计数；done前将复核最终EV实际注册。r212/STATUS禁令和父blocked不变，不执行apply/迁移/归档/GC/prune/push/force/reset/stash或Legacy。

下一步建议：Codex另冻剩余模板/NUL五项只读身份研究，DeepSeek独审；7历史运行身份继续BLOCKED，具体转发指令见本Task Handoff。建议不构成释放；不修改旧Review/NUL/source pin或授权清理。
