from fastapi import APIRouter

customer_router = APIRouter(prefix="/api/customer")


@customer_router.get("/")
def get_customer():
    ...


@customer_router.put("/address")
def put_address():
    ...


@customer_router.put("/password")
def put_password():
    ...


@customer_router.delete("/")
def delete_customer():
    ...
