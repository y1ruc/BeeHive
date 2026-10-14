import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import secrets

WORDS = [
    "apple", "banana", "cherry", "dragon", "eagle", "falcon", "garden", "hammer",
    "island", "jungle", "kitten", "lemon", "mango", "night", "orange", "panda",
    "quartz", "river", "silver", "tiger", "umber", "violet", "walnut", "xenon",
    "yellow", "zephyr", "anchor", "breeze", "cactus", "denim", "ember", "frost",
    "gravel", "harbor", "indigo", "jade", "koala", "lunar", "maple", "nebula",
    "ocean", "pepper", "quill", "raven", "saffron", "tundra", "umber", "velvet",
    "willow", "zinc", "acorn", "badger", "cedar", "dune", "ember", "fern",
]


def run():
    banner("PASSPHRASE GENERATOR")
    n = int(ask("words", "4") or 4)
    sep = ask("separator", "-") or "-"
    count = int(ask("count", "5") or 5)

    for _ in range(count):
        words = [secrets.choice(WORDS) for _ in range(n)]
        print("  " + c(sep.join(words), C.G))
    pause()


if __name__ == "__main__":
    run()
