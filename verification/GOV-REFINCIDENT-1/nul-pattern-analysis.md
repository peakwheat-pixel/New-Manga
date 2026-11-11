# NUL 引用模式的有限分析

事故现场 loose `refs/heads/main` 为 41 字节二进制 NUL；预期的 SHA-1 格式分支引用应能解析为对象 ID，事故期间 `git rev-parse --verify HEAD` EXIT 128。reflog 最后一条提交指向的 commit 和 tree 可读取，索引相对该提交、工作树相对索引的对照 EXIT 0；这些只覆盖所检查对象和状态，不能证明故障当时所有对象都健康。

本机 Git 2.52.0 的 `C:/Program Files/Git/mingw64/share/doc/git-doc/git-update-ref.html` SHA-256 `4739e78bcb566d4b86ef00df89fe501bfdd39bfd72cee29b1e06f00af488fa27`；文档说明事务准备阶段为引用创建锁，单个引用更新具有原子性，且可在更新前校验旧对象 ID。原始相关摘录保留于仓外 `investigation/git-doc-excerpt.txt`（SHA-256 `f949262b6ef59610765c8c782bc5243c5b263a260428cd6332ab1e3cc61be8b2`）。文档描述命令契约，不能证明事故中具体进程、文件系统或电源状态。

隔离演练直接 `git update-ref` 遇损坏 ref EXIT 128；移开隔离副本的 loose ref 后暴露 packed 旧值，CAS 对错误期望值拒绝，对匹配旧值成功。原仓库恢复须明确授权和排他窗口；演练不证明异常发生机制。原仓库两个非 sample hook 均仅 shell shebang，无脚本正文；这只覆盖这两份 hook 的静态字节，不排除其他进程。

G: USN 查询因非管理员 NOT_RUN；无写入者归属数据。Kernel-Power 41 的重启记录与 ref 时间接近是时间相关性，不证明哪一进程或存储层写入 NUL。
