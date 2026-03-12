import json
import asyncio
from playwright.async_api import async_playwright

# Map internal IDs to CSFloat Market Hash Names
TARGETS = {
    "dead_hand": "Sealed Dead Hand Terminal",
    "genesis": "Sealed Genesis Terminal",
    "gallery": "Gallery Case",
    "kilowatt": "Kilowatt Case",
    "bravo": "Operation Bravo Case",
    "hydra": "Operation Hydra Case"
}

async def scrape_csfloat():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        
        live_data = {}
        
        for cid, market_name in TARGETS.items():
            try:
                # Search for the specific container
                url = f"https://csfloat.com/search?sort_by=lowest_price&type=buy_now&market_hash_name={market_name.replace(' ', '%20')}"
                await page.goto(url)
                
                # Wait for the first price element to load
                await page.wait_for_selector(".price", timeout=8000)
                price_raw = await page.locator(".price").first.inner_text()
                
                # Clean price string (e.g., "$1.45" -> 1.45)
                price_val = float(price_raw.replace('$', '').replace(',', '').strip())
                
                # We calculate a rough EV based on 2026 market baselines
                # In a full build, you would scrape the internal skins here too
                live_data[cid] = {
                    "casePrice": price_val,
                    "lastUpdated": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                print(f"Synced: {market_name} @ ${price_val}")
                await asyncio.sleep(1) # Be polite to the server
            except Exception as e:
                print(f"Skipping {market_name}: Market busy or item not found.")

        with open('prices.json', 'w') as f:
            json.dump(live_data, f, indent=4)
        
        await browser.close()

if __name__ == "__main__":
    import time
    asyncio.run(scrape_csfloat())
