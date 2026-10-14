import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def _shift(ch, s):
    if "a" <= ch <= "z":
        return chr((ord(ch) - 97 + s) % 26 + 97)
    if "A" <= ch <= "Z":
        return chr((ord(ch) - 65 + s) % 26 + 65)
    return ch


def run():
    banner("ROT / CAESAR")
    mode = ask("mode (e/d)", "e").lower() or "e"
    shift = int(ask("shift (13 = rot13)", "13") or 13)
    text = ask("input", "")
    if not text:
        pause()
        return
    s = shift if mode.startswith("e") else (-shift % 26)
    out = "".join(_shift(ch, s) for ch in text)
    print(c(out, C.G))
    pause()


if __name__ == "__main__":
    run()
