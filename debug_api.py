import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        api_calls = []
        def on_request(req):
            if "/api/" in req.url:
                api_calls.append(("REQ", req.method, req.url))
        def on_response(resp):
            if "/api/" in resp.url:
                api_calls.append(("RESP", resp.status, resp.url[:100]))
        def on_console(msg):
            if "Failed" in msg.text or "error" in msg.text.lower():
                print(f"  CONSOLE: {msg.text[:200]}")

        page.on("request", on_request)
        page.on("response", on_response)
        page.on("console", on_console)

        await page.goto("http://localhost:3000/challenge", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(3000)

        print("API calls:")
        for entry in api_calls:
            print(f"  {entry}")

        # Also try calling the API directly from the browser
        result = await page.evaluate("""
            async () => {
                try {
                    const r = await fetch('/api/learning/profile');
                    const d = await r.json();
                    return {status: r.status, scores: d.ability_scores, progress: d.challenge_progress};
                } catch(e) {
                    return {error: e.message};
                }
            }
        """)
        print(f"\nDirect fetch result: {result}")

        await browser.close()

asyncio.run(main())