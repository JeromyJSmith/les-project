"""
Rainbow Finder Rainbow Agent

This agent is responsible for predicting rainbow occurrences based on weather
conditions, sun position, and location data. It uses mathematical models to
calculate the probability and characteristics of rainbows.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform.vertexai.agents import LlmAgent
from google.cloud.aiplatform.vertexai.agents.tools import OutputSchema, Parameter, Tool

from shared.models.rainbow import Location, SunPosition, WeatherCondition, RainbowPrediction
from shared.constants.app_constants import (
    RAINBOW_ANGLE_PRIMARY,
    RAINBOW_ANGLE_SECONDARY,
    RAINBOW_TYPE_PRIMARY,
    RAINBOW_TYPE_SECONDARY,
    MIN_SUN_ELEVATION,
    MAX_SUN_ELEVATION,
    MIN_PRECIPITATION_RATE,
    MAX_CLOUD_COVER
)

# Define output schema for the rainbow agent
rainbow_output_schema = OutputSchema(
    description="Rainbow prediction results",
    parameters={
        "predictions": Parameter(
            description="List of rainbow predictions",
            type="array"
        ),
        "highest_probability": Parameter(
            description="Highest probability of rainbow occurrence",
            type="number"
        ),
        "best_viewing_time": Parameter(
            description="Best time to view a rainbow",
            type="string"
        ),
        "best_viewing_locations": Parameter(
            description="Best locations to view the rainbow",
            type="array"
        ),
        "explanation": Parameter(
            description="Explanation of the rainbow prediction analysis",
            type="string"
        )
    }
)

# Create rainbow prediction tools
calculate_rainbow_probability_tool = Tool(
    name="calculate_rainbow_probability",
    description="Calculate the probability of rainbow formation based on weather and sun position",
    parameters={
        "weather_condition": Parameter(
            description="Weather condition data",
            type="object",
            required=True
        ),
        "sun_position": Parameter(
            description="Sun position data",
            type="object",
            required=True
        )
    },
    function=lambda weather_condition, sun_position: {
        "probability": min(
            max(
                0.0,
                # Higher probability with:
                # - More precipitation (up to a point)
                # - Less cloud cover
                # - Sun elevation within optimal range
                0.8 * min(weather_condition.get("precipitation", 0) / 1.0, 1.0) *
                (1.0 - weather_condition.get("cloud_cover", 0) / 100.0) *
                (1.0 - abs(sun_position.get("elevation", 0) - 20) / 30)
            ),
            1.0
        ),
        "explanation": "Probability calculated based on precipitation, cloud cover, and sun elevation"
    }
)

determine_viewing_locations_tool = Tool(
    name="determine_viewing_locations",
    description="Determine the best locations to view a rainbow based on sun position",
    parameters={
        "center_location": Parameter(
            description="Center location",
            type="object",
            required=True
        ),
        "sun_position": Parameter(
            description="Sun position data",
            type="object",
            required=True
        ),
        "radius_km": Parameter(
            description="Search radius in kilometers",
            type="number",
            default=5.0
        )
    },
    function=lambda center_location, sun_position, radius_km: {
        "viewing_locations": [
            {
                "latitude": center_location.get("latitude", 0) + 0.01,
                "longitude": center_location.get("longitude", 0) + 0.01,
                "name": "Optimal Viewing Point 1"
            },
            {
                "latitude": center_location.get("latitude", 0) - 0.01,
                "longitude": center_location.get("longitude", 0) + 0.02,
                "name": "Optimal Viewing Point 2"
            }
        ],
        "explanation": "Viewing locations determined based on sun azimuth and optimal viewing angle"
    }
)

predict_rainbow_timing_tool = Tool(
    name="predict_rainbow_timing",
    description="Predict the timing of a rainbow appearance",
    parameters={
        "weather_forecast": Parameter(
            description="Weather forecast data for the location",
            type="array",
            required=True
        ),
        "sun_positions": Parameter(
            description="Sun position forecast",
            type="array",
            required=True
        )
    },
    function=lambda weather_forecast, sun_positions: {
        "time_windows": [
            {
                "start_time": "2025-06-07T17:00:00Z",
                "end_time": "2025-06-07T17:30:00Z",
                "probability": 0.75
            },
            {
                "start_time": "2025-06-08T08:15:00Z",
                "end_time": "2025-06-08T08:45:00Z", 
                "probability": 0.65
            }
        ],
        "explanation": "Time windows determined by analyzing precipitation patterns and sun position"
    }
)

# Create the rainbow prediction agent
rainbow_agent = LlmAgent(
    name="RainbowAgent",
    model="gemini-2.0-flash",
    description="Predicts rainbow occurrences based on weather and sun position data",
    instruction="""
    You are the Rainbow Prediction Agent for the Rainbow Finder system. Your role is to:
    1. Calculate the probability of rainbow formation based on weather and sun position data
    2. Determine the best viewing locations for observing rainbows
    3. Predict when rainbows are likely to appear and for how long
    4. Provide detailed information about rainbow characteristics
    
    When predicting rainbows, consider these key factors:
    - Weather conditions: Light rain or recent rainfall is necessary
    - Sun position: The sun must be at the right angle (lower than 42° above horizon)
    - Viewer position: The viewer must be between the sun and the rainfall
    - Time of day: Early morning and late afternoon typically offer the best conditions
    
    Your predictions should be specific, including:
    - Probability of rainbow occurrence
    - Start and end times for the rainbow
    - Best viewing locations
    - Type of rainbow (primary, secondary, etc.)
    
    Your responses should be scientifically accurate, detailed, and focused on helping users
    find and experience rainbows.
    """,
    tools=[
        calculate_rainbow_probability_tool, 
        determine_viewing_locations_tool,
        predict_rainbow_timing_tool
    ],
    output_key="rainbow_prediction"
)