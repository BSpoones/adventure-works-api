from fastapi import FastAPI

from endpoint.Cart import cart_router
from endpoint.Customer import customer_router
from endpoint.Product import product_router

app = FastAPI()

routers = [
    cart_router,
    customer_router,
    product_router
]

for router in routers:
    app.include_router(router)


@app.get("/")
def test():
    return {"test": "worked!"}
