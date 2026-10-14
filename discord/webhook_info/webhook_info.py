import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req, parse_webhook

import json


def run():
    banner("WEBHOOK INFO")
    url = ask("webhook url", "")
    if not url:
        pause()
        return
    if not parse_webhook(url)[1]:
        print(c("  invalid webhook url", C.R))
        pause()
        return

    status, body = http_req(url)
    if status == 200:
        d = json.loads(body)
        rows = [
            ("name", d.get("name")),
            ("id", d.get("id")),
            ("channel", d.get("channel_id")),
            ("guild", d.get("guild_id")),
            ("type", "Incoming" if d.get("type") == 1 else str(d.get("type"))),
            ("avatar", d.get("avatar")),
            ("user", d.get("user", {}).get("username") if d.get("user") else None),
        ]
        for k, v in rows:
            if v is not None:
                print("  " + c(f"{k:<10}", C.CY) + c(str(v), C.W))
    else:
        print(c(f"  failed ({status}): {body.decode(errors='replace')[:200]}", C.R))
    pause()


if __name__ == "__main__":
    run()
