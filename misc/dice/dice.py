import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random


def run():
    banner("DICE ROLLER")
    sides = int(ask("sides", "6") or 6)
    count = int(ask("count", "5") or 5)

    total = 0
    rolls = []
    for _ in range(count):
        r = random.randint(1, sides)
        rolls.append(r)
        total += r
    print("  " + c(" ".join(str(r) for r in rolls), C.G))
    print("  " + c(f"total {total}", C.CY))

    if ask("flip a coin? (y/n)", "n").lower() in ("y", "yes"):
        flips = int(ask("flips", "5") or 5)
        heads = sum(1 for _ in range(flips) if random.random() < 0.5)
        print("  " + c(f"{heads} heads / {flips - heads} tails", C.G))
    pause()


if __name__ == "__main__":
    run()
