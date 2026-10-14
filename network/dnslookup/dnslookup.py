import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import socket
import subprocess


def run():
    banner("DNS LOOKUP")
    domain = ask("domain", "google.com") or "google.com"

    print(c(f"  {domain}", C.CY))
    try:
        infos = socket.getaddrinfo(domain, None)
        v4 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
        v6 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})
        for ip in v4:
            print("  " + c(f"A     {ip}", C.G))
        for ip in v6:
            print("  " + c(f"AAAA  {ip}", C.G))
    except Exception as e:
        print(c(f"  lookup failed: {e}", C.R))

    for rtype in ("MX", "NS", "TXT"):
        try:
            proc = subprocess.run(["nslookup", "-type=" + rtype, domain],
                                  capture_output=True, text=True, timeout=15)
            out = (proc.stdout or "") + (proc.stderr or "")
            seen = False
            for line in out.splitlines():
                s = line.strip()
                if not s or s.startswith("Server:") or s.startswith("Address:"):
                    continue
                if "Non-authoritative" in s or "DNS request timed out" in s:
                    continue
                if s:
                    print("  " + c(f"{rtype:<5} {s}", C.W))
                    seen = True
        except Exception:
            pass
    pause()


if __name__ == "__main__":
    run()
