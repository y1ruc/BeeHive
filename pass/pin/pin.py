import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import secrets


def run():
    banner("PIN GENERATOR")
    digits = int(ask("digits (4/6)", "4") or 4)
    count = int(ask("count", "10") or 10)

    for _ in range(count):
        pin = f"{secrets.randbelow(10 ** digits):0{digits}d}"
        print("  " + c(pin, C.G))
    pause()


if __name__ == "__main__":
    run()
