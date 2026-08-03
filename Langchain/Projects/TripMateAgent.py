from langchain_core.tools import tool
from langchain.agents.structured_output import ToolStrategy
import requests
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

import requests
from langchain_core.tools import tool
from tavily import TavilyClient
import os
import sqlite3
from pydantic import BaseModel,Field
from typing import Optional, Union
from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)

# WMO Weather Codes
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

load_dotenv()

@tool
def get_real_weather(city: str) -> str:
    """
    Get the current weather for a city using the Open-Meteo API.

    Args:
        city: Name of the city.

    Returns:
        Human-readable weather information.
    """
    try:
        # Step 1: Geocode city
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
            },
            timeout=10,
        )
        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Could not find location '{city}'."

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        location_name = location["name"]
        country = location.get("country", "")

        # Step 2: Get current weather
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                ],
            },
            timeout=10,
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data["current"]

        description = WEATHER_CODES.get(
            current["weather_code"],
            "Unknown",
        )

        return (
            f"Current weather in {location_name}, {country}:\n"
            f"🌤 Condition: {description}\n"
            f"🌡 Temperature: {current['temperature_2m']}°C\n"
            f"🤗 Feels Like: {current['apparent_temperature']}°C\n"
            f"💧 Humidity: {current['relative_humidity_2m']}%\n"
            f"💨 Wind Speed: {current['wind_speed_10m']} km/h"
        )

    except requests.RequestException as e:
        return f"Weather service error: {e}"

    except Exception as e:
        return f"Unexpected error: {e}"
    

@tool
def search_travel_info(query: str) -> str:
    """
    Search the web using the Tavily Search API.

    Args:
        query: Search query.

    Returns:
        Formatted search results.
    """

    try:
        api_key = os.getenv("TAVILY_API_KEY")
        # Create Tavily client
        client = TavilyClient(api_key=api_key)

        # Execute search
        response = client.search(
            query=query,
            search_depth="advanced",
            topic="general",
            max_results=5,
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )

        output = []

        # AI-generated answer
        if response.get("answer"):
            output.append("=" * 80)
            output.append("AI GENERATED ANSWER")
            output.append("=" * 80)
            output.append(response["answer"])
            output.append("")

        # Search Results
        output.append("=" * 80)
        output.append("SEARCH RESULTS")
        output.append("=" * 80)

        results = response.get("results", [])

        if not results:
            output.append("No search results found.")

        for i, result in enumerate(results, start=1):

            output.append(f"\n{i}. {result.get('title', 'No Title')}")
            output.append(f"URL      : {result.get('url', '')}")

            if result.get("score") is not None:
                output.append(f"Score    : {result['score']:.3f}")

            if result.get("content"):
                output.append(f"Summary  : {result['content']}")

        return "\n".join(output)

    except Exception as e:
        return f"Tavily Search Error: {str(e)}"
    
search_travel_info.invoke({"query": "Who won the FIFA World Cup in 2026`?"})

def setup_database():
    """
    Set up the SQLite database for storing travel information.
    """
    conn = sqlite3.connect("tripmate.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trips (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            destination TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'confirmed'
        )
        """
    )

    conn.commit()
    conn.close()
setup_database()


@tool
def save_trip(user_id: str, destination: str, start_date: str, end_date: str) -> str:
    """
    Save a trip to the SQLite database.

    Args:
        user_id: ID of the user.
        destination: Destination of the trip.
        start_date: Start date of the trip (YYYY-MM-DD).
        end_date: End date of the trip (YYYY-MM-DD).

    Returns:
        Confirmation message.
    """
    try:
        conn = sqlite3.connect("tripmate.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO trips (user_id, destination, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, destination, start_date, end_date),
        )

        conn.commit()
        conn.close()

        return f"Trip to {destination} from {start_date} to {end_date} saved successfully for user {user_id}."

    except Exception as e:
        return f"Error saving trip: {str(e)}"
    
@tool
def get_saved_trips(user_id: str) -> str:
    """
    Retrieve saved trips for a user from the SQLite database.

    Args:
        user_id: ID of the user.

    Returns:
        List of saved trips.
    """
    try:
        conn = sqlite3.connect("tripmate.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT trip_id,destination, start_date, end_date, status FROM trips WHERE user_id = ?
            """,
            (user_id,),
        )

        trips = cursor.fetchall()
        conn.close()

        if not trips:
            return f"No saved trips found for user {user_id}."

        output = [f"Trip to {trip[0]} from {trip[1]} to {trip[2]} (Status: {trip[3]})" for trip in trips]
        return "\n".join(output)

    except Exception as e:
        return f"Error retrieving saved trips: {str(e)}"

save_trip.invoke({"user_id": "user123", "destination": "Paris", "start_date": "2024-07-01", "end_date": "2024-07-10"})
save_trip.invoke({"user_id": "user123", "destination": "New York", "start_date": "2024-08-15", "end_date": "2024-08-25"})

def pretty_print_chat(state):
    """
    Pretty print a LangChain agent state.

    Args:
        state: Dictionary returned by agent.invoke(...)
    """

    role_icons = {
        HumanMessage: "🧑 Human",
        AIMessage: "🤖 AI",
        ToolMessage: "🛠️ Tool",
        SystemMessage: "⚙️ System",
    }

    print("=" * 100)

    for i, message in enumerate(state["messages"], start=1):

        role = role_icons.get(type(message), type(message).__name__)

        print(f"\n{role} ({i})")
        print("-" * 100)

        if message.content:
            print(message.content)

        # Print tool calls made by the AI
        if isinstance(message, AIMessage) and message.tool_calls:
            print("\n🔧 Tool Calls:")
            for tool in message.tool_calls:
                print(f"   • Tool : {tool['name']}")
                print(f"     Args : {tool['args']}")
                print(f"     ID   : {tool['id']}")

        # Print tool outputs
        if isinstance(message, ToolMessage):
            print(f"\nTool Name    : {message.name}")
            print(f"Tool Call ID : {message.tool_call_id}")

    print("\n" + "=" * 100)

from langgraph.checkpoint.memory import InMemorySaver
import uuid
checkpointer = InMemorySaver()

config = {
    "configurable": {
        "thread_id": str(uuid.uuid4())
    }
}


model = init_chat_model(
    model_provider="fireworks",
    model="accounts/fireworks/models/kimi-k3",
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)

class NewTripRequest(BaseModel):
    user_id: str
    destination: str
    start_date: str
    end_date: str

class ModifyTripRequest(BaseModel):
    trip_id: int
    user_id: str
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
class CancelTripRequest(BaseModel):
    trip_id: int
    user_id: str
        


from langchain.tools import ToolRuntime
from typing import Any
from langgraph.store.memory import InMemoryStore

travel_store = InMemoryStore()

@tool
def save_travel_style(user_id: str, style: str, runtime: ToolRuntime) -> str:
    """Save a traveler's preferred trip style (e.g. budget, luxury, adventure) for future visits."""
    runtime.store.put((user_id, "preferences"), "travel_style", {"value": style})
    return f"Noted -- I'll remember you prefer {style} travel."

@tool
def recall_travel_style(user_id: str, runtime: ToolRuntime) -> str:
    """Recall a traveler's preferred trip style, if saved before."""
    result = runtime.store.get((user_id, "preferences"), "travel_style")
    return result.value["value"] if result else "No travel style saved yet for this user."

@tool
def book_premium_concierge(destination: str) -> str:
    """Book a dedicated human concierge for trip planning. Premium members only."""
    return f"Premium concierge assigned for your {destination} trip."

from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def gate_premium_concierge(request: ModelRequest,handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Middleware to gate access to the book_premium_concierge tool."""
    is_premium_user = request.state.get("is_premium_user", False)
    if not is_premium_user:
        allowed_tools = [tool for tool in request.tools if tool.name != "book_premium_concierge"]
        request = request.override(tools=allowed_tools)
    return handler(request)    

from dataclasses import dataclass
from typing import Literal, Union

from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


@dataclass
class TravelerContext:
    user_id: str
    home_currency: str
    membership_tier: str
    is_premium_member: bool


class TravelInformationResponse(BaseModel):
    operation: Literal["travel_information"] = "travel_information"

    answer: str = Field(
        description="Answer to a general travel, destination, or weather question."
    )

    weather_checked: bool = Field(
        default=False,
        description="Whether the real weather tool was called."
    )

    preference_saved: bool = Field(
        default=False,
        description="Whether the user's travel preference was saved."
    )


TripMateResponse = Union[
    NewTripRequest,
    ModifyTripRequest,
    CancelTripRequest,
    TravelInformationResponse,
]


full_agent = create_agent(
    model=model,
    tools=[
        get_real_weather,
        search_travel_info,
        save_trip,
        get_saved_trips,
        save_travel_style,
        recall_travel_style,
        book_premium_concierge,
    ],
    system_prompt=(
        "You are TripMate, a real travel planning assistant. "
        "Use get_real_weather for current weather questions. "
        "Save trips only when confirmed. "
        "Save travel preferences when the user asks you to remember them. "
        "Do not repeatedly call the same tool with identical arguments. "
        "After the required tools complete, return the final structured response."
    ),
    middleware=[gate_premium_concierge],
    checkpointer=checkpointer,
    store=travel_store,
    context_schema=TravelerContext,
    name="TripMateAgent",
    response_format=ToolStrategy(TripMateResponse),
)


config = {
    "configurable": {
        "thread_id": "rohan-planning-session",
    },
    "recursion_limit": 25,
}


result = full_agent.invoke(
    {
        "messages": [
            (
                "user",
                "I'm rohan_01. What's the weather like in Bali? "
                "I prefer budget travel, please remember that.",
            )
        ],
    },
    config={
        "configurable": {
            "thread_id": "rohan-planning-session",
        },
        "recursion_limit": 25,
    },
    context={
        "user_id": "rohan_01",
        "home_currency": "INR",
        "membership_tier": "standard",
        "is_premium_member": False,
    },
)

pretty_print_chat(result)