import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import hashlib
import os as _os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"BHCRYPT"
BLOCK = 1024 * 1024


def _encrypt(src, dst, key):
    aes = AESGCM(key)
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        fout.write(MAGIC)
        while True:
            block = fin.read(BLOCK)
            if not block:
                break
            nonce = _os.urandom(12)
            ct = aes.encrypt(nonce, block, None)
            fout.write(nonce)
            fout.write(len(ct).to_bytes(4, "big"))
            fout.write(ct)


def _decrypt(src, dst, key):
    aes = AESGCM(key)
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        if fin.read(len(MAGIC)) != MAGIC:
            raise ValueError("not a BeeHive-encrypted file")
        while True:
            nonce = fin.read(12)
            if len(nonce) < 12:
                break
            lb = fin.read(4)
            if len(lb) < 4:
                break
            ct = fin.read(int.from_bytes(lb, "big"))
            fout.write(aes.decrypt(nonce, ct, None))


def run():
    banner("FILE ENCRYPT")
    mode = ask("mode (e/d)", "e").lower() or "e"
    path = ask("file path", "")
    if not path or not os.path.isfile(path):
        print(c("  file not found", C.R))
        pause()
        return
    pw = ask("password", "") or "password"
    key = hashlib.sha256(pw.encode()).digest()

    try:
        if mode.startswith("e"):
            dst = path + ".enc"
            _encrypt(path, dst, key)
            print(c(f"  encrypted -> {dst}", C.G))
        else:
            dst = path[:-4] if path.endswith(".enc") else path + ".dec"
            _decrypt(path, dst, key)
            print(c(f"  decrypted -> {dst}", C.G))
    except Exception as e:
        print(c(f"  failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
