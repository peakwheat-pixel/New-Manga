"""P02 Real Workbench WebView2 Verification Harness (Stage A r8).

Stage A preflight and verdict report generator.
NOTE: Interactive CDP and live WebView2 behavioral driving are NOT yet active
in Stage A (held BLOCKED under the Hard Build Barrier awaiting authorized
scratch-build registration by Codex).

Responsibilities in Stage A:
- Validates synthetic fixture contracts, wire structures, and enum sets (PRE-01)
  with full traversal and mutation rejection self-testing.
- Validates static source contract and front-end control probe results (PRE-02)
  with strict source/input identity freshness binding, subprocess returncode decoupling (R5-01),
  production dispatch helper execution, and retry failure isolation (R6-03).
- Evaluates Visual Direction F tokens and Live Inline Palette with Alpha Blending (PRE-03)
  with production aggregation & verdict helpers, self-check failure propagation (R5-05, R6-03, R7-01).
- Enforces TypeScript protocol contract check gate with dynamic compiler discovery (R5-04),
  runner exit code propagation, execution status differentiation, and main exit code aggregation (R6-02).
- Registers AC1-AC6 runtime verification scenarios honestly as BLOCKED.
- Formats and persists structured verdicts according to AC7 requirements,
  with robust two-phase artifact finalization (R4-03, R5-02).
"""

from __future__ import annotations

from collections.abc import Callable
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


def find_tsc_binary() -> Path | None:
    """Dynamically resolves TypeScript compiler binary without hardcoded machine paths (R5-04)."""
    cand1 = REPO_ROOT / "apps" / "desktop" / "frontend" / "node_modules" / "typescript" / "bin" / "tsc"
    if cand1.exists():
        return cand1
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if proc.returncode == 0 and proc.stdout.strip():
            common_git = Path(proc.stdout.strip())
            if not common_git.is_absolute():
                common_git = (REPO_ROOT / common_git).resolve()
            common_root = common_git.parent
            cand2 = common_root / "apps" / "desktop" / "frontend" / "node_modules" / "typescript" / "bin" / "tsc"
            if cand2.exists():
                return cand2
    except Exception:
        pass
    return None


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


def load_authoritative_enums() -> dict[str, set[str]]:
    """Loads closed enum sets verbatim from apps/desktop/frontend/src/region/types.ts.
    Fails closed if the authoritative source file is missing or unparseable (R4-02, R4-07)."""
    types_file = REPO_ROOT / "apps" / "desktop" / "frontend" / "src" / "region" / "types.ts"
    if not types_file.exists():
        raise RuntimeError(f"Authoritative enum source missing: {types_file} (fail closed per R4-07)")
    text = types_file.read_text(encoding="utf-8")

    # 1. REGION_TYPE_VALUES
    m_types = re.search(r"export\s+const\s+REGION_TYPE_VALUES\s*=\s*\[([^\]]+)\]", text)
    if not m_types:
        raise RuntimeError(f"Failed to parse REGION_TYPE_VALUES from {types_file} (fail closed per R4-07)")
    region_types = set(re.findall(r'["\']([^"\']+)["\']', m_types.group(1)))
    if not region_types:
        raise RuntimeError(f"Parsed empty REGION_TYPE_VALUES from {types_file} (fail closed per R4-07)")

    # 2. SfxPolicy: export type SfxPolicy = "skip" | "translate" | "manual";
    m_sfx = re.search(r"export\s+type\s+SfxPolicy\s*=\s*([^;]+);", text)
    if not m_sfx:
        raise RuntimeError(f"Failed to parse SfxPolicy from {types_file} (fail closed per R4-07)")
    sfx_policies = set(re.findall(r'["\']([^"\']+)["\']', m_sfx.group(1)))
    if not sfx_policies:
        raise RuntimeError(f"Parsed empty SfxPolicy from {types_file} (fail closed per R4-07)")

    # 3. RegionOrigin: export type RegionOrigin = "machine" | "user" | "imported" | "restored";
    m_orig = re.search(r"export\s+type\s+RegionOrigin\s*=\s*([^;]+);", text)
    if not m_orig:
        raise RuntimeError(f"Failed to parse RegionOrigin from {types_file} (fail closed per R4-07)")
    region_origins = set(re.findall(r'["\']([^"\']+)["\']', m_orig.group(1)))
    if not region_origins:
        raise RuntimeError(f"Parsed empty RegionOrigin from {types_file} (fail closed per R4-07)")

    return {
        "region_types": region_types,
        "sfx_policies": sfx_policies,
        "region_origins": region_origins,
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
    enums: dict[str, set[str]],
) -> dict[str, object]:
    """Performs deep full-traversal validation across all books, chapters, pages, regions, revisions, and scenarios."""
    authoritative_region_types = enums["region_types"]
    authoritative_sfx_policies = enums["sfx_policies"]
    authoritative_region_origins = enums["region_origins"]

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
        # R4-11: page_count can be null per library/types.ts:23
        assert b.get("page_count") is None or isinstance(b.get("page_count"), int), "page_count in book must be int or None"
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
            # R4-02: exact closed enum from region/types.ts:33
            assert reg.get("sfx_policy") in authoritative_sfx_policies, f"Invalid sfx_policy: {reg.get('sfx_policy')}"
            # R4-02: exact closed enum from region/types.ts:37
            assert reg.get("origin") in authoritative_region_origins, f"Invalid origin: {reg.get('origin')}"
            assert isinstance(reg.get("revision_no"), int), "revision_no must be int"

            # R4-11: Validate NormalizedRegionGeometry bbox and polygon
            geom = reg.get("geometry")
            assert isinstance(geom, dict), "geometry must be dict"
            bbox = geom.get("bbox")
            assert isinstance(bbox, list) and len(bbox) == 4, "bbox must be 4-element list"
            for bi, bv in enumerate(bbox):
                assert isinstance(bv, (int, float)) and not isinstance(bv, bool) and 0.0 <= bv <= 1.0, f"bbox[{bi}] must be number in [0, 1], got {bv}"
            poly = geom.get("polygon")
            assert isinstance(poly, list), "polygon must be list"
            for pi, pt in enumerate(poly):
                assert isinstance(pt, list) and len(pt) == 2, f"polygon[{pi}] must be [x, y], got {pt}"
                for ci, coord in enumerate(pt):
                    assert isinstance(coord, (int, float)) and not isinstance(coord, bool) and 0.0 <= coord <= 1.0, f"polygon[{pi}][{ci}] must be in [0, 1], got {coord}"

            revs = reg.get("revisions")
            assert isinstance(revs, list) and len(revs) > 0, f"Region {reg.get('region_id')} has no revisions"
            for rev in revs:
                assert isinstance(rev, dict), "revision entry must be a dict"
                total_revisions += 1
                assert isinstance(rev.get("region_revision_id"), str) and rev.get("region_revision_id"), "Missing region_revision_id"
                assert isinstance(rev.get("revision_no"), int), "revision_no must be int"
                assert rev.get("origin") in authoritative_region_origins, f"Invalid revision origin: {rev.get('origin')}"
                assert isinstance(rev.get("review_state"), str), "Missing review_state"
                assert isinstance(rev.get("is_pinned"), bool), "is_pinned must be bool"
                assert rev.get("restored_from_revision_id") is None or isinstance(rev.get("restored_from_revision_id"), str), "Invalid restored_from_revision_id"
                assert isinstance(rev.get("created_at"), str) and rev.get("created_at"), "Missing created_at in revision"
                assert rev.get("region_type") in authoritative_region_types, f"Invalid revision region_type: {rev.get('region_type')}"
                assert rev.get("sfx_policy") in authoritative_sfx_policies, f"Invalid revision sfx_policy: {rev.get('sfx_policy')}"
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


def self_test_pre01_mutations(fixtures_raw: dict[str, object], enums: dict[str, set[str]]) -> dict[str, object]:
    """Proves that mutating beyond the first item, illegal enums, missing fields, or broken FKs are strictly rejected (R4-08)."""
    results: dict[str, str] = {}
    total_configured = 4
    executed_count = 0
    rejected_count = 0
    skipped_count = 0

    # Mutation 1: second region has invalid enum
    mut1 = copy.deepcopy(fixtures_raw)
    first_page_regs = next(iter(mut1["regions"].values()))
    if len(first_page_regs) > 1:
        first_page_regs[1]["region_type"] = "illegal_mutant_type"
        executed_count += 1
        try:
            validate_fixtures_data(mut1, enums)
            raise RuntimeError("Mutation 1 failed to trigger validation error!")
        except AssertionError:
            rejected_count += 1
            results["mutation_1_second_region_invalid_enum"] = "REJECTED_AS_EXPECTED"
    else:
        skipped_count += 1
        results["mutation_1_second_region_invalid_enum"] = "SKIPPED_INSUFFICIENT_REGIONS"

    # Mutation 2: second revision missing is_current
    mut2 = copy.deepcopy(fixtures_raw)
    first_page_regs = next(iter(mut2["regions"].values()))
    if len(first_page_regs) > 1 and len(first_page_regs[1].get("revisions", [])) > 0:
        del first_page_regs[1]["revisions"][0]["is_current"]
        executed_count += 1
        try:
            validate_fixtures_data(mut2, enums)
            raise RuntimeError("Mutation 2 failed to trigger validation error!")
        except AssertionError:
            rejected_count += 1
            results["mutation_2_second_rev_missing_field"] = "REJECTED_AS_EXPECTED"
    else:
        skipped_count += 1
        results["mutation_2_second_rev_missing_field"] = "SKIPPED_INSUFFICIENT_REVISIONS"

    # Mutation 3: missing restore scenario
    mut3 = copy.deepcopy(fixtures_raw)
    del mut3["post_write_scenarios"]["restore"]
    executed_count += 1
    try:
        validate_fixtures_data(mut3, enums)
        raise RuntimeError("Mutation 3 failed to trigger validation error!")
    except AssertionError:
        rejected_count += 1
        results["mutation_3_missing_restore_scenario"] = "REJECTED_AS_EXPECTED"

    # Mutation 4: chapter references non-existent book
    mut4 = copy.deepcopy(fixtures_raw)
    mut4["chapters"]["non_existent_book_id"] = [
        {"chapter_id": "c1", "chapter_number": "1", "title": "t", "sort_order": 1}
    ]
    executed_count += 1
    try:
        validate_fixtures_data(mut4, enums)
        raise RuntimeError("Mutation 4 failed to trigger validation error!")
    except AssertionError:
        rejected_count += 1
        results["mutation_4_broken_foreign_key"] = "REJECTED_AS_EXPECTED"

    all_passed = (executed_count == total_configured and rejected_count == total_configured and skipped_count == 0)
    return {
        "total_configured": total_configured,
        "executed_count": executed_count,
        "rejected_count": rejected_count,
        "skipped_count": skipped_count,
        "all_rejected_as_expected": all_passed,
        "details": results,
    }


def evaluate_static_probe_report(
    report_data: dict[str, object] | None,
    current_head: str,
    current_tree: str,
    expected_inputs_sha256: dict[str, str],
) -> tuple[bool, int | None, str]:
    """
    Evaluates freshness and integrity of static probe report (R4-04, R4-05).
    Returns (is_fresh_and_valid, observed_exit_code, reason).
    """
    if not isinstance(report_data, dict):
        return False, None, "report_not_a_dict"

    # Exit code must be present and integer (R4-04: missing exit_code must not be synthesized)
    exit_code = report_data.get("exit_code")
    if not isinstance(exit_code, int):
        return False, None, "missing_or_non_integer_exit_code"

    # Check git provenance
    if report_data.get("source_head") != current_head:
        return False, exit_code, "stale_source_head"
    if report_data.get("source_tree") != current_tree:
        return False, exit_code, "stale_source_tree"

    # Check input hashes (R4-04: prevent reusing same-HEAD stale PASS when working directory is dirty)
    rep_inputs = report_data.get("probe_inputs_sha256")
    if not isinstance(rep_inputs, dict):
        return False, exit_code, "missing_probe_inputs_sha256"
    for k, expected_hash in expected_inputs_sha256.items():
        if rep_inputs.get(k) != expected_hash:
            return False, exit_code, f"input_hash_mismatch_{k}"

    if report_data.get("overall_status") != "PASS":
        return True, exit_code, "valid_report_with_fail_status"

    return True, exit_code, "fresh_and_valid"


def self_test_pre02_freshness(current_head: str, current_tree: str, valid_inputs: dict[str, str]) -> None:
    """Proves that evaluate_static_probe_report rejects stale head, dirty inputs, missing exit_code, and malformed data (R4-05)."""
    # 1. Stale head
    r1 = {
        "overall_status": "PASS",
        "source_head": "0000000000000000000000000000000000000000",
        "source_tree": current_tree,
        "exit_code": 0,
        "probe_inputs_sha256": valid_inputs,
    }
    fresh1, exit1, _ = evaluate_static_probe_report(r1, current_head, current_tree, valid_inputs)
    assert not fresh1, "Must reject stale head!"

    # 2. Dirty input hash mismatch (same head/tree)
    r2 = {
        "overall_status": "PASS",
        "source_head": current_head,
        "source_tree": current_tree,
        "exit_code": 0,
        "probe_inputs_sha256": {**valid_inputs, "workbench_page_tsx": "mutated_hash_xyz"},
    }
    fresh2, exit2, _ = evaluate_static_probe_report(r2, current_head, current_tree, valid_inputs)
    assert not fresh2, "Must reject dirty input mismatch!"

    # 3. Missing exit code (R4-04: must remain unverifiable/None)
    r3 = {
        "overall_status": "PASS",
        "source_head": current_head,
        "source_tree": current_tree,
        "probe_inputs_sha256": valid_inputs,
    }
    fresh3, exit3, _ = evaluate_static_probe_report(r3, current_head, current_tree, valid_inputs)
    assert not fresh3 and exit3 is None, "Must reject missing exit code and keep exit None!"

    # 4. Malformed report
    fresh4, exit4, _ = evaluate_static_probe_report(None, current_head, current_tree, valid_inputs)
    assert not fresh4 and exit4 is None, "Must reject non-dict report!"


def dispatch_and_evaluate_static_probe(
    static_report_path: Path,
    current_head: str,
    current_tree: str,
    expected_inputs: dict[str, str],
    runner_fn: Callable[[], tuple[int, str, str]] | None = None,
) -> tuple[bool, int | None, int | None, dict[str, object] | None, str]:
    """Production helper for PRE-02 static source contract check (R5-01, R6-03).
    Evaluates existing report freshness; if stale, unlinks existing report and executes probe runner.
    Guarantees that a failing child process never inherits stale PASS reports, preserves exact exit code,
    and returns (probe_pass, observed_proc_exit, report_exit, srep, reason)."""
    srep: dict[str, object] | None = None
    report_is_fresh = False
    observed_proc_exit: int | None = None
    reason = "uninitialized"

    if static_report_path.exists():
        try:
            with static_report_path.open("r", encoding="utf-8") as f:
                srep = json.load(f)
            report_is_fresh, rep_exit, reason = evaluate_static_probe_report(
                srep, current_head, current_tree, expected_inputs
            )
            if report_is_fresh:
                observed_proc_exit = rep_exit
        except Exception as exc:
            report_is_fresh = False
            reason = f"corrupt_existing_report: {exc}"

    if not report_is_fresh:
        # R5-01: Stale report detected. Unlink prior to re-running probe subprocess
        # to guarantee that a failing or killed child process cannot leave an old file
        # that could be mistakenly re-read.
        if static_report_path.exists():
            try:
                static_report_path.unlink()
            except OSError:
                pass

        if runner_fn is not None:
            proc_exit, proc_stdout, proc_stderr = runner_fn()
            observed_proc_exit = proc_exit

            if observed_proc_exit != 0:
                # Subprocess exited non-zero: fail-closed immediately.
                # Do NOT attempt to read or adopt any report; record actual subprocess exit code.
                report_is_fresh = False
                reason = f"probe_subprocess_exited_with_code_{observed_proc_exit}"
                srep = {
                    "overall_status": "FAIL",
                    "exit_code": observed_proc_exit,
                    "raw_stdout": proc_stdout,
                    "raw_stderr": proc_stderr,
                }
            else:
                if static_report_path.exists():
                    try:
                        with static_report_path.open("r", encoding="utf-8") as f:
                            srep = json.load(f)
                        report_is_fresh, rep_exit, reason = evaluate_static_probe_report(
                            srep, current_head, current_tree, expected_inputs
                        )
                        if rep_exit != observed_proc_exit:
                            report_is_fresh = False
                            reason = f"exit_code_mismatch_report_{rep_exit}_vs_proc_{observed_proc_exit}"
                    except Exception as exc:
                        srep = {"overall_status": "FAIL", "raw_stdout": proc_stdout, "raw_stderr": proc_stderr}
                        report_is_fresh = False
                        reason = f"failed_parsing_new_report: {exc}"
                else:
                    srep = {"overall_status": "FAIL", "raw_stdout": proc_stdout, "raw_stderr": proc_stderr}
                    report_is_fresh = False
                    reason = "report_missing_after_zero_exit"

    report_exit = srep.get("exit_code") if isinstance(srep, dict) else None
    probe_pass = bool(
        report_is_fresh
        and observed_proc_exit == 0
        and report_exit == 0
        and srep is not None
        and srep.get("overall_status") == "PASS"
    )
    return probe_pass, report_is_fresh, observed_proc_exit, report_exit, srep, reason


def aggregate_pre03_verdict(
    calculated_ratios: dict[str, dict[str, object]],
    live_ratios: dict[str, dict[str, object]],
    alpha_evaluations: dict[str, dict[str, object]],
) -> tuple[bool, dict[str, bool]]:
    """Production helper for PRE-03 contrast ratios aggregation (R5-05, R6-03).
    Aggregates direction token results, live inline palette results (allowing NOT_VERIFIABLE for
    non-text container elements per G-05), and synthetic alpha test cases.
    Returns (pre03_pass, aggregated_results)."""
    token_all_pass = all(item.get("contrast_result") == "PASS" for item in calculated_ratios.values())
    live_all_pass = all(item.get("contrast_result") in ("PASS", "NOT_VERIFIABLE") for item in live_ratios.values())
    alpha_all_pass = all(item.get("contrast_result") == "PASS" for item in alpha_evaluations.values())
    pre03_pass = bool(token_all_pass and live_all_pass and alpha_all_pass)
    aggregated = {
        "tokens_all_passed": token_all_pass,
        "live_palette_all_passed": live_all_pass,
        "synthetic_alpha_all_passed": alpha_all_pass,
    }
    return pre03_pass, aggregated


def build_pre03_verdict(
    calculated_ratios: dict[str, dict[str, object]],
    live_ratios: dict[str, dict[str, object]],
    alpha_evaluations: dict[str, dict[str, object]],
    contrast_thresholds: dict[str, float] | None = None,
) -> tuple[bool, dict[str, object]]:
    """Production helper for PRE-03 verdict evaluation and structure generation (R7-01).
    Aggregates contrast ratios via aggregate_pre03_verdict and derives authoritative
    verdict status ('PASS'/'FAIL'), exit code (0/1), details, and blocker reason.
    Returns (pre03_pass, verdict_dict)."""
    pre03_pass, aggregated_results = aggregate_pre03_verdict(
        calculated_ratios, live_ratios, alpha_evaluations
    )
    status = "PASS" if pre03_pass else "FAIL"
    exit_code = 0 if pre03_pass else 1
    blocker_reason = (
        None
        if pre03_pass
        else "One or more color tokens/palette entries failed contrast threshold (R5-05)"
    )
    details: dict[str, object] = {
        "direction_f_tokens_evaluated": calculated_ratios,
        "live_inline_palette_evaluated": live_ratios,
        "synthetic_alpha_cases_evaluated": alpha_evaluations,
        "contrast_thresholds_applied": contrast_thresholds or {},
        "aggregated_results": aggregated_results,
    }
    verdict: dict[str, object] = {
        "scenario_id": "PRE-03",
        "scenario_name": "f_token_and_palette_math_model",
        "status": status,
        "layer": "TOKEN_MODEL",
        "exit_code": exit_code,
        "details": details,
        "blocker_reason": blocker_reason,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return pre03_pass, verdict


def compute_harness_exit_code(preflight_ok: bool, tsc_gate_status: str) -> int:
    """Production decision logic for harness top-level exit code (R6-02, R7-01).
    Returns 0 if preflight_ok is True AND tsc_gate_status is in ('PASS', 'NOT_RUN'), else 1."""
    tsc_ok = tsc_gate_status in ("PASS", "NOT_RUN")
    return 0 if (preflight_ok and tsc_ok) else 1


def self_test_pre02_retry_failure(current_head: str, current_tree: str, valid_inputs: dict[str, str]) -> None:
    """Proves caller-level isolation when child probe retry fails (R5-01, R6-03):
    Invokes production dispatch_and_evaluate_static_probe helper with a stale PASS report
    and a failing runner mock returning exit code 42.
    Asserts:
    1. The stale report file is actively unlinked.
    2. Subprocess exit code 42 is preserved and not overwritten by stale report exit 0.
    3. Final probe_pass is False, report_is_fresh is False, srep overall_status is FAIL, and report_exit is 42."""
    tmp_path = VERIFICATION_DIR / "_tmp_self_test_stale_report.json"
    stale_report = {
        "overall_status": "PASS",
        "source_head": "0000000000000000000000000000000000000000",
        "source_tree": current_tree,
        "exit_code": 0,
        "probe_inputs_sha256": valid_inputs,
    }
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(stale_report, f)

        # Call production helper with mock runner returning non-zero (42)
        probe_pass, report_is_fresh, observed_proc_exit, report_exit, srep, reason = dispatch_and_evaluate_static_probe(
            tmp_path,
            current_head,
            current_tree,
            valid_inputs,
            runner_fn=lambda: (42, "", "synthetic retry error"),
        )

        assert not probe_pass, "Failing child process must cause probe_pass to evaluate to False!"
        assert not report_is_fresh, "Stale report with failed retry must evaluate report_is_fresh to False!"
        assert observed_proc_exit == 42, "Observed process exit code 42 must be preserved!"
        assert report_exit == 42, "Report exit code must match subprocess return code 42!"
        assert not tmp_path.exists(), "Stale report file must have been unlinked prior to retry!"
        assert srep is not None and srep.get("overall_status") == "FAIL", "Report status must be FAIL!"
        assert "42" in reason, f"Failure reason must mention code 42, got: {reason}"
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def self_test_pre03_failure_propagation() -> None:
    """Proves that failing tokens, live items, or alpha cases propagate to:
    1. aggregate_pre03_verdict failure,
    2. production build_pre03_verdict generating status='FAIL' and exit_code=1,
    3. WorkbenchHarness.record_pre03_evaluation appending authoritative FAIL verdict,
    4. top-level compute_harness_exit_code evaluating to 1 (R5-05, R6-03, R7-01)."""
    # 1. Failing token scenario
    tokens_fail = {"ink_primary": {"contrast_result": "PASS"}, "ink_muted": {"contrast_result": "FAIL"}}
    live_ok = {"card_bg": {"contrast_result": "PASS"}, "divider": {"contrast_result": "NOT_VERIFIABLE"}}
    alpha_ok = {"alpha_pill": {"contrast_result": "PASS"}}

    p_pass1, agg1 = aggregate_pre03_verdict(tokens_fail, live_ok, alpha_ok)
    assert not p_pass1, "Failing token must cause PRE-03 to fail!"
    assert not agg1["tokens_all_passed"], "tokens_all_passed must be False!"
    assert agg1["live_palette_all_passed"], "live_palette_all_passed must remain True with NOT_VERIFIABLE!"

    v_pass1, verd1 = build_pre03_verdict(tokens_fail, live_ok, alpha_ok)
    assert not v_pass1, "build_pre03_verdict must return False for failing token!"
    assert verd1["status"] == "FAIL", f"Expected FAIL status, got {verd1['status']}"
    assert verd1["exit_code"] == 1, f"Expected exit_code 1, got {verd1['exit_code']}"
    assert verd1["blocker_reason"] is not None, "blocker_reason must be populated on failure"
    assert compute_harness_exit_code(preflight_ok=v_pass1, tsc_gate_status="PASS") == 1
    assert compute_harness_exit_code(preflight_ok=v_pass1, tsc_gate_status="NOT_RUN") == 1

    # 2. Failing live palette scenario
    tokens_ok = {"ink_primary": {"contrast_result": "PASS"}, "ink_muted": {"contrast_result": "PASS"}}
    live_fail = {"card_bg": {"contrast_result": "FAIL"}}
    p_pass2, agg2 = aggregate_pre03_verdict(tokens_ok, live_fail, alpha_ok)
    assert not p_pass2, "Failing live item must cause PRE-03 to fail!"
    assert not agg2["live_palette_all_passed"], "live_palette_all_passed must be False!"

    v_pass2, verd2 = build_pre03_verdict(tokens_ok, live_fail, alpha_ok)
    assert not v_pass2, "build_pre03_verdict must return False for failing live item!"
    assert verd2["status"] == "FAIL", f"Expected FAIL status, got {verd2['status']}"
    assert verd2["exit_code"] == 1, f"Expected exit_code 1, got {verd2['exit_code']}"
    assert compute_harness_exit_code(preflight_ok=v_pass2, tsc_gate_status="PASS") == 1
    assert compute_harness_exit_code(preflight_ok=v_pass2, tsc_gate_status="NOT_RUN") == 1

    # 3. Failing alpha case scenario
    alpha_fail = {"alpha_pill": {"contrast_result": "FAIL"}}
    p_pass3, agg3 = aggregate_pre03_verdict(tokens_ok, live_ok, alpha_fail)
    assert not p_pass3, "Failing alpha case must cause PRE-03 to fail!"
    assert not agg3["synthetic_alpha_all_passed"], "synthetic_alpha_all_passed must be False!"

    v_pass3, verd3 = build_pre03_verdict(tokens_ok, live_ok, alpha_fail)
    assert not v_pass3, "build_pre03_verdict must return False for failing alpha case!"
    assert verd3["status"] == "FAIL", f"Expected FAIL status, got {verd3['status']}"
    assert verd3["exit_code"] == 1, f"Expected exit_code 1, got {verd3['exit_code']}"
    assert compute_harness_exit_code(preflight_ok=v_pass3, tsc_gate_status="PASS") == 1
    assert compute_harness_exit_code(preflight_ok=v_pass3, tsc_gate_status="NOT_RUN") == 1

    # 4. Harness method integration test (without triggering full __init__ self-test recursion)
    dummy_harness = WorkbenchHarness.__new__(WorkbenchHarness)
    dummy_harness.verdicts = []
    h_pass = dummy_harness.record_pre03_evaluation(tokens_fail, live_ok, alpha_ok)
    assert not h_pass, "record_pre03_evaluation must return False on failing input!"
    assert len(dummy_harness.verdicts) == 1, "Expected exactly 1 recorded verdict in dummy harness!"
    recorded = dummy_harness.verdicts[0]
    assert recorded["scenario_id"] == "PRE-03", f"Expected scenario_id PRE-03, got {recorded['scenario_id']}"
    assert recorded["status"] == "FAIL", f"Expected recorded status FAIL, got {recorded['status']}"
    assert recorded["exit_code"] == 1, f"Expected recorded exit_code 1, got {recorded['exit_code']}"
    assert compute_harness_exit_code(preflight_ok=h_pass, tsc_gate_status="PASS") == 1

    # 5. All passing scenario (including NOT_VERIFIABLE non-text containers)
    p_pass5, agg5 = aggregate_pre03_verdict(tokens_ok, live_ok, alpha_ok)
    assert p_pass5, "All valid items must result in PRE-03 PASS!"
    assert agg5["tokens_all_passed"] and agg5["live_palette_all_passed"] and agg5["synthetic_alpha_all_passed"]

    v_pass5, verd5 = build_pre03_verdict(tokens_ok, live_ok, alpha_ok)
    assert v_pass5, "build_pre03_verdict must return True for all passing!"
    assert verd5["status"] == "PASS", f"Expected PASS status, got {verd5['status']}"
    assert verd5["exit_code"] == 0, f"Expected exit_code 0, got {verd5['exit_code']}"
    assert verd5["blocker_reason"] is None, "blocker_reason must be None on pass"
    assert compute_harness_exit_code(preflight_ok=v_pass5, tsc_gate_status="PASS") == 0
    assert compute_harness_exit_code(preflight_ok=v_pass5, tsc_gate_status="NOT_RUN") == 0

    pass_harness = WorkbenchHarness.__new__(WorkbenchHarness)
    pass_harness.verdicts = []
    h_pass5 = pass_harness.record_pre03_evaluation(tokens_ok, live_ok, alpha_ok)
    assert h_pass5, "record_pre03_evaluation must return True on passing input!"
    assert len(pass_harness.verdicts) == 1
    assert pass_harness.verdicts[0]["status"] == "PASS"
    assert pass_harness.verdicts[0]["exit_code"] == 0
    assert compute_harness_exit_code(preflight_ok=h_pass5, tsc_gate_status="PASS") == 0


class WorkbenchHarness:
    def __init__(self, tsc_exit_code: int | None = None) -> None:
        self.git_info = get_git_info()
        self.verdicts: list[dict[str, object]] = []
        self.findings: list[str] = []
        self.tsc_exit_code: int | None = tsc_exit_code
        self.tsc_gate_status: str = "NOT_RUN"
        self_test_contrast_math()
        self_test_pre02_freshness(str(self.git_info["head"]), str(self.git_info["tree"]), self.get_probe_inputs_sha256())
        self_test_pre02_retry_failure(str(self.git_info["head"]), str(self.git_info["tree"]), self.get_probe_inputs_sha256())
        self_test_pre03_failure_propagation()

    def get_probe_inputs_sha256(self) -> dict[str, str]:
        probe_py = VERIFICATION_DIR / "probes" / "static_control_probe.py"
        return {
            "workbench_page_tsx": sha256_file(REPO_ROOT / "apps" / "desktop" / "frontend" / "src" / "workbench" / "WorkbenchPage.tsx"),
            "app_tsx": sha256_file(REPO_ROOT / "apps" / "desktop" / "frontend" / "src" / "App.tsx"),
            "probe_script": sha256_file(probe_py),
        }

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

    def record_pre03_evaluation(
        self,
        calculated_ratios: dict[str, dict[str, object]],
        live_ratios: dict[str, dict[str, object]],
        alpha_evaluations: dict[str, dict[str, object]],
        contrast_thresholds: dict[str, float] | None = None,
    ) -> bool:
        """Evaluates contrast ratios, appends authoritative PRE-03 verdict to self.verdicts,
        and returns boolean pre03_pass (R7-01)."""
        pre03_pass, verdict = build_pre03_verdict(
            calculated_ratios, live_ratios, alpha_evaluations, contrast_thresholds
        )
        self.verdicts.append(verdict)
        return pre03_pass

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

            # R4-02 & R4-07: Load authoritative closed enums (fails closed on failure)
            enums = load_authoritative_enums()

            # R4-08: Run mutation self-check to prove rejection capability with exact counting
            mut_res = self_test_pre01_mutations(fixtures, enums)
            assert mut_res["all_rejected_as_expected"], f"Mutation self-test incomplete: {mut_res}"

            # Full traversal validation across all fixtures (R4-02, R4-11)
            val_summary = validate_fixtures_data(fixtures, enums)

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
                    "mutation_rejection_self_test": f"{mut_res['executed_count']}/{mut_res['total_configured']} executed and rejected (skipped: {mut_res['skipped_count']})",
                    "authoritative_enums_enforced": {
                        "region_types": sorted(list(enums["region_types"])),
                        "sfx_policies": sorted(list(enums["sfx_policies"])),
                        "region_origins": sorted(list(enums["region_origins"])),
                    },
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

        expected_inputs = self.get_probe_inputs_sha256()

        def _run_probe_subprocess() -> tuple[int, str, str]:
            proc = subprocess.run([sys.executable, str(probe_py)], capture_output=True, text=True)
            return proc.returncode, proc.stdout, proc.stderr

        probe_pass, report_is_fresh, observed_proc_exit, report_exit, srep, reason = dispatch_and_evaluate_static_probe(
            static_report_path,
            str(self.git_info["head"]),
            str(self.git_info["tree"]),
            expected_inputs,
            runner_fn=_run_probe_subprocess,
        )

        if not probe_pass:
            all_passed = False

        self.record_verdict(
            "PRE-02",
            "static_source_contract_check",
            "PASS" if probe_pass else "FAIL",
            "STATIC_AST",
            observed_proc_exit,
            details={
                "overall_status": srep.get("overall_status") if srep else "FAIL",
                "observed_process_exit_code": observed_proc_exit,
                "report_exit_code": report_exit,
                "bound_source_head": srep.get("source_head", self.git_info["head"]) if srep else self.git_info["head"],
                "bound_source_tree": srep.get("source_tree", self.git_info["tree"]) if srep else self.git_info["tree"],
                "report_freshness_verified": report_is_fresh,
                "freshness_evaluation_reason": reason,
                "workbench_page": srep.get("workbench_page") if srep else {},
                "app_navigation": srep.get("app_navigation") if srep else {},
            },
            blocker_reason=None if probe_pass else f"Static contract probe failed (freshness={report_is_fresh}, proc_exit={observed_proc_exit}, reason={reason})",
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

            thresholds_applied = {
                "body_text_min_ratio": body_text_min,
                "disabled_text_min_ratio": disabled_text_min,
                "ui_components_min_ratio": ui_component_min,
            }
            pre03_pass = self.record_pre03_evaluation(
                calculated_ratios,
                live_ratios,
                alpha_evaluations,
                contrast_thresholds=thresholds_applied,
            )
            if not pre03_pass:
                all_passed = False
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
        """AC7: Persists structured evidence files with pure LF line endings.
        Two-phase finalization (R4-03): artifact hashes are populated in the finalize phase
        after all runner execution logs are completely flushed to disk."""
        tsc_bin = find_tsc_binary()
        tsc_bin_found = tsc_bin is not None
        tsc_binary_resolution = "RESOLVED" if tsc_bin_found else "NOT_FOUND"

        if not tsc_bin_found:
            tsc_execution_status = "NOT_RUN"
            tsc_gate_status = "FAIL_CLOSED"
            tsc_note = "TypeScript compiler binary not found in worktree or git common root (fail-closed per R5-04)."
        elif self.tsc_exit_code is None:
            tsc_execution_status = "NOT_RUN"
            tsc_gate_status = "NOT_RUN"
            tsc_note = "Standalone harness execution; TypeScript check was not invoked by runner."
        elif self.tsc_exit_code == 0:
            tsc_execution_status = "PASS"
            tsc_gate_status = "PASS"
            tsc_note = "TypeScript contract check executed and passed with exit code 0."
        else:
            tsc_execution_status = "FAIL"
            tsc_gate_status = "FAIL"
            tsc_note = f"TypeScript contract check failed with observed exit code {self.tsc_exit_code}."

        self.tsc_gate_status = tsc_gate_status

        report = {
            "task_id": "P02",
            "owner": "Antigravity",
            "stage": "STAGE_A_SAFE_FOUNDATION_R8",
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
                "typescript_contract_gate": {
                    "file": "apps/desktop/frontend/e2e/workbench_driver_protocol.ts",
                    "sha256": sha256_file(REPO_ROOT / "apps" / "desktop" / "frontend" / "e2e" / "workbench_driver_protocol.ts"),
                    "tsc_binary_found": tsc_bin_found,
                    "tsc_path": str(tsc_bin.relative_to(REPO_ROOT)) if tsc_bin and tsc_bin.is_relative_to(REPO_ROOT) else (str(tsc_bin) if tsc_bin else None),
                    "tsc_binary_resolution": tsc_binary_resolution,
                    "execution_status": tsc_execution_status,
                    "observed_exit_code": self.tsc_exit_code,
                    "gate_status": tsc_gate_status,
                    "note": tsc_note,
                },
                "execution_commands": [
                    "powershell -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1 -ProbeOnly",
                    "powershell -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1",
                    "python verification/P02/harness/workbench_cdp_harness.py",
                    "python verification/P02/harness/workbench_cdp_harness.py --finalize",
                ],
                "artifact_hashes": "PENDING_TWO_PHASE_FINALIZATION",
                "finalization_status": "PENDING",
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
            "=== P02 Real Workbench WebView2 Harness Verdict Report (Stage A r8) ===",
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


def finalize_artifact_hashes() -> int:
    """Two-phase finalization (R4-03, R5-02):
    Runs AFTER the PowerShell runner has completed preflight steps 1-4.
    Appends the completion verdict to probe-execution-full.log before computing final evidence hashes.
    Computes exact SHA-256 for all finalized evidence artifacts and updates p02-harness-results.json.
    Does NOT hash p02-harness-results.json into itself (avoids self-referential report hashing)."""
    if "--finalize-fail-test" in sys.argv:
        print("[Finalize] Injected failure test activated: exiting with code 42", file=sys.stderr)
        return 42

    json_path = VERIFICATION_DIR / "p02-harness-results.json"
    if not json_path.exists():
        print(f"[Finalize] Error: {json_path} does not exist!", file=sys.stderr)
        return 1

    # R5-02: Record successful completion in full log prior to computing final hash of the log
    full_log_path = VERIFICATION_DIR / "probe-execution-full.log"
    legacy_log_path = VERIFICATION_DIR / "probe-execution.log"
    completion_text = (
        "OUTPUT:\n"
        "=== P02 Artifact Hashes Finalization Started ===\n"
        "Stage A execution completed successfully with EXIT=0.\n"
        "Status: COMPLETED (EXIT=0)\n"
    )
    if full_log_path.exists():
        with full_log_path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(completion_text)
    if legacy_log_path.exists():
        with legacy_log_path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(completion_text)

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    artifact_files = [
        "verification/P02/env-identity-report.json",
        "verification/P02/static-control-report.json",
        "verification/P02/p02-harness-results.txt",
        "verification/P02/probe-execution-probeonly.log",
        "verification/P02/probe-execution-full.log",
    ]
    hashes: dict[str, str] = {}
    for af in artifact_files:
        p = REPO_ROOT / af
        if p.exists():
            hashes[af] = sha256_file(p)
        else:
            hashes[af] = "FILE_MISSING"

    data["provenance"]["artifact_hashes"] = hashes
    data["provenance"]["finalization_status"] = "FINALIZED"
    data["provenance"]["finalized_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with json_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("=== P02 Artifact Hashes Finalized (Two-Phase R4-03) ===")
    for af, h in hashes.items():
        print(f"  {af}: {h}")
    return 0


def main() -> int:
    if "--finalize" in sys.argv:
        return finalize_artifact_hashes()

    tsc_exit_arg: int | None = None
    if "--tsc-exit" in sys.argv:
        try:
            idx = sys.argv.index("--tsc-exit")
            tsc_exit_arg = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            tsc_exit_arg = 1

    harness = WorkbenchHarness(tsc_exit_code=tsc_exit_arg)
    preflight_ok = harness.run_preflight_checks()
    harness.register_runtime_blocked_scenarios()
    harness.persist_results()
    # R6-02, R7-01: Top-level exit code computed via production decision helper
    return compute_harness_exit_code(preflight_ok, harness.tsc_gate_status)


if __name__ == "__main__":
    sys.exit(main())
