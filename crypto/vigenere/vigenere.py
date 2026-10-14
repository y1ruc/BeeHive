import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def vigenere(text, key, decrypt=False):
    out = []
    ki = 0
    key = key.lower()
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key[ki % len(key)]) - ord("a")
            if decrypt:
                shift = -shift
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def run():
    banner("VIGENERE")
    mode = ask("mode (e/d)", "e").lower() or "e"
    key = ask("key", "key") or "key"
    text = ask("input", "")
    if not text:
        pause()
        return
    out = vigenere(text, key, decrypt=not mode.startswith("e"))
    print(c(out, C.G))
    pause()


if __name__ == "__main__":
    run()
