"""Read-only CPU, memory, and local disk observations."""

import ctypes
import os
import shutil
from pathlib import Path
from typing import Any


def _memory() -> dict[str, int | float | None]:
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total", ctypes.c_ulonglong),
                ("available", ctypes.c_ulonglong),
                ("page_file_total", ctypes.c_ulonglong),
                ("page_file_available", ctypes.c_ulonglong),
                ("virtual_total", ctypes.c_ulonglong),
                ("virtual_available", ctypes.c_ulonglong),
                ("extended_virtual_available", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return {
                "total_bytes": status.total,
                "available_bytes": status.available,
                "percentage": float(status.memory_load),
            }
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        available_pages = os.sysconf("SC_AVPHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        total = pages * page_size
        available = available_pages * page_size
        return {"total_bytes": total, "available_bytes": available, "percentage": (1 - available / total) * 100}
    except (AttributeError, OSError, ValueError):
        return {"total_bytes": None, "available_bytes": None, "percentage": None}


def collect_resources() -> dict[str, Any]:
    root = Path.cwd().anchor or Path.cwd().drive + "\\"
    usage = shutil.disk_usage(root)
    memory = _memory()
    return {
        "cpu_logical_processors": os.cpu_count() or 1,
        "memory_total_bytes": memory["total_bytes"],
        "memory_available_bytes": memory["available_bytes"],
        "memory_percentage": memory["percentage"],
        "disks": [{"path": root, "total_bytes": usage.total, "used_bytes": usage.used, "free_bytes": usage.free}],
    }
