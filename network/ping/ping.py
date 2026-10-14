import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import subprocess


def run():
    banner("PING")
    host = ask("host", "google.com") or "google.com"
    count = ask("count", "4") or "4"

    flag = "-n" if os.name == "nt" else "-c"
    print(c(f"  pinging {host} x{count}", C.CY))
    try:
        proc = subprocess.run(["ping", flag, count, host], capture_output=True,
                              text=True, timeout=40)
        out = (proc.stdout or "") + (proc.stderr or "")
        for line in out.splitlines():
            low = line.lower().strip()
            if not low:
                continue
            if "reply" in low or "from " in low or "ttl" in low:
                print("  " + c(line.strip(), C.G))
            elif any(k in low for k in ("request timed out", "unreachable", "100% loss", "could not find", "unknown host")):
                print("  " + c(line.strip(), C.R))
            elif any(k in low for k in ("packets:", "loss", "minimum", "maximum", "average", "statistics")):
                print("  " + c(line.strip(), C.Y))
    except Exception as e:
        print(c(f"  ping failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
