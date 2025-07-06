from pydantic import BaseModel
from typing import Optional

class CartAdd(BaseModel):
    product_id: int
    quantity: int

class CartOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attribute = True


class CartUpdate(BaseModel):
    quantity: int

    class Config:
        from_attribute = True