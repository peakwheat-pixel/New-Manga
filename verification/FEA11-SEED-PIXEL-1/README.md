# FEA11-SEED-PIXEL-1 证据

基线 `a482b9f36`。目标：让种子旧侧条目带 **pixel 画像**，使 matcher 能判 `changed`。

## 1. 改了什么

| 文件 | 改动 |
|---|---|
| `tests/fea11/conftest.py` | `add_source_tree` 新增可选参数 `pixel_profiles: dict[entry_id, dict]`；`source_entries` 的 INSERT 补上 `pixel_digest` / `pixel_digest_algorithm` / `orientation` / `decoder_name` / `decoder_version` / `decoder_params_json` 六列（此前完全没有写入）；**向后兼容**：不传时行为不变（仍按 `legacy_v7_evidence` 写 v7 形状） |
| `tests/fea11/support/ipc_seed.py` | 用**生产解码器** `application.sources.scanner._decode_pixel_profile(raw, budget)` 为 `old_entries` 计算真实画像后传入；`budget` 用 `SimpleNamespace(budget=SimpleNamespace(max_decode_bytes=0))`（`max_decode=0` 时 `_check_decode_budget` 直接跳过）；**若任一 entry 拿不到画像则 `SystemExit` 失败**，不静默降级 |

**为什么不是硬编码 digest**：`_decode_pixel_profile` 内部做 EXIF 归一化（`ImageOps.exif_transpose`）并按
`widthxheight\0rgb` 算 sha256 —— 硬编码会与生产路径不一致，测试就失去判别力。

## 2. 效果（带 opt-in，三类 13 个）

| 项 | 修复前 | 修复后 |
|---|---|---|
| `Fea11SourceIpcTests.FullSyncChain_…` | **FAIL**（`changed=0, ambiguous=1`） | **PASS** |
| 三类合计 | 11 passed / 2 failed | **12 passed / 1 failed** |

## 3. 判别力

把 `pixel_profiles=_old_pixel_profiles` 改成注释掉后重跑：
`Fea11SourceIpcTests.FullSyncChain_…` **重新变红**（`new container must produce a changed page`，已还原，`PROBE` 计数 0）。

⇒ 修复是**真的起作用**，不是巧合。

## 4. ★ 上一轮的"同族推断"被实测推翻

`FEA11-FULLSYNC-TRIAGE-1` 曾**推断** `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…`
与 `Fea11SourceIpcTests` 同因（并已标注"推断而非实测"）。**本轮实测证明不同因**：

```
NewManga.Host.Sources.SourceAccessException : SOURCE_ENTRY_MISSING
  at SourceReadCoordinator.DescribeContainer(String path, Int64 maxBytes) line 382
```

即失败发生在 **`DescribeContainer` 读容器**阶段，**不是** `changed` 断言，**与 pixel 画像无关**。
本轮的 pixel 修复**没有**让这个测试转绿（12/13 中它就是那 1 个）。

**教训（第二次同类）**：同族失败不能按"错误文本相似"推断同因，必须逐个复跑。

## 5. 未做

- `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…` 的 `SOURCE_ENTRY_MISSING` **未归因**。
- 未跑无夹具三项目全量（本次只改测试基础设施的 Python 侧，不改变 C# 测试集合）。
