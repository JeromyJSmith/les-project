"""
Rainbow Models

This module defines data models related to rainbow predictions.
These models are shared between frontend and backend components.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Location:
    """Geographic location representation."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    name: Optional[str] = None


@dataclass
class SunPosition:
    """Solar position representation."""
    azimuth: float  # Degrees from north
    elevation: float  # Degrees from horizon
    timestamp: datetime


@dataclass
class WeatherCondition:
    """Weather condition representation."""
    temperature: float  # Celsius
    humidity: float  # Percentage
    precipitation: float  # mm/h
    cloud_cover: float  # Percentage
    wind_speed: float  # km/h
    wind_direction: float  # Degrees
    timestamp: datetime


@dataclass
class RainbowPrediction:
    """Rainbow prediction representation."""
    location: Location
    probability: float  # 0.0 to 1.0
    predicted_time_start: datetime
    predicted_time_end: datetime
    viewing_locations: List[Location]
    sun_position: SunPosition
    weather_condition: WeatherCondition
    rainbow_type: str = "primary"  # primary, secondary, etc.
    intensity: float = 0.0  # 0.0 to 1.0
    arc_coordinates: Optional[List[Location]] = None


@dataclass
class UserPreferences:
    """User preferences for rainbow notifications."""
    min_probability: float = 0.5  # Minimum probability threshold
    max_distance_km: float = 10.0  # Maximum distance to travel
    notification_enabled: bool = True
    favorite_locations: List[Location] = None
    notification_lead_time_minutes: int = 30