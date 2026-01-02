#!/usr/bin/env python3
import os
import json
import requests

API_KEY = os.environ.get('USDA_API_KEY')
API_URL = "https://marsapi.ams.usda.gov/services/v1.2/reports/3646?allSections=true"

response = requests.get(API_URL, auth=(API_KEY, ''))
data = response.json()

print("=" * 50)
print("REPORT DETAIL SECTION (index 1)")
print("=" * 50)

# data is an array - [0] is Header, [1] is Detail
if isinstance(data, list) and len(data) > 1:
    detail = data[1]
    print(json.dumps(detail, indent=2)[:8000])
else:
    print("Unexpected format:")
    print(type(data))
    print(json.dumps(data, indent=2)[:3000])

print("=" * 50)
