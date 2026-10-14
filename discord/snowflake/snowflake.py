import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import datetime

DISCORD_EPOCH = 1420070400000


def run():
    banner("SNOWFLAKE DECODER")
    sid = ask("snowflake id", "")
    if not sid:
        pause()
        return
    try:
        sid = int(sid)
    except ValueError:
        print(c("  must be a number", C.R))
        pause()
        return

    ts_ms = (sid >> 22) + DISCORD_EPOCH
    worker = (sid >> 17) & 0x1F
    pid = (sid >> 12) & 0x1F
    inc = sid & 0xFFF
    dt = datetime.datetime.fromtimestamp(ts_ms / 1000, datetime.timezone.utc)

    print("  " + c(f"timestamp   {dt.isoformat()}", C.G))
    print("  " + c(f"local       {dt.astimezone()}", C.W))
    print("  " + c(f"worker      {worker}", C.W))
    print("  " + c(f"process     {pid}", C.W))
    print("  " + c(f"increment   {inc}", C.W))
    pause()


if __name__ == "__main__":
    run()
