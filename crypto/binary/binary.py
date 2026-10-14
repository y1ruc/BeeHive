import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("BINARY / OCTAL")
    mode = ask("mode (e/d)", "e").lower() or "e"
    base = ask("base (2/8)", "2")
    text = ask("input", "")
    if not text:
        pause()
        return
    try:
        if mode.startswith("e"):
            if base == "8":
                out = " ".join(format(b, "03o") for b in text.encode())
            else:
                out = " ".join(format(b, "08b") for b in text.encode())
        else:
            toks = text.replace(",", " ").split()
            if base == "8":
                data = bytes(int(t, 8) for t in toks)
            else:
                data = bytes(int(t, 2) for t in toks)
            out = data.decode(errors="replace")
        print(c(out, C.G))
    except Exception as e:
        print(c(f"  error: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
