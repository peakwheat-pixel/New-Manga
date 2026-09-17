"""Route gating and probing tests for TASK-018 revision slice (R-002 / R-007).

The test code itself uses only the standard library, but it imports the harness
module ``run_experiment`` in order to exercise the *real* ``route_gate`` /
``probe_requirement`` logic. That module imports PySide6 for image I/O, so this
suite is **standard-library-only in its own code**, not dependency-free end to
end: it requires an interpreter that can import ``run_experiment``.

Kept in a separate module so the original 12 protocol tests in
``test_mask_protocol.py`` stay untouched (their count must not change).

Run: ``PYTHONPATH=experiments/TASK-018 python -m unittest experiments/TASK-018/test_route_gating.py -v``
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import run_experiment as rx

#: R-104: fail loudly if a *different* ``run_experiment`` module was imported
#: (for example another task's ``experiments`` directory shadowing this one),
#: because every assertion below would silently test the wrong harness.
_HARNESS_MODULE = Path(rx.__file__).resolve()
_EXPECTED_DIR = Path(__file__).resolve().parent
assert _HARNESS_MODULE.parent == _EXPECTED_DIR, (
    f"imported run_experiment from {_HARNESS_MODULE.parent} instead of {_EXPECTED_DIR}; "
    "check PYTHONPATH ordering before trusting these results"
)


class FailClosedTests(unittest.TestCase):
    """R-007: an unimplemented route must never run, whatever the probes say."""

    def test_learned_routes_are_blocked_as_not_implemented(self) -> None:
        for route in ("manga-lama", "aot", "brushnet-powerpaint", "flux"):
            gate = rx.route_gate(route)
            self.assertFalse(gate["runnable"], route)
            self.assertEqual(gate["blocked_stage"], rx.BLOCKED_STAGE_NOT_IMPLEMENTED, route)

    def test_not_implemented_wins_even_when_all_dependencies_are_satisfied(self) -> None:
        """The counterexample required by the verification plan.

        Every requirement of ``flux`` is forced to 'satisfied' without touching
        the harness, then the gate must still refuse to run it.
        """
        original = rx.probe_requirement

        def always_satisfied(requirement):  # noqa: ANN001 - test double
            return {"descriptor": dict(requirement), "satisfied": True, "probe": "forced-for-counterexample"}

        rx.probe_requirement = always_satisfied
        try:
            gate = rx.route_gate("flux")
            self.assertFalse(gate["runnable"], "fail-closed violated: dependencies satisfied must NOT authorise an unimplemented route")
            self.assertEqual(gate["blocked_stage"], rx.BLOCKED_STAGE_NOT_IMPLEMENTED)
            self.assertEqual(gate["missing"], [])
        finally:
            rx.probe_requirement = original

    def test_no_filler_is_registered_for_learned_routes(self) -> None:
        for route in ("manga-lama", "aot", "brushnet-powerpaint", "flux"):
            self.assertNotIn(route, rx.FILLERS)

    def test_unregistered_route_raises_instead_of_substituting(self) -> None:
        pixels = [[(0, 0, 0)] * 4 for _ in range(4)]
        mask = [[False] * 4 for _ in range(4)]
        with self.assertRaises(KeyError):
            rx._evaluate_route("manga-lama", pixels, mask, repeat=1)

    def test_unknown_route_is_blocked_not_implemented(self) -> None:
        gate = rx.route_gate("does-not-exist")
        self.assertFalse(gate["runnable"])
        self.assertEqual(gate["blocked_stage"], rx.BLOCKED_STAGE_NOT_IMPLEMENTED)


class ProbingTests(unittest.TestCase):
    """R-002: status must come from probes, not from a static constant."""

    def test_module_probe_detects_a_present_and_an_absent_module(self) -> None:
        present = rx.probe_requirement({"type": rx.REQ_MODULE, "name": "json"})
        self.assertTrue(present["satisfied"])
        absent = rx.probe_requirement({"type": rx.REQ_MODULE, "name": "definitely_not_installed_module_xyz"})
        self.assertFalse(absent["satisfied"])

    def test_weight_probe_uses_environment_variable_and_file_existence(self) -> None:
        import os
        import tempfile
        from pathlib import Path

        env = "TASK018_TEST_WEIGHTS"
        missing = rx.probe_requirement({"type": rx.REQ_WEIGHT, "env": env, "label": "test"})
        self.assertFalse(missing["satisfied"])
        self.assertFalse(missing["env_var_set"])

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "weights.bin"
            target.write_bytes(b"not-a-real-model")
            os.environ[env] = str(target)
            try:
                found = rx.probe_requirement({"type": rx.REQ_WEIGHT, "env": env, "label": "test"})
                self.assertTrue(found["satisfied"])
                self.assertTrue(found["env_var_set"])
            finally:
                del os.environ[env]

    def test_baselines_are_ready_without_requirements(self) -> None:
        for route in ("simple-fill", "edge-bleed"):
            gate = rx.route_gate(route)
            self.assertTrue(gate["runnable"], route)
            self.assertIsNone(gate["blocked_stage"], route)
            self.assertEqual(gate["probes"], [], route)

    def test_dependency_stage_is_used_when_implementation_exists_but_probe_fails(self) -> None:
        """A synthetic implemented route with a failing descriptor → stage=dependency."""
        rx.ROUTES["__synthetic__"] = {
            "label": "synthetic",
            "kind": "baseline",
            "learned": False,
            "implementation": "simple_fill",
            "requirements": [{"type": rx.REQ_MODULE, "name": "definitely_not_installed_module_xyz"}],
            "size_class": "none (unmeasured tier)",
            "default_eligible": False,
            "note": "test-only",
        }
        try:
            gate = rx.route_gate("__synthetic__")
            self.assertFalse(gate["runnable"])
            self.assertEqual(gate["blocked_stage"], rx.BLOCKED_STAGE_DEPENDENCY)
            self.assertTrue(gate["missing"])
        finally:
            del rx.ROUTES["__synthetic__"]


class LabelTests(unittest.TestCase):
    """R-006: no unverified volume numbers in requirement keys or notes."""

    def test_no_volume_annotations_remain(self) -> None:
        banned = ("gb", "GB", "数 GB", "10GB", "several")
        for route, info in rx.ROUTES.items():
            text = " ".join([str(info.get("note", "")), str(info.get("size_class", "")), str(info.get("label", ""))])
            for token in banned:
                self.assertNotIn(token, text, f"{route} still contains volume annotation {token!r}")
            for req in info["requirements"]:
                blob = " ".join(str(v) for v in req.values())
                for token in banned:
                    self.assertNotIn(token, blob, f"{route} requirement still contains {token!r}")

    def test_size_class_is_labelled_unmeasured(self) -> None:
        for route, info in rx.ROUTES.items():
            self.assertIn("unmeasured", str(info["size_class"]), route)


class OutOfRootTests(unittest.TestCase):
    """R-003: an out-of-root output dir must not raise."""

    def test_display_path_falls_back_to_absolute(self) -> None:
        import tempfile
        from pathlib import Path

        outside = Path(tempfile.gettempdir()) / "task018-outside"
        display, inside = rx._display_path(outside)
        self.assertFalse(inside)
        self.assertTrue(Path(display).is_absolute())

    def test_display_path_inside_root_is_relative(self) -> None:
        display, inside = rx._display_path(rx.ROOT / "results")
        self.assertTrue(inside)
        self.assertFalse(Path(display).is_absolute())


class StartupAssertionTests(unittest.TestCase):
    """R-104: an ``implementation`` without a registered filler must fail at startup.

    The guard runs at import time in ``run_experiment``. To prove that — without
    editing the harness — a **copy** of the harness is misconfigured in a temp
    directory and imported in a fresh interpreter.
    """

    def test_current_configuration_passes_the_guard(self) -> None:
        self.assertIsNone(rx.assert_implementations_registered())

    def test_guard_rejects_a_route_with_unregistered_implementation(self) -> None:
        broken = dict(rx.ROUTES)
        broken["__misconfigured__"] = {
            **rx.ROUTES["simple-fill"],
            "implementation": "not_a_registered_filler",
        }
        with self.assertRaises(RuntimeError) as ctx:
            rx.assert_implementations_registered(broken, rx.FILLERS)
        self.assertIn("__misconfigured__", str(ctx.exception))
        self.assertIn("misconfiguration", str(ctx.exception))

    def test_misconfigured_copy_dies_at_import_and_writes_no_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            for name in ("run_experiment.py", "mask_protocol.py"):
                shutil.copy2(_EXPECTED_DIR / name, tmpdir / name)
            target = tmpdir / "run_experiment.py"
            text = target.read_text(encoding="utf-8")
            marker = '"edge-bleed": lambda pixels, mask: edge_bleed_fill(pixels, mask, iterations=8),'
            self.assertIn(marker, text, "guard test needs the edge-bleed filler registration")
            # Genuine misconfiguration: the route keeps its ``implementation``
            # but is no longer registered in FILLERS.
            target.write_text(
                text.replace(marker, '"_removed_for_counterexample_": lambda pixels, mask: None,'),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, "-c", "import run_experiment"],
                cwd=str(tmpdir),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0, "misconfigured harness must fail at import")
            self.assertIn("misconfiguration", proc.stderr or proc.stdout)
            self.assertEqual(list(tmpdir.glob("*.png")), [], "a misconfigured run must not write images")


if __name__ == "__main__":
    unittest.main()
