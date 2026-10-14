import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req

import json

NITRO = {0: "none", 1: "classic", 2: "boost", 3: "basic"}


def run():
    banner("TOKEN INFO")
    token = ask("token", "")
    if not token:
        pause()
        return

    status, body = http_req("https://discord.com/api/v10/users/@me",
                            headers={"Authorization": token})
    if status == 200:
        d = json.loads(body)
        rows = [
            ("username", d.get("username")),
            ("id", d.get("id")),
            ("email", d.get("email")),
            ("verified", d.get("verified")),
            ("mfa", d.get("mfa_enabled")),
            ("nitro", NITRO.get(d.get("premium_type", 0), "unknown")),
            ("locale", d.get("locale")),
            ("flags", d.get("flags")),
            ("banner", d.get("banner")),
            ("accent", d.get("accent_color")),
        ]
        for k, v in rows:
            if v is not None:
                print("  " + c(f"{k:<10}", C.CY) + c(str(v), C.W))
    elif status == 401:
        print(c("  invalid token (401 unauthorized)", C.R))
    else:
        print(c(f"  failed ({status}): {body.decode(errors='replace')[:200]}", C.R))
    pause()


if __name__ == "__main__":
    run()
