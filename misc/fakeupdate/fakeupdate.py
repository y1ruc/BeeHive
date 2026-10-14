import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("FAKE UPDATE")
    print(c("  Working on updates 0% complete", C.W))
    print(c("  Don't turn off your PC", C.DIM))
    time.sleep(0.5)
    for i in range(101):
        bar = "█" * (i // 2) + "░" * (50 - i // 2)
        sys.stdout.write("\r  " + C.CY + f"  {i:3d}%  [{bar}]" + C.RST)
        sys.stdout.flush()
        time.sleep(0.03)
    print()
    print(c("  update complete. restarting...", C.G))
    time.sleep(1)
    pause()


if __name__ == "__main__":
    run()
