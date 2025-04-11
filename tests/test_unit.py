import pytest
from sqlalchemy.orm import Session
from crud import create_wallet_request
from models import WalletRequest
from database import get_db, engine
from datetime import datetime


@pytest.fixture(scope="module")
def setup_database():
    # Создаем таблицы в тестовой базе данных
    from models import Base
    Base.metadata.create_all(bind=engine)
    yield
    # Удаляем таблицы после тестов
    Base.metadata.drop_all(bind=engine)


def test_create_wallet_request(setup_database):
    """
    Юнит-тест для функции create_wallet_request.
    Проверяет, что запись корректно создается в базе данных.
    """
    db: Session = next(get_db())

    # Данные для тестирования
    wallet_address = "TTestAddress"
    trx_balance = 100.0
    bandwidth = 50
    energy_used = 30
    energy_limit = 50
    energy = f"{energy_used}/{energy_limit}"  # Форматируем energy как "использовано/лимит"

    # Создаем запись
    created_request = create_wallet_request(
        db=db,
        wallet_address=wallet_address,
        trx_balance=trx_balance,
        bandwidth=bandwidth,
        energy=energy
    )

    # Проверяем, что запись создана
    assert created_request is not None
    assert created_request.wallet_address == wallet_address
    assert created_request.trx_balance == trx_balance
    assert created_request.bandwidth == bandwidth
    assert created_request.energy == energy  # Проверяем формат energy

    # Проверяем, что время создания установлено
    assert isinstance(created_request.requested_at, datetime)

    # Проверяем, что запись добавлена в базу данных
    fetched_request = db.query(WalletRequest).filter_by(wallet_address=wallet_address).first()
    assert fetched_request is not None
    assert fetched_request.id == created_request.id

    # Дополнительная проверка формата energy
    energy_parts = fetched_request.energy.split("/")
    assert len(energy_parts) == 2  # Должно быть два числа разделенные "/"
    assert all(part.isdigit() for part in energy_parts)  # Оба значения должны быть числами