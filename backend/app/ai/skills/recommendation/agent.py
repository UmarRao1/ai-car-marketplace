from sqlalchemy.orm import Session

from backend.app.ai.skills.recommendation.query import (
    extract_recommendation_filters
)

from backend.app.ai.skills.recommendation.skill import (
    recommend_cars
)


def recommend_cars_from_message(
    db: Session,
    user_message: str
):
    filters = extract_recommendation_filters(
        user_message
    )

    return recommend_cars(
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