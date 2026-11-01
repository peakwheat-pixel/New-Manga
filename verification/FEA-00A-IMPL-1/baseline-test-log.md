# FEA-00A 修复前测试基线

日期：2026-11-01（worktree HEAD c7b9d59e6b55b262c7523fe9dc24b2dbc331afbd）

执行环境：临时 uv cache 位于本 evidence 目录；`uv run --no-project` 装入项目已声明的 `pytest==9.1.1`、`pillow==12.3.0`、`pypdfium2==5.13.0`、`mobi==0.4.1` 与 numpy。未修改项目依赖声明。

命令：

```powershell
uv run --no-project --cache-dir verification/FEA-00A-IMPL-1/.uv-cache --with pytest==9.1.1 --with pillow==12.3.0 --with pypdfium2==5.13.0 --with mobi==0.4.1 --with numpy python -m pytest -q tests/core/test_bootstrap.py tests/core/test_page_catalog_modes.py tests/core/test_core_assembly.py tests/core/test_core_detect.py tests/core/test_sfx_assembly.py tests/core/test_sfx_policy_settings.py tests/pipeline/test_regionless_rebinding.py tests/pipeline/test_pipeline_production_seam.py tests/providers/test_detect_handler.py tests/providers/test_full_chain.py tests/providers/test_handlers_pipeline.py tests/providers/test_retype_redetect_persistence.py
```

结果：**180 passed，0 failed，0 skipped**，17.71 秒；EXIT=0。

基线执行头补充：Windows Node child_process 直接启动 uv（shell=none），当时未捕获该次 uv 临时环境的精确 Python executable 路径；因此不能追填为当前测试路径。修后 PowerShell/解释器路径已在 final-pytest-log.txt 与逐文件日志中记录。

AC8 修前 outcome 对照：

| 文件 | 修前结果 | 分类 |
|---|---:|---|
| `tests/core/test_bootstrap.py` | passed（纳入 180） | outcome 对照 |
| `tests/core/test_page_catalog_modes.py` | passed（纳入 180） | outcome 对照 |
| `tests/pipeline/test_regionless_rebinding.py` | passed（纳入 180） | outcome 对照 |
| `tests/providers/t111_support.py` | 不单独执行 | 适配文件，非 outcome 对照 |
| `tests/providers/test_detect_handler.py` | passed（纳入 180） | outcome 对照 |
| `tests/providers/test_full_chain.py` | passed（纳入 180） | outcome 对照 |
| `tests/providers/test_handlers_pipeline.py` | passed（纳入 180） | outcome 对照 |
| `tests/providers/test_retype_redetect_persistence.py` | passed（纳入 180） | outcome 对照 |

额外覆盖 core assembly 接线影响面：`test_core_assembly.py`、`test_core_detect.py`、`test_sfx_assembly.py`、`test_sfx_policy_settings.py`、`test_pipeline_production_seam.py` 也在同一命令内，全部通过。
