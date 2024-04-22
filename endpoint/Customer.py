from fastapi import APIRouter

customer_router = APIRouter(prefix="/api/customer")


# Get customer purchase history
@customer_router.get("/{id}/purchasehistory")
def get_customer_purchase_history():
    ...


# Edit customer details
@customer_router.put("/{id}/edit")
def put_customer_details():
    ...
