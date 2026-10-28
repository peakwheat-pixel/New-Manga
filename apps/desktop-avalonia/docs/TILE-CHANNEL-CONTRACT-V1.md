# Tile Channel Contract v1（S5-B 冻结）

状态：**FROZEN（S5-B，2026-10-27）**。本契约定义 Python Core → C# Host 的 tile 生成与下发，以及 Host → UI 的可见面。
本卡不改 Core；Core 侧落地在独立的 S5-B/Core 任务中，实现时不得改变本文件字段语义；如需变更必须新版本并重新验收。

## 1. Core → Host：`tile` grant manifest

Core 生成派生 tile（或整页派生图切片）到受控目录，并把 manifest 交给 Host。Host 只接受本结构：

```json
{
  "resource_id": "page:<opaque-id>",
  "revision": "<revision-fingerprint>",
  "size": 12345678,
  "absolute_path": "<host-visible derived file>",
  "allowed_root": "<host-visible derived root>",
  "tiles": [
    { "index": 0, "offset": 0, "length": 262144, "sha256": "<64-hex>" }
  ],
  "ttl_ms": 300000
}
```

规则：
- `tiles` 覆盖整页，`offset+length ≤ size`，`index` 从 0 连续递增，不允许重复。
- 每个 tile 必须携带 64-hex SHA-256；Host **不得跳过** digest 校验。
- `absolute_path` 必须在 `allowed_root` 内；Core 不应下发 junction/reparse/UNC 路径，Host 仍会拒绝。
- 授权默认 TTL 由 manifest 给出（Host 上限 5 分钟）；revoke 由 Core 事件驱动。

## 2. Host → UI：只读视图

```json
{
  "handle": "<opaque 32-hex token>",
  "resource_id": "page:<opaque-id>",
  "revision": "<revision-fingerprint>",
  "size": 12345678,
  "tile_count": 48,
  "issued_at": "<ISO-8601 UTC>",
  "expires_at": "<ISO-8601 UTC>"
}
```

读取结果只返回 `index`、`length`、`bytes`、`sha256_verified`。**UI 永远不接触 OS 路径、volume/file identity 或 per-tile digest。**

## 3. 安全不变量（Host 强制）

1. issue 时捕获 size、volume serial + file index、per-tile digest；拒绝越界/UNC/junction/reparse。
2. read 时从已打开句柄重导最终路径并再次校验 containment 与 reparse；校验 identity、size、tile digest（常量时间比较）。
3. 等长原地重写（含恢复 mtime）必然因 digest 失败被拒：**不得依赖 mtime**。
4. 同路径文件替换 → `TileIdentityMismatch`。
5. 授权缓存 TTL ≤1s；revoke 事件同步失效缓存；expiry 到期拒绝。
6. typed error 码：`TilePathOutsideRoot`、`TilePathReparse`、`TileIdentityMismatch`、`TileSizeMismatch`、`TileDigestMismatch`、`TileGrantRevoked`、`TileGrantExpired`、`TileIndexOutOfRange`、`TileManifestInvalid`、`TileIoFailure`。

## 4. 版本与兼容

- v1 只支持整页派生文件 + per-tile digest；不支持外部 URL、HTTP scheme、CORS。
- Host 缓存策略、digest 计算时机见 S5-A/S5-B Handoff 的 Record Decision；实现变更不得放宽任何校验。
