---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58
turn_id: turn_069920c6-4029-46a9-981f-d59b4ac5d7aa
decision: ALLOW_RECORDED_RUNTIME_REBINDING_WITH_REPRO_GATE
---

# 释放 Addendum 2：冻结脚本安全调用

两份 PIN-POLICY-1 脚本的默认输出会写历史路径，delta 还硬编码 `948d73…` 基线；禁止在 main 运行，也禁止按默认方式覆盖历史输出。ZCode 允许只在固定 base 隔离 clone 以 `importlib` 加载原字节脚本，`sys.dont_write_bytecode=True`，不覆写由脚本位置派生的 `ROOT`，不 monkey-patch 解析、判定或 hash 函数。

inventory 只重绑定 `OUT` 到本 Task 新文件 `pin-inventory-2df8db7a.json`；delta 只重绑定 `BASELINE` 到入库 e9f inventory、`EXPECTED_BASELINE_HEAD` 到 `e9f7bb1b48c885cb329848d2d3591e145ff3d229`、`CURRENT` 到新 inventory、`OUTPUT` 到 `pin-inventory-delta-e9f7bb1b-to-2df8db7a.json`。这是**运行时参数覆盖，计算逻辑为原脚本字节，不是默认行为运行**。

正式测量前必须先做 delta 复现锚：在 clone 使用默认 948d/e9f 输入，仅重绑定 OUTPUT 到本 Task 新文件，结果须与入库 `pin-inventory-delta.json` 逐字节一致（历史 SHA-256 `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`）；不一致立即停止。clone 先核对 clean、两个脚本和三份输入 JSON 的 blob ID/SHA；run log 记录脚本前后 SHA、wrapper SHA、绑定映射、输入输出 SHA、HEAD、Python/Git/autocrlf 与每步 EXIT。任何路径或输入漂移停止并交 ZCode。可选 e9f 环境语义重跑未执行时记 NOT_RUN。
