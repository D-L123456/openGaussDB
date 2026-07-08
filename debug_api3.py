import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # Capture all console messages
        def on_console(msg):
            print(f"  CONSOLE [{msg.type}]: {msg.text[:200]}")
        page.on("console", on_console)

        await page.goto("http://localhost:3000/challenge", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(3000)

        # Manually trigger fetchProfile via Pinia store
        result = await page.evaluate("""
            async () => {
                try {
                    // Direct axios call
                    const axios = (await import('/src/api/index.ts')).default;
                    const res = await axios.get('/learning/profile');
                    return {status: res.status, data: res.data};
                } catch(e) {
                    return {error: e.message, stack: e.stack?.slice(0, 300)};
                }
            }
        """)
        print(f"\nManual axios call: status={result.get('status')}, error={result.get('error')}")

        await browser.close()

asyncio.run(main())