import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import base64
import hashlib
import os as _os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def run():
    banner("AES-GCM")
    mode = ask("mode (e/d)", "e").lower() or "e"
    pw = ask("password", "") or "password"
    key = hashlib.sha256(pw.encode()).digest()

    if mode.startswith("e"):
        plain = ask("plaintext", "")
        if not plain:
            pause()
            return
        aes = AESGCM(key)
        nonce = _os.urandom(12)
        ct = aes.encrypt(nonce, plain.encode(), None)
        print(c(base64.b64encode(nonce + ct).decode(), C.G))
    else:
        b64 = ask("ciphertext", "")
        if not b64:
            pause()
            return
        try:
            raw = base64.b64decode(b64)
            nonce, ct = raw[:12], raw[12:]
            aes = AESGCM(key)
            out = aes.decrypt(nonce, ct, None).decode()
            print(c(out, C.G))
        except Exception:
            print(c("  decrypt failed (wrong password?)", C.R))
    pause()


if __name__ == "__main__":
    run()
