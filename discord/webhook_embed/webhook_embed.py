import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req, parse_webhook


def run():
    banner("WEBHOOK EMBED")
    url = ask("webhook url", "")
    if not url:
        pause()
        return
    if not parse_webhook(url)[1]:
        print(c("  invalid webhook url", C.R))
        pause()
        return
    title = ask("title", "Title") or "Title"
    desc = ask("description", "")
    footer = ask("footer (blank = none)", "")
    color = ask("color hex (blank = none)", "").strip()

    embed = {"title": title}
    if desc:
        embed["description"] = desc
    if footer:
        embed["footer"] = {"text": footer}
    if color:
        try:
            embed["color"] = int(color.lstrip("#"), 16)
        except Exception:
            pass

    status, body = http_req(url, method="POST", json={"embeds": [embed]})
    if status in (200, 204):
        print(c("  sent", C.G))
    else:
        print(c(f"  failed ({status}): {body.decode(errors='replace')[:200]}", C.R))
    pause()


if __name__ == "__main__":
    run()
