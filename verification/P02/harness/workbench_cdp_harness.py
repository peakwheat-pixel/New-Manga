"""P02 Real Workbench WebView2 Verification Harness (Stage A r3).

Stage A preflight and verdict report generator.
NOTE: Interactive CDP and live WebView2 behavioral driving are NOT yet active
in Stage A (held BLOCKED under the Hard Build Barrier awaiting authorized
scratch-build registration by Codex).

Responsibilities in Stage A:
- Validates synthetic fixture contracts, wire structures, and enum sets (PRE-01)
- Validates static source contract and front-end control probe results (PRE-02)
- Evaluates Visual Direction F tokens and Live Inline Palette with Alpha Blending (PRE-03)
- Registers AC1-AC6 runtime verification scenarios honestly as BLOCKED
- Formats and persists structured verdicts according to AC7 requirements
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFICATION_DIR = REPO_ROOT / "verification" / "P02"
FIXTURES_PATH = VERIFICATION_DIR / "fixtures" / "workbench_synthetic_data.json"
BEHAVIOR_BASELINE_COMMIT = "241ff3b70b6fc0490ea238efd486cc707f849031"

KEY_SOURCE_FILES = [
    "apps/desktop/frontend/src/workbench/WorkbenchPage.tsx",
    "apps/desktop/frontend/src/workbench/relabelMachine.ts",
    "apps/desktop/frontend/src/App.tsx",
    "apps/desktop/frontend/src/region/client.ts",
    "apps/desktop/frontend/src/region/types.ts",
    "apps/desktop/frontend/src/library/client.ts",
    "apps/desktop/frontend/src/library/types.ts",
]


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "FILE_MISSING"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def get_git_info() -> dict[str, object]:
    def run_git(args: list[str]) -> str:
        proc = subprocess.run(
            ["git"] + args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.stdout.strip()

    source_hashes = {}
    for rel in KEY_SOURCE_FILES:
        full_p = REPO_ROOT / rel
        source_hashes[rel] = sha256_file(full_p)

    return {
        "head": run_git(["rev-parse", "HEAD"]),
        "tree": run_git(["rev-parse", "HEAD^{tree}"]),
        "branch": run_git(["branch", "--show-current"]),
        "behavior_baseline_commit": BEHAVIOR_BASELINE_COMMIT,
        "source_files_sha256": source_hashes,
    }


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c + c for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def parse_rgba_string(rgba_str: str) -> tuple[int, int, int, float] | None:
    s = rgba_str.strip().lower()
    if s.startswith("#"):
        rgb = hex_to_rgb(s)
        return (rgb[0], rgb[1], rgb[2], 1.0)
    import re
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)", s)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return (r, g, b, a)
    return None


def blend_alpha(
    fg_rgba: tuple[int, int, int, float],
    bg_rgb: tuple[int, int, int],
) -> tuple[int, int, int]:
    rf, gf, bf, a = fg_rgba
    rb, gb, bb = bg_rgb
    return (
        round(a * rf + (1.0 - a) * rb),
        round(a * gf + (1.0 - a) * gb),
        round(a * bf + (1.0 - a) * bb),
    )


def calculate_luminance(rgb: tuple[int, int, int]) -> float:
    def adjust(val: int) -> float:
        s = val / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    rs, gs, bs = adjust(rgb[0]), adjust(rgb[1]), adjust(rgb[2])
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs


def calculate_contrast(
    fg_rgba: tuple[int, int, int, float] | tuple[int, int, int],
    bg_rgba: tuple[int, int, int, float] | tuple[int, int, int],
    known_base_rgb: tuple[int, int, int] | None = None,
) -> tuple[float | None, str]:
    # Determine effective background
    if len(bg_rgba) == 4 and bg_rgba[3] < 1.0:
        if known_base_rgb is None:
            return None, "NOT_VERIFIABLE: background has alpha < 1.0 without known base"
        effective_bg = blend_alpha(bg_rgba, known_base_rgb)  # type: ignore[arg-type]
    else:
        effective_bg = (bg_rgba[0], bg_rgba[1], bg_rgba[2])

    # Determine effective foreground
    if len(fg_rgba) == 4 and fg_rgba[3] < 1.0:
        effective_fg = blend_alpha(fg_rgba, effective_bg)  # type: ignore[arg-type]
    else:
        effective_fg = (fg_rgba[0], fg_rgba[1], fg_rgba[2])

    l1 = calculate_luminance(effective_fg)
    l2 = calculate_luminance(effective_bg)
    brighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = round((brighter + 0.05) / (darker + 0.05), 2)
    return ratio, "PASS"


def self_test_contrast_math() -> None:
    # Black on White must be 21:1
    ratio_bw, _ = calculate_contrast((0, 0, 0), (255, 255, 255))
    assert ratio_bw == 21.0, f"Expected 21.0, got {ratio_bw}"

    # Same colors must be 1:1
    ratio_same, _ = calculate_contrast((100, 100, 100), (100, 100, 100))
    assert ratio_same == 1.0, f"Expected 1.0, got {ratio_same}"

    # Semi-transparent black (alpha=0.5) over white creates (128, 128, 128)
    ratio_alpha, _ = calculate_contrast((0, 0, 0, 0.5), (255, 255, 255))
    assert ratio_alpha is not None and 3.9 < ratio_alpha < 4.1, f"Expected ~3.98, got {ratio_alpha}"

    # Background with alpha < 1.0 without known base must return NOT_VERIFIABLE
    ratio_no_base, status = calculate_contrast((0, 0, 0), (255, 255, 255, 0.8), known_base_rgb=None)
    assert ratio_no_base is None and "NOT_VERIFIABLE" in status, "Expected NOT_VERIFIABLE"


class WorkbenchHarness:
    def __init__(self) -> None:
        self.git_info = get_git_info()
        self.verdicts: list[dict[str, object]] = []
        self.findings: list[str] = []
        self_test_contrast_math()

    def record_verdict(
        self,
        scenario_id: str,
        scenario_name: str,
        status: str,
        layer: str,
        exit_code: int | None,
        details: dict[str, object] | None = None,
        blocker_reason: str | None = None,
    ) -> None:
        self.verdicts.append({
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "status": status,
            "layer": layer,
            "exit_code": exit_code,
            "details": details or {},
            "blocker_reason": blocker_reason,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

    def run_preflight_checks(self) -> bool:
        """Runs Stage A preflight checks (fixtures, static contract, token math)."""
        all_passed = True

        # 1. PRE-01: Synthetic Fixture Integrity & Deep Schema Validation
        if not FIXTURES_PATH.exists():
            self.record_verdict(
                "PRE-01",
                "synthetic_fixture_presence",
                "FAIL",
                "FILESYSTEM",
                1,
                blocker_reason=f"Synthetic fixture file missing: {FIXTURES_PATH}",
            )
            return False

        try:
            with FIXTURES_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            fixtures = data.get("fixtures", {})

            # Deep assertion of books, chapters, pages, regions wire keys
            books = fixtures.get("books", [])
            assert len(books) > 0 and "book_id" in books[0], "Missing book_id in books fixture"

            chapters = fixtures.get("chapters", {})
            first_chap_list = next(iter(chapters.values()), [])
            assert len(first_chap_list) > 0 and "chapter_id" in first_chap_list[0], "Missing chapter_id in chapters fixture"
            assert isinstance(first_chap_list[0]["chapter_number"], str), "chapter_number must be string"

            pages = fixtures.get("pages", {})
            first_page_list = next(iter(pages.values()), [])
            assert len(first_page_list) > 0 and "page_id" in first_page_list[0], "Missing page_id in pages fixture"

            regions = fixtures.get("regions", {})
            first_reg_list = next(iter(regions.values()), [])
            assert len(first_reg_list) > 0 and "region_id" in first_reg_list[0], "Missing region_id in regions fixture"
            reg0 = first_reg_list[0]
            assert reg0["region_type"] in ["speech", "sfx", "narration", "title", "note", "other"], "Invalid region_type enum"
            assert "revisions" in reg0 and len(reg0["revisions"]) > 0, "Missing revisions in region"
            rev0 = reg0["revisions"][0]
            assert "region_revision_id" in rev0 and "is_current" in rev0 and "sfx_policy" in rev0, "Missing wire keys in RevisionSummary"

            # Validate AC4 retype operation is speech <-> sfx per relabelMachine
            pw = fixtures.get("post_write_scenarios", {})
            retype_op = pw.get("retype", {})
            new_type = retype_op.get("ipc_write", {}).get("args", {}).get("newRegionType")
            assert new_type == "sfx", "AC4 retype must follow relabelMachine speech<->sfx transition"

            self.record_verdict(
                "PRE-01",
                "synthetic_fixture_presence",
                "PASS",
                "FILESYSTEM",
                0,
                details={
                    "sections_validated": list(fixtures.keys()),
                    "wire_keys_verified": ["book_id", "chapter_id", "page_id", "region_id", "region_revision_id"],
                    "relabel_transition_verified": "speech -> sfx",
                    "file": str(FIXTURES_PATH.relative_to(REPO_ROOT)),
                },
            )
        except Exception as exc:
            self.record_verdict(
                "PRE-01",
                "synthetic_fixture_presence",
                "FAIL",
                "FILESYSTEM",
                1,
                blocker_reason=f"Fixture validation assertion failed: {exc}",
            )
            return False

        # 2. PRE-02: Static Source Contract Probe
        # Read from static-control-report.json to ensure single execution across workflow
        static_report_path = VERIFICATION_DIR / "static-control-report.json"
        if not static_report_path.exists():
            probe_py = VERIFICATION_DIR / "probes" / "static_control_probe.py"
            subprocess.run([sys.executable, str(probe_py)], capture_output=True, text=True)

        if static_report_path.exists():
            try:
                with static_report_path.open("r", encoding="utf-8") as f:
                    srep = json.load(f)
                probe_pass = (srep.get("overall_status") == "PASS")
                if not probe_pass:
                    all_passed = False
                self.record_verdict(
                    "PRE-02",
                    "static_source_contract_check",
                    "PASS" if probe_pass else "FAIL",
                    "STATIC_AST",
                    0 if probe_pass else 1,
                    details=srep,
                )
            except Exception as exc:
                all_passed = False
                self.record_verdict(
                    "PRE-02",
                    "static_source_contract_check",
                    "FAIL",
                    "STATIC_AST",
                    1,
                    blocker_reason=f"Failed reading static report: {exc}",
                )

        # 3. PRE-03: Visual Direction F Token Math Model & Live Inline Palette Evaluation
        try:
            f_tokens = data["fixtures"]["visual_direction_f_tokens"]["tokens"]
            bg_page_hex = f_tokens["bg_page"]["hex"]
            bg_page_rgb = hex_to_rgb(bg_page_hex)

            calculated_ratios = {}
            for token_name, token_info in f_tokens.items():
                if token_name == "bg_page":
                    continue
                fg_rgb = hex_to_rgb(token_info["hex"])
                ratio, _ = calculate_contrast(fg_rgb, bg_page_rgb)
                min_target = 4.5 if "text" in token_info["role"] and "primary" in token_info["role"] else 3.0
                is_pass = ratio is not None and ratio >= min_target
                calculated_ratios[token_name] = {
                    "hex": token_info["hex"],
                    "role": token_info["role"],
                    "contrast_ratio": ratio,
                    "min_required": min_target,
                    "contrast_result": "PASS" if is_pass else "FAIL",
                    "token_mapping": "MAPPED",
                }

            # Evaluate Live Inline Palette against dynamically located base background
            live_palette = data["fixtures"]["live_inline_palette"]["colors"]
            base_bg_color = next((c for c in live_palette if c.get("role") == "app_base_background"), None)
            assert base_bg_color is not None, "app_base_background must be defined in live_inline_palette"
            live_bg_rgb = hex_to_rgb(base_bg_color["hex"])

            live_ratios = {}
            for item in live_palette:
                if item["hex"] == base_bg_color["hex"]:
                    continue
                fg_rgb = hex_to_rgb(item["hex"])
                # G-05: Only text roles with unambiguous background pairing are evaluated for WCAG ratio
                is_text_role = "text" in item["role"]
                if is_text_role:
                    ratio, _ = calculate_contrast(fg_rgb, live_bg_rgb)
                    min_target = 4.5 if "primary" in item["role"] else 3.0
                    live_ratios[item["hex"]] = {
                        "role": item["role"],
                        "source": f"{item['source_file']}:{item['line']}",
                        "background_hex": base_bg_color["hex"],
                        "contrast_ratio": ratio,
                        "min_required": min_target,
                        "token_mapping": "UNMAPPED",
                        "contrast_result": "PASS" if (ratio is not None and ratio >= min_target) else "FAIL",
                    }
                else:
                    # G-05: Backgrounds/borders without text pairing must NOT be paired arbitrarily or claimed as contrast failure
                    live_ratios[item["hex"]] = {
                        "role": item["role"],
                        "source": f"{item['source_file']}:{item['line']}",
                        "contrast_ratio": None,
                        "min_required": None,
                        "token_mapping": "UNMAPPED",
                        "contrast_result": "NOT_VERIFIABLE",
                        "notes": "Container background / border without standalone text pairing per G-05",
                    }

            # Evaluate synthetic alpha test cases
            alpha_cases = data["fixtures"]["live_inline_palette"].get("synthetic_alpha_cases", [])
            alpha_evaluations = {}
            for ac in alpha_cases:
                rgba_parsed = parse_rgba_string(ac["rgba"])
                fg_parsed = hex_to_rgb(ac["foreground_text_hex"])
                assert rgba_parsed is not None, f"Invalid rgba string: {ac['rgba']}"
                ratio, status = calculate_contrast(fg_parsed, rgba_parsed, known_base_rgb=live_bg_rgb)
                alpha_evaluations[ac["role"]] = {
                    "overlay_rgba": ac["rgba"],
                    "source": f"{ac['source_file']}:{ac['line']}",
                    "composite_base_background": base_bg_color["hex"],
                    "foreground_text": ac["foreground_text_hex"],
                    "contrast_ratio": ratio,
                    "contrast_result": "PASS" if (ratio is not None and ratio >= 4.5) else "FAIL",
                    "token_mapping": "UNMAPPED",
                }

            self.record_verdict(
                "PRE-03",
                "f_token_and_palette_math_model",
                "PASS",
                "TOKEN_MODEL",
                0,
                details={
                    "direction_f_tokens_evaluated": calculated_ratios,
                    "live_inline_palette_evaluated": live_ratios,
                    "synthetic_alpha_cases_evaluated": alpha_evaluations,
                },
            )
        except Exception as exc:
            all_passed = False
            self.record_verdict(
                "PRE-03",
                "f_token_and_palette_math_model",
                "FAIL",
                "TOKEN_MODEL",
                1,
                blocker_reason=f"Token evaluation error: {exc}",
            )

        return all_passed

    def register_runtime_blocked_scenarios(self) -> None:
        """Registers AC1-AC6 runtime scenarios as BLOCKED under Hard Build Barrier."""
        barrier_reason = (
            "Hard Build Barrier Active: tauri_build side-effects write into source tree "
            "(gen/schemas and permission TOMLs), and fixed baseline lacks trusted sidecar inputs. "
            "Building Cargo/Tauri binaries in this Owner worktree is strictly prohibited. "
            "Awaiting Codex scratch worktree registration and independent Review."
        )

        runtime_scenarios = [
            ("AC1", "real_webview2_harness_spawn", "REAL_WEBVIEW2"),
            ("AC2", "workbench_navigation_and_interaction", "REAL_WEBVIEW2"),
            ("AC3", "quiet_period_300ms_and_invalidation", "REAL_WEBVIEW2"),
            ("AC4", "post_write_refresh_immediate", "REAL_WEBVIEW_MOCK_IPC"),
            ("AC5", "keyboard_and_focus_navigation", "REAL_WEBVIEW2"),
            ("AC6", "runtime_computed_color_extraction", "REAL_WEBVIEW2"),
        ]

        for ac_id, scenario_name, layer in runtime_scenarios:
            self.record_verdict(
                ac_id,
                scenario_name,
                "BLOCKED",
                layer,
                exit_code=None,  # Observed exit is null since scenario was blocked before process launch
                details={
                    "source_head": self.git_info["head"],
                    "source_tree": self.git_info["tree"],
                    "behavior_baseline": self.git_info["behavior_baseline_commit"],
                    "note": (
                        "Per task contract, blocked runtime scenario retains BLOCKED; "
                        "cannot be satisfied with NOT_RUN or fake timers."
                    ),
                },
                blocker_reason=barrier_reason,
            )

    def persist_results(self) -> None:
        """AC7: Persists structured evidence files with pure LF line endings."""
        report = {
            "task_id": "P02",
            "owner": "Antigravity",
            "stage": "STAGE_A_SAFE_FOUNDATION_R3",
            "provenance": {
                "source_head": self.git_info["head"],
                "source_tree": self.git_info["tree"],
                "branch": self.git_info["branch"],
                "behavior_baseline_commit": self.git_info["behavior_baseline_commit"],
                "key_source_files_sha256": self.git_info["source_files_sha256"],
                "note": "Delivery commit will be created after these files are generated; exact head will be verified by Codex Gate.",
            },
            "host_platform": platform.platform(),
            "verdicts": self.verdicts,
            "summary": {
                "total": len(self.verdicts),
                "pass": sum(1 for v in self.verdicts if v["status"] == "PASS"),
                "fail": sum(1 for v in self.verdicts if v["status"] == "FAIL"),
                "blocked": sum(1 for v in self.verdicts if v["status"] == "BLOCKED"),
                "not_run": sum(1 for v in self.verdicts if v["status"] == "NOT_RUN"),
            },
            "hard_build_barrier": {
                "active": True,
                "reason": (
                    "Cargo/Tauri builds prohibited in Owner worktree to prevent source-tree corruption. "
                    "Awaiting Codex scratch worktree registration and independent Review."
                ),
            },
        }

        json_out = VERIFICATION_DIR / "p02-harness-results.json"
        txt_out = VERIFICATION_DIR / "p02-harness-results.txt"

        with json_out.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")

        lines = [
            "=== P02 Real Workbench WebView2 Harness Verdict Report (Stage A r3) ===",
            f"Source HEAD: {self.git_info['head']}",
            f"Source Tree: {self.git_info['tree']}",
            f"Branch: {self.git_info['branch']}",
            f"Behavior Baseline: {self.git_info['behavior_baseline_commit']}",
            f"Total Scenarios: {report['summary']['total']}",
            f"  PASS: {report['summary']['pass']}",
            f"  FAIL: {report['summary']['fail']}",
            f"  BLOCKED: {report['summary']['blocked']}",
            f"  NOT_RUN: {report['summary']['not_run']}",
            "--- Scenario Details ---",
        ]
        for v in self.verdicts:
            exit_str = "null" if v["exit_code"] is None else str(v["exit_code"])
            line = f"[{v['scenario_id']}] {v['scenario_name']}: {v['status']} (Layer: {v['layer']}, Exit: {exit_str})"
            if v["blocker_reason"]:
                line += f" -> Blocker: {v['blocker_reason']}"
            lines.append(line)

        with txt_out.open("w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

        print("\n".join(lines))


def main() -> int:
    harness = WorkbenchHarness()
    preflight_ok = harness.run_preflight_checks()
    harness.register_runtime_blocked_scenarios()
    harness.persist_results()
    return 0 if preflight_ok else 1


if __name__ == "__main__":
    sys.exit(main())
