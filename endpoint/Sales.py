from fastapi import APIRouter

sales_router = APIRouter(prefix="/api/sales")


# Delete sales order
@sales_router.delete("/{id}")
def delete_sale():
    ...


# Submit bulk sales order
@sales_router.post("/order")
def post_bulk_order():
    ...  # TODO -> Bulk and one?
