import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        api_calls = []
        def on_request(req):
            if "/api/learning" in req.url:
                api_calls.append(("REQ", req.method, req.url))
        def on_response(resp):
            if "/api/learning" in resp.url:
                api_calls.append(("RESP", resp.status, resp.url[:120]))

        page.on("request", on_request)
        page.on("response", on_response)

        await page.goto("http://localhost:3000/challenge", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(5000)

        print("Learning API calls:")
        for entry in api_calls:
            print(f"  {entry}")

        if not api_calls:
            print("  No /api/learning calls detected!")
            print("  Checking if store.fetchProfile was called...")

        # Check actual page state
        score_badge = page.locator(".ability-score-badge")
        if await score_badge.count() > 0:
            text = await score_badge.inner_text()
            print(f"\nScore badge: {text}")

        # Check completed level cards
        cards = page.locator(".level-card")
        for i in range(min(await cards.count(), 2)):
            card = cards.nth(i)
            cls = await card.get_attribute("class") or ""
            name_el = card.locator(".level-name")
            name = await name_el.inner_text() if await name_el.count() > 0 else "?"
            diff_el = card.locator(".level-difficulty")
            diff = await diff_el.inner_text() if await diff_el.count() > 0 else "?"
            print(f"  Card {i}: class='{cls}', name={name}, status={diff}")

        await browser.close()

asyncio.run(main())