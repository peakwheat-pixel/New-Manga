# 引用事故记录（脱敏摘要）

## 时间线与证据等级

时间均为 2026-11-11 Asia/Shanghai。主仓库 `G:/CODEX/New Manga`；本任务 base `fa5e58e3fdbd2b53453e55104a7b002d4e57d518`。原始记录为本目录 `incident.txt`；该文件是由执行者当时整理的日志，不是独立证人。

| 时点/步骤 | 观察 | 证据等级 |
|---|---|---|
| 18:21:39 | reflog 记录 `685d3a9… → fa5e58e3…` closeout commit；损坏 loose ref 文件 mtime 同秒 | 事故记录行 4–9；对象和索引对照当时执行，确切损坏时刻未知 |
| 18:22:05 | System 中 Kernel-Power 41 记录此前未正常关机后的重新启动；同秒 G: NTFS 98 报卷运行状况良好 | 本任务只读查询 EXIT 0；事件内容不证明根因或完整磁盘健康 |
| 事故发现与隔离 | 41 NUL；`rev-parse HEAD` EXIT 128；原提交/树可读；原索引与该提交、工作树与索引对照 EXIT 0 | 事故记录行 4–10、16–23；报告的是当时日志与后续只读复核，非持续监测 |
| 恢复 | 用户明确授权后，移出损坏 loose ref，用预期旧值 `7588ddc7…` CAS 更新至 `fa5e58e3…`；update-ref EXIT 0 | 事故记录行 25–28；reflog 追加可见，全部命令原始过程并非本任务独立重演 |
| 恢复后 | default/TaskPath/pins/API 均 EXIT 0；`fsck --full --no-reflogs` EXIT 0，工作树 clean | 事故记录行 28–30；fsck 输出及 reflog 已复核；不推断事故原因 |

## 只读核查及来源

仓外 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/git-ref-incident-20261111-1824/` 为 EXTERNAL 证据根；原件不改动。调查输出在其 `investigation/` 下：

| 文件 | 原始文件 SHA-256 | 内容/结果 |
|---|---|---|
| `pre-hashes.json` | `48d1b30c5ace92182a4b5cade07db71653643681f23e2ea7a1aae624304bee62` | 调查开始时 44 个既有文件，错误 0 |
| `post-final-hashes.json` | `604ec7d1dfcf5e8e9ea88dd0a9344ab21cd5c1ce44ac72766bf0da1e4680de1b` | 调查末次复算 44 个，差异 0、错误 0；两次均排除新建 `investigation/` |
| `known-hash-comparison.json` | `7279266aa52d1b632f0cd7ee5f41f36ed773da839888916cda5661c2f0005568` | 8 项重点副本与先前记录比较 OK，EXIT 0 |
| `system-events.json` | `f6b8c55f830ce877f66b16b56cc1fd72178b693139f79833a8d8dd7f9732a422` | 17:30–19:40 的限定系统提供程序查询，11 项，EXIT 0；原文仅仓外 |
| `environment-raw.txt` | `b91b4f2e84cf40a4953823245e6261cbc74e01fe83d9364904c175621576bfe3` | Git 版本、count-objects、hook/相关进程名；USN NOT_RUN |
| `git-config-filtered-v2.txt` | `b7a4c82a1ec407ee49592c00216dfad1d767dfc9c119dbae84e9b01c7de11775` | 限定核心配置键及来源，EXIT 0；首版过滤未选中记录，v2 修正 |
| `environment-supplement.txt` | `0d2b7cfdb481eb7a204200973cb4de10fd3b3f1560d8f621b17462b5726c8091` | G: Get-Volume NTFS/Healthy/OK，EXIT 0；两个 hook 均仅 shebang；其中首版 config 空筛选以 v2 为准 |
| `git-layout.txt` | `fd9253b4b753f2f9f0edbdf34b9f625dc238e34f3727bc36dfb6778e83db5758` | `.git` 顶层文件/目录名只读枚举，EXIT 0 |
| `observations.txt` | `9beabcf8ef024ea197ede5524fbf7ffe35921e2e99f5e6377bd67210d41eb53e` | 脱敏事件、hook 与 dangling 摘要 |
| `rehearsal-crlf/run.log` | `ee582351c0bfc4b7293aca17ff77b38f14f6e9fba0c6d7385c494ff95338b4be` | R2 V1–V3 通过；V4 为 checkout-index 新路径模拟，V5 为 fresh clone |
| `whitespace-check.txt` | `1ec84581f803c9a4da03de6dabe8f23aeeee09bce40758186160db718dcf1ee2` | 默认 diff check 因原始 CRLF EXIT 2；临时 cr-at-eol 检查 EXIT 0 |

恢复后 `fsck-post-stdout.txt` 的 SHA-256 为 `b111f60983b3b0154e3b81dc98bfe46445c00f4e3e0d62ebe716e9441051b0da`；479 行 dangling 按类型为 commit 347、tree 78、blob 51、tag 3，未移动或删除。`fsck-post-stderr.txt` 为空，`fsck-post-exit.txt` 记 EXIT 0；fsck 使用 `--no-reflogs`，不覆盖被排除的证据来源。

USN journal query/read：执行身份非管理员，按冻结范围 NOT_RUN，不提权。事件记录和进程快照不覆盖所有潜在进程或卷历史。`Get-Volume` 的 Healthy/OK 为当时状态，不等价于完整物理介质诊断。

## 原字节保全

仓外 `incident.txt` 原字节 SHA-256 `72456c6d002a6799e483221c7c1b9df69723a64faa18c9868e355cae86f53970`；工作区副本与提交 `48c250fa6b8ae7cf2332944dae5be10c3c1d1c83` 中 BLOB 同 SHA，5702 bytes。隔离 V2 状态 0 行，V3 默认 autocrlf 重 add 后索引 OID `37c06bd80723703926cf3122b33f9800b403b1e4` 不变；checkout-index 与本机 fresh clone 工作区 SHA 均与原件相同。精确 `rm`+`checkout --` 流程未运行，跨环境行为仍未知。
