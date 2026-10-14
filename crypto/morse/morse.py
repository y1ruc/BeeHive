import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    " ": "/",
}
REV = {v: k for k, v in MORSE.items()}


def run():
    banner("MORSE CODE")
    mode = ask("mode (e/d)", "e").lower() or "e"
    text = ask("input", "")
    if not text:
        pause()
        return
    try:
        if mode.startswith("e"):
            out = " ".join(MORSE.get(ch.upper(), ch) for ch in text)
        else:
            out = "".join(REV.get(s, s) for s in text.replace("  ", " / ").split())
        print(c(out, C.G))
    except Exception as e:
        print(c(f"  error: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
