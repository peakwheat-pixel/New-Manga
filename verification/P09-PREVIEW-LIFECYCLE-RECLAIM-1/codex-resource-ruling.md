# Codex Resource Ruling — P09-PREVIEW-LIFECYCLE-RECLAIM-1

- reviewed_head: 6cb1646a1848cb0b6a684318e5392baab4d2d06d
- decision: RULING_ISSUED_WITH_LIMITATIONS; non-destructive item dispositions only.
- ruled_at: 2026-10-19 11:33 UTC (19:33 Asia/Shanghai)
- adjudicator: Codex (Lead / Architect / Integrator)
- source manifest: resource-manifest.json; SHA-256 F4853B002DD894687EEEA44E694CCAB9A0236D6373DDBE9C139BD74C9C633EB6

## 1. 逐项资源处置

本裁定不执行任何仓外资源删除、移动或迁移。以下逐项 hash/文件数来自 source manifest。目录快照 hash 不代替逐文件语义检查；未核明的项目明确保留为 PRESERVE_UNKNOWN。

### §4.2 七类

| 类别 | disposition | 源 | 目标 | hash/manifest | 引用检查与结果 |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE | 主工作区 G:CODEXNew Manga；git worktree list 实测共 208 项 | 无 | 无本 Task 专属 worktree；Task 记录及 worktree list | 全程复用主工作区；工作区有既存 dirty/untracked 内容，不可清理；无删除授权。 |
| task-env | NOT_APPLICABLE | G:CODEXNew Manga.workspace	ask-envsP09-PREVIEW-LIFECYCLE-RECLAIM-1 | 无 | Test-Path=False；resource-manifest.json | 路径不存在，无待核销引用。 |
| dataset/model/test-material | NOT_APPLICABLE（外部数据/模型） | Task 未引入外部 dataset/model；探针用自造小图 fixture | 无 | Task 测试说明与交付清单 | 无外部输入；生成的 fixture 归入 temp/agent-output 项并保留。 |
| artifact | NOT_APPLICABLE（独立 build/package artifact） | 未发现独立构建/打包产物路径 | 无 | Task 交付清单、resource-manifest.json | 运行输出逐条列为 agent-output；无另一独立 artifact 清册。 |
| temp | PRESERVE_REFERENCED | coordinatorac2-referenced、ac4-assert、ac4-batch、ac4-retry | 分别保持原位 | 下方 AO-10/11/12/15 的 manifest SHA-256 | 探针源码引用精确固定路径；r8-injection-evidence 记录运行前会 rmtree 重建。未查当前进程；不运行探针、不清理。 |
| agent-output | 逐项见 AO-01…AO-29、AO-ROOT | G:CODEXNew Manga.workspaceagent-outputcoordinator | 每项保持原位 | 每行关联 resource-manifest.json ID 与 content SHA-256 | 引用、清册关联或缺失证据逐项列出；未知项不推定可删。聚合根 PRESERVE_USER_DATA。 |
| exchange | NOT_APPLICABLE（本 Task） | workspaceexchange 根存在；无本 Task exchange 子目录或 *-exchange 任务项 | 无 | 路径检查及 resource-manifest.json | 无本 Task 引用；共享根不作清理。 |

### Manifest 全部 37 项

| ID | 实测源路径 | 目标 | disposition | files / bytes | content SHA-256 | 引用检查及结果 |
|---|---|---|---:|---|---|
| AO-01 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-AC3-R6-b9901af250064a409a7ae441a9dd27e9 | 同源原位（不迁移） | PRESERVE_REFERENCED | 0 / 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-02 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R3-scratch | 同源原位（不迁移） | PRESERVE_REFERENCED | 667 / 8044955 | cdd477abefe8e98dea16b7f3e7c44191015929a2774997faf89e204fda43cc8d | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-03 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-PREVIEW-LIFECYCLE-RECLAIM-1-r7-22b0860 | 同源原位（不迁移） | PRESERVE_REFERENCED | 20 / 1407191 | bbc2da90703c46c456e825f358c70676d90bf1fddcf0aa6dba2f8c75d41ff656 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-04 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-R8-empty-survivors | 同源原位（不迁移） | PRESERVE_REFERENCED | 12 / 1055169 | fa2c7309ea3347c1a2b5c596a1093eb98516b1e53234408dc56dcf59215d23b6 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-05 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-R8-injection | 同源原位（不迁移） | PRESERVE_REFERENCED | 31 / 1761828 | cc6ac43a43196943f690a5ef9ad9d7a63ba0fad5c9bc3679f23bba9233f0d762 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-06 | G:\CODEX\New Manga.workspace\agent-output\coordinator\P09-R8-probes | 同源原位（不迁移） | PRESERVE_REFERENCED | 20 / 1408041 | 407edc719e29837c9ada574970b22c8357509f35ad8449e9a216ab86cf7b9fc8 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-07 | G:\CODEX\New Manga.workspace\agent-output\coordinator\R14-probe-copies | 同源原位（不迁移） | PRESERVE_REFERENCED | 20 / 1411402 | 6fa7e359a559b8214a522220cbaed6ac336fbcdb73ee1a7a2de5e41363e722cf | 清册标注 R10/R14 本 Task 复审轮次，故保留；未逐文件核用途/可重建性。AO-08 另有 skipped entry，必须保留并核查。 |
| AO-08 | G:\CODEX\New Manga.workspace\agent-output\coordinator\R14-pytest-tmp | 同源原位（不迁移） | PRESERVE_REFERENCED | 1899 / 178580696 | 455338b794a4a329189bf92386c0c08dc089a3dc9fa70c55e2bdf303b13a8756 | 清册标注 R10/R14 本 Task 复审轮次，故保留；未逐文件核用途/可重建性。AO-08 另有 skipped entry，必须保留并核查。 |
| AO-09 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac2-keys | 同源原位（不迁移） | PRESERVE_REFERENCED | 7 / 344416 | 0cea59474f626daa8b8e66cbaba86df7032144ccee9113d25b5cceddb2d0b3a2 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-10 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac2-referenced | 同源原位（不迁移） | PRESERVE_REFERENCED | 3 / 344412 | 8f511127cea789311b376fb3d3c47dfbb9b6a5d260d0365a589e4f1f624da4bb | 对应 ac2/ac4 探针源码固定路径已核；探针会 rmtree 重建。未核运行进程；保留原位。 |
| AO-11 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-assert | 同源原位（不迁移） | PRESERVE_REFERENCED | 3 / 344403 | a449c48a315cc1f4fdeb9e8fdedb8963ae9fc3fec8a203f5c5bbe955a6653ea0 | 对应 ac2/ac4 探针源码固定路径已核；探针会 rmtree 重建。未核运行进程；保留原位。 |
| AO-12 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-batch | 同源原位（不迁移） | PRESERVE_REFERENCED | 7 / 344462 | 8550b123efdc17e83d5d1275bbfb22c29937ca266a7aa6199667d31922a23873 | 对应 ac2/ac4 探针源码固定路径已核；探针会 rmtree 重建。未核运行进程；保留原位。 |
| AO-13 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-count | 同源原位（不迁移） | PRESERVE_REFERENCED | 8 / 344480 | 2e643c1b0d860a2ccc492be6b02c813693d4afd8f3f8c1e5111d5984c21a83aa | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-14 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-diag | 同源原位（不迁移） | PRESERVE_REFERENCED | 8 / 344476 | ee4eb54c55e18d1737755551d5ec456093889470945137850be6bd9d45ffcf0a | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-15 | G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-retry | 同源原位（不迁移） | PRESERVE_REFERENCED | 3 / 344402 | ce9c498160ef97f2a2f64f085922008a2d18b9e674f654568cd3418e8a3269e2 | 对应 ac2/ac4 探针源码固定路径已核；探针会 rmtree 重建。未核运行进程；保留原位。 |
| AO-16 | G:\CODEX\New Manga.workspace\agent-output\coordinator\n002-race-oldhook | 同源原位（不迁移） | PRESERVE_REFERENCED | 1 / 28 | 3a561cd7bf31b3a6aa5a13bead6ab36e9f03024f340192422905945f8eff89a9 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-17 | G:\CODEX\New Manga.workspace\agent-output\coordinator\n002-race2 | 同源原位（不迁移） | PRESERVE_REFERENCED | 2 / 56 | ef68c15041209c18ef1cbb8621d3e4689254dff17b9acd9172c1df04c999fff3 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-18 | G:\CODEX\New Manga.workspace\agent-output\coordinator\n004-prod | 同源原位（不迁移） | PRESERVE_REFERENCED | 2 / 44 | 64c6ed257599256fa8dc3586c7be13aebe37482ddd15746cd17436ac3c3f477f | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-19 | G:\CODEX\New Manga.workspace\agent-output\coordinator\n004-tmp | 同源原位（不迁移） | PRESERVE_REFERENCED | 8 / 176 | 75bfb2a987cc3313d5fac9766d77c9ac84ed118baaae8a0131c47c8a1633a1d9 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-20 | G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-cleanup | 同源原位（不迁移） | PRESERVE_UNKNOWN | 4 / 319556 | 6153e717df79591888b56056882456f3d5c8d98be4372598aec8c538779eaefb | p1-* 项未列入旧 Task 清册；同批 mtime 不能证明归属/引用/可重建性。缺逐文件用途与所有者核查；原位保留。 |
| AO-21 | G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-orphan | 同源原位（不迁移） | PRESERVE_UNKNOWN | 2 / 44 | 7e391b9c019898fb8e78a1095c378c459c1c4a3223617355f5eaff02ea5b5089 | p1-* 项未列入旧 Task 清册；同批 mtime 不能证明归属/引用/可重建性。缺逐文件用途与所有者核查；原位保留。 |
| AO-22 | G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-publish | 同源原位（不迁移） | PRESERVE_UNKNOWN | 2 / 44 | 056d5e940dd1adbcd3879586bef3db34774a44e1ac256fff40b49434fe8e4e90 | p1-* 项未列入旧 Task 清册；同批 mtime 不能证明归属/引用/可重建性。缺逐文件用途与所有者核查；原位保留。 |
| AO-23 | G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-race | 同源原位（不迁移） | PRESERVE_UNKNOWN | 2 / 44 | 4152efa929ac7e3340ca7153f7ec6f39c261fb28c455a385ee60dfdb514a5138 | p1-* 项未列入旧 Task 清册；同批 mtime 不能证明归属/引用/可重建性。缺逐文件用途与所有者核查；原位保留。 |
| AO-24 | G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-repro | 同源原位（不迁移） | PRESERVE_UNKNOWN | 2 / 44 | 64c6ed257599256fa8dc3586c7be13aebe37482ddd15746cd17436ac3c3f477f | p1-* 项未列入旧 Task 清册；同批 mtime 不能证明归属/引用/可重建性。缺逐文件用途与所有者核查；原位保留。 |
| AO-25 | G:\CODEX\New Manga.workspace\agent-output\coordinator\r10-injection-runs | 同源原位（不迁移） | PRESERVE_REFERENCED | 5 / 44580 | 8fc3ef110cee74b7269b25cceaba943e5c6b55a77484dc87a71c15ec2ee3cbf0 | 清册标注 R10/R14 本 Task 复审轮次，故保留；未逐文件核用途/可重建性。AO-08 另有 skipped entry，必须保留并核查。 |
| AO-26 | G:\CODEX\New Manga.workspace\agent-output\coordinator\r10-isolated-injections | 同源原位（不迁移） | PRESERVE_REFERENCED | 48 / 3526785 | d864a8db2ab65603620558f46bd8379c7c246771fdbc9aa9df2ae219a2f9e971 | 清册标注 R10/R14 本 Task 复审轮次，故保留；未逐文件核用途/可重建性。AO-08 另有 skipped entry，必须保留并核查。 |
| AO-27 | G:\CODEX\New Manga.workspace\agent-output\coordinator\r10-probe-runs | 同源原位（不迁移） | PRESERVE_REFERENCED | 20 / 1411379 | e30db2f73881ce4625905e0d535d35675deb3cbc2ae8875f1042eaa19c9ba941 | 清册标注 R10/R14 本 Task 复审轮次，故保留；未逐文件核用途/可重建性。AO-08 另有 skipped entry，必须保留并核查。 |
| AO-28 | G:\CODEX\New Manga.workspace\agent-output\coordinator\r4-n002-outside | 同源原位（不迁移） | PRESERVE_REFERENCED | 1 / 28 | e541ef7fa7a7c632b7f39293ed4c3e65bf633007dceed97d99d699a8d3f5f608 | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-29 | G:\CODEX\New Manga.workspace\agent-output\coordinator\r4-n002-root | 同源原位（不迁移） | PRESERVE_REFERENCED | 1 / 28 | 2fe4dba5e745e1041de1fcfb8756f61bfe0786f87b6e17444bc0f7d1c121121e | Task resource manifest 对应条目/round 命名提供关联；content SHA-256 与文件数按本行记录。处置为原位保留，不执行写操作。 |
| AO-ROOT | G:\CODEX\New Manga.workspace\agent-output\coordinator | 同源原位（不迁移） | PRESERVE_USER_DATA | 588 / 29245514 | 1da6ca7891ffaa3b5033589fc49b1fbaacd302224d919c76423472d938b9e272 | 588 顶层文件的多 Task 共享聚合根；混有 ac1-*/M2-C1/P20-*/harden2-*。禁止单 Task 整体处置；保持原位。 |
| RX-01 | G:\CODEX\New Manga.workspace\review-scratch\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8 | 同源原位（不迁移） | PRESERVE_UNKNOWN | 20 / 1594956 | e93ab2efd2c3309152c2f48ce0ecbc577e4a985074143ae67bb0b5c3f987d106 | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| RX-02 | G:\CODEX\New Manga.workspace\review-scratch\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export | 同源原位（不迁移） | PRESERVE_UNKNOWN | 11185 / 351312383 | 158f6ba1257516d760189f174d0ffb7ed88fe808588e36091c613f4b1b01ad41 | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| RX-03 | G:\CODEX\New Manga.workspace\review-scratch\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17 | 同源原位（不迁移） | PRESERVE_UNKNOWN | 20 / 1411503 | 87bedea4d5ee2022ac06133cd8c182358f5358879bbf70dc533171b0bacf2f3b | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| RX-04 | G:\CODEX\New Manga.workspace\review-scratch\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18 | 同源原位（不迁移） | PRESERVE_UNKNOWN | 39914 / 14344791860 | 30b695d531d2be953404bd7e3f68d5bb232ffc15b6b560f9a843f80f932bd9ce | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| WS-05 | G:\CODEX\New Manga.workspace\P09-PREVIEW-LIFECYCLE-RECLAIM-1-R20-scratch | 同源原位（不迁移） | PRESERVE_UNKNOWN | 2489 / 42899106 | 6213804e3dabec94a476058429cab6c5c14a59969ad492113ed793c6d05c0aef | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| WS-06 | G:\CODEX\New Manga.workspace\P09-BASELINE-T2 | 同源原位（不迁移） | PRESERVE_UNKNOWN | 11030 / 352537586 | 0348fc9d29584ac9cdd0df643d46e5abc4285d78f91fe43b8e66254fedc62639 | 当前引用、逐文件用途、独有修改/可重建性未完整核实；原位保留。WS-06 与本 Task 关系未建立。 |
| IN-01 | G:\CODEX\New Manga\verification\P09-PREVIEW-LIFECYCLE-RECLAIM-1 | 同源原位（不迁移） | PRESERVE_REFERENCED | 14 / 74130 | 89329c6054b8aa75d3f2a7ea27e92395ebc663fe4767f7324a1ed450a5999557 | canonical evidence_dir。ac6-ruling.md 与 codex-review-r23.md tracked；resource-manifest.json 在裁定前 untracked；其余文件不声称全部 tracked。保持原位。 |
## 2. allowed_paths 裁定

本 Task 的 verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ 证据不构成越界。Task 模板定义 evidence_dir；协作协议 §4.1 要求判别力结果进入版本化 verification/<TASK-ID>/，§5 要求证据提交至对应 verification 路径并由 Handoff 引用。这是该证据目录的交付依据。Task 的 allowed_paths 未列该目录，属于释放时清单不完整，不追溯判为无授权。

后续 Task 应显式将自己的 evidence_dir 加入 allowed_paths。由 Codex 在 READY/释放范围冻结窗口落到 Task；模板或协议的默认规则由 Codex 在下一治理文档维护窗口提出，由当前 Coordinator lease 持有人落盘。本裁定不修改治理文件或 Task。

## 3. 适用窗口

当前不是 §4.2 的 approved integration window。该窗口定义为：固定 delivery head 已独立 Review 通过、依赖与范围核清，Codex 串行批准集成后，执行集成与资源收口的窗口。

本 Task 与依赖 P09-AC3-DELETE-HARDEN-1 都是 closed_with_limitations 且 integration_commit=null，因此没有获批集成事务。本次是用户明确授权的受限裁定窗口，不等于 approved integration window。现在可逐项指定保留或 NOT_APPLICABLE，说明引用和证据缺口；不能授权或执行 DELETE_SAFE、MIGRATE、ARCHIVE。其阻塞是逐文件用途/引用/可重建性证据不足；worktree 还需当前 Safety Inventory、clean/独有提交/untracked/进程检查。此处不要求 Owner 重做已闭合清册。

## 4. 硬约束

- AC1–AC5 PASS；AC6 未满足，证据状态 NOT_VERIFIED，无 N/A、无豁免。
- P09 AC3 delete 子条件保持 BLOCKED。
- 本 Task 未集成：status closed_with_limitations，integration_commit null。
- 本裁定不改变 Task/Plan/STATUS，不表示集成或物理清理完成。

## 5. 工作区边界

动手前 git status --porcelain 为 1236 行既存差异，包含 resource-manifest.json 未跟踪及其他既存内容。本轮仅新增本裁定文件；未运行 AC 探针、未执行 git 写命令、未删除/移动/迁移仓外资源。
