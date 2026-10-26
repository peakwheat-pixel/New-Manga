# ADR-0002：资源通道安全模型 v2（AD-002 前置件 P3）

Status: ACCEPTED（S5 执行前需回归验收） · Date: 2026-10-26 · Owner: DSH
依据：[AD-002](../../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、`apps/desktop/src-tauri/src/resource_protocol.rs`（现状）、`core_bridge.rs`（wire v1）、DISPLAY-PERF 基线 AC2

## 背景

现状（旧壳）：WebView 只能经 `m2res` 自定义 scheme 取图，因此每个 chunk 请求都要：Core 解析授权 → 打开文件 → **顺序读完整文件算 SHA-256** → 只返回 16MiB 一块；响应 `Cache-Control: no-store`；前端逐块拼 Blob。实测单页 657KB 端到端 22.9ms，其中整文件哈希 4.65ms（占 20.4%）；大页线性放大。

新壳（Avalonia）**没有 WebView**，图片由 Host 直接读文件/内存映射后交给 UI 绘制 → `m2res` scheme、CORS、`no-store` 在架构上不再需要。但**安全语义不能随之丢失**。

## 必须保留的安全目标（不可协商）

1. **受限根**：只能读 `derived` / `managed` 两类根内的文件；`user-source` 不可服务。
2. **containment**：从已打开句柄重导最终路径并校验仍在根内（防 reparse/junction 逃逸）。
3. **文件身份**：volume serial + file index 与 issue 时一致。
4. **大小上限**：单文件 ≤256MiB（沿用）；单块 ≤16MiB（或由 tile 尺寸取代）。
5. **内容完整性**：**等长原地重写必须被拒**（F-02 教训：mtime 粒度不可靠）。
6. **授权生命周期**：grant 的 revoke / expiry 必须仍然生效。
7. **路径不泄露**：UI 不得看到 OS 绝对路径、digest、revision 指纹。

## 决策

### D1 传输形态

- Core 生成/交付 **tile 文件**（或整页派生图）到 `derived/`，由 Host 直接读取；**不再提供 HTTP scheme、不再有 CORS**。
- UI 只持有资源不透明句柄 + 展示尺寸；路径仅在 Host 内部存在。

### D2 完整性校验策略（取代"每请求全文件 SHA-256"）

| 时机 | 校验 |
|---|---|
| issue（签发） | Core 返回 grant：`{opaque_id, size, identity(volume_serial,file_index), digest}` |
| 每次打开 | identity + size + containment（从句柄重导路径） |
| 首次打开该 grant 的文件 | **一次全量 SHA-256**（覆盖读并捕获同一次读，防 TOCTOU） |
| 后续 tile 读取 | **per-tile SHA-256**（Core 写 tile 时计算并随 grant 下发清单）；Host 校验所读 tile 的摘要 |
| 撤销/过期 | 每次读取前查询 Core 授权状态（可短 TTL 缓存 ≤1s，且 revoke 必须能打断缓存——由 Core 主动失效事件驱动） |

- **禁止**：以 mtime 作为完整性短路（F-02 已证不可靠）。
- 若某类资源无法提供 per-tile digest（例如外部派生图），则该类退化为「每次访问全量校验」，并在 Task 记录例外。

### D3 允许删除的旧机制（仅当 D2 验收通过）

- `m2res` scheme、CORS 头、`Cache-Control: no-store`、**每请求**全量哈希 → 删除。
- 保留：grant 签发/撤销语义、identity/size 校验、containment、资源大小上限、不泄露路径。

### D4 回归验收（S5 关闭前必须全绿）

1. 等长原地重写 → **拒绝**（win32/typed error）。
2. revoke 后读取 → 拒绝；expiry 后读取 → 拒绝；revoke 打断 1s 缓存。
3. 越界路径 / junction / reparse point → 拒绝。
4. 篡改 tile（改字节、保持大小）→ per-tile 摘要校验失败 → 拒绝。
5. 身份变化（替换文件）→ 拒绝。
6. 大页性能：单页冷加载 ≤60ms、哈希开销占比 ≤10%（G5）。

## 后果

- 图片通道成本预计显著下降（去掉每请求全量哈希 + 去掉 Blob 拼装），与 AD-002 §3.5 体积预算协同。
- S2 阶段仍用旧 stdio 通道；S5 切到 tile 通道并跑 D4 全绿后才删除旧机制。
- 若 D4 任一项无法通过，S5 不得删除旧机制，改为保留旧通道作为回退路径并记录。
