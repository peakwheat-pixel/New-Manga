
import json, sys
from pathlib import Path

src_root, weights_path, out_path = sys.argv[1:4]
sys.path.insert(0, src_root)

import importlib.metadata as md
versions = {}
for dist in ("torch", "torchvision", "transformers", "safetensors", "python-doctr"):
    try:
        versions[dist] = md.version(dist)
    except Exception:
        versions[dist] = None

from infrastructure.providers.detection_doctr import DoctrDetectionProvider
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderNotConfigured

# A minimal 4x4 rgb24 frame: passes the pure-Python input validate gate so
# the failure lands on the WEIGHTS check (the thing under test), not on
# input validation.
frame = bytes(4 * 4 * 3)
request = DetectionRequest(page_id="probe-doctr-absent", image_bytes=frame, width=4, height=4)

provider = DoctrDetectionProvider(weights_path=Path(weights_path), device="cpu")
try:
    provider.detect(request)
    payload = {
        "exit": 1,
        "outcome": "no_error",
        "message": "detect did NOT fail closed on the absent doctr weights",
    }
except ProviderNotConfigured as error:
    payload = {
        "exit": 0,
        "outcome": "typed_not_configured",
        "error_code": getattr(error, "error_code", None),
        "provider_id": getattr(provider, "provider_id", None),
        "message_head": str(error)[:240],
    }
except Exception as error:  # noqa: BLE001 - any other shape is a FAIL
    payload = {
        "exit": 1,
        "outcome": "untyped_error",
        "error_class": type(error).__name__,
        "message_head": str(error)[:240],
    }
Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
