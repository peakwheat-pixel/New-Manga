"""Independent assertions over the recorded loader and bridge counterfactual."""
import json
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
controls = json.loads((base / "raw/icu-control-result.json").read_text(encoding="utf-8"))
assert [r["case"] for r in controls] == ["original", "owned_icu_renamed"]
assert controls[0]["exit"] == 1 and controls[0]["qtgui_import_error"]
assert controls[1]["exit"] == 0 and not controls[1]["qtgui_import_error"]
report = json.loads((base / "raw/symbol-probe-full-exports.json").read_text(encoding="utf-8"))
core, gui = report["binaries"]
icu = next(d for d in core["dependencies"] if d["dll"].lower() == "icuuc.dll")
assert icu["imported"] == 20 and len(icu["missing_symbols"]) == 20
assert "ucnv_open" in icu["missing_symbols"]
assert all(not d.get("missing_symbols") for d in gui["dependencies"])
rows = [json.loads(line) for line in (base / "raw/loader-system-icu-control.log").read_text(encoding="utf-8").splitlines() if line.startswith("{")]
assert len(rows) == 2 and all(r["loaded"] for r in rows)
assert all(rows[0]["native_export_lookup"].values())
assert not subprocess.check_output(["git", "diff", "--name-only", "9063c317", "HEAD", "--", "src", "apps", "tests", "packaging"])
print("PASS: bridge causal pair; 20 ICU symbol gaps; full Qt exports; native control; product diff zero")
