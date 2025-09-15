# Water Harvesting API

A comprehensive Flask-based API that provides personalized water harvesting recommendations for locations across India. The API integrates multiple free data sources to deliver detailed analysis including system specifications, financial projections, and implementation guidance.

## Features

- 🌧️ **Real-time Weather Data**: Integration with IMD and Open-Meteo APIs
- 🏔️ **Geological Analysis**: Soil type and groundwater assessment
- 💧 **Harvesting Calculations**: Accurate water collection potential estimates
- 💰 **Financial Analysis**: ROI, payback period, and cost projections
- 🔧 **System Recommendations**: Personalized equipment and installation advice
- 📅 **Implementation Planning**: Phase-wise project timelines
- 🛠️ **Maintenance Schedules**: Ongoing maintenance guidance

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional)**
```bash
cp .env.example .env
# Edit .env file with your configurations
```

4. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Using Docker

1. **Build the Docker image**
```bash
docker build -t water-harvesting-api .
```

2. **Run the container**
```bash
docker run -p 5000:5000 water-harvesting-api
```

## API Usage

### Basic Example

```python
import requests

# Sample analysis request
data = {
    "location": {
        "lat": 28.6139,
        "lng": 77.2090,
        "address": "New Delhi, India"
    },
    "property": {
        "roof_area_sqft": 1200,
        "roof_material": "concrete",
        "type": "residential"
    },
    "usage": {
        "household_size": 4,
        "daily_consumption_liters": 600
    },
    "preferences": {
        "budget_range": "75000-150000",
        "system_type": "standard"
    }
}

response = requests.post(
    'http://localhost:5000/api/v1/water-harvesting/analyze',
    json=data
)

result = response.json()
print(f"Annual Harvestable Water: {result['harvesting_potential']['annual_harvestable_liters']} liters")
```

### Test the API

Run the example usage script:
```bash
python example_usage.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/water-harvesting/analyze` | POST | Main analysis endpoint |
| `/api/v1/rainfall/{lat}/{lng}` | GET | Rainfall data for coordinates |
| `/api/v1/soil/{lat}/{lng}` | GET | Soil data for coordinates |

## Data Sources

The API integrates with several free data sources:

- **Open-Meteo**: Global weather data (no API key required)
- **IMD**: India Meteorological Department data
- **NRSC/ISRO**: Soil and geological information  
- **CGWB**: Central Ground Water Board data
- **Fallback databases**: City-specific historical averages

## Request/Response Examples

### Request Format
```json
{
    "location": {
        "lat": 28.6139,
        "lng": 77.2090
    },
    "property": {
        "roof_area_sqft": 1200,
        "roof_material": "concrete"
    },
    "usage": {
        "household_size": 4
    }
}
```

### Response Format
```json
{
    "status": "success",
    "harvesting_potential": {
        "annual_harvestable_liters": 25849,
        "storage_recommendations": {
            "optimal_liters": 8000
        }
    },
    "system_recommendations": {
        "primary_recommendation": {
            "system_type": "Rooftop Harvesting with Storage Tank",
            "estimated_cost_inr": 125000
        }
    },
    "financial_analysis": {
        "annual_cost_savings_inr": 9250,
        "payback_period_years": 13.5,
        "roi_percentage": 48
    }
}
```

## Configuration

Key configuration options in `config.py`:

- **API_VERSION**: Current API version
- **RATE_LIMIT**: Requests per minute limit
- **CACHE_TIMEOUT**: Response caching duration
- **DEFAULT_COLLECTION_EFFICIENCY**: Default system efficiency

## Development

### Project Structure
```
water-harvesting-api/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── example_usage.py      # Usage examples
├── API_DOCUMENTATION.md  # Detailed API docs
├── Dockerfile           # Container configuration
└── README.md            # This file
```

### Adding New Features

1. **New Calculations**: Add methods to `WaterHarvestingCalculator` class
2. **New Data Sources**: Create new service classes following the pattern
3. **New Endpoints**: Add routes in the main `app.py` file

### Error Handling

The API includes comprehensive error handling:
- Input validation
- External API failures with fallbacks
- Graceful degradation when data is unavailable
- Detailed error messages in responses

## Production Deployment

### Environment Variables
Set these for production:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key
```

### Using Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Performance Considerations
- Implement caching for frequently requested locations
- Use connection pooling for external APIs
- Monitor and log API usage patterns
- Consider rate limiting for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support, bug reports, or feature requests:
- Create an issue in the project repository
- Contact the development team
- Check the API documentation for common questions

## Changelog

### Version 1.0.0
- Initial release
- Core water harvesting analysis functionality
- Integration with major Indian data sources
- Comprehensive financial and implementation analysis
