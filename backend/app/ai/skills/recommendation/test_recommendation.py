from backend.app.database.database import SessionLocal

from backend.app.ai.skills.recommendation import (
    recommend_cars_from_message
)


db = SessionLocal()


message = """
I want a manual Suzuki under 30 lakh in BWP.
"""


cars = recommend_cars_from_message(
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