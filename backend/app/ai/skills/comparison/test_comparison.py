from backend.app.database.database import SessionLocal

from backend.app.ai.skills.comparison import (
    compare_cars_from_message
)


db = SessionLocal()


message = """
Compare car 2 and car 5.
"""


cars = compare_cars_from_message(
    db=db,
    user_message=message
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