import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req

import json


def run():
    banner("INVITE RESOLVER")
    inv = ask("invite code or url", "")
    if not inv:
        pause()
        return
    m = re.search(r"(?:discord\.gg|discord\.com/invite)/([A-Za-z0-9\-]+)", inv)
    code = m.group(1) if m else inv.strip()

    status, body = http_req(
        f"https://discord.com/api/v10/invites/{code}?with_counts=true&with_expiration=true")
    if status == 200:
        d = json.loads(body)
        guild = d.get("guild", {})
        channel = d.get("channel", {})
        rows = [
            ("invite", d.get("code")),
            ("guild", guild.get("name")),
            ("guild id", guild.get("id")),
            ("members", d.get("approximate_member_count")),
            ("online", d.get("approximate_presence_count")),
            ("channel", channel.get("name")),
            ("expires", d.get("expires_at")),
        ]
        for k, v in rows:
            if v is not None:
                print("  " + c(f"{k:<10}", C.CY) + c(str(v), C.W))
    else:
        print(c(f"  invalid invite ({status})", C.R))
    pause()


if __name__ == "__main__":
    run()
