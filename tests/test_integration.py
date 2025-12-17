import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, engine
from models import Base

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():

    Base.metadata.create_all(bind=engine)
    yield

    Base.metadata.drop_all(bind=engine)


def test_post_wallet_valid(setup_database):

    valid_address = "TVt7oQuLnHZz252eaDFLbh66zHDGgksoSY"
    response = client.post("/wallet/", json={"wallet_address": valid_address})


    assert response.status_code == 200


    data = response.json()
    assert "wallet_address" in data
    assert "trx_balance" in data
    assert "bandwidth" in data
    assert "energy" in data


    assert data["wallet_address"] == valid_address


    energy = data["energy"]
    assert isinstance(energy, str)
    energy_parts = energy.split("/")
    assert len(energy_parts) == 2  
    assert all(part.isdigit() for part in energy_parts)


def test_post_wallet_invalid():

    invalid_address = "TUzqjcFW8L1br3T5ttpUeTZBfsQGYdEGVав"
    response = client.post("/wallet/", json={"wallet_address": invalid_address})

    assert response.status_code == 400

    error_detail = response.json()["detail"]
    assert "Invalid TRON address format" in error_detail


