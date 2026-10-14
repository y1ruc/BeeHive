import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req, parse_webhook


def run():
    banner("WEBHOOK SPAM")
    url = ask("webhook url", "")
    if not url:
        pause()
        return
    if not parse_webhook(url)[1]:
        print(c("  invalid webhook url", C.R))
        pause()
        return
    content = ask("message", "spam") or "spam"
    count = int(ask("count", "10") or 10)
    delay = float(ask("delay (s)", "0.5") or 0.5)

    ok = fail = 0
    for i in range(count):
        status, body = http_req(url, method="POST", json={"content": content})
        if status in (200, 204):
            ok += 1
        else:
            fail += 1
            msg = body.decode(errors="replace")[:120]
            print(c(f"  [{i + 1}] failed {status}: {msg}", C.R))
            if status == 429:
                print(c("  rate limited — discord caps webhooks at ~30/min", C.Y))
                break
        time.sleep(delay)

    print(c(f"  done: {ok} sent, {fail} failed", C.G if ok else C.Y))
    pause()


if __name__ == "__main__":
    run()
