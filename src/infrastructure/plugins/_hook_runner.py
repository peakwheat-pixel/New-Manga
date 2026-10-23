"""Isolated single-hook entry point for the plugin runtime (D1).

The Core spawns this module as a *separate* ``python -I`` subprocess for every
hook invocation:

    python -I _hook_runner.py <entry.py> <hook_name>

The hook payload is read from stdin as JSON; a single JSON object
``{"ok": true, "result": ...}`` or ``{"ok": false, "error": ...}`` is written
to stdout. The runner never prints anything else, never imports Core modules,
and exits non-zero only for usage/loader failures (the parent maps every
non-zero exit to a typed ``plugin_error`` audit + skipped hook).
"""

from __future__ import annotations

import importlib.util
import json
import sys


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        _emit({"ok": False, "error": "runner_usage"})
        return 2
    entry_path, hook_name = argv[1], argv[2]
    try:
        raw_payload = sys.stdin.read()
        payload = json.loads(raw_payload) if raw_payload.strip() else {}
    except json.JSONDecodeError:
        _emit({"ok": False, "error": "hook_payload_not_json"})
        return 2
    try:
        spec = importlib.util.spec_from_file_location("nm_plugin_entry", entry_path)
        if spec is None or spec.loader is None:
            _emit({"ok": False, "error": "entry_not_importable"})
            return 3
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as error:  # noqa: BLE001 - isolation boundary
        _emit({"ok": False, "error": "entry_import_failed", "detail": error.__class__.__name__})
        return 3
    hook = getattr(module, hook_name, None)
    if not callable(hook):
        _emit({"ok": False, "error": "hook_not_callable"})
        return 3
    try:
        result = hook(payload)
    except Exception as error:  # noqa: BLE001 - isolation boundary
        _emit({"ok": False, "error": "hook_raised", "detail": error.__class__.__name__})
        return 4
    try:
        _emit({"ok": True, "result": result})
    except (TypeError, ValueError):
        _emit({"ok": False, "error": "hook_result_not_json"})
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
