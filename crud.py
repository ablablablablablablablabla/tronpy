from sqlalchemy.orm import Session
from models import WalletRequest
from sqlalchemy import desc

def create_wallet_request(db: Session, wallet_address: str, trx_balance: float, bandwidth: int, energy: int):
    """
    Создает запись в базе данных о запросе кошелька.
    :param db: Сессия базы данных.
    :param wallet_address: Адрес кошелька.
    :param trx_balance: Баланс TRX.
    :param bandwidth: Значение bandwidth.
    :param energy: Значение energy.
    :return: Созданная запись.
    """
    db_request = WalletRequest(
        wallet_address=wallet_address,
        trx_balance=trx_balance,
        bandwidth=bandwidth,
        energy=energy
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_wallet_requests(db: Session, limit: int, offset: int):
    """
    Получает список запросов с пагинацией.
    :param db: Сессия базы данных.
    :param limit: Количество записей на странице.
    :param offset: Смещение.
    :return: Список запросов.
    """
    return (
        db.query(WalletRequest)  # Запрашиваем все записи таблицы WalletRequest
        .order_by(desc(WalletRequest.requested_at))  # Сортируем по времени запроса (от новых к старым)
        .limit(limit)  # Ограничиваем количество записей
        .offset(offset)  # Устанавливаем смещение
        .all()  # Получаем все записи
    )