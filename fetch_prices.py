#!/usr/bin/env python3
"""
Fetch weekly chicken prices from USDA MARS API
Runs via GitHub Actions every Friday at 5pm ET
"""

import json
import requests
from datetime import datetime, timedelta
import os

# USDA MARS API configuration
API_BASE = "https://marsapi.ams.usda.gov/services/v1.2/reports"
API_KEY = os.environ.get("USDA_API_KEY", "")

# Report IDs for chicken/poultry data
# PY_FG100 = National Weekly Chicken Report (Wholesale Prices)
CHICKEN_REPORT_ID = "2469"  # Weekly National Chicken Report

def fetch_chicken_prices():
    """Fetch latest chicken prices from USDA MARS API"""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Basic auth: API key as username, empty password
    auth = (API_KEY, "")
    
    # Get the latest report data
    url = f"{API_BASE}/{CHICKEN_REPORT_ID}"
    
    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return parse_chicken_data(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_chicken_data(data):
    """Parse USDA response into ticker-friendly format"""
    
    prices = {
        "updated": datetime.now().isoformat(),
        "source": "USDA AMS Weekly National Chicken Report",
        "items": []
    }
    
    # Extract results from API response
    results = data.get("results", [])
    
    if not results:
        print("No results found in API response")
        return prices
    
    # Group by item and get latest prices
    price_map = {}
    
    for record in results:
        item_name = record.get("item_description", "")
        price_low = record.get("price_low")
        price_high = record.get("price_high")
        price_avg = record.get("weighted_average")
        report_date = record.get("report_date", "")
        
        # Calculate average if not provided
        if price_avg is None and price_low and price_high:
            price_avg = (float(price_low) + float(price_high)) / 2
        
        if item_name and price_avg:
            # Keep the most recent price for each item
            if item_name not in price_map or report_date > price_map[item_name]["date"]:
                price_map[item_name] = {
                    "name": item_name,
                    "price": round(float(price_avg), 2),
                    "unit": "¢/lb",
                    "date": report_date
                }
    
    # Convert to list and map to display names
    display_names = {
        "Leg Quarters": "Leg Quarters",
        "Breast, Boneless/Skinless": "Breast B/S",
        "Wings": "Wings",
        "Drumsticks": "Drumsticks",
        "Whole Broiler": "Whole Broiler",
        "Backs and Necks": "Backs & Necks",
        "Thighs, Boneless/Skinless": "Thighs B/S",
    }
    
    for item_name, data in price_map.items():
        # Try to match to our display names
        display_name = None
        for key, name in display_names.items():
            if key.lower() in item_name.lower():
                display_name = name
                break
        
        if display_name:
            # Convert cents to dollars for display
            price_dollars = data["price"] / 100
            prices["items"].append({
                "name": display_name,
                "price": f"${price_dollars:.2f}/lb",
                "raw_cents": data["price"],
                "date": data["date"]
            })
    
    # Add PA SREC placeholder (would need separate data source)
    prices["items"].append({
        "name": "PA SREC",
        "price": "$35.00",
        "raw_cents": 3500,
        "note": "Pennsylvania Solar Renewable Energy Credit"
    })
    
    return prices

def save_prices(prices, output_path="prices.json"):
    """Save prices to JSON file"""
    with open(output_path, "w") as f:
        json.dump(prices, f, indent=2)
    print(f"Saved prices to {output_path}")

def main():
    print(f"Fetching chicken prices at {datetime.now()}")
    
    if not API_KEY:
        print("ERROR: USDA_API_KEY environment variable not set")
        return 1
    
    prices = fetch_chicken_prices()
    
    if prices:
        save_prices(prices)
        print(f"Successfully updated {len(prices['items'])} price items")
        return 0
    else:
        print("Failed to fetch prices")
        return 1

if __name__ == "__main__":
    exit(main())
