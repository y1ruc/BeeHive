import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import html


def run():
    banner("HTML ENTITIES")
    mode = ask("mode (e/d)", "e").lower() or "e"
    text = ask("input", "")
    if not text:
        pause()
        return
    if mode.startswith("e"):
        out = html.escape(text)
    else:
        out = html.unescape(text)
    print(c(out, C.G))
    pause()


if __name__ == "__main__":
    run()
