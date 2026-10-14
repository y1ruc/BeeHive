import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import base64


def run():
    banner("BASE ENCODER")
    mode = ask("mode (e/d)", "e").lower() or "e"
    algo = ask("algo (64/32/16/85)", "64")
    text = ask("input", "")
    if not text:
        pause()
        return
    try:
        data = text.encode()
        if mode.startswith("e"):
            if algo == "64":
                out = base64.b64encode(data).decode()
            elif algo == "32":
                out = base64.b32encode(data).decode()
            elif algo == "16":
                out = base64.b16encode(data).decode()
            elif algo == "85":
                out = base64.b85encode(data).decode()
            else:
                out = base64.b64encode(data).decode()
        else:
            if algo == "64":
                out = base64.b64decode(text).decode()
            elif algo == "32":
                out = base64.b32decode(text).decode()
            elif algo == "16":
                out = base64.b16decode(text).decode()
            elif algo == "85":
                out = base64.b85decode(text).decode()
            else:
                out = base64.b64decode(text).decode()
        print(c(out, C.G))
    except Exception as e:
        print(c(f"  error: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
