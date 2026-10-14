import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("HEX")
    mode = ask("mode (e/d)", "e").lower() or "e"
    text = ask("input", "")
    if not text:
        pause()
        return
    try:
        if mode.startswith("e"):
            out = text.encode().hex()
        else:
            out = bytes.fromhex(text.replace(" ", "").replace("0x", "")).decode(errors="replace")
        print(c(out, C.G))
    except Exception as e:
        print(c(f"  error: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
