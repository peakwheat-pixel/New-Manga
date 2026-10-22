# P02M6：profile-folder 创建前路径核验 API 合同评估

## 任务边界

- Owner/作者=`Codex /root`；Integrator=`Codex /root`；Reviewer=`/root/orchestration_docs_review`，非作者。
- 仓库基线：`G:\CODEX\New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 唯一 Owner 输出为本报告；独立 Reviewer 唯一写入路径=`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-review-20261010.md`。
- 只阅读 Microsoft Learn 官方 API 文档并做静态合同分析。没有调用 Windows API、访问 AppContainer profile/registry/ACL、读取目标路径、做写入探针、运行 Sandbox、build/Cargo 或 AC。
- P02M5 精确 manifest Review 已批准的对象为静态文档；当前这项独立分析只检查 P02PRE 的一个前置条件，不改变 P02 的产品范围或用户 waiver。

## 官方合同事实

1. Microsoft Learn 对 [`GetAppContainerFolderPath`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath) 的说明是：取得指定 AppContainer 的 local app data folder 路径。签名只有 `pszAppContainerSid` 和输出路径指针；成功返回时需由调用者以 `CoTaskMemFree` 释放字符串。文档称其返回路径与调用 `SHGetKnownFolderPath(FOLDERID_LocalAppData)` 得到的路径相同，并规定线程 token 存在时按当前用户的 AppContainer 计算、否则按进程 identity 计算。该页面没有写明此 API 是纯查询、不会创建目录、对目录不存在时如何返回，或它内部选择了哪些 known-folder flags。
2. Microsoft Learn 对 [`SHGetKnownFolderPath`](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath) 的合同包含 `dwFlags` 参数，允许传 `0` 或 known-folder flags；输入的 `hToken` 可以指定用户。官方 [`KNOWN_FOLDER_FLAG`](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) 定义 `KF_FLAG_CREATE`（`0x00008000`）会强制创建不存在的文件夹；`KF_FLAG_DONT_VERIFY`（`0x00004000`）会跳过检验文件夹是否存在。它们能说明这些 flags 在该 known-folder API 上的语义，但不能单凭“返回路径相同”证明 `GetAppContainerFolderPath` 等同于调用 `SHGetKnownFolderPath` 时具体传了哪些 flags，也不能证明其 target-specific behavior 不会创建目录。
3. Microsoft Learn 对 [`CreateAppContainerProfile`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) 明确规定该 API 为当前用户创建 per-user/per-app profile。profile 包含 folders 和 registry storage；`S_OK` 表示 data store 创建成功，`HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)` 表示该 app data store 已存在。此创建合同不回答上述 path getter 在调用 Create 前是否无副作用。
4. Microsoft 的 [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) 指南把创建 profile 与通过 `GetAppContainerFolderPath` 取得可写位置放在 profile 创建之后的流程中。该示例顺序不能单独证明 getter 在创建前一定会创建或一定不会创建。

## 结论

返回值/路径映射事实与“执行该 getter 绝不创建目录”的副作用保证是两个不同命题。当前公开 Microsoft 合同没有明示该 getter 的 no-create 保证、路径缺失时的精确结果，或其内部 flags。用 `SHGetKnownFolderPath` 的 flag 描述推导 `GetAppContainerFolderPath` 的内部实现，会超出文档证据；通过 guessed SID path、猜测 package path 或执行未经验证的目标 API 来补证也违反 P02 当前禁止边界。

因此 `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。现有证据不支持在 Create 前调用 `GetAppContainerFolderPath` 后把返回路径不存在记成可信 pre-state；也没有找到正式合同确认的、能在不创建 profile 的情况下返回完全相同路径并检查缺失状态的替代 API。未执行运行时探测，不把静态解释升级为 OS 事实。

## 允许的后续路径

- 继续只读搜索更具体、可适用于当前 Windows 版本的 Microsoft/Windows SDK 正式合同；若找到直接明确的 no-create 语义，固定 exact source/version 并交非作者 Review，再由 Codex 另行审 adjudication。
- 若正式合同仍未覆盖，P02 Create 保持 BLOCKED。当前 Owner waiver 明确只覆盖 private-registry storage 创建前缺失证明，不覆盖 profile folder；任何扩大这项风险接受都必须由用户单独决定。本报告不请求或推定该决定。
- 其它安全 blocker（zero-capability registry Getter、WER/T0、controller/probe、子进程/写入闭包、保护文件/hash、Build descendants 和逐项 AC）仍需独立处理；不得因本报告或 P02M5 通过解除。

## 验收与状态

- 已完成：精确引用 Microsoft Learn 的 getter、known-folder flags、Create API 和执行指南合同；把明确事实、推断边界、阻塞状态及后续选项分开；没有调用任何 OS API。
- 待完成：`/root/orchestration_docs_review` 对本精确报告的独立静态 Review；Codex 根据报告与 Review 作 adjudication 并刷新唯一 Plan/STATUS/Task/checkpoint。
- 当前 Gate：`profile_folder_no_side_effect=UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。
- 用户风险状态必须原样保留：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。此 waiver 仍仅限 private-registry storage 的创建前缺失证明。
