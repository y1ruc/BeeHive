"""
Quizlet Live flooder.

Code entry verified (input#charInput + Continue). Name step best-effort.
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swarm_core import run_flood, dismiss_cookies, name_step, _enable_ansi

JOIN_URL = "https://quizlet.com/live"
CODE_SELECTOR = "input#charInput"


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
        await page.get_by_role("button", name="Continue").click(timeout=5000)

        if not await name_step(page, name, submit_texts=("Join game", "Join", "Continue", "Play")):
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
    ap = argparse.ArgumentParser(description="Quizlet Live flooder")
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
