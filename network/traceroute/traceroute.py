import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import subprocess


def run():
    banner("TRACEROUTE")
    host = ask("host", "google.com") or "google.com"

    cmd = ["tracert", "-d", host] if os.name == "nt" else ["traceroute", host]
    print(c(f"  tracing {host}  (this can take a while)", C.CY))
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            s = line.rstrip()
            if not s.strip():
                continue
            low = s.lower()
            if "ms" in low or "msec" in low or "*" in low:
                print("  " + c(s, C.G))
            elif any(k in low for k in ("trace", "tracing", "maximum", "unable to resolve", "could not", "timed out")):
                print("  " + c(s, C.Y))
            else:
                print("  " + c(s, C.W))
        proc.wait()
    except FileNotFoundError:
        print(c("  tracert/traceroute not found", C.R))
    except Exception as e:
        print(c(f"  trace failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
