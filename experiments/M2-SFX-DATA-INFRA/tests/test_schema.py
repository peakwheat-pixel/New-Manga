"""附加单测：schema 往返与 JSON Schema 双落地一致性。"""

from __future__ import annotations

import pytest

from sfx_data_infra.schema import (
    ANNOTATION_STATUSES,
    SPLITS,
    SchemaError,
    SampleRecord,
    make_json_schema,
)


def _sample(**over):
    from sfx_data_infra.schema import BoxAnnotation, ImageRef

    d = {
        "sample_id": "x-1",
        "image": ImageRef(path="a.png", sha256="b" * 64, width=10, height=10),
        "boxes": [BoxAnnotation(polygon=[[0, 0], [5, 0], [5, 5], [0, 5]], text="ドン")],
        "annotation_status": "partial",
        "provenance": {"type": "asset_case", "case_id": "BJ06"},
        "group": "densho810/vol03",
        "created_at": "2026-10-04T00:00:00+00:00",
    }
    d.update(over)
    return SampleRecord(**d)


def test_to_from_dict_roundtrip():
    s = _sample()
    assert SampleRecord.from_dict(s.to_dict()) == s


def test_validate_flags_bad_status_and_split():
    with pytest.raises(SchemaError):
        SampleRecord.from_dict(_sample(annotation_status="guess").to_dict())
    with pytest.raises(SchemaError):
        SampleRecord.from_dict(_sample(split="holdout").to_dict())
    assert set(SPLITS) >= {"train", "val", "test", "challenge"}
    assert set(ANNOTATION_STATUSES) == {"complete", "partial", "pseudo", "synthetic"}


def test_json_schema_matches_dataclass_enums():
    js = make_json_schema()
    assert js["properties"]["annotation_status"]["enum"] == list(ANNOTATION_STATUSES)
    assert js["properties"]["split"]["enum"] == list(SPLITS)
    assert js["properties"]["image"]["required"] == ["path", "sha256", "width", "height"]
    assert js["properties"]["boxes"]["items"]["properties"]["cls"]["enum"] == ["sfx"]


def test_schema_json_file_matches_generator():
    """AC1 双落地：盘上 schema.json 与 make_json_schema() 生成物一致。"""
    import json
    from pathlib import Path

    schema_file = Path(__file__).resolve().parents[1] / "schema.json"
    on_disk = json.loads(schema_file.read_text(encoding="utf-8"))
    assert on_disk == make_json_schema()


def test_empty_boxes_rejected():
    from sfx_data_infra.schema import SampleRecord as SR

    s = _sample()
    s.boxes = []
    with pytest.raises(SchemaError):
        SR.from_dict(s.to_dict())
