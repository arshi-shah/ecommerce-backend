from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.products.routes import router as admin_products_router
from app.products.public_routes import public_router as public_products_router
from app.cart.routes import router as cart_router
from app.checkout.routes import router as checkout_router
from app.orders.routes import router as order_router  # Assuming you have an order router

app = FastAPI()
app.include_router(auth_router)
app.include_router(admin_products_router)  
app.include_router(public_products_router)
app.include_router(cart_router) 
app.include_router(checkout_router)
app.include_router(order_router)  # Assuming you have an order router

@app.get("/")
async def root():
    return {"message": "Hello World"}