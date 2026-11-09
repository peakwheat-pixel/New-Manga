"""FEA-11-HOST-AUTH-3: redact bare signature material from archived wirelogs.

The C-16 §7 redactor masks name-based sensitive keys plus Bearer/sk- shapes; a bare
``"signature":"<hex>"`` field inside a host-control request is outside that screen.
Archived evidence must not carry live signing material, so this tool rewrites those
values deterministically before the archive is committed. It is idempotent.

Wirelogs store the request as an ESCAPED JSON string, so the field looks like
``\"signature\":\"<value>\"`` in the file text; both escaped and plain forms are handled.
"""

from __future__ import annotations

import argparse
import pathlib
import re

_ESCAPED = re.compile(r'\\"signature\\":\\"[^"\\]*\\"')
_PLAIN = re.compile(r'"signature"\s*:\s*"[^"]*"')


def redact_text(text: str) -> tuple[str, int]:
    text, escaped = _ESCAPED.subn(r'\\"signature\\":\\"[redacted]\\"', text)
    text, plain = _PLAIN.subn('"signature":"[redacted]"', text)
    return text, escaped + plain


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    changed = 0
    for raw in args.paths:
        path = pathlib.Path(raw)
        files = sorted(path.rglob("wire-redacted.ndjson")) if path.is_dir() else [path]
        for file in files:
            text = file.read_text(encoding="utf-8")
            updated, count = redact_text(text)
            if count:
                file.write_text(updated, encoding="utf-8")
                changed += count
                print(f"redacted {count} signature value(s) in {file}")
    print(f"total_redacted={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
