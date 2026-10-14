import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import json
import urllib.request


def run():
    banner("WHOIS")
    domain = ask("domain", "google.com") or "google.com"
    url = f"https://rdap.org/domain/{domain}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=15).read())
        print("  " + c(f"domain    {d.get('ldhName', domain)}", C.CY))

        for ev in d.get("events", []):
            action = ev.get("eventAction", "?")
            date = ev.get("eventDate", "")
            if date:
                print("  " + c(f"{action:<10}{date}", C.W))

        for ns in d.get("nameservers", []):
            name = ns.get("ldhName", "")
            if name:
                print("  " + c(f"ns        {name}", C.G))

        for ent in d.get("entities", []):
            handle = ent.get("handle", "")
            roles = ",".join(ent.get("roles", []))
            if handle:
                print("  " + c(f"entity    {handle}  ({roles})", C.Y))
            for v in ent.get("vcardArray", [[], []])[-1] if isinstance(ent.get("vcardArray"), list) and len(ent.get("vcardArray", [])) > 1 else []:
                if isinstance(v, list) and len(v) >= 4 and v[0] in ("fn", "org"):
                    print("  " + c(f"          {v[3]}", C.W))
    except Exception as e:
        print(c(f"  whois failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
