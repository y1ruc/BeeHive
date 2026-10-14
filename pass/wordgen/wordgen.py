import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import itertools


def run():
    banner("WORDLIST GENERATOR")
    charset = ask("charset (blank = a-z0-9)", "abcdefghijklmnopqrstuvwxyz0123456789")
    if not charset:
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    mn = int(ask("min length", "1") or 1)
    mx = int(ask("max length", "3") or 3)
    outfile = ask("output file", "wordlist.txt") or "wordlist.txt"

    total = sum(len(charset) ** n for n in range(mn, mx + 1))
    print(c(f"  generating {total:,} entries -> {outfile}", C.CY))

    count = 0
    with open(outfile, "w", encoding="utf-8") as f:
        for n in range(mn, mx + 1):
            for tup in itertools.product(charset, repeat=n):
                f.write("".join(tup) + "\n")
                count += 1
    print(c(f"  wrote {count:,} words", C.G))
    pause()


if __name__ == "__main__":
    run()
