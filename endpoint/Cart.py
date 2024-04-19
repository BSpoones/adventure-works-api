from fastapi import APIRouter

cart_router = APIRouter(prefix="/api/cart")


@cart_router.get("/")
def get_cart():
    ...


@cart_router.delete("/item")
def delete_cart_item():
    ...


@cart_router.put("/item")
def post_cart_item():
    ...
