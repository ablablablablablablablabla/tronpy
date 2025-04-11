from tronpy import Tron
from tronpy.exceptions import AddressNotFound


def get_wallet_info(wallet_address: str):
    """
    Получает информацию о кошельке TRON.
    :param wallet_address: Адрес кошелька.
    :return: Словарь с данными о кошельке.
    """
    client = Tron(network='mainnet')

    # Проверяем валидность адреса
    if not client.is_address(wallet_address):
        raise ValueError("Invalid wallet address")

    try:
        # Получаем информацию об аккаунте
        account = client.get_account(wallet_address)

        # Получаем баланс TRX
        trx_balance = account.get('balance', 0) / 1_000_000

        # Получаем данные об энергии
        account_resource = client.get_account_resource(wallet_address)
        energy_limit = account_resource.get('EnergyLimit', 0)

        # Проверяем наличие ключа 'EnergyUsed'
        energy_used = account_resource.get('EnergyUsed',
                                           energy_limit)  # Используем EnergyLimit, если EnergyUsed отсутствует

        energy = f"{energy_used}/{energy_limit}"  # Форматируем как "использовано/лимит"

        # Получаем доступный Bandwidth
        bandwidth = client.get_bandwidth(wallet_address)

        return {
            "trx_balance": trx_balance,
            "bandwidth": bandwidth,
            "energy": energy
        }
    except AddressNotFound:
        raise ValueError("Wallet address not found")
    except KeyError as ke:
        raise RuntimeError(f"Missing key in API response: {str(ke)}")
    except Exception as e:
        raise RuntimeError(f"Error fetching wallet data: {str(e)}")