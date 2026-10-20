---
id: M2-PROD-DETECT-ENV-1
title: 恢复 manga 检测链路的运行环境基线
kind: environment
governance_version: 3
status: closed_with_limitations
language: zh-CN
parent: M2-PROD-DETECT-1
blocked_by: null
blocked_reason: null  # r192 解除：原「离线」判断为误判，见 Closeout Record
approval: released_by_r42_20261020
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 0e93a5687
branch: null
worktree: null
integration_commit: 9464003cd
delivery_head: 9464003cd
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/M2-PROD-DETECT-ENV-1
allowed_paths:
  - verification/M2-PROD-DETECT-ENV-1/
---

# M2-PROD-DETECT-ENV-1：恢复 manga 检测链路的运行环境基线

## 来源与目标

**来源**：`verification/PDF-STREAM-FIX-1/full-suite-failure-classification.md`（A 类）与 r42 裁定 §三。

**当前本机 manga 检测链路**完全不可用**——两个真实检测用例在**模型加载阶段**失败**：

```
AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection
```

**三方对照（都已核实）**：

| 方 | 内容 | 判定 |
|---|---|---|
| **权重** `config.json` | `architectures: ["RTDetrV2ForObjectDetection"]`、`transformers_version: "4.49.0"` | 声明需要 V2 |
| **代码** `detection_manga.py:525` | `transformers.RTDetrV2ForObjectDetection` | **与权重一致，正确** |
| **`requirements.txt` L28** | **`transformers==5.17.0`** | 项目固定基线 |
| **本机** | **`4.48.3`** | **不符合项目自身基线** |

**顺带核实**：同组的 `torch` 装的是 `2.11.0+cu128`，**不是偏离**——
`requirements.txt` L9-12 明确写 GPU/CUDA wheels 是单独打包决定、不在文件内，
且记录的正是该版本与 RTX 5070 Ti。`safetensors` 一致。

**所以本 Task 的目标不是改代码，是让运行环境符合项目已声明的依赖基线。**

## Acceptance Criteria

- [x] **AC1 环境记录** <<MET>>
- [x] **AC2 本地权重构造** <<MET>>
- [x] **AC3 真实用例** <<MET>>
- [x] **AC4 落点与复现** <<MET>>
- [x] **AC5 不改 V2 为 V1** <<MET>>

### AC 证据

| AC | 证据 |
|---|---|
| AC1 | `environment-restoration.md` §二：`transformers` 5.17.0 与钉值一致；`torch`/`torchvision` 的不一致是 `requirements.txt` L9-12 记录在案的 GPU 变体 |
| AC2 | 同文件 §三：`HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` 下从本地快照构造 `RTDetrImageProcessor` + `RTDetrV2ForObjectDetection`（42,733,137 参数，5.5 s），未下载权重 |
| AC3 | 同文件 §四：`tests/providers/test_detection_manga_real.py` **2 passed**；改前是模型加载阶段失败 |
| AC4 | 同文件 §六：隔离 venv 落点 + 可复现命令；**未升级全局 Python 环境** |
| AC5 | 同文件 §五：`detection_manga.py:525` 仍为 `RTDetrV2ForObjectDetection`，未被改动 |

## 允许修改范围

- `verification/M2-PROD-DETECT-ENV-1/`
- **本 Task 预期不改仓库代码**；若确需改动，须先由 Codex 重新冻结范围

## 禁止范围

- **不得修改 `src/infrastructure/providers/detection_manga.py` 的模型类选择**
- 不得修改 `tests/**` 以求变绿
- 不得联网下载权重替代本地快照

## 测试要求

- 复用 `tests/providers/test_detection_manga_real.py` 的两个用例作为验收探针
- 证据须含实际版本输出、加载成功/失败日志、两个用例的逐项结果

## 依赖、风险与阻塞

| # | 项 |
|---|---|
| **B1** | **本机离线**：`python -m pip index versions transformers` → `No matching distribution found`；pip 缓存中 `transformers` 相关 wheel 为 **0 个**。需在有网络的环境执行 |
| **B2** | `requirements.txt` 钉 `transformers==5.17.0`，可能与已装 `torch 2.11.0+cu128`（GPU 变体）存在兼容性差异，须实测而非假定 |
| **R1** | 若按锁定基线仍无法加载权重，再以新证据另行判断是否需要代码 Task |

## 修复前声明口径

**在此 Task 完成前，任何涉及检测链路的陈述都必须写成**：

> **「检测实现与权重预期使用 RT-DETR-v2；当前本机运行环境 `transformers` 版本不符合项目固定依赖，
> 两个真实检测用例未通过，**本机 manga 检测链路目前不可用**，
> 尚未验证正确环境下的真实推理结果。」**

**不得简写为「9 个旧测试红」，也不得写成「检测链路已可用」。**

## 交付与运行记录

（未开始）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-ENV-DOC | AC1-AC5 | `verification/M2-PROD-DETECT-ENV-1/environment-restoration.md` | 9464003cd | - | CANONICAL |
| EV-ENV-TEST | AC3 | `tests/providers/test_detection_manga_real.py` | a016d38cb | - | CANONICAL |
| EV-ENV-SRC | AC5 | `src/infrastructure/providers/detection_manga.py` | ed86cc465 | - | CANONICAL |

| EV-ZC-REVIEW | Review | `verification/M2-PROD-DETECT-ENV-1/dsh-zcode-review-r193.md` | d4d0f46ab | - | CANONICAL |

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource_type | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| （无） | — | NOT_APPLICABLE | — | — | 仅环境恢复与证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

- **Closeout date**：2026-10-20 · **Executor**：DSH · **Reviewer**：待 ZCode
- **canonical_evidence_status**：`complete`
- **resource_closeout_status**：`complete`
- **删除、迁移、归档数量/字节数**：**0**

### 阻塞理由被证伪

**原 `blocked_reason` 写**：「本机离线，`pip index` 不可达」。

**实测：网络通。** TCP 443、DNS、HTTPS GET 全部正常，`pip download` 成功。

**真实原因**：配置的镜像 `pypi.tuna.tsinghua.edu.cn` 对 `transformers` 返回空版本列表，
而 `pip index versions` 默认走该镜像——**「某个镜像坏了」被读成了「没有网络」。**

**`requirements.txt` 钉的 `transformers==5.17.0` 在 `pypi.org` 上确实存在。**

### 结果

| 环境 | `tests/providers` |
|---|---|
| 全局 `transformers 4.48.3`（修前）| **2 failed**, 440 passed, 3 skipped |
| **隔离 venv `5.17.0`** | **0 failed**, **442 passed**, 3 skipped |

**`src/` 与 `tests/` 零改动**——差异完全来自环境。

### 限制

| # | 限制 |
|---|---|
| **L1** | **已由 ZCode 独立 Review（r193）**：`approve_with_conditions`；C1/C2/C3 已全部闭合（见下）|
| **L2** | **未改 `requirements.txt`**——本 Task 只恢复环境，不动基线声明 |
| **L3** | **CPU 构建基线（`torch==2.14.0`）未验证**——本机是 GPU 机器，只验了 `2.11.0+cu128` |
| **L4** | **`python-doctr==1.1.0` 缺失**——属 T1.1.1 检测器，本 Task 范围外的既有状态 |
| **L5** | **只修了本机**；其他机器/CI 需各自按证据 §六 复现 |
| **L6** | **镜像对该包仍异常**——复现必须显式 `--index-url https://pypi.org/simple` |
| **L7** | **venv 未入版本控制**（在 workspace 目录，按工区治理规则本就不入库）|

### ZCode Review r193 的处置

**产出**：`verification/M2-PROD-DETECT-ENV-1/dsh-zcode-review-r193.md`
**结论**：**`approve_with_conditions`**（1×P2 + 2×P3，全部为文档表述级，无代码/环境返修）

| 项 | 处置 |
|---|---|
| **C1（P2）**「镜像返回空版本列表」的机制表述与实测不符 | **已重写**。核实后发现**三种解释都不成立**：不是离线（网络通）、不是镜像无此包（其 JSON 索引含 5.17.0）、不是同步滞后（ZCode 测到上限 5.5.0，我测到 5.20.2）。**可复现事实是 pip 收到 403 而 urllib/requests 收到 200**，触发条件未能隔离，已如实写明 |
| **C2（P3）** 「同一快照」的证据形式不足 | **已补**：`detection_manga.py:511-519` 的**完整 64 位** SHA-256 fail-closed 校验先于 `from_pretrained`，**故 AC3 通过即蕴含三文件校验通过** |
| **C3（P3）** venv 使用警示缺失 | **已补**：卸载/降级会露出全局 4.48.3；依赖解析看得见全局栈 |

**Review 的独立佐证（其沙箱无法执行 python/pwsh/git，全部 pytest 复跑登记 `NOT_RUN`）**：
`pip.ini` 内容、tuna/pypi 双索引抓取、venv `pyvenv.cfg` 与 dist-info、`RTDetrV2` 模块文件与 `.pyc` 物证、
权重三文件字节数、321 个 Task 文件的 `\| resource \|` 表头扫描（**0 命中**，与我的结论一致）。

### 后续建议

1. ~~交 ZCode 独立 Review~~（**已完成**）
2. **L3**：若需 CPU 构建基线，另立 Task（本机无 CPU 环境变量组合的验证条件）
3. **L6**：可考虑在 `requirements.txt` 或装配文档里注明该包须走 `pypi.org`

