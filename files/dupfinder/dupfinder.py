import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import hashlib
from collections import defaultdict


def _hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run():
    banner("DUPLICATE FINDER")
    path = ask("folder", ".") or "."
    if not os.path.isdir(path):
        print(c("  not a folder", C.R))
        pause()
        return

    print(c("  scanning ...", C.CY))
    by_size = defaultdict(list)
    for dirpath, _dirs, files in os.walk(path):
        for f in files:
            full = os.path.join(dirpath, f)
            try:
                by_size[os.path.getsize(full)].append(full)
            except Exception:
                pass

    dups = 0
    groups = []
    for size, files in by_size.items():
        if len(files) < 2:
            continue
        by_hash = defaultdict(list)
        for full in files:
            try:
                by_hash[_hash(full)].append(full)
            except Exception:
                pass
        for h, group in by_hash.items():
            if len(group) > 1:
                groups.append(group)

    for group in groups:
        print("  " + c("--- duplicates ---", C.Y))
        for full in group:
            print("  " + c(full, C.W))
        dups += len(group) - 1

    if not groups:
        print(c("  no duplicates found", C.G))
    else:
        print(c(f"  {dups} duplicate file(s) across {len(groups)} group(s)", C.G))
        if ask("delete duplicates, keep first? (y/n)", "n").lower() in ("y", "yes"):
            removed = 0
            for group in groups:
                for full in group[1:]:
                    try:
                        os.remove(full)
                        removed += 1
                    except Exception as e:
                        print(c(f"  skip {full}: {e}", C.Y))
            print(c(f"  removed {removed} file(s)", C.G))
    pause()


if __name__ == "__main__":
    run()
