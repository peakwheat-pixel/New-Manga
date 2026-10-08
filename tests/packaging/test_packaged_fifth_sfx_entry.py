"""Targeted tests for packaged fifth SFX entry in M2-AC5 clean-start runner (P03).

Covers:
  - Inclusion of sfx_detect_probe.exe in SIDECAR_EXES and install assertion manifest.
  - Fifth entry in sidecar process survivor zero-survival assertion via evaluate_sidecar_survivors.
  - Evaluation of sfx_detect_probe success scenario (frozen=True, exit 0, strict int candidates>0,
    pinned weights sha256, resolved_from=bundle_probe inside install_dir, three-key EP fallback preservation).
  - Rejection of external env/arg weights or paths outside install dir (R-001).
  - Robust handling of non-dict JSON payloads, boolean candidates, missing error keys (R-005, R-007).
  - Evaluation of sfx_detect_probe expected failure scenario (frozen=True, exit 1, non-empty error).
  - CLI argument parsing for --sfx-real-page option while preserving --output-dir requirement.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
AC5_RUNNER = ROOT / "packaging" / "m2ac5" / "run_clean_start_e2e.py"
PINNED_WEIGHTS_SHA256 = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"


def load_ac5_module() -> ModuleType:
    m2_conftest_path = ROOT / "tests" / "m2_resource_channel" / "conftest.py"
    m2_conftest_spec = importlib.util.spec_from_file_location("m2_resource_channel_conftest", m2_conftest_path)
    assert m2_conftest_spec is not None and m2_conftest_spec.loader is not None
    m2_conftest = importlib.util.module_from_spec(m2_conftest_spec)
    m2_conftest_spec.loader.exec_module(m2_conftest)

    old_conftest = sys.modules.get("conftest")
    sys.modules["conftest"] = m2_conftest
    try:
        spec = importlib.util.spec_from_file_location("ac5_runner_for_p03_tests", AC5_RUNNER)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old_conftest is not None:
            sys.modules["conftest"] = old_conftest
        else:
            sys.modules.pop("conftest", None)


@pytest.fixture(scope="module")
def ac5_mod() -> ModuleType:
    return load_ac5_module()


def test_sidecar_exes_includes_fifth_sfx_entry(ac5_mod: ModuleType):
    """AC1: SIDECAR_EXES contains exactly the 5 frozen sidecars, including sfx_detect_probe.exe."""
    expected = (
        "host_bridge.exe",
        "core_service.exe",
        "acceptance_bridge.exe",
        "catalog_loader.exe",
        "sfx_detect_probe.exe",
    )
    assert ac5_mod.SIDECAR_EXES == expected
    assert "sfx_detect_probe.exe" in ac5_mod.SIDECAR_EXES


def test_survivor_reaping_judgement_includes_fifth_sfx_entry(ac5_mod: ModuleType):
    """AC1 / R-003: Survivor check calls evaluate_sidecar_survivors; rejects surviving sfx_detect_probe.exe and passes when zero."""
    # When all 5 are 0 -> pass
    survivors_all_clean = {
        "host_bridge.exe": 0,
        "core_service.exe": 0,
        "acceptance_bridge.exe": 0,
        "catalog_loader.exe": 0,
        "sfx_detect_probe.exe": 0,
        "python.exe": 1,  # record-only
    }
    ok_clean, obs_clean = ac5_mod.evaluate_sidecar_survivors(survivors_all_clean)
    assert ok_clean is True

    # When sfx_detect_probe.exe is surviving -> must fail
    survivors_sfx_leak = dict(survivors_all_clean)
    survivors_sfx_leak["sfx_detect_probe.exe"] = 1
    ok_leak, obs_leak = ac5_mod.evaluate_sidecar_survivors(survivors_sfx_leak)
    assert ok_leak is False
    assert obs_leak["sfx_detect_probe.exe"] == 1

    # When sfx_detect_probe.exe is omitted from survivor dict -> fail closed
    survivors_missing = dict(survivors_all_clean)
    del survivors_missing["sfx_detect_probe.exe"]
    ok_missing, _ = ac5_mod.evaluate_sidecar_survivors(survivors_missing)
    assert ok_missing is False

    # Production default uses SIDECAR_EXES which must include sfx_detect_probe.exe
    assert "sfx_detect_probe.exe" in ac5_mod.SIDECAR_EXES


def test_evaluate_sfx_probe_success_valid(ac5_mod: ModuleType, tmp_path: Path):
    """AC2 / R-001 / R-002: evaluate_sfx_probe_success passes on valid frozen bundle output and records provenance."""
    install_dir = tmp_path / "install"
    weights_path = install_dir / "resources" / "core-sidecar" / "models" / "detector" / "yolo11s-seg.onnx"
    payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "label": "injected-real-page",
        "python": {"frozen": True, "executable": str(install_dir / "resources" / "core-sidecar" / "sfx_detect_probe.exe")},
        "page": {"source": "injected", "sha256": "pixel_rgb24_hash_abcdef"},
        "weights": {
            "path": str(weights_path),
            "exists": True,
            "resolved_from": "bundle_probe",
            "sha256": PINNED_WEIGHTS_SHA256,
        },
        "provider": {"id": "sfx_detect", "type": "sfx_detection"},
        "result": {
            "n_candidates": 4,
            "elapsed_ms": 120,
            "device": "dml",
            "sfx_ep": "dml",
            "sfx_ep_fallback": None,
            "options": {"device": "dml", "sfx_ep": "dml"},
        },
        "error": None,
    }
    stdout = f"Human log line 1\nSFX_PROBE_JSON: {json.dumps(payload)}\n"
    passed, obs = ac5_mod.evaluate_sfx_probe_success(0, stdout, "", install_dir=install_dir)
    assert passed is True
    assert obs["exit"] == 0
    assert obs["marker_count"] == 1
    assert obs["json_parsed"] is True
    assert obs["frozen"] is True
    assert obs["has_error_key"] is True
    assert obs["error"] is None
    assert obs["n_candidates"] == 4
    assert obs["weights_sha256_matches_pin"] is True
    assert obs["weights_resolved_from"] == "bundle_probe"
    assert obs["weights_in_install_dir"] is True
    assert obs["page_pixel_sha256"] == "pixel_rgb24_hash_abcdef"
    assert obs["device"] == "dml"
    assert obs["sfx_ep"] == "dml"
    assert obs["sfx_ep_fallback"] is None


def test_evaluate_sfx_probe_success_with_cpu_fallback(ac5_mod: ModuleType, tmp_path: Path):
    """AC2: evaluate_sfx_probe_success records runtime fallback without hiding or failing."""
    install_dir = tmp_path / "install"
    weights_path = install_dir / "resources" / "core-sidecar" / "models" / "detector" / "yolo11s-seg.onnx"
    payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "label": "injected-real-page",
        "python": {"frozen": True, "executable": str(install_dir / "resources" / "core-sidecar" / "sfx_detect_probe.exe")},
        "weights": {
            "path": str(weights_path),
            "exists": True,
            "resolved_from": "bundle_probe",
            "sha256": PINNED_WEIGHTS_SHA256,
        },
        "result": {
            "n_candidates": 2,
            "elapsed_ms": 250,
            "device": "cpu",
            "sfx_ep": "cpu",
            "sfx_ep_fallback": "DirectML device removed, fell back to CPU",
            "options": {"device": "cpu"},
        },
        "error": None,
    }
    stdout = f"SFX_PROBE_JSON: {json.dumps(payload)}\n"
    passed, obs = ac5_mod.evaluate_sfx_probe_success(0, stdout, "", install_dir=install_dir)
    assert passed is True
    assert obs["device"] == "cpu"
    assert obs["sfx_ep"] == "cpu"
    assert obs["sfx_ep_fallback"] == "DirectML device removed, fell back to CPU"


def test_evaluate_sfx_probe_rejects_external_env_or_outside_weights(ac5_mod: ModuleType, tmp_path: Path):
    """R-001: evaluate_sfx_probe_success rejects weights from external env override or outside install dir."""
    install_dir = tmp_path / "install"
    outside_weights = tmp_path / "custom" / "yolo11s-seg.onnx"
    inside_weights = install_dir / "resources" / "core-sidecar" / "models" / "detector" / "yolo11s-seg.onnx"

    base_payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "python": {"frozen": True},
        "weights": {
            "path": str(inside_weights),
            "resolved_from": "bundle_probe",
            "sha256": PINNED_WEIGHTS_SHA256,
        },
        "result": {"n_candidates": 2, "device": "dml", "sfx_ep": "dml", "sfx_ep_fallback": None},
        "error": None,
    }

    # Case 1: resolved_from is "env" (external env cannot replace bundle weights)
    env_payload = dict(base_payload)
    env_payload["weights"] = dict(base_payload["weights"])
    env_payload["weights"]["resolved_from"] = "env"
    stdout_env = f"SFX_PROBE_JSON: {json.dumps(env_payload)}\n"
    passed_env, obs_env = ac5_mod.evaluate_sfx_probe_success(0, stdout_env, "", install_dir=install_dir)
    assert passed_env is False
    assert obs_env["weights_resolved_from"] == "env"

    # Case 2: resolved_from is "arg"
    arg_payload = dict(base_payload)
    arg_payload["weights"] = dict(base_payload["weights"])
    arg_payload["weights"]["resolved_from"] = "arg"
    stdout_arg = f"SFX_PROBE_JSON: {json.dumps(arg_payload)}\n"
    passed_arg, obs_arg = ac5_mod.evaluate_sfx_probe_success(0, stdout_arg, "", install_dir=install_dir)
    assert passed_arg is False
    assert obs_arg["weights_resolved_from"] == "arg"

    # Case 3: weights path is outside install_dir
    outside_payload = dict(base_payload)
    outside_payload["weights"] = dict(base_payload["weights"])
    outside_payload["weights"]["path"] = str(outside_weights)
    stdout_out = f"SFX_PROBE_JSON: {json.dumps(outside_payload)}\n"
    passed_out, obs_out = ac5_mod.evaluate_sfx_probe_success(0, stdout_out, "", install_dir=install_dir)
    assert passed_out is False
    assert obs_out["weights_in_install_dir"] is False


@pytest.mark.parametrize(
    "exit_code,payload_modifier,stdout_modifier,desc",
    [
        (1, lambda p: p, lambda s: s, "nonzero exit code"),
        (0, lambda p: p, lambda s: s + "SFX_PROBE_JSON: {}\n", "multiple marker lines"),
        (0, lambda p: p, lambda s: "no marker here\n", "missing marker line"),
        (0, lambda p: p, lambda s: "SFX_PROBE_JSON: {invalid json\n", "malformed json"),
        (0, lambda p: p, lambda s: "SFX_PROBE_JSON: [1, 2, 3]\n", "json payload is list not dict"),
        (0, lambda p: p, lambda s: "SFX_PROBE_JSON: \"just a string\"\n", "json payload is string not dict"),
        (0, lambda p: p, lambda s: "SFX_PROBE_JSON: 12345\n", "json payload is integer not dict"),
        (0, lambda p: p, lambda s: "SFX_PROBE_JSON: true\n", "json payload is bool not dict"),
        (0, lambda p: {**p, "python": {"frozen": False}}, lambda s: s, "not frozen"),
        (0, lambda p: {**p, "error": {"class": "Exception"}}, lambda s: s, "error not null"),
        (0, lambda p: {k: v for k, v in p.items() if k != "error"}, lambda s: s, "missing error key"),
        (0, lambda p: {**p, "result": {**p["result"], "n_candidates": 0}}, lambda s: s, "zero candidates"),
        (0, lambda p: {**p, "result": {**p["result"], "n_candidates": True}}, lambda s: s, "n_candidates is boolean True"),
        (0, lambda p: {**p, "result": {**p["result"], "n_candidates": 1.5}}, lambda s: s, "n_candidates is float"),
        (0, lambda p: {**p, "weights": {**p["weights"], "sha256": "wrong_hash"}}, lambda s: s, "weights sha mismatch"),
        (0, lambda p: {**p, "weights": {**p["weights"], "resolved_from": "env"}}, lambda s: s, "weights resolved_from env"),
    ],
)
def test_evaluate_sfx_probe_success_negative_cases(
    ac5_mod: ModuleType, exit_code, payload_modifier, stdout_modifier, desc
):
    """AC2 / R-005 / R-007: evaluate_sfx_probe_success fails closed on any violation of contract."""
    base_payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "python": {"frozen": True},
        "weights": {
            "path": "C:\\fake\\models\\yolo11s-seg.onnx",
            "resolved_from": "bundle_probe",
            "sha256": PINNED_WEIGHTS_SHA256,
        },
        "result": {
            "n_candidates": 3,
            "device": "dml",
            "sfx_ep": "dml",
            "sfx_ep_fallback": None,
        },
        "error": None,
    }
    payload = payload_modifier(base_payload)
    if any(k in desc for k in ("invalid json", "list", "string not dict", "integer not dict", "bool not dict")):
        stdout = stdout_modifier("")
    else:
        json_line = f"SFX_PROBE_JSON: {json.dumps(payload)}\n"
        stdout = stdout_modifier(json_line)

    passed, _ = ac5_mod.evaluate_sfx_probe_success(exit_code, stdout, "")
    assert passed is False, f"Expected failure for case: {desc}"


def test_evaluate_sfx_probe_failure_valid(ac5_mod: ModuleType):
    """AC2: evaluate_sfx_probe_failure passes when exit 1, frozen=True, exactly one JSON and error is non-empty."""
    payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "label": "missing-page-failure",
        "python": {"frozen": True, "executable": "C:\\fake\\sfx_detect_probe.exe"},
        "page": None,
        "weights": None,
        "result": None,
        "error": {
            "class": "FileNotFoundError",
            "error_code": "PROVIDER_FAILED",
            "message_head": "No such file or directory: guaranteed-missing.png",
        },
    }
    stdout = f"sfx_detect_probe: FAILED\nSFX_PROBE_JSON: {json.dumps(payload)}\n"
    passed, obs = ac5_mod.evaluate_sfx_probe_failure(1, stdout, "traceback details")
    assert passed is True
    assert obs["exit"] == 1
    assert obs["marker_count"] == 1
    assert obs["json_parsed"] is True
    assert obs["frozen"] is True
    assert obs["error"]["class"] == "FileNotFoundError"


@pytest.mark.parametrize(
    "exit_code,payload_modifier,stdout_modifier,desc",
    [
        (0, lambda p: p, lambda s: s, "exit code 0 instead of 1"),
        (1, lambda p: p, lambda s: s + "SFX_PROBE_JSON: {}\n", "multiple marker lines"),
        (1, lambda p: p, lambda s: "no marker here\n", "missing marker"),
        (1, lambda p: p, lambda s: "SFX_PROBE_JSON: [1, 2, 3]\n", "failure payload is list"),
        (1, lambda p: p, lambda s: "SFX_PROBE_JSON: \"failure string\"\n", "failure payload is string"),
        (1, lambda p: {**p, "python": {"frozen": False}}, lambda s: s, "not frozen"),
        (1, lambda p: {**p, "error": None}, lambda s: s, "error is None"),
        (1, lambda p: {**p, "error": {}}, lambda s: s, "error is empty dict"),
        (1, lambda p: {**p, "error": "not a dict"}, lambda s: s, "error is string not dict"),
    ],
)
def test_evaluate_sfx_probe_failure_negative_cases(
    ac5_mod: ModuleType, exit_code, payload_modifier, stdout_modifier, desc
):
    """AC2 / R-005: evaluate_sfx_probe_failure fails closed if expected failure contract is violated."""
    base_payload = {
        "probe": "m2-prod-sfx-probe-1.sfx_detect_probe",
        "python": {"frozen": True},
        "error": {"class": "FileNotFoundError", "error_code": "PROVIDER_FAILED"},
    }
    payload = payload_modifier(base_payload)
    if "list" in desc or "string" in desc and "payload is string" in desc:
        stdout = stdout_modifier("")
    else:
        json_line = f"SFX_PROBE_JSON: {json.dumps(payload)}\n"
        stdout = stdout_modifier(json_line)

    passed, _ = ac5_mod.evaluate_sfx_probe_failure(exit_code, stdout, "")
    assert passed is False, f"Expected failure for case: {desc}"


def test_ac5_parser_supports_sfx_real_page(ac5_mod: ModuleType, tmp_path: Path):
    """AC1/AC2: Parser accepts --sfx-real-page path while keeping --output-dir required."""
    parser = ac5_mod.build_parser()
    target_dir = tmp_path / "raw"
    real_page = tmp_path / "k07.png"

    # Default is None
    args_default = parser.parse_args(["--output-dir", str(target_dir)])
    assert args_default.sfx_real_page is None

    # Opt-in real page path accepted
    args_with_page = parser.parse_args([
        "--output-dir", str(target_dir),
        "--sfx-real-page", str(real_page),
    ])
    assert args_with_page.sfx_real_page == real_page

    # Omission of --output-dir still rejected with exit 2
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--sfx-real-page", str(real_page)])
    assert exc_info.value.code == 2
