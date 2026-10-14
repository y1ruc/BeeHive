import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import uuid


def run():
    banner("UUID GENERATOR")
    v = ask("version (1/4)", "4") or "4"
    count = int(ask("count", "5") or 5)
    for _ in range(count):
        u = uuid.uuid1() if v == "1" else uuid.uuid4()
        print("  " + c(str(u), C.G))
    pause()


if __name__ == "__main__":
    run()
