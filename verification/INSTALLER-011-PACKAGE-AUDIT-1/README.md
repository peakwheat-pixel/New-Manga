# INSTALLER-011-PACKAGE-AUDIT-1：0.1.1 包级静态核实（零风险）—— 发现**交付包确实缺 SFX 权重**

基线 `dd771dd25`。执行 `INSTALLER-011-ASSERTION-PLAN-1` §5 提出的零风险替代。

## 1. setup.exe 的 sha256 与 build-info **完全一致**

| 项 | 实测 / 记录 |
|---|---|
| 路径 | `task-envs\INSTALLER-MATRIX-1\out2\NewManga-0.1.1-setup.exe` |
| bytes | **652,107,016**（621.9 MB） |
| **实测 sha256** | `0c0415993b6deab7027baee941f683487a263a0e0fb65c2cd16040ee4c358f06` |
| **build-info 声称** | `0c0415993b6deab7027baee941f683487a263a0e0fb65c2cd16040ee4c358f06` |
| 一致 | ✅ **逐位一致** |

## 2. `build-info.republished.json` 自洽

```
version            = 0.1.1
installer.bytes    = 652107016 (621.9 MB)
installer.sha256   = 0c041599…58f06
installer.authenticode_status = NotSigned      ← 确认 unsigned
installer.product_version     = 0.1.1
stage.file_count   = 1037
stage.bytes        = 889353540 (848.15 MB)
stage.manifest_sha256 = 58b54b04…
stage.version_json = {version: 0.1.1, variant: base, license: GPL-3.0-or-later}
toolchain.makensis = v3.13
generated_at_utc   = 2026-11-14T21:02:05.2761083Z
```

**⇒ 包身份、大小、签名状态、stage 指纹全部自洽。**

## 3. ★ stage 的 `VERSION.json` 与**已安装的 exe** 交叉一致

`stage/VERSION.json` 的 `app_build`：

```
exe_sha256 = a3ec2133b5da3f619b752c818371ba54867b4c150fdba65b8c22d8b17f739230
exe_bytes  = 99554850
repo_head  = 71cecb95a10c42ffe02d1396ab065e1fc9c43ca9
```

**已安装的 exe 实测**：`ProductVersion = 0.1.1+71cecb95a10c42ffe02d1396ab065e1fc9c43ca9`、
`bytes = 99554850`、`sha256 = a3ec2133b5da3f61…`

**⇒ stage 声明的 exe 与**机器上装的 exe 是同一个**（sha256 前 16 位 + 字节数 + head 全对）。**

## 4. ★★ 关键发现：**交付包确实缺 `yolo11s-seg.onnx`**

**已安装目录**（`%LOCALAPPDATA%\Programs\NewManga`）实测：

| 文件 | 大小 |
|---|---|
| `app\core-sidecar\models\detector\rtdetr-v2-fixed.onnx` | 163.7 MB |
| `app\core-sidecar\models\ocr\manga-ocr-onnx\decoder_model.onnx` | 112 MB |
| `app\core-sidecar\models\ocr\manga-ocr-onnx\encoder_model.onnx` | 327.5 MB |
| **`yolo11s-seg.onnx`** | **count = 0** ❌ |

**且 stage 的 `VERSION.json` 已经诚实地自陈了这件事**：

```
sidecar_build.known_limitation =
  "sfx weights (yolo11s-seg.onnx) are NOT present, so sfx_detect_probe fails closed
   with PROVIDER_NOT_CONFIGURED; the other four entry points are intact"
```

**⇒ 也就是说：**
1. **0.1.1 交付包在打包时就没有 SFX 权重**；
2. **它不是静默失败** —— `VERSION.json` 明确写了 `fails closed with PROVIDER_NOT_CONFIGURED`，
   且 `models` 字段还写了一段自我更正：
   > "this field replaces the previous 'none (no model weights in this variant)' claim, **which was WRONG for this build**"
3. **我此前恢复 `yolo11s-seg.onnx` 只补到了 `apps/desktop-avalonia/build/sidecar/...`（源码构建链），
   /NOT/ 补到已安装的 0.1.1 包**。

## 5. 对条件 4 的准确影响

| 项 | 状态 |
|---|---|
| 包身份/大小/哈希自洽 | ✅ **可复核**（本卡） |
| stage ↔ 已安装 exe 一致 | ✅ **可复核**（sha256 + head + bytes） |
| **SFX 权重是否随包交付** | ❌ **未交付**（`VERSION.json` 已自陈 `fails closed`） |
| **要修复它** | **需重新打包（含 yolo11s-seg.onnx）+ 重装** —— 我已在 `GATE4-MODEL-RECOVERED-1` 把权重放进了源码构建链，但**没有重打包** |

**⇒ 条件 4 的准确表述**：
**交付的 0.1.1 包在 SFX 权重上是"明确声明的降级"**（`fails closed`，其余四个 entry point 完好），
**不是"包坏了"**；要让它完整，需**重打包 + 重装**。

## 6. 与 `GATE4-MODEL-RECOVERED-1` 的关系（必须说清）

我在 `GATE4-MODEL-RECOVERED-1` 里把 `yolo11s-seg.onnx` 复制到了
`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/models/detector/` 并验证可加载。

**那只影响"源码构建的 sidecar"**，**不影响已安装的 0.1.1 包**，也没有触发重新打包。

**⇒ 我此前的表述"模型已就位并验证可加载"容易让人以为"交付包也完整了"。**
**准确说法是**：**源码构建链已可加载；已安装的 0.1.1 包仍缺，`VERSION.json` 已自陈。**

## 7. 未做

- **未重打包**（`package.ps1 -WithModels`），也未重装 —— 那会改动用户机器。
- 未核 `manifest-summary.json` / `smoke-singlefile.json`（**这两个文件在 `INSTALLER-MATRIX-1/` 下不存在**；
  实际存在的是 `manifest-singlefile.json`）。
- 未核 `manifest-singlefile.json` 的内部一致性（本轮聚焦 sha256 ↔ build-info ↔ stage ↔ 已安装 exe 这条链）。
