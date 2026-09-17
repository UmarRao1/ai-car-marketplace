import json

from backend.app.ai.gemini import client


def extract_car_filters(user_message: str) -> dict:

    prompt = f"""
You are a car marketplace search assistant.

Convert the user's car-search request into JSON filters.

Available fields:

- search: car make or model
- city: city name
- fuel_type: fuel type
- transmission: transmission type
- min_price: minimum price as a number
- max_price: maximum price as a number
- min_year: minimum year
- max_year: maximum year
- min_mileage: minimum mileage
- max_mileage: maximum mileage

Rules:

1. Return ONLY valid JSON.
2. Do not add explanations.
3. Use null when a value is not mentioned.
4. Convert "30 lakh" to 3000000.
5. Convert "25 lakh" to 2500000.
6. Convert "20 lakh" to 2000000.
7. Do not invent values.

Example:

User:
Find me an automatic Toyota under 30 lakh in Bahawalpur

Output:
{{
    "search": "Toyota",
    "city": "Bahawalpur",
    "fuel_type": null,
    "transmission": "Automatic",
    "min_price": null,
    "max_price": 3000000,
    "min_year": null,
    "max_year": null,
    "min_mileage": null,
    "max_mileage": null
}}

User request:

{user_message}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return json.loads(response.text.strip())