import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

BLUE = "\x1b[44m"
WHITE = "\x1b[97m"
RST = "\x1b[0m"

LINES = [
    "",
    " :( ",
    "",
    "Your PC ran into a problem and needs to restart.",
    "We're just collecting some error info, and then we'll restart for you.",
    "",
    "0% complete",
    "",
    "For more information about this issue and possible fixes, visit",
    "https://windows.com/stopcode",
    "",
    "If you call a support person, give them this info:",
    "Stop code: CRITICAL_PROCESS_DIED",
    "",
]


def run():
    os.system("cls" if os.name == "nt" else "clear")
    for ln in LINES:
        print(BLUE + WHITE + ln.ljust(58) + RST)
    pause()


if __name__ == "__main__":
    run()
