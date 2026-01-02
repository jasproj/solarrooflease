#!/usr/bin/env python3
import os
import json
import requests

API_KEY = os.environ.get('USDA_API_KEY')
API_URL = "https://marsapi.ams.usda.gov/services/v1.2/reports/3646?allSections=true"

response = requests.get(API_URL, auth=(API_KEY, ''))
data = response.json()

print("=" * 50)
print("USDA API RAW RESPONSE (with allSections=true)")
print("=" * 50)
print(json.dumps(data, indent=2)[:8000])
print("=" * 50)
