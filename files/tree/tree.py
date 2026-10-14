import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def _walk(path, prefix, maxdepth, depth):
    try:
        entries = sorted(os.listdir(path))
    except Exception:
        return
    for i, e in enumerate(entries):
        full = os.path.join(path, e)
        last = i == len(entries) - 1
        branch = "└── " if last else "├── "
        if os.path.isdir(full):
            print(prefix + c(branch, C.CY) + c(e + "/", C.CY))
            if maxdepth is None or depth < maxdepth:
                _walk(full, prefix + ("    " if last else "│   "), maxdepth, depth + 1)
        else:
            print(prefix + c(branch, C.DIM) + c(e, C.W))


def run():
    banner("DIRECTORY TREE")
    path = ask("folder", ".") or "."
    if not os.path.isdir(path):
        print(c("  not a folder", C.R))
        pause()
        return
    d = ask("max depth (blank = all)", "")
    maxdepth = int(d) if d.isdigit() else None
    print("  " + c(path, C.G))
    _walk(path, "", maxdepth, 0)
    pause()


if __name__ == "__main__":
    run()
