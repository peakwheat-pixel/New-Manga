# NOTICE — New Manga

本产品以 **GPL-3.0-or-later** 发布（见 [LICENSE](../../LICENSE)）。若发行包集成了 AGPL-3.0 组件（例如 Ultralytics 系模型/代码），则该发行包整体按 **AGPL-3.0** 分发并在本文档注明。

## 第三方来源登记

| 组件 | 来源 | 许可证 | 使用方式 | 登记状态 |
|---|---|---|---|---|
| Saber-Translator | https://github.com/MashiroSaber03/Saber-Translator | GPL-3.0 | **参考**（架构/流程/交互）；当前仓库**未包含其代码** | 待移植时逐文件登记 |
| （移植登记区） | — | — | 每移植一个文件在此记：源路径 + commit + 许可头保留 | 空 |

## 移植规则（强制）

1. 每个从 Saber-Translator 移植的文件必须在文件头保留原版权声明与 GPL-3.0 许可头，并在上表登记「源路径 + 上游 commit + 本仓库路径」。
2. 不得移植后附加额外限制、不得改许可、不得删除版权声明。
3. 模型权重按其自身许可证处理，不视为本仓库代码；随包分发前必须逐个核实（见 `THIRD_PARTY_LICENSES.md`）。
4. 字体只允许随包分发 OFL/Apache 等兼容许可字体；商业/系统字体（如 `msyh`、`STKAITI`、`STZHONGS`）不得随包。

## 当前状态

- 仓库当前**没有**任何 Saber-Translator 代码；仅有参考规格与截图（`verification/DISPLAY-PERF-DECISION-1/ui-spec/`）。
- 本文件与 `LICENSE`、`THIRD_PARTY_LICENSES.md` 构成发行前的许可三件套。
