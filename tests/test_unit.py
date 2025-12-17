import pytest
from sqlalchemy.orm import Session
from crud import create_wallet_request
from models import WalletRequest
from database import get_db, engine
from datetime import datetime


@pytest.fixture(scope="module")
def setup_database():

    from models import Base
    Base.metadata.create_all(bind=engine)
    yield

    Base.metadata.drop_all(bind=engine)


def test_create_wallet_request(setup_database):

    db: Session = next(get_db())

    wallet_address = "TTestAddress"
    trx_balance = 100.0
    bandwidth = 50
    energy_used = 30
    energy_limit = 50
    energy = f"{energy_used}/{energy_limit}" 


    created_request = create_wallet_request(
        db=db,
        wallet_address=wallet_address,
        trx_balance=trx_balance,
        bandwidth=bandwidth,
        energy=energy
    )

    assert created_request is not None
    assert created_request.wallet_address == wallet_address
    assert created_request.trx_balance == trx_balance
    assert created_request.bandwidth == bandwidth
    assert created_request.energy == energy 


    assert isinstance(created_request.requested_at, datetime)

    fetched_request = db.query(WalletRequest).filter_by(wallet_address=wallet_address).first()
    assert fetched_request is not None
    assert fetched_request.id == created_request.id

    energy_parts = fetched_request.energy.split("/")
    assert len(energy_parts) == 2  
    assert all(part.isdigit() for part in energy_parts)  
