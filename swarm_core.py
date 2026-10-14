"""
swarm_core — shared flood engine for BeeHive.

Every site driver is a thin module that implements:

    async def join_one(page, code, name) -> (ok, detail)

and this module supplies the generic browser/context/naming/progress machinery.

Drivers:
    from swarm_core import run_flood, build_names
"""

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

BLOCK_PATTERNS = [
    re.compile(r"\.(png|jpe?g|gif|webp|svg|ico)(\?|$)", re.I),
    re.compile(r"\.(woff2?|ttf|otf|eot)(\?|$)", re.I),
    re.compile(r"\.(mp3|ogg|wav|m4a)(\?|$)", re.I),
    re.compile(r"(amplitude|googletagmanager|google-analytics|cookieyes|sentry|hotjar|doubleclick|snowplow|rollbar)", re.I),
]

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
    R = "\x1b[31m"; G = "\x1b[32m"; Y = "\x1b[33m"; B = "\x1b[34m"
    M = "\x1b[35m"; CY = "\x1b[36m"; W = "\x1b[37m"; GRAY = "\x1b[90m"
    BOLD = "\x1b[1m"; DIM = "\x1b[2m"; RST = "\x1b[0m"


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
            out = []
            for i in range(bots):
                base = raw[i % len(raw)]
                out.append(base[:15] if i < len(raw) else f"{base[:12]}{i - len(raw) + 1}")
            return out
    if name_file:
        with open(name_file, "r", encoding="utf-8") as f:
            raw = [ln.strip() for ln in f if ln.strip()]
        if not raw:
            raise SystemExit("[!] name file is empty")
        out = []
        for i in range(bots):
            base = raw[i % len(raw)]
            out.append(base[:15] if i < len(raw) else f"{base[:12]}{i - len(raw) + 1}")
        return out
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
    out = []
    for i in range(bots):
        tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        out.append(f"{prefix}{i}{tag}"[:15])
    return out


# ---- networking -----------------------------------------------------------

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
    out = {"server": f"{scheme or 'http'}://{host}:{port}"}
    if user:
        out["username"] = user
        out["password"] = pw or ""
    return out


def load_proxies(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]


async def auto_answer(page, stop, selector="[data-functional-selector^='answer-']:visible"):
    answered = False
    while not stop.is_set():
        try:
            btns = page.locator(selector)
            n = await btns.count()
            if n > 0 and not answered:
                await btns.nth(random.randint(0, n - 1)).click(timeout=1500)
                answered = True
            elif n == 0:
                answered = False
        except Exception:
            pass
        await asyncio.sleep(0.25)


# ---- generic helpers -------------------------------------------------------

_NAME_HINT = re.compile(r"(name|nickname|alias)", re.I)
_SUBMIT_TEXTS = ("Join", "Continue", "Enter", "Play", "OK", "Ok", "Go", "Next", "Submit", "Join game")


def banner(title):
    _enable_ansi()
    print(c("─" * 58, C.GRAY))
    print(c(title.center(58), C.CY + C.BOLD))
    print(c("─" * 58, C.GRAY))


def ask(label, default=""):
    try:
        return input(c(f"  {label:<18}", C.CY) + c(f"[{default}] ", C.GRAY)).strip()
    except (EOFError, KeyboardInterrupt):
        return default


def pause():
    try:
        input(c("  press ENTER to return", C.GRAY))
    except (EOFError, KeyboardInterrupt):
        pass


def http_req(url, method="GET", headers=None, data=None, json=None, timeout=15):
    """Minimal HTTP helper. Returns (status:int|None, body:bytes)."""
    import json as _json
    import urllib.error
    import urllib.request

    headers = dict(headers or {})
    headers.setdefault("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/130.0.0.0 Safari/537.36")
    if json is not None:
        data = _json.dumps(json).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return None, str(e).encode()


def parse_webhook(url):
    """Extract (id, token) from a discord webhook URL."""
    m = re.search(r"discord(?:app)?\.com/api/(?:v\d+/)?webhooks/(\d+)/([A-Za-z0-9_.\-]+)", url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"discord\.com/api/webhooks/(\d+)/([A-Za-z0-9_.\-]+)", url)
    if m:
        return m.group(1), m.group(2)
    return None, None


async def dismiss_cookies(page, labels=("Allow all", "Accept all", "Accept all cookies", "I agree", "Agree")):
    for label in labels:
        btn = page.get_by_role("button", name=label)
        try:
            if await btn.count():
                await btn.first.click(timeout=1500)
                return
        except Exception:
            continue


async def name_step(page, name, submit_texts=_SUBMIT_TEXTS):
    """Best-effort: find a name/nickname input, fill it, submit. Returns bool."""
    for _ in range(80):
        inputs = page.locator("input:visible")
        n = await inputs.count()
        for i in range(n):
            el = inputs.nth(i)
            try:
                ph = (await el.get_attribute("placeholder") or "").lower()
                nm = (await el.get_attribute("name") or "").lower()
                ar = (await el.get_attribute("aria-label") or "").lower()
                typ = (await el.get_attribute("type") or "text").lower()
            except Exception:
                continue
            if typ in ("hidden", "checkbox", "radio", "submit", "button", "number"):
                continue
            if _NAME_HINT.search(ph + nm + ar):
                try:
                    await el.fill(name, timeout=3000)
                except Exception:
                    pass
                for t in submit_texts:
                    b = page.get_by_role("button", name=t)
                    if await b.count():
                        try:
                            await b.first.click(timeout=3000)
                            return True
                        except Exception:
                            pass
                sb = page.locator("button[type='submit']:visible")
                if await sb.count():
                    try:
                        await sb.first.click(timeout=3000)
                        return True
                    except Exception:
                        pass
                try:
                    await el.press("Enter")
                    return True
                except Exception:
                    pass
                return True
        await asyncio.sleep(0.25)
    return False


# ---- core -----------------------------------------------------------------

async def run_flood(join_one, code, bots=10, prefix="", name_file="", use_random=False,
                    name_list=None, delay=0.0, concurrency=6, visible=False,
                    headless=False, quiet=False, bar=False, answer=False,
                    proxy_file="", block=True, answer_selector="[data-functional-selector^='answer-']:visible",
                    label="code"):
    code = code.strip()

    names = build_names(bots, prefix, name_file, use_random, name_list)
    proxies = load_proxies(proxy_file) if proxy_file else []

    async with async_playwright() as p:
        launch_args = ["--disable-blink-features=AutomationControlled"]
        if not visible and not headless:
            launch_args.append("--window-position=-32000,-32000")

        browser = await p.chromium.launch(headless=headless, args=launch_args)

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
                opts = {"user_agent": UA, "viewport": {"width": 1280, "height": 800}}
                if proxies:
                    opts["proxy"] = parse_proxy(proxies[idx % len(proxies)])
                ctx = await browser.new_context(**opts)
                await ctx.add_init_script(STEALTH)
                if block:
                    await ctx.route("**/*", _route_handler)
                page = await ctx.new_page()
                ok, detail = await join_one(page, code, name)
                if not ok:
                    await ctx.close()
                else:
                    if answer:
                        answer_tasks.append(asyncio.create_task(auto_answer(page, stop, answer_selector)))
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
        print(c(f"[*] {label} {code}  ·  {bots} bots  ·  concurrency {concurrency}  ·  mode {mode}",
                C.CY))

        tasks = [asyncio.create_task(worker(i, name)) for i, name in enumerate(names)]
        await asyncio.gather(*tasks)

        if bar:
            sys.stdout.write("\r" + bar_line(joined) + "\n")
            sys.stdout.flush()
        print(c(f"[*] {joined}/{bots} joined, parked.", C.G if joined else C.Y))

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
