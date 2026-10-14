import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

LEET = str.maketrans("aegiost", "4631057")
UNLEET = str.maketrans("4631057", "aegiost")


def run():
    banner("LEETSPEAK")
    mode = ask("mode (e/d)", "e").lower() or "e"
    text = ask("input", "")
    if not text:
        pause()
        return
    if mode.startswith("e"):
        out = text.lower().translate(LEET)
    else:
        out = text.translate(UNLEET)
    print(c(out, C.G))
    pause()


if __name__ == "__main__":
    run()
