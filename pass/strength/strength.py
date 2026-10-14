import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import math

SYMBOLS = "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~"


def _pool(pw):
    pool = 0
    if any(ch.islower() for ch in pw):
        pool += 26
    if any(ch.isupper() for ch in pw):
        pool += 26
    if any(ch.isdigit() for ch in pw):
        pool += 10
    if any(ch in SYMBOLS for ch in pw):
        pool += len(SYMBOLS)
    return pool


def _human(seconds):
    if seconds < 1:
        return "instant"
    if seconds < 60:
        return f"{seconds:.1f}s"
    m = seconds / 60
    if m < 60:
        return f"{m:.1f}m"
    h = m / 60
    if h < 24:
        return f"{h:.1f}h"
    d = h / 24
    if d < 365:
        return f"{d:.0f}d"
    y = d / 365
    if y < 1e6:
        return f"{y:,.0f}y"
    return f"{y:.2e}y"


def run():
    banner("PASSWORD STRENGTH")
    pw = ask("password", "")
    if not pw:
        pause()
        return

    L = len(pw)
    pool = _pool(pw)
    entropy = L * math.log2(pool) if pool else 0
    guesses = 2 ** max(0, entropy - 1)

    if entropy < 28:
        score, color = "WEAK", C.R
    elif entropy < 50:
        score, color = "FAIR", C.Y
    elif entropy < 70:
        score, color = "STRONG", C.G
    else:
        score, color = "EXCELLENT", C.G

    print("  " + c(f"length     {L}", C.W))
    print("  " + c(f"pool       {pool} symbols", C.W))
    print("  " + c(f"entropy    {entropy:.1f} bits", C.W))
    print("  " + c(f"score      {score}", color))
    print("  " + c(f"online     {_human(guesses / 1000)}", C.CY))
    print("  " + c(f"offline    {_human(guesses / 1e10)}", C.CY))
    pause()


if __name__ == "__main__":
    run()
