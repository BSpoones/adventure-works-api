from pydantic import field_validator
from db.model.base.Table import Table
from datetime import datetime
from uuid import uuid4


class ProductionProduct(Table):
    """
    ProductionProduct table

    This table mirrors Production_Product
    """

    ProductID: int | None
    Name: str | None
    ProductNumber: str | None
    MakeFlag: int | None
    FinishedGoodsFlag: int | None
    Color: str | None
    SafetyStockLevel: int | None
    ReorderPoint: int | None
    StandardCost: float | None
    ListPrice: float | None
    Size: str | None
    SizeUnitMeasureCode: str | None
    WeightUnitMeasureCode: str | None
    Weight: float | None
    DaysToManufacture: int | None
    ProductLine: str | None
    Class: str | None
    Style: str | None
    ProductSubcategoryID: int | None
    ProductModelID: int | None
    SellStartDate: datetime | None
    SellEndDate: datetime | None
    DiscontinuedDate: datetime | None
    rowguid: str | None
    ModifiedDate: datetime | None

    @staticmethod
    def table_name() -> str:
        return "Production_Product"

    @staticmethod
    def primary_key_name() -> str:
        return "ProductID"

    @classmethod
    def create(cls, **kwargs):
        optionals = {
            "ProductID": cls.get_next_id(),
            "rowguid": str(uuid4()),
            "ModifiedDate": datetime.now()
        }

        clazz = cls(**((kwargs or {}) | optionals))

        clazz.insert()
        return clazz

    # Validators based on the AdventureWorks2019 schema

    @field_validator("Name")
    @classmethod
    def validate_name(cls, value):
        cls.size_g_validate("Name", value, 100)

    @field_validator("ProductNumber")
    @classmethod
    def validate_product_number(cls, value):
        cls.size_g_validate("ProductNumber", value, 25)

    @field_validator("MakeFlag", "FinishedGoodsFlag")
    @classmethod
    def validate_flat(cls, value):
        cls.one_of_validate("Flag", value, (1, 0))

    @field_validator("Color")
    @classmethod
    def validate_color(cls, value):
        cls.size_g_validate("Color", value, 15)

    @field_validator("StandardCost", "ListPrice", "Weight")
    @classmethod
    def validate_cost(cls, value):
        cls.size_v_validate("Cost", value, 0)

    @field_validator("SizeUnitMeasureCode", "WeightUnitMeasureCode")
    @classmethod
    def validate_unit_measure_code(cls, value):
        cls.size_g_validate("Measure Code", value, 3)

    @field_validator("ProductLine")
    @classmethod
    def validate_product_line(cls, value):
        cls.size_g_validate("ProductLine", value, 2)
        cls.one_of_validate("ProductLine", value, ("R", "M", "T", "S"))

    @field_validator("Class")
    @classmethod
    def validate_class_line(cls, value):
        cls.size_g_validate("Class", value, 2)
        cls.one_of_validate("Class", value, ("H", "M", "L"))

    @field_validator("Style")
    @classmethod
    def validate_style_line(cls, value):
        cls.size_g_validate("Style", value, 2)
        cls.one_of_validate("Style", value, ("W", "M", "U"))

    def get_primary_key(self):
        return self.ProductID

    def set_primary_key(self, key):
        self.ProductID = key
