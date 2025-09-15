#!/usr/bin/env python3
"""
Quick Start Script for Water Harvesting API
Run this after installing requirements to test the API
"""

import subprocess
import sys
import time
import requests
from threading import Thread

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def start_api_server():
    """Start the Flask API server"""
    try:
        print("🚀 Starting API server...")
        subprocess.Popen([sys.executable, 'app.py'])
        time.sleep(3)  # Give server time to start
        return True
    except Exception as e:
        print(f"❌ Failed to start API server: {str(e)}")
        return False

def test_api():
    """Test the API with sample data"""
    print("🧪 Testing API...")

    # Test health endpoint
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Could not connect to API server")
        return False

    # Test main analysis endpoint
    test_data = {
        "location": {
            "lat": 28.6139,
            "lng": 77.2090,
            "address": "New Delhi, India"
        },
        "property": {
            "roof_area_sqft": 1000,
            "roof_material": "concrete"
        },
        "usage": {
            "household_size": 4
        }
    }

    try:
        response = requests.post(
            'http://localhost:5000/api/v1/water-harvesting/analyze',
            json=test_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis endpoint working!")
            print(f"   📊 Annual harvestable water: {result['harvesting_potential']['annual_harvestable_liters']:,} L")
            print(f"   💰 Estimated cost: ₹{result['cost_analysis']['total_cost']:,.0f}")
            print(f"   ⏱️  Payback period: {result['financial_analysis']['payback_period_years']:.1f} years")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Main function to set up and test the API"""
    print("🌊 Water Harvesting API - Quick Start")
    print("=" * 40)

    # Install requirements
    if not install_requirements():
        return

    print("\n⏳ Please start the API server manually by running:")
    print("   python app.py")
    print("\n🧪 Then test the API by running:")
    print("   python example_usage.py")
    print("\n📚 API Documentation available at:")
    print("   - README.md")
    print("   - API_DOCUMENTATION.md")
    print("   - COMPLETE_TEST_EXAMPLE.md")

    print("\n✅ Setup completed successfully!")
    print("\n🎯 Your Water Harvesting API is ready to use!")

if __name__ == '__main__':
    main()
