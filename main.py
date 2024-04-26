import uvicorn
from pydantic import ValidationError

from endpoint.Customer import customer_router
from endpoint.Order import order_router
from endpoint.Product import product_router
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(debug=True)


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """
    Error handler to handle ValidationErrors correctly
    """

    return JSONResponse(
        status_code=422,
        content={
            "validation_error": repr(exc),
        },
    )

routers = [
    customer_router,
    order_router,
    product_router,
]

for router in routers:
    app.include_router(router)

@app.get("/")
def test():
    return {"data": "Adventure-Works API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=3002, reload=True)

