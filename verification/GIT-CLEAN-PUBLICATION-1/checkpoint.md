# 当前恢复点

2026-10-24 / Codex。父 GIT-CLEAN-PUBLICATION-1 保持 in_review；DSH r1 decision=blocked，文件不可改写。源main固定349e61faff5f93067af5d4ce2d9e394e0d665b8c、index空；父候选e34a90d001cce1fa966aec7d2b032bb5ad1cf148不变，不push、不done。

唯一执行为 GIT-CLEAN-PUBLICATION-DIAG-1；恢复先读其Task、RESULT、APPOINTMENT。默认并发复现151 passed/2 failed/1 ignored/12 filtered；四条registry测试各自单进程通过，产品并发压力边界仍未排除。r2/r3串行均152/1 failed/1 ignored/12 filtered、exit101，r4补P22夹具后153/0/1/12、exit0；不冒充一次通过。

r2三个DB已按原路径/hash/plugin_error冻结为SOURCE_PIN；WAL均0字节，immutable只读副本，原DB hash不变。旧icacls returncode/stderr未知；隔离diag head fed1a9c保留异常字段，2个mock通过，不改系统ACL或源main。新head已重新Appointment到DSH，尚未执行。

补充冻结包为workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package-r2，62项文件SHA/338禁止ID/19个事后EXIT envelope；旧包/旧日志/旧review均保留，缺失环境标UNRECORDED。所有包和临时DB仅本地复审，不随源码交付。packaged必须在新构建sidecar冻结后运行，实际进度/结果以diag RESULT为准。不得重跑快照生成器覆盖旧候选，不清理已有资源。

最新状态：DIAG DSH r1已approved（仅fed诊断），其旧“待执行”记录为历史；父仍in_review/r1 blocked。Rust隔离/真实压力Task ready，Core V2–V5 Task proposed。父升级前必补R-01至R-03并携DIAG-50..52及旧包manifest交叉链重新Appointment；无新父head，不push、不done、不改main/系统ACL。
