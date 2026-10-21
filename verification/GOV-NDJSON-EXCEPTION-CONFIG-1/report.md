# 当前例外配置迁移：实现与验证

实现7fd00e8b4a1ec53440aac64b4d44566761579cd6，实际worktree基线98993fe10（Task来源基线bbc9532b8，之间仅本Task冻结/认领治理元数据）。产品/guard行为只变默认配置入口，AST对比证明其它节点完全相同。新tools/governance/non-declaration-json-exceptions.json含69条，前67逐项等同历史表，新增两条path/raw SHA/reason来自已独审NDJSON身份。旧Canonical表/旧Task/pin、两日志未改，不覆盖历史记录；精确字节不同即丢失例外，内容判定仍依赖独立审查，不是通用坏JSON豁免。

用同一canonical main数据快照（含未跟踪R23）加载基线代码和候选worktree代码：默认32→30，仅移除两份指定日志的JSON_PARSE，其余30完整身份不变；保护1764→1764，旧集合子集成立。错路径、错hash、内存字节加换行各31错误且R23仍fatal；内存改成合法资源时旧hash失效并实际注册声明，其余30/保护不变。不是真的改源或重命名，候选覆盖仅workspace。实际候选默认CLI audit exit2/30，非清理PASS。详configuration-proof.json/candidate-default-audit.json。

29声明+80安全回归全部通过，0skip；两事故回放各15REJECT/0删除/0违规。临时测试fixture隔离本Task output/test-temp，自有夹具按测试清理；真实项目/用户资源未删除。原始输出workspace保留，版本化日志为LF转写。三调用入口clean_workspace/remove_worktrees/consolidate共用guard新默认，caller不修改。产品/构建NOT_RUN（治理配置），无安装/网络/旧collector/Legacy代码。

main在批准集成前仍用历史默认32；候选结果不是已集成main结果。新增Task branch/worktree原位保留，当前99heads/137worktrees；历史保护/STATUS-r212清理禁令/父Task blocked不变。独立Review通过后Codex合并并重新运行main默认审计和实际pin注册/治理检查，才可done。
