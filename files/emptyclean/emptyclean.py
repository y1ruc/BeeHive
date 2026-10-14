import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("EMPTY FOLDER CLEANER")
    root = ask("folder", ".") or "."
    if not os.path.isdir(root):
        print(c("  not a folder", C.R))
        pause()
        return

    removed = []
    for dirpath, _dirs, files in os.walk(root, topdown=False):
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
                removed.append(dirpath)
        except Exception:
            pass

    if removed:
        for d in removed:
            print("  " + c(f"[removed] {d}", C.G))
        print(c(f"  removed {len(removed)} empty folder(s)", C.G))
    else:
        print(c("  no empty folders found", C.G))
    pause()


if __name__ == "__main__":
    run()
