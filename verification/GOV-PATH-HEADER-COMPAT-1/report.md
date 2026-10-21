# 固定表头兼容验证

仅在 `_exact_column` 与 `_duplicate_identity_columns` 中同步把完整固定模板标签 `path（仓库相对路径或绝对路径）` 归为 `path`。没有新增依赖、模糊别名、source_path/destination_path别名或路径/JSON/disposition豁免。Code/test diff不修改历史Task、原始证据或例外清单。

- 新增5测试/0skip，既有29声明测试/0skip，80安全测试/0skip，全通过。
- baseline discriminator：把同一新测试加载到未修改main解析器，预期失败exit1，原始失败日志入库；并非未解释的测试失败。
- 同一main输入快照（main tracked/untracked status原始字节指纹前后完全相同）：77→32 errors；旧保护根1280全部保留，修复后1690，新增410。与初始内存模拟的1277/1687差3来自已登记本Task的3个资源根，不是减少保护。
- 剩余32按原类别原错误保留；没有误称全部声明合法。没有调用apply。
- 两套incident replay各15/15 REJECT，deleted0/violations0，exit0。首轮clean回放漏传ledger参数，CLI exit2；原日志replay-clean.log保留，核对帮助后正确传参，仅重跑一次成功；不是无限重试或隐藏失败。
- 测试只在本Task隔离temp中创建/回收测试自有夹具；真实项目资源删除/移动/merge/GC/prune/push均0。

父收敛Task仍blocked；修复会识别更多保护，不能据此删除任何资源。当前多1个Task分支/工作树（98/136），按父禁令保留；数量目标尚未达成。
