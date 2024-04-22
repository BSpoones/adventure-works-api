from fastapi import APIRouter

product_router = APIRouter(prefix="/api/product")


# Get most popular products
@product_router.get("/popular")
def get_popular():
    ...


# Create new product line
@product_router.post("/product")
def post_product():
    ...


# Adjust stock in product inventory
@product_router.put("/{id}/stock}")
def put_stock():
    ...
