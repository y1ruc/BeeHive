import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

import zipfile


def run():
    banner("ZIP TOOL")
    mode = ask("mode (zip/unzip)", "zip").lower()
    src = ask("source path", "")
    dst = ask("destination", "")

    try:
        if mode.startswith("z"):
            if not os.path.exists(src):
                print(c("  source not found", C.R))
                pause()
                return
            dst = dst or (src.rstrip("/\\") + ".zip")
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
                if os.path.isdir(src):
                    for root, _d, files in os.walk(src):
                        for f in files:
                            full = os.path.join(root, f)
                            z.write(full, os.path.relpath(full, src))
                else:
                    z.write(src, os.path.basename(src))
            print(c(f"  zipped -> {dst}", C.G))
        else:
            if not os.path.isfile(src):
                print(c("  archive not found", C.R))
                pause()
                return
            dst = dst or (src[:-4] if src.endswith(".zip") else src + "_extracted")
            with zipfile.ZipFile(src, "r") as z:
                z.extractall(dst)
            print(c(f"  extracted -> {dst}", C.G))
    except Exception as e:
        print(c(f"  failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
