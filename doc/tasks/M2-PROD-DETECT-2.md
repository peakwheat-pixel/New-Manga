---
id: M2-PROD-DETECT-2
title: "发布形态检测器运行时/权重分发：ML 栈进 sidecar 闭包 + manga 权重随包（M2-PROD-DETECT-1 遗留 slice①；用户「继续」推进 2026-09-30）"
kind: feature
status: ready
approval: user_directive_2026-09-30_continue
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30）
depends_on: [M2-PROD-DETECT-1]
base_commit: 1d876ef7
branch: agent/zcode/M2-PROD-DETECT-2
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode
---

# M2-PROD-DETECT-2：发布形态检测器运行时/权重分发

## 来源与目标

- 来源：M2-PROD-DETECT-1 遗留 slice①（DSH r1 R1）：发布包内默认 manga backend 的 detect 报 `PROVIDER_DEPENDENCY_MISSING`（docTR 在 base 同样如此）——发布形态与源码形态存在**检测能力差距**。用户对本 Task 的推荐回复**「继续」**（2026-09-30）。
- 目标：让 **NSIS 安装包形态**的 detect 链路真正可用——ML 运行时（torch CPU + transformers + doctr）进 sidecar 闭包、manga 权重随包分发、装配段支持包内权重回退查找；docTR 保持代码可切回（其权重不进包，发布形态切回时 fail-closed+指引，登记）。

## 已核实的设计事实（释放侦察）

1. **Tauri resource 机制**（`apps/desktop/src-tauri/tauri.conf.json` L30-31）：`"target/core-sidecar/core-sidecar": "resources/core-sidecar"` 把整个 onedir 目录打进安装包——**权重放入 `core-sidecar/` 内部即可随包分发，tauri.conf.json 零改动**。
2. **闭包现状**（`packaging/m2ac5/core_sidecar.spec`）：EXCLUDED = torch/torchvision/doctr/pandas + build tooling；`transformers` 不在 EXCLUDED（build venv 根本没装，Analysis 阶段不收集）。**build venv 与运行时 venv 分离**（`requirements-build.txt`：pyinstaller==6.22.3 + PySide6_Essentials==6.11.2 + shiboken6==6.11.2，注释明示「build venv needs nothing beyond the pinned packager」）——本 Task 翻转该定位（代理裁决，见下）。
3. **体积实测**（主 venv T1.1.1-impl-py312 site-packages）：torch 537MB、transformers 112MB、doctr 4MB、tokenizers 8MB、safetensors 1MB ≈ **662MB**；manga 权重 171,543,900B + config 2,320B + preprocessor 470B。预期 onedir 99.3MB → ~800MB+、NSIS 安装包 26.63MiB → **数百 MiB（实测为准）**。
4. **权重路径解析**（`core_assembly.py` 装配段）：现语义 = env `NEWMANGA_DETECTOR_WEIGHTS` override > 默认 `<data root>/models/detector/<...>`；frozen 包内回退层不存在（本 Task 新增）。
5. **GATE 口径冻结**：`run_clean_start_e2e.py`（M2-AC5 交付物）的 25 场景**不改**；真实 detect 验证用独立探针脚本（verification 下），不扩 GATE 口径。
6. **发布形态 data root**：`core_service.assemble_production_core` → `default_data_root()`；宿主 %APPDATA% 零触碰是 M2-AC5 冻结纪律，包内回退不写 data root。

## 设计决策（代理裁决，用户可撤销）

- **裁决 1（安装包体积）**：接受安装包从 26.63MiB 涨到数百 MiB（torch CPU 闭包 + 171MB 权重）。理由：检测是产品核心链路第一步，发布形态可用 > 安装包轻量；本机/干净机分发（M2-RG1 口径）无外部分发压力。撤销方式：revert 本 Task 的 spec/requirements-build 改动即回轻量包（detect 回 DEPENDENCY_MISSING，行为同 M2-PROD-DETECT-1 交付态）。
- **裁决 2（build venv 定位翻转）**：`requirements-build.txt` 从「minimal packager」变为「packager + runtime closure」——ML 栈版本与主 `requirements.txt` **逐字一致**（torch==2.14.0 / torchvision==0.29.0 / python-doctr==1.1.0 / transformers==5.17.0 / safetensors==0.8.0，CPU wheels 源注释同主文件）；文件头注释同步改写并登记本裁决。
- **裁决 3（只带 manga 权重）**：包内只放 manga 权重（默认 backend）；docTR 权重 65MB 不进包——doctr 切回在发布形态 = 依赖就绪但 fail-closed NOT_CONFIGURED + 指引（源码 venv 形态不受影响）。登记为已知限制。
- **裁决 4（权重查找顺序）**：env override > data root（存在性探测）> frozen 包内（存在性探测，仅 `sys.frozen`/PyInstaller onedir 布局下 `Path(sys.executable).parent/models/detector/<dir>`）> 默认 data root 路径（fail-closed 报错信息列出全部已探测候选）。**非 frozen（源码 venv）形态行为零变化**；探测逻辑可 import `detection_manga` 的文件清单常量（不复制清单知识）。
- **契约零修订优先**：`ports/**` 不动；`detection_manga.py`/`detection_doctr.py` 行为不动（装配段解析是唯一 src 改动点）；`run_clean_start_e2e.py` 不动。

## Acceptance Criteria

- [ ] AC1（构建链）：`requirements-build.txt` 授权 ML 栈（裁决 2）+ build venv 更新；`core_sidecar.spec` 撤 EXCLUDED 的 torch/torchvision/doctr（pandas/build-tooling 排除保持）+ 按需 hiddenimports（transformers 动态 import 兼容；如需 hook 最小化）；`build_sidecar.ps1` 构建成功（四入口 closure 含 ML 栈）。
- [ ] AC2（权重随包）：`build_sidecar.ps1` 最小适配——构建后将 manga 权重三文件从 task-envs 快照复制进 `core-sidecar/models/detector/ogkalu-comic-text-and-bubble-detector/`，**逐文件 SHA-256 校验后复制**（复用 pin 常量或脚本内等价校验）；docTR 权重不进包；tauri.conf.json 零改动（权重经既有 resource 机制随包）。
- [ ] AC3（包内回退解析）：`core_assembly.py` 装配段按裁决 4 增加包内回退（manga 与 doctr 两个 backend 同样语义）；单测覆盖查找顺序矩阵（env/ data root/ frozen 包内/ 全缺→typed 错误含候选列表；非 frozen 零变化——monkeypatch frozen 标记，不真打包）。
- [ ] AC4（GATE 回归）：M2-AC5 runner 25/25 PASS（新 onedir + 新 NSIS 安装包）；体积前后对比如实记录入 `verification/M2-PROD-DETECT-2/`（onedir 字节/文件数、NSIS 字节、构建时长）；M2-AC5 raw 证据零改动（runner 重写行为按 M2-PROD-DETECT-1 先例处置：产物移入本 Task 目录 + `git checkout --` 还原）。
- [ ] AC5（发布形态 detect 真实推理验证）：独立探针（verification 下脚本，不进 runner）——对安装后环境（runner 已装目录或 NSIS 静默安装）以默认 backend 跑一次真实 detect（合成漫画页或 K01 页），EXIT=0 且 text 候选 >0，记录耗时；docTR 切回探针验证 fail-closed NOT_CONFIGURED（裁决 3 行为）。
- [ ] AC6（回归与纪律）：pytest 三套件（providers/m2_acceptance/core）基数保持（387+1 既有失败口径）；cargo/vitest 留痕（预期零影响）；`git diff --check` EXIT=0；禁改面专项 diff 为空。
- [ ] AC7（交付与 Handoff）：Task 测试表填实、Handoff 按模板（含代理裁决四条的撤销方式、体积数字、已知限制）。

## 允许修改范围

- `packaging/m2ac5/core_sidecar.spec`（EXCLUDED/hiddenimports 最小适配）
- `packaging/m2ac5/requirements-build.txt`（ML 栈授权 + 头注释改写）
- `packaging/m2ac5/build_sidecar.ps1`（权重复制 + 校验最小适配）
- `packaging/m2ac5/README.md`（闭包说明同步，如需）
- `src/bootstrap/core_assembly.py`（仅检测器权重解析段）
- `tests/**`（装配解析新逻辑单测）
- `doc/tasks/M2-PROD-DETECT-2.md`、`doc/handoffs/M2-PROD-DETECT-2-*.md`、`verification/M2-PROD-DETECT-2/**`

## 禁止范围

- `apps/**`、`tauri.conf.json`、`core_sidecar.spec` 之外的 tauri/spec 面
- `packaging/m2ac5/run_clean_start_e2e.py`（GATE 口径冻结）
- `ports/**`、`src/infrastructure/providers/detection_manga.py` 与 `detection_doctr.py` 行为（MERGE_* 与 pin 常量零触碰）
- `requirements.txt`（主运行时依赖零改动）、`experiments/**`、C4/C1 产物
- 模型/权重文件入库（权重只进本地构建产物目录；git 层面权重永不 tracked）
- 下载器/首启引导/网络分发实现（不在本刀）

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 构建 | build_sidecar.ps1 | build venv 含 ML 栈 | RUN | verification/M2-PROD-DETECT-2/ |
| AC2 权重随包 | 检查 core-sidecar/models/.../ 三文件 + sha256 | 快照在位 | RUN | 同上 |
| AC3 解析单测 | pytest tests/...（frozen 矩阵） | — | RUN | 本表 |
| AC4 GATE | run_clean_start_e2e.py | 新 NSIS | RUN：25/25 | 同上 |
| AC5 发布形态探针 | 独立探针脚本 | 安装后环境 | RUN：EXIT=0 | 同上 |
| AC6 回归 | pytest 三套件 + cargo + vitest | — | RUN：387+1 口径 | 本表 |

## 依赖、风险与阻塞

- 依赖：M2-PROD-DETECT-1 `done` @`056617e4`（provider 与装配语义已集成）。
- 风险：①**PyInstaller × transformers 动态 import**（hiddenimports/hook 兼容）——最可能的返工点，不兼容即停登记，不得放宽 excludes 掩盖警告；②构建时长与体积（NSIS 压缩 ~400MB 级）；③torch DLL 进 onedir 后启动内存/时间变化——GATE 25/25 实测兜底；④权重随包后「发布即冻结」——权重损坏时 detect 报 PROVIDER_FAILED（pin 校验兜底，行为正确）。
- 阻塞：无。

## 遗留与边界

- docTR 权重发布形态不可用（裁决 3，fail-closed+指引）。
- 权重更新机制（换权重不重装）走 data root 优先级已天然支持（运维放置即覆盖包内），无 UI。
- 首启引导/在线下载（方案 C）本 Task 不实施；若未来外部分发需要再立 slice。
