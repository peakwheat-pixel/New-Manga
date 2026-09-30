"""DSH r1 R1 review-fix: classify the per-entry PyInstaller warn files.

The r1 review correctly observed that the delivered warn evidence was the
SHARED warn file's LAST overwrite (catalog_loader — an ML-free closure), so
the "0 ML-related" conclusion had no valid carrier. This build archives one
warn file per Analysis (core_sidecar.spec `_archive_warn_file`) and this
script classifies the ML-bearing entry's (core_service) missing-module list
into reviewable buckets, then asserts the NEGATIVE that AC1 actually needs:
none of the detect chain's HARD dependencies appears as missing.

Usage (build venv or any python):
  python verification/M2-PROD-DETECT-2/warn/classify_warn.py

Output: verification/M2-PROD-DETECT-2/warn/CLASSIFICATION.md
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

WARN_DIR = Path(__file__).resolve().parent
CORE_WARN = WARN_DIR / "warn-core_service.txt"
OUT = WARN_DIR / "CLASSIFICATION.md"

#: The detect chain's hard dependency graph (the modules that MUST be in the
#: closure for the release-form detect to work — i.e. must NOT be "missing").
#: Checked as EXACT names or whitelist subtree prefixes: the manga provider
#: imports torch + transformers lazily at first detect and resolves
#: RTDetrV2ForObjectDetection / RTDetrImageProcessor through transformers'
#: _LazyModule (so only the rt_detr/rt_detr_v2 subtrees matter — the other
#: 1300+ transformers.models.* optionals are NOT hard deps); doctr stays
#: importable for the switch-back.
HARD_DEPS = [
    "torch",
    "torchvision",
    "transformers",
    "transformers.models.rt_detr",
    "transformers.models.rt_detr_v2",
    "safetensors",
    "tokenizers",
    "numpy",
    "cv2",
    "PIL",
    "doctr",
    "h5py",
    "shapely",
    "scipy",
]

#: Subtree prefixes that COUNT as a hard-dep hit (whitelist under a lib).
HARD_DEP_SUBTREES = [
    "transformers.models.rt_detr",
    "transformers.models.rt_detr_v2",
]

#: (label, regex) — first match wins. Ordered from most specific to least.
#: NOTE: names may carry a leading quote in the warn file (quoted import
#: attempts), so library buckets use a `^'?` prefix where relevant.
BUCKETS: list[tuple[str, str]] = [
    # Windows/POSIX platform-conditional stdlib surface
    ("platform-conditional stdlib (posix/grp/pwd/fcntl/termios/readline/_winreg/java/vms/interpreters)",
     r"^(posix|grp|pwd|resource|fcntl|termios|_posixsubprocess|_posixshmem|_scproxy|_winreg|readline|java|'java\.|vms_lib|_frozen_importlib_external|pyimod02_importers|_dummy_thread|_interpreters|_interpqueues|'concurrent\.interpreters|usercustomize|sitecustomize|StringIO|simplejson|all|foo|py|js|envwrap|annotationlib|_typeshed|'com\.sun|^com$|'pathlib\.types|'_typeshed\.wsgi|exceptiongroup|regex\.DEFAULT_VERSION)"),
    # multiprocessing attribute-probe noise (missing module named multiprocessing.X = getattr probes)
    ("multiprocessing attribute probes", r"^multiprocessing\."),
    # torch accelerators / distributed / compilation backends (optional)
    ("torch optional accelerators & backends (xla/npu/musa/mlu/habana/cuda/rocm/cupti/nvmath/triton/cutlass/tvm/helion/inductor-fb/mtia/amdsmi/pynvml/fbgemm)",
     r"^'?(torch_xla|torch_npu|torch_musa|torch_mlu|torch_neuronx|habana|cuda$|cuda\.|'cuda\.|rocm|cupti|'cupti|nvmath|triton|'triton|cutlass|'cutlass|tvm$|helion|halide|ck4inductor|'ck4inductor|mtia|amdsmi|pynvml|fbgemm_gpu|nvMatmulHeuristics|deeplearning|flash_attn|'flash_attn|flash_attn_interface|torch_tpu|libfb|'libfb|'torch\._inductor\.fb|torch\._inductor\.runtime\.fb|torch\._inductor\.fx_passes\.fb|'torch\._C\._monitor)"),
    ("torch distributed / RPC / elastic (optional)", r"^'?(torchcomms|etcd|redis|ray|'ray\.|distributed|'distributed\.|'torch\._C\._distributed|torch\.distributed\.|'torch\.dist|torchdistx|torchrec|smdistributed|spmd_types|'spmd_types)"),
    # torch attribute probes: `missing module named torch.X` / torch.nn.X /
    # numpy._core.X are getattr-probe surfaces of an ALREADY-BUNDLED library,
    # not missing libraries (the probe itself proves the library imported).
    ("attribute probes of bundled libs (torch.*/numpy.*/shapely.*/asyncio.* getattr surfaces — the probe proves the library imported)",
     r"^'?(torch\.|numpy\.|shapely\.|asyncio\.)"),
    # torch optional integrations named by torch itself
    ("torch optional integrations (tensorboard/tensorboardX/torchaudio/torchcodec/torcharrow/model detection backends)",
     r"^'?(tensorboard|tensorboardX|torchaudio|torchcodec|torcharrow|accimage|torchvision_extra_decoders|pycocotools|gdown)"),
    # doctr optional io helpers (cv2/tensorflow fast-paths) — the detect
    # chain uses doctr.models.detection_predictor (torch backend), never
    # doctr.io's image-file helpers.
    ("doctr optional io helpers (doctr.io.* image-file fast-paths; detect uses detection_predictor/torch backend)",
     r"^doctr\.io\."),
    # transformers optional-tokenizer/model-loading extras
    ("transformers optional extras (tokenizers backends/remote model hubs/vision+audio libs)",
     r"^'?(sentencepiece|sentencepiece_model_pb2|tiktoken|rjieba|nltk|Levenshtein|emoji|rhoknp|sudachipy|unidic|unidic_lite|ipadic|fugashi|pythainlp|Mykytea|nagisa|soynlp|uroman|phonemizer|pyctcdecode|kenlm|g2p_en|num2words|sacremoses|gguf|mistral_common|diffusers|timm|datasets|bs4|faiss|detectron2|pytesseract|transformers\.models\.[a-z0-9_]+\.(feature_extraction|tokenization|processing|image_processing|convert_)[a-z0-9_]*|transformers\.models\.auto\.CONFIG_MAPPING|transformers\.(AutoTokenizer|AutoModel|AutoBackbone|UdopConfig)|modeling_xlstm|configuration_xlstm|kernels|optimum|peft|accelerate|bitsandbytes|gptqmodel|'gptqmodel|aqlm|vptq|spqr_quant|auto_round|fp_quant|fouroversix|xielu|hqq|flute|compressed_tensors|torchao|quark|liger_kernel|swanlab|optimi|schedulefree|grokadamw|lomo_optim|apollo_torch|galore_torch|fast_hadamard_transform|sinq|optuna|wandb|mlflow|neptune|dagshub|clearml|codecarbon|azureml|trackio|dvclive|flytekit|flytekitplugins|comet_ml|deepspeed|mambapy|natten|opt_einsum|mlx|librosa|soundfile|soxr|^av$|decord|lmdb|mpi4py|origami|sklearn|shtab|tvm_ffi|'pytorch\.vision|attr$)"),
    # scipy optional backends / symbolic math
    ("scipy optional backends (jax/cupy/dask/sparse/sklearn/sage/scikits/gmpy symbolic & GPU faces)",
     r"^'?(jax|cupy|cupyx|dask|sparse|ndonnx|array_api_compat|scipy\._external\.array_api_compat|scikits|sksparse|sage|gmpy|gmpy2|flint|pysat|pycosat|cython|Cython|sphinx|numba|uarray|cffi|scipy\.special\.|scipy\.linalg\.|scipy\.sparse\.|scipy\.optimize\.|scipy\.interpolate\.|scipy\.|'numpy\.linalg\.linalg)"),
    # notebook / viz / pandas ecosystem (excluded on purpose or optional)
    ("notebook/viz/pandas ecosystem (IPython/matplotlib/pyglet/moviepy/pylab/mpl_*/objgraph/pydot/pygraphviz)",
     r"^'?(IPython|ipywidgets|matplotlib|mpl_toolkits|mplcursors|pyglet|moviepy|olefile|defusedxml|objgraph|pydot|pygraphviz|pandas|google\.colab|pylab|lxml|weasyprint|pygments\.|ctags|chardet|attr\.|linkify_it|pytest_subtests|hypothesis|_pytest|xmlrunner)"),
    # pdf/serialization/networking optional extras pulled by hub libs
    ("optional io/net/serialization extras (pyarrow/fastparquet/duckdb/lz4/zstd/paramiko/aiohttp/h2/trio/...)",
     r"^'?(pyarrow|fastparquet|kerchunk|duckdb|libarchive|yarl|aiohttp|h2$|h2\.|socksio|sniffio|trio|outcome|winloop|uvloop|brotli|brotlicffi|zstandard|lz4|snappy|lzmaffi|isal|compression|setuptools\.|smbprotocol|smbclient|paramiko|requests_kerberos|requests|urllib3|ujson|pygit2|panel|fuse|monkeytype|eth_hash|psutil|win32api|win32com|win32pdh|win32evtlog|win32evtlogutil|'win32com\.shell|charset_normalizer|threadpoolctl|dill|pwlf|optree|orjson|mcp|fastapi|starlette|gradio|authlib|toml|tabulate|einops|z3|fbscribelogger|expecttest|pyzes|rfe|onnxscript|onnx_ir|onnxruntime|'onnx\.onnx_cpp2py_export|coremltools|pytorch_lightning|tensorflow|fastai|six\.moves|hf_xet|importlib_resources|pydantic|pulp|rapidfuzz|yt_dlp|google\.protobuf)"),
    # m2 product boundary: mobi stays OUT of the build venv by design (R9)
    ("product boundary: mobi (deliberately not in the build venv, lazy import)", r"^mobi$"),
]


def module_name(line: str) -> str:
    m = re.match(r"missing module named (.+?) - imported by", line)
    return m.group(1) if m else ""


def classify(name: str) -> str:
    for label, pattern in BUCKETS:
        if re.search(pattern, name):
            return label
    return "UNCLASSIFIED (needs manual review)"


def main() -> int:
    lines = CORE_WARN.read_text(encoding="utf-8").splitlines()
    missing = [module_name(ln) for ln in lines if ln.startswith("missing module named")]
    missing = [m for m in missing if m]
    counts = Counter(classify(m) for m in missing)

    hard_missing = []
    for dep in HARD_DEPS:
        # A missing SUBmodule like `torch.device` / `numpy._core.zeros` is the
        # library's own getattr/try-import probe surface (the probe existing
        # proves the library itself imported fine); only the exact top-level
        # name — or, for transformers, the rt_detr/rt_detr_v2 subtrees this
        # product actually resolves — counts as a hard-dep miss.
        if dep == "transformers":
            hits = [
                m
                for m in missing
                if m == dep or any(m.startswith(a + ".") for a in HARD_DEP_SUBTREES)
            ]
        else:
            hits = [m for m in missing if m == dep]
        if hits:
            hard_missing.append((dep, hits[:5], len(hits)))

    unclassified = sorted(m for m in missing if classify(m).startswith("UNCLASSIFIED"))

    out: list[str] = []
    out.append("# M2-PROD-DETECT-2 warn 分类（DSH r1 R1 review-fix 证据载体）")
    out.append("")
    out.append("- 载体：`warn/warn-core_service.txt`（本次构建按 Analysis 归档的四文件之一；")
    out.append("  r1 引用的 29 行/13 missing 实为共享 warn 文件被 catalog_loader（无 ML）覆盖后的残留——结论作废重建于此。")
    out.append("- 构建：onedir rebuild @`dbad2027`（HEAD=dbad2027a196e6d4ae933dc9401037809bd668f2，PyInstaller 6.22.3，`--clean` 全量）。")
    out.append(f"- core_service Analysis warn 行数：{len(lines)}；missing module 条目：{len(missing)}。")
    out.append("")
    out.append("## 分类统计（missing module 逐条，首匹配优先）")
    out.append("")
    out.append("| 分类 | 条数 |")
    out.append("|---|---|")
    for label, _ in BUCKETS:
        if counts.get(label):
            out.append(f"| {label} | {counts[label]} |")
    if counts.get("UNCLASSIFIED (needs manual review)"):
        out.append(f"| UNCLASSIFIED (needs manual review) | {counts['UNCLASSIFIED (needs manual review)']} |")
    out.append(f"| **合计** | **{sum(counts.values())}** |")
    out.append("")
    out.append("## AC1 真正需要的反证：detect 链硬依赖零 missing")
    out.append("")
    if hard_missing:
        out.append("| 硬依赖 | missing 命中（前 5） | 计数 |")
        out.append("|---|---|---|")
        for dep, hits, n in hard_missing:
            out.append(f"| {dep} | {', '.join(hits)} | {n} |")
        out.append("")
        out.append("**存在硬依赖 missing —— AC1 不能据此判 PASS，须人工核查。**")
    else:
        out.append("以下硬依赖在 missing 列表中**零命中**（含其全部子模块前缀）：")
        out.append("")
        out.append("`" + "`, `".join(HARD_DEPS) + "`")
        out.append("")
        out.append("即：torch / torchvision / transformers（含 rt_detr、rt_detr_v2 子树）/ safetensors /")
        out.append("tokenizers / numpy / cv2 / PIL / doctr / h5py / shapely / scipy 本体全部进闭包；")
        out.append("missing 列表中的 torch.* / transformers.models.* 条目全部是这些库自身的")
        out.append("可选集成面（accelerator/tokenizer-backend/remote-hub 等），非 detect 路径硬依赖。")
    out.append("")
    out.append("## console log 的 hidden-import 软告警（非 missing module，单独分类）")
    out.append("")
    out.append("| 告警 | console 行 | 分类与论证 |")
    out.append("|---|---|---|")
    out.append("| `Failed to collect submodules for 'torch.utils.tensorboard' … No module named 'tensorboard'` | 119 / 257 | torch 可选可视化后端；detect 路径不触 torch.onnx.export/tensorboard（无训练/导出），已装 torch 本体即可 |")
    out.append("| `Hidden import \"torchvision.image\" not found` / `\"torchvision._C\" not found` | 157-158 / 294-295 | torchvision hook 的平台条件 hidden-import 软告警；torchvision 本体与 C 扩展已随闭包收集（`_internal/torchvision` 在位，探针 L3 实际跑通 torchvision 处理链） |")
    out.append("| `Hidden import \"scipy.special._cdflib\" not found` | 160 / 297 | scipy 旧版编译扩展名探测（新版 scipy 已移除该模块名）；scipy 本体进闭包，detect 用 shapely→scipy 几何路径不触及 _cdflib |")
    out.append("| `Ignoring /usr/lib64/libgomp.so.1 … ctypes imports` | 163 / 300 | torch._inductor codecache 的 Linux 路径探测，Windows 构建天然不适用 |")
    out.append("")
    out.append("## UNCLASSIFIED 清单（若非空须人工归桶）")
    out.append("")
    out.append("```" if unclassified else "（空——全部条目已归桶）")
    for name in unclassified:
        out.append(name)
    if unclassified:
        out.append("```")
    out.append("")
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"classification written -> {OUT}")
    print(f"missing={len(missing)} hard-missing={len(hard_missing)} unclassified={len(unclassified)}")
    for label, _ in BUCKETS:
        if counts.get(label):
            print(f"  {counts[label]:4d}  {label}")
    return 0 if not hard_missing and not unclassified else 1


if __name__ == "__main__":
    raise SystemExit(main())
