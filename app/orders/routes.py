from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import require_user
from app.orders import models, schemas
from app.core.logger import logger

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=list[schemas.OrderSummary])
def get_order_history(user=Depends(require_user), db: Session = Depends(get_db)):
    logger.info(f"User {user.id} requested order history")
    orders = db.query(models.Order).filter(models.Order.user_id == user.id).all()
    logger.info(f"Fetched {len(orders)} orders for user {user.id}")
    return orders

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order_by_id(order_id: int, user=Depends(require_user), db: Session = Depends(get_db)):
    logger.info(f"User {user.id} requested order ID {order_id}")
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id
    ).first()

    if not order:
        logger.warning(f"Order ID {order_id} not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Order not found")

    logger.info(f"Order ID {order_id} details returned for user {user.id}")
    return order
