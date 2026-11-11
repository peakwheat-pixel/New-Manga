# GOV-REFINCIDENT-1 证据索引

- `incident.txt` 是仓外事故记录的原字节副本，BLOB SHA-256 `72456c6d002a6799e483221c7c1b9df69723a64faa18c9868e355cae86f53970`，提交 `48c250fa6b8ae7cf2332944dae5be10c3c1d1c83`。按 R2 一次性关闭 autocrlf 入库；隔离预演及来源见 `incident-record.md`。
- `incident-record.md`：时间线、只读取证、仓外原始输出路径及 hash；`nul-pattern-analysis.md`：字节现象与本机 Git 文档的有限对照。
- `hypotheses.md`：假设及证据等级；`recurrence.md`：未实施的监测建议与应急前置。

## 限制与 NOT_RUN

- G: USN journal query/read：NOT_RUN，执行身份非管理员；未请求提权。事件和进程原始数据仅留仓外。
- Git/磁盘根因仍为 `root_cause_unknown_with_evidence`；单条 NTFS 健康事件与 `Get-Volume` 健康状态不等于完整硬件健康证明；Git fsck 不验证系统掉电原因。
- 默认 `git diff --check` 会将原始混合换行中的 CRLF 报为尾随空白（EXIT 2）；`git -c core.whitespace=cr-at-eol diff --cached --check` 对本次原字节暂存 EXIT 0。不得因此改写原件字节。
- 隔离 R2 的 V4 使用 `git checkout-index` 导出到新路径，未删除或覆盖预演文件；裁决建议的 `rm` 后 `checkout --` 精确流程为 NOT_RUN。V5 fresh clone 在本机保持相同工作区 SHA；跨环境 fresh-checkout 表现未知，不作无条件承诺。
- 后续独立 Review、终裁与收口门禁尚未完成；未 push、未清理资源、未实施监测工具。
