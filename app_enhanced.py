"""
Water Harvesting API - Enhanced Flask Application
Provides personalized water harvesting recommendations for locations in India
Updated with comprehensive feasibility analysis and structure recommendations
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
    """Enhanced calculation engine for water harvesting analysis"""

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

        # Enhanced cost estimates (INR)
        self.cost_estimates = {
            'tank_cost_per_liter': 85,
            'filtration_basic': 25000,
            'filtration_advanced': 40000,
            'pump_0_5hp': 12000,
            'pump_1hp': 18000,
            'installation_base': 20000,
            'contingency_factor': 0.10,
            # Recharge structure costs
            'recharge_pit_per_cum': 2500,
            'percolation_tank_per_cum': 1800,
            'injection_well_base': 45000,
            'recharge_trench_per_meter': 1200,
            'check_dam_base': 75000
        }

        # Water pricing (INR per 1000 liters) by region
        self.water_pricing = {
            'urban': 15,
            'suburban': 12,
            'rural': 8
        }

    def calculate_feasibility_score(self, annual_rainfall: float, roof_area: float, 
                                  soil_data: Dict, household_size: int) -> Dict:
        """Calculate comprehensive feasibility score for RTRWH"""

        scores = {}

        # Rainfall feasibility (0-25 points)
        if annual_rainfall >= 1000:
            scores['rainfall'] = 25
        elif annual_rainfall >= 750:
            scores['rainfall'] = 20
        elif annual_rainfall >= 500:
            scores['rainfall'] = 15
        elif annual_rainfall >= 300:
            scores['rainfall'] = 10
        else:
            scores['rainfall'] = 5

        # Roof area feasibility (0-25 points)
        if roof_area >= 1500:
            scores['roof_area'] = 25
        elif roof_area >= 1000:
            scores['roof_area'] = 20
        elif roof_area >= 600:
            scores['roof_area'] = 15
        elif roof_area >= 300:
            scores['roof_area'] = 10
        else:
            scores['roof_area'] = 5

        # Soil suitability (0-25 points)
        soil_type = soil_data.get('soil_type', '').lower()
        if 'alluvial' in soil_type:
            scores['soil_suitability'] = 25
        elif 'red' in soil_type:
            scores['soil_suitability'] = 20
        elif 'black' in soil_type:
            scores['soil_suitability'] = 15
        elif 'laterite' in soil_type:
            scores['soil_suitability'] = 18
        else:
            scores['soil_suitability'] = 12

        # Water demand feasibility (0-25 points)
        daily_demand = household_size * 150  # 150L per person
        monthly_demand = daily_demand * 30
        if monthly_demand <= 10000:
            scores['water_demand'] = 25
        elif monthly_demand <= 20000:
            scores['water_demand'] = 20
        elif monthly_demand <= 30000:
            scores['water_demand'] = 15
        else:
            scores['water_demand'] = 10

        total_score = sum(scores.values())

        # Feasibility classification
        if total_score >= 80:
            feasibility = "Highly Feasible"
            recommendation = "Excellent conditions for RTRWH implementation"
        elif total_score >= 65:
            feasibility = "Feasible"
            recommendation = "Good conditions with minor considerations"
        elif total_score >= 50:
            feasibility = "Moderately Feasible"
            recommendation = "Feasible with proper planning and design"
        elif total_score >= 35:
            feasibility = "Low Feasibility"
            recommendation = "Consider alternative water sources or hybrid systems"
        else:
            feasibility = "Not Feasible"
            recommendation = "RTRWH not recommended for this location"

        return {
            'total_score': total_score,
            'max_score': 100,
            'score_breakdown': scores,
            'feasibility_level': feasibility,
            'recommendation': recommendation
        }

    def suggest_rtrwh_structures(self, annual_harvest: float, soil_data: Dict, 
                               roof_area: float, budget: str = None) -> Dict:
        """Suggest appropriate RTRWH and artificial recharge structures"""

        structures = {
            'rooftop_harvesting': [],
            'artificial_recharge': [],
            'hybrid_systems': []
        }

        # Rooftop Harvesting Options
        if annual_harvest > 15000:
            structures['rooftop_harvesting'].append({
                'type': 'Underground Storage Tank',
                'capacity_range': '8000-15000 liters',
                'suitability': 'High water yield areas',
                'advantages': ['Reliable water supply', 'Space efficient', 'Good water quality'],
                'disadvantages': ['Higher initial cost', 'Regular maintenance needed']
            })

        structures['rooftop_harvesting'].append({
            'type': 'Overhead Storage Tank',
            'capacity_range': '3000-8000 liters',
            'suitability': 'All roof areas',
            'advantages': ['Lower installation cost', 'Easy maintenance', 'Gravity feed'],
            'disadvantages': ['Space requirement', 'Limited capacity']
        })

        # Artificial Recharge Options
        soil_type = soil_data.get('soil_type', '').lower()
        infiltration = soil_data.get('infiltration_rate', '').lower()

        if 'high' in infiltration or 'excellent' in soil_data.get('recharge_suitability', '').lower():
            structures['artificial_recharge'].extend([
                {
                    'type': 'Recharge Pit',
                    'dimensions': '2m x 2m x 3m depth',
                    'suitability': 'High infiltration soils',
                    'capacity': '12 cubic meters',
                    'cost_estimate': 30000,
                    'maintenance': 'Annual cleaning and de-silting'
                },
                {
                    'type': 'Percolation Tank',
                    'dimensions': '10m x 5m x 2.5m depth',
                    'suitability': 'Large catchment areas',
                    'capacity': '125 cubic meters',
                    'cost_estimate': 225000,
                    'maintenance': 'Bi-annual cleaning'
                }
            ])

        if 'medium' in infiltration:
            structures['artificial_recharge'].extend([
                {
                    'type': 'Recharge Trench',
                    'dimensions': '0.5m wide x 1.5m deep x 10m length',
                    'suitability': 'Medium infiltration soils',
                    'capacity': '7.5 cubic meters',
                    'cost_estimate': 12000,
                    'maintenance': 'Quarterly inspection'
                },
                {
                    'type': 'Injection Well',
                    'dimensions': '150mm diameter x 30m depth',
                    'suitability': 'Low permeability areas',
                    'capacity': 'Direct injection to aquifer',
                    'cost_estimate': 45000,
                    'maintenance': 'Annual pump testing'
                }
            ])

        # Hybrid Systems
        structures['hybrid_systems'].append({
            'type': 'Storage + Recharge Combination',
            'description': 'Small storage tank with overflow to recharge pit',
            'storage_capacity': '5000 liters',
            'recharge_capacity': '8 cubic meters',
            'advantages': ['Water security + groundwater enhancement', 'Cost effective'],
            'total_cost_estimate': 85000
        })

        return structures

    def get_aquifer_information(self, lat: float, lng: float, soil_data: Dict) -> Dict:
        """Get principal aquifer information based on location and soil type"""

        # Regional aquifer mapping (simplified)
        aquifer_info = {}

        # Determine region-based aquifer characteristics
        if 20 <= lat <= 30 and 68 <= lng <= 78:  # Northwestern India
            if lng < 74:  # Rajasthan/Gujarat
                aquifer_info = {
                    'principal_aquifer': 'Thar Desert Aquifer System',
                    'aquifer_type': 'Unconfined to semi-confined',
                    'lithology': 'Sand and sandstone with clay lenses',
                    'water_quality': 'Saline to fresh (TDS: 500-5000 mg/L)',
                    'yield_characteristics': 'Low to moderate (5-20 m³/hr)',
                    'sustainability': 'Over-exploited in most areas'
                }
            else:  # Punjab/Haryana/UP plains
                aquifer_info = {
                    'principal_aquifer': 'Indo-Gangetic Alluvial Aquifer',
                    'aquifer_type': 'Unconfined to confined multi-layered',
                    'lithology': 'Fine to coarse alluvium with clay layers',
                    'water_quality': 'Fresh to brackish (TDS: 200-1500 mg/L)',
                    'yield_characteristics': 'High (20-100 m³/hr)',
                    'sustainability': 'Over-exploited to critical'
                }
        elif 18 <= lat <= 25 and 72 <= lng <= 85:  # Central India
            aquifer_info = {
                'principal_aquifer': 'Deccan Trap Aquifer',
                'aquifer_type': 'Fractured hard rock',
                'lithology': 'Basaltic lava flows with vesicular zones',
                'water_quality': 'Fresh to slightly saline (TDS: 300-2000 mg/L)',
                'yield_characteristics': 'Moderate (10-50 m³/hr)',
                'sustainability': 'Semi-critical to critical'
            }
        elif lat < 18:  # South India
            aquifer_info = {
                'principal_aquifer': 'Crystalline Rock Aquifer',
                'aquifer_type': 'Fractured and weathered hard rock',
                'lithology': 'Granite, gneiss with weathered overburden',
                'water_quality': 'Fresh (TDS: 200-1000 mg/L)',
                'yield_characteristics': 'Low to moderate (5-30 m³/hr)',
                'sustainability': 'Semi-critical to safe'
            }
        elif lng > 85:  # Eastern India
            aquifer_info = {
                'principal_aquifer': 'Bengal Basin Aquifer',
                'aquifer_type': 'Multi-layered confined/unconfined',
                'lithology': 'Quaternary alluvium with clay aquitards',
                'water_quality': 'Fresh but arsenic contamination risk',
                'yield_characteristics': 'High (30-150 m³/hr)',
                'sustainability': 'Safe to semi-critical'
            }
        else:  # Default/Himalayan region
            aquifer_info = {
                'principal_aquifer': 'Himalayan Rock Aquifer',
                'aquifer_type': 'Fractured rock with limited storage',
                'lithology': 'Metamorphic and sedimentary rocks',
                'water_quality': 'Fresh (TDS: 100-500 mg/L)',
                'yield_characteristics': 'Low (2-15 m³/hr)',
                'sustainability': 'Safe but limited availability'
            }

        # Add recharge potential assessment
        soil_type = soil_data.get('soil_type', '').lower()
        if 'alluvial' in soil_type:
            aquifer_info['recharge_potential'] = 'High - Good connectivity with surface'
        elif 'black' in soil_type:
            aquifer_info['recharge_potential'] = 'Moderate - Limited vertical percolation'
        elif 'red' in soil_type:
            aquifer_info['recharge_potential'] = 'High - Good infiltration capacity'
        else:
            aquifer_info['recharge_potential'] = 'Variable - Site-specific assessment needed'

        return aquifer_info

    def calculate_runoff_capacity(self, roof_area: float, rainfall_data: Dict, 
                                roof_material: str) -> Dict:
        """Calculate detailed runoff generation capacity"""

        runoff_coeff = self.runoff_coefficients.get(roof_material.lower(), 0.75)
        annual_rainfall = rainfall_data.get('annual', 800)
        monthly_distribution = rainfall_data.get('distribution', {})

        # Convert roof area to square meters
        roof_area_sqm = roof_area * 0.092903

        # Calculate monthly runoff
        monthly_runoff = {}
        total_annual_runoff = 0

        for month, percentage in monthly_distribution.items():
            monthly_rainfall = annual_rainfall * (percentage / 100)
            monthly_runoff_vol = roof_area_sqm * monthly_rainfall * runoff_coeff / 1000  # in cubic meters
            monthly_runoff[month] = {
                'rainfall_mm': round(monthly_rainfall, 1),
                'runoff_volume_liters': round(monthly_runoff_vol * 1000, 0),
                'runoff_volume_cubic_meters': round(monthly_runoff_vol, 2)
            }
            total_annual_runoff += monthly_runoff_vol

        # Peak runoff calculations
        peak_month = max(monthly_distribution.items(), key=lambda x: x[1])
        peak_monthly_runoff = monthly_runoff[peak_month[0]]['runoff_volume_liters']

        # Daily peak calculations (assuming 20% of monthly rain in peak day)
        peak_daily_runoff = peak_monthly_runoff * 0.20

        return {
            'roof_area_sqm': round(roof_area_sqm, 2),
            'runoff_coefficient': runoff_coeff,
            'annual_runoff_capacity': {
                'total_liters': round(total_annual_runoff * 1000, 0),
                'total_cubic_meters': round(total_annual_runoff, 2)
            },
            'monthly_runoff_details': monthly_runoff,
            'peak_runoff': {
                'peak_month': peak_month[0],
                'peak_monthly_liters': peak_monthly_runoff,
                'estimated_peak_daily_liters': round(peak_daily_runoff, 0)
            },
            'runoff_characteristics': {
                'collection_efficiency_factor': 0.85,  # Accounting for losses
                'first_flush_diversion': '2-3mm rainfall (initial runoff to be discarded)',
                'quality_parameters': 'Good for non-potable uses after basic filtration'
            }
        }

    def design_recharge_structures(self, annual_runoff: float, soil_data: Dict, 
                                 available_space: float = None) -> Dict:
        """Design specifications for recharge pits, trenches, and shafts"""

        designs = {}
        soil_type = soil_data.get('soil_type', '').lower()
        infiltration_rate = soil_data.get('infiltration_rate', '').lower()

        # Determine infiltration rate in mm/hr for calculations
        if 'high' in infiltration_rate:
            inf_rate_mm_hr = 20
        elif 'medium' in infiltration_rate:
            inf_rate_mm_hr = 10
        else:
            inf_rate_mm_hr = 5

        # Design Recharge Pits
        recommended_pits = max(1, math.ceil(annual_runoff / 15000))  # 15,000L per pit capacity

        designs['recharge_pits'] = {
            'number_recommended': recommended_pits,
            'individual_pit_specifications': {
                'length': '2.0 meters',
                'width': '2.0 meters', 
                'depth': '3.0 meters',
                'volume': '12 cubic meters',
                'side_wall_construction': 'Honey-comb brick work or perforated concrete rings',
                'bottom_filling': '60cm gravel (20-40mm) + 30cm coarse sand',
                'top_cover': 'Perforated concrete slab with inspection chamber'
            },
            'total_recharge_capacity': f'{recommended_pits * 12} cubic meters',
            'construction_cost': recommended_pits * 30000,
            'maintenance_requirements': [
                'Annual cleaning of silt accumulation',
                'Replacement of filter media every 3-5 years',
                'Quarterly inspection during monsoon'
            ]
        }

        # Design Recharge Trenches
        trench_length = min(50, annual_runoff / 500)  # 500L per meter capacity

        designs['recharge_trenches'] = {
            'recommended_configuration': 'Network of interconnected trenches',
            'specifications': {
                'total_length': f'{round(trench_length, 1)} meters',
                'width': '0.5 meters',
                'depth': '1.5 meters',
                'spacing_between_trenches': '5-10 meters',
                'gradient': '1:100 to 1:200 (gentle slope)',
                'backfill_material': 'Graded filter media (gravel + sand + brick aggregate)'
            },
            'total_capacity': f'{round(trench_length * 0.75, 1)} cubic meters',
            'construction_cost': round(trench_length * 1200, 0),
            'suitability': 'Ideal for large open areas with gentle slope'
        }

        # Design Injection Wells/Shafts
        if inf_rate_mm_hr < 10:  # For low permeability soils
            designs['injection_wells'] = {
                'type': 'Bore well recharge shaft',
                'specifications': {
                    'diameter': '150-200mm',
                    'depth': '25-40 meters (depending on water table)',
                    'casing': 'PVC slotted casing in water bearing zone',
                    'gravel_pack': '20-40mm gravel around slotted zone',
                    'surface_chamber': '1m x 1m x 1m concrete chamber with silt trap'
                },
                'recharge_rate': f'{round(annual_runoff * 0.8, 0)} liters annually',
                'construction_cost': 45000,
                'advantages': [
                    'Direct recharge to aquifer',
                    'Suitable for low permeability soils',
                    'Space efficient'
                ]
            }

        # Design Check Dams (for larger catchments)
        if annual_runoff > 50000:  # For large runoff volumes
            designs['check_dams'] = {
                'type': 'Small check dam across seasonal drainage',
                'specifications': {
                    'height': '1.5-2.5 meters',
                    'length': '15-25 meters (depending on drain width)',
                    'spillway_width': '3-5 meters',
                    'foundation_depth': '1.0-1.5 meters',
                    'construction_material': 'Stone masonry or concrete blocks'
                },
                'storage_capacity': '500-1500 cubic meters',
                'construction_cost': 75000,
                'recharge_benefit': 'Increased groundwater recharge in upstream area'
            }

        return designs

    def enhanced_cost_benefit_analysis(self, system_cost: float, annual_harvest: float,
                                     annual_savings: float, recharge_benefit: float = 0) -> Dict:
        """Enhanced cost-benefit analysis with multiple scenarios"""

        analysis = {}

        # Base financial metrics
        if annual_savings > 0:
            payback_period = system_cost / annual_savings
        else:
            payback_period = float('inf')

        # NPV calculation (10% discount rate)
        discount_rate = 0.10
        project_life = 20

        npv = 0
        for year in range(1, project_life + 1):
            cash_flow = annual_savings + (recharge_benefit * 0.1)  # 10% of recharge value
            npv += cash_flow / ((1 + discount_rate) ** year)

        npv = npv - system_cost

        # IRR calculation (simplified)
        if annual_savings > 0:
            irr = (annual_savings / system_cost) * 100
        else:
            irr = 0

        analysis['financial_metrics'] = {
            'initial_investment': system_cost,
            'annual_cost_savings': annual_savings,
            'simple_payback_period_years': round(payback_period, 1),
            'net_present_value_20_years': round(npv, 0),
            'internal_rate_of_return_percent': round(irr, 1),
            'benefit_cost_ratio': round(npv / system_cost + 1, 2) if system_cost > 0 else 0
        }

        # Water security benefits (qualitative to quantitative)
        water_security_value = annual_harvest * 2  # ₹2 per liter security premium

        analysis['non_financial_benefits'] = {
            'water_security_value_inr': round(water_security_value, 0),
            'groundwater_recharge_benefit': f'{round(annual_harvest * 0.3, 0)} liters/year',
            'flood_mitigation_benefit': 'Reduced surface runoff and urban flooding',
            'environmental_benefits': [
                'Reduced strain on municipal water supply',
                'Lower carbon footprint (reduced pumping)',
                'Enhanced local groundwater levels',
                'Reduced soil erosion and surface runoff'
            ]
        }

        # Sensitivity analysis
        analysis['sensitivity_analysis'] = {
            'optimistic_scenario': {
                'condition': '25% higher water savings',
                'payback_period_years': round(payback_period / 1.25, 1) if payback_period != float('inf') else 'N/A',
                'npv_inr': round(npv * 1.4, 0)
            },
            'pessimistic_scenario': {
                'condition': '25% lower water savings',
                'payback_period_years': round(payback_period / 0.75, 1) if payback_period != float('inf') else 'N/A',
                'npv_inr': round(npv * 0.6, 0)
            }
        }

        # Risk assessment
        risk_factors = []
        if payback_period > 15:
            risk_factors.append('Long payback period - consider subsidies')
        if annual_harvest < 5000:
            risk_factors.append('Low water yield - verify rainfall patterns')
        if system_cost > 150000:
            risk_factors.append('High initial investment - explore phased implementation')

        analysis['risk_assessment'] = {
            'risk_level': 'Low' if len(risk_factors) == 0 else 'Medium' if len(risk_factors) <= 2 else 'High',
            'risk_factors': risk_factors,
            'mitigation_strategies': [
                'Apply for government subsidies and incentives',
                'Consider phased implementation approach',
                'Implement hybrid storage + recharge system',
                'Regular maintenance to ensure optimal performance'
            ]
        }

        return analysis

    # Existing methods remain the same...
    def calculate_harvestable_water(self, roof_area_sqft: float, annual_rainfall_mm: float, 
                                  roof_material: str = 'concrete', system_quality: str = 'standard') -> float:
        """Calculate annual harvestable water volume in liters"""
        roof_area_sqm = roof_area_sqft * 0.092903
        runoff_coeff = self.runoff_coefficients.get(roof_material.lower(), 0.75)
        collection_eff = self.collection_efficiency.get(system_quality.lower(), 0.80)
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


# Keep existing WeatherDataService and SoilDataService classes unchanged
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
            'mumbai': (19.0760, 72.8777), 'delhi': (28.6139, 77.2090), 'bangalore': (12.9716, 77.5946),
            'chennai': (13.0827, 80.2707), 'kolkata': (22.5726, 88.3639), 'hyderabad': (17.3850, 78.4867),
            'pune': (18.5204, 73.8567), 'ahmedabad': (23.0225, 72.5714), 'jaipur': (26.9124, 75.7873),
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
            response = requests.get(
                f"{self.open_meteo_base_url}/historical-weather",
                params={
                    'latitude': lat, 'longitude': lng, 'start_date': '2020-01-01',
                    'end_date': '2023-12-31', 'daily': 'precipitation_sum',
                    'timezone': 'Asia/Kolkata'
                }, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_open_meteo_data(data)

        except Exception as e:
            logger.warning(f"Failed to fetch from Open-Meteo: {str(e)}")

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

            return {'annual': round(annual_total, 0), 'distribution': distribution}

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
            'alluvial': 'Excellent', 'black': 'Good', 'red': 'Moderate to Good',
            'laterite': 'Moderate', 'desert': 'Poor to Moderate', 'mountain': 'Variable'
        }
        return prospects.get(soil_type, 'Moderate')


# Create service instances
calculator = WaterHarvestingCalculator()
weather_service = WeatherDataService()
soil_service = SoilDataService()

print("Enhanced Water Harvesting Calculator created with all requested features!")
print("New capabilities added:")
print("✓ Feasibility check for RTRWH")
print("✓ Suggested RTRWH/Artificial Recharge structures")
print("✓ Principal aquifer information")
print("✓ Detailed runoff generation capacity")
print("✓ Recommended dimensions for recharge structures")
print("✓ Enhanced cost-benefit analysis")

# API Routes and Supporting Functions for Enhanced Water Harvesting API

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'features': [
            'Feasibility Analysis',
            'RTRWH Structure Recommendations', 
            'Aquifer Information',
            'Runoff Capacity Analysis',
            'Recharge Structure Designs',
            'Enhanced Cost-Benefit Analysis'
        ]
    })


@app.route('/api/v1/water-harvesting/analyze', methods=['POST'])
def analyze_water_harvesting():
    """Enhanced main API endpoint for comprehensive water harvesting analysis"""

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

        # Extract other parameters
        usage = data.get('usage', {})
        household_size = usage.get('household_size', 4)
        preferences = data.get('preferences', {})
        system_type = preferences.get('system_type', 'standard')
        region_type = preferences.get('region_type', 'urban')
        roof_material = property_details.get('roof_material', 'concrete')
        budget_range = preferences.get('budget_range', '75000-150000')

        logger.info(f"Enhanced analysis for location: {lat}, {lng}")

        # Fetch external data
        rainfall_data = weather_service.get_rainfall_data(lat, lng)
        soil_data = soil_service.get_soil_type(lat, lng)

        # 1. FEASIBILITY CHECK FOR RTRWH
        feasibility_analysis = calculator.calculate_feasibility_score(
            annual_rainfall=rainfall_data['annual'],
            roof_area=roof_area_sqft,
            soil_data=soil_data,
            household_size=household_size
        )

        # 2. Calculate harvestable water and runoff capacity
        annual_harvest = calculator.calculate_harvestable_water(
            roof_area_sqft=roof_area_sqft,
            annual_rainfall_mm=rainfall_data['annual'],
            roof_material=roof_material,
            system_quality=system_type
        )

        # 3. RUNOFF GENERATION CAPACITY
        runoff_capacity = calculator.calculate_runoff_capacity(
            roof_area=roof_area_sqft,
            rainfall_data=rainfall_data,
            roof_material=roof_material
        )

        # 4. Monthly potential and storage sizing
        monthly_harvest = calculator.calculate_monthly_potential(
            annual_harvest, rainfall_data['distribution']
        )

        storage_sizes = calculator.calculate_optimal_storage_size(monthly_harvest)

        # 5. SUGGESTED RTRWH/ARTIFICIAL RECHARGE STRUCTURES  
        structure_recommendations = calculator.suggest_rtrwh_structures(
            annual_harvest=annual_harvest,
            soil_data=soil_data,
            roof_area=roof_area_sqft,
            budget=budget_range
        )

        # 6. PRINCIPAL AQUIFER INFORMATION
        aquifer_info = calculator.get_aquifer_information(lat, lng, soil_data)

        # 7. RECHARGE STRUCTURE DIMENSIONS
        recharge_designs = calculator.design_recharge_structures(
            annual_runoff=annual_harvest,
            soil_data=soil_data,
            available_space=property_details.get('plot_area_sqft', 2000)
        )

        # 8. Cost analysis
        optimal_capacity = storage_sizes['optimal_liters']
        cost_analysis = calculator.calculate_system_cost(optimal_capacity, system_type)

        # Basic financial analysis
        basic_financial = calculator.calculate_financial_analysis(
            annual_harvest, cost_analysis['total_cost'], region_type
        )

        # 9. ENHANCED COST-BENEFIT ANALYSIS
        recharge_benefit = annual_harvest * 0.3 * 2  # 30% recharge at ₹2/liter value
        enhanced_cost_benefit = calculator.enhanced_cost_benefit_analysis(
            system_cost=cost_analysis['total_cost'],
            annual_harvest=annual_harvest,
            annual_savings=basic_financial['annual_cost_savings_inr'],
            recharge_benefit=recharge_benefit
        )

        # Generate additional recommendations
        system_recommendations = generate_enhanced_system_recommendations(
            roof_area_sqft, annual_harvest, storage_sizes, cost_analysis, 
            soil_data, feasibility_analysis
        )

        # Generate implementation plan
        implementation_plan = generate_enhanced_implementation_plan(
            cost_analysis['total_cost'], structure_recommendations
        )

        # Build comprehensive response with all requested features
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'api_version': '2.0',

            # Basic location and input summary
            'location': {
                'coordinates': {'lat': lat, 'lng': lng},
                'address': location.get('address', f'Location {lat}, {lng}'),
                'region_type': region_type,
                'administrative_info': determine_administrative_region(lat, lng)
            },

            # 1. FEASIBILITY CHECK FOR ROOFTOP RAINWATER HARVESTING
            'feasibility_analysis': feasibility_analysis,

            # 2. LOCAL RAINFALL DATA (Enhanced)
            'rainfall_data': {
                'annual_rainfall_mm': rainfall_data['annual'],
                'monthly_distribution': rainfall_data['distribution'],
                'peak_months': get_peak_rainfall_months(rainfall_data['distribution']),
                'monsoon_characteristics': analyze_monsoon_pattern(rainfall_data['distribution']),
                'collection_window': determine_collection_window(rainfall_data['distribution'])
            },

            # 3. RUNOFF GENERATION CAPACITY  
            'runoff_capacity': runoff_capacity,

            # 4. DEPTH TO GROUNDWATER LEVEL & AQUIFER INFO
            'groundwater_and_aquifer': {
                'depth_to_groundwater': soil_data['groundwater_depth'],
                'aquifer_prospects': soil_data['aquifer_prospects'],
                'principal_aquifer_info': aquifer_info,
                'recharge_potential': aquifer_info.get('recharge_potential', 'Moderate')
            },

            # 5. SOIL AND GEOLOGICAL DATA
            'soil_and_geology': {
                **soil_data,
                'suitability_for_recharge': assess_recharge_suitability(soil_data),
                'recommended_approach': recommend_approach_based_on_soil(soil_data)
            },

            # 6. HARVESTING POTENTIAL
            'harvesting_potential': {
                'roof_area_sqft': roof_area_sqft,
                'annual_harvestable_liters': annual_harvest,
                'monthly_potential': monthly_harvest,
                'storage_recommendations': storage_sizes,
                'collection_efficiency_achieved': get_collection_efficiency(roof_material, system_type)
            },

            # 7. SUGGESTED TYPE OF RTRWH/ARTIFICIAL RECHARGE STRUCTURES
            'suggested_structures': structure_recommendations,

            # 8. RECOMMENDED DIMENSIONS OF RECHARGE PITS, TRENCHES, AND SHAFTS  
            'recharge_structure_designs': recharge_designs,

            # 9. SYSTEM RECOMMENDATIONS (Enhanced)
            'system_recommendations': system_recommendations,

            # 10. COST ESTIMATION AND COST-BENEFIT ANALYSIS
            'cost_estimation': cost_analysis,
            'cost_benefit_analysis': enhanced_cost_benefit,

            # Additional comprehensive information
            'implementation_plan': implementation_plan,
            'maintenance_schedule': generate_maintenance_schedule(),
            'regulatory_compliance': generate_enhanced_regulatory_info(lat, lng),
            'performance_monitoring': generate_performance_monitoring_plan(),
            'environmental_impact': assess_environmental_impact(annual_harvest, recharge_benefit)
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in enhanced water harvesting analysis: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


def determine_administrative_region(lat: float, lng: float) -> Dict:
    """Determine administrative region for regulatory info"""

    # Simplified state mapping based on coordinates
    if 28.4 <= lat <= 28.9 and 76.8 <= lng <= 77.3:
        return {'state': 'Delhi', 'region': 'National Capital Territory'}
    elif 18.9 <= lat <= 19.3 and 72.7 <= lng <= 73.0:
        return {'state': 'Maharashtra', 'region': 'Mumbai Metropolitan'}
    elif 12.8 <= lat <= 13.1 and 77.4 <= lng <= 77.8:
        return {'state': 'Karnataka', 'region': 'Bangalore Urban'}
    elif 22.4 <= lat <= 22.7 and 88.2 <= lng <= 88.5:
        return {'state': 'West Bengal', 'region': 'Kolkata Metropolitan'}
    elif 13.0 <= lat <= 13.2 and 80.1 <= lng <= 80.4:
        return {'state': 'Tamil Nadu', 'region': 'Chennai Metropolitan'}
    else:
        # Broader state classification
        if lat >= 28:
            return {'state': 'Northern India', 'region': 'Himalayan/Plains'}
        elif lat <= 15:
            return {'state': 'Southern India', 'region': 'Peninsular'}
        else:
            return {'state': 'Central India', 'region': 'Deccan Plateau'}


def analyze_monsoon_pattern(distribution: Dict) -> Dict:
    """Analyze monsoon characteristics"""

    monsoon_months = ['jun', 'jul', 'aug', 'sep']
    pre_monsoon = ['mar', 'apr', 'may']
    post_monsoon = ['oct', 'nov', 'dec']
    winter = ['jan', 'feb']

    monsoon_total = sum(distribution.get(month, 0) for month in monsoon_months)
    pre_monsoon_total = sum(distribution.get(month, 0) for month in pre_monsoon)
    post_monsoon_total = sum(distribution.get(month, 0) for month in post_monsoon)
    winter_total = sum(distribution.get(month, 0) for month in winter)

    return {
        'monsoon_concentration_percent': round(monsoon_total, 1),
        'pre_monsoon_percent': round(pre_monsoon_total, 1),
        'post_monsoon_percent': round(post_monsoon_total, 1),
        'winter_percent': round(winter_total, 1),
        'pattern_type': determine_pattern_type(monsoon_total, post_monsoon_total)
    }


def determine_pattern_type(monsoon_percent: float, post_monsoon_percent: float) -> str:
    """Determine rainfall pattern type"""
    if monsoon_percent > 70:
        return "Monsoon Dominated"
    elif post_monsoon_percent > 25:
        return "Bi-modal (Monsoon + Post-Monsoon)"
    elif monsoon_percent < 50:
        return "Distributed Pattern"
    else:
        return "Monsoon with Extended Season"


def determine_collection_window(distribution: Dict) -> Dict:
    """Determine optimal collection window"""

    # Find months with >10% rainfall
    significant_months = [month for month, pct in distribution.items() if pct > 10]

    # Find peak collection period (consecutive months with >5%)
    all_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    collection_months = [month for month in all_months if distribution.get(month, 0) > 5]

    if len(collection_months) >= 4:
        collection_season = "Extended (4+ months)"
    elif len(collection_months) >= 2:
        collection_season = "Moderate (2-3 months)"
    else:
        collection_season = "Short (1-2 months)"

    return {
        'primary_collection_months': significant_months,
        'collection_season_type': collection_season,
        'optimal_storage_period': f"{len(collection_months)} months",
        'storage_strategy': get_storage_strategy(len(collection_months))
    }


def get_storage_strategy(collection_months: int) -> str:
    """Get recommended storage strategy"""
    if collection_months <= 2:
        return "Large storage capacity needed for dry season supply"
    elif collection_months <= 4:
        return "Moderate storage with seasonal usage planning"
    else:
        return "Smaller storage with continuous harvesting approach"


def assess_recharge_suitability(soil_data: Dict) -> Dict:
    """Assess detailed recharge suitability"""

    infiltration = soil_data.get('infiltration_rate', '').lower()
    soil_type = soil_data.get('soil_type', '').lower()

    if 'high' in infiltration or 'excellent' in soil_data.get('recharge_suitability', '').lower():
        suitability = "Excellent"
        methods = ["Recharge pits", "Percolation tanks", "Trenches"]
        limitations = "Minimal - regular maintenance needed"
    elif 'medium' in infiltration:
        suitability = "Good"
        methods = ["Recharge trenches", "Modified pits", "Injection wells"]
        limitations = "May need filter media enhancement"
    else:
        suitability = "Moderate"
        methods = ["Injection wells", "Deep recharge shafts"]
        limitations = "Requires specialized design for low permeability"

    return {
        'overall_suitability': suitability,
        'recommended_methods': methods,
        'limitations': limitations,
        'enhancement_options': get_enhancement_options(soil_type)
    }


def get_enhancement_options(soil_type: str) -> List[str]:
    """Get soil enhancement options"""
    if 'black' in soil_type.lower():
        return ["Add sand/gravel layers", "Create drainage channels", "Use injection wells"]
    elif 'clay' in soil_type.lower():
        return ["Deep boring", "Filter media installation", "Fracturing techniques"]
    else:
        return ["Standard filter media", "Regular de-silting", "Vegetation management"]


def recommend_approach_based_on_soil(soil_data: Dict) -> str:
    """Recommend overall approach based on soil characteristics"""

    infiltration = soil_data.get('infiltration_rate', '').lower()

    if 'high' in infiltration:
        return "Primary focus on artificial recharge with supplementary storage"
    elif 'medium' in infiltration:
        return "Balanced approach - combine storage and recharge systems"
    else:
        return "Storage-focused approach with limited recharge options"


def get_collection_efficiency(roof_material: str, system_type: str) -> Dict:
    """Get detailed collection efficiency breakdown"""

    material_coeff = {
        'concrete': 0.85, 'metal': 0.90, 'tile': 0.75,
        'asbestos': 0.80, 'thatch': 0.60, 'other': 0.70
    }

    system_eff = {
        'advanced': 0.90, 'standard': 0.80, 'basic': 0.70
    }

    roof_coeff = material_coeff.get(roof_material.lower(), 0.75)
    sys_eff = system_eff.get(system_type.lower(), 0.80)

    overall_efficiency = roof_coeff * sys_eff

    return {
        'roof_material_coefficient': roof_coeff,
        'system_efficiency': sys_eff,
        'overall_collection_efficiency': round(overall_efficiency, 2),
        'efficiency_factors': {
            'first_flush_loss': '5-10%',
            'gutter_overflow': '5-15%',
            'evaporation_loss': '2-5%',
            'filtration_loss': '5-10%'
        }
    }


def generate_enhanced_system_recommendations(roof_area, annual_harvest, storage_sizes, 
                                           cost_analysis, soil_data, feasibility):
    """Generate enhanced system recommendations"""

    recommendations = {
        'primary_recommendation': {},
        'alternative_options': [],
        'feasibility_based_advice': {},
        'customized_suggestions': []
    }

    # Primary recommendation based on feasibility score
    feasibility_score = feasibility['total_score']

    if feasibility_score >= 80:
        recommendations['primary_recommendation'] = {
            'system_type': 'Comprehensive RTRWH with Underground Storage',
            'rationale': 'Excellent conditions support full-scale implementation',
            'tank_capacity_liters': storage_sizes['optimal_liters'],
            'tank_material': 'Ferrocement with polymer lining',
            'filtration_system': 'Advanced multi-stage (first flush + sand + carbon + UV)',
            'pump_specification': '0.75 HP variable speed pump',
            'estimated_cost_inr': cost_analysis['total_cost'],
            'expected_performance': 'High water yield with excellent quality'
        }
    elif feasibility_score >= 65:
        recommendations['primary_recommendation'] = {
            'system_type': 'Standard RTRWH with Overhead Storage',
            'rationale': 'Good conditions with standard implementation approach',
            'tank_capacity_liters': storage_sizes['minimum_liters'],
            'tank_material': 'Food-grade PVC or polyethylene',
            'filtration_system': 'Standard (first flush + sand filter)',
            'pump_specification': '0.5 HP centrifugal pump',
            'estimated_cost_inr': cost_analysis['total_cost'] * 0.8,
            'expected_performance': 'Good water yield for household needs'
        }
    else:
        recommendations['primary_recommendation'] = {
            'system_type': 'Basic RTRWH with Recharge Focus',
            'rationale': 'Moderate feasibility - prioritize groundwater recharge',
            'storage_capacity_liters': storage_sizes['minimum_liters'],
            'recharge_component': 'Primary focus on artificial recharge',
            'estimated_cost_inr': cost_analysis['total_cost'] * 0.6,
            'expected_performance': 'Limited storage with groundwater enhancement'
        }

    # Feasibility-based advice
    recommendations['feasibility_based_advice'] = {
        'score_interpretation': feasibility['feasibility_level'],
        'key_recommendations': feasibility['recommendation'],
        'improvement_suggestions': get_feasibility_improvements(feasibility['score_breakdown'])
    }

    return recommendations


def get_feasibility_improvements(score_breakdown: Dict) -> List[str]:
    """Get suggestions to improve feasibility"""
    suggestions = []

    if score_breakdown.get('rainfall', 0) < 15:
        suggestions.append("Consider water-efficient appliances to maximize limited rainfall")

    if score_breakdown.get('roof_area', 0) < 15:
        suggestions.append("Explore community or neighborhood-level harvesting")

    if score_breakdown.get('soil_suitability', 0) < 15:
        suggestions.append("Focus on storage systems rather than recharge")

    if score_breakdown.get('water_demand', 0) < 15:
        suggestions.append("Implement water conservation measures before RTRWH")

    if not suggestions:
        suggestions.append("Excellent conditions - proceed with confidence")

    return suggestions


def generate_enhanced_implementation_plan(total_cost, structure_recommendations):
    """Generate enhanced implementation plan with structure details"""

    return {
        'total_duration': '6-8 weeks',
        'project_phases': [
            {
                'phase': 1,
                'name': 'Site Assessment and Design',
                'duration': '1-2 weeks',
                'activities': [
                    'Detailed site survey and soil testing',
                    'Structural assessment of roof and foundation',
                    'Final system design and engineering drawings',
                    'Permit applications and approvals'
                ],
                'estimated_cost': round(total_cost * 0.12),
                'deliverables': ['Technical drawings', 'Material specifications', 'Work permits']
            },
            {
                'phase': 2,
                'name': 'Material Procurement and Preparation',
                'duration': '1 week',
                'activities': [
                    'Purchase tanks, pipes, and filtration equipment',
                    'Quality inspection of materials',
                    'Site preparation and temporary arrangements',
                    'Contractor mobilization'
                ],
                'estimated_cost': round(total_cost * 0.08),
                'deliverables': ['Material delivery', 'Site readiness', 'Team deployment']
            },
            {
                'phase': 3,
                'name': 'Primary Installation',
                'duration': '2-3 weeks',
                'activities': [
                    'Excavation and foundation work',
                    'Tank installation and positioning',
                    'Plumbing network installation',
                    'Electrical connections and controls'
                ],
                'estimated_cost': round(total_cost * 0.55),
                'deliverables': ['Installed storage system', 'Connected plumbing', 'Basic testing']
            },
            {
                'phase': 4,
                'name': 'Filtration and Recharge Systems',
                'duration': '1-2 weeks',
                'activities': [
                    'Filtration system installation',
                    'Recharge pit/trench construction',
                    'Pump and automation setup',
                    'System integration and calibration'
                ],
                'estimated_cost': round(total_cost * 0.15),
                'deliverables': ['Complete filtration setup', 'Recharge structures', 'Automated controls']
            },
            {
                'phase': 5,
                'name': 'Testing and Commissioning',
                'duration': '1 week',
                'activities': [
                    'Comprehensive system testing',
                    'Water quality analysis',
                    'Performance optimization',
                    'User training and documentation handover'
                ],
                'estimated_cost': round(total_cost * 0.10),
                'deliverables': ['Performance report', 'Quality certificates', 'User manual']
            }
        ],
        'critical_success_factors': [
            'Proper site assessment and soil conditions',
            'Quality materials and skilled installation',
            'Adequate filtration for intended use',
            'Regular maintenance scheduling'
        ],
        'risk_mitigation': [
            'Weather contingency planning',
            'Material quality assurance',
            'Skilled contractor selection',
            'Regular progress monitoring'
        ]
    }


def generate_performance_monitoring_plan():
    """Generate performance monitoring and evaluation plan"""

    return {
        'key_performance_indicators': {
            'water_quantity': [
                'Monthly water harvested (liters)',
                'System efficiency percentage',
                'Storage utilization rate',
                'Overflow frequency and volume'
            ],
            'water_quality': [
                'pH levels (6.5-8.5 range)',
                'Turbidity (< 5 NTU)',
                'Total dissolved solids',
                'Bacterial contamination levels'
            ],
            'system_performance': [
                'Pump operational hours',
                'Filter replacement frequency',
                'Energy consumption',
                'Maintenance cost per month'
            ]
        },
        'monitoring_schedule': {
            'daily': ['Visual inspection', 'Basic system checks'],
            'weekly': ['Water level monitoring', 'Quality assessment'],
            'monthly': ['Performance data analysis', 'Preventive maintenance'],
            'quarterly': ['Comprehensive system audit', 'Water quality testing'],
            'annually': ['System upgrade assessment', 'Cost-benefit review']
        },
        'monitoring_tools': [
            'Water level sensors with alerts',
            'Flow meters for harvest measurement',
            'Basic water quality test kits',
            'Mobile app for data logging'
        ],
        'performance_targets': {
            'collection_efficiency': '>75% of theoretical potential',
            'system_uptime': '>95% during monsoon season',
            'water_quality': 'Meet IS 10500 standards for intended use',
            'cost_savings': 'Achieve projected savings within 10% variance'
        }
    }


def assess_environmental_impact(annual_harvest: float, recharge_benefit: float):
    """Assess environmental impact and benefits"""

    return {
        'positive_impacts': {
            'groundwater_recharge': {
                'annual_recharge_liters': round(annual_harvest * 0.3, 0),
                'aquifer_benefit': 'Enhanced local groundwater levels',
                'sustainability_impact': 'Reduced pressure on municipal supply'
            },
            'flood_mitigation': {
                'runoff_reduction_percent': '60-80%',
                'urban_flooding_benefit': 'Reduced peak flow in storm drains',
                'erosion_control': 'Minimized soil erosion from roof runoff'
            },
            'carbon_footprint_reduction': {
                'annual_co2_savings_kg': round(annual_harvest * 0.006, 1),  # 6g CO2 per liter
                'energy_savings': 'Reduced pumping for municipal water',
                'transport_savings': 'Eliminated water tanker dependency'
            }
        },
        'ecosystem_benefits': [
            'Enhanced local microclimate',
            'Reduced heat island effect',
            'Support for local vegetation',
            'Improved water cycle balance'
        ],
        'long_term_sustainability': {
            'water_security_enhancement': 'High',
            'climate_resilience_building': 'Moderate to High',
            'community_impact': 'Positive demonstration effect',
            'scalability_potential': 'High for similar properties'
        }
    }


def generate_enhanced_regulatory_info(lat: float, lng: float):
    """Generate enhanced regulatory and compliance information"""

    admin_region = determine_administrative_region(lat, lng)
    state = admin_region.get('state', 'Unknown')

    # State-specific regulations (simplified)
    if 'Delhi' in state:
        return {
            'local_mandate': 'Mandatory for plots >100 sq m under Delhi Building Bye-laws',
            'authority': 'Delhi Jal Board and DDA',
            'required_permits': ['Building plan approval', 'DJB NoC', 'Electrical safety clearance'],
            'available_subsidies': [
                {'scheme': 'DJB RTRWH Subsidy', 'amount': '₹15,000', 'eligibility': 'Residential properties'},
                {'scheme': 'Delhi Solar Policy', 'amount': '₹5,000', 'eligibility': 'With solar integration'}
            ],
            'compliance_timeline': 'Must be completed before occupancy certificate',
            'penalties': 'Water connection may be disconnected for non-compliance',
            'technical_standards': 'As per CPWD guidelines and IS codes',
            'inspection_requirements': 'Pre-monsoon system check mandatory'
        }
    elif 'Maharashtra' in state:
        return {
            'local_mandate': 'Compulsory for plots >300 sq m in Mumbai, >500 sq m in other cities',
            'authority': 'Maharashtra Water Resources Department',
            'required_permits': ['Municipal building approval', 'Water supply NOC'],
            'available_subsidies': [
                {'scheme': 'Jal Yukt Shivar', 'amount': '₹10,000-25,000', 'eligibility': 'Rural and semi-urban'}
            ],
            'compliance_timeline': 'Within 6 months of building construction',
            'technical_standards': 'Maharashtra RTRWH guidelines 2019',
            'inspection_requirements': 'Annual compliance certificate'
        }
    else:
        return {
            'local_mandate': 'Check with local municipal corporation/panchayat',
            'authority': 'State Water Resources Department',
            'required_permits': ['Building plan approval', 'Local body NOC'],
            'available_subsidies': 'Contact state/district water authority',
            'compliance_timeline': 'Usually before occupancy certificate',
            'technical_standards': 'Follow BIS and CPWD guidelines',
            'inspection_requirements': 'As per local regulations'
        }


# Keep existing helper functions
def get_peak_rainfall_months(distribution):
    """Get peak rainfall months from distribution"""
    sorted_months = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    return [month for month, _ in sorted_months[:3]]


def generate_maintenance_schedule():
    """Generate comprehensive maintenance schedule"""

    return {
        'routine_maintenance': {
            'weekly_during_monsoon': [
                'Clean gutters and remove debris',
                'Check first flush diverter operation',
                'Inspect roof surface for damage',
                'Monitor water levels and quality'
            ],
            'monthly_throughout_year': [
                'Clean mesh filters and leaf guards',
                'Test pump operation and pressure',
                'Check pipe joints for leaks',
                'Inspect storage tank exterior'
            ],
            'quarterly_maintenance': [
                'Replace/clean filter media',
                'Comprehensive system performance check',
                'Water quality testing (pH, TDS, bacteria)',
                'Electrical connections inspection'
            ]
        },
        'annual_major_maintenance': [
            'Complete tank cleaning and disinfection',
            'Professional system audit and optimization',
            'Pump servicing and electrical safety check',
            'Structural inspection of all components',
            'Performance evaluation and upgrade recommendations'
        ],
        'cost_estimates': {
            'routine_monthly_cost': '₹500-800',
            'quarterly_maintenance': '₹1,500-2,500',  
            'annual_major_service': '₹8,000-12,000',
            'total_annual_budget': '₹15,000-20,000'
        },
        'diy_vs_professional': {
            'diy_tasks': 'Weekly cleaning, basic inspection, filter replacement',
            'professional_required': 'Pump servicing, electrical work, tank cleaning, water testing'
        }
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
