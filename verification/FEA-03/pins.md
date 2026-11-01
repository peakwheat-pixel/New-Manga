# FEA-03 Frozen Pin 证据

工作树直接运行：
pwsh -NoProfile -File tools/governance/verify_pins.ps1

结果：FAIL (15)。脚本报告 C01b、C02、C03、C04b、C05、C06、C07、C08、C09、C10、C11、C12、C13、C14、FEA01 均 mismatch。例：C13 pin=8faf1e805eac，working-tree actual=71621515bd75。

诊断：
- Git config --show-origin --get core.autocrlf => file:C:/Program Files/Git/etc/gitconfig true
- doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md 工作树含 222 个 CRLF、0 个裸 LF；git show HEAD:<path> 的 blob SHA-256 为 8faf1e805eac500ab20037d8628b8594f8720e455387a85639897f1127afd45c。
- 冻结文件未被本任务修改；没有重写或归一化 frozen docs。

规范 HEAD 字节 fixture：
从 HEAD Git blob 读取 verify_pins.ps1 所列 15 个 contract source 和 frozen record，在系统临时目录建立相同相对路径，再运行同一脚本。
结果：PIN AUDIT: PASS (all 15)。
C-13：OK C13 8faf1e805eac，即 v6 pin。
这个 fixture 证明当前 HEAD 的冻结 blob 与记录 pin 相符；它不改变工作树直接命令受 autocrlf 影响的事实。