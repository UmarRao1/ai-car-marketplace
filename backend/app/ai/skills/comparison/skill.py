from sqlalchemy.orm import Session

from backend.app.models.car import Car


def compare_cars(
    db: Session,
    car_ids: list[int]
):
    cars = db.query(Car).filter(
        Car.id.in_(car_ids)
    ).all()

    cars_by_id = {
        car.id: car
        for car in cars
    }

    ordered_cars = [
        cars_by_id[car_id]
        for car_id in car_ids
        if car_id in cars_by_id
    ]

    return ordered_cars