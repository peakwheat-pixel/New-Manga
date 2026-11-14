# L2-CORE-E2E：Core → provider → 落库端到端翻译（2026-11-14，验证任务）

**结论：未取得翻译产出（BLOCKED，非通过）。** 本轮把链路推进到「StartRun 被接受 + Run 真实执行 + 逐 target 落 typed 失败」，但**停在 `detect` 步，translate 从未执行**。

## 1. 源码 Core 入口（探明结果）

| 问题 | 结论 |
|---|---|
| 入口 | `python -m bootstrap.core_service` **可跑**（`src/bootstrap/core_service.py:9008` 的 `if __name__ == "__main__": raise SystemExit(main())`） |
| 必需环境 | `cwd = <repo>/src` 且 `PYTHONPATH=<repo>/src`（二者都给最稳；缺 cwd 时 `bootstrap` 包不可导入） |
| 其它环境变量 | 与旧探针一致：`NEWMANGA_DATA_ROOT` / `M2RC1_DERIVED_ROOT` / `M2RC2_CATALOG_DB` / `M2RC1_MANAGED_ROOT` |
| 握手 | `core.ping` 返回 `protocol_version 2.3`、`status=ready` |

探针已加 `--python-core <repo>` 模式（`workspace/flea-loop/run_translate_probe.py`）：spawn `[sys.executable, "-m", "bootstrap.core_service"]`，cwd/PYTHONPATH 指向 `<repo>/src`；`--sidecar` 变为可选。

## 2. fixture 迁移

- 新 work-root：`workspace/task-envs/L2-CORE-E2E/work-root`（从 `BOOK-FIXTURE-1/isolated-data` **复制**，旧目录未动）。
- 迁移：**v6 → v14**（`[core.schema] applied 8 migration(s) up to v14`），自动备份 4,023,101 B（verified=True）。
- 迁移后计数不变：`books=1, chapters=1, pages=8, regions=0`；新增表 `source_entries` / `page_bindings`（均 0 行）；`media_artifacts` 0 行，但 8 张原图在 `managed/books/<book>/chapters/<chapter>/original/*.jpg` 且 `pages.managed_original_ref` 有值（Managed Copy 读路径仍可用）。

## 3. 关键结构性发现（比"缺模型"更根本）

provider 实例在**装配期**按 `pipeline_defaults` 行一次性构建（`core_assembly.py:1421-1426`，即 T-A AC8 的"配置变更需重启"）。因此：

- 只在 `StartRun.overrides.settings.providers.profiles` 里给 profile **不生效**：registry 的 `freeze_run_snapshots` 用装配期实例的 `config` 生成 `execution`，实测得到 `base_url="" / model="" / credential_ref=None` → `validate_provider_execution` 拒绝，StartRun 报 `RUN_SNAPSHOT_INCOMPLETE: provider replay configuration is incomplete or unsafe`。
- **正确做法**：先把 profile + bindings 写进 `pipeline_defaults`（DB 行），再启动 Core。本轮按此 seed 后 StartRun 即被接受。

## 4. 运行结果（真实输出）

```json
{"terminal":"completed_with_failures","counts":{"total":8,"completed":0,"failed":8,"skipped":0},
 "step_status":{"detect":{"failed":8}},
 "distinct (step,error_code)":[["detect","PROVIDER_NOT_CONFIGURED"]]}
```

- run_id `run-84394ff7494e43c5afad314074b56e8f`；`regions=0`、`region_revisions=0` ⇒ **`regions_translated_differs = 0`（无任何翻译产出）**。
- 卡在 `detect`：fixture 是 **0 region** 初始态，`translate_untranslated` 对 region-less 页先跑 `detect`；`manga-ocr` 只覆盖 OCR，**没有 detect provider 绑定**，故 8/8 死在 detect。

## 5. 已排除的假设

1. **"sidecar 缺模型"**：本轮完全绕开 sidecar（源码 Core），失败原因与模型无关（detect 连 provider 都没有）。
2. **"fixture 被污染"**：新目录 copy，迁移后 `regions=0` 未变。
3. **"Host/探针 payload 形状错"**：StartRun 被接受并产出真实 run/target 记录。
4. **"Credential 路径不通"**：尚未走到 translate 步，**未验证**（既不能确认也不能排除）。
5. **"profile 注入方式"**：已证明 run-level override 无效、必须 DB seed（§3）。

## 6. 下一步需要的条件（三条，任一即可推进）

- **A. 提供 detect provider**：给 `detect` 绑一个可用检测器（远程视觉模型或本地 ONNX + 模型文件），才能让 0-region 页走到 ocr→translate。
- **B. 预置 regions + OCR 文本**：直接 seed 区域与日文文本，改跑 `retranslate_region`（translate+render），跳过 detect/ocr。**需要 OCR 文本形状定义**（`regions.text_json` 的 key 约定）。
- **C. 本地 OCR 模型**：`manga-ocr` 需要模型文件（仓库内没有；0.1.1 发布包内有 detector，但那是 sidecar 资源）。

**未做产品代码改动**（只改探针与本次 work-root/DB 数据，均在工作区）。

## 7. 证据文件

- `l2-run.json`：StartRun → 轮询 → GetTaskProjection 的完整原始响应（无 key）
- `core-stderr.log`：源码 Core 的 stderr（含 T-B 新增的 `[core.run]` 精确原因行）
- `probe-console.log`、`profile-deepseek.json`（只含 `credential_ref`，不含 secret）