import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.auth.routes import router as auth_router
from backend.app.database.database import (
    Base,
    engine,
    SessionLocal
)

from backend.app.models.user import User
from backend.app.models.car import Car
from backend.app.models.car_image import CarImage

from backend.app.api.routes.cars import (
    router as cars_router
)

from backend.app.ai.agent import (
    run_marketplace_agent
)


# =====================================================
# DATABASE
# =====================================================

Base.metadata.create_all(
    bind=engine
)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Car Marketplace API"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(
    cars_router
)

app.include_router(
    auth_router
)


# =====================================================
# AI REQUEST
# =====================================================

class AgentRequest(BaseModel):
    message: str


# =====================================================
# FIND CAR IDS INSIDE AI RESULT
# =====================================================

def extract_listing_ids(
    value,
    ids=None
):
    """
    Recursively find car/listing IDs
    from the result returned by the AI agent.
    """

    if ids is None:
        ids = set()

    if value is None:
        return ids


    # -----------------------------
    # DICTIONARY
    # -----------------------------

    if isinstance(
        value,
        dict
    ):

        car_fields = {
            "make",
            "model",
            "year",
            "price",
            "mileage",
            "fuel_type",
            "transmission"
        }

        for key, item in value.items():

            key_name = str(
                key
            ).lower()


            if key_name in {
                "car_id",
                "listing_id",
                "vehicle_id"
            }:

                try:
                    ids.add(
                        int(item)
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    pass


            elif (
                key_name == "id"
                and isinstance(
                    item,
                    int
                )
                and any(
                    field in value
                    for field in car_fields
                )
            ):

                ids.add(
                    item
                )


            extract_listing_ids(
                item,
                ids
            )

        return ids


    # -----------------------------
    # LIST / TUPLE / SET
    # -----------------------------

    if isinstance(
        value,
        (
            list,
            tuple,
            set
        )
    ):

        for item in value:

            extract_listing_ids(
                item,
                ids
            )

        return ids


    # -----------------------------
    # STRING
    # -----------------------------

    if isinstance(
        value,
        str
    ):

        patterns = [

            r"listing\s*(?:id)?\s*[:#-]?\s*(\d+)",

            r"car\s*(?:id)?\s*[:#-]?\s*(\d+)",

            r"vehicle\s*(?:id)?\s*[:#-]?\s*(\d+)",

        ]


        for pattern in patterns:

            matches = re.findall(
                pattern,
                value,
                flags=re.IGNORECASE
            )

            for match in matches:

                try:
                    ids.add(
                        int(match)
                    )

                except ValueError:
                    pass


    return ids


# =====================================================
# SERIALIZE CAR FOR AI
# =====================================================

def serialize_agent_car(
    car: Car,
    db: Session
):

    images = (
        db.query(
            CarImage
        )
        .filter(
            CarImage.car_id == car.id
        )
        .order_by(
            CarImage.id.asc()
        )
        .all()
    )


    seller = (
        db.query(
            User
        )
        .filter(
            User.id == car.seller_id
        )
        .first()
    )


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

        "seller_name": (
            seller.name
            if seller
            else "Unknown Seller"
        ),

        "images": [

            {
                "id": image.id,

                "image_url": (
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


# =====================================================
# CONVERT AI RESULT TO MESSAGE
# =====================================================

def extract_agent_message(
    result
):

    if isinstance(
        result,
        str
    ):
        return result


    if isinstance(
        result,
        dict
    ):

        for key in [
            "message",
            "answer",
            "response",
            "text"
        ]:

            value = result.get(
                key
            )

            if value:

                if isinstance(
                    value,
                    str
                ):
                    return value

                return str(
                    value
                )


        if "result" in result:

            return str(
                result["result"]
            )


    return str(
        result
    )


# =====================================================
# AI AGENT ENDPOINT
# =====================================================

@app.post(
    "/agent"
)
def car_marketplace_agent(
    request: AgentRequest
):

    # Run existing AI agent
    result = run_marketplace_agent(
        request.message
    )


    # Find listing IDs
    listing_ids = extract_listing_ids(
        result
    )


    db = SessionLocal()

    try:

        listings = []


        if listing_ids:

            cars = (
                db.query(
                    Car
                )
                .filter(
                    Car.id.in_(
                        list(
                            listing_ids
                        )
                    )
                )
                .all()
            )


            cars_by_id = {
                car.id: car
                for car in cars
            }


            # Keep AI order as much as possible
            for listing_id in listing_ids:

                car = cars_by_id.get(
                    listing_id
                )

                if car:

                    listings.append(
                        serialize_agent_car(
                            car,
                            db
                        )
                    )


        return {

            "message":
                extract_agent_message(
                    result
                ),

            "listings":
                listings

        }

    finally:

        db.close()


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message":
            "Car Marketplace API is running!"
    }