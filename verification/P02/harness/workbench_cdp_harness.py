"""P02 Real Workbench WebView2 Verification Harness (Stage A r2).

Stage A preflight and verdict report generator.
NOTE: Interactive CDP and live WebView2 behavioral driving are NOT yet active
in Stage A (held BLOCKED under the Hard Build Barrier awaiting authorized
scratch-build registration by Codex).

Responsibilities in Stage A:
- Validates synthetic fixture contracts and schema integrity (PRE-01)
- Validates static source contract and front-end control probe (PRE-02)
- Evaluates Visual Direction F token mathematical contrast model with alpha blending (PRE-03)
- Registers AC1-AC6 runtime verification scenarios honestly as BLOCKED
- Formats and persists structured verdicts according to AC7 requirements
"""

from __future__ import annotations

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


def get_git_info() -> dict[str, str]:
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

    return {
        "head": run_git(["rev-parse", "HEAD"]),
        "tree": run_git(["rev-parse", "HEAD^{tree}"]),
        "branch": run_git(["branch", "--show-current"]),
        "behavior_baseline_commit": BEHAVIOR_BASELINE_COMMIT,
    }


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c + c for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


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
    bg_rgb: tuple[int, int, int],
) -> float:
    if len(fg_rgba) == 4:
        effective_fg = blend_alpha(fg_rgba, bg_rgb)  # type: ignore[arg-type]
    else:
        effective_fg = fg_rgba  # type: ignore[assignment]

    l1 = calculate_luminance(effective_fg)
    l2 = calculate_luminance(bg_rgb)
    brighter = max(l1, l2)
    darker = min(l1, l2)
    return round((brighter + 0.05) / (darker + 0.05), 2)


def self_test_contrast_math() -> None:
    # Black (#000000) on White (#ffffff) must be 21:1
    ratio_bw = calculate_contrast((0, 0, 0), (255, 255, 255))
    assert ratio_bw == 21.0, f"Expected 21.0, got {ratio_bw}"

    # Same colors must be 1:1
    ratio_same = calculate_contrast((100, 100, 100), (100, 100, 100))
    assert ratio_same == 1.0, f"Expected 1.0, got {ratio_same}"

    # Semi-transparent black (alpha=0.5) over white creates #808080 (128, 128, 128)
    # Contrast of (128, 128, 128) on (255, 255, 255) is ~3.98:1
    ratio_alpha = calculate_contrast((0, 0, 0, 0.5), (255, 255, 255))
    assert ratio_alpha > 3.9 and ratio_alpha < 4.1, f"Expected ~3.98, got {ratio_alpha}"


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

        # 1. PRE-01: Synthetic Fixture Integrity
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
            required_sections = [
                "books",
                "chapters",
                "pages",
                "regions",
                "post_write_scenarios",
                "visual_direction_f_tokens",
                "live_inline_palette",
            ]
            missing_sections = [s for s in required_sections if s not in fixtures]
            if missing_sections:
                self.record_verdict(
                    "PRE-01",
                    "synthetic_fixture_presence",
                    "FAIL",
                    "FILESYSTEM",
                    1,
                    blocker_reason=f"Missing fixture sections: {missing_sections}",
                )
                return False

            self.record_verdict(
                "PRE-01",
                "synthetic_fixture_presence",
                "PASS",
                "FILESYSTEM",
                0,
                details={
                    "sections_validated": list(fixtures.keys()),
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
                blocker_reason=f"Invalid fixture JSON: {exc}",
            )
            return False

        # 2. PRE-02: Run static control probe
        probe_py = VERIFICATION_DIR / "probes" / "static_control_probe.py"
        if probe_py.exists():
            res = subprocess.run([sys.executable, str(probe_py)], capture_output=True, text=True)
            probe_pass = (res.returncode == 0)
            if not probe_pass:
                all_passed = False
            self.record_verdict(
                "PRE-02",
                "static_source_contract_check",
                "PASS" if probe_pass else "FAIL",
                "STATIC_AST",
                res.returncode,
                details={"stdout": res.stdout.strip(), "stderr": res.stderr.strip()},
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
                ratio = calculate_contrast(fg_rgb, bg_page_rgb)
                min_target = 4.5 if "text" in token_info["role"] and "primary" in token_info["role"] else 3.0
                calculated_ratios[token_name] = {
                    "hex": token_info["hex"],
                    "role": token_info["role"],
                    "contrast_ratio": ratio,
                    "min_required": min_target,
                    "contrast_result": "PASS" if ratio >= min_target else "FAIL",
                    "token_mapping": "MAPPED",
                }

            # Evaluate Live Inline Palette against App Base Background
            live_palette = data["fixtures"]["live_inline_palette"]["colors"]
            live_bg_hex = "#101418"
            live_bg_rgb = hex_to_rgb(live_bg_hex)
            live_ratios = {}
            for item in live_palette:
                if item["hex"] == live_bg_hex:
                    continue
                fg_rgb = hex_to_rgb(item["hex"])
                ratio = calculate_contrast(fg_rgb, live_bg_rgb)
                live_ratios[item["hex"]] = {
                    "role": item["role"],
                    "source": f"{item['source_file']}:{item['line']}",
                    "contrast_ratio": ratio,
                    "token_mapping": "UNMAPPED",
                    "contrast_result": "PASS" if ratio >= 3.0 else "FAIL",
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
                exit_code=None,  # Observed exit is None since scenario was blocked before process launch
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
            "stage": "STAGE_A_SAFE_FOUNDATION_R2",
            "provenance": {
                "source_head": self.git_info["head"],
                "source_tree": self.git_info["tree"],
                "branch": self.git_info["branch"],
                "behavior_baseline_commit": self.git_info["behavior_baseline_commit"],
                "evidence_carrier": "verification/P02/p02-harness-results.json",
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
            "=== P02 Real Workbench WebView2 Harness Verdict Report (Stage A r2) ===",
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
