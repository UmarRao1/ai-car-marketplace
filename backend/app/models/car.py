from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.app.database.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)

    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    mileage = Column(Integer, nullable=False)

    fuel_type = Column(String, nullable=False)
    fuel_average = Column(Float, nullable=False)
    transmission = Column(String, nullable=False)

    city = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)

    description = Column(String, nullable=True)

    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)