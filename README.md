# BeeHive

Honey-themed multi-tool launcher for classroom game flooding and assorted
tools. Run it and pick a category, then a tool.

```
python beehive.py
```

## GUI

A modern PySide6 GUI is included. It keeps the honey/hex aesthetic, adds a
category sidebar, searchable tool grid, resizable output console, and global
settings editor.

```
python gui.py
```

The GUI runs every tool through the same backends as the CLI. Tools that ask
for input in the terminal will pop a small dialog inside the GUI instead.

## Layout

```
beehive.py            CLI launcher (entry point)
gui.py                GUI launcher
gui/                  PySide6 GUI package
  app.py              QApplication entry
  main_window.py      main window + routing
  components.py       reusable widgets
  forms.py            dedicated tool forms
  runners.py          tool execution layer
  theme.py            honey/cyber/venom/mono themes
beehive.json          persisted settings (theme, concurrency, naming)
requirements.txt      Python dependencies
swarm_core.py         shared flood engine (browser, stealth, proxies, blocking)
web/                  Web Bots & Nukers
network/              Network & DoS
crypto/               Crypto & Encoding
pass/                 Passwords & Wordlists
discord/              Discord
files/                Files & System
misc/                 Misc & Prank
```

Each tool lives in its own folder under its category. `swarm_core.run_flood`
is the shared engine — a new site driver just implements `join_one(page, code,
name)` and everything else (contexts, stealth, request blocking, proxies,
auto-answer, naming, progress) comes free.

## Requirements

- Python 3.9+
- Playwright + Chromium (for web flood tools)
- PySide6 (for the GUI)

```
pip install -r requirements.txt
python -m playwright install chromium
```

## Notes

- Game codes are transient — the game has to be live on the host side.
- Runs real Chromium headful but parked off-screen; headless trips the sites'
  anti-bot checks.
- Blooket and Kahoot are verified end to end. Quizizz/Gimkit/Menti/Quizlet have
  their code-entry selectors verified; the name-entry step is best-effort until
  it's tested against a live game.
