from pydantic import BaseModel
from pydantic_core import PydanticCustomError
from .books import ReturnedBook
#__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllbooks"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
    password : str

# Класс, валидирующий исходящие данные. Он уже содержит id
class NewSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

# Класс для возврата одного продавца
class ReturnedSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    books: list[ReturnedBook] = [] #??? list[BaseBook] = []


# Класс для возврата массива объектов "Продавцы"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]