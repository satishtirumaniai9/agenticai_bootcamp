

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-5",
    messages=[
        {"role": "user", "content": "Who will win the 2026 FIFA World Cup?"},
    ],
)

print(response.choices[0].message.content)