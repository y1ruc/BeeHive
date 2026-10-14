import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("FILE SPLITTER")
    mode = ask("mode (split/join)", "split").lower()
    path = ask("file path", "")

    if mode.startswith("s"):
        if not path or not os.path.isfile(path):
            print(c("  file not found", C.R))
            pause()
            return
        mb = int(ask("part size (MB)", "10") or 10)
        chunk = mb * 1024 * 1024
        total = os.path.getsize(path)
        part = 0
        with open(path, "rb") as fin:
            while True:
                data = fin.read(chunk)
                if not data:
                    break
                part += 1
                with open(f"{path}.part{part:03d}", "wb") as fout:
                    fout.write(data)
        print(c(f"  split into {part} parts", C.G))
    else:
        if not path or not os.path.isfile(path):
            print(c("  file not found", C.R))
            pause()
            return
        out = ask("output file", "joined.bin") or "joined.bin"
        parts = sorted([f for f in os.listdir(os.path.dirname(path))
                        if f.startswith(os.path.basename(path) + ".part")])
        with open(out, "wb") as fout:
            for p in parts:
                with open(os.path.join(os.path.dirname(path), p), "rb") as fin:
                    fout.write(fin.read())
        print(c(f"  joined {len(parts)} parts -> {out}", C.G))
    pause()


if __name__ == "__main__":
    run()
