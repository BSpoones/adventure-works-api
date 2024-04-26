from pydantic import field_validator

from db.model.base.Table import Table
from datetime import datetime
from uuid import uuid4


class SalesCustomer(Table):
    """
    SalesCustomer table

    This table mirrors Sales_customer
    """

    CustomerID: int | None
    PersonID: int | None
    StoreID: int | None
    TerritoryID: int | None
    AccountNumber: str | None
    rowguid: str | None
    ModifiedDate: datetime | None

    @staticmethod
    def table_name() -> str:
        return "Sales_Customer"

    @staticmethod
    def primary_key_name() -> str:
        return "CustomerID"

    @classmethod
    def create(cls, **kwargs):
        optionals = {
            "CustomerID": cls.get_next_id(),
            "rowguid": str(uuid4()),
            "ModifiedDate": datetime.now()
        }

        clazz = cls(**(optionals | (kwargs or {})))

        clazz.insert()
        return clazz

    # Validators based on the AdventureWorks2019 schema

    @field_validator("AccountNumber")
    @classmethod
    def validate_account_number(cls, value):
        # cls.unique_validate("AccountNumber", value)
        cls.size_g_validate("AccountNumber", value, 10)
        return value

    def get_primary_key(self):
        return self.CustomerID

    def set_primary_key(self, key):
        self.CustomerID = key
