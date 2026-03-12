import requests
import json
import time

# Core Constants
KEY_COST = 2.49
STEAM_API_URL = "https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name="

# Valve Probability Matrix
ODDS = {
    "gold": 0.0026,
    "red": 0.0064,
    "pink": 0.032,
    "purple": 0.1598,
    "blue": 0.7992
}

# Database Structure
# We define the container, its low-tier floor (average value of blue/purple drops combined), and the Top ROI contributors.
DATABASE = {
    "gallery": {
        "name": "Gallery Case",
        "low_tier_floor": 0.08, 
        "is_souvenir": False,
        "skins": [
            {"name": "★ Kukri Knife", "rarity": "gold", "search": "★ Kukri Knife | Vanilla"},
            {"name": "M4A1-S | Vaporwave", "rarity": "red", "search": "M4A1-S | Vaporwave (Field-Tested)"},
            {"name": "Glock-18 | Gold Toof", "rarity": "red", "search": "Glock-18 | Gold Toof (Field-Tested)"}
        ]
    },
    "kilowatt": {
        "name": "Kilowatt Case",
        "low_tier_floor": 0.05,
        "is_souvenir": False,
        "skins": [
            {"name": "★ Kukri Knife", "rarity": "gold", "search": "★ Kukri Knife | Vanilla"},
            {"name": "AK-47 | Inheritance", "rarity": "red", "search": "AK-47 | Inheritance (Field-Tested)"},
            {"name": "AWP | Chrome Cannon", "rarity": "red", "search": "AWP | Chrome Cannon (Field-Tested)"}
        ]
    }
}

def get_cash_price(market_hash_name):
    """Fetches SCM price and converts to real cash value."""
    try:
        response = requests.get(f"{STEAM_API_URL}{market_hash_name}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'lowest_price' in data:
                # Clean price string (e.g., "$45.50" -> 45.50)
                raw_price = float(data['lowest_price'].replace('$', '').replace(',', ''))
                # Strip the 15% Steam Tax to get true cash value
                return round(raw_price * 0.85, 2)
    except Exception as e:
        print(f"Network error for {market_hash_name}: {e}")
    return 0.0

def generate_market_report():
    print("Initiating Market Scan...")
    final_output = {}

    for case_id, data in DATABASE.items():
        print(f"\nScanning: {data['name']}")
        
        # 1. Fetch Container Price
        case_price = get_cash_price(data['name'])
        time.sleep(3) # Throttle to respect Steam's 20-requests-per-minute limit
        
        total_ev = data['low_tier_floor']
        processed_skins = []

        # 2. Fetch Top Contributor Prices and Calculate EV
        for skin in data['skins']:
            skin_price = get_cash_price(skin['search'])
            time.sleep(3) # Throttle
            
            # Math: Price * Probability
            probability = ODDS[skin['rarity']]
            ev_contribution = skin_price * probability
            total_ev += ev_contribution
            
            processed_skins.append({
                "n": skin['name'],
                "r": skin['rarity'],
                "o": f"{probability * 100}%",
                "p": skin_price
            })

        # 3. Calculate Final ROI
        total_cost = case_price + (0 if data['is_souvenir'] else KEY_COST)
        roi = round((total_ev / total_cost) * 100, 1) if total_cost > 0 else 0

        # 4. Package for the Front-End
        final_output[case_id] = {
            "name": data['name'],
            "casePrice": case_price,
            "totalEv": round(total_ev, 2),
            "roi": roi,
            "skins": processed_skins
        }
        
        print(f"Result -> Cost: ${round(total_cost, 2)} | EV: ${round(total_ev, 2)} | ROI: {roi}%")

    # Write to JSON
    with open('prices.json', 'w') as f:
        json.dump(final_output, f, indent=4)
    print("\nScan Complete. prices.json updated.")

if __name__ == "__main__":
    generate_market_report()
