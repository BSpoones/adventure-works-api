from fastapi import APIRouter, HTTPException

from db.DatabaseHandler import DB
from db.model.ProductionProduct import ProductionProduct
from fastapi.responses import JSONResponse

product_router = APIRouter(prefix="/api/product")


@product_router.get(
    "/popular",
    response_model=dict,
    summary="Get the most popular products by their sales",
    description="This will output the product name, number, and the amount sold (Also evidence of providing a "
                "response that isn't a BaseModel"
)
def get_popular():
    statement = f"SELECT p.Name, p.ProductNumber, COUNT(s.ProductId) as sales FROM {ProductionProduct.table_name()} p LEFT JOIN Sales_SalesOrderDetail s ON p.ProductId = s.ProductID GROUP BY p.ProductID ORDER BY COUNT(s.ProductId) DESC"
    data = DB.records(statement)
    return JSONResponse(
        status_code=200,
        content={
            "data": data
        },
    )


@product_router.post(
    "/",
    response_model=ProductionProduct,
    summary="Add a new product to the database"
)
def post_product(
        product: ProductionProduct
):
    # All validations are done at a table level
    return ProductionProduct.create(**product.dict())


@product_router.put(
    "/{product_id}/safety_stock}",
    response_model=ProductionProduct,
    summary="Adjust the safety stock of a product",
    description="This is evidence of editing a single variable, instead of an entire BaseModel"
)
def put_stock(
        product_id: int,
        safety_stock: int
):
    product = ProductionProduct.get_from_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    setattr(product, "SafetyStockLevel", safety_stock)
    return product.update(product_id, product)
