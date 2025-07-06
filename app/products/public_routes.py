from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from app.auth.dependencies import get_db
from app.products.models import Product
from app.products.schemas import ProductOut
from typing import List, Optional

public_router = APIRouter(prefix="/products", tags=["Public Products"])

@public_router.get("/", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(default="name", pattern="^(name|price|stock)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if sort_by == "price":
        query = query.order_by(Product.price)
    elif sort_by == "stock":
        query = query.order_by(Product.stock)
    else:
        query = query.order_by(Product.name)

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

@public_router.get("/{product_id}", response_model=ProductOut)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@public_router.get("/search", response_model=List[ProductOut])
def search_products(
    keyword: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    results = db.query(Product).filter(
        (Product.name.ilike(f"%{keyword}%")) |
        (Product.description.ilike(f"%{keyword}%")) |
        (Product.category.ilike(f"%{keyword}%"))
    ).all()
    return results