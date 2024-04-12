from fastapi import FastAPI

from endpoint.put.Address import router
app = FastAPI()

app.include_router(router)

@app.get("/")
def test():
    return {"test": "worked!"}