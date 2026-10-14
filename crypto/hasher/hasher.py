import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import hashlib

ALGOS = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512", "blake2b", "blake2s",
]


def _digest(algo, data):
    if algo == "blake2b":
        return hashlib.blake2b(data).hexdigest()
    if algo == "blake2s":
        return hashlib.blake2s(data).hexdigest()
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()


def run():
    banner("HASH CALCULATOR")
    mode = ask("mode (text/file)", "text").lower() or "text"
    if mode.startswith("f"):
        path = ask("file path", "")
        if not path:
            pause()
            return
        try:
            data = open(path, "rb").read()
            print(c(f"  {path}  ({len(data)} bytes)", C.CY))
        except Exception as e:
            print(c(f"  error: {e}", C.R))
            pause()
            return
    else:
        text = ask("input", "")
        if not text:
            pause()
            return
        data = text.encode()

    for algo in ALGOS:
        print("  " + c(f"{algo:<10}", C.CY) + c(_digest(algo, data), C.W))
    pause()


if __name__ == "__main__":
    run()
