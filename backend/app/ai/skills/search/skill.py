from sqlalchemy.orm import Session

from backend.app.models.car import Car


def search_cars(
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
    query = db.query(Car)

    if search:
        search_text = f"%{search}%"

        query = query.filter(
            (Car.make.ilike(search_text))
            | (Car.model.ilike(search_text))
        )

    if city:
        query = query.filter(
            Car.city.ilike(city)
        )

    if fuel_type:
        query = query.filter(
            Car.fuel_type.ilike(fuel_type)
        )

    if transmission:
        query = query.filter(
            Car.transmission.ilike(transmission)
        )

    if min_price is not None:
        query = query.filter(
            Car.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Car.price <= max_price
        )

    if min_year is not None:
        query = query.filter(
            Car.year >= min_year
        )

    if max_year is not None:
        query = query.filter(
            Car.year <= max_year
        )

    if min_mileage is not None:
        query = query.filter(
            Car.mileage >= min_mileage
        )

    if max_mileage is not None:
        query = query.filter(
            Car.mileage <= max_mileage
        )

    return query.all()