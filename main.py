
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from services import get_wallet_info
from crud import create_wallet_request, get_wallet_requests
from database import get_db
from models import Base  # Импортируем Base для создания таблиц
from models import WalletRequest as DBWalletRequest  # Импортируем SQLAlchemy модель с псевдонимом
from sqlalchemy.orm import Session
from database import engine
from typing import Optional

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Переименуем Pydantic модель
class WalletRequestSchema(BaseModel):
    wallet_address: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Tron Wallet API!"}


@app.post("/wallet/")
def get_wallet_data(request: WalletRequestSchema):
    """
    Ендпоинт для получения данных о кошельке.
    При возникновении ошибки 401 выполняется повторная попытка.
    """
    db: Session = next(get_db())
    wallet_address = request.wallet_address

    # Проверка формата адреса
    if not wallet_address.startswith("T") or len(wallet_address) != 34:
        raise HTTPException(status_code=400, detail="Invalid TRON address format")

    retries = 10  # Максимальное количество попыток (включая первую)
    attempt = 0

    while attempt < retries:
        try:
            # Получаем данные о кошельке
            wallet_info = get_wallet_info(wallet_address)

            # Записываем запрос в базу данных
            create_wallet_request(
                db=db,
                wallet_address=wallet_address,
                trx_balance=wallet_info["trx_balance"],
                bandwidth=wallet_info["bandwidth"],
                energy=wallet_info["energy"]
            )

            # Возвращаем данные клиенту
            return {
                "wallet_address": wallet_address,
                "trx_balance": wallet_info["trx_balance"],
                "bandwidth": wallet_info["bandwidth"],
                "energy": wallet_info["energy"]
            }

        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

        except RuntimeError as re:
            # Проверяем, является ли ошибка 401
            if "401 Client Error" in str(re) and attempt < retries - 1:
                attempt += 1
                continue  # Повторяем попытку
            else:
                raise HTTPException(status_code=500, detail=str(re))


@app.get("/requests/")
def get_requests(
        page: int = Query(1, gt=0, description="Page number"),
        limit: int = Query(10, gt=0, le=100, description="Number of records per page")
):
    """
    Ендпоинт для получения списка последних запросов с пагинацией.
    """
    db: Session = next(get_db())
    try:
        # Вычисляем offset
        offset = (page - 1) * limit

        # Получаем общее количество записей
        total_count = db.query(DBWalletRequest).count()  # Используем импортированную модель

        # Получаем записи с учетом пагинации
        requests = get_wallet_requests(db, limit=limit, offset=offset)

        # Формируем результат
        return {
            "total": total_count,
            "page": page,
            "limit": limit,
            "data": [
                {
                    "id": req.id,
                    "wallet_address": req.wallet_address,
                    "trx_balance": req.trx_balance,
                    "bandwidth": req.bandwidth,
                    "energy": req.energy,
                    "requested_at": req.requested_at.isoformat()  # Преобразуем datetime в строку
                } for req in requests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/front", response_class=HTMLResponse)
def frontend():
    """
    Ендпоинт для отображения простого фронтенда.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tron Wallet Frontend</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .container {
                max-width: 600px;
                margin: auto;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                box-sizing: border-box;
            }
            button {
                padding: 10px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            .result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Tron Wallet Checker</h1>
            <input type="text" id="walletAddress" placeholder="Введите адрес кошелька">
            <button onclick="addWallet()">Добавить кошелёк</button>
            <button onclick="location.href='/requests/'">Список ключей</button>
            <div class="result" id="result"></div>
        </div>
        <script>
            async function addWallet() {
                const walletAddress = document.getElementById('walletAddress').value;
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = 'Загрузка...';
                try {
                    const response = await fetch('/wallet/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ wallet_address: walletAddress })
                    });
                    if (response.ok) {
                        const data = await response.json();
                        resultDiv.innerHTML = `
                            <p>Кошелёк добавлен:</p>
                            <p>Адрес: ${data.wallet_address}</p>
                            <p>Баланс TRX: ${data.trx_balance}</p>
                            <p>Bandwidth: ${data.bandwidth}</p>
                            <p>Energy: ${data.energy}</p>
                        `;
                    } else {
                        const errorData = await response.json();
                        resultDiv.innerHTML = `<p>Ошибка: ${errorData.detail || 'Кошелёк не найден'}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = '<p>Произошла ошибка при обработке запроса.</p>';
                }
            }
        </script>
    </body>
    </html>
    """
