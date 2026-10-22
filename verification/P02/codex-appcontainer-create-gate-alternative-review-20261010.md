---
task_id: P02
reviewer: Codex independent Reviewer / orchestration_docs_review
author: Codex Lead
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_document_sha256: DC4186511DF30CE1AC20B8B53B5C0D9714B6B50947043CEDA31495D8FE1016B9
decision: approved
---

# P02 注册表准入条件替代方案 · 独立静态 Review

**结论：APPROVED，仅批准固定草案作为可交用户决定的静态提案。** P0/P1/P2/P3=`0/0/0/0`；在记录范围内未发现问题。草案没有声称证明现行的创建前 private-registry absence；它明确提出替换验收语义，并将该选择留给用户。API 返回语义、异常分支和清理约束与 Microsoft 文档一致。此批准不是用户接受替代条件、manifest 批准、执行授权或 Gate 通过。

## 对象及实际 pin

仓库=`G:/CODEX/New Manga`，branch=`main`，实际 HEAD/base/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。受审对象为此 HEAD 上的冻结未提交草案。Reviewer 非作者；唯一写入本 Review，未修改草案、Task、Plan/STATUS/Index 或其他证据。

实际本地读取长度与 SHA-256 和派发值一致：

| 输入 | bytes | SHA-256 |
|---|---:|---|
| 替代方案草案 | 7344 | `DC4186511DF30CE1AC20B8B53B5C0D9714B6B50947043CEDA31495D8FE1016B9` |
| P02 Task 快照 | 140979 | `CA68887C2A822377AD2A5D437AE02DCA16B20E682A7BB09FB6D72BC31B5A29DA` |
| 提权评估 r2 | 19618 | `BB95709DE27A5E13FE302FA3B3E68EB8B92143352B88B45C0668218138B3C736` |
| 提权评估 r2 Review | 6859 | `C45B8194D5923A7B8B315C5821A7924881EA13FC43EC6E151093E2DB8A469D21` |

草案 `:6` 固定引用无误。P02 Task 的当前静态提权评估授权不包含改变 AC/验收标准或系统实施；草案 `:24`、`:41` 明确另请用户决定，并要求后续精确 manifest 非作者 Review。此前原 Task 的“确定和执行范围”许可不能绕过当前 absence blocker，草案 `:10–12` 没有将其放大。

审查期间 Lead 在 Task 末尾追加了 r2/本提案的治理记录，报告写后 Task 为 `144727 bytes / 3E58BD819A70060C997EFAB113279DA06021B06E21386F77692DF4F41E62DB9D`。本次使用 `.NET SHA256.ComputeHash` 复算其前 `140979` bytes，仍为派发 pin `CA68887C2A822377AD2A5D437AE02DCA16B20E682A7BB09FB6D72BC31B5A29DA`；固定输入前缀保留，草案和 HEAD 未变。Reviewer 没有写入 Task，也没有覆盖该追加记录。

## Findings

无新增 finding。以下为核查事实与批准边界，不是待修问题。

## Architecture：语义、权限和清理核验

| 核查 | 草案位置 | 事实与结论 |
|---|---|---|
| Create 当前用户/返回值 | `:16`、`:28–30` | Microsoft 定义 per-user/per-app 创建；S_OK 为 data store 创建成功，ERROR_ALREADY_EXISTS 为已存在；E_ACCESSDENIED/E_INVALIDARG 属失败。草案只接受精确 S_OK，不以 SUCCEEDED 接受未知正值；已存在立即停止，其他结果、中断及无效 SID 为 UNKNOWN/BLOCKED，不删除后重建。与文档相符。[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) |
| 未文档化状态 | `:16`、`:30`、`:33–35` | 官方文档不承诺事务原子性、失败自动回滚或所有 registry 子对象先前不存在。草案没有反推这些条件，将其作为用户需接受的残余风险；因此“本轮新建”仅是拟接受 API S_OK 创建语义，不能扩张为各子对象原先缺失的证明。[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) |
| Get 的访问与目标 | `:18`、`:31` | API 接受 desiredAccess，返回 current profile 的 HKEY；调用者须具备对应用户访问上下文，没有按 moniker/SID 查询任意 profile 的参数。草案仅后置只读、KEY_READ，要求绑定本轮对象且不符即停，没有把 Get 当成前置无副作用探针。如何在具体调用上下文绑定当前 profile、读取哪些安全描述符仍由精确 manifest 冻结，当前不推断已实现。[GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) |
| Delete 与失败状态 | `:20`、`:32` | 不存在 profile 删除亦成功，不能证明先前 absence；文档要求最好先关闭 storage 文件句柄，失败后状态不确定并建议再调用。草案只允许对有本轮 S_OK 记录的同用户/moniker清理，失败记 CLEANUP_BLOCKED，不清理来源未知的部分残留；未用 Delete 作为 existence probe 或碰撞处理。[DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile) |
| 固定身份与 capability | `:28` | 固定单一 moniker，当前用户、零 capability；身份、显示名/描述、空 capability 表示、API 与证据参数必须事先进入 manifest。草案未授权 impersonate 其他用户、扫描 profile/registry 或扩权。文档的当前用户语义支持此限制。[Create 参数与 Remarks](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) |
| 清理调用上下文 | `:32`、`:41` | Delete 不支持在 AppContainer 内调用。草案没有提供执行 manifest，也未指定在容器内清理，故不是现有错误；后续 manifest 必须固定容器外同用户 cleanup controller、句柄关闭及成功/失败分支，不得把本次 Review 当成对此上下文的验证。[Delete 返回条件](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile) |
| 用户决定与 Gate | `:12`、`:24`、`:35`、`:39–48` | 接受与维持两个决定明确。接受只允许后续改写准入条件，未 Review manifest 不可执行；其余隔离 Gate 未自动解除。当前无 READY 产品实现 Task，Review 不是 Gate 证据。 |

Architecture 结论：作为验收变更候选，草案清楚呈现条件、已知风险和权限边界；不存在由 Reviewer/Codex 代替用户接受风险的表述。真正的 API 调用 manifest 尚未批准，本次不提供实施安全性保证。

## Verification：实际读取与未运行项目

本次 PowerShell 只读命令：`git rev-parse HEAD`、`git branch --show-current`；固定输入的 `Get-Item`、`Get-FileHash -Algorithm SHA256`；草案带行号的 `Get-Content`、Task 尾部读取与 `rg -n` 核查创建前禁令/moniker；指定输出的 `Test-Path`（起初不存在）。网页工具直接读取三项草案引用的一手页面：

1. [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)：参数、SID 释放要求、返回值、profile storage、current-user/impersonation 语义。
2. [DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)：不存在亦成功、容器内不支持、关闭句柄、失败状态不确定与重试语义。
3. [GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)：desiredAccess/current profile HKEY、访问用户身份与返回值。

均取得可读官方正文。没有运行任何上述 API，也没有查询主机 profile、registry、ACL、用户 token 或 OS 状态。未来调用后的真实返回、输出 SID、folder/registry 绑定、权限、安全描述符、失败残留与清理结果全部 UNKNOWN / NOT_VERIFIED。

当前 Gate：private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。其余 Task 的 Phase A、scratch ACL/label、hook/cache/child-process closure 前置条件同样不因本草案变化。未运行 Sandbox、OS probe、build、Cargo 或产品测试；NOT_RUN 未表述为 PASS 或失败。

Verification 结论：静态 pin 与 API 文档语义核验完成，可以批准提案文本；系统/产品验证全部未执行。

## 下一步建议

Agent=Codex Lead/Integrator；当前步骤为 P02 静态提案 adjudication 与提交用户选择，恢复点为上述主仓 main/base/head。允许范围仅规定 P02 Task/治理记录和裁决证据；保留草案、Review、其他固定证据与他人文件。交付为文档裁决和准确的用户决定请求；验证固定 hash、引用、授权边界，不提升 Gate。

可转发：

> Codex Lead：在 `G:/CODEX/New Manga` 的 `main@cddff58469b56e181019a8ddfeade80684bc7eb9` 对冻结草案 `DC4186511DF30CE1AC20B8B53B5C0D9714B6B50947043CEDA31495D8FE1016B9` 与本 Review 独立 adjudicate；仅追加规定 P02 文档/裁决证据，向用户提交是否接受“单次精确 S_OK + 后置只读验证”的验收替换及部分失败风险。用户决定与后续精确 manifest 独立 Review 前，不改验收标准、不调用 API、不创建/删除 profile，不运行 OS/Sandbox/build/Cargo/产品验证。

未检查：实际主机权限、API 返回、对象状态或清理行为；未运行系统/产品验证。
剩余风险：用户尚未接受验收变更；创建部分失败与 registry 子对象语义仍未知，产品 Gate 继续阻塞。
