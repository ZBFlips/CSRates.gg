import requests
import json
import time

# Core Economics
KEY_COST = 2.49
BULK_API_URL = "http://csgobackpack.net/api/GetItemsList/v2/?no_details=true"

# The Master Probability Matrix
RARITY_ODDS = { "gold": 0.0026, "red": 0.0064, "pink": 0.032, "purple": 0.1598, "blue": 0.7992 }
WEAR_WEIGHTS = { "Factory New": 0.07, "Minimal Wear": 0.08, "Field-Tested": 0.23, "Well-Worn": 0.07, "Battle-Scarred": 0.55 }
STATTRAK_CHANCE = { "ST": 0.10, "Non-ST": 0.90 }

# Capped-Float Anomalies (Adjusts mathematical weights for restricted skins)
FLOAT_ANOMALIES = {
    "Asiimov": ["Field-Tested", "Well-Worn", "Battle-Scarred"],
    "Redline": ["Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"],
    "Fade": ["Factory New", "Minimal Wear"],
    "Doppler": ["Factory New", "Minimal Wear"],
    "Gamma Doppler": ["Factory New", "Minimal Wear"],
    "Tiger Tooth": ["Factory New", "Minimal Wear"],
    "Marble Fade": ["Factory New", "Minimal Wear"],
    "Slaughter": ["Factory New", "Minimal Wear", "Field-Tested"]
}

# The Full 40-Container Roster
ROSTER = {
    "weapon1": {"name": "CS:GO Weapon Case", "s": False, "f": 4.50, "skins": [{"w": "AWP", "p": "Lightning Strike", "r": "red"}, {"w": "AK-47", "p": "Case Hardened", "r": "pink"}]},
    "weapon2": {"name": "CS:GO Weapon Case 2", "s": False, "f": 0.80, "skins": [{"w": "SSG 08", "p": "Blood in the Water", "r": "red"}, {"w": "P90", "p": "Cold Blooded", "r": "pink"}]},
    "weapon3": {"name": "CS:GO Weapon Case 3", "s": False, "f": 0.40, "skins": [{"w": "CZ75-Auto", "p": "Victoria", "r": "red"}, {"w": "P250", "p": "Undertow", "r": "pink"}]},
    "bravo": {"name": "Operation Bravo Case", "s": False, "f": 2.50, "skins": [{"w": "AK-47", "p": "Fire Serpent", "r": "red"}, {"w": "Desert Eagle", "p": "Golden Koi", "r": "red"}, {"w": "P90", "p": "Emerald Dragon", "r": "pink"}]},
    "esports2013": {"name": "eSports 2013 Case", "s": False, "f": 1.50, "skins": [{"w": "P90", "p": "Death by Kitty", "r": "red"}, {"w": "AWP", "p": "BOOM", "r": "pink"}]},
    "esportswinter": {"name": "eSports 2013 Winter Case", "s": False, "f": 0.70, "skins": [{"w": "M4A4", "p": "X-Ray", "r": "red"}, {"w": "Desert Eagle", "p": "Cobalt Disruption", "r": "pink"}]},
    "esportssummer": {"name": "eSports 2014 Summer Case", "s": False, "f": 0.60, "skins": [{"w": "M4A4", "p": "Bullet Rain", "r": "red"}, {"w": "AK-47", "p": "Jaguar", "r": "pink"}]},
    "winteroff": {"name": "Winter Offensive Weapon Case", "s": False, "f": 0.50, "skins": [{"w": "M4A4", "p": "Asiimov", "r": "red"}, {"w": "AWP", "p": "Redline", "r": "pink"}]},
    "phoenix": {"name": "Operation Phoenix Weapon Case", "s": False, "f": 0.35, "skins": [{"w": "AWP", "p": "Asiimov", "r": "red"}, {"w": "AK-47", "p": "Redline", "r": "pink"}]},
    "huntsman": {"name": "Huntsman Weapon Case", "s": False, "f": 0.40, "skins": [{"w": "AK-47", "p": "Vulcan", "r": "red"}, {"w": "M4A4", "p": "Desert-Strike", "r": "red"}]},
    "breakout": {"name": "Operation Breakout Weapon Case", "s": False, "f": 0.30, "skins": [{"w": "M4A1-S", "p": "Cyrex", "r": "red"}, {"w": "P90", "p": "Asiimov", "r": "red"}]},
    "vanguard": {"name": "Operation Vanguard Weapon Case", "s": False, "f": 0.30, "skins": [{"w": "AK-47", "p": "Wasteland Rebel", "r": "red"}, {"w": "M4A4", "p": "Griffin", "r": "pink"}]},
    "chroma": {"name": "Chroma Case", "s": False, "f": 0.20, "skins": [{"w": "AWP", "p": "Man-o'-war", "r": "red"}, {"w": "Galil AR", "p": "Chatterbox", "r": "red"}]},
    "chroma2": {"name": "Chroma 2 Case", "s": False, "f": 0.15, "skins": [{"w": "M4A1-S", "p": "Hyper Beast", "r": "red"}, {"w": "MAC-10", "p": "Neon Rider", "r": "red"}]},
    "chroma3": {"name": "Chroma 3 Case", "s": False, "f": 0.15, "skins": [{"w": "M4A1-S", "p": "Chantico's Fire", "r": "red"}, {"w": "PP-Bizon", "p": "Judgement of Anubis", "r": "red"}]},
    "falchion": {"name": "Falchion Case", "s": False, "f": 0.15, "skins": [{"w": "AWP", "p": "Hyper Beast", "r": "red"}, {"w": "AK-47", "p": "Aquamarine Revenge", "r": "red"}]},
    "shadow": {"name": "Shadow Case", "s": False, "f": 0.12, "skins": [{"w": "USP-S", "p": "Kill Confirmed", "r": "red"}, {"w": "M4A1-S", "p": "Golden Coil", "r": "red"}]},
    "revolver": {"name": "Revolver Case", "s": False, "f": 0.10, "skins": [{"w": "M4A4", "p": "Point Disarray", "r": "red"}, {"w": "R8 Revolver", "p": "Fade", "r": "red"}]},
    "wildfire": {"name": "Operation Wildfire Case", "s": False, "f": 0.15, "skins": [{"w": "AK-47", "p": "Fuel Injector", "r": "red"}, {"w": "M4A4", "p": "The Battlestar", "r": "red"}]},
    "gamma": {"name": "Gamma Case", "s": False, "f": 0.15, "skins": [{"w": "M4A1-S", "p": "Mecha Industries", "r": "red"}, {"w": "Glock-18", "p": "Wasteland Rebel", "r": "red"}]},
    "gamma2": {"name": "Gamma 2 Case", "s": False, "f": 0.15, "skins": [{"w": "AK-47", "p": "Neon Revolution", "r": "red"}, {"w": "FAMAS", "p": "Roll Cage", "r": "red"}]},
    "glove": {"name": "Glove Case", "s": False, "f": 0.10, "skins": [{"w": "M4A4", "p": "Buzz Kill", "r": "red"}, {"w": "SSG 08", "p": "Dragonfire", "r": "red"}]},
    "spectrum": {"name": "Spectrum Case", "s": False, "f": 0.10, "skins": [{"w": "AK-47", "p": "Bloodsport", "r": "red"}, {"w": "USP-S", "p": "Neo-Noir", "r": "red"}]},
    "spectrum2": {"name": "Spectrum 2 Case", "s": False, "f": 0.08, "skins": [{"w": "AK-47", "p": "The Empress", "r": "red"}, {"w": "P250", "p": "See Ya Later", "r": "red"}]},
    "hydra": {"name": "Operation Hydra Case", "s": False, "f": 0.50, "skins": [{"w": "AWP", "p": "Oni Taiji", "r": "red"}, {"w": "Five-SeveN", "p": "Hyper Beast", "r": "red"}]},
    "clutch": {"name": "Clutch Case", "s": False, "f": 0.05, "skins": [{"w": "M4A4", "p": "Neo-Noir", "r": "red"}, {"w": "MP7", "p": "Bloodsport", "r": "red"}]},
    "horizon": {"name": "Horizon Case", "s": False, "f": 0.05, "skins": [{"w": "AK-47", "p": "Neon Rider", "r": "red"}, {"w": "Desert Eagle", "p": "Code Red", "r": "red"}]},
    "dangerzone": {"name": "Danger Zone Case", "s": False, "f": 0.05, "skins": [{"w": "AK-47", "p": "Asiimov", "r": "red"}, {"w": "AWP", "p": "Neo-Noir", "r": "red"}]},
    "prisma": {"name": "Prisma Case", "s": False, "f": 0.05, "skins": [{"w": "M4A4", "p": "The Emperor", "r": "red"}, {"w": "Five-SeveN", "p": "Angry Mob", "r": "red"}]},
    "prisma2": {"name": "Prisma 2 Case", "s": False, "f": 0.04, "skins": [{"w": "M4A1-S", "p": "Player Two", "r": "red"}, {"w": "MAC-10", "p": "Stalker", "r": "red"}]},
    "cs20": {"name": "CS20 Case", "s": False, "f": 0.06, "skins": [{"w": "AWP", "p": "Wildfire", "r": "red"}, {"w": "FAMAS", "p": "Commemoration", "r": "red"}]},
    "shatteredweb": {"name": "Shattered Web Case", "s": False, "f": 0.08, "skins": [{"w": "AWP", "p": "Containment Breach", "r": "red"}, {"w": "MAC-10", "p": "Stalker", "r": "red"}]},
    "fracture": {"name": "Fracture Case", "s": False, "f": 0.05, "skins": [{"w": "AK-47", "p": "Legion of Anubis", "r": "red"}, {"w": "Desert Eagle", "p": "Printstream", "r": "red"}]},
    "brokenfang": {"name": "Operation Broken Fang Case", "s": False, "f": 0.08, "skins": [{"w": "M4A1-S", "p": "Printstream", "r": "red"}, {"w": "Glock-18", "p": "Neo-Noir", "r": "red"}]},
    "snakebite": {"name": "Snakebite Case", "s": False, "f": 0.04, "skins": [{"w": "M4A4", "p": "In Living Color", "r": "red"}, {"w": "USP-S", "p": "The Traitor", "r": "red"}]},
    "riptide": {"name": "Operation Riptide Case", "s": False, "f": 0.08, "skins": [{"w": "Desert Eagle", "p": "Ocean Drive", "r": "red"}, {"w": "AK-47", "p": "Leaded Glass", "r": "pink"}]},
    "dreams": {"name": "Dreams & Nightmares Case", "s": False, "f": 0.07, "skins": [{"w": "AK-47", "p": "Nightwish", "r": "red"}, {"w": "MP9", "p": "Starlight Protector", "r": "red"}]},
    "recoil": {"name": "Recoil Case", "s": False, "f": 0.04, "skins": [{"w": "USP-S", "p": "Printstream", "r": "red"}, {"w": "AWP", "p": "Chromatic Aberration", "r": "red"}]},
    "revolution": {"name": "Revolution Case", "s": False, "f": 0.06, "skins": [{"w": "M4A4", "p": "Temukau", "r": "red"}, {"w": "AK-47", "p": "Head Shot", "r": "red"}]},
    "kilowatt": {"name": "Kilowatt Case", "s": False, "f": 0.05, "skins": [{"w": "AK-47", "p": "Inheritance", "r": "red"}, {"w": "AWP", "p": "Chrome Cannon", "r": "red"}]},
    "gallery": {"name": "Gallery Case", "s": False, "f": 0.08, "skins": [{"w": "M4A1-S", "p": "Vaporwave", "r": "red"}, {"w": "Glock-18", "p": "Gold Toof", "r": "red"}]},
    "genesis": {"name": "Sealed Genesis Terminal", "s": True, "f": 0.10, "skins": [{"w": "AK-47", "p": "Searing Rage", "r": "red"}, {"w": "Glock-18", "p": "Shinobu", "r": "red"}]},
    "deadhand": {"name": "Sealed Dead Hand Terminal", "s": True, "f": 0.15, "skins": [{"w": "AWP", "p": "Queen's Gambit", "r": "red"}, {"w": "Glock-18", "p": "Fully Tuned", "r": "red"}]}
}

def fetch_bulk_market_data():
    """Fetches entire SCM pricing DB in one request."""
    print("Downloading Bulk API Dump...")
    try:
        res = requests.get(BULK_API_URL, timeout=30)
        if res.status_code == 200:
            return res.json().get('items_list', {})
    except Exception as e:
        print(f"Failed to fetch bulk data: {e}")
    return {}

def get_price_from_dump(dump, market_hash_name):
    """Extracts skin price, removes Steam Tax (0.85x)."""
    item = dump.get(market_hash_name)
    if item and 'price' in item and item['price']:
        raw_price = item['price'].get('lowest_price', 0)
        if isinstance(raw_price, str):
            raw_price = float(raw_price.replace('$', '').replace(',', ''))
        return round(raw_price * 0.85, 2)
    return 0.0

def process_market():
    market_dump = fetch_bulk_market_data()
    if not market_dump:
        print("Abort: No market data retrieved.")
        return

    final_db = {}
    
    for case_id, case_data in ROSTER.items():
        case_price = get_price_from_dump(market_dump, case_data['name'])
        total_case_ev = case_data['f'] # Start with low-tier floor value
        skin_reports = []
        
        for skin in case_data['skins']:
            skin_ev = 0.0
            top_pull = {"name": "", "price": 0.0}
            
            # Dynamic Float Capping Logic
            active_wears = WEAR_WEIGHTS.copy()
            if skin['pattern'] in FLOAT_ANOMALIES:
                allowed = FLOAT_ANOMALIES[skin['pattern']]
                active_wears = {k: v for k, v in active_wears.items() if k in allowed}
                # Normalize weights so they equal 100% of the drop pool
                total_allowed_weight = sum(active_wears.values())
                active_wears = {k: v / total_allowed_weight for k, v in active_wears.items()}

            for wear, w_weight in active_wears.items():
                for st_status, st_weight in STATTRAK_CHANCE.items():
                    # Souvenirs and Terminals handling for ST
                    if case_data['s'] and st_status == "ST":
                        continue 
                        
                    st_prefix = "StatTrak™ " if st_status == "ST" else ""
                    hash_name = f"{st_prefix}{skin['w']} | {skin['p']} ({wear})"
                    
                    price = get_price_from_dump(market_dump, hash_name)
                    
                    variant_ev = price * RARITY_ODDS[skin['r']] * w_weight * st_weight
                    skin_ev += variant_ev
                    total_case_ev += variant_ev
                    
                    if price > top_pull["price"]:
                        top_pull = {"name": hash_name, "price": price}

            skin_reports.append({
                "base_name": f"{skin['w']} | {skin['p']}",
                "rarity": skin['r'],
                "weighted_ev": round(skin_ev, 4),
                "top_pull": top_pull['name'] or f"{skin['w']} | {skin['p']}",
                "top_pull_price": top_pull['price']
            })
            
        total_cost = case_price + (0 if case_data['s'] else KEY_COST)
        roi = round((total_case_ev / total_cost) * 100, 2) if total_cost > 0 else 0
        
        final_db[case_id] = {
            "name": case_data['name'],
            "casePrice": case_price,
            "totalEv": round(total_case_ev, 2),
            "roi": roi,
            "skins": skin_reports
        }
        
    with open('prices.json', 'w') as f:
        json.dump(final_db, f, indent=4)
    print("Market Engine Complete. Output saved to prices.json.")

if __name__ == "__main__":
    process_market()
