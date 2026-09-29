# M2-TA2C 附件只读审计

审计输入：`C:/Users/49745/Downloads/漫画素材包_无HF方案_日漫韩漫.zip`；SHA-256 `ee6b963c341f0c77f500d632f8d8a1ab2ad9478637188a666952b8840cb0a0f6`。18,056 bytes，40 条目，安全解压到临时目录后得到 25 个文件 / 20,441 bytes，临时目录退出即清除。`素材/` 仅空目录和 `.keep`，图像、mask、ground truth 实物均为 0。ZIP 成员无绝对路径、`..`、drive 前缀、符号链接、重名或加密项，CRC 通过。没有执行包内脚本。

| 包内文件 | 静态发现 | 处置 |
|---|---|---|
| `README_先看.md`、`官方来源.md`、`素材索引.csv`、`manifests/datasets.json` | 来源设想，不是本仓 65 个 Case 的统一 catalog；“无需 HF 账号”不等于“无需 HF 服务” | 来源线索逐项复核；不另建第二套清单 |
| `00_准备环境.ps1`、`requirements.txt` | 创建 venv、升级 pip、安装未锁版本的 `huggingface_hub` 与 `requests`；README 建议 `ExecutionPolicy Bypass` | 不运行，不改依赖 |
| `01_下载全部公开素材.ps1`、`tools/download_assets_no_hf.py` | 可对 KO 再下载约 844 MiB；克隆 OpenMantra、Artificial Manga、JMangaBench，下载 TextMasks；`git pull` 失败容忍。`stream_download` 在 MD5 校验前发布最终文件，未核对断点续传 `Content-Range` | 不运行；复用现有标准库 `assets.py` 的安全下载和验证路径 |
| `tools/verify.py`、`02_验证素材.ps1` | 只计数和大小；零素材也成功，不能证明 Case READY | 不接入；沿用现有格式及 SHA-256 校验 |
| `tools/pack_downloaded.py`、`04_重新打包已下载素材.ps1` | 无许可/敏感文件白名单，递归包含未来 `.git`、`.venv`、受限原图及可能的凭据，覆盖输出 ZIP | 禁止作为套件打包器复用 |
| `03_手动数据说明.ps1` | 仅输出人工下载说明，未发现直接删除或上传凭据逻辑 | 信息参考，不执行 |

附件脚本未见直接 arbitrary-code `eval`/`exec` 或把 token 写入文件的逻辑；但依赖安装、Git 远程同步、错误续传与无差别重打包仍不满足本项目资产/许可规则。外部仓库的内容也不能作为信任代码执行。
