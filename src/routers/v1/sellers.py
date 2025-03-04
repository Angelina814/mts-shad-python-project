# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
#from src.schemas import IncomingBook, ReturnedAllbooks, ReturnedBook
from src.schemas.sellers import BaseSeller, ReturnedAllSellers, ReturnedSeller, NewSeller
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from sqlalchemy.orm import selectinload

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# @books_router.post("/books/", status_code=status.HTTP_201_CREATED)
@sellers_router.post(
    "/", response_model=NewSeller, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: BaseSeller,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession

    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "email": seller.email,
            "password": seller.password,
        }
    )

    session.add(new_seller)
    await session.flush()

    return new_seller



@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    query = select(Seller).options(selectinload(Seller.books))  # SELECT * FROM book
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}



@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    #if result := await session.get(Seller, seller_id):
    result = await session.execute(
        select(Seller).options(selectinload(Seller.books)).filter(Seller.id == seller_id)
    )
    seller = result.scalar_one_or_none()
    if seller is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    return seller



@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.email = new_seller_data.email
        updated_seller.password = updated_seller.password

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
