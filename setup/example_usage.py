#!/usr/bin/env python3
"""
Example usage of Water Harvesting API
"""

import requests
import json

# API base URL
BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_water_harvesting_analysis():
    """Test main water harvesting analysis"""
    print("Testing water harvesting analysis...")

    # Sample request data
    data = {
        "location": {
            "lat": 28.6139,
            "lng": 77.2090,
            "address": "New Delhi, India"
        },
        "property": {
            "type": "residential",
            "roof_area_sqft": 1200,
            "roof_material": "concrete",
            "floors": 2
        },
        "usage": {
            "household_size": 4,
            "daily_consumption_liters": 600
        },
        "preferences": {
            "budget_range": "75000-150000",
            "system_type": "standard",
            "region_type": "urban"
        }
    }

    response = requests.post(
        f'{BASE_URL}/api/v1/water-harvesting/analyze',
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Annual Harvestable Water: {result['harvesting_potential']['annual_harvestable_liters']} liters")
        print(f"Recommended Tank Size: {result['system_recommendations']['primary_recommendation']['tank_capacity_liters']} liters")
        print(f"Total Cost: ₹{result['cost_analysis']['total_cost']:,.0f}")
        print(f"Annual Savings: ₹{result['financial_analysis']['annual_cost_savings_inr']:,.0f}")
        print(f"Payback Period: {result['financial_analysis']['payback_period_years']} years")
    else:
        print(f"Error: {response.text}")

    print()

def test_rainfall_data():
    """Test rainfall data endpoint"""
    print("Testing rainfall data...")
    lat, lng = 19.0760, 72.8777  # Mumbai coordinates

    response = requests.get(f'{BASE_URL}/api/v1/rainfall/{lat}/{lng}')
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Annual Rainfall: {result['rainfall_data']['annual']} mm")
        print(f"Peak Month Distribution: {max(result['rainfall_data']['distribution'].items(), key=lambda x: x[1])}")
    else:
        print(f"Error: {response.text}")

    print()

def test_soil_data():
    """Test soil data endpoint"""
    print("Testing soil data...")
    lat, lng = 12.9716, 77.5946  # Bangalore coordinates

    response = requests.get(f'{BASE_URL}/api/v1/soil/{lat}/{lng}')
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Soil Type: {result['soil_data']['soil_type']}")
        print(f"Infiltration Rate: {result['soil_data']['infiltration_rate']}")
        print(f"Groundwater Depth: {result['soil_data']['groundwater_depth']}")
    else:
        print(f"Error: {response.text}")

    print()

def main():
    """Run all tests"""
    print("Water Harvesting API - Example Usage")
    print("=" * 40)

    try:
        test_health_check()
        test_water_harvesting_analysis()
        test_rainfall_data()
        test_soil_data()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the Flask application is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
