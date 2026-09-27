"""Host memory/CPU facts for the M2-S1 environment manifest.

Read-only. Uses only ctypes + os so it works under a file sandbox without
WMI/CIM access (which is denied in this workspace).

Run: python verification/M2-S1/probes/00_meminfo.py
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import os
import platform
import sys


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", w.DWORD),
        ("dwMemoryLoad", w.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def main() -> int:
    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    out = {
        "os": platform.platform(),
        "windows_build": platform.win32_ver(),
        "python": sys.version,
        "machine": platform.machine(),
        "processor": os.environ.get("PROCESSOR_IDENTIFIER"),
        "logical_processors": os.cpu_count(),
        "global_memory_status_ok": bool(ok),
    }
    if ok:
        out.update(
            {
                "total_phys_mb": round(status.ullTotalPhys / 1048576, 1),
                "avail_phys_mb": round(status.ullAvailPhys / 1048576, 1),
                "memory_load_percent": status.dwMemoryLoad,
                "total_pagefile_mb": round(status.ullTotalPageFile / 1048576, 1),
                "avail_pagefile_mb": round(status.ullAvailPageFile / 1048576, 1),
                "total_virtual_mb": round(status.ullTotalVirtual / 1048576, 1),
            }
        )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
