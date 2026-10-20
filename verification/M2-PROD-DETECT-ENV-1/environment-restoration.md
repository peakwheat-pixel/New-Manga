# M2-PROD-DETECT-ENV-1：检测链路运行环境恢复（实测）

**产出**：2026-10-20 · **执行者**：DSH
**Task**：`doc/tasks/M2-PROD-DETECT-ENV-1.md`
**原状态**：`blocked`（理由：本机离线，`pip index` 不可达）

## 一、阻塞理由被证伪

**原记录写**：「本机离线，`pip index` 不可达，无法升级」。

**实测：网络是通的。**

| 检查 | 结果 |
|---|---|
| TCP 443 → `pypi.tuna.tsinghua.edu.cn` | **True** |
| TCP 443 → `pypi.org` | **True** |
| DNS 解析 `pypi.org` | **成功**（`2a04:4e42:…`）|
| HTTPS GET `/simple/transformers/`（两个索引）| **HTTP 200，有实际内容** |
| `pip download transformers --index-url https://pypi.org/simple` | **成功** |

**所以原先的「不可达」判断是**错的**。**

### 真实原因（r193 Review C1 后重写）

**我最初写的是「镜像对该包返回空版本列表」。那句话是**错的**——ZCode 的独立复核与我后来的实测都推翻了它。**

**可复现的事实只有这些：**

| 观察 | 结果 |
|---|---|
| `pip` 对 tuna 的 `/simple/pip/` 与 `/simple/transformers/` | **HTTP 403 Forbidden**（pip 自身 `-vvv` 日志记录）|
| 同一 URL 用 `urllib` 取 | **HTTP 200**，页面含 5.17.0，最高 5.20.2 |
| 同一 URL 用 `requests`（含 pip 的 UA）取 | **HTTP 200**，136,564 字节 |
| 清空 `HTTP_PROXY`/`HTTPS_PROXY` 后重跑 pip | **仍 `from versions: none`** |
| tuna 的 JSON 索引（`Accept: application/vnd.pypi.simple.v1+json`）| **495 files，含 5.17.0，最高 5.20.2** |
| `pip` 显式 `--index-url https://pypi.org/simple` | **成功** |

**所以三条错论都被排除：**

- **不是「没有网络」**——TCP、DNS、HTTPS 均通
- **不是「镜像没有这个包」**——它的 JSON 索引明确列出 5.17.0
- **不是「同步滞后到 5.5.0」**——ZCode 当时观测到的上限；我现在测到 5.20.2，说明镜像内容本身在变
- **也不是代理**——清空代理环境变量后行为不变

**剩下的可复现事实是：`pip` 从该镜像收到 403，而同一 URL 对 `urllib`/`requests` 正常。**

**`pip` 侧的具体触发条件我**没能隔离**。这是如实陈述，不是保留。**

**未验证的推测**：镜像按 TLS 指纹或客户端特征拒绝 pip；镜像对 pip 版本做过滤。
**我没有证据支持其中任何一条，所以不写进结论。**

**修复（已实施且已验证）**：显式 `--index-url https://pypi.org/simple`。

## 二、AC1：环境记录与基线核对

**落点**：`G:\CODEX\New Manga.workspace\task-envs\M2-PROD-DETECT-ENV-1\venv`
**方式**：`python -m venv --system-site-packages`（**复用已装 torch，不重装数 GB**）

| 包 | `requirements.txt` 钉 | 实际 | 判定 |
|---|---|---|---|
| `transformers` | **`5.17.0`** | **`5.17.0`**（venv 内） | **一致** |
| `torch` | `2.14.0`（CPU 构建） | `2.11.0+cu128` | **见下** |
| `torchvision` | `0.29.0` | `0.26.0+cu128` | **见下** |
| `safetensors` | `0.8.0` | `0.8.0` | **一致** |
| `python-doctr` | `1.1.0` | 缺失 | 与本 Task 无关（T1.1.1 检测器）|
| Python | — | `3.14.6` | — |

**关于 `torch` / `torchvision` 的「不一致」**：
`requirements.txt` L9-12 明确写——

> **「GPU (CUDA) wheels 是单独的打包决定（T3.2.1）……证明可用于
> （torch 2.11.0+cu128, RTX 5070 Ti）的一次性 venv……但**不在 `requirements.txt` 内**。」**

**所以 `2.11.0+cu128` 不是偏离，是文档记录在案的 GPU 变体。**
**CPU 构建基线（2.14.0）与 GPU 实测基线（2.11.0+cu128）是两个不同口径，不能混读。**

## 三、AC2：离线从本地快照构造模型与 processor

**权重目录**：`G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector`

| 文件 | 大小 | SHA-256（前 16）|
|---|---:|---|
| `config.json` | 2,320 B | `b6d707933e12e959…` |
| `model.safetensors` | **171,543,900 B** | `037930a861e67870…` |
| `preprocessor_config.json` | 470 B | `7e9e2245806aa3ef…` |

**`config.json` 声明**：`architectures: ["RTDetrV2ForObjectDetection"]`、`model_type: rt_detr_v2`、
`transformers_version: "4.49.0"`。

**在 `HF_HUB_OFFLINE=1` 与 `TRANSFORMERS_OFFLINE=1` 下构造**：

```
processor: RTDetrImageProcessor
model    : RTDetrV2ForObjectDetection
num params: 42,733,137
load seconds: 5.5
```

**没有联网下载任何权重**——`local_files_only=True` 且两个离线环境变量均置 1。

### 为什么这证明了「同一模型快照」（r193 Review C2）

**`detection_manga.py:511-519` 在 `from_pretrained`（`:522-527`）**之前**，对三个权重文件逐一做
**完整 64 位** SHA-256 校验，不匹配即 `raise ProviderError`（fail-closed，不是 warning）。**

**所以 §四 那两个用例通过这件事**本身蕴含**「三文件完整校验通过」——
否则引擎根本建不起来，测试不可能绿。**

**因此「权重与受测代码为同一快照」不是靠前 16 位前缀推断的，是由 AC3 的通过反推的。
前 16 位只是便于人眼核对代码里的 pin。**

## 四、AC3：两个真实检测用例

**命令**：

```powershell
& <venv>\Scripts\python.exe -m pytest tests/providers/test_detection_manga_real.py -q
```

**结果**：**`2 passed in 6.61s`**

| 用例 | 结果 |
|---|---|
| `test_real_detection_returns_block_candidates` | **PASSED** |
| `test_real_blank_page_yields_zero_candidates` | **PASSED** |

**这一点必须对比说明**：

**在**未被修复的环境**（全局 `transformers 4.48.3`）里，这两个用例**失败**，
且失败在**模型加载阶段**（`AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection`）。**

**所以此前「本机 manga 检测链路不可用」是准确陈述；现在它可用了。**

## 五、全套件结果（含 AC5 的验证）

**同一个 venv 内跑整个 `tests/providers`**：

```
442 passed, 3 skipped in 15.29s
```

**零失败。**

**对比**（同一台机器）：

| 环境 | `tests/providers` |
|---|---|
| 全局 `transformers 4.48.3` | **2 failed**, 440 passed, 3 skipped |
| **venv `transformers 5.17.0`** | **0 failed**, **442 passed**, 3 skipped |

**而 `git diff` 显示**：本 Task **没有改 `src/`、没有改 `tests/`**——
**差异完全来自环境。**

**AC5（不得把 V2 改成 V1）**：`src/infrastructure/providers/detection_manga.py:525`
**仍是 `transformers.RTDetrV2ForObjectDetection`**，与权重声明一致，未被改动。

## 六、AC4：修复落点与复现

### 落点

**隔离 venv**，位于工作区目录下：

```
G:\CODEX\New Manga.workspace\task-envs\M2-PROD-DETECT-ENV-1\venv
```

**未升级全局 Python 环境**（`C:\Python314` 与用户 site-packages 均未改动）。

### 复现步骤

```powershell
$venv = "G:\CODEX\New Manga.workspace\task-envs\M2-PROD-DETECT-ENV-1\venv"
python -m venv $venv --system-site-packages
& "$venv\Scripts\python.exe" -m pip install "transformers==5.17.0" `
    --index-url https://pypi.org/simple --timeout 60

$env:PYTHONPATH = "G:\CODEX\New Manga;G:\CODEX\New Manga\src"
& "$venv\Scripts\python.exe" -m pytest tests/providers -q
# 期望：442 passed, 3 skipped
```

### 为什么用 `--system-site-packages`

**为了复用已装的 `torch 2.11.0+cu128`（GPU 变体，约数 GB）。**
**不带该选项重建 venv 会重新下载整条 torch 栈，成本与收益不成比例。**

**代价**：venv 里 `transformers 5.17.0` 与全局 `4.48.3` 并存；
venv 的 `site-packages` 在 `sys.path` 中优先，所以 venv 内解析到 5.17.0（已实测确认）。

### 使用警示（r193 Review C3）

| 陷阱 | 后果 |
|---|---|
| **在该 venv 内 `pip uninstall` 或降级 `transformers`** | 只移除 venv 副本，随后**露出全局 `4.48.3`**——检测链路会「无声地」退回不可用 |
| **该 venv 的依赖解析「看得见」整个全局栈** | 将来装新包时其依赖可能被**全局旧版**满足而不在 venv 内落副本，版本来源不清 |

**所以这个 venv 是「全局栈 + transformers 覆盖层」，不是干净环境。
任何排障必须先问：现在解析到的是哪一个。**

## 七、限制

| # | 限制 |
|---|---|
| **L1** | **未改 `requirements.txt`**——按 AC5 与 r42 边界，本 Task 只恢复环境，不动基线声明 |
| **L2** | **venv 未纳入版本控制**（在 workspace 目录，按工区治理规则本就不入库）|
| **L3** | **CPU 构建基线（`torch==2.14.0`）未验证**——本机是 GPU 机器，只验了 GPU 变体 |
| **L4** | **`python-doctr==1.1.0` 缺失**——属 T1.1.1 检测器，本 Task 范围外的既有状态 |
| **L5** | **只修了本机**；CI 或其他机器仍需各自按 §六 复现 |
| **L6** | **配置的镜像对 `pip` 返回 HTTP 403**（对 `urllib`/`requests` 正常），触发条件未隔离；**复现时必须显式 `--index-url https://pypi.org/simple`** |

## 八、明确未做

- **未升级全局 `transformers`**
- **未修改 `requirements.txt` 或任何依赖声明**
- **未改 `src/` 与 `tests/`**
- **未下载任何权重**（只用既有本地快照）
- **未验证 CPU 构建基线**
