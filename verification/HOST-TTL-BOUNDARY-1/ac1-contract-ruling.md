# AC1 契约边界裁决

日期：2026-10-16。裁决冻结时间：生产代码修改前。

## 权威条文

- [M2-C1_TYPED_IPC_CONTRACT.md §5.7](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md#57-hostcontrol-host-only-grant-registration--revoke-host-issuer-1-c1) L456：`RegisterImportSource` 复用既有私有 seam；grant 的 scope、签名输入和“有效期上限”沿用 §10.3/§10.4，本节不另行定义。
- 同契约 §5.7 L476：注册时已过期或超过既有有效期约束的 grant 使用 `REF_EXPIRED`，沿用 §10.3/§10.4。
- 同契约 §10.4 L826：导入引用默认 TTL 为 300 秒，并在活动消费期间滑动续期；该条没有要求 host 必须在签发时刻加满 300 秒，也没有把此默认值定义成精确的 host 签发上限。

## HOST-ISSUER-1-C1 rev 2.3 对照

- 契约 rev 2.3 L3、L17、L23 将修订范围限定为 HostControl 注册通道等内容，明确既有 P12 `ImportPages` payload/result/error、`ImportSourceRef` 字段及 `REF_*` 语义不变。
- [coverage-matrix.md](../../verification/HOST-ISSUER-1-C1/coverage-matrix.md) L14、L22–23 对照 §10.3/§10.4 的既有 expiry/ref 语义，并说明 P12 `ImportPages` wire 不变；HOST-ISSUER-1-C1 没有给导入 grant 增加精确 TTL 上限。

## 裁决与实现约束

裁决 AC1(b)：契约给出导入引用的 300 秒默认 TTL 和滑动续期语义，但未定义 host 必须取满 300 秒或精确 `expires_at` 上限。现有 Core 接受不超过 `now + 300` 的注册值；host 恰取满该窗口会把允许区间压成零裕量。按契约修 host 的取值为 `host_build_time + 299.0`，留下明确 1 秒裕量。Core 的 `expires_at <= now` 过期拒绝、`expires_at > now + 300` 超窗拒绝和所有来源/只读/session/签名校验保持不变。

本裁决没有通过两侧试数得到。后续测试须分别断言正常成功、Core 时钟等于/略早于 host 时刻仍成功、确实过期拒绝及确实越过 300 秒窗口拒绝。

## Export grant 裁决补充（2026-10-16）

本节是 DSH R1 I1 的修复记录。契约条文在 export issuer 修改前已对读；本段文字在导出测试完成后补录。

- §5.7 L456/L476 将 export grant 的有效期上限与注册拒绝语义交回 §10.3；HostControl 没有另订精确签发值。
- §10.3 L814 将 export ref 生命周期规定为默认 300 秒、不滑动续期、一次有效调用后消费；它没有要求 host 必须签发恰好 300 秒，也没有把默认值定义成精确的 host 签发上限。
- 因此 export 侧沿用同一 AC1(b) 裁决：`build_export_grant` 使用 `host_build_time + 299.0`，留下 1 秒裕量；Core `expires_at <= now` 和 `expires_at > now + 300` 拒绝保持不变。单目标写授权、单次消费及不续期语义不变。

Export 签名仍使用 Rust `{expires_at:.6}` 与 Python `{expires_at:.6f}`；没有更改签名规范化精度或任何授权字段。
