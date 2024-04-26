from fastapi import APIRouter, HTTPException
from db.DatabaseHandler import DB
from db.model.SalesCustomer import SalesCustomer
from db.model.SalesOrderHeader import SalesOrderHeader

customer_router = APIRouter(prefix="/api/customer")

@customer_router.get(
    "/{customer_id}/purchasehistory/{limit}",
    response_model=list[SalesOrderHeader],
    summary="Retrieve the purchase history for a customer",
)
def get_customer_purchase_history(
        customer_id: int,
        limit: int | None = None
):
    data = DB.records("SELECT * FROM Sales_SalesOrderHeader WHERE CustomerID = %s LIMIT %s", customer_id, limit or 50)
    if not data:
        raise HTTPException(status_code=404, detail="No purchase history found for this customer.")
    return [SalesOrderHeader.create_update(**item) for item in data]


@customer_router.put(
    "/{customer_id}",
    response_model=SalesCustomer,
    summary="Edit customer details",
    description="Pass in a SalesCustomer JSON, any non-null fields will edit the original"
)
def put_customer_details(
        customer_id: int,
        customer: SalesCustomer
):
    # All validations are done when creating SalesCustomer from the input
    return customer.update(customer_id)


@customer_router.delete(
    "/{customer_id}",
    response_model=SalesCustomer,
    summary="Delete a customer from their CustomerID"
)
def delete_customer(
        customer_id: int
):
    data = SalesCustomer.get_from_id(customer_id)
    if not data:
        raise HTTPException(status_code=404, detail="Order not found.")
    data.delete()

    return data
