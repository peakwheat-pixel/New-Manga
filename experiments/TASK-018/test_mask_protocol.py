"""Dependency-free self-tests for the TASK-018 mask protocol.

Run: ``PYTHONPATH=experiments/TASK-018 python -m unittest experiments/TASK-018/test_mask_protocol.py -v``

These tests assert the *experiment harness* invariants only. They never claim
model quality: no inpainting model is loaded here.
"""

from __future__ import annotations

import unittest

from mask_protocol import (
    DEFAULT_MASK_PARAMS,
    SAMPLE_KINDS,
    bbox,
    covers,
    dilate,
    edge_bleed_fill,
    empty_mask,
    erode,
    ink_pixels_inside,
    mask_area,
    mask_records,
    protected_pixels,
    rect_mask,
    refine_mask,
    residual_text_pixels,
    route_available,
    simple_fill,
)


class MaskGeometryTests(unittest.TestCase):
    def test_rect_mask_matches_requested_area(self) -> None:
        mask = rect_mask(10, 10, (2, 3, 5, 7))
        self.assertEqual(mask_area(mask), 3 * 4)
        self.assertEqual(bbox(mask), (2, 3, 5, 7))
        self.assertTrue(mask[3][2])
        self.assertFalse(mask[0][0])

    def test_rect_mask_rejects_out_of_bounds(self) -> None:
        with self.assertRaises(ValueError):
            rect_mask(10, 10, (0, 0, 11, 5))

    def test_dilate_and_erode_are_inverse_on_solid_block(self) -> None:
        base = rect_mask(12, 12, (4, 4, 8, 8))
        grown = dilate(base, 2)
        self.assertTrue(covers(grown, base))
        self.assertEqual(mask_area(grown), 8 * 8)
        shrunk = erode(base, 1)
        self.assertTrue(covers(base, shrunk))
        self.assertEqual(mask_area(shrunk), 2 * 2)

    def test_refine_chain_preserves_raw_and_final_separately(self) -> None:
        raw = rect_mask(16, 16, (6, 6, 10, 10))
        final = refine_mask(raw, erode_radius=1, dilate_radius=2)
        record = mask_records(raw, final, DEFAULT_MASK_PARAMS)
        self.assertEqual(record["raw_mask_area"], 16)
        self.assertNotEqual(record["raw_mask_area"], record["final_mask_area"])
        self.assertTrue(record["final_covers_raw"])
        self.assertEqual(record["mask_params"], DEFAULT_MASK_PARAMS)

    def test_empty_mask_has_no_bbox(self) -> None:
        self.assertIsNone(bbox(empty_mask(4, 4)))
        self.assertEqual(mask_area(empty_mask(4, 4)), 0)

    def test_sample_kind_set_is_fixed_by_spec(self) -> None:
        self.assertEqual(
            set(SAMPLE_KINDS),
            {"white-background", "line-art", "screentone", "gradient", "structure-crossing"},
        )


class NonTargetProtectionTests(unittest.TestCase):
    def _image(self, value: tuple[int, int, int], width: int = 8, height: int = 8):
        return [[value for _ in range(width)] for _ in range(height)]

    def test_simple_fill_changes_only_masked_pixels(self) -> None:
        before = self._image((0, 0, 0))
        mask = rect_mask(8, 8, (2, 2, 5, 5))
        after = simple_fill(before, mask, fill=(255, 255, 255))
        self.assertEqual(protected_pixels(before, after, mask), [])
        self.assertEqual(after[2][2], (255, 255, 255))
        self.assertEqual(after[0][0], (0, 0, 0))

    def test_protected_pixels_detects_an_out_of_mask_write(self) -> None:
        before = self._image((0, 0, 0))
        mask = rect_mask(8, 8, (2, 2, 5, 5))
        after = simple_fill(before, mask, fill=(255, 255, 255))
        after[0][0] = (1, 1, 1)  # illegal edit outside the mask
        self.assertEqual(protected_pixels(before, after, mask), [(0, 0)])

    def test_edge_bleed_fill_also_confines_writes_to_the_mask(self) -> None:
        before = self._image((10, 10, 10))
        before[3][3] = (250, 250, 250)
        mask = rect_mask(8, 8, (2, 2, 5, 5))
        after = edge_bleed_fill(before, mask, iterations=3)
        self.assertEqual(protected_pixels(before, after, mask), [])

    def test_residual_and_ink_pixel_counters(self) -> None:
        before = self._image((255, 255, 255))
        mask = rect_mask(8, 8, (2, 2, 5, 5))
        before[3][3] = (0, 0, 0)
        self.assertEqual(ink_pixels_inside(before, mask), 1)
        self.assertEqual(residual_text_pixels(before, before, mask), 1)
        cleaned = simple_fill(before, mask, fill=(255, 255, 255))
        self.assertEqual(residual_text_pixels(before, cleaned, mask), 0)


class RouteGateTests(unittest.TestCase):
    def test_route_available_reports_missing_requirements(self) -> None:
        routes = {
            "simple-fill": {"requirements": {}},
            "manga-lama": {"requirements": {"torch": False, "weights": False}},
        }
        self.assertEqual(route_available(routes, "simple-fill"), (True, "ready"))
        runnable, reason = route_available(routes, "manga-lama")
        self.assertFalse(runnable)
        self.assertIn("missing dependency/weight", reason)

    def test_unknown_route_is_not_silently_usable(self) -> None:
        runnable, reason = route_available({}, "flux")
        self.assertFalse(runnable)
        self.assertIn("unknown route", reason)


if __name__ == "__main__":
    unittest.main()
