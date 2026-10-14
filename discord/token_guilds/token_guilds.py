import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req

import json


def run():
    banner("TOKEN GUILDS")
    token = ask("token", "")
    if not token:
        pause()
        return

    status, body = http_req("https://discord.com/api/v10/users/@me/guilds",
                            headers={"Authorization": token})
    if status == 200:
        guilds = json.loads(body)
        print(c(f"  {len(guilds)} guilds", C.CY))
        for g in guilds:
            owner = " [OWNER]" if g.get("owner") else ""
            print("  " + c(g.get("name", "?"), C.G) + c(f"  ·  {g.get('id')}{owner}", C.W))
    elif status == 401:
        print(c("  invalid token (401)", C.R))
    else:
        print(c(f"  failed ({status}): {body.decode(errors='replace')[:200]}", C.R))
    pause()


if __name__ == "__main__":
    run()
