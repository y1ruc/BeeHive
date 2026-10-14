import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause, http_req

import base64
import os as _os


def _gen():
    p1 = base64.urlsafe_b64encode(_os.urandom(12)).decode().rstrip("=")
    p2 = base64.urlsafe_b64encode(_os.urandom(8)).decode().rstrip("=")
    p3 = base64.urlsafe_b64encode(_os.urandom(24)).decode().rstrip("=")
    return f"{p1}.{p2}.{p3}"


def run():
    banner("TOKEN GENERATOR")
    count = int(ask("count", "5") or 5)
    check = ask("check against api? (y/n)", "n").lower()

    for _ in range(count):
        tok = _gen()
        print("  " + c(tok, C.W))
        if check in ("y", "yes"):
            status, _ = http_req("https://discord.com/api/v10/users/@me",
                                 headers={"Authorization": tok})
            tag = c("VALID", C.G) if status == 200 else c(f"invalid ({status})", C.R)
            print("        " + tag)

    print(c("  note: real tokens are ~120+ bits of randomness — these are", C.DIM))
    print(c("        format-correct but essentially never valid.", C.DIM))
    pause()


if __name__ == "__main__":
    run()
