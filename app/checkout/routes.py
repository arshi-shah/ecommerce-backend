import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.auth.dependencies import get_db, require_user
from app.orders import models as order_models
from app.cart import models as cart_models
from app.products.models import Product
from enum import Enum

router = APIRouter(prefix="/checkout", tags=["checkout"])
logger = logging.getLogger(__name__)

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


@router.post("", status_code=status.HTTP_201_CREATED)
def checkout(db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        cart_items = db.query(cart_models.Carts).filter_by(user_id=current_user.id).all()
        if not cart_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        total_amount = 0
        order_items = []

        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product ID {item.product_id} not found"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for Product ID {item.product_id}"
                )

            product.stock -= item.quantity
            total_amount += product.price * item.quantity

            order_item = order_models.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
            order_items.append(order_item)

        order = order_models.Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.paid.value,
            created_at=datetime.utcnow(),
            items=order_items
        )

        db.add(order)

        for item in cart_items:
            db.delete(item)

        db.commit()
        db.refresh(order)

        logger.info(f"User {current_user.id} completed checkout for order {order.id} with total {total_amount}")

        return {
            "message": "Checkout successful",
            "order_id": order.id,
            "total_amount": total_amount,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase
                }
                for item in order.items
            ],
            "status": order.status
        }

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError as db_err:
        db.rollback()
        logger.exception("Database error during checkout")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        logger.exception("Unexpected error during checkout")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")