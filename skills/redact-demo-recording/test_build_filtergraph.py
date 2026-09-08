#!/usr/bin/env python3
"""Regression tests for build_filtergraph.py.

Hermetic: ffprobe is never invoked. Run either as `python3 test_build_filtergraph.py`
or `pytest test_build_filtergraph.py` from this directory.
"""

import importlib.util
import re
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "build_filtergraph", Path(__file__).with_name("build_filtergraph.py")
)
bfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bfg)


def region(x, y, w, h, start=None, end=None):
    return {"x": x, "y": y, "w": w, "h": h, "start": start, "end": end}


def no_empty_segments(graph):
    """A trailing `,` or doubled `;` produces `No such filter: ''` at runtime."""
    return ";;" not in graph and ",," not in graph and not graph.startswith((",", ";"))


class ParseRegion(unittest.TestCase):
    def test_no_window(self):
        r = bfg.parse_region("100,200,50,60")
        self.assertEqual((r["x"], r["y"], r["w"], r["h"]), (100, 200, 50, 60))
        self.assertIsNone(r["start"])
        self.assertIsNone(r["end"])

    def test_with_window(self):
        r = bfg.parse_region("100,200,50,60@6.5-10.5")
        self.assertEqual(r["start"], 6.5)
        self.assertEqual(r["end"], 10.5)

    def test_too_small_rejected(self):
        with self.assertRaises(SystemExit):
            bfg.parse_region("10,10,1,4")
        with self.assertRaises(SystemExit):
            bfg.parse_region("10,10,4,1")

    def test_bad_syntax_rejected(self):
        for bad in ("garbage", "1,2,3", "1,2,3,4@", "1,2,3,4@1", "-1,0,4,4"):
            with self.assertRaises(SystemExit):
                bfg.parse_region(bad)


class ChromaDivisor(unittest.TestCase):
    def test_420(self):
        self.assertEqual(bfg.chroma_divisor("yuv420p"), (2, 2))

    def test_422(self):
        self.assertEqual(bfg.chroma_divisor("yuv422p"), (2, 1))

    def test_444_and_rgb(self):
        self.assertEqual(bfg.chroma_divisor("yuv444p"), (1, 1))
        self.assertEqual(bfg.chroma_divisor("rgb24"), (1, 1))


class BlurClamp(unittest.TestCase):
    def test_284x28_on_yuv420p_clamps_both_planes(self):
        # The pathological case from the PR body: a 28px-tall region has
        # chroma plane 14px, so the chroma radius must clamp to 7 while luma
        # clamps to 14. Emitting the 4-param form is what enforces this;
        # a 2-param form would let chroma inherit 14 and fail.
        self.assertEqual(bfg.blur_filter(284, 28, "yuv420p", 20), "boxblur=14:2:7:2")

    def test_small_region_stays_legal(self):
        # 4x4 in yuv420p: luma_max = 2, chroma_max = 1.
        self.assertEqual(bfg.blur_filter(4, 4, "yuv420p", 12), "boxblur=2:2:1:2")

    def test_large_region_uses_requested_strength(self):
        self.assertEqual(bfg.blur_filter(420, 530, "yuv420p", 20), "boxblur=20:2:20:2")

    def test_yuv444_treats_chroma_as_full_res(self):
        self.assertEqual(bfg.blur_filter(28, 28, "yuv444p", 20), "boxblur=14:2:14:2")

    def test_minimum_radius_is_one(self):
        self.assertEqual(bfg.blur_filter(2, 2, "yuv420p", 12), "boxblur=1:2:1:2")


class PixelateAtAnySize(unittest.TestCase):
    def test_tiny_region_still_legal(self):
        # `--mode pixelate` is documented as legal at any region size.
        f = bfg.pixelate_filter(4, 4, "yuv420p", 12)
        self.assertEqual(f, "scale=1:1,scale=4:4:flags=neighbor")

    def test_normal_region(self):
        self.assertEqual(
            bfg.pixelate_filter(420, 530, "yuv420p", 12),
            "scale=35:44,scale=420:530:flags=neighbor",
        )


class BuildGraph(unittest.TestCase):
    def test_single_region_no_window(self):
        g = bfg.build([region(100, 200, 50, 60)], 1920, 1080, "yuv420p", "blur", 5)
        self.assertTrue(no_empty_segments(g))
        self.assertIn("[0:v]split=2[m1][s1]", g)
        self.assertIn("crop=50:60:100:200", g)
        self.assertIn("[m1][b1]overlay=100:200[v1]", g)
        self.assertNotIn("between(t,", g)

    def test_time_window_wraps_overlay(self):
        g = bfg.build(
            [region(100, 200, 50, 60, start=6.5, end=10.5)],
            1920, 1080, "yuv420p", "blur", 5,
        )
        self.assertIn("overlay=100:200:enable='between(t,6.5,10.5)'", g)

    def test_multi_region_chains(self):
        g = bfg.build(
            [
                region(100, 200, 50, 60, start=6.5, end=10.5),
                region(400, 300, 80, 40),
            ],
            1920, 1080, "yuv420p", "pixelate", 12,
        )
        self.assertTrue(no_empty_segments(g))
        self.assertIn("[0:v]split=2[m1][s1]", g)
        self.assertIn("[v1]split=2[m2][s2]", g)
        self.assertIn("[m1][b1]overlay=100:200:enable='between(t,6.5,10.5)'[v1]", g)
        self.assertIn("[m2][b2]overlay=400:300[v2]", g)
        self.assertTrue(g.rstrip().endswith("[vout]"))

    def test_out_of_bounds_rejected(self):
        with self.assertRaises(SystemExit):
            bfg.build([region(1900, 0, 50, 60)], 1920, 1080, "yuv420p", "blur", 5)
        with self.assertRaises(SystemExit):
            bfg.build([region(0, 1050, 50, 60)], 1920, 1080, "yuv420p", "blur", 5)

    def test_odd_source_gets_even_output_scale(self):
        # Retina captures like 2940x1833 must not leak odd dims into libx264.
        g = bfg.build([region(10, 10, 100, 100)], 2940, 1833, "yuv420p", "blur", 5)
        self.assertIn("scale=trunc(iw/2)*2:trunc(ih/2)*2[vout]", g)

    def test_284x28_on_odd_source_emits_clamped_chroma(self):
        # The exact regression case the PR body calls out: odd source,
        # narrow region, 4-param boxblur must land with chroma < luma.
        g = bfg.build(
            [region(1130, 450, 284, 28, start=6.5, end=10.5)],
            2940, 1833, "yuv420p", "blur", 20,
        )
        self.assertIn("boxblur=14:2:7:2", g)
        self.assertIn("scale=trunc(iw/2)*2:trunc(ih/2)*2[vout]", g)
        self.assertTrue(no_empty_segments(g))

    def test_pathological_4x4_region_both_modes(self):
        for mode in ("blur", "pixelate"):
            g = bfg.build(
                [region(0, 0, 4, 4)], 1920, 1080, "yuv420p", mode, 12
            )
            self.assertTrue(no_empty_segments(g), mode)
            self.assertRegex(g, r"crop=4:4:0:0")

    def test_no_empty_segments_across_shapes(self):
        # Guard against a future refactor reintroducing `;;` / `,,`.
        cases = [
            ([region(0, 0, 4, 4)], 1920, 1080, "blur"),
            ([region(0, 0, 4, 4)], 1920, 1080, "pixelate"),
            ([region(1130, 450, 284, 28, 6.5, 10.5)], 2940, 1833, "blur"),
            (
                [region(1, 1, 6, 6), region(10, 10, 8, 8, 1.0, 2.0)],
                1920, 1080, "pixelate",
            ),
        ]
        for regions, w, h, mode in cases:
            g = bfg.build(regions, w, h, "yuv420p", mode, 12)
            self.assertTrue(no_empty_segments(g), f"empty segment in: {g}")
            # Every named label produced should be consumed.
            labels = re.findall(r"\[([msbv]\d+)\]", g)
            self.assertEqual(len(labels) % 2, 0, "unbalanced label refs")


if __name__ == "__main__":
    unittest.main(verbosity=2)
