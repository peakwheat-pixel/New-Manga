# manga 检测器权重安装 SOP（ogkalu/comic-text-and-bubble-detector @ 16e8a622）

> 适用范围：Windows / React + TypeScript / Tauri / Python Core 架构（AD-001）下
> manga 文本检测器（`src/infrastructure/providers/detection_manga.py`，M2-PROD-DETECT-1）
> 的权重获取、校验与安装。归属 slice：M2-MANGA-WEIGHTS-SOP（GOAL.md T2）。
> 唯一脚本入口：`verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py`
> （下称「fetch 脚本」），stdlib-only，无 torch/transformers 依赖。

## 0. 背景与 pin 权威

生产 adapter 在运行时**永不下载**权重：`detection_manga.py` 以
`local_files_only=True` 从本地目录构建模型，目录或文件缺失是 typed
`PROVIDER_NOT_CONFIGURED`，哈希不符是 typed `PROVIDER_FAILED`，绝不静默回退、
绝不触网。

快照身份与逐文件 SHA-256 pin：

| 文件 | SHA-256 pin |
| --- | --- |
| `model.safetensors` | `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d` |
| `config.json` | `b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072` |
| `preprocessor_config.json` | `7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca` |

- 模型：`ogkalu/comic-text-and-bubble-detector`（HuggingFace，RT-DETR-v2，
  Apache-2.0），pinned revision `16e8a622`。
- **pin 权威**：`src/infrastructure/providers/detection_manga.py` 中的常量
  （`MANGA_*_SHA256`）是唯一权威。fetch 脚本内的同名常量只是部署便利副本，
  两者不一致时脚本按 fail-closed 原则直接失败——先改代码 pin（走 re-pin
  slice），再同步脚本。
- 权重永不入 Git 库：默认落在数据根（`%LOCALAPPDATA%` 下，仓库外）或安装
  目录；任何 `--dest` 用法都不应把权重放进仓库工作区。

目标目录布局（与生产解析顺序一致，见
`bootstrap/core_assembly.py` 的 `_resolve_detector_weights_path`）：

1. env `NEWMANGA_DETECTOR_WEIGHTS`（目录 override）>
2. `<数据根>/models/detector/ogkalu-comic-text-and-bubble-detector/` >
3. 发布形态安装包内置副本（exe 旁 `models/detector/...`，仅 frozen 生效）。

数据根解析（`bootstrap/core_assembly.py::default_data_root`）：
`NEWMANGA_DATA_ROOT` > `%LOCALAPPDATA%`（无则 `$HOME`）下的 `New Manga` 目录。
即默认权重目录为
`%LOCALAPPDATA%\New Manga\models\detector\ogkalu-comic-text-and-bubble-detector\`。

## 1. 场景 A：源码 venv（跑 fetch 脚本）

适用：从源码运行应用 / 跑真实检测相关测试与实验的开发机。

前置条件：

- Python 3.10+（任意 venv 均可，fetch 脚本本身不需要 torch/transformers；
  只有跑真实检测时才需要 ML runtime）；
- 网络可达 `huggingface.co`（代理环境见场景 D）。

步骤（PowerShell 示例）：

```powershell
# 1) 确认数据根（默认 %LOCALAPPDATA%\New Manga；设置了 NEWMANGA_DATA_ROOT 则以它为准）
echo $env:NEWMANGA_DATA_ROOT

# 2) 拉取 + 逐文件 SHA-256 校验（幂等：已验证的文件自动跳过）
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py"

# 3) 复核（离线校验，不触网）
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only
```

期望输出：三行 `already fetched and verified:` / `verified and installed:`，
`--verify-only` 以 `all 3 pinned files verified` 结尾且退出码 `EXIT=0`。

自定义目标目录（例如本地快照/共享缓存）：

```powershell
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --dest "D:\weights\ogkalu-comic-text-and-bubble-detector"
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only --dest "D:\weights\ogkalu-comic-text-and-bubble-detector"
```

行为约定：

- 已存在且 hash 符合 → skip（幂等，重复执行安全）；
- 已存在但 hash 不符（截断/损坏/被替换）→ 自动重新下载，新字节校验通过才
  覆盖旧文件；
- 下载失败或 hash 持续不符 → 退出码非 0 并点名失败文件；hash 持续不符视为
  供应链事件，登记并上报，不得手工放行。

## 2. 场景 B：发布包（权重随包，零操作）

适用：NSIS 安装包/便携发布的最终用户。

- 发布构建把 pinned 权重快照随包打进安装目录
  （`<安装目录>\models\detector\ogkalu-comic-text-and-bubble-detector\`，
  M2-PROD-DETECT-2 集成产物：171MB 权重经 sha256 校验复制 + whole-dir
  Tauri resource + 构建期闭包断言）。
- frozen 进程的权重解析顺序（`_resolve_detector_weights_path`）：
  `NEWMANGA_DETECTOR_WEIGHTS` > 数据根 → **安装包内置副本**。数据根没有
  权重时，应用直接使用包内副本——**最终用户零操作**。
- 验证方法（可选，离线）：

```powershell
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only --dest "C:\Program Files\NewManga\models\detector\ogkalu-comic-text-and-bubble-detector"
```

- 注意：包内副本由构建管线以 pin 校验复制（`verification/M2-PROD-DETECT-2/`
  集成记录），随包分发后仍可用 `--verify-only` 抽查；若不符按损坏安装处理
  （重装/重下发），不要手工替换文件。

## 3. 场景 C：发布形态换权重（数据根覆盖包内）

适用：运维需要让某台机器使用与包内不同的权重目录（例如集中缓存盘、
离线机房预置），或把源码机已验证的快照搬到发布机。

数据根覆盖法（推荐，优先级高于包内副本）：

```powershell
# 1) 目标机器上把 pinned 快照放到数据根布局（三文件齐全，目录名固定）
robocopy "D:\cache\ogkalu-comic-text-and-bubble-detector" "%LOCALAPPDATA%\New Manga\models\detector\ogkalu-comic-text-and-bubble-detector"

# 2) 离线校验
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only

# 3) 启动应用即生效（数据根候选存在时优先于包内副本）
```

env override 法（临时/单进程）：

```powershell
$env:NEWMANGA_DETECTOR_WEIGHTS = "D:\cache\ogkalu-comic-text-and-bubble-detector"
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only --dest "D:\cache\ogkalu-comic-text-and-bubble-detector"
```

- 纪律：无论哪种方式，放入目录的文件必须先通过 `--verify-only` 三 pin 校验；
  校验不过的目录宁可不放，让应用以 typed `PROVIDER_NOT_CONFIGURED` fail-closed。
- `NEWMANGA_DETECTOR_WEIGHTS` 对 manga 是**目录**语义；指向 `.pt` 文件是
  docTR 时代的误配置，fetch 脚本会拒绝并以退出码 2 提示（真实检测路径同理
  失败，见 `detection_manga.py` 的配置指引）。

## 4. 场景 D：代理环境

fetch 脚本使用 stdlib `urllib` 默认 opener，**原生尊重**
`HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` 环境变量（脚本启动时打印当前生效
的 proxy 列表，便于审计）。HuggingFace `resolve` 会 302 跳转到 CDN，默认
handler 自动跟随，代理对跳转后的请求同样生效。

```powershell
# 本机代理示例（CLash 类，端口 7890）
$env:HTTP_PROXY  = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py"
```

注意事项：

- 变量值需要 scheme 前缀（`http://...`），只写 `127.0.0.1:7890` 不生效；
- 只需代理 HF 时可临时设置，跑完 `Remove-Item Env:HTTPS_PROXY` 清理；
- 企业代理若做 TLS 中间人（自签根证书），`urllib` 会报证书错误——把企业根
  证书加入 Windows 证书库后用系统 Python 通常可解；不应通过关闭校验绕过；
- 完全离线环境：不要硬跑下载路径。用有网机器执行场景 A，然后把已通过
  `--verify-only` 的目录整目录拷贝到目标机（场景 C），目标机只做
  `--verify-only` 复核。

## 5. pin 漂移 / 换 revision 流程

- `--source-revision` 默认即 pinned `16e8a622`；显式给**其他** revision 时，
  脚本进入 UNVERIFIED 模式：必须同时给 `--dest`（禁止落入默认生产布局），
  下载后不做 pin 对比、只报告实际 SHA-256 并全程标注 UNVERIFIED。
- 任何 revision 升级 = 一次正式 re-pin slice：在新 revision 快照上重跑验收
  （C4 同款 evidence）→ 更新 `detection_manga.py` 的 `MANGA_HF_REVISION` 与
  三 pin → 同步 fetch 脚本副本常量与本 SOP 表格。绝不允许跳过 re-pin 直接
  把新 revision 文件放进生产权重目录。

## 6. 故障排查速查

| 现象 | 处置 |
| --- | --- |
| `--verify-only` 报 `weights directory ... does not exist` | 先跑下载（场景 A），或 `--dest` 指错目录 |
| `MISSING` / `sha256 ... != pinned` | 重跑下载路径自动重下；持续不符按供应链事件登记上报 |
| 下载 429/403/超时 | 配置场景 D 代理后重试；HF 偶发限流等几分钟 |
| `NEWMANGA_DETECTOR_WEIGHTS` 报 file/suffix 错误 | 该 env 对 manga 必须是目录；`--dest` 显式指定或清掉该变量 |
| 应用报 `PROVIDER_NOT_CONFIGURED`（manga） | 按场景 A/C 安装权重后重启；不要手写部分文件凑数 |
