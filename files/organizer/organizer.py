import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("FILE ORGANIZER")
    path = ask("folder", ".") or "."
    if not os.path.isdir(path):
        print(c("  not a folder", C.R))
        pause()
        return

    moved = 0
    for f in os.listdir(path):
        full = os.path.join(path, f)
        if os.path.isfile(full):
            ext = os.path.splitext(f)[1].lower().lstrip(".") or "noext"
            destdir = os.path.join(path, ext)
            try:
                os.makedirs(destdir, exist_ok=True)
                shutil.move(full, os.path.join(destdir, f))
                moved += 1
            except Exception as e:
                print(c(f"  skip {f}: {e}", C.Y))
    print(c(f"  moved {moved} files into extension folders", C.G))
    pause()


if __name__ == "__main__":
    run()
