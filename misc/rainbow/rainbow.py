import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

RAINBOW = [
    "\x1b[38;5;196m", "\x1b[38;5;208m", "\x1b[38;5;226m", "\x1b[38;5;46m",
    "\x1b[38;5;51m", "\x1b[38;5;21m", "\x1b[38;5;129m", "\x1b[38;5;201m",
]


def run():
    banner("RAINBOW TEXT")
    text = ask("text", "BeeHive") or "BeeHive"
    out = "".join(RAINBOW[i % len(RAINBOW)] + ch for i, ch in enumerate(text)) + "\x1b[0m"
    print("  " + out)
    pause()


if __name__ == "__main__":
    run()
