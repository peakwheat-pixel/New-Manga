"""TASK-062 review probe (Qoder, non-author): put the new redaction screen
under adversarial and realistic inputs through the *production* entry point.

    python t062_redaction_probe.py [tree_root]

Nothing here is a repo test; it measures three things the shipped tests do not:
S1  does any credential shape still reach the serialized report (sections, keys
    and the recent-error composite)?
S2  how much does whole-value replacement cost diagnosability on a realistic
    provider-auth error?
S3  collateral: which ordinary strings the widened `search` now masks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from application.maintenance.diagnostics import (  # noqa: E402
    RecentError,
    build_diagnostics_report,
    redact_value,
)

print(f"== tree: {ROOT}")


def report_json(**overrides) -> dict:
    base = dict(
        generated_at="2026-09-19T00:00:00+00:00",
        app_version="0.1.0",
        platform_python="CPython 3.12.3",
        schema_version=7,
        database_path="D:/MangaData/library.db",
        settings_summary={"theme": "dark", "api_key": "sk-SUPERSECRET0123456"},
        recent_errors=(),
        environment_paths={"data_root": "D:/MangaData"},
    )
    base.update(overrides)
    report = build_diagnostics_report(**base)
    return json.loads(report.to_json_bytes().decode("utf-8"))


print("\n-- S1 can a credential shape still reach the serialized report?")
payload = report_json()
blob = json.dumps(payload, ensure_ascii=False)
print("   sensitive *key name* -> value masked:",
      payload["settings_summary"]["api_key"] == "[redacted]")
# a credential embedded in a key NAME (settings/environment keys are emitted as-is)
leaky = report_json(settings_summary={"sk-abcdefgh123456": "benign value"})
leaky_blob = json.dumps(leaky, ensure_ascii=False)
print("   settings key containing an sk- run is emitted verbatim?",
      "sk-abcdefgh123456" in leaky_blob,
      f"-> {list(leaky['settings_summary'])}")
paths_keyed = report_json(environment_paths={"D:/x/sk-abcdefgh123456": "value"})
print("   environment_paths key with the same shape:",
      "sk-abcdefgh123456" in json.dumps(paths_keyed))
# non-string values reach the screen only after str() for schema_version;
# what if a caller passes a non-str where str is declared?
try:
    weird = report_json(settings_summary={"note": 12345})  # type: ignore[dict-item]
    print("   non-str settings value:", json.dumps(weird["settings_summary"]))
except Exception as error:  # noqa: BLE001
    print(f"   non-str settings value raises {type(error).__name__}: {str(error)[:90]}")

print("\n-- S2 diagnosability cost on a realistic provider-auth failure")
realistic = RecentError(
    "2026-09-19T08:12:03+00:00",
    "provider.translation.openai",
    "PROVIDER_AUTH_FAILED",
    "HTTP 401 from https://api.example.com/v1/chat: invalid api key in header"
    " 'Authorization: Bearer sk-abcdefgh12345678' - check Settings > Providers",
)
out = report_json(recent_errors=(realistic,))
value = list(out["recent_errors"].values())[0]
key = list(out["recent_errors"].keys())[0]
print(f"   error text as reported : {value!r}")
print(f"   composite key          : {key!r}")
print("   -> the whole message (status code, endpoint, which header, the hint)"
      " is gone, not just the token")
half = realistic._replace(message="HTTP 401 from https://api.example.com/v1/chat"
                                   " - check Settings > Providers") if hasattr(
    realistic, "_replace") else None
if half is not None:
    kept = list(report_json(recent_errors=(half,)).recent_errors.values()
                ) if False else list(report_json(recent_errors=(half,))["recent_errors"].values())
    print(f"   same error without the token: {kept[0]!r}")
print("   span-only masking would keep the first and hide only the token:")
import re  # noqa: E402
from application.maintenance import diagnostics as diag  # noqa: E402

masked = diag._BEARER.sub("Bearer [redacted]", diag._OPENAI_STYLE.sub("sk-[redacted]",
                                                                      realistic.message))
print(f"     {masked!r}")

print("\n-- S3 collateral of the widened search (left guard blocks alnum only)")
cases = [
    ("ordinary data root", "D:/MangaData"),
    ("windows backslash path", "D:\\MangaData\\managed"),
    ("hyphenated word", "D:/workspace/task-live-run/comic-sketch.png"),
    ("version with build meta", "1.0.0+build.7"),
    ("python banner", "CPython 3.12.3"),
    ("user dir literally sk-*", "C:/Users/sk-1a2b3c4d/Manga/library.db"),
    ("project folder sk-tools-market", "D:/workspace/sk-tools-market/x.png"),
    ("identifier with underscore", "provider_sk-abcdefgh1234 in trace"),
    ("dotted module-ish name", "pkg.sk-abcdefgh1234"),
    ("Bearer as a plain word + number", "Bearer 12345678 people in queue"),
    ("short sk- (7 token chars)", "sk-abc1234"),
    ("sk- followed by punctuation", "sk-!!!!!!!"),
    ("lowercase bearer without space", "bearertoken123"),
    ("truncated bearer", "Bearer ab"),
]
for label, value in cases:
    verdict = "REDACTED" if redact_value("data_root", value) == "[redacted]" else "kept"
    print(f"   {verdict:<9} {label:<28} {value!r}")

print("\n   left-guard check: does a preceding underscore/dot still allow a match?")
for value in ("foo_sk-abcdefgh1234", ".sk-abcdefgh1234", "asdk-abcdefgh1234"):
    print(f"     {value!r} -> {redact_value('note', value)!r}")
