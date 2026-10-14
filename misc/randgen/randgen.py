import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random


def run():
    banner("RANDOM GENERATOR")
    mode = ask("mode (num/pick/shuffle)", "num").lower()
    if mode.startswith("p"):
        items = ask("items (comma separated)", "a,b,c")
        lst = [x.strip() for x in items.split(",") if x.strip()]
        n = int(ask("count", "3") or 3)
        print("  " + c(", ".join(random.choice(lst) for _ in range(n)), C.G))
    elif mode.startswith("s"):
        items = ask("items (comma separated)", "a,b,c")
        lst = [x.strip() for x in items.split(",") if x.strip()]
        random.shuffle(lst)
        print("  " + c(" ".join(lst), C.G))
    else:
        lo = int(ask("min", "1") or 1)
        hi = int(ask("max", "100") or 100)
        n = int(ask("count", "5") or 5)
        print("  " + c(" ".join(str(random.randint(lo, hi)) for _ in range(n)), C.G))
    pause()


if __name__ == "__main__":
    run()
