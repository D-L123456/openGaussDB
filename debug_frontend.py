import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # Monitor network requests
        learning_responses = []
        def on_response(resp):
            if "learning" in resp.url:
                learning_responses.append((resp.status, resp.url[:100]))
        page.on("response", on_response)

        # Monitor console errors
        def on_console(msg):
            if msg.type == "error" or "Failed" in msg.text:
                print(f"  CONSOLE ERROR: {msg.text[:150]}")
        page.on("console", on_console)

        await page.goto("http://localhost:3000/challenge", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(3000)

        # Check learning API calls
        print(f"Learning API calls: {len(learning_responses)}")
        for status, url in learning_responses:
            print(f"  {status} {url}")

        # Check score
        score_badge = page.locator(".ability-score-badge")
        if await score_badge.count() > 0:
            text = await score_badge.inner_text()
            print(f"Score badge text: {text}")

        # Check completed levels
        completed_cards = page.locator(".level-card.completed")
        completed_count = await completed_cards.count()
        print(f"Completed level cards: {completed_count}")

        # Check all card states
        cards = page.locator(".level-card")
        for i in range(await cards.count()):
            card = cards.nth(i)
            classes = await card.get_attribute("class")
            text = await card.inner_text()
            lines = text.strip().split("\n")
            print(f"  Card {i}: class={classes}, name={lines[1] if len(lines) > 1 else '?'}")

        await browser.close()

asyncio.run(main())