import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

LEET = str.maketrans("aegiost", "4631057")
SUFFIXES = ("1", "12", "123", "1234", "12345", "2024", "2025", "2026",
            "!", "!!", "123!", "@", "#", "_", "69", "007", "000", "x")


def mutate(word):
    out = set()
    for base in (word, word.lower(), word.upper(), word.capitalize()):
        out.add(base)
        out.add(base.translate(LEET))
        out.add(base[::-1])
    for v in list(out):
        for s in SUFFIXES:
            out.add(v + s)
            out.add(s + v)
    return sorted(out)


def run():
    banner("WORDLIST MUTATOR")
    words = ask("base words (comma separated)", "password")
    if not words:
        pause()
        return
    bases = [w.strip() for w in words.split(",") if w.strip()]

    variants = []
    for b in bases:
        variants.extend(mutate(b))

    print(c(f"  {len(variants)} variants from {len(bases)} base word(s)", C.CY))
    save = ask("save to file? (blank = just show)", "").strip()
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write("\n".join(variants) + "\n")
        print(c(f"  wrote {len(variants)} to {save}", C.G))
    else:
        for v in variants:
            print("  " + c(v, C.W))
    pause()


if __name__ == "__main__":
    run()
