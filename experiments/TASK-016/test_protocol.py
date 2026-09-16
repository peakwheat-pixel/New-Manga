from __future__ import annotations

import unittest

from protocol import fallback_status, map_region_result, order_results, tile_polygon_to_global


class ProtocolTests(unittest.TestCase):
    def test_single_region_preserves_region_id_and_global_coordinates(self) -> None:
        result = map_region_result(
            region_id="r-17",
            text="人工标注",
            polygon=[[10, 20], [30, 20], [30, 40], [10, 40]],
            reading_order=3,
        )
        self.assertEqual(result["region_id"], "r-17")
        self.assertEqual(result["coordinate_space"], "page-global")
        self.assertEqual(result["polygon"][0], [10, 20])

    def test_tile_polygon_maps_to_page_global(self) -> None:
        self.assertEqual(
            tile_polygon_to_global([[1, 2], [11, 2], [11, 12], [1, 12]], [100, 600]),
            [[101, 602], [111, 602], [111, 612], [101, 612]],
        )
        result = map_region_result(
            region_id="long-02",
            text="두 번째 장면입니다.",
            polygon=[[80, 160], [300, 160], [300, 210], [80, 210]],
            reading_order=1,
            coordinate_space="tile-local",
            tile_origin=[0, 600],
        )
        self.assertEqual(result["polygon"][0], [80, 760])

    def test_reading_order_is_stable(self) -> None:
        results = order_results([
            {"region_id": "b", "reading_order": 2},
            {"region_id": "a", "reading_order": 1},
            {"region_id": "c", "reading_order": 2},
        ])
        self.assertEqual([item["region_id"] for item in results], ["a", "b", "c"])

    def test_fallback_never_invents_an_unconfigured_route(self) -> None:
        self.assertEqual(fallback_status("BLOCKED", set()), "BLOCKED")
        self.assertEqual(fallback_status("FAIL", {"paddleocr-korean"}), "FALLBACK_CONFIGURED")


if __name__ == "__main__":
    unittest.main()
