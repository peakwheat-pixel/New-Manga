"""附加单测：dhash/框哈希/去重 + 导入器纯函数。"""

from __future__ import annotations

import numpy as np
from PIL import Image

from sfx_data_infra.dedup import drop_duplicates, find_duplicates
from sfx_data_infra.hash import box_exact_hash, dhash_image, hamming_distance
from sfx_data_infra.importers import (
    bbox_to_polygon,
    page_filename_for_case,
    parse_ogkalu_region_key,
    xyxy_to_polygon,
)


def _noise_img(seed: int, size=(64, 64)):
    rng = np.random.default_rng(seed)
    return Image.fromarray(rng.integers(0, 256, size=size, dtype=np.uint8).repeat(3, axis=2)[:, :, :3], "RGB")


def test_dhash_stable_and_discriminative():
    a = _noise_img(1)
    assert dhash_image(a) == dhash_image(a.copy())
    b = _noise_img(2)
    assert hamming_distance(dhash_image(a), dhash_image(b)) > 8, "不同噪声图汉明距离应明显"
    assert hamming_distance(dhash_image(a), dhash_image(a)) == 0


def test_dhash_robust_to_resize():
    a = _noise_img(7).resize((256, 256))
    a_small = a.resize((64, 64))
    assert hamming_distance(dhash_image(a), dhash_image(a_small)) <= 8, "缩放不动点：dhash 应近似不变"


def test_box_exact_hash_stable_and_sensitive():
    poly = [[10.0, 20.0], [110.0, 20.0], [110.0, 90.0], [10.0, 90.0]]
    h1 = box_exact_hash(poly, "sfx", "ドン", "a" * 64)
    h2 = box_exact_hash([list(pt) for pt in poly], "sfx", "ドン", "a" * 64)
    h3 = box_exact_hash(poly, "sfx", "ゴゴ", "a" * 64)
    h4 = box_exact_hash(poly, "sfx", "ドン", "b" * 64)
    assert h1 == h2
    assert h1 != h3 and h1 != h4


def test_find_duplicates_exact_and_perceptual(tmp_path):
    from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord

    img = _noise_img(9)
    p1 = tmp_path / "a.png"
    p2 = tmp_path / "b.png"
    img.save(p1)
    img.save(p2)  # 完全相同字节 → exact
    from sfx_data_infra.hash import _sha256_file

    def mk(i, path, sha):
        return SampleRecord(
            sample_id=f"s{i}",
            image=ImageRef(path=str(path), sha256=sha, width=64, height=64),
            boxes=[BoxAnnotation(polygon=[[0, 0], [8, 0], [8, 8], [0, 8]])],
            annotation_status="synthetic",
            provenance={"type": "synthetic_render", "render_seed": i},
            group="synthetic/poc",
            created_at="2026-10-04T00:00:00+00:00",
        )

    samples = [
        mk(0, p1, _sha256_file(p1)),
        mk(1, p2, _sha256_file(p2)),
        mk(2, tmp_path / "c.png", "c" * 64),  # 无文件的占位（不同 sha，跳过感知比对）
    ]
    report = find_duplicates(samples, image_loader=lambda p: Image.open(p).convert("RGB"))
    assert report.duplicate_of.get("s1") == "s0", "同图副本应判重复"
    kept = drop_duplicates(samples, report)
    assert [s.sample_id for s in kept] == ["s0", "s2"]


def test_ogkalu_key_and_polygons():
    assert parse_ogkalu_region_key("K01_R035") == "K01"
    assert parse_ogkalu_region_key("K10_R007") == "K10"
    assert bbox_to_polygon(5, 6, 10, 20) == [[5.0, 6.0], [15.0, 6.0], [15.0, 26.0], [5.0, 26.0]]
    assert xyxy_to_polygon(2210, 240, 2560, 1000) == [[2210.0, 240.0], [2560.0, 240.0], [2560.0, 1000.0], [2210.0, 1000.0]]


def test_page_filename_from_cases_index():
    cases_index = {"BJ13": {"case_id": "BJ13", "source_id": "vol03_p0048"}}
    assert page_filename_for_case("BJ13", cases_index) == "vol03_p0048.png"
