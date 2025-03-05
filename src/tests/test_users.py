import pytest
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book
from fastapi import status
from icecream import ic


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivanov@mail.ru",
        "password": "123Ivan",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivanov@mail.ru"
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = Seller(first_name="Maria", last_name = "Ivanova", email = "ivanova@mail.ru", password = "123Maria")
    seller_2 = Seller(first_name="Irina", last_name = "Petrova", email = "petrova@mail.ru", password = "123Irina")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "id": seller.id,
                "first_name": "Maria",
                "last_name": "Ivanova",
                "email": "ivanova@mail.ru",
                "books": []
            },
            {
                "id": seller_2.id,
                "first_name": "Irina",
                "last_name": "Petrova",
                "email": "petrova@mail.ru",
                "books": []
            },
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):

    seller = Seller(first_name="Maria", last_name = "Ivanova", email = "ivanova@mail.ru", password = "123Maria")
    seller_2 = Seller(first_name="Irina", last_name = "Petrova", email = "petrova@mail.ru", password = "123Irina")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": seller.id,
        "first_name": "Maria",
        "last_name": "Ivanova",
        "email": "ivanova@mail.ru",
        "books": []
    }


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="Maria", last_name = "Ivanova", email = "ivanova_maria@mail.ru", password = "123Maria")


    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "id": seller.id,
            "first_name": "Maria",
            "last_name": "Ivanova",
            "email": "ivanova_maria@mail.ru",
            "books":[]
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Maria"
    assert res.last_name == "Ivanova"
    assert res.email == "ivanova_maria@mail.ru"
    assert res.password == "123Maria"
    assert res.id == seller.id

# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Maria", last_name = "Ivanova", email = "ivanova_maria@mail.ru", password = "123Maria")
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, seller_id = seller.id, pages=104)
    db_session.add(book)
    await db_session.flush()

    ic(seller.id)

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0

    # Проверка что книги удаленного продавца не существуют (то есть тоже удалились)
    all_books = await db_session.execute(select(Book).where(Book.seller_id == seller.id))
    res_books = all_books.scalars().all()
    assert len(res_books) == 0


# Тест на ручку удаления продавца с несуществующим id
@pytest.mark.asyncio
async def test_delete_seller_with_invalid_id(db_session, async_client):
    seller = Seller(first_name="Maria", last_name = "Ivanova", email = "ivanova_maria@mail.ru", password = "123Maria")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
