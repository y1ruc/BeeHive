import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import json
import urllib.request


def run():
    banner("IP INFO")
    target = ask("ip or domain (blank = you)", "")
    url = f"http://ip-api.com/json/{target}" if target else "http://ip-api.com/json/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read())
        if data.get("status") == "fail":
            print(c(f"  {data.get('message', 'lookup failed')}", C.R))
            pause()
            return
        rows = [
            ("IP", data.get("query")),
            ("Country", data.get("country")),
            ("Region", data.get("regionName")),
            ("City", data.get("city")),
            ("ZIP", data.get("zip")),
            ("Lat/Lon", f"{data.get('lat')},{data.get('lon')}"),
            ("ISP", data.get("isp")),
            ("Org", data.get("org")),
            ("AS", data.get("as")),
            ("Timezone", data.get("timezone")),
        ]
        for label, val in rows:
            if val:
                print("  " + c(f"{label:<10}", C.CY) + c(str(val), C.W))
    except Exception as e:
        print(c(f"  lookup failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
