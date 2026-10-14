import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req


def run():
    banner("CHANNEL SPAMMER")
    token = ask("token", "")
    channel = ask("channel id", "")
    if not token or not channel:
        pause()
        return
    content = ask("message", "spam") or "spam"
    count = int(ask("count", "10") or 10)
    delay = float(ask("delay (s)", "0.5") or 0.5)

    ok = fail = 0
    url = f"https://discord.com/api/v10/channels/{channel}/messages"
    for i in range(count):
        status, body = http_req(url, method="POST",
                                headers={"Authorization": token},
                                json={"content": content})
        if status == 200:
            ok += 1
        else:
            fail += 1
            msg = body.decode(errors="replace")[:160]
            print(c(f"  [{i + 1}] failed {status}: {msg}", C.R))
            if status in (401, 403):
                print(c("  token invalid or no access to channel", C.Y))
                break
            if status == 429:
                print(c("  rate limited", C.Y))
                break
        time.sleep(delay)

    print(c(f"  done: {ok} sent, {fail} failed", C.G if ok else C.Y))
    pause()


if __name__ == "__main__":
    run()
