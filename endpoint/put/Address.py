from fastapi import APIRouter

router = APIRouter()


@router.get("/put")
def put_address():
    return {"address": "Working"}
