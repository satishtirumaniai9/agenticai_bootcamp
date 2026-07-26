
import json
import os

from dotenv import load_dotenv

load_dotenv()


SAMPLE_WEATHER = {
    "tokyo": {"celsius": 22, "conditions": "partly cloudy"},
    "delhi": {"celsius": 34, "conditions": "clear skies"},
    "london": {"celsius": 15, "conditions": "light rain"},
}


def get_weather(city: str) -> str:
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"


get_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever "
                        "the user asks about weather, temperature, or conditions "
                        "in a specific place. Don't use it for AQI"
                        },
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}
            }
                            },
}

get_air_quality_schema = {
    "type": "function",
    "function": {
        "name": "get_air_quality",
        "description": "Get the current air quality for a city. Use this whenever "
                        "the user asks about air quality, pollution, or AQI "
                        "in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Delhi'."}
            },
            "required": ["city"],
        },
    },
}

get_calculator_schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Use this tool to perform calculations. Use this whenever "
                        "the user asks for a calculation or a math problem.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The mathematical expression to calculate, e.g. '2 + 2'."}
            },
            "required": ["expression"],
        },
    },
}
get_complete_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever "
                        "the user asks about weather, temperature, or conditions "
                        "in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}
            },
            "required": ["city"],
        },
    },
}

get_capital_schema = {
    "type": "function",
    "function": {
        "name": "get_capital",
        "description": "Get the capital city of a country. Use this whenever "
                        "the user asks about the capital of a specific country.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "The country name, e.g. 'France'."}
            },
            "required": ["country"],
        },
    },
}


def get_tool_information(tool_name):
    return get_tool_schemas().get(tool_name)

get_tool_schemas = lambda: {
    "get_weather": get_complete_weather_schema,
    "get_air_quality": get_air_quality_schema,
    "calculator": get_calculator_schema,
    "get_capital": get_capital_schema,
}

get_tool_schema_for_llm={
    "type": "function",
    "function": {
        "name": "get_tool_schema_for_llm",
        "description": "Get the schema of a tool by its name. Use this whenever " 
                        "the user asks for the schema of a specific tool.",     
        "parameters": {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "The name of the tool, e.g. 'get_weather'."}
            },
            "required": ["tool_name"],
        },
    },
}



def get_client_and_model():
    from openai import OpenAI

    if os.environ.get("GROQ_API_KEY"):
        return (
            OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1"),
            "llama-3.3-70b-versatile",
        )
    if os.environ.get("OPENROUTER_API_KEY"):
        return (
            OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1"),
            "openrouter/free",
        )
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), "gpt-4o-mini"

    raise RuntimeError(
        "No OpenAI-compatible key found. Set one of GROQ_API_KEY, "
        "OPENROUTER_API_KEY, or OPENAI_API_KEY in your .env file."
    )


def ask_ai_to_choose(question: str):
    client, model = get_client_and_model()
    response = client.chat.completions.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": question}],
        tools=[get_weather_schema,get_capital_schema, get_tool_schema_for_llm],
    )

    return response.choices[0].message


if __name__ == "__main__": 
    question =  "what is the Weather in Tokyo? "
    message = ask_ai_to_choose(question)

    print(f"Model's raw reply: {message!r}")

    if message.tool_calls:
        call = message.tool_calls[0]
        arguments = json.loads(call.function.arguments)
        result = get_weather(**arguments)
        print(f"{call.function.name}({arguments}) -> {result}")
    else:
        print(message.content)


