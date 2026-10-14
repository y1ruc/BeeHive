import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import hashlib
import itertools

ALGOS_BY_LEN = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}

WORDLIST = [
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123", "654321", "superman",
    "qazwsx", "michael", "football", "admin", "admin123", "welcome", "login",
    "princess", "1q2w3e4r", "solo", "whatever", "school", "student", "teacher",
    "computer", "hacker", "secret", "root", "toor", "god", "test", "guest",
    "123456789", "111111", "000000", "696969", "starwars", "hello", "freedom",
    "password1", "pokemon", "batman", "access", "flower", "matrix", "ninja",
]


def run():
    banner("HASH CRACKER")
    h = ask("hash", "").strip().lower()
    if not h:
        pause()
        return
    algo = ask("algo (auto/md5/sha1/sha256/sha512)", "auto") or "auto"
    if algo == "auto":
        algo = ALGOS_BY_LEN.get(len(h))
    if not algo:
        print(c("  couldn't detect algorithm", C.R))
        pause()
        return
    if not re.fullmatch(r"[0-9a-f]+", h):
        print(c("  hash must be hex", C.R))
        pause()
        return

    print(c(f"  cracking {algo} ...", C.CY))

    for w in WORDLIST:
        if hashlib.new(algo, w.encode()).hexdigest() == h:
            print(c(f"  [FOUND] {w}", C.G))
            pause()
            return

    maxlen = int(ask("  not in list. brute max len (0=skip)", "4") or 4)
    if maxlen > 0:
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        print(c(f"  brute forcing a-z0-9 up to {maxlen} ...", C.CY))
        tries = 0
        for n in range(1, maxlen + 1):
            for tup in itertools.product(charset, repeat=n):
                w = "".join(tup)
                tries += 1
                if hashlib.new(algo, w.encode()).hexdigest() == h:
                    print(c(f"  [FOUND] {w}  ({tries} tries)", C.G))
                    pause()
                    return
    print(c("  not found", C.Y))
    pause()


if __name__ == "__main__":
    run()
