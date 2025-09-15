"""
Configuration settings for Water Harvesting API
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # API settings
    API_VERSION = '1.0'
    API_TITLE = 'Water Harvesting Analysis API'
    API_DESCRIPTION = 'Provides personalized water harvesting recommendations for locations in India'

    # External API URLs
    OPEN_METEO_BASE_URL = 'https://api.open-meteo.com/v1'
    IMD_BASE_URL = 'https://mausam.imd.gov.in/api'

    # Rate limiting (requests per minute)
    RATE_LIMIT = 60

    # Cache settings (in seconds)
    CACHE_TIMEOUT = 3600  # 1 hour

    # Default system parameters
    DEFAULT_COLLECTION_EFFICIENCY = 0.80
    DEFAULT_RUNOFF_COEFFICIENT = 0.85

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
