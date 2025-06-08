"""
Application Constants

This module defines constants used throughout the Rainbow Finder application.
These constants are shared between frontend and backend components.
"""

# API Endpoints
API_BASE_URL = "/api/v1"
RAINBOW_PREDICTION_ENDPOINT = f"{API_BASE_URL}/predictions"
WEATHER_ENDPOINT = f"{API_BASE_URL}/weather"
USER_PREFERENCES_ENDPOINT = f"{API_BASE_URL}/user/preferences"
LOCATIONS_ENDPOINT = f"{API_BASE_URL}/locations"

# Rainbow Types
RAINBOW_TYPE_PRIMARY = "primary"
RAINBOW_TYPE_SECONDARY = "secondary"
RAINBOW_TYPE_SUPERNUMERARY = "supernumerary"
RAINBOW_TYPE_FOGBOW = "fogbow"
RAINBOW_TYPE_MOONBOW = "moonbow"

# Rainbow Physics Constants
RAINBOW_ANGLE_PRIMARY = 42.0  # Degrees
RAINBOW_ANGLE_SECONDARY = 51.0  # Degrees
WATER_REFRACTIVE_INDEX = 1.33

# Weather Condition Thresholds
MIN_PRECIPITATION_RATE = 0.1  # mm/h for rainbow formation
MAX_CLOUD_COVER = 70  # % cloud cover beyond which rainbows are unlikely
MIN_SUN_ELEVATION = 0  # Degrees above horizon
MAX_SUN_ELEVATION = 42  # Degrees above horizon for rainbow visibility

# Notification Settings
DEFAULT_MIN_PROBABILITY = 0.5
DEFAULT_NOTIFICATION_RADIUS_KM = 10.0
DEFAULT_NOTIFICATION_LEAD_TIME_MINUTES = 30

# Time Constants
PREDICTION_UPDATE_INTERVAL_MINUTES = 5
WEATHER_UPDATE_INTERVAL_MINUTES = 15