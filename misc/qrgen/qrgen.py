import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import urllib.parse
import urllib.request
import webbrowser


def run():
    banner("QR CODE")
    data = ask("text or url", "https://google.com") or "https://google.com"
    size = ask("size px", "300") or "300"
    out = "qr.png"

    url = (f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data="
           + urllib.parse.quote(data))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with open(out, "wb") as f:
            f.write(urllib.request.urlopen(req, timeout=20).read())
        print(c(f"  saved -> {out}", C.G))
        try:
            os.startfile(out)
        except Exception:
            webbrowser.open(out)
    except Exception as e:
        print(c(f"  failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
