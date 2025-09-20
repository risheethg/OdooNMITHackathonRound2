from typing import Literal
from .base_model import MongoBaseModel

class Product(MongoBaseModel):
    name: str
    type: Literal['Raw Material', 'End Product']