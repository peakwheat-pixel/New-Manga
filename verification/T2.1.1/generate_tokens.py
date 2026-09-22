"""Regenerate src/ui/qml/theme/Tokens.qml from doc/design/tokens-cand-f.json.

The JSON is the source of truth (contract §7); this script exists so a contract
revision can be re-applied mechanically instead of by hand-editing 63 values.
tests/ui_shell/test_design_tokens.py compares the generated file back against
the JSON, so a stale or mistyped value fails the suite rather than shipping.

QML cannot assign a CSS ``rgba(...)`` string to a ``color`` property (Qt
rejects it with "Invalid property assignment: color expected"), so the map
keeps the contract's literal strings and ``Tokens.colorFor`` converts them at
read time. The literals therefore stay byte-identical to the design file.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "doc" / "design" / "tokens-cand-f.json"
TARGET = ROOT / "src" / "ui" / "qml" / "theme" / "Tokens.qml"

# Not colors: CSS shadow specifications, exposed verbatim as text.
STRING_TOKENS = {"shadow", "shadow-sm"}


def camel(kebab: str) -> str:
    head, *rest = kebab.split("-")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


def qml_string(value: str) -> str:
    if '"' in value:
        raise ValueError(f"unexpected quote in token value: {value!r}")
    return f'"{value}"'


def render_map(name: str, pairs: dict[str, str]) -> str:
    lines = [f"    readonly property var _{name}: ({{"]
    for key, value in pairs.items():
        lines.append(f'        "{key}": {qml_string(value)},')
    lines.append("    })")
    return "\n".join(lines)


def render_geometry(pairs: dict[str, str]) -> str:
    lines = ["    readonly property var _geometry: ({"]
    for key, value in pairs.items():
        if not value.endswith("px"):
            raise ValueError(f"geometry token is not a px value: {key}={value}")
        lines.append(f'        "{key}": {int(value[:-2])},')
    lines.append("    })")
    return "\n".join(lines)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    modes = data["modes"]
    dark = modes["dark"]["color"]
    light = modes["light"]["color"]
    if set(dark) != set(light):
        raise SystemExit("dark/light token namespaces differ")
    if len(dark) != 42 or len(data["geometry"]) != 21:
        raise SystemExit(f"unexpected token counts: {len(dark)} colors / "
                         f"{len(data['geometry'])} geometry")

    out = [
        "pragma Singleton",
        "import QtQuick",
        "",
        "// T2.1.1 · F \"Graphite Atelier\" design tokens (ND-1 / DDR-9, DDR-10).",
        "// GENERATED from doc/design/tokens-cand-f.json by "
        "verification/T2.1.1/",
        "//    generate_tokens.py -- do not hand-edit values; contract §7 makes",
        "//    the JSON the source of truth. "
        "tests/ui_shell/test_design_tokens.py",
        "// fails on any drift between a token here and the contract.",
        "//",
        "// F is dark by default with light fully provided (contract §3, §11).",
        "// Modes are a design-surface concern: nothing in the product switches",
        "// them yet, and wiring a user setting is out of this slice.",
        "QtObject {",
        '    id: tokens',
        "",
        '    property string mode: "dark"',
        "",
        render_map("dark", dark),
        "",
        render_map("light", light),
        "",
        render_geometry(data["geometry"]),
        "",
        "    readonly property var _palette: "
        "mode === \"light\" ? _light : _dark",
        "",
        "    function value(name) {",
        "        var raw = _palette[name];",
        "        return raw === undefined ? \"\" : raw;",
        "    }",
        "",
        "    function geometry(name) {",
        "        var raw = _geometry[name];",
        "        return raw === undefined ? 0 : raw;",
        "    }",
        "",
        "    // The contract writes translucent tokens in CSS rgba(). QML rejects",
        "    // that form for a color property, so the conversion happens here and",
        "    // nowhere else: pages keep binding `Tokens.<name>` as a color.",
        "    // An unrecognized value yields a fully transparent color, which the",
        "    // parity test reads as a failure instead of rendering as a guess.",
        "    function colorFor(name) {",
        "        var raw = String(value(name));",
        "        if (raw.charAt(0) === \"#\") {",
        "            return raw;",
        "        }",
        "        var open = raw.indexOf(\"(\");",
        "        if (raw.indexOf(\"rgba\") === 0 && open > 0) {",
        "            var parts = raw.substring(open + 1, raw.length - 1).split(\",\");",
        "            if (parts.length === 4) {",
        "                return Qt.rgba(Number(parts[0]) / 255, Number(parts[1]) / 255,",
        "                               Number(parts[2]) / 255, Number(parts[3]));",
        "            }",
        "        }",
        "        return Qt.rgba(0, 0, 0, 0);",
        "    }",
        "",
        "    // ---- named surface used by the pages --------------------------",
    ]

    for key in dark:
        name = camel(key)
        qml_type = "string" if key in STRING_TOKENS else "color"
        accessor = "value" if key in STRING_TOKENS else "colorFor"
        out.append(
            f"    readonly property {qml_type} {name}: {accessor}(\"{key}\")"
        )

    out.append("")
    out.append("    // ---- geometry (mode independent) ------------------------")
    for key in data["geometry"]:
        out.append(
            f"    readonly property int {camel(key)}: geometry(\"{key}\")"
        )
    out.append("}")
    out.append("")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("\n".join(out), encoding="utf-8", newline="\r\n")
    print(f"wrote {TARGET} ({len(dark)} colors, {len(data['geometry'])} geometry)")


if __name__ == "__main__":
    main()
