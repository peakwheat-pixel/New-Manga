"""AC1：样本 manifest schema（dataclass + JSON Schema 双落地）。

标注目标口径冻结（决策记录，见 README §口径冻结）：
GT = sfx 实例包络（instance envelope，含遮挡推断），非字形像素 mask。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

ANNOTATION_STATUSES = ("complete", "partial", "pseudo", "synthetic")
SPLITS = ("train", "val", "test", "challenge", "unassigned")
SPLIT_CLASSES = ("train", "val", "test", "challenge")
BOX_CLASSES = ("sfx",)
PROVENANCE_TYPES = ("asset_case", "synthetic_render", "derived", "external_model")


class SchemaError(ValueError):
    """样本记录校验失败。"""


@dataclass
class ImageRef:
    """图引用：路径 + sha256 + 尺寸。"""

    path: str
    sha256: str
    width: int
    height: int


@dataclass
class BoxAnnotation:
    """一个 sfx 实例包络：多边形（>=4 点）+ 类 + 可选文本 + 遮挡标记。"""

    polygon: list[list[float]]
    cls: str = "sfx"
    text: Optional[str] = None
    occluded: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.cls not in BOX_CLASSES:
            errors.append(f"box.cls={self.cls!r} 不在 {BOX_CLASSES}")
        if len(self.polygon) < 4:
            errors.append(f"polygon 至少 4 点，得 {len(self.polygon)}")
        for i, pt in enumerate(self.polygon):
            if len(pt) != 2 or not all(isinstance(v, (int, float)) for v in pt):
                errors.append(f"polygon[{i}] 非二维数值点: {pt!r}")
        return errors


@dataclass
class SampleRecord:
    """单样本 manifest 记录（AC1 冻结字段集）。"""

    sample_id: str
    image: ImageRef
    boxes: list[BoxAnnotation]
    annotation_status: str
    provenance: dict[str, Any]
    group: str
    split: str = "unassigned"
    created_at: str = ""
    schema_version: str = "sfx-data-infra/sample@1"
    notes: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.sample_id:
            errors.append("sample_id 为空")
        if self.annotation_status not in ANNOTATION_STATUSES:
            errors.append(f"annotation_status={self.annotation_status!r} 不在 {ANNOTATION_STATUSES}")
        if self.split not in SPLITS:
            errors.append(f"split={self.split!r} 不在 {SPLITS}")
        if not self.group:
            errors.append("group 为空")
        if not self.created_at:
            errors.append("created_at 为空")
        prov_type = self.provenance.get("type") if isinstance(self.provenance, dict) else None
        if prov_type not in PROVENANCE_TYPES:
            errors.append(f"provenance.type={prov_type!r} 不在 {PROVENANCE_TYPES}")
        if not (isinstance(self.image.sha256, str) and len(self.image.sha256) == 64):
            errors.append(f"image.sha256 非合法 sha256 hex: {self.image.sha256!r}")
        if self.image.width <= 0 or self.image.height <= 0:
            errors.append(f"image 尺寸非法: {self.image.width}x{self.image.height}")
        if not self.boxes:
            errors.append("boxes 为空（v1 manifest 只收正样本）")
        for i, box in enumerate(self.boxes):
            for e in box.validate():
                errors.append(f"boxes[{i}].{e}")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "sample_id": self.sample_id,
            "image": {
                "path": self.image.path,
                "sha256": self.image.sha256,
                "width": self.image.width,
                "height": self.image.height,
            },
            "boxes": [
                {
                    "polygon": [list(pt) for pt in box.polygon],
                    "cls": box.cls,
                    "text": box.text,
                    "occluded": box.occluded,
                }
                for box in self.boxes
            ],
            "annotation_status": self.annotation_status,
            "provenance": dict(self.provenance),
            "group": self.group,
            "split": self.split,
            "created_at": self.created_at,
            **({"notes": self.notes} if self.notes else {}),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SampleRecord":
        rec = cls(
            sample_id=d["sample_id"],
            image=ImageRef(
                path=d["image"]["path"],
                sha256=d["image"]["sha256"],
                width=d["image"]["width"],
                height=d["image"]["height"],
            ),
            boxes=[
                BoxAnnotation(
                    polygon=[list(pt) for pt in b["polygon"]],
                    cls=b.get("cls", "sfx"),
                    text=b.get("text"),
                    occluded=bool(b.get("occluded", False)),
                )
                for b in d["boxes"]
            ],
            annotation_status=d["annotation_status"],
            provenance=dict(d["provenance"]),
            group=d["group"],
            split=d.get("split", "unassigned"),
            created_at=d["created_at"],
            schema_version=d.get("schema_version", "sfx-data-infra/sample@1"),
            notes=d.get("notes", ""),
        )
        errors = rec.validate()
        if errors:
            raise SchemaError(f"sample {rec.sample_id}: " + "; ".join(errors))
        return rec


def make_json_schema() -> dict[str, Any]:
    """生成与 dataclass 等价的 JSON Schema（draft-07）。

    运行时不依赖 jsonschema 库（零新依赖）；schema.json 为互操作/文档落地，
    运行时校验走 SampleRecord.validate()。测试断言两者字段集一致。
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "sfx-data-infra/sample@1",
        "title": "SFX sample manifest record",
        "type": "object",
        "required": [
            "schema_version",
            "sample_id",
            "image",
            "boxes",
            "annotation_status",
            "provenance",
            "group",
            "split",
            "created_at",
        ],
        "properties": {
            "schema_version": {"const": "sfx-data-infra/sample@1"},
            "sample_id": {"type": "string", "minLength": 1},
            "image": {
                "type": "object",
                "required": ["path", "sha256", "width", "height"],
                "properties": {
                    "path": {"type": "string"},
                    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "width": {"type": "integer", "minimum": 1},
                    "height": {"type": "integer", "minimum": 1},
                },
                "additionalProperties": False,
            },
            "boxes": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["polygon", "cls"],
                    "properties": {
                        "polygon": {
                            "type": "array",
                            "minItems": 4,
                            "items": {
                                "type": "array",
                                "minItems": 2,
                                "maxItems": 2,
                                "items": {"type": "number"},
                            },
                        },
                        "cls": {"enum": list(BOX_CLASSES)},
                        "text": {"type": ["string", "null"]},
                        "occluded": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            },
            "annotation_status": {
                "enum": list(ANNOTATION_STATUSES),
                "description": "complete=人工精确; partial=人工核验但近似框; pseudo=模型产出未经人工确认; synthetic=程序合成精确 GT",
            },
            "provenance": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"enum": list(PROVENANCE_TYPES)},
                },
            },
            "group": {"type": "string", "minLength": 1},
            "split": {"enum": list(SPLITS)},
            "created_at": {"type": "string", "format": "date-time"},
            "notes": {"type": "string"},
        },
        "additionalProperties": False,
    }
