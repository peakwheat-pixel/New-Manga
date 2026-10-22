# P02PRE-R1F Round 5 Review：Codex Adjudication

## 输入与独立 Review 证据

- Owner/Author/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`，session=`session-c42e3dff-f2db-4333-a39e-9c970a261772`。
- 首轮 Review 输入 pins：Task=`17488 bytes / 0795FA274CED5694FF4586EDA0553AAAA9D463C44A78B373E47B4F30AF46B0CD`；manifest=`16284 / 5B5C3740DFF998DFBC1833E01236429273DE5BA9C755512AFD88012F7E1AD1C9`；script=`60725 / 80C8BC311CE372832BF1D4567ABDCF7E8AA2D7296CBE339FE95BAD65D63E5216`；self-check=`1694 / 06A8387E6ABCC6DD4F3912FDCBEE006E58B96C8E00F64A165C365435D7ADD2CE`。
- DSH decision=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/1/2/5`。报告=`verification/P02/dsh-p02pre-r1f-review-r5-20261011.stdout.md`（`21403 bytes / 8448A331D20AD36692D7A67738B2D7C5BFA7587A0AA1C922ECDE1A16C8F954E3`）；prompt SHA-256=`5FF83A1B8ADBD578A7CC7A08C173F0339ED792FA4798E2E607BBBA5711AC682`；stderr=`110376 bytes / 61BC658261E84DA99CC5CD4252A4C3BA2D601F59C6E3010C898F65CC629864AC`；exit file 内容=`0\n`（2 bytes），CLI exit=`0`。
- Reviewer 声明只读 Task/manifest/script/self-check，不运行命令、capture、host getter、registry/ACL API，不访问 `.tmp.driveupload`，不写共享文件。Codex 对报告与文件 pins 作独立核对；本 adjudication 不把 Review 或 self-check 视作 P02PRE/Technical/Build Gate PASS。

## F1–F8 裁定

| Finding | 裁定 | Codex 处置与剩余限制 |
|---|---|---|
| F1 parent directory 被误判 | `ACCEPTED / FIXED_IN_CANDIDATE` | `Get-InventoryAction` 只对 leaf 应用目录与 Git mode 限制；任何 reparse component 仍 stop。Self-check 增加普通父目录、tracked-symlink 候选父目录、directory leaf 断言。 |
| F2 `$null` 被 `[string]` 形参归一 | `ACCEPTED / FIXED_IN_CANDIDATE` | `$GitMode` 改为 `[object]`，只在 leaf 且 mode 非 null 时校验索引模式；self-check 覆盖无 index mode 的 regular leaf 与 reparse leaf。未跟踪 regular file 依 frozen manifest 允许 hash。 |
| F3 `.tmp.driveupload` 路径形式绕过 | `ACCEPTED / FIXED_IN_CANDIDATE` | 增加纯函数拒绝绝对路径、空/`.`/`..` 段、ADS `:`、尾随点/空格与重复分隔符；规范化后做仓库边界校验，派生 canonical relative 并要求与规范输入一致，随后只用 canonical path 作 staging exclusion。Self-check 覆盖 reviewer 给出的三种别名与 ADS/越界/空段。 |
| F4 Task 仍写 parser final r6 | `ACCEPTED / FIXED_IN_CANDIDATE` | Task 将历史目标标为 superseded，最终 parser 目标统一为 Windows PowerShell 5.1 R8；文中分别称 `Review Round 5` 与 parser R5–R8。 |
| F5 首次 wrapper failure 未说明源 pins 已过时 | `ACCEPTED / FIXED_IN_CANDIDATE` | Task/manifest 记下该 wrapper 绑定替换前 source=`60662 / AA99D7C4D9E38EE8FF14315AAE968226AE1FA67935283408F294603619B2A884`，并注明在 parse 前失败，不是脚本失败。artifact 原样保留。 |
| F6 正常 repository record 缺 error keys | `ACCEPTED / FIXED_IN_CANDIDATE` | 初始 record 加入 `errorOperation=$null` 与 `error=$null`，保证成功与失败 JSON 字段结构一致。 |
| F7 manifest 环境变量计数 | `ACCEPTED / FIXED_IN_CANDIDATE` | Codex 从固定 R1 manifest 与脚本分别读取逗号清单，结果均为 35 项且逐项顺序相同；R1F manifest 改为 35。 |
| F8 status getter 先于 staging 排除 | `ACCEPTED / FIXED_WITH_LIMITATION` | 固定 status 命令增加 pathspec `-- . :(exclude).tmp.driveupload`。对 main 与 scratch 执行只读 status 查询均 exit 0、stderr 0、输出不含该路径；main=`701 records / 44443 bytes`，scratch=`0 / 0`；`.git/index` 前后 SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。这是精确 argv 与返回值证据，不是 OS 级 Git 内部访问监控；Git status 的全部内部 metadata/content no-read 仍=`UNPROVABLE`。 |

## Self-check 与阶段状态

- 修复候选 script=`64626 bytes / SHA-256 83C0126123C9799B594CF4F152D1B03AD7BC26E194EBD65E34309B23053A8E91`。
- 新 Windows PowerShell 5.1 isolated self-check=`verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json`，`2694 bytes / SHA-256 F2FCE66ECAE8E1BAC1AB8B795C2E004D91D8EE7061389415C76B92F7176FE39F`；child=`5.1.26100.9549`，exact source `PARSE_OK`，6 个抽取函数/断言 `PASS`，输出计数 0，capture/getter/registry/ACL write 均 false，parent/child source pins 一致。Parent PowerShell 7 helper 的异步等待返回值未被赋空，工具 stdout 因而另外显示两行 `System.Threading.Tasks.VoidTaskResult`；child 原始 stdout 单独捕获并通过结构核验，该 wrapper 输出没有进入 self-check/capture。
- 当前 script 自检仅覆盖解析与纯内存函数，不能替代 follow-up Review、R8 parser artifact、Codex pre-run adjudication 或 host capture。
- 下一步：冻结修复版 Task/manifest/script/self-check pins；DeepSeek Harness 对这些 exact bytes 执行独立只读 follow-up Review。Review=`APPROVED` 并由 Codex adjudicate 后，才执行 R8 parse-only 与 pre-run 核验。capture、Build/Cargo、AC1–AC7 当前仍=`NOT_RUN / BLOCKED`。

风险状态不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`。
