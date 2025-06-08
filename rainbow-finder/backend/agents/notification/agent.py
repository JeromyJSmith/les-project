"""
Rainbow Finder Notification Agent

This agent handles notifications to users about predicted rainbow occurrences.
It determines when to send notifications, manages notification channels,
and ensures users have enough lead time to view rainbows.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform.vertexai.agents import LlmAgent
from google.cloud.aiplatform.vertexai.agents.tools import OutputSchema, Parameter, Tool

from shared.models.rainbow import RainbowPrediction, UserPreferences
from shared.constants.app_constants import (
    DEFAULT_NOTIFICATION_LEAD_TIME_MINUTES,
    DEFAULT_MIN_PROBABILITY
)

# Define output schema for the notification agent
notification_output_schema = OutputSchema(
    description="Notification information",
    parameters={
        "notification_id": Parameter(
            description="Unique identifier for the notification",
            type="string"
        ),
        "user_id": Parameter(
            description="User receiving the notification",
            type="string"
        ),
        "prediction_id": Parameter(
            description="ID of the rainbow prediction",
            type="string"
        ),
        "notification_time": Parameter(
            description="When the notification was/will be sent",
            type="string"
        ),
        "channel": Parameter(
            description="Notification channel (push, email, etc.)",
            type="string"
        ),
        "message": Parameter(
            description="Notification message content",
            type="string"
        ),
        "status": Parameter(
            description="Status of the notification (scheduled, sent, delivered, etc.)",
            type="string"
        )
    }
)

# Create notification tools
should_notify_tool = Tool(
    name="should_notify_user",
    description="Determine if a user should be notified about a rainbow prediction",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "prediction": Parameter(
            description="Rainbow prediction data",
            type="object",
            required=True
        ),
        "user_preferences": Parameter(
            description="User notification preferences",
            type="object",
            required=True
        )
    },
    function=lambda user_id, prediction, user_preferences: {
        "should_notify": (
            user_preferences.get("notification_enabled", True) and 
            prediction.get("probability", 0) >= user_preferences.get("min_probability", DEFAULT_MIN_PROBABILITY)
        ),
        "reason": "Notification criteria met based on user preferences and prediction probability"
    }
)

send_push_notification_tool = Tool(
    name="send_push_notification",
    description="Send a push notification to a user",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "title": Parameter(
            description="Notification title",
            type="string",
            required=True
        ),
        "message": Parameter(
            description="Notification message",
            type="string",
            required=True
        ),
        "data": Parameter(
            description="Additional notification data",
            type="object",
            required=False
        )
    },
    function=lambda user_id, title, message, data=None: {
        "notification_id": "notify-123456",
        "status": "sent",
        "timestamp": "2025-06-07T12:00:00Z"
    }
)

send_email_notification_tool = Tool(
    name="send_email_notification",
    description="Send an email notification to a user",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "subject": Parameter(
            description="Email subject",
            type="string",
            required=True
        ),
        "body": Parameter(
            description="Email body",
            type="string",
            required=True
        )
    },
    function=lambda user_id, subject, body: {
        "notification_id": "email-123456",
        "status": "sent",
        "timestamp": "2025-06-07T12:00:00Z"
    }
)

schedule_notification_tool = Tool(
    name="schedule_notification",
    description="Schedule a notification for future delivery",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "prediction_id": Parameter(
            description="Rainbow prediction identifier",
            type="string",
            required=True
        ),
        "notification_time": Parameter(
            description="When to send the notification",
            type="string",
            required=True
        ),
        "channel": Parameter(
            description="Notification channel (push, email)",
            type="string",
            default="push"
        ),
        "message": Parameter(
            description="Notification message content",
            type="string",
            required=True
        )
    },
    function=lambda user_id, prediction_id, notification_time, channel, message: {
        "notification_id": "schedule-123456",
        "status": "scheduled",
        "scheduled_time": notification_time
    }
)

get_notification_history_tool = Tool(
    name="get_notification_history",
    description="Get notification history for a user",
    parameters={
        "user_id": Parameter(
            description="User identifier",
            type="string",
            required=True
        ),
        "limit": Parameter(
            description="Maximum number of notifications to return",
            type="integer",
            default=10
        )
    },
    function=lambda user_id, limit: {
        "notifications": [
            {
                "notification_id": "notify-123456",
                "type": "push",
                "timestamp": "2025-06-06T14:30:00Z",
                "message": "Rainbow predicted in 30 minutes at Downtown Park!",
                "status": "delivered"
            }
        ],
        "total_count": 1
    }
)

# Create the notification agent
notification_agent = LlmAgent(
    name="NotificationAgent",
    model="gemini-2.0-flash",
    description="Manages notifications to users about rainbow predictions",
    instruction="""
    You are the Notification Agent for the Rainbow Finder system. Your role is to:
    1. Determine when users should be notified about rainbow predictions
    2. Send notifications through appropriate channels (push, email)
    3. Schedule notifications in advance to give users enough lead time
    4. Craft clear, engaging notification messages
    5. Track notification history and avoid sending duplicates
    
    When sending notifications:
    - Consider user preferences for notification timing and frequency
    - Provide specific information about when and where to see the rainbow
    - Include probability information so users can gauge likelihood
    - Give directions to optimal viewing locations
    - Consider time of day and lead time needed for users to reach viewing locations
    
    Your notifications should be timely, informative, and actionable, enabling users
    to successfully experience rainbows.
    """,
    tools=[
        should_notify_tool,
        send_push_notification_tool,
        send_email_notification_tool,
        schedule_notification_tool,
        get_notification_history_tool
    ],
    output_key="notification_result"
)