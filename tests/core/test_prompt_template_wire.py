"""FEA-14-AI-1: Core wire face for prompt templates (PREQ AI P21-P25)."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR, PROTOCOL_MINOR, PROTOCOL_NAME, CoreServiceServer, assemble_production_core,
)
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore, initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402


def _rpc(server: CoreServiceServer, command: str, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": PROTOCOL_NAME, "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "ai-wire", "command": command, "payload": payload,
    })
    return server.dispatch_request(raw)[0]


def _server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    server = CoreServiceServer(
        core, stdout=io.StringIO(),
        render_previews=RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db)),
    )
    return core, server


def test_prompt_template_wire_roundtrip(tmp_path):
    core, server = _server(tmp_path)

    listed = _rpc(server, "ListPromptTemplates", {})
    assert listed["error"] is None
    templates = listed["result"]["templates"]
    assert listed["result"]["builtin_count"] == len([t for t in templates if t["builtin"]])
    assert listed["result"]["builtin_count"] >= 1
    assert all(set(template) == {"template_id", "name", "version", "builtin"} for template in templates)

    created = _rpc(server, "SavePromptTemplate", {"name": "Wire template", "body": "Translate."})
    assert created["error"] is None
    template_id = created["result"]["template_id"]
    assert created["result"]["version"] == 1

    updated = _rpc(server, "SavePromptTemplate", {
        "template_id": template_id, "name": "Wire template v2", "body": "Translate better.",
    })
    assert updated["error"] is None
    assert updated["result"]["template_id"] == template_id
    assert updated["result"]["version"] == 2

    duplicate = _rpc(server, "SavePromptTemplate", {"name": "Wire template v2", "body": "x"})
    assert duplicate["error"] is not None
    assert duplicate["error"]["code"] == "TEMPLATE_NAME_EXISTS"
    assert duplicate["error"]["category"] == "conflict"

    builtin_id = next(t["template_id"] for t in templates if t["builtin"])
    copied = _rpc(server, "CopyBuiltinPromptTemplate", {"builtin_id": builtin_id})
    assert copied["error"] is None
    copy_id = copied["result"]["template_id"]
    assert copy_id != builtin_id
    named_copy = _rpc(server, "CopyBuiltinPromptTemplate", {"builtin_id": builtin_id, "name": "Named copy"})
    assert named_copy["error"] is None

    references = _rpc(server, "GetPromptTemplateReferences", {"template_id": template_id})
    assert references["error"] is None and references["result"] == {"references": []}

    deleted = _rpc(server, "DeletePromptTemplate", {
        "template_id": template_id, "replacement_id": copy_id,
    })
    assert deleted["error"] is None and deleted["result"] == {"deleted": True}
    remaining, _ = core.prompt_templates.list_templates()
    assert template_id not in {item["template_id"] for item in remaining}


def test_prompt_template_wire_errors_are_typed(tmp_path):
    core, server = _server(tmp_path)

    bad_list = _rpc(server, "ListPromptTemplates", {"extra": 1})
    assert bad_list["error"] is not None and bad_list["error"]["code"] == "INVALID_REQUEST"

    for payload in (
        {"name": "", "body": "x"},
        {"name": "n", "body": ""},
        {"name": 5, "body": "x"},
        {"template_id": "", "name": "n", "body": "x"},
    ):
        response = _rpc(server, "SavePromptTemplate", payload)
        assert response["error"] is not None, payload
        assert response["error"]["code"] == "INVALID_REQUEST", (payload, response["error"])

    unknown_update = _rpc(server, "SavePromptTemplate", {
        "template_id": "nope", "name": "n", "body": "x",
    })
    assert unknown_update["error"]["code"] == "TARGET_NOT_FOUND"

    listed = _rpc(server, "ListPromptTemplates", {})["result"]["templates"]
    builtin_id = next(t["template_id"] for t in listed if t["builtin"])
    builtin_save = _rpc(server, "SavePromptTemplate", {
        "template_id": builtin_id, "name": "Hijack", "body": "x",
    })
    assert builtin_save["error"]["code"] == "INVALID_REQUEST"

    unknown_copy = _rpc(server, "CopyBuiltinPromptTemplate", {"builtin_id": "nope"})
    assert unknown_copy["error"]["code"] == "TARGET_NOT_FOUND"

    template = _rpc(server, "SavePromptTemplate", {"name": "Del", "body": "b"})["result"]
    missing_replacement = _rpc(server, "DeletePromptTemplate", {"template_id": template["template_id"]})
    assert missing_replacement["error"]["code"] == "INVALID_REQUEST"
    self_replacement = _rpc(server, "DeletePromptTemplate", {
        "template_id": template["template_id"], "replacement_id": template["template_id"],
    })
    assert self_replacement["error"]["code"] == "INVALID_REQUEST"
    unknown_replacement = _rpc(server, "DeletePromptTemplate", {
        "template_id": template["template_id"], "replacement_id": "nope",
    })
    assert unknown_replacement["error"]["code"] == "TARGET_NOT_FOUND"

    missing_refs = _rpc(server, "GetPromptTemplateReferences", {"template_id": "nope"})
    assert missing_refs["error"]["code"] == "TARGET_NOT_FOUND"
    builtin_refs = _rpc(server, "GetPromptTemplateReferences", {"template_id": builtin_id})
    assert builtin_refs["error"] is None and builtin_refs["result"] == {"references": []}
