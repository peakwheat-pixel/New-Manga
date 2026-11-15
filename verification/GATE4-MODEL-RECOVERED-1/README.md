# GATE4-MODEL-RECOVERED-1：`yolo11s-seg.onnx` **一直在仓库里** —— 我"需用户提供"的判断是错的

基线 `ffeaaa4f9`。由**独立复核（agent-8）**发现，我随后自己复核确认。

## 1. ★ 我的错误（第 3 次同模式）

我此前在 `GATE4-REMAINING-1` 与 `BLOCKED-ITEM-AUDIT-1` 里写：
`yolo11s-seg.onnx` 是"训练产物，**工作区确实不存在**（全盘搜索过）"，因此**标为 BLOCKED、需用户提供**。

**这个判断是错的。**

## 2. 文件一直在仓库里

```
apps/desktop/src-tauri/target/debug/resources/core-sidecar/models/detector/yolo11s-seg.onnx
apps/desktop/src-tauri/target/release/resources/core-sidecar/models/detector/yolo11s-seg.onnx
```

（旧 Tauri 线的构建产物；`target/` 被 `.gitignore` 忽略，所以 `git grep` / 索引搜索**看不到** ——
这正是我"搜索过"却失败的**具体原因**。）

**实测**：

```
LEN    = 40824255
SHA256 = 944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d
```

与 `src/infrastructure/providers/detection_sfx.py:131` 的 `SFX_WEIGHTS_SHA256`
**逐位一致** ⇒ **字节可信**（该 pin 本就是 fail-closed 校验）。

## 3. 产品确实用它（不是 rtdetr）

`detection_sfx.py:130` `SFX_WEIGHTS_FILENAME = "yolo11s-seg.onnx"`；
默认路径 `<data root>/models/detector/yolo11s-seg.onnx`（`:53`）；`SFX_DEFAULT_IMGSZ = 1024`。

新 sidecar 的 `models/detector/` 原本**只有 `rtdetr-v2-fixed.onnx`（163.7 MB）**，
那是**另一个用途**，**不能替代** SFX 检测。

## 4. 已修复（复制 + 三重验证）

复制到新 sidecar 的 stage 目录：

```
apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/models/detector/yolo11s-seg.onnx
```

**三重验证**：

| 验证 | 结果 |
|---|---|
| 复制后 SHA-256 | `944e8114…acd418d` —— **与 pin 逐位一致** |
| 长度 | `40824255` —— 与源一致 |
| **onnxruntime 真实加载** | **`LOADED OK`**（ort 1.24.4） |

加载后的 shape：

```
inputs : [('images', [1, 3, 1024, 1024])]      ← 与 SFX_DEFAULT_IMGSZ = 1024 一致
outputs: [('output0', [1, 40, 21504]), ('output1', [1, 32, 256, 256])]
```

**⇒ 不只是"文件在位"，是模型**真的能被推理引擎加载**且输入尺寸与产品默认匹配。**

## 5. 对 Gate 条件 4 的影响

| 项 | 原状态 | 现状态 |
|---|---|---|
| `yolo11s-seg.onnx` | **BLOCKED（需用户）** | ✅ **已就位并验证可加载** |
| 签名证书 | BLOCKED（需用户） | **仍 BLOCKED** |
| `reader` 页 | NEEDS_INTERACTION | **仍需 F11** |

**⇒ 条件 4 的阻塞从 2 项实物降为 1 项（签名证书）。**

## 6. 未做（诚实）

- **未跑端到端的 `resolve_page_resource` 检测路径**（需要完整 sidecar 启动 + 一张真实页面 +
  检测后端可用）。本卡只验证到"模型可加载 + 尺寸匹配"。
- **未重打安装包**。`build/sidecar` 是构建产物，`package.ps1 -WithModels` 会从这里取；
  下次打包会把模型带上，但**本轮没打包**。
- 未验证 GPU/DML 路径（本卡走 `CPUExecutionProvider`）。

## 7. 这是第 3 次同模式错误

| # | 项 | 我的错误判断 | 实际 |
|---|---|---|---|
| 1 | `L-F1-3` | "需真人定义压测口径" | 裁决只说要夹具与环境，夹具我能造 |
| 2 | `E-9` | "需新增持久化映射" | 路径就在 `roots[0]`，一个判别分支 |
| 3 | **`yolo11s-seg.onnx`** | "全盘搜索过，不存在" | **文件在 `target/` 里，被 gitignore 所以搜不到** |

**共同点：我都在"搜索范围不完整"或"没读关键一行"的情况下，下了"做不了/需人"的结论。**
**三次都是外部（ZCode）替我抓住的。**
