#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M2-PACKAGED-AC1-DLL-DIAG: read-only PE import-table probe (stdlib only).

The inspected binaries are only READ AS BYTES. This script never loads,
executes, patches or writes them; its only write is the JSON report it is
asked to emit (--out). No third-party dependency, no network, no secrets.

It answers the AC3 question "which closure entry cannot be resolved": for
every imported and delay-imported DLL *name* of a candidate binary, report
whether a resolution candidate exists in the packaged `_internal` layout (or
in System32). An unresolved name is a PROVEN-missing closure entry; a
resolved name is only PROVEN-present -- loadability still needs the real
process run (`run_dll_diag_probe.ps1` step 5). Never over-claim from this.

Usage:
  python pe_import_probe.py --bundle <.../target/core-sidecar/core-sidecar> \
      --out <report.json> [--binary <path>]...

Default binaries: the five bundle exes plus
  _internal/PySide6/QtGui.pyd, QtCore.pyd, Qt6Gui.dll, Qt6Core.dll,
  pyside6.abi3.dll, _internal/shiboken6/shiboken6.abi3.dll
"""

import argparse
import json
import os
import struct
import sys

SYSTEM32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")

# Names the OS is expected to satisfy; unresolved ones are not a bundle defect.
OS_SUPPLIED_PREFIXES = ("api-ms-win-", "ext-ms-win-")
OS_SUPPLIED_EXACT = {
    "kernel32.dll", "user32.dll", "gdi32.dll", "advapi32.dll", "shell32.dll",
    "ole32.dll", "oleaut32.dll", "shlwapi.dll", "ws2_32.dll", "crypt32.dll",
    "d3d11.dll", "dxgi.dll", "dwmapi.dll", "uxtheme.dll", "comdlg32.dll",
    "imm32.dll", "winmm.dll", "version.dll", "netapi32.dll", "userenv.dll",
    "d3dcompiler_47.dll", "opengl32.dll", "setupapi.dll", "mpr.dll",
    "winspool.drv", "wtsapi32.dll", "psapi.dll", "bcrypt.dll", "ncrypt.dll",
    "secur32.dll", "iphlpapi.dll", "dnsapi.dll", "msvcrt.dll", "ntdll.dll",
}

DEFAULT_BINARIES = [
    "host_bridge.exe",
    "core_service.exe",
    "acceptance_bridge.exe",
    "catalog_loader.exe",
    "sfx_detect_probe.exe",
    os.path.join("_internal", "PySide6", "QtGui.pyd"),
    os.path.join("_internal", "PySide6", "QtCore.pyd"),
    os.path.join("_internal", "PySide6", "Qt6Gui.dll"),
    os.path.join("_internal", "PySide6", "Qt6Core.dll"),
    os.path.join("_internal", "PySide6", "pyside6.abi3.dll"),
    os.path.join("_internal", "shiboken6", "shiboken6.abi3.dll"),
]


def _u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]


def _u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


class PE(object):
    """Minimal PE32/PE32+ reader: section map + import / delay-import names."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as fh:
            self.buf = fh.read()
        b = self.buf
        if b[:2] != b"MZ":
            raise ValueError("not a PE image (no MZ): %s" % path)
        pe_off = _u32(b, 0x3C)
        if b[pe_off:pe_off + 4] != b"PE\0\0":
            raise ValueError("not a PE image (no PE signature): %s" % path)
        coff = pe_off + 4
        self.machine = _u16(b, coff)
        n_sections = _u16(b, coff + 2)
        opt_size = _u16(b, coff + 16)
        opt = coff + 20
        magic = _u16(b, opt)
        if magic == 0x20B:
            self.is64 = True
            dd_off = opt + 112
            n_dd = _u32(b, opt + 108)
        elif magic == 0x10B:
            self.is64 = False
            dd_off = opt + 96
            n_dd = _u32(b, opt + 92)
        else:
            raise ValueError("unknown optional-header magic 0x%x" % magic)
        self.dirs = []
        for i in range(min(n_dd, 16)):
            self.dirs.append((_u32(b, dd_off + i * 8), _u32(b, dd_off + i * 8 + 4)))
        sec = opt + opt_size
        self.sections = []
        for i in range(n_sections):
            o = sec + i * 40
            name = b[o:o + 8].rstrip(b"\0").decode("ascii", "replace")
            vsize = _u32(b, o + 8)
            va = _u32(b, o + 12)
            raw_size = _u32(b, o + 16)
            raw_ptr = _u32(b, o + 20)
            self.sections.append((name, va, vsize, raw_ptr, raw_size))

    def off(self, rva):
        for _name, va, vsize, raw_ptr, raw_size in self.sections:
            if va <= rva < va + max(vsize, raw_size):
                delta = rva - va
                if delta < raw_size:
                    return raw_ptr + delta
        return None

    def cstr(self, rva):
        o = self.off(rva)
        if o is None:
            return None
        end = self.buf.find(b"\0", o)
        if end < 0:
            return None
        return self.buf[o:end].decode("ascii", "replace")

    def _dir_names(self, index, stride, name_field_off):
        out = []
        if index >= len(self.dirs):
            return out
        rva, size = self.dirs[index]
        if not rva or not size:
            return out
        base = self.off(rva)
        if base is None:
            return out
        o = base
        while True:
            chunk = self.buf[o:o + stride]
            if len(chunk) < stride or all(x == 0 for x in chunk):
                break
            name_rva = _u32(self.buf, o + name_field_off)
            if name_rva:
                name = self.cstr(name_rva)
                if name:
                    out.append(name)
            o += stride
        return out

    def imports(self):
        return self._dir_names(1, 20, 12)          # IMAGE_IMPORT_DESCRIPTOR.Name

    def delay_imports(self):
        # IMAGE_DELAYLOAD_DESCRIPTOR: Attributes(u32), DllNameRVA(u32), ...
        out = []
        if len(self.dirs) <= 13:
            return out
        rva, size = self.dirs[13]
        if not rva or not size:
            return out
        base = self.off(rva)
        if base is None:
            return out
        o = base
        while True:
            chunk = self.buf[o:o + 32]
            if len(chunk) < 32 or all(x == 0 for x in chunk):
                break
            attrs = _u32(self.buf, o)
            name_rva = _u32(self.buf, o + 4)
            if (attrs & 1) == 0 and name_rva:      # bit0==0 -> RVA-based names
                name = self.cstr(name_rva)
                if name:
                    out.append(name)
            o += 32
        return out


def search_dirs(binary, bundle):
    dirs = []
    for d in (
        os.path.dirname(os.path.abspath(binary)),
        os.path.join(bundle, "_internal"),
        os.path.join(bundle, "_internal", "PySide6"),
        os.path.join(bundle, "_internal", "shiboken6"),
        bundle,
        SYSTEM32,
    ):
        if d and os.path.isdir(d) and d not in dirs:
            dirs.append(d)
    return dirs


def resolve(name, dirs):
    for d in dirs:
        candidate = os.path.join(d, name)
        if os.path.isfile(candidate):
            return candidate
    return None


def is_os_supplied(name):
    low = name.lower()
    return low in OS_SUPPLIED_EXACT or low.startswith(OS_SUPPLIED_PREFIXES)


def scan(binary, bundle):
    pe = PE(binary)
    dirs = search_dirs(binary, bundle)
    entry = {
        "binary": os.path.relpath(binary, bundle) if binary.startswith(bundle) else binary,
        "machine": hex(pe.machine),
        "is_64bit": pe.is64,
        "imports": {"total": 0, "resolved": [], "unresolved": [], "unresolved_os_supplied": []},
        "delay_imports": {"total": 0, "resolved": [], "unresolved": [], "unresolved_os_supplied": []},
    }
    for key, names in (("imports", pe.imports()), ("delay_imports", pe.delay_imports())):
        seen = []
        for n in names:
            if n.lower() not in [x.lower() for x in seen]:
                seen.append(n)
        entry[key]["total"] = len(seen)
        for name in seen:
            where = resolve(name, dirs)
            if where:
                entry[key]["resolved"].append({"name": name, "at": where})
            elif is_os_supplied(name):
                entry[key]["unresolved_os_supplied"].append(name)
            else:
                entry[key]["unresolved"].append(name)
    return entry


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True,
                    help="core-sidecar onedir bundle (the dir holding the exes and _internal)")
    ap.add_argument("--out", required=True, help="JSON report path (written by this probe)")
    ap.add_argument("--binary", action="append", default=None,
                    help="binary to scan (repeatable, abs or bundle-relative); default = curated set")
    args = ap.parse_args(argv)

    bundle = os.path.abspath(args.bundle)
    targets = args.binary if args.binary else DEFAULT_BINARIES
    report = {"bundle": bundle, "scanned": [], "skipped": [], "missing_union": []}
    union = []
    for target in targets:
        path = target if os.path.isabs(target) else os.path.join(bundle, target)
        if not os.path.isfile(path):
            report["skipped"].append({"path": os.path.relpath(path, bundle), "reason": "not found"})
            continue
        try:
            entry = scan(path, bundle)
        except Exception as exc:  # keep the probe going, record the failure
            report["skipped"].append({"path": os.path.relpath(path, bundle), "reason": repr(exc)})
            continue
        report["scanned"].append(entry)
        for n in entry["imports"]["unresolved"] + entry["delay_imports"]["unresolved"]:
            if n not in union:
                union.append(n)
    report["missing_union"] = sorted(union)
    report["verdict"] = (
        "UNRESOLVED_IMPORTS_FOUND" if report["missing_union"] else "ALL_SCANNED_IMPORTS_RESOLVABLE"
    )
    report["caveat"] = (
        "Resolution here is a static file-existence check over the _internal layout and "
        "System32; it is NOT a load test. Only step 5 of run_dll_diag_probe.ps1 loads the "
        "real process. An OS-supplied name being absent from the bundle is not proof "
        "of failure."
    )
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print("bundle: %s" % bundle)
    for entry in report["scanned"]:
        print("%-42s imports=%-4d unresolved=%-3d delay_unresolved=%d" % (
            entry["binary"], entry["imports"]["total"],
            len(entry["imports"]["unresolved"]), len(entry["delay_imports"]["unresolved"])))
    for item in report["skipped"]:
        print("skipped: %s (%s)" % (item["path"], item["reason"]))
    print("verdict: %s" % report["verdict"])
    if report["missing_union"]:
        print("missing_union: %s" % ", ".join(report["missing_union"]))
    print("report: %s" % args.out)
    return 0 if not report["missing_union"] else 2


if __name__ == "__main__":
    sys.exit(main())
