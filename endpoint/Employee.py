from fastapi import APIRouter

employee_router = APIRouter(prefix="/api/employee")


# Delete employee
@employee_router.delete("/{id}")
def delete_employee():
    ...
