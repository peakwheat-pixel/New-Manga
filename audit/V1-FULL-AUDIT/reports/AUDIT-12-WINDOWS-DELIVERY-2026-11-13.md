# AUDIT-12：Windows 构建与交付

**Codex adjudication（2026-11-13，独立上下文）：** 本报告中的 `REVIEW_PENDING` 候选已由 Codex 最终独立 Review 裁决（首轮 `reviewed_head=d92859c9ac8a4d3122d6cabfe4d44af980574104`，复审 `226eb048006ffa804ebefd9f98e51bbc13793f31`；结论 REJECT 属交付文档返修，不改变产品 Gate）。现行状态以 `reports/11_ISSUES.md` 与 `AUDIT_ISSUES.md` 为准；本报告原观察与限制保持原字节语义。 本报告中的 `AUDIT-12-CAND-001` 被裁为 **finding P3（交付工具）**。

状态：`PARTIAL`。当前 fixed source HEAD 的 Avalonia Release configuration build 与 AUDIT-09 的开发输出 GUI launch 有证据；隔离工作区外还存在 2026-10-26/28 的旧 zip 与 NSIS setup 包。旧包不能绑定到当前产品基线，因此本阶段不把它们作为当前 build/release 通过证据。当前 Task 明确不授权 publish/install/uninstall，本轮没有运行安装包。

## 证据与当前输出

- 当前产品源基线：`10e4ee013835605800d3830fb960ae8d3aa04167`；AUDIT-09 Release configuration `dotnet build apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj --no-restore --configuration Release --verbosity minimal` 在 HEAD `2509db99057a8a57423b3cf3cf4490c558994b37` EXIT 0，0 warnings / 0 errors。实际 GUI 会话从 `apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/NewManga.App.exe` 启动；它不是已安装应用。
- AUDIT-12 静态 inventory 在 HEAD `4e04e68c0db07ab136bc801e7fee27e7a5097564` EXIT 0；`logs/audit12-delivery-inventory-20261112T223042315179Z.log` 与 runner JSON 记录产品 build exe、sidecar 文件、交付脚本 SHA-256/关键行和外部包的直接文件 metadata。当前 `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe` 与 Python runtime 文件可见；这只证明本机存在 sidecar 输出，未证明其与任何旧 setup 包匹配。
- 外部只读 inventory 发现：`NewManga.workspace/task-envs/FINAL-VALIDATION-1/out/` 有 2026-10-26 base zip（102,493,981 bytes）和 models zip（724,501,664 bytes）；`NSIS-INSTALLER-1/out/` 有 2026-10-28 `NewManga-0.1.0-setup.exe`（68,611,208 bytes）。该 installer 实际 SHA-256 为 `EBAD86624A0ADD5393B8A28D258E2334C23FD13EE52F0A0F0B598A5BA9753691`，与 `build-info.json` 一致，metadata 标记 `NotSigned`。同日 `AGPL-RELEASE-1/out/` 有另两份 zip（103,492,048 / 725,499,708 bytes）。这些 metadata 来自更早的任务环境，记录的 worktree/source provenance 没有绑定当前固定基线；只证明历史产物存在。
- 历史 `package-summary-*.json` 声称 model variant 包含约 673 MB models、base variant 不含模型，许可文件摘要 byte-identical；本轮未打开或解包这些 archive 核验内容，也未重新构建它们。

## 静态交付路径观察

- `apps/desktop-avalonia/scripts/package.ps1` 默认把输出放在 workspace `task-envs/FINAL-VALIDATION-1/out`，对 stage/zip 有 `Remove-Item -Recurse -Force` 重建逻辑，并依赖已构建 sidecar。该脚本未运行。
- `apps/desktop-avalonia/scripts/publish.ps1` 默认把输出指向 repo 内 `apps/desktop-avalonia/artifacts/win-x64-single`，若目录已存在会递归删除后再 publish。它不是本轮推荐的 isolated output path，候选见 `AUDIT-12-CAND-001`。
- `install.ps1`、`uninstall.ps1`、`install-smoke.ps1` 会创建/移除安装目录；uninstall 的 `-PurgeData` 还能删除指定 DataRoot。按 Task 明确的禁止范围，本轮没有执行这些脚本、启动 setup、写注册表、安装或卸载。

## 未验证矩阵

当前 HEAD 的 `dotnet publish` / single-file output、当前 sidecar 与应用合包、模型/OCR资源完整性、NSIS installer build、安装/启动/四页可达/卸载、干净 Windows、非管理员账户、中文路径、缺失 VC/.NET runtime、升级与数据保留均 `NOT_RUN`。虽然发现历史安装包，但没有执行安装；此前 FEA 验收或历史 package metadata 不替代本 Task 对当前固定源码的交付验证。

结论：AUDIT-12=`PARTIAL`。不因开发机 build 成功或旧 artifacts 存在推导 release 可用性。后续若需安装验证，必须由新的 Task 明确释放范围与隔离安装目录；本轮保持既有授权边界不变。
