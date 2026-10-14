import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import urllib.parse


def run():
    banner("URL ENCODE")
    mode = ask("mode (e/d)", "e").lower() or "e"
    text = ask("input", "")
    if not text:
        pause()
        return
    if mode.startswith("e"):
        out = urllib.parse.quote(text)
    else:
        out = urllib.parse.unquote(text)
    print(c(out, C.G))
    pause()


if __name__ == "__main__":
    run()
