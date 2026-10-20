# -*- coding: utf-8 -*-
"""SEC-FMT-004: full ManagedFileStorage lifecycle on a >300 char root.

Uses a literal relative path - the adapter's own path CONSTRUCTION is a
separate concern from whether its IO works at length, and the construction
already strips to known safe components.
"""
import os
import sys
import tempfile

sys.path.insert(0, r"G:\CODEX\New Manga")
sys.path.insert(0, r"G:\CODEX\New Manga\src")

import infrastructure.filesystem.managed_storage as ms


def build_deep(root, target_len):
    deep = root
    i = 0
    while len(deep) < target_len and i < 40:
        deep = os.path.join(deep, "segment" + str(i).zfill(3) + "x" * 12)
        i += 1
    return deep


def main():
    cls = next(getattr(ms, n) for n in dir(ms)
               if "Storage" in n and isinstance(getattr(ms, n), type))
    print("  class:", cls.__name__)

    base = tempfile.mkdtemp(prefix="sfx004c-")
    deep = build_deep(base, 300)
    os.makedirs(deep, exist_ok=True)
    print("  root length:", len(deep))

    storage = cls(deep)
    storage.ensure_layout()

    rel = "books/" + "b" * 60 + "/chapters/" + "c" * 40 + "/images/r1.png"
    full = storage.absolute_path(rel)
    print("  rel length :", len(rel))
    print("  full length:", len(full))

    results = []

    def step(label, fn):
        try:
            out = fn()
            print("   %-26s ok   %s" % (label, str(out)[:60]))
            results.append((label, True))
            return out
        except Exception as exc:
            print("   %-26s FAIL %s: %s" % (label, type(exc).__name__, str(exc)[:85]))
            results.append((label, False))
            return None

    handle = step("write_temp", lambda: storage.write_temp(b"y" * 8192))
    if handle:
        step("verify_temp", lambda: storage.verify_temp(handle))
        step("publish", lambda: storage.publish(handle, rel))
        step("exists", lambda: os.path.exists(full))
        step("read back", lambda: len(open(full, "rb").read()))
        step("remove_managed", lambda: storage.remove_managed(rel))
        step("gone", lambda: not os.path.exists(full))

    passed = sum(1 for _l, ok in results if ok)
    print("\n  === %d/%d passed ===" % (passed, len(results)))
    for label, ok in results:
        print("    %-26s %s" % (label, "PASS" if ok else "FAIL"))


if __name__ == "__main__":
    main()
