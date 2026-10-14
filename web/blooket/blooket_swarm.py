"""
Blooket Swarm — client replicator / lobby flooder.

Opens one real browser tab per bot and drives each through Blooket's exact
join flow: game code (prefilled via ?id=) -> nickname -> lobby. Bots hold
their websocket session open for as long as their tab stays alive.

Cloudflare notes
----------------
Blooket's join is a Next.js server action. The GET page loads under headless,
but the POST that actually joins is 403'd by Cloudflare — true headless is
detected and blocked even with a stealth patch. The workaround: run the real
Chromium headful but parked off-screen (-32000,-32000), so there is no visible
window yet Cloudflare sees a normal browser. That is the default. Use
--visible to debug, --headless only if you want to confirm it gets 403'd.

Usage:
    python blooket_swarm.py --code 400621 --bots 25
    python blooket_swarm.py --code 400621 --bots 50 --name jeff --concurrency 8
    python blooket_swarm.py --code 400621 --bots 30 --name-file names.txt
    python blooket_swarm.py --code 400621 --bots 40 --random

    # styled interactive menu
    python menu.py
"""

import argparse
import asyncio
import os
import random
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

JOIN_URL = "https://play.blooket.com/play"

ERROR_MARKERS = (
    "Invalid game ID",
    "game is full",
    "Game is full",
    "has ended",
    "This game has ended",
    "try again",
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
    for label in ("Accept All", "Accept all"):
        btn = page.get_by_role("button", name=label)
        try:
            if await btn.count():
                await btn.first.click(timeout=3000)
                break
        except Exception:
            continue
    for _ in range(20):
        if not await page.get_by_role("button", name="Accept All").count():
            return
        await asyncio.sleep(0.25)


async def goto_join(page, code, attempts=3):
    """Navigate to ?id=<code>. A live code renders the nickname form directly;
    a dead code renders the join-code form. Return True once either is ready."""
    for a in range(attempts):
        try:
            await page.goto(f"{JOIN_URL}?id={code}", wait_until="domcontentloaded", timeout=60000)
            for _ in range(60):
                if await page.query_selector("input[name='join-code'], input[name='gamer']"):
                    return True
                await asyncio.sleep(0.5)
            return False
        except Exception:
            if a == attempts - 1:
                return False
            await asyncio.sleep(1.2)
    return False


async def join_one(page, code, name):
    """Drive one page: prefilled code -> nickname -> lobby. Returns (ok, detail)."""
    try:
        if not await goto_join(page, code):
            return False, "page load blocked (challenge)"
        await dismiss_cookies(page)

        if await page.query_selector("input[name='gamer']") is None:
            await page.click("button[type='submit']")
            try:
                await page.wait_for_selector("input[name='gamer']", timeout=20000)
            except Exception:
                body = await page.inner_text("body")
                for m in ERROR_MARKERS:
                    if m in body:
                        return False, f"rejected: {m.strip()}"
                return False, "code not accepted (no nickname form)"

        gamer = page.locator("input[name='gamer']")
        if await gamer.is_editable():
            await gamer.fill(name)

        before = page.url
        await page.click("button[type='submit']")

        try:
            await page.wait_for_url(lambda u: u != before, timeout=20000)
            return True, page.url
        except Exception:
            body = await page.inner_text("body")
            for m in ERROR_MARKERS:
                if m in body:
                    return False, f"rejected: {m.strip()}"
            return False, "no redirect after nickname"
    except Exception as e:
        return False, f"error: {type(e).__name__}: {e}"


# ---- core -----------------------------------------------------------------

async def run_flood(code, bots=10, prefix="", name_file="", use_random=False,
                    name_list=None, delay=0.0, concurrency=4, visible=False,
                    headless=False, quiet=False, bar=False):
    """Launch the swarm. Blocks until stopped (ENTER or Ctrl+C). Returns joined count."""
    code = code.strip()
    if not code.isdigit():
        print(c(f"[!] code looks wrong: {code!r}", C.R))

    names = build_names(bots, prefix, name_file, use_random, name_list)

    async with async_playwright() as p:
        launch_args = ["--disable-blink-features=AutomationControlled"]
        if not visible and not headless:
            launch_args.append("--window-position=-32000,-32000")

        browser = await p.chromium.launch(headless=headless, args=launch_args)
        ctx = await browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 800})

        warm = await ctx.new_page()
        if not await goto_join(warm, code):
            print(c("[!] warmup page never reached the join form (Cloudflare?)", C.Y))
        await dismiss_cookies(warm)
        await warm.wait_for_timeout(2000)
        await warm.close()

        sem = asyncio.Semaphore(concurrency)
        lock = asyncio.Lock()
        joined = 0
        total = len(names)

        def bar_line(done):
            ratio = done / total if total else 0
            width = 44
            filled = round(width * ratio)
            b = C.G + "█" * filled + C.GRAY + "░" * (width - filled) + C.RST
            return f"  {b}  {C.CY}{done}/{total}{C.RST} joined"

        async def worker(idx, name):
            nonlocal joined
            async with sem:
                page = await ctx.new_page()
                ok, detail = await join_one(page, code, name)
                if not ok:
                    await page.close()
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
        print(c(f"[*] code {code}  ·  {bots} bots  ·  concurrency {concurrency}  ·  mode {mode}",
                C.CY))

        tasks = [asyncio.create_task(worker(i, name)) for i, name in enumerate(names)]
        await asyncio.gather(*tasks)

        if bar:
            sys.stdout.write("\r" + bar_line(joined) + "\n")
            sys.stdout.flush()
        print(c(f"[*] {joined}/{bots} joined, parked in lobby.", C.G if joined else C.Y))

        stop = asyncio.Event()
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
        await browser.close()
    return joined


async def main():
    ap = argparse.ArgumentParser(description="Blooket lobby flooder")
    ap.add_argument("--code", required=True, help="game pin, e.g. 400621")
    ap.add_argument("--bots", type=int, default=10, help="number of bots")
    ap.add_argument("--name", default="", help="name prefix")
    ap.add_argument("--name-file", default="", help="file of names, one per line")
    ap.add_argument("--random", action="store_true", help="random pronounceable names")
    ap.add_argument("--delay", type=float, default=0.0, help="extra seconds between bot starts")
    ap.add_argument("--concurrency", type=int, default=4, help="parallel joins")
    ap.add_argument("--visible", action="store_true", help="show the browser window")
    ap.add_argument("--headless", action="store_true", help="true headless (Cloudflare 403s the join)")
    args = ap.parse_args()

    _enable_ansi()
    await run_flood(
        code=args.code, bots=args.bots, prefix=args.name, name_file=args.name_file,
        use_random=args.random, delay=args.delay, concurrency=args.concurrency,
        visible=args.visible, headless=args.headless,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
