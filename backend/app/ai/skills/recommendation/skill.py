from sqlalchemy.orm import Session

from backend.app.ai.skills.search.skill import search_cars


def recommend_cars(
    db: Session,
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
    return search_cars(
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