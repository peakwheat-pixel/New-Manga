# M2-PROD-DETECT-2 warn 分类（DSH r1 R1 review-fix 证据载体）

- 载体：`warn/warn-core_service.txt`（本次构建按 Analysis 归档的四文件之一；
  r1 引用的 29 行/13 missing 实为共享 warn 文件被 catalog_loader（无 ML）覆盖后的残留——结论作废重建于此。
- 构建：onedir rebuild @`dbad2027`（HEAD=dbad2027a196e6d4ae933dc9401037809bd668f2，PyInstaller 6.22.3，`--clean` 全量）。
- core_service Analysis warn 行数：979；missing module 条目：958。

## 分类统计（missing module 逐条，首匹配优先）

| 分类 | 条数 |
|---|---|
| platform-conditional stdlib (posix/grp/pwd/fcntl/termios/readline/_winreg/java/vms/interpreters) | 58 |
| multiprocessing attribute probes | 10 |
| torch optional accelerators & backends (xla/npu/musa/mlu/habana/cuda/rocm/cupti/nvmath/triton/cutlass/tvm/helion/inductor-fb/mtia/amdsmi/pynvml/fbgemm) | 72 |
| torch distributed / RPC / elastic (optional) | 30 |
| attribute probes of bundled libs (torch.*/numpy.*/shapely.*/asyncio.* getattr surfaces — the probe proves the library imported) | 320 |
| torch optional integrations (tensorboard/tensorboardX/torchaudio/torchcodec/torcharrow/model detection backends) | 13 |
| doctr optional io helpers (doctr.io.* image-file fast-paths; detect uses detection_predictor/torch backend) | 2 |
| transformers optional extras (tokenizers backends/remote model hubs/vision+audio libs) | 180 |
| scipy optional backends (jax/cupy/dask/sparse/sklearn/sage/scikits/gmpy symbolic & GPU faces) | 94 |
| notebook/viz/pandas ecosystem (IPython/matplotlib/pyglet/moviepy/pylab/mpl_*/objgraph/pydot/pygraphviz) | 50 |
| optional io/net/serialization extras (pyarrow/fastparquet/duckdb/lz4/zstd/paramiko/aiohttp/h2/trio/...) | 128 |
| product boundary: mobi (deliberately not in the build venv, lazy import) | 1 |
| **合计** | **958** |

## AC1 真正需要的反证：detect 链硬依赖零 missing

以下硬依赖在 missing 列表中**零命中**（含其全部子模块前缀）：

`torch`, `torchvision`, `transformers`, `transformers.models.rt_detr`, `transformers.models.rt_detr_v2`, `safetensors`, `tokenizers`, `numpy`, `cv2`, `PIL`, `doctr`, `h5py`, `shapely`, `scipy`

即：torch / torchvision / transformers（含 rt_detr、rt_detr_v2 子树）/ safetensors /
tokenizers / numpy / cv2 / PIL / doctr / h5py / shapely / scipy 本体全部进闭包；
missing 列表中的 torch.* / transformers.models.* 条目全部是这些库自身的
可选集成面（accelerator/tokenizer-backend/remote-hub 等），非 detect 路径硬依赖。

## console log 的 hidden-import 软告警（非 missing module，单独分类）

| 告警 | console 行 | 分类与论证 |
|---|---|---|
| `Failed to collect submodules for 'torch.utils.tensorboard' … No module named 'tensorboard'` | 119 / 257 | torch 可选可视化后端；detect 路径不触 torch.onnx.export/tensorboard（无训练/导出），已装 torch 本体即可 |
| `Hidden import "torchvision.image" not found` / `"torchvision._C" not found` | 157-158 / 294-295 | torchvision hook 的平台条件 hidden-import 软告警；torchvision 本体与 C 扩展已随闭包收集（`_internal/torchvision` 在位，探针 L3 实际跑通 torchvision 处理链） |
| `Hidden import "scipy.special._cdflib" not found` | 160 / 297 | scipy 旧版编译扩展名探测（新版 scipy 已移除该模块名）；scipy 本体进闭包，detect 用 shapely→scipy 几何路径不触及 _cdflib |
| `Ignoring /usr/lib64/libgomp.so.1 … ctypes imports` | 163 / 300 | torch._inductor codecache 的 Linux 路径探测，Windows 构建天然不适用 |

## UNCLASSIFIED 清单（若非空须人工归桶）

（空——全部条目已归桶）
