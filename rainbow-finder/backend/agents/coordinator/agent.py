"""
Rainbow Finder Coordinator Agent

This agent serves as the central coordinator for all other agents in the system.
It orchestrates the flow of information and delegates tasks to specialized agents.
"""

import logging
from typing import Dict, List, Any
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform.vertexai.agents import LlmAgent
from google.cloud.aiplatform.vertexai.agents.tools import OutputSchema, Parameter, Tool

# Import sub-agents
from backend.agents.weather.agent import weather_agent
from backend.agents.rainbow.agent import rainbow_agent
from backend.agents.user.agent import user_agent
from backend.agents.notification.agent import notification_agent

# Define output schema for the coordinator
coordinator_output_schema = OutputSchema(
    description="The response from the Rainbow Finder coordinator agent",
    parameters={
        "response_type": Parameter(
            description="Type of response",
            type="string",
            enum=["prediction", "weather", "user_update", "notification", "error"]
        ),
        "message": Parameter(
            description="Human-readable message explaining the response",
            type="string"
        ),
        "data": Parameter(
            description="Response data payload",
            type="object"
        )
    }
)

# Create coordinator tools
process_request_tool = Tool(
    name="process_rainbow_request",
    description="Process a rainbow prediction request",
    parameters={
        "location": Parameter(
            description="Location to check for rainbow prediction (lat,lng)",
            type="string",
            required=True
        ),
        "time_window_hours": Parameter(
            description="Time window in hours to look for rainbow predictions",
            type="integer",
            default=24
        )
    },
    function=lambda location, time_window_hours: {"status": "processing", "message": f"Processing rainbow prediction for {location} in the next {time_window_hours} hours"}
)

# Create the root coordinator agent
coordinator_agent = LlmAgent(
    name="RainbowFinderCoordinator",
    model="gemini-2.0-flash",
    description="Coordinates the Rainbow Finder system to predict where and when rainbows will appear",
    instruction="""
    You are the Rainbow Finder Coordinator Agent. Your role is to:
    1. Receive requests for rainbow predictions
    2. Coordinate with specialized agents to process these requests
    3. Collect and integrate information from weather, sun position, and location data
    4. Return consolidated rainbow predictions with viewing locations and timing
    
    When a user requests a rainbow prediction:
    - Delegate weather data collection to the Weather Agent
    - Request sun position calculations based on location and time
    - Pass relevant data to the Rainbow Prediction Agent
    - Use the User Agent to incorporate user preferences
    - Determine if notifications should be sent via the Notification Agent
    
    Your responses should be clear, helpful, and focused on providing accurate rainbow predictions.
    """,
    tools=[process_request_tool],
    sub_agents=[weather_agent, rainbow_agent, user_agent, notification_agent],
    output_key="coordinator_response"
)