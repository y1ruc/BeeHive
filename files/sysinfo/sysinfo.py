import os
import platform
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def _ram():
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        m = MEMORYSTATUSEX()
        m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys, m.ullAvailPhys
    except Exception:
        return None, None


def _human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def run():
    banner("SYSTEM INFO")
    total, avail = _ram()
    rows = [
        ("OS", platform.platform()),
        ("System", platform.system()),
        ("Release", platform.release()),
        ("Version", platform.version()),
        ("Machine", platform.machine()),
        ("Processor", platform.processor()),
        ("CPU cores", os.cpu_count()),
        ("RAM", f"{_human(avail)} free / {_human(total)}" if total else "n/a"),
        ("Python", platform.python_version()),
        ("User", os.environ.get("USERNAME") or os.environ.get("USER") or "?"),
    ]
    for k, v in rows:
        print("  " + c(f"{k:<11}", C.CY) + c(str(v), C.W))

    for drive in ("C:\\", "D:\\", "E:\\"):
        try:
            u = shutil.disk_usage(drive)
            print("  " + c(f"{drive:<11}", C.CY) +
                  c(f"{_human(u.free)} free / {_human(u.total)}", C.G))
        except Exception:
            pass
    pause()


if __name__ == "__main__":
    run()
