import json
import asyncio
import time
from playwright.async_api import async_playwright

# The list of items we need to track for ROI
# For cases, we pull the case price. For ROI contributors, we pull the specific skin price.
TARGET_ITEMS = {
    "gallery": "Gallery Case",
    "kilowatt": "Kilowatt Case",
    "bravo": "Operation Bravo Case",
    "m4_vaporwave": "M4A1-S | Vaporwave (Field-Tested)",
    "ak_inheritance": "AK-47 | Inheritance (Field-Tested)",
    "ak_fire_serpent": "AK-47 | Fire Serpent (Field-Tested)"
}

async def get_price(page, item_name):
    try:
        # Search for the item on CSFloat
        search_url = f"https://csfloat.com/search?sort_by=lowest_price&type=buy_now&market_hash_name={item_name.replace(' ', '%20')}"
        await page.goto(search_url)
        
        # Wait for the first listing to appear
        # Selector targets the price amount inside the first item card
        await page.wait_for_selector(".price", timeout=10000)
        
        price_text = await page.locator(".price").first.inner_text()
        # Clean price (remove $, commas, etc.)
        price_val = float(price_text.replace('$', '').replace(',', '').strip())
        
        print(f"Verified: {item_name} -> ${price_val}")
        return price_val
    except Exception as e:
        print(f"Error fetching {item_name}: {e}")
        return None

async def run_update():
    async with async_playwright() as p:
        # We use a real User-Agent to avoid immediate blocking
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        results = {}
        for key, name in TARGET_ITEMS.items():
            price = await get_price(page, name)
            if price:
                results[key] = price
            # Sleep to prevent rate-limiting (CSFloat is sensitive)
            await asyncio.sleep(2)
            
        # Save to the JSON file your website reads
        with open('prices.json', 'w') as f:
            json.dump(results, f, indent=4)
            
        print("\n--- Update Complete: prices.json synced ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_update())
