# P02 r8 Codex 路线校验器独立复核

Reviewer：/root/review_p02_r7（只读 follow-up）

## 结论

approved。对最新 verify_plan.py 与 route-validator-mutation-probe.py 差异未发现新增问题；前次指出的 P3 已闭合。

## 复核范围

- 例外集合严格等于唯一授权路径：apps/desktop/frontend/e2e/workbench_driver_protocol.ts。
- validator 的 unexpected_p01_product_changes() 对变更路径逐项过滤；未豁免的路径仍会被保留并触发 P01 产品代码差量失败。
- 探针直接调用生产过滤 helper，验证仅有 E2E driver 时放行、再加入 apps/desktop/frontend/src/App.tsx 时拒绝。
- 已读取两项脚本的 Codex EXIT=0 日志；原有两种路线状态漂移拒绝探针也仍为 PASS。

## 边界

本改动用于避免 P01 宽目录守卫误报 P02 frozen allowlist 已授权的一个 E2E 测试 driver。没有扩大 P02 Owner allowlist，也没有修改 P01 基线或历史 inventory。Reviewer 未改文件、未自行重跑脚本、未运行产品测试或构建；执行结论来自归档的 Codex 日志。