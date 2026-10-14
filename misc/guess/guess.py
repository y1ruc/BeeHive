import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random


def run():
    banner("GUESS THE NUMBER")
    lo, hi = 1, 100
    target = random.randint(lo, hi)
    tries = 0
    print(c(f"  i'm thinking of a number {lo}-{hi}", C.CY))
    while True:
        g = ask("guess", "")
        if g == "":
            print(c(f"  it was {target}", C.Y))
            break
        try:
            g = int(g)
        except ValueError:
            print(c("  enter a number", C.R))
            continue
        tries += 1
        if g < target:
            print(c("  higher", C.Y))
        elif g > target:
            print(c("  lower", C.Y))
        else:
            print(c(f"  correct! {tries} tries", C.G))
            break
    pause()


if __name__ == "__main__":
    run()
