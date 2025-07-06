from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: int = Field(..., ge=0, description="Stock must be zero or more")
    category: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductUpdate(ProductCreate):
    pass

class ProductOut(ProductCreate):
    id: int

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: str

    class Config:
        from_attributes = True