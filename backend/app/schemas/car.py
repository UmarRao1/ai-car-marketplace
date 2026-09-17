from pydantic import BaseModel


class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: float
    mileage: int
    fuel_type: str
    fuel_average: float
    transmission: str
    city: str
    contact_number: str
    description: str | None = None

class CarUpdate(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    price: float | None = None
    mileage: int | None = None
    fuel_type: str | None = None
    fuel_average: float | None = None
    transmission: str | None = None
    city: str | None = None
    contact_number: str | None = None
    description: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "model": "CULTUS"
            }
        }
    }


class CarResponse(CarCreate):
    id: int
    seller_id: int

    class Config:
        from_attributes = True