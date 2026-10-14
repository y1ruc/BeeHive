import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("BATCH RENAMER")
    path = ask("folder", ".") or "."
    if not os.path.isdir(path):
        print(c("  not a folder", C.R))
        pause()
        return
    prefix = ask("prefix (blank = none)", "")
    suffix = ask("suffix (blank = none)", "")
    find = ask("find text (blank = skip)", "")
    replace = ask("replace with", "")
    num = ask("add numbering? (y/n)", "n").lower()

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    renamed = 0
    for i, f in enumerate(files, 1):
        stem, ext = os.path.splitext(f)
        new = stem
        if find:
            new = new.replace(find, replace)
        if num in ("y", "yes"):
            new = f"{i:03d}_{new}"
        new = prefix + new + suffix + ext
        if new != f:
            try:
                os.rename(os.path.join(path, f), os.path.join(path, new))
                renamed += 1
            except Exception as e:
                print(c(f"  skip {f}: {e}", C.Y))
    print(c(f"  renamed {renamed} files", C.G))
    pause()


if __name__ == "__main__":
    run()
