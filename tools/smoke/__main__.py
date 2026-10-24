"""``python -m tools.smoke`` is an alias for the plugin/software check CLI."""

from __future__ import annotations

from tools.smoke.plugins import main

if __name__ == "__main__":
    raise SystemExit(main())
