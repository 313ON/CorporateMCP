"""Safe aggregate process observations."""

import ctypes
import os
from multiprocessing import current_process
from typing import Any


def _process_count() -> int:
    if os.name != "nt":
        try:
            return sum(name.isdigit() for name in os.listdir("/proc"))
        except OSError:
            return 1

    class ProcessEntry(ctypes.Structure):
        _fields_ = [("size", ctypes.c_ulong), ("rest", ctypes.c_byte * 556)]

    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == -1:
        return 1
    try:
        entry = ProcessEntry()
        entry.size = ctypes.sizeof(entry)
        count = 0
        if kernel32.Process32First(snapshot, ctypes.byref(entry)):
            count = 1
            while kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                count += 1
        return count or 1
    finally:
        kernel32.CloseHandle(snapshot)


def collect_process_summary() -> dict[str, Any]:
    return {
        "process_count": _process_count(),
        "current_process_id": os.getpid(),
        "current_process_name": current_process().name,
    }
