from sqlalchemy.orm import Session

from backend.app.ai.skills.comparison.query import (
    extract_car_ids
)

from backend.app.ai.skills.comparison.skill import (
    compare_cars
)


def compare_cars_from_message(
    db: Session,
    user_message: str
):
    car_ids = extract_car_ids(user_message)

    cars = compare_cars(
        db=db,
        car_ids=car_ids
    )

    return cars