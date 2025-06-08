"""
Rainbow Finder Weather Agent

This agent handles weather data collection and processing for rainbow predictions.
It retrieves current and forecast weather conditions for specific locations.
"""

import logging
from typing import Dict, List, Any
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform.vertexai.agents import LlmAgent
from google.cloud.aiplatform.vertexai.agents.tools import OutputSchema, Parameter, Tool

from shared.models.rainbow import WeatherCondition
from shared.constants.app_constants import (
    MIN_PRECIPITATION_RATE, 
    MAX_CLOUD_COVER,
    WEATHER_UPDATE_INTERVAL_MINUTES
)

# Define output schema for the weather agent
weather_output_schema = OutputSchema(
    description="Weather data for rainbow prediction",
    parameters={
        "current_conditions": Parameter(
            description="Current weather conditions at the location",
            type="object"
        ),
        "forecast": Parameter(
            description="Weather forecast for the requested time period",
            type="array"
        ),
        "rainbow_favorable": Parameter(
            description="Whether current conditions are favorable for rainbow formation",
            type="boolean"
        ),
        "explanation": Parameter(
            description="Explanation of the weather analysis",
            type="string"
        )
    }
)

# Create weather tools
get_weather_tool = Tool(
    name="get_current_weather",
    description="Get current weather conditions for a location",
    parameters={
        "latitude": Parameter(
            description="Latitude coordinate",
            type="number",
            required=True
        ),
        "longitude": Parameter(
            description="Longitude coordinate",
            type="number",
            required=True
        )
    },
    function=lambda latitude, longitude: {
        "temperature": 20.0,
        "humidity": 75.0,
        "precipitation": 0.2,
        "cloud_cover": 40.0,
        "wind_speed": 10.0,
        "wind_direction": 180.0,
        "timestamp": "2025-06-07T12:00:00Z"
    }
)

get_forecast_tool = Tool(
    name="get_weather_forecast",
    description="Get weather forecast for a location",
    parameters={
        "latitude": Parameter(
            description="Latitude coordinate",
            type="number",
            required=True
        ),
        "longitude": Parameter(
            description="Longitude coordinate",
            type="number",
            required=True
        ),
        "hours": Parameter(
            description="Number of hours to forecast",
            type="integer",
            default=24
        )
    },
    function=lambda latitude, longitude, hours: [
        {
            "temperature": 20.0,
            "humidity": 75.0,
            "precipitation": 0.2,
            "cloud_cover": 40.0,
            "wind_speed": 10.0,
            "wind_direction": 180.0,
            "timestamp": f"2025-06-07T{12+i if 12+i<24 else 12+i-24}:00:00Z"
        } for i in range(hours)
    ]
)

analyze_rainbow_conditions_tool = Tool(
    name="analyze_rainbow_conditions",
    description="Analyze weather conditions for rainbow formation potential",
    parameters={
        "weather_data": Parameter(
            description="Weather data to analyze",
            type="object",
            required=True
        )
    },
    function=lambda weather_data: {
        "favorable": (
            weather_data.get("precipitation", 0) >= MIN_PRECIPITATION_RATE and
            weather_data.get("cloud_cover", 100) <= MAX_CLOUD_COVER
        ),
        "explanation": "Analysis of precipitation and cloud cover patterns"
    }
)

# Create the weather agent
weather_agent = LlmAgent(
    name="WeatherAgent",
    model="gemini-2.0-flash",
    description="Collects and analyzes weather data for rainbow predictions",
    instruction="""
    You are the Weather Agent for the Rainbow Finder system. Your role is to:
    1. Retrieve current weather conditions for specific locations
    2. Get weather forecasts for the requested time periods
    3. Analyze weather data for conditions favorable to rainbow formation
    4. Provide detailed weather information to assist rainbow predictions
    
    When analyzing weather for rainbow formation, consider:
    - Precipitation: Some precipitation is needed, but not heavy rain
    - Cloud cover: Partial cloud cover is ideal
    - Sun position: The sun must be visible for rainbows to form
    - Wind conditions: Light to moderate wind may help disperse water droplets
    
    Your responses should be factual, data-driven, and focused on providing accurate 
    weather information relevant to rainbow formation.
    """,
    tools=[get_weather_tool, get_forecast_tool, analyze_rainbow_conditions_tool],
    output_key="weather_data"
)