# 素材许可核查：`test-materials` 的 147 个对象

**产出**: 2026-10-20 · **性质**: 只读核查 · **结论**: **可在私有工作区内用于测试，但不得复制入 Git**

## 一、查了什么

| 位置 | 内容 | 有许可字段？ |
|---|---|---|
| `test-materials/manifest.json` | 147 对象 | **否**（只有 `object_id` / `path` / `sha256` / `size_bytes`）|
| `data-registry/registry.json` | **3089** 对象 | **否**（见下）|

**两次都没找到「license」字段。0 / 3089。**

## 二、但 registry 里有 policy，它管这件事

`data-registry/registry.json` → `policy`，原文：

> **Private workspace storage. Preserve per-source attribution and terms;
> unknown rights mean no redistribution. Objects are content-addressed and
> immutable; edit only a task-local copy.**

**三个要点**：

| 条款 | 含义 |
|---|---|
| `Private workspace storage` | 这是**私有工作区**存储，不是发布物 |
| `Preserve per-source attribution and terms` | 保留每源归属与条款 |
| **`unknown rights mean no redistribution`** | **权利不明 = 不得再分发** |
| `edit only a task-local copy` | 只能改 task 本地副本 |

## 三、registry 里有什么可供归属

每个对象的 `canonical_source` 是一个结构化记录，含：

```json
{
  "worktree_name": "M2-KO-TILE-CALIB-zcode",
  "task_id": "M2-KO-TILE-CALIB",
  "source_relative_path": "..."
}
```

**所以「用途 / 来源 Task」是有记录的。** `WORKSPACE_GOVERNANCE.md` 要求的
「Task/用途」这一项**满足**。

**但「获取时间 / 来源 URL / 许可」这三项在 147 个对象上都没有记录。**

## 四、因此的可做与不可做

### 可以做

**在私有工作区内使用这些图片做检测测试。**
理由：policy 说的是「不得**再分发**」，而**在 `G:\CODEX\New Manga.workspace\` 内部
读取一张图跑一次检测，不是再分发**。

**且 147 个对象里 145 个的 `canonical_category` 是 `test-materials`**
——它们的登记用途**本来就是测试素材**。

### 不可以做

**把图片复制进 `G:\CODEX\New Manga\`（Git 仓库）。**

理由：那会构成**把私有工作区素材提交为版本化内容**，
即 policy 禁止的 redistribuion。**这与 `WORKSPACE_GOVERNANCE.md` L83 一致**：

> Task worktree 可以包含代码和轻量 manifest 引用，
> **不得包含数据集、模型 checkpoint 或大体积测试漫画的私有副本**。

## 五、对 `DETECT-TILING-1` 的具体约束

**证据应当引用 `test-materials` 的路径与 SHA-256，而不是把图片复制进仓库。**

| 项 | 做法 |
|---|---|
| 样本引用 | 写 `test-materials/objects/sha256/<hash>` 路径 + `sha256` |
| 证据 | 记录**尺寸、像素数、解码峰值内存、检测结果摘要**，不入库原图 |
| 复核方式 | 第三方凭 `sha256` 在 `test-materials` 中定位同一对象 |

**这与 `CANONICAL` / `SOURCE_PIN` 的证据二分法一致**：**pin 可以指向仓外路径**，
只要路径与 hash 可解析。

## 六、一个必须指出的缺口

**`WORKSPACE_GOVERNANCE.md` L79 要求每个导入对象在 master registry 中「至少包含」**：

> 稳定 `object_id`、SHA-256、字节数、canonical path、所有源文件相对路径与原 worktree、
> **Task/用途、获取时间、来源 URL 或**（原文此处截断）

**实况**：
- `object_id` ✓、`sha256` ✓、`size_bytes` ✓、`target_path` ✓、`canonical_source.task_id` ✓
- **`获取时间` ✗**
- **`来源 URL` ✗**
- **`许可` ✗**

**所以 registry 对该条款是部分满足的。**

**这不是 `DETECT-TILING-1` 的阻塞**（policy 允许私有使用），
**但如果将来要把任何一张图作为「已许可素材」对外引用，这几项缺失就是真缺口。**

**建议**：另立一个「素材许可补录」Task，而不是让每个用到素材的 Task 各自撞一次。

## 七、明确未做

- 未修改 `test-materials` 或 `data-registry`。
- 未获取任何新素材。
- 未把任何图片复制进仓库。
- **未核实 `获取时间/来源URL/许可` 是否记录在别处**——本文件只核了这两个文件与
  `WORKSPACE_GOVERNANCE.md`。**可能还有其他登记处，未查。**
