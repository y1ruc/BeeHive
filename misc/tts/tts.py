import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import c, C, banner, ask, pause


def run():
    banner("TEXT TO SPEECH")
    text = ask("text to speak", "hello there") or "hello there"
    safe = text.replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Speech; "
          f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')")
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-Command", ps],
                         creationflags=0x08000000 if os.name == "nt" else 0)
        print(c("  speaking...", C.G))
    except Exception as e:
        print(c(f"  failed: {e}", C.R))
    pause()


if __name__ == "__main__":
    run()
