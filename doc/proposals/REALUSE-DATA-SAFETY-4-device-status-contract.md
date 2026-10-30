# 契约变更提案：设备与模型状态查询（REALUSE-DATA-SAFETY-4 AC3）

- 提案日期：2026-10-31
- 提出：DSH（Lead）
- 状态：**待裁决，未实施**
- 目标契约文件：`doc/contracts/V11R_COMMAND_CONTRACT_V1.md`
- 关联 Task：[REALUSE-DATA-SAFETY-4](REALUSE-DATA-SAFETY-4.md)，审计缺陷 MA-06 / MA-02

## 为什么需要改契约

控制台 ④「模型与设备」分区目前**没有任何可读数据源**。Host 命令注册表里不存在设备或权重状态命令，因此该分区只能如实写「Core 未暴露」，无法回答用户最关心的两个问题：

1. 我这台机器会用 GPU 还是 CPU 做检测/修复？
2. 检测模型权重到底在不在？为什么检测一提交就返回 `PROVIDER_NOT_CONFIGURED`？

第二个问题是真实用户路径上的断点：即使 Provider 配好了，权重缺失仍会让检测失败，而失败发生在**提交任务之后**，用户拿到的只是一个错误码。`PROVIDER_NOT_CONFIGURED` 这个码同时被用于「Provider 未配置」和「权重文件不可用」两种原因，用户无法区分——这本身也是 MA-02 的一半。

## 提案内容（最小面）

新增一条只读命令，不引入任何写路径：

```
cleanup 之外的新面：diagnostics.device_status
请求：{}（无参数）
响应：{
  "devices": [
    {"device_id": "<string>", "kind": "cpu"|"gpu", "label": "<string>", "available": <bool>}
  ],
  "detector": {
    "backend": "<string>",              // 例如 "manga" / "doctr"
    "weights_present": <bool>,
    "weights_label": "<string>",        // 文件名或版本标签，不含绝对路径
    "weights_source": "bundled"|"user"|"missing"
  },
  "probe_error": "<string|null>"        // 探测失败时的 typed code
}
```

约束（与既有投影风格一致，来自 review-b2 的既有裁决）：
- **不出现绝对 OS 路径**：只给文件名/标签，与 `cleanup.preview` 只给相对路径同一原则。
- 探测失败返回 `probe_error` 而不是抛异常，UI 才能区分「没有 GPU」和「探测本身坏了」。
- 该命令是**只读**，不改变任何状态，不需要 `WritesAllowed` 门。

## 协议版本

建议 `protocol.minor` 递增 1（与既往新增命令同一做法），命令本身向后兼容：旧客户端不调用即不受影响。

## 不实施时的替代方案（当前已落地）

④ 分区保持「能力待接入」的诚实标注，同时补上**能从现有数据推导的唯一事实**——检测能力是否绑定了已启用的 Provider：

- 未绑定：明确写「检测会失败并返回 `PROVIDER_NOT_CONFIGURED`」，并给出跳转 ②「Provider 与凭据」的入口；
- 已绑定：说明检测可以提交。

设备与权重部分仍然如实写「Core 未暴露」，不显示任何推测值。

即：`285ae7c`（见 Task 卡）已交付替代方案；本提案只用于把它升级为完整答案。

## 裁决点

1. 是否接受新增 `diagnostics.device_status`（只读、无绝对路径）？
2. 若接受，`weights_present` 由 Core 以什么口径判定（打包目录存在 vs 可加载 vs 哈希匹配）？建议最低标准为「文件存在且可读」，更深校验留给启动自检。
3. 是否需要在同一命令里同时返回当前生效的 `detector.backend`，以便用户理解「为什么换了权重还是失败」？

## 裁决结果

（待 DSH 与用户裁决后填写；未裁决前不得实施。）
