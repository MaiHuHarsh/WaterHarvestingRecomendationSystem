import requests, json

data = {
    "location": {"lat": 28.6139, "lng": 77.2090},
    "property": {"roof_area_sqft": 1200, "roof_material": "concrete"},
    "usage": {"household_size": 4, "daily_consumption_liters": 600},
    "preferences": {"budget_range": "75000-150000", "system_type": "standard"}
}

response = requests.post('http://localhost:5000/api/v1/water-harvesting/analyze', json=data)
result = response.json()

with open("data.json", "w") as json_file:
    json.dump(result, json_file, indent=4)

# print(f"Annual Harvest: {result['harvesting_potential']['annual_harvestable_liters']} L")
# print(f"Recommended Tank: {result['system_recommendations']['primary_recommendation']['tank_capacity_liters']} L") 
# print(f"Total Cost: ₹{result['cost_analysis']['total_cost']:,.0f}")

