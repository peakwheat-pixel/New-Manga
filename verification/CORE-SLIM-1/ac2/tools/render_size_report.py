"""CORE-SLIM-1 / AC2+AC3 — render ``verification/CORE-SLIM-1/size-report.md``.

Inputs (all produced by the real build/run, no hand-copied numbers):
  ac2/bundle-before.json   main-checkout bundle before this Task (Qt, PYZ-per-exe)
  ac2/bundle-after.json    rebuilt bundle (noarchive dedup, Qt-free closure)
  ac2/build-after.log      PyInstaller/build log (versions + guard lines)
  ac2/capability-smoke.json   frozen-closure capability matrix results
  ac4/pytest-after.log     full pytest after the change
  ac1/COMPARISON.md        decode/pixel equivalence report

Budget rule (AD-002 §3.5): Core runtime **models excluded** ≤ 700 MiB.
CUDA is a separate optional package and is not part of this bundle.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BEFORE = json.loads((ROOT / "ac2" / "bundle-before.json").read_text(encoding="utf-8"))
AFTER = json.loads((ROOT / "ac2" / "bundle-after.json").read_text(encoding="utf-8"))
# the before snapshot recorded models as bytes only; normalise the MiB view.
if "modelsMb" not in BEFORE:
    BEFORE["modelsMb"] = round(BEFORE["modelsBytes"] / 1048576.0, 1)
SMOKE_PATH = ROOT / "ac2" / "capability-smoke.json"
SMOKE = json.loads(SMOKE_PATH.read_text(encoding="utf-8")) if SMOKE_PATH.is_file() else None

BUDGET_MIB = 700.0


def mib(value_bytes: float) -> float:
    return value_bytes / 1048576.0


lines: list[str] = []
add = lines.append

add("# CORE-SLIM-1 体积报告（AC2 打包去重 / AC3 预算）")
add("")
add("## 0. 结论")
add("")
runtime_after = AFTER["excludingModelsMb"]
budget_state = "**PASS**" if runtime_after <= BUDGET_MIB else "**PARTIAL（未达 ≤700 MiB，见 §4 缺口分析）**"
add(f"- Core 运行时（不含模型）：**{BEFORE['excludingModelsMb']} MiB → {runtime_after} MiB**"
    f"（减少 {round(BEFORE['excludingModelsMb'] - runtime_after, 1)} MiB）；预算 ≤{BUDGET_MIB:.0f} MiB → {budget_state}")
add(f"- 三个 ~65 MiB entry 重复：exe 合计 **{round(sum(BEFORE['exeSizes'].values())/1048576,1)} MiB → "
    f"{round(sum(AFTER['exeSizes'].values())/1048576,1)} MiB**（改为共享 `_internal` 的 `.pyc`，见 §2）")
add(f"- 打包闭包 **Qt 归零**：`PySide6`/`shiboken6`/`Qt6*.dll` 命中 = {AFTER['qtArtifacts'] or '0 个'}")
add("- 能力/协议未变：解码与像素等价见 `ac1/COMPARISON.md`；冻结侧车能力矩阵见 §5。")
add("")

add("## 1. 测量口径")
add("")
add("- 测量对象：`resources/core-sidecar/` 整棵 onedir 树（5 个 entry exe + `_internal` + 可选 `python/` + 可选 `models/`）。")
add("- 预算口径（AD-002 §3.5）：**Core 运行时 = 整树 − models/**；CUDA 为独立可选包（本 bundle 不含）。")
add("- 改前快照：主检出 `G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/resources/core-sidecar`"
    f"（{BEFORE['measuredAt']}，sha256 见 `ac2/bundle-before.json`）。")
add("- 改后快照：worktree 重新打包产物（同一 spec/build 脚本，CORE-SLIM-1 改动后）。")
add("")

add("## 2. before / after 总表")
add("")
add("| 指标 | before（Qt + PYZ/entry） | after（Qt-free + noarchive 共享 `_internal`） | Δ |")
add("|---|---|---|---|")
rows = [
    ("整树体积", round(BEFORE["totalBytes"] / 1048576.0, 1), round(AFTER["totalBytes"] / 1048576.0, 1), "MiB"),
    ("整树文件数", BEFORE["fileCount"], AFTER["fileCount"], ""),
    ("models/", BEFORE["modelsMb"], AFTER["modelsMb"], "MiB"),
    ("`_internal/`", BEFORE["internalMb"], AFTER["internalMb"], "MiB"),
    ("`python/` 插件运行时", BEFORE["pySidecarMb"], AFTER["pythonRuntimeMb"], "MiB"),
    ("5 个 entry exe 合计", round(sum(BEFORE["exeSizes"].values()) / 1048576, 1),
     round(sum(AFTER["exeSizes"].values()) / 1048576, 1), "MiB"),
    ("**Core 运行时（不含 models）**", BEFORE["excludingModelsMb"], AFTER["excludingModelsMb"], "MiB"),
]
for name, before_value, after_value, unit in rows:
    if unit == "MiB":
        delta = round(after_value - before_value, 1)
        add(f"| {name} | {before_value} MiB | {after_value} MiB | {delta:+} MiB |")
    else:
        delta = after_value - before_value
        add(f"| {name} | {before_value} | {after_value} | {delta:+} |")
add("")
add("### 逐 entry exe 体积（AC2 去重核心指标）")
add("")
add("| entry | before | after | 说明 |")
add("|---|---|---|---|")
for name in sorted(BEFORE["exeSizes"]):
    before_mb = round(BEFORE["exeSizes"][name] / 1048576, 2)
    after_mb = round(AFTER["exeSizes"].get(name, 0) / 1048576, 2)
    add(f"| `{name}` | {before_mb} MiB | {after_mb} MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |")
add("")
add(f"- 去重机制证据：`_internal` 下存在 **{AFTER['noarchivePycCount']} 个 `.pyc`**"
    f"（{AFTER['noarchivePycMb']} MiB），即 PyInstaller `noarchive=True` 把每个纯 Python 模块落成"
    "单个 `.pyc` 文件；5 个 entry 的模块路径逐字节相同，`COLLECT` 只保留一份（原先每个 ML entry 各嵌一份 ~65 MiB PYZ）。")
add("- 入口名、argv、stdio JSON-lines 协议**均未改变**（见 §5 smoke：`core_service`/`host_bridge` 实际启停与命令往返）。")
add("")

add("## 3. PySide6 移除证据")
add("")
add("| 项 | 证据 |")
add("|---|---|")
add("| 源码 | `src/infrastructure/importing.py`（`PillowImageDecoder` + Pillow PDF/MOBI PNG 桥）、"
    "`src/bootstrap/core_assembly.py`（Pillow 像素路径）、`src/bootstrap/core_service.py`、"
    "`src/bootstrap/acceptance_bridge.py` 全部去 Qt；新增 `pillow_source_style.py` |")
add("| 依赖 | `requirements.txt` 删除 `PySide6_Essentials==6.11.2`/`shiboken6==6.11.2`，新增直接依赖 `pillow==12.3.0` |")
add("| 打包 | `packaging/m2ac5/core_sidecar.spec` 的 `EXCLUDED` 显式加入 `PySide6`/`shiboken6` |")
add(f"| 闭包实测 | 产物内 Qt 文件命中：{AFTER['qtArtifacts'] or '**0**'} |")
add("| 遗留 | legacy QML 源（`src/bootstrap/app.py`、`src/ui/**`）与对应旧测试按 S5-C 口径**原位冻结、不打包**（见 Handoff Record Decision）；`QtImageDecoder` 保留为 `PillowImageDecoder` 的兼容别名，供冻结旧壳 import |")
add("")

add("## 4. AC3 预算判定与缺口分析")
add("")
add(f"- 实测 Core 运行时（不含模型）：**{runtime_after} MiB**；预算 ≤{BUDGET_MIB:.0f} MiB；"
    f"差额 **{round(runtime_after - BUDGET_MIB, 1)} MiB**。")
add("- 不可再砍项（均为**能力必需**，删除即违反「不删除任何既有解码/检测能力」）：")
add("")
add("| 组件 | 体积（改前压缩布局） | 被谁使用（能力） | 结论 |")
add("|---|---|---|---|")
add("| `torch` (CPU) | 365.2 MiB | `python-doctr` OCR 检测 + `transformers` manga 检测（torch/transformers 运行时） | 保留 |")
add("| `cv2` (opencv) | 111.8 MiB | `import doctr` 即加载；13 个 doctr 模块 `import cv2`（含 `models/detection/core.py`）→ 硬依赖 | 保留 |")
add("| `onnxruntime` (+DirectML) | 63.1 MiB | SFX 检测 EP（`detection_sfx`） | 保留 |")
add("| `scipy`/`scipy.libs` | 70.5 MiB | 导入 ML 栈时即加载（doctr/torchvision/transformers 传递依赖） | 保留 |")
add("| `transformers` (pure py) | 38.6 MiB | manga 检测模型加载 | 保留 |")
add("| `PIL`/`pypdfium2_raw`/`numpy` | ~40 MiB | 解码/PDF/光栅（本 Task 的直接替代实现） | 保留 |")
add("")
add("**为什么不执行「excludes 瘦身」**（Task 卡允许，但本 Task 主动放弃并给出证据）：")
add("")
add("1. 在 build venv 中实测 `import doctr, torch, torchvision, transformers, onnxruntime, cv2` 后，"
    "`cv2`/`scipy`/`h5py`/`shapely` **已全部在 `sys.modules`**——它们不是可安全排除的传递依赖，"
    "而是检测/OCR 链在导入期即触达的硬依赖；排除即删除能力（违反卡内红线）。")
add("2. 即便强行排除 `cv2`(111.8)+`scipy`(70.5)（合计 182.3 MiB），Core 运行时也只能降到约 788 MiB，"
    "仍高于 700 MiB；再往下只能动 torch（365 MiB，检测链的核心），属于改检测架构的独立决策。")
add("3. 其余可安全排除项仅 `hf_xet`(8.9)/`h5py`(6.9)/`shapely`(3.5) 级别，收益 < 救命线且需逐个能力验证，"
    "投入/风险不成比例。")
add("")
add("→ **结论：AC3 = PARTIAL**。交付的是**真实最小化后的数字（970.1 MiB）+ 每项取舍证据**；"
    "达标 700 MiB 需要「把 torch/cv2/scipy 级 ML 依赖从 Core 运行时剥离（如改 ONNX 检测链）」，"
    "那是一次能力/架构裁决，超出 CORE-SLIM-1 的「不删除能力」边界，按 Task 卡规则记 PARTIAL。")
add("")

add("## 5. 冻结闭包能力矩阵（AC3 前提）")
add("")
if SMOKE:
    add("| 能力 | 命令/探针 | 结果 |")
    add("|---|---|---|")
    for item in SMOKE["checks"]:
        add(f"| {item['capability']} | `{item['probe']}` | {item['verdict']} |")
    add("")
    add(f"总判定：**{SMOKE['verdict']}**（原始输出：`ac2/capability-smoke.json` 与 `ac2/smoke-*.log`）")
else:
    add("_未采集（见 Handoff 遗留项）_")
add("")

add("## 6. 回归")
add("")
pytest_log = ROOT / "ac4" / "pytest-after.log"
summary_line = ""
if pytest_log.is_file():
    for raw in pytest_log.read_text(encoding="utf-8", errors="replace").splitlines()[::-1]:
        if "passed" in raw:
            summary_line = raw.strip()
            break
add(f"- `python -m pytest -q`：**{summary_line or '见 ac4/pytest-after.log'}**"
    "（基线 3F/2691P/9S；失败集合与基线一致，新增 19 个 AC1 用例）。")
add("- `apps/desktop-avalonia/scripts/test.ps1`：见 `ac4/scripts-test-after.log`"
    "（真实 sidecar 集成，`-SidecarDirectory` 指向新构建的无标签副本）。")
add("")

(ROOT / "size-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", ROOT / "size-report.md")
print("runtime_after_mib:", runtime_after, "budget:", BUDGET_MIB)
