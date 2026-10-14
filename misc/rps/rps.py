import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random

NAMES = {"r": "rock", "p": "paper", "s": "scissors"}
BEATS = {"r": "s", "s": "p", "p": "r"}


def run():
    banner("ROCK PAPER SCISSORS")
    score = {"you": 0, "pc": 0}
    print(c("  r=rock  p=paper  s=scissors  q=quit", C.DIM))
    while True:
        m = ask("r/p/s", "").lower()
        if m in ("q", "quit", ""):
            break
        if m not in BEATS:
            print(c("  pick r, p, or s", C.R))
            continue
        pc = random.choice(list(BEATS))
        if m == pc:
            res = "draw"
            color = C.Y
        elif BEATS[m] == pc:
            res = "you win"
            score["you"] += 1
            color = C.G
        else:
            res = "you lose"
            score["pc"] += 1
            color = C.R
        print("  " + c(f"{NAMES[m]} vs {NAMES[pc]} -> {res}", color))
        print("  " + c(f"score  you {score['you']} : {score['pc']} pc", C.W))
    pause()


if __name__ == "__main__":
    run()
