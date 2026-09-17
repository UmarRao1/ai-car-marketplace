from sqlalchemy.orm import Session

from backend.app.ai.skills.search.query import (
    extract_car_filters
)

from backend.app.ai.skills.search.skill import (
    search_cars
)


def search_cars_from_message(
    db: Session,
    user_message: str
):
    filters = extract_car_filters(
        user_message
    )

    cars = search_cars(
        db=db,
        search=filters.get("search"),
        city=filters.get("city"),
        fuel_type=filters.get("fuel_type"),
        transmission=filters.get("transmission"),
        min_price=filters.get("min_price"),
        max_price=filters.get("max_price"),
        min_year=filters.get("min_year"),
        max_year=filters.get("max_year"),
        min_mileage=filters.get("min_mileage"),
        max_mileage=filters.get("max_mileage"),
    )

    return cars
    