# P12-C1 兼容性与破坏性影响

## 协议版本

- 当前 envelope：major `2` / minor `2`；从 P16-C1 rev `2.1` 的 minor `1` 增至 `2`。
- 理由：本次只把一个原本标为 proposal 且真实 runtime 返回 `UNKNOWN_COMMAND` 的 `ImportPages` 冻结为新命令；没有改动任何已冻结命令字段、结果、错误或事件。按 §3.2 的新增 command 规则升 minor，不升 major。
- rev `2.1` 客户端不能调用新增的导入面；没有版本协商或自动迁移，导入消费者与 Core 必须显式配对到 rev `2.2`。旧命令的已冻结语义保持不变。
- 破坏性影响限定在未冻结的 proposal/实验调用：路径/URL 输入不构成受支持 wire；新契约只接受 `ImportSourceRef`。旧 raw-path/URL caller 必须停止使用并升级到受信 host grant flow。该 caller 从未获契约兼容承诺；P18 实测 `UNKNOWN_COMMAND` 也不能视作可工作的旧行为。
- rev `2.2` 是契约目标，不是运行时版本证据。当前 Python Runtime 与 Tauri host issuer 均未实现/验证，本 Task 不声称链路已通。

## 与 `ExportTargetRef` 同源对照

| 面向 | `ImportSourceRef`（§10.4，读） | `ExportTargetRef`（§10.3，写） | 共同约束 |
|---|---|---|---|
| Issuer / 交付 | 唯一 issuer 为受信 Tauri host；只在 host→Python Core 边界使用 | 唯一 issuer 为受信 Tauri host；只注入可信 `StartExport` | Host grant + Core 侧受信解析；React/WebView 不拿引用或路径 |
| Reference wire | `{grant_id, host_signature}` | `{grant_id, host_signature}` | opaque grant ID；不含/不编码路径，不在错误或普通事件泄露签名/路径 |
| Scope / 能力 | 用户显式选择的精确文件或文件夹；`ImportPages` 只读；文件夹仅直接子项 | 一个精确最终目标文件与一次 `StartExport`；只写该文件及 staging | scope 受限；拒绝伪造、越 scope 与 reparse/路径逃逸；无任意路径回退 |
| 生命周期 | 默认 300 秒；活动消费期间按 §10.1 T6 滑动续期；Host 可撤销，下一次解析立即生效 | 默认 300 秒，不滑动续期；有效调用后一次消费 | Core 校验 issuer/session、scope、有效期、撤销状态后才解析能力 |
| 副作用方向 | 只读源；源文件零写、零移、零删；创建 Managed Copy/Page 遵循 P09 | 只写授权输出与 staging；source、Managed Copy、artifact、current/pinned Revision 零写 | 引用只授权单一方向，不互换、不扩权 |

两者共同采用 §10.3 已冻结的 host-grant 形态，但生命周期与授权方向不同：写引用的一次消费规则不套用到只读导入引用；导入引用的滑动续期也不放宽 ExportTargetRef。Runtime 实现不得因共享 resolver 而混用 scope。

## Runtime 授权影响

§12 新增只读导入来源 grant 的 Python IPC Runtime 授权，并把写入面精确限定为 Core service/assembly、既有 resource-channel grant resolver 与 `tests/core/**`。导入 use case、Library service、SQLite adapters 为只读复用面。该授权不包括 React/WebView、Tauri command/host issuer、Rust、QML/PySide6/Legacy、Schema/migration、依赖、打包、其他产品行为或 allowlist 外代码。Host issuer 需独立 Task 授权。

运行风险仍由后续验收处理：`ImportSourceRef` issuer/签名校验、open-then-verify、撤销和过期拒绝、零副作用、PDF 预检、Managed Copy 顺序、Unicode/重复/中断，以及 2.2 客户端/Core 配对均未在本契约 Task 执行。
