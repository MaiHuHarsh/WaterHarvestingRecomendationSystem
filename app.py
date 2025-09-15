"""
Water Harvesting API - Flask Application
Provides personalized water harvesting recommendations for locations in India
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class WaterHarvestingCalculator:
    """Core calculation engine for water harvesting analysis"""

    def __init__(self):
        # Runoff coefficients by roof material
        self.runoff_coefficients = {
            'concrete': 0.85,
            'metal': 0.90,
            'tile': 0.75,
            'asbestos': 0.80,
            'thatch': 0.60,
            'other': 0.70
        }

        # Collection efficiency by system quality
        self.collection_efficiency = {
            'advanced': 0.90,
            'standard': 0.80,
            'basic': 0.70
        }

        # Cost estimates (INR)
        self.cost_estimates = {
            'tank_cost_per_liter': 85,
            'filtration_basic': 25000,
            'filtration_advanced': 40000,
            'pump_0_5hp': 12000,
            'pump_1hp': 18000,
            'installation_base': 20000,
            'contingency_factor': 0.10
        }

        # Water pricing (INR per 1000 liters) by region
        self.water_pricing = {
            'urban': 15,
            'suburban': 12,
            'rural': 8
        }

    def calculate_harvestable_water(self, roof_area_sqft: float, annual_rainfall_mm: float, 
                                  roof_material: str = 'concrete', system_quality: str = 'standard') -> float:
        """Calculate annual harvestable water volume in liters"""

        # Convert sq ft to sq meters
        roof_area_sqm = roof_area_sqft * 0.092903

        # Get coefficients
        runoff_coeff = self.runoff_coefficients.get(roof_material.lower(), 0.75)
        collection_eff = self.collection_efficiency.get(system_quality.lower(), 0.80)

        # Calculate harvestable water (in liters)
        harvestable_liters = roof_area_sqm * annual_rainfall_mm * runoff_coeff * collection_eff

        return round(harvestable_liters, 0)

    def calculate_monthly_potential(self, annual_harvest: float, rainfall_distribution: Dict[str, float]) -> Dict[str, float]:
        """Calculate monthly harvesting potential"""
        monthly_harvest = {}

        for month, percentage in rainfall_distribution.items():
            monthly_harvest[month] = round(annual_harvest * (percentage / 100), 0)

        return monthly_harvest

    def calculate_optimal_storage_size(self, monthly_harvest: Dict[str, float]) -> Dict[str, int]:
        """Calculate optimal storage tank sizes"""

        peak_monthly = max(monthly_harvest.values())

        min_size = max(3000, peak_monthly * 0.5)
        optimal_size = peak_monthly * 1.3
        max_beneficial = peak_monthly * 2.0

        return {
            'minimum_liters': int(min_size),
            'optimal_liters': int(optimal_size),
            'maximum_beneficial_liters': int(max_beneficial)
        }

    def calculate_system_cost(self, tank_capacity: int, system_type: str = 'standard') -> Dict[str, float]:
        """Calculate implementation costs"""

        tank_cost = tank_capacity * self.cost_estimates['tank_cost_per_liter']

        if system_type == 'advanced':
            filtration_cost = self.cost_estimates['filtration_advanced']
            pump_cost = self.cost_estimates['pump_1hp']
        else:
            filtration_cost = self.cost_estimates['filtration_basic']
            pump_cost = self.cost_estimates['pump_0_5hp']

        installation_cost = self.cost_estimates['installation_base']
        subtotal = tank_cost + filtration_cost + pump_cost + installation_cost
        contingency = subtotal * self.cost_estimates['contingency_factor']
        total_cost = subtotal + contingency

        return {
            'tank_cost': round(tank_cost, 0),
            'filtration_cost': round(filtration_cost, 0),
            'pump_cost': round(pump_cost, 0),
            'installation_cost': round(installation_cost, 0),
            'contingency': round(contingency, 0),
            'total_cost': round(total_cost, 0)
        }

    def calculate_financial_analysis(self, annual_harvest: float, total_cost: float, 
                                   region_type: str = 'urban') -> Dict[str, float]:
        """Calculate financial projections"""

        utilization_rate = 0.70
        usable_water = annual_harvest * utilization_rate
        water_rate = self.water_pricing.get(region_type, 12)
        annual_savings = (usable_water / 1000) * water_rate

        payback_period = total_cost / annual_savings if annual_savings > 0 else float('inf')
        total_20_year_savings = annual_savings * 20
        net_20_year_benefit = total_20_year_savings - total_cost
        roi_percentage = (net_20_year_benefit / total_cost) * 100 if total_cost > 0 else 0

        return {
            'annual_water_savings_liters': round(usable_water, 0),
            'annual_cost_savings_inr': round(annual_savings, 0),
            'payback_period_years': round(payback_period, 1),
            'total_20_year_savings': round(total_20_year_savings, 0),
            'net_20_year_benefit': round(net_20_year_benefit, 0),
            'roi_percentage': round(roi_percentage, 1)
        }


class WeatherDataService:
    """Service to fetch weather and rainfall data"""

    def __init__(self):
        self.open_meteo_base_url = "https://api.open-meteo.com/v1"

        # Fallback rainfall data for major cities
        self.fallback_rainfall_data = {
            'mumbai': {'annual': 2200, 'distribution': {'jan': 0.1, 'feb': 0.1, 'mar': 0.3, 'apr': 0.5, 'may': 1.8, 'jun': 18.5, 'jul': 28.2, 'aug': 26.8, 'sep': 16.4, 'oct': 4.1, 'nov': 1.3, 'dec': 0.2}},
            'delhi': {'annual': 797, 'distribution': {'jan': 2.1, 'feb': 2.5, 'mar': 4.2, 'apr': 3.7, 'may': 6.2, 'jun': 18.6, 'jul': 44.7, 'aug': 39.2, 'sep': 22.6, 'oct': 9.2, 'nov': 3.2, 'dec': 1.9}},
            'bangalore': {'annual': 970, 'distribution': {'jan': 0.3, 'feb': 0.5, 'mar': 2.1, 'apr': 4.8, 'may': 9.2, 'jun': 8.4, 'jul': 9.6, 'aug': 11.2, 'sep': 16.8, 'oct': 18.7, 'nov': 5.2, 'dec': 0.8}},
            'chennai': {'annual': 1400, 'distribution': {'jan': 1.8, 'feb': 0.7, 'mar': 1.1, 'apr': 2.3, 'may': 4.2, 'jun': 4.8, 'jul': 7.2, 'aug': 9.6, 'sep': 11.2, 'oct': 24.3, 'nov': 28.6, 'dec': 12.1}},
            'kolkata': {'annual': 1582, 'distribution': {'jan': 0.9, 'feb': 1.8, 'mar': 2.1, 'apr': 3.4, 'may': 7.2, 'jun': 19.8, 'jul': 26.4, 'aug': 25.6, 'sep': 18.9, 'oct': 7.8, 'nov': 1.2, 'dec': 0.3}},
            'hyderabad': {'annual': 812, 'distribution': {'jan': 0.6, 'feb': 1.2, 'mar': 1.8, 'apr': 2.4, 'may': 4.2, 'jun': 11.2, 'jul': 16.8, 'aug': 17.4, 'sep': 18.2, 'oct': 12.6, 'nov': 2.1, 'dec': 0.8}},
            'pune': {'annual': 722, 'distribution': {'jan': 0.2, 'feb': 0.3, 'mar': 0.8, 'apr': 1.2, 'may': 2.1, 'jun': 16.8, 'jul': 26.4, 'aug': 24.2, 'sep': 15.6, 'oct': 6.2, 'nov': 1.8, 'dec': 0.4}},
            'ahmedabad': {'annual': 803, 'distribution': {'jan': 0.3, 'feb': 0.2, 'mar': 0.6, 'apr': 0.8, 'may': 1.2, 'jun': 13.4, 'jul': 28.6, 'aug': 26.8, 'sep': 14.2, 'oct': 2.4, 'nov': 0.8, 'dec': 0.2}},
            'jaipur': {'annual': 650, 'distribution': {'jan': 1.8, 'feb': 1.2, 'mar': 2.1, 'apr': 2.8, 'may': 4.2, 'jun': 16.2, 'jul': 32.4, 'aug': 28.6, 'sep': 18.4, 'oct': 3.8, 'nov': 1.2, 'dec': 0.8}},
            'kochi': {'annual': 3055, 'distribution': {'jan': 0.8, 'feb': 1.2, 'mar': 2.4, 'apr': 4.8, 'may': 12.6, 'jun': 21.4, 'jul': 22.8, 'aug': 18.4, 'sep': 11.2, 'oct': 10.8, 'nov': 5.2, 'dec': 1.8}}
        }

    def get_city_from_coordinates(self, lat: float, lng: float) -> str:
        """Determine nearest major city from coordinates"""
        cities = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.6139, 77.2090),
            'bangalore': (12.9716, 77.5946),
            'chennai': (13.0827, 80.2707),
            'kolkata': (22.5726, 88.3639),
            'hyderabad': (17.3850, 78.4867),
            'pune': (18.5204, 73.8567),
            'ahmedabad': (23.0225, 72.5714),
            'jaipur': (26.9124, 75.7873),
            'kochi': (9.9312, 76.2673)
        }

        min_distance = float('inf')
        nearest_city = 'delhi'

        for city, (city_lat, city_lng) in cities.items():
            distance = math.sqrt((lat - city_lat)**2 + (lng - city_lng)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_city = city

        return nearest_city

    def get_rainfall_data(self, lat: float, lng: float) -> Dict:
        """Get rainfall data with fallback options"""

        try:
            # Try Open-Meteo API first
            response = requests.get(
                f"{self.open_meteo_base_url}/historical-weather",
                params={
                    'latitude': lat,
                    'longitude': lng,
                    'start_date': '2020-01-01',
                    'end_date': '2023-12-31',
                    'daily': 'precipitation_sum',
                    'timezone': 'Asia/Kolkata'
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_open_meteo_data(data)

        except Exception as e:
            logger.warning(f"Failed to fetch from Open-Meteo: {str(e)}")

        # Fallback to city-based data
        nearest_city = self.get_city_from_coordinates(lat, lng)
        return self.fallback_rainfall_data.get(nearest_city, self.fallback_rainfall_data['delhi'])

    def _process_open_meteo_data(self, data: Dict) -> Dict:
        """Process Open-Meteo historical data"""
        try:
            daily_data = data.get('daily', {})
            precipitation = daily_data.get('precipitation_sum', [])
            dates = daily_data.get('time', [])

            if not precipitation or not dates:
                return self.fallback_rainfall_data['delhi']

            monthly_totals = {month: 0 for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec']}

            month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                          'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

            for i, date_str in enumerate(dates):
                if i < len(precipitation):
                    month_idx = int(date_str.split('-')[1]) - 1
                    monthly_totals[month_names[month_idx]] += precipitation[i]

            annual_total = sum(monthly_totals.values())

            distribution = {}
            for month, total in monthly_totals.items():
                distribution[month] = round((total / annual_total * 100), 1) if annual_total > 0 else 0

            return {
                'annual': round(annual_total, 0),
                'distribution': distribution
            }

        except Exception as e:
            logger.error(f"Error processing Open-Meteo data: {str(e)}")
            return self.fallback_rainfall_data['delhi']


class SoilDataService:
    """Service to get soil and groundwater information"""

    def __init__(self):
        self.soil_data = {
            'alluvial': {'infiltration_rate': 'Medium (5-15 mm/hr)', 'suitability': 'Good for both storage and recharge'},
            'black': {'infiltration_rate': 'Low (1-5 mm/hr)', 'suitability': 'Better for storage systems'},
            'red': {'infiltration_rate': 'High (15-30 mm/hr)', 'suitability': 'Excellent for recharge'},
            'laterite': {'infiltration_rate': 'Medium-High (10-20 mm/hr)', 'suitability': 'Good for recharge'},
            'desert': {'infiltration_rate': 'Very High (20-50 mm/hr)', 'suitability': 'Excellent for recharge'},
            'mountain': {'infiltration_rate': 'Variable (5-25 mm/hr)', 'suitability': 'Site-specific assessment needed'}
        }

    def get_soil_type(self, lat: float, lng: float) -> Dict:
        """Get soil type based on geographical location"""

        # Simplified regional mapping
        if 20 <= lat <= 30 and 68 <= lng <= 78:
            soil_type = 'desert' if lng < 74 else 'alluvial'
        elif 18 <= lat <= 25 and 72 <= lng <= 85:
            soil_type = 'black'
        elif 8 <= lat <= 18 and 75 <= lng <= 80:
            soil_type = 'red'
        elif lat < 18 and lng > 75:
            soil_type = 'red'
        elif lat > 25 and lng > 85:
            soil_type = 'alluvial'
        elif lat > 28:
            soil_type = 'mountain'
        else:
            soil_type = 'alluvial'

        soil_info = self.soil_data.get(soil_type, self.soil_data['alluvial'])

        return {
            'soil_type': soil_type.title(),
            'infiltration_rate': soil_info['infiltration_rate'],
            'recharge_suitability': soil_info['suitability'],
            'groundwater_depth': self._estimate_groundwater_depth(lat, lng),
            'aquifer_prospects': self._assess_aquifer_prospects(soil_type)
        }

    def _estimate_groundwater_depth(self, lat: float, lng: float) -> str:
        """Estimate groundwater depth based on region"""
        if 20 <= lat <= 30 and lng < 75:
            return "20-50 meters"
        elif 18 <= lat <= 25:
            return "10-30 meters"
        elif lat < 18:
            return "5-20 meters"
        elif lng > 85:
            return "5-15 meters"
        else:
            return "10-25 meters"

    def _assess_aquifer_prospects(self, soil_type: str) -> str:
        """Assess aquifer prospects based on soil type"""
        prospects = {
            'alluvial': 'Excellent',
            'black': 'Good',
            'red': 'Moderate to Good',
            'laterite': 'Moderate',
            'desert': 'Poor to Moderate',
            'mountain': 'Variable'
        }
        return prospects.get(soil_type, 'Moderate')


# Create service instances
calculator = WaterHarvestingCalculator()
weather_service = WeatherDataService()
soil_service = SoilDataService()


# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })


@app.route('/api/v1/water-harvesting/analyze', methods=['POST'])
def analyze_water_harvesting():
    """Main API endpoint for water harvesting analysis"""

    try:
        # Get request data
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract location
        location = data.get('location', {})
        lat = location.get('lat')
        lng = location.get('lng')

        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400

        # Extract property details
        property_details = data.get('property', {})
        roof_area_sqft = property_details.get('roof_area_sqft')

        if not roof_area_sqft:
            return jsonify({'error': 'Roof area is required'}), 400

        # Extract usage patterns
        usage = data.get('usage', {})
        household_size = usage.get('household_size', 4)

        # Extract preferences
        preferences = data.get('preferences', {})
        system_type = preferences.get('system_type', 'standard')
        region_type = preferences.get('region_type', 'urban')
        roof_material = property_details.get('roof_material', 'concrete')

        # Get external data
        logger.info(f"Analyzing location: {lat}, {lng}")

        # Fetch weather data
        rainfall_data = weather_service.get_rainfall_data(lat, lng)

        # Fetch soil data
        soil_data = soil_service.get_soil_type(lat, lng)

        # Calculate harvestable water
        annual_harvest = calculator.calculate_harvestable_water(
            roof_area_sqft=roof_area_sqft,
            annual_rainfall_mm=rainfall_data['annual'],
            roof_material=roof_material,
            system_quality=system_type
        )

        # Calculate monthly potential
        monthly_harvest = calculator.calculate_monthly_potential(
            annual_harvest, rainfall_data['distribution']
        )

        # Calculate storage requirements
        storage_sizes = calculator.calculate_optimal_storage_size(monthly_harvest)

        # Calculate costs
        optimal_capacity = storage_sizes['optimal_liters']
        cost_analysis = calculator.calculate_system_cost(optimal_capacity, system_type)

        # Calculate financial analysis
        financial_analysis = calculator.calculate_financial_analysis(
            annual_harvest, cost_analysis['total_cost'], region_type
        )

        # Generate recommendations
        recommendations = generate_system_recommendations(
            roof_area_sqft, annual_harvest, storage_sizes, cost_analysis, soil_data
        )

        # Generate implementation plan
        implementation_plan = generate_implementation_plan(cost_analysis['total_cost'])

        # Build response
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'location': {
                'coordinates': {'lat': lat, 'lng': lng},
                'address': location.get('address', f'Location {lat}, {lng}'),
                'region_type': region_type
            },
            'climate_analysis': {
                'annual_rainfall_mm': rainfall_data['annual'],
                'rainfall_distribution': rainfall_data['distribution'],
                'peak_months': get_peak_rainfall_months(rainfall_data['distribution']),
                'collection_efficiency': 0.80 if system_type == 'standard' else 0.90
            },
            'soil_and_geology': soil_data,
            'harvesting_potential': {
                'roof_area_sqft': roof_area_sqft,
                'annual_harvestable_liters': annual_harvest,
                'monthly_potential': monthly_harvest,
                'storage_recommendations': storage_sizes
            },
            'system_recommendations': recommendations,
            'cost_analysis': cost_analysis,
            'financial_analysis': financial_analysis,
            'implementation_plan': implementation_plan,
            'maintenance_schedule': generate_maintenance_schedule(),
            'regulatory_info': generate_regulatory_info(lat, lng)
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in water harvesting analysis: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


def generate_system_recommendations(roof_area, annual_harvest, storage_sizes, cost_analysis, soil_data):
    """Generate system recommendations based on analysis"""

    primary_recommendation = {
        'system_type': 'Rooftop Harvesting with Storage Tank',
        'tank_capacity_liters': storage_sizes['optimal_liters'],
        'tank_material': 'Ferrocement or Food-grade PVC',
        'filtration_components': [
            'First flush diverter (200-300 liters)',
            'Coarse mesh filter',
            'Sand and activated carbon filter'
        ],
        'pump_specification': '0.5 HP centrifugal pump',
        'estimated_cost_inr': cost_analysis['total_cost']
    }

    alternative_options = []

    # Add recharge option if suitable
    if 'recharge' in soil_data['recharge_suitability'].lower():
        alternative_options.append({
            'type': 'Groundwater Recharge System',
            'components': ['Recharge pit', 'Filter chamber', 'Distribution system'],
            'estimated_cost_inr': cost_analysis['total_cost'] * 0.6,
            'benefits': 'Lower cost, groundwater enhancement, flood mitigation'
        })

    # Add hybrid option
    alternative_options.append({
        'type': 'Hybrid Storage + Recharge System',
        'storage_capacity_liters': storage_sizes['minimum_liters'],
        'components': ['Smaller storage tank', 'Overflow recharge pit'],
        'estimated_cost_inr': cost_analysis['total_cost'] * 0.8,
        'benefits': 'Best of both systems, optimal water security'
    })

    return {
        'primary_recommendation': primary_recommendation,
        'alternative_options': alternative_options,
        'suitability_score': calculate_suitability_score(annual_harvest, soil_data)
    }


def generate_implementation_plan(total_cost):
    """Generate phased implementation plan"""

    return {
        'total_duration': '4-6 weeks',
        'phases': [
            {
                'phase': 1,
                'name': 'Planning and Permits',
                'duration': '1-2 weeks',
                'activities': [
                    'Site survey and measurements',
                    'Permit applications',
                    'Material procurement',
                    'Contractor selection'
                ],
                'estimated_cost': round(total_cost * 0.15)
            },
            {
                'phase': 2,
                'name': 'Installation',
                'duration': '2-3 weeks',
                'activities': [
                    'Excavation for underground tank',
                    'Tank installation and waterproofing',
                    'Plumbing and pipe laying',
                    'Electrical connections'
                ],
                'estimated_cost': round(total_cost * 0.65)
            },
            {
                'phase': 3,
                'name': 'Testing and Commissioning',
                'duration': '1 week',
                'activities': [
                    'System testing and leak checks',
                    'Filtration system setup',
                    'Pump installation and testing',
                    'User training and handover'
                ],
                'estimated_cost': round(total_cost * 0.20)
            }
        ]
    }


def generate_maintenance_schedule():
    """Generate maintenance schedule"""

    return {
        'monthly_tasks': [
            'Visual inspection of gutters and downpipes',
            'Check first flush diverter',
            'Clean leaf guards and mesh filters',
            'Test pump operation'
        ],
        'quarterly_tasks': [
            'Clean storage tank (external)',
            'Replace/clean filter media',
            'Check pipe joints and connections',
            'Water quality testing'
        ],
        'annual_tasks': [
            'Complete tank cleaning and disinfection',
            'Professional system audit',
            'Replace worn components',
            'Pump servicing'
        ],
        'estimated_annual_cost': 4500
    }


def generate_regulatory_info(lat, lng):
    """Generate regulatory information based on location"""

    # Simplified state-based regulations
    state_regulations = {
        'delhi': {
            'mandate': 'Mandatory for plots >100 sq m',
            'subsidy': 'Up to ₹15,000 for residential',
            'authority': 'Delhi Jal Board'
        },
        'karnataka': {
            'mandate': 'Mandatory for plots >60×40 feet',
            'subsidy': 'Up to ₹10,000 for residential',
            'authority': 'Karnataka Urban Water Supply'
        },
        'tamil nadu': {
            'mandate': 'Mandatory for all new buildings',
            'subsidy': 'Up to ₹12,000 for residential',
            'authority': 'Tamil Nadu Water Supply'
        }
    }

    # Default regulatory info
    return {
        'local_mandate': 'Check with local municipal corporation',
        'required_permits': ['Building plan approval', 'Plumbing permit'],
        'available_subsidies': 'Contact local water authority',
        'compliance_timeline': 'Usually required before occupancy certificate',
        'penalty_non_compliance': 'May affect water connection approval'
    }


def get_peak_rainfall_months(distribution):
    """Get peak rainfall months from distribution"""
    sorted_months = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    return [month for month, _ in sorted_months[:3]]


def calculate_suitability_score(annual_harvest, soil_data):
    """Calculate overall suitability score"""

    base_score = min(100, (annual_harvest / 10000) * 50)  # Up to 50 points for harvest potential

    # Soil suitability bonus
    if 'excellent' in soil_data['recharge_suitability'].lower():
        soil_bonus = 30
    elif 'good' in soil_data['recharge_suitability'].lower():
        soil_bonus = 20
    else:
        soil_bonus = 10

    # Groundwater depth consideration
    if '5-15' in soil_data['groundwater_depth']:
        depth_bonus = 20
    elif '10-25' in soil_data['groundwater_depth']:
        depth_bonus = 15
    else:
        depth_bonus = 10

    total_score = min(100, base_score + soil_bonus + depth_bonus)
    return round(total_score, 1)


@app.route('/api/v1/rainfall/<float:lat>/<float:lng>', methods=['GET'])
def get_rainfall_data(lat, lng):
    """Get rainfall data for specific coordinates"""

    try:
        rainfall_data = weather_service.get_rainfall_data(lat, lng)

        return jsonify({
            'status': 'success',
            'location': {'lat': lat, 'lng': lng},
            'rainfall_data': rainfall_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/soil/<float:lat>/<float:lng>', methods=['GET'])
def get_soil_data(lat, lng):
    """Get soil data for specific coordinates"""

    try:
        soil_data = soil_service.get_soil_type(lat, lng)

        return jsonify({
            'status': 'success',
            'location': {'lat': lat, 'lng': lng},
            'soil_data': soil_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
