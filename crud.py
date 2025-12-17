from sqlalchemy.orm import Session
from models import WalletRequest
from sqlalchemy import desc

def create_wallet_request(db: Session, wallet_address: str, trx_balance: float, bandwidth: int, energy: int):

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

    return (
        db.query(WalletRequest)
        .order_by(desc(WalletRequest.requested_at)) 
        .limit(limit)
        .offset(offset)
        .all()
    )
