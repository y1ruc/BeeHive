import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import concurrent.futures
import socket

COMMON = [20, 21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995,
          1433, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443]


def _check(host, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return port, True
    except Exception:
        return port, False
    finally:
        s.close()


def _service(port):
    try:
        return socket.getservbyport(port)
    except Exception:
        return ""


def run():
    banner("PORT SCANNER")
    host = ask("target host/ip", "127.0.0.1") or "127.0.0.1"
    rng = ask("ports (a-b | common)", "common") or "common"
    if rng == "common":
        ports = COMMON
    else:
        try:
            a, b = rng.split("-")
            ports = list(range(int(a), int(b) + 1))
        except Exception:
            ports = COMMON
    threads = int(ask("threads", "200") or 200)
    timeout = float(ask("timeout (s)", "1.0") or 1.0)

    print(c(f"  scanning {host}  ·  {len(ports)} ports  ·  {threads} threads", C.CY))
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(_check, host, p, timeout): p for p in ports}
        done = 0
        for f in concurrent.futures.as_completed(futs):
            port, ok = f.result()
            done += 1
            if ok:
                open_ports.append(port)
                svc = _service(port)
                print("  " + c(f"[+] {port:<6} {svc}", C.G))
    print(c(f"  done: {done} scanned, {len(open_ports)} open", C.G if open_ports else C.Y))
    pause()


if __name__ == "__main__":
    run()
