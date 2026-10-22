# P02PRE-R1H 独立 source-pin reconciliation addendum

Reviewer=`/root/p02_r1h_remediation_review`；Owner=`/root/p02_r1h_codex_owner`；Integrator=`/root`。本补充仅核对冻结输入与当前 Task 对原 findings 的影响，不是新的代码 Review verdict、Gate 或 AC PASS。

派发 prompt SHA-256=`DE35D93D5F5E5AE0AA38C213D87E36281FBE0062402B51DF9ED1F01EAACEC83E`；当前 reconciliation JSON SHA-256=`516C202248B2347BE790707AB71465B57BC26A3C8F056FE82BF25354441BB4E2`。二者实测相符。

## 当前 pin 核对

按当前 JSON 的逐项 bytes/SHA-256 实测：source=`8/8 MATCH`；candidate=`3/3 MATCH`；合计=`11/11 MATCH`。

| 对象 | bytes | 当前 SHA-256 |
|---|---:|---|
| 当前 `doc/tasks/P02PRE-R1H.md` | 13733 | `86FFDD51CE8033C7C836A032BCA7F9EAE07C45F7C2411E68F8049BAB9EFF185D` |
| R1H manifest | 4760 | `28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74` |
| 首轮 static Review | 2308 | `4BB1D8B8C8FACD96C4C087774756A71D79F832F10AD75026ADA3800579EE6688` |
| 首轮 adjudication | 1543 | `20EA61BC98F5826BF7FDF487E01B3F34CF6FBA609E9C3999C242100920268497` |
| 首轮 post-pins JSON | 2070 | `9AA0A6783B9466BD146DB04A65FC61287144C6ADA5B6747AE5958538251BCDB4` |
| remediation static Review | 7949 | `2BF89EE77D3552C3DC11008F1C3A98F5ED143D711949705303CD133A22AC6021` |
| remediation input-pins JSON | 3120 | `66CCFB05CD3E05FF12D4C1D4C85469AA864E0A0C5CCAC2149E8AD554D9A09CA3` |
| remediation dispatch prompt | 3282 | `79786443FE374E25989AE049A81A5B3949A45578B3E20B3150FE61BEB30799DB` |
| candidate capture | 93124 | `0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3` |
| candidate selfcheck | 24452 | `17202B6EDD5C3185432F90F7618ECDC689739492173AE2D4EA4E9D1AEF9CBCD8` |
| candidate Handoff | 4397 | `2E4E9EA2930930BF4A2AD9F04AE3FD542635F384E7CB07A27349ADDDE6B6F0E0` |

Candidate HEAD/tree 经只读 `git rev-parse HEAD HEAD^{tree}` 确认仍为 `4a02811d6edf9ab423d299a36c51f103e62dd5f3` / `95eb4b2977bded814e667b392e46ce5f76015c9f`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`，冻结 base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。

原 Review 的 `8/8 MATCH` 仅属于当时 Reviewer 实际读取和复算的输入快照。Task 原 pin=`95AC04FABD0EBFC1B97AF1B0C37F8B24AF62B7E8C1346057E0826AEA726E85CA`、11538 bytes，当前 Task 已变化，不能延用该旧 Task pin。本次 `11/11 MATCH` 明确使用新的当前 reconciliation JSON。

## Task 与 findings 的对应关系

本轮完整读取当前 Task，将其 AC1–AC7 与本 Reviewer 原静态 Review 时读取的条文比对：七项验收条文保持相同。当前仍要求 skip 停止后续 hash/ACL/枚举/target 读取（AC1）、断言真实 skip 顺序且无 target 读取（AC2）、P0/P1/P2 为零或修复后再审（AC3）、self-check 实际 PASS（AC4），其余 pre-run/one-shot/Gate 条件亦未改变。原有禁止范围及三文件写集合保持不变。

当前可见差异为 Reviewer 元数据、Handoff/Review 进度文本、历史标题及追加 delivery/review evidence 段；没有对 R1H-005/006 的相关实施要求作放宽。完整旧 Task 的不可变字节副本未在本派发中提供，因此不声称以磁盘上的旧副本证明了 root 只做三个替换；本结论基于本 Reviewer 先前已实际读取的 AC/要求与本次当前文件的比对，以及可复算的当前 pin。

- **R1H-005 / P2=`OPEN`，仍有效。** selfcheck 278–282 对 helper 的全部成员调用禁令仍与 capture 144 的 `[string]::IsNullOrEmpty`、398 的 `[Math]::Max` 冲突，无法满足当前 AC2/AC4。候选字节未变，没有新增运行证据。
- **R1H-006 / P2=`OPEN`，仍有效。** selfcheck 263–301 的 AST 覆盖仍未验证组件循环至 continue 前的全部操作区间，缺少真实控制流变异负例；其纯函数复制断言仍不能代替实际候选绑定。这与当前 AC1/AC2 及冻结 Review 派发中的 R1H-004 标准直接相关。

原 `CHANGES_REQUESTED`（P0/P1/P2/P3=`0/0/2/0`）仍成立；本补充没有把未完成安全条件提升为 PASS，也没有批准集成或运行。

## 实际操作与限制

仅 `Get-Content`、`Get-Item`、`Get-FileHash` 对派发已枚举输入进行静态读取/bytes/SHA 核对，以及上述只读 Git HEAD/tree 查询。第一条复合核对命令因 shell 中 `foreach` 后直接接管道语法错误 exit=1，未执行其中的核对；修正为显式 `$rows` 数组后执行 exit=0，得到表中 11 项匹配。该 shell 解析错误不是候选 parser/test 结果。

唯一写入为本 addendum。未修改候选、Task、Plan、STATUS、Index 或原 Review；未执行候选 parser/self-check/preflight/capture/getters/tests/Build/Cargo/AC1–AC7/OS 动态验证/Sandbox。

下一步：由 `/root` adjudicate 本补充，然后由原 Owner 在同一授权三文件范围修复 R1H-005/006，新 head 再交非作者独立 Review。

未进行任何运行验证；两项 P2 仍开放，Build Barrier 不可据本次 pin 对账解除。
