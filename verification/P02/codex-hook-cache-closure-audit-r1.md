# P02 Codex 静态 hook/cache 写入闭包审计 r1

状态：只读静态审计完成；结论 `BLOCKED / NOT_VERIFIED`。本报告只补充当前 Build Gate 证据，不批准 Sandbox smoke、产品 build 或 P02 AC 执行。

## 固定现场

- 源码 HEAD=`549a6544f0be1eec66c09ece393fd1a409f10bf3`，tree=`531ed2cf2f59303c3fee15c0585de5465aedf0ec`；提交 parent=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`。root 的当前 dirty 状态详见 [`root start manifest`](codex-process-isolation-root-start-manifest.json)。
- 目标 Python 环境：`G:\CODEX\New Manga.task-envs\m2ac5-build\Scripts\python.exe`。安装元数据版本：PyInstaller `6.22.3`、pyinstaller-hooks-contrib `2026.7`、Torch `2.14.0`、huggingface_hub `1.33.0`、Transformers `5.17.0`。
- 审计者：Codex 子代理 `/root/p02_hook_cache_closure`；Codex 在固定 HEAD 与现有 Gate/Task/Plan 上复核。方法限于 `Get-Content`、`Get-ChildItem`、`Get-FileHash`、`rg`、Git identity 与 package `METADATA` 只读读取；没有运行 Python import、PyInstaller analysis、build 或 runner。

## 已确认的静态路径

| 组件/位置 | 观察 | 文件 SHA-256 |
|---|---|---|
| `_pyinstaller_hooks_contrib/stdhooks/hook-torch.py:43` | hook 调用 `collect_submodules("torch")` | `72C0B693D1F92CA45C1929067467D9E1DFE53F5A82C96822FFDE5E27B86730E7` |
| `PyInstaller/utils/hooks/__init__.py:634-697` | isolated process 递归枚举子包并逐模块 `__import__` | `124A8A5DB0490FB44F5519E39410238882032D6A1138EDFF293D491E3270A582` |
| `PyInstaller/isolated/_parent.py:142-177` | 通过 `subprocess.Popen` 启动 worker，复制进程环境并保留 `PYTHONPATH` | `C35006B4AF2F5A56B3A4951A023941575D0C4ACD4912D7D59F1ABF4F8D296364` |
| `PyInstaller/configure.py:53-71` | `PYINSTALLER_CONFIG_DIR` 可改变 PyInstaller 自身配置缓存位置 | `732D79C6BCBA25C9725AA19F8533EDB028095DF440F10A7B08C1938076587850` |
| `torch/hub.py:185-188,276` | `TORCH_HOME` / `XDG_CACHE_HOME` 派生并创建 Torch Hub 路径 | `5407525D4C4858D5018A81A0396ABD3D90BD96372A7D12A6F822C017E643A522` |
| `huggingface_hub/constants.py:159-180,218-254,341-342` | `HF_HOME`、`XDG_CACHE_HOME`、`HF_HUB_CACHE`、`HF_XET_CACHE` 等派生 cache、状态和 token 路径 | `7B846AEB03E6381C6143FE0026DF84EF0465D83F43EA41DCC9AD65CFA09EE67C` |

既有只读 inventory 记录 PyInstaller hooks 480 个文件、hooks-contrib stdhooks 684 个文件；数量不说明本次 analysis 实际会执行哪些 hooks。`collect_submodules("torch")` 会递归导入大量子模块；代码静态检查不能枚举其运行时写入，也不能证明每个依赖/子进程只使用 scratch 缓存。

## 结论边界

- 现有 `pip freeze --all`、requirements pin 对照、缓存环境变量清单都不足以证明 PyInstaller analysis/import 的完整可达写入闭包。
- 未发现本次审计产生 scratch 外写入；也没有证据表明过去已发生这类外部写入。
- 由于 `NOT_VERIFIED` 不能转为 PASS，Build Gate 继续 `BLOCKED`、build 继续 `NOT_AUTHORIZED / NOT_RUN`。后续需要由 OS/VM 进程边界约束 host 可写路径，并用真实 Sandbox smoke 证明配置与映射，再由 Codex单独决定是否通过 Build Gate。