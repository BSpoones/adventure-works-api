from fastapi import APIRouter

product_router = APIRouter(prefix="/api/product")


@product_router.post("/review")
def post_review():
    ...
