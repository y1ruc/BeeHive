import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req, parse_webhook


def run():
    banner("WEBHOOK SEND")
    url = ask("webhook url", "")
    if not url:
        pause()
        return
    if not parse_webhook(url)[1]:
        print(c("  invalid webhook url", C.R))
        pause()
        return
    content = ask("message", "hello") or "hello"
    name = ask("username (blank = default)", "")
    avatar = ask("avatar url (blank = default)", "")

    data = {"content": content}
    if name:
        data["username"] = name
    if avatar:
        data["avatar_url"] = avatar

    status, body = http_req(url, method="POST", json=data)
    if status in (200, 204):
        print(c("  sent", C.G))
    else:
        print(c(f"  failed ({status}): {body.decode(errors='replace')[:200]}", C.R))
    pause()


if __name__ == "__main__":
    run()
