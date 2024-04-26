from pydantic import validators, field_validator
from dataclasses import dataclass, field, fields

from db.model.base.Table import Table
from datetime import datetime
from uuid import uuid4


class SalesOrderHeader(Table):
    """
    SalesOrderHeader table

    This table mirrors Sales_SalesOrderHeader
    """

    SalesOrderID: int | None
    RevisionNumber: int | None
    OrderDate: datetime | None
    DueDate: datetime | None
    ShipDate: datetime | None
    Status: int | None
    OnlineOrderFlag: int | None
    SalesOrderNumber: str | None
    PurchaseOrderNumber: str | None
    AccountNumber: str | None
    CustomerID: int | None
    SalesPersonID: int | None
    TerritoryID: int | None
    BillToAddressID: int | None
    ShipToAddressID: int | None
    ShipMethodID: int | None
    CreditCardID: int | None
    CreditCardApprovalCode: str | None
    CurrencyRateID: int | None
    SubTotal: float | None
    TaxAmt: float | None
    Freight: float | None
    TotalDue: float | None
    Comment: str | None
    rowguid: str | None
    ModifiedDate: datetime | None

    @staticmethod
    def table_name() -> str:
        return "Sales_SalesOrderHeader"

    @staticmethod
    def primary_key_name() -> str:
        return "SalesOrderID"

    @classmethod
    def create(
            cls,
            **kwargs
    ):
        optionals = {
            "SalesOrderID": cls.get_next_id(),
            "OrderDate": datetime.now(),
            "rowguid": str(uuid4()),
            "ModifiedDate": datetime.now()
        }

        clazz = cls(**(optionals | (kwargs or {})))

        clazz.insert()
        return clazz

    # Validators based on the AdventureWorks2019 schema

    @field_validator('Status', mode='before')
    @classmethod
    def validate_status(cls, value) -> str:
        cls.one_of_validate("Status", value, (1, 2, 3, 4, 5, 6))
        return value

    @field_validator("OnlineOrderFlag")
    @classmethod
    def validate_flag(cls, value):
        cls.one_of_validate("OnlineOrderFlag", value, (0, 1))

    @field_validator("SalesOrderNumber")
    @classmethod
    def validate_sales_order_number(cls, value):
        cls.size_g_validate("SalesOrderNumber", value, 25)

    @field_validator("PurchaseOrderNumber")
    @classmethod
    def validate_purchase_order_number(cls, value):
        cls.size_g_validate("PurchaseOrderNumber", value, 50)

    @field_validator("SubTotal", "TaxAmt", "Freight", "TotalDue")
    @classmethod
    def validate_prices(cls, value):
        cls.size_v_validate("Price", value, 0)

    def get_primary_key(self):
        return self.SalesOrderID

    def set_primary_key(self, key):
        self.SalesOrderID = key
