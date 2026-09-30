# M2-PROD-DETECT-2 释放证据（release @1d876ef7，2026-09-30）

## 授权

用户对本会话推荐（候选 1「发布形态检测器运行时/权重分发」= M2-PROD-DETECT-1 遗留 slice①）回复**「继续」**（2026-09-30）。

## 释放侦察事实（已核实）

1. Tauri resource 整目录机制：`tauri.conf.json` L30-31 `"target/core-sidecar/core-sidecar": "resources/core-sidecar"` → 权重进 onedir 内部即随包，**tauri.conf.json 零改动**。
2. spec/构建链：EXCLUDED=torch/torchvision/doctr/pandas+tooling（spec L48-61）；build venv=pyinstaller-only+PySide6（requirements-build.txt，注释自述「needs nothing beyond the pinned packager」）→ 本 Task 翻转定位（裁决 2）。
3. 体积实测（主 venv）：torch 537MB / transformers 112MB / doctr 4MB / tokenizers 8MB / safetensors 1MB ≈ 662MB；manga 权重 171,543,900B。基线：onedir 99,308,142B/161 文件、NSIS 27,924,371B（M2-PROD-DETECT-1 轮实测）。
4. 权重解析现状：env override > `<data root>/models/detector/<...>`；frozen 回退层不存在；`MANGA_WEIGHTS_DIRNAME` 定义于 detection_manga.py:79（零触碰）。
5. GATE 口径：run_clean_start_e2e.py 25 场景冻结不改；真实 detect 验证走独立探针。
6. M2-AC5 raw 重写先例：产物移本 Task 目录 + `git checkout --` 还原（M2-PROD-DETECT-1 已验证可行）。

## 代理裁决登记（用户可撤销）

- 裁决 1：接受安装包 26.63MiB → 数百 MiB（检测可用 > 轻量；M2-RG1「本机=干净机」口径无外部分发压力）。撤销=revert spec/requirements-build 改动。
- 裁决 2：build venv 定位「minimal packager」→「packager + runtime closure」，ML 版本与主 requirements 逐字一致。
- 裁决 3：包内只带 manga 权重；docTR 权重不进包（发布形态切回=fail-closed NOT_CONFIGURED+指引，源码形态不受影响）。
- 裁决 4：权重查找 env > data root（探测）> frozen 包内（探测）> 默认路径（报错列候选）；非 frozen 零行为变化。

## 范围

允许：spec/requirements-build.txt/build_sidecar.ps1/README（m2ac5 内最小适配）、core_assembly.py 仅权重解析段、tests/**、Task/Handoff/verification/M2-PROD-DETECT-2/**。
禁止：tauri.conf.json、run_clean_start_e2e.py、ports/**、两个 provider 行为、requirements.txt、experiments/**、权重入库、下载器实现。
