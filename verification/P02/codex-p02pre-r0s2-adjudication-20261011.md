# Codex adjudication：P02PRE-R0S2

## 对象与基线绑定

- Task=`P02PRE-R0S2`；Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- Repo=`G:/CODEX/New Manga`；branch=`main`；reviewed base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Review 前 Task=`7394 bytes / SHA-256 2DD4DDCBCC34479C49D3B54CF0AAA32D342682732F53AE20CABE67AB9799E9BB`；manifest=`7710 bytes / SHA-256 589DCD21C0C98128468A8758D433D630D6F3318409025B4F9FE26C548DB2F2FD`；prompt=`2320 bytes / SHA-256 F57132B89A6B567B0F0C9C6657EADAF049AC7B7B0335FDB7D95A98FEE6D06B54`。
- Reviewer 的最终 stdout=`19235 bytes / SHA-256 4EE88FF450005A59E7D3B0B2E36F3D96DEE61038CF95B1BE28B28F642656B19E`；归档 Review 与 stdout byte-identical、同 SHA。dispatch exit=`0`；`.exit`=`0`；stderr=`101893 bytes / SHA-256 70DE3AEE67C033997EFF5558084FBF322FBE9D9AEF3AE695B506ED6B817D10A5`（仅固定 hash，不在此复制内容）。
- DSH version=`0.2.0-rc.2`；route probe `dsh headless '只回复两个字：收到'` 返回 `收到`、exit=`0`。DSH session=`session-4c6ed355-3ef5-4175-bd55-ffb399644f8c`；`mount_session.py --latest` exit=`0`，mount log=`300 bytes / SHA-256 4683FE0BC22C38D1DA29BC65CA8710C0BE4F2FDA5F596E455C2967C853194E2C`。
- DSH 没有独立复算 Task/manifest SHA 或 live HEAD；Review prompt 列了固定路径但没有附 bytes/SHA。Codex 在 dispatch 前已计算并在当前 Task/Plan 绑定这两个对象；Review 期间 Task/manifest 未修改。故 Review 的内容审查有效，但 reviewer-to-byte pin 独立性=`NOT_VERIFIED`。R0S2 runner 未运行，因此没有实际 cmd bytes 需要事后绑定。
- Root Codex model/effort 未向 runtime 暴露，不作推断；`/root/r0s1_manifest_advisor` 对 R0S2 作静态只读筛查，实际配置=`gpt-6.1-sol / high`。DSH Review 的模型/effort=`NOT_VERIFIED`。

## 决策与执行状态

DSH 独立 Review=`NOT_SAFE_FOR_R0`；findings=`P0=0 / P1=1 / P2=3 / P3=5`。Codex 接受其 P1 RP-01。PowerShell shell selector 与 `login=false` 未证明 `-NoProfile`；启动时 profile/module analysis cache/PSReadLine history、实际 executable/完整 argv 及 `exec_command` wrapper/temp/log behavior 均未冻结为无副作用边界。用户要求安全不确定时停止；R0S2 候选必须标 `NOT_SAFE_FOR_R0`，不得转 `ready`、创建 pre-query checkpoint、调用 `OpenBaseKey` 或 `OpenSubKey`。

没有运行 R0S2 manifest body、PowerShell host query、Registry API、profile API、ACL/文件写入或任何目标机 WER 查询。Review 的静态批准/否决不改变 owner risk acceptance，也不证明 registry key 当前存在或不存在。

## DSH findings adjudication

| Finding | 级别 | Codex 处置 | 状态与影响 |
|---|---:|---|---|
| RP-01：PowerShell/profile/module cache/host wrapper 副作用无法证明 | P1 | `ACCEPT / STOP`。候选 runner=`NOT_SAFE_FOR_R0`；未执行。R0S2 Task=`blocked`。任何新 runner 必须另行冻结启动参数、profile/cache/history 及 wrapper/子进程边界并做非作者 Review。 | 阻止两个 Registry view 查询；不得以 login=false 或“没有 profile”推测放行。 |
| RP-02：review dispatch 未提供 Task/manifest bytes/SHA pins | P2 | `ACCEPT_WITH_LIMIT`。Codex 的 pre-dispatch pins 绑定被审文档；DSH 未独立复算，且 prompt 没有传入 pins。此为 Review 绑定限制，不改变 P1 的安全否决。 | Review 不是独立 hash 校验；下一次派发应把 pins 写入 prompt。 |
| RP-03：缺每 view query end UTC | P2 | `ACCEPT`。本次 query=`NOT_RUN`；不得补造每 view 结束时间。新候选若释放，必须为每条查询显式记录 start/end。 | 无运行结果受影响；当前视图观察仍 `UNPROVABLE`。 |
| RP-04：host 架构/view 可用性未冻结 | P2 | `ACCEPT`。未查询架构、未尝试 Registry32/64；不得假定视图支持或静默映射。 | view 观察未进行，相关状态 `UNPROVABLE`。 |
| RP-05：API observation 与目标谓词状态易混淆 | P3 | `ACCEPT`。即使未来拿到返回，需将 capture completeness=`PASS_WITH_EVIDENCE` 与 key presence/absence predicate 分列；`null` 不等同 key absence。 | 不产生本机状态证据。 |
| RP-06：未定义 stderr 缺失/非空分类 | P3 | `ACCEPT`。未来 manifest 必须记录 stderr 可得性与非空情况；本轮没有目标 capture stderr。 | 不产生本机状态证据。 |
| RP-07：GetCurrent(true) null/thread identity 语义未绑定 | P3 | `ACCEPT`。现有 R0S1 观测不替代本候选的 API 语义合同；新 runner 不得据未证语义放行。 | identity gate 没有为 R0S2 执行；本机 view 状态仍未知。 |
| RP-08：R0S1 的 module/child-name findings 与 R0S2 关系未显式说明 | P3 | `ACCEPT / CLARIFY`。R0S2 未使用 PowerShell module/provider cmdlet 或 Get-ChildItem，故不能解除 R0S1 两项分类；R0S2 另有 RP-01 启动边界 blocker。 | module gate 与 child inventory 原分类保持。 |
| RP-09：R6 历史候选并非授权来源未逐字说明 | P3 | `ACCEPT / CLARIFY`。本候选的授权来源是用户 2026-10-11 controlled read-only authorization；r6 的 HKLM 字符串只作对象来源，非本轮授权来源。 | 不扩大 scope 或 waiver。 |

## P02PRE 分类裁定

| 条件/对象 | 分类 | 范围与证据 |
|---|---|---|
| R0 固定时点 host identity、限定对象 metadata/ACL descriptor、候选 WER snapshot、13 项 protected-file pre/post hashes | `PASS_WITH_EVIDENCE` | 仅 R0 evidence 中被精确固定的对象和时间；不外推未来状态或完整 protected set。 |
| 两个 scratch leaf empty-or-absent | `UNPROVABLE` | R0S1 在 G: path 查询前停止；没有目标查询返回。 |
| R0S1 runner trusted-module continuation prerequisite | `NOT_SAFE_FOR_R0` | 当前实际 shell 未满足冻结的可信模块谓词；不推断模块数量、路径或安装状态。 |
| R0S1 的 Get-ChildItem direct-child inventory 方法 | `NOT_SAFE_FOR_R0` | 与“不读取 child name/metadata”承诺不兼容；未执行。 |
| R0S2 PowerShell startup/profile/wrapper runner | `NOT_SAFE_FOR_R0` | DSH RP-01；profile/cache/history、实际 executable/argv 与 wrapper side effects 无证。 |
| R0S2 HKLM LocalDumps Registry32/Registry64 当前 API 返回 | `UNPROVABLE` | 两次目标查询均 `NOT_RUN`；候选 runner 不可安全放行。 |
| WER 实际 reader/view/global/per-image policy/destination/expanded actor/T0 | `UNPROVABLE` | M9 adjudication 与 r6 未决边界；两视图存在性即使未来观测也不能证明该条件。 |
| private registry storage absence | `UNPROVABLE` | Technical condition remains unmet; `Owner Risk Acceptance=APPROVED`; `Gate Disposition=WAIVED_BY_OWNER`。waiver 仅覆盖该项风险接受，不是技术 PASS。 |
| profile-folder exact path / no-side-effect / absence | `NOT_SAFE_FOR_R0` / `UNPROVABLE` | getter 与路径合同仍未证；不猜路径、不调用。 |
| 详细 token/elevation/capabilities、有效写边界、未来 child/cache/TEMP/write closure | `NOT_SAFE_FOR_R0` 或 `REQUIRES_ACTIVE_TEST` | 按既有 R0 adjudication/r6 范围保留；没有动态执行证据。 |
|完整 protected inventory、祖先/file identity、hardlink/ADS 与未来 hash freshness | `UNPROVABLE` | 固定 R0 13 项 hash 不构成完整集合或未来状态。 |
| 所有本轮未执行的条件 | `FAILED` | 无。`NOT_RUN` / `UNPROVABLE` / `NOT_SAFE_FOR_R0` 不描述成测试失败。 |

## 风险、Gate 与接续

原值精确保留：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。用户本次 P02PRE 只读授权不是新的风险豁免或 Gate PASS。

P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。不查询、安装、启用或启动 Windows Sandbox。

相较 R0S1 pre-query checkpoint：R0S1 capture 已启动并按冻结 STOP 安全停止；DSH Review 和 Codex adjudication 完成；R0S2 候选经独立 Review 被否决，目标机 registry 查询没有启动。后续若出现新的只读执行路线，必须先有可验证的无副作用 runner/进程边界、完整对象 pins、非作者 Review 与 Codex 单独 adjudication；当前不派发另一个 Windows query。
