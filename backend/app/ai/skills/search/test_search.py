from backend.app.database.database import SessionLocal

from backend.app.ai.skills.search.query import (
    extract_car_filters
)

from backend.app.ai.skills.search.skill import (
    search_cars
)


db = SessionLocal()


message = """
Find me a manual Suzuki under 30 lakh in BWP.
"""


filters = extract_car_filters(message)

print("\nGemini extracted filters:")
print(filters)


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


print(f"\nFound {len(cars)} cars\n")


for car in cars:
    print(
        f"ID: {car.id} | "
        f"{car.make} {car.model} | "
        f"Price: {car.price} | "
        f"City: {car.city} | "
        f"Transmission: {car.transmission}"
    )


db.close()