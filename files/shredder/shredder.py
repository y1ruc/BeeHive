import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import os as _os


def run():
    banner("FILE SHREDDER")
    path = ask("file path", "")
    if not path or not os.path.isfile(path):
        print(c("  file not found", C.R))
        pause()
        return
    passes = int(ask("passes", "3") or 3)

    size = os.path.getsize(path)
    print(c(f"  shredding {path} ({size} bytes, {passes} passes)", C.CY))
    try:
        with open(path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                remaining = size
                while remaining > 0:
                    chunk = _os.urandom(min(1024 * 1024, remaining))
                    f.write(chunk)
                    remaining -= len(chunk)
                f.flush()
            f.seek(0)
            remaining = size
            while remaining > 0:
                chunk = b"\x00" * min(1024 * 1024, remaining)
                f.write(chunk)
                remaining -= len(chunk)
            f.flush()
        os.remove(path)
        print(c("  shredded and deleted", C.G))
    except Exception as e:
        print(c(f"  failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
