"""
BeeHive — honey-themed multi-tool launcher.

Run:  python beehive.py
"""

import asyncio
import datetime
import json
import os
import random
import re
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
for _cat in ("web", "network", "crypto", "pass", "discord", "files", "misc"):
    _catdir = os.path.join(ROOT, _cat)
    if os.path.isdir(_catdir):
        for _sub in sorted(os.listdir(_catdir)):
            _t = os.path.join(_catdir, _sub)
            if os.path.isdir(_t) and _t not in sys.path:
                sys.path.insert(0, _t)

from blooket_swarm import run_flood as blooket_flood, _enable_ansi
import kahoot
import swarm_core
import quizizz
import gimkit
import menti
import quizletlive
import portscan
import httpflood
import udpflood
import tcpflood
import ping
import dnslookup
import ipinfo
import subscan
import traceroute
import whois
import b64
import hexcode
import url
import htmlent
import rot
import vigenere
import xor
import atbash
import morse
import binary
import hasher
import hashcrack
import hmacgen
import aes
import uuidgen
import leet
import pwgen
import passphrase
import strength
import wordgen
import mutate
import pin
import webhook_send
import webhook_spam
import webhook_embed
import webhook_info
import webhook_delete
import token_info
import token_check
import token_guilds
import message_spam
import invite_resolver
import snowflake
import token_gen
import organizer
import renamer
import dupfinder
import filecrypt
import shredder
import splitter
import foldersize
import tree
import ziptool
import sysinfo
import filesearch
import emptyclean
import matrix
import fakebsod
import fakeupdate
import openurl
import tts
import asciiart
import qrgen
import dice
import randgen
import guess
import rps
import rainbow

WIDTH = 60

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "beehive.json")

DEFAULTS = {
    "concurrency": 8,
    "delay": 0.0,
    "name_mode": "prefix",   # prefix | random | file
    "name_prefix": "Bee",
    "name_file": "",
    "theme": "honey",
}

SETTINGS = dict(DEFAULTS)

_enable_ansi()


# ---- color -----------------------------------------------------------------

def c256(n):
    return f"\x1b[38;5;{n}m"


THEMES = {
    "honey": {
        "MG": c256(220),  "CY": c256(226),  "BL": c256(214),
        "GN": c256(82),   "YL": c256(230),  "RD": c256(196),
        "WH": c256(230),  "DM": c256(137),
        "GRAD": (c256(226), c256(220), c256(214), c256(208), c256(172)),
    },
    "cyber": {
        "MG": "\x1b[95m", "CY": "\x1b[96m", "BL": "\x1b[94m",
        "GN": "\x1b[92m", "YL": "\x1b[93m", "RD": "\x1b[91m",
        "WH": "\x1b[97m", "DM": "\x1b[90m",
        "GRAD": ("\x1b[96m", "\x1b[95m", "\x1b[94m", "\x1b[95m", "\x1b[96m"),
    },
    "venom": {
        "MG": "\x1b[92m", "CY": "\x1b[96m", "BL": "\x1b[32m",
        "GN": "\x1b[92m", "YL": "\x1b[93m", "RD": "\x1b[91m",
        "WH": "\x1b[97m", "DM": "\x1b[90m",
        "GRAD": ("\x1b[92m", "\x1b[32m", "\x1b[96m", "\x1b[32m", "\x1b[92m"),
    },
    "mono": {
        "MG": "\x1b[97m", "CY": "\x1b[37m", "BL": "\x1b[90m",
        "GN": "\x1b[97m", "YL": "\x1b[97m", "RD": "\x1b[37m",
        "WH": "\x1b[97m", "DM": "\x1b[90m",
        "GRAD": ("\x1b[97m", "\x1b[37m", "\x1b[90m", "\x1b[37m", "\x1b[97m"),
    },
}


class P:
    BG = "\x1b[40m"
    BD = "\x1b[1m"
    DI = "\x1b[2m"
    RST = "\x1b[0m"
    GRAD = THEMES["honey"]["GRAD"]

    MG = THEMES["honey"]["MG"]
    CY = THEMES["honey"]["CY"]
    BL = THEMES["honey"]["BL"]
    GN = THEMES["honey"]["GN"]
    YL = THEMES["honey"]["YL"]
    RD = THEMES["honey"]["RD"]
    WH = THEMES["honey"]["WH"]
    DM = THEMES["honey"]["DM"]

    @staticmethod
    def apply(name):
        t = THEMES.get(name, THEMES["honey"])
        for k, v in t.items():
            setattr(P, k, v)

    @staticmethod
    def grad(s, colors=None):
        colors = colors or P.GRAD
        return "".join(colors[i % len(colors)] + ch for i, ch in enumerate(s)) + P.RST


# ---- terminal helpers ------------------------------------------------------

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def vis_len(s):
    return len(_ANSI_RE.sub("", str(s)))


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def center(s, width=WIDTH, fill=" "):
    pad = max(0, width - vis_len(s))
    left = pad // 2
    return fill * left + s + fill * (pad - left)


def bar(char="─", color=None):
    return (color or P.DM) + char * WIDTH + P.RST


def rule(label="", color=None, fill="─"):
    color = color or P.DM
    if not label:
        return bar(fill, color)
    total = WIDTH - vis_len(label) - 2
    left = total // 2
    right = total - left
    return color + fill * left + " " + P.RST + label + color + " " + fill * right + P.RST


def panel(lines, border=None):
    border = border or P.MG
    top = "╭" + "─" * (WIDTH - 2) + "╮"
    bot = "╰" + "─" * (WIDTH - 2) + "╯"
    out = [border + top + P.RST]
    for ln in lines:
        s = str(ln)
        pad = max(0, WIDTH - 4 - vis_len(s))
        out.append(border + "│ " + s + " " * pad + " │" + P.RST)
    out.append(border + bot + P.RST)
    return "\n".join(out)


def kv(key, val, kc=None, vc=None):
    return f"{kc or P.DM}{key}{P.RST} {vc or P.CY}{val}{P.RST}"


# ---- honey motifs ----------------------------------------------------------

def hex_edge(color=None):
    return (color or P.BL) + ("╲╱" * (WIDTH // 2)) + P.RST


# ---- effects ---------------------------------------------------------------

def typewrite(text, delay=0.014, end="\n"):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


def spinner(label, seconds):
    glyphs = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write("\r  " + P.CY + glyphs[i % len(glyphs)] + P.RST + " " + label)
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    sys.stdout.write("\r" + " " * (vis_len(label) + 4) + "\r")
    sys.stdout.flush()


def flicker(text, cycles=3, dim=0.045, bright=0.03):
    lines = text.count("\n") + 1
    print(text)
    plain = _ANSI_RE.sub("", text)
    for _ in range(cycles):
        time.sleep(bright)
        sys.stdout.write("\x1b[%dA\r" % lines)
        sys.stdout.write(P.DM + plain + P.RST)
        sys.stdout.flush()
        time.sleep(dim)
        sys.stdout.write("\x1b[%dA\r" % lines)
        sys.stdout.write(text)
        sys.stdout.flush()
    sys.stdout.write("\n")


def glitch(s, p=0.07):
    chars = "▓▒░#*"
    out = []
    for ch in s:
        if ch != " " and random.random() < p:
            out.append(random.choice(chars))
        else:
            out.append(ch)
    return "".join(out)


def boot():
    clear()
    print()
    print()
    typewrite(P.MG + "  warming the hive" + P.RST + P.DI + " ..." + P.RST, 0.012)
    spinner("collecting nectar", 0.7)
    spinner("verifying routes", 0.7)
    spinner("waking worker bees", 0.7)
    clear()
    flicker(logo(), cycles=3)


# ---- logo ------------------------------------------------------------------

_GLYPHS = {
    "B": ["█████", "██ ██", "█████", "██ ██", "█████"],
    "E": ["█████", "██   ", "█████", "██   ", "█████"],
    "H": ["██ ██", "██ ██", "█████", "██ ██", "██ ██"],
    "I": ["█████", "  ██ ", "  ██ ", "  ██ ", "█████"],
    "V": ["██ ██", "██ ██", "██ ██", "██ ██", " ███ "],
}


def _row_color(r):
    g = P.GRAD
    return g[min(r, len(g) - 1)]


def logo(glitched=False):
    rows = []
    for r in range(5):
        line = " ".join(_GLYPHS[ch][r] for ch in "BEEHIVE")
        rows.append(center(_row_color(r) + line + P.RST))
    word = "B E E H I V E"
    if glitched:
        word = glitch(word)
    wordline = center(P.grad(word, (P.MG, P.CY, P.MG)))
    return "\n".join([wordline, "", "\n".join(rows)])


def status_line():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    left = kv("BEEHIVE", "ONLINE", kc=P.DM, vc=P.GN)
    mid = kv("conc", str(SETTINGS["concurrency"])) + "  " + \
          kv("names", SETTINGS["name_mode"]) + "  " + kv("theme", SETTINGS["theme"])
    right = kv("", now, kc=P.DM, vc=P.DM)
    return left + " " * max(1, WIDTH - vis_len(left) - vis_len(mid) - vis_len(right)) + mid + right


def header(glitch_logo=True):
    return "\n".join([
        hex_edge(P.BL),
        "",
        logo(glitched=glitch_logo),
        "",
        hex_edge(P.BL),
    ])


# ---- config ----------------------------------------------------------------

def load_config():
    global SETTINGS
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        for k in DEFAULTS:
            if k in d:
                SETTINGS[k] = d[k]
    except Exception:
        pass
    P.apply(SETTINGS["theme"])


def save_config():
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(SETTINGS, f, indent=2)
    except Exception:
        pass


# ---- naming ----------------------------------------------------------------

def resolve_names(raw):
    raw = (raw or "").strip()
    if raw == "":
        if SETTINGS["name_mode"] == "random":
            return {"mode": "random"}
        if SETTINGS["name_mode"] == "file" and SETTINGS.get("name_file"):
            return {"mode": "file", "path": SETTINGS["name_file"]}
        return {"mode": "prefix", "prefix": SETTINGS["name_prefix"]}
    if raw.lower() in ("r", "random"):
        return {"mode": "random"}
    if raw.lower().startswith("file:"):
        p = raw[5:].strip()
        if p:
            return {"mode": "file", "path": p}
        return {"mode": "prefix", "prefix": SETTINGS["name_prefix"]}
    if "," in raw:
        lst = [x.strip() for x in raw.split(",") if x.strip()]
        if lst:
            return {"mode": "list", "names": lst}
    return {"mode": "prefix", "prefix": raw}


# ---- flood tool ------------------------------------------------------------

def launch_flood(flood_fn, code_key, code_label, title, extra_flags=None):
    clear()
    print(status_line())
    print(header())
    print()
    typewrite(center(P.BD + P.MG + "▶ " + title + P.RST), 0.004)
    print()
    code = input(P.CY + f"  {code_label:<16}" + P.RST + P.DM + "[numeric] " + P.RST).strip()
    if not code.isdigit():
        print(P.RD + "  ! need a numeric code." + P.RST)
        _pause()
        return
    bots = _ask_int("bots", 25, 1, 5000)
    concurrency = _ask_int("concurrency", SETTINGS["concurrency"], 1, 64)
    name = input(P.CY + "  names            " + P.RST +
                 P.DM + f"[{SETTINGS['name_prefix']}] " + P.RST).strip()

    n = resolve_names(name)
    if n["mode"] == "prefix":
        nlabel = f"{n['prefix']}*"
    elif n["mode"] == "random":
        nlabel = "random"
    elif n["mode"] == "file":
        nlabel = f"file:{n['path']}"
    else:
        nlabel = ", ".join(n["names"][:4]) + ("…" if len(n["names"]) > 4 else "")

    kwargs = {code_key: code, "bots": bots, "concurrency": concurrency,
              "delay": SETTINGS["delay"], "bar": True}
    if n["mode"] == "random":
        kwargs["use_random"] = True
    elif n["mode"] == "file":
        kwargs["name_file"] = n["path"]
    elif n["mode"] == "list":
        kwargs["name_list"] = n["names"]
    else:
        kwargs["prefix"] = n["prefix"]

    extra = {}
    if extra_flags:
        for key, prompt in extra_flags:
            v = input(P.YL + f"  {prompt:<32}" + P.RST + P.DM + "[y/N] " + P.RST).strip().lower()
            extra[key] = v in ("y", "yes")
    kwargs.update(extra)

    rows = [
        kv("TARGET", code, vc=P.MG),
        kv("BOTS", str(bots), vc=P.MG),
        kv("CONCURRENCY", str(concurrency), vc=P.MG),
        kv("NAMES", nlabel, vc=P.MG),
    ]
    rows += [kv(k.upper(), "yes" if v else "no", vc=P.MG) for k, v in extra.items()]

    print()
    print(panel(rows, border=P.MG))
    print()
    go = input(P.YL + "  launch? [Y/n]   " + P.RST + P.DM + "[y] " + P.RST).strip()
    if go and go.lower() not in ("y", "yes"):
        return

    print()
    typewrite(P.CY + "  > waking the swarm" + P.RST + P.DI + " ..." + P.RST, 0.01)
    spinner("deploying workers", 0.9)
    print()
    print(rule(P.grad(" SWARM DEPLOYED ")))
    try:
        asyncio.run(flood_fn(**kwargs))
    except KeyboardInterrupt:
        pass
    print(rule(P.grad(" SWARM TERMINATED ")))
    _pause()


def tool_blooket():
    launch_flood(blooket_flood, "code", "game code", "BLOOKET SWARM")


def tool_kahoot():
    launch_flood(kahoot.run_flood, "pin", "game pin", "KAHOOT FLOOD",
                 extra_flags=[("answer", "auto-answer questions?")])


def site_flood(join_one):
    async def _run(**kw):
        return await swarm_core.run_flood(join_one, **kw)
    return _run


def tool_quizizz():
    launch_flood(site_flood(quizizz.join_one), "code", "game code", "QUIZIZZ FLOOD")


def tool_gimkit():
    launch_flood(site_flood(gimkit.join_one), "code", "game code", "GIMKIT FLOOD")


def tool_menti():
    launch_flood(site_flood(menti.join_one), "code", "game code", "MENTI FLOOD")


def tool_quizlet():
    launch_flood(site_flood(quizletlive.join_one), "code", "game code", "QUIZLET LIVE FLOOD")


# ---- categories ------------------------------------------------------------

CATEGORIES = [
    ("web",     "Web Bots & Nukers",    P.MG, "◈", "flood classroom games with bots"),
    ("network", "Network & DoS",        P.CY, "⌁", "scanners · floods · ip tools"),
    ("crypto",  "Crypto & Encoding",    P.GN, "⬢", "hash · encode · decode"),
    ("pass",    "Passwords & Wordlists", P.YL, "◉", "generate · analyze"),
    ("discord", "Discord",              P.BL, "◆", "webhooks · tools"),
    ("files",   "Files & System",       P.WH, "▤", "file & system utilities"),
    ("misc",    "Misc & Prank",         P.RD, "✦", "everything else"),
]

TOOLS = {
    "web": [
        ("Blooket Swarm", "flood a blooket lobby", tool_blooket),
        ("Kahoot Flooder", "flood a kahoot lobby", tool_kahoot),
        ("Quizizz Flooder", "flood a quizizz lobby", tool_quizizz),
        ("Gimkit Flooder", "flood a gimkit lobby", tool_gimkit),
        ("Mentimeter Flooder", "flood a menti lobby", tool_menti),
        ("Quizlet Live Flooder", "flood a quizlet live", tool_quizlet),
    ],
    "network": [
        ("Port Scanner", "scan a host for open ports", portscan.run),
        ("HTTP Flood", "flood a url with requests", httpflood.run),
        ("UDP Flood", "blast udp packets", udpflood.run),
        ("TCP Flood", "spam tcp connections", tcpflood.run),
        ("Ping", "latency to a host", ping.run),
        ("DNS Lookup", "a/mx/ns/txt records", dnslookup.run),
        ("IP Info", "geolocate an ip/domain", ipinfo.run),
        ("Subdomain Scan", "brute common subdomains", subscan.run),
        ("Traceroute", "trace the route", traceroute.run),
        ("WHOIS", "domain registration", whois.run),
    ],
    "crypto": [
        ("Base64", "base64/32/16/85 codec", b64.run),
        ("Hex", "text <-> hex", hexcode.run),
        ("URL Encode", "url encode/decode", url.run),
        ("HTML Entities", "html encode/decode", htmlent.run),
        ("ROT / Caesar", "rotate letters", rot.run),
        ("Vigenere", "vigenere cipher", vigenere.run),
        ("XOR Cipher", "xor with key", xor.run),
        ("Atbash", "atbash cipher", atbash.run),
        ("Morse Code", "text <-> morse", morse.run),
        ("Binary / Octal", "text <-> binary", binary.run),
        ("Hash Calculator", "md5/sha/blake of text/file", hasher.run),
        ("Hash Cracker", "crack md5/sha hashes", hashcrack.run),
        ("HMAC", "hmac of a message", hmacgen.run),
        ("AES Encrypt", "aes-gcm encrypt/decrypt", aes.run),
        ("UUID Gen", "generate uuids", uuidgen.run),
        ("Leetspeak", "text <-> leet", leet.run),
    ],
    "pass": [
        ("Password Gen", "secure random passwords", pwgen.run),
        ("Passphrase", "diceware-style phrases", passphrase.run),
        ("Strength Check", "entropy + crack time", strength.run),
        ("Wordlist Gen", "brute-force wordlists", wordgen.run),
        ("Wordlist Mutate", "leet/case/number variants", mutate.run),
        ("PIN Gen", "random numeric pins", pin.run),
    ],
    "discord": [
        ("Webhook Send", "post a message", webhook_send.run),
        ("Webhook Spam", "spam messages", webhook_spam.run),
        ("Webhook Embed", "send an embed", webhook_embed.run),
        ("Webhook Info", "get webhook details", webhook_info.run),
        ("Webhook Delete", "nuke a webhook", webhook_delete.run),
        ("Token Info", "user info from token", token_info.run),
        ("Token Checker", "validate tokens", token_check.run),
        ("Token Guilds", "list guilds of a token", token_guilds.run),
        ("Channel Spammer", "spam a channel (token)", message_spam.run),
        ("Invite Resolver", "resolve an invite", invite_resolver.run),
        ("Snowflake Decoder", "decode snowflake ids", snowflake.run),
        ("Token Generator", "generate format tokens", token_gen.run),
    ],
    "files": [
        ("File Organizer", "sort files by extension", organizer.run),
        ("Batch Renamer", "prefix/suffix/find-replace", renamer.run),
        ("Duplicate Finder", "find dups by hash", dupfinder.run),
        ("File Encrypt", "aes-gcm encrypt files", filecrypt.run),
        ("File Shredder", "overwrite + delete", shredder.run),
        ("File Splitter", "split/join files", splitter.run),
        ("Folder Size", "compute folder size", foldersize.run),
        ("Directory Tree", "print a tree", tree.run),
        ("Zip Tool", "zip/unzip", ziptool.run),
        ("System Info", "os/cpu/ram/disk", sysinfo.run),
        ("File Search", "find by name/content", filesearch.run),
        ("Empty Folder Cleaner", "remove empty dirs", emptyclean.run),
    ],
    "misc": [
        ("Matrix Rain", "green falling code", matrix.run),
        ("Fake Blue Screen", "prank bsod", fakebsod.run),
        ("Fake Update", "prank windows update", fakeupdate.run),
        ("Open URL", "open a url / rickroll", openurl.run),
        ("Text to Speech", "speak text aloud", tts.run),
        ("ASCII Art", "text -> figlet art", asciiart.run),
        ("QR Code", "generate a qr code", qrgen.run),
        ("Dice Roller", "dice + coin flips", dice.run),
        ("Random Generator", "numbers/pick/shuffle", randgen.run),
        ("Guess the Number", "mini game", guess.run),
        ("Rock Paper Scissors", "mini game", rps.run),
        ("Rainbow Text", "rainbow output", rainbow.run),
    ],
}


def category_screen(cat_id, name, color, icon, desc):
    tools = TOOLS.get(cat_id, [])
    while True:
        clear()
        print(status_line())
        print(bar())
        print(center(color + P.BD + f"{icon} {name}" + P.RST))
        print(center(P.DM + desc))
        print(bar())
        print()
        if tools:
            for i, (tname, tdesc, _) in enumerate(tools, 1):
                print(color + f"  [{i}] " + P.RST + color + P.BD + tname.ljust(16) + P.RST +
                      P.DM + "· " + tdesc + P.RST)
        else:
            print(center(P.DM + "( nothing here yet — coming soon )"))
        print()
        print(P.DM + "  [0]  back" + P.RST)
        print()
        ch = _ask_str("select", "0")
        if ch == "0":
            return
        if tools and ch.isdigit() and 1 <= int(ch) <= len(tools):
            tools[int(ch) - 1][2]()


# ---- screens ---------------------------------------------------------------

def settings_screen():
    while True:
        clear()
        print(status_line())
        print(bar())
        print(center(P.BD + P.CY + "◆ SETTINGS" + P.RST))
        print(bar())
        print()
        rows = [
            ("1", "theme", f"honey/cyber/venom/mono  [{SETTINGS['theme']}]"),
            ("2", "concurrency", str(SETTINGS["concurrency"])),
            ("3", "join delay", f"{SETTINGS['delay']}s"),
            ("4", "name mode", f"prefix/random/file  [{SETTINGS['name_mode']}]"),
            ("5", "name prefix", SETTINGS["name_prefix"]),
            ("6", "name file", SETTINGS["name_file"] or "(none)"),
        ]
        for num, label, val in rows:
            print(P.CY + f"  [{num}] " + P.RST + P.DM + f"{label:<13}" + P.RST + P.WH + val + P.RST)
        print()
        print(P.DM + "  [0]  back & save" + P.RST)
        print()
        ch = _ask_str("select", "0")
        if ch == "0":
            save_config()
            return
        if ch == "1":
            v = input(P.CY + "  theme (honey/cyber/venom/mono)  " + P.RST +
                      P.DM + f"[{SETTINGS['theme']}] " + P.RST).strip().lower()
            if v in THEMES:
                SETTINGS["theme"] = v
                P.apply(v)
        elif ch == "2":
            SETTINGS["concurrency"] = _ask_int("concurrency", SETTINGS["concurrency"], 1, 64)
        elif ch == "3":
            v = input(P.CY + "  delay seconds  " + P.RST +
                      P.DM + f"[{SETTINGS['delay']}] " + P.RST).strip()
            try:
                SETTINGS["delay"] = float(v) if v else 0.0
            except ValueError:
                pass
        elif ch == "4":
            v = input(P.CY + "  mode (prefix/random/file)  " + P.RST +
                      P.DM + f"[{SETTINGS['name_mode']}] " + P.RST).strip().lower()
            if v in ("prefix", "random", "file"):
                SETTINGS["name_mode"] = v
        elif ch == "5":
            v = input(P.CY + "  prefix  " + P.RST +
                      P.DM + f"[{SETTINGS['name_prefix']}] " + P.RST).strip()
            if v:
                SETTINGS["name_prefix"] = v[:12]
        elif ch == "6":
            v = input(P.CY + "  name file path  " + P.RST +
                      P.DM + f"[{SETTINGS['name_file'] or 'none'}] " + P.RST).strip()
            SETTINGS["name_file"] = v


def about_screen():
    clear()
    print(status_line())
    print(bar())
    print(center(P.BD + P.MG + "◆ ABOUT" + P.RST))
    print(bar())
    print()
    print(panel([
        "",
        center(P.grad("BEEHIVE")),
        center(P.DM + "multi-tool launcher"),
        "",
        kv("ENGINE", "Playwright · Chromium"),
        kv("CATEGORIES", str(len(CATEGORIES))),
        kv("TOOLS", str(sum(len(v) for v in TOOLS.values()))),
        kv("EVASION", "headful, off-screen"),
        "",
    ], border=P.MG))
    print()
    _pause()


# ---- input helpers ---------------------------------------------------------

def _ask_int(label, default, lo, hi):
    while True:
        v = input(P.CY + f"  {label:<16}" + P.RST + P.DM + f"[{default}] " + P.RST).strip()
        if v == "":
            return default
        try:
            n = int(v)
            if lo <= n <= hi:
                return n
        except ValueError:
            pass
        print(P.RD + "  ! out of range, try again" + P.RST)


def _ask_str(label, default):
    return input(P.CY + f"  {label:<16}" + P.RST + P.DM + f"[{default}] " + P.RST).strip()


def _pause():
    input(P.DM + "  press ENTER to return" + P.RST)


# ---- main menu -------------------------------------------------------------

def menu():
    while True:
        clear()
        print(status_line())
        print(header())
        print()
        for i, (cid, name, color, icon, desc) in enumerate(CATEGORIES, 1):
            print(color + f"  [{i}] " + P.RST + color + P.BD + name.ljust(21) + P.RST +
                  P.DM + "· " + desc + P.RST)
        print()
        print(P.CY + "  [S] " + P.RST + P.CY + P.BD + "SETTINGS" + P.RST + P.DM + " · theme, speed & names" + P.RST)
        print(P.MG + "  [A] " + P.RST + P.MG + P.BD + "ABOUT" + P.RST + P.DM + " · what this is" + P.RST)
        print(P.RD + "  [0] " + P.RST + P.RD + P.BD + "QUIT" + P.RST + P.DM + " · exit" + P.RST)
        print()
        ch = input(P.grad("  HIVE") + P.RST + P.MG + " " + "\x1b[5m▸\x1b[25m " + P.RST).strip()
        if ch.isdigit():
            i = int(ch)
            if 1 <= i <= len(CATEGORIES):
                cid, name, color, icon, desc = CATEGORIES[i - 1]
                category_screen(cid, name, color, icon, desc)
            elif i == 0:
                break
        elif ch.lower() == "s":
            settings_screen()
        elif ch.lower() == "a":
            about_screen()
        elif ch.lower() in ("q", "x"):
            break
    clear()
    print(P.MG + "  ▓▒░ hive offline." + P.RST)
    sys.exit(0)


if __name__ == "__main__":
    try:
        load_config()
        boot()
        menu()
    except (KeyboardInterrupt, EOFError):
        print()
        print(P.MG + "  ▓▒░ hive offline." + P.RST)
        sys.exit(0)
