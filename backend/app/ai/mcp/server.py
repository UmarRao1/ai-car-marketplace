from mcp.server.fastmcp import FastMCP

from backend.app.database.database import SessionLocal
from backend.app.models.car import Car
from backend.app.models.car_image import CarImage

from backend.app.ai.skills.search.skill import search_cars
from backend.app.ai.skills.comparison.skill import compare_cars
from backend.app.ai.skills.recommendation.skill import recommend_cars


mcp = FastMCP("Car Marketplace")


# ============================================================
# 1. SEARCH CARS
# ============================================================

@mcp.tool()
def search_cars_tool(
    search: str | None = None,
    city: str | None = None,
    fuel_type: str | None = None,
    transmission: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_mileage: int | None = None,
    max_mileage: int | None = None,
):
    """
    Search available cars in the marketplace.
    """

    db = SessionLocal()

    try:
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

        return [
            {
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
            for car in cars
        ]

    finally:
        db.close()


# ============================================================
# 2. GET CAR DETAILS
# ============================================================

@mcp.tool()
def get_car_details_tool(car_id: int):
    """
    Get complete details of a specific car.
    """

    db = SessionLocal()

    try:
        car = db.query(Car).filter(
            Car.id == car_id
        ).first()

        if car is None:
            return {
                "error": "Car not found"
            }

        images = db.query(CarImage).filter(
            CarImage.car_id == car_id
        ).all()

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
            "images": [
                {
                    "id": image.id,
                    "image_url": (
                        "http://127.0.0.1:8000/"
                        + image.image_path.replace("\\", "/")
                    )
                }
                for image in images
            ]
        }

    finally:
        db.close()


# ============================================================
# 3. COMPARE CARS
# ============================================================

@mcp.tool()
def compare_cars_tool(car_ids: list[int]):
    """
    Get cars requested by the user for comparison.
    """

    db = SessionLocal()

    try:
        cars = compare_cars(
            db=db,
            car_ids=car_ids
        )

        return [
            {
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
            for car in cars
        ]

    finally:
        db.close()


# ============================================================
# 4. RECOMMEND CARS
# ============================================================

@mcp.tool()
def recommend_cars_tool(
    search: str | None = None,
    city: str | None = None,
    fuel_type: str | None = None,
    transmission: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_mileage: int | None = None,
    max_mileage: int | None = None,
):
    """
    Find cars matching the user's requirements.
    """

    db = SessionLocal()

    try:
        cars = recommend_cars(
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

        return [
            {
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
            for car in cars
        ]

    finally:
        db.close()


# ============================================================
# START MCP SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()