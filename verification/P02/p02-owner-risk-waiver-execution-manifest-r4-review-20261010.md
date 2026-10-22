---
task_id: P02M4
reviewer: Codex /root/p02_manifest_reviewer
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: changes_requested
---

# Review：P02 execution manifest r4

r4 将 raw Git status 与 protected 投影分开，保留每条授权 delta 并与物理 output inventory 对应。MR3-01 在静态规则层已修正；新冻结的 status 命令默认可能写 index，与本 manifest 的禁止写入和 index invariant 冲突。本次 P0/P1/P2/P3=`0/0/1/0`；新 P2 open。Create、Hard Build Barrier、Build/AC 均未放行。

## 范围与精确对象绑定

- Reviewer=`/root/p02_manifest_reviewer`，非作者 `/root`，不是 Advisor。派发/Task 的角色配置=`gpt-6.1-sol / medium`；运行时 model ID/effort 无独立 introspection，记 `MODEL_RUNTIME_NOT_EXPOSED`。
- 本轮读完整 r4、r3 adjudication、当前 Task/Plan/STATUS/00_INDEX，并沿用同一会话已读的 r1/r2/r3 与各 Review、identity evidence/Advisor、相关 versioned contract、Review 模板和协作协议。新核 Git 官方 status/全局参数合同。唯一写入为本报告；未修改被审对象或其他文档。
- 当前治理入口正刷新为 P02M4，初读 STATUS/Index 仍为 r3；Task/Plan 已登记 r4 精确 pin。各版本 waiver/Gate 原值一致，不借刷新过程推断执行已释放。
- Reviewer 自己通过 PowerShell 文件读取核验 r4：`Get-Item Length=28347`；`Get-FileHash -Algorithm SHA256=DFB2A7DFABBA4BF5F8D17788DC5FD22534DA692A2848918CD4E978D63CA5C300`，与派发 pin 完全一致；完成前再次复算同 SHA。对象命令 exit=0。
- Reviewer 自己核 Git branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`、common-dir=`G:/CODEX/New Manga/.git`。tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b` 是 Owner/治理文档提供值，本轮未独立复算 tree。

`object_binding=VERIFIED` 仅针对精确 r4 的 28347 bytes/SHA，不能推广到同 HEAD 的其他 dirty 内容。identity evidence 的留存 SHA 已于本 Reviewer前次核验；原命令真实性/运行时身份仍没有本轮新证据。

未执行 r4 status 命令、OS/API/profile/registry/ACL/token/path probe、Sandbox、build/Cargo 或 AC；没有为证明 finding 运行 index 写入实验。

## Architecture：executed / CHANGES_REQUESTED

### MR3-01 及既有处置

| finding | 文档层处置 | 依据/限制 |
|---|---|---|
| MR3-01 / P2 | FIXED_IN_R4（投影规则） | :129 移除 raw status 全等 invariant；:130 保存 raw bytes/hash 与 parsed records，仅 protected projection 的 XY/path bytes 前后相等，authorized delta 保留并对应物理 ID/hash。canary 新增不再仅因 raw status 变化违规。执行命令副作用另见 MR4-01。 |
| MR2-01 / P2 | 文档 regular-file/output/status 分类冲突已处置 | :129–131 互斥集合、逐对象 SD/stream/hash、exact scratch roots 与唯一 canary 文件，:132 成功时两组 protected 规则一致。禁止排除祖先/整段 verification/P02 或事后过滤。 |
| MR2-02 / P2 | FIXED_IN_R3，r4 保留 | :128 十文件 allowlist/16 KiB incident/64 MiB 上限，:132 九项成功记录，:133 停止确认后的 BLOCKED incident 与真实 partial records，无占位 PASS、无覆盖/重试/清理。实际实现仍未冻结或执行。 |
| MR1-01/02 | 前次静态修正维持 | SID=`2661602853` 绑定留存 stdout；Create store/profile Temp/scratch/canary 范围分开，父目录/负向 control 无写许可，ACL/label 零变更。实时对象身份/权限仍未知。 |

### status 格式核对

固定 flags `--porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none` 在 Git 官方格式上有依据：porcelain v1 的路径相对 repo root、无颜色；`-z` 以 NUL 分隔且不 quote 特殊路径，XY 与首个 path 之间保留一个空格。`--no-renames` 关闭 rename detection，`--untracked-files=all` 避免目录聚合。r4 要求保留原始 bytes、按 exact output root/file 分类、XY/path bytes 比较，方向明确。[Git status 文档](https://git-scm.com/docs/git-status)

具体 parser、固定 offset/XY 合法值、NUL 终止完整性、异常记录失败分支、repo identity 与路径组件边界、受控配置/版本仍需在 implementation freeze 中审代码；不能仅凭文档称已经正确解析空格/Unicode/边界。其余物理 inventory 仍覆盖被 Git ignore 的授权 outputs，不以 status 没显示就省略实物记录。r4 没有扩大目录排除或修改 ignore 的授权。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态/修订 commit |
|---|---|---|---|---|---|---|
| MR4-01 | P2 | r4 :129–130、:132、:134 | 固定 status 命令未禁用 optional locks。index stat cache 需要刷新时，Git status 默认可能写 index 并创建 index.lock；该宿主写入不在授权 output 范围，且可能改变 :129 保护的 index hash，使测量自身污染 invariant。 | 静态命令为 `git -c core.quotepath=false status ...`，无 `--no-optional-locks`/冻结 GIT_OPTIONAL_LOCKS=0。Git 官方 §BACKGROUND REFRESH 明确默认刷新并写出 index；全局参数文档定义禁用 optional locks 的方式。本 Reviewer未运行此命令，不能声称已发生本机 index 变化。 | 将冻结命令改为 `git --no-optional-locks -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`，或同等精确 GIT_OPTIONAL_LOCKS=0；保留 index invariant，不添加 index 写例外。native/controller freeze 另核配置、fsmonitor/helpers/submodule 与进程副作用，不把该参数当完整 no-write 保证。 | open / 无修订 commit |

官方证据：[Git status / Background Refresh](https://git-scm.com/docs/git-status#_background_refresh)、[Git --no-optional-locks](https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks)。默认 index 写刷新是明确合同，不能由 Owner 一次 exit=0 或“只读命令”称谓排除。

## Verification

| 场景 | 实际步骤 | 环境/对象 | 结果 | 证据/限制 |
|---|---|---|---|---|
| r4 精确 bytes/SHA | Get-Item、Get-FileHash；完成前再次 hash | PowerShell；固定 HEAD | PASS（文档对象） | 28347 / 指定 SHA，exit 0 |
| Git 恢复 | rev-parse HEAD、branch、common-dir | PowerShell；main | PASS（恢复信息） | 同 HEAD/common-dir；tree 未重新核验 |
| MR3-01 静态投影 | 交叉读 r3/report/adjudication/r4 | 精确 r4 | PASS（规则修订） | :129–132；不能代替实现 |
| status 命令安全性静态核对 | 读取 Git 官方 status/全局参数文档 | git-scm.com；本轮公开资料 | FAIL | MR4-01；默认可能写 index |
| Owner 的 exact command exit=0 | 本轮仅阅读 adjudication/Task 所述运行 | Owner 提供的说明 | NOT_RUN（Reviewer 未运行/无日志核验） | Owner称命令可用；stdout 未保存，不能作安全 Gate |
| parser/buffer/physical inventory/evidence成功失败实现 | 未执行；implementation尚未冻结 | 当前 r4 | NOT_RUN / BLOCKED | 无运行 artefact |
| OS/API/Create/profile/registry/ACL/token/cache/WER/child/write closure | 未执行，派发禁止 | 当前仓库 | NOT_RUN / BLOCKED | 无 OS 测量或安全证据 |
| Sandbox/build/Cargo/AC1–AC7 | 未执行，派发禁止 | 当前仓库 | NOT_RUN / BLOCKED | Hard Build Barrier=EFFECTIVE |

所有 PASS 都限于实际文档/恢复检查；没有 AC/test 数字。Findings 是冻结方案问题，非已发生越权或产品测试失败。报告为唯一允许持久化产物，不另造运行日志。

## 仍阻止 preflight/Create/Build/AC 的条件

1. **preflight**：native controller/probe 代码及 exact EXE/DLL/path-ID/hash/架构/依赖、参数/CWD、完整环境、API/access masks/flags/share、timeout/记录/容量/故障状态机、bootstrap 尚未冻结和独立审查。MR4-01 需修订；Git helpers/config/identity/stdio/buffer/parser 的实际行为必须纳入 no-child/no-write 边界。
2. **Create**：固定身份需实时重核；profile-folder 创建前无副作用定位/absence 未证；zero-cap LPAC Getter 资格与额外副作用未证；精确 WER images/views/per-image override/destination/T0 顺序未冻结；input/scratch/canary reparse/hardlink/ADS/file-ID/ACL/label/inventory、TEMP/cache、protected pre-state/evidence 新鲜度均无实际证据。
3. **probe resume/创建后**：真实 LPAC SID/Low IL/空 capability/token invariants、Job/child policy、无继承特权 handles、全部 child/broker/COM/WER/瞬时 writes 强制闭包没有验证。Job 消息、polling/self-report/hash equality 不替代这些证据。
4. **证据**：16 KiB incident 与64 MiB buffer 的精确容量计算/字段/event上限/序列化/溢出/ reserve failure、安全停止与 post collector actor、十文件 CREATE_NEW/path identity/race/partial branch 尚需已审实现及运行证据；原始 status byte编码/NUL parser/路径边界/对应 inventory 必须验证。
5. **Hard Build Barrier/真实 build/AC**：真实 compiler/package manager/WebView descendants 的 token 与写入强制边界未冻结/验证；synthetic single-process 成功不代替 build。scratch ACL/label 当前零改动，既有权限不足只能 BLOCKED。AC1–AC7 必须真实运行逐项留证，P02M4 静态 Review 不能满足产品 AC、P22/P04 集成 Gate 或发布 Gate。
6. **清理**：现有停止、保留现场、不自动 Delete/递归清理/重跑有效。未来清理必须另冻结精确本轮所有权、API、句柄/进程关闭、结果/重试上限；未知或并发变化仍 CLEANUP_BLOCKED。

waiver 仍仅豁免创建前 registry absence proof，不覆盖以上条件。维持 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION` 与 `technical condition unmet; user explicitly accepted residual risk`。

## 结论与下一步

`decision=changes_requested`。Architecture：MR4-01/P2 未处置；Verification：静态来源指出固定命令存在默认写副作用，关键执行项仍 NOT_RUN。本 Review 不授权 preflight/Create/profile/registry/ACL/probe/build/Cargo/AC/Sandbox；Codex 最终 adjudicate。

推荐下一 Task：**Codex 的 P02M4 adjudication 与 r5 静态修订**。Owner=Codex，Reviewer=非作者。恢复点=`G:/CODEX/New Manga`、`main`、base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；先在 Task/STATUS 登记新 manifest/adjudication/checkpoint 的允许路径，保留 r4 和本报告。交付修订命令/flags、MR4 disposition、new bytes/SHA 与非作者复审；禁止产品代码/他人 dirty 内容及所有 OS/API/build 操作。

可直接转发：在 `G:/CODEX/New Manga`、main、base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9` 完成 P02M4 adjudication。保留 r4；登记 r5 文档允许路径；针对 MR4-01 冻结禁用 optional index locks/refresh 写入的 Git 命令，保留 index hash invariant，不添加 index 写例外，也不重跑冻结候选命令证明安全。形成新 bytes/SHA、disposition 与 checkpoint，派非作者复审。其它实现和 OS/Gate blockers继续登记；所有 Create/OS/API/profile/registry/ACL/token/path probe/Sandbox/build/Cargo/AC 保持 NOT_RUN/BLOCKED，Hard Build Barrier EFFECTIVE。

未检查：实际模型后端、Git 安全命令运行/parser实现、OS/API/二进制/buffer/build/AC。
风险：固定 status 默认可能写 index；单项用户 waiver 不解除其余安全条件。
