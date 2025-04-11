import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, engine
from models import Base

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    # Создаем таблицы в тестовой базе данных
    Base.metadata.create_all(bind=engine)
    yield
    # Удаляем таблицы после тестов
    Base.metadata.drop_all(bind=engine)


def test_post_wallet_valid(setup_database):
    """
    Интеграционный тест для POST /wallet/.
    Проверяет, что валидный запрос возвращает корректные данные.
    """
    valid_address = "TVt7oQuLnHZz252eaDFLbh66zHDGgksoSY"
    response = client.post("/wallet/", json={"wallet_address": valid_address})

    # Проверяем статус-код
    assert response.status_code == 200

    # Проверяем структуру ответа
    data = response.json()
    assert "wallet_address" in data
    assert "trx_balance" in data
    assert "bandwidth" in data
    assert "energy" in data

    # Проверяем, что адрес совпадает с отправленным
    assert data["wallet_address"] == valid_address

    # Проверяем формат energy (использовано/лимит)
    energy = data["energy"]
    assert isinstance(energy, str)
    energy_parts = energy.split("/")
    assert len(energy_parts) == 2  # Должно быть два числа разделенные "/"
    assert all(part.isdigit() for part in energy_parts)  # Оба значения должны быть числами


def test_post_wallet_invalid():
    """
    Интеграционный тест для POST /wallet/.
    Проверяет, что невалидный запрос возвращает ошибку 400.
    """
    invalid_address = "TUzqjcFW8L1br3T5ttpUeTZBfsQGYdEGVав"
    response = client.post("/wallet/", json={"wallet_address": invalid_address})

    # Проверяем статус-код
    assert response.status_code == 400

    # Проверяем сообщение об ошибке
    error_detail = response.json()["detail"]
    assert "Invalid TRON address format" in error_detail


