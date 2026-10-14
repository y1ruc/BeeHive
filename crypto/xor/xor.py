import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("XOR CIPHER")
    mode = ask("mode (e/d)", "e").lower() or "e"
    key = ask("key", "key") or "key"
    text = ask("input", "")
    if not text:
        pause()
        return
    try:
        k = key.encode()
        if mode.startswith("e"):
            data = text.encode()
        else:
            data = bytes.fromhex(text.replace(" ", "").replace("0x", ""))
        out = bytes(b ^ k[i % len(k)] for i, b in enumerate(data))
        if mode.startswith("e"):
            print(c(out.hex(), C.G))
        else:
            print(c(out.decode(errors="replace"), C.G))
    except Exception as e:
        print(c(f"  error: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
