from fastapi.exceptions import ValidationException
from pydantic import BaseModel
from dataclasses import fields
from abc import ABC, abstractmethod


class Table(BaseModel, ABC):
    """
    Parent class for all Pydantic models in the API
    """

    @classmethod
    def get_cols(cls, other_cols=None) -> list[str]:
        """
        Gets a list of table columns / gets all the
        given cols in a table

        Args:
            other_cols (iterable, optional): List of column names (str). Defaults to None.

        Returns:
            set: Set of (valid) columns
        """
        field_set = {field.name for field in fields(cls)}
        if not other_cols:
            return field_set

        other_cols = set(other_cols)
        # Check for invalid col names
        if len(other_cols - field_set) != 0:
            raise ValueError(f"Invalid column(s) given: {other_cols - field_set}")

        return field_set.intersection(other_cols)

    @staticmethod
    def table_name() -> str:
        """
        Static property to retrieve the table name of a class
        NOTE: A @property decorator has not been added due to python's
              incompatibility with static properties
        """
        raise NotImplementedError("Subclass must implement table_name")

    @staticmethod
    def primary_key_name() -> str:
        """
        Static property to retrieve the primary key name of a class
        NOTE: A @property decorator has not been added due to python's
              incompatibility with static properties
        """
        raise NotImplementedError("Subclass must implement primary_key_name")

    @abstractmethod
    def get_primary_key(self):
        """
        Abstract property to retrieve the primary key value of a class
        NOTE: A @property decorator has not been added due to python's
              incompatibility with abstract properties
        """
        raise NotImplementedError("Subclass must implement get_primary_key")

    @classmethod
    @abstractmethod
    def create(cls, **kwargs):
        """
        Method to create an instance of a model and insert into the database
        :param kwargs: Table arguments
        """
        raise NotImplementedError("Subclass must implement create")

    @classmethod
    def create_update(cls, **kwargs):
        """
        Method to create an instance of a model
        :param kwargs: Table arguments
        """
        return cls(**kwargs)

    def insert(self, with_commit=True):
        """
        Method to insert the table into the database

        :param with_commit: Should the database commit when this function is run?
        """
        from db.DatabaseHandler import DB  # Preventing circular imports
        return DB.insert(self, with_commit)

    def delete(self, with_commit=True):
        """
        Method to delete the table from the database

        :param with_commit: Should the database commit when this function is run?
        """
        from db.DatabaseHandler import DB
        DB.delete(self, with_commit)

    def update(self, primary_key_value: str | int, with_commit=True):
        """
        Method to update the table contents in the database

        :param with_commit: Should the database commit when this function is run?
        """
        from db.DatabaseHandler import DB
        return DB.update(self, primary_key_value, with_commit)

    @classmethod
    def size_g_validate(cls, field_name: str, value: any, max_size: int) -> None:
        """
        Validating a field to be less than the max size
        """
        if value is not None and len(value) > max_size:
            raise ValidationException(f"{field_name} must be less than {max_size} characters.")

    @classmethod
    def size_l_validate(cls, field_name, value, min_size):
        """
        Validating a field to be greater than the max size
        """
        if value is not None and len(value) < min_size:
            raise ValidationException(f"{field_name} must be greater than {min_size} characters.")

    @classmethod
    def size_v_validate(cls, field_name, value, min_size):
        """
        Validating a field to be greater than the max size
        """
        if value is not None and value < min_size:
            raise ValidationException(f"{field_name} must be greater than {min_size}.")


    @classmethod
    def unique_validate(cls, field_name, value):
        """
        Validating a field to be unique
        """
        from db.DatabaseHandler import DB
        if DB.is_in_db(cls, field_name, value):
            raise ValidationException(f"{field_name} must be unique")

    @classmethod
    def one_of_validate(cls, field_name, value, items: tuple):
        """
        Validating a field to be in a given tuple of items
        """
        if value is not None and value not in items:
            raise ValidationException(f"{field_name} must be one of {', '.join(map(str, items))}")

    @classmethod
    def get_from_id(cls, primary_key_value: int):
        """
        Retrieves a table from the database with a given primary key ID
        """
        from db.DatabaseHandler import DB
        record = DB.record(f"SELECT * FROM {cls.table_name()} WHERE {cls.primary_key_name()} = %s", primary_key_value)
        if record is not None:
            return cls(**record)
        else:
            return None

    @classmethod
    def get_next_id(cls) -> int:
        """
        Returns the table's next primary key ID

        This is used as the AdventureWorks2019 database has no AUTO_INCREMENT :(
        """
        from db.DatabaseHandler import DB
        return DB.get_next_id(cls)
