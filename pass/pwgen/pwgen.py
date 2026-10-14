import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import secrets
import string


def run():
    banner("PASSWORD GENERATOR")
    length = int(ask("length", "16") or 16)
    count = int(ask("count", "10") or 10)

    pool = ""
    if ask("lowercase (y/n)", "y").lower() in ("", "y", "yes"):
        pool += string.ascii_lowercase
    if ask("uppercase (y/n)", "y").lower() in ("", "y", "yes"):
        pool += string.ascii_uppercase
    if ask("digits (y/n)", "y").lower() in ("", "y", "yes"):
        pool += string.digits
    if ask("symbols (y/n)", "y").lower() in ("", "y", "yes"):
        pool += string.punctuation
    if not pool:
        pool = string.ascii_letters + string.digits

    print(c(f"  {length} chars from {len(pool)}-symbol pool", C.CY))
    for _ in range(count):
        pw = "".join(secrets.choice(pool) for _ in range(length))
        print("  " + c(pw, C.G))
    pause()


if __name__ == "__main__":
    run()
