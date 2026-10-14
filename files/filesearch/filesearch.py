import fnmatch
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("FILE SEARCH")
    root = ask("folder", ".") or "."
    if not os.path.isdir(root):
        print(c("  not a folder", C.R))
        pause()
        return
    pattern = ask("pattern (*.txt | name)", "*") or "*"
    content = ask("containing text (blank = skip)", "")

    print(c("  searching ...", C.CY))
    results = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                full = os.path.join(dirpath, f)
                if content:
                    try:
                        with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                            if content in fh.read():
                                results.append(full)
                    except Exception:
                        pass
                else:
                    results.append(full)

    print(c(f"  {len(results)} match(es)", C.G))
    for r in results[:200]:
        print("  " + c(r, C.W))
    if len(results) > 200:
        print(c(f"  ...and {len(results) - 200} more", C.DIM))
    pause()


if __name__ == "__main__":
    run()
