import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req

import json


def _check(token):
    status, body = http_req("https://discord.com/api/v10/users/@me",
                            headers={"Authorization": token})
    if status == 200:
        try:
            u = json.loads(body)
            return True, f"{u.get('username')}#{u.get('discriminator', '0')} ({u.get('id')})"
        except Exception:
            return True, "valid (couldn't parse user)"
    return False, f"{status}"


def run():
    banner("TOKEN CHECKER")
    src = ask("token or file path", "")
    if not src:
        pause()
        return

    if os.path.isfile(src):
        with open(src, "r", encoding="utf-8") as f:
            tokens = [ln.strip() for ln in f if ln.strip()]
    else:
        tokens = [src]

    print(c(f"  checking {len(tokens)} token(s)", C.CY))
    for t in tokens:
        ok, info = _check(t)
        tag = c("[VALID] ", C.G) if ok else c("[DEAD]  ", C.R)
        print("  " + tag + c(t[:20] + "..." + "  " + info, C.W))
    pause()


if __name__ == "__main__":
    run()
