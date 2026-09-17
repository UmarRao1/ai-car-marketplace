import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.ai.gemini import client

from backend.app.database.database import SessionLocal

from backend.app.models.car import Car
from backend.app.models.car_image import CarImage

from backend.app.ai.skills.search.skill import search_cars
from backend.app.ai.skills.comparison.skill import compare_cars
from backend.app.ai.skills.recommendation.skill import recommend_cars


# ============================================================
# CONVERT CAR OBJECT TO DICTIONARY
# ============================================================

def car_to_dict(car):
    return {
        "id": car.id,
        "make": car.make,
        "model": car.model,
        "year": car.year,
        "price": car.price,
        "mileage": car.mileage,
        "fuel_type": car.fuel_type,
        "fuel_average": car.fuel_average,
        "transmission": car.transmission,
        "city": car.city,
        "contact_number": car.contact_number,
        "description": car.description,
        "seller_id": car.seller_id,
    }


# ============================================================
# FORMAT SEARCH RESULT
# ============================================================

def format_search_answer(cars):

    if not cars:
        return "I could not find any cars matching your requirements."

    lines = [
        f"I found {len(cars)} matching car(s):"
    ]

    for car in cars:

        lines.append(
            f"- {car.make} {car.model} {car.year} | "
            f"Rs {car.price:,.0f} | "
            f"{car.transmission} | "
            f"{car.fuel_type} | "
            f"{car.mileage:,} km | "
            f"{car.city}"
        )

    return "\n".join(lines)


# ============================================================
# FORMAT RECOMMENDATION RESULT
# ============================================================

def format_recommendation_answer(cars):

    if not cars:
        return (
            "I could not find a car matching "
            "your requirements."
        )

    # Rule-based ranking:
    # newer year
    # lower mileage
    # better fuel average
    # lower price

    ranked_cars = sorted(
        cars,
        key=lambda car: (
            -(car.year or 0),
            car.mileage or float("inf"),
            -(car.fuel_average or 0),
            car.price or float("inf"),
        )
    )

    best = ranked_cars[0]

    answer = (
        "Based on your requirements, "
        "the top matching car is:\n\n"

        f"{best.make} {best.model} {best.year}\n"
        f"Price: Rs {best.price:,.0f}\n"
        f"Mileage: {best.mileage:,} km\n"
        f"Fuel: {best.fuel_type}\n"
        f"Fuel average: {best.fuel_average} km/l\n"
        f"Transmission: {best.transmission}\n"
        f"City: {best.city}\n"
        f"Contact: {best.contact_number}"
    )

    if len(ranked_cars) > 1:

        answer += (
            f"\n\nI found {len(ranked_cars)} "
            "matching cars in total."
        )

    return answer


# ============================================================
# FORMAT COMPARISON RESULT
# ============================================================

def format_comparison_answer(cars):

    if not cars:
        return (
            "I could not find the cars you "
            "wanted to compare."
        )

    if len(cars) == 1:

        return (
            "I found only one matching car. "
            "Please mention another car to compare it with.\n\n"
            + format_search_answer(cars)
        )

    lines = [
        "Here is the comparison:\n"
    ]

    for car in cars:

        lines.append(
            f"{car.make} {car.model} {car.year}\n"
            f"  Price: Rs {car.price:,.0f}\n"
            f"  Mileage: {car.mileage:,} km\n"
            f"  Fuel: {car.fuel_type}\n"
            f"  Fuel average: {car.fuel_average} km/l\n"
            f"  Transmission: {car.transmission}\n"
            f"  City: {car.city}\n"
        )

    return "\n".join(lines)


# ============================================================
# FORMAT DETAILS RESULT
# ============================================================

def format_details_answer(car, images):

    if car is None:
        return "The requested car was not found."

    answer = (
        f"Complete details for "
        f"{car.make} {car.model} {car.year}:\n\n"

        f"Make: {car.make}\n"
        f"Model: {car.model}\n"
        f"Year: {car.year}\n"
        f"Price: Rs {car.price:,.0f}\n"
        f"Mileage: {car.mileage:,} km\n"
        f"Fuel type: {car.fuel_type}\n"
        f"Fuel average: {car.fuel_average} km/l\n"
        f"Transmission: {car.transmission}\n"
        f"City: {car.city}\n"
        f"Contact: {car.contact_number}\n"
        f"Description: {car.description}\n"
    )

    if images:

        answer += "\nImages:\n"

        for image in images:

            image_url = (
                "http://127.0.0.1:8000/"
                + image.image_path.replace("\\", "/")
            )

            answer += f"- {image_url}\n"

    return answer


# ============================================================
# RESOLVE HUMAN-FRIENDLY COMPARISON REQUEST
# ============================================================

def resolve_comparison_cars(
    db: Session,
    comparison_requests: list
):

    resolved_cars = []
    ambiguous_requests = []

    for item in comparison_requests:

        if not isinstance(item, dict):
            continue

        search = item.get("search")
        city = item.get("city")
        fuel_type = item.get("fuel_type")
        transmission = item.get("transmission")

        min_price = item.get("min_price")
        max_price = item.get("max_price")

        min_year = item.get("min_year")
        max_year = item.get("max_year")

        min_mileage = item.get("min_mileage")
        max_mileage = item.get("max_mileage")

        cars = search_cars(
            db=db,
            search=search,
            city=city,
            fuel_type=fuel_type,
            transmission=transmission,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year,
            min_mileage=min_mileage,
            max_mileage=max_mileage,
        )

        if not cars:

            ambiguous_requests.append({
                "request": item,
                "reason": "no_match"
            })

            continue

        # ----------------------------------------------
        # EXACT / UNIQUE MATCH
        # ----------------------------------------------

        if len(cars) == 1:

            resolved_cars.append(cars[0])

            continue

        # ----------------------------------------------
        # TRY TO FIND A MORE EXACT MATCH
        # ----------------------------------------------

        exact_matches = cars

        requested_year = item.get("year")

        if requested_year is not None:

            year_matches = [
                car
                for car in exact_matches
                if car.year == requested_year
            ]

            if year_matches:
                exact_matches = year_matches

        if len(exact_matches) == 1:

            resolved_cars.append(
                exact_matches[0]
            )

            continue

        # ----------------------------------------------
        # AMBIGUOUS
        # ----------------------------------------------

        ambiguous_requests.append({
            "request": item,
            "reason": "multiple_matches",
            "cars": exact_matches
        })

    return (
        resolved_cars,
        ambiguous_requests
    )


# ============================================================
# MAIN MARKETPLACE AGENT
# ============================================================

def run_marketplace_agent(
    user_message: str
):

    # --------------------------------------------------------
    # 1. ASK GEMINI TO UNDERSTAND USER REQUEST
    # --------------------------------------------------------

    prompt = f"""
You are the intent detection system for a car marketplace.

Understand the user's request and return ONLY valid JSON.

Possible intents:

- search
- compare
- recommend
- details

Return this structure:

{{
    "intent": "search",

    "search": null,
    "city": null,
    "fuel_type": null,
    "transmission": null,

    "min_price": null,
    "max_price": null,

    "min_year": null,
    "max_year": null,

    "min_mileage": null,
    "max_mileage": null,

    "car_ids": [],

    "comparison_requests": []
}}

IMPORTANT RULES:

1. "Find", "search", "show", or
   "looking for" usually means search.

2. "Compare", "comparison", "compare these",
   "which is better", or "compare X and Y"
   means compare.

3. "Recommend", "suggest", or
   "which car should I consider"
   means recommend.

4. "Details", "complete details",
   "tell me about this car", or a request
   for information about a specific car
   means details.

5. Extract numeric car/listing IDs ONLY
   when the user explicitly mentions them.

6. NEVER invent an ID.

7. The user normally does NOT know internal
   listing IDs.

8. For comparison requests, DO NOT require
   listing IDs.

9. For comparison requests, identify each
   requested car using human-readable information.

10. A human-readable car reference may contain:

    - make
    - model
    - year
    - city
    - fuel type
    - transmission
    - price
    - mileage

11. For example:

    User:
    "Compare Suzuki Alto and Honda BR-V"

    Return something similar to:

    {{
        "intent": "compare",
        "search": null,
        "city": null,
        "fuel_type": null,
        "transmission": null,
        "min_price": null,
        "max_price": null,
        "min_year": null,
        "max_year": null,
        "min_mileage": null,
        "max_mileage": null,
        "car_ids": [],
        "comparison_requests": [
            {{
                "search": "Suzuki Alto",
                "city": null,
                "fuel_type": null,
                "transmission": null,
                "min_price": null,
                "max_price": null,
                "min_year": null,
                "max_year": null,
                "min_mileage": null,
                "max_mileage": null
            }},
            {{
                "search": "Honda BR-V",
                "city": null,
                "fuel_type": null,
                "transmission": null,
                "min_price": null,
                "max_price": null,
                "min_year": null,
                "max_year": null,
                "min_mileage": null,
                "max_mileage": null
            }}
        ]
    }}

12. If the user says:

    "Compare Alto and BR-V in BWP"

    include BWP in both comparison requests.

13. If the user says:

    "Compare a manual Alto and automatic BR-V"

    include the appropriate transmission
    in each comparison request.

14. If the user says:

    "Compare the 2023 Alto and 2022 BR-V"

    include the appropriate year
    in each comparison request.

15. If the user says:

    "Compare the Suzuki under 30 lakh
    with the Honda under 40 lakh"

    include the corresponding price
    limits in each comparison request.

16. For a comparison, create one
    comparison_requests item for EACH car.

17. Do not ask the user for IDs merely
    because they did not provide IDs.

18. Convert lakh into numbers.

19. Examples:

    30 lakh = 3000000
    25 lakh = 2500000
    20 lakh = 2000000

20. Use null for values not mentioned.

21. Return ONLY valid JSON.

User request:

{user_message}
"""

    # --------------------------------------------------------
    # GEMINI REQUEST
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"Gemini request failed: {str(e)}"
        )

    if not response.text:

        raise HTTPException(
            status_code=502,
            detail="Gemini returned an empty response."
        )

    raw_response = response.text.strip()

    # Remove markdown JSON fences
    if raw_response.startswith("```"):

        raw_response = raw_response.replace(
            "```json",
            ""
        )

        raw_response = raw_response.replace(
            "```",
            ""
        )

        raw_response = raw_response.strip()

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        request_data = json.loads(
            raw_response
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=502,
            detail={
                "message":
                    "Gemini did not return valid JSON.",
                "gemini_response":
                    raw_response
            }
        )

    intent = request_data.get(
        "intent"
    )

    db = SessionLocal()

    try:

        # ====================================================
        # SEARCH
        # ====================================================

        if intent == "search":

            cars = search_cars(
                db=db,
                search=request_data.get(
                    "search"
                ),
                city=request_data.get(
                    "city"
                ),
                fuel_type=request_data.get(
                    "fuel_type"
                ),
                transmission=request_data.get(
                    "transmission"
                ),
                min_price=request_data.get(
                    "min_price"
                ),
                max_price=request_data.get(
                    "max_price"
                ),
                min_year=request_data.get(
                    "min_year"
                ),
                max_year=request_data.get(
                    "max_year"
                ),
                min_mileage=request_data.get(
                    "min_mileage"
                ),
                max_mileage=request_data.get(
                    "max_mileage"
                ),
            )

            return {
                "intent": "search",

                "message":
                    format_search_answer(cars),

                "count":
                    len(cars),

                "results": [
                    car_to_dict(car)
                    for car in cars
                ]
            }

        # ====================================================
        # RECOMMEND
        # ====================================================

        if intent == "recommend":

            cars = recommend_cars(
                db=db,
                search=request_data.get(
                    "search"
                ),
                city=request_data.get(
                    "city"
                ),
                fuel_type=request_data.get(
                    "fuel_type"
                ),
                transmission=request_data.get(
                    "transmission"
                ),
                min_price=request_data.get(
                    "min_price"
                ),
                max_price=request_data.get(
                    "max_price"
                ),
                min_year=request_data.get(
                    "min_year"
                ),
                max_year=request_data.get(
                    "max_year"
                ),
                min_mileage=request_data.get(
                    "min_mileage"
                ),
                max_mileage=request_data.get(
                    "max_mileage"
                ),
            )

            return {
                "intent": "recommend",

                "message":
                    format_recommendation_answer(
                        cars
                    ),

                "count":
                    len(cars),

                "results": [
                    car_to_dict(car)
                    for car in cars
                ]
            }

        # ====================================================
        # COMPARE
        # ====================================================

        if intent == "compare":

            comparison_requests = (
                request_data.get(
                    "comparison_requests",
                    []
                )
            )

            explicit_car_ids = (
                request_data.get(
                    "car_ids",
                    []
                )
            )

            # ------------------------------------------------
            # FIRST: HUMAN-FRIENDLY COMPARISON
            # ------------------------------------------------

            if comparison_requests:

                cars, ambiguous_requests = (
                    resolve_comparison_cars(
                        db=db,
                        comparison_requests=(
                            comparison_requests
                        )
                    )
                )

                # --------------------------------------------
                # AMBIGUOUS REQUEST
                # --------------------------------------------

                if ambiguous_requests:

                    message_parts = []

                    for item in ambiguous_requests:

                        request = item.get(
                            "request",
                            {}
                        )

                        request_name = (
                            request.get(
                                "search"
                            )
                            or "the requested car"
                        )

                        if item.get(
                            "reason"
                        ) == "no_match":

                            message_parts.append(
                                f"I could not find "
                                f"a listing matching "
                                f"'{request_name}'."
                            )

                        else:

                            matching_cars = item.get(
                                "cars",
                                []
                            )

                            options = []

                            for car in matching_cars[:5]:

                                options.append(
                                    f"{car.make} "
                                    f"{car.model} "
                                    f"{car.year} "
                                    f"(Rs "
                                    f"{car.price:,.0f}, "
                                    f"{car.city})"
                                )

                            message_parts.append(
                                f"I found multiple "
                                f"listings matching "
                                f"'{request_name}'. "
                                f"Please specify the "
                                f"year, city, price, "
                                f"or another feature.\n"
                                +
                                "\n".join(
                                    f"- {option}"
                                    for option in options
                                )
                            )

                    # If we couldn't resolve all requested
                    # comparison cars, do not compare
                    # an incomplete set.
                    return {
                        "intent": "compare",
                        "message": "\n\n".join(
                            message_parts
                        ),
                        "count": 0,
                        "results": []
                    }

                # --------------------------------------------
                # NEED AT LEAST TWO CARS
                # --------------------------------------------

                if len(cars) < 2:

                    if not cars:

                        return {
                            "intent": "compare",
                            "message": (
                                "I could not find "
                                "the cars you want "
                                "to compare."
                            ),
                            "count": 0,
                            "results": []
                        }

                    return {
                        "intent": "compare",
                        "message": (
                            "I found only one "
                            "matching car. "
                            "Please mention another "
                            "car to compare it with."
                        ),
                        "count": 1,
                        "results": [
                            car_to_dict(cars[0])
                        ]
                    }

                # --------------------------------------------
                # SUCCESSFUL HUMAN-FRIENDLY COMPARISON
                # --------------------------------------------

                return {
                    "intent": "compare",

                    "message":
                        format_comparison_answer(
                            cars
                        ),

                    "count":
                        len(cars),

                    "results": [
                        car_to_dict(car)
                        for car in cars
                    ]
                }

            # ------------------------------------------------
            # SECOND: EXPLICIT IDS
            # ------------------------------------------------

            if explicit_car_ids:

                cars = compare_cars(
                    db=db,
                    car_ids=explicit_car_ids
                )

                return {
                    "intent": "compare",

                    "message":
                        format_comparison_answer(
                            cars
                        ),

                    "count":
                        len(cars),

                    "results": [
                        car_to_dict(car)
                        for car in cars
                    ]
                }

            # ------------------------------------------------
            # NOTHING PROVIDED
            # ------------------------------------------------

            return {
                "intent": "compare",

                "message": (
                    "Please tell me the names or "
                    "features of the cars you want "
                    "to compare, for example: "
                    "'Compare Suzuki Alto and "
                    "Honda BR-V'."
                ),

                "count": 0,
                "results": []
            }

        # ====================================================
        # DETAILS
        # ====================================================

        if intent == "details":

            car_ids = request_data.get(
                "car_ids",
                []
            )

            # ------------------------------------------------
            # DETAILS BY EXPLICIT ID
            # ------------------------------------------------

            if car_ids:

                car_id = car_ids[0]

                car = (
                    db.query(Car)
                    .filter(
                        Car.id == car_id
                    )
                    .first()
                )

                if car is None:

                    return {
                        "intent": "details",
                        "message":
                            "Car not found.",
                        "count": 0,
                        "results": []
                    }

                images = (
                    db.query(CarImage)
                    .filter(
                        CarImage.car_id == car_id
                    )
                    .all()
                )

                return {
                    "intent": "details",

                    "message":
                        format_details_answer(
                            car,
                            images
                        ),

                    "count": 1,

                    "results": [
                        {
                            **car_to_dict(car),

                            "images": [
                                {
                                    "id":
                                        image.id,

                                    "image_url":
                                        (
                                            "http://127.0.0.1:8000/"
                                            +
                                            image.image_path.replace(
                                                "\\",
                                                "/"
                                            )
                                        )
                                }

                                for image in images
                            ]
                        }
                    ]
                }

            # ------------------------------------------------
            # DETAILS BY HUMAN-FRIENDLY SEARCH
            # ------------------------------------------------

            search = request_data.get(
                "search"
            )

            if search:

                cars = search_cars(
                    db=db,
                    search=search,
                    city=request_data.get(
                        "city"
                    ),
                    fuel_type=request_data.get(
                        "fuel_type"
                    ),
                    transmission=request_data.get(
                        "transmission"
                    ),
                    min_price=request_data.get(
                        "min_price"
                    ),
                    max_price=request_data.get(
                        "max_price"
                    ),
                    min_year=request_data.get(
                        "min_year"
                    ),
                    max_year=request_data.get(
                        "max_year"
                    ),
                    min_mileage=request_data.get(
                        "min_mileage"
                    ),
                    max_mileage=request_data.get(
                        "max_mileage"
                    ),
                )

                if len(cars) == 1:

                    car = cars[0]

                    images = (
                        db.query(CarImage)
                        .filter(
                            CarImage.car_id == car.id
                        )
                        .all()
                    )

                    return {
                        "intent": "details",

                        "message":
                            format_details_answer(
                                car,
                                images
                            ),

                        "count": 1,

                        "results": [
                            {
                                **car_to_dict(
                                    car
                                ),

                                "images": [
                                    {
                                        "id":
                                            image.id,

                                        "image_url":
                                            (
                                                "http://127.0.0.1:8000/"
                                                +
                                                image.image_path.replace(
                                                    "\\",
                                                    "/"
                                                )
                                            )
                                    }

                                    for image in images
                                ]
                            }
                        ]
                    }

                if len(cars) > 1:

                    return {
                        "intent": "details",

                        "message": (
                            "I found multiple listings "
                            f"matching '{search}'. "
                            "Please specify the year, "
                            "city, price, or another "
                            "feature."
                        ),

                        "count": 0,
                        "results": []
                    }

            return {
                "intent": "details",

                "message": (
                    "Please tell me the car name "
                    "or another identifying feature "
                    "so I can find its details."
                ),

                "count": 0,
                "results": []
            }

        # ====================================================
        # UNKNOWN INTENT
        # ====================================================

        return {
            "intent": "unknown",

            "message": (
                "I can help you search cars, "
                "compare cars, recommend cars, "
                "or provide car details."
            ),

            "count": 0,
            "results": []
        }

    finally:

        db.close()