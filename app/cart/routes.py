from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.cart import schemas
from app.products.models import Product
from app.cart.models import Cart as CartItem
from app.auth.dependencies import require_user
from typing import Union

from app.core.logger import logger

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=schemas.CartOut)
def add_to_cart(data: schemas.CartAdd, db: Session = Depends(get_db), user=Depends(require_user)):
    logger.info(f"Add to cart request by user {user.id} for product {data.product_id} (qty: {data.quantity})")
   
    # check if procduct is available
    product = db.query(Product).filter(Product.id == data.product_id).first()

    if not product:
        logger.warning(f"Product {data.product_id} not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        logger.warning(f"Insufficient stock for product {data.product_id} requested by user {user.id}")
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # check if a product is already in cart
    cart_item = db.query(CartItem).filter_by(user_id=user.id, product_id=data.product_id).first()
    if cart_item:
        cart_item.quantity += data.quantity
        logger.info(f"Updated cart quantity for product {data.product_id} (new qty: {cart_item.quantity})")
    else:
        cart_item = CartItem(user_id=user.id, product_id=data.product_id, quantity=data.quantity)
       
        db.add(cart_item)
        logger.info(f"Added product {data.product_id} to cart for user {user.id}")

    try:
        db.commit()
    except Exception as e:   
        db.rollback()
        logger.error(f"Database commit failed when adding to cart for user {user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database commit failed")

    db.refresh(cart_item)
    logger.info(f"Cart updated successfully for user {user.id}")
    return cart_item


@router.get("/", response_model=list[schemas.CartOut])
def view_cart(db: Session = Depends(get_db), user=Depends(require_user)):
    logger.info(f"User {user.id} requested to view cart")
    return db.query(CartItem).filter_by(user_id=user.id).all()


@router.put("/{product_id}", response_model=Union[schemas.CartOut, dict])
def update_cart_quantity(
    product_id: int,
    data: schemas.CartUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    # check if item is present in cart
    logger.info(f"User {user.id} is updating cart for product {product_id} to qty: {data.quantity}")
    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        logger.warning(f"Cart update failed: Item not found (User: {user.id}, Product: {product_id})")
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if data.quantity <= 0:
        db.delete(item)
        db.commit()
        logger.info(f"Item removed from cart due to zero quantity (User: {user.id}, Product: {product_id})")
        return {"detail": "Item removed from cart due to zero quantity"}

    # check product's stock
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.stock < data.quantity:
        logger.warning(f"Cart update failed: Insufficient stock (User: {user.id}, Product: {product_id})")
        raise HTTPException(status_code=400, detail="Insufficient stock")

    #update the qunatity
    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    logger.info(f"Cart quantity updated (User: {user.id}, Product: {product_id}, Qty: {data.quantity})")
    return item


@router.delete("/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user=Depends(require_user)):
    logger.info(f"User {user.id} requested to remove product {product_id} from cart")
    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        logger.warning(f"Remove from cart failed: Item not found (User: {user.id}, Product: {product_id})")
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(item)
    db.commit()
    logger.info(f"Product {product_id} removed from cart (User: {user.id})")
    return {"detail": "Item removed from cart"}