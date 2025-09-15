# Water Harvesting API Documentation

## Overview
The Water Harvesting API provides personalized water harvesting recommendations for locations across India. It integrates multiple free data sources to deliver comprehensive analysis including system specifications, financial projections, and implementation guidance.

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
Currently, no authentication is required. In production, consider implementing API key authentication.

## Endpoints

### 1. Health Check
**GET** `/health`

Returns API status and version information.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-09-15T16:30:00",
    "version": "1.0"
}
```

### 2. Water Harvesting Analysis
**POST** `/api/v1/water-harvesting/analyze`

Main endpoint for comprehensive water harvesting analysis.

**Request Body:**
```json
{
    "location": {
        "lat": 28.6139,
        "lng": 77.2090,
        "address": "New Delhi, India"
    },
    "property": {
        "type": "residential",
        "roof_area_sqft": 1200,
        "roof_material": "concrete",
        "floors": 2,
        "plot_area_sqft": 2400
    },
    "usage": {
        "household_size": 4,
        "daily_consumption_liters": 600,
        "current_sources": ["municipal", "borewell"],
        "intended_use": ["drinking", "toilet_flushing"]
    },
    "preferences": {
        "budget_range": "75000-150000",
        "system_type": "standard",
        "region_type": "urban",
        "priority": "cost_savings"
    }
}
```

**Required Fields:**
- `location.lat` (float): Latitude
- `location.lng` (float): Longitude  
- `property.roof_area_sqft` (float): Roof area in square feet

**Optional Fields:**
- All other fields have sensible defaults

**Response Structure:**
```json
{
    "status": "success",
    "timestamp": "2025-09-15T16:30:00",
    "location": {
        "coordinates": {"lat": 28.6139, "lng": 77.2090},
        "address": "New Delhi, India",
        "region_type": "urban"
    },
    "climate_analysis": {
        "annual_rainfall_mm": 797,
        "rainfall_distribution": {
            "jan": 2.1, "feb": 2.5, "mar": 4.2,
            "apr": 3.7, "may": 6.2, "jun": 18.6,
            "jul": 44.7, "aug": 39.2, "sep": 22.6,
            "oct": 9.2, "nov": 3.2, "dec": 1.9
        },
        "peak_months": ["jul", "aug", "sep"],
        "collection_efficiency": 0.80
    },
    "soil_and_geology": {
        "soil_type": "Alluvial",
        "infiltration_rate": "Medium (5-15 mm/hr)",
        "recharge_suitability": "Good for both storage and recharge",
        "groundwater_depth": "10-25 meters",
        "aquifer_prospects": "Excellent"
    },
    "harvesting_potential": {
        "roof_area_sqft": 1200,
        "annual_harvestable_liters": 25849,
        "monthly_potential": {
            "jan": 543, "feb": 646, "mar": 1086, "apr": 957,
            "may": 1602, "jun": 4808, "jul": 11554, "aug": 10133,
            "sep": 5843, "oct": 2378, "nov": 827, "dec": 491
        },
        "storage_recommendations": {
            "minimum_liters": 5777,
            "optimal_liters": 15020,
            "maximum_beneficial_liters": 23108
        }
    },
    "system_recommendations": {
        "primary_recommendation": {
            "system_type": "Rooftop Harvesting with Storage Tank",
            "tank_capacity_liters": 15020,
            "tank_material": "Ferrocement or Food-grade PVC",
            "filtration_components": [
                "First flush diverter (200-300 liters)",
                "Coarse mesh filter",
                "Sand and activated carbon filter"
            ],
            "pump_specification": "0.5 HP centrifugal pump",
            "estimated_cost_inr": 1299702
        },
        "alternative_options": [...],
        "suitability_score": 87.2
    },
    "cost_analysis": {
        "tank_cost": 1276700,
        "filtration_cost": 25000,
        "pump_cost": 12000,
        "installation_cost": 20000,
        "contingency": 133370,
        "total_cost": 1467070
    },
    "financial_analysis": {
        "annual_water_savings_liters": 18094,
        "annual_cost_savings_inr": 271,
        "payback_period_years": 5408.0,
        "total_20_year_savings": 5420,
        "net_20_year_benefit": -1461650,
        "roi_percentage": -99.6
    },
    "implementation_plan": {
        "total_duration": "4-6 weeks",
        "phases": [...]
    },
    "maintenance_schedule": {
        "monthly_tasks": [...],
        "quarterly_tasks": [...],
        "annual_tasks": [...],
        "estimated_annual_cost": 4500
    },
    "regulatory_info": {
        "local_mandate": "Check with local municipal corporation",
        "required_permits": ["Building plan approval", "Plumbing permit"],
        "available_subsidies": "Contact local water authority"
    }
}
```

### 3. Rainfall Data
**GET** `/api/v1/rainfall/{lat}/{lng}`

Get rainfall data for specific coordinates.

**Example:** `/api/v1/rainfall/28.6139/77.2090`

### 4. Soil Data  
**GET** `/api/v1/soil/{lat}/{lng}`

Get soil and geological data for specific coordinates.

**Example:** `/api/v1/soil/28.6139/77.2090`

## Error Responses

All endpoints return error responses in the following format:

```json
{
    "error": "Error description",
    "message": "Detailed error message"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server processing error

## Data Sources

The API integrates with several free data sources:

1. **Open-Meteo Weather API**: Historical and forecast weather data
2. **IMD (India Meteorological Department)**: Official rainfall data  
3. **NRSC/ISRO Bhuvan**: Soil and geological data
4. **CGWB**: Groundwater information
5. **Local fallback data**: City-specific rainfall averages

## Rate Limits

- Development: No limits
- Production: 60 requests per minute per IP

## Support

For technical support or questions about the API, please contact the development team.

## Changelog

### Version 1.0
- Initial release
- Basic water harvesting analysis
- Integration with weather and soil data sources
- Financial analysis and recommendations
