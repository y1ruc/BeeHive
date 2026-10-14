import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import concurrent.futures
import socket

SUBS = [
    "www", "mail", "ftp", "admin", "api", "dev", "test", "staging", "vpn",
    "portal", "remote", "webmail", "smtp", "pop", "ns1", "ns2", "cdn", "static",
    "app", "blog", "shop", "secure", "login", "m", "mobile", "beta", "old",
    "new", "intranet", "git", "docs", "support", "status", "mx", "dns",
    "backup", "db", "mysql", "panel", "cpanel", "web", "files", "upload",
    "download", "proxy", "gw", "firewall", "auth", "sso", "gateway", "edge",
]


def _resolve(sub, domain):
    try:
        socket.getaddrinfo(f"{sub}.{domain}", None)
        return sub, True
    except Exception:
        return sub, False


def run():
    banner("SUBDOMAIN SCANNER")
    domain = ask("domain", "google.com") or "google.com"
    threads = int(ask("threads", "50") or 50)

    print(c(f"  scanning {domain}  ·  {len(SUBS)} subdomains", C.CY))
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        for sub, ok in ex.map(lambda s: _resolve(s, domain), SUBS):
            if ok:
                found.append(sub)
                print("  " + c(f"[+] {sub}.{domain}", C.G))
    print(c(f"  {len(found)}/{len(SUBS)} resolved", C.G if found else C.Y))
    pause()


if __name__ == "__main__":
    run()
