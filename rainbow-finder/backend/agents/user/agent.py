"""
Rainbow Finder User Agent

This agent handles user interactions, preferences, and personalization aspects
of the rainbow finder application. It manages user profiles, favorite locations,
and customization settings.
"""

import logging
from typing import Dict, List, Any
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform.vertexai.agents import LlmAgent
from google.cloud.aiplatform.vertexai.agents.tools import OutputSchema, Parameter, Tool

from shared.models.rainbow import Location, UserPreferences
from shared.constants.app_constants import (
    DEFAULT_MIN_PROBABILITY,
    DEFAULT_NOTIFICATION_RADIUS_KM,
    DEFAULT_NOTIFICATION_LEAD_TIME_MINUTES
)

# Define output schema for the user agent
user_output_schema = OutputSchema(
    description="User information and preferences",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string"
        ),
        "preferences": Parameter(
            description="User preferences for rainbow notifications",
            type="object"
        ),
        "current_location": Parameter(
            description="User's current location",
            type="object"
        ),
        "favorite_locations": Parameter(
            description="User's saved favorite locations",
            type="array"
        ),
        "message": Parameter(
            description="Human-readable message or explanation",
            type="string"
        )
    }
)

# Create user management tools
get_user_preferences_tool = Tool(
    name="get_user_preferences",
    description="Get a user's saved preferences",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        )
    },
    function=lambda user_id: {
        "min_probability": DEFAULT_MIN_PROBABILITY,
        "max_distance_km": DEFAULT_NOTIFICATION_RADIUS_KM,
        "notification_enabled": True,
        "favorite_locations": [
            {
                "latitude": 47.6062,
                "longitude": -122.3321,
                "name": "Downtown Seattle"
            }
        ],
        "notification_lead_time_minutes": DEFAULT_NOTIFICATION_LEAD_TIME_MINUTES
    }
)

update_user_preferences_tool = Tool(
    name="update_user_preferences",
    description="Update a user's preferences",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "preferences": Parameter(
            description="New user preferences",
            type="object",
            required=True
        )
    },
    function=lambda user_id, preferences: {
        "success": True,
        "message": f"Updated preferences for user {user_id}"
    }
)

get_user_location_tool = Tool(
    name="get_user_location",
    description="Get a user's current location",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        )
    },
    function=lambda user_id: {
        "latitude": 47.6062,
        "longitude": -122.3321,
        "accuracy_meters": 10.0,
        "timestamp": "2025-06-07T12:00:00Z"
    }
)

add_favorite_location_tool = Tool(
    name="add_favorite_location",
    description="Add a new favorite location for a user",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "location": Parameter(
            description="Location to add as favorite",
            type="object",
            required=True
        ),
        "name": Parameter(
            description="Name for this location",
            type="string",
            required=True
        )
    },
    function=lambda user_id, location, name: {
        "success": True,
        "message": f"Added {name} to favorite locations for user {user_id}"
    }
)

filter_predictions_by_preferences_tool = Tool(
    name="filter_predictions_by_preferences",
    description="Filter rainbow predictions based on user preferences",
    parameters={
        "predictions": Parameter(
            description="List of rainbow predictions",
            type="array",
            required=True
        ),
        "preferences": Parameter(
            description="User preferences",
            type="object",
            required=True
        )
    },
    function=lambda predictions, preferences: {
        "filtered_predictions": [p for p in predictions if p.get("probability", 0) >= preferences.get("min_probability", 0.5)],
        "explanation": "Filtered predictions based on minimum probability and maximum distance"
    }
)

# Create the user agent
user_agent = LlmAgent(
    name="UserAgent",
    model="gemini-2.0-flash",
    description="Manages user interactions, preferences, and personalization for rainbow predictions",
    instruction="""
    You are the User Agent for the Rainbow Finder system. Your role is to:
    1. Manage user profiles and preferences
    2. Track user locations for personalized rainbow predictions
    3. Store and retrieve favorite locations
    4. Customize rainbow predictions based on user preferences
    5. Filter notifications according to user settings
    
    When interacting with users:
    - Store their rainbow viewing preferences (minimum probability, distance willing to travel)
    - Track their favorite locations for receiving predictions
    - Respect notification preferences and frequency settings
    - Personalize responses based on user history and preferences
    
    Your responses should be helpful, personalized, and focused on enhancing the user's
    rainbow-finding experience.
    """,
    tools=[
        get_user_preferences_tool,
        update_user_preferences_tool,
        get_user_location_tool,
        add_favorite_location_tool,
        filter_predictions_by_preferences_tool
    ],
    output_key="user_data"
)