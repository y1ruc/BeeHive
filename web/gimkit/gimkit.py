"""
Gimkit flooder.

Code entry verified; name step is best-effort (needs a live game to confirm).
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import run_flood, dismiss_cookies, name_step, _enable_ansi

JOIN_URL = "https://www.gimkit.com/join"
CODE_SELECTOR = "input[placeholder='Game Code']"


async def join_one(page, code, name):
    try:
        for _ in range(3):
            try:
                await page.goto(JOIN_URL, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_selector(CODE_SELECTOR, timeout=20000)
                break
            except Exception:
                await asyncio.sleep(1.0)
        else:
            return False, "join page not loaded"

        await dismiss_cookies(page)
        await page.fill(CODE_SELECTOR, code)

        btn = page.get_by_role("button", name="Join")
        if await btn.count():
            await btn.first.click(timeout=5000)
        else:
            await page.press(CODE_SELECTOR, "Enter")

        if not await name_step(page, name):
            body = await page.inner_text("body")
            for m in ("invalid", "not found", "doesn't exist", "ended", "expired", "wrong"):
                if m in body.lower():
                    return False, f"code rejected: {m}"
            return False, "no name form"

        await asyncio.sleep(1.5)
        return True, "joined"
    except Exception as e:
        return False, f"error: {type(e).__name__}: {e}"


async def main():
    ap = argparse.ArgumentParser(description="Gimkit flooder")
    ap.add_argument("--code", required=True)
    ap.add_argument("--bots", type=int, default=10)
    ap.add_argument("--name", default="")
    ap.add_argument("--concurrency", type=int, default=6)
    args = ap.parse_args()
    _enable_ansi()
    await run_flood(join_one, args.code, bots=args.bots, prefix=args.name,
                    concurrency=args.concurrency, label="code")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
