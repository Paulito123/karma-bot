from sqlalchemy import Column, DateTime, Integer, String, func, BigInteger, Text, update, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr, Union, Dict, Tuple
from connect import engine, session
from datetime import datetime
from config import Config

Base = declarative_base()

class OnboardLog(Base):
    __tablename__ = "onboardlog"

    id = Column(Integer, primary_key=True)
    # Link to Discord account
    discord_id = Column(BigInteger, nullable=False)
    discord_name = Column(String(40), nullable=False)
    address = Column(String(64), nullable=False, unique=True)
    # indicator if account is open for onboarding 1 = Yes, 0 = No
    is_request_open = Column(Integer, nullable=False, default=1)
    message = Column(Text, nullable=True)
    # technical timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def get_onboard_candidates():
        return session\
            .query(OnboardLog)\
            .where(OnboardLog.is_request_open == 1)\
            .order_by(OnboardLog.created_at)\
            .limit(5)\
            .all()
    
    def close_onboard_request(address: AnyStr) -> Dict:
        try:
            o = update(OnboardLog)
            o = o.values({"is_request_open": 0})
            o = o.where(OnboardLog.address == address)
            engine.execute(o)
            return {"status": "success", "message": "Onboard request closed"}
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")
            return {"status": "failed", "message": "Error occurred, onboard request could not be closed"}


Base.metadata.create_all(engine)
