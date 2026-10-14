import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def _human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def run():
    banner("FOLDER SIZE")
    path = ask("folder", ".") or "."
    if not os.path.isdir(path):
        print(c("  not a folder", C.R))
        pause()
        return

    total = 0
    count = 0
    for dirpath, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
                count += 1
            except Exception:
                pass
    print("  " + c(f"size   {_human(total)}", C.G))
    print("  " + c(f"files  {count}", C.W))
    pause()


if __name__ == "__main__":
    run()
