from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WalletRequest(Base):
    __tablename__ = "wallet_requests"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, nullable=False)
    trx_balance = Column(Float, nullable=True)
    bandwidth = Column(Integer, nullable=True)
    energy = Column(String, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)