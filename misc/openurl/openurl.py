import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import webbrowser

RICKROLL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def run():
    banner("OPEN URL")
    print("  " + c("[1]", C.CY) + " rickroll preset")
    print("  " + c("[2]", C.CY) + " custom url")
    print()
    ch = ask("choice", "1")
    if ch == "2":
        url = ask("url", "https://example.com") or "https://example.com"
    else:
        url = RICKROLL
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    print(c(f"  opened {url}", C.G))
    pause()


if __name__ == "__main__":
    run()
