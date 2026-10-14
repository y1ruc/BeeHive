import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import hashlib
import hmac


def run():
    banner("HMAC")
    msg = ask("message", "")
    key = ask("key", "secret") or "secret"
    algo = ask("algo (sha256/sha512/md5)", "sha256") or "sha256"
    if not msg:
        pause()
        return
    if algo == "sha512":
        fn = hashlib.sha512
    elif algo == "md5":
        fn = hashlib.md5
    else:
        fn = hashlib.sha256
    dig = hmac.new(key.encode(), msg.encode(), fn).hexdigest()
    print(c(dig, C.G))
    pause()


if __name__ == "__main__":
    run()
