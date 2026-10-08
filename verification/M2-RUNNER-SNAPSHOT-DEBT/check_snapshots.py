"""Exercise actual runner predicates without launching apps; stdlib only."""
import ast
import json
import re
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]


def definitions(path, names, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in names for t in node.targets
        ):
            selected.append(node)
    exec(compile(ast.Module(selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def main():
    rc = definitions(ROOT / "verification/M2-RC2/run_e2e.py",
                     {"ALLOWLIST_RE", "PRODUCTION_EXPECTED", "PROBE_EXPECTED", "check_announcement"},
                     {"re": re, "Path": Path})
    rust = (ROOT / "apps/desktop/src-tauri/src/main.rs").read_text(encoding="utf-8")
    body = rust.split("pub const PRODUCTION_COMMANDS:", 1)[1].split("= &[", 1)[1].split("];", 1)[0]
    implemented = re.findall(r'"([a-z_]+)"', re.sub(r"//[^\n]*", "", body))
    # Independent pinned oracle: released Task scope + M2-C1 rev1.8 section 5.
    # Do not derive expected values from either runner or the runtime response.
    frozen = [
        "issue_resource_url", "revoke_ref", "revoke_resource_refs", "core_ping",
        "library_list_books", "settings_get", "settings_update_section",
        "set_region_type", "list_regions", "list_region_revisions",
        "restore_region_revision", "rerender_page", "resolve_page_resource",
        "list_chapters", "list_chapter_pages",
    ]
    assert implemented == frozen and rc["PRODUCTION_EXPECTED"] == frozen
    core = ast.parse((ROOT / "src/bootstrap/core_service.py").read_text(encoding="utf-8"))
    protocol = {}
    for node in core.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"PROTOCOL_MAJOR", "PROTOCOL_MINOR"}:
                    protocol[target.id] = ast.literal_eval(node.value)
    version = {"major": protocol["PROTOCOL_MAJOR"], "minor": protocol["PROTOCOL_MINOR"]}
    assert version == {"major": 1, "minor": 6}
    count = 0
    with tempfile.TemporaryDirectory(prefix="runner-snapshot-check-") as temp:
        output = Path(temp)
        announcement = output / "announcement.log"
        cases = [frozen, frozen[:9], frozen + ["unexpected"], frozen[::-1],
                 frozen + ["probe_exit"], []]
        for commands in cases:
            announcement.write_text("[m2rc2-allowlist] production:" + ",".join(commands), encoding="utf-8")
            assert rc["check_announcement"](announcement, "production")[0] == (commands == frozen)
            count += 1
        announcement.write_text("[m2rc2-allowlist] probe:" + ",".join(rc["PROBE_EXPECTED"]), encoding="utf-8")
        assert len(rc["PROBE_EXPECTED"]) == 7
        assert rc["check_announcement"](announcement, "probe")[0]
        assert not rc["check_announcement"](announcement, "production")[0]
        count += 2
        ping_cases = [
            (version, ["library.list_books"], "ready", None),
            ({"major": 1, "minor": 3}, ["library.list_books"], "ready", None),
            ({"major": 1, "minor": 7}, ["library.list_books"], "ready", None),
            (None, ["library.list_books"], "ready", None),
            (version, [], "ready", None),
            (version, ["unrelated"], "ready", None),
            (version, ["library.list_books"], "starting", None),
            (version, ["library.list_books"], "ready", {"code": "FAIL"}),
        ]
        for response_version, capabilities, status, error in ping_cases:
            class Process:
                returncode = 0

                def communicate(self, input, timeout):
                    requests = [json.loads(line) for line in input.decode().splitlines()]
                    assert all(r["version"] == {"major": 1, "minor": 3} for r in requests)
                    replies = [
                        {"request_id": "r1", "error": error, "result": {"status": status, "protocol_version": response_version,
                                                         "capabilities": capabilities}},
                        {"request_id": "r2", "result": []},
                        {"request_id": "r3", "result": {"status": "stopped"}},
                    ]
                    return "\n".join(json.dumps(r) for r in replies).encode(), b""

            packaged = definitions(ROOT / "packaging/m2ac5/run_clean_start_e2e.py",
                                   {"Gate", "run_library_probe"},
                                   {"json": json, "Path": Path, "RAW": output, "log": lambda _: None,
                                    "subprocess": SimpleNamespace(Popen=lambda *a, **kw: Process(), PIPE=-1)})
            gate = packaged["Gate"]()
            packaged["run_library_probe"](gate, output, {}, output)
            ping = next(s for s in gate.scenarios if s["id"] == "CS-L1-packaged-core-ping")
            assert (ping["status"] == "PASS") == (response_version == version and "library.list_books" in capabilities and status == "ready" and error is None)
            count += 1
    for path in ["verification/M2-RC2/run_e2e.py", "packaging/m2ac5/run_clean_start_e2e.py"]:
        compile((ROOT / path).read_text(encoding="utf-8"), path, "exec")
    print(f"PASS: {count} actual-predicate cases; source alignment and syntax; no product/runtime claim")


if __name__ == "__main__":
    main()
