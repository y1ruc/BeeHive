import os
import random
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

CHARS = "01"


def run():
    banner("MATRIX RAIN")
    cols = int(ask("columns (0 = auto)", "0") or 0) or max(20, shutil.get_terminal_size().columns // 2)
    rows = 18
    secs = float(ask("seconds (0 = until ctrl+c)", "8") or 8)
    speed = 0.05

    drops = [random.randint(-rows, 0) for _ in range(cols)]
    end = time.time() + (secs if secs > 0 else 1e9)
    try:
        while time.time() < end:
            frame = []
            for y in range(rows):
                row = ""
                for x in range(cols):
                    if drops[x] == y:
                        row += C.W + random.choice(CHARS) + C.RST
                    elif 0 <= y - drops[x] < 8:
                        row += C.G + random.choice(CHARS) + C.RST
                    else:
                        row += " "
                frame.append(row)
            sys.stdout.write("\x1b[H\x1b[2J")
            sys.stdout.write("\n".join(frame) + "\n")
            sys.stdout.flush()
            for i in range(cols):
                if random.random() < 0.06 or drops[i] > rows + 8:
                    drops[i] = random.randint(-rows, 0)
                else:
                    drops[i] += 1
            time.sleep(speed)
    except KeyboardInterrupt:
        pass
    sys.stdout.write("\x1b[H\x1b[2J")
    pause()


if __name__ == "__main__":
    run()
