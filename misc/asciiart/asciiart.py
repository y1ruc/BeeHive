import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import pyfiglet


def run():
    banner("ASCII ART")
    text = ask("text", "BeeHive") or "BeeHive"
    font = ask("font (blank = standard)", "")
    try:
        if font:
            art = pyfiglet.figlet_format(text, font=font)
        else:
            art = pyfiglet.figlet_format(text)
        print(c(art, C.G))
    except Exception as e:
        print(c(f"  failed (bad font?): {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
