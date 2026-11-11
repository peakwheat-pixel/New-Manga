# 复发建议与应急前置

以下均为建议，**未实施，需另行释放范围**：在合适位置检测当前 ref 格式及目标对象可读性；定期只读 `git fsck --connectivity-only`；保留受访问控制的 refs/reflog 快照，并记录来源与 hash。不能自动删除 dangling 对象、重写 refs 或替代独立 Review。

若再次发生相似故障，先停止写入，记录仓库路径、损坏引用字节/哈希、HEAD 与 reflog、index、packed-refs 和对象检查结果，并将副本放仓外受控位置；排查并发 Git/其他写入后再由授权人裁决修复。原事故 `incident.txt` 行 16–23 记录只读 fsck、隔离演练、packed 旧值暴露和 CAS 判别；行 25–30 记录授权后的实际恢复与验证。引用、packed-refs 或目标对象发生漂移时不得复用旧值或照搬旧命令。

原事故的 NUL 原件为仓外事故目录 `main.original-corrupt`，reflog 副本为 `main.reflog` 与 `HEAD.reflog`。恢复前须重新核对 hash、当前引用/packed 值、目标 commit、index/worktree、锁与并发进程；移动 loose ref 会暴露 packed 旧值，CAS 不能防止读取者观察中间态。原事故批准不自动授权未来故障的引用改写。
