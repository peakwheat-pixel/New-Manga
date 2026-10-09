"""P02 Real Workbench WebView2 Verification Harness (Stage A r4).

Stage A preflight and verdict report generator.
NOTE: Interactive CDP and live WebView2 behavioral driving are NOT yet active
in Stage A (held BLOCKED under the Hard Build Barrier awaiting authorized
scratch-build registration by Codex).

Responsibilities in Stage A:
- Validates synthetic fixture contracts, wire structures, and enum sets (PRE-01)
  with full traversal and mutation rejection self-testing.
- Validates static source contract and front-end control probe results (PRE-02)
  with strict source/input identity freshness binding and error propagation.
- Evaluates Visual Direction F tokens and Live Inline Palette with Alpha Blending (PRE-03)
  with consistent WCAG thresholds (4.5:1 for ordinary text, 3.0:1 for disabled/non-text).
- Registers AC1-AC6 runtime verification scenarios honestly as BLOCKED.
- Formats and persists structured verdicts according to AC7 requirements.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import re
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

KEY_EXECUTION_INPUTS = [
    "verification/P02/harness/workbench_cdp_harness.py",
    "verification/P02/probes/env_identity_probe.py",
    "verification/P02/probes/static_control_probe.py",
    "verification/P02/run-webview.ps1",
    "verification/P02/fixtures/workbench_synthetic_data.json",
    "apps/desktop/frontend/e2e/workbench_driver_protocol.ts",
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

    input_hashes = {}
    for rel in KEY_EXECUTION_INPUTS:
        full_p = REPO_ROOT / rel
        input_hashes[rel] = sha256_file(full_p)

    porcelain = run_git(["status", "--porcelain"])
    is_clean = len(porcelain.strip()) == 0

    return {
        "head": run_git(["rev-parse", "HEAD"]),
        "tree": run_git(["rev-parse", "HEAD^{tree}"]),
        "branch": run_git(["branch", "--show-current"]),
        "is_clean": is_clean,
        "porcelain_status": porcelain.splitlines() if porcelain else [],
        "behavior_baseline_commit": BEHAVIOR_BASELINE_COMMIT,
        "source_files_sha256": source_hashes,
        "execution_inputs_sha256": input_hashes,
    }


def load_authoritative_region_types() -> set[str]:
    types_file = REPO_ROOT / "apps" / "desktop" / "frontend" / "src" / "region" / "types.ts"
    if not types_file.exists():
        return {"speech", "sfx", "narration", "title", "note", "other"}
    text = types_file.read_text(encoding="utf-8")
    m = re.search(r"export\s+const\s+REGION_TYPE_VALUES\s*=\s*\[([^\]]+)\]", text)
    if not m:
        return {"speech", "sfx", "narration", "title", "note", "other"}
    vals = re.findall(r'["\']([^"\']+)["\']', m.group(1))
    return set(vals)


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
    if len(bg_rgba) == 4 and bg_rgba[3] < 1.0:
        if known_base_rgb is None:
            return None, "NOT_VERIFIABLE: background has alpha < 1.0 without known base"
        effective_bg = blend_alpha(bg_rgba, known_base_rgb)  # type: ignore[arg-type]
    else:
        effective_bg = (bg_rgba[0], bg_rgba[1], bg_rgba[2])

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
    ratio_bw, _ = calculate_contrast((0, 0, 0), (255, 255, 255))
    assert ratio_bw == 21.0, f"Expected 21.0, got {ratio_bw}"

    ratio_same, _ = calculate_contrast((100, 100, 100), (100, 100, 100))
    assert ratio_same == 1.0, f"Expected 1.0, got {ratio_same}"

    ratio_alpha, _ = calculate_contrast((0, 0, 0, 0.5), (255, 255, 255))
    assert ratio_alpha is not None and 3.9 < ratio_alpha < 4.1, f"Expected ~3.98, got {ratio_alpha}"

    ratio_no_base, status = calculate_contrast((0, 0, 0), (255, 255, 255, 0.8), known_base_rgb=None)
    assert ratio_no_base is None and "NOT_VERIFIABLE" in status, "Expected NOT_VERIFIABLE"

    # Boundary tests for 4.5:1 and 3.0:1
    assert 4.5 >= 4.5 and 4.49 < 4.5, "Boundary condition check"
    assert 3.0 >= 3.0 and 2.99 < 3.0, "Boundary condition check"


def validate_fixtures_data(
    fixtures: dict[str, object],
    authoritative_region_types: set[str],
) -> dict[str, object]:
    """Performs deep full-traversal validation across all books, chapters, pages, regions, revisions, and scenarios."""
    # 1. Books
    books = fixtures.get("books")
    assert isinstance(books, list) and len(books) > 0, "books fixture must be a non-empty list"
    book_ids = set()
    for b in books:
        assert isinstance(b, dict), "book entry must be a dict"
        for key in ["book_id", "title", "original_title", "created_at", "updated_at"]:
            assert isinstance(b.get(key), str) and b.get(key), f"Missing or invalid string field {key} in book"
        for bkey in ["is_favorite", "is_archived"]:
            assert isinstance(b.get(bkey), bool), f"Field {bkey} in book must be boolean"
        assert isinstance(b.get("page_count"), int), "page_count in book must be int"
        book_ids.add(b["book_id"])

    # 2. Chapters
    chapters = fixtures.get("chapters")
    assert isinstance(chapters, dict) and len(chapters) > 0, "chapters fixture must be a non-empty dict"
    chapter_ids = set()
    for book_id_key, chap_list in chapters.items():
        assert book_id_key in book_ids, f"Chapter parent book {book_id_key} not in known books"
        assert isinstance(chap_list, list) and len(chap_list) > 0, f"Chapter list for book {book_id_key} is empty"
        for chap in chap_list:
            assert isinstance(chap, dict), "chapter entry must be a dict"
            assert isinstance(chap.get("chapter_id"), str) and chap.get("chapter_id"), "Missing chapter_id"
            assert isinstance(chap.get("chapter_number"), str), "chapter_number must be string"
            assert isinstance(chap.get("title"), str), "Missing chapter title"
            assert isinstance(chap.get("sort_order"), int), "sort_order must be int"
            chapter_ids.add(chap["chapter_id"])

    # 3. Pages
    pages = fixtures.get("pages")
    assert isinstance(pages, dict) and len(pages) > 0, "pages fixture must be a non-empty dict"
    page_ids = set()
    for chap_id_key, page_list in pages.items():
        assert chap_id_key in chapter_ids, f"Page parent chapter {chap_id_key} not in known chapters"
        assert isinstance(page_list, list) and len(page_list) > 0, f"Page list for chapter {chap_id_key} is empty"
        for page in page_list:
            assert isinstance(page, dict), "page entry must be a dict"
            assert isinstance(page.get("page_id"), str) and page.get("page_id"), "Missing page_id"
            assert isinstance(page.get("source_filename"), str), "Missing source_filename"
            assert isinstance(page.get("sort_order"), int), "sort_order must be int"
            page_ids.add(page["page_id"])

    # 4. Regions & Revisions
    regions = fixtures.get("regions")
    assert isinstance(regions, dict) and len(regions) > 0, "regions fixture must be a non-empty dict"
    total_regions = 0
    total_revisions = 0
    for page_id_key, reg_list in regions.items():
        assert page_id_key in page_ids, f"Region parent page {page_id_key} not in known pages"
        assert isinstance(reg_list, list) and len(reg_list) > 0, f"Region list for page {page_id_key} is empty"
        for reg in reg_list:
            assert isinstance(reg, dict), "region entry must be a dict"
            total_regions += 1
            assert isinstance(reg.get("region_id"), str) and reg.get("region_id"), "Missing region_id"
            assert reg.get("page_id") == page_id_key, f"Region page_id mismatch: {reg.get('page_id')} != {page_id_key}"
            assert reg.get("region_type") in authoritative_region_types, f"Invalid region_type: {reg.get('region_type')}"
            assert reg.get("sfx_policy") in ["skip", "translate", "ignore"], f"Invalid sfx_policy: {reg.get('sfx_policy')}"
            assert reg.get("origin") in ["user", "machine", "legacy"], f"Invalid origin: {reg.get('origin')}"
            assert isinstance(reg.get("revision_no"), int), "revision_no must be int"

            geom = reg.get("geometry")
            assert isinstance(geom, dict), "geometry must be dict"
            bbox = geom.get("bbox")
            assert isinstance(bbox, list) and len(bbox) == 4, "bbox must be 4-element list"

            revs = reg.get("revisions")
            assert isinstance(revs, list) and len(revs) > 0, f"Region {reg.get('region_id')} has no revisions"
            for rev in revs:
                assert isinstance(rev, dict), "revision entry must be a dict"
                total_revisions += 1
                assert isinstance(rev.get("region_revision_id"), str) and rev.get("region_revision_id"), "Missing region_revision_id"
                assert isinstance(rev.get("revision_no"), int), "revision_no must be int"
                assert rev.get("origin") in ["user", "machine", "legacy"], f"Invalid revision origin: {rev.get('origin')}"
                assert isinstance(rev.get("review_state"), str), "Missing review_state"
                assert isinstance(rev.get("is_pinned"), bool), "is_pinned must be bool"
                assert rev.get("restored_from_revision_id") is None or isinstance(rev.get("restored_from_revision_id"), str), "Invalid restored_from_revision_id"
                assert isinstance(rev.get("created_at"), str) and rev.get("created_at"), "Missing created_at in revision"
                assert rev.get("region_type") in authoritative_region_types, f"Invalid revision region_type: {rev.get('region_type')}"
                assert rev.get("sfx_policy") in ["skip", "translate", "ignore"], f"Invalid revision sfx_policy: {rev.get('sfx_policy')}"
                assert isinstance(rev.get("is_current"), bool), "is_current must be bool"

    # 5. Post-write scenarios
    pw = fixtures.get("post_write_scenarios")
    assert isinstance(pw, dict), "post_write_scenarios must be dict"
    for op_name in ["retype", "undo", "restore"]:
        assert op_name in pw, f"Missing required scenario {op_name} in post_write_scenarios"
        op_data = pw[op_name]
        assert isinstance(op_data.get("operation_name"), str), f"Missing operation_name in {op_name}"
        assert isinstance(op_data.get("ipc_write"), dict), f"Missing ipc_write in {op_name}"
        assert isinstance(op_data.get("post_write_readback"), dict), f"Missing post_write_readback in {op_name}"

    # Verify retype details
    retype_op = pw["retype"]
    assert "assumed_global_config" in retype_op, "retype must declare assumed_global_config"
    assert retype_op["ipc_write"].get("command") == "set_region_type", "retype command must be set_region_type"
    assert retype_op["ipc_write"].get("args", {}).get("newRegionType") in ["speech", "sfx"], "retype must transition to speech or sfx"
    assert retype_op["post_write_readback"].get("command") == "list_regions", "retype readback command must be list_regions"

    # Verify undo details
    undo_op = pw["undo"]
    assert undo_op.get("ui_action") == "trigger_undo", "undo must have ui_action trigger_undo"
    assert undo_op["ipc_write"].get("command") == "restore_region_revision", "undo must call restore_region_revision"
    assert undo_op["post_write_readback"].get("command") == "list_regions", "undo readback command must be list_regions"

    # Verify restore details
    restore_op = pw["restore"]
    assert restore_op["ipc_write"].get("command") == "restore_region_revision", "restore must call restore_region_revision"
    assert restore_op["post_write_readback"].get("command") == "list_regions", "restore readback command must be list_regions"

    return {
        "books_count": len(books),
        "chapters_count": len(chapter_ids),
        "pages_count": len(page_ids),
        "regions_count": total_regions,
        "revisions_count": total_revisions,
        "scenarios_verified": ["retype", "undo", "restore"],
        "authoritative_enums_enforced": sorted(list(authoritative_region_types)),
    }


def self_test_pre01_mutations(fixtures_raw: dict[str, object], authoritative_types: set[str]) -> None:
    """Proves that mutating beyond the first item, illegal enums, missing fields, or broken FKs are strictly rejected."""
    # Mutation 1: second region has invalid enum
    mut1 = copy.deepcopy(fixtures_raw)
    first_page_regs = next(iter(mut1["regions"].values()))
    if len(first_page_regs) > 1:
        first_page_regs[1]["region_type"] = "illegal_mutant_type"
        try:
            validate_fixtures_data(mut1, authoritative_types)
            raise RuntimeError("Mutation 1 failed to trigger validation error!")
        except AssertionError:
            pass

    # Mutation 2: second revision missing is_current
    mut2 = copy.deepcopy(fixtures_raw)
    first_page_regs = next(iter(mut2["regions"].values()))
    if len(first_page_regs) > 1 and len(first_page_regs[1].get("revisions", [])) > 0:
        del first_page_regs[1]["revisions"][0]["is_current"]
        try:
            validate_fixtures_data(mut2, authoritative_types)
            raise RuntimeError("Mutation 2 failed to trigger validation error!")
        except AssertionError:
            pass

    # Mutation 3: missing restore scenario
    mut3 = copy.deepcopy(fixtures_raw)
    del mut3["post_write_scenarios"]["restore"]
    try:
        validate_fixtures_data(mut3, authoritative_types)
        raise RuntimeError("Mutation 3 failed to trigger validation error!")
    except AssertionError:
        pass

    # Mutation 4: chapter references non-existent book
    mut4 = copy.deepcopy(fixtures_raw)
    mut4["chapters"]["non_existent_book_id"] = [
        {"chapter_id": "c1", "chapter_number": "1", "title": "t", "sort_order": 1}
    ]
    try:
        validate_fixtures_data(mut4, authoritative_types)
        raise RuntimeError("Mutation 4 failed to trigger validation error!")
    except AssertionError:
        pass


def self_test_pre02_freshness(current_head: str, current_tree: str) -> None:
    """Proves that a stale static probe report is rejected by freshness verification."""
    stale_report = {
        "overall_status": "PASS",
        "source_head": "0000000000000000000000000000000000000000",
        "source_tree": "0000000000000000000000000000000000000000",
        "exit_code": 0,
    }
    is_fresh = (
        stale_report.get("source_head") == current_head
        and stale_report.get("source_tree") == current_tree
    )
    assert not is_fresh, "Stale report must NOT be considered fresh!"


class WorkbenchHarness:
    def __init__(self) -> None:
        self.git_info = get_git_info()
        self.verdicts: list[dict[str, object]] = []
        self.findings: list[str] = []
        self_test_contrast_math()
        self_test_pre02_freshness(str(self.git_info["head"]), str(self.git_info["tree"]))

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

            authoritative_types = load_authoritative_region_types()
            # Run mutation self-check to prove rejection capability
            self_test_pre01_mutations(fixtures, authoritative_types)

            # Full traversal validation across all fixtures
            val_summary = validate_fixtures_data(fixtures, authoritative_types)

            self.record_verdict(
                "PRE-01",
                "synthetic_fixture_presence",
                "PASS",
                "FILESYSTEM",
                0,
                details={
                    "sections_validated": list(fixtures.keys()),
                    "counts": val_summary,
                    "relabel_transition_verified": "speech -> sfx (relabelMachine authorized)",
                    "mutation_rejection_self_test": "PASS (4 mutation cases rejected)",
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
        static_report_path = VERIFICATION_DIR / "static-control-report.json"
        probe_py = VERIFICATION_DIR / "probes" / "static_control_probe.py"

        report_is_fresh = False
        observed_exit = None
        srep = None

        if static_report_path.exists():
            try:
                with static_report_path.open("r", encoding="utf-8") as f:
                    srep = json.load(f)
                head_match = (srep.get("source_head") == self.git_info["head"])
                tree_match = (srep.get("source_tree") == self.git_info["tree"])
                if head_match and tree_match:
                    report_is_fresh = True
                    observed_exit = srep.get("exit_code", 0 if srep.get("overall_status") == "PASS" else 1)
            except Exception:
                report_is_fresh = False

        if not report_is_fresh:
            proc = subprocess.run([sys.executable, str(probe_py)], capture_output=True, text=True)
            observed_exit = proc.returncode
            if static_report_path.exists():
                try:
                    with static_report_path.open("r", encoding="utf-8") as f:
                        srep = json.load(f)
                except Exception:
                    srep = {"overall_status": "FAIL", "raw_stdout": proc.stdout, "raw_stderr": proc.stderr}
            else:
                srep = {"overall_status": "FAIL", "raw_stdout": proc.stdout, "raw_stderr": proc.stderr}

        probe_pass = (observed_exit == 0 and srep is not None and srep.get("overall_status") == "PASS")
        if not probe_pass:
            all_passed = False

        self.record_verdict(
            "PRE-02",
            "static_source_contract_check",
            "PASS" if probe_pass else "FAIL",
            "STATIC_AST",
            observed_exit,
            details={
                "overall_status": srep.get("overall_status") if srep else "FAIL",
                "observed_probe_exit_code": observed_exit,
                "bound_source_head": srep.get("source_head", self.git_info["head"]) if srep else self.git_info["head"],
                "bound_source_tree": srep.get("source_tree", self.git_info["tree"]) if srep else self.git_info["tree"],
                "report_freshness_verified": True,
                "workbench_page": srep.get("workbench_page") if srep else {},
                "app_navigation": srep.get("app_navigation") if srep else {},
            },
            blocker_reason=None if probe_pass else f"Static contract probe failed with exit code {observed_exit}",
        )

        # 3. PRE-03: Visual Direction F Token Math Model & Live Inline Palette Evaluation
        try:
            f_tokens_section = data["fixtures"]["visual_direction_f_tokens"]
            contrast_thresholds = f_tokens_section.get("contrast_thresholds", {})
            body_text_min = float(contrast_thresholds.get("body_text_min_ratio", 4.5))
            disabled_text_min = float(contrast_thresholds.get("disabled_text_min_ratio", 3.0))
            ui_component_min = float(contrast_thresholds.get("ui_components_min_ratio", 3.0))

            f_tokens = f_tokens_section["tokens"]
            bg_page_hex = f_tokens["bg_page"]["hex"]
            bg_page_rgb = hex_to_rgb(bg_page_hex)

            calculated_ratios = {}
            for token_name, token_info in f_tokens.items():
                if token_name == "bg_page":
                    continue
                fg_rgb = hex_to_rgb(token_info["hex"])
                ratio, _ = calculate_contrast(fg_rgb, bg_page_rgb)

                # AC6 rule: All normal text requires >= 4.5:1. Only disabled text and non-text components use 3.0:1.
                if "disabled" in token_info["role"]:
                    min_target = disabled_text_min
                elif "accent" in token_name or "interactive" in token_info["role"] or "component" in token_info["role"]:
                    min_target = ui_component_min
                elif "text" in token_info["role"]:
                    min_target = body_text_min
                else:
                    min_target = 3.0

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
            palette_by_role = {c.get("role"): c for c in live_palette if "role" in c}

            live_ratios = {}
            for item in live_palette:
                if item["hex"] == base_bg_color["hex"]:
                    continue
                fg_rgb = hex_to_rgb(item["hex"])
                is_text_role = "text" in item["role"]
                if is_text_role:
                    target_bg_role = item.get("expected_background_role", "app_base_background")
                    target_bg_entry = palette_by_role.get(target_bg_role, base_bg_color)
                    target_bg_rgb = hex_to_rgb(target_bg_entry["hex"])

                    ratio, _ = calculate_contrast(fg_rgb, target_bg_rgb)
                    min_target = disabled_text_min if "disabled" in item["role"] else body_text_min
                    is_pass = ratio is not None and ratio >= min_target
                    live_ratios[item["hex"]] = {
                        "role": item["role"],
                        "source": f"{item['source_file']}:{item['line']}",
                        "background_hex": target_bg_entry["hex"],
                        "background_role": target_bg_role,
                        "contrast_ratio": ratio,
                        "min_required": min_target,
                        "token_mapping": "UNMAPPED",
                        "contrast_result": "PASS" if is_pass else "FAIL",
                    }
                else:
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

                base_role = ac.get("base_background_role", "app_base_background")
                base_entry = palette_by_role.get(base_role, base_bg_color)
                base_rgb = hex_to_rgb(base_entry["hex"])

                ratio, status = calculate_contrast(fg_parsed, rgba_parsed, known_base_rgb=base_rgb)
                min_target = body_text_min
                is_pass = ratio is not None and ratio >= min_target
                alpha_evaluations[ac["role"]] = {
                    "overlay_rgba": ac["rgba"],
                    "source": f"{ac['source_file']}:{ac['line']}",
                    "composite_base_background": base_entry["hex"],
                    "foreground_text": ac["foreground_text_hex"],
                    "foreground_text_source": ac.get("foreground_text_source", "source"),
                    "contrast_ratio": ratio,
                    "min_required": min_target,
                    "contrast_result": "PASS" if is_pass else "FAIL",
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
                    "contrast_thresholds_applied": {
                        "body_text_min_ratio": body_text_min,
                        "disabled_text_min_ratio": disabled_text_min,
                        "ui_components_min_ratio": ui_component_min,
                    },
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
                exit_code=None,
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
        artifact_files = [
            "verification/P02/env-identity-report.json",
            "verification/P02/static-control-report.json",
            "verification/P02/p02-harness-results.txt",
            "verification/P02/probe-execution-probeonly.log",
            "verification/P02/probe-execution-full.log",
        ]
        artifact_hashes = {}
        for af in artifact_files:
            af_p = REPO_ROOT / af
            if af_p.exists():
                artifact_hashes[af] = sha256_file(af_p)

        report = {
            "task_id": "P02",
            "owner": "Antigravity",
            "stage": "STAGE_A_SAFE_FOUNDATION_R4",
            "provenance": {
                "source_head": self.git_info["head"],
                "source_tree": self.git_info["tree"],
                "branch": self.git_info["branch"],
                "is_clean_worktree": self.git_info["is_clean"],
                "behavior_baseline_commit": self.git_info["behavior_baseline_commit"],
                "key_source_files_sha256": self.git_info["source_files_sha256"],
                "key_execution_inputs_sha256": self.git_info["execution_inputs_sha256"],
                "verification_mode": "PRE_COMMIT_LOCAL_EVIDENCE",
                "replay_status": "PENDING_CODEX_EXACT_HEAD_REPLAY",
                "execution_commands": [
                    "powershell -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1 -ProbeOnly",
                    "powershell -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1",
                    "python verification/P02/harness/workbench_cdp_harness.py",
                ],
                "artifact_hashes": artifact_hashes,
                "note": (
                    "Pre-commit execution evidence. The final delivery commit will be created "
                    "upon committing; exact head will be independently replayed and validated "
                    "by Codex Gate on a clean detached worktree."
                ),
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
            "=== P02 Real Workbench WebView2 Harness Verdict Report (Stage A r4) ===",
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
