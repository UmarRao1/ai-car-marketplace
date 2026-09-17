import os
import shutil
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.car import Car
from backend.app.models.car_image import CarImage
from backend.app.schemas.car import (
    CarCreate,
    CarUpdate,
    CarResponse
)


router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)


BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# IMAGE HELPERS
# ============================================================

def image_to_dict(image: CarImage):
    return {
        "id": image.id,
        "car_id": image.car_id,
        "image_url": (
            f"{BASE_URL}/"
            + image.image_path.replace("\\", "/")
        )
    }


def serialize_car(car: Car, db: Session):
    """
    Return a complete car listing including:
    - seller name
    - images
    """

    images = (
        db.query(CarImage)
        .filter(
            CarImage.car_id == car.id
        )
        .order_by(
            CarImage.id.asc()
        )
        .all()
    )

    seller = (
        db.query(User)
        .filter(
            User.id == car.seller_id
        )
        .first()
    )

    return {
        "id": car.id,
        "make": car.make,
        "model": car.model,
        "year": car.year,
        "price": car.price,
        "mileage": car.mileage,
        "fuel_type": car.fuel_type,
        "fuel_average": car.fuel_average,
        "transmission": car.transmission,
        "city": car.city,
        "contact_number": car.contact_number,
        "description": car.description,
        "seller_id": car.seller_id,
        "seller_name": (
            seller.name
            if seller
            else "Unknown Seller"
        ),
        "images": [
            image_to_dict(image)
            for image in images
        ]
    }


# ============================================================
# CREATE CAR
# ============================================================

@router.post(
    "/",
    response_model=CarResponse
)
def create_car(
    car: CarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_car = Car(
        make=car.make,
        model=car.model,
        year=car.year,
        price=car.price,
        mileage=car.mileage,
        fuel_type=car.fuel_type,
        fuel_average=car.fuel_average,
        transmission=car.transmission,
        city=car.city,
        contact_number=car.contact_number,
        description=car.description,
        seller_id=current_user.id
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car


# ============================================================
# GET ALL CARS + SEARCH + FILTERS + SORTING + PAGINATION
# ============================================================

@router.get(
    "/",
    response_model=list[CarResponse]
)
def get_cars(
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

    sort_by: str = "id",
    order: str = "asc",

    page: int = 1,
    limit: int = 10,

    db: Session = Depends(get_db)
):

    query = db.query(Car)

    # --------------------------------------------------------
    # SEARCH MAKE OR MODEL
    # --------------------------------------------------------

    if search:
        search_text = f"%{search.strip()}%"

        query = query.filter(
            (Car.make.ilike(search_text))
            |
            (Car.model.ilike(search_text))
        )

    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    if city:
        city_text = f"%{city.strip()}%"

        query = query.filter(
            Car.city.ilike(city_text)
        )

    # --------------------------------------------------------
    # FUEL
    # --------------------------------------------------------

    if fuel_type:
        query = query.filter(
            Car.fuel_type.ilike(
                fuel_type.strip()
            )
        )

    # --------------------------------------------------------
    # TRANSMISSION
    # --------------------------------------------------------

    if transmission:
        query = query.filter(
            Car.transmission.ilike(
                transmission.strip()
            )
        )

    # --------------------------------------------------------
    # PRICE RANGE
    # --------------------------------------------------------

    if min_price is not None:
        query = query.filter(
            Car.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Car.price <= max_price
        )

    # --------------------------------------------------------
    # YEAR RANGE
    # --------------------------------------------------------

    if min_year is not None:
        query = query.filter(
            Car.year >= min_year
        )

    if max_year is not None:
        query = query.filter(
            Car.year <= max_year
        )

    # --------------------------------------------------------
    # MILEAGE RANGE
    # --------------------------------------------------------

    if min_mileage is not None:
        query = query.filter(
            Car.mileage >= min_mileage
        )

    if max_mileage is not None:
        query = query.filter(
            Car.mileage <= max_mileage
        )

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    allowed_sort_fields = {
        "price": Car.price,
        "year": Car.year,
        "mileage": Car.mileage,
        "id": Car.id
    }

    sort_column = allowed_sort_fields.get(
        sort_by,
        Car.id
    )

    if order.lower() == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    if limit > 100:
        limit = 100

    offset = (page - 1) * limit

    cars = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return cars


# ============================================================
# MY LISTINGS
# IMPORTANT: THIS MUST COME BEFORE /{car_id}
# ============================================================

@router.get(
    "/my-listings",
    response_model=list[CarResponse]
)
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cars = (
        db.query(Car)
        .filter(
            Car.seller_id == current_user.id
        )
        .order_by(
            Car.id.desc()
        )
        .all()
    )

    return cars


# ============================================================
# GET SINGLE CAR
# COMPLETE LISTING
# ============================================================

@router.get("/{car_id}")
def get_car(
    car_id: int,
    db: Session = Depends(get_db)
):

    car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    return serialize_car(
        car,
        db
    )


# ============================================================
# FULL UPDATE CAR
# ============================================================

@router.put(
    "/{car_id}",
    response_model=CarResponse
)
def update_car(
    car_id: int,
    car: CarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if existing_car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if existing_car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own cars"
        )

    existing_car.make = car.make
    existing_car.model = car.model
    existing_car.year = car.year
    existing_car.price = car.price
    existing_car.mileage = car.mileage
    existing_car.fuel_type = car.fuel_type
    existing_car.fuel_average = car.fuel_average
    existing_car.transmission = car.transmission
    existing_car.city = car.city
    existing_car.contact_number = car.contact_number
    existing_car.description = car.description

    db.commit()
    db.refresh(existing_car)

    return existing_car


# ============================================================
# DELETE CAR
# ALSO DELETE ITS IMAGES
# ============================================================

@router.delete("/{car_id}")
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if existing_car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if existing_car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own cars"
        )

    # Remove all image records and files
    images = (
        db.query(CarImage)
        .filter(
            CarImage.car_id == car_id
        )
        .all()
    )

    for image in images:

        if os.path.exists(
            image.image_path
        ):
            os.remove(
                image.image_path
            )

        db.delete(image)

    db.delete(existing_car)
    db.commit()

    return {
        "message": "Car deleted successfully"
    }


# ============================================================
# PATCH CAR
# PARTIAL UPDATE
# ============================================================

@router.patch(
    "/{car_id}",
    response_model=CarResponse
)
def patch_car(
    car_id: int,
    car: CarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if existing_car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if existing_car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own cars"
        )

    update_data = car.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            existing_car,
            field,
            value
        )

    db.commit()
    db.refresh(existing_car)

    return existing_car


# ============================================================
# UPLOAD CAR IMAGE
# ============================================================

@router.post("/{car_id}/images")
def upload_car_image(
    car_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only upload images for your own cars"
        )

    # Only images allowed
    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    upload_folder = "uploads/cars"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # Keep original extension
    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if not extension:
        extension = ".jpg"

    # Unique filename
    unique_name = (
        f"{car_id}_{uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        unique_name
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    new_image = CarImage(
        car_id=car_id,
        image_path=file_path
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {
        "message": "Image uploaded successfully",
        "image_id": new_image.id,
        "car_id": car_id,
        "image_path": file_path,
        "image_url": (
            f"{BASE_URL}/"
            + file_path.replace("\\", "/")
        )
    }


# ============================================================
# GET CAR IMAGES
# ============================================================

@router.get("/{car_id}/images")
def get_car_images(
    car_id: int,
    db: Session = Depends(get_db)
):

    car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    images = (
        db.query(CarImage)
        .filter(
            CarImage.car_id == car_id
        )
        .order_by(
            CarImage.id.asc()
        )
        .all()
    )

    return [
        image_to_dict(image)
        for image in images
    ]


# ============================================================
# DELETE CAR IMAGE
# ============================================================

@router.delete(
    "/images/{car_id}/{image_id}"
)
def delete_car_image(
    car_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    image = (
        db.query(CarImage)
        .filter(
            CarImage.id == image_id,
            CarImage.car_id == car_id
        )
        .first()
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found for this car"
        )

    car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete images of your own cars"
        )

    if os.path.exists(
        image.image_path
    ):
        os.remove(
            image.image_path
        )

    db.delete(image)
    db.commit()

    return {
        "message": "Image deleted successfully",
        "car_id": car_id,
        "image_id": image_id
    }


# ============================================================
# REPLACE CAR IMAGE
# ============================================================

@router.patch(
    "/images/{car_id}/{image_id}"
)
def replace_car_image(
    car_id: int,
    image_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    image = (
        db.query(CarImage)
        .filter(
            CarImage.id == image_id,
            CarImage.car_id == car_id
        )
        .first()
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found for this car"
        )

    car = (
        db.query(Car)
        .filter(
            Car.id == car_id
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    if car.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only replace images of your own cars"
        )

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    # Remove old file
    if os.path.exists(
        image.image_path
    ):
        os.remove(
            image.image_path
        )

    upload_folder = "uploads/cars"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if not extension:
        extension = ".jpg"

    unique_name = (
        f"{car_id}_{uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        unique_name
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    image.image_path = file_path

    db.commit()
    db.refresh(image)

    return {
        "message": "Image replaced successfully",
        "image_id": image.id,
        "car_id": car_id,
        "image_path": file_path,
        "image_url": (
            f"{BASE_URL}/"
            + file_path.replace("\\", "/")
        )
    }