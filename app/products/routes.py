import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.products import models, schemas
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    logger.info(f"[admin] Product created with ID: {new_product.id}")
    print("REQUEST RECEIVED:", product.dict())
    return new_product

@router.get("/", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Product).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    logger.info("[admin] Listing all products")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updated: schemas.ProductUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    logger.info(f"[admin] Fetching product with ID: {product_id}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        logger.warning(f"[admin] Product not found with ID: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in updated.dict().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    logger.info(f"[admin] Product updated: ID {product.id}")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    logger.info(f"[admin] Deleting product ID: {product_id}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        logger.warning(f"[admin] Delete failed, product not found: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    logger.info(f"[admin] Product deleted: ID {product_id}")
    return None