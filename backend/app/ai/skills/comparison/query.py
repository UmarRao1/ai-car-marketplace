import json

from backend.app.ai.gemini import client


def extract_car_ids(user_message: str) -> list[int]:

    prompt = f"""
You are a car marketplace assistant.

Extract the car IDs that the user wants to compare.

Return ONLY valid JSON.

The JSON must have this format:

{{
    "car_ids": [2, 4]
}}

Rules:

1. Return only IDs explicitly mentioned by the user.
2. Do not invent IDs.
3. Return an empty list if no car IDs are mentioned.
4. Car IDs are integers.

User message:

{user_message}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    data = json.loads(response.text.strip())

    return data.get("car_ids", [])