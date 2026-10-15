# P02 已审成果 main 集成核验（2026-10-15）

## 结果

本地 main 已使用原生 git merge --ff-only --no-autostash 从 a9c3214b2d7806c2b8920897e5684c039ae14057 快进到固定已审交付 9e3c5310d5652f5491f3dc11825d86c03dac22ee，merge exit=0。main tree 与该交付完全一致，全部 source/Review/E adjudication/关闭记录已进入主线。关闭文档候选基于该 exact head，后续只追加本 Task 证据与当前治理字段。
DSH 内容 Review @ 4abb8d28 与 E Review @ 738759cd 保持 APPROVED；本轮无产品源码/测试行为/依赖/Schema/构建脚本修改，不重开审查或 I3。独立 Review 被沿用，不由 Integrator 自审自己的实现。

## 用户改动保护

执行前保存 index 和保护文件；两组隔离 Git fixture 证明 index-only 对齐 approved blob 可使原生 FF 保留 dirty tracked 与同名 untracked 字节。实际 17 个冲突路径只在 index 写入目标交付对象，不读用户文件生成提交内容；FF 后 index 无暂存内容，38 份受保护文件逐字节相同，非相关 untracked 均仍存在。根目录用户其它修改不纳入候选提交。备份/原始命令与恢复脚本位于 workspace/agent-output/codex/P02-MAINLINE-INTEGRATION/ff-reviewed-p02-r1/，不会删除。
初次 apply 的前态比较因 Windows 默认代码页误读 UTF-8 中文文件名而 fail-closed，Git/index 未变；将 JSON 显式按 UTF-8 读取后，原 dry-run 与真实前态一致，实际 FF PASS。没有跳过前态比对或覆盖用户内容。

## main 上的 pin 复验

官方 generate-evidence-manifest.py --repo main --verify：source manifest 102/102 PASS。Gate capsule 初次 19 项有 7 个新写出文本被 Git autocrlf 转为 CRLF，出现字节 hash FAIL；先逐文件证明 git_blob 完全相同且差异仅 CRLF/LF、原 main 不存在这些文件且不在用户保护集，备份 Git 写出前态后恢复为已审 canonical bytes。capsule manifest 本身也仅恢复已审换行字节（另 1 文件）；manifest 字段、raw runtime data、用户文件均未改；重新官方 VERIFY 为 19/19 PASS。首次失败与精确 EOL 记录保留，不写成一直 PASS。
不修改 .gitattributes/core.autocrlf 或冻结清单。主线正确 tree 的 identity 由固定 commit/blob 验证；当前 checkout 的 canonical 字节身份由 SHA/bytes 验证，两者均成立。

## 收口与边界

P02 新时点 AC1–AC7 / AC6 resolution 保持 DONE 并将当前集成目标与 canonical pins 转到 main。P02 历史总入口按 closed_with_limitations 关闭：只接受用户授权的新时点路径，不关闭旧 H1/P2-1 finding，不补齐其 13 项历史缺失，不把 BC-AC5 PARTIAL 或产品 P3/P4 改成 PASS。原始 Task、Review、manifest、证据保持其时点语义。
main 中旧 completion-adjudication 的“未合 main”为 9e3c5310 之前的 immutable 历史事实，当前是否合 main 以本报告、主线 Task 与 STATUS 为准。
保留所有 worktree/task-env/model/build/cache/output；删除/迁移/归档=0。本轮未 push，也未修理旧坏 ref 或运行 gc/prune。

## 实际检查

- 两组隔离 FF fixture assertions：PASS；orchestrator helper SELFTEST 127/127 PASS。
- main ancestry gate 与 native FF：exit 0；保护文件 38/38 PASS；index empty。
- 主线 source pins：102/102 PASS；主线 Gate pins：19/19 PASS（canonical EOL 恢复后）。
- runtime/epoch 3 lease：LEASE_VALID；integrator live PREFLIGHT=PASS。
- 治理与最终收口后 FF 的结果见 Task 的 Closeout Record 与 rolling checkpoint，不由本 immutable 内容报告预报未来命令。

## 下一步

本轮仅做已审成果主线化；无其它已释放 READY。P3/P4 与 Git 维护不自动扩成产品任务；无需下一步操作。
