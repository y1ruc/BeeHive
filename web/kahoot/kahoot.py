"""
Kahoot flooder — drives the kahoot.it join flow with a headful, off-screen
Chromium. One tab per bot: game PIN -> nickname -> waiting room. Bots hold
their session open as long as their tab stays alive.

Usage:
    python kahoot.py --code 1234567 --bots 25
    python kahoot.py --code 1234567 --bots 50 --name jeff --concurrency 8
    python kahoot.py --code 1234567 --bots 30 --name-file names.txt
    python kahoot.py --code 1234567 --bots 40 --random
"""

import argparse
import asyncio
import os
import random
import re
import signal
import string
import sys
import threading

from playwright.async_api import async_playwright

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)

JOIN_URL = "https://kahoot.it/"

STEALTH = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
window.chrome = window.chrome || { runtime: {}, loadTimes: function(){}, csi: function(){} };
const _q = navigator.permissions && navigator.permissions.query;
if (_q) {
  navigator.permissions.query = (p) => p && p.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : _q(p);
}
"""

ERROR_MARKERS = (
    "not found",
    "doesn't exist",
    "doesn’t exist",
    "didn't recognize",
    "didn’t recognize",
    "recognize that game",
    "no game",
    "incorrect",
    "has ended",
    "ended",
)

SYL = ("ka", "bo", "za", "lu", "mi", "go", "ra", "te", "vi", "no",
       "si", "da", "fu", "pe", "xo", "wu", "qi", "je", "ha", "mo")


# ---- ANSI -----------------------------------------------------------------

def _enable_ansi():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if k.GetConsoleMode(h, ctypes.byref(mode)):
                k.SetConsoleMode(h, mode.value | 0x0004)
        except Exception:
            pass
        try:
            os.system("chcp 65001 > nul")
        except Exception:
            pass
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


class C:
    R = "\x1b[31m"
    G = "\x1b[32m"
    Y = "\x1b[33m"
    B = "\x1b[34m"
    M = "\x1b[35m"
    CY = "\x1b[36m"
    W = "\x1b[37m"
    GRAY = "\x1b[90m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    UND = "\x1b[4m"
    RST = "\x1b[0m"


def c(t, *codes):
    return "".join(codes) + t + C.RST


# ---- naming ---------------------------------------------------------------

def random_name():
    n = random.randint(2, 3)
    return "".join(random.choice(SYL) for _ in range(n)).title()


def build_names(bots, prefix="", name_file="", use_random=False, name_list=None):
    if name_list:
        raw = [s.strip() for s in name_list if s.strip()]
        if raw:
            names = []
            for i in range(bots):
                base = raw[i % len(raw)]
                names.append(base[:15] if i < len(raw) else f"{base[:12]}{i - len(raw) + 1}")
            return names

    if name_file:
        with open(name_file, "r", encoding="utf-8") as f:
            raw = [ln.strip() for ln in f if ln.strip()]
        if not raw:
            raise SystemExit("[!] name file is empty")
        names = []
        for i in range(bots):
            base = raw[i % len(raw)]
            names.append(base[:15] if i < len(raw) else f"{base[:12]}{i - len(raw) + 1}")
        return names

    if use_random:
        seen = set()
        out = []
        for _ in range(bots):
            n = random_name()
            while n in seen:
                n = random_name() + str(random.randint(10, 99))
            seen.add(n)
            out.append(n[:15])
        return out

    prefix = (prefix or "Bot")[:12]
    names = []
    for i in range(bots):
        tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        names.append(f"{prefix}{i}{tag}"[:15])
    return names


# ---- page driving ---------------------------------------------------------

async def dismiss_cookies(page):
    for label in ("Accept all cookies", "Accept all", "Allow all", "Accept All",
                  "I'm ok with cookies"):
        btn = page.get_by_role("button", name=label)
        try:
            if await btn.count():
                await btn.first.click(timeout=1500)
                return
        except Exception:
            continue


async def goto_pin(page, attempts=3):
    for a in range(attempts):
        try:
            await page.goto(JOIN_URL, wait_until="domcontentloaded", timeout=60000)
            for _ in range(80):
                if await page.query_selector("input[name='gameId']"):
                    return True
                await asyncio.sleep(0.25)
            return False
        except Exception:
            if a == attempts - 1:
                return False
            await asyncio.sleep(0.8)
    return False


async def join_one(page, pin, name):
    """Drive one page: PIN -> nickname -> waiting room. Returns (ok, detail)."""
    try:
        if not await goto_pin(page):
            return False, "pin screen not loaded"
        await dismiss_cookies(page)

        await page.fill("input[name='gameId']", pin)
        await page.click("button[data-functional-selector='join-game-pin']")

        # Either the nickname form appears directly, or Kahoot shows a
        # "Back in action?" resume prompt for a previously-seen browser.
        for _ in range(80):
            if await page.query_selector("input[name='nickname']"):
                break
            resume = page.get_by_role("button", name="Join as new participant")
            if await resume.count():
                try:
                    await resume.first.click(timeout=2000)
                except Exception:
                    pass
            await asyncio.sleep(0.25)
        else:
            body = await page.inner_text("body")
            for m in ERROR_MARKERS:
                if m in body.lower():
                    return False, f"pin rejected: {m}"
            return False, "no nickname form"

        await dismiss_cookies(page)

        try:
            await page.fill("input[name='nickname']", name, timeout=4000)
        except Exception:
            pass  # readonly random-name mode -> use the generated name

        await page.click("button[data-functional-selector='join-button-username']")

        # Nickname form tears down -> "You're in!" + avatar/character select.
        try:
            await page.wait_for_selector("input[name='nickname']", state="detached", timeout=25000)
        except Exception:
            body = await page.inner_text("body")
            if "taken" in body.lower() or "in use" in body.lower():
                return False, "nickname taken"

        # Avatar/character step is cosmetic; complete it only if it's enabled.
        done = page.get_by_role("button", name="Done")
        if await done.count() and not await done.is_disabled():
            try:
                await done.click(timeout=3000)
            except Exception:
                pass
        return True, "waiting room"
    except Exception as e:
        return False, f"error: {type(e).__name__}: {e}"


# ---- core -----------------------------------------------------------------

BLOCK_PATTERNS = [
    re.compile(r"\.(png|jpe?g|gif|webp|svg|ico)(\?|$)", re.I),
    re.compile(r"\.(woff2?|ttf|otf|eot)(\?|$)", re.I),
    re.compile(r"\.(mp3|ogg|wav|m4a)(\?|$)", re.I),
    re.compile(r"(amplitude|googletagmanager|google-analytics|cookieyes|sentry|hotjar|doubleclick)", re.I),
]


async def _route_handler(route):
    u = route.request.url
    for pat in BLOCK_PATTERNS:
        if pat.search(u):
            await route.abort()
            return
    await route.continue_()


def parse_proxy(s):
    m = re.match(r"(?:(\w+)://)?(?:(.+?):(.+?)@)?([^:]+):(\d+)/?$", s.strip())
    if not m:
        return None
    scheme, user, pw, host, port = m.groups()
    server = f"{scheme or 'http'}://{host}:{port}"
    out = {"server": server}
    if user:
        out["username"] = user
        out["password"] = pw or ""
    return out


def load_proxies(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]


async def auto_answer(page, stop):
    """Click a random answer every time answer buttons appear. Runs until stop."""
    answered = False
    while not stop.is_set():
        try:
            btns = page.locator("[data-functional-selector^='answer-']:visible")
            n = await btns.count()
            if n > 0 and not answered:
                await btns.nth(random.randint(0, n - 1)).click(timeout=1500)
                answered = True
            elif n == 0:
                answered = False
        except Exception:
            pass
        await asyncio.sleep(0.25)


async def run_flood(pin, bots=10, prefix="", name_file="", use_random=False,
                    name_list=None, delay=0.0, concurrency=6, visible=False,
                    headless=False, quiet=False, bar=False, answer=False,
                    proxy_file="", block=True):
    pin = pin.strip()
    if not pin.isdigit():
        print(c(f"[!] pin looks wrong: {pin!r}", C.R))

    names = build_names(bots, prefix, name_file, use_random, name_list)

    proxies = load_proxies(proxy_file) if proxy_file else []

    async with async_playwright() as p:
        launch_args = ["--disable-blink-features=AutomationControlled"]
        if not visible and not headless:
            launch_args.append("--window-position=-32000,-32000")

        browser = await p.chromium.launch(headless=headless, args=launch_args)

        # Warmup throwaway context to confirm reachability.
        warm = await browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 800})
        await warm.add_init_script(STEALTH)
        wp = await warm.new_page()
        if not await goto_pin(wp):
            print(c("[!] warmup never reached the pin screen", C.Y))
        await dismiss_cookies(wp)
        await wp.wait_for_timeout(1500)
        await warm.close()

        sem = asyncio.Semaphore(concurrency)
        lock = asyncio.Lock()
        joined = 0
        total = len(names)
        answer_tasks = []
        stop = asyncio.Event()

        def bar_line(done):
            ratio = done / total if total else 0
            width = 44
            filled = round(width * ratio)
            b = C.G + "█" * filled + C.GRAY + "░" * (width - filled) + C.RST
            return f"  {b}  {C.CY}{done}/{total}{C.RST} joined"

        async def worker(idx, name):
            nonlocal joined
            async with sem:
                # Each bot gets its own isolated browser context so Kahoot sees
                # distinct sessions instead of one shared device.
                opts = {"user_agent": UA, "viewport": {"width": 1280, "height": 800}}
                if proxies:
                    opts["proxy"] = parse_proxy(proxies[idx % len(proxies)])
                ctx = await browser.new_context(**opts)
                await ctx.add_init_script(STEALTH)
                if block:
                    await ctx.route("**/*", _route_handler)
                page = await ctx.new_page()
                ok, detail = await join_one(page, pin, name)
                if not ok:
                    await ctx.close()
                else:
                    if answer:
                        answer_tasks.append(asyncio.create_task(auto_answer(page, stop)))
                async with lock:
                    joined += ok
                    if bar:
                        sys.stdout.write("\r" + bar_line(joined))
                        sys.stdout.flush()
                    elif ok:
                        print(c(f"  [+] bot {idx:>3} '{name}' joined", C.G))
                    else:
                        print(c(f"  [-] bot {idx:>3} '{name}' failed: {detail}", C.R))

        mode = "headless" if headless else "stealth" if not visible else "visible"
        print(c(f"[*] pin {pin}  ·  {bots} bots  ·  concurrency {concurrency}  ·  mode {mode}",
                C.CY))

        tasks = [asyncio.create_task(worker(i, name)) for i, name in enumerate(names)]
        await asyncio.gather(*tasks)

        if bar:
            sys.stdout.write("\r" + bar_line(joined) + "\n")
            sys.stdout.flush()
        print(c(f"[*] {joined}/{bots} joined, parked in waiting room.", C.G if joined else C.Y))

        loop = asyncio.get_running_loop()

        def _sig(*_):
            stop.set()

        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, _sig)
            except NotImplementedError:
                pass

        if sys.stdin.isatty() and not quiet:
            print(c("      press ENTER to disconnect all bots and return", C.DIM))

            def _reader():
                try:
                    input()
                except Exception:
                    pass
                loop.call_soon_threadsafe(stop.set)

            threading.Thread(target=_reader, daemon=True).start()
        else:
            print(c("      Ctrl+C to disconnect all bots and close the browser.", C.DIM))

        await stop.wait()
        for t in answer_tasks:
            t.cancel()
        await browser.close()
    return joined


async def main():
    ap = argparse.ArgumentParser(description="Kahoot lobby flooder")
    ap.add_argument("--code", required=True, help="game pin, e.g. 1234567")
    ap.add_argument("--bots", type=int, default=10, help="number of bots")
    ap.add_argument("--name", default="", help="name prefix")
    ap.add_argument("--name-file", default="", help="file of names, one per line")
    ap.add_argument("--random", action="store_true", help="random pronounceable names")
    ap.add_argument("--delay", type=float, default=0.0, help="extra seconds between bot starts")
    ap.add_argument("--concurrency", type=int, default=6, help="parallel joins")
    ap.add_argument("--visible", action="store_true", help="show the browser window")
    ap.add_argument("--headless", action="store_true", help="true headless (likely blocked)")
    ap.add_argument("--answer", action="store_true", help="bots answer questions (random choice)")
    ap.add_argument("--proxy-file", default="", help="file of proxies (one per line, round-robin)")
    ap.add_argument("--no-block", action="store_true", help="don't block images/fonts/tracking")
    args = ap.parse_args()

    _enable_ansi()
    await run_flood(
        pin=args.code, bots=args.bots, prefix=args.name, name_file=args.name_file,
        use_random=args.random, delay=args.delay, concurrency=args.concurrency,
        visible=args.visible, headless=args.headless, answer=args.answer,
        proxy_file=args.proxy_file, block=not args.no_block,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
