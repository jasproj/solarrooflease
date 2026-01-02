#!/usr/bin/env python3
"""
Fetch weekly chicken prices from USDA MARS API
Report 3646: Weekly National Chicken Report
"""

import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get('USDA_API_KEY')
API_URL = "https://marsapi.ams.usda.gov/services/v1.2/reports/3646?allSections=true"

# Items we want to display (in order)
WANTED_ITEMS = [
    "Breast - B/S",
    "Leg Quarters",
    "Wings",
    "Drumsticks",
    "Whole Bird",
    "Thighs - B/S",
    "Tenders"
]

def fetch_prices():
    if not API_KEY:
        print("Error: USDA_API_KEY environment variable not set")
        return None
    
    print(f"Fetching chicken prices at {datetime.now()}")
    
    try:
        response = requests.get(API_URL, auth=(API_KEY, ''))
        response.raise_for_status()
        data = response.json()
        
        # data is array: [0]=Report Header, [1]=Report Detail
        if not isinstance(data, list) or len(data) < 2:
            print("Unexpected API response format")
            return None
        
        detail = data[1]
        results = detail.get('results', [])
        
        if not results:
            print("No results in Report Detail")
            return None
        
        # Get the most recent report date
        latest_date = results[0].get('report_date', '')
        print(f"Latest report date: {latest_date}")
        
        # Filter for latest date, National region, Fresh, Domestic
        latest_results = [
            r for r in results 
            if r.get('report_date') == latest_date
            and r.get('region') == 'National'
            and r.get('condition') == 'Fresh'
            and r.get('trade_status') == 'Domestic'
        ]
        
        print(f"Found {len(latest_results)} items for {latest_date}")
        
        # Build price lookup
        price_lookup = {}
        for r in latest_results:
            item = r.get('item', '')
            if item and item not in price_lookup:
                price_lookup[item] = {
                    'wtd_avg_price': r.get('wtd_avg_price', 0),
                    'price_change': r.get('price_change', 0),
                    'wtd_avg_price_previous': r.get('wtd_avg_price_previous', 0)
                }
        
        # Build output items in preferred order
        items = []
        for wanted in WANTED_ITEMS:
            if wanted in price_lookup:
                p = price_lookup[wanted]
                cents = float(p['wtd_avg_price'])
                dollars = cents / 100
                change_cents = float(p['price_change'])
                prev_cents = float(p['wtd_avg_price_previous']) if p['wtd_avg_price_previous'] else cents
                
                # Calculate percent change
                if prev_cents > 0:
                    pct_change = (change_cents / prev_cents) * 100
                else:
                    pct_change = 0
                
                change_str = f"+{pct_change:.1f}%" if pct_change >= 0 else f"{pct_change:.1f}%"
                
                items.append({
                    "name": wanted,
                    "price": f"${dollars:.2f}/lb",
                    "raw_cents": cents,
                    "change": change_str
                })
        
        # If we didn't get enough items, add more from what's available
        if len(items) < 5:
            for item_name, p in price_lookup.items():
                if item_name not in WANTED_ITEMS and len(items) < 8:
                    cents = float(p['wtd_avg_price'])
                    dollars = cents / 100
                    change_cents = float(p['price_change'])
                    prev_cents = float(p['wtd_avg_price_previous']) if p['wtd_avg_price_previous'] else cents
                    
                    if prev_cents > 0:
                        pct_change = (change_cents / prev_cents) * 100
                    else:
                        pct_change = 0
                    
                    change_str = f"+{pct_change:.1f}%" if pct_change >= 0 else f"{pct_change:.1f}%"
                    
                    # Shorten long names
                    short_name = item_name[:18]
                    
                    items.append({
                        "name": short_name,
                        "price": f"${dollars:.2f}/lb",
                        "raw_cents": cents,
                        "change": change_str
                    })
        
        output = {
            "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "USDA AMS Weekly National Chicken Report",
            "report_date": latest_date,
            "items": items[:8]
        }
        
        return output
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    prices = fetch_prices()
    
    if prices:
        with open('prices.json', 'w') as f:
            json.dump(prices, f, indent=2)
        print(f"Saved {len(prices['items'])} items to prices.json")
        print(json.dumps(prices, indent=2))
    else:
        print("Failed to fetch prices")
        exit(1)

if __name__ == "__main__":
    main()
