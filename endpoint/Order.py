from fastapi import APIRouter, HTTPException
from fastapi.exceptions import ValidationException
from db.model.SalesOrderHeader import SalesOrderHeader

order_router = APIRouter(prefix="/api/order")

@order_router.delete(
    "/{order_id}",
    response_model=SalesOrderHeader,
    summary="Delete an order by its OrderID"
)
def delete_order(
        order_id: int
):
    data = SalesOrderHeader.get_from_id(order_id)
    if not data:
        raise HTTPException(status_code=404, detail="Order not found.")
    data.delete()

    return data


# Submit bulk sales order
@order_router.post(
    "/bulk",
    response_model=list[SalesOrderHeader],
    summary="Add one or many orders to the database"
)
def post_bulk_order(
        orders: list[SalesOrderHeader]
):
    if not orders:
        raise ValidationException("Please add at least one order")

    data = []

    for order in orders:
        # All validations for orders are done at the tabel level
        table = SalesOrderHeader.create(**order.dict())
        data.append(table)

    return data
