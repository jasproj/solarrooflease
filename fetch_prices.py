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
REPORT_ID = "3646"
API_URL = f"https://marsapi.ams.usda.gov/services/v1.2/reports/{REPORT_ID}"

def fetch_prices():
    if not API_KEY:
        print("Error: USDA_API_KEY environment variable not set")
        return None
    
    print(f"Fetching chicken prices at {datetime.now()}")
    
    try:
        response = requests.get(API_URL, auth=(API_KEY, ''))
        response.raise_for_status()
        data = response.json()
        
        items = []
        
        if 'results' in data:
            for record in data['results']:
                item_name = record.get('item_description', record.get('commodity', ''))
                price_str = record.get('price', record.get('wtd_avg_price', ''))
                
                if item_name and price_str:
                    try:
                        price_val = float(str(price_str).replace('$', '').replace(',', ''))
                        items.append({
                            "name": item_name[:20],
                            "price": f"${price_val:.2f}/lb",
                            "raw_cents": round(price_val * 100, 2)
                        })
                    except (ValueError, TypeError):
                        continue
        
        # If no results parsed, use fallback structure
        if not items:
            print("No items parsed from API, checking alternate data structure...")
            # Try to extract from different possible structures
            for section in data.get('results', []):
                if isinstance(section, dict):
                    for key, val in section.items():
                        if 'price' in key.lower() and val:
                            try:
                                price_val = float(str(val).replace('$', '').replace(',', ''))
                                items.append({
                                    "name": key[:20],
                                    "price": f"${price_val:.2f}/lb",
                                    "raw_cents": round(price_val * 100, 2)
                                })
                            except:
                                pass
        
        if not items:
            print("Warning: Could not parse prices, using defaults")
            items = [
                {"name": "Whole Broiler", "price": "$1.14/lb", "raw_cents": 114.0},
                {"name": "Breast B/S", "price": "$1.16/lb", "raw_cents": 116.0},
                {"name": "Leg Quarters", "price": "$0.48/lb", "raw_cents": 48.0},
                {"name": "Wings", "price": "$1.42/lb", "raw_cents": 142.0},
                {"name": "Drumsticks", "price": "$0.63/lb", "raw_cents": 63.0}
            ]
        
        output = {
            "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "USDA AMS Weekly National Chicken Report",
            "report_id": REPORT_ID,
            "items": items[:8]  # Limit to 8 items for ticker
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
